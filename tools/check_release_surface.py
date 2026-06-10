#!/usr/bin/env python3
"""Verify Loom CLI and installer release surfaces stay separated."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


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

RELEASE_DOC_CONTRACT = "release-doc-contract"
RELEASE_WORKFLOW_CONTRACT = "release-workflow-contract"
INSTALLER_SUNSET_GUARD = "installer-sunset-guard"
FORBIDDEN_RELEASE_SURFACE_PATTERNS = "forbidden-release-surface-patterns"
AGGREGATE_RELEASE_SURFACE = "aggregate-release-surface"

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


@dataclass(frozen=True)
class SurfaceError:
    surface_label: str
    failure_label: str
    evidence_locator: str
    source_locator: str
    summary: str


@dataclass(frozen=True)
class SurfaceDefinition:
    label: str
    description: str
    evidence_locator: str
    run: Callable[[list[SurfaceError]], None]


def relative_to_root(path: Path) -> str:
    return str(path.relative_to(ROOT))


def evidence_locator(surface_label: str) -> str:
    return f"python3 tools/check_release_surface.py --surface {surface_label}"


def add_error(
    errors: list[SurfaceError],
    *,
    surface_label: str,
    failure_label: str,
    evidence_locator: str,
    source_locator: str,
    summary: str,
) -> None:
    errors.append(
        SurfaceError(
            surface_label=surface_label,
            failure_label=failure_label,
            evidence_locator=evidence_locator,
            source_locator=source_locator,
            summary=summary,
        )
    )


def require_file(path: Path, errors: list[SurfaceError], *, surface_label: str, evidence_locator: str) -> str:
    if not path.exists():
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-missing-source",
            evidence_locator=evidence_locator,
            source_locator=relative_to_root(path),
            summary=f"missing {relative_to_root(path)}",
        )
        return ""
    return path.read_text(encoding="utf-8")


def require_needles(
    path: Path,
    needles: tuple[str, ...],
    errors: list[SurfaceError],
    *,
    surface_label: str,
    evidence_locator: str,
) -> str:
    text = require_file(path, errors, surface_label=surface_label, evidence_locator=evidence_locator)
    for needle in needles:
        if needle not in text:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-missing-required-text",
                evidence_locator=evidence_locator,
                source_locator=relative_to_root(path),
                summary=f"{relative_to_root(path)} must mention `{needle}`",
            )
    return text


def line_locator(path: Path, text: str, start: int) -> str:
    line_number = text.count("\n", 0, start) + 1
    return f"{relative_to_root(path)}:{line_number}"


def forbid_active_installer_evidence(
    path: Path,
    errors: list[SurfaceError],
    *,
    surface_label: str,
    evidence_locator: str,
) -> None:
    text = require_file(path, errors, surface_label=surface_label, evidence_locator=evidence_locator)
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
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-active-installer-evidence",
                evidence_locator=evidence_locator,
                source_locator=line_locator(path, text, match.start()),
                summary=f"must not present loom-installer as active CLI/install/release evidence: `{snippet}`",
            )


def forbid_separate_install_surfaces(
    path: Path,
    errors: list[SurfaceError],
    *,
    surface_label: str,
    evidence_locator: str,
) -> None:
    text = require_file(path, errors, surface_label=surface_label, evidence_locator=evidence_locator)
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
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-separate-install-surface",
                evidence_locator=evidence_locator,
                source_locator=line_locator(path, text, match.start()),
                summary=f"must not present SKILLS, plugins, or loom-installer as separate install surfaces: `{snippet}`",
            )


def assert_pattern_guards(
    errors: list[SurfaceError],
    *,
    surface_label: str,
    evidence_locator: str,
) -> None:
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
    source_locator = "tools/check_release_surface.py#pattern-guard-fixtures"
    for example in negative_examples:
        lowered = example.lower()
        if any(pattern.search(example) and not any(marker in lowered for marker in NEGATED_CONTEXT_MARKERS) for pattern in FORBIDDEN_SEPARATE_INSTALL_SURFACE_PATTERNS):
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-false-positive-fixture",
                evidence_locator=evidence_locator,
                source_locator=source_locator,
                summary=f"CLI-only install guard false-positive fixture failed: {example}",
            )
    for example in positive_examples:
        lowered = example.lower()
        if not any(pattern.search(example) and not any(marker in lowered for marker in NEGATED_CONTEXT_MARKERS) for pattern in FORBIDDEN_SEPARATE_INSTALL_SURFACE_PATTERNS):
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-false-negative-fixture",
                evidence_locator=evidence_locator,
                source_locator=source_locator,
                summary=f"CLI-only install guard failed to reject fixture: {example}",
            )


def check_release_doc_contract(errors: list[SurfaceError]) -> None:
    surface_label = RELEASE_DOC_CONTRACT
    locator = evidence_locator(surface_label)
    require_needles(
        CLI_ONLY_CONTRACT,
        (
            "The only primary user-facing install surface for Loom is the root `loom` CLI",
            "Host plugins are host adapter payloads managed by the `loom` CLI",
            "`SKILLS` are executable scenario payloads managed, synchronized, and verified",
            "`loom-installer` must not gain a new migration journey",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        CLI_RELEASE_DOC,
        (
            "The `loom` CLI release line is the primary release line",
            "GitHub `v*` tag and GitHub Release",
            "Installer npm state is never publish evidence for this judgment",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
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
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        README,
        (
            "Loom CLI release surface",
            "loom-installer deprecated legacy line",
            "users do not install them as a separate surface",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        README_ZH,
        (
            "Loom CLI 发布面",
            "loom-installer deprecated legacy line",
            "用户不再把它们作为独立安装面安装",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        CODEX_INSTALL,
        (
            "The npm installer is not the Codex default path",
            "plugins/loom/skills/",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        UNIFIED_INSTALL,
        (
            "use `loom host install` to install host plugin payloads",
            "Historical: `@mc-and-his-agents/loom-installer` references retained only for deprecated evidence",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        HOST_ADAPTER_MATRIX,
        (
            "embedded skills at `plugins/loom/skills/`",
            "update root CLI, rerun",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )


def check_release_workflow_contract(errors: list[SurfaceError]) -> None:
    surface_label = RELEASE_WORKFLOW_CONTRACT
    locator = evidence_locator(surface_label)
    require_needles(
        CLI_RELEASE_DOC,
        (
            "For `push` events on `main`, `loom-cli-release` automatically creates the GitHub `v*` tag, publishes `@mc-and-his-agents/loom` to npm, and creates the GitHub Release",
            "when the `NPM_TOKEN` secret is missing for an npm publish",
            "must fail closed when CLI publish behavior changed but the current `VERSION` is already published on a different commit",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
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
        surface_label=surface_label,
        evidence_locator=locator,
    )


def check_installer_sunset_guard(errors: list[SurfaceError]) -> None:
    surface_label = INSTALLER_SUNSET_GUARD
    locator = evidence_locator(surface_label)
    require_needles(
        CLI_RELEASE_DOC,
        (
            "`loom-installer` is a deprecated legacy artifact",
            "must not use `@mc-and-his-agents/loom-installer` `latest`",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
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
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        INSTALLER_PR,
        (
            "node packages/loom-installer/scripts/check-version-bump.mjs",
            "python3 tools/check_release_surface.py",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    bump_check = require_needles(
        INSTALLER_BUMP_CHECK,
        (
            "packages/loom-installer/src/",
            "packages/loom-installer/package.json",
            "no installer shim changes",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )

    forbidden_installer_behavior_needles = (
        "plugins/loom/.codex-plugin/|src/skills/|skills/",
        "plugins/loom/.codex-plugin/",
        "'src/skills/**'",
    )
    release_state_section = installer_release.split("Resolve sunset state", 1)[-1]
    for needle in forbidden_installer_behavior_needles:
        if needle in release_state_section:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-installer-shim-scope-expanded",
                evidence_locator=locator,
                source_locator=relative_to_root(INSTALLER_RELEASE),
                summary=f"installer release state must not classify `{needle}` as installer shim behavior",
            )

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
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-active-publish-capability",
                evidence_locator=locator,
                source_locator=relative_to_root(INSTALLER_RELEASE),
                summary=f"installer release workflow must not contain active publish capability `{needle}`",
            )

    for needle in ("plugins/loom/.codex-plugin/", "skills/"):
        if needle in bump_check and "ignoredCompatibilityPaths" not in bump_check:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-shim-bump-scope-expanded",
                evidence_locator=locator,
                source_locator=relative_to_root(INSTALLER_BUMP_CHECK),
                summary=f"installer version bump check must not classify `{needle}` as shim behavior",
            )


def check_forbidden_release_surface_patterns(errors: list[SurfaceError]) -> None:
    surface_label = FORBIDDEN_RELEASE_SURFACE_PATTERNS
    locator = evidence_locator(surface_label)
    for path in ACTIVE_SURFACE_DOCS:
        forbid_active_installer_evidence(path, errors, surface_label=surface_label, evidence_locator=locator)
        forbid_separate_install_surfaces(path, errors, surface_label=surface_label, evidence_locator=locator)
    assert_pattern_guards(errors, surface_label=surface_label, evidence_locator=locator)


SURFACES = (
    SurfaceDefinition(
        label=RELEASE_DOC_CONTRACT,
        description="Release authority docs keep the root loom CLI line, GitHub v* tag/Release, npm package, and deprecated installer boundary separated.",
        evidence_locator=evidence_locator(RELEASE_DOC_CONTRACT),
        run=check_release_doc_contract,
    ),
    SurfaceDefinition(
        label=RELEASE_WORKFLOW_CONTRACT,
        description="loom-cli-release keeps PR judgment read-only, main-push publishing, workflow_dispatch repair, duplicate-version fail-closed handling, and NPM_TOKEN checks.",
        evidence_locator=evidence_locator(RELEASE_WORKFLOW_CONTRACT),
        run=check_release_workflow_contract,
    ),
    SurfaceDefinition(
        label=INSTALLER_SUNSET_GUARD,
        description="loom-installer remains deprecated legacy evidence and does not regain npm publish, installer tag, installer GitHub Release, or active CLI release authority.",
        evidence_locator=evidence_locator(INSTALLER_SUNSET_GUARD),
        run=check_installer_sunset_guard,
    ),
    SurfaceDefinition(
        label=FORBIDDEN_RELEASE_SURFACE_PATTERNS,
        description="Active install/release docs do not present loom-installer, direct SKILLS, or host plugins as separate primary install or release evidence.",
        evidence_locator=evidence_locator(FORBIDDEN_RELEASE_SURFACE_PATTERNS),
        run=check_forbidden_release_surface_patterns,
    ),
)
SURFACE_BY_LABEL = {surface.label: surface for surface in SURFACES}


def release_surface_evidence_line(**fields: object) -> str:
    rendered = " ".join(f"{key}={json.dumps(str(value), sort_keys=True)}" for key, value in fields.items())
    return f"release surface evidence: {rendered}"


def print_surface_evidence(*, stream, **fields: object) -> None:
    print(release_surface_evidence_line(**fields), file=stream)


def select_surfaces(requested: list[str] | None) -> tuple[SurfaceDefinition, ...]:
    if not requested:
        return SURFACES
    if AGGREGATE_RELEASE_SURFACE in requested:
        if len(requested) > 1:
            raise ValueError(f"`{AGGREGATE_RELEASE_SURFACE}` cannot be combined with named surfaces")
        return SURFACES
    return tuple(SURFACE_BY_LABEL[label] for label in requested)


def run_surfaces(selected: tuple[SurfaceDefinition, ...]) -> list[SurfaceError]:
    errors: list[SurfaceError] = []
    for surface in selected:
        surface.run(errors)
    return errors


def print_failures(errors: list[SurfaceError]) -> None:
    print("release surface check failed:", file=sys.stderr)
    for error in errors:
        print_surface_evidence(
            stream=sys.stderr,
            bucket_label="release-surface-validation",
            surface_label=error.surface_label,
            surface_kind="named_surface",
            command=error.evidence_locator,
            result="block",
            failure_label=error.failure_label,
            failure_taxonomy=error.failure_label,
            failure_summary=error.summary,
            source_locator=error.source_locator,
            evidence_locator=error.evidence_locator,
        )
        print(
            "- "
            f"surface_label={error.surface_label} "
            f"failure_label={error.failure_label} "
            f"source_locator={error.source_locator} "
            f"evidence_locator={error.evidence_locator}: "
            f"{error.summary}",
            file=sys.stderr,
        )


def print_pass_evidence(selected: tuple[SurfaceDefinition, ...], *, include_aggregate: bool) -> None:
    for surface in selected:
        print_surface_evidence(
            stream=sys.stdout,
            bucket_label="release-surface-validation",
            surface_label=surface.label,
            surface_kind="named_surface",
            command=surface.evidence_locator,
            result="pass",
            source_locator=surface.evidence_locator,
            evidence_locator=surface.evidence_locator,
            is_aggregate="false",
        )
    if include_aggregate:
        subsurface_results = ",".join(f"{surface.label}:pass" for surface in selected)
        print_surface_evidence(
            stream=sys.stdout,
            bucket_label="release-surface-validation",
            surface_label=AGGREGATE_RELEASE_SURFACE,
            surface_kind="aggregate_surface",
            command="python3 tools/check_release_surface.py",
            result="pass",
            source_locator="python3 tools/check_release_surface.py",
            evidence_locator="python3 tools/check_release_surface.py",
            is_aggregate="true",
            subsurface_count=len(selected),
            subsurface_results=subsurface_results,
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    labels = tuple(surface.label for surface in SURFACES)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--surface",
        action="append",
        choices=(AGGREGATE_RELEASE_SURFACE, *labels),
        help=(
            "Run only the named release validation surface. May be passed more than once. "
            f"Omit to preserve aggregate behavior; use {AGGREGATE_RELEASE_SURFACE} to name the aggregate explicitly."
        ),
    )
    parser.add_argument(
        "--list-surfaces",
        action="store_true",
        help="List available release validation surface names without running checks.",
    )
    parser.add_argument(
        "--show-surface-evidence",
        action="store_true",
        help="Print machine-readable surface evidence on passing checks.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.list_surfaces:
        print(f"{AGGREGATE_RELEASE_SURFACE}\tpython3 tools/check_release_surface.py\tAll release surfaces; preserves aggregate compatibility.")
        for surface in SURFACES:
            print(f"{surface.label}\t{surface.evidence_locator}\t{surface.description}")
        return 0

    try:
        selected = select_surfaces(args.surface)
    except ValueError as exc:
        print(f"release surface check configuration failed: {exc}", file=sys.stderr)
        return 2

    errors = run_surfaces(selected)
    if errors:
        print_failures(errors)
        return 1

    explicitly_named = bool(args.surface)
    aggregate_selected = not args.surface or args.surface == [AGGREGATE_RELEASE_SURFACE]
    if args.show_surface_evidence or explicitly_named:
        print_pass_evidence(selected, include_aggregate=aggregate_selected)

    if len(selected) == len(SURFACES) and aggregate_selected:
        print("release surface check: OK")
    else:
        print("release surface check: OK (" + ", ".join(surface.label for surface in selected) + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
