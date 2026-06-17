#!/usr/bin/env python3
"""Generate and verify the checked-in Loom skills install surface."""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "src" / "skills"
TARGET_ROOT = REPO_ROOT / "skills"
PLUGIN_MANIFEST = REPO_ROOT / "plugins" / "loom" / ".codex-plugin" / "plugin.json"
REPO_VERSION_FILE = REPO_ROOT / "VERSION"
PRIVATE_RUNTIME_DIR = ".loom-runtime"
SKILL_PACKAGE_VERSION = "1.0.0"
RUNTIME_CORE_VERSION = "1.0.0"
HOST_ADAPTER_VERSION = "1.0.0"
SOURCE_REVISION = "repository-working-tree"
IGNORED_NAMES = {"__pycache__", ".DS_Store"}
TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}
DOC_REFERENCE_SYNC = {
    "docs/methodology/templates/spec-suite.md": "shared/references/templates/spec-suite.md",
    "docs/methodology/templates/execution-breakdown.md": "shared/references/templates/execution-breakdown.md",
    "docs/methodology/harness/task-carrier-contract.md": "shared/references/harness/task-carrier-contract.md",
    "docs/methodology/templates/evidence-map.md": "shared/references/templates/evidence-map.md",
    "docs/methodology/templates/consistency-analysis.md": "shared/references/templates/consistency-analysis.md",
    "docs/methodology/templates/scaffold/full-suite-index.md": "shared/references/templates/scaffold/full-suite-index.md",
    "docs/methodology/templates/scaffold/spec.md": "shared/references/templates/scaffold/spec.md",
    "docs/methodology/templates/scaffold/plan.md": "shared/references/templates/scaffold/plan.md",
    "docs/methodology/templates/scaffold/research.md": "shared/references/templates/scaffold/research.md",
    "docs/methodology/templates/scaffold/contracts.md": "shared/references/templates/scaffold/contracts.md",
    "docs/methodology/templates/scaffold/readiness-checklist.md": "shared/references/templates/scaffold/readiness-checklist.md",
}

DOC_REFERENCE_SYNC_SURFACE = "docs-reference-sync"
GENERATED_TREE_DRIFT_SURFACE = "generated-tree-drift"
PACKAGE_METADATA_SURFACE = "package-metadata"
CACHE_ARTIFACTS_SURFACE = "cache-artifacts"
LAUNCHER_SMOKE_SURFACE = "launcher-smoke"
REFERENCE_INTEGRITY_SURFACE = "reference-integrity"
RUNTIME_COPY_PARITY_FILES = (
    "registry.json",
    "install-layout.json",
    "upgrade-contract.json",
    "route-matrix.md",
    "distribution-and-adapter-contract.md",
)


@dataclass(frozen=True)
class SurfaceDefinition:
    label: str
    failure_name: str
    evidence_locator: str
    run: Callable[[tuple[str, ...] | None], None]


class SurfaceFailure(RuntimeError):
    def __init__(
        self,
        *,
        surface_label: str,
        failure_name: str,
        evidence_locator: str,
        details: list[str],
    ) -> None:
        self.surface_label = surface_label
        self.failure_name = failure_name
        self.evidence_locator = evidence_locator
        self.details = details
        super().__init__(
            "\n".join(
                [
                    f"surface_label={surface_label}",
                    f"failure_name={failure_name}",
                    f"evidence_locator={evidence_locator}",
                    "details:",
                    *[f"- {detail}" for detail in details[:80]],
                ]
            )
        )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def should_ignore(path: Path) -> bool:
    return path.name in IGNORED_NAMES or path.name.endswith(".pyc") or path.name == PRIVATE_RUNTIME_DIR


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if should_ignore(Path(name))}

    shutil.copytree(source, target, ignore=ignore)


def repo_version() -> str:
    return REPO_VERSION_FILE.read_text(encoding="utf-8").strip()


def source_repository() -> str:
    return "https://github.com/MC-and-his-Agents/Loom"


