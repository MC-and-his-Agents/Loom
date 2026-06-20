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
PLUGIN_SKILLS_REGISTRY = ROOT / "plugins" / "loom" / "skills" / "registry.json"
CLI_RELEASE_SURFACE = ROOT / "docs" / "adoption" / "loom-cli-release-surface.md"
RELEASE_SURFACE_CHECK = ROOT / "tools" / "check_release_surface.py"


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
            "Loom CLI release candidate",
            "Published Loom CLI release",
            "Deprecated installer legacy artifact",
            "plugin surface version",
            "host adapter version",
            "plugin payload registry_version",
            "contract_version",
            "schema_version",
            "Versions are not globally synchronized",
        ):
            if needle not in text:
                errors.append(f"version authority map must mention `{needle}`")
    if not CLI_RELEASE_SURFACE.exists():
        errors.append("missing docs/adoption/loom-cli-release-surface.md")
    else:
        release_text = CLI_RELEASE_SURFACE.read_text(encoding="utf-8")
        for needle in (
            "The `loom` CLI release line is the primary release line",
            "GitHub `v*` tag and GitHub Release",
            "`loom-installer` is a deprecated legacy artifact",
            "must not use `@mc-and-his-agents/loom-installer` `latest`",
        ):
            if needle not in release_text:
                errors.append(f"CLI release surface must mention `{needle}`")
    if not RELEASE_SURFACE_CHECK.exists():
        errors.append("missing tools/check_release_surface.py")

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
    registry = read_json(SKILLS_REGISTRY)
    registry_version = registry.get("registry_version")
    plugin_registry = read_json(PLUGIN_SKILLS_REGISTRY)
    if not repo_version.startswith("v"):
        errors.append("repo VERSION must use v-prefixed release candidate syntax")
    if not installer_version:
        errors.append("installer package version is missing")
    if not registry_version:
        errors.append("skills registry_version is missing")
    if plugin_registry != registry:
        errors.append("plugin payload registry must match generated skills registry")
    if plugin_registry.get("root_entry") != "loom-init":
        errors.append("plugin payload root_entry must be loom-init")

    for payload_root in (ROOT / "skills", ROOT / "plugins" / "loom" / "skills"):
        if any(path.name == "loom-package.json" for path in payload_root.glob("loom-*/loom-package.json")):
            errors.append(f"{payload_root.relative_to(ROOT)} must not contain single-skill loom-package.json files")
        if any(".loom-runtime" in path.parts for path in payload_root.rglob("*")):
            errors.append(f"{payload_root.relative_to(ROOT)} must not contain package-internal .loom-runtime directories")
        for entry in registry.get("entries", []):
            skill_id = entry.get("id") if isinstance(entry, dict) else None
            if not isinstance(skill_id, str):
                errors.append(f"{payload_root.relative_to(ROOT)} registry contains invalid skill entry")
                continue
            skill_dir = payload_root / skill_id
            contract_path = skill_dir / "contract.json"
            if not (skill_dir / "SKILL.md").is_file():
                errors.append(f"{skill_dir.relative_to(ROOT)} missing SKILL.md")
            if not contract_path.is_file():
                errors.append(f"{skill_dir.relative_to(ROOT)} missing contract.json")
                continue
            contract = read_json(contract_path)
            if entry.get("contract_version") != contract.get("contract_version"):
                errors.append(f"{contract_path.relative_to(ROOT)} contract_version mismatch")

    if errors:
        print("version surface check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("version surface check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
