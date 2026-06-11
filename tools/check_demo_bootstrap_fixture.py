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
CANONICALIZATION_SURFACE_LABEL = "demo-bootstrap-canonicalization"
DRIFT_SURFACE_LABEL = "demo-bootstrap-fixture-drift"
CLEANLINESS_SURFACE_LABEL = "demo-bootstrap-examples-cleanliness"
GENERATION_SCENARIO_LABEL = "new-project-bootstrap-command"
CANONICALIZATION_SCENARIO_LABEL = "init-result-host-dynamic-canonicalization"
DRIFT_SCENARIO_LABEL = "stable-fixture-comparison"
CLEANLINESS_SCENARIO_LABEL = "examples-new-project-tracked-cleanliness"
AGGREGATE_SCENARIO_LABEL = "new-project-fixture-check"
GENERATION_FAILURE_LABEL = "demo-bootstrap-generation-command-failed"
GENERATION_TIMEOUT_LABEL = "demo-bootstrap-generation-timeout"
FIXTURE_MISSING_LABEL = "demo-bootstrap-fixture-missing"
CANONICALIZATION_INVALID_JSON_LABEL = "demo-bootstrap-canonicalization-invalid-json"
CANONICALIZATION_INVALID_SHAPE_LABEL = "demo-bootstrap-canonicalization-invalid-shape"
CANONICALIZATION_INCOMPLETE_LABEL = "demo-bootstrap-canonicalization-incomplete"
DRIFT_FAILURE_LABEL = "demo-bootstrap-fixture-drift"
CLEANLINESS_FAILURE_LABEL = "demo-bootstrap-examples-cleanliness-dirty"
CLEANLINESS_STATUS_FAILURE_LABEL = "demo-bootstrap-examples-cleanliness-status-failed"
GENERATION_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface generation"
CANONICALIZATION_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface canonicalization"
DRIFT_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface fixture-drift"
CLEANLINESS_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface cleanliness"
AGGREGATE_EVIDENCE_LOCATOR = "tools/check_demo_bootstrap_fixture.py --surface aggregate"
INIT_RESULT_RELATIVE = ".loom/bootstrap/init-result.json"
CANONICAL_DYNAMIC_SENTINEL = {"comparison": "ignored-host-dynamic"}

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


@dataclass
class CanonicalizationDiagnostic:
    target_label: str
    init_result_locator: str
    failure_label: str
    failure_summary: str


@dataclass
class CanonicalizationReport:
    elapsed_ms: int
    canonicalized_sections: tuple[str, ...]
    init_result_locators: tuple[str, ...]
    diagnostics: list[CanonicalizationDiagnostic]


@dataclass
class GitStatusSnapshot:
    command: list[str]
    stdout: str
    stderr: str
    returncode: int
    elapsed_ms: int


@dataclass
class CleanlinessReport:
    elapsed_ms: int
    before: GitStatusSnapshot
    after: GitStatusSnapshot


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
    if relative == INIT_RESULT_RELATIVE:
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
                payload[section] = dict(CANONICAL_DYNAMIC_SENTINEL)
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def init_result_locator(root: Path, repo_root: Path) -> str:
    return relative_to_root(root / INIT_RESULT_RELATIVE, repo_root)