def public_skill_entries(source_root: Path) -> list[dict[str, Any]]:
    registry = read_json(source_root / "registry.json")
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("src/skills/registry.json must declare public entries")
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise RuntimeError("src/skills/registry.json contains an invalid entry")
    return entries


def runtime_script(skill_id: str) -> str:
    return "loom_init.py" if skill_id in {"loom-init", "loom-adopt"} else "loom_flow.py"


def skill_launcher(contract: dict[str, Any]) -> str:
    entrypoint = contract.get("entrypoint")
    if not isinstance(entrypoint, dict):
        raise RuntimeError(f"{contract.get('id', '<unknown>')} contract is missing entrypoint")
    for key in ("script", "bootstrap_cli", "orchestration_cli", "route_cli"):
        value = entrypoint.get(key)
        if isinstance(value, str) and value:
            return value
    raise RuntimeError(f"{contract.get('id', '<unknown>')} contract does not declare a launcher")


def write_wrapper(skill_id: str, target: Path) -> None:
    script = runtime_script(skill_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "",
                "import os",
                "import runpy",
                "import sys",
                "from pathlib import Path",
                "",
                'os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")',
                "sys.dont_write_bytecode = True",
                "SCRIPT_PATH = Path(__file__).resolve()",
                "PACKAGE_ROOT = SCRIPT_PATH.parents[1]",
                f'RUNTIME_ROOT = PACKAGE_ROOT / "{PRIVATE_RUNTIME_DIR}"',
                "",
                'os.environ.setdefault("LOOM_INSTALLED_SKILLS_ROOT", str(RUNTIME_ROOT))',
                f'os.environ.setdefault("LOOM_PACKAGE_SKILL_ID", "{skill_id}")',
                'sys.path.insert(0, str(RUNTIME_ROOT / "shared/scripts"))',
                f'runpy.run_path(RUNTIME_ROOT / "shared/scripts/{script}", run_name="__main__")',
                "",
            ]
        ),
        encoding="utf-8",
    )
    target.chmod(0o755)


def relative_posix(from_dir: Path, target: Path) -> str:
    return os.path.relpath(target, from_dir).replace(os.sep, "/")


def _inside(path: Path, root: Path) -> tuple[bool, str | None]:
    try:
        return True, str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return False, None


def _reference_target_base(path: Path, package_root: Path, runtime_root: Path) -> tuple[str, str]:
    for label, root in (
        ("runtime", runtime_root),
        ("install", package_root),
    ):
        is_inside, relative = _inside(path, root)
        if is_inside and relative is not None:
            return label, relative
    return "outside", path.as_posix()


def is_markdown_file_reference(target: str) -> bool:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
        return False
    return bool(target.strip())


def is_json_file_reference(value: str) -> bool:
    file_reference_prefixes = (
        "../",
        "./",
        ".loom-runtime/",
        "references/",
        "scripts/",
        "assets/",
        "agents/",
    )
    return value.startswith(file_reference_prefixes)


def validate_local_reference(path: Path, target: str, package_root: Path, runtime_root: Path, *, source: str) -> list[str]:
    errors: list[str] = []
    clean_target = target.split("#", 1)[0]
    if not clean_target:
        return errors
    resolved = (path.parent / clean_target).resolve()
    base, base_relative = _reference_target_base(resolved, package_root, runtime_root)
    if base == "outside":
        errors.append(
            f"{path.relative_to(package_root)} {source} outside install/runtime (base={base}); "
            f"target={target}"
        )
    elif not resolved.exists():
        errors.append(
            f"{path.relative_to(package_root)} {source} missing {base}:{base_relative}; "
            f"target={target}"
        )
    return errors


MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)#][^) ]*)([^)]*\))")


def rewrite_markdown_links(text: str, source_file: Path, source_skill_root: Path, package_file: Path, package_root: Path) -> str:
    source_parent = source_file.parent
    package_parent = package_file.parent

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            return match.group(0)
        if not target.startswith("../"):
            return match.group(0)
        fragment = ""
        clean_target = target
        if "#" in target:
            clean_target, fragment = target.split("#", 1)
            fragment = "#" + fragment
        resolved = (source_parent / clean_target).resolve()
        try:
            resolved.relative_to(source_skill_root.resolve())
            return match.group(0)
        except ValueError:
            pass
        try:
            runtime_relative = resolved.relative_to(SOURCE_ROOT.resolve())
        except ValueError:
            return match.group(0)
        rewritten = relative_posix(package_parent, package_root / PRIVATE_RUNTIME_DIR / runtime_relative)
        return f"{prefix}{rewritten}{fragment}{suffix}"

    return MARKDOWN_LINK_RE.sub(replace, text)


