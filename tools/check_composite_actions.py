#!/usr/bin/env python3
"""Validate repository-local composite GitHub actions without executing them."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
    runs = payload.get("runs")
    if not isinstance(runs, dict) or runs.get("using") != "composite":
        return [f"{path}: runs.using must be composite"]
    steps = runs.get("steps")
    if not isinstance(steps, list) or not steps:
        return [f"{path}: runs.steps must be a non-empty list"]
    errors: list[str] = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"{path}: step {index} must be a mapping")
            continue
        has_run = isinstance(step.get("run"), str) and bool(step["run"].strip())
        has_uses = isinstance(step.get("uses"), str) and bool(step["uses"].strip())
        if has_run == has_uses:
            errors.append(f"{path}: step {index} must declare exactly one of run or uses")
        if has_run and not isinstance(step.get("shell"), str):
            errors.append(f"{path}: run step {index} must declare shell")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    action_root = args.root.resolve() / ".github" / "actions"
    manifests = sorted({*action_root.glob("*/action.yml"), *action_root.glob("*/action.yaml")})
    errors = [error for path in manifests for error in validate_action(path)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"composite action contract: OK ({len(manifests)} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
