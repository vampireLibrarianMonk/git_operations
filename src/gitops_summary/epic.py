"""GitLab epic setup/status/update workflows and helpers."""

import json
import os
import sys
from datetime import datetime, timedelta
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bedrock import call_bedrock
from .config import GITLAB_CONFIG_FILE, MAX_TOKENS_EPIC
from .git_ops import run_git_command_allow_failure
from .prompts import _clean_commit_message, build_mapping_prompt, build_status_update_prompt
from .ui import Spinner, prompt_yes_no


def load_gitlab_config() -> Optional[Dict[str, Any]]:
    """Load GitLab configuration from .venv directory."""
    if not GITLAB_CONFIG_FILE.exists():
        return None
    try:
        with open(GITLAB_CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[epic] Warning: Could not load config: {e}")
        return None


def save_gitlab_config(config: Dict[str, Any]) -> None:
    """Save GitLab configuration to .venv directory."""
    GITLAB_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GITLAB_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"[epic] Configuration saved to {GITLAB_CONFIG_FILE}")


def ensure_gitignore_entry() -> str:
    """Ensure .gitignore protects the local GitLab secret config."""
    gitignore_path = Path(".gitignore")

    entries = [
        ("# GitLab Epic Config (contains token)", ".venv/.gitlab_epic_config.json"),
    ]

    if not gitignore_path.exists():
        # Create .gitignore with all entries
        lines = []
        for comment, path in entries:
            lines.append(f"{comment}\n{path}")
        content = "\n".join(lines) + "\n"
        with open(gitignore_path, "w") as f:
            f.write(content)
        return "Created .gitignore with GitLab secret config protection"

    # Check existing content
    with open(gitignore_path, "r") as f:
        content = f.read()

    added = []
    for comment, path in entries:
        if path not in content:
            # Append the entry
            with open(gitignore_path, "a") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                    content += "\n"
                f.write(f"\n{comment}\n{path}\n")
                content += f"\n{comment}\n{path}\n"
            added.append(path)

    if not added:
        return ".gitignore already contains all required entries"

    return f"Added to .gitignore: {', '.join(added)}"


def get_gitlab_client(url: str, token: str):
    """Create and return authenticated GitLab client."""
    try:
        import gitlab
    except ImportError:
        print(
            "[epic] Error: python-gitlab not installed. Run: pip install python-gitlab",
        )
        sys.exit(1)

    gl = gitlab.Gitlab(url, private_token=token)
    return gl


def test_gitlab_connection(url: str, token: str) -> tuple[bool, str, Any]:
    """Test GitLab connection and permissions. Returns (success, message, client)."""
    try:
        import gitlab
    except ImportError:
        return False, "python-gitlab not installed", None

    try:
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()
        user = gl.user
        return True, f"Authenticated as: {user.username} ({user.name})", gl
    except gitlab.exceptions.GitlabAuthenticationError:
        return False, "Authentication failed - invalid token", None
    except Exception as e:
        return False, f"Connection failed: {e}", None


def find_epic(gl, project_path: str, epic_iid: int) -> tuple[bool, str, Any, Any]:
    """Find epic in project's group. Returns (success, message, project, epic)."""
    try:
        project = gl.projects.get(project_path)
        # Epics belong to groups, not projects - get the group
        group_id = project.namespace["id"]
        group = gl.groups.get(group_id)
        epic = group.epics.get(epic_iid)
        return True, f"Found epic: {epic.title}", project, epic
    except Exception as e:
        return False, f"Could not find epic #{epic_iid}: {e}", None, None


