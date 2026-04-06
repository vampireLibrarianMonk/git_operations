"""Commit message generation workflow."""

import sys

from .bedrock import call_bedrock
from .config import MAX_DIFF_CHARS
from .git_ops import (
    filter_status_output,
    filter_unified_diff_excluding_paths,
    get_new_files_from_staged,
    get_untracked_files,
    handle_untracked_files,
    is_initial_commit,
    is_script_generated_file,
    remove_script_generated_files_from_index,
    run_git_command,
    run_git_command_allow_failure,
)
from .prompts import build_prompt, clean_commit_response
from .ui import prompt_yes_no


def commit_workflow() -> int:
    """Original workflow: summarize uncommitted changes and optionally commit."""
    # First, check if there are any changes at all
    try:
        print("[git-commit-summary] Checking for changes...")
        status_check = run_git_command(["status", "--porcelain"])
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not status_check.strip():
        print("No changes detected. Make changes before generating a message.")
        return 0

    # Check for unstaged tracked changes and staged changes
    try:
        unstaged_diff = run_git_command(["diff"])
        staged_diff = run_git_command(["diff", "--cached"])
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    # Get untracked files
    untracked_all = get_untracked_files()
    untracked = [f for f in untracked_all if not is_script_generated_file(f)]
    excluded_untracked = [f for f in untracked_all if is_script_generated_file(f)]

    # If there are unstaged tracked changes or untracked files, ask user how to proceed
    has_unstaged = bool(unstaged_diff.strip())
    has_untracked = bool(untracked)
    has_staged = bool(staged_diff.strip())

    if has_unstaged or has_untracked:
        print("\n[git-commit-summary] Found uncommitted changes:")
        if has_staged:
            print("  - Staged changes (ready to commit)")
        if has_unstaged:
            print("  - Unstaged tracked file changes")
        if has_untracked:
            print(f"  - {len(untracked)} untracked file(s)")
        if excluded_untracked:
            print(
                f"  - {len(excluded_untracked)} script-generated untracked file(s) (auto-excluded)",
            )

        print("\nHow would you like to proceed?")
        print("  [a] Stage ALL changes (tracked + untracked) and generate summary")
        print("  [s] Select which files to stage interactively")
        if has_staged:
            print("  [c] Continue with only currently staged changes")
        print("  [q] Quit")

        choice = input("\nChoice [a/s/c/q]: ").strip().lower()

        if choice == "q":
            print("Aborted.")
            return 0
        elif choice == "a":
            print("[git-commit-summary] Staging all changes...")
            run_git_command(["add", "-A"])
        elif choice == "s":
            # Handle untracked files first
            staged_untracked, untracked_content = handle_untracked_files()
            if staged_untracked:
                print(
                    f"\n[git-commit-summary] Staged {len(staged_untracked)} new file(s)",
                )

            # Now handle unstaged tracked changes
            if has_unstaged:
                if prompt_yes_no("\nStage all tracked file changes?"):
                    run_git_command(["add", "-u"])
                    print("[git-commit-summary] Staged tracked changes")
        elif choice == "c" and has_staged:
            print("[git-commit-summary] Continuing with staged changes only...")
        else:
            print("Invalid choice. Aborted.")
            return 0

    # Safety guard: never include script-generated files in the commit set.
    excluded_staged = remove_script_generated_files_from_index()
    if excluded_staged:
        print("[git-commit-summary] Auto-excluded script-generated files from commit:")
        for p in excluded_staged:
            print(f"  - {p}")

    # Now collect the final state for summary generation
    try:
        print("[git-commit-summary] Collecting git status...")
        status = run_git_command(["status", "-sb"])
        print("[git-commit-summary] Collecting git diff...")
        staged_diff = run_git_command(["diff", "--cached"])
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    status = filter_status_output(status)
    staged_diff = filter_unified_diff_excluding_paths(staged_diff)

    if not staged_diff.strip():
        print("No staged changes to commit (script-generated files are auto-excluded).")
        return 0

    # Get list of newly added files (to distinguish from modifications)
    new_files = get_new_files_from_staged()
    initial_commit = is_initial_commit()

    if len(staged_diff) > MAX_DIFF_CHARS:
        staged_diff = staged_diff[:MAX_DIFF_CHARS] + "\n... (diff truncated)"

    print("[git-commit-summary] Preparing prompt...")
    prompt = build_prompt(
        status,
        staged_diff,
        new_files,
        is_initial_commit=initial_commit,
    )
    try:
        print("[git-commit-summary] Sending request to Bedrock...")
        message = call_bedrock(prompt)
    except Exception as exc:
        print(f"Bedrock request failed: {exc}", file=sys.stderr)
        return 1

    message = clean_commit_response(message)
    print(message)

    if not prompt_yes_no("Use this message to create a commit?"):
        return 0

    try:
        print("[git-commit-summary] Creating commit...")
        run_git_command(["commit", "-F", "-"], input_text=message)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not prompt_yes_no("Commit created. Push to remote?"):
        return 0

    print("[git-commit-summary] Checking upstream...")
    upstream_check = run_git_command_allow_failure(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
    )
    if upstream_check.returncode == 0:
        print("[git-commit-summary] Running git push...")
        run_git_command(["push"])
        return 0

    print("[git-commit-summary] No upstream found. Setting upstream and pushing...")
    branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    run_git_command(["push", "--set-upstream", "origin", branch])
    return 0