def inspect_init_result_canonicalization(
    *,
    root: Path,
    repo_root: Path,
    target_label: str,
) -> tuple[tuple[str, ...], CanonicalizationDiagnostic | None]:
    locator = init_result_locator(root, repo_root)
    path = root / INIT_RESULT_RELATIVE
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return (), CanonicalizationDiagnostic(
            target_label=target_label,
            init_result_locator=locator,
            failure_label=CANONICALIZATION_INVALID_JSON_LABEL,
            failure_summary=f"invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}",
        )
    except OSError as exc:
        return (), CanonicalizationDiagnostic(
            target_label=target_label,
            init_result_locator=locator,
            failure_label=CANONICALIZATION_INCOMPLETE_LABEL,
            failure_summary=f"cannot read init-result JSON: {exc}",
        )

    if not isinstance(payload, dict):
        return (), CanonicalizationDiagnostic(
            target_label=target_label,
            init_result_locator=locator,
            failure_label=CANONICALIZATION_INVALID_SHAPE_LABEL,
            failure_summary="init-result JSON root must be an object",
        )

    present_sections = tuple(sorted(section for section in HOST_DYNAMIC_INIT_RESULT_SECTIONS if section in payload))
    missing_sections = tuple(sorted(HOST_DYNAMIC_INIT_RESULT_SECTIONS - set(present_sections)))
    if missing_sections:
        return present_sections, CanonicalizationDiagnostic(
            target_label=target_label,
            init_result_locator=locator,
            failure_label=CANONICALIZATION_INCOMPLETE_LABEL,
            failure_summary=f"missing host-dynamic section(s): {', '.join(missing_sections)}",
        )

    for section in present_sections:
        payload[section] = dict(CANONICAL_DYNAMIC_SENTINEL)
    incomplete_sections = tuple(
        section for section in present_sections if payload.get(section) != CANONICAL_DYNAMIC_SENTINEL
    )
    if incomplete_sections:
        return present_sections, CanonicalizationDiagnostic(
            target_label=target_label,
            init_result_locator=locator,
            failure_label=CANONICALIZATION_INCOMPLETE_LABEL,
            failure_summary=f"host-dynamic section(s) remained uncanonicalized: {', '.join(incomplete_sections)}",
        )

    return present_sections, None


def check_canonicalization(fixture: Path, generated: Path, repo_root: Path) -> CanonicalizationReport:
    started = time.perf_counter()
    diagnostics: list[CanonicalizationDiagnostic] = []
    canonicalized_sections: set[str] = set()
    init_result_locators = (
        init_result_locator(fixture, repo_root),
        init_result_locator(generated, repo_root),
    )
    for root, target_label in ((fixture, "stable-fixture"), (generated, "generated-fixture")):
        sections, diagnostic = inspect_init_result_canonicalization(
            root=root,
            repo_root=repo_root,
            target_label=target_label,
        )
        canonicalized_sections.update(sections)
        if diagnostic is not None:
            diagnostics.append(diagnostic)

    return CanonicalizationReport(
        elapsed_ms=int((time.perf_counter() - started) * 1000),
        canonicalized_sections=tuple(sorted(canonicalized_sections)),
        init_result_locators=init_result_locators,
        diagnostics=diagnostics,
    )


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


def tracked_status_command(repo_root: Path, fixture: Path) -> list[str]:
    return [
        "git",
        "status",
        "--short",
        "--untracked-files=no",
        "--",
        relative_to_root(fixture, repo_root),
    ]


def read_tracked_status(repo_root: Path, fixture: Path) -> GitStatusSnapshot:
    command = tracked_status_command(repo_root, fixture)
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return GitStatusSnapshot(
        command=command,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
    )


def check_cleanliness(repo_root: Path, fixture: Path, before: GitStatusSnapshot) -> CleanlinessReport:
    started = time.perf_counter()
    after = read_tracked_status(repo_root, fixture)
    return CleanlinessReport(
        elapsed_ms=before.elapsed_ms + int((time.perf_counter() - started) * 1000),
        before=before,
        after=after,
    )


def status_lines(snapshot: GitStatusSnapshot) -> tuple[str, ...]:
    return tuple(line for line in snapshot.stdout.splitlines() if line.strip())