def _extract_workflow_status(
    labels: List[str],
    state: str,
    health_status: Optional[str] = None,
    board_workflow_labels: List[str] = None,
) -> str:
    """Extract workflow status from GitLab health_status, board labels, or state."""

    # Priority 1: Check health_status attribute (GitLab Premium feature)
    if health_status:
        status_map = {
            "on_track": "On Track",
            "needs_attention": "Needs Attention",
            "at_risk": "At Risk",
            "in_progress": "In Progress",
        }
        return status_map.get(health_status, health_status.replace("_", " ").title())

    # Priority 2: Check for board workflow labels (from board columns)
    if board_workflow_labels:
        for label in labels:
            if label in board_workflow_labels:
                return label

    # Priority 3: Check for scoped status labels (status::in-progress, workflow::done)
    for label in labels:
        if "::" in label:
            prefix, value = label.split("::", 1)
            if prefix.lower() in ["workflow", "status", "state"]:
                return value.strip()

    # Priority 4: Check for common standalone workflow labels
    workflow_patterns = [
        ("in progress", "In Progress"),
        ("in-progress", "In Progress"),
        ("inprogress", "In Progress"),
        ("doing", "In Progress"),
        ("wip", "In Progress"),
        ("to do", "To Do"),
        ("to-do", "To Do"),
        ("todo", "To Do"),
        ("backlog", "Backlog"),
        ("blocked", "Blocked"),
        ("review", "In Review"),
        ("in review", "In Review"),
        ("in-review", "In Review"),
        ("done", "Done"),
        ("complete", "Complete"),
        ("completed", "Complete"),
    ]

    for label in labels:
        label_lower = label.lower()
        for pattern, replacement in workflow_patterns:
            if label_lower == pattern:
                return replacement

    # Fall back to GitLab state (opened/closed)
    if state == "closed":
        return "Closed"
    return "Open"


def _normalize_status(status: str) -> str:
    """Normalize status string for comparison."""
    # Convert to lowercase, replace separators with spaces, strip
    normalized = status.lower().replace("-", " ").replace("_", " ").strip()
    # Map common variations to canonical form
    mappings = {
        "in progress": "in_progress",
        "inprogress": "in_progress",
        "to do": "to_do",
        "todo": "to_do",
        "in review": "in_review",
        "inreview": "in_review",
        "no change": "no_change",
        "nochange": "no_change",
    }
    return mappings.get(normalized, normalized.replace(" ", "_"))


def _statuses_match(status1: str, status2: str) -> bool:
    """Check if two statuses are effectively the same."""
    return _normalize_status(status1) == _normalize_status(status2)


def _get_current_status_label(labels: List[str]) -> Optional[str]:
    """Extract the current status:: label from issue labels."""
    for label in labels:
        if label.lower().startswith("status::"):
            return label
    return None


def _labels_match(label1: Optional[str], label2: Optional[str]) -> bool:
    """Check if two labels are the same (case-insensitive)."""
    if label1 is None and label2 is None:
        return True
    if label1 is None or label2 is None:
        return False
    return label1.lower() == label2.lower()


def get_board_workflow_labels(
    gl,
    project_id: int = None,
    group_id: int = None,
) -> List[str]:
    """Fetch board list labels to identify workflow status labels."""
    workflow_labels = []

    # Try project boards first
    if project_id:
        try:
            project = gl.projects.get(project_id)
            boards = project.boards.list()
            for board in boards:
                lists = board.lists.list()
                for lst in lists:
                    if hasattr(lst, "label") and lst.label:
                        label_name = (
                            lst.label.get("name")
                            if isinstance(lst.label, dict)
                            else getattr(
                                lst.label,
                                "name",
                                None,
                            )
                        )
                        if label_name and label_name not in workflow_labels:
                            workflow_labels.append(label_name)
        except Exception as _exc:
            _ = _exc

    # Also try group boards
    if group_id:
        try:
            group = gl.groups.get(group_id)
            boards = group.boards.list()
            for board in boards:
                lists = board.lists.list()
                for lst in lists:
                    if hasattr(lst, "label") and lst.label:
                        label_name = (
                            lst.label.get("name")
                            if isinstance(lst.label, dict)
                            else getattr(
                                lst.label,
                                "name",
                                None,
                            )
                        )
                        if label_name and label_name not in workflow_labels:
                            workflow_labels.append(label_name)
        except Exception as _exc:
            _ = _exc

    return workflow_labels


