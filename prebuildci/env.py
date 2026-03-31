from __future__ import annotations

import os


def env(key: str, default: str | None = None) -> str | None:
    """Read an environment variable or secret."""
    return os.environ.get(key, default)
