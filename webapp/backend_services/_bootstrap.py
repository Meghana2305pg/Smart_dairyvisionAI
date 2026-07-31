"""Bootstrap helpers for backend services that wrap the existing project modules."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_on_path() -> Path:
    """Ensure the existing repository root is importable from the Streamlit app."""
    project_root = Path(__file__).resolve().parents[2]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    return project_root