def get_epic_issues(
    gl,
    group_id: int,
    epic_iid: int,
    project_id: int = None,
) -> List[Dict]:
    """Get all issues linked to an epic with full details."""
    try:
        group = gl.groups.get(group_id)
        epic = group.epics.get(epic_iid)
        epic_issues = epic.issues.list(all=True)

        # Get workflow labels from group boards
        group_workflow_labels = get_board_workflow_labels(gl, group_id=group_id)

        # Cache projects
        project_cache = {}

        result = []
        for issue in epic_issues:
            health_status = None
            full_labels = issue.labels
            work_item_status = None

            issue_project_id = getattr(issue, "project_id", None)
            issue_state = issue.state  # Default from epic's issue list

            # Fetch full issue details
            if issue_project_id:
                try:
                    if issue_project_id not in project_cache:
                        project_cache[issue_project_id] = gl.projects.get(
                            issue_project_id,
                        )
                    project = project_cache[issue_project_id]

                    full_issue = project.issues.get(issue.iid)

                    # Get state from full issue (more accurate)
                    if hasattr(full_issue, "state"):
                        issue_state = full_issue.state

                    if hasattr(full_issue, "labels"):
                        full_labels = full_issue.labels
                    if hasattr(full_issue, "attributes"):
                        health_status = full_issue.attributes.get("health_status")

                    # Try to get status from labels (status:: scoped labels)
                    # Note: GitLab's "Status" UI field requires Ultimate and isn't exposed via API
                    # We fall back to checking for status:: labels
                    for label in full_labels:
                        if label.lower().startswith("status::"):
                            work_item_status = label.split("::", 1)[1]
                            break
                except Exception:
                    full_labels = issue.labels

            # Determine workflow status
            if work_item_status:
                workflow_status = work_item_status
            elif health_status:
                workflow_status = health_status.replace("_", " ").title()
            else:
                workflow_status = _extract_workflow_status(
                    full_labels,
                    issue_state,
                    None,
                    group_workflow_labels,
                )

            result.append(
                {
                    "iid": issue.iid,
                    "project_id": issue_project_id,
                    "title": issue.title,
                    "state": issue_state,
                    "health_status": health_status,
                    "workflow_status": workflow_status,
                    "labels": full_labels,
                    "web_url": issue.web_url,
                    "description": getattr(issue, "description", ""),
                },
            )
        return result
    except Exception as e:
        print(f"[epic] Error fetching issues: {e}")
        return []


def get_project_structure() -> str:
    """Get project directory structure for LLM analysis."""
    structure = []
    for root, dirs, files in os.walk("."):
        # Skip hidden dirs and common non-code dirs
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in [
                "venv",
                "__pycache__",
                "node_modules",
                ".git",
                "example_data",
                "example_reports",
            ]
        ]
        level = root.replace(".", "").count(os.sep)
        indent = "  " * level
        folder = os.path.basename(root) or "."
        structure.append(f"{indent}{folder}/")
        for file in files:
            if not file.startswith(".") and file.endswith(
                (".py", ".md", ".yml", ".yaml", ".json"),
            ):
                structure.append(f"{indent}  {file}")
    return "\n".join(structure[:100])  # Limit output


def map_issues_to_paths(config: Dict, gl) -> Dict[str, List[str]]:
    """Use LLM to map issues to code paths."""
    print("[epic] Analyzing project structure...")
    project_structure = get_project_structure()

    group_id = config["group_id"]
    epic_iid = config["epic_iid"]
    project_id = config.get("project_id")
    issues = get_epic_issues(gl, group_id, epic_iid, project_id)

    if not issues:
        print("[epic] No child issues found for this epic.")
        return {}

    print(f"[epic] Found {len(issues)} child issues. Generating path mappings...")
    prompt = build_mapping_prompt(config["epic_title"], issues, project_structure)

    try:
        response = call_bedrock(prompt, max_tokens=MAX_TOKENS_EPIC)
        # Extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            mapping_data = json.loads(response[start:end])
            return mapping_data
    except Exception as e:
        print(f"[epic] Error generating mappings: {e}")
    return {}


