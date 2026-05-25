#!/usr/bin/env python3
"""Verify Loom CLI and installer release surfaces stay separated."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI_RELEASE_DOC = ROOT / "docs" / "adoption" / "loom-cli-release-surface.md"
VERSION_AUTHORITY = ROOT / "docs" / "adoption" / "version-authority-map.md"
INSTALLER_RELEASE = ROOT / ".github" / "workflows" / "node-installer-release.yml"
INSTALLER_PR = ROOT / ".github" / "workflows" / "node-installer-pr.yml"
CLI_RELEASE = ROOT / ".github" / "workflows" / "loom-cli-release.yml"
INSTALLER_BUMP_CHECK = ROOT / "packages" / "loom-installer" / "scripts" / "check-version-bump.mjs"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"


def require_file(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require_needles(path: Path, needles: tuple[str, ...], errors: list[str]) -> str:
    text = require_file(path, errors)
    for needle in needles:
        if needle not in text:
            errors.append(f"{path.relative_to(ROOT)} must mention `{needle}`")
    return text


def main() -> int:
    errors: list[str] = []

    require_needles(
        CLI_RELEASE_DOC,
        (
            "The `loom` CLI release line is the primary release line",
            "GitHub `v*` tag and GitHub Release",
            "Publishing requires an explicit `workflow_dispatch` run with publish enabled",
            "`loom-installer` is a compatibility and legacy maintenance line",
            "must not use `@mc-and-his-agents/loom-installer` `latest`",
        ),
        errors,
    )
    require_needles(
        VERSION_AUTHORITY,
        (
            "Loom CLI release candidate",
            "Published Loom CLI release",
            "Installer compatibility / legacy maintenance line",
            "No check may infer that a `loom-installer-v*` tag publishes the `loom` CLI",
        ),
        errors,
    )
    require_needles(
        CLI_RELEASE,
        (
            "name: loom-cli-release",
            "workflow_dispatch",
            "publish",
            "PACKAGE_TAG_PREFIX: 'v'",
            "no-cli-behavior-change",
            "gh release create",
        ),
        errors,
    )
    installer_release = require_needles(
        INSTALLER_RELEASE,
        (
            "name: node-installer-release",
            "PACKAGE_NAME: '@mc-and-his-agents/loom-installer'",
            "reason=installer-sunset-no-publish",
            "should_publish=false",
            "create_release=false",
        ),
        errors,
    )
    require_needles(
        INSTALLER_PR,
        (
            "node packages/loom-installer/scripts/check-version-bump.mjs",
            "python3 tools/check_release_surface.py",
        ),
        errors,
    )
    bump_check = require_needles(
        INSTALLER_BUMP_CHECK,
        (
            "packages/loom-installer/src/",
            "packages/loom-installer/package.json",
            "no installer shim changes",
        ),
        errors,
    )
    require_needles(README, ("Loom CLI release surface", "loom-installer compatibility line"), errors)
    require_needles(README_ZH, ("Loom CLI 发布面", "loom-installer 兼容线"), errors)

    forbidden_installer_behavior_needles = (
        "plugins/loom/.codex-plugin/|src/skills/|skills/",
        "plugins/loom/.codex-plugin/",
        "'src/skills/**'",
    )
    release_state_section = installer_release.split("Resolve sunset state", 1)[-1]
    for needle in forbidden_installer_behavior_needles:
        if needle in release_state_section:
            errors.append(f"installer release state must not classify `{needle}` as installer shim behavior")

    forbidden_installer_publish_needles = (
        "npm publish",
        "npm whoami",
        "git tag -a",
        "git push origin",
        "gh release create",
        "NODE_AUTH_TOKEN",
        "NPM_TOKEN",
        "contents: write",
        "id-token: write",
    )
    for needle in forbidden_installer_publish_needles:
        if needle in installer_release:
            errors.append(f"installer release workflow must not contain active publish capability `{needle}`")

    for needle in ("plugins/loom/.codex-plugin/", "skills/"):
        if needle in bump_check and "ignoredCompatibilityPaths" not in bump_check:
            errors.append(f"installer version bump check must not classify `{needle}` as shim behavior")

    if errors:
        print("release surface check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("release surface check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
