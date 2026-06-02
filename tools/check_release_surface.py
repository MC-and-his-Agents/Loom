#!/usr/bin/env python3
"""Verify Loom CLI and installer release surfaces stay separated."""

from __future__ import annotations

import re
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
CODEX_INSTALL = ROOT / "docs" / "adoption" / "codex-install.md"
CLI_ONLY_CONTRACT = ROOT / "docs" / "adoption" / "cli-only-install-contract.md"
UNIFIED_INSTALL = ROOT / "docs" / "adoption" / "unified-install-experience.md"
HOST_ADAPTER_MATRIX = ROOT / "docs" / "adoption" / "host-adapter-matrix.md"

ACTIVE_SURFACE_DOCS = (
    README,
    README_ZH,
    CLI_ONLY_CONTRACT,
    CLI_RELEASE_DOC,
    VERSION_AUTHORITY,
    CODEX_INSTALL,
    UNIFIED_INSTALL,
    HOST_ADAPTER_MATRIX,
)

FORBIDDEN_ACTIVE_INSTALLER_PATTERNS = (
    re.compile(r"@mc-and-his-agents/loom-installer[^.\n]*(?:is|as|remains)[^.\n]*(?:current|active|primary)[^.\n]*(?:CLI|release line|install path)", re.IGNORECASE),
    re.compile(r"@mc-and-his-agents/loom-installer[^.\n]*latest[^.\n]*(?:proves|publishes|is evidence for)[^.\n]*(?:loom|CLI)", re.IGNORECASE),
    re.compile(r"loom-installer-v[^\s`)]*[^.\n]*(?:publishes|proves|is evidence for)[^.\n]*(?:loom|CLI)", re.IGNORECASE),
    re.compile(r"npx\s+(?:@mc-and-his-agents/)?loom-installer[^.\n]*(?:is|as|remains)[^.\n]*(?:default|recommended|primary)[^.\n]*(?:Codex|install|path)", re.IGNORECASE),
    re.compile(r"(?:default|recommended|primary)[^.\n]*(?:Codex|install|path)[^.\n]*(?:is|uses)\s+npx\s+(?:@mc-and-his-agents/)?loom-installer", re.IGNORECASE),
)

FORBIDDEN_SEPARATE_INSTALL_SURFACE_PATTERNS = (
    re.compile(r"(?:SKILLS|skills/|plugins?/loom|host plugins?)[^.\n]*(?:is|are|as|remain)[^.\n]*(?:primary|default|recommended)[^.\n]*(?:install|installation|surface|path)", re.IGNORECASE),
    re.compile(r"(?:primary|default|recommended)[^.\n]*(?:install|installation|surface|path)[^.\n]*(?:SKILLS|skills/|plugins?/loom|host plugins?)", re.IGNORECASE),
    re.compile(r"(?:install|use)\s+(?:SKILLS|skills/|plugins?/loom|host plugins?)[^.\n]*(?:directly|separately|independently|as separate)", re.IGNORECASE),
    re.compile(r"(?:npm install|npx)\s+(?:-g\s+)?(?:@mc-and-his-agents/)?loom-installer", re.IGNORECASE),
)

NEGATED_CONTEXT_MARKERS = (
    "no check may",
    "must not",
    "do not",
    "is not",
    "are not",
    "not ",
    "not a",
    "not the",
    "not part",
    "without",
    "deprecated",
    "historical",
    "legacy",
    "unsupported",
    "cli-managed",
    "managed payload",
    "root `loom` cli",
)


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


def forbid_active_installer_evidence(path: Path, errors: list[str]) -> None:
    text = require_file(path, errors)
    if not text:
        return
    for pattern in FORBIDDEN_ACTIVE_INSTALLER_PATTERNS:
        match = pattern.search(text)
        if match:
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end].lower()
            if any(guard in line for guard in NEGATED_CONTEXT_MARKERS):
                continue
            snippet = " ".join(match.group(0).split())
            errors.append(
                f"{path.relative_to(ROOT)} must not present loom-installer as active CLI/install/release evidence: `{snippet}`"
            )


def forbid_separate_install_surfaces(path: Path, errors: list[str]) -> None:
    text = require_file(path, errors)
    if not text:
        return
    for pattern in FORBIDDEN_SEPARATE_INSTALL_SURFACE_PATTERNS:
        for match in pattern.finditer(text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end].lower()
            if any(guard in line for guard in NEGATED_CONTEXT_MARKERS):
                continue
            snippet = " ".join(match.group(0).split())
            errors.append(
                f"{path.relative_to(ROOT)} must not present SKILLS, plugins, or loom-installer as separate install surfaces: `{snippet}`"
            )


