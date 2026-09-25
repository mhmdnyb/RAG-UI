"""Shared utilities and paths for scripts."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def resolve_data_file() -> Path:
    """Find and return the regulations text file from known locations."""
    candidates = [
        PROJECT_ROOT / "data" / "New سند متنی.txt",
        PROJECT_ROOT / "data" / "regulations.txt",
        Path("ai-team/data/New سند متنی.txt"),
        Path("data/New سند متنی.txt"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not locate regulations text file. Checked: {candidates}"
    )
