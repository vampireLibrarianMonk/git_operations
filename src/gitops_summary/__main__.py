"""Module execution entrypoint.

Allows:
  python -m gitops_summary ...
"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