def epic_setup() -> int:
    """Interactive setup for GitLab epic tracking."""
    # Check for python-gitlab first
    try:
        import gitlab  # noqa: F401

        print("[epic] python-gitlab package found")
    except ImportError:
        print("[epic] Error: python-gitlab not installed.")
        print("  Run: pip install python-gitlab")
        return 1

    print("\n" + "=" * 60)
    print("GitLab Epic Tracking Setup")
    print("=" * 60)

    # Check for existing config
    existing = load_gitlab_config()
    if existing:
        print("\nExisting configuration found:")
        print(f"  URL: {existing.get('url')}")
        print(f"  Project: {existing.get('project_path')}")
        print(
            f"  Epic: #{existing.get('epic_iid')} - {existing.get('epic_title', 'Unknown')}",
        )
        if not prompt_yes_no("\nReconfigure?"):
            return 0

    # Get GitLab URL
    print("\n[Step 1/4] GitLab Instance URL")
    print("  Examples: https://gitlab.com, https://gitlab.mycompany.com")
    url = input("  Enter GitLab URL: ").strip().rstrip("/")
    if not url:
        print("  Error: URL is required")
        return 1

    # Get access token
    print("\n[Step 2/4] Personal Access Token")
    print(f"  Create at: {url}/-/user_settings/personal_access_tokens")
    print("  Required scopes: api, read_api, read_repository")
    token = getpass("  Enter token: ").strip()
    if not token:
        print("  Error: Token is required")
        return 1

    # Test connection
    print("\n[epic] Testing connection...")
    success, message, gl = test_gitlab_connection(url, token)
    print(f"  {message}")
    if not success:
        return 1

    # Get project path
    print("\n[Step 3/4] Project Path")
    print(
        "  Format: namespace/project (e.g., AWSProServe/opir/data-operations-insights-dashboard)",
    )
    project_path = input("  Enter project path: ").strip()
    if not project_path:
        print("  Error: Project path is required")
        return 1

    # Get epic number
    print("\n[Step 4/4] Epic Number")
    epic_input = input("  Enter epic IID (e.g., 103): ").strip()
    try:
        epic_iid = int(epic_input)
    except ValueError:
        print("  Error: Epic IID must be a number")
        return 1

    # Find and verify epic
    print("\n[epic] Locating epic...")
    success, message, project, epic = find_epic(gl, project_path, epic_iid)
    print(f"  {message}")
    if not success:
        return 1

    # Confirm with user
    print(f"\n  Epic Title: {epic.title}")
    print(f"  Epic URL: {epic.web_url}")
    if not prompt_yes_no("\n  Is this the correct epic?"):
        print("  Setup cancelled.")
        return 1

    # Save initial config
    config = {
        "url": url,
        "token": token,
        "project_path": project_path,
        "project_id": project.id,
        "group_id": project.namespace["id"],
        "epic_iid": epic_iid,
        "epic_title": epic.title,
        "epic_url": epic.web_url,
        "mappings": {},
        "setup_date": datetime.now().isoformat(),
    }

    # Generate path mappings
    if prompt_yes_no("\nGenerate AI-assisted code path mappings now?"):
        mapping_data = map_issues_to_paths(config, gl)
        if mapping_data:
            config["mappings"] = mapping_data
            print("\n[epic] Path mappings generated:")
            for m in mapping_data.get("mappings", []):
                print(f"  Issue #{m['issue_iid']}: {', '.join(m['paths'])}")

    save_gitlab_config(config)

    # Ensure .gitignore protects the config file
    gitignore_status = ensure_gitignore_entry()
    print(f"[epic] {gitignore_status}")

    print("\n[epic] Setup complete! You can now use:")
    print("  gitops-summary epic --status   # View status")
    print("  gitops-summary epic --update   # Update issues")
    return 0


def get_recent_commits_for_paths(
    paths: List[str],
    days: int = 7,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict]:
    """Get recent commits affecting specified paths."""
    if start_date and end_date:
        # Use date strings for --since (inclusive) and --until (exclusive of end_date)
        since_date = start_date.strftime("%Y-%m-%d")
        until_date = end_date.strftime("%Y-%m-%d")
    else:
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        until_date = None
    commits = []

    # Use a delimiter unlikely to appear in commit messages
    DELIM = "<<|>>"

    for path in paths:
        log_args = [
            "log",
            f"--since={since_date}",
            f"--format=%H{DELIM}%s{DELIM}%an{DELIM}%ai",
        ]
        if until_date:
            log_args.insert(2, f"--until={until_date}")
        log_args.extend(["--", path])
        result = run_git_command_allow_failure(log_args)
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                parts = line.split(DELIM)
                if len(parts) >= 4:
                    # Take only the first line of the subject if multi-line
                    subject = parts[1].split("\n")[0].strip()
                    # Clean up malformed AI-generated commit messages
                    subject = _clean_commit_message(subject)
                    commits.append(
                        {
                            "hash": parts[0][:8],
                            "full_hash": parts[0],  # Keep full hash for URLs
                            "message": subject,
                            "author": parts[2],
                            "date": parts[3][:10],
                            "path": path,
                        },
                    )

    # Deduplicate by hash
    seen = set()
    unique = []
    for c in commits:
        if c["hash"] not in seen:
            seen.add(c["hash"])
            unique.append(c)
    return unique


