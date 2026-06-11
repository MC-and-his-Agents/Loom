#!/usr/bin/env python3
"""Lightweight regression checks for loom_check runtime purity hardening."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SHARED_SCRIPTS = ROOT / "skills/shared/scripts"


@dataclass(frozen=True)
class RuntimeRegressionSurface:
    name: str
    fixture_group: str
    run: Callable[[list[str]], None]
    selectable: bool = False


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


def format_duration(seconds: float) -> str:
    return f"{seconds:.2f}s"


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
        fail(
            "failure_label=tempdir-cleanup-residue "
            "evidence_locator=tempdir-cleanup/loom-check-temp-dir-residue: "
            "loom_check temporary directories must be removed after use: "
            + ", ".join(leftovers),
            failures,
        )


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
        if is_subprocess_env_purity_failure(failure.detail):
            continue
        fail(f"{failure.category}: {failure.detail}", failures)


def is_subprocess_env_purity_failure(detail: str) -> bool:
    return (
        detail.startswith("default subprocess env must strip host-only variables")
        or detail.startswith("default env purity probe ")
        or detail.startswith("default subprocess env must not inherit ")
        or detail.startswith("explicit env fixture probe ")
        or detail.startswith("explicit fixture env must be preserved ")
    )


def subprocess_env_evidence_locator(detail: str) -> str:
    if detail.startswith("default subprocess env must strip host-only variables"):
        return "clean_subprocess_env/default-strip-host-only"
    if detail.startswith("default env purity probe "):
        return "run_command/default-env-probe"
    if detail.startswith("default subprocess env must not inherit "):
        return "run_command/default-env-inheritance"
    if detail.startswith("explicit env fixture probe "):
        return "run_command/explicit-env-fixture-probe"
    if detail.startswith("explicit fixture env must be preserved "):
        return "run_command/explicit-env-fixture-preservation"
    return "run_command/subprocess-env-purity"


def check_subprocess_env_purity(loom_check, failures: list[str]) -> None:
    for failure in loom_check.check_loom_check_runtime_purity():
        if not is_subprocess_env_purity_failure(failure.detail):
            continue
        evidence_locator = subprocess_env_evidence_locator(failure.detail)
        fail(f"{failure.category} evidence_locator={evidence_locator}: {failure.detail}", failures)


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
        fail(
            "failure_label=fixture-cleanliness-status-read "
            "evidence_locator=demo-fixture-cleanliness/git-status-before: "
            f"failed to read demo fixture git status: {before.stderr.strip() or before.stdout.strip()}",
            failures,
        )
        return
    result = run(["python3", "tools/check_demo_bootstrap_fixture.py"], timeout=180.0)
    if result.returncode != 0:
        fail(
            "failure_label=fixture-cleanliness-check-failed "
            "evidence_locator=demo-fixture-cleanliness/check-demo-bootstrap-fixture: "
            f"demo bootstrap fixture check failed: {result.stderr.strip() or result.stdout.strip()}",
            failures,
        )
        return
    after = run(["git", "status", "--short", "--", "examples/new-project"], timeout=30.0)
    if after.returncode != 0:
        fail(
            "failure_label=fixture-cleanliness-status-read "
            "evidence_locator=demo-fixture-cleanliness/git-status-after: "
            f"failed to re-read demo fixture git status: {after.stderr.strip() or after.stdout.strip()}",
            failures,
        )
        return
    if before.stdout != after.stdout:
        fail(
            "failure_label=fixture-cleanliness-tracked-drift "
            "evidence_locator=demo-fixture-cleanliness/tracked-file-cleanliness: "
            "demo bootstrap fixture check must not dirty examples/new-project",
            failures,
        )


def label_surface_failure(surface: RuntimeRegressionSurface, message: str) -> str:
    parts: list[str] = []
    if "failure_label=" not in message:
        parts.append(f"failure_label={surface.name}")
    if "evidence_locator=" not in message:
        parts.append(f"evidence_locator=runtime-regression/{surface.name}")
    if not parts:
        return message
    return " ".join(parts + [message])


def runtime_regression_surfaces(loom_check, temp_dir_baseline: set[Path]) -> tuple[RuntimeRegressionSurface, ...]:
    return (
        RuntimeRegressionSurface(
            name="single-flight-locking",
            fixture_group="locking",
            run=lambda failures: check_cli_single_flight(loom_check, failures),
            selectable=True,
        ),
        RuntimeRegressionSurface(
            name="worktree-local-lock-paths",
            fixture_group="locking",
            run=lambda failures: check_worktree_local_lock_paths(loom_check, failures),
            selectable=True,
        ),
        RuntimeRegressionSurface(
            name="runtime-purity-helpers",
            fixture_group="aggregate-runtime-regression",
            run=lambda failures: check_runtime_purity_helpers(loom_check, failures),
        ),
        RuntimeRegressionSurface(
            name="subprocess-env-purity",
            fixture_group="environment-purity",
            run=lambda failures: check_subprocess_env_purity(loom_check, failures),
            selectable=True,
        ),
        RuntimeRegressionSurface(
            name="installer-regression-lock-output",
            fixture_group="locking",
            run=check_installer_busy_output,
            selectable=True,
        ),
        RuntimeRegressionSurface(
            name="demo-fixture-cleanliness",
            fixture_group="fixture-cleanliness",
            run=check_demo_fixture_stays_clean,
            selectable=True,
        ),
        RuntimeRegressionSurface(
            name="temp-dir-cleanup",
            fixture_group="tempdir-cleanup",
            run=lambda failures: check_temp_dir_cleanup(temp_dir_baseline, failures),
            selectable=True,
        ),
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--surface",
        action="append",
        dest="surfaces",
        help="Run only the named runtime regression surface. May be passed more than once.",
    )
    parser.add_argument(
        "--fixture-group",
        action="append",
        dest="fixture_groups",
        help="Run only surfaces in the named fixture group. May be passed more than once.",
    )
    parser.add_argument(
        "--list-surfaces",
        action="store_true",
        help="List available surface names and fixture groups without running checks.",
    )
    return parser.parse_args(argv)


def select_surfaces(
    surfaces: tuple[RuntimeRegressionSurface, ...],
    *,
    requested_names: list[str] | None,
    requested_groups: list[str] | None,
) -> tuple[RuntimeRegressionSurface, ...]:
    selectable = tuple(surface for surface in surfaces if surface.selectable)
    selected = surfaces
    if requested_names:
        wanted = set(requested_names)
        known = {surface.name for surface in selectable}
        missing = wanted - known
        if missing:
            raise ValueError("unknown surface(s): " + ", ".join(sorted(missing)))
        selected = tuple(surface for surface in selectable if surface.name in wanted)
    if requested_groups:
        wanted_groups = set(requested_groups)
        known_groups = {surface.fixture_group for surface in selectable}
        missing_groups = wanted_groups - known_groups
        if missing_groups:
            raise ValueError("unknown fixture group(s): " + ", ".join(sorted(missing_groups)))
        candidates = selected if requested_names else selectable
        selected = tuple(surface for surface in candidates if surface.fixture_group in wanted_groups)
    if not selected:
        raise ValueError("surface filters selected no checks")
    return selected


def run_surfaces(surfaces: tuple[RuntimeRegressionSurface, ...]) -> int:
    failures: list[tuple[RuntimeRegressionSurface, float, str]] = []
    suite_start = time.perf_counter()
    total = len(surfaces)
    for index, surface in enumerate(surfaces, start=1):
        start = time.perf_counter()
        surface_failures: list[str] = []
        print(
            f"[{index}/{total}] runtime-regression surface={surface.name} fixture_group={surface.fixture_group} start",
            file=sys.stderr,
        )
        try:
            surface.run(surface_failures)
        except Exception as exc:
            surface_failures.append(f"raised {type(exc).__name__}: {exc}")
        elapsed = time.perf_counter() - start
        if surface_failures:
            for message in surface_failures:
                failures.append((surface, elapsed, label_surface_failure(surface, message)))
            print(
                f"[{index}/{total}] runtime-regression surface={surface.name} fixture_group={surface.fixture_group} failed in {format_duration(elapsed)} failures={len(surface_failures)}",
                file=sys.stderr,
            )
        else:
            print(
                f"[{index}/{total}] runtime-regression surface={surface.name} fixture_group={surface.fixture_group} passed in {format_duration(elapsed)}",
                file=sys.stderr,
            )

    if failures:
        print("loom_check runtime regression: FAILED")
        for surface, elapsed, message in failures:
            print(
                f"- surface={surface.name} fixture_group={surface.fixture_group} duration={format_duration(elapsed)}: {message}"
            )
        return 1
    total_elapsed = time.perf_counter() - suite_start
    print(f"loom_check runtime regression: OK ({total} surfaces, {format_duration(total_elapsed)})")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    temp_dir_baseline = current_loom_check_temp_dirs()
    loom_check = load_loom_check()
    surfaces = runtime_regression_surfaces(loom_check, temp_dir_baseline)
    if args.list_surfaces:
        for surface in surfaces:
            if not surface.selectable:
                continue
            print(f"{surface.name}\t{surface.fixture_group}")
        return 0
    try:
        selected = select_surfaces(
            surfaces,
            requested_names=args.surfaces,
            requested_groups=args.fixture_groups,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        print("available surfaces:", file=sys.stderr)
        for surface in surfaces:
            print(f"- {surface.name} (fixture_group={surface.fixture_group})", file=sys.stderr)
        return 2
    return run_surfaces(selected)


if __name__ == "__main__":
    raise SystemExit(main())