def assert_pattern_guards(errors: list[str]) -> None:
    negative_examples = (
        "SKILLS are managed by the root loom CLI and are not a separate install surface.",
        "Host plugins are CLI-managed payloads, not primary install paths.",
        "`loom-installer` is a deprecated historical artifact, not the current install path.",
    )
    positive_examples = (
        "SKILLS are the recommended install surface for Loom.",
        "The primary install path uses plugins/loom directly.",
        "Run npx @mc-and-his-agents/loom-installer to install Loom.",
    )
    for example in negative_examples:
        lowered = example.lower()
        if any(pattern.search(example) and not any(marker in lowered for marker in NEGATED_CONTEXT_MARKERS) for pattern in FORBIDDEN_SEPARATE_INSTALL_SURFACE_PATTERNS):
            errors.append(f"CLI-only install guard false-positive fixture failed: {example}")
    for example in positive_examples:
        lowered = example.lower()
        if not any(pattern.search(example) and not any(marker in lowered for marker in NEGATED_CONTEXT_MARKERS) for pattern in FORBIDDEN_SEPARATE_INSTALL_SURFACE_PATTERNS):
            errors.append(f"CLI-only install guard failed to reject fixture: {example}")


def main() -> int:
    errors: list[str] = []

    require_needles(
        CLI_ONLY_CONTRACT,
        (
            "The only primary user-facing install surface for Loom is the root `loom` CLI",
            "Host plugins are host adapter payloads managed by the `loom` CLI",
            "`SKILLS` are executable scenario payloads managed, synchronized, and verified",
            "`loom-installer` must not gain a new migration journey",
        ),
        errors,
    )
    require_needles(
        CLI_RELEASE_DOC,
        (
            "The `loom` CLI release line is the primary release line",
            "GitHub `v*` tag and GitHub Release",
            "For `push` events on `main`, `loom-cli-release` automatically creates the GitHub `v*` tag, publishes `@mc-and-his-agents/loom` to npm, and creates the GitHub Release",
            "when the `NPM_TOKEN` secret is missing for an npm publish",
            "must fail closed when CLI publish behavior changed but the current `VERSION` is already published on a different commit",
            "Installer npm state is never publish evidence for this judgment",
            "`loom-installer` is a deprecated legacy artifact",
            "must not use `@mc-and-his-agents/loom-installer` `latest`",
        ),
        errors,
    )
    require_needles(
        VERSION_AUTHORITY,
        (
            "Loom CLI release candidate",
            "Published Loom CLI release",
            "Deprecated installer legacy artifact",
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
            "push",
            "AUTO_PUBLISH_ALLOWED",
            "cli_publish_behavior_changed",
            "version-already-published-on-different-commit",
            "PACKAGE_TAG_PREFIX: 'v'",
            "NPM_PACKAGE_NAME: '@mc-and-his-agents/loom'",
            "secrets.NPM_TOKEN",
            "npm publish --access public --provenance",
            "npm view \"${NPM_PACKAGE_NAME}@${NPM_VERSION}\" version",
            "npm pack --dry-run --json --ignore-scripts",
            "python3 tools/check_npm_package.py",
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
    require_needles(README, ("Loom CLI release surface", "loom-installer deprecated legacy line", "users do not install them as a separate surface"), errors)
    require_needles(README_ZH, ("Loom CLI 发布面", "loom-installer deprecated legacy line", "用户不再把它们作为独立安装面安装"), errors)
    require_needles(CODEX_INSTALL, ("The npm installer is not the Codex default path", "plugins/loom/skills/"), errors)
    require_needles(UNIFIED_INSTALL, ("use `loom host install` to install host plugin payloads", "Historical: `@mc-and-his-agents/loom-installer` references retained only for deprecated evidence"), errors)
    require_needles(HOST_ADAPTER_MATRIX, ("embedded skills at `plugins/loom/skills/`", "update root CLI, rerun"), errors)

    for path in ACTIVE_SURFACE_DOCS:
        forbid_active_installer_evidence(path, errors)
        forbid_separate_install_surfaces(path, errors)
    assert_pattern_guards(errors)

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