def cleanliness_failure(report: CleanlinessReport) -> tuple[str, str]:
    if report.before.returncode != 0:
        return (
            CLEANLINESS_STATUS_FAILURE_LABEL,
            f"git status before validation exited with status {report.before.returncode}",
        )
    if report.after.returncode != 0:
        return (
            CLEANLINESS_STATUS_FAILURE_LABEL,
            f"git status after validation exited with status {report.after.returncode}",
        )
    before_lines = status_lines(report.before)
    if before_lines:
        return (
            CLEANLINESS_FAILURE_LABEL,
            f"examples/new-project tracked status was already dirty before validation: {len(before_lines)} path(s)",
        )
    after_lines = status_lines(report.after)
    if after_lines:
        return (
            CLEANLINESS_FAILURE_LABEL,
            f"examples/new-project tracked status changed after validation: {len(after_lines)} path(s)",
        )
    return "", ""


def cleanliness_evidence(report: CleanlinessReport, fixture: Path, repo_root: Path) -> dict[str, object]:
    return {
        "bucket_label": BUCKET_LABEL,
        "surface_label": CLEANLINESS_SURFACE_LABEL,
        "surface_kind": "named_surface",
        "scenario_label": CLEANLINESS_SCENARIO_LABEL,
        "command": CLEANLINESS_EVIDENCE_LOCATOR,
        "result": "pass",
        "elapsed_ms": report.elapsed_ms,
        "source_locator": relative_to_root(fixture, repo_root),
        "evidence_locator": CLEANLINESS_EVIDENCE_LOCATOR,
        "validator_mode": "demo-bootstrap-examples-cleanliness",
        "is_aggregate": "false",
        "status_scope": "tracked",
        "status_command": command_display(report.after.command, repo_root),
    }


