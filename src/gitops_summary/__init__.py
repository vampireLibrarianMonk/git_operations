"""gitops_summary package."""

__all__ = ["__version__", "main"]

from ._version import __version__


def main() -> int:
    """Lazy-imported package entrypoint."""
    from .cli import main as _main

    return _main()