def epic_status() -> int:
    """Display current epic and issue status."""
    config = load_gitlab_config()
    if not config:
        print("[epic] No configuration found. Run: gitops-summary epic --setup")
        return 1

    print("\n" + "=" * 60)
    print(f"Epic Status: {config['epic_title']}")
    print("=" * 60)
    print(f"URL: {config['epic_url']}")

    # Connect to GitLab
    spinner = Spinner("[epic] Connecting to GitLab...")
    spinner.start()
    gl = get_gitlab_client(config["url"], config["token"])
    try:
        gl.auth()
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(f"[epic] Authentication failed: {e}")
        return 1

    # Get issues
    spinner.start("[epic] Fetching issues...")
    issues = get_epic_issues(
        gl,
        config["group_id"],
        config["epic_iid"],
        config.get("project_id"),
    )
    spinner.stop()

    mappings = config.get("mappings", {}).get("mappings", [])
    mapping_lookup = {m["issue_iid"]: m["paths"] for m in mappings}

    print(f"\nChild Issues ({len(issues)}):")
    print("-" * 60)

    for issue in issues:
        state_icon = "✓" if issue["state"] == "closed" else "○"
        paths = mapping_lookup.get(issue["iid"], [])
        commits = get_recent_commits_for_paths(paths) if paths else []

        # Get status label and other labels separately
        status_label = _get_current_status_label(issue.get("labels", []))
        other_labels = [label_name for label_name in issue.get("labels", []) if not label_name.lower().startswith("status::")]

        # Display status: use status label if present, otherwise state
        if status_label:
            status_display = status_label.split("::", 1)[1]  # e.g., "in-progress"
        else:
            status_display = issue["state"].capitalize()  # "Opened" -> "Open" or "Closed"
            if status_display == "Opened":
                status_display = "Open"

        print(f"\n  [{state_icon}] #{issue['iid']}: {issue['title']}")
        print(f"      Status: {status_display}")
        print(f"      Labels: {', '.join(other_labels) or 'None'}")
        print(f"      Mapped paths: {', '.join(paths) or 'Not mapped'}")
        print(f"      Recent commits: {len(commits)}")

    return 0


