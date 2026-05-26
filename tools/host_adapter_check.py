#!/usr/bin/env python3
"""Static checks for Loom host adapter distribution contracts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "adoption" / "host-adapter-matrix.md"
UNIFIED = ROOT / "docs" / "adoption" / "unified-install-experience.md"

HOSTS = ("Codex", "Claude Code", "OpenCode", "Gemini", "Cursor")
REQUIRED_FIELDS = (
    "default_install_path",
    "advanced_single_skill_path",
    "install_surface",
    "discovery_surface",
    "bootstrap_or_session_start_surface",
    "default_entry",
    "tool_mapping_surface",
    "upgrade_surface",
    "verification_surface",
    "fail_closed_conditions",
    "version_metadata_location",
)


def require_contains(path: Path, needles: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return [f"missing {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    return [f"{path.relative_to(ROOT)} must mention `{needle}`" for needle in needles if needle not in text]


def main() -> int:
    errors: list[str] = []
    errors.extend(require_contains(MATRIX, HOSTS))
    errors.extend(require_contains(MATRIX, REQUIRED_FIELDS))
    errors.extend(require_contains(MATRIX, ("loom-init", "skills/<skill-id>", "fail closed", "static adapter check")))
    errors.extend(require_contains(UNIFIED, ("root CLI", "native", "single-skill", "skills/<skill-id>", "loom-init")))
    if errors:
        print("host adapter check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("host adapter check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
