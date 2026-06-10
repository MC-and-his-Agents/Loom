#!/usr/bin/env python3
"""Check the demo bootstrap fixture without rewriting the stable fixture."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


BUCKET_LABEL = "demo-bootstrap"
AGGREGATE_SURFACE_LABEL = "demo-bootstrap-fixture"
GENERATION_SURFACE_LABEL = "demo-bootstrap-generation"
DRIFT_SURFACE_LABEL = "demo-bootstrap-fixture-drift"
GENERATION_SCENARIO_LABEL = "new-project-bootstrap-command"
DRIFT_SCENARIO_LABEL = "stable-fixture-comparison"
AGGREGATE_SCENARIO_LABEL = "new-project-fixture-check"
GENERATION_FAILURE_LABEL = "demo-bootstrap-generation-command-failed"
GENERATION_TIMEOUT_LABEL = "demo-bootstrap-generation-timeout"
FIXTURE_MISSING_LABEL = "demo-bootstrap-fixture-missing"
DRIFT_FAILURE_LABEL = "demo-bootstrap-fixture-drift"
GENERATION_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface generation"
DRIFT_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface fixture-drift"
AGGREGATE_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface aggregate"

DEFAULT_IGNORES = {
    ".loom/runtime",
    ".loom/tmp",
    ".loom/cache",
    "__pycache__",
}

HOST_DYNAMIC_INIT_RESULT_SECTIONS = {
    "governance_surface",
    "lifecycle_expectations",
    "maturity_upgrade_path",
    "runtime_state",
}


@dataclass
class BootstrapRun:
    command: list[str]
    stdout: str
    stderr: str
    returncode: int
    elapsed_ms: int
    timed_out: bool = False


def relative_to_root(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def ignored(path: Path, root: Path, ignored_relatives: set[str]) -> bool:
    relative = relative_to_root(path, root)
    parts = set(path.relative_to(root).parts)
    if bool(parts & ignored_relatives):
        return True
    return any(relative == ignored or relative.startswith(f"{ignored}/") for ignored in ignored_relatives)


def compare_trees(expected: Path, actual: Path, ignored_relatives: set[str]) -> list[str]:
    differences: list[str] = []

    expected_paths = {
        relative_to_root(path, expected)
        for path in expected.rglob("*")
        if not ignored(path, expected, ignored_relatives)
    }
    actual_paths = {
        relative_to_root(path, actual)
        for path in actual.rglob("*")
        if not ignored(path, actual, ignored_relatives)
    }

    for relative in sorted(expected_paths - actual_paths):
        differences.append(f"missing generated path: {relative}")
    for relative in sorted(actual_paths - expected_paths):
        differences.append(f"unexpected generated path: {relative}")

    for relative in sorted(expected_paths & actual_paths):
        expected_path = expected / relative
        actual_path = actual / relative
        if expected_path.is_dir() or actual_path.is_dir():
            if expected_path.is_dir() != actual_path.is_dir():
                differences.append(f"path type differs: {relative}")
            continue
        if expected_path.is_symlink() or actual_path.is_symlink():
            if expected_path.is_symlink() != actual_path.is_symlink() or os.readlink(expected_path) != os.readlink(actual_path):
                differences.append(f"symlink target differs: {relative}")
            continue
        if comparable_bytes(expected_path, relative) != comparable_bytes(actual_path, relative):
            differences.append(f"file content differs: {relative}")

    return differences


def comparable_bytes(path: Path, relative: str) -> bytes:
    if relative == ".loom/bootstrap/init-result.json":
        return canonical_init_result(path)
    return path.read_bytes()


def canonical_init_result(path: Path) -> bytes:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        # Host/runtime visibility is intentionally outside the stable demo
        # fixture drift contract; compare authored bootstrap content without
        # live GitHub, CI, checkout, or runtime path proof.
        for section in HOST_DYNAMIC_INIT_RESULT_SECTIONS:
            if section in payload:
                payload[section] = {"comparison": "ignored-host-dynamic"}
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def bootstrap_command(repo_root: Path, generated: Path) -> list[str]:
    return [
        sys.executable,
        "tools/loom_init.py",
        "bootstrap",
        "--target",
        str(generated),
        "--scenario",
        "new",
        "--intent",
        "execution-control",
        "--intake",
        str(generated / ".loom/bootstrap/intake.snapshot.json"),
        "--write",
        "--force",
        "--install-pr-template",
        "--portable-output",
    ]


def command_display(command: list[str], repo_root: Path) -> str:
    display: list[str] = []
    for item in command:
        if item == sys.executable:
            display.append("python3")
            continue
        try:
            display.append(str(Path(item).resolve().relative_to(repo_root)))
        except (OSError, ValueError):
            display.append(item)
    return shlex.join(display)


def source_locator(fixture: Path, repo_root: Path) -> str:
    return f"{relative_to_root(fixture, repo_root)}/.loom/bootstrap/intake.snapshot.json"


def printable_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def surface_evidence_line(**fields: object) -> str:
    rendered = " ".join(f"{key}={json.dumps(str(value), sort_keys=True)}" for key, value in fields.items())
    return f"demo bootstrap surface evidence: {rendered}"


def print_surface_evidence(*, stream, **fields: object) -> None:
    print(surface_evidence_line(**fields), file=stream)


def run_bootstrap(repo_root: Path, generated: Path, timeout: float) -> BootstrapRun:
    command = bootstrap_command(repo_root, generated)
    started = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return BootstrapRun(
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
        )
    except subprocess.TimeoutExpired as exc:
        return BootstrapRun(
            command=command,
            stdout=printable_text(exc.stdout),
            stderr=printable_text(exc.stderr),
            returncode=124,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
            timed_out=True,
        )


def print_generation_failure(run_result: BootstrapRun, fixture: Path, repo_root: Path) -> None:
    failure_label = GENERATION_TIMEOUT_LABEL if run_result.timed_out else GENERATION_FAILURE_LABEL
    summary = (
        f"bootstrap command timed out after {run_result.elapsed_ms} ms"
        if run_result.timed_out
        else f"bootstrap command exited with status {run_result.returncode}"
    )
    print("demo bootstrap fixture check failed while rebuilding isolated fixture", file=sys.stderr)
    print_surface_evidence(
        stream=sys.stderr,
        bucket_label=BUCKET_LABEL,
        surface_label=GENERATION_SURFACE_LABEL,
        surface_kind="named_surface",
        scenario_label=GENERATION_SCENARIO_LABEL,
        command=command_display(run_result.command, repo_root),
        result="block",
        elapsed_ms=run_result.elapsed_ms,
        failure_label=failure_label,
        failure_taxonomy=failure_label,
        failure_summary=summary,
        source_locator=source_locator(fixture, repo_root),
        evidence_locator=GENERATION_EVIDENCE_LOCATOR,
        validator_mode="demo-bootstrap-generation",
        is_aggregate="false",
    )
    print(run_result.stdout, end="")
    print(run_result.stderr, end="", file=sys.stderr)


def run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    fixture = (repo_root / args.fixture).resolve()
    if not fixture.exists():
        print(f"demo bootstrap fixture is missing: {fixture}", file=sys.stderr)
        print_surface_evidence(
            stream=sys.stderr,
            bucket_label=BUCKET_LABEL,
            surface_label=GENERATION_SURFACE_LABEL,
            surface_kind="named_surface",
            scenario_label=GENERATION_SCENARIO_LABEL,
            command=GENERATION_EVIDENCE_LOCATOR,
            result="block",
            elapsed_ms=0,
            failure_label=FIXTURE_MISSING_LABEL,
            failure_taxonomy=FIXTURE_MISSING_LABEL,
            failure_summary=f"stable fixture is missing: {fixture}",
            source_locator=args.fixture,
            evidence_locator=GENERATION_EVIDENCE_LOCATOR,
            validator_mode="demo-bootstrap-generation",
            is_aggregate="false",
        )
        return 2

    ignored_relatives = set(DEFAULT_IGNORES)
    ignored_relatives.update(args.ignore)

    with tempfile.TemporaryDirectory(prefix=".loom-demo-bootstrap-check-", dir=repo_root) as tmp:
        generated = Path(tmp) / fixture.name
        shutil.copytree(fixture, generated, symlinks=True)
        generation = run_bootstrap(repo_root, generated, args.timeout)
        if generation.returncode != 0:
            print_generation_failure(generation, fixture, repo_root)
            return generation.returncode

        generation_evidence = {
            "bucket_label": BUCKET_LABEL,
            "surface_label": GENERATION_SURFACE_LABEL,
            "surface_kind": "named_surface",
            "scenario_label": GENERATION_SCENARIO_LABEL,
            "command": command_display(generation.command, repo_root),
            "result": "pass",
            "elapsed_ms": generation.elapsed_ms,
            "source_locator": source_locator(fixture, repo_root),
            "evidence_locator": GENERATION_EVIDENCE_LOCATOR,
            "validator_mode": "demo-bootstrap-generation",
            "is_aggregate": "false",
        }
        if args.surface == "generation":
            print_surface_evidence(stream=sys.stdout, **generation_evidence)
            print(f"demo bootstrap generation: OK ({fixture.relative_to(repo_root)})")
            return 0

        drift_started = time.perf_counter()
        differences = compare_trees(fixture, generated, ignored_relatives)
        drift_elapsed_ms = int((time.perf_counter() - drift_started) * 1000)
        if differences:
            print("demo bootstrap fixture drift detected:", file=sys.stderr)
            for difference in differences[: args.max_differences]:
                print(f"- {difference}", file=sys.stderr)
            if len(differences) > args.max_differences:
                print(f"- ... {len(differences) - args.max_differences} more differences", file=sys.stderr)
            print("run `make loom-demo-new-project-sync` to refresh the stable fixture intentionally.", file=sys.stderr)
            print_surface_evidence(
                stream=sys.stderr,
                bucket_label=BUCKET_LABEL,
                surface_label=DRIFT_SURFACE_LABEL,
                surface_kind="named_surface",
                scenario_label=DRIFT_SCENARIO_LABEL,
                command=DRIFT_EVIDENCE_LOCATOR,
                result="block",
                elapsed_ms=drift_elapsed_ms,
                failure_label=DRIFT_FAILURE_LABEL,
                failure_taxonomy=DRIFT_FAILURE_LABEL,
                failure_summary=f"{len(differences)} generated fixture difference(s)",
                source_locator=relative_to_root(fixture, repo_root),
                evidence_locator=DRIFT_EVIDENCE_LOCATOR,
                validator_mode="demo-bootstrap-fixture-drift",
                is_aggregate="false",
            )
            return 1

        if args.show_surface_evidence:
            print_surface_evidence(stream=sys.stdout, **generation_evidence)
            print_surface_evidence(
                stream=sys.stdout,
                bucket_label=BUCKET_LABEL,
                surface_label=DRIFT_SURFACE_LABEL,
                surface_kind="named_surface",
                scenario_label=DRIFT_SCENARIO_LABEL,
                command=DRIFT_EVIDENCE_LOCATOR,
                result="pass",
                elapsed_ms=drift_elapsed_ms,
                source_locator=relative_to_root(fixture, repo_root),
                evidence_locator=DRIFT_EVIDENCE_LOCATOR,
                validator_mode="demo-bootstrap-fixture-drift",
                is_aggregate="false",
            )
            if args.surface == "aggregate":
                print_surface_evidence(
                    stream=sys.stdout,
                    bucket_label=BUCKET_LABEL,
                    surface_label=AGGREGATE_SURFACE_LABEL,
                    surface_kind="aggregate_surface",
                    scenario_label=AGGREGATE_SCENARIO_LABEL,
                    command=AGGREGATE_EVIDENCE_LOCATOR,
                    result="pass",
                    elapsed_ms=generation.elapsed_ms + drift_elapsed_ms,
                    source_locator=relative_to_root(fixture, repo_root),
                    evidence_locator=AGGREGATE_EVIDENCE_LOCATOR,
                    validator_mode="demo-bootstrap-fixture",
                    is_aggregate="true",
                    subsurface_count=2,
                    subsurface_results=f"{GENERATION_SURFACE_LABEL}:pass,{DRIFT_SURFACE_LABEL}:pass",
                )

    print(f"demo bootstrap fixture: OK ({fixture.relative_to(repo_root)})")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Loom source repository root.")
    parser.add_argument("--fixture", default="examples/new-project", help="Stable demo fixture path.")
    parser.add_argument("--ignore", action="append", default=[], help="Additional repo-relative fixture paths to ignore.")
    parser.add_argument("--timeout", type=float, default=120.0, help="Isolated bootstrap timeout in seconds.")
    parser.add_argument("--max-differences", type=int, default=40, help="Maximum drift entries to print.")
    parser.add_argument(
        "--surface",
        choices=("aggregate", "generation", "fixture-drift"),
        default="aggregate",
        help="Validation surface to run. aggregate preserves the existing fixture check contract.",
    )
    parser.add_argument(
        "--show-surface-evidence",
        action="store_true",
        help="Print machine-readable surface evidence on passing aggregate or fixture-drift checks.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    raise SystemExit(main())