def epic_update() -> int:
    """Update epic child issues with AI-generated status comments."""
    config = load_gitlab_config()
    if not config:
        print("[epic] No configuration found. Run: gitops-summary epic --setup")
        return 1

    print("\n" + "=" * 60)
    print(f"Updating Epic: {config['epic_title']}")
    print("=" * 60)

    # Connect to GitLab
    spinner = Spinner("[epic] Connecting to GitLab...")
    spinner.start()
    gl = get_gitlab_client(config["url"], config["token"])
    try:
        gl.auth()
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(f"[epic] Authentication failed: {e}")
        return 1

    # Get issues (epic can span multiple projects)
    spinner.start("[epic] Fetching issues...")
    issues = get_epic_issues(
        gl,
        config["group_id"],
        config["epic_iid"],
        config.get("project_id"),
    )
    spinner.stop()

    # Cache projects by ID for issue operations
    project_cache = {}

    mappings = config.get("mappings", {}).get("mappings", [])
    mapping_lookup = {m["issue_iid"]: m["paths"] for m in mappings}

    if not issues:
        print("[epic] No child issues found.")
        return 0

    # Calculate date range for commit lookups
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    print(f"\nProcessing {len(issues)} issues...")
    print(
        f"  Commit window: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
    )

    updates = []
    for issue in issues:
        paths = mapping_lookup.get(issue["iid"], [])
        commits = get_recent_commits_for_paths(paths) if paths else []

        print(f"\n  Processing #{issue['iid']}: {issue['title']}")
        print(f"    Commits found: {len(commits)}")

        # Get current status label
        current_status_label = _get_current_status_label(issue.get("labels", []))

        # Generate status update
        prompt = build_status_update_prompt(issue, commits, current_status_label)
        try:
            spinner.start(f"    Generating update for #{issue['iid']}...")
            response = call_bedrock(prompt, max_tokens=400).strip()
            spinner.stop()
            # Parse JSON response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                comment = data.get("comment", response)
                suggested_label = data.get("suggested_label")
                # Handle null/None/"null" values
                if suggested_label in [None, "null", "None", ""]:
                    suggested_label = None
            else:
                comment = response
                suggested_label = None

            updates.append(
                {
                    "issue": issue,
                    "comment": comment,
                    "commits": commits,  # Store full commit data for URLs
                    "commit_count": len(commits),
                    "current_label": current_status_label,
                    "suggested_label": suggested_label,
                },
            )
            print(f"    Generated: {comment[:60]}...")
        except Exception as e:
            spinner.stop()
            print(f"    Error generating update: {e}")

    if not updates:
        print("\n[epic] No updates generated.")
        return 0

    # Preview and confirm
    print("\n" + "=" * 60)
    print("Preview of Updates")
    print("=" * 60)
    pending_state_changes = []  # Collect all potential state changes for review
    label_changes = []

    for u in updates:
        print(f"\n  #{u['issue']['iid']}: {u['issue']['title']}")
        print(f"  Comment: {u['comment']}")

        current_label = u["current_label"]
        suggested_label = u["suggested_label"]
        issue_state = u["issue"]["state"]  # opened or closed

        current_display = current_label.split("::", 1)[1] if current_label else "None"
        suggested_display = suggested_label.split("::", 1)[1] if suggested_label else "None"

        # Check label change
        if _labels_match(current_label, suggested_label) or suggested_label is None:
            print(f"  Label: No change (remains {current_display})")
        else:
            print(f"  Label: {current_display} → {suggested_display} [SUGGESTED]")
            label_changes.append(
                {
                    "iid": u["issue"]["iid"],
                    "project_id": u["issue"]["project_id"],
                    "title": u["issue"]["title"],
                    "current_label": current_label,
                    "suggested_label": suggested_label,
                },
            )

            # Collect potential state changes for manual review
            if suggested_label and "complete" in suggested_label.lower() and issue_state == "opened":
                print("  State: opened → closed [SUGGESTED]")
                pending_state_changes.append(
                    {
                        "iid": u["issue"]["iid"],
                        "project_id": u["issue"]["project_id"],
                        "title": u["issue"]["title"],
                        "action": "close",
                        "current_state": "opened",
                    },
                )
            elif (
                suggested_label
                and suggested_label.lower()
                not in [
                    "status::complete",
                    "status::won't fix",
                ]
                and issue_state == "closed"
            ):
                print("  State: closed → opened [SUGGESTED]")
                pending_state_changes.append(
                    {
                        "iid": u["issue"]["iid"],
                        "project_id": u["issue"]["project_id"],
                        "title": u["issue"]["title"],
                        "action": "reopen",
                        "current_state": "closed",
                    },
                )

    # Helper to get project from cache
    def get_project(project_id):
        if project_id not in project_cache:
            project_cache[project_id] = gl.projects.get(project_id)
        return project_cache[project_id]

    # Review and post comments individually
    print("\n" + "=" * 60)
    print("Review Comments")
    print("=" * 60)
    print("Review each comment individually. You can edit or skip.\n")

    # Build commit URL base from config
    commit_url_base = f"{config['url']}/{config['project_path']}/-/commit"

    for u in updates:
        print(f"\n  #{u['issue']['iid']}: {u['issue']['title']}")
        print("  Current comment:")
        print(f"    {u['comment']}")

        # Show commits with markdown-style links
        if u["commits"]:
            print("  Commits to link:")
            for c in u["commits"][:10]:
                commit_url = f"{commit_url_base}/{c['full_hash']}"
                print(f"    [{c['hash']}]({commit_url})")
            if len(u["commits"]) > 10:
                print(f"    ... and {len(u['commits']) - 10} more")
        print()

        response = input("  [p]ost / [e]dit / [s]kip? ").strip().lower()

        if response == "s":
            print("    ✗ Skipped")
            continue
        elif response == "e":
            print("  Enter new comment (press Enter twice to finish):")
            lines = []
            while True:
                line = input("    ")
                if line == "":
                    if lines:
                        break
                else:
                    lines.append(line)
            new_comment = " ".join(lines) if lines else u["comment"]
            u["comment"] = new_comment
            print(f"  Updated comment: {new_comment[:60]}...")

        # Post the comment (either original or edited)
        if response in ["p", "e", ""]:
            try:
                # Build comment body with commit links
                comment_body = f"**Automated Status Update**\n\n{u['comment']}"

                # Add commit links section if there are commits (just clickable IDs)
                if u["commits"]:
                    commit_links = []
                    for c in u["commits"][:10]:  # Limit to 10 commits
                        commit_url = f"{commit_url_base}/{c['full_hash']}"
                        commit_links.append(f"[`{c['hash']}`]({commit_url})")

                    comment_body += "\n\n**Related Commits:** " + " ".join(
                        commit_links,
                    )
                    if len(u["commits"]) > 10:
                        comment_body += f" ... and {len(u['commits']) - 10} more"

                proj = get_project(u["issue"]["project_id"])
                gitlab_issue = proj.issues.get(u["issue"]["iid"])
                gitlab_issue.notes.create({"body": comment_body})
                print(f"    ✓ Posted to #{u['issue']['iid']}")
            except Exception as e:
                print(f"    ✗ Failed #{u['issue']['iid']}: {e}")

    # Apply label changes with manual verification
    approved_label_changes = []
    if label_changes:
        print("\n" + "=" * 60)
        print("Review Label Changes")
        print("=" * 60)
        print("Review each suggested label change individually:\n")

        for change in label_changes:
            old_display = change["current_label"].split("::", 1)[1] if change["current_label"] else "None"
            new_display = change["suggested_label"].split("::", 1)[1] if change["suggested_label"] else "None"
            print(f"  #{change['iid']}: {change['title']}")
            print(f"    Current: {old_display} → Suggested: {new_display}")

            if prompt_yes_no("    Apply this label change?"):
                approved_label_changes.append(change)
                print("    ✓ Approved")
            else:
                print("    ✗ Skipped")

        if approved_label_changes:
            print("\n[epic] Applying approved label changes...")
            for change in approved_label_changes:
                try:
                    proj = get_project(change["project_id"])
                    gitlab_issue = proj.issues.get(change["iid"])
                    current_labels = list(gitlab_issue.labels)

                    # Remove old status label if present
                    if change["current_label"]:
                        current_labels = [label_name for label_name in current_labels if label_name.lower() != change["current_label"].lower()]

                    # Add new status label
                    if change["suggested_label"]:
                        current_labels.append(change["suggested_label"])

                    gitlab_issue.labels = current_labels
                    gitlab_issue.save()

                    old_display = change["current_label"].split("::", 1)[1] if change["current_label"] else "None"
                    new_display = change["suggested_label"].split("::", 1)[1] if change["suggested_label"] else "None"
                    print(f"  ✓ #{change['iid']}: {old_display} → {new_display}")
                except Exception as e:
                    print(f"  ✗ Failed #{change['iid']}: {e}")

    # Handle state changes with manual verification
    issues_to_close = []
    issues_to_reopen = []

    if pending_state_changes:
        print("\n" + "=" * 60)
        print("Review State Changes")
        print("=" * 60)
        print("Review each suggested state change individually:\n")

        for state_change in pending_state_changes:
            action = state_change["action"]
            if action == "close":
                print(f"  #{state_change['iid']}: {state_change['title']}")
                print("    Suggested: CLOSE this issue (mark as complete)")
                if prompt_yes_no("    Close this issue?"):
                    issues_to_close.append(state_change)
                    print("    ✓ Will close")
                else:
                    print("    ✗ Skipped")
            elif action == "reopen":
                print(f"  #{state_change['iid']}: {state_change['title']}")
                print(
                    "    Suggested: REOPEN this issue (currently closed but has activity)",
                )
                if prompt_yes_no("    Reopen this issue?"):
                    issues_to_reopen.append(state_change)
                    print("    ✓ Will reopen")
                else:
                    print("    ✗ Skipped")

    # Apply approved closes
    if issues_to_close:
        print("\n[epic] Closing approved issues...")
        for issue_info in issues_to_close:
            try:
                proj = get_project(issue_info["project_id"])
                gitlab_issue = proj.issues.get(issue_info["iid"])
                gitlab_issue.state_event = "close"
                gitlab_issue.save()
                print(f"  ✓ Closed #{issue_info['iid']}: {issue_info['title']}")
            except Exception as e:
                print(f"  ✗ Failed to close #{issue_info['iid']}: {e}")

    # Apply approved reopens
    if issues_to_reopen:
        print("\n[epic] Reopening approved issues...")
        for issue_info in issues_to_reopen:
            try:
                proj = get_project(issue_info["project_id"])
                gitlab_issue = proj.issues.get(issue_info["iid"])
                gitlab_issue.state_event = "reopen"
                gitlab_issue.save()
                print(f"  ✓ Reopened #{issue_info['iid']}: {issue_info['title']}")
            except Exception as e:
                print(f"  ✗ Failed to reopen #{issue_info['iid']}: {e}")

    print("\n[epic] Update complete!")
    return 0