def rewrite_skill_text_files(source_skill_root: Path, package_root: Path) -> None:
    for package_file in package_root.rglob("*"):
        if not package_file.is_file() or PRIVATE_RUNTIME_DIR in package_file.parts or package_file.suffix not in {".md", ".yaml", ".yml"}:
            continue
        source_file = source_skill_root / package_file.relative_to(package_root)
        if not source_file.exists():
            continue
        original = package_file.read_text(encoding="utf-8")
        rewritten = rewrite_markdown_links(original, source_file, source_skill_root, package_file, package_root)
        if rewritten != original:
            package_file.write_text(rewritten, encoding="utf-8")


def map_contract_value(value: Any, source_base: Path, source_skill_root: Path, package_base: Path, package_root: Path) -> Any:
    if isinstance(value, dict):
        return {
            key: map_contract_value(child, source_base, source_skill_root, package_base, package_root)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [map_contract_value(child, source_base, source_skill_root, package_base, package_root) for child in value]
    if not isinstance(value, str) or not value.startswith("../"):
        return value

    resolved = (source_base / value).resolve()
    try:
        resolved.relative_to(source_skill_root.resolve())
        return value
    except ValueError:
        pass
    try:
        runtime_relative = resolved.relative_to(SOURCE_ROOT.resolve())
    except ValueError:
        return value
    return relative_posix(package_base, package_root / PRIVATE_RUNTIME_DIR / runtime_relative)


def rewrite_contract(source_contract: Path, package_contract: Path, source_skill_root: Path, package_root: Path) -> dict[str, Any]:
    contract = read_json(source_contract)
    rewritten = map_contract_value(contract, source_contract.parent, source_skill_root, package_contract.parent, package_root)
    write_json(package_contract, rewritten)
    return rewritten


def write_package_metadata(
    package_root: Path,
    contract: dict[str, Any],
    registry: dict[str, Any],
    plugin_manifest: dict[str, Any],
) -> None:
    skill_id = contract["id"]
    launcher = skill_launcher(contract)
    write_json(
        package_root / "loom-package.json",
        {
            "schema_version": "loom-skill-package/v1",
            "package_type": "single-skill",
            "package_id": skill_id,
            "display_name": contract.get("display_name", skill_id),
            "repo_version": repo_version(),
            "source_repository": source_repository(),
            "source_revision": SOURCE_REVISION,
            "skill_package_version": SKILL_PACKAGE_VERSION,
            "skill_contract_version": contract.get("contract_version"),
            "registry_version": registry.get("registry_version"),
            "runtime_core_version": RUNTIME_CORE_VERSION,
            "runtime_root": PRIVATE_RUNTIME_DIR,
            "launcher": launcher,
            "root_entry": bool(contract.get("root_entry")),
            "plugin_surface_version": plugin_manifest.get("version"),
            "host_adapter_version": plugin_manifest.get("x-loom", {}).get("host_adapter_version", HOST_ADAPTER_VERSION),
            "full_repo_install_surface": False,
            "fail_closed_on": [
                "missing SKILL.md",
                "missing contract.json",
                "missing launcher",
                "missing package metadata",
                "missing package-internal runtime",
                "package-external runtime reference",
                "runtime registry or install-layout drift",
            ],
        },
    )


def generate_surface(source_root: Path = SOURCE_ROOT, target_root: Path = TARGET_ROOT) -> None:
    if not source_root.exists():
        raise RuntimeError(f"missing source skills root: {source_root}")
    registry = read_json(source_root / "registry.json")
    plugin_manifest = read_json(PLUGIN_MANIFEST)

    staging = Path(tempfile.mkdtemp(prefix="loom-skills-surface-"))
    try:
        generated = staging / "skills"
        copy_tree(source_root, generated)
        for entry in public_skill_entries(source_root):
            skill_id = entry["id"]
            source_skill_root = source_root / skill_id
            package_root = generated / skill_id
            if not source_skill_root.exists():
                raise RuntimeError(f"missing public skill source: {source_skill_root}")

            runtime_root = package_root / PRIVATE_RUNTIME_DIR
            copy_tree(source_root, runtime_root)

            scripts_dir = package_root / "scripts"
            if scripts_dir.exists():
                shutil.rmtree(scripts_dir)
            source_contract = source_skill_root / "contract.json"
            package_contract = package_root / "contract.json"
            rewritten_contract = rewrite_contract(source_contract, package_contract, source_skill_root, package_root)
            write_wrapper(skill_id, package_root / skill_launcher(rewritten_contract))
            rewrite_skill_text_files(source_skill_root, package_root)
            write_package_metadata(package_root, rewritten_contract, registry, plugin_manifest)

        if target_root.exists():
            shutil.rmtree(target_root)
        shutil.move(str(generated), str(target_root))
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def comparable_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if should_ignore(path):
            continue
        if path.is_file():
            files.append(path.relative_to(root))
    return sorted(files)


def compare_trees(expected: Path, actual: Path) -> list[str]:
    errors: list[str] = []
    expected_files = comparable_files(expected)
    actual_files = comparable_files(actual)
    if expected_files != actual_files:
        missing = sorted(set(expected_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(expected_files))
        if missing:
            errors.append("missing generated files: " + ", ".join(str(path) for path in missing[:20]))
        if extra:
            errors.append("unexpected generated files: " + ", ".join(str(path) for path in extra[:20]))
        return errors
    for relative in expected_files:
        expected_path = expected / relative
        actual_path = actual / relative
        if not filecmp.cmp(expected_path, actual_path, shallow=False):
            errors.append(f"generated file drift: {relative}")
        expected_exec = bool(expected_path.stat().st_mode & 0o111)
        actual_exec = bool(actual_path.stat().st_mode & 0o111)
        if expected_exec != actual_exec:
            errors.append(f"generated executable bit drift: {relative}")
    return errors


def compare_doc_reference_sync() -> list[str]:
    errors: list[str] = []
    for doc_relative, source_relative in DOC_REFERENCE_SYNC.items():
        doc_path = REPO_ROOT / doc_relative
        source_path = SOURCE_ROOT / source_relative
        if not doc_path.is_file():
            errors.append(f"missing source doc reference: {doc_relative}")
            continue
        if not source_path.is_file():
            errors.append(f"missing source skills reference copy: {source_relative}")
            continue
        if not filecmp.cmp(doc_path, source_path, shallow=False):
            errors.append(f"source skills reference drift: {source_relative} from {doc_relative}")
    return errors


def check_doc_reference_sync_surface() -> None:
    reference_drift = compare_doc_reference_sync()
    if reference_drift:
        raise SurfaceFailure(
            surface_label=DOC_REFERENCE_SYNC_SURFACE,
            failure_name="skills_docs_reference_sync_drift",
            evidence_locator="tools/skills_surface.py:DOC_REFERENCE_SYNC",
            details=reference_drift,
        )


def python_cache_artifacts(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo", ".pyd"}
    )


def check_cache_artifacts_surface() -> None:
    cache_artifacts = python_cache_artifacts(TARGET_ROOT)
    if cache_artifacts:
        raise SurfaceFailure(
            surface_label=CACHE_ARTIFACTS_SURFACE,
            failure_name="skills_cache_artifacts_present",
            evidence_locator="skills/**/__pycache__; skills/**/*.py[cod]",
            details=cache_artifacts,
        )


def compare_source_install_runtime_parity(source_root: Path, package_root: Path) -> list[str]:
    errors: list[str] = []
    for required in RUNTIME_COPY_PARITY_FILES:
        source_path = source_root / required
        install_path = package_root / required
        if not source_path.is_file():
            errors.append(f"missing source parity asset: {required}")
            continue
        if not install_path.is_file():
            errors.append(f"missing install parity asset: {required}")
            continue
        if not filecmp.cmp(source_path, install_path, shallow=False):
            errors.append(f"install parity drift: {required} differs from source/skills")
    return errors


def validate_reference_copy_parity(source_root: Path, package_root: Path, runtime_root: Path) -> list[str]:
    errors: list[str] = []
    for required in RUNTIME_COPY_PARITY_FILES:
        source_path = source_root / required
        runtime_path = runtime_root / required
        if not source_path.is_file():
            errors.append(f"missing source parity asset: {required}")
            continue
        if not runtime_path.is_file():
            errors.append(f"{package_root.name}: runtime parity missing {required}")
            continue
        if not filecmp.cmp(source_path, runtime_path, shallow=False):
            errors.append(f"{package_root.name}: runtime parity drift for {required}")
    return errors


def validate_reference_target_base(
    package_root: Path,
    metadata: dict[str, Any],
) -> list[str]:
    runtime_root = package_root / str(metadata.get("runtime_root", PRIVATE_RUNTIME_DIR))
    if not runtime_root.is_dir():
        return []
    return assert_no_package_external_links(package_root, runtime_root)


def check_reference_integrity_surface() -> None:
    errors: list[str] = []
    errors.extend(compare_source_install_runtime_parity(SOURCE_ROOT, TARGET_ROOT))
    for entry in public_skill_entries(TARGET_ROOT):
        package_root = TARGET_ROOT / entry["id"]
        if not package_root.is_dir():
            errors.append(f"missing generated package directory: {entry['id']}")
            continue
        metadata_path = package_root / "loom-package.json"
        if not metadata_path.is_file():
            errors.append(f"{entry['id']}: missing loom-package.json")
            continue
        metadata = read_json(metadata_path)
        runtime_root = package_root / str(metadata.get("runtime_root", PRIVATE_RUNTIME_DIR))
        errors.extend(validate_reference_copy_parity(SOURCE_ROOT, package_root, runtime_root))
        errors.extend(validate_reference_target_base(package_root, metadata))

    if errors:
        raise SurfaceFailure(
            surface_label=REFERENCE_INTEGRITY_SURFACE,
            failure_name="skills_reference_integrity_invalid",
            evidence_locator="src/skills; skills; skills/*/.loom-runtime",
            details=errors,
        )


def iter_text_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and path.suffix in TEXT_SUFFIXES]


def assert_no_package_external_links(package_root: Path, runtime_root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_text_files(package_root):
        if PRIVATE_RUNTIME_DIR in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = match.group(2)
            if not is_markdown_file_reference(target):
                continue
            errors.extend(validate_local_reference(path, target, package_root, runtime_root, source="links"))
        if path.suffix == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.relative_to(package_root)} invalid JSON for reference scan: {exc.msg}")
                continue
            errors.extend(
                assert_json_paths_inside_package(
                    payload,
                    path,
                    package_root=package_root,
                    runtime_root=runtime_root,
                )
            )
    return errors


def assert_json_paths_inside_package(
    payload: Any,
    path: Path,
    *,
    package_root: Path,
    runtime_root: Path,
) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for value in payload.values():
            errors.extend(
                assert_json_paths_inside_package(
                    value,
                    path,
                    package_root=package_root,
                    runtime_root=runtime_root,
                )
            )
    elif isinstance(payload, list):
        for value in payload:
            errors.extend(
                assert_json_paths_inside_package(
                    value,
                    path,
                    package_root=package_root,
                    runtime_root=runtime_root,
                )
            )
    elif isinstance(payload, str) and is_json_file_reference(payload):
        errors.extend(validate_local_reference(path, payload, package_root, runtime_root, source="JSON reference"))
    return errors


def validate_skill_package(package_root: Path, skill_id: str) -> list[str]:
    errors: list[str] = []
    metadata_path = package_root / "loom-package.json"
    contract_path = package_root / "contract.json"
    if not (package_root / "SKILL.md").is_file():
        errors.append(f"{skill_id}: missing SKILL.md")
    if not contract_path.is_file():
        errors.append(f"{skill_id}: missing contract.json")
        return errors
    if not metadata_path.is_file():
        errors.append(f"{skill_id}: missing loom-package.json")
        return errors
    contract = read_json(contract_path)
    metadata = read_json(metadata_path)
    launcher = metadata.get("launcher")
    runtime_root = metadata.get("runtime_root")
    if metadata.get("schema_version") != "loom-skill-package/v1":
        errors.append(f"{skill_id}: unsupported loom-package schema")
    if metadata.get("package_id") != skill_id:
        errors.append(f"{skill_id}: package_id mismatch")
    if metadata.get("skill_contract_version") != contract.get("contract_version"):
        errors.append(f"{skill_id}: contract version metadata mismatch")
    if not isinstance(launcher, str) or not (package_root / launcher).is_file():
        errors.append(f"{skill_id}: launcher is missing: {launcher}")
    if not isinstance(runtime_root, str) or not (package_root / runtime_root / "shared" / "scripts").is_dir():
        errors.append(f"{skill_id}: runtime root is missing shared scripts")
    for required in ("registry.json", "install-layout.json", "upgrade-contract.json", "route-matrix.md"):
        if not (package_root / str(runtime_root) / required).exists():
            errors.append(f"{skill_id}: runtime missing {required}")
    runtime_path = package_root / str(runtime_root) if isinstance(runtime_root, str) else package_root / PRIVATE_RUNTIME_DIR
    errors.extend(f"{skill_id}: {error}" for error in assert_no_package_external_links(package_root, runtime_path))
    return errors


def run_launcher_smoke(package_root: Path, skill_id: str) -> list[str]:
    metadata = read_json(package_root / "loom-package.json")
    package_id = metadata.get("package_id", skill_id)
    launcher_value = metadata.get("launcher")
    launcher = package_root / str(launcher_value)
    evidence_locator = f"{package_root.relative_to(REPO_ROOT).as_posix()}/loom-package.json"
    if isinstance(launcher_value, str) and launcher_value:
        evidence_locator += f"; {(package_root / launcher_value).relative_to(REPO_ROOT).as_posix()}"
    detail_prefix = f"skill={skill_id} package={package_id} evidence_locator={evidence_locator}"
    args = [sys.executable, str(launcher), "runtime-state", "--target", str(REPO_ROOT)]
    if skill_id not in {"loom-init", "loom-adopt"}:
        args.extend(["--item", "INIT-0001"])
    env = os.environ.copy()
    for key in (
        "LOOM_INSTALLED_SKILLS_ROOT",
        "LOOM_PACKAGE_SKILL_ID",
        "LOOM_RUNTIME_SCENE",
        "LOOM_SOURCE_REPO_ROOT",
    ):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=REPO_ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return [
            f"{detail_prefix} command={' '.join(args)} failure=runtime-state-failed "
            f"output={(result.stderr or result.stdout).strip()}"
        ]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [f"{detail_prefix} command={' '.join(args)} failure=invalid-json output={exc.msg}"]
    runtime_state = payload.get("runtime_state")
    if not isinstance(runtime_state, dict) or runtime_state.get("scene") != "installed-runtime":
        return [f"{detail_prefix} command={' '.join(args)} failure=unexpected-runtime-scene"]
    return []


def verify_surface(root: Path = TARGET_ROOT, *, run_launchers: bool = True) -> list[str]:
    errors: list[str] = []
    registry = read_json(root / "registry.json")
    for entry in registry.get("entries", []):
        skill_id = entry["id"]
        package_root = root / skill_id
        errors.extend(validate_skill_package(package_root, skill_id))
        if run_launchers and not errors:
            errors.extend(run_launcher_smoke(package_root, skill_id))
    return errors


def check_package_metadata_surface() -> None:
    try:
        errors = verify_surface(TARGET_ROOT, run_launchers=False)
    except Exception as exc:
        errors = [str(exc)]
    if errors:
        raise SurfaceFailure(
            surface_label=PACKAGE_METADATA_SURFACE,
            failure_name="skills_package_metadata_invalid",
            evidence_locator="skills/*/loom-package.json; skills/*/contract.json; skills/*/.loom-runtime",
            details=errors,
        )


def selected_skill_ids(root: Path, requested_skill_ids: tuple[str, ...] | None) -> list[str]:
    registry = read_json(root / "registry.json")
    skill_ids = [
        entry["id"]
        for entry in registry.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    ]
    if not requested_skill_ids:
        return skill_ids
    missing = sorted(set(requested_skill_ids) - set(skill_ids))
    if missing:
        raise SurfaceFailure(
            surface_label=LAUNCHER_SMOKE_SURFACE,
            failure_name="skills_launcher_smoke_unknown_skill",
            evidence_locator="skills/registry.json",
            details=[f"unknown launcher smoke skill target: {skill_id}" for skill_id in missing],
        )
    requested = set(requested_skill_ids)
    return [skill_id for skill_id in skill_ids if skill_id in requested]


def check_launcher_smoke_surface(requested_skill_ids: tuple[str, ...] | None = None) -> None:
    errors: list[str] = []
    try:
        skill_ids = selected_skill_ids(TARGET_ROOT, requested_skill_ids)
    except SurfaceFailure:
        raise
    except Exception as exc:
        errors = [str(exc)]
        skill_ids = []
    for skill_id in skill_ids:
        package_root = TARGET_ROOT / skill_id
        try:
            errors.extend(run_launcher_smoke(package_root, skill_id))
        except Exception as exc:
            errors.append(
                f"skill={skill_id} package={skill_id} "
                f"evidence_locator={package_root.relative_to(REPO_ROOT).as_posix()}/loom-package.json "
                f"failure=launcher-smoke-exception output={exc}"
            )
    if errors:
        raise SurfaceFailure(
            surface_label=LAUNCHER_SMOKE_SURFACE,
            failure_name="skills_launcher_smoke_failed",
            evidence_locator="skills/<skill-id>/loom-package.json; skills/<skill-id>/<launcher>",
            details=errors,
        )


def check_generated_tree_drift_surface() -> None:
    with tempfile.TemporaryDirectory(prefix="loom-skills-check-") as tmp:
        expected = Path(tmp) / "skills"
        generate_surface(SOURCE_ROOT, expected)
        drift = compare_trees(expected, TARGET_ROOT)
        if drift:
            raise SurfaceFailure(
                surface_label=GENERATED_TREE_DRIFT_SURFACE,
                failure_name="skills_generated_tree_drift",
                evidence_locator="src/skills -> skills",
                details=drift,
            )


def available_surface_definitions() -> tuple[SurfaceDefinition, ...]:
    return (
        SurfaceDefinition(
            label=DOC_REFERENCE_SYNC_SURFACE,
            failure_name="skills_docs_reference_sync_drift",
            evidence_locator="tools/skills_surface.py:DOC_REFERENCE_SYNC",
            run=lambda _skill_ids: check_doc_reference_sync_surface(),
        ),
        SurfaceDefinition(
            label=GENERATED_TREE_DRIFT_SURFACE,
            failure_name="skills_generated_tree_drift",
            evidence_locator="src/skills -> skills",
            run=lambda _skill_ids: check_generated_tree_drift_surface(),
        ),
        SurfaceDefinition(
            label=PACKAGE_METADATA_SURFACE,
            failure_name="skills_package_metadata_invalid",
            evidence_locator="skills/*/loom-package.json; skills/*/contract.json; skills/*/.loom-runtime",
            run=lambda _skill_ids: check_package_metadata_surface(),
        ),
        SurfaceDefinition(
            label=CACHE_ARTIFACTS_SURFACE,
            failure_name="skills_cache_artifacts_present",
            evidence_locator="skills/**/__pycache__; skills/**/*.py[cod]",
            run=lambda _skill_ids: check_cache_artifacts_surface(),
        ),
        SurfaceDefinition(
            label=LAUNCHER_SMOKE_SURFACE,
            failure_name="skills_launcher_smoke_failed",
            evidence_locator="skills/<skill-id>/loom-package.json; skills/<skill-id>/<launcher>",
            run=check_launcher_smoke_surface,
        ),
        SurfaceDefinition(
            label=REFERENCE_INTEGRITY_SURFACE,
            failure_name="skills_reference_integrity_invalid",
            evidence_locator="src/skills; skills; skills/*/.loom-runtime",
            run=lambda _skill_ids: check_reference_integrity_surface(),
        ),
    )


def selected_surface_definitions(surface_labels: list[str]) -> tuple[SurfaceDefinition, ...]:
    surfaces = {surface.label: surface for surface in available_surface_definitions()}
    missing = sorted(set(surface_labels) - set(surfaces))
    if missing:
        raise RuntimeError("unknown skills surface(s): " + ", ".join(missing))
    return tuple(surfaces[label] for label in surface_labels)


def run_surface_definition(surface: SurfaceDefinition, *, emit_success: bool, skill_ids: tuple[str, ...] | None) -> None:
    start = time.perf_counter()
    try:
        surface.run(skill_ids)
    except SurfaceFailure as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        print(
            f"skills surface {surface.label}: BLOCK "
            f"failure_name={exc.failure_name} "
            f"evidence_locator={exc.evidence_locator} "
            f"elapsed_ms={elapsed_ms}",
            file=sys.stderr,
        )
        raise
    if emit_success:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        print(
            f"skills surface {surface.label}: OK "
            f"evidence_locator={surface.evidence_locator} "
            f"elapsed_ms={elapsed_ms}"
        )


def check_selected_surfaces(surface_labels: list[str], *, emit_success: bool, skill_ids: tuple[str, ...] | None = None) -> None:
    for surface in selected_surface_definitions(surface_labels):
        run_surface_definition(surface, emit_success=emit_success, skill_ids=skill_ids)


def check_surface(selected_surfaces: list[str] | None = None, *, skill_ids: tuple[str, ...] | None = None) -> None:
    if skill_ids and selected_surfaces != [LAUNCHER_SMOKE_SURFACE]:
        raise RuntimeError("--skill may only be used with --surface launcher-smoke")
    if selected_surfaces:
        check_selected_surfaces(selected_surfaces, emit_success=True, skill_ids=skill_ids)
        return
    check_selected_surfaces([DOC_REFERENCE_SYNC_SURFACE], emit_success=False)
    check_selected_surfaces([CACHE_ARTIFACTS_SURFACE], emit_success=False)
    check_selected_surfaces([GENERATED_TREE_DRIFT_SURFACE], emit_success=False)
    check_selected_surfaces([PACKAGE_METADATA_SURFACE], emit_success=False)
    check_selected_surfaces([REFERENCE_INTEGRITY_SURFACE], emit_success=False)
    check_selected_surfaces([LAUNCHER_SMOKE_SURFACE], emit_success=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate", help="rebuild root skills/ from src/skills/")
    check_parser = subparsers.add_parser("check", help="verify generated skills/ has no drift and is self-contained")
    check_parser.add_argument(
        "--surface",
        action="append",
        choices=tuple(surface.label for surface in available_surface_definitions()),
        help="Run only the named read-only skills validation surface. May be passed more than once.",
    )
    check_parser.add_argument(
        "--skill",
        action="append",
        help="Run launcher-smoke only for the named generated skill package. May be passed more than once.",
    )
    check_parser.add_argument(
        "--list-surfaces",
        action="store_true",
        help="List targetable skills validation surfaces without running checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "generate":
            generate_surface()
            print("skills surface generated from src/skills")
        elif args.command == "check":
            if args.list_surfaces:
                for surface in available_surface_definitions():
                    print(
                        f"{surface.label}\t"
                        f"failure_name={surface.failure_name}\t"
                        f"evidence_locator={surface.evidence_locator}"
                    )
            else:
                check_surface(args.surface, skill_ids=tuple(args.skill) if args.skill else None)
                if args.surface:
                    print("skills surface targeted check: OK")
                else:
                    print("skills surface check: OK")
    except Exception as exc:
        print(f"skills surface {args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
