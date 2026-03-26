"""CLI entrypoint and parser wiring for gitops_summary."""

from __future__ import annotations

import argparse

from .commit import commit_workflow
from .docs import generate_readme, print_manual
from .epic import epic_workflow
from .weekly import resolve_weekly_date_range, weekly_issues_workflow, weekly_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Git summary generator with GitLab epic tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitops-summary commit              # Summarize and commit changes
  gitops-summary weekly              # Weekly summary (last 7 days)
  gitops-summary weekly --issues     # Weekly summary (issue-based)
  gitops-summary weekly --start-date 2026-01-01 --days 7  # Custom range (Jan 1-7 inclusive)
  gitops-summary epic --setup        # Configure GitLab epic tracking
  gitops-summary epic --status       # View epic/issue status
  gitops-summary epic --update       # Post AI status updates (with manual review)
  gitops-summary epic --map          # Re-map code paths to issues
  gitops-summary epic --labels       # Debug: show status labels
  gitops-summary --manual            # Show full user manual
  gitops-summary --generate-md       # Generate README file

Update workflow (--update):
  Each comment, label change, and state change is reviewed individually.
  Comments: [p]ost / [e]dit / [s]kip
  Labels & States: [y/N] for each change
        """,
    )

    parser.add_argument("--manual", action="store_true", help="Display full user manual")
    parser.add_argument("--generate-md", action="store_true", help="Generate README.md file")

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    subparsers.add_parser("commit", help="Summarize current changes and commit")

    weekly_parser = subparsers.add_parser("weekly", help="Summarize last 7 days (rolling window)")
    weekly_parser.add_argument("--issues", action="store_true", help="Generate report based on GitLab issues with activity")
    weekly_parser.add_argument("--start-date", help="Start date (YYYY-MM-DD) for custom range (inclusive)")
    weekly_parser.add_argument("--days", type=int, help="Number of days to include starting from start-date (inclusive)")

    epic_parser = subparsers.add_parser("epic", help="GitLab epic tracking")
    epic_parser.add_argument("--setup", action="store_true", help="Initial setup (token, URL, epic)")
    epic_parser.add_argument("--status", action="store_true", help="Show epic and child issue status")
    epic_parser.add_argument("--update", action="store_true", help="Update child issues with AI comments")
    epic_parser.add_argument("--map", action="store_true", help="Re-map code paths to issues")
    epic_parser.add_argument("--labels", action="store_true", help="Debug: Show all status-related labels")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.manual:
        return print_manual()
    if args.generate_md:
        return generate_readme()

    if args.mode == "commit":
        return commit_workflow()
    if args.mode == "weekly":
        try:
            start_date, end_date = resolve_weekly_date_range(args.start_date, args.days)
        except ValueError as exc:
            print(f"[weekly] Error: {exc}")
            return 1
        if getattr(args, "issues", False):
            return weekly_issues_workflow(start_date, end_date)
        return weekly_workflow(start_date, end_date)
    if args.mode == "epic":
        return epic_workflow(args)

    parser.print_help()
    return 0
