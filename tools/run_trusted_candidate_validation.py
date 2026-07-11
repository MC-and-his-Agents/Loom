#!/usr/bin/env python3
"""Run candidate validation with checker code and fixtures from a trusted checkout."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
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


def replace_path(source: Path, destination: Path) -> None:
    if destination.is_dir() and not destination.is_symlink():
        shutil.rmtree(destination)
    elif destination.exists() or destination.is_symlink():
        destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def trusted_overlay(trusted_root: Path, candidate_root: Path, output_root: Path) -> None:
    # Preserve candidate symlinks without dereferencing host paths into the validation tree.
    shutil.copytree(candidate_root, output_root, symlinks=True)
    replace_path(trusted_root / "Makefile", output_root / "Makefile")
    replace_path(trusted_root / "tools" / "fixtures", output_root / "tools" / "fixtures")
    for source in sorted((trusted_root / "tools").glob("check_*.py")):
        replace_path(source, output_root / "tools" / source.name)
    for name in TRUSTED_TOOL_FILES:
        source = trusted_root / "tools" / name
        if source.is_file():
            replace_path(source, output_root / "tools" / name)
    package_test = trusted_root / "test" / "npm-package-smoke.test.mjs"
    if package_test.is_file():
        replace_path(package_test, output_root / "test" / package_test.name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--targets-json", required=True)
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
    candidate_root = args.candidate_root.resolve()
    if not (trusted_root / "Makefile").is_file() or not candidate_root.is_dir():
        return 2
    allowlist_path = trusted_root / "src" / "skills" / "shared" / "scripts" / "native_validation.py"
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
            trusted_overlay(trusted_root, candidate_root, validation_root)
            completed = subprocess.run(
                ["make", "-f", str(validation_root / "Makefile"), "--", *targets],
                cwd=validation_root,
                env={**os.environ, "PYTHONSAFEPATH": "1"},
                check=False,
            )
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
