#!/usr/bin/env python3
"""Verify Loom distribution version surfaces are explicit and machine-readable."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_MAP = ROOT / "docs" / "adoption" / "version-authority-map.md"
PLUGIN_MANIFEST = ROOT / "plugins" / "loom" / ".codex-plugin" / "plugin.json"
INSTALLER_PACKAGE = ROOT / "packages" / "loom-installer" / "package.json"
REPO_VERSION = ROOT / "VERSION"
SKILLS_REGISTRY = ROOT / "skills" / "registry.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    if not AUTHORITY_MAP.exists():
        errors.append("missing docs/adoption/version-authority-map.md")
    else:
        text = AUTHORITY_MAP.read_text(encoding="utf-8")
        for needle in (
            "VERSION",
            "GitHub release",
            "installer package version",
            "plugin surface version",
            "host adapter version",
            "skill_package_version",
            "contract_version",
            "schema_version",
            "Versions are not globally synchronized",
        ):
            if needle not in text:
                errors.append(f"version authority map must mention `{needle}`")

    plugin = read_json(PLUGIN_MANIFEST)
    x_loom = plugin.get("x-loom")
    if not isinstance(x_loom, dict):
        errors.append("plugin manifest must expose x-loom metadata")
    else:
        for key in ("plugin_surface_version", "host_adapter_version", "version_authority", "default_entry", "distribution_model"):
            if key not in x_loom:
                errors.append(f"plugin x-loom metadata missing `{key}`")
        if x_loom.get("plugin_surface_version") != plugin.get("version"):
            errors.append("plugin_surface_version must equal plugin manifest version")

    repo_version = REPO_VERSION.read_text(encoding="utf-8").strip()
    installer_version = read_json(INSTALLER_PACKAGE).get("version")
    registry_version = read_json(SKILLS_REGISTRY).get("registry_version")
    if not repo_version.startswith("v"):
        errors.append("repo VERSION must use v-prefixed release candidate syntax")
    if not installer_version:
        errors.append("installer package version is missing")
    if not registry_version:
        errors.append("skills registry_version is missing")

    for skill_dir in sorted((ROOT / "skills").glob("loom-*")):
        if not skill_dir.is_dir():
            continue
        metadata_path = skill_dir / "loom-package.json"
        contract_path = skill_dir / "contract.json"
        if not metadata_path.exists():
            errors.append(f"{skill_dir.relative_to(ROOT)} missing loom-package.json")
            continue
        metadata = read_json(metadata_path)
        contract = read_json(contract_path)
        for key in (
            "schema_version",
            "package_type",
            "package_id",
            "repo_version",
            "source_repository",
            "source_revision",
            "skill_package_version",
            "skill_contract_version",
            "registry_version",
            "runtime_core_version",
            "runtime_root",
            "launcher",
            "fail_closed_on",
        ):
            if key not in metadata:
                errors.append(f"{metadata_path.relative_to(ROOT)} missing `{key}`")
        if metadata.get("repo_version") != repo_version:
            errors.append(f"{metadata_path.relative_to(ROOT)} repo_version mismatch")
        if metadata.get("registry_version") != registry_version:
            errors.append(f"{metadata_path.relative_to(ROOT)} registry_version mismatch")
        if metadata.get("skill_contract_version") != contract.get("contract_version"):
            errors.append(f"{metadata_path.relative_to(ROOT)} skill_contract_version mismatch")

    if errors:
        print("version surface check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("version surface check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
