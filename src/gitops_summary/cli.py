"""CLI entrypoint and parser wiring for gitops_summary."""

from __future__ import annotations

import argparse

from .benchmark import benchmark_workflow, check_benchmark_staleness, print_leaderboard
from .commit import commit_workflow
from .diagram_prompts import get_supported_diagram_types
from .diagrams import diagrams_workflow
from .docs import generate_readme, print_manual
from .epic import epic_workflow
from .model import model_workflow
from .weekly import resolve_weekly_date_range, scrum_workflow, weekly_issues_workflow, weekly_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Git summary generator with GitLab epic tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitops commit              # Summarize and commit changes
  gitops weekly              # Weekly summary (last 7 days)
  gitops weekly --issues     # Weekly summary (issue-based)
  gitops weekly --since 2026-06-01 --until 2026-06-07 --paragraphs 2
  gitops weekly --start-date 2026-01-01 --days 7  # Custom range (Jan 1-7 inclusive)
  gitops scrum               # Standup update (3x/week cadence)
  gitops scrum --frequency 5 # Daily standup (1-day lookback)
  gitops benchmark           # Evaluate models (minimal tier)
  gitops benchmark --tier standard --repos ../other_repo .
  gitops benchmark --leaderboard
  gitops benchmark --auto-select
  gitops model               # Manually pick a Bedrock model
  gitops epic --setup        # Configure GitLab epic tracking
  gitops epic --status       # View epic/issue status
  gitops epic --update       # Post AI status updates (with manual review)
  gitops epic --map          # Re-map code paths to issues
  gitops epic --labels       # Debug: show status labels
  gitops diagrams            # Generate PlantUML diagrams for the repo
  gitops diagrams --list-types
  gitops diagrams --type architecture --type sequence --format svg
  gitops --manual            # Show full user manual
  gitops --generate-md       # Generate README file
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__import__('gitops_summary').__version__}",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Display full user manual",
    )
    parser.add_argument(
        "--generate-md",
        action="store_true",
        help="Generate README.md file",
    )

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    subparsers.add_parser("commit", help="Summarize current changes and commit")

    weekly_parser = subparsers.add_parser(
        "weekly",
        help="Summarize last 7 days (rolling window)",
    )
    weekly_parser.add_argument(
        "--issues",
        action="store_true",
        help="Generate report based on GitLab issues with activity",
    )
    weekly_parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD) for custom range (inclusive)",
    )
    weekly_parser.add_argument(
        "--days",
        type=int,
        help="Number of days to include starting from start-date (inclusive)",
    )
    weekly_parser.add_argument(
        "--since",
        help="Start datetime (YYYY-MM-DD or YYYY-MM-DDTHH:MM)",
    )
    weekly_parser.add_argument(
        "--until",
        help="End datetime (YYYY-MM-DD or YYYY-MM-DDTHH:MM, default: now)",
    )
    weekly_parser.add_argument(
        "--paragraphs",
        type=int,
        default=3,
        choices=range(1, 6),
        metavar="N",
        help="Number of paragraphs in the summary (1-5, default: 3)",
    )

    scrum_parser = subparsers.add_parser(
        "scrum",
        help="Interactive standup/scrum summary generator",
    )
    scrum_parser.add_argument(
        "--frequency",
        type=int,
        default=3,
        choices=range(1, 8),
        metavar="N",
        help="Scrums per week (1-7, default: 3). Determines the lookback window per scrum.",
    )

    epic_parser = subparsers.add_parser("epic", help="GitLab epic tracking")
    epic_parser.add_argument(
        "--setup",
        action="store_true",
        help="Initial setup (token, URL, epic)",
    )
    epic_parser.add_argument(
        "--status",
        action="store_true",
        help="Show epic and child issue status",
    )
    epic_parser.add_argument(
        "--update",
        action="store_true",
        help="Update child issues with AI comments",
    )
    epic_parser.add_argument(
        "--map",
        action="store_true",
        help="Re-map code paths to issues",
    )
    epic_parser.add_argument(
        "--labels",
        action="store_true",
        help="Debug: Show all status-related labels",
    )

    subparsers.add_parser("model", help="Change the Bedrock model used for generation")

    bench_parser = subparsers.add_parser(
        "benchmark",
        help="Evaluate models for commit message quality and cost",
    )
    bench_parser.add_argument(
        "--repos",
        nargs="+",
        default=None,
        help="Repository paths to pull test commits from (default: current dir)",
    )
    bench_parser.add_argument(
        "--commits",
        type=int,
        default=3,
        help="Number of recent commits per repo to test (default: 3)",
    )
    bench_parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Max concurrent API calls (default: min(cpu_count, 8))",
    )
    bench_parser.add_argument(
        "--tier",
        choices=["minimal", "quick", "standard", "thorough", "exhaustive"],
        default="minimal",
        help="Model set: minimal (3), quick (6), standard (10), thorough (15), exhaustive (20)",
    )
    bench_parser.add_argument(
        "--leaderboard",
        action="store_true",
        help="Show current leaderboard without running new trials",
    )
    bench_parser.add_argument(
        "--auto-select",
        action="store_true",
        help="Set the best-scoring model as the active model",
    )

    diagrams_parser = subparsers.add_parser(
        "diagrams",
        help="Generate or render PlantUML diagrams",
    )
    diagrams_parser.add_argument(
        "--repo",
        default=".",
        help="Path to the repository to analyze (default: current directory)",
    )
    diagrams_parser.add_argument(
        "--output",
        default="docs/diagrams",
        help="Directory for .puml and rendered files",
    )
    diagrams_parser.add_argument(
        "--type",
        dest="diagram_types",
        action="append",
        choices=get_supported_diagram_types(),
        help="Diagram type to generate (repeatable)",
    )
    diagrams_parser.add_argument(
        "--format",
        dest="output_format",
        default="png",
        choices=["png", "svg", "txt"],
        help="Rendered output format",
    )
    diagrams_parser.add_argument(
        "--model",
        default=None,
        help="Override the Bedrock model ID",
    )
    diagrams_parser.add_argument(
        "--render-only",
        action="store_true",
        help="Render existing PlantUML source files without calling Bedrock",
    )
    diagrams_parser.add_argument(
        "--list-types",
        action="store_true",
        help="List supported diagram types and exit",
    )

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
            start_date, end_date = resolve_weekly_date_range(
                args.start_date,
                args.days,
                since=args.since,
                until=args.until,
            )
        except ValueError as exc:
            print(f"[weekly] Error: {exc}")
            return 1
        if getattr(args, "issues", False):
            return weekly_issues_workflow(start_date, end_date)
        return weekly_workflow(start_date, end_date, paragraphs=args.paragraphs)
    if args.mode == "scrum":
        return scrum_workflow(frequency=args.frequency)
    if args.mode == "epic":
        return epic_workflow(args)
    if args.mode == "model":
        return model_workflow()
    if args.mode == "benchmark":
        if args.leaderboard:
            print_leaderboard()
            return 0
        if args.auto_select:
            from .benchmark import get_best_model, load_scores
            from .model import save_model_id

            best = get_best_model(load_scores())
            if best:
                save_model_id(best)
                print(f"✓ Auto-selected: {best}")
                return 0
            print("Not enough data. Run 'gitops benchmark' first.")
            return 1
        return benchmark_workflow(repos=args.repos, commits_per_repo=args.commits, tier=args.tier, workers=args.workers)
    if args.mode == "diagrams":
        return diagrams_workflow(args)

    parser.print_help()
    stale = check_benchmark_staleness()
    if stale:
        print(f"\n💡 {stale}")
    return 0
