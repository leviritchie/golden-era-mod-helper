"""Resolved locations for the Olden Era mod helper.

All write operations must go through ``isolation.py``. This module only
knows where the helper itself lives.
"""

from __future__ import annotations

from pathlib import Path

HELPER_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = HELPER_ROOT / "data"
DOCS_DIR = HELPER_ROOT / "docs"
STUDIO_DIR = HELPER_ROOT / "studio"
SANDBOX_DIR = HELPER_ROOT / "sandbox"
CSHARP_DIR = HELPER_ROOT / "csharp"
SAMPLE_DIR = DATA_DIR / "sample"
