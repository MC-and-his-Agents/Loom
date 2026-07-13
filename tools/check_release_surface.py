#!/usr/bin/env python3
"""Verify Loom CLI and installer release surfaces stay separated."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
CLI_RELEASE_DOC = ROOT / "docs" / "adoption" / "loom-cli-release-surface.md"
VERSION_AUTHORITY = ROOT / "docs" / "adoption" / "version-authority-map.md"
CLI_RELEASE = ROOT / ".github" / "workflows" / "loom-cli-release.yml"
INSTALLER_PACKAGE = ROOT / "packages" / "loom-installer" / "package.json"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
CODEX_INSTALL = ROOT / "docs" / "adoption" / "codex-install.md"
CLI_ONLY_CONTRACT = ROOT / "docs" / "adoption" / "cli-only-install-contract.md"
UNIFIED_INSTALL = ROOT / "docs" / "adoption" / "unified-install-experience.md"
HOST_ADAPTER_MATRIX = ROOT / "docs" / "adoption" / "host-adapter-matrix.md"
PACKAGE_JSON = ROOT / "package.json"
VERSION = ROOT / "VERSION"

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
INSTALLED_GLOBAL_CLI_SMOKE = "installed-global-cli-smoke"
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
            "HotCP-style stale carrier fixture",
            "carrier closeout-sync",
            "workspace retire",
            "idle` / `no_active_item",
            "`loom release readback` is the local read-only entry for a release intent",
            "`partial_published`",
            "`docs/evidence/fixtures/release-readback-fixtures.json`",
            "auth and host-access diagnosis remains owned by #1597",
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
            "Loom is CLI-first",
            "global `loom` command",
            "metadata-only repository adoption",
            "Codex user-level plugin",
            "Work Item",
            "host-native admission",
            "hosted delivery gate",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    require_needles(
        README_ZH,
        (
            "命令行优先设计",
            "Codex 用户级插件",
            "metadata-only 模式启用仓库",
            "工作项",
            "宿主原生 admission",
            "hosted delivery gate",
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
            "A later CLI source merge with an already published version returns `release_pending` and never republishes that version.",
            "an explicit `workflow_dispatch` publish request names a `VERSION` tag that points at another commit",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    workflow = require_needles(
        CLI_RELEASE,
        (
            "name: loom-cli-release",
            "workflow_dispatch",
            "publish",
            "push",
            "AUTO_PUBLISH_ALLOWED",
            "cli_publish_behavior_changed",
            "reason=release_pending",
            "version-already-published-on-different-commit",
            "PACKAGE_TAG_PREFIX: 'v'",
            "NPM_PACKAGE_NAME: '@mc-and-his-agents/loom'",
            "secrets.NPM_TOKEN",
            "npm publish --access public --provenance",
            "npm view \"${NPM_PACKAGE_NAME}@${NPM_VERSION}\" version",
            "npm pack --dry-run --json --ignore-scripts",
            "python3 tools/stamp_plugin_payload_metadata.py --source-git-sha \"${{ github.sha }}\" --write --json",
            "python3 tools/check_npm_package.py",
            "no-cli-behavior-change",
            "gh release create",
        ),
        errors,
        surface_label=surface_label,
        evidence_locator=locator,
    )
    judgment_start = workflow.find("  release-judgment:\n")
    publisher_start = workflow.find("  release-publisher:\n")
    if judgment_start < 0 or publisher_start < 0 or publisher_start <= judgment_start:
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-missing-permission-split",
            evidence_locator=locator,
            source_locator=relative_to_root(CLI_RELEASE),
            summary="release workflow must separate release-judgment from release-publisher",
        )
        return
    judgment = workflow[judgment_start:publisher_start]
    publisher = workflow[publisher_start:]
    pending_index = judgment.find('reason=release_pending')
    explicit_publish_index = judgment.find('if [ "$PUBLISH_REQUESTED" != "true" ]')
    collision_index = judgment.find('reason=version-already-published-on-different-commit')
    if min(pending_index, explicit_publish_index, collision_index) < 0 or not (
        explicit_publish_index < pending_index < collision_index
    ):
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-release-pending-admission",
            evidence_locator=locator,
            source_locator=relative_to_root(CLI_RELEASE),
            summary=(
                "normal main pushes with an earlier published VERSION must return release_pending, "
                "while explicit publish requests remain fail-closed"
            ),
        )
    for needle in ("contents: read", "persist-credentials: false"):
        if needle not in judgment:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-judgment-permission",
                evidence_locator=locator,
                source_locator=relative_to_root(CLI_RELEASE),
                summary=f"release-judgment must contain `{needle}`",
            )
    for needle in ("contents: write", "id-token: write", "secrets.NPM_TOKEN", "npm publish", "git tag -a", "gh release create"):
        if needle in judgment:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-judgment-privilege-leak",
                evidence_locator=locator,
                source_locator=relative_to_root(CLI_RELEASE),
                summary=f"release-judgment must not contain `{needle}`",
            )
    for needle in (
        "needs: release-judgment",
        "github.event_name == 'push'",
        "github.event_name == 'workflow_dispatch'",
        "needs.release-judgment.outputs.publish_allowed == 'true'",
        "contents: write",
        "id-token: write",
        "secrets.NPM_TOKEN",
        "npm publish",
        "git tag -a",
        "gh release create",
    ):
        if needle not in publisher:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-publisher-contract",
                evidence_locator=locator,
                source_locator=relative_to_root(CLI_RELEASE),
                summary=f"release-publisher must contain `{needle}`",
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
    if INSTALLER_PACKAGE.parent.exists():
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-tracked-tombstone",
            evidence_locator=locator,
            source_locator=relative_to_root(INSTALLER_PACKAGE.parent),
            summary="retired installer metadata must remain in npm/tag history, not in the active source tree",
        )

    for workflow_name in ("node-installer-pr.yml", "node-installer-release.yml"):
        workflow = ROOT / ".github" / "workflows" / workflow_name
        if workflow.exists():
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-active-workflow",
                evidence_locator=locator,
                source_locator=relative_to_root(workflow),
                summary=f"retired installer workflow `{workflow_name}` must be absent",
            )


def check_forbidden_release_surface_patterns(errors: list[SurfaceError]) -> None:
    surface_label = FORBIDDEN_RELEASE_SURFACE_PATTERNS
    locator = evidence_locator(surface_label)
    for path in ACTIVE_SURFACE_DOCS:
        forbid_active_installer_evidence(path, errors, surface_label=surface_label, evidence_locator=locator)
        forbid_separate_install_surfaces(path, errors, surface_label=surface_label, evidence_locator=locator)
    assert_pattern_guards(errors, surface_label=surface_label, evidence_locator=locator)


def command_locator(command: tuple[str, ...]) -> str:
    return " ".join(command)


def compact_output(stdout: str, stderr: str) -> str:
    rendered = "\n".join(part.strip() for part in (stdout, stderr) if part.strip())
    return rendered[:800] if rendered else "<no output>"


def run_command(command: tuple[str, ...], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def check_installed_global_cli_smoke(errors: list[SurfaceError]) -> None:
    surface_label = INSTALLED_GLOBAL_CLI_SMOKE
    locator = evidence_locator(surface_label)
    starting_error_count = len(errors)
    package = require_file(PACKAGE_JSON, errors, surface_label=surface_label, evidence_locator=locator)
    version = require_file(VERSION, errors, surface_label=surface_label, evidence_locator=locator).strip()
    if not package or not version:
        return

    try:
        package_data = json.loads(package)
    except json.JSONDecodeError as exc:
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-invalid-package-json",
            evidence_locator=locator,
            source_locator=relative_to_root(PACKAGE_JSON),
            summary=f"package.json must be valid JSON for installed CLI smoke: {exc}",
        )
        return

    expected_version = version.removeprefix("v")
    if package_data.get("name") != "@mc-and-his-agents/loom":
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-package-name-mismatch",
            evidence_locator=locator,
            source_locator="package.json:name",
            summary="installed CLI smoke requires root package name @mc-and-his-agents/loom",
        )
    if package_data.get("version") != expected_version:
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-package-version-mismatch",
            evidence_locator=locator,
            source_locator="package.json:version",
            summary=f"package.json version must match VERSION without v prefix: {expected_version}",
        )
    if package_data.get("bin", {}).get("loom") != "bin/loom.mjs":
        add_error(
            errors,
            surface_label=surface_label,
            failure_label=f"{surface_label}-bin-contract-mismatch",
            evidence_locator=locator,
            source_locator="package.json:bin.loom",
            summary="installed CLI smoke requires package bin loom -> bin/loom.mjs",
        )
    if len(errors) > starting_error_count:
        return

    with tempfile.TemporaryDirectory(prefix="loom-installed-global-cli-smoke-") as tmp:
        tmp_path = Path(tmp)
        pack_dir = tmp_path / "pack"
        prefix = tmp_path / "global"
        cache = tmp_path / "npm-cache"
        pack_dir.mkdir()
        env = {
            **os.environ,
            "HOME": str(tmp_path / "home"),
            "npm_config_cache": str(cache),
        }
        pack_command = ("npm", "pack", "--pack-destination", str(pack_dir), "--json", "--ignore-scripts")
        pack = run_command(pack_command, cwd=ROOT, env=env)
        if pack.returncode != 0:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-npm-pack-failed",
                evidence_locator=locator,
                source_locator=command_locator(("npm", "pack", "--pack-destination", "<tmp>", "--json", "--ignore-scripts")),
                summary=f"npm pack failed before installed CLI smoke: {compact_output(pack.stdout, pack.stderr)}",
            )
            return
        try:
            pack_payload = json.loads(pack.stdout)
        except json.JSONDecodeError as exc:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-npm-pack-json-invalid",
                evidence_locator=locator,
                source_locator=command_locator(("npm", "pack", "--pack-destination", "<tmp>", "--json", "--ignore-scripts")),
                summary=f"npm pack did not emit JSON for installed CLI smoke: {exc}",
            )
            return

        if not isinstance(pack_payload, list) or not pack_payload or not isinstance(pack_payload[0], dict):
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-npm-pack-empty",
                evidence_locator=locator,
                source_locator=command_locator(("npm", "pack", "--pack-destination", "<tmp>", "--json", "--ignore-scripts")),
                summary="npm pack did not return a package payload for installed CLI smoke",
            )
            return
        tarball_name = pack_payload[0].get("filename")
        tarball = pack_dir / tarball_name if isinstance(tarball_name, str) else None
        if tarball is None or not tarball.exists():
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-pack-tarball-missing",
                evidence_locator=locator,
                source_locator=command_locator(("npm", "pack", "--pack-destination", "<tmp>", "--json", "--ignore-scripts")),
                summary="npm pack did not create a tarball for installed CLI smoke",
            )
            return

        install_command = ("npm", "install", "--global", "--prefix", str(prefix), str(tarball))
        install = run_command(install_command, cwd=ROOT, env=env)
        if install.returncode != 0:
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-npm-install-global-failed",
                evidence_locator=locator,
                source_locator=command_locator(("npm", "install", "--global", "--prefix", "<tmp>/global", "<pack.tgz>")),
                summary=f"temporary global install failed: {compact_output(install.stdout, install.stderr)}",
            )
            return

        bin_dir = prefix / ("Scripts" if sys.platform == "win32" else "bin")
        loom_bin = bin_dir / ("loom.cmd" if sys.platform == "win32" else "loom")
        if not loom_bin.exists():
            add_error(
                errors,
                surface_label=surface_label,
                failure_label=f"{surface_label}-loom-bin-missing",
                evidence_locator=locator,
                source_locator="<tmp>/global/bin/loom",
                summary="temporary global install did not expose the loom bin",
            )
            return

        for args, failure_suffix in (
            (("version", "--json"), "version-command-failed"),
            (("help", "--json"), "help-command-failed"),
        ):
            command = (str(loom_bin), *args)
            completed = run_command(command, cwd=ROOT, env=env)
            if completed.returncode != 0:
                add_error(
                    errors,
                    surface_label=surface_label,
                    failure_label=f"{surface_label}-{failure_suffix}",
                    evidence_locator=locator,
                    source_locator=command_locator(("loom", *args)),
                    summary=f"installed loom {' '.join(args)} failed: {compact_output(completed.stdout, completed.stderr)}",
                )
                return
            try:
                payload = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                add_error(
                    errors,
                    surface_label=surface_label,
                    failure_label=f"{surface_label}-{failure_suffix}-invalid-json",
                    evidence_locator=locator,
                    source_locator=command_locator(("loom", *args)),
                    summary=f"installed loom {' '.join(args)} did not emit JSON: {exc}",
                )
                return
            if payload.get("result") != "pass":
                add_error(
                    errors,
                    surface_label=surface_label,
                    failure_label=f"{surface_label}-{failure_suffix}-blocked",
                    evidence_locator=locator,
                    source_locator=command_locator(("loom", *args)),
                    summary=f"installed loom {' '.join(args)} did not pass",
                )
                return
            if args[0] == "version" and payload.get("versions", {}).get("repo_version") != version:
                add_error(
                    errors,
                    surface_label=surface_label,
                    failure_label=f"{surface_label}-version-output-mismatch",
                    evidence_locator=locator,
                    source_locator="loom version --json",
                    summary=f"installed loom version output must report {version}",
                )
                return
            if args[0] == "help" and not any(command.get("command") == "version" for command in payload.get("commands", [])):
                add_error(
                    errors,
                    surface_label=surface_label,
                    failure_label=f"{surface_label}-help-command-matrix-missing-version",
                    evidence_locator=locator,
                    source_locator="loom help --json",
                    summary="installed loom help output must include the version command",
                )
                return


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
    SurfaceDefinition(
        label=INSTALLED_GLOBAL_CLI_SMOKE,
        description="Temporary global install of the packed root @mc-and-his-agents/loom package exposes the loom bin and runs version/help JSON smoke from the installed package.",
        evidence_locator=evidence_locator(INSTALLED_GLOBAL_CLI_SMOKE),
        run=check_installed_global_cli_smoke,
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
