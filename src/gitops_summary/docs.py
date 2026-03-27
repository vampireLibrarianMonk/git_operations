"""Manual/readme output helpers."""

from pathlib import Path

from .config import MANUAL_TEXT, README_CONTENT
from .epic import ensure_gitignore_entry


def generate_readme() -> int:
    """Generate README.md file."""
    readme_path = Path("README.md")

    with open(readme_path, "w") as f:
        f.write(README_CONTENT.strip() + "\n")

    print(f"Generated {readme_path}")

    # Ensure .gitignore has the entry
    gitignore_status = ensure_gitignore_entry()
    print(f"[gitignore] {gitignore_status}")

    return 0


def print_manual() -> int:
    """Print the full user manual."""
    print(MANUAL_TEXT)
    return 0
