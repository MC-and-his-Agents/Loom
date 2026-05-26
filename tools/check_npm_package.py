#!/usr/bin/env python3
"""Validate the root Loom npm package contract and dry-run payload."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = REPO_ROOT / "package.json"
VERSION = REPO_ROOT / "VERSION"

EXPECTED_PACKAGE = "@mc-and-his-agents/loom"
EXPECTED_BIN = "bin/loom.mjs"
REQUIRED_FILES = {
    "package.json",
    "bin/loom.mjs",
    "tools/loom.py",
    "tools/loom_flow.py",
    "tools/loom_init.py",
    "tools/loom_check.py",
    "tools/check_npm_package.py",
    "skills/registry.json",
    "skills/loom-init/SKILL.md",
    "skills/loom-init/loom-package.json",
    "plugins/loom/.codex-plugin/plugin.json",
    "src/skills/registry.json",
    "docs/adoption/cli-only-install-contract.md",
    "docs/adoption/loom-cli-release-surface.md",
    "docs/adoption/version-authority-map.md",
    "docs/adoption/codex-install.md",
    "docs/methodology/harness/cli-command-matrix.md",
    "VERSION",
    "README.md",
    "README.zh-CN.md",
    "VISION.md",
    "AGENTS.md",
    "LICENSE",
}
FORBIDDEN_PREFIXES = (
    ".git/",
    ".github/",
    ".loom/",
    "examples/",
    "packages/loom-installer/",
)
FORBIDDEN_MANIFEST_STRINGS = (
    "@mc-and-his-agents/loom-installer",
    "loom-installer",
    "packages/loom-installer",
)
REQUIRED_MANIFEST_FILES = (
    "skills",
    "src/skills",
    "plugins/loom/.codex-plugin/plugin.json",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise AssertionError(message)


def npm_version_from_root() -> str:
    version = VERSION.read_text(encoding="utf-8").strip()
    if not version.startswith("v"):
        fail(f"VERSION must use v-prefixed release form, got {version!r}")
    return version[1:]


def npm_pack_files() -> set[str]:
    completed = subprocess.run(
        ["npm", "pack", "--dry-run", "--json", "--ignore-scripts"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        fail(f"npm pack --dry-run failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(f"npm pack --dry-run did not emit JSON: {exc}\n{completed.stdout}")
    if not isinstance(payload, list) or not payload:
        fail("npm pack --dry-run returned an empty payload")
    files = payload[0].get("files", [])
    return {item.get("path", "") for item in files if isinstance(item, dict)}


def main() -> int:
    package = load_json(PACKAGE_JSON)
    if package.get("name") != EXPECTED_PACKAGE:
        fail(f"package name must be {EXPECTED_PACKAGE}")
    if package.get("version") != npm_version_from_root():
        fail("package version must match root VERSION without the v prefix")
    if package.get("bin", {}).get("loom") != EXPECTED_BIN:
        fail(f"bin loom must point at {EXPECTED_BIN}")
    if package.get("publishConfig", {}).get("access") != "public":
        fail("publishConfig.access must be public")
    manifest_text = json.dumps(package, sort_keys=True)
    for forbidden in FORBIDDEN_MANIFEST_STRINGS:
        if forbidden in manifest_text:
            fail(f"root package manifest must not reference deprecated installer surface: {forbidden}")
    manifest_files = package.get("files")
    if not isinstance(manifest_files, list):
        fail("package files must explicitly enumerate the root CLI payload")
    missing_manifest_files = sorted(item for item in REQUIRED_MANIFEST_FILES if item not in manifest_files)
    if missing_manifest_files:
        fail(f"package files must include CLI-managed payload surfaces: {missing_manifest_files}")
    forbidden_manifest_files = sorted(item for item in manifest_files if isinstance(item, str) and item.startswith(FORBIDDEN_PREFIXES))
    if forbidden_manifest_files:
        fail(f"package files must not include forbidden repository/internal surfaces: {forbidden_manifest_files}")

    missing_sources = sorted(path for path in REQUIRED_FILES if not (REPO_ROOT / path).exists())
    if missing_sources:
        fail(f"required package source files are missing: {missing_sources}")

    pack_files = npm_pack_files()
    missing_pack_files = sorted(REQUIRED_FILES - pack_files)
    if missing_pack_files:
        fail(f"npm pack payload is missing required files: {missing_pack_files}")

    forbidden = sorted(path for path in pack_files if path.startswith(FORBIDDEN_PREFIXES))
    if forbidden:
        fail(f"npm pack payload contains forbidden repository/internal files: {forbidden[:20]}")

    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "package": EXPECTED_PACKAGE,
        "version": package["version"],
        "bin": "loom",
        "payload_file_count": len(pack_files),
        "required_files": sorted(REQUIRED_FILES),
        "required_manifest_files": sorted(REQUIRED_MANIFEST_FILES),
        "forbidden_prefixes": list(FORBIDDEN_PREFIXES),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(json.dumps({
            "schema_version": "loom-npm-package-check/v1",
            "result": "block",
            "failed_layer": "npm-package-payload",
            "fail_closed_reason": str(exc),
            "fallback_to": ["docs/adoption/cli-only-install-contract.md", "npm pack --dry-run --json --ignore-scripts"],
        }, indent=2), file=sys.stderr)
        raise SystemExit(1)
