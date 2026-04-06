"""Git command and diff/status utilities."""

import subprocess  # nosec B404
from typing import List

from .config import EXCLUDED_SUMMARY_PATHS, SCRIPT_GENERATED_FILES
from .ui import prompt_yes_no


def run_git_command(args: List[str], input_text: str | None = None) -> str:
    result = subprocess.run(  # nosec
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed: git {' '.join(args)}\n{result.stderr.strip()}",
        )
    return result.stdout.strip()


def run_git_command_allow_failure(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # nosec
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def is_initial_commit() -> bool:
    """Return True when the repository does not yet have a HEAD commit."""
    result = run_git_command_allow_failure(["rev-parse", "--verify", "HEAD"])
    return result.returncode != 0


def get_untracked_files() -> List[str]:
    """Get list of untracked files from git status."""
    result = run_git_command_allow_failure(["status", "--porcelain"])
    if result.returncode != 0 or not result.stdout.strip():
        return []
    untracked = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith("??"):
            untracked.append(line[3:])
    return untracked


def is_script_generated_file(filepath: str) -> bool:
    """Return True if path is generated/managed by this script."""
    normalized = filepath.strip().replace("\\", "/")
    return normalized in SCRIPT_GENERATED_FILES


def is_excluded_summary_path(filepath: str) -> bool:
    """Return True if a path should be excluded from all generated summaries."""
    normalized = filepath.strip().replace("\\", "/")
    return normalized in EXCLUDED_SUMMARY_PATHS


def _extract_path_from_diff_header(line: str) -> str:
    """Extract path from a unified diff header line."""
    # Example: diff --git a/app/file.py b/app/file.py
    parts = line.strip().split()
    if len(parts) >= 4 and parts[0] == "diff" and parts[1] == "--git":
        b_path = parts[3]
        if b_path.startswith("b/"):
            return b_path[2:]
        return b_path
    return ""


def filter_status_output(status_text: str) -> str:
    """Remove excluded paths from git status text."""
    kept: List[str] = []
    for line in status_text.splitlines():
        normalized_line = line.replace("\\", "/")
        if any(path in normalized_line for path in EXCLUDED_SUMMARY_PATHS):
            continue
        kept.append(line)
    return "\n".join(kept)


def filter_unified_diff_excluding_paths(diff_text: str) -> str:
    """Remove whole diff blocks for excluded files from unified git diff text."""
    if not diff_text.strip():
        return diff_text

    output_lines: List[str] = []
    current_block: List[str] = []
    include_current_block = True

    for line in diff_text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            if current_block and include_current_block:
                output_lines.extend(current_block)
            current_block = [line]
            path = _extract_path_from_diff_header(line)
            include_current_block = not is_excluded_summary_path(path)
        else:
            if current_block:
                current_block.append(line)
            else:
                output_lines.append(line)

    if current_block and include_current_block:
        output_lines.extend(current_block)

    return "".join(output_lines)


def git_exclude_pathspecs() -> List[str]:
    """Build git pathspec exclusions for files hidden from generated summaries."""
    return [f":(exclude){path}" for path in sorted(EXCLUDED_SUMMARY_PATHS)]


def remove_script_generated_files_from_index() -> List[str]:
    """Unstage script-generated files if they were staged."""
    staged_result = run_git_command_allow_failure(["diff", "--cached", "--name-only"])
    if staged_result.returncode != 0 or not staged_result.stdout.strip():
        return []

    staged_paths = [p.strip() for p in staged_result.stdout.splitlines() if p.strip()]
    to_unstage = [p for p in staged_paths if is_script_generated_file(p)]
    if not to_unstage:
        return []

    # Keep files in working tree, but remove from staged commit set.
    restore_result = run_git_command_allow_failure(
        ["restore", "--staged", "--", *to_unstage],
    )
    if restore_result.returncode != 0:
        # Fallback for environments where restore may not be available/compatible.
        run_git_command_allow_failure(["reset", "HEAD", "--", *to_unstage])

    return to_unstage


def get_new_files_from_staged() -> List[str]:
    """Get list of newly added files from staged changes (files that don't exist in HEAD)."""
    result = run_git_command_allow_failure(["diff", "--cached", "--name-status"])
    if result.returncode != 0 or not result.stdout.strip():
        return []
    new_files = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith("A\t"):
            candidate = line[2:]
            if not is_excluded_summary_path(candidate):
                new_files.append(candidate)
    return new_files


def read_file_content(filepath: str, max_chars: int = 10000) -> str:
    """Read file content, truncating if too large."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
            if len(content) == max_chars:
                content += "\n... (file truncated)"
            return content
    except Exception as exc:
        return f"[Could not read file: {exc}]"


def handle_untracked_files() -> tuple[List[str], str]:
    """Prompt user to stage untracked files one by one."""
    untracked = [f for f in get_untracked_files() if not is_script_generated_file(f)]
    if not untracked:
        return [], ""

    print(f"\n[git-commit-summary] Found {len(untracked)} untracked file(s):")
    staged_files = []
    untracked_content = []

    for filepath in untracked:
        print(f"\n  Untracked: {filepath}")
        if prompt_yes_no(f"  Stage '{filepath}' for commit?"):
            run_git_command(["add", filepath])
            staged_files.append(filepath)
            content = read_file_content(filepath)
            untracked_content.append(f"[NEW FILE: {filepath}]\n{content}")
            print(f"    Staged: {filepath}")
        else:
            print(f"    Skipped: {filepath}")

    content_str = "\n\n".join(untracked_content) if untracked_content else ""
    return staged_files, content_str
