"""Configuration constants and static text for gitops_summary."""

from pathlib import Path

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

MAX_DIFF_CHARS = 120_000

MAX_TOKENS_COMMIT = 4000

MAX_TOKENS_WEEKLY = 1500

MAX_TOKENS_EPIC = 2000

SCRIPT_GENERATED_FILES = {
    ".venv/.gitlab_epic_config.json",
    "README.md",
    "git_summary.py",
    "src/gitops_summary/core.py",
}

EXCLUDED_SUMMARY_PATHS = {p.replace("\\", "/") for p in SCRIPT_GENERATED_FILES}

GITLAB_CONFIG_FILE = Path(".venv") / ".gitlab_epic_config.json"

VALID_STATUS_LABELS = [
    "status::blocked-external",
    "status::blocked-internal",
    "status::complete",
    "status::in-progress",
    "status::not-started",
    "status::review-external",
    "status::review-internal",
    "status::won't fix",
]

README_CONTENT = """# Git Summary Tool

A developer productivity tool that uses AWS Bedrock (Claude) to generate intelligent commit messages, weekly summaries, and manage GitLab epic tracking.

## Quick Start

```bash
# Generate commit message for current changes
gitops-summary commit

# Weekly summary of commits (last 7 days)
gitops-summary weekly

# Weekly summary by GitLab issues
gitops-summary weekly --issues

# Weekly summary for custom range (starts at date, includes N days)
gitops-summary weekly --start-date 2026-01-01 --days 7  # Jan 1-7 inclusive

# Setup GitLab epic tracking
gitops-summary epic --setup
```

## Requirements

- Python 3.11+
- AWS credentials with Bedrock access
- `boto3` and `python-gitlab` packages
- GitLab Personal Access Token (for epic features)

```bash
pip install boto3 python-gitlab
```

## Modes

### 1. Commit Mode

Generates AI-powered commit messages from staged/unstaged changes.

```bash
gitops-summary commit
```

- Detects untracked files and prompts to stage them
- Generates executive summary + per-file breakdown
- Optionally creates commit and pushes to remote

### 2. Weekly Mode

Summarizes the last 7 days of work (rolling window).

```bash
gitops-summary weekly                               # Commit-based summary
gitops-summary weekly --issues                      # Issue-based summary (requires epic setup)
gitops-summary weekly --start-date 2026-01-01 --days 7  # Custom range: Jan 1-7 inclusive
```

### 3. Epic Mode

Manages GitLab epic tracking with AI-assisted status updates.

```bash
gitops-summary epic --setup     # Initial configuration
gitops-summary epic --status    # View epic/issue status
gitops-summary epic --update    # Post AI status updates to issues
gitops-summary epic --map       # Re-map code paths to issues
gitops-summary epic --labels    # Debug: show status labels
```

#### Epic Update Workflow

The `--update` command provides manual control over all changes:

1. **Comment Review**: For each issue, choose to:
   - `[p]ost` - Post comment as-is
   - `[e]dit` - Edit before posting
   - `[s]kip` - Skip this issue

2. **Label Review**: Approve/reject each suggested label change

3. **State Review**: Approve/reject each suggested open/close change

## GitLab Token Setup

Create a Personal Access Token with these scopes:
- `api`
- `read_api`
- `read_repository`

Token URL: `https://YOUR_GITLAB/-/user_settings/personal_access_tokens`

## Configuration

Configuration is stored in `.venv/.gitlab_epic_config.json` and automatically added to `.gitignore`.

## AWS Credentials

Configure via:
- AWS CLI: `aws configure`
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- IAM role (if on AWS infrastructure)

## Other Commands

```bash
gitops-summary --manual       # Full user manual
gitops-summary --generate-md  # Regenerate README.md
gitops-summary --help         # Show help
```
"""

MANUAL_TEXT = """
================================================================================
                        GIT SUMMARY - USER MANUAL
================================================================================

OVERVIEW
--------
gitops-summary is a developer productivity tool that uses AWS Bedrock (Claude)
to generate intelligent summaries and manage GitLab epic tracking.

MODES
-----

1. COMMIT MODE (gitops-summary commit)

   Generates AI-powered commit messages from your current changes.

   Workflow:
   - Detects untracked files and prompts to stage them
   - Collects git status and diff
   - Sends to Claude for summary generation
   - Displays proposed commit message
   - Optionally creates commit and pushes to remote

   Requirements:
   - Uncommitted changes in your repository
   - AWS credentials configured for Bedrock access

2. WEEKLY MODE (gitops-summary weekly [options])

   Generates a summary of the last 7 days of work (rolling window).

   Options:
     (none)       Commit-based summary (rolling last 7 days)
     --issues     Issue-based summary (shows GitLab issues with activity)
     --start-date YYYY-MM-DD --days N  Custom date range (starts at date, includes N days)

   Commit-based (default):
   - Analyzes commits day by day (rolling last 7 days)
   - Generates daily summaries
   - Rolls up into weekly executive summary

   Issue-based (--issues):
   - Requires GitLab epic configuration (run epic --setup first)
   - Shows all issues with commit activity in the selected date window
   - Lists commits per issue with clickable links
   - Generates AI summary of work by issue/theme

   Output:
   - Executive summary of the week's accomplishments
   - For --issues: per-issue breakdown with commit links

3. EPIC MODE (gitops-summary epic [options])

   Manages GitLab epic tracking with AI-assisted status updates.

   Options:
     --setup    Initial configuration (GitLab URL, token, project, epic)
     --status   Display current epic and child issue status
     --update   Generate and post AI status comments to issues
     --map      Re-generate code path to issue mappings
     --labels   Debug: Show all status-related labels

   Setup Process:
   1. Prompts for GitLab instance URL
   2. Prompts for Personal Access Token (hidden input)
   3. Prompts for project path (namespace/project)
   4. Prompts for epic IID number
   5. Validates connection and permissions
   6. Optionally generates AI code path mappings

   Update Workflow (--update):
   The update command provides full manual control over all changes:

   1. COMMENT REVIEW - For each issue, you can:
      - [p]ost: Post the AI-generated comment as-is
      - [e]dit: Edit the comment before posting (enter text, press Enter twice)
      - [s]kip: Skip posting a comment to this issue

   2. LABEL REVIEW - For each suggested label change:
      - Prompted individually with [y/N] to approve or skip
      - Shows current label and suggested new label

   3. STATE REVIEW - For each suggested open/close change:
      - Prompted individually with [y/N] to approve or skip
      - Closed issues with activity suggest reopening (requires approval)
      - Issues marked complete suggest closing (requires approval)

   Note: Closed issues with minor activity will generate appropriate comments
   like "Follow-up work on this completed issue..." without suggesting reopening.

   Configuration Storage:
   - Stored in .venv/.gitlab_epic_config.json
   - Automatically added to .gitignore
   - Token is stored locally, never committed

REQUIREMENTS
------------
- Python 3.11+
- AWS credentials with Bedrock access (for all modes)
- python-gitlab package (for epic mode only, install separately)
- boto3 package

GITLAB TOKEN SCOPES
-------------------
For epic mode, create a Personal Access Token with these scopes:
- api
- read_api  
- read_repository

TOKEN URL: https://YOUR_GITLAB/-/user_settings/personal_access_tokens

ENVIRONMENT
-----------
AWS credentials should be configured via:
- AWS CLI (aws configure)
- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- IAM role (if running on AWS infrastructure)

FILES
-----
.venv/.gitlab_epic_config.json  - GitLab configuration (auto-generated)
.gitignore                      - Updated to exclude config file

================================================================================
"""

