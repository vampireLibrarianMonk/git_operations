"""gitops_summary package."""

__all__ = ["__version__", "main"]

__version__ = "0.1.0"


def main() -> int:
    """Lazy-imported package entrypoint."""
    from .cli import main as _main

    return _main()
