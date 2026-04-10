"""Prompt builders and LLM response cleanup helpers."""

import re
from typing import Dict, List, Optional

from .config import VALID_STATUS_LABELS


COMMIT_SYSTEM_PROMPT = """You write git commit messages for software repositories.

Return only a valid commit message.
- First line: a concise subject line in imperative mood, ideally 50-72 characters.
- Body format: after a blank line, include one short executive-summary paragraph.
- After that paragraph, you may include short bullet points beginning with '- '.
- Use only facts supported by the provided git status and diff.
- Never write project reviews, implementation assessments, phase alignment notes, TODO lists, or advice.
- Never say things like 'Based on the implementation plan', 'here are my observations', 'overall', or 'let me know'.
- Never ask follow-up questions.
"""


_INVALID_COMMIT_PHRASES = (
    "based on the implementation plan",
    "based on the source files",
    "here are my observations",
    "overall the core is in place",
    "phase 1",
    "missing/todo",
    "let me know if you need",
    "alignment with",
)

_STRIP_COMMIT_LINES_CONTAINING = (
    "based on the implementation plan",
    "based on the source files",
    "here are my observations",
    "let me know if you need",
)

_STRIP_COMMIT_LINE_PREFIXES = (
    "backend:",
    "frontend:",
    "missing/todo:",
    "overall ",
)

_SKIP_COMMIT_SECTION_PREFIXES = (
    "missing/todo:",
    "todo:",
    "remaining work:",
)


def _truncate_commit_subject(subject: str, max_len: int = 72) -> str:
    """Normalize and cap commit subject length."""

    normalized = re.sub(r"\s+", " ", subject).strip().rstrip(".")
    if not normalized:
        normalized = "Update staged changes"
    if len(normalized) <= max_len:
        return normalized
    return normalized[: max_len - 1].rstrip() + "…"


def _is_plausible_commit_subject(line: str) -> bool:
    """Return True when a line looks like a commit subject."""

    candidate = line.strip()
    if not candidate:
        return False
    if len(candidate) > 90:
        return False
    if candidate.startswith(("-", "*", "•")):
        return False
    if candidate.endswith((":", "?", ".")):
        return False
    lowered = candidate.lower()
    if any(lowered.startswith(prefix) for prefix in _STRIP_COMMIT_LINE_PREFIXES):
        return False
    return True


def _parse_status_entries(status: str) -> List[Dict[str, str]]:
    """Parse `git status -sb` lines into structured change entries."""

    entries: List[Dict[str, str]] = []
    for raw_line in status.splitlines():
        if not raw_line.strip() or raw_line.startswith("##"):
            continue

        code = raw_line[:2]
        path_text = raw_line[3:].strip() if len(raw_line) > 3 else ""
        if not path_text:
            continue

        primary_code = code[0] if code and code[0] != " " else code[1]
        action = {
            "A": "add",
            "D": "delete",
            "M": "modify",
            "R": "rename",
            "C": "copy",
            "?": "add",
        }.get(primary_code, "update")

        if action == "rename" and " -> " in path_text:
            old_path, new_path = [part.strip() for part in path_text.split(" -> ", 1)]
            entries.append(
                {
                    "action": action,
                    "path": old_path,
                    "new_path": new_path,
                }
            )
            continue

        entries.append(
            {
                "action": action,
                "path": path_text,
                "new_path": "",
            }
        )

    return entries


def _top_level_component(entries: List[Dict[str, str]]) -> str:
    """Return a shared top-level directory name when one is obvious."""

    components = []
    for entry in entries:
        path = entry.get("new_path") or entry["path"]
        if "/" not in path:
            continue
        components.append(path.split("/", 1)[0])

    if components and len(set(components)) == 1:
        return components[0]
    return ""


def _display_name(path: str) -> str:
    """Return basename-like display name for a repo path."""

    return path.rsplit("/", 1)[-1]


def build_fallback_commit_subject(status: str, is_initial_commit: bool = False) -> str:
    """Build only the subject line for a deterministic fallback commit message."""

    entries = _parse_status_entries(status)
    if not entries:
        return "Update staged changes"

    component = _top_level_component(entries)
    actions = {entry["action"] for entry in entries}
    count = len(entries)

    if is_initial_commit:
        subject = "Bootstrap project scaffolding"
        if component:
            subject = f"Bootstrap {component} project scaffolding"
    elif count == 1:
        entry = entries[0]
        path = entry.get("new_path") or entry["path"]
        if entry["action"] == "add":
            subject = f"Add {_display_name(path)}"
        elif entry["action"] == "delete":
            subject = f"Remove {_display_name(path)}"
        elif entry["action"] == "rename":
            subject = f"Rename {_display_name(entry['path'])} to {_display_name(entry['new_path'])}"
        else:
            subject = f"Update {_display_name(path)}"
    else:
        if actions == {"add"}:
            subject = f"Add {count} new files"
        elif actions <= {"modify", "update"}:
            subject = f"Update {count} files"
        elif actions == {"delete"}:
            subject = f"Remove {count} files"
        else:
            subject = "Update staged changes"

        if component:
            subject = f"{subject} in {component}"

    return _truncate_commit_subject(subject)