def epic_remap() -> int:
    """Re-generate code path mappings for issues."""
    config = load_gitlab_config()
    if not config:
        print("[epic] No configuration found. Run: gitops-summary epic --setup")
        return 1

    print("\n[epic] Re-mapping code paths to issues...")

    gl = get_gitlab_client(config["url"], config["token"])
    try:
        gl.auth()
    except Exception as e:
        print(f"[epic] Authentication failed: {e}")
        return 1

    mapping_data = map_issues_to_paths(config, gl)
    if mapping_data:
        config["mappings"] = mapping_data
        config["last_mapped"] = datetime.now().isoformat()
        save_gitlab_config(config)

        print("\n[epic] Updated mappings:")
        for m in mapping_data.get("mappings", []):
            print(f"  Issue #{m['issue_iid']}: {', '.join(m['paths'])}")
            if m.get("reason"):
                print(f"    Reason: {m['reason']}")
    else:
        print("[epic] Failed to generate mappings.")
        return 1

    return 0


def epic_labels() -> int:
    """Debug: Show all project/group labels containing 'status'."""
    config = load_gitlab_config()
    if not config:
        print("[epic] No configuration found. Run: gitops-summary epic --setup")
        return 1

    print("\n" + "=" * 60)
    print("DEBUG: Status-Related Labels")
    print("=" * 60)

    spinner = Spinner("[epic] Connecting to GitLab...")
    spinner.start()
    gl = get_gitlab_client(config["url"], config["token"])
    try:
        gl.auth()
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(f"[epic] Authentication failed: {e}")
        return 1

    # Get project labels
    spinner.start("[epic] Fetching project labels...")
    try:
        project = gl.projects.get(config["project_id"])
        project_labels = project.labels.list(all=True)
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(f"[epic] Error fetching project labels: {e}")
        project_labels = []

    # Get group labels
    spinner.start("[epic] Fetching group labels...")
    try:
        group = gl.groups.get(config["group_id"])
        group_labels = group.labels.list(all=True)
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(f"[epic] Error fetching group labels: {e}")
        group_labels = []

    # Filter and display status-related labels
    print("\n[Project Labels with 'status']")
    print("-" * 40)
    status_labels = []
    for label in project_labels:
        name = label.name
        if "status" in name.lower():
            status_labels.append(label)
            desc = getattr(label, "description", "") or ""
            color = getattr(label, "color", "")
            print(f"  Name: {name}")
            print(f"    Color: {color}")
            if desc:
                print(f"    Description: {desc}")
            print()

    if not status_labels:
        print("  (none found)")

    print("\n[Group Labels with 'status']")
    print("-" * 40)
    group_status_labels = []
    for label in group_labels:
        name = label.name
        if "status" in name.lower():
            group_status_labels.append(label)
            desc = getattr(label, "description", "") or ""
            color = getattr(label, "color", "")
            print(f"  Name: {name}")
            print(f"    Color: {color}")
            if desc:
                print(f"    Description: {desc}")
            print()

    if not group_status_labels:
        print("  (none found)")

    # Also show all scoped labels (contain ::)
    print("\n[All Scoped Labels (contain '::')]")
    print("-" * 40)
    all_labels = list(project_labels) + list(group_labels)
    scoped = set()
    for label in all_labels:
        if "::" in label.name:
            scoped.add(label.name)

    for name in sorted(scoped):
        print(f"  {name}")

    if not scoped:
        print("  (none found)")

    return 0


def epic_workflow(args) -> int:
    """Main epic workflow dispatcher."""
    if args.setup:
        return epic_setup()
    elif args.status:
        return epic_status()
    elif args.update:
        return epic_update()
    elif args.map:
        return epic_remap()
    elif args.labels:
        return epic_labels()
    else:
        # Default to status if no flag
        config = load_gitlab_config()
        if not config:
            print("[epic] No configuration found. Starting setup...")
            return epic_setup()
        return epic_status()
