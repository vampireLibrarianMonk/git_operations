"""Weekly summary workflows."""

from datetime import datetime, timedelta
from typing import List, Optional

from .bedrock import call_bedrock
from .config import MAX_DIFF_CHARS, MAX_TOKENS_WEEKLY
from .epic import get_epic_issues, get_gitlab_client, get_recent_commits_for_paths, load_gitlab_config, _get_current_status_label
from .git_ops import git_exclude_pathspecs, run_git_command_allow_failure
from .prompts import build_daily_summary_prompt, build_weekly_rollup_prompt
from .ui import Spinner

def parse_start_date(date_str: str) -> datetime:
    """Parse YYYY-MM-DD into a datetime at 00:00:00."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError as exc:
        raise ValueError("start-date must be in YYYY-MM-DD format") from exc

def resolve_weekly_date_range(
        start_date_str: Optional[str],
        days: Optional[int],
) -> tuple[datetime, datetime]:
    """Resolve the weekly date range using optional start-date/days overrides.

    When --start-date and --days are provided, returns a range starting at
    start_date and including exactly 'days' number of days (inclusive).
    E.g., --start-date 2026-01-01 --days 7 covers Jan 1-7 inclusive.
    """
    if start_date_str or days is not None:
        if not start_date_str or days is None:
            raise ValueError("Both --start-date and --days are required together")
        if days <= 0:
            raise ValueError("--days must be a positive integer")
        start_date = parse_start_date(start_date_str)
        end_date = start_date + timedelta(days=days)
        return start_date, end_date

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date

def iter_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Build a list of day-start datetimes within [start_date, end_date)."""
    end_inclusive = (end_date - timedelta(seconds=1)).date()
    current_date = start_date.date()
    days = []
    while current_date <= end_inclusive:
        days.append(datetime.combine(current_date, datetime.min.time()))
        current_date += timedelta(days=1)
    return days

def get_commits_for_day(date: datetime) -> List[str]:
    """Get commit hashes for a specific day."""
    # Use --since (inclusive) and --until (inclusive) with date-only format
    # to capture all commits on this day
    day_str = date.strftime("%Y-%m-%d")
    next_day_str = (date + timedelta(days=1)).strftime("%Y-%m-%d")
    result = run_git_command_allow_failure([
        "log",
        f"--since={day_str}",
        f"--until={next_day_str}",
        "--format=%H",
        "--",
        ".",
        *git_exclude_pathspecs(),
    ])
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return result.stdout.strip().split("\n")

def get_diff_for_commits(commits: List[str]) -> str:
    """Get combined diff for a list of commits."""
    if not commits:
        return ""
    oldest = commits[-1]
    newest = commits[0]
    result = run_git_command_allow_failure([
        "diff",
        f"{oldest}^..{newest}",
        "--",
        ".",
        *git_exclude_pathspecs(),
    ])
    if result.returncode != 0:
        diffs = []
        for commit in commits:
            r = run_git_command_allow_failure([
                "show",
                "--stat",
                commit,
                "--",
                ".",
                *git_exclude_pathspecs(),
            ])
            if r.returncode == 0:
                diffs.append(r.stdout)
        return "\n".join(diffs)
    return result.stdout

