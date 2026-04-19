#!/usr/bin/env python3
"""Repo-local wrapper for the installed-skills loom_init runtime."""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"

os.environ.setdefault("LOOM_INSTALLED_SKILLS_ROOT", str(SKILLS_ROOT))
os.environ.setdefault("LOOM_SOURCE_REPO_ROOT", str(REPO_ROOT))
sys.path.insert(0, str(SKILLS_ROOT / "shared/scripts"))
runpy.run_path(SKILLS_ROOT / "shared/scripts/loom_init.py", run_name="__main__")