def build_fallback_commit_message(status: str, is_initial_commit: bool = False) -> str:
    """Build a deterministic commit message when the LLM response is unusable."""

    entries = _parse_status_entries(status)
    if not entries:
        return "Update staged changes"

    subject = build_fallback_commit_subject(status, is_initial_commit=is_initial_commit)

    bullets = []
    for entry in entries[:6]:
        action = entry["action"]
        path = entry["path"]
        new_path = entry.get("new_path") or ""

        if action == "add":
            bullets.append(f"- Add {path}")
        elif action == "delete":
            bullets.append(f"- Remove {path}")
        elif action == "rename":
            bullets.append(f"- Rename {path} to {new_path}")
        elif action == "copy":
            bullets.append(f"- Copy {path}")
        else:
            bullets.append(f"- Update {path}")

    remaining = len(entries) - len(bullets)
    if remaining > 0:
        bullets.append(f"- Update {remaining} additional file(s)")

    return subject if not bullets else f"{subject}\n\n" + "\n".join(bullets)


def build_prompt(
    status: str,
    diff: str,
    new_files: Optional[List[str]] = None,
    is_initial_commit: bool = False,
) -> str:
    new_files_section = ""
    if new_files:
        new_files_list = "\n".join(f"  - {f}" for f in new_files)
        new_files_section = f"\n\nNEWLY ADDED FILES (these are brand new, not modifications):\n{new_files_list}\n"

    initial_commit_section = ""
    if is_initial_commit:
        initial_commit_section = (
            "\nINITIAL COMMIT CONTEXT:\n"
            "- This is the first commit in the repository.\n"
            "- Write the summary in a natural, human way that reflects initial setup, scaffolding, or first implementation work.\n"
            "- Favor phrasing like 'Initial project scaffolding for ...', 'Initial implementation of ...', or 'Bootstrap ...'.\n"
            "- Avoid describing the work like a routine follow-up update with words such as 'updated' or 'modified' unless the diff clearly requires that wording.\n"
        )

    # Count files from status to adjust detail level for larger commits.
    file_count = len([line for line in status.split("\n") if line.strip()])

    if file_count > 30:
        format_instructions = (
            "FORMAT FOR LARGE COMMITS (30+ files):\n"
            "1) First line: one concise git commit subject in imperative mood, max 72 characters, no trailing period.\n"
            "2) Body: after one blank line, include a 2-4 sentence executive summary paragraph covering the main themes.\n"
            "3) Then include 3-6 bullets grouped by major component/theme.\n"
            "4) Each bullet must begin with '- ' and mention specific files, functions, classes, or behavior changes.\n"
        )
    else:
        format_instructions = (
            "FORMAT:\n"
            "1) First line: one concise git commit subject in imperative mood, max 72 characters, no trailing period.\n"
            "2) Body: after one blank line, include a 1-3 sentence executive summary paragraph.\n"
            "3) Then include 1-4 bullets beginning with '- '.\n"
            "4) Bullets must include concrete technical details, not generic summaries.\n"
        )

    return (
        "You are generating ONE git commit message for the staged changes below.\n"
        f"{format_instructions}\n\n"
        "CRITICAL RULES FOR ACCURACY:\n"
        "- SKIP files that have no visible changes in the diff "
        "(e.g., whitespace-only or formatting-only changes with no actual code diff). "
        "Do NOT list them or say 'No changes'.\n"
        "- EXTRACT SPECIFIC DETAILS from the diff: function names, variable names, class names, "
        "parameter changes, new imports, removed code, renamed identifiers, etc.\n"
        "- NEVER use generic phrases like 'updated logic', 'improved functionality', 'made changes', "
        "'various updates', 'minor updates', 'minor improvements', or 'refactored code' without specifying WHAT was changed.\n"
        "- For each file WITH ACTUAL CHANGES, cite the ACTUAL changes visible in the diff:\n"
        "  * If a function was added: name it (e.g., 'Added validate_input() function')\n"
        "  * If a class was added: name it (e.g., 'Added CVEDetailPattern class')\n"
        "  * If parameters changed: specify them (e.g., 'Added timeout parameter to fetch_data()')\n"
        "  * If logic changed: describe the specific change (e.g., 'Changed retry count from 3 to 5')\n"
        "  * If imports added/removed: list them (e.g., 'Added import for datetime module')\n"
        "  * If error handling changed: specify how (e.g., 'Added try/except for ConnectionError')\n"
        "- If a file is renamed, mention both old and new names.\n"
        "- If a file is deleted, mark it as [DELETED] and briefly note what it contained.\n"
        "- NEVER mention these files under any circumstance: .venv/.gitlab_epic_config.json.\n"
        "- IMPORTANT: Only label a file as '[NEW]' if it appears in the NEWLY ADDED FILES list below. "
        "Files not in that list are modifications to existing files, NOT new files.\n"
        "- Only summarize what is ACTUALLY visible in the diff - do not infer or assume.\n\n"
        "OUTPUT FORMAT RULES:\n"
        "- Output must be plain text with no markdown formatting (no ```, no headers, no bold).\n"
        "- Output ONLY the commit message text itself.\n"
        "- Do write a real commit message with subject line, summary paragraph, and optional bullets.\n"
        "- Do NOT write a standalone implementation review, project assessment, or plan status update.\n"
        "- Do NOT include phrases like 'Here is the commit message:' or 'Executive Summary:'.\n"
        "- Do NOT wrap output in code blocks or markdown.\n"
        "- Do NOT echo back the git status or git diff.\n"
        "- Do NOT mention implementation plans, phases, alignment, observations, missing work, or TODOs.\n"
        "- Start directly with the commit subject line.\n\n"
        f"{initial_commit_section}"
        "Git status:\n"
        f"{status}\n\n"
        "Git diff:\n"
        f"{diff}"
        f"{new_files_section}"
    )


