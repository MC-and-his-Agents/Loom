#!/usr/bin/env python3
"""Stamp Codex plugin payload release metadata before publishing."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import sys
sys.dont_write_bytecode = True
import build_distribution


ROOT = Path(__file__).resolve().parents[1]
VERSION = ROOT / "VERSION"
PACKAGE_JSON = ROOT / "package.json"
PLUGIN_PAYLOAD_ROOT = ROOT / "plugins" / "loom"
PLUGIN_MANIFEST = PLUGIN_PAYLOAD_ROOT / ".codex-plugin" / "plugin.json"
EXPECTED_PACKAGE = "@mc-and-his-agents/loom"
IGNORE_NAMES = {".DS_Store", "__pycache__"}
IGNORE_SUFFIXES = {".pyc"}
HASH_FIELD_RE = re.compile(rb'("plugin_payload_hash"\s*:\s*)("[^"]*"|null)')


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def package_version() -> str:
    package = load_json(PACKAGE_JSON)
    version = VERSION.read_text(encoding="utf-8").strip()
    expected = version[1:] if version.startswith("v") else version
    observed = str(package.get("version") or "")
    if observed != expected:
        raise SystemExit(f"package.json version {observed!r} does not match VERSION {version!r}")
    return observed


def ignored(path: Path) -> bool:
    relative = path.relative_to(PLUGIN_PAYLOAD_ROOT)
    return any(part in IGNORE_NAMES for part in relative.parts) or path.suffix in IGNORE_SUFFIXES


def payload_files() -> list[Path]:
    return sorted(
        (path for path in PLUGIN_PAYLOAD_ROOT.rglob("*") if path.is_file() and not ignored(path)),
        key=lambda path: path.relative_to(PLUGIN_PAYLOAD_ROOT).as_posix(),
    )


def compute_hash() -> dict[str, Any]:
    hasher = hashlib.sha256()
    normalized: list[str] = []
    files = payload_files()
    for path in files:
        relative = path.relative_to(PLUGIN_PAYLOAD_ROOT).as_posix()
        content = path.read_bytes()
        if relative == ".codex-plugin/plugin.json":
            content, substitutions = HASH_FIELD_RE.subn(rb'\1""', content)
            if substitutions:
                normalized.append(relative)
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(content)
        hasher.update(b"\0")
    return {
        "algorithm": "sha256",
        "digest": hasher.hexdigest(),
        "file_count": len(files),
        "normalized_self_references": normalized,
    }


def compute_generated_hash() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="loom-plugin-stamp-") as tmp:
        output = Path(tmp) / "distribution"
        build_distribution.build(output)
        build_distribution.materialize(output, "package")
        try:
            return compute_hash()
        finally:
            build_distribution.clean_materialized("package")


def expected_status(source_git_sha: str) -> str:
    return "pending_release_commit" if source_git_sha == "unreleased" else "release_commit"


def stamp(source_git_sha: str, *, write: bool) -> dict[str, Any]:
    version = package_version()
    manifest = load_json(PLUGIN_MANIFEST)
    x_loom = manifest.setdefault("x-loom", {})
    if not isinstance(x_loom, dict):
        raise SystemExit("plugins/loom/.codex-plugin/plugin.json x-loom must be an object")

    x_loom["source_package"] = EXPECTED_PACKAGE
    x_loom["source_package_version"] = version
    x_loom["source_git_sha"] = source_git_sha
    x_loom["source_git_sha_status"] = expected_status(source_git_sha)
    x_loom["plugin_payload_version"] = version
    x_loom["plugin_payload_hash"] = ""

    if write:
        write_json(PLUGIN_MANIFEST, manifest)

    digest = compute_generated_hash()["digest"] if write else None
    if write:
        manifest = load_json(PLUGIN_MANIFEST)
        manifest["x-loom"]["plugin_payload_hash"] = digest
        write_json(PLUGIN_MANIFEST, manifest)
        hash_payload = compute_generated_hash()
    else:
        current_hash = compute_generated_hash()
        digest = current_hash["digest"]
        hash_payload = current_hash

    manifest = load_json(PLUGIN_MANIFEST)
    current = manifest.get("x-loom", {})
    expected = {
        "source_package": EXPECTED_PACKAGE,
        "source_package_version": version,
        "source_git_sha": source_git_sha,
        "source_git_sha_status": expected_status(source_git_sha),
        "plugin_payload_version": version,
        "plugin_payload_hash": hash_payload["digest"],
    }
    mismatches = {
        key: {"expected": value, "observed": current.get(key)}
        for key, value in expected.items()
        if current.get(key) != value
    }
    return {
        "schema_version": "loom-plugin-payload-metadata-stamp/v1",
        "result": "pass" if not mismatches else "block",
        "write": write,
        "manifest": "plugins/loom/.codex-plugin/plugin.json",
        "source_package": EXPECTED_PACKAGE,
        "source_package_version": version,
        "source_git_sha": source_git_sha,
        "source_git_sha_status": expected_status(source_git_sha),
        "plugin_payload_version": version,
        "plugin_payload_hash": hash_payload["digest"],
        "plugin_payload_hash_algorithm": hash_payload["algorithm"],
        "plugin_payload_file_count": hash_payload["file_count"],
        "normalized_self_references": hash_payload["normalized_self_references"],
        "mismatches": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = stamp(args.source_git_sha, write=args.write)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif payload["result"] == "pass":
        print(
            "plugin payload metadata stamp: "
            f"{payload['source_package_version']} {payload['source_git_sha']} {payload['plugin_payload_hash']}"
        )
    if payload["result"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
