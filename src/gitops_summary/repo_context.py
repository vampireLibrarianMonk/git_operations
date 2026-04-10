"""Repository context collection for diagram generation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


IGNORED_DIR_NAMES = {
    ".git",
    ".idea",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}

README_CANDIDATES = ("README.md", "readme.md", "README.rst")
CONFIG_CANDIDATES = (
    "pyproject.toml",
    "package.json",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "Dockerfile",
    "Makefile",
)


def collect_repo_context(repo_path: str) -> dict[str, Any]:
    """Collect repository context used to generate diagrams."""

    root = Path(repo_path).resolve()
    if not root.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if root.is_file():
        root = root.parent

    file_paths = _collect_file_paths(root)
    configs = _collect_config_snippets(root)
    readme = _read_readme(root)
    git_log = _read_git_log(root)
    signals = _detect_signals(root, file_paths, readme, configs)

    return {
        "repo_path": str(root),
        "top_level_entries": sorted(path.name for path in root.iterdir()),
        "file_paths": file_paths,
        "file_tree": _render_file_tree(file_paths),
        "readme": readme,
        "configs": configs,
        "git_log": git_log,
        "signals": sorted(signals),
    }


def _collect_file_paths(root: Path, limit: int = 400) -> list[str]:
    paths: list[str] = []

    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = sorted(d for d in dir_names if d not in IGNORED_DIR_NAMES)
        rel_root = Path(current_root).relative_to(root)

        for file_name in sorted(file_names):
            rel_path = (rel_root / file_name) if str(rel_root) != "." else Path(file_name)
            paths.append(str(rel_path).replace("\\", "/"))
            if len(paths) >= limit:
                return paths

    return paths


def _render_file_tree(file_paths: list[str], char_limit: int = 8000) -> str:
    rendered = "\n".join(file_paths)
    if len(rendered) <= char_limit:
        return rendered
    return rendered[: char_limit - 32] + "\n... (file tree truncated)"


def _read_readme(root: Path, char_limit: int = 3500) -> str:
    for name in README_CANDIDATES:
        path = root / name
        if path.exists() and path.is_file():
            return _read_text(path, char_limit)
    return ""


def _collect_config_snippets(root: Path, char_limit: int = 2200) -> dict[str, str]:
    snippets: dict[str, str] = {}

    for candidate in CONFIG_CANDIDATES:
        path = root / candidate
        if path.exists() and path.is_file():
            snippets[str(path.relative_to(root)).replace("\\", "/")] = _read_text(path, char_limit)

    for alt in (
        "infra/docker/compose/docker-compose.yml",
        "docker/docker-compose.yml",
        "compose/docker-compose.yml",
    ):
        path = root / alt
        if path.exists() and path.is_file():
            snippets[str(path.relative_to(root)).replace("\\", "/")] = _read_text(path, char_limit)

    return snippets


def _read_git_log(root: Path, max_lines: int = 20) -> str:
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={max_lines}", "--oneline"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""

    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _read_text(path: Path, char_limit: int) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return text[:char_limit].strip()


def _detect_signals(root: Path, file_paths: list[str], readme: str, configs: dict[str, str]) -> set[str]:
    signals: set[str] = set()
    if readme:
        signals.add("readme")

    path_text = "\n".join(file_paths).lower()
    config_text = "\n".join(configs.values()).lower()
    combined_text = f"{path_text}\n{readme.lower()}\n{config_text}"

    if any(path.endswith(".py") for path in file_paths):
        signals.add("python")

    if any(token in combined_text for token in ("argparse", "click", "typer", "__main__", "cli.py", "console_scripts")):
        signals.add("cli")

    if any(token in combined_text for token in ("fastapi", "flask", "django", "router", "endpoint", "rest", "uvicorn")):
        signals.add("api")

    if any(token in combined_text for token in ("react", "vue", "frontend", "vite", "nextjs", "next.js", "angular", "svelte")):
        signals.add("frontend")

    if any(token in combined_text for token in ("docker", "dockerfile", "container")):
        signals.add("docker")

    if any(token in combined_text for token in ("docker-compose", "compose.yml", "compose.yaml", "services:")):
        signals.add("compose")

    if any(token in combined_text for token in ("kubernetes", "helm", "k8s", "deployment.yaml", "statefulset")):
        signals.add("kubernetes")

    if any(token in combined_text for token in ("terraform", ".tf", "cloudformation", "pulumi")):
        signals.add("terraform")

    if any(token in combined_text for token in ("postgres", "mysql", "sqlite", "database", "db", "redis")):
        signals.add("database")

    if any(token in combined_text for token in ("sqlalchemy", "orm", "peewee", "django.db", "declarative_base")):
        signals.add("orm")
        signals.add("models")

    if any(token in combined_text for token in ("migrations", "alembic", "schema", ".sql")):
        signals.add("migrations")
        signals.add("sql")

    if any(token in combined_text for token in ("worker", "celery", "rq", "background", "job queue", "jobs")):
        signals.add("worker")

    if any(token in combined_text for token in ("s3", "minio", "storage", "bucket", "uploads")):
        signals.add("storage")

    if any(token in combined_text for token in ("opensearch", "elasticsearch", "bm25", "search", "index")):
        signals.add("search")

    if any(token in combined_text for token in ("bedrock", "claude", "llm", "anthropic", "ai")):
        signals.add("bedrock")
        signals.add("ai")
        signals.add("cloud")
    elif any(token in combined_text for token in ("aws", "gcp", "azure", "cloud")):
        signals.add("cloud")

    if any(token in combined_text for token in ("status", "workflow", "transition", "state", "lifecycle")):
        signals.add("workflow")
        signals.add("stateful")

    class_count = _estimate_python_class_count(root)
    if class_count >= 3:
        signals.add("classes")

    return signals


def _estimate_python_class_count(root: Path, max_files: int = 25) -> int:
    count = 0
    scanned = 0
    for path in sorted(root.rglob("*.py")):
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        count += text.count("\nclass ") + (1 if text.startswith("class ") else 0)
        scanned += 1
        if scanned >= max_files:
            break
    return count