def build_commit_retry_prompt(
    status: str,
    diff: str,
    new_files: Optional[List[str]] = None,
    is_initial_commit: bool = False,
    invalid_response: str = "",
) -> str:
    """Build a stricter retry prompt when the model returns analysis instead of a commit."""

    base_prompt = build_prompt(
        status,
        diff,
        new_files,
        is_initial_commit=is_initial_commit,
    )
    return (
        f"{base_prompt}\n\n"
        "The previous answer was invalid because it was not a git commit message.\n"
        "Rewrite from scratch as a real commit message.\n"
        "Do not preserve any review or assessment language from the invalid answer.\n"
        "Invalid answer:\n"
        f"{invalid_response}\n"
    )


def clean_commit_response(response: str) -> str:
    """Clean up LLM response to extract just the commit message."""
    lines = response.strip().split("\n")
    cleaned_lines = []
    skip_until_content = True

    for line in lines:
        stripped = line.strip()

        # Skip empty lines at the start
        if skip_until_content and not stripped:
            continue

        # Skip common preamble patterns
        if skip_until_content:
            lower = stripped.lower()
            if any(
                lower.startswith(p)
                for p in [
                    "here is",
                    "here's",
                    "below is",
                    "the commit message",
                    "commit message:",
                    "executive summary:",
                    "summary:",
                    "subject:",
                    "```",
                ]
            ):
                continue
            # Found real content
            skip_until_content = False

        # Stop at trailing code block markers
        if stripped == "```":
            break

        if stripped.lower().startswith("let me know if you need"):
            break

        cleaned_lines.append(line)

    # Remove trailing empty lines
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    cleaned = "\n".join(cleaned_lines).strip()
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.replace("**", "")
    return sanitize_commit_response(cleaned)


def sanitize_commit_response(response: str) -> str:
    """Strip common review/planning boilerplate while preserving commit content."""

    sanitized_lines = []
    skip_section = False
    for line in response.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()

        if not stripped:
            if sanitized_lines and sanitized_lines[-1] != "":
                sanitized_lines.append("")
            continue

        if lowered.endswith(":"):
            skip_section = any(lowered.startswith(prefix) for prefix in _SKIP_COMMIT_SECTION_PREFIXES)

        if skip_section and not lowered.endswith(":"):
            continue

        if any(phrase in lowered for phrase in _STRIP_COMMIT_LINES_CONTAINING):
            continue

        if any(lowered.startswith(prefix) for prefix in _STRIP_COMMIT_LINE_PREFIXES):
            continue

        sanitized_lines.append(stripped)

    while sanitized_lines and not sanitized_lines[-1]:
        sanitized_lines.pop()

    return "\n".join(sanitized_lines).strip()