def print_cleanliness_failure(report: CleanlinessReport, fixture: Path, repo_root: Path) -> None:
    failure_label, summary = cleanliness_failure(report)
    print("demo bootstrap examples/new-project cleanliness failed:", file=sys.stderr)
    for label, snapshot in (("before", report.before), ("after", report.after)):
        if snapshot.returncode != 0:
            print(f"- {label}: git status exited with status {snapshot.returncode}", file=sys.stderr)
            if snapshot.stderr.strip():
                print(snapshot.stderr, end="" if snapshot.stderr.endswith("\n") else "\n", file=sys.stderr)
        for line in status_lines(snapshot):
            print(f"- {label}: {line}", file=sys.stderr)
    print_surface_evidence(
        stream=sys.stderr,
        bucket_label=BUCKET_LABEL,
        surface_label=CLEANLINESS_SURFACE_LABEL,
        surface_kind="named_surface",
        scenario_label=CLEANLINESS_SCENARIO_LABEL,
        command=CLEANLINESS_EVIDENCE_LOCATOR,
        result="block",
        elapsed_ms=report.elapsed_ms,
        failure_label=failure_label,
        failure_taxonomy=failure_label,
        failure_summary=summary,
        source_locator=relative_to_root(fixture, repo_root),
        evidence_locator=CLEANLINESS_EVIDENCE_LOCATOR,
        validator_mode="demo-bootstrap-examples-cleanliness",
        is_aggregate="false",
        status_scope="tracked",
        status_command=command_display(report.after.command, repo_root),
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


def canonicalization_evidence(report: CanonicalizationReport, fixture: Path, repo_root: Path) -> dict[str, object]:
    return {
        "bucket_label": BUCKET_LABEL,
        "surface_label": CANONICALIZATION_SURFACE_LABEL,
        "surface_kind": "named_surface",
        "scenario_label": CANONICALIZATION_SCENARIO_LABEL,
        "command": CANONICALIZATION_EVIDENCE_LOCATOR,
        "result": "pass",
        "elapsed_ms": report.elapsed_ms,
        "source_locator": relative_to_root(fixture, repo_root),
        "evidence_locator": CANONICALIZATION_EVIDENCE_LOCATOR,
        "validator_mode": "demo-bootstrap-canonicalization",
        "is_aggregate": "false",
        "canonicalized_sections": ",".join(report.canonicalized_sections),
        "init_result_locators": ",".join(report.init_result_locators),
    }


def print_canonicalization_failure(report: CanonicalizationReport, fixture: Path, repo_root: Path) -> None:
    first_diagnostic = report.diagnostics[0]
    print("demo bootstrap canonicalization diagnostics failed:", file=sys.stderr)
    for diagnostic in report.diagnostics:
        print(
            f"- {diagnostic.target_label}: {diagnostic.failure_label}: "
            f"{diagnostic.failure_summary} ({diagnostic.init_result_locator})",
            file=sys.stderr,
        )
    print_surface_evidence(
        stream=sys.stderr,
        bucket_label=BUCKET_LABEL,
        surface_label=CANONICALIZATION_SURFACE_LABEL,
        surface_kind="named_surface",
        scenario_label=CANONICALIZATION_SCENARIO_LABEL,
        command=CANONICALIZATION_EVIDENCE_LOCATOR,
        result="block",
        elapsed_ms=report.elapsed_ms,
        failure_label=first_diagnostic.failure_label,
        failure_taxonomy=first_diagnostic.failure_label,
        failure_summary=f"{len(report.diagnostics)} canonicalization diagnostic(s)",
        source_locator=relative_to_root(fixture, repo_root),
        evidence_locator=CANONICALIZATION_EVIDENCE_LOCATOR,
        validator_mode="demo-bootstrap-canonicalization",
        is_aggregate="false",
        canonicalized_sections=",".join(report.canonicalized_sections),
        diagnostic_locators=",".join(diagnostic.init_result_locator for diagnostic in report.diagnostics),
    )


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
    needs_cleanliness = args.surface in ("aggregate", "cleanliness")
    cleanliness_before = read_tracked_status(repo_root, fixture) if needs_cleanliness else None

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

        canonicalization = check_canonicalization(fixture, generated, repo_root)
        if canonicalization.diagnostics:
            print_canonicalization_failure(canonicalization, fixture, repo_root)
            return 1

        canonicalization_pass_evidence = canonicalization_evidence(canonicalization, fixture, repo_root)
        if args.surface == "canonicalization":
            print_surface_evidence(stream=sys.stdout, **canonicalization_pass_evidence)
            print(f"demo bootstrap canonicalization: OK ({fixture.relative_to(repo_root)})")
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

        cleanliness_report = (
            check_cleanliness(repo_root, fixture, cleanliness_before)
            if cleanliness_before is not None
            else None
        )
        if cleanliness_report is not None:
            failure_label, _summary = cleanliness_failure(cleanliness_report)
            if failure_label:
                print_cleanliness_failure(cleanliness_report, fixture, repo_root)
                return 1
            cleanliness_pass_evidence = cleanliness_evidence(cleanliness_report, fixture, repo_root)
            if args.surface == "cleanliness":
                print_surface_evidence(stream=sys.stdout, **cleanliness_pass_evidence)
                print(f"demo bootstrap examples/new-project cleanliness: OK ({fixture.relative_to(repo_root)})")
                return 0
        else:
            cleanliness_pass_evidence = None

        if args.show_surface_evidence:
            print_surface_evidence(stream=sys.stdout, **generation_evidence)
            print_surface_evidence(stream=sys.stdout, **canonicalization_pass_evidence)
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
            if cleanliness_pass_evidence is not None:
                print_surface_evidence(stream=sys.stdout, **cleanliness_pass_evidence)
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
                    subsurface_count=4 if cleanliness_pass_evidence is not None else 3,
                    subsurface_results=(
                        f"{GENERATION_SURFACE_LABEL}:pass,"
                        f"{CANONICALIZATION_SURFACE_LABEL}:pass,"
                        f"{DRIFT_SURFACE_LABEL}:pass"
                        + (
                            f",{CLEANLINESS_SURFACE_LABEL}:pass"
                            if cleanliness_pass_evidence is not None
                            else ""
                        )
                    ),
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
        choices=("aggregate", "generation", "canonicalization", "fixture-drift", "cleanliness"),
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
