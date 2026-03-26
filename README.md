# gitops-summary

`gitops-summary` is a practical CLI for day-to-day engineering workflows:

- Generate high-quality commit summaries from local diffs (with optional commit/push)
- Produce weekly development summaries
- Track and update GitLab epic child issues with AI-assisted status comments

It uses AWS Bedrock (Claude) for language generation and `python-gitlab` for epic/issue operations.

## Why this exists

This tool is meant to reduce repetitive status-writing and commit-message cleanup while keeping humans in control:

- You review generated messages before commit/posting
- Label/state changes in epic update flow are explicitly approved one-by-one
- Secrets stay local in `.venv/.gitlab_epic_config.json` (and are gitignored)

---

## Installation

### Prerequisites

- Python 3.10+
- Git CLI available in PATH
- AWS credentials with Bedrock invoke permissions
- (Epic mode) GitLab Personal Access Token with:
  - `api`
  - `read_api`
  - `read_repository`

### Install locally (editable, recommended for development)

```bash
pip install -e .
```

If your pip/setuptools combo does not support editable installs in your environment, use standard install instead.

### Standard install

```bash
pip install .
```

After install, the CLI command is:

```bash
gitops-summary --help
```

You can also run as a module:

```bash
python -m gitops_summary --help
```

---

## Configuration

### AWS / Bedrock

Any normal AWS credential strategy works:

- `aws configure`
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.)
- IAM role (if running in AWS)

### GitLab (epic mode only)

Run the interactive setup:

```bash
gitops-summary epic --setup
```

This stores config in:

- `.venv/.gitlab_epic_config.json`

The tool also ensures relevant entries are in `.gitignore`.

---

## Daily Operations (Runbook)

## 1) Commit workflow

```bash
gitops-summary commit
```

What happens:

1. Detects staged/unstaged/untracked changes
2. Lets you choose staging behavior
3. Generates a commit summary from diff content
4. Asks for confirmation before committing
5. Optionally pushes (sets upstream if missing)

## 2) Weekly summary workflow

### Commit-based weekly summary

```bash
gitops-summary weekly
```

### Custom date window

```bash
gitops-summary weekly --start-date 2026-01-01 --days 7
```

### Issue-based weekly summary (requires epic setup)

```bash
gitops-summary weekly --issues
```

## 3) Epic tracking workflow

```bash
gitops-summary epic --status
gitops-summary epic --update
gitops-summary epic --map
gitops-summary epic --labels
```

`--update` is human-in-the-loop:

- Review/edit/skip each generated comment
- Approve label changes individually
- Approve close/reopen actions individually

---

## CLI reference

```bash
gitops-summary --manual
gitops-summary --generate-md

gitops-summary commit
gitops-summary weekly [--issues] [--start-date YYYY-MM-DD --days N]
gitops-summary epic [--setup|--status|--update|--map|--labels]
```

---

## Project structure

```text
.
├── pyproject.toml
├── README.md
└── src/
    └── gitops_summary/
        ├── __init__.py
        ├── __main__.py
        ├── bedrock.py
        ├── cli.py
        ├── commit.py
        ├── config.py
        ├── docs.py
        ├── engine.py
        ├── epic.py
        ├── git_ops.py
        ├── prompts.py
        ├── ui.py
        ├── weekly.py
        └── workflows/
            └── __init__.py
```

---

## Troubleshooting

- **`No module named gitops_summary`**
  - Ensure installation was run from project root: `pip install -e .`
- **Bedrock invocation errors**
  - Verify AWS credentials and Bedrock model access permissions
- **GitLab auth/setup failures**
  - Re-run `gitops-summary epic --setup` and confirm token scopes
- **No changes detected in commit mode**
  - Stage or modify files first, then rerun

---
