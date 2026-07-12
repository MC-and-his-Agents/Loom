#!/usr/bin/env python3
"""Shared process, path, and JSON primitives for Loom flow modules."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from github_host import run_process
from runtime_state import detect_runtime_state


def resolve_target_arg(raw_target: str) -> Path:
    target = Path(raw_target).expanduser()
    if target.is_absolute():
        return target.resolve()
    invocation_cwd = os.environ.get("LOOM_INVOCATION_CWD")
    base = Path(invocation_cwd).expanduser() if invocation_cwd else Path.cwd()
    return (base / target).resolve()


def emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("result") == "pass" else 1


def runtime_state_payload(target_root: Path) -> dict[str, Any]:
    return detect_runtime_state(str(Path(__file__).with_name("loom_flow.py")), "loom-flow", target_root=target_root)


def command_target(target_root: Path) -> str:
    return shlex.quote(str(target_root))


def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        return subprocess.run(["git", *args], cwd=root, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return None


def git_branch(root: Path) -> str | None:
    result = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip() or None


def git_head_sha(root: Path) -> str | None:
    result = run_git(root, ["rev-parse", "HEAD"])
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip() or None


def local_command_json(target_root: Path, args: list[str], *, entrypoint: Path) -> tuple[dict[str, Any] | None, list[str]]:
    result = run_process([sys.executable, str(entrypoint), *args], target_root)
    if not result.stdout.strip():
        return None, [result.stderr.strip() or "command produced no JSON output"]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON from {' '.join(args)}: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"{' '.join(args)} did not return a JSON object"]
    return payload, []
