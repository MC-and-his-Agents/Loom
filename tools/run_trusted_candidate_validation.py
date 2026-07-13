#!/usr/bin/env python3
"""Run candidate code through a base-owned validation boundary."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


TARGET_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
BASE_OWNED_VALIDATION_PATHS = (
    "Makefile",
    "tools/fixtures",
    "test/__init__.py",
    "test/npm-package-smoke.test.mjs",
    "test/loom_flow_module_split_test.py",
    "test/trusted_candidate_validation_test.py",
    "tools/host_adapter_check.py",
    "tools/py_compile_clean.py",
    "tools/read_delivery_gate_required_identity.py",
    "tools/run_trusted_candidate_validation.py",
    "tools/skills_surface.py",
    "tools/version_surface_check.py",
)
BASE_OWNED_VALIDATION_GLOBS = ("tools/check_*.py",)
LOOM_FLOW_PATH = "src/skills/shared/scripts/loom_flow.py"
PYTHON_IMPORT_ROOTS = ("tools", "src/skills/shared/scripts")
PYTHON_STARTUP_MODULES = {"sitecustomize", "usercustomize"}


def base_owned_validation_paths(trusted_root: Path) -> list[str]:
    paths = set(BASE_OWNED_VALIDATION_PATHS)
    for pattern in BASE_OWNED_VALIDATION_GLOBS:
        paths.update(str(path.relative_to(trusted_root)) for path in trusted_root.glob(pattern))
    return sorted(paths)


def _path_snapshot(path: Path) -> object:
    if path.is_file():
        return ("file", stat.S_IMODE(path.stat().st_mode), path.read_bytes())
    if path.is_dir():
        return (
            "directory",
            stat.S_IMODE(path.stat().st_mode),
            tuple(
                (str(item.relative_to(path)), stat.S_IMODE(item.stat().st_mode), item.read_bytes())
                for item in sorted(path.rglob("*"))
                if item.is_file()
            ),
        )
    return None


def candidate_import_shadows(trusted_root: Path, candidate_root: Path) -> list[str]:
    blocked_names = set(sys.stdlib_module_names) | PYTHON_STARTUP_MODULES
    shadows: list[str] = []
    for relative_root in PYTHON_IMPORT_ROOTS:
        candidate_dir = candidate_root / relative_root
        trusted_dir = trusted_root / relative_root
        if not candidate_dir.is_dir():
            continue
        for path in candidate_dir.iterdir():
            if path.name.split(".", 1)[0] not in blocked_names:
                continue
            relative = str(path.relative_to(candidate_root))
            if _path_snapshot(path) != _path_snapshot(trusted_dir / path.name):
                shadows.append(relative)
    return sorted(shadows)


def ensure_contained_path(root: Path, destination: Path) -> None:
    lexical_root = root.absolute()
    try:
        relative = destination.absolute().relative_to(lexical_root)
    except ValueError as error:
        raise ValueError(f"overlay destination escapes validation root: {destination}") from error
    current = lexical_root
    for part in relative.parts[:-1]:
        current /= part
        if current.exists() and stat.S_ISLNK(os.lstat(current).st_mode):
            raise ValueError(f"overlay ancestor is a symlink: {current}")
    if destination.is_symlink():
        raise ValueError(f"overlay destination is a symlink: {destination}")
    if destination.parent.resolve().is_relative_to(root.resolve()) is False:
        raise ValueError(f"resolved overlay parent escapes validation root: {destination.parent}")


def replace_path(source: Path, destination: Path, output_root: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"trusted overlay source is a symlink: {source}")
    ensure_contained_path(output_root, destination)
    if destination.is_dir() and not destination.is_symlink():
        shutil.rmtree(destination)
    elif destination.exists() or destination.is_symlink():
        destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def materialize_snapshot(snapshot: object, destination: Path, output_root: Path) -> None:
    ensure_contained_path(output_root, destination)
    if destination.is_dir() and not destination.is_symlink():
        shutil.rmtree(destination)
    elif destination.exists() or destination.is_symlink():
        destination.unlink()
    if snapshot is None:
        return
    kind, mode, content = snapshot
    if kind == "file":
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        destination.chmod(mode)
        return
    destination.mkdir(parents=True, exist_ok=True)
    destination.chmod(mode)
    for relative, file_mode, data in content:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(file_mode)


def freeze_base_owned_files(trusted_root: Path) -> dict[str, object]:
    return {relative: _path_snapshot(trusted_root / relative) for relative in base_owned_validation_paths(trusted_root)}


def verify_base_owned_files(frozen: dict[str, object], validation_root: Path) -> None:
    drift = [
        relative
        for relative, snapshot in frozen.items()
        if snapshot != _path_snapshot(validation_root / relative)
    ]
    if drift:
        raise ValueError("candidate execution modified base-owned validation files: " + ", ".join(drift))


def candidate_environment(validation_root: Path) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key in {"HOME", "LANG", "LC_ALL", "PATH", "SHELL", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR"}
    }
    environment.update(
        {
            "LOOM_CANDIDATE_VALIDATION": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONSAFEPATH": "1",
            "PYTHONPATH": os.pathsep.join(
                (
                    str(validation_root / "src" / "skills" / "shared" / "scripts"),
                    str(validation_root / "tools"),
                )
            ),
        }
    )
    return environment


def candidate_symlinks(candidate_root: Path, policy: str) -> list[Path]:
    symlinks: set[Path] = set()
    indexed = subprocess.run(
        ["git", "-C", str(candidate_root), "ls-files", "-s", "-z"],
        check=False,
        capture_output=True,
    )
    if indexed.returncode == 0:
        for entry in indexed.stdout.split(b"\0"):
            if not entry:
                continue
            metadata, raw_path = entry.split(b"\t", 1)
            if metadata.split(b" ", 1)[0] == b"120000":
                symlinks.add(candidate_root / os.fsdecode(raw_path))
    for directory, names, files in os.walk(candidate_root, followlinks=False):
        base = Path(directory)
        for name in [*names, *files]:
            path = base / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                symlinks.add(path)
    if policy == "reject":
        return sorted(symlinks)
    protected = ("Makefile", "tools", ".github/actions")
    candidate_resolved = candidate_root.resolve()
    unsafe: list[Path] = []
    for path in symlinks:
        relative = path.relative_to(candidate_root).as_posix()
        if any(relative == prefix or relative.startswith(prefix + "/") for prefix in protected):
            unsafe.append(path)
            continue
        if not path.is_symlink():
            unsafe.append(path)
            continue
        raw_target = os.readlink(path)
        if os.path.isabs(raw_target):
            unsafe.append(path)
            continue
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(candidate_resolved)
        except (FileNotFoundError, RuntimeError, ValueError):
            unsafe.append(path)
    return sorted(unsafe)


def trusted_overlay(
    candidate_root: Path,
    output_root: Path,
    symlink_policy: str,
    frozen_base_owned: dict[str, object],
) -> None:
    unsafe = candidate_symlinks(candidate_root, symlink_policy)
    if unsafe:
        raise ValueError("candidate tree contains symlinks: " + ", ".join(str(path) for path in unsafe))
    shutil.copytree(candidate_root, output_root, symlinks=symlink_policy != "reject")
    for relative, snapshot in frozen_base_owned.items():
        materialize_snapshot(snapshot, output_root / relative, output_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument("--runner-root", type=Path)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--targets-json", required=True)
    parser.add_argument("--symlink-policy", choices=("reject", "protected"), default="reject")
    args = parser.parse_args()

    try:
        targets = json.loads(args.targets_json)
    except json.JSONDecodeError:
        return 2
    if not isinstance(targets, list) or not targets or any(
        not isinstance(target, str) or not TARGET_RE.fullmatch(target) for target in targets
    ):
        return 2

    trusted_root = args.trusted_root.resolve()
    runner_root = (args.runner_root or args.trusted_root).resolve()
    candidate_root = args.candidate_root.resolve()
    trusted_makefile = trusted_root / "Makefile"
    if not trusted_makefile.is_file() or trusted_makefile.is_symlink() or not candidate_root.is_dir():
        return 2
    allowlist_path = runner_root / "src" / "skills" / "shared" / "scripts" / "native_validation.py"
    if not allowlist_path.is_file() or allowlist_path.is_symlink():
        return 2
    spec = importlib.util.spec_from_file_location("trusted_native_validation", allowlist_path)
    if spec is None or spec.loader is None:
        return 2
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if any(target not in module.ALLOWED_MAKE_TARGETS for target in targets):
        return 2
    unsafe = candidate_symlinks(candidate_root, args.symlink_policy)
    if unsafe:
        print("candidate tree contains symlinks: " + ", ".join(str(path) for path in unsafe), file=sys.stderr)
        return 2
    shadows = candidate_import_shadows(trusted_root, candidate_root)
    if shadows:
        print("candidate tree shadows trusted Python imports: " + ", ".join(shadows), file=sys.stderr)
        return 2
    try:
        frozen_base_owned = freeze_base_owned_files(trusted_root)
        validate_loom_flow_boundary = (trusted_root / LOOM_FLOW_PATH).is_file()
        validate_security_contract = frozen_base_owned.get("test/trusted_candidate_validation_test.py") is not None
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="loom-candidate-validation-") as temporary:
        try:
            for index, target in enumerate(targets):
                validation_root = Path(temporary) / f"candidate-{index}"
                trusted_overlay(
                    candidate_root,
                    validation_root,
                    args.symlink_policy,
                    frozen_base_owned,
                )
                safe_environment = candidate_environment(validation_root)
                security_contract = validation_root / "test" / "trusted_candidate_validation_test.py"
                if validate_security_contract:
                    security = subprocess.run(
                        [sys.executable, str(security_contract)],
                        cwd=validation_root,
                        env=safe_environment,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    verify_base_owned_files(frozen_base_owned, validation_root)
                    if security.returncode != 0:
                        raise ValueError("trusted candidate validation contract failed:\n" + security.stderr.strip())

                completed = subprocess.run(
                    ["make", "-f", str(validation_root / "Makefile"), "--", target],
                    cwd=validation_root,
                    env=safe_environment,
                    check=False,
                )
                verify_base_owned_files(frozen_base_owned, validation_root)
                if completed.returncode != 0:
                    return completed.returncode

                if validate_loom_flow_boundary:
                    boundary = subprocess.run(
                        [sys.executable, str(validation_root / "test" / "loom_flow_module_split_test.py")],
                        cwd=validation_root,
                        env=safe_environment,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    verify_base_owned_files(frozen_base_owned, validation_root)
                    if boundary.returncode != 0:
                        raise ValueError("candidate loom_flow module boundary failed:\n" + boundary.stderr.strip())
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
