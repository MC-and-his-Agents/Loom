#!/usr/bin/env python3
"""Validate repository-local composite GitHub actions without executing them."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
REMOTE_USES_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[A-Za-z0-9_./-]+")
STEP_KEYS = {"continue-on-error", "env", "id", "if", "name", "run", "shell", "uses", "with", "working-directory"}
RUBY_LOADER = r'''
require "json"
require "yaml"
value = YAML.safe_load(File.read(ARGV[0]), permitted_classes: [], permitted_symbols: [], aliases: false)
STDOUT.write(JSON.generate(value))
'''


def read_yaml(path: Path) -> object:
    completed = subprocess.run(
        ["ruby", "-e", RUBY_LOADER, str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or "invalid YAML")
    return json.loads(completed.stdout)


def validate_action(path: Path) -> list[str]:
    try:
        payload = read_yaml(path)
    except (ValueError, json.JSONDecodeError) as error:
        return [f"{path}: {error}"]
    if not isinstance(payload, dict):
        return [f"{path}: action manifest must be a mapping"]
    errors: list[str] = []
    for field in ("name", "description"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            errors.append(f"{path}: {field} must be a non-empty string")
    runs = payload.get("runs")
    if not isinstance(runs, dict) or runs.get("using") != "composite":
        errors.append(f"{path}: runs.using must be composite")
        return errors
    unknown_runs = sorted(set(runs) - {"using", "steps"})
    if unknown_runs:
        errors.append(f"{path}: runs contains unsupported keys: {', '.join(unknown_runs)}")
    steps = runs.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{path}: runs.steps must be a non-empty list")
        return errors
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"{path}: step {index} must be a mapping")
            continue
        unknown = sorted(set(step) - STEP_KEYS)
        if unknown:
            errors.append(f"{path}: step {index} contains unsupported keys: {', '.join(unknown)}")
        has_run = isinstance(step.get("run"), str) and bool(step["run"].strip())
        has_uses = isinstance(step.get("uses"), str) and bool(step["uses"].strip())
        if has_run == has_uses:
            errors.append(f"{path}: step {index} must declare exactly one of run or uses")
        if has_run and not isinstance(step.get("shell"), str):
            errors.append(f"{path}: run step {index} must declare shell")
        if has_uses:
            uses = step["uses"]
            if "${{" in uses or any(character.isspace() for character in uses):
                errors.append(f"{path}: step {index} uses must not contain expressions or whitespace")
            elif uses.startswith("./"):
                relative = PurePosixPath(uses[2:])
                if not relative.parts or ".." in relative.parts or relative.is_absolute():
                    errors.append(f"{path}: step {index} local uses must remain inside the repository")
            elif not REMOTE_USES_RE.fullmatch(uses):
                errors.append(f"{path}: step {index} uses must be local or owner/repository@ref")
        for field in ("env", "with"):
            value = step.get(field)
            if value is not None and not isinstance(value, dict):
                errors.append(f"{path}: step {index} {field} must be a mapping")
    return errors


def discover_manifests(repository_root: Path, action_root: Path) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    manifests: list[Path] = []
    if not action_root.exists():
        return manifests, errors
    for ancestor in (repository_root / ".github", action_root):
        if ancestor.is_symlink():
            return manifests, [f"{ancestor}: composite action ancestor must not be a symlink"]
    root = action_root.resolve()
    try:
        root.relative_to(repository_root.resolve())
    except ValueError:
        return manifests, [f"{action_root}: actions root escapes repository root"]
    for directory, names, files in os.walk(action_root, followlinks=False):
        base = Path(directory)
        for name in [*names, *files]:
            path = base / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                errors.append(f"{path}: composite action tree must not contain symlinks")
        for name in files:
            if name not in {"action.yml", "action.yaml"}:
                continue
            path = base / name
            try:
                path.resolve().relative_to(root)
            except ValueError:
                errors.append(f"{path}: manifest escapes actions root")
                continue
            manifests.append(path)
    return sorted(manifests), errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    repository_root = args.root.resolve()
    action_root = repository_root / ".github" / "actions"
    manifests, errors = discover_manifests(repository_root, action_root)
    errors.extend(error for path in manifests for error in validate_action(path))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"composite action contract: OK ({len(manifests)} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
