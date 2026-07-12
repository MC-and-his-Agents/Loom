#!/usr/bin/env python3
"""Run candidate validation with checker code and fixtures from a trusted checkout."""

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
TRUSTED_TOOL_FILES = (
    "host_adapter_check.py",
    "py_compile_clean.py",
    "read_delivery_gate_required_identity.py",
    "skills_surface.py",
    "version_surface_check.py",
)
PROTECTED_HARNESS_FILES = (
    ".github/workflows/loom-delivery-gate.yml",
    "Makefile",
    "src/skills/shared/scripts/delivery_gate.py",
    "src/skills/shared/scripts/failure_envelope.py",
    "src/skills/shared/scripts/light_profile.py",
    "src/skills/shared/scripts/native_validation.py",
    "test/npm-package-smoke.test.mjs",
    *tuple(f"tools/{name}" for name in TRUSTED_TOOL_FILES),
)


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


def path_snapshot(path: Path) -> object:
    if not path.exists():
        return None
    if path.is_file():
        return ("file", path.read_bytes())
    if path.is_dir():
        return (
            "directory",
            tuple(
                (str(item.relative_to(path)), item.read_bytes())
                for item in sorted(path.rglob("*"))
                if item.is_file()
            ),
        )
    return ("unsupported",)


def protected_harness_drift(trusted_root: Path, candidate_root: Path) -> list[str]:
    protected = set(PROTECTED_HARNESS_FILES)
    protected.add("tools/fixtures")
    protected.update(
        f"tools/{path.name}"
        for root in (trusted_root, candidate_root)
        for path in (root / "tools").glob("check_*.py")
    )
    return sorted(
        relative
        for relative in protected
        if path_snapshot(trusted_root / relative) != path_snapshot(candidate_root / relative)
    )


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


def trusted_overlay(trusted_root: Path, candidate_root: Path, output_root: Path, symlink_policy: str) -> None:
    unsafe = candidate_symlinks(candidate_root, symlink_policy)
    if unsafe:
        raise ValueError("candidate tree contains symlinks: " + ", ".join(str(path) for path in unsafe))
    drift = protected_harness_drift(trusted_root, candidate_root)
    if drift:
        raise ValueError("protected validation harness drift requires a base-trusted bootstrap: " + ", ".join(drift))
    shutil.copytree(candidate_root, output_root, symlinks=symlink_policy != "reject")
    replace_path(trusted_root / "Makefile", output_root / "Makefile", output_root)
    trusted_fixtures = trusted_root / "tools" / "fixtures"
    if trusted_fixtures.is_dir():
        replace_path(trusted_fixtures, output_root / "tools" / "fixtures", output_root)
    for source in sorted((trusted_root / "tools").glob("check_*.py")):
        replace_path(source, output_root / "tools" / source.name, output_root)
    for name in TRUSTED_TOOL_FILES:
        source = trusted_root / "tools" / name
        if source.is_file():
            replace_path(source, output_root / "tools" / name, output_root)
    package_test = trusted_root / "test" / "npm-package-smoke.test.mjs"
    if package_test.is_file():
        replace_path(package_test, output_root / "test" / package_test.name, output_root)


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
    if not (trusted_root / "Makefile").is_file() or not candidate_root.is_dir():
        return 2
    allowlist_path = runner_root / "src" / "skills" / "shared" / "scripts" / "native_validation.py"
    spec = importlib.util.spec_from_file_location("trusted_native_validation", allowlist_path)
    if spec is None or spec.loader is None:
        return 2
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if any(target not in module.ALLOWED_MAKE_TARGETS for target in targets):
        return 2

    with tempfile.TemporaryDirectory(prefix="loom-candidate-validation-") as temporary:
        validation_root = Path(temporary) / "candidate"
        try:
            trusted_overlay(trusted_root, candidate_root, validation_root, args.symlink_policy)
            safe_environment = {
                key: value
                for key, value in os.environ.items()
                if key in {"HOME", "LANG", "LC_ALL", "PATH", "SHELL", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR"}
            }
            safe_environment.update(
                {
                    "LOOM_CANDIDATE_VALIDATION": "1",
                    "PYTHONSAFEPATH": "1",
                    "PYTHONPATH": os.pathsep.join(
                        (
                            str(validation_root / "src" / "skills" / "shared" / "scripts"),
                            str(validation_root / "tools"),
                        )
                    ),
                }
            )
            completed = subprocess.run(
                ["make", "-f", str(validation_root / "Makefile"), "--", *targets],
                cwd=validation_root,
                env=safe_environment,
                check=False,
            )
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
