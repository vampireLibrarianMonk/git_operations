"""Engine compatibility module.

Implementation is modularized across commit/weekly/epic/git_ops/prompts/etc.
"""

from .cli import build_parser, main
from .commit import commit_workflow
from .docs import generate_readme, print_manual
from .epic import epic_workflow
from .weekly import resolve_weekly_date_range, weekly_issues_workflow, weekly_workflow

__all__ = [
    "build_parser",
    "main",
    "print_manual",
    "generate_readme",
    "commit_workflow",
    "resolve_weekly_date_range",
    "weekly_workflow",
    "weekly_issues_workflow",
    "epic_workflow",
]
