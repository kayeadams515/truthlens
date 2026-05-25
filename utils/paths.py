"""Path helpers for PyInstaller compatibility.

In PyInstaller bundles (sys.frozen=True):
  - Base dir (read-only resources): sys._MEIPASS
  - Data dir (writable user data): ~/.truthlens/

In development:
  - Base dir: project root
  - Data dir: project_root/data/
"""

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Project root — read-only in bundles, writable in dev."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Writable directory for settings, reports, logs, cache."""
    if getattr(sys, "frozen", False):
        data_dir = Path.home() / ".truthlens"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    return Path(__file__).parent.parent / "data"