def coerce_commit_message(response: str, status: str, is_initial_commit: bool = False) -> str:
    """Convert imperfect model output into a usable commit message when possible."""

    cleaned = clean_commit_response(response)
    if looks_like_commit_message(cleaned):
        return cleaned

    if not cleaned:
        return build_fallback_commit_message(status, is_initial_commit=is_initial_commit)

    narrative_lines = []
    bullets = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("-", "*", "•")):
            bullets.append("- " + stripped.lstrip("-*• "))
        else:
            narrative_lines.append(stripped)

    subject = build_fallback_commit_subject(status, is_initial_commit=is_initial_commit)
    summary_lines = narrative_lines
    if narrative_lines and _is_plausible_commit_subject(narrative_lines[0]):
        subject = _truncate_commit_subject(narrative_lines[0])
        summary_lines = narrative_lines[1:]

    body_parts = []
    if summary_lines:
        body_parts.append(" ".join(summary_lines))
    if bullets:
        body_parts.append("\n".join(bullets[:8]))

    if not body_parts:
        return subject
    return f"{subject}\n\n" + "\n\n".join(body_parts)


def looks_like_commit_message(response: str) -> bool:
    """Heuristic guard to reject review-style output in commit workflow."""

    cleaned = clean_commit_response(response)
    if not cleaned:
        return False

    lowered = cleaned.lower()
    if any(phrase in lowered for phrase in _INVALID_COMMIT_PHRASES):
        return False

    first_line = cleaned.splitlines()[0].strip()
    if not first_line:
        return False
    if len(first_line) > 90:
        return False
    if first_line.startswith(("-", "*", "•")):
        return False
    if first_line.endswith("."):
        return False
    if first_line.endswith("?"):
        return False

    disallowed_prefixes = (
        "backend",
        "frontend",
        "missing/todo",
        "overall",
        "observations",
    )
    if any(first_line.lower().startswith(prefix) for prefix in disallowed_prefixes):
        return False

    return True


def build_mapping_prompt(
    epic_title: str,
    issues: List[Dict],
    project_structure: str,
) -> str:
    """Build prompt for LLM to map code paths to issues."""
    issues_text = "\n".join(f"  - Issue #{i['iid']}: {i['title']}\n    Description: {i['description'][:200] if i['description'] else 'N/A'}" for i in issues)
    return f"""You are analyzing a software project to map code paths to GitLab issues.

Epic: {epic_title}

Child Issues:
{issues_text}

Project Structure:
{project_structure}

Task: For each issue, identify which directories/files in the project are most relevant.
Output JSON only, no explanation. Format:
{{
  "mappings": [
    {{"issue_iid": 123, "paths": ["app/api/", "app/ingest/"], "reason": "brief reason"}}
  ],
  "epic_paths": ["list of paths relevant to the overall epic"]
}}

Rules:
- Use directory paths ending with / for entire directories
- Use specific file paths for individual files
- Each issue should have 1-5 relevant paths
- Be specific - don't just map everything to root
- Consider the issue title and description to infer relevance
"""


def _clean_commit_message(msg: str) -> str:
    """Clean up malformed AI-generated commit messages."""
    # Strip common AI output prefixes
    prefixes_to_strip = [
        "```",
        "Here is the commit message:",
        "Here are the key details in the commit:",
        "Executive Summary:",
        "Executive summary:",
        "This commit contains several changes related to",
        "```diff",
    ]

    cleaned = msg.strip()
    for prefix in prefixes_to_strip:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()

    # If message is now empty or too short, use a placeholder
    if len(cleaned) < 5:
        cleaned = "(commit message unavailable)"

    return cleaned


