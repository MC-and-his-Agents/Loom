#!/usr/bin/env python3
"""Build deterministic Loom runtime payloads from the canonical Python source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
CANONICAL_SKILLS = ROOT / "src" / "skills"
DEFAULT_OUTPUT = ROOT / "build" / "loom-distribution"
RUNTIME_NAMES = (
    "authority_contract.py",
    "closeout_flow.py",
    "companion_contract.py",
    "delivery_control.py",
    "execution_attempts.py",
    "execution_flow.py",
    "fact_chain_support.py",
    "failure_envelope.py",
    "flow_runtime.py",
    "github_admission.py",
    "github_host.py",
    "governance_surface.py",
    "host_attestation.py",
    "host_profile.py",
    "live_smoke.py",
    "loom_check.py",
    "loom_flow.py",
    "loom_init.py",
    "loom_status.py",
    "loom_story_carriers.py",
    "product_acceptance.py",
    "review_flow.py",
    "runtime_paths.py",
    "runtime_state.py",
)
RUNTIME_MANIFEST_NAME = "distribution-manifest.json"
GENERATOR = "tools/build_distribution.py"
RECEIPT_SCHEMA = "loom-materialization-receipt/v1"
ROW_KEYS = {"path", "sha256", "size"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target, copy_function=shutil.copy2)


def owned_build_output(output: Path) -> bool:
    manifest = output / "manifest.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        isinstance(payload, dict)
        and set(payload) == {
            "schema_version", "generator", "canonical_root", "output_root",
            "aggregate_sha256", "file_count", "files",
        }
        and payload.get("schema_version") == "loom-generated-distribution/v1"
        and payload.get("generator") == GENERATOR
        and payload.get("canonical_root") == "src/skills"
        and payload.get("output_root") == "."
    )


def validate_output_path(output: Path, *, allow_missing: bool = True) -> Path:
    resolved = output.resolve()
    protected = (ROOT.resolve(), CANONICAL_SKILLS.resolve())
    if resolved == Path(resolved.anchor) or any(resolved == path or path.is_relative_to(resolved) for path in protected):
        raise RuntimeError(f"refusing unsafe distribution output path: {resolved}")
    allowed_roots = ((ROOT / "build").resolve(), Path(tempfile.gettempdir()).resolve())
    if resolved in allowed_roots or not any(resolved.is_relative_to(root) for root in allowed_roots):
        raise RuntimeError(f"distribution output must stay under build/ or the system temporary root: {resolved}")
    if resolved.exists() and not owned_build_output(resolved):
        raise RuntimeError(f"refusing to replace non-owned distribution output: {resolved}")
    if not resolved.exists() and not allow_missing:
        raise RuntimeError(f"distribution output does not exist: {resolved}")
    return resolved


def build(output: Path) -> dict[str, object]:
    if not CANONICAL_SKILLS.is_dir():
        raise RuntimeError(f"missing canonical source: {CANONICAL_SKILLS}")
    output = validate_output_path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent))
    copy_tree(CANONICAL_SKILLS, staging / "skills")
    plugin_root = staging / "plugins" / "loom"
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    shutil.copy2(ROOT / "plugins" / "loom" / ".codex-plugin" / "plugin.json", plugin_root / ".codex-plugin" / "plugin.json")
    copy_tree(CANONICAL_SKILLS, plugin_root / "skills")
    shared = CANONICAL_SKILLS / "shared" / "scripts"
    for runtime_root in (staging / "repo-runtime", staging / "example-runtime"):
        runtime_root.mkdir()
        for name in RUNTIME_NAMES:
            source = shared / name
            if not source.is_file():
                raise RuntimeError(f"canonical runtime source is missing: {source.relative_to(ROOT)}")
            shutil.copy2(source, runtime_root / name)

    files = sorted(path for path in staging.rglob("*") if path.is_file())
    rows = [
        {"path": path.relative_to(staging).as_posix(), "sha256": sha256(path), "size": path.stat().st_size}
        for path in files
    ]
    aggregate = hashlib.sha256(
        "".join(f"{row['path']}\0{row['sha256']}\n" for row in rows).encode("utf-8")
    ).hexdigest()
    manifest: dict[str, object] = {
        "schema_version": "loom-generated-distribution/v1",
        "generator": GENERATOR,
        "canonical_root": "src/skills",
        "output_root": ".",
        "aggregate_sha256": aggregate,
        "file_count": len(rows),
        "files": rows,
    }
    (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    backup = output.with_name(f".{output.name}.previous-{os.getpid()}")
    try:
        if output.exists():
            os.replace(output, backup)
        os.replace(staging, output)
        if backup.exists():
            shutil.rmtree(backup)
    except BaseException:
        if not output.exists() and backup.exists():
            os.replace(backup, output)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return manifest


def runtime_manifest(manifest: dict[str, object], prefix: str) -> dict[str, object]:
    rows = manifest.get("files")
    selected = [
        {"path": str(row["path"]).removeprefix(prefix), "sha256": row["sha256"], "size": row["size"]}
        for row in rows if isinstance(row, dict) and str(row.get("path", "")).startswith(prefix)
    ] if isinstance(rows, list) else []
    selected.sort(key=lambda row: str(row["path"]))
    aggregate = hashlib.sha256(
        "".join(f"{row['path']}\0{row['sha256']}\n" for row in selected).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": "loom-generated-repo-runtime/v1",
        "generator": GENERATOR,
        "canonical_root": "src/skills/shared/scripts",
        "output_root": ".",
        "aggregate_sha256": aggregate,
        "file_count": len(selected),
        "files": selected,
    }


def validated_distribution(output: Path) -> dict[str, object]:
    output = validate_output_path(output, allow_missing=False)
    manifest_path = output / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid distribution manifest: {manifest_path}") from exc
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version", "generator", "canonical_root", "output_root",
        "aggregate_sha256", "file_count", "files",
    }:
        raise RuntimeError("distribution manifest has unknown or missing fields")
    if (
        manifest.get("schema_version") != "loom-generated-distribution/v1"
        or manifest.get("generator") != GENERATOR
        or manifest.get("canonical_root") != "src/skills"
        or manifest.get("output_root") != "."
    ):
        raise RuntimeError("distribution manifest authority is invalid")
    actual = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path != manifest_path
    }
    rows = validated_receipt(
        manifest,
        schema="loom-generated-distribution/v1",
        expected=actual,
        envelope_keys={
            "schema_version", "generator", "canonical_root", "output_root",
            "aggregate_sha256", "file_count", "files",
        },
    )
    for row in rows:
        path = output / str(row["path"])
        if path.stat().st_size != row["size"] or sha256(path) != row["sha256"]:
            raise RuntimeError(f"distribution payload drift: {path}")
    return manifest


def canonical_python_files() -> list[Path]:
    return sorted(path.relative_to(CANONICAL_SKILLS) for path in CANONICAL_SKILLS.rglob("*.py"))


def read_receipt(root: Path, name: str) -> dict[str, object] | None:
    path = root / name
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def package_receipt_path(root: Path) -> Path:
    label = "plugin-skills" if root == ROOT / "plugins" / "loom" / "skills" else "skills"
    return ROOT / "build" / "loom-materialization-receipts" / f"{label}.json"


def validated_receipt(
    receipt: dict[str, object],
    *,
    schema: str,
    expected: set[str],
    envelope_keys: set[str] | None = None,
) -> list[dict[str, object]]:
    required_keys = envelope_keys or {"schema_version", "generator", "aggregate_sha256", "file_count", "files"}
    if set(receipt) != required_keys:
        raise RuntimeError("materialization receipt has unknown or missing fields")
    if receipt.get("schema_version") != schema or receipt.get("generator") != GENERATOR:
        raise RuntimeError("materialization receipt has an unsupported authority")
    rows = receipt.get("files")
    if not isinstance(rows, list) or receipt.get("file_count") != len(rows):
        raise RuntimeError("materialization receipt file count is invalid")
    normalized: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != ROW_KEYS:
            raise RuntimeError("materialization receipt row is invalid")
        path = row.get("path")
        digest = row.get("sha256")
        size = row.get("size")
        if (
            not isinstance(path, str)
            or not path
            or Path(path).is_absolute()
            or ".." in Path(path).parts
            or not isinstance(digest, str)
            or len(digest) != 64
            or not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
        ):
            raise RuntimeError("materialization receipt row values are invalid")
        normalized.append(row)
    declared = {str(row["path"]) for row in normalized}
    if declared != expected or len(declared) != len(normalized):
        raise RuntimeError("materialization receipt inventory drift")
    aggregate = hashlib.sha256(
        "".join(f"{row['path']}\0{row['sha256']}\n" for row in sorted(normalized, key=lambda item: str(item["path"]))).encode("utf-8")
    ).hexdigest()
    if receipt.get("aggregate_sha256") != aggregate:
        raise RuntimeError("materialization receipt aggregate drift")
    return normalized


def verify_owned_materialization(
    root: Path,
    receipt: dict[str, object],
    expected: set[str],
    *,
    schema: str,
    envelope_keys: set[str] | None = None,
) -> list[dict[str, object]]:
    rows = validated_receipt(receipt, schema=schema, expected=expected, envelope_keys=envelope_keys)
    resolved_root = root.resolve()
    for row in rows:
        path = root / str(row["path"])
        if not path.resolve().is_relative_to(resolved_root) or not path.is_file():
            raise RuntimeError(f"materialized path escapes its root: {path}")
        if path.stat().st_size != row["size"] or sha256(path) != row["sha256"]:
            raise RuntimeError(f"materialized file was modified or replaced: {path}")
    return rows


def receipt_payload(rows: list[dict[str, object]], *, schema: str) -> dict[str, object]:
    ordered = sorted(rows, key=lambda row: str(row["path"]))
    aggregate = hashlib.sha256(
        "".join(f"{row['path']}\0{row['sha256']}\n" for row in ordered).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": schema,
        "generator": GENERATOR,
        "aggregate_sha256": aggregate,
        "file_count": len(ordered),
        "files": ordered,
    }


def write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def package_materialization(output: Path, root: Path) -> list[str]:
    relatives = canonical_python_files()
    expected = {relative.as_posix() for relative in relatives}
    receipt_path = package_receipt_path(root)
    receipt = read_receipt(receipt_path.parent, receipt_path.name)
    existing = {path.relative_to(root).as_posix() for path in root.rglob("*.py")} if root.is_dir() else set()
    if receipt is not None:
        verify_owned_materialization(root, receipt, expected, schema=RECEIPT_SCHEMA)
        if existing != expected:
            raise RuntimeError(f"package materialization inventory drift at {root}")
    elif existing:
        raise RuntimeError(f"refusing to overwrite pre-existing generated Python files without receipt: {root}")
    root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    writes: list[str] = []
    for relative in relatives:
        source = output / "skills" / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.tmp-{os.getpid()}")
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
        rows.append({"path": relative.as_posix(), "sha256": sha256(target), "size": target.stat().st_size})
        writes.append(target.relative_to(ROOT).as_posix())
    write_json_atomic(receipt_path, receipt_payload(rows, schema=RECEIPT_SCHEMA))
    return writes


def runtime_materialization(output: Path, source_name: str, root: Path, manifest: dict[str, object]) -> list[str]:
    expected = set(RUNTIME_NAMES)
    receipt = read_receipt(root, RUNTIME_MANIFEST_NAME)
    existing = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()} if root.is_dir() else set()
    runtime_envelope = {
        "schema_version", "generator", "canonical_root", "output_root",
        "aggregate_sha256", "file_count", "files",
    }
    if receipt is not None:
        local_receipt = runtime_manifest(receipt, f"{source_name}/")
        verify_owned_materialization(
            root,
            local_receipt,
            expected,
            schema="loom-generated-repo-runtime/v1",
            envelope_keys=runtime_envelope,
        )
        if existing != expected | {RUNTIME_MANIFEST_NAME}:
            raise RuntimeError(f"repo runtime inventory drift at {root}")
    elif existing:
        raise RuntimeError(f"refusing to overwrite repo runtime without distribution manifest: {root}")
    root.mkdir(parents=True, exist_ok=True)
    writes: list[str] = []
    for name in RUNTIME_NAMES:
        target = root / name
        temporary = target.with_name(f".{target.name}.tmp-{os.getpid()}")
        shutil.copy2(output / source_name / name, temporary)
        os.replace(temporary, target)
        writes.append(target.relative_to(ROOT).as_posix())
    manifest_target = root / RUNTIME_MANIFEST_NAME
    write_json_atomic(manifest_target, manifest)
    writes.append(manifest_target.relative_to(ROOT).as_posix())
    return writes


def materialize(output: Path, surface: str) -> list[str]:
    manifest = validated_distribution(output)
    writes: list[str] = []
    if surface in {"package", "all"}:
        for root in (ROOT / "skills", ROOT / "plugins" / "loom" / "skills"):
            writes.extend(package_materialization(output, root))
    if surface in {"repo-fixtures", "all"}:
        for source_name, target_root in (
            ("repo-runtime", ROOT / ".loom" / "bin"),
            ("example-runtime", ROOT / "examples" / "new-project" / ".loom" / "bin"),
        ):
            writes.extend(runtime_materialization(output, source_name, target_root, manifest))
    return sorted(writes)


def clean_materialized(surface: str) -> list[str]:
    removed: list[str] = []
    if surface in {"package", "all"}:
        for root in (ROOT / "skills", ROOT / "plugins" / "loom" / "skills"):
            receipt_path = package_receipt_path(root)
            receipt = read_receipt(receipt_path.parent, receipt_path.name)
            if receipt is None:
                if root.is_dir() and any(root.rglob("*.py")):
                    raise RuntimeError(f"refusing to clean generated Python files without receipt: {root}")
                continue
            raw_rows = receipt.get("files")
            expected = {str(row.get("path")) for row in raw_rows if isinstance(row, dict)} if isinstance(raw_rows, list) else set()
            actual = {path.relative_to(root).as_posix() for path in root.rglob("*.py")}
            if actual != expected:
                raise RuntimeError(f"refusing to clean package materialization with inventory drift: {root}")
            rows = verify_owned_materialization(root, receipt, expected, schema=RECEIPT_SCHEMA)
            for row in rows:
                relative = str(row["path"])
                target = root / relative
                if target.stat().st_size != row["size"] or sha256(target) != row["sha256"]:
                    raise RuntimeError(f"refusing to delete concurrently modified materialization: {target}")
                target.unlink()
                removed.append(target.relative_to(ROOT).as_posix())
            receipt_path.unlink()
            removed.append(receipt_path.relative_to(ROOT).as_posix())
    if surface in {"repo-fixtures", "all"}:
        for root in (ROOT / ".loom" / "bin", ROOT / "examples" / "new-project" / ".loom" / "bin"):
            receipt = read_receipt(root, RUNTIME_MANIFEST_NAME)
            if receipt is None:
                if root.is_dir() and any(root.iterdir()):
                    raise RuntimeError(f"refusing to clean repo runtime without distribution manifest: {root}")
                continue
            source_name = "repo-runtime" if root == ROOT / ".loom" / "bin" else "example-runtime"
            local_receipt = runtime_manifest(receipt, f"{source_name}/")
            raw_rows = local_receipt.get("files")
            expected = {str(row.get("path")) for row in raw_rows if isinstance(row, dict)} if isinstance(raw_rows, list) else set()
            actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
            if actual != expected | {RUNTIME_MANIFEST_NAME}:
                raise RuntimeError(f"refusing to clean repo runtime with inventory drift: {root}")
            rows = verify_owned_materialization(
                root,
                local_receipt,
                expected,
                schema="loom-generated-repo-runtime/v1",
                envelope_keys={
                    "schema_version", "generator", "canonical_root", "output_root",
                    "aggregate_sha256", "file_count", "files",
                },
            )
            for row in rows:
                name = str(row["path"])
                target = root / name
                if target.stat().st_size != row["size"] or sha256(target) != row["sha256"]:
                    raise RuntimeError(f"refusing to delete concurrently modified runtime: {target}")
                target.unlink()
                removed.append(target.relative_to(ROOT).as_posix())
            manifest_path = root / RUNTIME_MANIFEST_NAME
            manifest_path.unlink()
            removed.append(manifest_path.relative_to(ROOT).as_posix())
    return sorted(removed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("generate", "clean", "pack"), nargs="?", default="generate")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--materialize", choices=("package", "repo-fixtures", "all"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.action == "pack":
        build(output)
        materialize(output, "package")
        try:
            completed = subprocess.run(
                ["npm", "pack", "--dry-run", "--json", "--ignore-scripts"],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        finally:
            clean_materialized("package")
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        return completed.returncode
    if args.action == "clean":
        removed = clean_materialized(args.materialize or "all")
        if output.exists():
            shutil.rmtree(validate_output_path(output, allow_missing=False))
        payload = {"schema_version": "loom-generated-distribution-clean/v1", "result": "pass", "removed": removed}
    else:
        manifest = build(output)
        writes = materialize(output, args.materialize) if args.materialize else []
        payload = {"schema_version": "loom-generated-distribution-build/v1", "result": "pass", "manifest": manifest, "materialized": writes}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"distribution {args.action}: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