def weekly_issues_workflow(start_date: datetime, end_date: datetime) -> int:
    """Generate weekly report based on GitLab issues with activity."""
    config = load_gitlab_config()
    if not config:
        print("[weekly-issues] No GitLab configuration found. Run: gitops-summary epic --setup")
        return 1

    print("\n" + "=" * 60)
    print(f"Weekly Issues Report: {config['epic_title']}")
    print("=" * 60)

    # Connect to GitLab
    spinner = Spinner("[weekly-issues] Connecting to GitLab...")
    spinner.start()
    gl = get_gitlab_client(config["url"], config["token"])
    try:
        gl.auth()
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(f"[weekly-issues] Authentication failed: {e}")
        return 1

    # Get issues
    spinner.start("[weekly-issues] Fetching issues...")
    issues = get_epic_issues(gl, config["group_id"], config["epic_iid"], config.get("project_id"))
    spinner.stop()

    mappings = config.get("mappings", {}).get("mappings", [])
    mapping_lookup = {m["issue_iid"]: m["paths"] for m in mappings}

    if not issues:
        print("[weekly-issues] No child issues found.")
        return 0

    # Build commit URL base
    commit_url_base = f"{config['url']}/{config['project_path']}/-/commit"
    issue_url_base = f"{config['url']}/{config['project_path']}/-/issues"

    # Collect issues with activity
    print(f"\n[weekly-issues] Analyzing {len(issues)} issues for recent activity...")
    print(f"  Commit window: {start_date.date()} to {end_date.date()} (exclusive end)")

    issues_with_activity = []
    for issue in issues:
        paths = mapping_lookup.get(issue["iid"], [])
        commits = (
            get_recent_commits_for_paths(paths, start_date=start_date, end_date=end_date)
            if paths else []
        )

        if commits:
            issues_with_activity.append({
                "issue": issue,
                "commits": commits,
                "paths": paths,
            })

    if not issues_with_activity:
        print("\n[weekly-issues] No issues with recent commit activity found.")
        return 0

    # Sort by number of commits (most active first)
    issues_with_activity.sort(key=lambda x: len(x["commits"]), reverse=True)

    # Generate report
    print(f"\n[weekly-issues] Found {len(issues_with_activity)} issues with activity\n")
    print("=" * 60)
    print("ISSUES WITH ACTIVITY THIS WEEK")
    print("=" * 60)

    report_lines = []
    for item in issues_with_activity:
        issue = item["issue"]
        commits = item["commits"]

        # Get status label
        status_label = _get_current_status_label(issue.get('labels', []))
        status_display = status_label.split("::", 1)[1] if status_label else "No status"

        issue_url = f"{issue_url_base}/{issue['iid']}"

        print(f"\n#{issue['iid']}: {issue['title']}")
        print(f"  Status: {status_display}")
        print(f"  Commits: {len(commits)}")
        print(f"  URL: {issue_url}")

        # Show commit links
        print("  Recent commits:")
        for c in commits[:5]:
            commit_url = f"{commit_url_base}/{c['full_hash']}"
            print(f"    [{c['hash']}]({commit_url})")
        if len(commits) > 5:
            print(f"    ... and {len(commits) - 5} more")

        # Build report line for summary
        commit_links = " ".join([f"[{c['hash']}]({commit_url_base}/{c['full_hash']})" for c in commits[:5]])
        report_lines.append({
            "iid": issue["iid"],
            "title": issue["title"],
            "status": status_display,
            "commit_count": len(commits),
            "commits": commits,
        })

    # Generate AI summary of the week's work
    print("\n" + "=" * 60)
    print("GENERATING WEEKLY SUMMARY...")
    print("=" * 60)

    issues_summary_text = "\n".join([
        f"- Issue #{r['iid']}: {r['title']} ({r['status']}) - {r['commit_count']} commits"
        for r in report_lines
    ])

    summary_prompt = f"""Summarize the following work on a software project based on GitLab issues with activity.

Epic: {config['epic_title']}

Issues with commits this week:
{issues_summary_text}

Generate a 3-4 sentence plain-English summary of what was worked on this week.
Focus on themes and progress, not individual commits.
Write like a teammate's weekly update: clear, grounded, and specific.
Avoid lofty language or summary jargon (e.g., 'transformative', 'strategic', 'holistic', 'profound').
Prefer direct verbs and concrete nouns.
Output plain text only, no markdown headers.
"""

    try:
        spinner.start("[weekly-issues] Generating summary...")
        weekly_summary = call_bedrock(summary_prompt, max_tokens=500).strip()
        spinner.stop()

        print("\n" + weekly_summary)
    except Exception as e:
        spinner.stop()
        print(f"\n[weekly-issues] Failed to generate summary: {e}")

    print("\n" + "=" * 60)
    return 0

def weekly_workflow(start_date: datetime, end_date: datetime) -> int:
    """Summarize all commits from the resolved weekly date range."""
    print(f"[git-weekly-summary] Analyzing commits from {start_date.date()} to {end_date.date()} (exclusive end)")

    daily_summaries: dict[str, str] = {}
    for day_date in iter_date_range(start_date, end_date):
        day_name = day_date.strftime("%A")

        print(f"[git-weekly-summary] Processing {day_name}...")
        commits = get_commits_for_day(day_date)
        if not commits:
            print(f"  No commits on {day_name}")
            continue

        print(f"  Found {len(commits)} commit(s)")
        diff = get_diff_for_commits(commits)
        if not diff.strip():
            continue

        if len(diff) > MAX_DIFF_CHARS:
            diff = diff[:MAX_DIFF_CHARS] + "\n... (truncated)"

        try:
            prompt = build_daily_summary_prompt(day_name, diff)
            summary = call_bedrock(prompt).strip()
            daily_summaries[day_name] = summary
            print(f"  {day_name}: {summary[:80]}...")
        except Exception as exc:
            print(f"  Failed to summarize {day_name}: {exc}")

    if not daily_summaries:
        print("No commits found for this date range.")
        return 0

    print("\n[git-weekly-summary] Generating weekly rollup...")
    try:
        rollup_prompt = build_weekly_rollup_prompt(daily_summaries)
        weekly_summary = call_bedrock(rollup_prompt, max_tokens=MAX_TOKENS_WEEKLY).strip()
    except Exception as exc:
        print(f"Bedrock request failed: {exc}", file=sys.stderr)
        return 1

    print("\n" + "=" * 60)
    print("WEEKLY SUMMARY")
    print("=" * 60)
    print(weekly_summary)
    print("=" * 60)

    return 0

