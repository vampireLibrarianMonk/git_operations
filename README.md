# gitops-summary

`gitops-summary` is a practical CLI for day-to-day engineering workflows:

- Generate high-quality commit summaries from local diffs (with optional commit/push)
- Produce weekly development summaries
- Track and update GitLab epic child issues with AI-assisted status comments
- Generate and render PlantUML diagrams from repository context

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
- (Diagrams mode) Java runtime plus PlantUML command or jar for rendering
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

### Install directly from GitHub

Use pip's VCS URL format, not the plain repository URL:

```bash
pip install "git+https://github.com/vampireLibrarianMonk/git_operations.git"
```

Why: `pip install https://github.com/...` downloads the GitHub HTML page/repo endpoint, which is not a Python source archive, so pip cannot unpack it. The `git+https://...` form tells pip to clone the repository and build/install the package from `pyproject.toml`.

After install, the CLI command is:

```bash
gitops-summary --help
```

You can also run as a module:

```bash
python -m gitops_summary --help
```

### PlantUML setup for diagrams mode

The easiest setup is Java + the PlantUML jar file.

- You do not need `apt install plantuml`
- For the diagram types used here, Graphviz is not required
- The CLI already forces headless mode during rendering with `JAVA_TOOL_OPTIONS=-Djava.awt.headless=true`

#### Ubuntu / Debian

```bash
sudo apt-get install -y default-jre-headless wget
wget -O /tmp/plantuml.jar "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
export PLANTUML_JAR=/tmp/plantuml.jar
JAVA_TOOL_OPTIONS="-Djava.awt.headless=true" java -jar /tmp/plantuml.jar -version
```

#### Amazon Linux 2

```bash
sudo yum install -y java-17-amazon-corretto-headless wget
wget -O /tmp/plantuml.jar "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
export PLANTUML_JAR=/tmp/plantuml.jar
JAVA_TOOL_OPTIONS="-Djava.awt.headless=true" java -jar /tmp/plantuml.jar -version
```

#### Windows (PowerShell)

```powershell
winget install EclipseAdoptium.Temurin.17.JRE
Invoke-WebRequest -OutFile $env:TEMP\plantuml.jar -Uri "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
$env:PLANTUML_JAR = "$env:TEMP\plantuml.jar"
[Environment]::SetEnvironmentVariable('PLANTUML_JAR', "$env:TEMP\plantuml.jar", 'User')
$env:JAVA_TOOL_OPTIONS = '-Djava.awt.headless=true'
java -jar $env:TEMP\plantuml.jar -version
```

Manual render example:

```bash
JAVA_TOOL_OPTIONS="-Djava.awt.headless=true" java -jar /tmp/plantuml.jar -tpng docs/diagrams/architecture.puml
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

## 4) Diagrams workflow

The `diagrams` command analyzes a repository, asks Bedrock to generate PlantUML, writes the `.puml` source files, and then renders them to an output format such as PNG or SVG.

### What you need before running it

1. AWS credentials with Bedrock access
2. The project dependencies installed
3. Java + the PlantUML jar available

Recommended verification before first use:

```bash
gitops-summary diagrams --list-types
JAVA_TOOL_OPTIONS="-Djava.awt.headless=true" java -jar /tmp/plantuml.jar -version
```

If your jar is not at a default location, set:

```bash
export PLANTUML_JAR=/tmp/plantuml.jar
```

The CLI already sets the headless Java flag during rendering, so you do not need to set `JAVA_TOOL_OPTIONS` every time for normal CLI usage.

### What the command does

When you run `gitops-summary diagrams`, it:

1. Scans the repository for context such as README, file tree, config files, and architecture signals
2. Chooses the requested diagram types
3. Generates PlantUML source with Bedrock
4. Writes `.puml` files to the output directory
5. Renders each `.puml` file to the requested format
6. Reports whether each diagram was generated normally, generated as best-effort, or skipped due to weak evidence

### Default behavior

```bash
gitops-summary diagrams
```

By default this writes output to:

```text
docs/diagrams/
```

If that directory does not exist, the command creates it.

### Common examples

Generate the default diagram set:

```bash
gitops-summary diagrams
```

Generate only selected types:

```bash
gitops-summary diagrams --type architecture --type data_model --type sequence
```

Generate into a custom location:

```bash
gitops-summary diagrams --output /tmp/diagrams
```

Analyze a different repository:

```bash
gitops-summary diagrams --repo /path/to/other/repo --output /tmp/diagrams
```

Render existing `.puml` files without calling Bedrock:

```bash
gitops-summary diagrams --render-only --format svg
```

Show supported diagram types:

```bash
gitops-summary diagrams --list-types
```

### Supported diagram types

- `architecture`
- `containers`
- `data_model`
- `ingestion`
- `search_ask`
- `sequence`
- `component`
- `deployment`
- `class`
- `state`
- `use_case`
- `activity`

### How output is written

For each successful generation, the command writes:

- a versionable PlantUML source file such as `docs/diagrams/architecture.puml`
- a rendered file such as `docs/diagrams/architecture.png`

This means you can:

- commit the `.puml` source to git
- regenerate images later
- use `--render-only` after editing a `.puml` file by hand

### Best-effort and skipped diagrams

Not every repository contains enough evidence for every diagram type.

The command is intentionally conservative:

- if repo evidence is strong, it generates the diagram normally
- if evidence is partial, it generates a best-effort diagram and tells you so
- if evidence is too weak, it skips that diagram and explains why

Examples of user-facing messages:

- `Generated deployment diagram (best effort: limited deployment evidence found in repo)`
- `Skipped data_model: not enough schema information found to produce a trustworthy diagram`

### Troubleshooting diagrams mode

If Bedrock works but rendering fails, the `.puml` source file may still be written successfully. In that case, install Java + the PlantUML jar and rerun the command.

If PlantUML is not found, the CLI prints setup guidance for:

- Ubuntu / Debian
- Amazon Linux 2
- Windows (PowerShell)

If `boto3` is missing in your current interpreter, run the CLI from the project virtualenv or reinstall project dependencies.

---

## CLI reference

```bash
gitops-summary --manual
gitops-summary --generate-md

gitops-summary commit
gitops-summary weekly [--issues] [--start-date YYYY-MM-DD --days N]
gitops-summary epic [--setup|--status|--update|--map|--labels]
gitops-summary diagrams [--repo PATH] [--output DIR] [--type NAME ...] [--format png|svg|txt] [--model MODEL_ID] [--render-only] [--list-types]
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
- **PlantUML not found**
  - Install the `plantuml` command or download a PlantUML jar and ensure Java is available

---