def build_status_update_prompt(
    issue: Dict,
    commits: List[Dict],
    current_status_label: Optional[str],
) -> str:
    """Build prompt for generating issue status update."""
    commits_text = "\n".join(f"  - {c['date']} [{c['hash']}] {c['message']} ({c['author']})" for c in commits[:10]) if commits else "  No recent commits"

    current_label_display = current_status_label or "None"
    valid_labels_list = "\n".join(f"  - {label}" for label in VALID_STATUS_LABELS)

    issue_state = issue.get("state", "opened")
    state_context = ""
    if issue_state == "closed":
        state_context = """
IMPORTANT: This issue is currently CLOSED. If there are recent commits:
- The comment should acknowledge the issue was previously completed but has new activity
- Use phrasing like "Additional work has been done on this completed issue..." or "Follow-up commits were made..."
- Do NOT suggest reopening unless the commits clearly indicate the feature needs rework
"""

    return f"""Generate a brief status update comment for this GitLab issue.

Issue: #{issue['iid']} - {issue['title']}
Current Status Label: {current_label_display}
Issue State: {issue_state}
Labels: {', '.join(issue.get('labels', [])) or 'None'}
{state_context}
Recent Commits (last 7 days):
{commits_text}

CRITICAL RULES FOR ACCURACY:
- Your comment MUST reference SPECIFIC details from the commit messages above.
- NEVER use generic phrases like "progress has been made", "work continues", "updates were applied".
- Instead, cite ACTUAL work: "Added validation for user input", "Fixed timeout handling in API client", etc.
- If commit messages mention specific functions, files, or features, include those names.
- If no commits exist, state clearly "No commits this week" - do not fabricate activity.

Generate a JSON response with:
1. "comment": A 2-3 sentence status update that cites SPECIFIC work from the commits
2. "suggested_label": The recommended status label based on progress

Valid status labels (use EXACTLY as shown, including "status::" prefix):
{valid_labels_list}
  - null (for no change)

Label selection rules:
- If issue is CLOSED and commits are minor/maintenance, use null (keep current state)
- Use "status::in-progress" if there are recent commits showing active work on an OPEN issue
- Use "status::complete" only if commits clearly indicate feature completion
- Use "status::blocked-internal" if commits mention internal blockers
- Use "status::blocked-external" if waiting on external dependencies
- Use "status::review-internal" if code is ready for internal review
- Use "status::review-external" if waiting on external review
- Use "status::not-started" if no work has begun
- Use null if current label should remain unchanged OR if issue is closed with only minor activity

Language rules for comment:
- Use direct, action-oriented language: "Work has progressed on...", "Development continued with...", "Completed work on..."
- For CLOSED issues with activity: "Follow-up work on this completed issue...", "Additional commits related to..."
- AVOID passive or uncertain language like "indicates", "appears", "seems", "suggests"
- State facts directly based on commit messages: "Added X", "Fixed Y", "No commits this week"

Output ONLY valid JSON, no preamble:
{{"comment": "your comment here", "suggested_label": "status::in-progress"}}
"""


def build_daily_summary_prompt(day_name: str, diff: str) -> str:
    """Build prompt for summarizing a single day's changes."""
    return (
        f"Summarize the following git changes from {day_name} in 2-3 sentences.\n"
        "Write like a practical teammate giving a quick standup update.\n"
        "Focus on what was accomplished, not individual file changes.\n\n"
        "CRITICAL: Extract SPECIFIC details from the diff:\n"
        "- Name functions, classes, or modules that were added/modified\n"
        "- Cite specific features or fixes (e.g., 'Added user authentication', 'Fixed null pointer in parser')\n"
        "- NEVER use vague phrases like 'various improvements' or 'code updates'\n"
        "- NEVER mention: README.md, .venv/.gitlab_epic_config.json\n"
        "- Avoid inflated or corporate language (for example: 'transformative', 'synergy', 'paradigm', 'robust framework', 'strategic initiative')\n"
        "- Prefer plain words and direct verbs: added, fixed, removed, simplified, tested\n\n"
        f"Diff:\n{diff}\n"
    )


def build_weekly_rollup_prompt(daily_summaries: dict[str, str]) -> str:
    """Build prompt for rolling up daily summaries into weekly summary."""
    summaries_text = "\n\n".join(f"{day}:\n{summary}" for day, summary in daily_summaries.items() if summary)
    return (
        "You are summarizing a week of software development work.\n"
        "Create a summary with:\n"
        "1) A 4-sentence plain-English summary of the week's accomplishments.\n"
        "2) A bulleted list of key changes, grouped by theme or feature.\n\n"
        "CRITICAL RULES:\n"
        "- Be concrete and specific about what was built or changed.\n"
        "- Reference ACTUAL function names, feature names, and module names from the daily summaries.\n"
        "- NEVER use generic phrases like 'various improvements', 'code enhancements', or 'updates made'.\n"
        "- Each bullet point should cite a SPECIFIC change (e.g., 'Added retry logic to API client', not 'Improved API handling').\n"
        "- NEVER mention: README.md, .venv/.gitlab_epic_config.json.\n"
        "- Focus on outcomes and features, not process.\n"
        "- Write in a natural, human tone that sounds like an engineer talking to teammates.\n"
        "- Avoid grand or abstract wording such as 'profound', 'revolutionary', 'holistic', 'comprehensive modernization', or similar hype language.\n"
        "- Keep sentences short and straightforward.\n"
        "- Output plain text, no markdown headers.\n\n"
        f"Daily summaries:\n{summaries_text}\n"
    )
