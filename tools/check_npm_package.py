#!/usr/bin/env python3
"""Validate the root Loom npm package manifest and dry-run payload surfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = REPO_ROOT / "package.json"
VERSION = REPO_ROOT / "VERSION"
PLUGIN_PAYLOAD_ROOT = REPO_ROOT / "plugins" / "loom"
PLUGIN_MANIFEST = PLUGIN_PAYLOAD_ROOT / ".codex-plugin" / "plugin.json"

EXPECTED_PACKAGE = "@mc-and-his-agents/loom"
EXPECTED_BIN = "bin/loom.mjs"
REQUIRED_FILES = {
    "package.json",
    "bin/loom.mjs",
    "tools/loom.py",
    "tools/runtime_wrapper.py",
    "tools/loom_flow.py",
    "tools/loom_init.py",
    "tools/loom_check.py",
    "tools/check_npm_package.py",
    "plugins/loom/.codex-plugin/plugin.json",
    "plugins/loom/skills/registry.json",
    "plugins/loom/skills/loom-init/SKILL.md",
    "src/skills/registry.json",
    "docs/adoption/cli-only-install-contract.md",
    "docs/adoption/loom-cli-release-surface.md",
    "docs/adoption/version-authority-map.md",
    "docs/adoption/codex-install.md",
    "docs/adoption/legacy-install-migration.md",
    "docs/adoption/github-profile.md",
    "docs/methodology/harness/cli-command-matrix.md",
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/harness/gate-chain.md",
    "docs/methodology/harness/task-carrier-contract.md",
    "docs/methodology/templates/consistency-analysis.md",
    "docs/methodology/templates/evidence-map.md",
    "docs/methodology/templates/execution-breakdown.md",
    "docs/methodology/templates/spec-suite.md",
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
    "skills/",
)
FORBIDDEN_PATH_PARTS = (
    "/__pycache__/",
    "__pycache__/",
    ".pyc",
)
FORBIDDEN_MANIFEST_STRINGS = (
    "@mc-and-his-agents/loom-installer",
    "loom-installer",
    "packages/loom-installer",
)
REQUIRED_MANIFEST_FILES = (
    "src/skills",
    "plugins/loom",
    "docs/adoption/github-profile.md",
    "docs/adoption/legacy-install-migration.md",
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/harness/gate-chain.md",
    "docs/methodology/harness/task-carrier-contract.md",
    "docs/methodology/templates/consistency-analysis.md",
    "docs/methodology/templates/evidence-map.md",
    "docs/methodology/templates/execution-breakdown.md",
    "docs/methodology/templates/spec-suite.md",
)
SURFACE_AGGREGATE = "aggregate"
SURFACE_MANIFEST = "npm-package-manifest"
SURFACE_PAYLOAD = "npm-pack-payload"
SURFACE_PLUGIN_PAYLOAD_HASH = "plugin-payload-hash"
SURFACE_RUNTIME_COPY_PARITY = "runtime-copy-parity"
PLUGIN_PAYLOAD_IGNORE_NAMES = {".DS_Store", "__pycache__"}
PLUGIN_PAYLOAD_IGNORE_SUFFIXES = {".pyc"}
PLUGIN_PAYLOAD_HASH_FIELD_RE = re.compile(
    rb'("plugin_payload_hash"\s*:\s*)("[^"]*"|null)'
)


@dataclass(frozen=True)
class SurfaceDefinition:
    name: str
    command: str
    description: str
    evidence_locators: tuple[str, ...]
    evidence_labels: tuple[str, ...]
    failure_label: str


SURFACES: dict[str, SurfaceDefinition] = {
    SURFACE_AGGREGATE: SurfaceDefinition(
        name=SURFACE_AGGREGATE,
        command="python3 tools/check_npm_package.py",
        description="Aggregate npm package validation; runs manifest, packed payload, plugin hash, and runtime copy parity checks.",
        evidence_locators=(
            "package.json",
            "VERSION",
            "npm pack --dry-run --json --ignore-scripts",
            "plugins/loom",
        ),
        evidence_labels=(SURFACE_MANIFEST, SURFACE_PAYLOAD, SURFACE_PLUGIN_PAYLOAD_HASH, SURFACE_RUNTIME_COPY_PARITY),
        failure_label="npm-package-validation-failed",
    ),
    SURFACE_MANIFEST: SurfaceDefinition(
        name=SURFACE_MANIFEST,
        command=f"python3 tools/check_npm_package.py --surface {SURFACE_MANIFEST}",
        description="Root package manifest validation for name, version, bin, publish config, global CLI, source skills, and Codex user plugin payload.",
        evidence_locators=("package.json", "VERSION"),
        evidence_labels=(SURFACE_MANIFEST,),
        failure_label="npm-package-manifest-failed",
    ),
    SURFACE_PAYLOAD: SurfaceDefinition(
        name=SURFACE_PAYLOAD,
        command=f"python3 tools/check_npm_package.py --surface {SURFACE_PAYLOAD}",
        description="Dry-run npm pack payload validation for required and forbidden package contents.",
        evidence_locators=(
            "package.json",
            "npm pack --dry-run --json --ignore-scripts",
        ),
        evidence_labels=(SURFACE_PAYLOAD,),
        failure_label="npm-pack-payload-failed",
    ),
    SURFACE_PLUGIN_PAYLOAD_HASH: SurfaceDefinition(
        name=SURFACE_PLUGIN_PAYLOAD_HASH,
        command=f"python3 tools/check_npm_package.py --surface {SURFACE_PLUGIN_PAYLOAD_HASH}",
        description="Deterministic SHA-256 validation for the installable Codex plugin payload under plugins/loom.",
        evidence_locators=("plugins/loom", "plugins/loom/.codex-plugin/plugin.json"),
        evidence_labels=(SURFACE_PLUGIN_PAYLOAD_HASH,),
        failure_label="plugin-payload-hash-failed",
    ),
    SURFACE_RUNTIME_COPY_PARITY: SurfaceDefinition(
        name=SURFACE_RUNTIME_COPY_PARITY,
        command=f"python3 tools/check_npm_package.py --surface {SURFACE_RUNTIME_COPY_PARITY}",
        description="Exact parity check for shared runtime copies across source, generated skills, plugin payload, and repo-local .loom/bin.",
        evidence_locators=("skills/shared/scripts", "src/skills/shared/scripts", "plugins/loom/skills/shared/scripts", ".loom/bin"),
        evidence_labels=(SURFACE_RUNTIME_COPY_PARITY,),
        failure_label="runtime-copy-parity-failed",
    ),
}
SURFACE_ALIASES = {
    SURFACE_AGGREGATE: SURFACE_AGGREGATE,
    "all": SURFACE_AGGREGATE,
    "manifest": SURFACE_MANIFEST,
    SURFACE_MANIFEST: SURFACE_MANIFEST,
    "payload": SURFACE_PAYLOAD,
    SURFACE_PAYLOAD: SURFACE_PAYLOAD,
    "plugin-hash": SURFACE_PLUGIN_PAYLOAD_HASH,
    SURFACE_PLUGIN_PAYLOAD_HASH: SURFACE_PLUGIN_PAYLOAD_HASH,
    "runtime-parity": SURFACE_RUNTIME_COPY_PARITY,
    SURFACE_RUNTIME_COPY_PARITY: SURFACE_RUNTIME_COPY_PARITY,
}


class ValidationFailure(AssertionError):
    def __init__(
        self,
        surface: str,
        message: str,
        *,
        evidence_locators: tuple[str, ...] | None = None,
        fallback_to: tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(message)
        self.surface = surface
        self.message = message
        definition = SURFACES[surface]
        self.evidence_locators = evidence_locators or definition.evidence_locators
        self.fallback_to = fallback_to or definition.evidence_locators

    @property
    def failure_label(self) -> str:
        return SURFACES[self.surface].failure_label

    def __str__(self) -> str:
        return self.message


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(
    surface: str,
    message: str,
    *,
    evidence_locators: tuple[str, ...] | None = None,
    fallback_to: tuple[str, ...] | None = None,
) -> None:
    raise ValidationFailure(surface, message, evidence_locators=evidence_locators, fallback_to=fallback_to)


def npm_version_from_root() -> str:
    version = VERSION.read_text(encoding="utf-8").strip()
    if not version.startswith("v"):
        fail(SURFACE_MANIFEST, f"VERSION must use v-prefixed release form, got {version!r}", evidence_locators=("VERSION",))
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
        fail(
            SURFACE_PAYLOAD,
            f"npm pack --dry-run failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}",
            evidence_locators=("npm pack --dry-run --json --ignore-scripts",),
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(
            SURFACE_PAYLOAD,
            f"npm pack --dry-run did not emit JSON: {exc}\n{completed.stdout}",
            evidence_locators=("npm pack --dry-run --json --ignore-scripts",),
        )
    if not isinstance(payload, list) or not payload:
        fail(
            SURFACE_PAYLOAD,
            "npm pack --dry-run returned an empty payload",
            evidence_locators=("npm pack --dry-run --json --ignore-scripts",),
        )
    files = payload[0].get("files", [])
    return {item.get("path", "") for item in files if isinstance(item, dict)}


def validate_manifest() -> dict[str, Any]:
    package = load_json(PACKAGE_JSON)
    if package.get("name") != EXPECTED_PACKAGE:
        fail(SURFACE_MANIFEST, f"package name must be {EXPECTED_PACKAGE}", evidence_locators=("package.json:name",))
    if package.get("version") != npm_version_from_root():
        fail(
            SURFACE_MANIFEST,
            "package version must match root VERSION without the v prefix",
            evidence_locators=("package.json:version", "VERSION"),
        )
    if package.get("bin", {}).get("loom") != EXPECTED_BIN:
        fail(SURFACE_MANIFEST, f"bin loom must point at {EXPECTED_BIN}", evidence_locators=("package.json:bin.loom",))
    if package.get("publishConfig", {}).get("access") != "public":
        fail(
            SURFACE_MANIFEST,
            "publishConfig.access must be public",
            evidence_locators=("package.json:publishConfig.access",),
        )
    manifest_text = json.dumps(package, sort_keys=True)
    for forbidden in FORBIDDEN_MANIFEST_STRINGS:
        if forbidden in manifest_text:
            fail(
                SURFACE_MANIFEST,
                f"root package manifest must not reference deprecated installer surface: {forbidden}",
                evidence_locators=("package.json",),
            )
    manifest_files = package.get("files")
    if not isinstance(manifest_files, list):
        fail(
            SURFACE_MANIFEST,
            "package files must explicitly enumerate the root CLI payload",
            evidence_locators=("package.json:files",),
        )
    missing_manifest_files = sorted(item for item in REQUIRED_MANIFEST_FILES if item not in manifest_files)
    if missing_manifest_files:
        fail(
            SURFACE_MANIFEST,
            f"package files must include global CLI and Codex user plugin payload surfaces: {missing_manifest_files}",
            evidence_locators=("package.json:files",),
        )
    forbidden_manifest_files = sorted(item for item in manifest_files if isinstance(item, str) and item.startswith(FORBIDDEN_PREFIXES))
    if forbidden_manifest_files:
        fail(
            SURFACE_MANIFEST,
            f"package files must not include forbidden repository/internal surfaces: {forbidden_manifest_files}",
            evidence_locators=("package.json:files",),
        )
    return package


def validate_payload() -> set[str]:
    missing_sources = sorted(path for path in REQUIRED_FILES if not (REPO_ROOT / path).exists())
    if missing_sources:
        fail(
            SURFACE_PAYLOAD,
            f"required package source files are missing: {missing_sources}",
            evidence_locators=tuple(missing_sources),
        )

    pack_files = npm_pack_files()
    missing_pack_files = sorted(REQUIRED_FILES - pack_files)
    if missing_pack_files:
        fail(
            SURFACE_PAYLOAD,
            f"npm pack payload is missing required files: {missing_pack_files}",
            evidence_locators=("npm pack --dry-run --json --ignore-scripts",),
        )

    forbidden = sorted(path for path in pack_files if path.startswith(FORBIDDEN_PREFIXES))
    if forbidden:
        fail(
            SURFACE_PAYLOAD,
            f"npm pack payload contains forbidden repository/internal files: {forbidden[:20]}",
            evidence_locators=("npm pack --dry-run --json --ignore-scripts",),
        )
    forbidden_parts = sorted(
        path
        for path in pack_files
        if any(part in path for part in FORBIDDEN_PATH_PARTS)
    )
    if forbidden_parts:
        fail(
            SURFACE_PAYLOAD,
            f"npm pack payload contains Python cache files: {forbidden_parts[:20]}",
            evidence_locators=("npm pack --dry-run --json --ignore-scripts",),
        )
    return pack_files


def ignored_plugin_payload_path(path: Path, payload_root: Path) -> bool:
    relative = path.relative_to(payload_root)
    if any(part in PLUGIN_PAYLOAD_IGNORE_NAMES for part in relative.parts):
        return True
    return path.suffix in PLUGIN_PAYLOAD_IGNORE_SUFFIXES


def plugin_payload_files(payload_root: Path = PLUGIN_PAYLOAD_ROOT) -> list[Path]:
    return sorted(
        (
            path
            for path in payload_root.rglob("*")
            if path.is_file() and not ignored_plugin_payload_path(path, payload_root)
        ),
        key=lambda path: path.relative_to(payload_root).as_posix(),
    )


def plugin_payload_root_label(payload_root: Path) -> str:
    try:
        return payload_root.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(payload_root)


def compute_plugin_payload_hash(payload_root: Path = PLUGIN_PAYLOAD_ROOT) -> dict[str, Any]:
    hasher = hashlib.sha256()
    files = plugin_payload_files(payload_root)
    normalized_files: list[str] = []
    for path in files:
        relative = path.relative_to(payload_root).as_posix()
        content = path.read_bytes()
        if relative == ".codex-plugin/plugin.json":
            content, substitutions = PLUGIN_PAYLOAD_HASH_FIELD_RE.subn(rb'\1""', content)
            if substitutions:
                normalized_files.append(relative)
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(content)
        hasher.update(b"\0")
    return {
        "algorithm": "sha256",
        "digest": hasher.hexdigest(),
        "file_count": len(files),
        "payload_root": plugin_payload_root_label(payload_root),
        "ignored_names": sorted(PLUGIN_PAYLOAD_IGNORE_NAMES),
        "ignored_suffixes": sorted(PLUGIN_PAYLOAD_IGNORE_SUFFIXES),
        "normalized_self_references": normalized_files,
        "files": [path.relative_to(payload_root).as_posix() for path in files],
    }


def expected_plugin_payload_metadata() -> dict[str, str]:
    package = load_json(PACKAGE_JSON)
    package_version = str(package.get("version") or "")
    version_file = VERSION.read_text(encoding="utf-8").strip()
    version_without_prefix = version_file[1:] if version_file.startswith("v") else version_file
    if package_version != version_without_prefix:
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            f"package.json version {package_version!r} does not match VERSION {version_file!r}",
            evidence_locators=("package.json", "VERSION"),
        )
    return {
        "source_package": EXPECTED_PACKAGE,
        "source_package_version": package_version,
        "plugin_payload_version": package_version,
    }


def validate_plugin_payload_hash() -> dict[str, Any]:
    if not PLUGIN_PAYLOAD_ROOT.is_dir():
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "plugin payload root is missing: plugins/loom",
            evidence_locators=("plugins/loom",),
        )
    if not PLUGIN_MANIFEST.is_file():
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "plugin manifest is missing: plugins/loom/.codex-plugin/plugin.json",
            evidence_locators=("plugins/loom/.codex-plugin/plugin.json",),
        )
    computed = compute_plugin_payload_hash(PLUGIN_PAYLOAD_ROOT)
    if computed["file_count"] == 0:
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "plugin payload hash has no input files",
            evidence_locators=("plugins/loom",),
        )
    manifest = load_json(PLUGIN_MANIFEST)
    x_loom = manifest.get("x-loom")
    if not isinstance(x_loom, dict):
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "plugin manifest x-loom metadata is missing",
            evidence_locators=("plugins/loom/.codex-plugin/plugin.json:x-loom",),
        )
    expected_metadata = expected_plugin_payload_metadata()
    metadata_errors = [
        f"{key}={x_loom.get(key)!r} expected {expected!r}"
        for key, expected in expected_metadata.items()
        if x_loom.get(key) != expected
    ]
    source_git_sha = x_loom.get("source_git_sha")
    if not isinstance(source_git_sha, str) or not source_git_sha:
        metadata_errors.append("source_git_sha must be a non-empty string")
    if metadata_errors:
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "plugin release metadata is missing or stale: " + "; ".join(metadata_errors),
            evidence_locators=("plugins/loom/.codex-plugin/plugin.json:x-loom", "package.json", "VERSION"),
        )
    declared_hash = x_loom.get("plugin_payload_hash") if isinstance(x_loom, dict) else None
    if not isinstance(declared_hash, str) or not declared_hash:
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "plugin manifest x-loom.plugin_payload_hash is missing",
            evidence_locators=("plugins/loom/.codex-plugin/plugin.json:x-loom.plugin_payload_hash",),
        )
    if declared_hash is not None and declared_hash != computed["digest"]:
        fail(
            SURFACE_PLUGIN_PAYLOAD_HASH,
            "declared plugin_payload_hash does not match the current plugins/loom payload",
            evidence_locators=("plugins/loom/.codex-plugin/plugin.json:x-loom.plugin_payload_hash", "plugins/loom"),
        )
    computed["declared_hash"] = declared_hash
    computed["declared_hash_status"] = "matched"
    computed["release_metadata"] = {
        "source_package": x_loom.get("source_package"),
        "source_package_version": x_loom.get("source_package_version"),
        "source_git_sha": source_git_sha,
        "plugin_payload_version": x_loom.get("plugin_payload_version"),
    }
    return computed


RUNTIME_COPY_ROOTS = (
    "skills/shared/scripts",
    "src/skills/shared/scripts",
    "plugins/loom/skills/shared/scripts",
    ".loom/bin",
)
RUNTIME_COPY_FILES = (
    "authority_contract.py",
    "failure_envelope.py",
    "execution_attempts.py",
    "github_admission.py",
    "github_host.py",
    "loom_init.py",
    "fact_chain_support.py",
    "governance_surface.py",
    "loom_flow.py",
    "loom_status.py",
    "runtime_paths.py",
    "runtime_state.py",
    "loom_check.py",
    "loom_story_carriers.py",
)
RUNTIME_COPY_PAIRS = tuple(
    (f"{left}/{name}", f"{right}/{name}")
    for name in RUNTIME_COPY_FILES
    for left, right in zip(RUNTIME_COPY_ROOTS, RUNTIME_COPY_ROOTS[1:])
)


def validate_runtime_copy_parity() -> dict[str, Any]:
    drifted: list[str] = []
    missing: list[str] = []
    for source, copy in RUNTIME_COPY_PAIRS:
        source_path = REPO_ROOT / source
        copy_path = REPO_ROOT / copy
        if not source_path.exists() or not copy_path.exists():
            missing.append(f"{source} -> {copy}")
            continue
        if source_path.read_bytes() != copy_path.read_bytes():
            drifted.append(f"{source} -> {copy}")
    if missing or drifted:
        details = []
        if missing:
            details.append("missing runtime copy pairs: " + ", ".join(missing))
        if drifted:
            details.append("drifted runtime copy pairs: " + ", ".join(drifted))
        fail(
            SURFACE_RUNTIME_COPY_PARITY,
            "; ".join(details),
            evidence_locators=RUNTIME_COPY_ROOTS,
            fallback_to=("sync shared runtime copies across skills, src/skills, plugin payload, and .loom/bin",),
        )
    return {
        "pair_count": len(RUNTIME_COPY_PAIRS),
        "pairs": [{"source": source, "copy": copy} for source, copy in RUNTIME_COPY_PAIRS],
    }


def surface_pass(surface: str, *, payload_file_count: int | None = None) -> dict[str, Any]:
    definition = SURFACES[surface]
    payload: dict[str, Any] = {
        "surface": surface,
        "result": "pass",
        "evidence_labels": list(definition.evidence_labels),
        "evidence_locators": list(definition.evidence_locators),
        "command": definition.command,
    }
    if payload_file_count is not None:
        payload["payload_file_count"] = payload_file_count
    return payload


def emit_manifest_pass(package: dict[str, Any]) -> None:
    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "surface": SURFACE_MANIFEST,
        "package": EXPECTED_PACKAGE,
        "version": package["version"],
        "bin": "loom",
        "required_manifest_files": sorted(REQUIRED_MANIFEST_FILES),
        "forbidden_prefixes": list(FORBIDDEN_PREFIXES),
        "evidence_label": SURFACE_MANIFEST,
        "evidence_locators": list(SURFACES[SURFACE_MANIFEST].evidence_locators),
    }, indent=2))


def emit_payload_pass(pack_files: set[str]) -> None:
    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "surface": SURFACE_PAYLOAD,
        "package": EXPECTED_PACKAGE,
        "payload_file_count": len(pack_files),
        "required_files": sorted(REQUIRED_FILES),
        "forbidden_prefixes": list(FORBIDDEN_PREFIXES),
        "forbidden_path_parts": list(FORBIDDEN_PATH_PARTS),
        "evidence_label": SURFACE_PAYLOAD,
        "evidence_locators": list(SURFACES[SURFACE_PAYLOAD].evidence_locators),
    }, indent=2))


def emit_plugin_payload_hash_pass(hash_payload: dict[str, Any]) -> None:
    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "surface": SURFACE_PLUGIN_PAYLOAD_HASH,
        "package": EXPECTED_PACKAGE,
        "plugin_payload_hash": hash_payload["digest"],
        "plugin_payload_hash_algorithm": hash_payload["algorithm"],
        "plugin_payload_file_count": hash_payload["file_count"],
        "declared_hash_status": hash_payload["declared_hash_status"],
        "normalized_self_references": hash_payload["normalized_self_references"],
        "release_metadata": hash_payload["release_metadata"],
        "ignored_names": hash_payload["ignored_names"],
        "ignored_suffixes": hash_payload["ignored_suffixes"],
        "evidence_label": SURFACE_PLUGIN_PAYLOAD_HASH,
        "evidence_locators": list(SURFACES[SURFACE_PLUGIN_PAYLOAD_HASH].evidence_locators),
    }, indent=2))


def emit_runtime_copy_parity_pass(parity_payload: dict[str, Any]) -> None:
    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "surface": SURFACE_RUNTIME_COPY_PARITY,
        "pair_count": parity_payload["pair_count"],
        "pairs": parity_payload["pairs"],
        "evidence_label": SURFACE_RUNTIME_COPY_PARITY,
        "evidence_locators": list(SURFACES[SURFACE_RUNTIME_COPY_PARITY].evidence_locators),
    }, indent=2))


def emit_aggregate_pass(package: dict[str, Any], pack_files: set[str], hash_payload: dict[str, Any], parity_payload: dict[str, Any]) -> None:
    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "surface": SURFACE_AGGREGATE,
        "package": EXPECTED_PACKAGE,
        "version": package["version"],
        "bin": "loom",
        "payload_file_count": len(pack_files),
        "plugin_payload_hash": hash_payload["digest"],
        "plugin_payload_file_count": hash_payload["file_count"],
        "required_files": sorted(REQUIRED_FILES),
        "required_manifest_files": sorted(REQUIRED_MANIFEST_FILES),
        "forbidden_prefixes": list(FORBIDDEN_PREFIXES),
        "forbidden_path_parts": list(FORBIDDEN_PATH_PARTS),
        "runtime_copy_pair_count": parity_payload["pair_count"],
        "evidence_labels": [SURFACE_MANIFEST, SURFACE_PAYLOAD, SURFACE_PLUGIN_PAYLOAD_HASH, SURFACE_RUNTIME_COPY_PARITY],
        "evidence_locators": list(SURFACES[SURFACE_AGGREGATE].evidence_locators),
        "surfaces": [
            surface_pass(SURFACE_MANIFEST),
            surface_pass(SURFACE_PAYLOAD, payload_file_count=len(pack_files)),
            {
                **surface_pass(SURFACE_PLUGIN_PAYLOAD_HASH),
                "plugin_payload_hash": hash_payload["digest"],
                "plugin_payload_file_count": hash_payload["file_count"],
                "declared_hash_status": hash_payload["declared_hash_status"],
                "normalized_self_references": hash_payload["normalized_self_references"],
            },
            {
                **surface_pass(SURFACE_RUNTIME_COPY_PARITY),
                "runtime_copy_pair_count": parity_payload["pair_count"],
            },
        ],
    }, indent=2))


def emit_surface_list() -> None:
    print(json.dumps({
        "schema_version": "loom-npm-package-check/v1",
        "result": "pass",
        "surfaces": [
            {
                "surface": definition.name,
                "command": definition.command,
                "description": definition.description,
                "evidence_labels": list(definition.evidence_labels),
                "evidence_locators": list(definition.evidence_locators),
                "failure_label": definition.failure_label,
            }
            for definition in SURFACES.values()
        ],
    }, indent=2))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--surface",
        choices=sorted(SURFACE_ALIASES),
        default=SURFACE_AGGREGATE,
        help=(
            "Validation surface to run. Stable surfaces: aggregate, "
            f"{SURFACE_MANIFEST}, {SURFACE_PAYLOAD}, {SURFACE_PLUGIN_PAYLOAD_HASH}, {SURFACE_RUNTIME_COPY_PARITY}."
        ),
    )
    parser.add_argument(
        "--list-surfaces",
        action="store_true",
        help="List targetable npm package validation surfaces and their evidence locators.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or [])
    if args.list_surfaces:
        emit_surface_list()
        return 0

    surface = SURFACE_ALIASES[args.surface]
    if surface == SURFACE_MANIFEST:
        emit_manifest_pass(validate_manifest())
        return 0
    if surface == SURFACE_PAYLOAD:
        emit_payload_pass(validate_payload())
        return 0
    if surface == SURFACE_PLUGIN_PAYLOAD_HASH:
        emit_plugin_payload_hash_pass(validate_plugin_payload_hash())
        return 0
    if surface == SURFACE_RUNTIME_COPY_PARITY:
        emit_runtime_copy_parity_pass(validate_runtime_copy_parity())
        return 0

    package = validate_manifest()
    pack_files = validate_payload()
    hash_payload = validate_plugin_payload_hash()
    parity_payload = validate_runtime_copy_parity()
    emit_aggregate_pass(package, pack_files, hash_payload, parity_payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ValidationFailure as exc:
        print(json.dumps({
            "schema_version": "loom-npm-package-check/v1",
            "result": "block",
            "surface": exc.surface,
            "evidence_label": exc.surface,
            "failure_label": exc.failure_label,
            "failed_layer": exc.surface,
            "fail_closed_reason": str(exc),
            "evidence_locators": list(exc.evidence_locators),
            "fallback_to": list(exc.fallback_to),
        }, indent=2), file=sys.stderr)
        raise SystemExit(1)
