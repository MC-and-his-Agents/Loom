#!/usr/bin/env python3
"""Lightweight regression checks for loom_check runtime purity hardening."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SHARED_SCRIPTS = ROOT / "skills/shared/scripts"


def load_loom_check():
    sys.path.insert(0, str(SHARED_SCRIPTS))
    import loom_check  # type: ignore[import-not-found]

    return loom_check


def run(args: list[str], *, env: dict[str, str] | None = None, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    command_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        command_env.update(env)
    return subprocess.run(
        args,
        cwd=ROOT,
        env=command_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def current_loom_check_temp_dirs() -> set[Path]:
    roots = {Path(tempfile.gettempdir()), Path("/tmp"), Path("/private/tmp")}
    found: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("loom-check-*"):
            if path.is_dir():
                found.add(path.resolve())
    return found


def check_temp_dir_cleanup(baseline: set[Path], failures: list[str]) -> None:
    leftovers = sorted(str(path) for path in current_loom_check_temp_dirs() - baseline)
    if leftovers:
        fail("loom_check temporary directories must be removed after use: " + ", ".join(leftovers), failures)


def check_cli_single_flight(loom_check, failures: list[str]) -> None:
    lock_path = loom_check.loom_check_lock_path(ROOT)
    if lock_path.exists():
        fail(f"loom_check lock already exists before regression: {lock_path}", failures)
        return
    owner = {
        "schema_version": "loom-check-single-flight-lock/v1",
        "run_id": "regression-owner",
        "pid": os.getpid(),
        "started_at": loom_check.utc_now_iso(),
        "command": "regression lock owner",
        "cwd": str(ROOT),
    }
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_path.write_text(json.dumps(owner, indent=2) + "\n", encoding="utf-8")
        result = run(["python3", "tools/loom_check.py", "--profile", "source", str(ROOT)], timeout=15.0)
        output = result.stdout + result.stderr
        if result.returncode != 3:
            fail(f"second loom_check process must fail fast with lock status 3, got {result.returncode}", failures)
        for term in ("another run is already active", "owner:", "started_at=", "owner_command:", "owner_cwd:", "fallback:"):
            if term not in output:
                fail(f"single-flight CLI output must include `{term}`", failures)
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def check_worktree_local_lock_paths(loom_check, failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="loom-check-regression-") as tmp:
        first = Path(tmp) / "repo-a"
        second = Path(tmp) / "repo-b"
        first.mkdir()
        second.mkdir()
        lock_a = loom_check.acquire_single_flight_lock(first, ["loom_check.py", str(first)])
        try:
            lock_b = loom_check.acquire_single_flight_lock(second, ["loom_check.py", str(second)])
            try:
                if lock_a.path == lock_b.path:
                    fail("different worktrees must not share the same loom_check lock path", failures)
            finally:
                loom_check.release_single_flight_lock(lock_b)
        finally:
            loom_check.release_single_flight_lock(lock_a)


def check_runtime_purity_helpers(loom_check, failures: list[str]) -> None:
    for failure in loom_check.check_loom_check_runtime_purity():
        fail(f"{failure.category}: {failure.detail}", failures)


def check_installer_busy_output(failures: list[str]) -> None:
    package_root = ROOT / "packages/loom-installer"
    lock_dir = package_root / ".installer-regression-lock"
    owner_path = lock_dir / "owner.json"
    if lock_dir.exists():
        fail(f"installer regression lock already exists before regression: {lock_dir}", failures)
        return
    owner = {
        "schema_version": "loom-installer-regression-lock/v1",
        "run_id": "regression-owner",
        "pid": os.getpid(),
        "started_at": "2099-01-01T00:00:00.000Z",
        "command": "regression lock owner",
        "cwd": str(ROOT),
    }
    try:
        lock_dir.mkdir()
        owner_path.write_text(json.dumps(owner, indent=2) + "\n", encoding="utf-8")
        result = run(
            ["node", "packages/loom-installer/scripts/run-regression.mjs"],
            env={"LOOM_INSTALLER_REGRESSION_LOCK_TIMEOUT_SECONDS": "0.1"},
            timeout=15.0,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail("installer regression must not run while the package-root lock is owned", failures)
        for term in ("installer regression lock is busy", "owner:", "started_at=", "owner_command:", "owner_cwd:", "fallback:"):
            if term not in output:
                fail(f"installer regression busy output must include `{term}`", failures)
    finally:
        shutil.rmtree(lock_dir, ignore_errors=True)


def check_demo_fixture_stays_clean(failures: list[str]) -> None:
    before = run(["git", "status", "--short", "--", "examples/new-project"], timeout=30.0)
    if before.returncode != 0:
        fail(f"failed to read demo fixture git status: {before.stderr.strip() or before.stdout.strip()}", failures)
        return
    result = run(["python3", "tools/check_demo_bootstrap_fixture.py"], timeout=180.0)
    if result.returncode != 0:
        fail(f"demo bootstrap fixture check failed: {result.stderr.strip() or result.stdout.strip()}", failures)
        return
    after = run(["git", "status", "--short", "--", "examples/new-project"], timeout=30.0)
    if after.returncode != 0:
        fail(f"failed to re-read demo fixture git status: {after.stderr.strip() or after.stdout.strip()}", failures)
        return
    if before.stdout != after.stdout:
        fail("demo bootstrap fixture check must not dirty examples/new-project", failures)


def main() -> int:
    failures: list[str] = []
    temp_dir_baseline = current_loom_check_temp_dirs()
    loom_check = load_loom_check()
    check_cli_single_flight(loom_check, failures)
    check_worktree_local_lock_paths(loom_check, failures)
    check_runtime_purity_helpers(loom_check, failures)
    check_installer_busy_output(failures)
    check_demo_fixture_stays_clean(failures)
    check_temp_dir_cleanup(temp_dir_baseline, failures)

    if failures:
        print("loom_check runtime regression: FAILED")
        for item in failures:
            print(f"- {item}")
        return 1
    print("loom_check runtime regression: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
