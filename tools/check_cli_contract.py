#!/usr/bin/env python3
"""Contract checks for the CLI-first Loom surface."""

from __future__ import annotations

import json
import argparse
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
LOOM = REPO_ROOT / "tools" / "loom.py"
LEGACY_FIXTURES = REPO_ROOT / "docs" / "evidence" / "fixtures" / "legacy-migration-validation-fixtures.json"
RELEASE_READBACK_FIXTURES = REPO_ROOT / "docs" / "evidence" / "fixtures" / "release-readback-fixtures.json"
CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS = 60

SCAFFOLD_FORBIDDEN_TRUTH_SURFACES = (
    ".loom/work-items/WI-truth.md",
    ".loom/progress/WI-truth.md",
    ".loom/status/current.md",
    ".loom/reviews/WI-truth.json",
    ".loom/reviews/WI-truth.spec.json",
    ".loom/runtime/attempts/WI-truth/latest.json",
    ".loom/runtime/review/WI-truth/head/context-pack.json",
    ".loom/shadow/review-loom.json",
    ".loom/shadow/merge-ready-loom.json",
    ".loom/shadow/closeout-loom.json",
    ".loom/specs/WI-truth/evidence-map.md",
    ".loom/specs/WI-truth/consistency-analysis.md",
    ".loom/specs/WI-truth/task-carrier.md",
    ".loom/tasks/WI-truth.md",
    "tasks.md",
    "skills/registry.json",
    "skills/loom-init/SKILL.md",
    "src/skills/route-matrix.md",
    "plugins/loom/.codex-plugin/plugin.json",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/loom.yml",
)

SCAFFOLD_FORBIDDEN_ACTION_KEYS = {
    "closeout_actions",
    "closeout_result",
    "generated_skills",
    "host_actions",
    "issue_actions",
    "managed_writes",
    "merge_ready_result",
    "pr_actions",
    "project_actions",
    "review_record",
    "review_verdict",
}

REQUIRED_COMMANDS = {
    "version",
    "help",
    "installed-state show",
    "installed-state validate",
    "installed-state export",
    "detect",
    "doctor",
    "repair plan",
    "repair apply",
    "install",
    "upgrade-plan",
    "upgrade",
    "rollback",
    "verify",
    "init",
    "adopt",
    "route",
    "carrier closeout-sync",
    "status",
    "fact-chain",
    "profile status",
    "profile upgrade-plan",
    "profile upgrade",
    "checkpoint admission",
    "checkpoint build",
    "checkpoint merge",
    "gate pre-review",
    "gate spec-review",
    "gate review",
    "gate pr",
    "gate merge",
    "gate freeze check",
    "gate freeze write",
    "gate closeout",
    "release readback",
    "release resume",
    "closeout run",
    "host list",
    "host doctor",
    "host install",
    "host verify",
    "host register",
    "host upgrade",
    "host remove",
    "workspace create",
    "workspace locate",
    "workspace check",
    "workspace audit",
    "workspace retire",
    "issue inspect",
    "issue bind",
    "issue reconcile",
    "project status",
    "project reconcile",
    "pr inspect",
    "pr metadata-render",
    "pr metadata-readback",
    "pr metadata-update",
    "pr metadata-preflight",
    "pr gate",
    "merge check",
    "merge run",
    "ship",
    "reconcile",
    "skills list",
    "skills generate",
    "skills check",
    "skills doctor",
    "skills package",
    "skills release-check",
    "suite inspect",
    "suite scaffold",
    "suite validate",
    "suite evidence inspect",
    "suite evidence scaffold",
    "suite evidence validate",
    "suite carrier inspect",
    "suite carrier validate",
}


@dataclass(frozen=True)
class SurfaceCheck:
    name: str
    fixture_group: str
    run: Callable[[], None]


def format_duration(seconds: float) -> str:
    return f"{seconds:.2f}s"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Loom CLI contract checks.",
    )
    parser.add_argument(
        "--surface",
        action="append",
        dest="surfaces",
        help="Run only the named surface. May be passed more than once.",
    )
    parser.add_argument(
        "--fixture-group",
        action="append",
        dest="fixture_groups",
        help="Run only checks in the named fixture group. May be passed more than once.",
    )
    parser.add_argument(
        "--list-surfaces",
        action="store_true",
        help="List available surface names and fixture groups without running checks.",
    )
    return parser.parse_args(argv)


def selected_surface_checks(
    checks: tuple[SurfaceCheck, ...],
    *,
    surfaces: list[str] | None,
    fixture_groups: list[str] | None,
) -> tuple[SurfaceCheck, ...]:
    selected = checks
    if surfaces:
        wanted = set(surfaces)
        selected = tuple(check for check in selected if check.name in wanted)
        missing = wanted - {check.name for check in checks}
        if missing:
            raise ValueError("unknown surface(s): " + ", ".join(sorted(missing)))
    if fixture_groups:
        wanted_groups = set(fixture_groups)
        selected = tuple(check for check in selected if check.fixture_group in wanted_groups)
        missing_groups = wanted_groups - {check.fixture_group for check in checks}
        if missing_groups:
            raise ValueError("unknown fixture group(s): " + ", ".join(sorted(missing_groups)))
    if not selected:
        raise ValueError("surface filters selected no checks")
    return selected


def run_surface_checks(checks: tuple[SurfaceCheck, ...]) -> int:
    failures: list[tuple[SurfaceCheck, float, Exception]] = []
    suite_start = time.perf_counter()
    total = len(checks)
    for index, check in enumerate(checks, start=1):
        start = time.perf_counter()
        print(
            f"[{index}/{total}] surface={check.name} fixture_group={check.fixture_group} start",
            file=sys.stderr,
        )
        try:
            check.run()
        except Exception as exc:
            elapsed = time.perf_counter() - start
            failures.append((check, elapsed, exc))
            print(
                f"[{index}/{total}] surface={check.name} fixture_group={check.fixture_group} failed in {format_duration(elapsed)}",
                file=sys.stderr,
            )
        else:
            elapsed = time.perf_counter() - start
            print(
                f"[{index}/{total}] surface={check.name} fixture_group={check.fixture_group} passed in {format_duration(elapsed)}",
                file=sys.stderr,
            )

    total_elapsed = time.perf_counter() - suite_start
    if failures:
        print("cli contract failures:", file=sys.stderr)
        for check, elapsed, exc in failures:
            print(
                f"- surface={check.name} fixture_group={check.fixture_group} duration={format_duration(elapsed)}: {exc}",
                file=sys.stderr,
            )
        print(f"cli contract checks failed in {format_duration(total_elapsed)}", file=sys.stderr)
        return 1
    print(f"cli contract surfaces passed in {format_duration(total_elapsed)}", file=sys.stderr)
    return 0


def run_json(args: list[str], *, expect: int | None = None, env_overrides: dict[str, str] | None = None) -> tuple[int, dict[str, Any]]:
    if args[:2] == ["skills", "check"]:
        for cache_dir in REPO_ROOT.rglob("__pycache__"):
            shutil.rmtree(cache_dir)
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("LOOM_SKIP_NPM_LATEST", "1")
    try:
        completed = subprocess.run(
            [sys.executable, str(LOOM), *args],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(
            f"{args} timed out after {CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS}s\n"
            f"{exc.stderr or ''}\n{exc.stdout or ''}"
        ) from exc
    if expect is not None and completed.returncode != expect:
        raise AssertionError(f"{args} returned {completed.returncode}, expected {expect}\n{completed.stderr}\n{completed.stdout}")
    raw = completed.stdout or completed.stderr
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{args} did not emit JSON: {exc}\n{raw}") from exc
    return completed.returncode, payload


def runtime_payload_from_agent_safe_output(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("envelope_schema") != "loom-agent-output-envelope/v1":
        return payload
    full_output = payload.get("full_output")
    locator = full_output.get("artifact_locator") if isinstance(full_output, dict) else None
    if not isinstance(locator, str) or not locator.strip():
        raise AssertionError("agent-safe output envelope did not expose full output artifact locator")
    path = Path(locator)
    if not path.is_absolute():
        path = REPO_ROOT / path
    artifact = json.loads(path.read_text(encoding="utf-8"))
    runtime_payload = artifact.get("payload")
    if not isinstance(runtime_payload, dict):
        raise AssertionError("agent-safe full output artifact did not contain a runtime payload")
    return runtime_payload


def run_flow_json(args: list[str], *, cwd: Path = REPO_ROOT, expect: int | None = None) -> tuple[int, dict[str, Any]]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "loom_flow.py"), *args],
            cwd=cwd,
            env=env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(
            f"loom_flow.py {args} timed out after {CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS}s\n"
            f"{exc.stderr or ''}\n{exc.stdout or ''}"
        ) from exc
    if expect is not None and completed.returncode != expect:
        raise AssertionError(f"loom_flow.py {args} returned {completed.returncode}, expected {expect}\n{completed.stderr}\n{completed.stdout}")
    raw = completed.stdout or completed.stderr
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"loom_flow.py {args} did not emit JSON: {exc}\n{raw}") from exc
    return completed.returncode, payload


def assert_repo_local_closeout_runtime_argument_contract() -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / ".loom" / "bin" / "loom_flow.py"), "closeout", "check", "--help"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise AssertionError(f"repo-local closeout runtime help failed\n{completed.stderr}\n{completed.stdout}")
    help_text = completed.stdout + completed.stderr
    if "--item" not in help_text:
        raise AssertionError("repo-local closeout runtime must accept --item for wrapper/runtime contract parity")
    for flag in ("--implementation-pr", "--release-pr", "--carrier-sync-pr", "--final-closeout-pr", "--pr-role"):
        if flag not in help_text:
            raise AssertionError(f"repo-local closeout runtime must accept {flag} for PR role contract parity")


def assert_merge_wrapper_pr_argument_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for merge wrapper regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    captured: dict[str, Any] = {}

    def fake_emit_flow(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> int:
        captured.clear()
        captured["command"] = command
        captured["flow_args"] = flow_args
        captured["fallback_to"] = fallback_to
        return 0

    original_emit_flow = module.emit_flow
    module.emit_flow = fake_emit_flow
    try:
        for action, runtime_action in (("check", "check"), ("run", "merge")):
            args = [
                action,
                "1288",
                "--work-item",
                "WI-1287",
                "--head-sha",
                "fixture-head",
                "--merge-method",
                "squash",
            ]
            if action == "run":
                args.append("--apply")
            status = module.handle_merge(args)
            if status != 0:
                raise AssertionError(f"merge {action} wrapper regression did not complete")
            if captured.get("command") != f"merge {action}":
                raise AssertionError(f"merge {action} wrapper did not preserve command label")
            flow_args = captured.get("flow_args")
            if not isinstance(flow_args, list):
                raise AssertionError(f"merge {action} wrapper did not delegate to controlled-merge")
            if flow_args[:2] != ["controlled-merge", runtime_action]:
                raise AssertionError(f"merge {action} wrapper delegated to the wrong runtime operation")
            try:
                pr_index = flow_args.index("--pr")
            except ValueError as exc:
                raise AssertionError(f"merge {action} wrapper did not pass --pr to controlled-merge") from exc
            if flow_args[pr_index + 1] != "1288":
                raise AssertionError(f"merge {action} wrapper passed the subcommand placeholder instead of the PR number")
            if "pr" in flow_args:
                raise AssertionError(f"merge {action} wrapper leaked the literal `pr` placeholder to controlled-merge")
            if "--merge-method" not in flow_args or flow_args[flow_args.index("--merge-method") + 1] != "squash":
                raise AssertionError(f"merge {action} wrapper did not preserve merge method")
            if action == "run" and "--execute" not in flow_args:
                raise AssertionError("merge run --apply did not delegate to controlled-merge --execute")
        try:
            module.handle_merge(["check", "pr"])
        except SystemExit as exc:
            if exc.code == 0:
                raise AssertionError("merge wrapper accepted literal `pr` as a PR number")
        else:
            raise AssertionError("merge wrapper accepted literal `pr` as a PR number")
    finally:
        module.emit_flow = original_emit_flow


def assert_merge_closeout_run_wrapper_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for merge closeout-run regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []
    closeout_calls: list[argparse.Namespace] = []
    emitted: dict[str, Any] = {}

    def fake_emit(payload: dict[str, Any], *, stream: Any | None = None) -> int:
        emitted.clear()
        emitted.update(payload)
        return 0 if payload.get("result") == "pass" else 1

    def passing_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        calls.append(flow_args)
        if flow_args[:2] != ["controlled-merge", "merge"]:
            raise AssertionError(f"merge --closeout-run delegated unexpected flow args: {flow_args}")
        if "--execute" not in flow_args:
            raise AssertionError("merge --closeout-run must execute controlled merge")
        return {
            "command": "controlled-merge",
            "result": "pass",
            "summary": "merged",
            "pr": {
                "number": 1707,
                "state": "MERGED",
                "baseRefName": "main",
                "mergeCommit": {"oid": "fixture-merge-sha"},
            },
        }

    def fake_closeout_payload(args: argparse.Namespace, target: Path) -> dict[str, Any]:
        closeout_calls.append(args)
        if args.item != "WI-1692" or args.issue != "1692" or args.pr != "1707":
            raise AssertionError("merge --closeout-run did not preserve Work Item, issue, and PR bindings")
        if args.branch != "main":
            raise AssertionError("merge --closeout-run did not pass the closeout target branch")
        if args.apply is not True:
            raise AssertionError("merge --closeout-run must apply the closeout run after merge")
        return {
            "command": "closeout run",
            "schema_version": "loom-closeout-run/v1",
            "result": "pass",
            "summary": "closeout complete",
            "issue": {"number": "1692", "state": "CLOSED"},
            "pr": {"number": "1707", "state": "MERGED"},
            "terminal_metadata": {
                "terminal_state": "closed_out",
                "issue": "1692",
                "pr": "1707",
                "merge_commit": "fixture-merge-sha",
                "target_branch": "main",
                "closed_at": "fixture-closed-at",
                "evidence_locator": "host-readback",
            },
            "evidence_locators": ["host-readback"],
        }

    original_flow_payload = module.flow_payload
    original_closeout_payload = module.run_closeout_payload
    original_emit = module.emit
    module.flow_payload = passing_flow_payload
    module.run_closeout_payload = fake_closeout_payload
    module.emit = fake_emit
    try:
        status = module.handle_merge(
            [
                "run",
                "1707",
                "--work-item",
                "WI-1692",
                "--issue",
                "1692",
                "--target-branch",
                "main",
                "--head-sha",
                "fixture-head",
                "--merge-method",
                "squash",
                "--apply",
                "--closeout-run",
                "--json",
            ]
        )
        if status != 0 or emitted.get("result") != "pass":
            raise AssertionError("merge --closeout-run did not emit a passing payload")
        if [call[:2] for call in calls] != [["controlled-merge", "merge"]]:
            raise AssertionError("merge --closeout-run should only call controlled merge before closeout")
        if len(closeout_calls) != 1:
            raise AssertionError("merge --closeout-run did not run closeout exactly once after merge pass")
        if emitted.get("schema_version") != "loom-merge-run/v1":
            raise AssertionError("merge --closeout-run must expose the merge-run schema")
        if emitted.get("closeout_run") is not True or emitted.get("creates_closeout_pr") is not False:
            raise AssertionError("merge --closeout-run must be explicit and must not create a closeout PR")
        if emitted.get("closeout_mode") != "inline":
            raise AssertionError("merge --closeout-run must report inline closeout mode")
        if [step.get("name") for step in emitted.get("steps", [])] != ["controlled-merge-apply", "closeout-run"]:
            raise AssertionError("merge --closeout-run emitted an unexpected step sequence")

        def host_only_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
            calls.append(flow_args)
            if flow_args[:2] == ["controlled-merge", "merge"]:
                return {
                    "command": "controlled-merge",
                    "result": "pass",
                    "summary": "merged",
                    "pr": {"number": 1707, "state": "MERGED", "baseRefName": "main"},
                }
            if flow_args[:2] == ["reconciliation", "sync"]:
                if "--apply" not in flow_args:
                    raise AssertionError("host-only closeout must apply reconciliation after merge")
                return {"command": "reconciliation", "result": "pass", "summary": "issue closed"}
            if flow_args[:2] == ["closeout", "check"]:
                return {
                    "command": "closeout",
                    "result": "pass",
                    "summary": "host closeout pass",
                    "issue": {"number": "1692", "state": "CLOSED"},
                    "pr": {"number": "1707", "state": "MERGED"},
                }
            raise AssertionError(f"host-only merge closeout delegated unexpected flow args: {flow_args}")

        def fail_if_closeout_run(args: argparse.Namespace, target: Path) -> dict[str, Any]:
            raise AssertionError("host-only closeout mode must not run carrier closeout-run")

        module.flow_payload = host_only_flow_payload
        module.run_closeout_payload = fail_if_closeout_run
        calls.clear()
        closeout_calls.clear()
        emitted.clear()
        status = module.handle_merge(
            [
                "run",
                "1707",
                "--work-item",
                "WI-1692",
                "--issue",
                "1692",
                "--target-branch",
                "main",
                "--apply",
                "--closeout-run",
                "--closeout-mode",
                "host_only",
                "--json",
            ]
        )
        if status != 0 or emitted.get("result") != "pass":
            raise AssertionError("merge --closeout-run host_only did not pass")
        if [call[:2] for call in calls] != [["controlled-merge", "merge"], ["reconciliation", "sync"], ["closeout", "check"]]:
            raise AssertionError("merge --closeout-run host_only did not preserve host-only closeout sequence")
        if emitted.get("closeout_mode") != "host_only" or emitted.get("creates_closeout_pr") is not False:
            raise AssertionError("merge --closeout-run host_only must not create a closeout PR")

        module.flow_payload = passing_flow_payload
        module.run_closeout_payload = fake_closeout_payload
        calls.clear()
        closeout_calls.clear()
        emitted.clear()
        status = module.handle_merge(
            [
                "run",
                "1707",
                "--work-item",
                "WI-1692",
                "--issue",
                "1692",
                "--target-branch",
                "main",
                "--apply",
                "--closeout-run",
                "--closeout-mode",
                "full_closeout_pr",
                "--json",
                "--full-output",
            ]
        )
        if status == 0 or emitted.get("result") != "block":
            raise AssertionError("merge --closeout-run must block full_closeout_pr before merge")
        if calls or closeout_calls:
            raise AssertionError("merge --closeout-run full_closeout_pr must not merge or run closeout")
        if emitted.get("closeout_mode") != "full_closeout_pr" or emitted.get("creates_closeout_pr") is not False:
            raise AssertionError("merge --closeout-run full_closeout_pr must fail closed without creating a PR")

        def blocking_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
            calls.append(flow_args)
            return {"command": "controlled-merge", "result": "block", "summary": "merge blocked", "missing_inputs": ["required check pending"]}

        module.flow_payload = blocking_flow_payload
        module.run_closeout_payload = fake_closeout_payload
        calls.clear()
        closeout_calls.clear()
        emitted.clear()
        status = module.handle_merge(
            [
                "run",
                "1707",
                "--work-item",
                "WI-1692",
                "--issue",
                "1692",
                "--target-branch",
                "main",
                "--apply",
                "--closeout-run",
                "--json",
            ]
        )
        if status == 0 or emitted.get("result") != "block":
            raise AssertionError("merge --closeout-run must block when controlled merge blocks")
        if closeout_calls:
            raise AssertionError("merge --closeout-run must not run closeout after controlled merge block")
    finally:
        module.flow_payload = original_flow_payload
        module.run_closeout_payload = original_closeout_payload
        module.emit = original_emit


def assert_ship_dry_run_wrapper_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for ship wrapper regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []
    emitted: dict[str, Any] = {}

    def fake_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        calls.append(flow_args)
        if flow_args[:2] == ["pr-metadata", "preflight"]:
            return {
                "command": "pr-metadata",
                "result": "pass",
                "summary": "metadata ok",
                "governance_intensity_carrier": {
                    "envelope": {
                        "fields": {
                            "governance_intensity": "light",
                            "change_class": "docs_governance",
                            "release_judgment": "no_release",
                            "upgrade_triggers": [],
                        }
                    }
                },
            }
        if flow_args[:2] == ["pr-gate", "check"]:
            return {"command": "pr-gate", "result": "pass", "summary": "pr gate ok"}
        if flow_args[:2] == ["controlled-merge", "check"]:
            return {"command": "controlled-merge", "result": "pass", "summary": "merge check ok"}
        raise AssertionError(f"ship dry-run delegated unexpected flow args: {flow_args}")

    def fake_emit(payload: dict[str, Any], *, stream: Any | None = None) -> int:
        emitted.clear()
        emitted.update(payload)
        return 0 if payload.get("result") == "pass" else 1

    original_flow_payload = module.flow_payload
    original_emit = module.emit
    module.flow_payload = fake_flow_payload
    module.emit = fake_emit
    try:
        status = module.handle_ship([
            "--item",
            "WI-1690",
            "--issue",
            "1690",
            "--pr",
            "1704",
            "--branch",
            "work/1690-ship-dry-run",
            "--head-sha",
            "a" * 40,
            "--intensity",
            "auto",
            "--json",
        ])
        if status != 0 or emitted.get("result") != "pass":
            raise AssertionError("ship dry-run wrapper did not emit a passing dry-run plan")
        if emitted.get("schema_version") != "loom-ship/v1" or emitted.get("mutates") is not False:
            raise AssertionError("ship dry-run must emit loom-ship/v1 and remain non-mutating")
        if emitted.get("next_action") != "run loom ship --apply after dry-run blockers are clear":
            raise AssertionError("ship dry-run must keep the short next_action for the ordinary apply path")
        expected_prefixes = [
            ["pr-metadata", "preflight"],
            ["pr-gate", "check"],
            ["controlled-merge", "check"],
        ]
        if [call[:2] for call in calls] != expected_prefixes:
            raise AssertionError("ship dry-run did not preserve the expected read-only gate sequence")
        flattened = [token for call in calls for token in call]
        if "--execute" in flattened or "--apply" in flattened:
            raise AssertionError("ship dry-run delegated a mutating runtime flag")
        policy = emitted.get("closeout_policy", {})
        if policy.get("policy") != "host_only" or policy.get("creates_closeout_pr_by_default") is not False:
            raise AssertionError("ship dry-run did not consume light closeout policy")
        if not any(step.get("name") == "post-merge-closeout" and step.get("result") == "skipped" for step in emitted.get("steps", [])):
            raise AssertionError("ship dry-run must plan post-merge closeout without executing it")

    finally:
        module.flow_payload = original_flow_payload
        module.emit = original_emit


def assert_ship_infers_pr_bindings_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for ship inference regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []
    emitted: dict[str, Any] = {}
    inferred_branch = "work/1738-ship-inference"
    inferred_head = "f" * 40

    def fake_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        calls.append(flow_args)
        if tuple(flow_args[:2]) in {("pr-metadata", "preflight"), ("pr-gate", "check"), ("controlled-merge", "check")}:
            if "--branch" in flow_args and flow_args[flow_args.index("--branch") + 1] != inferred_branch:
                raise AssertionError("ship did not pass inferred branch to delegated gate")
            if "--head-sha" not in flow_args or flow_args[flow_args.index("--head-sha") + 1] != inferred_head:
                raise AssertionError("ship did not pass inferred head SHA to delegated gate")
        if flow_args[:2] == ["pr-metadata", "preflight"]:
            return {
                "command": "pr-metadata",
                "result": "pass",
                "summary": "metadata ok",
                "governance_intensity_carrier": {
                    "envelope": {
                        "fields": {
                            "governance_intensity": "light",
                            "change_class": "docs_governance",
                            "release_judgment": "no_release",
                            "upgrade_triggers": [],
                        }
                    }
                },
            }
        if flow_args[:2] == ["pr-gate", "check"]:
            return {"command": "pr-gate", "result": "pass", "summary": "pr gate ok"}
        if flow_args[:2] == ["controlled-merge", "check"]:
            return {"command": "controlled-merge", "result": "pass", "summary": "merge check ok", "pr": {"baseRefName": "main"}}
        raise AssertionError(f"ship inference delegated unexpected flow args: {flow_args}")

    def fake_emit(payload: dict[str, Any], *, stream: Any | None = None) -> int:
        emitted.clear()
        emitted.update(payload)
        return 0 if payload.get("result") == "pass" else 1

    def fake_ship_pr_payload(args: Any, target: Any) -> tuple[dict[str, Any], list[str]]:
        return {"headRefName": inferred_branch, "headRefOid": inferred_head, "baseRefName": "main"}, []

    original_flow_payload = module.flow_payload
    original_emit = module.emit
    original_ship_pr_payload = module.ship_pr_payload
    original_git_branch = module.git_branch_for_target
    original_git_head = module.git_head_sha_for_target
    module.flow_payload = fake_flow_payload
    module.emit = fake_emit
    module.ship_pr_payload = fake_ship_pr_payload
    module.git_branch_for_target = lambda target: "work/local-checkout"
    module.git_head_sha_for_target = lambda target: "e" * 40
    try:
        status = module.handle_ship(["--item", "WI-1738", "--pr", "1748", "--json"])
        if status != 0 or emitted.get("result") != "pass":
            raise AssertionError("ship dry-run did not pass with inferred PR bindings")
        binding = emitted.get("binding_inference", {})
        bindings = binding.get("bindings", {}) if isinstance(binding, dict) else {}
        if bindings.get("branch") != inferred_branch or bindings.get("head_sha") != inferred_head or bindings.get("target_branch") != "main":
            raise AssertionError("ship did not expose inferred branch/head/target_branch bindings")
        inferred_fields = {entry.get("field") for entry in binding.get("inferences", []) if isinstance(entry, dict)}
        if {"branch", "head_sha", "target_branch"} - inferred_fields:
            raise AssertionError("ship inference did not record inferred binding fields")
    finally:
        module.flow_payload = original_flow_payload
        module.emit = original_emit
        module.ship_pr_payload = original_ship_pr_payload
        module.git_branch_for_target = original_git_branch
        module.git_head_sha_for_target = original_git_head


def assert_ship_pr_readback_uses_api_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for ship PR readback regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []

    def fake_run_capture(args: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        payload = {
            "number": 1762,
            "state": "OPEN",
            "headRefName": "work/1738-ship-inference",
            "headRefOid": "a" * 40,
            "baseRefName": "main",
            "body": "PR body",
            "url": "https://github.com/MC-and-his-Agents/Loom/pull/1762",
        }
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=json.dumps(payload), stderr="")

    original_run_capture = module.run_capture
    original_infer_github_repo = module.infer_github_repo
    module.run_capture = fake_run_capture
    module.infer_github_repo = lambda target: "MC-and-his-Agents/Loom"
    try:
        args = argparse.Namespace(pr=1762, pr_payload_file=None, owner=None, repo_name=None)
        payload, errors = module.ship_pr_payload(args, REPO_ROOT)
        if errors or payload is None:
            raise AssertionError(f"ship PR readback should pass with gh api payload, got errors={errors}")
        if payload.get("headRefName") != "work/1738-ship-inference" or payload.get("headRefOid") != "a" * 40:
            raise AssertionError("ship PR readback must preserve normalized branch/head fields")
        if not calls or calls[0][:3] != ["gh", "api", "repos/MC-and-his-Agents/Loom/pulls/1762"]:
            raise AssertionError(f"ship PR readback must use gh api pull request endpoint, got {calls}")
        if any("pr" in part and "view" in part for part in calls[0]):
            raise AssertionError("ship PR readback must not use the high-frequency PR view shortcut")
    finally:
        module.run_capture = original_run_capture
        module.infer_github_repo = original_infer_github_repo


def assert_ship_apply_wrapper_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for ship apply wrapper regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []
    emitted: dict[str, Any] = {}

    def passing_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        calls.append(flow_args)
        if flow_args[:2] == ["pr-metadata", "update"]:
            if "--apply" not in flow_args:
                raise AssertionError("ship --apply safe metadata repair must apply PR metadata update")
            return {"command": "pr-metadata", "result": "pass", "summary": "metadata repaired"}
        if flow_args[:2] == ["pr-metadata", "preflight"]:
            return {
                "command": "pr-metadata",
                "result": "pass",
                "summary": "metadata ok",
                "governance_intensity_carrier": {
                    "envelope": {
                        "fields": {
                            "governance_intensity": "light",
                            "change_class": "docs_governance",
                            "release_judgment": "no_release",
                            "upgrade_triggers": [],
                        }
                    }
                },
            }
        if flow_args[:2] == ["pr-gate", "check"]:
            return {"command": "pr-gate", "result": "pass", "summary": "pr gate ok"}
        if flow_args[:2] == ["controlled-merge", "check"]:
            return {"command": "controlled-merge", "result": "pass", "summary": "merge check ok", "pr": {"baseRefName": "main"}}
        if flow_args[:2] == ["controlled-merge", "merge"]:
            if "--execute" not in flow_args:
                raise AssertionError("ship --apply must execute controlled merge with --execute")
            if "--apply" in flow_args:
                raise AssertionError("ship --apply must not pass --apply to controlled merge runtime")
            return {
                "command": "controlled-merge",
                "result": "pass",
                "summary": "merged",
                "pr": {
                    "number": 1706,
                    "state": "MERGED",
                    "baseRefName": "main",
                    "mergeCommit": {"oid": "fixture-merge-sha"},
                },
            }
        if flow_args[:2] == ["reconciliation", "sync"]:
            if "--apply" not in flow_args:
                raise AssertionError("ship --apply must apply host reconciliation after merge")
            return {"command": "reconciliation", "result": "pass", "summary": "issue closed"}
        if flow_args[:2] == ["closeout", "check"]:
            return {
                "command": "closeout",
                "result": "pass",
                "summary": "closeout pass",
                "issue": {"number": 1691, "state": "CLOSED"},
                "pr": {"number": 1706, "state": "MERGED", "baseRefName": "main", "mergeCommit": {"oid": "fixture-merge-sha"}},
            }
        raise AssertionError(f"ship apply delegated unexpected flow args: {flow_args}")

    def fake_emit(payload: dict[str, Any], *, stream: Any | None = None) -> int:
        emitted.clear()
        emitted.update(payload)
        return 0 if payload.get("result") == "pass" else 1

    original_flow_payload = module.flow_payload
    original_emit = module.emit
    original_ship_pr_payload = module.ship_pr_payload
    module.flow_payload = passing_flow_payload
    module.emit = fake_emit
    module.ship_pr_payload = lambda args, target: ({"headRefName": args.branch, "headRefOid": args.head_sha, "baseRefName": "main"}, [])
    try:
        status = module.handle_ship(
            [
                "--item",
                "WI-1691",
                "--issue",
                "1691",
                "--pr",
                "1706",
                "--branch",
                "work/1691-ship-apply",
                "--head-sha",
                "b" * 40,
                "--merge-method",
                "squash",
                "--apply",
                "--json",
            ]
        )
        if status != 0 or emitted.get("result") != "pass":
            raise AssertionError("ship --apply wrapper did not emit a passing apply result")
        if emitted.get("schema_version") != "loom-ship/v1" or emitted.get("mutates") is not True or emitted.get("dry_run") is not False:
            raise AssertionError("ship --apply must emit mutating loom-ship/v1 apply payload")
        if emitted.get("creates_closeout_pr") is not False or emitted.get("closeout_mode") != "host_only":
            raise AssertionError("ship --apply must default to host-only closeout without creating a closeout PR")
        expected_prefixes = [
            ["pr-metadata", "update"],
            ["pr-metadata", "preflight"],
            ["pr-gate", "check"],
            ["controlled-merge", "check"],
            ["controlled-merge", "merge"],
            ["reconciliation", "sync"],
            ["closeout", "check"],
        ]
        if [call[:2] for call in calls] != expected_prefixes:
            raise AssertionError(f"ship --apply delegated unexpected sequence: {[call[:2] for call in calls]}")
        merge_call = calls[4]
        if "--merge-method" not in merge_call or merge_call[merge_call.index("--merge-method") + 1] != "squash":
            raise AssertionError("ship --apply did not preserve merge method")
        reconciliation_call = calls[5]
        for flag, expected in {"--item": "WI-1691", "--issue": "1691", "--pr": "1706", "--branch": "main"}.items():
            if flag not in reconciliation_call or reconciliation_call[reconciliation_call.index(flag) + 1] != expected:
                raise AssertionError(f"ship --apply did not preserve {flag} for host closeout")

        def blocking_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
            calls.append(flow_args)
            if flow_args[:2] == ["pr-metadata", "update"]:
                return {"command": "pr-metadata", "result": "pass"}
            if flow_args[:2] == ["pr-metadata", "preflight"]:
                return {
                    "command": "pr-metadata",
                    "result": "pass",
                    "governance_intensity_carrier": {
                        "envelope": {
                            "fields": {
                                "governance_intensity": "light",
                                "change_class": "docs_governance",
                                "release_judgment": "no_release",
                                "upgrade_triggers": [],
                            }
                        }
                    },
                }
            if flow_args[:2] == ["pr-gate", "check"]:
                return {"command": "pr-gate", "result": "block", "summary": "review missing", "missing_inputs": ["review record missing"]}
            if flow_args[:2] == ["controlled-merge", "check"]:
                return {"command": "controlled-merge", "result": "pass", "summary": "merge check ok", "pr": {"baseRefName": "main"}}
            raise AssertionError(f"ship --apply should stop before mutating merge or closeout after PR gate block: {flow_args}")

        module.flow_payload = blocking_flow_payload
        calls.clear()
        emitted.clear()
        status = module.handle_ship(
            [
                "--item",
                "WI-1691",
                "--issue",
                "1691",
                "--pr",
                "1706",
                "--branch",
                "work/1691-ship-apply",
                "--head-sha",
                "b" * 40,
                "--apply",
                "--json",
            ]
        )
        if status == 0 or emitted.get("result") != "block":
            raise AssertionError("ship --apply gate blocker must emit block")
        if emitted.get("schema_version") != "loom-cli-output/v1":
            raise AssertionError("ship --apply blocker must stay within the agent-safe summary envelope")
        if emitted.get("key_gaps") != ["review record missing"]:
            raise AssertionError("ship --apply must preserve missing_inputs as summary key_gaps")
        findings = emitted.get("actionable_findings", [])
        if not any(isinstance(finding, dict) and finding.get("next_action") == "resolve `pr-gate`" for finding in findings):
            raise AssertionError("ship --apply must surface the PR gate next_action in short diagnostics")
        full_output = emitted.get("full_output") if isinstance(emitted.get("full_output"), dict) else {}
        if full_output.get("available") is not True:
            raise AssertionError("ship --apply blocker summary must retain an artifact locator for full diagnostics")
        if any(call[:2] == ["controlled-merge", "merge"] for call in calls):
            raise AssertionError("ship --apply must not merge after a gate blocker")
    finally:
        module.flow_payload = original_flow_payload
        module.emit = original_emit
        module.ship_pr_payload = original_ship_pr_payload


def assert_ship_closeout_policy_admission_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for ship closeout policy regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []
    emitted: dict[str, Any] = {}

    def fake_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        calls.append(flow_args)
        if flow_args[:2] == ["pr-metadata", "update"]:
            return {"command": "pr-metadata", "result": "pass", "summary": "metadata repaired"}
        if flow_args[:2] == ["pr-metadata", "preflight"]:
            return {
                "command": "pr-metadata",
                "result": "pass",
                "summary": "metadata ok",
                "governance_intensity_carrier": {
                    "envelope": {
                        "fields": {
                            "governance_intensity": "reinforced",
                            "change_class": "security",
                            "release_judgment": "no_release",
                            "upgrade_triggers": [],
                        }
                    }
                },
            }
        if flow_args[:2] == ["pr-gate", "check"]:
            return {"command": "pr-gate", "result": "pass", "summary": "pr gate ok"}
        if flow_args[:2] == ["controlled-merge", "check"]:
            return {"command": "controlled-merge", "result": "pass", "summary": "merge check ok", "pr": {"baseRefName": "main"}}
        if flow_args[:2] == ["controlled-merge", "merge"]:
            raise AssertionError("ship must not execute merge when closeout policy requires an explicit path")
        raise AssertionError(f"ship closeout policy delegated unexpected flow args: {flow_args}")

    def fake_emit(payload: dict[str, Any], *, stream: Any | None = None) -> int:
        emitted.clear()
        emitted.update(payload)
        return 0 if payload.get("result") == "pass" else 1

    original_flow_payload = module.flow_payload
    original_emit = module.emit
    original_ship_pr_payload = module.ship_pr_payload
    module.flow_payload = fake_flow_payload
    module.emit = fake_emit
    module.ship_pr_payload = lambda args, target: ({"headRefName": args.branch, "headRefOid": args.head_sha, "baseRefName": "main"}, [])
    try:
        status = module.handle_ship(
            [
                "--item",
                "WI-1735",
                "--issue",
                "1735",
                "--pr",
                "1740",
                "--branch",
                "work/1735-ship-contract",
                "--head-sha",
                "c" * 40,
                "--apply",
                "--json",
            ]
        )
        if status == 0 or emitted.get("result") != "block":
            raise AssertionError("ship --apply must block when closeout policy requires an explicit path")
        if emitted.get("schema_version") != "loom-cli-output/v1":
            raise AssertionError("ship closeout policy blocker must stay within the agent-safe summary envelope")
        if emitted.get("key_gaps") != ["closeout policy `full_closeout_pr` is not eligible for default host-only closeout"]:
            raise AssertionError("ship closeout policy blocker must preserve the policy admission gap")
        findings = emitted.get("actionable_findings", [])
        if not any(isinstance(finding, dict) and finding.get("next_action") == "loom closeout queue status --item <id> --issue <n> --pr <n> --json" for finding in findings):
            raise AssertionError("ship closeout policy admission must point callers to the explicit closeout queue path")
        if any(call[:2] == ["controlled-merge", "merge"] for call in calls):
            raise AssertionError("ship closeout policy admission must stop before merge")
    finally:
        module.flow_payload = original_flow_payload
        module.emit = original_emit
        module.ship_pr_payload = original_ship_pr_payload


def assert_ship_docs_entry_contract() -> None:
    required_snippets = {
        "README.md": [
            "## Daily Delivery Path",
            "loom ship \\",
            "inline or host-only closeout",
            "explicit full closeout PR",
            "The wrapper contract stays narrow and ordered",
            "short wrapper diagnostics",
            "follow-up issue scope",
        ],
        "README.zh-CN.md": [
            "## 日常交付路径",
            "loom ship \\",
            "内联或仅宿主收尾",
            "显式完整收尾拉取请求",
            "这个包装器的合同保持收敛且有固定顺序",
            "短诊断输出",
            "后续 issue 承接",
        ],
        "docs/methodology/harness/cli-command-matrix.md": [
            "loom ship",
            "Its main-path contract is",
            "blocker classification stays step-scoped",
            "remain follow-up issue scope; `loom ship` must block",
        ],
        "src/skills/README.md": [
            "For ordinary delivery after a Work Item has a PR, use `loom ship`",
            "follow-up closeout PR",
        ],
        "src/skills/README.zh-CN.md": [
            "普通交付默认使用 `loom ship`",
            "额外创建后续收尾拉取请求",
            "收尾拉取请求",
        ],
        "src/skills/route-matrix.md": [
            "普通交付 / ship",
            "`loom ship --target <repo>",
        ],
        "src/skills/loom-merge-ready/SKILL.md": [
            "普通交付默认使用 `loom ship`",
            "内联或仅宿主收尾",
        ],
        "src/skills/loom-retire/SKILL.md": [
            "普通交付后的合并与收尾默认由 `loom ship` 完成",
            "仅宿主收尾通过",
        ],
    }
    for relative_path, snippets in required_snippets.items():
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                raise AssertionError(f"{relative_path} missing ship entry snippet `{snippet}`")

    generated_pairs = [
        ("src/skills/README.md", "skills/README.md"),
        ("src/skills/README.zh-CN.md", "skills/README.zh-CN.md"),
        ("src/skills/route-matrix.md", "skills/route-matrix.md"),
        ("src/skills/loom-merge-ready/SKILL.md", "skills/loom-merge-ready/SKILL.md"),
        ("src/skills/loom-retire/SKILL.md", "skills/loom-retire/SKILL.md"),
    ]
    for source_path, generated_path in generated_pairs:
        source_text = (REPO_ROOT / source_path).read_text(encoding="utf-8")
        generated_text = (REPO_ROOT / generated_path).read_text(encoding="utf-8")
        if source_text != generated_text:
            raise AssertionError(f"{generated_path} drifted from {source_path}")


def assert_controlled_merge_triggered_check_rollup_contract(tmp: Path) -> None:
    target = tmp / "controlled-merge-triggered-check-rollup"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    pass_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if pass_payload.get("result") != "pass":
        raise AssertionError("controlled-merge triggered check fixture could not produce a pr-gate pass")

    fixture_dir = target / ".loom" / "fixtures" / fixture["item"]
    checks_file = fixture_dir / "checks.json"
    branch_protection_file = fixture_dir / "branch-protection.json"
    ruleset_file = fixture_dir / "ruleset.json"
    checks_file.write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "non-required-failed", "conclusion": "FAILURE", "status": "COMPLETED"},
                {"name": "non-required-pending", "status": "IN_PROGRESS"},
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    branch_protection_file.write_text(
        json.dumps({"required_status_checks": {"contexts": ["loom-pr-merge-gate"]}}, indent=2) + "\n",
        encoding="utf-8",
    )
    ruleset_file.write_text(json.dumps([], indent=2) + "\n", encoding="utf-8")

    _, payload = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            fixture["head_sha"],
            "--pr-payload-file",
            fixture["pr_file"],
            "--status-checks-file",
            f".loom/fixtures/{fixture['item']}/checks.json",
            "--branch-protection-file",
            f".loom/fixtures/{fixture['item']}/branch-protection.json",
            "--ruleset-file",
            f".loom/fixtures/{fixture['item']}/ruleset.json",
        ]
    )
    required_checks = payload.get("required_checks", {})
    missing_inputs = payload.get("missing_inputs", [])
    if (
        payload.get("result") != "block"
        or required_checks.get("result") != "pass"
        or required_checks.get("missing") != []
        or required_checks.get("pending") != []
        or required_checks.get("failing") != []
        or payload.get("triggered_check_rollup", {}).get("result") != "block"
        or payload.get("triggered_check_rollup", {}).get("blocking") != ["non-required-failed"]
        or payload.get("triggered_check_rollup", {}).get("pending") != ["non-required-pending"]
        or payload.get("controlled_merge_consumption", {}).get("result") != "block"
        or "triggered check `non-required-failed` failed" not in missing_inputs
        or "triggered check `non-required-pending` is pending" not in missing_inputs
    ):
        raise AssertionError("controlled-merge did not fail closed on failed/pending triggered non-required checks")


def assert_closeout_wrapper_argument_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for closeout wrapper regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    captured: dict[str, Any] = {}
    flow_payload_calls: list[dict[str, Any]] = []
    emitted_payloads: list[dict[str, Any]] = []

    def fake_emit_flow(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> int:
        captured.clear()
        captured["command"] = command
        captured["flow_args"] = flow_args
        captured["fallback_to"] = fallback_to
        return 0

    def arg_value(flow_args: list[str], flag: str) -> str | None:
        if flag not in flow_args:
            return None
        index = flow_args.index(flag)
        return flow_args[index + 1] if index + 1 < len(flow_args) else None

    def int_arg_value(flow_args: list[str], flag: str) -> int | None:
        value = arg_value(flow_args, flag)
        return int(value) if value is not None else None

    def closeout_pr_roles_from_flow_args(flow_args: list[str]) -> dict[str, Any]:
        roles = {
            role: number
            for role, number in (
                ("implementation_pr", int_arg_value(flow_args, "--implementation-pr")),
                ("release_pr", int_arg_value(flow_args, "--release-pr")),
                ("carrier_sync_pr", int_arg_value(flow_args, "--carrier-sync-pr")),
                ("final_closeout_pr", int_arg_value(flow_args, "--final-closeout-pr")),
            )
            if number is not None
        }
        requested_role = arg_value(flow_args, "--pr-role")
        legacy_pr = int_arg_value(flow_args, "--pr")
        if requested_role is not None:
            current_role = requested_role
            current_number = roles.get(requested_role, legacy_pr)
            source = f"--{requested_role.replace('_', '-')}" if requested_role in roles else "--pr plus --pr-role"
        else:
            current_role = "implementation_pr" if legacy_pr is not None else None
            current_number = legacy_pr
            source = "--pr" if legacy_pr is not None else None
        return {
            "schema_version": "loom-closeout-pr-roles/v1",
            "supported_roles": ["implementation_pr", "release_pr", "carrier_sync_pr", "final_closeout_pr"],
            "roles": roles,
            "legacy_pr": legacy_pr,
            "requested_role": requested_role,
            "current": {"role": current_role, "number": current_number, "source": source},
        }

    def fake_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        captured.clear()
        captured["command"] = command
        captured["flow_args"] = flow_args
        captured["fallback_to"] = fallback_to
        flow_payload_calls.append({"command": command, "flow_args": list(flow_args), "fallback_to": fallback_to})
        payload: dict[str, Any] = {"command": command, "result": "pass"}
        if flow_args[:2] == ["closeout", "check"]:
            pr_roles = closeout_pr_roles_from_flow_args(flow_args)
            current_pr = pr_roles["current"]["number"] or int_arg_value(flow_args, "--pr")
            issue_number = int_arg_value(flow_args, "--issue") or 1555
            payload.update(
                {
                    "pr_roles": pr_roles,
                    "current_pr_role": pr_roles["current"],
                    "issue": {
                        "number": issue_number,
                        "state": "CLOSED",
                        "closedAt": "2026-06-18T10:00:00Z",
                        "url": f"https://github.com/MC-and-his-Agents/Loom/issues/{issue_number}",
                    },
                    "pr": {
                        "number": current_pr,
                        "state": "MERGED",
                        "baseRefName": "main",
                        "mergedAt": "2026-06-18T09:55:00Z",
                        "url": f"https://github.com/MC-and-his-Agents/Loom/pull/{current_pr}",
                        "mergeCommit": {"oid": "fixture-merge-sha"},
                    },
                }
            )
        return payload

    def fake_emit(_payload: dict[str, Any]) -> int:
        emitted_payloads.append(_payload)
        return 0

    original_emit_flow = module.emit_flow
    original_flow_payload = module.flow_payload
    original_emit = module.emit
    module.emit_flow = fake_emit_flow
    module.flow_payload = fake_flow_payload
    module.emit = fake_emit
    try:
        status = module.handle_scenario(
            "closeout",
            [
                "--target",
                ".",
                "--item",
                "WI-1554",
                "--issue",
                "1554",
                "--pr",
                "1562",
                "--pr-role",
                "final_closeout_pr",
                "--implementation-pr",
                "1592",
                "--release-pr",
                "1592",
                "--carrier-sync-pr",
                "1593",
                "--final-closeout-pr",
                "1593",
                "--project",
                "4",
                "--phase",
                "1504",
                "--fr",
                "1505",
                "--branch",
                "work/1554-wrapper-closeout-contract",
                "--goal-completion",
                ".loom/goal-completion.json",
                "--gate-profile",
                "closeout-contract",
                "--owner",
                "MC-and-his-Agents",
                "--repo",
                "Loom",
                "--comment",
                "closeout comment",
                "--issue-payload-file",
                ".loom/fixtures/issue.json",
                "--pr-payload-file",
                ".loom/fixtures/pr.json",
                "--project-payload-file",
                ".loom/fixtures/project.json",
                "--status-checks-file",
                ".loom/fixtures/checks.json",
                "--branch-protection-file",
                ".loom/fixtures/protection.json",
                "--ruleset-file",
                ".loom/fixtures/ruleset.json",
                "--skip-gate",
            ],
        )
        if status != 0:
            raise AssertionError("closeout wrapper regression did not complete")
        if captured.get("command") != "closeout":
            raise AssertionError("closeout wrapper did not preserve command label")
        flow_args = captured.get("flow_args")
        if not isinstance(flow_args, list) or flow_args[:2] != ["closeout", "check"]:
            raise AssertionError("closeout wrapper did not delegate to closeout check")
        expected_pairs = {
            "--item": "WI-1554",
            "--issue": "1554",
            "--pr": "1562",
            "--pr-role": "final_closeout_pr",
            "--implementation-pr": "1592",
            "--release-pr": "1592",
            "--carrier-sync-pr": "1593",
            "--final-closeout-pr": "1593",
            "--project": "4",
            "--phase": "1504",
            "--fr": "1505",
            "--branch": "work/1554-wrapper-closeout-contract",
            "--goal-completion": ".loom/goal-completion.json",
            "--gate-profile": "closeout-contract",
            "--owner": "MC-and-his-Agents",
            "--repo": "Loom",
            "--comment": "closeout comment",
            "--issue-payload-file": ".loom/fixtures/issue.json",
            "--pr-payload-file": ".loom/fixtures/pr.json",
            "--project-payload-file": ".loom/fixtures/project.json",
            "--status-checks-file": ".loom/fixtures/checks.json",
            "--branch-protection-file": ".loom/fixtures/protection.json",
            "--ruleset-file": ".loom/fixtures/ruleset.json",
        }
        for flag, expected in expected_pairs.items():
            if flag not in flow_args:
                raise AssertionError(f"closeout wrapper did not pass {flag} to runtime")
            if flow_args[flow_args.index(flag) + 1] != expected:
                raise AssertionError(f"closeout wrapper changed {flag} value")
        if "--skip-gate" not in flow_args:
            raise AssertionError("closeout wrapper did not pass --skip-gate to runtime")

        status = module.handle_gate(["closeout", "--target", ".", "--item", "WI-1554", "--issue", "1554"])
        if status != 0:
            raise AssertionError("gate closeout wrapper regression did not complete")
        if captured.get("command") != "gate closeout":
            raise AssertionError("gate closeout wrapper did not preserve command label")
        flow_args = captured.get("flow_args")
        if not isinstance(flow_args, list) or flow_args[:2] != ["closeout", "check"]:
            raise AssertionError("gate closeout wrapper did not delegate to closeout check")
        for flag, expected in (("--item", "WI-1554"), ("--issue", "1554")):
            if flag not in flow_args or flow_args[flow_args.index(flag) + 1] != expected:
                raise AssertionError(f"gate closeout wrapper did not preserve {flag}")

        flow_payload_calls.clear()
        emitted_payloads.clear()
        status = module.handle_closeout_run(
            [
                "--target",
                ".",
                "--item",
                "WI-1555",
                "--issue",
                "1555",
                "--pr",
                "1563",
                "--project",
                "4",
                "--phase",
                "1504",
                "--fr",
                "1505",
                "--branch",
                "work/1555-one-shot-closeout-run",
                "--goal-completion",
                ".loom/goal-completion.json",
                "--gate-profile",
                "closeout-contract",
                "--owner",
                "MC-and-his-Agents",
                "--repo",
                "Loom",
                "--comment",
                "closeout comment",
                "--issue-payload-file",
                ".loom/fixtures/issue.json",
                "--pr-payload-file",
                ".loom/fixtures/pr.json",
                "--project-payload-file",
                ".loom/fixtures/project.json",
                "--status-checks-file",
                ".loom/fixtures/checks.json",
                "--branch-protection-file",
                ".loom/fixtures/protection.json",
                "--ruleset-file",
                ".loom/fixtures/ruleset.json",
                "--skip-gate",
                "--json",
            ]
        )
        if status != 0:
            raise AssertionError("closeout run wrapper regression did not complete")
        call_heads = [call["flow_args"][:2] for call in flow_payload_calls]
        if call_heads != [["reconciliation", "sync"], ["closeout", "check"], ["carrier", "closeout-sync"]]:
            raise AssertionError(f"closeout run dry-run delegated unexpected runtime sequence: {call_heads}")
        reconciliation_args = flow_payload_calls[0]["flow_args"]
        closeout_args = flow_payload_calls[1]["flow_args"]
        carrier_args = flow_payload_calls[2]["flow_args"]
        for flag, expected in {
            "--item": "WI-1555",
            "--issue": "1555",
            "--pr": "1563",
            "--project": "4",
            "--phase": "1504",
            "--fr": "1505",
            "--branch": "work/1555-one-shot-closeout-run",
            "--owner": "MC-and-his-Agents",
            "--repo": "Loom",
            "--comment": "closeout comment",
            "--issue-payload-file": ".loom/fixtures/issue.json",
            "--pr-payload-file": ".loom/fixtures/pr.json",
            "--project-payload-file": ".loom/fixtures/project.json",
        }.items():
            if flag not in reconciliation_args or reconciliation_args[reconciliation_args.index(flag) + 1] != expected:
                raise AssertionError(f"closeout run reconciliation step did not preserve {flag}")
        if "--dry-run" not in reconciliation_args or "--apply" in reconciliation_args:
            raise AssertionError("closeout run dry-run did not delegate reconciliation sync as dry-run")
        for flag, expected in {
            "--goal-completion": ".loom/goal-completion.json",
            "--gate-profile": "closeout-contract",
            "--status-checks-file": ".loom/fixtures/checks.json",
            "--branch-protection-file": ".loom/fixtures/protection.json",
            "--ruleset-file": ".loom/fixtures/ruleset.json",
        }.items():
            if flag not in closeout_args or closeout_args[closeout_args.index(flag) + 1] != expected:
                raise AssertionError(f"closeout run closeout-check step did not preserve {flag}")
        if "--skip-gate" not in closeout_args:
            raise AssertionError("closeout run closeout-check step did not preserve --skip-gate")
        for flag, expected in {
            "--item": "WI-1555",
            "--terminal-state": "closed_out",
            "--issue": "1555",
            "--pr": "1563",
            "--merge-commit": "fixture-merge-sha",
            "--target-branch": "main",
            "--closed-at": "2026-06-18T10:00:00Z",
            "--evidence-locator": "https://github.com/MC-and-his-Agents/Loom/issues/1555;https://github.com/MC-and-his-Agents/Loom/pull/1563",
        }.items():
            if flag not in carrier_args or carrier_args[carrier_args.index(flag) + 1] != expected:
                raise AssertionError(f"closeout run carrier step did not preserve inferred {flag}")
        if "--dry-run" not in carrier_args or "--apply" in carrier_args:
            raise AssertionError("closeout run dry-run did not delegate carrier closeout-sync as dry-run")
        if not emitted_payloads or emitted_payloads[-1].get("schema_version") != "loom-closeout-run/v1":
            raise AssertionError("closeout run must emit loom-closeout-run/v1")

        flow_payload_calls.clear()
        emitted_payloads.clear()
        status = module.handle_closeout_run(
            [
                "--target",
                ".",
                "--item",
                "WI-1515",
                "--issue",
                "1515",
                "--implementation-pr",
                "1592",
                "--release-pr",
                "1592",
                "--final-closeout-pr",
                "1593",
                "--pr-role",
                "final_closeout_pr",
                "--branch",
                "work/1515-post-release-closeout",
                "--json",
            ]
        )
        if status != 0:
            raise AssertionError("closeout run PR role fixture regression did not complete")
        call_heads = [call["flow_args"][:2] for call in flow_payload_calls]
        if call_heads != [["reconciliation", "sync"], ["closeout", "check"], ["carrier", "closeout-sync"]]:
            raise AssertionError(f"closeout run PR role fixture delegated unexpected runtime sequence: {call_heads}")
        reconciliation_args = flow_payload_calls[0]["flow_args"]
        closeout_args = flow_payload_calls[1]["flow_args"]
        carrier_args = flow_payload_calls[2]["flow_args"]
        for args_name, flow_args in (("reconciliation", reconciliation_args), ("closeout-check", closeout_args)):
            for flag, expected in {
                "--implementation-pr": "1592",
                "--release-pr": "1592",
                "--final-closeout-pr": "1593",
                "--pr-role": "final_closeout_pr",
            }.items():
                if flag not in flow_args or flow_args[flow_args.index(flag) + 1] != expected:
                    raise AssertionError(f"closeout run {args_name} step did not preserve {flag} for PR role fixture")
            if "--pr" in flow_args:
                raise AssertionError(f"closeout run {args_name} step leaked legacy --pr for role-only fixture")
        if carrier_args[carrier_args.index("--pr") + 1] != "1593":
            raise AssertionError("closeout run PR role fixture did not consume final_closeout_pr for carrier metadata")
        role_payload = emitted_payloads[-1].get("current_pr_role") if emitted_payloads else {}
        if role_payload != {"role": "final_closeout_pr", "number": 1593, "source": "--final-closeout-pr"}:
            raise AssertionError(f"closeout run PR role fixture emitted unexpected current role: {role_payload}")

        flow_payload_calls.clear()
        emitted_payloads.clear()
        status = module.handle_closeout_run(
            [
                "--target",
                ".",
                "--item",
                "WI-1555",
                "--issue",
                "1555",
                "--pr",
                "1563",
                "--branch",
                "work/1555-one-shot-closeout-run",
                "--apply",
                "--json",
            ]
        )
        if status != 0:
            raise AssertionError("closeout run apply wrapper regression did not complete")
        call_heads = [call["flow_args"][:2] for call in flow_payload_calls]
        if call_heads != [
            ["reconciliation", "sync"],
            ["closeout", "check"],
            ["carrier", "closeout-sync"],
            ["recovery", "writeback"],
            ["carrier", "refresh"],
            ["carrier", "refresh"],
            ["closeout", "check"],
        ]:
            raise AssertionError(f"closeout run apply delegated unexpected runtime sequence: {call_heads}")
        if "--apply" not in flow_payload_calls[0]["flow_args"] or "--dry-run" in flow_payload_calls[0]["flow_args"]:
            raise AssertionError("closeout run apply did not delegate reconciliation sync as apply")
        if "--apply" not in flow_payload_calls[2]["flow_args"] or "--dry-run" in flow_payload_calls[2]["flow_args"]:
            raise AssertionError("closeout run apply did not delegate carrier closeout-sync as apply")
        recovery_args = flow_payload_calls[3]["flow_args"]
        for flag, expected in {
            "--item": "WI-1555",
            "--current-checkpoint": "closed_out",
            "--current-lane": "post-merge-closeout-run",
        }.items():
            if flag not in recovery_args or recovery_args[recovery_args.index(flag) + 1] != expected:
                raise AssertionError(f"closeout run recovery writeback did not preserve {flag}")
        payload = emitted_payloads[-1] if emitted_payloads else {}
        if payload.get("result") != "pass" or payload.get("apply") is not True:
            raise AssertionError("closeout run apply did not emit a passing apply payload")

        def blocking_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
            flow_payload_calls.append({"command": command, "flow_args": list(flow_args), "fallback_to": fallback_to})
            if flow_args[:2] == ["closeout", "check"]:
                return {
                    "command": command,
                    "result": "block",
                    "missing_inputs": ["issue is not closed"],
                    "issue": {"number": 1555, "state": "OPEN"},
                    "pr": {"number": 1563, "state": "MERGED", "mergeCommit": {"oid": "fixture-merge-sha"}},
                }
            return {"command": command, "result": "pass"}

        module.flow_payload = blocking_flow_payload
        flow_payload_calls.clear()
        emitted_payloads.clear()
        status = module.handle_closeout_run(
            [
                "--target",
                ".",
                "--item",
                "WI-1555",
                "--issue",
                "1555",
                "--pr",
                "1563",
                "--branch",
                "work/1555-one-shot-closeout-run",
                "--apply",
                "--json",
            ]
        )
        if status != 0:
            raise AssertionError("closeout run apply-block wrapper regression did not complete")
        call_heads = [call["flow_args"][:2] for call in flow_payload_calls]
        if call_heads != [["reconciliation", "sync"], ["closeout", "check"]]:
            raise AssertionError(f"closeout run apply must stop before carrier mutation when closeout-check blocks: {call_heads}")
        payload = emitted_payloads[-1] if emitted_payloads else {}
        if payload.get("result") != "block" or payload.get("failure_classifier") != "issue_not_closed":
            raise AssertionError("closeout run apply block did not classify the first blocking step")

        status = module.handle_pr(["gate", "1569", "--surface", "closeout", "--work-item", "WI-1542"])
        if status != 0:
            raise AssertionError("pr gate closeout surface wrapper regression did not complete")
        if captured.get("command") != "pr gate":
            raise AssertionError("pr gate wrapper did not preserve command label")
        flow_args = captured.get("flow_args")
        if not isinstance(flow_args, list) or flow_args[:2] != ["pr-gate", "check"]:
            raise AssertionError("pr gate wrapper did not delegate to pr-gate check")
        expected_pairs = {"--pr": "1569", "--surface": "closeout", "--item": "WI-1542"}
        for flag, expected in expected_pairs.items():
            if flag not in flow_args or flow_args[flow_args.index(flag) + 1] != expected:
                raise AssertionError(f"pr gate wrapper did not preserve {flag}")
    finally:
        module.emit_flow = original_emit_flow
        module.flow_payload = original_flow_payload
        module.emit = original_emit


def assert_workspace_audit_wrapper_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for workspace audit wrapper regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    captured: dict[str, Any] = {}

    def fake_flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> dict[str, Any]:
        captured.clear()
        captured["command"] = command
        captured["flow_args"] = flow_args
        captured["fallback_to"] = fallback_to
        return {"command": "work-item-audit", "result": "pass"}

    original_flow_payload = module.flow_payload
    module.flow_payload = fake_flow_payload
    try:
        payload = module.workspace_payload(
            "audit",
            argparse.Namespace(target=".", item="WI-1542"),
        )
        if payload.get("command") != "workspace audit":
            raise AssertionError("workspace audit wrapper did not preserve command label")
        if payload.get("wrapped_command") != "work-item-audit":
            raise AssertionError("workspace audit wrapper did not record wrapped runtime command")
        flow_args = captured.get("flow_args")
        if flow_args != ["work-item-audit", "--target", str(REPO_ROOT), "--item", "WI-1542"]:
            raise AssertionError(f"workspace audit wrapper delegated unexpected runtime args: {flow_args}")
    finally:
        module.flow_payload = original_flow_payload


def retained_closeout_work_item_id() -> str | None:
    candidates: list[tuple[str, str, str]] = []
    for path in sorted((REPO_ROOT / ".loom" / "progress").glob("WI-*.md")):
        text = path.read_text(encoding="utf-8")
        item_match = re.search(r"(?im)^\s*-\s*Item ID:\s*(WI-\d+)\s*$", text)
        checkpoint_match = re.search(r"(?im)^\s*-\s*Current Checkpoint:\s*([A-Za-z_-]+)\s*$", text)
        if not item_match or not checkpoint_match:
            continue
        checkpoint = checkpoint_match.group(1).lower().replace("-", "_")
        if checkpoint not in {"closed", "closed_out", "done"} or "## Terminal Closeout Metadata" not in text:
            continue
        closed_match = re.search(r"(?im)^\s*-\s*Closed At:\s*([^\n]+?)\s*$", text)
        closed_at = closed_match.group(1).strip() if closed_match else ""
        candidates.append((closed_at, path.name, item_match.group(1)))
    if not candidates:
        return None
    return sorted(candidates)[-1][2]


def active_work_item_id() -> str:
    payload = json.loads((REPO_ROOT / ".loom" / "bootstrap" / "init-result.json").read_text(encoding="utf-8"))
    fact_chain = payload.get("fact_chain", {}) if isinstance(payload.get("fact_chain"), dict) else {}
    item_id = fact_chain.get("entry_points", {}).get("current_item_id") if isinstance(fact_chain.get("entry_points"), dict) else None
    if fact_chain.get("mode") == "idle" or item_id == "no_active_item":
        retained_item = retained_closeout_work_item_id()
        if retained_item:
            return retained_item
    if not isinstance(item_id, str) or not item_id:
        raise AssertionError("init-result current_item_id is missing")
    return item_id


def run_json_preserving_attempts(args: list[str], *, item: str, expect: int | None = None) -> tuple[int, dict[str, Any]]:
    attempt_root = REPO_ROOT / ".loom" / "runtime" / "attempts" / item
    with tempfile.TemporaryDirectory(prefix="loom-attempt-backup-") as raw_backup:
        backup = Path(raw_backup) / "attempts"
        existed = attempt_root.exists()
        if existed:
            shutil.copytree(attempt_root, backup)
        try:
            return run_json(args, expect=expect)
        finally:
            if attempt_root.exists():
                shutil.rmtree(attempt_root)
            if existed:
                shutil.copytree(backup, attempt_root)


@contextmanager
def preserved_repo_paths(relatives: tuple[str, ...]):
    with tempfile.TemporaryDirectory(prefix="loom-path-backup-") as raw_backup:
        backup = Path(raw_backup)
        snapshots: dict[str, Path | None] = {}
        for relative in relatives:
            source = REPO_ROOT / relative
            destination = backup / relative
            if source.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
                snapshots[relative] = destination
            else:
                snapshots[relative] = None
        try:
            yield
        finally:
            for relative, snapshot in snapshots.items():
                source = REPO_ROOT / relative
                if source.exists():
                    if source.is_dir():
                        shutil.rmtree(source)
                    else:
                        source.unlink()
                if snapshot is None:
                    continue
                source.parent.mkdir(parents=True, exist_ok=True)
                if snapshot.is_dir():
                    shutil.copytree(snapshot, source)
                else:
                    shutil.copy2(snapshot, source)


@contextmanager
def isolated_codex_workstation(home: Path):
    old_home = os.environ.get("HOME")
    old_codex_home = os.environ.get("CODEX_HOME")
    os.environ["HOME"] = str(home)
    os.environ["CODEX_HOME"] = str(home / ".codex")
    try:
        yield
    finally:
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home
        if old_codex_home is None:
            os.environ.pop("CODEX_HOME", None)
        else:
            os.environ["CODEX_HOME"] = old_codex_home


def register_fixture_codex_plugin() -> None:
    run_json(
        [
            "host",
            "register",
            "--host",
            "codex",
            "--scope",
            "user",
            "--apply",
            "--json",
        ],
        expect=0,
    )


def assert_suite_gate_consumption(payload: dict[str, Any], *, expected_surface: str) -> None:
    suite_gate = payload.get("suite_gate_validation")
    if not isinstance(suite_gate, dict):
        raise AssertionError(f"{expected_surface} did not expose suite gate validation")
    if suite_gate.get("schema_version") != "loom-suite-gate-validation/v1":
        raise AssertionError(f"{expected_surface} suite gate validation schema drifted")
    if suite_gate.get("surface") != expected_surface:
        raise AssertionError(f"{expected_surface} suite gate validation surface drifted")
    if suite_gate.get("result") not in {"pass", "block", "fallback", "not_applicable"}:
        raise AssertionError(f"{expected_surface} suite gate validation result drifted")
    authority = suite_gate.get("authority_boundary", {})
    if authority.get("role") != "gate_input_evidence" or "review_record" not in authority.get("does_not_replace", []):
        raise AssertionError(f"{expected_surface} suite gate authority boundary drifted")
    validations = suite_gate.get("validations", {})
    for domain, command_fragment in (
        ("evidence", "suite evidence validate"),
        ("carrier", "suite carrier validate"),
    ):
        validation = validations.get(domain)
        if not isinstance(validation, dict):
            raise AssertionError(f"{expected_surface} missing {domain} validation payload")
        command = str(validation.get("command", ""))
        if command != "not_applicable" and command_fragment not in command:
            raise AssertionError(f"{expected_surface} {domain} validation command drifted")
    step_names = {step.get("name") for step in payload.get("steps", []) if isinstance(step, dict)}
    subcheck_names = {
        subcheck.get("id")
        for subcheck in payload.get("gate", {}).get("subchecks", [])
        if isinstance(subcheck, dict)
    }
    has_step_evidence = {"suite-evidence-validate", "suite-carrier-validate"}.issubset(step_names)
    has_closeout_subchecks = {"suite_evidence_validation", "suite_carrier_validation"}.issubset(subcheck_names)
    if not has_step_evidence and not has_closeout_subchecks:
        raise AssertionError(f"{expected_surface} did not expose suite evidence/carrier validation steps")
    consumed = suite_gate.get("consumed_locators", {})
    if not isinstance(consumed, dict) or "evidence_map" not in consumed or "task_carriers" not in consumed:
        raise AssertionError(f"{expected_surface} suite gate consumed locators drifted")
    if suite_gate.get("result") != "not_applicable" and expected_surface != "closeout" and "consistency_analysis" not in consumed:
        raise AssertionError(f"{expected_surface} suite gate consumed locators drifted")


def assert_suite_build_consumption(payload: dict[str, Any]) -> None:
    suite_validation = payload.get("suite_validation")
    if not isinstance(suite_validation, dict):
        raise AssertionError("build did not expose suite validation")
    if (
        suite_validation.get("command") != "suite validate"
        or suite_validation.get("validator_mode") != "repo-local-cli"
        or suite_validation.get("mutates") is not False
    ):
        raise AssertionError("build suite validation did not consume repo-local CLI JSON")
    carrier_validation = payload.get("suite_carrier_validation")
    if not isinstance(carrier_validation, dict):
        raise AssertionError("build did not expose suite carrier validation")
    if (
        "suite carrier validate" not in str(carrier_validation.get("command", ""))
        or carrier_validation.get("validator_mode") != "repo-local-cli"
        or not isinstance(carrier_validation.get("payload"), dict)
    ):
        raise AssertionError("build suite carrier validation did not consume repo-local CLI JSON")
    step_names = {step.get("name") for step in payload.get("steps", []) if isinstance(step, dict)}
    if {"suite-validate", "suite-carrier-validate"} - step_names:
        raise AssertionError("build did not expose suite validation steps")


def assert_review_record_consumed_locators(tmp: Path) -> None:
    target = tmp / "review-record-consumed-locators"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    active_item = fixture["item"]
    spec_review = target / ".loom" / "reviews" / f"{active_item}.spec.json"
    implementation_review = target / ".loom" / "reviews" / f"{active_item}.json"
    expected_spec = f".loom/specs/{active_item}/spec.md"
    expected_plan = f".loom/specs/{active_item}/plan.md"
    expected_evidence = f".loom/specs/{active_item}/evidence-map.md"
    expected_carrier = f".loom/specs/{active_item}/task-carrier.md"
    suite_not_applicable = False
    _, spec_record_payload = run_json(
        [
            "review",
            "record",
            "--target",
            str(target),
            "--item",
            active_item,
            "--decision",
            "allow",
            "--kind",
            "spec_review",
            "--summary",
            "Contract fixture spec review allow.",
            "--reviewer",
            "contract-check",
        ],
        expect=0,
    )
    if spec_record_payload.get("result") != "pass":
        raise AssertionError("spec review record fixture did not pass")
    spec_record = json.loads(spec_review.read_text(encoding="utf-8"))
    spec_consumed = spec_record.get("consumed_inputs", {})
    base_spec_consumed = (
        spec_consumed.get("suite_validation") == "suite validate"
        and spec_consumed.get("suite_validator_mode") == "repo-local-cli"
        and spec_consumed.get("suite_spec") == expected_spec
        and "suite_consistency_analysis" in spec_consumed
    )
    not_applicable_spec_consumed = (
        suite_not_applicable
        and spec_consumed.get("suite_plan") is None
        and spec_consumed.get("suite_evidence_map") is None
        and spec_consumed.get("suite_task_carriers") == []
    )
    full_or_minimal_spec_consumed = (
        spec_consumed.get("suite_plan") == expected_plan
        and spec_consumed.get("suite_evidence_map") == expected_evidence
        and expected_carrier in spec_consumed.get("suite_task_carriers", [])
    )
    if not base_spec_consumed or not (not_applicable_spec_consumed or full_or_minimal_spec_consumed):
        raise AssertionError("spec review record consumed suite locators drifted")
    commit_fixture_file(target, spec_review.relative_to(target).as_posix(), "fixture spec review record")

    _, implementation_record_payload = run_json(
        [
            "review",
            "record",
            "--target",
            str(target),
            "--item",
            active_item,
            "--decision",
            "allow",
            "--kind",
            "code_review",
            "--summary",
            "Contract fixture implementation review allow.",
            "--reviewer",
            "contract-check",
        ],
        expect=0,
    )
    if implementation_record_payload.get("result") != "pass":
        raise AssertionError("implementation review record fixture did not pass")
    implementation_record = json.loads(implementation_review.read_text(encoding="utf-8"))
    implementation_consumed = implementation_record.get("consumed_inputs", {})
    not_applicable_implementation_consumed = (
        suite_not_applicable
        and implementation_consumed.get("suite_evidence_validation") == "not_applicable"
        and implementation_consumed.get("suite_carrier_validation") == "not_applicable"
        and implementation_consumed.get("suite_evidence_map") is None
        and implementation_consumed.get("suite_task_carriers") == []
    )
    full_or_minimal_implementation_consumed = (
        "suite evidence validate" in str(implementation_consumed.get("suite_evidence_validation", ""))
        and "suite carrier validate" in str(implementation_consumed.get("suite_carrier_validation", ""))
        and implementation_consumed.get("suite_evidence_map") == expected_evidence
        and expected_carrier in implementation_consumed.get("suite_task_carriers", [])
    )
    if (
        "suite_consistency_analysis" not in implementation_consumed
        or not isinstance(implementation_consumed.get("suite_evidence_consumed_contracts"), list)
        or not isinstance(implementation_consumed.get("suite_carrier_consumed_contracts"), list)
        or not (not_applicable_implementation_consumed or full_or_minimal_implementation_consumed)
    ):
        raise AssertionError("implementation review record consumed suite/evidence locators drifted")


def active_suite_path_not_applicable(active_item: str) -> bool:
    spec_path = REPO_ROOT / ".loom" / "specs" / active_item / "spec.md"
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.exists() else ""
    return bool(re.search(r"(?im)^\s*(?:[-*]\s*)?suite path\s*:\s*not_applicable\b", spec_text))


def assert_closeout_blocks_missing_suite_evidence(active_item: str, closeout_payload: dict[str, Any]) -> None:
    if active_suite_path_not_applicable(active_item):
        return
    suite_gate = closeout_payload.get("suite_gate_validation")
    if isinstance(suite_gate, dict) and suite_gate.get("result") == "not_applicable":
        return
    evidence_map = f".loom/specs/{active_item}/evidence-map.md"
    with preserved_repo_paths((evidence_map,)):
        path = REPO_ROOT / evidence_map
        if path.exists():
            path.unlink()
        status, payload = run_json(["closeout", "--target", str(REPO_ROOT), "--json"])
        payload = runtime_payload_from_agent_safe_output(payload)
        if status == 0 or payload.get("result") != "block":
            raise AssertionError("closeout did not fail closed when suite evidence was missing")
        suite_gate = payload.get("suite_gate_validation")
        if not isinstance(suite_gate, dict) or suite_gate.get("surface") != "closeout":
            raise AssertionError("closeout missing suite gate validation on missing suite evidence")
        missing = payload.get("missing_inputs")
        if not isinstance(missing, list) or not any("suite_evidence_validation" in str(message) for message in missing):
            raise AssertionError("closeout missing inputs did not identify suite evidence validation")


def load_loom_flow_module() -> Any:
    module_path = REPO_ROOT / "src" / "skills" / "shared" / "scripts" / "loom_flow.py"
    spec = importlib.util.spec_from_file_location("loom_flow_contract", module_path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load loom_flow module for reconciliation contract checks")
    module = importlib.util.module_from_spec(spec)
    scripts_root = str(module_path.parent)
    sys.path.insert(0, scripts_root)
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == scripts_root:
            sys.path.pop(0)
    return module


def assert_gate_freeze_carrier_shadow_bindings_contract() -> None:
    loom_flow = load_loom_flow_module()
    with tempfile.TemporaryDirectory(prefix="loom-freeze-shadow-") as raw_tmp:
        target = Path(raw_tmp)
        source = target / "shadow-source.md"
        source.write_text("current shadow source\n", encoding="utf-8")
        interop = target / ".loom" / "companion" / "interop.json"
        interop.parent.mkdir(parents=True, exist_ok=True)
        shadow_dir = target / ".loom" / "shadow"
        shadow_dir.mkdir(parents=True, exist_ok=True)
        interop.write_text(
            json.dumps(
                {
                    "schema_version": "loom-repo-interop/v1",
                    "host_adapters": [],
                    "repo_native_carriers": [],
                    "shadow_surfaces": {
                        "review": {
                            "loom_locator": ".loom/shadow/review-loom.json",
                            "repo_locator": ".loom/shadow/review-repo.json",
                        }
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        stale_payload = {
            "result": "match",
            "source_files": ["shadow-source.md"],
            "source_sha256": {"shadow-source.md": "0" * 64},
        }
        fresh_payload = {
            "result": "match",
            "source_files": ["shadow-source.md"],
            "source_sha256": {"shadow-source.md": loom_flow.sha256_file(source)},
        }
        (shadow_dir / "review-loom.json").write_text(json.dumps(stale_payload, indent=2) + "\n", encoding="utf-8")
        (shadow_dir / "review-repo.json").write_text(json.dumps(fresh_payload, indent=2) + "\n", encoding="utf-8")
        governance_surface = {
            "repo_interop": {
                "availability": "present",
                "contract": {"locator": ".loom/companion/interop.json"},
            }
        }

        binding = loom_flow.gate_freeze_shadow_freshness_binding(target, governance_surface)
        if binding.get("schema_version") != "loom-gate-freeze-shadow-freshness/v1":
            raise AssertionError("gate freeze shadow freshness binding schema drifted")
        if binding.get("result") != "block" or binding.get("failure_kind") != "shadow_source_hash_drift":
            raise AssertionError(f"gate freeze shadow freshness did not block source hash drift: {binding}")
        drift_record = next(
            (
                record
                for record in binding.get("records", [])
                if isinstance(record, dict) and record.get("path") == ".loom/shadow/review-loom.json"
            ),
            None,
        )
        if not isinstance(drift_record, dict):
            raise AssertionError("gate freeze shadow freshness did not expose the stale shadow path")
        expected_record_fields = {
            "surface": "review",
            "freshness": "stale",
            "drift_kind": "shadow_source_hash_drift",
            "refreshable": True,
        }
        for key, expected in expected_record_fields.items():
            if drift_record.get(key) != expected:
                raise AssertionError(f"gate freeze shadow freshness {key} drifted: {drift_record}")
        if not drift_record.get("current_source_sha256") or not drift_record.get("expected_source_sha256"):
            raise AssertionError("gate freeze shadow freshness must expose current and expected source hashes")
        suggestions = loom_flow.gate_freeze_refresh_suggestions({"shadow_freshness": binding})
        if not suggestions or any("loom shadow-parity" in suggestion for suggestion in suggestions):
            raise AssertionError(f"gate freeze refresh suggestions must use existing refresh paths: {suggestions}")
        blocking_inputs = loom_flow.gate_freeze_blocking_inputs({"shadow_freshness": binding})
        if not any(finding.get("failure_kind") == "shadow_source_hash_drift" for finding in blocking_inputs):
            raise AssertionError(f"gate freeze blocking inputs did not preserve source-hash drift taxonomy: {blocking_inputs}")


def assert_reconciliation_suite_taxonomy_contract() -> None:
    loom_flow = load_loom_flow_module()
    suite_gate = {
        "schema_version": "loom-suite-gate-validation/v1",
        "surface": "closeout",
        "result": "block",
        "missing_inputs": ["evidence: stale_evidence", "carrier: carrier_truth_conflict"],
        "fallback_to": "suite evidence validate",
        "validations": {
            "evidence": {
                "result": "block",
                "fallback_to": "suite evidence validate",
                "command": "loom suite evidence validate --target . --item WI-taxonomy --json",
                "payload": {
                    "blocking_gaps": [
                        {
                            "id": "stale-evidence",
                            "classification": "stale",
                            "failure_kind": "stale_evidence",
                            "failed_layer": "evidence_map",
                            "source_locator": ".loom/specs/WI-taxonomy/evidence-map.md:5",
                            "binding": "suite-evidence-validate",
                            "consumer_impact": "closeout cannot consume stale evidence",
                            "remediation_direction": "refresh evidence",
                            "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
                        },
                        {
                            "id": "head-drift",
                            "classification": "stale",
                            "failure_kind": "head_or_pr_drift",
                            "failed_layer": "evidence_map",
                            "source_locator": ".loom/specs/WI-taxonomy/evidence-map.md:6",
                            "binding": "suite-evidence-validate",
                            "consumer_impact": "closeout cannot consume evidence bound to a stale PR head",
                            "remediation_direction": "rerun merge-ready against the current PR head",
                            "fallback_to": "loom gate merge --target <repo> --pr <pr> --json",
                        },
                    ]
                },
            },
            "carrier": {
                "result": "block",
                "fallback_to": "suite carrier validate",
                "command": "loom suite carrier validate --target . --item WI-taxonomy --json",
                "payload": {
                    "payload": {
                        "blocking_gaps": [
                            {
                                "id": "host-conflict",
                                "classification": "conflict",
                                "failure_kind": "carrier_truth_conflict",
                                "failed_layer": "task_carrier",
                                "source_locator": ".loom/specs/WI-taxonomy/task-carrier.md:5",
                                "binding": "suite-carrier-validate",
                                "consumer_impact": "host carrier mirror conflicts with Work Item truth",
                                "remediation_direction": "reconcile host mirror",
                                "fallback_to": "loom suite carrier inspect --target <repo> --item <item> --json",
                            }
                        ],
                        "host_signal_conflicts": [{"id": "project-done-issue-open", "blocking": True}],
                    }
                },
            },
        },
    }
    findings = loom_flow.suite_gate_reconciliation_findings(suite_gate, subject="issue #1143")
    kinds = {finding.get("kind") for finding in findings}
    required = {"suite_stale_evidence", "suite_head_or_pr_drift", "suite_host_state_conflict"}
    if not required.issubset(kinds):
        raise AssertionError(f"reconciliation suite taxonomy findings drifted: {kinds}")
    if any(finding.get("severity") != "block" or finding.get("category") != "suite_drift" for finding in findings):
        raise AssertionError("reconciliation suite taxonomy findings must be blocking suite_drift findings")
    failure_kinds = {finding.get("evidence", {}).get("failure_kind") for finding in findings}
    if {"stale_evidence", "head_or_pr_drift", "carrier_truth_conflict"} - failure_kinds:
        raise AssertionError("reconciliation suite taxonomy evidence did not retain source failure kinds")

    missing_gate_findings = loom_flow.suite_gate_reconciliation_findings(
        {
            "schema_version": "loom-suite-gate-validation/v1",
            "surface": "closeout",
            "result": "block",
            "missing_inputs": ["suite evidence validation"],
            "fallback_to": "suite evidence validate",
            "validations": {},
        },
        subject="issue #1143",
    )
    if [finding.get("kind") for finding in missing_gate_findings] != ["missing_suite_gate"]:
        raise AssertionError("reconciliation did not classify missing suite gate drift")


def assert_issue_dependency_machine_block_contract() -> None:
    loom_flow = load_loom_flow_module()
    historical_issue_body = (
        "## Historical Notes\n\n"
        "- depends on #1514 and blocked by #1513 were prior planning notes only.\n"
        "- 前置：#1542、#1544 已在历史收口中消费，不代表当前 active blocker。\n"
        "- 依赖 #1529 的说明只是归档文字，不应生成 active edge。\n"
    )
    historical_edges = loom_flow.parse_authored_dependency_edges(historical_issue_body, 1515)
    if historical_edges:
        raise AssertionError(f"historical issue prose must not produce authored dependency edges: {historical_edges}")
    historical_graph = loom_flow.dependency_graph_payload(
        issue_number=1515,
        issue_payload={"number": 1515, "state": "closed", "body": historical_issue_body},
        native_dependency_payload={"availability": "present", "checks": [], "native_edges": []},
    )
    if historical_graph.get("authored_edges") or historical_graph.get("findings"):
        raise AssertionError("historical issue prose must not create active dependency drift or findings")

    machine_block_body = (
        "## Dependency Carrier\n\n"
        '<!-- loom:issue-dependencies {"schema_version":"loom-issue-dependencies/v1","blocked_by":["#793"],"blocks":[795]} -->\n'
    )
    machine_edges = loom_flow.parse_authored_dependency_edges(machine_block_body, 794)
    edge_keys = {
        (edge.get("source_issue"), edge.get("blocking_issue"), edge.get("direction"))
        for edge in machine_edges
        if isinstance(edge, dict)
    }
    if edge_keys != {(794, 793, "blocked_by"), (795, 794, "blocking")}:
        raise AssertionError(f"structured issue dependency machine block parsed unexpected edges: {machine_edges}")
    if not all(
        isinstance(edge, dict)
        and edge.get("source_of_truth") == "issue_body_machine_block"
        and edge.get("provenance", {}).get("source_owner") == "github_issue_machine_block"
        for edge in machine_edges
    ):
        raise AssertionError("structured issue dependency machine block must retain machine-block provenance")
    machine_graph = loom_flow.dependency_graph_payload(
        issue_number=794,
        issue_payload={"number": 794, "state": "open", "body": machine_block_body},
        native_dependency_payload={"availability": "present", "checks": [], "native_edges": []},
    )
    missing_native_findings = [
        finding
        for finding in machine_graph.get("findings", [])
        if isinstance(finding, dict) and finding.get("kind") == "missing_native_edge"
    ]
    if len(missing_native_findings) != 2:
        raise AssertionError("structured issue dependency machine block must remain consumable as authored proof")


def assert_docs_contract_suite_not_applicable_gate_contract(tmp: Path) -> None:
    loom_flow = load_loom_flow_module()
    target = tmp / "docs-contract-suite-not-applicable"
    (target / ".loom/specs/WI-docs").mkdir(parents=True)
    (target / ".loom/reviews").mkdir(parents=True)
    (target / ".loom/specs/WI-docs/spec.md").write_text(
        "# Spec\n\n"
        "- Suite path: not_applicable\n\n"
        "- Suite-level not_applicable: rationale: docs-only contract freeze does not require a formal suite; "
        "consumer boundary: suite validate, spec review, pr-gate, merge-ready, and closeout may consume this only "
        "as formal suite non-applicability and must still require Work Item truth, current-head implementation review, "
        "CI, release/no-release evidence, and closeout evidence; "
        "recheck condition: scope expands beyond docs-only contract or carrier updates.\n",
        encoding="utf-8",
    )
    context = {
        "target_root": target,
        "item_id": "WI-docs",
        "review_entry": ".loom/reviews/WI-docs.json",
        "current_checkpoint": "merge",
        "associated_artifacts": [],
    }
    original_spec_suite_validation_payload = loom_flow.spec_suite_validation_payload
    original_git_head_sha = loom_flow.git_head_sha
    original_suite_gate_validation_payload = loom_flow.suite_gate_validation_payload
    try:
        loom_flow.git_head_sha = lambda _target_root: "current-head"
        loom_flow.spec_suite_validation_payload = lambda _context: {
            "schema_version": "loom-suite-validation-consumption/v1",
            "command": "suite validate",
            "result": "not_applicable",
            "summary": "Suite validate found a not_applicable suite path decision.",
            "missing_inputs": [],
            "blocking_gaps": [],
            "payload": {
                "suite_path": "not_applicable",
                "path_decision_locator": ".loom/specs/WI-docs/spec.md",
                "not_applicable_rationale": [
                    {
                        "artifact": "suite",
                        "locator": ".loom/specs/WI-docs/spec.md:block-3",
                        "rationale": "docs-only contract freeze",
                        "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                        "recheck_condition": "scope expands beyond docs-only contract or carrier updates",
                    }
                ],
            },
        }
        spec_gate = loom_flow.spec_review_gate_payload(context)
        if (
            spec_gate.get("result") != "not_applicable"
            or spec_gate.get("required") is not False
            or spec_gate.get("missing_inputs")
            or spec_gate.get("fallback_to") is not None
        ):
            raise AssertionError("spec review gate did not consume suite not_applicable as non-applicable")
        implementation_gate = loom_flow.implementation_review_status_payload(context)
        if (
            implementation_gate.get("result") != "block"
            or ".loom/reviews/WI-docs.json" not in " ".join(implementation_gate.get("missing_inputs", []))
        ):
            raise AssertionError("suite not_applicable must not bypass implementation review")
        if not loom_flow.spec_review_gate_ready_for_implementation_review(spec_gate):
            raise AssertionError("suite not_applicable must allow implementation review recording after spec gate")

        def unexpected_suite_gate_validation(_context: dict[str, Any], *, surface: str) -> dict[str, Any]:
            raise AssertionError(f"docs-only suite not_applicable must not call suite gate validators for {surface}")

        loom_flow.suite_gate_validation_payload = unexpected_suite_gate_validation
        review_suite_gate = loom_flow.suite_gate_payload_for_surface(context, surface="review")
        merge_ready_suite_gate = loom_flow.suite_gate_payload_for_surface(context, surface="merge_ready")
        if review_suite_gate.get("result") != "not_applicable" or merge_ready_suite_gate.get("result") != "not_applicable":
            raise AssertionError("review and merge-ready must consume docs-only suite not_applicable")
        for gate in (review_suite_gate, merge_ready_suite_gate):
            if gate.get("missing_inputs") or gate.get("fallback_to") is not None:
                raise AssertionError("suite not_applicable gate must not require evidence/carrier fallback inputs")
        loom_flow.suite_gate_validation_payload = original_suite_gate_validation_payload

        loom_flow.spec_suite_validation_payload = lambda _context: {
            "schema_version": "loom-suite-validation-consumption/v1",
            "command": "suite validate",
            "result": "block",
            "summary": "suite validation blocked invalid not_applicable rationale",
            "missing_inputs": ["not_applicable_rationale:.loom/specs/WI-docs/spec.md:block-3:rationale"],
            "blocking_gaps": [
                {
                    "failure_kind": "invalid_not_applicable_rationale",
                    "source_locator": ".loom/specs/WI-docs/spec.md:block-3",
                    "remediation_direction": "Author suite-level not_applicable rationale.",
                }
            ],
            "fallback_to": "loom suite validate --target <repo> --item <item> --json",
        }
        (target / ".loom/specs/WI-docs/plan.md").write_text("# Plan\n", encoding="utf-8")
        (target / ".loom/specs/WI-docs/implementation-contract.md").write_text(
            "# Implementation Contract\n",
            encoding="utf-8",
        )
        blocked_spec_gate = loom_flow.spec_review_gate_payload(context)
        if (
            blocked_spec_gate.get("result") != "block"
            or not any("invalid_not_applicable_rationale" in str(message) for message in blocked_spec_gate.get("missing_inputs", []))
        ):
            raise AssertionError("invalid suite not_applicable rationale did not fail closed")
        if loom_flow.spec_review_gate_ready_for_implementation_review(blocked_spec_gate):
            raise AssertionError("blocked suite validation must not allow implementation review recording")
    finally:
        loom_flow.spec_suite_validation_payload = original_spec_suite_validation_payload
        loom_flow.suite_gate_validation_payload = original_suite_gate_validation_payload
        loom_flow.git_head_sha = original_git_head_sha


def snapshot_tree(target: Path) -> list[str]:
    return sorted(path.relative_to(target).as_posix() for path in target.rglob("*"))


def digest_path(path: Path) -> dict[str, str]:
    if path.is_dir():
        return {"kind": "directory"}
    return {
        "kind": "file",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def snapshot_paths(target: Path, relatives: tuple[str, ...]) -> dict[str, dict[str, str]]:
    snapshot: dict[str, dict[str, str]] = {}
    for relative in relatives:
        path = target / relative
        if path.exists():
            snapshot[relative] = digest_path(path)
    return snapshot


def init_git_fixture(target: Path) -> str:
    subprocess.run(["git", "init"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=target, check=True)
    (target / "README.md").write_text("# Fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()


def write_forbidden_truth_fixture(target: Path) -> dict[str, dict[str, str]]:
    for index, relative in enumerate(SCAFFOLD_FORBIDDEN_TRUTH_SURFACES):
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            path.write_text(json.dumps({"fixture_surface": relative, "index": index}, indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(f"# Forbidden scaffold truth fixture\n\n- locator: {relative}\n- index: {index}\n", encoding="utf-8")
    return snapshot_paths(target, SCAFFOLD_FORBIDDEN_TRUTH_SURFACES)


def assert_forbidden_truth_unchanged(target: Path, before: dict[str, dict[str, str]]) -> None:
    after = snapshot_paths(target, SCAFFOLD_FORBIDDEN_TRUTH_SURFACES)
    if after != before:
        raise AssertionError("suite scaffold modified forbidden host/review/merge-ready/closeout/generated-skill truth surfaces")


def assert_scaffold_write_boundary(payload: dict[str, Any], *, item: str, allowed_artifacts: list[str]) -> None:
    allowed_locators = {f".loom/specs/{item}/{artifact}" for artifact in allowed_artifacts}
    planned = payload.get("planned_writes", [])
    if not isinstance(planned, list):
        raise AssertionError("suite scaffold planned_writes is not a list")
    for entry in planned:
        locator = entry.get("locator")
        if locator not in allowed_locators:
            raise AssertionError(f"suite scaffold planned write escaped allowed artifact set: {locator}")
    created = payload.get("created_locators", [])
    if not isinstance(created, list):
        raise AssertionError("suite scaffold created_locators is not a list")
    unexpected_created = sorted(locator for locator in created if locator not in allowed_locators)
    if unexpected_created:
        raise AssertionError(f"suite scaffold created forbidden locators: {unexpected_created}")
    forbidden_keys = sorted(SCAFFOLD_FORBIDDEN_ACTION_KEYS & set(payload))
    if forbidden_keys:
        raise AssertionError(f"suite scaffold emitted forbidden host/truth action keys: {forbidden_keys}")


def run_suite_inspect_fixture(target: Path, item: str) -> dict[str, Any]:
    before = snapshot_tree(target)
    _, payload = run_json(["suite", "inspect", "--target", str(target), "--item", item, "--json"], expect=0)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite inspect mutated fixture target for {item}")
    if payload.get("command") != "suite inspect" or payload.get("result") != "pass" or payload.get("mutates") is not False:
        raise AssertionError(f"suite inspect envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite inspect item binding drifted for {item}")
    return payload


def run_suite_scaffold_fixture(target: Path, item: str, extra_args: list[str] | None = None, *, expect: int = 0) -> dict[str, Any]:
    before = snapshot_tree(target)
    args = ["suite", "scaffold", "--target", str(target), "--item", item, "--json"]
    if extra_args:
        args.extend(extra_args)
    _, payload = run_json(args, expect=expect)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite scaffold mutated fixture target for {item}: {extra_args or []}")
    if payload.get("command") != "suite scaffold" or payload.get("mutates") is not False:
        raise AssertionError(f"suite scaffold envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite scaffold item binding drifted for {item}")
    return payload


def run_suite_scaffold_apply_fixture(target: Path, item: str, extra_args: list[str] | None = None) -> dict[str, Any]:
    args = ["suite", "scaffold", "--target", str(target), "--item", item, "--json", "--apply"]
    if extra_args:
        args.extend(extra_args)
    _, payload = run_json(args, expect=0)
    if payload.get("command") != "suite scaffold" or payload.get("result") != "pass":
        raise AssertionError(f"suite scaffold apply envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite scaffold apply item binding drifted for {item}")
    return payload


def run_suite_validate_fixture(target: Path, item: str, *, expect: int = 0) -> dict[str, Any]:
    before = snapshot_tree(target)
    _, payload = run_json(["suite", "validate", "--target", str(target), "--item", item, "--json"], expect=expect)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite validate mutated fixture target for {item}")
    if payload.get("command") != "suite validate" or payload.get("mutates") is not False:
        raise AssertionError(f"suite validate envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite validate item binding drifted for {item}")
    if not isinstance(payload.get("blocking_gaps"), list) or not isinstance(payload.get("advisory_gaps"), list):
        raise AssertionError(f"suite validate gaps are not structured for {item}")
    return payload


def run_suite_evidence_inspect_fixture(target: Path, item: str) -> dict[str, Any]:
    before = snapshot_tree(target)
    _, payload = run_json(["suite", "evidence", "inspect", "--target", str(target), "--item", item, "--json"], expect=0)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite evidence inspect mutated fixture target for {item}")
    if payload.get("command") != "suite evidence inspect" or payload.get("result") != "pass" or payload.get("mutates") is not False:
        raise AssertionError(f"suite evidence inspect envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite evidence inspect item binding drifted for {item}")
    return payload


def run_suite_evidence_scaffold_fixture(target: Path, item: str, extra_args: list[str] | None = None, *, expect: int = 0) -> dict[str, Any]:
    before = snapshot_tree(target)
    args = ["suite", "evidence", "scaffold", "--target", str(target), "--item", item, "--json"]
    if extra_args:
        args.extend(extra_args)
    _, payload = run_json(args, expect=expect)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite evidence scaffold mutated fixture target for {item}: {extra_args or []}")
    if payload.get("command") != "suite evidence scaffold" or payload.get("mutates") is not False:
        raise AssertionError(f"suite evidence scaffold dry-run envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite evidence scaffold item binding drifted for {item}")
    return payload


def run_suite_evidence_scaffold_apply_fixture(target: Path, item: str, extra_args: list[str] | None = None, *, expect: int = 0) -> dict[str, Any]:
    args = ["suite", "evidence", "scaffold", "--target", str(target), "--item", item, "--json", "--apply"]
    if extra_args:
        args.extend(extra_args)
    _, payload = run_json(args, expect=expect)
    if payload.get("command") != "suite evidence scaffold":
        raise AssertionError(f"suite evidence scaffold apply command drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite evidence scaffold apply item binding drifted for {item}")
    return payload


def run_suite_evidence_validate_fixture(target: Path, item: str, *, expect: int = 0) -> dict[str, Any]:
    before = snapshot_tree(target)
    _, payload = run_json(["suite", "evidence", "validate", "--target", str(target), "--item", item, "--json"], expect=expect)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite evidence validate mutated fixture target for {item}")
    if payload.get("command") != "suite evidence validate" or payload.get("mutates") is not False:
        raise AssertionError(f"suite evidence validate envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite evidence validate item binding drifted for {item}")
    if not isinstance(payload.get("blocking_gaps"), list) or not isinstance(payload.get("advisory_gaps"), list):
        raise AssertionError(f"suite evidence validate gaps are not structured for {item}")
    return payload


def run_suite_carrier_inspect_fixture(target: Path, item: str) -> dict[str, Any]:
    before = snapshot_tree(target)
    _, payload = run_json(["suite", "carrier", "inspect", "--target", str(target), "--item", item, "--json"], expect=0)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite carrier inspect mutated fixture target for {item}")
    if payload.get("command") != "suite carrier inspect" or payload.get("result") != "pass" or payload.get("mutates") is not False:
        raise AssertionError(f"suite carrier inspect envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite carrier inspect item binding drifted for {item}")
    return payload


def run_suite_carrier_validate_fixture(target: Path, item: str, *, expect: int = 0) -> dict[str, Any]:
    before = snapshot_tree(target)
    _, payload = run_json(["suite", "carrier", "validate", "--target", str(target), "--item", item, "--json"], expect=expect)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError(f"suite carrier validate mutated fixture target for {item}")
    if payload.get("command") != "suite carrier validate" or payload.get("mutates") is not False:
        raise AssertionError(f"suite carrier validate envelope drifted for {item}")
    if payload.get("item_id") != item:
        raise AssertionError(f"suite carrier validate item binding drifted for {item}")
    if not isinstance(payload.get("blocking_gaps"), list) or not isinstance(payload.get("advisory_gaps"), list):
        raise AssertionError(f"suite carrier validate gaps are not structured for {item}")
    return payload


def assert_suite_failure_taxonomy(payload: dict[str, Any], failure_kind: str, *, result: str, layer: str) -> None:
    suite_payload = payload.get("payload", {})
    findings = suite_payload.get("findings", [])
    taxonomy = suite_payload.get("failure_taxonomy", [])
    supported = suite_payload.get("supported_failure_kinds", [])
    if failure_kind not in supported:
        raise AssertionError(f"suite validate supported failure kinds missing {failure_kind}")
    matching_findings = [entry for entry in findings if entry.get("failure_kind") == failure_kind]
    if not matching_findings:
        raise AssertionError(f"suite validate findings missing {failure_kind}")
    for finding in matching_findings:
        for field in (
            "id",
            "classification",
            "failure_kind",
            "default_result",
            "failed_layer",
            "source_locator",
            "binding",
            "consumer_impact",
            "remediation_direction",
            "fallback_to",
        ):
            if field not in finding:
                raise AssertionError(f"suite validate finding {failure_kind} missing {field}")
        if finding.get("default_result") != result or finding.get("failed_layer") != layer:
            raise AssertionError(f"suite validate finding taxonomy drifted for {failure_kind}")
    taxonomy_entry = next((entry for entry in taxonomy if entry.get("failure_kind") == failure_kind), None)
    if not taxonomy_entry:
        raise AssertionError(f"suite validate failure_taxonomy missing {failure_kind}")
    for field in (
        "classification",
        "default_result",
        "failed_layer",
        "source_locator",
        "consumer_impact",
        "remediation_direction",
        "fallback_to",
        "binding",
    ):
        if field not in taxonomy_entry:
            raise AssertionError(f"suite validate taxonomy {failure_kind} missing {field}")
    if taxonomy_entry.get("default_result") != result or taxonomy_entry.get("failed_layer") != layer:
        raise AssertionError(f"suite validate failure_taxonomy values drifted for {failure_kind}")


def assert_suite_negative_fail_closed(
    payload: dict[str, Any],
    failure_kind: str,
    *,
    expected_missing_inputs: tuple[str, ...] = (),
    expected_missing_fields: tuple[str, ...] = (),
) -> None:
    if payload.get("result") != "block" or payload.get("fail_closed_reason") != failure_kind:
        raise AssertionError(f"suite validate did not fail closed with {failure_kind}")
    blocking_gaps = payload.get("blocking_gaps", [])
    if not blocking_gaps or not any(gap.get("failure_kind") == failure_kind for gap in blocking_gaps):
        raise AssertionError(f"suite validate blocking gaps missing {failure_kind}")
    matching_gaps = [gap for gap in blocking_gaps if gap.get("failure_kind") == failure_kind]
    for gap in matching_gaps:
        if not gap.get("remediation_direction") or not gap.get("consumer_impact") or not gap.get("fallback_to"):
            raise AssertionError(f"suite validate {failure_kind} gap missing remediation contract")
    payload_body = payload.get("payload", {})
    if not payload_body.get("remediation_directions"):
        raise AssertionError(f"suite validate {failure_kind} payload missing remediation directions")
    top_missing = payload.get("missing_inputs", [])
    payload_missing = payload_body.get("missing_inputs", [])
    for expected in expected_missing_inputs:
        if expected not in top_missing or expected not in payload_missing:
            raise AssertionError(f"suite validate {failure_kind} missing input drifted: {expected}")
    if expected_missing_fields:
        records = payload_body.get("not_applicable_rationale", [])
        missing_fields = {
            field
            for record in records
            if isinstance(record, dict)
            for field in record.get("missing_fields", [])
        }
        for expected in expected_missing_fields:
            if expected not in missing_fields:
                raise AssertionError(f"suite validate not_applicable missing field drifted: {expected}")
    assert_suite_failure_taxonomy(payload, failure_kind, result="block", layer=str(payload.get("failed_layer") or "suite"))


def write_state(target: Path, payload: dict[str, Any]) -> None:
    state_dir = target / ".loom"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "installed-state.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def materialize_surface(target: Path, relative: str) -> None:
    path = target / relative
    if path.suffix:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"fixture_surface": relative}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    path.mkdir(parents=True, exist_ok=True)


def assert_global_cli_runtime_fixture_catalog(fixture_data: dict[str, Any]) -> None:
    catalog = fixture_data.get("synthetic_regression_fixtures")
    if not isinstance(catalog, list):
        raise AssertionError("legacy migration fixture catalog is missing #1244 synthetic regression fixtures")
    fixtures = {fixture.get("id"): fixture for fixture in catalog if isinstance(fixture, dict)}
    expected = {
        "hotcp-style-global-cli-no-loom-bin": {
            "fixture_type": "global-cli-no-bin",
            "classification": "current",
            "runtime_provider": "global-cli",
        },
        "repo-local-wrapper-compatibility": {
            "fixture_type": "repo-local-wrapper-compatibility",
            "classification": "current",
            "runtime_provider": "repo-local-wrapper",
        },
        "global-cli-retained-loom-bin-residue": {
            "fixture_type": "global-cli-retained-residue",
            "classification": "current-with-repairable-residue",
            "runtime_provider": "global-cli",
        },
        "global-cli-retained-loom-bin-carrier-blocker": {
            "fixture_type": "global-cli-retained-blocker",
            "repair_plan_status": "blocked",
        },
        "global-cli-provider-command-mismatch": {
            "fixture_type": "global-cli-mismatch",
            "doctor_result": "block",
            "failed_layer": "global-cli-runtime-provider",
        },
    }
    missing = sorted(set(expected) - set(fixtures))
    if missing:
        raise AssertionError(f"#1244 synthetic fixture catalog missing entries: {missing}")
    for fixture_id, expected_values in expected.items():
        fixture = fixtures[fixture_id]
        if fixture.get("issue") != 1244 or fixture.get("synthetic") is not True:
            raise AssertionError(f"{fixture_id} must stay a synthetic #1244 fixture")
        if not fixture.get("summary") or fixture.get("source_path"):
            raise AssertionError(f"{fixture_id} must document a synthetic summary without copying repository history")
        expected_payload = fixture.get("expected")
        if not isinstance(expected_payload, dict):
            raise AssertionError(f"{fixture_id} is missing expected fixture payload")
        for key, value in expected_values.items():
            actual = fixture.get(key) if key == "fixture_type" else expected_payload.get(key)
            if actual != value:
                raise AssertionError(f"{fixture_id} expected {key} drifted: {actual!r}")
    no_bin = fixtures["hotcp-style-global-cli-no-loom-bin"]
    if ".loom/bin" not in no_bin.get("absent_surfaces", []):
        raise AssertionError("global-cli no-bin fixture must explicitly forbid .loom/bin")
    retained = fixtures["global-cli-retained-loom-bin-residue"].get("expected", {})
    if retained.get("requires_confirmation") is not True or retained.get("deletes") != [".loom/bin"]:
        raise AssertionError("retained .loom/bin fixture must keep deletion proposal-only")
    blocker = fixtures["global-cli-retained-loom-bin-carrier-blocker"].get("expected", {})
    if set(blocker.get("blocking_reference_paths", [])) != {".loom/bootstrap/init-result.json", ".loom/status/current.md"}:
        raise AssertionError("retained .loom/bin blocker fixture must name stable carrier paths")


def assert_legacy_fixture_contract(tmp: Path) -> None:
    fixture_data = json.loads(LEGACY_FIXTURES.read_text(encoding="utf-8"))
    if fixture_data.get("schema_version") != "loom-legacy-migration-validation-fixtures/v1":
        raise AssertionError("legacy migration fixture schema drifted")
    assert_global_cli_runtime_fixture_catalog(fixture_data)
    for fixture in fixture_data["fixtures"]:
        target = tmp / fixture["id"]
        target.mkdir()
        for relative in fixture["surfaces"]:
            materialize_surface(target, relative)
        expected = fixture["expected"]
        _, detected = run_json(["detect", "--target", str(target), "--json"], expect=0)
        if detected["classification"] != expected["classification"]:
            raise AssertionError(f"{fixture['id']} classified as {detected['classification']}")
        detected_kinds = {surface["kind"] for surface in detected["surfaces"]}
        missing_kinds = sorted(set(expected["surface_kinds"]) - detected_kinds)
        if missing_kinds:
            raise AssertionError(f"{fixture['id']} missing surface kinds: {missing_kinds}")

        status, doctor = run_json(["doctor", "--target", str(target), "--json"])
        if status == 0 or doctor["result"] != expected["doctor_result"] or doctor["fallback_to"] != expected["doctor_fallback_to"]:
            raise AssertionError(f"{fixture['id']} doctor did not fail closed to repair plan")

        _, repair_plan = run_json(["repair", "plan", "--target", str(target), "--json"], expect=0)
        if repair_plan["mutates"] != expected["repair_plan_mutates"] or not repair_plan["actions"]:
            raise AssertionError(f"{fixture['id']} repair plan did not expose non-mutating actions")

        _, upgrade_plan = run_json(["upgrade-plan", "--target", str(target), "--json"], expect=0)
        action_ids = {action["id"] for action in upgrade_plan["actions"]}
        missing_actions = sorted(set(expected["upgrade_plan_required_actions"]) - action_ids)
        if upgrade_plan["mutates"] != expected["upgrade_plan_mutates"] or missing_actions:
            raise AssertionError(f"{fixture['id']} upgrade-plan missing actions: {missing_actions}")

        status, verify = run_json(["verify", "--target", str(target), "--json"])
        if status == 0 or verify["result"] != expected["verify_result"]:
            raise AssertionError(f"{fixture['id']} verify did not block on legacy surfaces")


def assert_downstream_plugin_layout_contract(tmp: Path) -> None:
    target = tmp / "downstream-plugin-layout"
    home = tmp / "downstream-plugin-home"
    target.mkdir()
    home.mkdir()
    with isolated_codex_workstation(home):
        _, dry_run = run_json(["host", "install", "--host", "codex", "--scope", "user", "--target", str(target), "--dry-run", "--json"], expect=0)
        if dry_run.get("source_kind") != "global-loom-package" or dry_run.get("mutates") is not False:
            raise AssertionError("user-level host install dry-run did not use the global Loom package")
        _, installed = run_json(["host", "install", "--host", "codex", "--scope", "user", "--target", str(target), "--apply", "--json"], expect=0)
        if installed.get("source_kind") != "global-loom-package" or installed.get("workstation_install", {}).get("result") != "pass":
            raise AssertionError("user-level host install did not read back the installed Codex plugin payload")
        for write in installed.get("writes", []):
            if Path(write).resolve().is_relative_to(target.resolve()):
                raise AssertionError(f"user-level host install wrote inside the target repository: {write}")
        _, registered = run_json(["host", "register", "--host", "codex", "--scope", "user", "--target", str(target), "--apply", "--json"], expect=0)
        if registered.get("source_kind") != "global-loom-package" or registered.get("workstation_registration", {}).get("result") != "pass":
            raise AssertionError("user-level host register did not read back Codex registration")
        for write in registered.get("writes", []):
            if Path(write).resolve().is_relative_to(target.resolve()):
                raise AssertionError(f"user-level host register wrote inside the target repository: {write}")
        for unexpected in ("plugins/loom", "skills", ".agents/skills", ".loom/bin", ".loom/installed-state.json"):
            if (target / unexpected).exists():
                raise AssertionError(f"user-level host install/register wrote unsupported repository payload: {unexpected}")


def write_payload_hash(manifest: Path, value: str) -> None:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload.setdefault("x-loom", {})["plugin_payload_hash"] = value
    manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def remove_payload_hash(manifest: Path) -> None:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload.setdefault("x-loom", {}).pop("plugin_payload_hash", None)
    manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def assert_codex_payload_readback_contract(tmp: Path) -> None:
    target = tmp / "codex-payload-readback"
    home = tmp / "codex-payload-home"
    bad_source = tmp / "codex-payload-bad-source"
    target.mkdir()
    home.mkdir()
    with isolated_codex_workstation(home):
        run_json(["host", "register", "--host", "codex", "--scope", "user", "--target", str(target), "--apply", "--json"], expect=0)
        runtime = home / ".codex" / "plugins" / "cache" / "local-user-plugins" / "loom" / "0.4.0"
        shutil.copytree(home / "plugins" / "loom", runtime)
        older_surface_runtime = home / ".codex" / "plugins" / "cache" / "local-user-plugins" / "loom" / "0.3.0"
        shutil.copytree(home / "plugins" / "loom", older_surface_runtime)
        write_payload_hash(older_surface_runtime / ".codex-plugin" / "plugin.json", "stale-older-surface")

        _, current = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        if current.get("plugin_payload_readback", {}).get("freshness") != "already_current":
            raise AssertionError("host doctor did not report current plugin payload freshness")

        shutil.copytree(REPO_ROOT / "plugins" / "loom", bad_source)
        (bad_source / ".codex-plugin" / "plugin.json").write_text("{not-json", encoding="utf-8")
        _, invalid_source = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--source", str(bad_source), "--target", str(target), "--json"], expect=0)
        source_layer = next(
            (
                layer
                for layer in invalid_source.get("plugin_payload_readback", {}).get("layers", [])
                if layer.get("layer") == "source-payload"
            ),
            {},
        )
        if invalid_source.get("plugin_payload_readback", {}).get("freshness") != "source_metadata_missing" or not source_layer.get("error"):
            raise AssertionError("host doctor did not fail closed on malformed Codex source payload metadata")
        if invalid_source.get("version_freshness", {}).get("plugin_payload", {}).get("freshness") != "source_metadata_missing":
            raise AssertionError("host doctor version freshness did not reuse explicit Codex source payload readback")

        remove_payload_hash(home / "plugins" / "loom" / ".codex-plugin" / "plugin.json")
        _, missing_marketplace = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        readback = missing_marketplace.get("plugin_payload_readback", {})
        if readback.get("freshness") != "marketplace_source_metadata_missing" or readback.get("action") != "install_plugin":
            raise AssertionError("host doctor did not identify missing Codex marketplace source metadata")

        shutil.rmtree(home / "plugins" / "loom")
        shutil.copytree(REPO_ROOT / "plugins" / "loom", home / "plugins" / "loom")
        marketplace_manifest = home / "plugins" / "loom" / ".codex-plugin" / "plugin.json"
        marketplace_manifest.write_text("{not-json", encoding="utf-8")
        _, invalid_marketplace = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        marketplace_layer = next(
            (
                layer
                for layer in invalid_marketplace.get("plugin_payload_readback", {}).get("layers", [])
                if layer.get("layer") == "marketplace-source"
            ),
            {},
        )
        if invalid_marketplace.get("plugin_payload_readback", {}).get("freshness") != "marketplace_source_metadata_missing" or not marketplace_layer.get("error"):
            raise AssertionError("host doctor did not fail closed on malformed Codex marketplace source metadata")

        shutil.rmtree(home / "plugins" / "loom")
        shutil.copytree(REPO_ROOT / "plugins" / "loom", home / "plugins" / "loom")
        write_payload_hash(home / "plugins" / "loom" / ".codex-plugin" / "plugin.json", "stale-marketplace")
        _, stale_marketplace = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        readback = stale_marketplace.get("plugin_payload_readback", {})
        if readback.get("freshness") != "marketplace_source_stale" or readback.get("action") != "install_plugin":
            raise AssertionError("host doctor did not identify stale Codex marketplace source")

        shutil.rmtree(home / "plugins" / "loom")
        shutil.copytree(REPO_ROOT / "plugins" / "loom", home / "plugins" / "loom")
        remove_payload_hash(runtime / ".codex-plugin" / "plugin.json")
        _, missing_runtime = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        readback = missing_runtime.get("plugin_payload_readback", {})
        if readback.get("freshness") != "runtime_cache_metadata_missing" or readback.get("action") != "reload_host":
            raise AssertionError("host doctor did not identify missing Codex runtime cache metadata")

        shutil.rmtree(runtime)
        shutil.copytree(REPO_ROOT / "plugins" / "loom", runtime)
        write_payload_hash(runtime / ".codex-plugin" / "plugin.json", "stale-runtime")
        _, stale_runtime = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        readback = stale_runtime.get("plugin_payload_readback", {})
        if readback.get("freshness") != "runtime_cache_stale" or readback.get("action") != "reload_host":
            raise AssertionError("host doctor did not identify stale Codex runtime cache")

        runtime_manifest = runtime / ".codex-plugin" / "plugin.json"
        runtime_manifest.write_text("{not-json", encoding="utf-8")
        _, invalid_runtime = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0)
        runtime_layer = next(
            (
                layer
                for layer in invalid_runtime.get("plugin_payload_readback", {}).get("layers", [])
                if layer.get("layer") == "runtime-cache"
            ),
            {},
        )
        if invalid_runtime.get("plugin_payload_readback", {}).get("freshness") != "runtime_cache_metadata_missing" or not runtime_layer.get("error"):
            raise AssertionError("host doctor did not fail closed on malformed Codex runtime cache metadata")


def assert_version_freshness_contract(tmp: Path) -> None:
    target = tmp / "version-freshness"
    home = tmp / "version-freshness-home"
    target.mkdir()
    home.mkdir()
    installed_version = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    with isolated_codex_workstation(home):
        run_json(["install", "--target", str(target), "--apply", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        register_fixture_codex_plugin()
        runtime = home / ".codex" / "plugins" / "cache" / "local-user-plugins" / "loom" / "0.4.0"
        shutil.copytree(home / "plugins" / "loom", runtime)

        _, current = run_json(["version", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        freshness = current.get("version_freshness", {})
        if freshness.get("action") != "already_current" or freshness.get("plugin_payload", {}).get("freshness") != "already_current":
            raise AssertionError("version did not report current CLI and plugin payload freshness")
        if freshness.get("surface_compatibility", {}).get("status") != "compatible":
            raise AssertionError("version did not report compatible plugin surface for current payloads")
        current_guidance = freshness.get("plugin_payload", {}).get("refresh_guidance", {})
        if current_guidance.get("status") != "current" or current_guidance.get("readback_command") != "loom host doctor --host codex --scope user --json":
            raise AssertionError("current plugin payload freshness did not expose host readback guidance")
        short_output = subprocess.run(
            [sys.executable, str(LOOM), "version"],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "LOOM_TEST_NPM_LATEST_VERSION": installed_version},
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
        )
        if short_output.returncode != 0 or "action already_current" not in short_output.stdout:
            raise AssertionError(f"version short output did not expose freshness action\n{short_output.stderr}\n{short_output.stdout}")

        _, host_doctor = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        if host_doctor.get("version_freshness", {}).get("action") != "already_current":
            raise AssertionError("host doctor did not expose version freshness action")

        _, upgrade_plan = run_json(["upgrade-plan", "--target", str(target), "--host", "codex", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        freshness_action = next((action for action in upgrade_plan.get("actions", []) if action.get("id") == "cli-plugin-freshness"), None)
        if not freshness_action or freshness_action.get("status") != "current":
            raise AssertionError("upgrade-plan did not expose current CLI/plugin freshness action")
        if freshness_action.get("readback_command") != "loom host doctor --host codex --scope user --json":
            raise AssertionError("upgrade-plan current freshness action did not expose host readback command")

        _, stale_cli = run_json(["version", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": "99.0.0"})
        if stale_cli.get("version_freshness", {}).get("action") != "upgrade_cli":
            raise AssertionError("version did not identify stale CLI")

        write_payload_hash(home / "plugins" / "loom" / ".codex-plugin" / "plugin.json", "stale-marketplace")
        _, stale_marketplace_plan = run_json(["upgrade-plan", "--target", str(target), "--host", "codex", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        stale_marketplace_action = next((action for action in stale_marketplace_plan.get("actions", []) if action.get("id") == "cli-plugin-freshness"), None)
        expected_apply = [
            "loom host install --host codex --scope user --apply --json",
            "loom host register --host codex --scope user --apply --json",
        ]
        if (
            not stale_marketplace_action
            or stale_marketplace_action.get("action") != "refresh_plugin"
            or stale_marketplace_action.get("apply_commands") != expected_apply
            or stale_marketplace_action.get("readback_command") != "loom host doctor --host codex --scope user --json"
        ):
            raise AssertionError("upgrade-plan did not expose executable stale marketplace plugin refresh guidance")
        run_json(["host", "install", "--host", "codex", "--scope", "user", "--target", str(target), "--apply", "--json"], expect=0)
        run_json(["host", "register", "--host", "codex", "--scope", "user", "--target", str(target), "--apply", "--json"], expect=0)
        _, repaired_marketplace = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        if repaired_marketplace.get("version_freshness", {}).get("plugin_payload", {}).get("freshness") != "already_current":
            raise AssertionError("host install/register guidance did not repair stale plugin marketplace payload")

        write_payload_hash(runtime / ".codex-plugin" / "plugin.json", "stale-runtime")
        _, stale_plugin = run_json(["version", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        if stale_plugin.get("version_freshness", {}).get("action") != "refresh_plugin":
            raise AssertionError("version did not identify stale plugin payload")
        stale_guidance = stale_plugin.get("version_freshness", {}).get("plugin_payload", {}).get("refresh_guidance", {})
        if (
            stale_guidance.get("action") != "reload_host"
            or stale_guidance.get("reload_required") is not True
            or stale_guidance.get("apply_commands") != []
            or stale_guidance.get("readback_command") != "loom host doctor --host codex --scope user --json"
        ):
            raise AssertionError("stale runtime payload did not expose reload/readback guidance")
        shutil.rmtree(runtime)
        shutil.copytree(home / "plugins" / "loom", runtime)
        runtime_manifest = runtime / ".codex-plugin" / "plugin.json"
        runtime_payload = json.loads(runtime_manifest.read_text(encoding="utf-8"))
        runtime_payload.setdefault("x-loom", {})["plugin_surface_version"] = "0.0.0-test"
        runtime_manifest.write_text(json.dumps(runtime_payload, indent=2) + "\n", encoding="utf-8")
        _, incompatible_surface = run_json(["version", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        if (
            incompatible_surface.get("version_freshness", {}).get("surface_compatibility", {}).get("status") != "incompatible"
            or "runtime-cache" not in incompatible_surface.get("version_freshness", {}).get("surface_compatibility", {}).get("incompatible_layers", [])
        ):
            raise AssertionError("version did not identify plugin surface incompatibility")
        shutil.rmtree(runtime)
        shutil.copytree(home / "plugins" / "loom", runtime)
        _, repaired_runtime = run_json(["host", "doctor", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        if repaired_runtime.get("version_freshness", {}).get("plugin_payload", {}).get("freshness") != "already_current":
            raise AssertionError("simulated Codex reload did not repair stale runtime payload readback")

        remove_payload_hash(runtime / ".codex-plugin" / "plugin.json")
        _, missing_metadata = run_json(["version", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": installed_version})
        if missing_metadata.get("version_freshness", {}).get("plugin_payload", {}).get("freshness") != "runtime_cache_metadata_missing":
            raise AssertionError("version did not expose missing plugin payload metadata")

        shutil.rmtree(runtime)
        shutil.copytree(home / "plugins" / "loom", runtime)
        _, unreadable = run_json(["version", "--json"], expect=0, env_overrides={"LOOM_TEST_NPM_LATEST_VERSION": "__unreadable__"})
        if unreadable.get("version_freshness", {}).get("cli", {}).get("freshness") != "npm_unreadable":
            raise AssertionError("version did not expose npm latest read failure")


def assert_metadata_only_adoption_contract(tmp: Path) -> None:
    target = tmp / "metadata-only-adoption"
    target.mkdir()
    status, install_plan = run_json(["install", "--target", str(target), "--host", "codex", "--json"])
    if (
        status == 0
        or install_plan.get("failed_layer") != "install-apply"
        or install_plan.get("host_plugin_refresh", {}).get("id") != "host-plugin-refresh-boundary"
        or "loom host install --host codex --scope user --apply --json" not in install_plan.get("host_plugin_refresh", {}).get("apply_commands", [])
    ):
        raise AssertionError("target install did not expose Codex host plugin refresh boundary")
    _, installed = run_json(
        ["install", "--target", str(target), "--apply", "--json"],
        expect=0,
    )
    if installed.get("host_plugin_refresh", {}).get("id") != "host-plugin-refresh-boundary":
        raise AssertionError("metadata-only install did not preserve separate host plugin refresh guidance")
    managed_writes = set(installed.get("managed_writes", []))
    if managed_writes != {".loom/installed-state.json", "AGENTS.md"}:
        raise AssertionError(f"metadata-only install wrote unexpected artifacts: {sorted(managed_writes)}")
    agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
    if "<!-- LOOM_BOOTSTRAP_START -->" not in agents_text or "loom host install --host codex --scope user --apply --json" not in agents_text:
        raise AssertionError("metadata-only install did not write Loom bootstrap block to AGENTS.md")
    for unexpected in ("plugins/loom", "plugins/loom/skills", ".agents/skills", "skills", ".loom/bin", ".loom/bootstrap"):
        if (target / unexpected).exists():
            raise AssertionError(f"metadata-only install created {unexpected}")

    state = json.loads((target / ".loom" / "installed-state.json").read_text(encoding="utf-8"))
    if state.get("repo_payload", {}).get("mode") != "metadata-only":
        raise AssertionError("metadata-only installed-state did not declare repo_payload.mode")
    if state.get("skills_provider", {}).get("scope") != "user":
        raise AssertionError("metadata-only installed-state did not declare user skills provider")
    layer_paths = {layer.get("installed_path") for layer in state.get("layers", []) if isinstance(layer, dict)}
    layer_types = {layer.get("layer_type") for layer in state.get("layers", []) if isinstance(layer, dict)}
    if "plugins/loom/skills" in layer_paths or "plugin-embedded-skills" in layer_types:
        raise AssertionError("metadata-only installed-state declared embedded plugin skills")
    if "workstation:codex-loom-plugin" not in layer_paths or "user-level-skills-provider" not in layer_types:
        raise AssertionError("metadata-only installed-state did not model user-level skills provider")

    _, validate = run_json(["installed-state", "validate", "--target", str(target), "--json"], expect=0)
    if validate.get("runtime_state") != "ready":
        raise AssertionError("metadata-only installed-state validate did not pass")

    _, upgrade_plan = run_json(["upgrade-plan", "--target", str(target), "--host", "codex", "--json"], expect=0)
    refresh_action = next((action for action in upgrade_plan.get("actions", []) if action.get("id") == "host-plugin-refresh-boundary"), None)
    if (
        not refresh_action
        or refresh_action.get("command") != "loom host doctor --host codex --scope user --json"
        or refresh_action.get("status") != "separate-command"
        or "does not refresh the Codex workstation plugin cache" not in str(refresh_action.get("reason"))
    ):
        raise AssertionError("upgrade-plan did not redirect Codex plugin refresh intent to host commands")

    status, upgrade_payload = run_json(["upgrade", "--target", str(target), "--host", "codex", "--json"])
    if (
        status == 0
        or upgrade_payload.get("failed_layer") != "upgrade-apply"
        or upgrade_payload.get("host_plugin_refresh", {}).get("id") != "host-plugin-refresh-boundary"
    ):
        raise AssertionError("target upgrade did not expose separate Codex host plugin refresh guidance")

    host_home = tmp / "metadata-only-codex-home"
    host_home.mkdir()
    with isolated_codex_workstation(host_home):
        status, missing_provider = run_json(["host", "verify", "--host", "codex", "--target", str(target), "--json"])
        if (
            status == 0
            or missing_provider.get("result") != "block"
            or missing_provider.get("failed_layer") != "workstation-registration"
        ):
            raise AssertionError("metadata-only host verify did not require Codex user-level provider registration")
        register_fixture_codex_plugin()
        _, host_verify = run_json(["host", "verify", "--host", "codex", "--target", str(target), "--json"], expect=0)
    if host_verify.get("verifies") != "repository-adoption-metadata-and-codex-user-plugin-provider":
        raise AssertionError("metadata-only host verify did not verify repository adoption metadata and Codex provider")
    if host_verify.get("workstation_registration", {}).get("result") != "pass":
        raise AssertionError("metadata-only host verify did not read back Codex provider registration")
    host_paths = {check["path"]: check["status"] for check in host_verify.get("checks", [])}
    if host_paths.get(".loom/installed-state.json") != "pass":
        raise AssertionError("metadata-only host verify did not check installed-state")
    for absent in ("plugins/loom", "plugins/loom/skills", ".agents/skills", "skills", ".loom/bin", ".loom/bootstrap"):
        if host_paths.get(absent) != "pass":
            raise AssertionError(f"metadata-only host verify did not treat absent {absent} as intentional")

    _, skills_check = run_json(["skills", "check", "--target", str(target), "--json"], expect=0)
    metadata_check_output = json.loads(skills_check["checks"][0]["stdout"])
    skill_check_paths = {check["path"]: check["status"] for check in metadata_check_output}
    if skill_check_paths.get("plugins/loom/skills") != "pass" or skill_check_paths.get("skills") != "pass":
        raise AssertionError("metadata-only skills check required a repo skills payload")

    _, detected = run_json(["detect", "--target", str(target), "--json"], expect=0)
    if detected["classification"] != "current":
        raise AssertionError("metadata-only target was not classified as current")

    plugin_payload = target / "plugins" / "loom" / "skills"
    plugin_payload.mkdir(parents=True)
    with isolated_codex_workstation(host_home):
        register_fixture_codex_plugin()
        status, polluted_verify = run_json(["host", "verify", "--host", "codex", "--target", str(target), "--json"])
    if status == 0 or polluted_verify.get("result") != "block":
        raise AssertionError("metadata-only host verify did not block unexpected embedded skills payload")
    old_mode = subprocess.run(
        [sys.executable, str(LOOM), "install", "--target", str(target), "--mode", "plugin", "--json"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    if old_mode.returncode == 0:
        raise AssertionError("loom install still accepted legacy --mode plugin")
    host_help = subprocess.run(
        [sys.executable, str(LOOM), "host", "--help"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    host_help_text = host_help.stdout + host_help.stderr
    if host_help.returncode != 0 or "--mode" in host_help_text or "--skill-id" in host_help_text:
        raise AssertionError("loom host help still exposes legacy install mode or single-skill arguments")
    skills_help = subprocess.run(
        [sys.executable, str(LOOM), "skills", "--help"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    skills_help_text = skills_help.stdout + skills_help.stderr
    if skills_help.returncode != 0 or "sync" in skills_help_text:
        raise AssertionError("loom skills help still exposes downstream skills sync")
    downstream_generate_target = tmp / "downstream-skills-generate"
    downstream_generate_target.mkdir()
    status, downstream_generate = run_json(["skills", "generate", "--target", str(downstream_generate_target), "--apply", "--json"])
    if status == 0 or downstream_generate.get("failed_layer") != "skills-surface":
        raise AssertionError("skills generate still allowed downstream repository skills payload writes")
    for unexpected in ("plugins/loom", "plugins/loom/skills", ".agents/skills", "skills", ".loom/bin", ".loom/bootstrap"):
        if (downstream_generate_target / unexpected).exists():
            raise AssertionError(f"downstream skills generate wrote unsupported repository payload: {unexpected}")
    help_result = subprocess.run(
        [sys.executable, str(LOOM), "--help"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=CLI_CONTRACT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    help_text = help_result.stdout + help_result.stderr
    if help_result.returncode != 0 or "repo-local-wrapper repos keep declared .loom/bin carriers as valid wrappers" in help_text:
        raise AssertionError("loom --help still advertises repo-local-wrapper .loom/bin as current")


def assert_install_upgrade_host_boundary_docs() -> None:
    required = {
        "README.md": [
            "`loom install` and `loom upgrade` manage only the target repository's",
            "`loom host doctor|install|register --host codex --scope user`",
            "Target repository upgrade commands do not refresh the Codex plugin cache.",
        ],
        "README.zh-CN.md": [
            "`loom install` 和 `loom upgrade` 只管理目标仓库的仅元数据启用状态。",
            "`loom host doctor|install|register --host codex --scope user`",
            "目标仓库的 upgrade 命令不会刷新 Codex 插件缓存。",
        ],
        "src/skills/README.md": [
            "loom host doctor --host codex --scope user --json",
            "loom host install --host codex --scope user --apply --json",
            "`loom install` and `loom upgrade` manage that target repository state only",
        ],
    }
    for relative, snippets in required.items():
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            raise AssertionError(f"{relative} missing install/upgrade host boundary snippets: {missing}")


def valid_state(target: Path) -> dict[str, Any]:
    return global_cli_state(target)


GLOBAL_CLI_REQUIRED_COMMANDS = [
    "installed-state validate",
    "detect",
    "doctor",
    "verify",
    "fact-chain",
    "status",
    "shadow-parity",
    "story",
]


def global_cli_state(target: Path) -> dict[str, Any]:
    return {
        "schema_version": "loom-installed-state/v2",
        "installation_id": "fixture-global-cli",
        "target": str(target),
        "upgrade_eligibility": "current",
        "runtime_provider": "global-cli",
        "provider_requirements": {
            "global_cli": {
                "required": True,
                "provider": "loom-cli",
                "authority": "workstation",
                "package": "@mc-and-his-agents/loom",
                "executable": "loom",
                "version_requirement": "v0.13.0",
                "required_commands": list(GLOBAL_CLI_REQUIRED_COMMANDS),
                "compatibility_mode_allowed": False,
            }
        },
        "repo_payload": {
            "mode": "metadata-only",
            "intentional_absent_paths": [
                ".loom/bin",
                "plugins/loom/.codex-plugin/plugin.json",
                "plugins/loom/skills",
                ".agents/skills",
                "skills",
            ],
        },
        "layers": [
            {
                "id": "adoption-metadata",
                "layer_type": "repository-adoption-metadata",
                "installed_path": ".loom/installed-state.json",
                "version_context": {
                    "repo_version": "v0.13.0",
                    "installed_state_schema": "loom-installed-state/v2",
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["repository adoption truth"],
                "consumes": ["user-skills-provider", "global-cli-provider"],
            },
            {
                "id": "user-skills-provider",
                "layer_type": "user-level-skills-provider",
                "installed_path": "workstation:codex-loom-plugin",
                "version_context": {
                    "plugin_surface_version": "v0.13.0",
                    "host_adapter_version": "v0.13.0",
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["Loom scenario skills from user-level Codex plugin"],
                "consumes": [],
            },
            {
                "id": "global-cli-provider",
                "layer_type": "global-cli-runtime-provider",
                "installed_path": "workstation:loom-cli",
                "version_context": {
                    "package": "@mc-and-his-agents/loom",
                    "version_requirement": "v0.13.0",
                },
                "runtime_state": "unknown",
                "upgrade_eligibility": "unknown",
                "provides": ["loom command semantics", "runtime provider"],
                "declared_support": {"commands": list(GLOBAL_CLI_REQUIRED_COMMANDS)},
                "consumes": [],
            },
        ],
        "installation_graph": {
            "layers": ["adoption-metadata", "user-skills-provider", "global-cli-provider"],
            "edges": [
                {"from": "adoption-metadata", "to": "user-skills-provider", "relationship": "requires-external-provider"},
                {"from": "adoption-metadata", "to": "global-cli-provider", "relationship": "requires-runtime-provider"},
            ],
        },
        "skills_provider": {
            "provider": "codex-loom-plugin",
            "scope": "user",
            "required": True,
            "registration_authority": "workstation",
        },
    }


def write_global_cli_fact_chain_fixture(target: Path) -> None:
    replacements = {
        "python3 .loom/bin/loom_init.py bootstrap --target . --write --repair-gitignore": "loom init bootstrap --target . --write --repair-gitignore --json",
        "python3 .loom/bin/loom_init.py verify --target .": "loom verify --target . --json",
        "python3 .loom/bin/loom_init.py fact-chain --target .": "loom fact-chain --target . --json",
        "python3 .loom/bin/loom_flow.py flow resume --target . --item INIT-0001": "loom resume --target . --item INIT-0001 --json",
        "python3 .loom/bin/loom_status.py --target . --item INIT-0001": "loom status --target . --item INIT-0001 --json",
        "python3 .loom/bin/loom_flow.py flow merge-ready --target . --item INIT-0001": "loom merge-ready --target . --item INIT-0001 --json",
        "python3 .loom/bin/loom_flow.py checkpoint merge --target . --item INIT-0001": "loom checkpoint merge --target . --item INIT-0001 --json",
        "python3 .loom/bin/loom_flow.py closeout check --target .": "loom closeout --target . --json",
        "python3 .loom/bin/loom_flow.py reconciliation audit --target .": "loom reconcile --json",
        "python3 .loom/bin/loom_flow.py adopt verify --target .": "loom adopt verify --target . --json",
        "python3 .loom/bin/loom_flow.py governance-profile upgrade --target . --to standard --dry-run": "loom profile upgrade --target . --to standard --dry-run --json",
        "python3 .loom/bin/loom_flow.py governance-profile status --target .": "loom profile status --target . --json",
        "python3 .loom/bin/loom_flow.py governance-profile upgrade-plan --target .": "loom profile upgrade-plan --target . --json",
    }
    fixture_files = {
        ".loom/work-items/INIT-0001.md": REPO_ROOT / "examples/new-project/.loom/work-items/INIT-0001.md",
        ".loom/progress/INIT-0001.md": REPO_ROOT / "examples/new-project/.loom/progress/INIT-0001.md",
        ".loom/status/current.md": REPO_ROOT / "examples/new-project/.loom/status/current.md",
        ".loom/bootstrap/init-result.json": REPO_ROOT / "examples/new-project/.loom/bootstrap/init-result.json",
    }
    for relative, source in fixture_files.items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = source.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        destination.write_text(text, encoding="utf-8")


def write_global_cli_gate_blocker_fixture(target: Path) -> None:
    replacements = {
        "loom fact-chain --target . --json": "python3 .loom/bin/loom_init.py fact-chain --target .",
    }
    fixture_files = {
        ".loom/status/current.md": target / ".loom" / "status" / "current.md",
        ".loom/bootstrap/init-result.json": target / ".loom" / "bootstrap" / "init-result.json",
    }
    for relative, path in fixture_files.items():
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        if relative.endswith("init-result.json"):
            text = text.replace("loom verify --target . --json", "python3 .loom/bin/loom_init.py verify --target .")
        path.write_text(text, encoding="utf-8")


def write_minimal_suite(target: Path, item: str) -> None:
    suite_dir = target / ".loom" / "specs" / item
    suite_dir.mkdir(parents=True)
    (target / ".loom" / "work-items").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "progress").mkdir(parents=True, exist_ok=True)
    (suite_dir / "spec.md").write_text(
        "# Spec\n\n"
        "- Suite path: minimal\n\n"
        "## Scenarios\n\n"
        "- Scenario S1: Minimal suite happy path validates without full-path artifacts.\n\n"
        "## Acceptance Criteria\n\n"
        "- AC-1: Suite validation passes with a legal full-artifact skip rationale.\n"
        "- AC-2: Evidence validation passes with behavior, test, and fresh verification evidence.\n"
        "- AC-3: Carrier validation passes with a primary Work Item carrier.\n\n"
        "- Full suite artifacts not_applicable: rationale: low-risk verify profile fixture; "
        "consumer boundary: minimal suite happy path fixture requires suite validate, evidence validate, "
        "and carrier validate but not full-path artifacts; "
        "recheck condition: profile expands beyond minimal suite validation.\n",
        encoding="utf-8",
    )
    (suite_dir / "plan.md").write_text(
        "# Plan\n\n"
        "- Suite path: minimal\n\n"
        "## Validation\n\n"
        "- S1 -> automated validation evidence: suite validate, suite evidence validate, and suite carrier validate.\n"
        "- AC-1 -> test evidence: suite validate pass payload.\n"
        "- AC-2 -> test evidence: suite evidence validate pass payload.\n"
        "- AC-3 -> test evidence: suite carrier validate pass payload.\n\n"
        "## Minimal Path Applicability Records\n\n"
        "- full-path-artifacts not_applicable rationale: low-risk verify profile fixture; "
        "consumer boundary: minimal suite happy path fixture requires suite validate, evidence validate, "
        "and carrier validate but not full-path artifacts; "
        "recheck condition: profile expands beyond minimal suite validation.\n",
        encoding="utf-8",
    )
    (target / ".loom" / "work-items" / f"{item}.md").write_text(
        f"# {item}\n\n"
        f"- Item ID: {item}\n"
        "- Scope: Minimal suite happy path fixture for source and installed regression checks.\n"
        f"- Spec Entry: .loom/specs/{item}/spec.md\n"
        f"- Plan Entry: .loom/specs/{item}/plan.md\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Validation Entry: suite validate; suite evidence validate; suite carrier validate\n",
        encoding="utf-8",
    )
    (target / ".loom" / "progress" / f"{item}.md").write_text(
        f"# {item} Progress\n\n"
        f"- Item ID: {item}\n"
        "- Current Stop: Minimal suite happy path fixture is ready for validation.\n"
        "- Next Step: Run source and installed suite regression checks.\n"
        "- Latest Validation Summary: fixture validation pending until commands run.\n"
        "- Recovery Boundary: Fixture only; does not author review, merge-ready, closeout, or Project truth.\n"
        "- Current Lane: fixture\n"
        f"- Plan Locator: .loom/specs/{item}/plan.md\n"
        f"- Acceptance Locator: .loom/specs/{item}/spec.md\n"
        f"- Validation Evidence Locator: .loom/specs/{item}/evidence-map.md\n",
        encoding="utf-8",
    )
    (suite_dir / "execution-breakdown.md").write_text(
        "# Execution Breakdown\n\n"
        f"| Unit | Scope | Owner | Status | Validation |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| unit-{item.lower()}-1 | Minimal suite happy path fixture. | loom_check fixture | done | suite validate / evidence validate / carrier validate |\n",
        encoding="utf-8",
    )
    (suite_dir / "evidence-map.md").write_text(
        "# Evidence Map\n\n"
        "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| EV-001 | behavior_evidence | .loom/specs/{item}/spec.md | S1 / AC-1 | {item} / minimal suite behavior | present | fixture evidence only | Re-run suite validate after changing the fixture. |\n"
        f"| EV-002 | test_evidence | .loom/specs/{item}/plan.md | validation plan | {item} / minimal suite tests | present | fixture evidence only | Re-run source and installed checks after changing the fixture. |\n"
        f"| EV-003 | fresh_verification_input | .loom/progress/{item}.md | EV-001 EV-002 | {item} / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after validation changes. |\n",
        encoding="utf-8",
    )
    (suite_dir / "task-carrier.md").write_text(
        "# Task Carrier\n\n"
        "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| repo_tasks_md | .loom/work-items/{item}.md | fixture in progress | in_progress | primary | .loom/work-items/{item}.md | .loom/specs/{item}/execution-breakdown.md#unit-{item.lower()}-1 | .loom/specs/{item}/spec.md#scenario-s1 | .loom/specs/{item}/plan.md#validation | .loom/specs/{item}/plan.md#validation | minimal suite happy path fixture | Recheck before consuming fixture output. |\n",
        encoding="utf-8",
    )


def write_full_suite(target: Path, item: str) -> None:
    suite_dir = target / ".loom" / "specs" / item
    suite_dir.mkdir(parents=True)
    (target / ".loom" / "work-items").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "progress").mkdir(parents=True, exist_ok=True)
    (suite_dir / "suite-index.md").write_text(
        "# Full Suite Index\n\n"
        "- Schema marker: loom-full-suite-index/v1\n"
        "- Suite path: full\n\n"
        "## Artifact Inventory\n\n"
        "- spec.md: required\n"
        "- plan.md: required\n"
        "- research.md: conditional / present\n"
        "- contracts.md: conditional / present\n"
        "- readiness-checklist.md: conditional / present\n"
        "- evidence-map.md: closeout evidence / present\n"
        "- consistency-analysis.md: consistency evidence / present\n"
        "- execution-breakdown.md: task breakdown / present\n"
        "- task-carrier.md: task carrier / present\n",
        encoding="utf-8",
    )
    (suite_dir / "spec.md").write_text(
        "# Spec\n\n"
        "## Scenarios\n\n"
        "### Scenario S1\n\n"
        "Given a full suite fixture with required and conditional artifacts\n"
        "When suite validation runs\n"
        "Then the full path passes without bypass records\n\n"
        "### Scenario S2\n\n"
        "Given behavior and test evidence rows\n"
        "When evidence validation runs\n"
        "Then the evidence map is consumable by review, merge-ready, and closeout\n\n"
        "### Scenario S3\n\n"
        "Given a primary task carrier row\n"
        "When carrier validation runs\n"
        "Then Work Item, breakdown, spec, and plan backlinks are consumable\n\n"
        "## Acceptance Criteria\n\n"
        "- AC-1: Suite inspect reports a full path from suite-index.md.\n"
        "- AC-2: Suite validate passes with required and conditional artifacts present.\n"
        "- AC-3: Suite evidence validate passes with behavior, test, and fresh verification inputs.\n"
        "- AC-4: Suite carrier validate passes with a primary Work Item carrier.\n",
        encoding="utf-8",
    )
    (suite_dir / "plan.md").write_text(
        "# Plan\n\n"
        "- Suite path: full\n\n"
        "## Validation\n\n"
        "- S1 -> automated validation evidence: suite inspect and suite validate full pass payloads.\n"
        "- S2 -> automated validation evidence: suite evidence validate pass payload.\n"
        "- S3 -> automated validation evidence: suite carrier validate pass payload.\n"
        "- AC-1 -> test evidence: path decision locator is suite-index.md.\n"
        "- AC-2 -> test evidence: required and conditional artifacts are present.\n"
        "- AC-3 -> test evidence: evidence-map.md rows cover behavior, tests, and fresh verification.\n"
        "- AC-4 -> test evidence: task-carrier.md row backlinks to Work Item and execution breakdown.\n",
        encoding="utf-8",
    )
    (suite_dir / "research.md").write_text(
        "# Research\n\n"
        "- Finding: full suite happy path requires no bypass record when conditional artifacts are present.\n"
        "- Source: docs/methodology/harness/full-spec-suite-cli-surface.md\n",
        encoding="utf-8",
    )
    (suite_dir / "contracts.md").write_text(
        "# Contracts\n\n"
        "- Suite validator consumes docs/methodology/harness/full-spec-suite-cli-surface.md.\n"
        "- Evidence validator consumes docs/methodology/templates/evidence-map.md.\n"
        "- Carrier validator consumes docs/methodology/harness/task-carrier-contract.md.\n",
        encoding="utf-8",
    )
    (suite_dir / "readiness-checklist.md").write_text(
        "# Readiness Checklist\n\n"
        "- [x] Full suite path decision is present.\n"
        "- [x] Required artifacts are present.\n"
        "- [x] Conditional artifacts are present for this fixture.\n"
        "- [x] Evidence and carrier artifacts are present for gate consumption.\n",
        encoding="utf-8",
    )
    (target / ".loom" / "work-items" / f"{item}.md").write_text(
        f"# {item}\n\n"
        f"- Item ID: {item}\n"
        "- Scope: Full suite happy path fixture for source and installed regression checks.\n"
        f"- Spec Entry: .loom/specs/{item}/spec.md\n"
        f"- Plan Entry: .loom/specs/{item}/plan.md\n"
        f"- Suite Entry: .loom/specs/{item}/suite-index.md\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Validation Entry: suite validate; suite evidence validate; suite carrier validate\n",
        encoding="utf-8",
    )
    (target / ".loom" / "progress" / f"{item}.md").write_text(
        f"# {item} Progress\n\n"
        f"- Item ID: {item}\n"
        "- Current Stop: Full suite happy path fixture is ready for validation.\n"
        "- Next Step: Run source and installed full suite regression checks.\n"
        "- Latest Validation Summary: fixture validation pending until commands run.\n"
        "- Recovery Boundary: Fixture only; does not author review, merge-ready, closeout, or Project truth.\n"
        "- Current Lane: fixture\n"
        f"- Plan Locator: .loom/specs/{item}/plan.md\n"
        f"- Acceptance Locator: .loom/specs/{item}/spec.md\n"
        f"- Validation Evidence Locator: .loom/specs/{item}/evidence-map.md\n",
        encoding="utf-8",
    )
    (suite_dir / "execution-breakdown.md").write_text(
        "# Execution Breakdown\n\n"
        "| Unit | Scope | Owner | Status | Validation |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| unit-{item.lower()}-1 | Full suite happy path fixture. | loom_check fixture | done | suite validate / evidence validate / carrier validate |\n",
        encoding="utf-8",
    )
    (suite_dir / "consistency-analysis.md").write_text(
        "# Consistency Analysis\n\n"
        "| Source | Target | Status | Evidence |\n"
        "| --- | --- | --- | --- |\n"
        f"| .loom/specs/{item}/spec.md | .loom/specs/{item}/plan.md | consistent | S1-S3 and AC-1-AC-4 mapped |\n"
        f"| .loom/specs/{item}/evidence-map.md | .loom/specs/{item}/task-carrier.md | consistent | EV-001 through EV-004 bind to {item} |\n",
        encoding="utf-8",
    )
    (suite_dir / "evidence-map.md").write_text(
        "# Evidence Map\n\n"
        "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| EV-001 | behavior_evidence | .loom/specs/{item}/spec.md | S1 S2 S3 / AC-1 | {item} / full suite behavior | present | fixture evidence only | Re-run suite validate after changing the fixture. |\n"
        f"| EV-002 | test_evidence | .loom/specs/{item}/plan.md | AC-2 AC-3 AC-4 | {item} / full suite tests | present | fixture evidence only | Re-run source and installed checks after changing the fixture. |\n"
        f"| EV-003 | behavior_evidence | .loom/specs/{item}/consistency-analysis.md | consistency analysis | {item} / full suite consistency | present | review / merge-ready / closeout evidence | Refresh consistency analysis after spec or plan changes. |\n"
        f"| EV-004 | fresh_verification_input | .loom/progress/{item}.md | EV-001 EV-002 EV-003 | {item} / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after validation changes. |\n",
        encoding="utf-8",
    )
    (suite_dir / "task-carrier.md").write_text(
        "# Task Carrier\n\n"
        "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| repo_tasks_md | .loom/work-items/{item}.md | fixture in progress | in_progress | primary | .loom/work-items/{item}.md | .loom/specs/{item}/execution-breakdown.md#unit-{item.lower()}-1 | .loom/specs/{item}/spec.md#scenario-s1 | .loom/specs/{item}/plan.md#validation | .loom/specs/{item}/plan.md#validation | full suite happy path fixture | Recheck before consuming fixture output. |\n",
        encoding="utf-8",
    )


def assert_minimal_suite_happy_path_fixture(target: Path, item: str) -> None:
    suite_minimal = run_suite_inspect_fixture(target, item)
    minimal_payload = suite_minimal.get("payload", {})
    minimal_inventory = {entry["artifact"]: entry for entry in minimal_payload.get("artifact_inventory", [])}
    if (
        minimal_payload.get("suite_path") != "minimal"
        or minimal_payload.get("path_decision_locator") != f".loom/specs/{item}/spec.md"
        or minimal_payload.get("spec_locator") != f".loom/specs/{item}/spec.md"
        or minimal_payload.get("plan_locator") != f".loom/specs/{item}/plan.md"
        or minimal_inventory.get("spec.md", {}).get("locator") != f".loom/specs/{item}/spec.md"
        or minimal_inventory.get("plan.md", {}).get("locator") != f".loom/specs/{item}/plan.md"
        or minimal_payload.get("missing_inputs")
    ):
        raise AssertionError("suite inspect minimal happy path payload drifted")
    suite_minimal_validate = run_suite_validate_fixture(target, item)
    if (
        suite_minimal_validate.get("result") != "pass"
        or suite_minimal_validate.get("failed_layer") is not None
        or suite_minimal_validate.get("fail_closed_reason") is not None
        or suite_minimal_validate.get("missing_inputs")
        or suite_minimal_validate.get("blocking_gaps")
        or suite_minimal_validate.get("advisory_gaps")
        or not suite_minimal_validate.get("payload", {}).get("not_applicable_rationale")
        or "docs/methodology/harness/full-spec-suite-cli-surface.md"
        not in suite_minimal_validate.get("payload", {}).get("consumed_contracts", [])
    ):
        raise AssertionError("suite validate minimal happy path payload drifted")
    suite_evidence_validate = run_suite_evidence_validate_fixture(target, item)
    if (
        suite_evidence_validate.get("result") != "pass"
        or suite_evidence_validate.get("missing_inputs")
        or suite_evidence_validate.get("blocking_gaps")
        or suite_evidence_validate.get("payload", {}).get("evidence_map", {}).get("status") != "present"
    ):
        raise AssertionError("suite evidence validate minimal happy path payload drifted")
    suite_carrier_validate = run_suite_carrier_validate_fixture(target, item)
    if (
        suite_carrier_validate.get("result") != "pass"
        or suite_carrier_validate.get("missing_inputs")
        or suite_carrier_validate.get("blocking_gaps")
        or suite_carrier_validate.get("payload", {}).get("task_carrier", {}).get("status") != "present"
    ):
        raise AssertionError("suite carrier validate minimal happy path payload drifted")


def assert_full_suite_happy_path_fixture(target: Path, item: str) -> None:
    suite_full = run_suite_inspect_fixture(target, item)
    full_payload = suite_full.get("payload", {})
    full_inventory = {entry["artifact"]: entry for entry in full_payload.get("artifact_inventory", [])}
    expected_locators = {
        "suite-index.md": f".loom/specs/{item}/suite-index.md",
        "spec.md": f".loom/specs/{item}/spec.md",
        "plan.md": f".loom/specs/{item}/plan.md",
        "research.md": f".loom/specs/{item}/research.md",
        "contracts.md": f".loom/specs/{item}/contracts.md",
        "readiness-checklist.md": f".loom/specs/{item}/readiness-checklist.md",
        "evidence-map.md": f".loom/specs/{item}/evidence-map.md",
        "consistency-analysis.md": f".loom/specs/{item}/consistency-analysis.md",
        "execution-breakdown.md": f".loom/specs/{item}/execution-breakdown.md",
        "task-carrier": f".loom/specs/{item}/task-carrier.md",
    }
    if (
        full_payload.get("suite_path") != "full"
        or full_payload.get("suite_locator") != f".loom/specs/{item}/suite-index.md"
        or full_payload.get("path_decision_locator") != f".loom/specs/{item}/suite-index.md"
        or full_payload.get("missing_inputs")
    ):
        raise AssertionError("suite inspect full happy path payload drifted")
    for artifact, locator in expected_locators.items():
        entry = full_inventory.get(artifact, {})
        if entry.get("locator") != locator or entry.get("status") != "present":
            raise AssertionError(f"suite inspect full locator drifted for {artifact}")
        if str(entry.get("locator", "")).startswith("/"):
            raise AssertionError("suite inspect emitted absolute full suite artifact locator")
    suite_full_validate = run_suite_validate_fixture(target, item)
    mapping = suite_full_validate.get("payload", {}).get("spec_plan_mapping", {})
    if (
        suite_full_validate.get("result") != "pass"
        or suite_full_validate.get("failed_layer") is not None
        or suite_full_validate.get("fail_closed_reason") is not None
        or suite_full_validate.get("missing_inputs")
        or suite_full_validate.get("blocking_gaps")
        or suite_full_validate.get("advisory_gaps")
        or suite_full_validate.get("payload", {}).get("not_applicable_rationale")
        or mapping.get("missing_scenarios")
        or mapping.get("missing_acceptance")
        or "docs/methodology/harness/full-spec-suite-cli-surface.md"
        not in suite_full_validate.get("payload", {}).get("consumed_contracts", [])
    ):
        raise AssertionError("suite validate full happy path payload drifted")
    suite_evidence_validate = run_suite_evidence_validate_fixture(target, item)
    if (
        suite_evidence_validate.get("result") != "pass"
        or suite_evidence_validate.get("missing_inputs")
        or suite_evidence_validate.get("blocking_gaps")
        or suite_evidence_validate.get("payload", {}).get("evidence_map", {}).get("status") != "present"
        or suite_evidence_validate.get("payload", {}).get("evidence_map", {}).get("row_count") != 4
        or "docs/methodology/templates/evidence-map.md"
        not in suite_evidence_validate.get("payload", {}).get("consumed_contracts", [])
    ):
        raise AssertionError("suite evidence validate full happy path payload drifted")
    suite_carrier_validate = run_suite_carrier_validate_fixture(target, item)
    if (
        suite_carrier_validate.get("result") != "pass"
        or suite_carrier_validate.get("missing_inputs")
        or suite_carrier_validate.get("blocking_gaps")
        or suite_carrier_validate.get("payload", {}).get("task_carrier", {}).get("status") != "present"
        or "docs/methodology/harness/task-carrier-contract.md"
        not in suite_carrier_validate.get("payload", {}).get("consumed_contracts", [])
    ):
        raise AssertionError("suite carrier validate full happy path payload drifted")


def assert_generated_skills_surface_parity_contract(skills_check: dict[str, Any]) -> None:
    if (
        skills_check.get("command") != "skills check"
        or skills_check.get("result") != "pass"
        or skills_check.get("schema") != "loom-skills-surface/v1"
        or skills_check.get("root_entry") != "loom-init"
        or skills_check.get("failed_layer") is not None
        or skills_check.get("fail_closed_reason") is not None
    ):
        raise AssertionError("skills check did not expose a passing generated skills parity contract")
    checks = skills_check.get("checks")
    if not isinstance(checks, list) or not any(
        isinstance(check, dict)
        and "tools/skills_surface.py check" in str(check.get("command", ""))
        and check.get("returncode") == 0
        and "skills surface check: OK" in str(check.get("stdout", ""))
        for check in checks
    ):
        raise AssertionError("skills check did not consume tools/skills_surface.py check")

    stable_surface_files = (
        "registry.json",
        "install-layout.json",
        "upgrade-contract.json",
        "distribution-and-adapter-contract.md",
        "route-matrix.md",
        "shared/references/templates/spec-suite.md",
        "shared/references/templates/evidence-map.md",
        "shared/references/templates/consistency-analysis.md",
        "shared/references/harness/task-carrier-contract.md",
    )
    for relative in stable_surface_files:
        source = REPO_ROOT / "src" / "skills" / relative
        generated = REPO_ROOT / "skills" / relative
        if not source.is_file() or not generated.is_file():
            raise AssertionError(f"generated skills surface missing parity file: {relative}")
        if source.read_bytes() != generated.read_bytes():
            raise AssertionError(f"generated skills surface drifted from src/skills: {relative}")

    registry = json.loads((REPO_ROOT / "src/skills/registry.json").read_text(encoding="utf-8"))
    for entry in registry.get("entries", []):
        skill_id = entry.get("id")
        if not isinstance(skill_id, str) or not skill_id:
            raise AssertionError("src/skills registry contains an invalid skill entry")
        for payload_root in (REPO_ROOT / "skills", REPO_ROOT / "plugins" / "loom" / "skills"):
            package_root = payload_root / skill_id
            if not (package_root / "SKILL.md").is_file():
                raise AssertionError(f"{payload_root.relative_to(REPO_ROOT)}/{skill_id} missing SKILL.md")
            if not (package_root / "contract.json").is_file():
                raise AssertionError(f"{payload_root.relative_to(REPO_ROOT)}/{skill_id} missing contract.json")
            if (package_root / "loom-package.json").exists() or (package_root / ".loom-runtime").exists():
                raise AssertionError(f"{payload_root.relative_to(REPO_ROOT)}/{skill_id} still exposes single-skill package artifacts")


def write_governance_chain_fixture(target: Path, *, issue_open: bool = False, project_done: bool = True) -> dict[str, str]:
    item = "WI-1153"
    issue_number = "1153"
    pr_number = "1199"
    branch = "work/1153-pr-gate-closeout-integration"
    target_branch = "main"
    validation_summary = "fixture validation passed for PR gate, merge-ready, closeout, issue, Project, target branch, and merge commit evidence."

    write_full_suite(target, item)
    work_item = target / ".loom" / "work-items" / f"{item}.md"
    work_item.write_text(
        "# WI-1153\n\n"
        "## Static Facts\n\n"
        f"- Item ID: {item}\n"
        "- Goal: Fixture proves the end-to-end governance chain consumes suite automation.\n"
        "- Scope: Non-mutating closeout/reconciliation fixture only; PR merged alone is not closeout complete.\n"
        f"- Execution Path: issue #{issue_number} -> branch {branch} -> target-local workspace `.` -> PR #{pr_number}.\n"
        "- Workspace Entry: .\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Review Entry: .loom/reviews/{item}.json\n"
        "- Validation Entry: fixture PR gate; merge-ready; closeout; reconciliation\n"
        "- Closing Condition: closeout consumes merged PR, issue closed, Project Done, target branch, merge commit, review, merge-ready, and suite evidence together.\n"
        "\n## Associated Artifacts\n\n"
        f"- `.loom/work-items/{item}.md`\n"
        f"- `.loom/progress/{item}.md`\n"
        f"- `.loom/reviews/{item}.json`\n"
        f"- `.loom/specs/{item}/spec.md`\n"
        f"- `.loom/specs/{item}/plan.md`\n"
        f"- `.loom/specs/{item}/evidence-map.md`\n"
        f"- `.loom/specs/{item}/task-carrier.md`\n",
        encoding="utf-8",
    )
    progress = target / ".loom" / "progress" / f"{item}.md"
    progress.write_text(
        f"# {item} Progress\n\n"
        "## Dynamic Facts\n\n"
        f"- Item ID: {item}\n"
        "- Current Checkpoint: merge-ready\n"
        "- Current Stop: Fixture has retained review and merge-ready evidence for closeout consumption.\n"
        "- Next Step: Run non-mutating closeout and reconciliation fixture checks.\n"
        "- Blockers: None recorded.\n"
        f"- Latest Validation Summary: {validation_summary}\n"
        "- Recovery Boundary: Fixture only; does not mutate GitHub issue, PR, Project, or parent truth.\n"
        "- Current Lane: full-spec-suite-cli/e2e-governance/closeout-integration\n"
        "\n## Execution Ledger\n\n"
        "- Ledger Binding: recovery_entry\n"
        f"- Plan Locator: .loom/specs/{item}/plan.md\n"
        f"- Acceptance Locator: .loom/specs/{item}/spec.md\n"
        f"- Validation Evidence Locator: .loom/specs/{item}/evidence-map.md\n"
        "- Handoff Notes Locator: not_applicable\n"
        "- Evidence Freshness: current\n",
        encoding="utf-8",
    )

    subprocess.run(["git", "init", "-b", target_branch], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=target, check=True)
    (target / "README.md").write_text("# Governance Chain Fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture base"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "checkout", "-b", branch], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (target / "fixture-change.txt").write_text("PR head evidence\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture pr head"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()

    (target / ".loom" / "reviews").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "reviews" / f"{item}.json").write_text(
        json.dumps(
            {
                "schema_version": "loom-review/v1",
                "item_id": item,
                "decision": "allow",
                "kind": "code_review",
                "summary": "Fixture implementation review allows closeout integration consumption.",
                "reviewer": "codex",
                "authored_at": "2026-05-29T00:00:00Z",
                "reviewed_head": head_sha,
                "reviewed_validation_summary": validation_summary,
                "semantic_review_disposition": {
                    "status": "passed",
                    "reason": "authored implementation review approved the fixture.",
                },
                "fallback_to": None,
                "findings": [],
                "blocking_issues": [],
                "follow_ups": [],
                "consumed_inputs": {
                    "work_item": f".loom/work-items/{item}.md",
                    "recovery_entry": f".loom/progress/{item}.md",
                    "suite_evidence_map": f".loom/specs/{item}/evidence-map.md",
                    "suite_task_carriers": [f".loom/specs/{item}/task-carrier.md"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    attempt_dir = target / ".loom" / "runtime" / "attempts" / item
    attempt_dir.mkdir(parents=True, exist_ok=True)
    attempt_payload = {
        "schema_version": "loom-execution-attempt/v1",
        "attempt_id": f"{item}-merge-ready-fixture",
        "item_id": item,
        "command": "flow",
        "operation": "merge-ready",
        "result": "pass",
        "created_at": "2026-05-30T00:00:00Z",
        "head_sha": head_sha,
        "branch": branch,
        "workspace": {"entry": ".", "path": "."},
        "failure": {
            "category": "none",
            "execution_classification": "none",
            "execution_summary": "fixture merge-ready pass",
            "missing_inputs": [],
            "fallback_to": None,
        },
        "steps": [],
        "evidence": {
            "status": "present",
            "locator": f".loom/runtime/attempts/{item}/{item}-merge-ready-fixture.json",
            "latest_locator": f".loom/runtime/attempts/{item}/latest.json",
        },
    }
    for name in (f"{item}-merge-ready-fixture.json", "latest.json"):
        (attempt_dir / name).write_text(json.dumps(attempt_payload, indent=2) + "\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture retained closeout evidence"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run(["git", "checkout", target_branch], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "merge", "--no-ff", branch, "-m", "fixture merge"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    merge_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    origin = target.parent / f"{target.name}-origin.git"
    subprocess.run(["git", "init", "--bare", str(origin)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "remote", "add", "origin", str(origin)], cwd=target, check=True)
    subprocess.run(["git", "push", "-u", "origin", target_branch], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    fixture_dir = target / ".loom" / "fixtures" / "WI-1153"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    issue_payload = {
        "id": "ISSUE_fixture_1153",
        "number": int(issue_number),
        "state": "OPEN" if issue_open else "CLOSED",
        "title": "WI fixture",
        "url": f"https://github.com/owner/repo/issues/{issue_number}",
        "labels": ["work-item"],
    }
    pr_payload = {
        "number": int(pr_number),
        "state": "MERGED",
        "title": "PR fixture",
        "body": f"Loom Work Item: {item}\nBranch: {branch}\nHead SHA: {head_sha}\n",
        "url": f"https://github.com/owner/repo/pull/{pr_number}",
        "isDraft": False,
        "mergedAt": "2026-05-30T00:00:00Z",
        "mergeCommit": {"oid": merge_commit},
        "mergeStateStatus": "MERGEABLE",
        "headRefName": branch,
        "headRefOid": head_sha,
        "baseRefName": target_branch,
    }
    project_payload = {
        "project_id": "PROJECT_fixture",
        "status_field_id": "STATUS_fixture",
        "done_option_id": "DONE_fixture",
        "items": [
            {
                "id": "PROJECT_ITEM_issue_1153",
                "status": "Done" if project_done else "In Progress",
                "content": {"type": "Issue", "number": int(issue_number), "title": "WI fixture"},
            },
            {
                "id": "PROJECT_ITEM_pr_1199",
                "status": "Done",
                "content": {"type": "PullRequest", "number": int(pr_number), "title": "PR fixture"},
            },
        ],
    }
    checks_payload = [
        {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
        {"name": "loom-check", "conclusion": "SUCCESS", "status": "COMPLETED"},
    ]
    for filename, payload in (
        ("issue.json", issue_payload),
        ("pr.json", pr_payload),
        ("project.json", project_payload),
        ("checks.json", checks_payload),
        ("branch-protection.json", {"required_status_checks": {"contexts": []}}),
        ("ruleset.json", []),
    ):
        (fixture_dir / filename).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {
        "item": item,
        "issue": issue_number,
        "pr": pr_number,
        "branch": branch,
        "head_sha": head_sha,
        "merge_commit": merge_commit,
        "issue_file": ".loom/fixtures/WI-1153/issue.json",
        "pr_file": ".loom/fixtures/WI-1153/pr.json",
        "project_file": ".loom/fixtures/WI-1153/project.json",
        "checks_file": ".loom/fixtures/WI-1153/checks.json",
        "branch_protection_file": ".loom/fixtures/WI-1153/branch-protection.json",
        "ruleset_file": ".loom/fixtures/WI-1153/ruleset.json",
    }


def write_semantic_review_pr_gate_fixture(target: Path) -> dict[str, str]:
    item = "WI-1287"
    branch = "work/1287-1288-review-head-binding"
    validation_summary = "git diff --check; targeted pr-gate semantic review disposition fixtures passed."
    write_full_suite(target, item)
    suite_dir = target / ".loom" / "specs" / item
    (suite_dir / "implementation-contract.md").write_text(
        "# Implementation Contract\n\n"
        "- Contract: pr-gate consumes semantic_review_disposition from the authored review record.\n"
        "- Boundary: PR payload fixture binds only Work Item, branch, and head SHA.\n",
        encoding="utf-8",
    )
    (target / ".github").mkdir(parents=True, exist_ok=True)
    (target / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text(
        "## Summary\n\n- Problem:\n- Scope:\n\n"
        "## Validation\n\n- [ ] Verified locally\n\n"
        "## Risks And Follow-ups\n\n- Risks:\n- Follow-ups:\n\n"
        "## Related Work\n\n- Loom Work Item:\n",
        encoding="utf-8",
    )
    (target / ".gitignore").write_text(".loom/fixtures/\n", encoding="utf-8")
    work_item = target / ".loom" / "work-items" / f"{item}.md"
    work_item.write_text(
        f"# {item}\n\n"
        "## Static Facts\n\n"
        f"- Item ID: {item}\n"
        "- Goal: Fixture proves semantic_review_disposition and PR head binding enforcement.\n"
        "- Scope: `fixture-change.txt`, `.loom/reviews/WI-1287.json`, and PR payload fixture only.\n"
        f"- Execution Path: issue #1287/#1288 -> branch {branch} -> target-local workspace `.` -> PR #1288.\n"
        "- Workspace Entry: .\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Review Entry: .loom/reviews/{item}.json\n"
        f"- Validation Entry: {validation_summary}\n"
        "- Closing Condition: pr-gate consumes current-head semantic review disposition.\n"
        "\n## Associated Artifacts\n\n"
        f"- `.loom/work-items/{item}.md`\n"
        f"- `.loom/progress/{item}.md`\n"
        f"- `.loom/reviews/{item}.json`\n"
        f"- `.loom/specs/{item}/spec.md`\n"
        f"- `.loom/specs/{item}/plan.md`\n",
        encoding="utf-8",
    )
    progress = target / ".loom" / "progress" / f"{item}.md"
    progress.write_text(
        f"# {item} Progress\n\n"
        "## Dynamic Facts\n\n"
        f"- Item ID: {item}\n"
        "- Current Checkpoint: merge\n"
        "- Current Stop: Fixture is ready for pr-gate semantic disposition checks.\n"
        "- Next Step: Run pr-gate semantic disposition fixtures.\n"
        "- Blockers: None recorded.\n"
        f"- Latest Validation Summary: {validation_summary}\n"
        "- Recovery Boundary: Fixture only; no host writes.\n"
        "- Current Lane: pr-gate-fixture\n"
        "\n## Execution Ledger\n\n"
        "- Ledger Binding: recovery_entry\n"
        f"- Plan Locator: .loom/specs/{item}/plan.md\n"
        f"- Acceptance Locator: .loom/specs/{item}/spec.md\n"
        f"- Validation Evidence Locator: .loom/specs/{item}/evidence-map.md\n"
        "- Handoff Notes Locator: not_applicable\n"
        "- Evidence Freshness: current\n",
        encoding="utf-8",
    )
    status = target / ".loom" / "status" / "current.md"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(
        "# Current Status\n\n"
        "## Derived Fact Chain View\n\n"
        f"- Item ID: {item}\n"
        "- Goal: Fixture proves semantic_review_disposition and PR head binding enforcement.\n"
        "- Scope: `fixture-change.txt`, `.loom/reviews/WI-1287.json`, and PR payload fixture only.\n"
        f"- Execution Path: issue #1287/#1288 -> branch {branch} -> target-local workspace `.` -> PR #1288.\n"
        "- Workspace Entry: .\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Review Entry: .loom/reviews/{item}.json\n"
        f"- Validation Entry: {validation_summary}\n"
        "- Closing Condition: pr-gate consumes current-head semantic review disposition.\n"
        "- Current Checkpoint: merge\n"
        "- Current Stop: Fixture is ready for pr-gate semantic disposition checks.\n"
        "- Next Step: Run pr-gate semantic disposition fixtures.\n"
        "- Blockers: None recorded.\n"
        f"- Latest Validation Summary: {validation_summary}\n"
        "- Recovery Boundary: Fixture only; no host writes.\n"
        "- Current Lane: pr-gate-fixture\n\n"
        "## Runtime Evidence\n\n"
        "- Run Entry: not_applicable\n"
        "- Logs Entry: not_applicable\n"
        "- Diagnostics Entry: not_applicable\n"
        "- Verification Entry: targeted pr-gate semantic disposition fixture\n"
        "- Lane Entry: pr-gate-fixture\n\n"
        "## Sources\n\n"
        f"- Static Truth: .loom/work-items/{item}.md\n"
        f"- Dynamic Truth: .loom/progress/{item}.md\n"
        "- Locator Truth: .loom/bootstrap/init-result.json\n"
        "- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .\n",
        encoding="utf-8",
    )
    init_result = target / ".loom" / "bootstrap" / "init-result.json"
    init_result.parent.mkdir(parents=True, exist_ok=True)
    init_result.write_text(
        json.dumps(
            {
                "fact_chain": {
                    "read_entry": "python3 .loom/bin/loom_init.py fact-chain --target .",
                    "mode": "fixture",
                    "entry_points": {
                        "current_item_id": item,
                        "work_item": f".loom/work-items/{item}.md",
                        "recovery_entry": f".loom/progress/{item}.md",
                        "status_surface": ".loom/status/current.md",
                    },
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=target, check=True)
    subprocess.run(["git", "checkout", "-b", branch], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (target / "fixture-change.txt").write_text("semantic review disposition fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture reviewed head"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    reviewed_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    review_path = target / ".loom" / "reviews" / f"{item}.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    spec_review_payload = {
        "schema_version": "loom-review/v1",
        "item_id": item,
        "decision": "allow",
        "kind": "spec_review",
        "summary": "Fixture spec review allows semantic disposition fixture consumption.",
        "reviewer": "codex",
        "reviewed_head": reviewed_head,
        "reviewed_validation_summary": validation_summary,
        "fallback_to": None,
        "findings": [],
        "blocking_issues": [],
        "follow_ups": [],
        "consumed_inputs": {
            "work_item": f".loom/work-items/{item}.md",
            "spec": f".loom/specs/{item}/spec.md",
            "plan": f".loom/specs/{item}/plan.md",
            "implementation_contract": f".loom/specs/{item}/implementation-contract.md",
        },
    }
    (target / ".loom" / "reviews" / f"{item}.spec.json").write_text(
        json.dumps(spec_review_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    review_payload = {
        "schema_version": "loom-review/v1",
        "item_id": item,
        "decision": "allow",
        "kind": "code_review",
        "summary": "Fixture implementation review allows semantic disposition gate consumption.",
        "reviewer": "codex",
        "authored_at": "2026-05-29T00:00:00Z",
        "reviewed_head": reviewed_head,
        "reviewed_validation_summary": validation_summary,
        "semantic_review_disposition": {
            "status": "passed",
            "reason": "authored implementation review approved the fixture.",
        },
        "fallback_to": None,
        "findings": [],
        "blocking_issues": [],
        "follow_ups": [],
        "consumed_inputs": {
            "work_item": f".loom/work-items/{item}.md",
            "recovery_entry": f".loom/progress/{item}.md",
            "suite_evidence_map": f".loom/specs/{item}/evidence-map.md",
            "suite_task_carriers": [f".loom/specs/{item}/task-carrier.md"],
        },
    }
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture review carrier"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    fixture_dir = target / ".loom" / "fixtures" / item
    fixture_dir.mkdir(parents=True, exist_ok=True)
    pr_file = fixture_dir / "pr.json"
    pr_payload = {
        "number": 1288,
        "state": "OPEN",
        "title": "semantic review disposition fixture",
        "body": f"Loom Work Item: {item}\nBranch: {branch}\nHead SHA: {head_sha}\n",
        "url": "https://github.com/owner/repo/pull/1288",
        "isDraft": False,
        "headRefName": branch,
        "headRefOid": head_sha,
        "baseRefName": "main",
    }
    pr_file.write_text(json.dumps(pr_payload, indent=2) + "\n", encoding="utf-8")
    return {
        "item": item,
        "branch": branch,
        "review_path": f".loom/reviews/{item}.json",
        "pr_file": f".loom/fixtures/{item}/pr.json",
        "reviewed_head": reviewed_head,
        "head_sha": head_sha,
        "validation_summary": validation_summary,
    }


def commit_fixture_file(target: Path, path: str, message: str) -> str:
    subprocess.run(["git", "add", path], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()


def update_fixture_pr_head(target: Path, fixture: dict[str, str], *, state: str = "OPEN", extra: dict[str, Any] | None = None) -> None:
    pr_path = target / fixture["pr_file"]
    payload = json.loads(pr_path.read_text(encoding="utf-8"))
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    payload["state"] = state
    payload["headRefOid"] = head_sha
    payload["body"] = f"Loom Work Item: {fixture['item']}\nBranch: {fixture['branch']}\nHead SHA: {head_sha}\n"
    if extra:
        payload.update(extra)
    pr_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def semantic_pr_gate_fixture_payload(
    target: Path,
    fixture: dict[str, str],
    *,
    surface: str | None = None,
    body_file: str | None = None,
    compare_body_file: str | None = None,
    gate_freeze_snapshot_file: str | None = None,
) -> dict[str, Any]:
    command = [
        "pr-gate",
        "check",
        "--target",
        str(target),
        "--item",
        fixture["item"],
        "--pr-payload-file",
        fixture["pr_file"],
    ]
    if surface:
        command.extend(["--surface", surface])
    if body_file:
        command.extend(["--body-file", body_file])
    if compare_body_file:
        command.extend(["--compare-body-file", compare_body_file])
    if gate_freeze_snapshot_file:
        command.extend(["--gate-freeze-snapshot-file", gate_freeze_snapshot_file])
    _, payload = run_flow_json(command)
    return payload


def gate_freeze_fixture_payload(target: Path, fixture: dict[str, str]) -> dict[str, Any]:
    _, payload = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--pr-payload-file",
            fixture["pr_file"],
        ]
    )
    return payload


def write_hosted_freeze_admission_inputs(target: Path) -> None:
    write_governance_metadata_contract_fixture(target)
    install_bootstrapped_runtime(target)
    source = target / ".loom" / "companion" / "README.md"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    shadow_dir = target / ".loom" / "shadow"
    shadow_dir.mkdir(parents=True, exist_ok=True)
    shadow_surfaces: dict[str, dict[str, str]] = {}
    for surface in ("admission", "review", "merge_ready", "closeout"):
        slug = surface.replace("_", "-")
        loom_locator = f".loom/shadow/{slug}-loom.json"
        repo_locator = f".loom/shadow/{slug}-repo.json"
        payload = {
            "surface": surface,
            "result": "match",
            "source_files": [".loom/companion/README.md"],
            "source_sha256": {".loom/companion/README.md": source_hash},
        }
        (target / loom_locator).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (target / repo_locator).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        shadow_surfaces[surface] = {
            "summary": f"Fixture {surface} shadow parity is current.",
            "loom_locator": loom_locator,
            "repo_locator": repo_locator,
        }
    (target / ".loom" / "companion" / "interop.json").write_text(
        json.dumps(
            {
                "schema_version": "loom-repo-interop/v1",
                "host_adapters": [],
                "repo_native_carriers": [],
                "shadow_surfaces": shadow_surfaces,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def assert_hosted_freeze_admission_pr_gate_fixture(tmp: Path) -> None:
    target = tmp / "hosted-freeze-admission"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    write_hosted_freeze_admission_inputs(target)
    subprocess.run(["git", "add", "."], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["git", "commit", "-m", "fixture hosted freeze admission inputs"],
        cwd=target,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    update_fixture_pr_head(target, fixture)
    record_current_fixture_review(target, fixture)
    append_governance_intensity_metadata_body(target, fixture)

    pr_payload = json.loads((target / fixture["pr_file"]).read_text(encoding="utf-8"))
    fixture_dir = target / ".loom" / "fixtures" / fixture["item"]
    body_file = f".loom/fixtures/{fixture['item']}/hosted-pr-body.md"
    readback_drift_file = f".loom/fixtures/{fixture['item']}/hosted-pr-body-drift.md"
    snapshot_file = f".loom/fixtures/{fixture['item']}/hosted-freeze-snapshot.json"
    body_path = target / body_file
    readback_drift_path = target / readback_drift_file
    snapshot_path = target / snapshot_file
    fixture_dir.mkdir(parents=True, exist_ok=True)
    body_path.write_text(pr_payload["body"], encoding="utf-8")
    readback_drift_path.write_text(pr_payload["body"] + "\nOperator drift after readback.\n", encoding="utf-8")

    pass_payload = semantic_pr_gate_fixture_payload(
        target,
        fixture,
        body_file=body_file,
        compare_body_file=body_file,
    )
    admission = pass_payload.get("hosted_freeze_admission")
    if not isinstance(admission, dict) or admission.get("schema_version") != "loom-hosted-freeze-admission/v1":
        raise AssertionError("pr-gate did not expose hosted freeze admission schema")
    if admission.get("result") != "pass" or pass_payload.get("result") != "pass":
        raise AssertionError(f"hosted freeze admission positive fixture did not pass: {admission}")
    if admission.get("artifact_comparison", {}).get("result") != "not_applicable":
        raise AssertionError("hosted freeze admission without snapshot must mark artifact comparison not_applicable")
    if admission.get("readback", {}).get("result") != "pass":
        raise AssertionError("hosted freeze admission did not consume matching PR body readback")
    if not isinstance(admission.get("carrier_refresh"), dict) or not isinstance(admission.get("shadow_freshness"), dict):
        raise AssertionError("hosted freeze admission must expose carrier refresh and shadow freshness classifications")
    if not any(step.get("name") == "hosted-freeze-admission" for step in pass_payload.get("steps", []) if isinstance(step, dict)):
        raise AssertionError("pr-gate steps must include hosted-freeze-admission before merge checkpoint consumption")

    body_drift_payload = semantic_pr_gate_fixture_payload(
        target,
        fixture,
        body_file=body_file,
        compare_body_file=readback_drift_file,
    )
    body_drift_admission = body_drift_payload.get("hosted_freeze_admission")
    if body_drift_payload.get("result") != "block" or body_drift_admission.get("result") != "block":
        raise AssertionError("hosted freeze admission must block PR body readback drift")
    if body_drift_admission.get("readback", {}).get("result") != "block":
        raise AssertionError("hosted freeze admission did not classify PR body readback drift")
    if not any(
        finding.get("classifier") == "pr_metadata_drift"
        for finding in body_drift_admission.get("failure_classifier", {}).get("findings", [])
        if isinstance(finding, dict)
    ):
        raise AssertionError("hosted freeze admission PR body drift must carry classifier next action")

    snapshot = dict(admission.get("recomputed_freeze") or {})
    snapshot["snapshot_id"] = "0" * 64
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    snapshot_mismatch_payload = semantic_pr_gate_fixture_payload(
        target,
        fixture,
        body_file=body_file,
        compare_body_file=body_file,
        gate_freeze_snapshot_file=snapshot_file,
    )
    snapshot_admission = snapshot_mismatch_payload.get("hosted_freeze_admission")
    if snapshot_mismatch_payload.get("result") != "block" or snapshot_admission.get("result") != "block":
        raise AssertionError("hosted freeze admission must block snapshot mismatch")
    if snapshot_admission.get("artifact_comparison", {}).get("result") != "block":
        raise AssertionError("hosted freeze admission did not expose blocking artifact comparison")
    if not any(
        finding.get("classifier") == "hosted_snapshot_mismatch"
        and "regenerate the freeze snapshot" in str(finding.get("next_action"))
        for finding in snapshot_admission.get("failure_classifier", {}).get("findings", [])
        if isinstance(finding, dict)
    ):
        raise AssertionError("hosted snapshot mismatch must carry classifier next action")


def assert_closeout_freeze_profile_fixture(tmp: Path) -> None:
    target = tmp / "closeout-freeze-profile"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    write_hosted_freeze_admission_inputs(target)
    subprocess.run(["git", "add", "."], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["git", "commit", "-m", "fixture closeout freeze inputs"],
        cwd=target,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    update_fixture_pr_head(target, fixture)
    record_current_fixture_review(target, fixture)
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    update_fixture_pr_head(
        target,
        fixture,
        state="MERGED",
        extra={
            "mergedAt": "2026-06-18T00:00:00Z",
            "mergeCommit": {"oid": head_sha},
            "baseRefName": fixture["branch"],
        },
    )
    append_governance_intensity_metadata_body(target, fixture)
    pr_path = target / fixture["pr_file"]
    fixture_dir = target / ".loom" / "fixtures" / fixture["item"]
    release_evidence_file = fixture_dir / "no-release-evidence.md"
    release_evidence_relative = f".loom/fixtures/{fixture['item']}/no-release-evidence.md"
    release_evidence_file.write_text(
        "# No-release Evidence\n\n"
        "- Judgment: no_release\n"
        "- Readback: fixture closeout lane changes only local checker/admission behavior and does not publish a release.\n",
        encoding="utf-8",
    )
    pr_payload = json.loads(pr_path.read_text(encoding="utf-8"))
    pr_payload["body"] = (
        f"{pr_payload['body'].rstrip()}\n\n"
        f"No-release evidence locator: {release_evidence_relative}\n"
        "Closes #1532\n"
    )
    pr_path.write_text(json.dumps(pr_payload, indent=2) + "\n", encoding="utf-8")
    issue_file = fixture_dir / "issue.json"
    issue_file.write_text(
        json.dumps(
            {
                "number": 1532,
                "state": "closed",
                "title": "closeout freeze fixture",
                "closed_at": "2026-06-18T00:01:00Z",
                "html_url": "https://github.com/owner/repo/issues/1532",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    issue_relative = f".loom/fixtures/{fixture['item']}/issue.json"
    dependency_file = fixture_dir / "dependencies.json"
    dependency_file.write_text(
        json.dumps(
            {
                "availability": "present",
                "checks": [],
                "native_edges": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    dependency_relative = f".loom/fixtures/{fixture['item']}/dependencies.json"
    body_file = f".loom/fixtures/{fixture['item']}/closeout-pr-body.md"
    readback_drift_file = f".loom/fixtures/{fixture['item']}/closeout-pr-body-drift.md"
    missing_release_pr_file = f".loom/fixtures/{fixture['item']}/pr-missing-release-evidence.json"
    (target / body_file).write_text(pr_payload["body"], encoding="utf-8")
    (target / readback_drift_file).write_text(pr_payload["body"] + "\nOperator drift after readback.\n", encoding="utf-8")
    missing_release_pr_payload = dict(pr_payload)
    missing_release_pr_payload["body"] = pr_payload["body"].replace(
        f"No-release evidence locator: {release_evidence_relative}\n",
        "",
    )
    (target / missing_release_pr_file).write_text(json.dumps(missing_release_pr_payload, indent=2) + "\n", encoding="utf-8")

    def read_only_snapshot() -> dict[str, str]:
        fetch_head = subprocess.check_output(["git", "rev-parse", "--git-path", "FETCH_HEAD"], cwd=target, text=True).strip()
        fetch_path = target / fetch_head
        return {
            "status": subprocess.check_output(["git", "status", "--short"], cwd=target, text=True),
            "refs": subprocess.check_output(["git", "for-each-ref", "--format=%(refname):%(objectname)"], cwd=target, text=True),
            "fetch_head": fetch_path.read_text(encoding="utf-8") if fetch_path.exists() else "<missing>",
        }

    before_check = read_only_snapshot()
    _, pass_payload = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
            "--body-file",
            body_file,
            "--compare-body-file",
            body_file,
        ],
        expect=0,
    )
    after_check = read_only_snapshot()
    if after_check != before_check:
        raise AssertionError("closeout freeze check must not mutate git status, refs, or FETCH_HEAD")
    if pass_payload.get("schema_version") != "loom-closeout-freeze/v1":
        raise AssertionError("closeout freeze check must emit loom-closeout-freeze/v1")
    if pass_payload.get("result") != "pass" or pass_payload.get("profile") != "closeout":
        raise AssertionError(f"closeout freeze positive fixture did not pass: {pass_payload.get('missing_inputs')}")
    if not str(pass_payload.get("snapshot_id", "")).startswith("sha256:"):
        raise AssertionError("closeout freeze snapshot_id must be sha256-prefixed")
    base_snapshot = pass_payload.get("base_freeze_snapshot", {})
    if base_snapshot.get("schema_version") != "loom-gate-freeze/v1":
        raise AssertionError("closeout freeze must retain the reused hosted gate freeze snapshot surface")
    reused_inputs = base_snapshot.get("input_bindings", {})
    for key in ("carrier_refresh", "shadow_freshness", "readback", "failure_classifier"):
        if key not in reused_inputs:
            raise AssertionError(f"closeout freeze did not retain reused {key} input")
    pending_fields = set(pass_payload.get("pending_contract_fields", []))
    consumed_fields = set(pass_payload.get("consumed_contract_fields", []))
    stable_fields = {
        "carrier_refresh_result",
        "shadow_freshness",
        "hosted_snapshot_binding",
        "failure_classifier_mapping",
        "readback_drift",
        "release_evidence_readback",
    }
    stale_pending = stable_fields.intersection(pending_fields)
    if stale_pending:
        raise AssertionError(f"closeout freeze still marks stable fields pending: {sorted(stale_pending)}")
    missing_consumed = stable_fields.difference(consumed_fields)
    if missing_consumed:
        raise AssertionError(f"closeout freeze did not consume stable fields: {sorted(missing_consumed)}")
    release_boundary = pass_payload.get("release_boundary", {})
    if release_boundary.get("result") != "pass" or release_boundary.get("evidence_readback", {}).get("locator") != release_evidence_relative:
        raise AssertionError("closeout freeze must consume no-release evidence readback instead of PR metadata alone")
    if pass_payload.get("readiness", {}).get("closeout_pr_allowed") is not True:
        raise AssertionError("closeout freeze positive fixture must allow closeout PR creation")
    closeout_specific_gate = pass_payload.get("closeout_specific_gate", {})
    if (
        closeout_specific_gate.get("schema_version") != "loom-closeout-specific-gate/v1"
        or closeout_specific_gate.get("result") != "pass"
        or closeout_specific_gate.get("verdict") != "closeout_pr_allowed"
        or closeout_specific_gate.get("escalation_required") is not False
        or closeout_specific_gate.get("next_action") != "closeout_pr_allowed"
    ):
        raise AssertionError(f"closeout freeze must expose passing closeout-specific gate verdict: {closeout_specific_gate}")

    _, missing_release_evidence = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            missing_release_pr_file,
            "--target-branch",
            fixture["branch"],
        ],
        expect=1,
    )
    if missing_release_evidence.get("readiness", {}).get("closeout_pr_allowed") is not False:
        raise AssertionError("closeout freeze must fail closed when release/no-release evidence is missing")
    release_gap_gate = missing_release_evidence.get("closeout_specific_gate", {})
    if (
        release_gap_gate.get("schema_version") != "loom-closeout-specific-gate/v1"
        or release_gap_gate.get("result") != "block"
        or release_gap_gate.get("verdict") != "full_review_required"
        or release_gap_gate.get("escalation_reason") != "closeout_release_evidence_gap"
        or release_gap_gate.get("next_action") != "resolve_closeout_freeze_blockers"
    ):
        raise AssertionError(f"closeout freeze must expose release-gap closeout-specific escalation: {release_gap_gate}")
    if not any(
        blocking.get("input") == "release_boundary"
        and blocking.get("failure_kind") == "closeout_release_evidence_gap"
        for blocking in missing_release_evidence.get("readiness", {}).get("blocking_inputs", [])
        if isinstance(blocking, dict)
    ):
        raise AssertionError("closeout freeze missing release/no-release evidence must be a blocking input")

    _, readback_drift = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
            "--body-file",
            body_file,
            "--compare-body-file",
            readback_drift_file,
        ],
        expect=1,
    )
    if readback_drift.get("readiness", {}).get("closeout_pr_allowed") is not False:
        raise AssertionError("closeout freeze must fail closed when PR body readback drifts")
    if not any(
        blocking.get("input") == "readback"
        for blocking in readback_drift.get("readiness", {}).get("blocking_inputs", [])
        if isinstance(blocking, dict)
    ):
        raise AssertionError("closeout freeze readback drift must be a blocking input")

    unrelated_issue_file = fixture_dir / "issue-unrelated.json"
    unrelated_issue_file.write_text(
        json.dumps(
            {
                "number": 9999,
                "state": "closed",
                "title": "unrelated closed issue",
                "closed_at": "2026-06-18T00:01:00Z",
                "html_url": "https://github.com/owner/repo/issues/9999",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, unrelated_subject = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "9999",
            "--issue-payload-file",
            f".loom/fixtures/{fixture['item']}/issue-unrelated.json",
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
        ],
        expect=1,
    )
    if not any(
        blocking.get("failure_kind") == "closeout_terminal_subject_drift"
        for blocking in unrelated_subject.get("readiness", {}).get("blocking_inputs", [])
        if isinstance(blocking, dict)
    ):
        raise AssertionError("closeout freeze must block unrelated closed issue plus merged PR pairing")

    _, target_branch_drift = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            "main",
        ],
        expect=1,
    )
    if target_branch_drift.get("terminal_facts", {}).get("target_contains_merge_commit") is not False:
        raise AssertionError("closeout freeze must not fall back to HEAD for target branch merge containment")
    if not any(
        blocking.get("failure_kind") == "closeout_host_git_mismatch"
        for blocking in target_branch_drift.get("readiness", {}).get("blocking_inputs", [])
        if isinstance(blocking, dict)
    ):
        raise AssertionError("closeout freeze target branch drift must be a blocking input")

    dependency_drift_file = fixture_dir / "dependencies-open-blocker.json"
    dependency_drift_file.write_text(
        json.dumps(
            {
                "availability": "present",
                "checks": [],
                "native_edges": [
                    {
                        "source_issue": 1532,
                        "blocking_issue": 9999,
                        "direction": "blocked_by",
                        "blocker_state": "open",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, dependency_drift = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            f".loom/fixtures/{fixture['item']}/dependencies-open-blocker.json",
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
        ],
        expect=1,
    )
    dependency_binding = dependency_drift.get("carrier_bindings", {}).get("dependency_graph", {})
    if dependency_binding.get("result") != "block":
        raise AssertionError("closeout freeze must block dependency graph drift")
    if not any(
        finding.get("kind") == "open_blocker_executable_conflict"
        for finding in dependency_binding.get("findings", [])
        if isinstance(finding, dict)
    ):
        raise AssertionError("closeout freeze dependency graph must expose the open blocker finding")
    if not any(
        finding.get("failure_kind") == "closeout_dependency_graph_drift"
        for finding in dependency_drift.get("failure_classifier", {}).get("findings", [])
        if isinstance(finding, dict)
    ):
        raise AssertionError("closeout freeze dependency graph drift must carry a classifier finding")

    review_path = target / fixture["review_path"]
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_payload["semantic_review_disposition"] = {
        "status": "failed",
        "reason": "fixture retained review semantic drift",
    }
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    _, review_drift = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
        ],
        expect=1,
    )
    if not any(
        blocking.get("input") == "retained_review"
        for blocking in review_drift.get("readiness", {}).get("blocking_inputs", [])
        if isinstance(blocking, dict)
    ):
        raise AssertionError("closeout freeze must block retained review semantic drift")
    review_payload["semantic_review_disposition"] = {
        "status": "passed",
        "reason": "fixture restored retained review semantic disposition",
    }
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")

    write_path = f".loom/runtime/gate-freeze/{fixture['item']}-closeout.json"
    _, write_payload = run_flow_json(
        [
            "gate-freeze",
            "write",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
            "--write-path",
            write_path,
        ],
        expect=0,
    )
    if write_payload.get("write_artifact", {}).get("locator") != write_path:
        raise AssertionError("closeout freeze write must retain the closeout snapshot under .loom/runtime/gate-freeze")
    written = json.loads((target / write_path).read_text(encoding="utf-8"))
    if written.get("schema_version") != "loom-closeout-freeze/v1":
        raise AssertionError("closeout freeze write artifact must preserve loom-closeout-freeze/v1")

    task_carrier = target / ".loom" / "specs" / fixture["item"] / "task-carrier.md"
    task_carrier.write_text(f"{task_carrier.read_text(encoding='utf-8').rstrip()}\n\n- Closeout carrier sync fixture.\n", encoding="utf-8")
    commit_fixture_file(target, f".loom/specs/{fixture['item']}/task-carrier.md", "fixture closeout allowed carrier drift")
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_payload["reviewed_head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    review_payload["semantic_review_disposition"] = {
        "status": "passed",
        "reason": "fixture closeout carrier drift review refreshed",
    }
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture closeout review refresh after carrier drift")
    _, allowed_drift_payload = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
        ],
        expect=0,
    )
    if allowed_drift_payload.get("allowed_paths", {}).get("violations") != []:
        raise AssertionError("closeout freeze allowed paths must match terminal closeout carrier policy")
    if f".loom/specs/{fixture['item']}/task-carrier.md" not in allowed_drift_payload.get("allowed_paths", {}).get("changed_paths", []):
        raise AssertionError("closeout freeze allowed path fixture did not exercise task carrier drift")

    (target / "tools").mkdir(exist_ok=True)
    (target / "tools" / "loom.py").write_text("print('implementation drift')\n", encoding="utf-8")
    commit_fixture_file(target, "tools/loom.py", "fixture implementation drift after closeout merge")
    _, drift_payload = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
        ],
        expect=1,
    )
    if drift_payload.get("result") != "block":
        raise AssertionError("closeout freeze must block implementation drift after the merge commit")
    allowed_paths = drift_payload.get("allowed_paths", {})
    if "tools/loom.py" not in allowed_paths.get("violations", []):
        raise AssertionError("closeout freeze allowed_paths must identify implementation drift")
    if not any(
        finding.get("failure_kind") == "closeout_allowed_paths_violation"
        for finding in drift_payload.get("failure_classifier", {}).get("findings", [])
        if isinstance(finding, dict)
    ):
        raise AssertionError("closeout freeze implementation drift must carry a classifier finding")

    companion_readme = target / ".loom" / "companion" / "README.md"
    companion_readme.write_text("# Fixture Companion\n\nstale shadow source\n", encoding="utf-8")
    _, stale_carrier_shadow = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--profile",
            "closeout",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--issue",
            "1532",
            "--issue-payload-file",
            issue_relative,
            "--dependency-payload-file",
            dependency_relative,
            "--pr-payload-file",
            fixture["pr_file"],
            "--target-branch",
            fixture["branch"],
        ],
        expect=1,
    )
    if stale_carrier_shadow.get("readiness", {}).get("closeout_pr_allowed") is not False:
        raise AssertionError("closeout freeze must fail closed when carrier refresh or shadow freshness is stale")
    stale_inputs = {
        blocking.get("input")
        for blocking in stale_carrier_shadow.get("readiness", {}).get("blocking_inputs", [])
        if isinstance(blocking, dict)
    }
    if not {"carrier_refresh", "shadow_freshness"}.issubset(stale_inputs):
        raise AssertionError("closeout freeze stale carrier/shadow inputs must both block closeout admission")


def record_current_fixture_review(target: Path, fixture: dict[str, str]) -> dict[str, Any]:
    _, record_payload = run_flow_json(
        [
            "review",
            "record",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--review-file",
            fixture["review_path"],
            "--decision",
            "allow",
            "--kind",
            "code_review",
            "--summary",
            "Fixture implementation review approves the current head.",
            "--reviewer",
            "contract-test",
        ]
    )
    if record_payload.get("result") != "pass":
        raise AssertionError(f"review record fixture failed: {record_payload.get('missing_inputs')}")
    return record_payload


def record_current_fixture_spec_review(target: Path, fixture: dict[str, str]) -> dict[str, Any]:
    _, record_payload = run_flow_json(
        [
            "review",
            "record",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--review-file",
            f".loom/reviews/{fixture['item']}.spec.json",
            "--decision",
            "allow",
            "--kind",
            "spec_review",
            "--summary",
            "Fixture spec review approves the current suite path decision.",
            "--reviewer",
            "contract-test",
        ]
    )
    if record_payload.get("result") != "pass":
        raise AssertionError(f"spec review record fixture failed: {record_payload.get('missing_inputs')}")
    return record_payload


def assert_gate_freeze_review_binding_fixture(tmp: Path) -> None:
    target = tmp / "gate-freeze-review-binding"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)

    record_payload = record_current_fixture_review(target, fixture)
    recorded_disposition = record_payload.get("review", {}).get("record", {}).get("semantic_review_disposition", {})
    if recorded_disposition.get("status") != "passed":
        raise AssertionError("review record did not write passed semantic_review_disposition")

    fresh_payload = gate_freeze_fixture_payload(target, fixture)
    fresh_binding = fresh_payload.get("input_bindings", {}).get("review_binding")
    if not isinstance(fresh_binding, dict) or fresh_binding.get("schema_version") != "loom-gate-freeze-review-binding/v1":
        raise AssertionError("gate freeze did not emit review binding schema")
    if (
        fresh_binding.get("result") != "pass"
        or fresh_binding.get("decision") != "allow"
        or fresh_binding.get("kind") != "code_review"
        or fresh_binding.get("binding_status") != "fresh"
        or fresh_binding.get("semantic_review_disposition", {}).get("consumable") is not True
    ):
        raise AssertionError(f"gate freeze fresh review binding did not pass: {fresh_binding}")
    if not fresh_binding.get("reviewed_head") or fresh_binding.get("reviewed_head") != fresh_binding.get("current_head"):
        raise AssertionError("gate freeze fresh review binding did not expose reviewed/current head")

    commit_fixture_file(target, fixture["review_path"], "fixture review carrier-only drift")
    update_fixture_pr_head(target, fixture)
    carrier_payload = gate_freeze_fixture_payload(target, fixture)
    carrier_binding = carrier_payload.get("input_bindings", {}).get("review_binding")
    carrier_head = carrier_binding.get("head_binding", {}) if isinstance(carrier_binding, dict) else {}
    if (
        not isinstance(carrier_binding, dict)
        or carrier_binding.get("result") != "pass"
        or carrier_binding.get("binding_status") != "carrier-only"
        or fixture["review_path"] not in carrier_head.get("changed_paths", [])
        or carrier_head.get("disallowed_paths") != []
        or "carrier-only" not in str(carrier_binding.get("next_action"))
    ):
        raise AssertionError(f"gate freeze carrier-only review binding did not pass with path evidence: {carrier_binding}")
    carrier_pr_gate_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if (
        carrier_pr_gate_payload.get("result") != "pass"
        or carrier_pr_gate_payload.get("review_approval", {}).get("head_binding", {}).get("status") != "carrier-only"
        or carrier_pr_gate_payload.get("governance_lint", {}).get("result") != "pass"
    ):
        raise AssertionError(f"pr-gate did not consume carrier-only review drift: {carrier_pr_gate_payload.get('missing_inputs')}")
    append_governance_intensity_metadata_body(target, fixture, include_legacy_bindings=False)
    machine_only_pr_gate_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if (
        machine_only_pr_gate_payload.get("result") != "pass"
        or machine_only_pr_gate_payload.get("review_approval", {}).get("head_binding", {}).get("status") != "carrier-only"
    ):
        raise AssertionError(
            f"pr-gate did not consume machine-carrier-only PR binding: {machine_only_pr_gate_payload.get('missing_inputs')}"
        )

    generated_path = "skills/README.md"
    (target / "skills").mkdir(parents=True, exist_ok=True)
    (target / generated_path).write_text("# Generated fixture drift\n", encoding="utf-8")
    commit_fixture_file(target, generated_path, "fixture generated-only drift after freeze review")
    update_fixture_pr_head(target, fixture)
    generated_payload = gate_freeze_fixture_payload(target, fixture)
    generated_binding = generated_payload.get("input_bindings", {}).get("review_binding")
    generated_head = generated_binding.get("head_binding", {}) if isinstance(generated_binding, dict) else {}
    generated_actions = generated_head.get("generated_only_validation_actions", [])
    if (
        not isinstance(generated_binding, dict)
        or generated_binding.get("result") != "pass"
        or generated_binding.get("binding_status") != "generated-only"
        or generated_path not in generated_head.get("generated_only_paths", [])
        or generated_head.get("disallowed_paths") != []
        or not any("tools/skills_surface.py check" in str(action.get("action")) for action in generated_actions if isinstance(action, dict))
        or "generated-only" not in str(generated_binding.get("next_action"))
    ):
        raise AssertionError(f"gate freeze generated-only review binding did not pass with validation action: {generated_binding}")
    generated_pr_gate_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if (
        generated_pr_gate_payload.get("result") != "pass"
        or generated_pr_gate_payload.get("review_approval", {}).get("head_binding", {}).get("status") != "generated-only"
        or generated_pr_gate_payload.get("governance_lint", {}).get("result") != "pass"
    ):
        raise AssertionError(f"pr-gate did not consume generated-only review drift: {generated_pr_gate_payload.get('missing_inputs')}")

    (target / "implementation-drift.txt").write_text("unreviewed drift\n", encoding="utf-8")
    commit_fixture_file(target, "implementation-drift.txt", "fixture implementation drift after freeze review")
    update_fixture_pr_head(target, fixture)
    stale_payload = gate_freeze_fixture_payload(target, fixture)
    stale_binding = stale_payload.get("input_bindings", {}).get("review_binding")
    stale_head = stale_binding.get("head_binding", {}) if isinstance(stale_binding, dict) else {}
    if (
        not isinstance(stale_binding, dict)
        or stale_binding.get("result") != "block"
        or stale_binding.get("binding_status") not in {"stale", "implementation-drift-only"}
        or "implementation-drift.txt" not in stale_head.get("disallowed_paths", [])
        or "rerun authored Loom review" not in str(stale_binding.get("next_action"))
    ):
        raise AssertionError(f"gate freeze stale review binding did not block with rerun action: {stale_binding}")

    invalid_target = tmp / "gate-freeze-invalid-disposition"
    invalid_target.mkdir()
    invalid_fixture = write_semantic_review_pr_gate_fixture(invalid_target)
    record_current_fixture_review(invalid_target, invalid_fixture)
    review_path = invalid_target / invalid_fixture["review_path"]
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_payload["semantic_review_disposition"] = {"status": "commented"}
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    invalid_payload = gate_freeze_fixture_payload(invalid_target, invalid_fixture)
    invalid_binding = invalid_payload.get("input_bindings", {}).get("review_binding")
    if (
        not isinstance(invalid_binding, dict)
        or invalid_binding.get("result") != "block"
        or invalid_binding.get("semantic_review_disposition", {}).get("status") != "commented"
        or "semantic_review_disposition" not in " ".join(invalid_binding.get("missing_inputs", []))
        or "semantic_review_disposition" not in str(invalid_binding.get("next_action"))
    ):
        raise AssertionError(f"gate freeze invalid semantic disposition did not fail closed: {invalid_binding}")


def assert_pr_gate_blocks(
    target: Path,
    fixture: dict[str, str],
    label: str,
    *,
    expected_missing: str | None = None,
    expect_lite_gate_block: bool = False,
) -> dict[str, Any]:
    payload = semantic_pr_gate_fixture_payload(target, fixture)
    if payload.get("result") != "block":
        raise AssertionError(f"{label} did not fail closed")
    if expected_missing and not any(expected_missing in str(message) for message in payload.get("missing_inputs", [])):
        raise AssertionError(f"{label} did not expose expected missing input: {expected_missing}")
    if expect_lite_gate_block:
        lite_gate = payload.get("docs_governance_lite_gate")
        if not isinstance(lite_gate, dict) or lite_gate.get("result") != "block":
            raise AssertionError(f"{label} did not expose blocking docs-governance lite gate evidence")
    return payload


def assert_cross_repo_review_gate_fixtures(tmp: Path) -> None:
    hotcp_target = tmp / "hotcp-review-gate-fixtures"
    hotcp_target.mkdir()
    hotcp_fixture = write_semantic_review_pr_gate_fixture(hotcp_target)
    hotcp_review_path = hotcp_target / hotcp_fixture["review_path"]

    (hotcp_target / "hotcp-unreviewed-drift.txt").write_text("HotCP stale head drift\n", encoding="utf-8")
    commit_fixture_file(hotcp_target, "hotcp-unreviewed-drift.txt", "fixture HotCP stale head drift")
    update_fixture_pr_head(hotcp_target, hotcp_fixture)
    hotcp_stale = semantic_pr_gate_fixture_payload(hotcp_target, hotcp_fixture)
    if (
        hotcp_stale.get("result") != "block"
        or "review_stale" not in hotcp_stale.get("failure_taxonomy", [])
        or "head_binding_drift" not in hotcp_stale.get("failure_taxonomy", [])
    ):
        raise AssertionError("HotCP-style stale/head drift fixture did not fail closed")

    hotcp_review = json.loads(hotcp_review_path.read_text(encoding="utf-8"))
    hotcp_review["authored_at"] = "2026-05-31T00:00:00Z"
    hotcp_review_path.write_text(json.dumps(hotcp_review, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(hotcp_target, hotcp_fixture["review_path"], "fixture HotCP post merge review")
    update_fixture_pr_head(hotcp_target, hotcp_fixture, state="MERGED", extra={"mergedAt": "2026-05-30T00:00:00Z"})
    hotcp_post_merge = semantic_pr_gate_fixture_payload(hotcp_target, hotcp_fixture)
    hotcp_diagnostic = hotcp_post_merge.get("post_merge_review_diagnostic", {})
    if (
        hotcp_post_merge.get("result") != "block"
        or "post_merge_review_bypass" not in hotcp_post_merge.get("failure_taxonomy", [])
        or hotcp_diagnostic.get("finding", {}).get("kind") != "post_merge_review_bypass"
        or "backdate review evidence" not in hotcp_diagnostic.get("repair_plan", {}).get("forbidden_repairs", [])
    ):
        raise AssertionError("HotCP-style post-merge review fixture did not expose bypass repair semantics")

    hotcp_ci_target = tmp / "hotcp-ci-only-bypass"
    hotcp_ci_target.mkdir()
    hotcp_ci_fixture = write_semantic_review_pr_gate_fixture(hotcp_ci_target)
    hotcp_ci_review_path = hotcp_ci_target / hotcp_ci_fixture["review_path"]
    hotcp_ci_review = json.loads(hotcp_ci_review_path.read_text(encoding="utf-8"))
    hotcp_ci_review["semantic_review_disposition"] = {"status": "required"}
    hotcp_ci_review_path.write_text(json.dumps(hotcp_ci_review, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(hotcp_ci_target, hotcp_ci_fixture["review_path"], "fixture HotCP CI-only review required")
    update_fixture_pr_head(
        hotcp_ci_target,
        hotcp_ci_fixture,
        extra={"statusCheckRollup": [{"name": "hotcp-ci", "conclusion": "SUCCESS", "status": "COMPLETED"}]},
    )
    hotcp_ci_only = semantic_pr_gate_fixture_payload(hotcp_ci_target, hotcp_ci_fixture)
    if hotcp_ci_only.get("result") != "block" or "ci_only_bypass" not in hotcp_ci_only.get("failure_taxonomy", []):
        raise AssertionError("HotCP-style CI-only bypass fixture did not fail closed")

    webenvoy_target, webenvoy_fixture, _, webenvoy_dir = prepare_controlled_merge_fixture(
        tmp,
        fixture_name="webenvoy-guardian-triggered-block",
        branch_protection_contexts=["loom-pr-merge-gate"],
    )
    (webenvoy_dir / "checks-webenvoy-guardian-block.json").write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {
                    "name": "webenvoy-guardian",
                    "workflowName": "webenvoy-guardian",
                    "conclusion": "FAILURE",
                    "status": "COMPLETED",
                    "detailsUrl": "https://example.invalid/webenvoy/guardian",
                },
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, webenvoy_guardian = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(webenvoy_target),
            "--item",
            webenvoy_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            webenvoy_fixture["head_sha"],
            "--pr-payload-file",
            webenvoy_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks-webenvoy-guardian-block.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
    )
    if (
        webenvoy_guardian.get("result") != "block"
        or webenvoy_guardian.get("required_checks", {}).get("result") != "pass"
        or "webenvoy-guardian" not in webenvoy_guardian.get("triggered_check_rollup", {}).get("blocking", [])
    ):
        raise AssertionError("WebEnvoy-style guardian block was not consumed as a triggered-check merge blocker")
    (webenvoy_dir / "checks-webenvoy-guardian-pending.json").write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "webenvoy-guardian", "workflowName": "webenvoy-guardian", "status": "IN_PROGRESS"},
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, webenvoy_pending = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(webenvoy_target),
            "--item",
            webenvoy_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            webenvoy_fixture["head_sha"],
            "--pr-payload-file",
            webenvoy_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks-webenvoy-guardian-pending.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
    )
    if (
        webenvoy_pending.get("result") != "block"
        or webenvoy_pending.get("required_checks", {}).get("result") != "pass"
        or "webenvoy-guardian" not in webenvoy_pending.get("triggered_check_rollup", {}).get("pending", [])
    ):
        raise AssertionError("WebEnvoy-style pending guardian check was not consumed as a triggered-check merge blocker")

    syvert_target = tmp / "syvert-guardian-advisory-cannot-replace-review"
    syvert_target.mkdir()
    syvert_fixture = write_semantic_review_pr_gate_fixture(syvert_target)
    syvert_review_path = syvert_target / syvert_fixture["review_path"]
    syvert_review = json.loads(syvert_review_path.read_text(encoding="utf-8"))
    syvert_review["semantic_review_disposition"] = {"status": "required"}
    syvert_review_path.write_text(json.dumps(syvert_review, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(syvert_target, syvert_fixture["review_path"], "fixture Syvert advisory review required")
    update_fixture_pr_head(
        syvert_target,
        syvert_fixture,
        extra={
            "statusCheckRollup": [
                {"name": "syvert-guardian", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "syvert-integration-advisory", "conclusion": "NEUTRAL", "status": "COMPLETED"},
            ]
        },
    )
    syvert_advisory = semantic_pr_gate_fixture_payload(syvert_target, syvert_fixture)
    syvert_disposition = syvert_advisory.get("review_approval", {}).get("semantic_review_disposition", {})
    if (
        syvert_advisory.get("result") != "block"
        or syvert_disposition.get("consumable") is not False
        or "ci_only_bypass" not in syvert_advisory.get("failure_taxonomy", [])
        or not any("host-review signal cannot satisfy" in item for item in syvert_advisory.get("missing_inputs", []))
    ):
        raise AssertionError("Syvert-style guardian/integration advisory signals replaced Loom semantic review")

    syvert_merge_target, syvert_merge_fixture, _, syvert_merge_dir = prepare_controlled_merge_fixture(
        tmp,
        fixture_name="syvert-verdict-conflict-triggered-block",
        branch_protection_contexts=["loom-pr-merge-gate"],
    )
    (syvert_merge_dir / "checks-syvert-verdict-conflict.json").write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "syvert-guardian", "workflowName": "syvert-guardian", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {
                    "name": "syvert-integration",
                    "workflowName": "syvert-integration",
                    "conclusion": "FAILURE",
                    "status": "COMPLETED",
                },
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, syvert_conflict = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(syvert_merge_target),
            "--item",
            syvert_merge_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            syvert_merge_fixture["head_sha"],
            "--pr-payload-file",
            syvert_merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks-syvert-verdict-conflict.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
    )
    if (
        syvert_conflict.get("result") != "block"
        or syvert_conflict.get("required_checks", {}).get("result") != "pass"
        or "syvert-integration" not in syvert_conflict.get("triggered_check_rollup", {}).get("blocking", [])
    ):
        raise AssertionError("Syvert-style guardian/integration verdict conflict did not block controlled merge")
    (syvert_merge_dir / "checks-syvert-verdict-pending.json").write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "syvert-guardian", "workflowName": "syvert-guardian", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "syvert-integration", "workflowName": "syvert-integration", "status": "QUEUED"},
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, syvert_pending = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(syvert_merge_target),
            "--item",
            syvert_merge_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            syvert_merge_fixture["head_sha"],
            "--pr-payload-file",
            syvert_merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks-syvert-verdict-pending.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
    )
    if (
        syvert_pending.get("result") != "block"
        or syvert_pending.get("required_checks", {}).get("result") != "pass"
        or "syvert-integration" not in syvert_pending.get("triggered_check_rollup", {}).get("pending", [])
    ):
        raise AssertionError("Syvert-style pending integration verdict did not block controlled merge")


def write_governance_metadata_contract_fixture(target: Path) -> None:
    companion = target / ".loom" / "companion"
    companion.mkdir(parents=True, exist_ok=True)
    (companion / "README.md").write_text("# Fixture Companion\n", encoding="utf-8")
    (companion / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "loom-repo-companion-manifest/v1",
                "companion_entry": ".loom/companion/README.md",
                "repo_interface": ".loom/companion/repo-interface.json",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (target / ".github").mkdir(parents=True, exist_ok=True)
    (target / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text(
        "## Summary\n\n"
        "- Problem:\n"
        "- Scope:\n\n"
        "## Validation\n\n"
        "- [ ] Verified locally\n\n"
        "## Risks And Follow-ups\n\n"
        "- Risks:\n"
        "- Follow-ups:\n\n"
        "## Related Work\n\n"
        "- Issue:\n"
        "- Loom Work Item:\n\n"
        "## PR Metadata Machine Carrier\n",
        encoding="utf-8",
    )
    (target / "docs" / "methodology" / "harness").mkdir(parents=True, exist_ok=True)
    (target / "docs" / "methodology" / "harness" / "tiered-gate-consumption-contract.md").write_text(
        "# Tiered Gate Consumption Contract\n",
        encoding="utf-8",
    )
    (target / "tools").mkdir(parents=True, exist_ok=True)
    (target / "tools" / "loom_flow.py").write_text("# fixture command locator\n", encoding="utf-8")
    (companion / "repo-interface.json").write_text(
        json.dumps(
            {
                "schema_version": "loom-repo-interface/v2",
                "companion_entry": ".loom/companion/README.md",
                "repo_specific_requirements": {"review": [], "merge_ready": [], "closeout": []},
                "specialized_gates": [],
                "review_instruction_locators": {
                    "spec_review": {"locator": "loom_default", "mode": "loom_default"},
                    "implementation_review": {"locator": "loom_default", "mode": "loom_default"},
                },
                "metadata_contract": {
                    "fields": [
                        {
                            "id": "loom-governance-intensity",
                            "summary": "Governance intensity fixture carrier",
                            "applicability_locator": "docs/methodology/harness/tiered-gate-consumption-contract.md",
                            "authority_locator": ".github/PULL_REQUEST_TEMPLATE.md",
                            "enforcement": "blocking",
                            "machine_carrier": {
                                "type": "pr_body_html_comment_json",
                                "schema_version": "loom-repo-pr-metadata/v1",
                                "carrier_id": "loom-governance-intensity-pr-body-block",
                                "marker": "loom:repo-pr-metadata",
                                "surface": "merge_ready",
                                "repo_specific_field_set": [
                                    "loom_work_item",
                                    "branch",
                                    "head_sha",
                                    "governance_intensity",
                                    "change_class",
                                    "suite_path",
                                    "suite_not_applicable",
                                    "review_requirement",
                                    "fact_chain_required",
                                    "pr_gate_required",
                                    "release_judgment",
                                    "closeout_required",
                                    "upgrade_triggers",
                                ],
                                "enforcement": "blocking",
                                "required_fields": [
                                    "loom_work_item",
                                    "branch",
                                    "head_sha",
                                    "governance_intensity",
                                    "change_class",
                                    "suite_path",
                                    "review_requirement",
                                    "fact_chain_required",
                                    "pr_gate_required",
                                    "release_judgment",
                                    "closeout_required",
                                    "upgrade_triggers",
                                ],
                                "preflight": {
                                    "required_before": ["review", "merge_ready"],
                                    "failure_mode": "blocking",
                                    "command_locator": "tools/loom_flow.py",
                                },
                                "diagnostics": {
                                    "block_locator": True,
                                    "parse_error": True,
                                    "missing_fields": True,
                                    "expected_format": True,
                                    "suggested_fix": True,
                                },
                                "binding_priority": [
                                    "cli_explicit_input",
                                    "pr_body_machine_carrier",
                                    "host_readback",
                                    "repo_carrier",
                                    "human_pr_body_field",
                                    "issue_title_or_body",
                                ],
                                "safe_repair": {
                                    "allowed_when": "cli_explicit_input, pr_body_machine_carrier, and host_readback agree",
                                    "allowed_targets": [
                                        "missing_human_backlink",
                                        "display_field_format",
                                        "deterministic_machine_carrier_rerender",
                                    ],
                                    "forbidden_when": [
                                        "work_item_conflict",
                                        "issue_conflict",
                                        "pr_conflict",
                                        "branch_conflict",
                                        "head_sha_conflict",
                                        "release_judgment_conflict",
                                        "closeout_policy_conflict",
                                    ],
                                    "required_readback": "render, update PR body, read back, then rerun metadata preflight before gate consumption",
                                },
                                "migration_mode": "required",
                            },
                        }
                    ]
                },
                "context_schema": {"fields": []},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def governance_metadata_body(
    *,
    item: str = "WI-1321",
    branch: str = "work/1321-governance-intensity-metadata-carrier",
    head_sha: str = "1111111111111111111111111111111111111111",
    include_legacy_bindings: bool = True,
    fields_override: dict[str, Any] | None = None,
    surface: str = "merge_ready",
) -> str:
    fields: dict[str, Any] = {
        "loom_work_item": item,
        "branch": branch,
        "head_sha": head_sha,
        "governance_intensity": "standard",
        "change_class": "contract",
        "suite_path": "minimal",
        "suite_not_applicable": None,
        "review_requirement": "current_head_review_required",
        "fact_chain_required": True,
        "pr_gate_required": True,
        "release_judgment": "no_release",
        "closeout_required": True,
        "upgrade_triggers": [],
    }
    if fields_override:
        for key, value in fields_override.items():
            if value == "__DELETE__":
                fields.pop(key, None)
            else:
                fields[key] = value
    envelope = {
        "schema_version": "loom-repo-pr-metadata/v1",
        "metadata_contract_id": "loom-governance-intensity",
        "surface": surface,
        "fields": fields,
        "source": {"rendered_hash": "sha256:fixture"},
        "parser_version": "loom-pr-metadata-parser/v1",
    }
    legacy_binding = (
        f"Loom Work Item: {item}\n"
        f"Branch: {branch}\n"
        f"Head SHA: {head_sha}\n\n"
        if include_legacy_bindings
        else f"Loom Work Item: {item}\n\n"
    )
    return legacy_binding + "<!-- loom:repo-pr-metadata\n" + f"{json.dumps(envelope, indent=2)}\n" + "-->\n"


def governance_metadata_preflight_payload(target: Path, body_name: str, *, expect: int = 0) -> dict[str, Any]:
    _, payload = run_flow_json(
        [
            "pr-metadata",
            "preflight",
            "--target",
            str(target),
            "--surface",
            "merge_ready",
            "--body-file",
            body_name,
        ],
        expect=expect,
    )
    return payload


def assert_pr_metadata_wrapper_argument_contract() -> None:
    spec = importlib.util.spec_from_file_location("loom_cli_contract", LOOM)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load tools/loom.py for pr metadata wrapper regression")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    captured: dict[str, Any] = {}

    def fake_emit_flow(command: str, flow_args: list[str], *, fallback_to: list[str] | None = None) -> int:
        captured.clear()
        captured["command"] = command
        captured["flow_args"] = flow_args
        captured["fallback_to"] = fallback_to
        return 0

    original_emit_flow = module.emit_flow
    module.emit_flow = fake_emit_flow
    try:
        status = module.handle_pr(
            [
                "metadata-update",
                "--surface",
                "closeout",
                "--item",
                "WI-1541",
                "--issue",
                "1687",
                "--head-sha",
                "1" * 40,
                "--branch",
                "work/1541-pr-metadata-update-v2",
                "--output-file",
                ".loom/runtime/pr/rendered.md",
                "--readback-file",
                ".loom/runtime/pr/readback.md",
                "--base-body-file",
                ".github/PULL_REQUEST_TEMPLATE.md",
                "--governance-intensity",
                "standard",
                "--change-class",
                "contract",
                "--suite-path",
                "minimal",
                "--review-requirement",
                "current_head_review_required",
                "--release-judgment",
                "no_release",
                "--upgrade-trigger",
                "fixture",
            ]
        )
        if status != 0:
            raise AssertionError("pr metadata-update wrapper regression did not complete")
        if captured.get("command") != "pr metadata-update":
            raise AssertionError("pr metadata-update wrapper did not preserve command label")
        flow_args = captured.get("flow_args")
        if not isinstance(flow_args, list) or flow_args[:3] != ["pr-metadata", "update", "--target"]:
            raise AssertionError("pr metadata-update wrapper did not delegate to pr-metadata update")
        expected_pairs = {
            "--surface": "closeout",
            "--item": "WI-1541",
            "--issue": "1687",
            "--head-sha": "1" * 40,
            "--branch": "work/1541-pr-metadata-update-v2",
            "--output-file": ".loom/runtime/pr/rendered.md",
            "--readback-file": ".loom/runtime/pr/readback.md",
            "--base-body-file": ".github/PULL_REQUEST_TEMPLATE.md",
            "--governance-intensity": "standard",
            "--change-class": "contract",
            "--suite-path": "minimal",
            "--review-requirement": "current_head_review_required",
            "--release-judgment": "no_release",
            "--upgrade-trigger": "fixture",
        }
        for flag, expected in expected_pairs.items():
            if flag not in flow_args:
                raise AssertionError(f"pr metadata-update wrapper did not pass {flag}")
            if flow_args[flow_args.index(flag) + 1] != expected:
                raise AssertionError(f"pr metadata-update wrapper changed {flag} value")
        if "--dry-run" not in flow_args or "--apply" in flow_args:
            raise AssertionError("pr metadata-update wrapper must default to dry-run delegation")

        status = module.handle_pr(
            [
                "metadata-update",
                "--surface",
                "closeout",
                "--item",
                "WI-1541",
                "--apply",
            ]
        )
        if status != 0:
            raise AssertionError("pr metadata-update wrapper apply regression did not complete")
        flow_args = captured.get("flow_args")
        if "--apply" not in flow_args or "--dry-run" in flow_args:
            raise AssertionError("pr metadata-update wrapper did not forward explicit --apply")
    finally:
        module.emit_flow = original_emit_flow


def assert_governance_metadata_render_readback_fixture(tmp: Path) -> None:
    target = tmp / "governance-metadata-render-readback"
    target.mkdir()
    write_governance_metadata_contract_fixture(target)
    (target / ".github").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md", target / ".github" / "PULL_REQUEST_TEMPLATE.md")
    subprocess.run(["git", "init"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "checkout", "-b", "work/1541-render"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=target, check=True)
    (target / "README.md").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()

    _, render_payload = run_flow_json(
        [
            "pr-metadata",
            "render",
            "--target",
            str(target),
            "--surface",
            "closeout",
            "--item",
            "WI-1541",
            "--issue",
            "1541",
            "--head-sha",
            head_sha,
            "--branch",
            "work/1541-render",
            "--output-file",
            ".loom/runtime/pr/rendered.md",
        ]
    )
    if render_payload.get("result") != "pass":
        raise AssertionError(f"render payload failed: {render_payload.get('missing_inputs')}")
    if render_payload.get("effective_carrier_surface") != "closeout":
        raise AssertionError("closeout render should emit closeout carrier surface")
    rendered = target / ".loom" / "runtime" / "pr" / "rendered.md"
    if not rendered.exists():
        raise AssertionError("render did not write the repo-relative body artifact")
    rendered_body = rendered.read_text(encoding="utf-8")
    if "- Issue: #1541" not in rendered_body or "- Loom Work Item: WI-1541" not in rendered_body:
        raise AssertionError("render did not normalize human PR binding line spacing")

    _, readback_payload = run_flow_json(
        [
            "pr-metadata",
            "readback",
            "--target",
            str(target),
            "--surface",
            "closeout",
            "--item",
            "WI-1541",
            "--issue",
            "1541",
            "--head-sha",
            head_sha,
            "--branch",
            "work/1541-render",
            "--body-file",
            ".loom/runtime/pr/rendered.md",
        ]
    )
    if readback_payload.get("result") != "pass":
        raise AssertionError(f"readback payload failed: {readback_payload.get('missing_inputs')}")
    governance_fields = readback_payload.get("governance_fields")
    if not isinstance(governance_fields, dict) or governance_fields.get("head_sha") != head_sha:
        raise AssertionError("readback did not expose parsed governance fields")

    _, update_dry_run_payload = run_flow_json(
        [
            "pr-metadata",
            "update",
            "--target",
            str(target),
            "--surface",
            "closeout",
            "--item",
            "WI-1541",
            "--issue",
            "1541",
            "--head-sha",
            head_sha,
            "--branch",
            "work/1541-render",
            "--output-file",
            ".loom/runtime/pr/update-rendered.md",
        ]
    )
    if (
        update_dry_run_payload.get("result") != "pass"
        or update_dry_run_payload.get("dry_run") is not True
        or update_dry_run_payload.get("host_mutations") is not False
        or update_dry_run_payload.get("apply_required") is not True
        or update_dry_run_payload.get("readback") is not None
    ):
        raise AssertionError("pr metadata-update must default to dry-run local render/preflight without host mutation")


def assert_governance_intensity_metadata_preflight_fixture(tmp: Path) -> None:
    target = tmp / "governance-intensity-metadata"
    target.mkdir()
    write_governance_metadata_contract_fixture(target)
    repo_interface = json.loads((target / ".loom/companion/repo-interface.json").read_text(encoding="utf-8"))
    machine_carrier = repo_interface["metadata_contract"]["fields"][0]["machine_carrier"]
    if machine_carrier.get("binding_priority", [])[:3] != [
        "cli_explicit_input",
        "pr_body_machine_carrier",
        "host_readback",
    ] or "missing_human_backlink" not in machine_carrier.get("safe_repair", {}).get("allowed_targets", []):
        raise AssertionError("governance intensity metadata contract must expose binding priority and safe repair")
    positive = target / "positive.md"
    positive.write_text(governance_metadata_body(), encoding="utf-8")
    positive_payload = governance_metadata_preflight_payload(target, "positive.md")
    if positive_payload.get("result") != "pass" or not positive_payload.get("governance_intensity_carrier"):
        raise AssertionError("governance intensity metadata positive fixture did not pass")

    missing_issue_backlink = target / "missing-issue-backlink.md"
    missing_issue_backlink.write_text(governance_metadata_body(), encoding="utf-8")
    pr_payload = target / "missing-issue-pr.json"
    pr_payload.write_text(
        json.dumps(
            {
                "number": 2001,
                "state": "OPEN",
                "title": "Fixture PR",
                "body": missing_issue_backlink.read_text(encoding="utf-8"),
                "isDraft": False,
                "headRefName": "work/1321-governance-intensity-metadata-carrier",
                "headRefOid": "1111111111111111111111111111111111111111",
                "baseRefName": "main",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, missing_issue_payload = run_flow_json(
        [
            "pr-metadata",
            "preflight",
            "--target",
            str(target),
            "--surface",
            "merge_ready",
            "--body-file",
            "missing-issue-backlink.md",
            "--pr-payload-file",
            "missing-issue-pr.json",
            "--issue",
            "1687",
        ],
        expect=1,
    )
    repair_action = next(
        (
            action
            for action in missing_issue_payload.get("safe_repair_actions", [])
            if isinstance(action, dict) and action.get("kind") == "missing_human_backlink"
        ),
        None,
    )
    if (
        missing_issue_payload.get("result") != "block"
        or "PR body is missing Issue backlink: #1687" not in missing_issue_payload.get("missing_inputs", [])
        or not isinstance(repair_action, dict)
        or repair_action.get("action") != "update_pr_body_issue_backlink"
        or repair_action.get("body_line") != "- Issue: #1687"
        or "--issue 1687" not in str(repair_action.get("next_command"))
    ):
        raise AssertionError("missing Issue backlink did not expose a safe PR body repair action")

    light_docs_only = target / "light-docs-only.md"
    light_docs_only.write_text(
        governance_metadata_body(
            fields_override={
                "governance_intensity": "light",
                "change_class": "docs_only",
                "suite_path": "not_applicable",
                "suite_not_applicable": {
                    "rationale": "non-executable documentation clarification does not need formal suite artifacts",
                    "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                    "recheck_condition": "scope expands beyond documentation text and current carrier evidence",
                    "scope_proof": "diff is limited to documentation and current Loom carriers",
                    "review_requirement": "current_head_review_required",
                },
            }
        ),
        encoding="utf-8",
    )
    light_docs_only_payload = governance_metadata_preflight_payload(target, "light-docs-only.md")
    if light_docs_only_payload.get("result") != "pass":
        raise AssertionError(f"light docs-only metadata fixture did not pass: {light_docs_only_payload.get('missing_inputs')}")

    light_fixture = target / "light-fixture.md"
    light_fixture.write_text(
        governance_metadata_body(
            fields_override={
                "governance_intensity": "light",
                "change_class": "fixture",
                "suite_path": "minimal",
            }
        ),
        encoding="utf-8",
    )
    light_fixture_payload = governance_metadata_preflight_payload(target, "light-fixture.md")
    if light_fixture_payload.get("result") != "pass":
        raise AssertionError(f"light fixture metadata fixture did not pass: {light_fixture_payload.get('missing_inputs')}")

    negative_cases: dict[str, dict[str, Any]] = {
        "missing-intensity.md": {"governance_intensity": "__DELETE__"},
        "unknown-intensity.md": {"governance_intensity": "casual"},
        "light-runtime.md": {"governance_intensity": "light", "change_class": "runtime"},
        "light-release-impacting-docs.md": {"governance_intensity": "light", "change_class": "release"},
        "light-workflow.md": {"governance_intensity": "light", "change_class": "workflow"},
        "light-metadata-schema.md": {"governance_intensity": "light", "change_class": "metadata_schema"},
        "light-host-write.md": {"governance_intensity": "light", "change_class": "host_write"},
        "light-permissions.md": {"governance_intensity": "light", "change_class": "permissions"},
        "light-contract.md": {"governance_intensity": "light", "change_class": "contract"},
        "light-docs-governance-minimal.md": {
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "minimal",
        },
        "deferred-release.md": {"release_judgment": "deferred_release_judgment_blocking"},
        "missing-na-rationale.md": {
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "scope changes",
                "scope_proof": "docs-only diff",
                "review_requirement": "current_head_review_required",
            },
        },
        "branch-conflict.md": {"branch": "feature/not-a-work-branch"},
        "head-conflict.md": {"head_sha": "2222222222222222222222222222222222222222"},
    }
    for body_name, overrides in negative_cases.items():
        (target / body_name).write_text(governance_metadata_body(fields_override=overrides), encoding="utf-8")
        payload = governance_metadata_preflight_payload(target, body_name, expect=1)
        if payload.get("result") != "block":
            raise AssertionError(f"governance intensity metadata negative fixture did not block: {body_name}")
        if "PR metadata machine block invalid: loom-governance-intensity" not in payload.get("missing_inputs", []):
            raise AssertionError(f"governance intensity metadata fixture did not report invalid block: {body_name}")

    unknown_intensity_payload = governance_metadata_preflight_payload(target, "unknown-intensity.md", expect=1)
    first_unknown_diagnostic = next(
        (
            diagnostic
            for diagnostic in unknown_intensity_payload.get("diagnostics", [])
            if isinstance(diagnostic, dict)
        ),
        None,
    )
    if (
        not isinstance(first_unknown_diagnostic, dict)
        or first_unknown_diagnostic.get("classifier") != "enum_violation"
        or "fields.governance_intensity" not in (first_unknown_diagnostic.get("allowed_values") or {})
        or "allowed values" not in str(first_unknown_diagnostic.get("next_action"))
    ):
        raise AssertionError("enum violations must expose legal values and a rewrite next_action")

    head_conflict_payload = governance_metadata_preflight_payload(target, "head-conflict.md", expect=1)
    head_conflict_diagnostic = next(
        (
            diagnostic
            for diagnostic in head_conflict_payload.get("diagnostics", [])
            if isinstance(diagnostic, dict) and "fields.head_sha" in diagnostic.get("missing_fields", [])
        ),
        None,
    )
    if (
        not isinstance(head_conflict_diagnostic, dict)
        or head_conflict_diagnostic.get("classifier") != "head_sha_drift"
        or "--head-sha" not in str(head_conflict_diagnostic.get("next_action"))
    ):
        raise AssertionError("head_sha drift diagnostics must expose a targeted next_action")

    branch_conflict_payload = governance_metadata_preflight_payload(target, "branch-conflict.md", expect=1)
    branch_conflict_diagnostic = next(
        (
            diagnostic
            for diagnostic in branch_conflict_payload.get("diagnostics", [])
            if isinstance(diagnostic, dict) and "fields.branch" in diagnostic.get("missing_fields", [])
        ),
        None,
    )
    if (
        not isinstance(branch_conflict_diagnostic, dict)
        or branch_conflict_diagnostic.get("classifier") != "branch_drift"
        or "--branch" not in str(branch_conflict_diagnostic.get("next_action"))
    ):
        raise AssertionError("branch drift diagnostics must expose a targeted next_action")

    surface_mismatch = target / "surface-mismatch.md"
    surface_mismatch.write_text(governance_metadata_body(surface="closeout"), encoding="utf-8")
    _, surface_mismatch_payload = run_flow_json(
        [
            "pr-metadata",
            "preflight",
            "--target",
            str(target),
            "--surface",
            "merge_ready",
            "--body-file",
            "surface-mismatch.md",
        ],
        expect=1,
    )
    surface_diagnostic = next(
        (
            diagnostic
            for diagnostic in surface_mismatch_payload.get("diagnostics", [])
            if isinstance(diagnostic, dict)
        ),
        None,
    )
    if (
        not isinstance(surface_diagnostic, dict)
        or surface_diagnostic.get("classifier") != "surface_drift"
        or "`merge_ready`" not in str(surface_diagnostic.get("next_action"))
    ):
        raise AssertionError("surface drift diagnostics must expose the expected surface next_action")

    docs_governance_lite = target / "docs-governance-lite.md"
    docs_governance_lite.write_text(
        governance_metadata_body(
            fields_override={
                "governance_intensity": "light",
                "change_class": "docs_governance",
                "suite_path": "not_applicable",
                "suite_not_applicable": {
                    "rationale": "docs-governance clarification does not need formal suite artifacts",
                    "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                    "recheck_condition": "scope expands beyond docs-governance methodology or current carrier evidence",
                    "scope_proof": "diff is limited to governance docs and current Loom carriers",
                    "review_requirement": "current_head_review_required",
                },
            }
        ),
        encoding="utf-8",
    )
    lite_payload = governance_metadata_preflight_payload(target, "docs-governance-lite.md")
    if lite_payload.get("result") != "pass":
        raise AssertionError(f"docs-governance lite metadata fixture did not pass: {lite_payload.get('missing_inputs')}")
    _, review_surface_payload = run_flow_json(
        [
            "pr-metadata",
            "preflight",
            "--target",
            str(target),
            "--surface",
            "review",
            "--body-file",
            "docs-governance-lite.md",
        ]
    )
    if review_surface_payload.get("result") != "pass":
        raise AssertionError("review surface did not consume the declared merge_ready governance metadata carrier")
    docs_governance_lite_closeout = target / "docs-governance-lite-closeout.md"
    docs_governance_lite_closeout.write_text(
        governance_metadata_body(
            surface="closeout",
            fields_override={
                "governance_intensity": "light",
                "change_class": "docs_governance",
                "suite_path": "not_applicable",
                "suite_not_applicable": {
                    "rationale": "docs-governance clarification does not need formal suite artifacts",
                    "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                    "recheck_condition": "scope expands beyond docs-governance methodology or current carrier evidence",
                    "scope_proof": "diff is limited to governance docs and current Loom carriers",
                    "review_requirement": "current_head_review_required",
                },
            },
        ),
        encoding="utf-8",
    )
    _, closeout_surface_payload = run_flow_json(
        [
            "pr-metadata",
            "preflight",
            "--target",
            str(target),
            "--surface",
            "closeout",
            "--body-file",
            "docs-governance-lite-closeout.md",
        ]
    )
    if closeout_surface_payload.get("result") != "pass":
        raise AssertionError("closeout surface did not consume the declared closeout governance metadata carrier")

    readback_drift = target / "docs-governance-lite-readback-drift.md"
    readback_drift.write_text(
        docs_governance_lite.read_text(encoding="utf-8").replace(
            '"release_judgment": "no_release"',
            '"release_judgment": "release_required"',
        ),
        encoding="utf-8",
    )
    _, readback_drift_payload = run_flow_json(
        [
            "pr-metadata",
            "preflight",
            "--target",
            str(target),
            "--surface",
            "merge_ready",
            "--body-file",
            "docs-governance-lite.md",
            "--compare-body-file",
            "docs-governance-lite-readback-drift.md",
        ],
        expect=1,
    )
    if readback_drift_payload.get("result") != "block":
        raise AssertionError("PR body readback drift did not fail closed")
    body_artifact = readback_drift_payload.get("body_artifact")
    if not isinstance(body_artifact, dict) or body_artifact.get("result") != "block":
        raise AssertionError("PR body readback drift did not expose body_artifact block evidence")


def append_pr_metadata_surface(target: Path, fixture: dict[str, str], *, surface: str) -> None:
    pr_path = target / fixture["pr_file"]
    payload = json.loads(pr_path.read_text(encoding="utf-8"))
    head_sha = payload["headRefOid"]
    payload["body"] = (
        f"Loom Work Item: {fixture['item']}\n"
        f"Branch: {fixture['branch']}\n"
        f"Head SHA: {head_sha}\n\n"
        "<!-- loom:repo-pr-metadata\n"
        "{\n"
        '  "schema_version": "loom-repo-pr-metadata/v1",\n'
        '  "metadata_contract_id": "loom-default-pr-binding",\n'
        f'  "surface": "{surface}",\n'
        '  "fields": {\n'
        f'    "loom_work_item": "{fixture["item"]}",\n'
        f'    "branch": "{fixture["branch"]}",\n'
        f'    "head_sha": "{head_sha}"\n'
        "  },\n"
        '  "source": {"rendered_hash": "sha256:fixture"},\n'
        '  "parser_version": "repo-parser/v1"\n'
        "}\n"
        "-->\n"
    )
    pr_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_governance_intensity_metadata_body(
    target: Path,
    fixture: dict[str, str],
    *,
    include_legacy_bindings: bool = True,
    fields_override: dict[str, Any] | None = None,
    surface: str = "merge_ready",
) -> None:
    pr_path = target / fixture["pr_file"]
    payload = json.loads(pr_path.read_text(encoding="utf-8"))
    payload["body"] = governance_metadata_body(
        item=fixture["item"],
        branch=fixture["branch"],
        head_sha=payload["headRefOid"],
        include_legacy_bindings=include_legacy_bindings,
        fields_override=fields_override,
        surface=surface,
    )
    pr_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_docs_governance_not_applicable_suite(target: Path, item: str) -> None:
    suite_dir = target / ".loom" / "specs" / item
    for extra_artifact in (
        "suite-index.md",
        "research.md",
        "contracts.md",
        "readiness-checklist.md",
        "evidence-map.md",
        "consistency-analysis.md",
        "execution-breakdown.md",
        "task-carrier.md",
    ):
        path = suite_dir / extra_artifact
        if path.exists():
            path.unlink()
    not_applicable_text = (
        "- Suite path: not_applicable\n\n"
        "- Formal-suite not_applicable:\n"
        "  - rationale: docs-governance lite fixture only clarifies governance docs and current carrier evidence.\n"
        "  - consumer boundary: suite validate, spec review, implementation review, merge-ready, PR gate, hosted CI, and closeout consume this only as the formal suite decision while fact-chain, current-head review, PR metadata, no-release judgment, controlled merge, and closeout remain required.\n"
        "  - recheck condition: require a full or minimal suite if scope expands into runtime code, tools, fixtures, metadata schema, generated payloads, release mechanics, AGENTS root rules, or external-visible behavior.\n"
        "  - scope proof: fixture diff is limited to governance docs and current Loom carriers.\n"
        "  - review requirement: current_head_review_required.\n"
    )
    (suite_dir / "spec.md").write_text("# Spec\n\n" + not_applicable_text, encoding="utf-8")
    (suite_dir / "plan.md").write_text("# Plan\n\n" + not_applicable_text, encoding="utf-8")


def write_governance_intensity_minimal_suite(target: Path, item: str) -> None:
    suite_dir = target / ".loom" / "specs" / item
    for extra_artifact in (
        "suite-index.md",
        "research.md",
        "contracts.md",
        "readiness-checklist.md",
        "consistency-analysis.md",
    ):
        path = suite_dir / extra_artifact
        if path.exists():
            path.unlink()
    (suite_dir / "spec.md").write_text(
        "# Spec\n\n"
        "- Suite path: minimal\n\n"
        "## Scenarios\n\n"
        "- Scenario S1: A low-risk fixture-only change uses minimal suite evidence.\n\n"
        "## Acceptance Criteria\n\n"
        "- AC-1: PR gate consumes light fixture metadata without requiring whole-suite bypass.\n"
        "- AC-2: Suite validation keeps behavior, test, and carrier evidence present.\n\n"
        "- full-path-artifacts not_applicable rationale: fixture-only governance intensity gate regression uses the minimal suite path instead of full optional artifacts; "
        "consumer boundary: suite validate consumes this only as full-artifact non-applicability while minimal suite evidence, implementation review, merge-ready, PR gate, and closeout remain required; "
        "recheck condition: require full suite artifacts if scope expands beyond fixture or contract-test coverage.\n",
        encoding="utf-8",
    )
    (suite_dir / "plan.md").write_text(
        "# Plan\n\n"
        "- Suite path: minimal\n\n"
        "## Validation\n\n"
        "- S1 -> test evidence: `python3 tools/check_cli_contract.py --surface pr-metadata`.\n"
        "- AC-1 -> test evidence: `python3 tools/check_cli_contract.py --surface pr-metadata`.\n"
        "- AC-2 -> test evidence: `python3 tools/check_cli_contract.py --surface pr-metadata`.\n",
        encoding="utf-8",
    )
    (suite_dir / "evidence-map.md").write_text(
        "# Evidence Map\n\n"
        "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| EV-001 | behavior_evidence | .loom/specs/{item}/spec.md | light fixture minimal suite behavior | {item} / governance-intensity-pr-gate | present | PR gate fixture | Re-run contract fixtures after metadata gate changes. |\n"
        f"| EV-002 | test_evidence | .loom/specs/{item}/plan.md | PR gate fixture coverage | {item} / governance-intensity-pr-gate | present | PR gate fixture | Re-run contract fixtures after metadata gate changes. |\n"
        f"| EV-003 | fresh_verification_input | .loom/progress/{item}.md | EV-001 EV-002 | {item} / latest validation summary | present | review / merge-ready / closeout | Refresh progress summary after validation changes. |\n",
        encoding="utf-8",
    )
    (suite_dir / "task-carrier.md").write_text(
        "# Task Carrier\n\n"
        "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| github_issue | https://github.com/owner/repo/issues/1287 | fixture-only PR gate regression | in_progress | primary | .loom/work-items/{item}.md | .loom/work-items/{item}.md#static-facts | .loom/specs/{item}/spec.md#scenario-s1 | .loom/specs/{item}/plan.md#validation | .loom/specs/{item}/plan.md#validation | governance intensity fixture | Recheck before PR gate consumption. |\n",
        encoding="utf-8",
    )


def prepare_current_head_reviewed_fixture(target: Path, fixture: dict[str, str], commit_message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=target,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    record_current_fixture_spec_review(target, fixture)
    commit_fixture_file(target, f".loom/reviews/{fixture['item']}.spec.json", "fixture spec review refresh")
    record_current_fixture_review(target, fixture)
    update_fixture_pr_head(target, fixture)


def assert_governance_intensity_pr_gate_positive_variants(tmp: Path) -> None:
    docs_target = tmp / "governance-intensity-pr-gate-docs-only"
    docs_target.mkdir()
    docs_fixture = write_semantic_review_pr_gate_fixture(docs_target)
    write_governance_metadata_contract_fixture(docs_target)
    write_docs_governance_not_applicable_suite(docs_target, docs_fixture["item"])
    prepare_current_head_reviewed_fixture(docs_target, docs_fixture, "fixture docs-only light metadata and suite")
    append_governance_intensity_metadata_body(
        docs_target,
        docs_fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_only",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "docs-only fixture does not need formal suite artifacts",
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond documentation text and current carrier evidence",
                "scope_proof": "diff is limited to documentation and current Loom carriers",
                "review_requirement": "current_head_review_required",
            },
        },
    )
    docs_suite_payload = run_suite_validate_fixture(docs_target, docs_fixture["item"], expect=1)
    if docs_suite_payload.get("result") != "not_applicable":
        raise AssertionError("light docs-only suite validate fixture did not return not_applicable")
    docs_payload = semantic_pr_gate_fixture_payload(docs_target, docs_fixture)
    docs_intensity_gate = docs_payload.get("governance_intensity_gate", {})
    if (
        docs_payload.get("result") != "pass"
        or docs_intensity_gate.get("result") != "pass"
        or docs_intensity_gate.get("metadata_fields", {}).get("change_class") != "docs_only"
        or docs_intensity_gate.get("effective_suite_path") != "not_applicable"
    ):
        raise AssertionError(f"light docs-only pr-gate fixture blocked: {docs_payload.get('missing_inputs')}")

    fixture_target = tmp / "governance-intensity-pr-gate-fixture"
    fixture_target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(fixture_target)
    write_governance_metadata_contract_fixture(fixture_target)
    write_governance_intensity_minimal_suite(fixture_target, fixture["item"])
    prepare_current_head_reviewed_fixture(fixture_target, fixture, "fixture light minimal metadata and suite")
    append_governance_intensity_metadata_body(
        fixture_target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "fixture",
            "suite_path": "minimal",
        },
    )
    fixture_suite_payload = run_suite_validate_fixture(fixture_target, fixture["item"])
    if fixture_suite_payload.get("result") != "pass":
        raise AssertionError("light fixture minimal suite validate fixture did not pass")
    fixture_payload = semantic_pr_gate_fixture_payload(fixture_target, fixture)
    fixture_intensity_gate = fixture_payload.get("governance_intensity_gate", {})
    if (
        fixture_payload.get("result") != "pass"
        or fixture_intensity_gate.get("result") != "pass"
        or fixture_intensity_gate.get("metadata_fields", {}).get("change_class") != "fixture"
        or fixture_intensity_gate.get("effective_suite_path") != "minimal"
    ):
        raise AssertionError(f"light fixture minimal pr-gate fixture blocked: {fixture_payload.get('missing_inputs')}")


def assert_docs_governance_lite_pr_gate_fixture(tmp: Path) -> None:
    target = tmp / "docs-governance-lite-pr-gate"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    write_governance_metadata_contract_fixture(target)
    write_docs_governance_not_applicable_suite(target, fixture["item"])
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-m", "fixture docs governance lite metadata and suite"],
        cwd=target,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    record_current_fixture_spec_review(target, fixture)
    commit_fixture_file(target, f".loom/reviews/{fixture['item']}.spec.json", "fixture spec review refresh")
    _, review_record_payload = run_flow_json(
        [
            "review",
            "record",
            "--target",
            str(target),
            "--item",
            fixture["item"],
            "--review-file",
            fixture["review_path"],
            "--decision",
            "allow",
            "--kind",
            "code_review",
            "--summary",
            "Fixture docs-governance lite review approves the current head.",
            "--reviewer",
            "contract-test",
        ]
    )
    if review_record_payload.get("result") != "pass":
        raise AssertionError(f"docs-governance lite review record fixture failed: {review_record_payload.get('missing_inputs')}")
    update_fixture_pr_head(target, fixture)
    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "docs-governance lite fixture does not need formal suite artifacts",
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond governance docs and current carrier evidence",
                "scope_proof": "diff is limited to governance docs and current Loom carriers",
                "review_requirement": "current_head_review_required",
            },
        },
    )
    suite_payload = run_suite_validate_fixture(target, fixture["item"], expect=1)
    if suite_payload.get("result") != "not_applicable":
        raise AssertionError("docs-governance lite suite validate fixture did not return not_applicable")
    pass_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if pass_payload.get("result") != "pass":
        raise AssertionError(f"docs-governance lite pr-gate fixture blocked: {pass_payload.get('missing_inputs')}")
    intensity_gate = pass_payload.get("governance_intensity_gate", {})
    if (
        intensity_gate.get("result") != "pass"
        or intensity_gate.get("effective_governance_intensity") != "light"
        or intensity_gate.get("effective_suite_path") != "not_applicable"
        or intensity_gate.get("upgrade_reasons") != []
        or "fact_chain" not in intensity_gate.get("authority_boundary", {}).get("does_not_replace", [])
    ):
        raise AssertionError("governance intensity gate did not expose the generalized pass payload")
    lite_gate = pass_payload.get("docs_governance_lite_gate", {})
    if lite_gate.get("result") != "pass":
        raise AssertionError("docs-governance lite pr-gate did not consume the positive gate payload")
    if pass_payload.get("merge_checkpoint", {}).get("result") != "pass":
        raise AssertionError("docs-governance lite pr-gate did not preserve merge checkpoint enforcement")

    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "minimal",
        },
    )
    assert_pr_gate_blocks(
        target,
        fixture,
        "docs-governance lite metadata/suite mismatch",
        expected_missing="PR metadata machine block invalid: loom-governance-intensity",
    )

    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond governance docs and current carrier evidence",
                "scope_proof": "diff is limited to governance docs and current Loom carriers",
                "review_requirement": "current_head_review_required",
            },
        },
    )
    assert_pr_gate_blocks(
        target,
        fixture,
        "docs-governance lite missing rationale",
        expected_missing="PR metadata machine block invalid: loom-governance-intensity",
    )

    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "not_applicable",
            "review_requirement": "specialized_review_required",
            "suite_not_applicable": {
                "rationale": "docs-governance lite fixture does not need formal suite artifacts",
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond governance docs and current carrier evidence",
                "scope_proof": "diff is limited to governance docs and current Loom carriers",
                "review_requirement": "specialized_review_required",
            },
        },
    )
    assert_pr_gate_blocks(
        target,
        fixture,
        "docs-governance lite non-current-head review requirement",
        expected_missing="PR metadata machine block invalid: loom-governance-intensity",
    )

    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "not_applicable",
            "release_judgment": "deferred_release_judgment_blocking",
            "suite_not_applicable": {
                "rationale": "docs-governance lite fixture does not need formal suite artifacts",
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond governance docs and current carrier evidence",
                "scope_proof": "diff is limited to governance docs and current Loom carriers",
                "review_requirement": "current_head_review_required",
            },
        },
    )
    assert_pr_gate_blocks(
        target,
        fixture,
        "docs-governance lite deferred release judgment",
        expected_missing="PR metadata machine block invalid: loom-governance-intensity",
    )

    abuse_cases: dict[str, dict[str, Any]] = {
        "runtime/code change declared as light": {
            "governance_intensity": "light",
            "change_class": "runtime",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "runtime behavior cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "runtime code changes require stronger governance",
                "scope_proof": "fixture intentionally models runtime/code change abuse",
                "review_requirement": "current_head_review_required",
            },
        },
        "fixture change declared as light": {
            "governance_intensity": "light",
            "change_class": "fixture",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "fixture changes cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "fixture changes require stronger governance",
                "scope_proof": "fixture intentionally models regression fixture abuse",
                "review_requirement": "current_head_review_required",
            },
        },
        "release-impacting docs declared as light": {
            "governance_intensity": "light",
            "change_class": "release",
            "suite_path": "not_applicable",
            "release_judgment": "release_required",
            "suite_not_applicable": {
                "rationale": "release-impacting docs cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "release-impacting scope requires release evidence",
                "scope_proof": "fixture intentionally models release-impacting docs abuse",
                "review_requirement": "current_head_review_required",
            },
        },
        "workflow change declared as light": {
            "governance_intensity": "light",
            "change_class": "workflow",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "workflow changes cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "workflow changes alter automation or CI behavior",
                "scope_proof": "fixture intentionally models workflow change abuse",
                "review_requirement": "current_head_review_required",
            },
        },
        "PR metadata schema change declared as light": {
            "governance_intensity": "light",
            "change_class": "metadata_schema",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "PR metadata schema changes cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "metadata schema changes alter gate input parsing",
                "scope_proof": "fixture intentionally models PR metadata schema abuse",
                "review_requirement": "current_head_review_required",
            },
        },
        "host write change declared as light": {
            "governance_intensity": "light",
            "change_class": "host_write",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "host write changes cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "host write changes mutate external control-plane state",
                "scope_proof": "fixture intentionally models host write abuse",
                "review_requirement": "current_head_review_required",
            },
        },
        "permissions change declared as light": {
            "governance_intensity": "light",
            "change_class": "permissions",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "permission changes cannot use docs-governance light bypass",
                "consumer_boundary": "suite validate and pr-gate",
                "recheck_condition": "permission changes alter security or host authorization",
                "scope_proof": "fixture intentionally models permissions abuse",
                "review_requirement": "current_head_review_required",
            },
        },
    }
    for label, overrides in abuse_cases.items():
        append_governance_intensity_metadata_body(target, fixture, fields_override=overrides)
        assert_pr_gate_blocks(
            target,
            fixture,
            label,
            expected_missing="PR metadata machine block invalid: loom-governance-intensity",
        )

    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "not_applicable",
            "head_sha": "0" * 40,
            "suite_not_applicable": {
                "rationale": "docs-governance lite fixture does not need formal suite artifacts",
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond governance docs and current carrier evidence",
                "scope_proof": "diff is limited to governance docs and current Loom carriers",
                "review_requirement": "current_head_review_required",
            },
        },
    )
    assert_pr_gate_blocks(
        target,
        fixture,
        "governance metadata carrier/head mismatch",
        expected_missing="PR metadata machine block invalid: loom-governance-intensity",
    )

    update_fixture_pr_head(target, fixture, extra={"headRefName": "work/1323-mismatched-pr-branch"})
    append_governance_intensity_metadata_body(
        target,
        fixture,
        fields_override={
            "governance_intensity": "light",
            "change_class": "docs_governance",
            "suite_path": "not_applicable",
            "suite_not_applicable": {
                "rationale": "docs-governance lite fixture does not need formal suite artifacts",
                "consumer_boundary": "suite validate and pr-gate consume only formal suite non-applicability",
                "recheck_condition": "scope expands beyond governance docs and current carrier evidence",
                "scope_proof": "diff is limited to governance docs and current Loom carriers",
                "review_requirement": "current_head_review_required",
            },
        },
    )
    assert_pr_gate_blocks(
        target,
        fixture,
        "PR body branch mismatch",
        expected_missing="PR body Branch does not match PR payload headRefName",
    )


def assert_terminal_closeout_pr_gate_fixture(tmp: Path) -> None:
    target = tmp / "terminal-closeout-pr-gate"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    item = fixture["item"]
    write_hosted_freeze_admission_inputs(target)
    subprocess.run(["git", "add", "."], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["git", "commit", "-m", "fixture terminal closeout hosted admission inputs"],
        cwd=target,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    update_fixture_pr_head(target, fixture)
    record_current_fixture_review(target, fixture)
    progress_path = target / ".loom" / "progress" / f"{item}.md"
    status_path = target / ".loom" / "status" / "current.md"
    task_carrier_path = target / ".loom" / "specs" / item / "task-carrier.md"
    progress_text = progress_path.read_text(encoding="utf-8").replace(
        "- Current Checkpoint: merge",
        "- Current Checkpoint: closed_out",
    ).replace(
        "- Current Stop: Fixture is ready for pr-gate semantic disposition checks.",
        "- Current Stop: Fixture implementation PR is merged and closeout carrier sync is pending.",
    ).replace(
        "- Next Step: Run pr-gate semantic disposition fixtures.",
        "- Next Step: Merge the closeout-only carrier sync.",
    ).replace(
        "- Current Lane: pr-gate-fixture",
        "- Current Lane: post-merge-closeout-consumed",
    )
    progress_path.write_text(progress_text, encoding="utf-8")
    status_text = status_path.read_text(encoding="utf-8").replace(
        "- Current Checkpoint: merge",
        "- Current Checkpoint: closed_out",
    ).replace(
        "- Current Stop: Fixture is ready for pr-gate semantic disposition checks.",
        "- Current Stop: Fixture implementation PR is merged and closeout carrier sync is pending.",
    ).replace(
        "- Next Step: Run pr-gate semantic disposition fixtures.",
        "- Next Step: Merge the closeout-only carrier sync.",
    ).replace(
        "- Current Lane: pr-gate-fixture",
        "- Current Lane: post-merge-closeout-consumed",
    )
    status_path.write_text(status_text, encoding="utf-8")
    task_carrier_path.write_text(
        task_carrier_path.read_text(encoding="utf-8")
        + "\n| closeout_carrier | fixture PR merged / closeout sync pending | done | primary |\n",
        encoding="utf-8",
    )
    commit_fixture_file(target, f".loom/progress/{item}.md", "fixture terminal closeout progress")
    commit_fixture_file(target, ".loom/status/current.md", "fixture terminal closeout status")
    commit_fixture_file(target, f".loom/specs/{item}/task-carrier.md", "fixture terminal closeout task carrier")
    update_fixture_pr_head(target, fixture)
    append_governance_intensity_metadata_body(target, fixture, surface="closeout")
    closeout_payload = semantic_pr_gate_fixture_payload(target, fixture, surface="closeout")
    checkpoint_step = next(
        (
            step
            for step in closeout_payload.get("steps", [])
            if isinstance(step, dict) and step.get("name") == "checkpoint-merge"
        ),
        {},
    )
    if (
        closeout_payload.get("result") != "pass"
        or closeout_payload.get("review_approval", {}).get("status") != "terminal_closeout_retained"
        or closeout_payload.get("terminal_closeout_consumption", {}).get("result") != "pass"
        or closeout_payload.get("pr_metadata_preflight", {}).get("surface") != "closeout"
        or checkpoint_step.get("terminal_closed_checkpoint") is not True
    ):
        step_names = [
            step.get("name")
            for step in closeout_payload.get("steps", [])
            if isinstance(step, dict)
        ]
        raise AssertionError(
            "terminal closeout pr-gate fixture did not pass: "
            f"{closeout_payload.get('missing_inputs')}; steps={step_names}"
        )
    pr_closeout_gate = closeout_payload.get("closeout_specific_gate", {})
    if (
        pr_closeout_gate.get("schema_version") != "loom-closeout-specific-gate/v1"
        or pr_closeout_gate.get("source") != "pr-gate"
        or pr_closeout_gate.get("result") != "pass"
        or pr_closeout_gate.get("verdict") != "closeout_pr_allowed"
        or pr_closeout_gate.get("next_action") != "closeout_pr_allowed"
    ):
        raise AssertionError(f"terminal closeout pr-gate must expose passing closeout-specific gate verdict: {pr_closeout_gate}")
    pr_payload = json.loads((target / fixture["pr_file"]).read_text(encoding="utf-8"))
    hosted_body_file = f".loom/fixtures/{item}/closeout-hosted-pr-body.md"
    (target / hosted_body_file).write_text(pr_payload["body"], encoding="utf-8")
    hosted_closeout_payload = semantic_pr_gate_fixture_payload(
        target,
        fixture,
        surface="closeout",
        body_file=hosted_body_file,
        compare_body_file=hosted_body_file,
    )
    hosted_admission = hosted_closeout_payload.get("hosted_freeze_admission", {})
    hosted_freeze_surface = (
        hosted_admission.get("recomputed_freeze", {})
        .get("snapshot_subject", {})
        .get("surface")
    )
    hosted_carrier_refresh = (
        hosted_admission.get("recomputed_freeze", {})
        .get("input_bindings", {})
        .get("carrier_refresh", {})
    )
    if (
        hosted_closeout_payload.get("result") != "pass"
        or hosted_admission.get("result") != "pass"
        or hosted_freeze_surface != "closeout"
        or hosted_carrier_refresh.get("result") != "pass"
    ):
        raise AssertionError(
            "terminal closeout hosted admission did not preserve closeout surface: "
            f"result={hosted_closeout_payload.get('result')}; "
            f"admission={hosted_admission.get('result')}; "
            f"freeze_surface={hosted_freeze_surface}; "
            f"carrier_refresh={hosted_carrier_refresh.get('result')}; "
            f"missing={hosted_closeout_payload.get('missing_inputs')}"
        )
    _, direct_carrier_refresh = run_flow_json(
        [
            "carrier",
            "refresh",
            "--target",
            str(target),
            "--item",
            item,
            "--surface",
            "closeout",
        ]
    )
    if direct_carrier_refresh.get("result") != "pass" or direct_carrier_refresh.get("surface") != "closeout":
        raise AssertionError(
            "carrier refresh --surface closeout did not consume terminal closeout carrier paths: "
            f"{direct_carrier_refresh.get('missing_inputs')}"
        )
    _, direct_gate_freeze = run_flow_json(
        [
            "gate-freeze",
            "check",
            "--target",
            str(target),
            "--item",
            item,
            "--surface",
            "closeout",
            "--pr-payload-file",
            fixture["pr_file"],
            "--body-file",
            hosted_body_file,
            "--compare-body-file",
            hosted_body_file,
        ]
    )
    if (
        direct_gate_freeze.get("result") != "pass"
        or direct_gate_freeze.get("snapshot_subject", {}).get("surface") != "closeout"
    ):
        raise AssertionError(
            "gate-freeze --surface closeout did not emit a hosted closeout freeze snapshot: "
            f"{direct_gate_freeze.get('missing_inputs')}"
        )

    spec_review_path = target / ".loom" / "reviews" / f"{item}.spec.json"
    spec_review = json.loads(spec_review_path.read_text(encoding="utf-8"))
    spec_review["reviewed_head"] = "0" * 40
    spec_review_path.write_text(json.dumps(spec_review, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, f".loom/reviews/{item}.spec.json", "fixture unreachable spec review head")
    update_fixture_pr_head(target, fixture)
    append_governance_intensity_metadata_body(target, fixture, surface="closeout")
    unreachable_spec_head_payload = semantic_pr_gate_fixture_payload(target, fixture, surface="closeout")
    if (
        unreachable_spec_head_payload.get("result") != "pass"
        or unreachable_spec_head_payload.get("terminal_closeout_consumption", {}).get("result") != "pass"
    ):
        raise AssertionError(
            "terminal closeout pr-gate did not tolerate hosted-only retained spec review head unreachability: "
            f"{unreachable_spec_head_payload.get('missing_inputs')}"
        )

    append_governance_intensity_metadata_body(target, fixture, surface="merge_ready")
    merge_ready_payload = semantic_pr_gate_fixture_payload(target, fixture, surface="merge_ready")
    if merge_ready_payload.get("result") == "pass" or merge_ready_payload.get("terminal_closeout_consumption", {}).get("result") != "block":
        raise AssertionError("terminal closeout retained review bypassed a non-closeout PR metadata surface")
    if "closeout_specific_gate" in merge_ready_payload:
        raise AssertionError("non-closeout merge_ready pr-gate must not expose closeout-specific gate verdict")


def prepare_controlled_merge_fixture(
    tmp: Path,
    *,
    fixture_name: str,
    branch_protection_contexts: list[str],
    ruleset_required_contexts: list[str] | None = None,
) -> tuple[Path, dict[str, Any], dict[str, Any], Path]:
    merge_target = tmp / fixture_name
    merge_target.mkdir()
    merge_fixture = write_semantic_review_pr_gate_fixture(merge_target)
    merge_pass_payload = semantic_pr_gate_fixture_payload(merge_target, merge_fixture)
    if merge_pass_payload.get("result") != "pass":
        raise AssertionError("controlled-merge fixture could not produce a retained pr-gate pass")
    fixture_dir = merge_target / ".loom" / "fixtures" / "WI-1287"
    check_names = sorted({"loom-pr-merge-gate", *branch_protection_contexts, *(ruleset_required_contexts or [])})
    (fixture_dir / "checks.json").write_text(
        json.dumps(
            [{"name": name, "conclusion": "SUCCESS", "status": "COMPLETED"} for name in check_names],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (fixture_dir / "branch-protection.json").write_text(
        json.dumps({"required_status_checks": {"contexts": branch_protection_contexts}}, indent=2) + "\n",
        encoding="utf-8",
    )
    ruleset_payload: list[dict[str, Any]] = []
    if ruleset_required_contexts:
        ruleset_payload = [
            {
                "type": "required_status_checks",
                "parameters": {
                    "required_status_checks": [{"context": context} for context in ruleset_required_contexts],
                },
            }
        ]
    (fixture_dir / "ruleset.json").write_text(json.dumps(ruleset_payload, indent=2) + "\n", encoding="utf-8")
    return merge_target, merge_fixture, merge_pass_payload, fixture_dir


def assert_controlled_merge_ruleset_trigger_fixture(tmp: Path) -> None:
    merge_target, merge_fixture, _, _ = prepare_controlled_merge_fixture(
        tmp,
        fixture_name="controlled-merge-ruleset-trigger",
        branch_protection_contexts=[],
        ruleset_required_contexts=["loom-pr-merge-gate"],
    )
    _, payload = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(merge_target),
            "--item",
            merge_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            merge_fixture["head_sha"],
            "--pr-payload-file",
            merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
        expect=0,
    )
    host_enforcement = payload.get("host_enforcement")
    if payload.get("result") != "pass":
        raise AssertionError("controlled-merge did not accept active ruleset required context for the triggered check surface")
    if not isinstance(host_enforcement, dict) or "loom-pr-merge-gate" not in host_enforcement.get("ruleset_required_contexts", []):
        raise AssertionError("controlled-merge did not expose active ruleset required contexts")
    if "loom-pr-merge-gate" in host_enforcement.get("branch_protection_required_contexts", []):
        raise AssertionError("controlled-merge ruleset-trigger fixture incorrectly attributed host enforcement to branch protection")
    if payload.get("pr_gate", {}).get("result") != "pass" or payload.get("controlled_merge_consumption", {}).get("result") != "pass":
        raise AssertionError("controlled-merge ruleset-trigger fixture did not preserve pre-merge gate consumption")


def assert_semantic_review_disposition_pr_gate_fixture(tmp: Path) -> None:
    target = tmp / "semantic-review-pr-gate"
    target.mkdir()
    fixture = write_semantic_review_pr_gate_fixture(target)
    loom_flow = load_loom_flow_module()
    parser_cases = {
        "Loom Work Item: WI-1287\n": "WI-1287",
        "Loom Work Item: WI-1240-1242\n": "WI-1240-1242",
        "Loom Work Item: INIT-0001\n": "INIT-0001",
    }
    for body, expected in parser_cases.items():
        if loom_flow.pr_work_item_from_body(body) != expected:
            raise AssertionError(f"PR body Work Item parser did not preserve `{expected}`")

    record_payload = record_current_fixture_review(target, fixture)
    recorded_disposition = record_payload.get("review", {}).get("record", {}).get("semantic_review_disposition", {})
    if recorded_disposition.get("status") != "passed":
        raise AssertionError("review record did not write passed semantic_review_disposition")

    pass_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if pass_payload.get("result") != "pass":
        raise AssertionError(f"semantic review disposition pass fixture blocked: {pass_payload.get('missing_inputs')}")
    disposition = pass_payload.get("review_approval", {}).get("semantic_review_disposition", {})
    if disposition.get("status") != "passed" or disposition.get("consumable") is not True:
        raise AssertionError("pr-gate did not consume passed semantic_review_disposition")
    if pass_payload.get("pr", {}).get("work_item_from_body") != fixture["item"]:
        raise AssertionError("pr-gate did not preserve single Work Item id parsing")
    assert_gate_freeze_review_binding_fixture(tmp)
    assert_hosted_freeze_admission_pr_gate_fixture(tmp)
    assert_closeout_freeze_profile_fixture(tmp)
    assert_terminal_closeout_pr_gate_fixture(tmp)
    assert_governance_intensity_pr_gate_positive_variants(tmp)
    assert_docs_governance_lite_pr_gate_fixture(tmp)
    assert_controlled_merge_ruleset_trigger_fixture(tmp)
    assert_cross_repo_review_gate_fixtures(tmp)

    pr_path = target / fixture["pr_file"]
    merge_target, merge_fixture, merge_pass_payload, fixture_dir = prepare_controlled_merge_fixture(
        tmp,
        fixture_name="semantic-review-controlled-merge",
        branch_protection_contexts=["loom-pr-merge-gate"],
    )
    _, merge_check_payload = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(merge_target),
            "--item",
            merge_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            merge_fixture["head_sha"],
            "--pr-payload-file",
            merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
        expect=0,
    )
    if (
        merge_check_payload.get("result") != "pass"
        or merge_check_payload.get("pr_gate", {}).get("result") != "pass"
        or merge_check_payload.get("controlled_merge_consumption", {}).get("result") != "pass"
    ):
        raise AssertionError("controlled-merge did not consume inline pr-gate pass before host merge")
    if merge_check_payload.get("triggered_check_rollup", {}).get("result") != "pass":
        raise AssertionError("controlled-merge positive fixture did not allow successful triggered checks")

    failed_triggered_file = fixture_dir / "checks-triggered-failed.json"
    failed_triggered_file.write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {
                    "name": "optional-ci",
                    "workflowName": "optional",
                    "conclusion": "FAILURE",
                    "status": "COMPLETED",
                    "detailsUrl": "https://example.invalid/checks/optional-ci",
                },
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, failed_triggered_payload = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(merge_target),
            "--item",
            merge_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            merge_fixture["head_sha"],
            "--pr-payload-file",
            merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks-triggered-failed.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
    )
    if (
        failed_triggered_payload.get("result") != "block"
        or failed_triggered_payload.get("required_checks", {}).get("result") != "pass"
        or failed_triggered_payload.get("triggered_check_rollup", {}).get("result") != "block"
        or "triggered checks readback"
        not in failed_triggered_payload.get("controlled_merge_consumption", {}).get("missing_inputs", [])
    ):
        raise AssertionError("controlled-merge did not block non-required failed triggered check")

    pending_triggered_file = fixture_dir / "checks-triggered-pending.json"
    pending_triggered_file.write_text(
        json.dumps(
            [
                {"name": "loom-pr-merge-gate", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "optional-pending", "workflowName": "optional", "status": "IN_PROGRESS"},
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _, pending_triggered_payload = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(merge_target),
            "--item",
            merge_fixture["item"],
            "--pr",
            "1288",
            "--head-sha",
            merge_fixture["head_sha"],
            "--pr-payload-file",
            merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks-triggered-pending.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
        ],
    )
    if (
        pending_triggered_payload.get("result") != "block"
        or pending_triggered_payload.get("required_checks", {}).get("result") != "pass"
        or "optional-pending" not in pending_triggered_payload.get("triggered_check_rollup", {}).get("pending", [])
    ):
        raise AssertionError("controlled-merge did not block pending triggered check")
    retained_gate_file = fixture_dir / "pr-gate-pass.json"
    retained_gate_file.write_text(json.dumps(merge_pass_payload, indent=2) + "\n", encoding="utf-8")
    (merge_target / "retained-gate-drift.txt").write_text("drift after retained pr-gate\n", encoding="utf-8")
    commit_fixture_file(merge_target, "retained-gate-drift.txt", "fixture retained pr gate drift")
    update_fixture_pr_head(merge_target, merge_fixture)
    _, retained_drift_payload = run_flow_json(
        [
            "controlled-merge",
            "check",
            "--target",
            str(merge_target),
            "--item",
            merge_fixture["item"],
            "--pr",
            "1288",
            "--pr-payload-file",
            merge_fixture["pr_file"],
            "--status-checks-file",
            ".loom/fixtures/WI-1287/checks.json",
            "--branch-protection-file",
            ".loom/fixtures/WI-1287/branch-protection.json",
            "--ruleset-file",
            ".loom/fixtures/WI-1287/ruleset.json",
            "--pr-gate-result-file",
            ".loom/fixtures/WI-1287/pr-gate-pass.json",
        ]
    )
    if (
        retained_drift_payload.get("result") != "block"
        or retained_drift_payload.get("retained_results", {}).get("pr_gate", {}).get("consumption", {}).get("result") != "block"
        or "controlled merge consumption: fresh retained PR gate consumption"
        not in retained_drift_payload.get("missing_inputs", [])
    ):
        raise AssertionError("controlled-merge did not block retained pr-gate head drift before host merge")

    original_pr_payload = json.loads(pr_path.read_text(encoding="utf-8"))
    aggregate_item = "WI-1240-1242"
    aggregate_pr_payload = dict(original_pr_payload)
    aggregate_pr_payload["body"] = (
        f"Loom Work Item: {aggregate_item}\n"
        f"Branch: {fixture['branch']}\n"
        f"Head SHA: {original_pr_payload['headRefOid']}\n"
    )
    pr_path.write_text(json.dumps(aggregate_pr_payload, indent=2) + "\n", encoding="utf-8")
    aggregate_payload = semantic_pr_gate_fixture_payload(target, {**fixture, "item": aggregate_item})
    if aggregate_payload.get("pr", {}).get("work_item_from_body") != aggregate_item:
        raise AssertionError("pr-gate did not parse aggregate Work Item id from PR body")
    aggregate_taxonomy = aggregate_payload.get("failure_taxonomy", [])
    if aggregate_payload.get("result") != "block" or "work_item_binding_missing" in aggregate_taxonomy:
        raise AssertionError("aggregate Work Item id parser fixture must consume the PR body Work Item binding")
    pr_path.write_text(json.dumps(original_pr_payload, indent=2) + "\n", encoding="utf-8")

    review_path = target / fixture["review_path"]
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_payload.pop("semantic_review_disposition", None)
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture missing semantic disposition")
    update_fixture_pr_head(target, fixture)
    missing_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if missing_payload.get("result") != "block" or "semantic_review_disposition_missing" not in missing_payload.get("failure_taxonomy", []):
        raise AssertionError("missing semantic_review_disposition did not fail closed")

    review_payload["semantic_review_disposition"] = {"status": "commented"}
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture unknown semantic disposition")
    update_fixture_pr_head(target, fixture)
    unknown_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if unknown_payload.get("result") != "block" or "semantic_review_disposition_invalid" not in unknown_payload.get("failure_taxonomy", []):
        raise AssertionError("unknown semantic_review_disposition did not fail closed")

    review_payload["semantic_review_disposition"] = {"status": "not_applicable", "reason": "docs-only fixture"}
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture incomplete not applicable disposition")
    update_fixture_pr_head(target, fixture)
    incomplete_na = semantic_pr_gate_fixture_payload(target, fixture)
    if incomplete_na.get("result") != "block" or "semantic_review_disposition_invalid" not in incomplete_na.get("failure_taxonomy", []):
        raise AssertionError("incomplete not_applicable semantic_review_disposition did not fail closed")

    review_payload["semantic_review_disposition"] = {
        "status": "waived",
        "reason": "explicit fixture waiver",
        "change_class": "harness_fixture",
        "substitute_validation": "targeted fixture validation",
        "authority": "fixture-owner",
        "risk_acceptance": "bounded fixture risk",
        "one_shot": True,
    }
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture waived semantic disposition")
    update_fixture_pr_head(target, fixture)
    waived_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if waived_payload.get("result") != "pass" or waived_payload.get("review_approval", {}).get("semantic_review_disposition", {}).get("status") != "waived":
        raise AssertionError("complete waived semantic_review_disposition was not consumable")

    update_fixture_pr_head(target, fixture)
    pr_path = target / fixture["pr_file"]
    pr_payload = json.loads(pr_path.read_text(encoding="utf-8"))
    pr_payload["body"] = f"Loom Work Item: {fixture['item']}\nBranch: {fixture['branch']}\n"
    pr_path.write_text(json.dumps(pr_payload, indent=2) + "\n", encoding="utf-8")
    missing_body_head = semantic_pr_gate_fixture_payload(target, fixture)
    if missing_body_head.get("result") != "block" or "head_binding_drift" not in missing_body_head.get("failure_taxonomy", []):
        raise AssertionError("missing PR body Head SHA machine carrier did not fail closed")

    update_fixture_pr_head(target, fixture)
    pr_payload = json.loads(pr_path.read_text(encoding="utf-8"))
    pr_payload["body"] = f"Loom Work Item: {fixture['item']}\nBranch: wrong-branch\nHead SHA: {pr_payload['headRefOid']}\n"
    pr_path.write_text(json.dumps(pr_payload, indent=2) + "\n", encoding="utf-8")
    wrong_body_branch = semantic_pr_gate_fixture_payload(target, fixture)
    if wrong_body_branch.get("result") != "block" or "head_binding_drift" not in wrong_body_branch.get("failure_taxonomy", []):
        raise AssertionError("mismatched PR body Branch machine carrier did not fail closed")

    (target / "implementation-drift.txt").write_text("unreviewed drift\n", encoding="utf-8")
    commit_fixture_file(target, "implementation-drift.txt", "fixture implementation drift after review")
    update_fixture_pr_head(target, fixture)
    stale_payload = semantic_pr_gate_fixture_payload(target, fixture)
    taxonomy = stale_payload.get("failure_taxonomy", [])
    if stale_payload.get("result") != "block" or "review_stale" not in taxonomy or "head_binding_drift" not in taxonomy:
        raise AssertionError("stale PR head was not classified as review_stale/head_binding_drift")

    review_payload["authored_at"] = "2026-05-31T00:00:00Z"
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture post merge authored review")
    update_fixture_pr_head(target, fixture, state="MERGED", extra={"mergedAt": "2026-05-30T00:00:00Z"})
    post_merge_payload = semantic_pr_gate_fixture_payload(target, fixture)
    post_merge_diagnostic = post_merge_payload.get("post_merge_review_diagnostic", {})
    if (
        "post_merge_review_bypass" not in post_merge_payload.get("failure_taxonomy", [])
        or post_merge_diagnostic.get("result") != "block"
        or post_merge_diagnostic.get("finding", {}).get("kind") != "post_merge_review_bypass"
        or "repair_plan" not in post_merge_diagnostic
    ):
        raise AssertionError("merged PR payload did not expose post-merge review bypass diagnostics and repair plan")

    review_payload["semantic_review_disposition"] = {"status": "required"}
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    commit_fixture_file(target, fixture["review_path"], "fixture ci only semantic disposition")
    update_fixture_pr_head(
        target,
        fixture,
        extra={"statusCheckRollup": [{"name": "ci", "conclusion": "SUCCESS", "status": "COMPLETED"}]},
    )
    ci_only_payload = semantic_pr_gate_fixture_payload(target, fixture)
    if ci_only_payload.get("result") != "block" or "ci_only_bypass" not in ci_only_payload.get("failure_taxonomy", []):
        raise AssertionError("CI-only bypass did not fail closed with ci_only_bypass taxonomy")


def assert_governance_chain_closeout_fixture(tmp: Path) -> None:
    pass_target = tmp / "governance-chain-pass"
    pass_target.mkdir()
    fixture = write_governance_chain_fixture(pass_target)
    command = [
        "closeout",
        "check",
        "--target",
        str(pass_target),
        "--item",
        fixture["item"],
        "--issue",
        fixture["issue"],
        "--pr",
        fixture["pr"],
        "--project",
        "4",
        "--branch",
        fixture["branch"],
        "--owner",
        "owner",
        "--repo",
        "repo",
        "--skip-gate",
        "--issue-payload-file",
        fixture["issue_file"],
        "--pr-payload-file",
        fixture["pr_file"],
        "--project-payload-file",
        fixture["project_file"],
        "--status-checks-file",
        fixture["checks_file"],
        "--branch-protection-file",
        fixture["branch_protection_file"],
        "--ruleset-file",
        fixture["ruleset_file"],
    ]
    _, closeout_payload = run_flow_json(command, expect=0)
    subchecks = {entry.get("id"): entry for entry in closeout_payload.get("gate", {}).get("subchecks", []) if isinstance(entry, dict)}
    if (
        closeout_payload.get("result") != "pass"
        or closeout_payload.get("reconciliation", {}).get("result") != "pass"
        or subchecks.get("pr_merge_backlink", {}).get("merge_commit_sha") != fixture["merge_commit"]
        or subchecks.get("pr_merge_backlink", {}).get("target_branch") != "main"
        or subchecks.get("merge_ready_attempt", {}).get("head_sha") != fixture["head_sha"]
        or closeout_payload.get("issue", {}).get("state") != "CLOSED"
        or closeout_payload.get("project", {}).get("issue_item", {}).get("status") != "Done"
    ):
        raise AssertionError("governance chain closeout pass fixture did not consume PR, issue, Project, target branch, merge commit, review, and merge-ready evidence together")

    auto_lookup_command = command.copy()
    item_index = auto_lookup_command.index("--item")
    del auto_lookup_command[item_index : item_index + 2]
    _, auto_lookup_payload = run_flow_json(auto_lookup_command, expect=0)
    auto_lookup_missing = auto_lookup_payload.get("missing_inputs", [])
    if (
        auto_lookup_payload.get("result") != "pass"
        or not isinstance(auto_lookup_missing, list)
        or any(isinstance(entry, str) and entry.startswith("retained-item lookup:") for entry in auto_lookup_missing)
    ):
        raise AssertionError("closeout --issue did not auto-resolve the canonical retained Work Item")

    _, reconciliation_payload = run_flow_json(
        [
            "reconciliation",
            "audit",
            "--target",
            str(pass_target),
            "--issue",
            fixture["issue"],
            "--pr",
            fixture["pr"],
            "--project",
            "4",
            "--branch",
            fixture["branch"],
            "--owner",
            "owner",
            "--repo",
            "repo",
            "--issue-payload-file",
            fixture["issue_file"],
            "--pr-payload-file",
            fixture["pr_file"],
            "--project-payload-file",
            fixture["project_file"],
        ],
        expect=0,
    )
    if reconciliation_payload.get("result") != "pass" or reconciliation_payload.get("findings"):
        raise AssertionError("governance chain reconciliation pass fixture drifted")

    mismatched_item = "WI-closeout-mismatch"
    (pass_target / ".loom" / "work-items" / f"{mismatched_item}.md").write_text(
        "# WI-closeout-mismatch\n\n"
        "## Static Facts\n\n"
        f"- Item ID: {mismatched_item}\n"
        "- Goal: Fixture wrong retained item for closeout item mismatch.\n"
        "- Scope: Closeout mismatch regression only.\n"
        "- Execution Path: issue #9999 -> branch fixture -> PR #9999.\n"
        "- Workspace Entry: .\n"
        f"- Recovery Entry: .loom/progress/{mismatched_item}.md\n"
        f"- Review Entry: .loom/reviews/{mismatched_item}.json\n"
        "- Validation Entry: closeout mismatch fixture\n"
        "- Closing Condition: closeout must reject issue/item mismatch.\n"
        "\n## Associated Artifacts\n\n"
        f"- `.loom/work-items/{mismatched_item}.md`\n"
        "- `https://github.com/owner/repo/issues/9999`\n",
        encoding="utf-8",
    )
    mismatched_item_command = command.copy()
    mismatched_item_command[mismatched_item_command.index("--item") + 1] = mismatched_item
    _, mismatched_item_payload = run_flow_json(mismatched_item_command, expect=1)
    missing_inputs = mismatched_item_payload.get("missing_inputs", [])
    if (
        mismatched_item_payload.get("result") != "block"
        or not isinstance(missing_inputs, list)
        or not any(
            isinstance(entry, str)
            and entry.startswith("retained-item lookup:")
            and "does not match retained-item lookup for issue" in entry
            for entry in missing_inputs
        )
    ):
        raise AssertionError("closeout --item mismatch did not fail closed through retained-item lookup")

    review_path = pass_target / ".loom" / "reviews" / f"{fixture['item']}.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_payload["authored_at"] = "2026-05-31T00:00:00Z"
    review_path.write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")
    _, post_merge_closeout = run_flow_json(command)
    review_subcheck = next(
        (
            entry
            for entry in post_merge_closeout.get("gate", {}).get("subchecks", [])
            if isinstance(entry, dict) and entry.get("id") == "review_record"
        ),
        {},
    )
    review_diagnostic = review_subcheck.get("post_merge_review_diagnostic", {})
    if (
        post_merge_closeout.get("result") != "block"
        or review_diagnostic.get("result") != "block"
        or review_diagnostic.get("finding", {}).get("kind") != "post_merge_review_bypass"
        or "repair_plan" not in review_diagnostic
    ):
        raise AssertionError("closeout did not block post-merge review bypass with diagnostics and repair plan")
    _, post_merge_reconciliation = run_flow_json(
        [
            "reconciliation",
            "audit",
            "--target",
            str(pass_target),
            "--issue",
            fixture["issue"],
            "--pr",
            fixture["pr"],
            "--project",
            "4",
            "--branch",
            fixture["branch"],
            "--owner",
            "owner",
            "--repo",
            "repo",
            "--issue-payload-file",
            fixture["issue_file"],
            "--pr-payload-file",
            fixture["pr_file"],
            "--project-payload-file",
            fixture["project_file"],
        ]
    )
    if not any(
        isinstance(finding, dict)
        and finding.get("kind") == "post_merge_review_bypass"
        and isinstance(finding.get("repair_plan"), dict)
        for finding in post_merge_reconciliation.get("findings", [])
    ):
        raise AssertionError("reconciliation audit did not expose post-merge review bypass repair plan")

    negative_target = tmp / "governance-chain-pr-merged-alone"
    negative_target.mkdir()
    negative = write_governance_chain_fixture(negative_target, issue_open=True, project_done=False)
    _, negative_closeout = run_flow_json(
        [
            *command[:3],
            str(negative_target),
            *command[4:],
        ],
        expect=1,
    )
    finding_kinds = {finding.get("kind") for finding in negative_closeout.get("reconciliation", {}).get("findings", []) if isinstance(finding, dict)}
    missing_inputs = set(negative_closeout.get("missing_inputs", []))
    if (
        negative_closeout.get("result") != "block"
        or "merged_but_open" not in finding_kinds
        or "project_drift" not in finding_kinds
        or "issue is not closed" not in missing_inputs
        or "issue project status is not Done" not in missing_inputs
    ):
        raise AssertionError("PR merged alone negative fixture must block closeout until issue and Project closeout evidence are present")


def write_terminal_carrier_target(target: Path, item: str) -> None:
    (target / ".loom" / "bootstrap").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "work-items").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "progress").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "status").mkdir(parents=True, exist_ok=True)
    goal = "Fixture for explicit carrier closeout sync."
    scope = "Versioned carrier metadata only; no host mutation."
    execution_path = "fixture -> carrier closeout-sync"
    validation_entry = "carrier closeout-sync fixture"
    closing_condition = "Structured terminal metadata is written only under explicit apply semantics."
    current_stop = "Fixture terminal closeout can be recorded."
    next_step = "None."
    blockers = "None."
    validation_summary = "Fixture validation passed."
    recovery_boundary = "Carrier-only closeout fixture."
    current_lane = "terminal-closeout"
    work_item = target / ".loom" / "work-items" / f"{item}.md"
    progress = target / ".loom" / "progress" / f"{item}.md"
    status = target / ".loom" / "status" / "current.md"
    work_item.write_text(
        f"# {item}\n\n"
        "## Static Facts\n\n"
        f"- Item ID: {item}\n"
        f"- Goal: {goal}\n"
        f"- Scope: {scope}\n"
        f"- Execution Path: {execution_path}\n"
        "- Workspace Entry: .\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Review Entry: .loom/reviews/{item}.json\n"
        f"- Validation Entry: {validation_entry}\n"
        f"- Closing Condition: {closing_condition}\n\n"
        "## Associated Artifacts\n\n"
        f"- `.loom/work-items/{item}.md`\n"
        f"- `.loom/progress/{item}.md`\n"
        "- `.loom/status/current.md`\n",
        encoding="utf-8",
    )
    progress.write_text(
        f"# {item} Progress\n\n"
        "## Dynamic Facts\n\n"
        f"- Item ID: {item}\n"
        "- Current Checkpoint: closed\n"
        f"- Current Stop: {current_stop}\n"
        f"- Next Step: {next_step}\n"
        f"- Blockers: {blockers}\n"
        f"- Latest Validation Summary: {validation_summary}\n"
        f"- Recovery Boundary: {recovery_boundary}\n"
        f"- Current Lane: {current_lane}\n\n"
        "## Execution Ledger\n\n"
        "- Ledger Binding: recovery_entry\n"
        "- Plan Locator: not_applicable\n"
        "- Acceptance Locator: not_applicable\n"
        "- Validation Evidence Locator: not_applicable\n"
        "- Handoff Notes Locator: not_applicable\n"
        "- Evidence Freshness: current\n",
        encoding="utf-8",
    )
    status.write_text(
        "# Current Status\n\n"
        "## Derived Fact Chain View\n\n"
        f"- Item ID: {item}\n"
        f"- Goal: {goal}\n"
        f"- Scope: {scope}\n"
        f"- Execution Path: {execution_path}\n"
        "- Workspace Entry: .\n"
        f"- Recovery Entry: .loom/progress/{item}.md\n"
        f"- Review Entry: .loom/reviews/{item}.json\n"
        f"- Validation Entry: {validation_entry}\n"
        f"- Closing Condition: {closing_condition}\n"
        "- Current Checkpoint: closed\n"
        f"- Current Stop: {current_stop}\n"
        f"- Next Step: {next_step}\n"
        f"- Blockers: {blockers}\n"
        f"- Latest Validation Summary: {validation_summary}\n"
        f"- Recovery Boundary: {recovery_boundary}\n"
        f"- Current Lane: {current_lane}\n\n"
        "## Runtime Evidence\n\n"
        "- Run Entry: not_applicable\n"
        "- Logs Entry: not_applicable\n"
        "- Diagnostics Entry: not_applicable\n"
        "- Verification Entry: not_applicable\n"
        "- Lane Entry: not_applicable\n\n"
        "## Sources\n\n"
        f"- Static Truth: .loom/work-items/{item}.md\n"
        f"- Dynamic Truth: .loom/progress/{item}.md\n"
        "- Locator Truth: .loom/bootstrap/init-result.json\n"
        "- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .\n",
        encoding="utf-8",
    )
    (target / ".loom" / "bootstrap" / "init-result.json").write_text(
        json.dumps(
            {
                "schema_version": "loom-init-output/v1",
                "fact_chain": {
                    "mode": "work-item + recovery-entry + derived status-surface",
                    "read_entry": "python3 .loom/bin/loom_init.py fact-chain --target .",
                    "entry_points": {
                        "current_item_id": item,
                        "work_item": f".loom/work-items/{item}.md",
                        "recovery_entry": f".loom/progress/{item}.md",
                        "status_surface": ".loom/status/current.md",
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_host_complete_active_repair_target(target: Path, item: str) -> None:
    write_terminal_carrier_target(target, item)
    (target / ".loom" / "installed-state.json").write_text(json.dumps(valid_state(target), indent=2) + "\n", encoding="utf-8")
    issue_url = "https://github.com/example/repo/issues/2002"
    pr_url = "https://github.com/example/repo/pull/2003"
    work_item = target / ".loom" / "work-items" / f"{item}.md"
    progress = target / ".loom" / "progress" / f"{item}.md"
    status = target / ".loom" / "status" / "current.md"
    work_item.write_text(
        work_item.read_text(encoding="utf-8") + f"- #2002\n- {issue_url}\n- {pr_url}\n",
        encoding="utf-8",
    )
    progress.write_text(
        progress.read_text(encoding="utf-8").replace("- Current Checkpoint: closed", "- Current Checkpoint: build"),
        encoding="utf-8",
    )
    status.write_text(
        status.read_text(encoding="utf-8").replace("- Current Checkpoint: closed", "- Current Checkpoint: build"),
        encoding="utf-8",
    )


def write_fake_closed_host_gh(bin_dir: Path) -> dict[str, str]:
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake_gh = bin_dir / "gh"
    fake_gh.write_text(
        """#!/usr/bin/env python3
import json
import sys

path = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "api" else ""
if path.endswith("/issues/2002"):
    print(json.dumps({"id": 2002, "node_id": "I_2002", "number": 2002, "state": "closed", "title": "Closed host issue", "body": "", "html_url": "https://github.com/example/repo/issues/2002", "closed_at": "2026-06-13T02:01:00Z", "labels": []}))
    raise SystemExit(0)
if path.endswith("/pulls/2003"):
    print(json.dumps({"number": 2003, "state": "closed", "title": "Merged host PR", "body": "Closes #2002", "html_url": "https://github.com/example/repo/pull/2003", "draft": False, "merged_at": "2026-06-13T02:00:00Z", "merge_commit_sha": "abc123", "head": {"ref": "work/closed-host-carrier", "sha": "def456"}, "base": {"ref": "main"}}))
    raise SystemExit(0)
print(json.dumps({"message": "not found"}), file=sys.stderr)
raise SystemExit(1)
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    current_path = os.environ.get("PATH", "")
    return {"PATH": str(bin_dir) if not current_path else f"{bin_dir}:{current_path}"}


def install_bootstrapped_runtime(target: Path) -> None:
    runtime_target = target / ".loom" / "bin"
    manifest_target = target / ".loom" / "bootstrap" / "manifest.json"
    if runtime_target.exists():
        shutil.rmtree(runtime_target)
    shutil.copytree(REPO_ROOT / ".loom" / "bin", runtime_target)
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / ".loom" / "bootstrap" / "manifest.json", manifest_target)


def write_idle_fact_chain_target(target: Path) -> None:
    install_bootstrapped_runtime(target)
    (target / ".loom" / "status").mkdir(parents=True, exist_ok=True)
    (target / ".loom" / "status" / "current.md").write_text(
        "# Current Status\n\n"
        "## Derived Fact Chain View\n\n"
        "- Item ID: no_active_item\n"
        "- Goal: not_applicable\n"
        "- Scope: not_applicable\n"
        "- Execution Path: not_applicable\n"
        "- Workspace Entry: not_applicable\n"
        "- Recovery Entry: not_applicable\n"
        "- Review Entry: not_applicable\n"
        "- Validation Entry: not_applicable\n"
        "- Closing Condition: not_applicable\n"
        "- Current Checkpoint: not_applicable\n"
        "- Current Stop: not_applicable\n"
        "- Next Step: not_applicable\n"
        "- Blockers: not_applicable\n"
        "- Latest Validation Summary: not_applicable\n"
        "- Recovery Boundary: not_applicable\n"
        "- Current Lane: not_applicable\n\n"
        "## Runtime Evidence\n\n"
        "- Run Entry: not_applicable\n"
        "- Logs Entry: not_applicable\n"
        "- Diagnostics Entry: not_applicable\n"
        "- Verification Entry: not_applicable\n"
        "- Lane Entry: not_applicable\n\n"
        "## Sources\n\n"
        "- Static Truth: not_applicable\n"
        "- Dynamic Truth: not_applicable\n"
        "- Locator Truth: .loom/bootstrap/init-result.json\n"
        "- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .\n",
        encoding="utf-8",
    )
    (target / ".loom" / "bootstrap" / "init-result.json").write_text(
        json.dumps(
            {
                "schema_version": "loom-init-output/v1",
                "fact_chain": {
                    "mode": "idle",
                    "read_entry": "python3 .loom/bin/loom_init.py fact-chain --target .",
                    "entry_points": {
                        "current_item_id": "no_active_item",
                        "work_item": "not_applicable",
                        "recovery_entry": "not_applicable",
                        "status_surface": ".loom/status/current.md",
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def assert_idle_read_surface_contract(tmp: Path) -> None:
    idle_target = tmp / "idle-read-surface"
    idle_target.mkdir()
    write_idle_fact_chain_target(idle_target)
    _, fact_chain = run_json(["fact-chain", "--target", str(idle_target), "--json", "--full-output"], expect=0)
    if (
        fact_chain.get("result") != "pass"
        or fact_chain.get("report", {}).get("repository_execution_state") != "idle"
        or fact_chain.get("report", {}).get("fact_chain", {}).get("entry_points", {}).get("current_item_id") != "no_active_item"
    ):
        raise AssertionError("idle fact-chain did not pass with no_active_item")
    _, status = run_json(["status", "--target", str(idle_target), "--json", "--full-output"], expect=0)
    if (
        status.get("result") != "pass"
        or status.get("item", {}).get("status") != "idle"
        or status.get("item", {}).get("id") != "no_active_item"
        or status.get("item", {}).get("workspace_entry") != "not_applicable"
    ):
        raise AssertionError("idle status did not report a non-blocking idle item")
    governance_surface = status.get("governance_surface")
    if not isinstance(governance_surface, dict):
        raise AssertionError("idle status did not include governance surface")
    if "INIT-0001" in json.dumps(governance_surface, sort_keys=True):
        raise AssertionError("idle governance surface defaulted to INIT-0001")

    locator_drift_target = tmp / "active-locator-drift"
    locator_drift_target.mkdir()
    write_terminal_carrier_target(locator_drift_target, "WI-active")
    init_result = locator_drift_target / ".loom" / "bootstrap" / "init-result.json"
    payload = json.loads(init_result.read_text(encoding="utf-8"))
    payload["fact_chain"]["entry_points"]["current_item_id"] = "WI-other"
    init_result.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    status_code, locator_drift = run_json(["fact-chain", "--target", str(locator_drift_target), "--json", "--full-output"])
    if status_code == 0 or locator_drift.get("result") != "block":
        raise AssertionError("active locator drift did not fail closed")

    stale_status_target = tmp / "active-stale-status"
    stale_status_target.mkdir()
    write_terminal_carrier_target(stale_status_target, "WI-active")
    status_path = stale_status_target / ".loom" / "status" / "current.md"
    status_path.write_text(
        status_path.read_text(encoding="utf-8").replace("- Goal: Fixture for explicit carrier closeout sync.", "- Goal: stale status value."),
        encoding="utf-8",
    )
    status_code, stale_status = run_json(["fact-chain", "--target", str(stale_status_target), "--json", "--full-output"])
    if status_code == 0 or stale_status.get("result") != "block":
        raise AssertionError("active stale status surface did not fail closed")


def assert_carrier_closeout_sync_contract(tmp: Path) -> None:
    target = tmp / "terminal-carrier"
    target.mkdir()
    item = "WI-terminal"
    write_terminal_carrier_target(target, item)
    progress = target / ".loom" / "progress" / f"{item}.md"
    before = progress.read_text(encoding="utf-8")
    _, dry_run = run_json(
        [
            "carrier",
            "closeout-sync",
            "--target",
            str(target),
            "--item",
            item,
            "--issue",
            "1230",
            "--pr",
            "1299",
            "--merge-commit",
            "abc123",
            "--target-branch",
            "main",
            "--closed-at",
            "2026-06-06T00:00:00Z",
            "--evidence-locator",
            "PR #1299 closeout",
            "--json",
        ],
        expect=0,
    )
    if (
        dry_run.get("command") != "carrier closeout-sync"
        or dry_run.get("wrapped_command") != "carrier"
        or dry_run.get("operation") != "closeout-sync"
        or dry_run.get("host_mutations") is not False
        or dry_run.get("host_actions") != []
        or progress.read_text(encoding="utf-8") != before
    ):
        raise AssertionError("carrier closeout-sync dry-run contract drifted")
    _, applied = run_json(
        [
            "carrier",
            "closeout-sync",
            "--target",
            str(target),
            "--item",
            item,
            "--issue",
            "1230",
            "--pr",
            "1299",
            "--merge-commit",
            "abc123",
            "--target-branch",
            "main",
            "--closed-at",
            "2026-06-06T00:00:00Z",
            "--evidence-locator",
            "PR #1299 closeout",
            "--apply",
            "--json",
        ],
        expect=0,
    )
    text = progress.read_text(encoding="utf-8")
    if (
        applied.get("result") != "pass"
        or applied.get("dry_run") is not False
        or applied.get("host_mutations") is not False
        or applied.get("host_actions") != []
        or "## Terminal Closeout Metadata" not in text
        or "- Terminal State: closed_out" not in text
        or "- Issue: 1230" not in text
        or "- PR: 1299" not in text
    ):
        raise AssertionError("carrier closeout-sync apply did not write structured terminal metadata")


def assert_repair_apply_carrier_closeout_contract(tmp: Path) -> None:
    target = tmp / "repair-active-carrier"
    target.mkdir()
    item = "WI-repair"
    write_host_complete_active_repair_target(target, item)
    env = write_fake_closed_host_gh(tmp / "fake-gh-bin")
    fixture_home = tmp / "repair-active-carrier-codex-home"
    fixture_home.mkdir()
    with isolated_codex_workstation(fixture_home):
        register_fixture_codex_plugin()
    env.update({"HOME": str(fixture_home), "CODEX_HOME": str(fixture_home / ".codex")})
    progress = target / ".loom" / "progress" / f"{item}.md"
    status = target / ".loom" / "status" / "current.md"
    init_result = target / ".loom" / "bootstrap" / "init-result.json"
    before = {
        "progress": progress.read_text(encoding="utf-8"),
        "status": status.read_text(encoding="utf-8"),
        "init_result": init_result.read_text(encoding="utf-8"),
    }

    omitted_issue_status, omitted_issue_plan = run_json(
        ["repair", "plan", "--target", str(target), "--json"],
        env_overrides=env,
    )
    if (
        omitted_issue_status == 0
        or omitted_issue_plan.get("result") != "block"
        or "issue selector is required" not in str(omitted_issue_plan.get("fail_closed_reason", ""))
        or progress.read_text(encoding="utf-8") != before["progress"]
        or status.read_text(encoding="utf-8") != before["status"]
        or init_result.read_text(encoding="utf-8") != before["init_result"]
    ):
        raise AssertionError("repair plan did not require an explicit issue selector for active carrier repair")

    _, plan = run_json(
        ["repair", "plan", "--target", str(target), "--issue", "2002", "--json"],
        expect=0,
        env_overrides=env,
    )
    carrier_action = next((action for action in plan.get("actions", []) if isinstance(action, dict) and action.get("kind") == "carrier_closeout_sync"), None)
    update_kinds = {update.get("kind") for update in carrier_action.get("versioned_carrier_updates", [])} if isinstance(carrier_action, dict) else set()
    if (
        plan.get("result") != "pass"
        or plan.get("mutates") is not False
        or carrier_action is None
        or carrier_action.get("host_mutations") is not False
        or carrier_action.get("host_actions") != []
        or not {"terminal-closeout-metadata", "idle-status-surface", "idle-init-result-fact-chain"}.issubset(update_kinds)
        or progress.read_text(encoding="utf-8") != before["progress"]
        or status.read_text(encoding="utf-8") != before["status"]
        or init_result.read_text(encoding="utf-8") != before["init_result"]
    ):
        raise AssertionError("repair plan did not expose non-mutating safe carrier closeout action")

    _, dry_run = run_json(
        ["repair", "apply", "--target", str(target), "--issue", "2002", "--dry-run", "--json"],
        expect=0,
        env_overrides=env,
    )
    if (
        dry_run.get("result") != "pass"
        or dry_run.get("mutates") is not False
        or progress.read_text(encoding="utf-8") != before["progress"]
        or status.read_text(encoding="utf-8") != before["status"]
        or init_result.read_text(encoding="utf-8") != before["init_result"]
    ):
        raise AssertionError("repair apply dry-run mutated carrier files")

    multi_issue = tmp / "repair-multi-issue-carrier"
    multi_issue.mkdir()
    write_host_complete_active_repair_target(multi_issue, item)
    multi_work_item = multi_issue / ".loom" / "work-items" / f"{item}.md"
    multi_work_item.write_text(
        multi_work_item.read_text(encoding="utf-8") + "- GitHub issue #2004\n",
        encoding="utf-8",
    )
    status_code, multi_issue_plan = run_json(
        ["repair", "plan", "--target", str(multi_issue), "--issue", "2002", "--json"],
        env_overrides=env,
    )
    if (
        status_code == 0
        or multi_issue_plan.get("result") != "block"
        or "found #2002, #2004" not in str(multi_issue_plan.get("fail_closed_reason", ""))
    ):
        raise AssertionError("repair plan did not refuse carrier text with multiple GitHub issue locators")

    mixed_action = tmp / "repair-mixed-action-carrier"
    mixed_action.mkdir()
    write_terminal_carrier_target(mixed_action, item)
    mixed_work_item = mixed_action / ".loom" / "work-items" / f"{item}.md"
    mixed_progress = mixed_action / ".loom" / "progress" / f"{item}.md"
    mixed_status = mixed_action / ".loom" / "status" / "current.md"
    mixed_init_result = mixed_action / ".loom" / "bootstrap" / "init-result.json"
    mixed_work_item.write_text(
        mixed_work_item.read_text(encoding="utf-8") + "- #2002\n- https://github.com/example/repo/issues/2002\n- https://github.com/example/repo/pull/2003\n",
        encoding="utf-8",
    )
    mixed_progress.write_text(
        mixed_progress.read_text(encoding="utf-8").replace("- Current Checkpoint: closed", "- Current Checkpoint: build"),
        encoding="utf-8",
    )
    mixed_status.write_text(
        mixed_status.read_text(encoding="utf-8").replace("- Current Checkpoint: closed", "- Current Checkpoint: build"),
        encoding="utf-8",
    )
    mixed_before = {
        "progress": mixed_progress.read_text(encoding="utf-8"),
        "status": mixed_status.read_text(encoding="utf-8"),
        "init_result": mixed_init_result.read_text(encoding="utf-8"),
    }
    mixed_status_code, mixed_apply = run_json(
        ["repair", "apply", "--target", str(mixed_action), "--issue", "2002", "--json"],
        env_overrides=env,
    )
    if (
        mixed_status_code == 0
        or mixed_apply.get("result") != "block"
        or mixed_apply.get("failed_layer") != "installed-surface"
        or mixed_progress.read_text(encoding="utf-8") != mixed_before["progress"]
        or mixed_status.read_text(encoding="utf-8") != mixed_before["status"]
        or mixed_init_result.read_text(encoding="utf-8") != mixed_before["init_result"]
    ):
        raise AssertionError("repair apply did not block mixed installed-surface and carrier repair actions before mutation")

    invalid_output_status, invalid_output_apply = run_json(
        [
            "repair",
            "apply",
            "--target",
            str(target),
            "--issue",
            "2002",
            "--output",
            ".loom/bootstrap/missing-init-result.json",
            "--json",
        ],
        env_overrides=env,
    )
    if (
        invalid_output_status == 0
        or invalid_output_apply.get("result") != "block"
        or progress.read_text(encoding="utf-8") != before["progress"]
        or status.read_text(encoding="utf-8") != before["status"]
        or init_result.read_text(encoding="utf-8") != before["init_result"]
    ):
        raise AssertionError("repair apply with invalid init-result locator did not fail closed without mutation")

    _, applied = run_json(
        ["repair", "apply", "--target", str(target), "--issue", "2002", "--json"],
        expect=0,
        env_overrides=env,
    )
    progress_text = progress.read_text(encoding="utf-8")
    status_text = status.read_text(encoding="utf-8")
    init_payload = json.loads(init_result.read_text(encoding="utf-8"))
    if (
        applied.get("result") != "pass"
        or applied.get("mutates") is not True
        or applied.get("host_mutations") is not False
        or applied.get("host_actions") != []
        or "## Terminal Closeout Metadata" not in progress_text
        or "- Issue: 2002" not in progress_text
        or "- PR: 2003" not in progress_text
        or "- Merge Commit: abc123" not in progress_text
        or "- Item ID: no_active_item" not in status_text
        or init_payload.get("fact_chain", {}).get("mode") != "idle"
        or init_payload.get("fact_chain", {}).get("entry_points", {}).get("current_item_id") != "no_active_item"
    ):
        raise AssertionError("repair apply did not terminalize active carrier and switch repo to idle")
    _, fact_chain = run_json(["fact-chain", "--target", str(target), "--json", "--full-output"], expect=0, env_overrides=env)
    if (
        fact_chain.get("result") != "pass"
        or fact_chain.get("report", {}).get("repository_execution_state") != "idle"
    ):
        raise AssertionError("repair apply did not produce consumable idle fact-chain")

    ambiguous = tmp / "repair-ambiguous-carrier"
    ambiguous.mkdir()
    write_host_complete_active_repair_target(ambiguous, item)
    duplicate_item = ambiguous / ".loom" / "work-items" / "GH-2002-duplicate.md"
    duplicate_progress = ambiguous / ".loom" / "progress" / "GH-2002-duplicate.md"
    duplicate_item.write_text(
        (ambiguous / ".loom" / "work-items" / f"{item}.md").read_text(encoding="utf-8")
        .replace(item, "GH-2002-duplicate")
        .replace(f".loom/progress/{item}.md", ".loom/progress/GH-2002-duplicate.md"),
        encoding="utf-8",
    )
    duplicate_progress.write_text(
        (ambiguous / ".loom" / "progress" / f"{item}.md").read_text(encoding="utf-8").replace(item, "GH-2002-duplicate"),
        encoding="utf-8",
    )
    status_code, ambiguous_plan = run_json(
        ["repair", "plan", "--target", str(ambiguous), "--issue", "2002", "--json"],
        env_overrides=env,
    )
    if (
        status_code == 0
        or ambiguous_plan.get("result") != "block"
        or "ambiguous" not in str(ambiguous_plan.get("fail_closed_reason", ""))
    ):
        raise AssertionError("repair plan did not refuse ambiguous retained item matches")


def append_terminal_closeout_metadata(
    target: Path,
    item: str,
    *,
    issue: int,
    pr: int,
    merge_commit: str,
    target_branch: str = "main",
    closed_at: str = "2026-06-14T00:00:00Z",
    evidence_locator: str = "fixture closeout evidence",
) -> None:
    progress = target / ".loom" / "progress" / f"{item}.md"
    progress.write_text(
        progress.read_text(encoding="utf-8").rstrip()
        + "\n\n"
        "## Terminal Closeout Metadata\n\n"
        "- Terminal State: closed_out\n"
        f"- Issue: {issue}\n"
        f"- PR: {pr}\n"
        f"- Merge Commit: {merge_commit}\n"
        f"- Target Branch: {target_branch}\n"
        f"- Closed At: {closed_at}\n"
        f"- Evidence Locator: {evidence_locator}\n",
        encoding="utf-8",
    )


def assert_closeout_queue_status_contract(tmp: Path) -> None:
    target = tmp / "closeout-queue-status"
    target.mkdir()
    for item in ("WI-9101", "WI-9102", "WI-9103", "WI-9104", "WI-9105"):
        write_terminal_carrier_target(target, item)
    append_terminal_closeout_metadata(
        target,
        "WI-9101",
        issue=9101,
        pr=9201,
        merge_commit="merge9101",
        evidence_locator="fixture auto no-op evidence",
    )
    for item in ("WI-9103",):
        progress = target / ".loom" / "progress" / f"{item}.md"
        status = target / ".loom" / "status" / "current.md"
        progress.write_text(
            progress.read_text(encoding="utf-8").replace("- Current Checkpoint: closed", "- Current Checkpoint: build"),
            encoding="utf-8",
        )
        status.write_text(
            status.read_text(encoding="utf-8").replace("- Current Checkpoint: closed", "- Current Checkpoint: build"),
            encoding="utf-8",
        )
    queue_file = target / "closeout-queue-fixture.json"
    queue_file.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "item_id": "WI-9102",
                        "issue_number": 9102,
                        "pr_number": 9202,
                        "host_completion": {
                            "issue_closed": True,
                            "pr_merged": True,
                            "merge_commit": "merge9102",
                            "target_branch": "main",
                            "closed_at": "2026-06-14T00:02:00Z",
                            "evidence_locator": "fixture light carrier sync",
                        },
                    },
                    {
                        "item_id": "WI-9103",
                        "issue_number": 9103,
                        "pr_number": 9203,
                        "host_completion": {
                            "issue_closed": True,
                            "pr_merged": True,
                            "merge_commit": "merge9103",
                            "target_branch": "main",
                            "closed_at": "2026-06-14T00:03:00Z",
                            "evidence_locator": "fixture batched closeout",
                        },
                    },
                    {
                        "item_id": "WI-9104",
                        "issue_number": 9104,
                        "pr_number": 9204,
                        "host_completion": {
                            "issue_closed": False,
                            "pr_merged": True,
                            "merge_commit": "merge9104",
                            "target_branch": "main",
                            "closed_at": "2026-06-14T00:04:00Z",
                            "evidence_locator": "fixture full closeout",
                        },
                    },
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    before = snapshot_tree(target)
    status_code, payload = run_json(
        ["closeout", "queue", "status", "--target", str(target), "--queue-file", "closeout-queue-fixture.json", "--json"]
    )
    payload = runtime_payload_from_agent_safe_output(payload)
    after = snapshot_tree(target)
    if before != after:
        raise AssertionError("closeout queue status mutated the fixture target")
    if (
        status_code == 0
        or payload.get("command") != "closeout queue status"
        or payload.get("wrapped_command") != "closeout-queue"
        or payload.get("schema_version") != "loom-closeout-queue-status/v1"
        or payload.get("result") != "block"
        or payload.get("mode") != "blocked"
        or payload.get("mutates") is not False
        or payload.get("host_mutations") is not False
        or payload.get("carrier_mutations") is not False
    ):
        raise AssertionError("closeout queue status envelope drifted")
    by_item = {item.get("item_id"): item for item in payload.get("items", []) if isinstance(item, dict)}
    expected_modes = {
        "WI-9101": "auto_no_op",
        "WI-9102": "light_carrier_sync",
        "WI-9103": "batched_closeout",
        "WI-9104": "full_closeout",
        "WI-9105": "blocked",
    }
    actual_modes = {item: by_item.get(item, {}).get("closeout_mode") for item in expected_modes}
    if actual_modes != expected_modes:
        raise AssertionError(f"closeout queue status modes drifted: {actual_modes}")
    if by_item["WI-9101"].get("next_command") is not None:
        raise AssertionError("auto_no_op queue item must not suggest a next command")
    if "loom carrier closeout-sync" not in str(by_item["WI-9102"].get("next_command")):
        raise AssertionError("light_carrier_sync item did not suggest carrier closeout-sync")
    if by_item["WI-9103"].get("next_command") != "loom repair plan --target <repo> --issue 9103 --json":
        raise AssertionError("batched_closeout item did not suggest repair plan")
    if by_item["WI-9104"].get("next_command") != "loom closeout --target <repo> --issue 9104 --pr 9204 --json":
        raise AssertionError("full_closeout item did not suggest closeout check")
    if "host_completion" not in by_item["WI-9105"].get("missing_inputs", []):
        raise AssertionError("blocked item did not report missing host_completion")

    _, light_only = run_json(
        [
            "closeout",
            "queue",
            "status",
            "--target",
            str(target),
            "--queue-file",
            "closeout-queue-fixture.json",
            "--item",
            "WI-9102",
            "--json",
        ],
        expect=0,
    )
    if light_only.get("mode") != "light_carrier_sync" or "loom carrier closeout-sync" not in str(light_only.get("next_command")):
        raise AssertionError("filtered light_carrier_sync queue status did not expose the item next command")

    status_code, missing_input = run_json(
        ["closeout", "queue", "status", "--target", str(target), "--json"],
        expect=1,
    )
    missing_input = runtime_payload_from_agent_safe_output(missing_input)
    if (
        status_code == 0
        or missing_input.get("mode") != "blocked"
        or "queue_input" not in missing_input.get("missing_inputs", [])
        or missing_input.get("mutates") is not False
        or missing_input.get("host_mutations") is not False
        or missing_input.get("carrier_mutations") is not False
    ):
        raise AssertionError("closeout queue status must require an explicit queue input before scanning retained carriers")

    status_code, missing_item = run_json(
        ["closeout", "queue", "status", "--target", str(target), "--item", "WI-does-not-exist", "--json"],
        expect=1,
    )
    missing_item = runtime_payload_from_agent_safe_output(missing_item)
    if status_code == 0 or missing_item.get("mode") != "blocked" or "item not found: WI-does-not-exist" not in missing_item.get("missing_inputs", []):
        raise AssertionError("closeout queue status must block explicit missing item filters")

    status_code, missing_issue = run_json(
        ["closeout", "queue", "status", "--target", str(target), "--issue", "999999", "--json"],
        expect=1,
    )
    missing_issue = runtime_payload_from_agent_safe_output(missing_issue)
    if status_code == 0 or missing_issue.get("mode") != "blocked" or "issue not found: 999999" not in missing_issue.get("missing_inputs", []):
        raise AssertionError("closeout queue status must block explicit missing issue filters")

    status_code, missing_target = run_json(
        ["closeout", "queue", "status", "--target", str(tmp / "missing-target"), "--json"],
        expect=1,
    )
    if (
        status_code == 0
        or missing_target.get("schema_version") != "loom-closeout-queue-status/v1"
        or missing_target.get("mode") != "blocked"
        or missing_target.get("mutates") is not False
        or missing_target.get("host_mutations") is not False
        or missing_target.get("carrier_mutations") is not False
    ):
        raise AssertionError("closeout queue status missing-target envelope drifted")


def assert_closeout_mode_docs_skill_protocol_contract() -> None:
    closeout_gate = (REPO_ROOT / "docs/methodology/harness/closeout-gate.md").read_text(encoding="utf-8")
    shared_reference = (REPO_ROOT / "skills/shared/references/harness/closeout-gate.md").read_text(encoding="utf-8")
    src_reference = (REPO_ROOT / "src/skills/shared/references/harness/closeout-gate.md").read_text(encoding="utf-8")
    if closeout_gate != shared_reference or closeout_gate != src_reference:
        raise AssertionError("closeout gate docs and skill shared references drifted")

    required_gate_snippets = [
        "## 2.1 Closeout Mode Protocol",
        "`inline`",
        "`auto_no_op`",
        "`light`",
        "`batched`",
        "`full`",
        "`light_carrier_sync`",
        "`batched_closeout`",
        "`full_closeout`",
        "### 2.1.1 Closeout Policy Decision",
        "`host_only`",
        "`batched_carrier_pr`",
        "`full_closeout_pr`",
        "`requires_closeout_pr`",
        "`loom-closeout-specific-gate/v1`",
        "`closeout_pr_allowed`",
        "`full_review_required`",
        "`escalation_required`",
        "`blocking_inputs`",
        "`next_action`",
        "## 2.3 Closeout Retained Work Item Binding",
        "canonical Work Item identity",
        "Weak text references",
    ]
    for snippet in required_gate_snippets:
        if snippet not in closeout_gate:
            raise AssertionError(f"closeout mode protocol docs missing `{snippet}`")

    cli_matrix = (REPO_ROOT / "docs/methodology/harness/cli-command-matrix.md").read_text(encoding="utf-8")
    required_matrix_snippets = [
        "| `auto_no_op` | `auto_no_op` |",
        "| `light_carrier_sync` | `light` |",
        "| `batched_closeout` | `batched` |",
        "| `full_closeout` | `full` |",
        "| `blocked` | `full` until repaired |",
    ]
    for snippet in required_matrix_snippets:
        if snippet not in cli_matrix:
            raise AssertionError(f"closeout queue mode mapping docs missing `{snippet}`")

    skill_expectations = {
        "skills/loom-merge-ready/SKILL.md": [
            "loom-closeout-specific-gate/v1",
            "closeout_pr_allowed=true",
            "full_review_required=true",
            "escalation_required=true",
            "light_carrier_sync",
            "batched_closeout",
            "full_closeout",
        ],
        "skills/loom-pre-review/SKILL.md": [
            "closeout-only carrier PR",
            "inline",
            "auto_no_op",
            "light",
            "batched",
            "full",
            "full_review_required",
            "escalation_required",
        ],
        "skills/loom-retire/SKILL.md": [
            "retire 不选择 closeout mode",
            "auto_no_op",
            "light_carrier_sync",
            "batched_closeout",
            "full_closeout",
            "workspace retire",
            "carrier closeout-sync --apply",
        ],
    }
    for relative_path, snippets in skill_expectations.items():
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                raise AssertionError(f"{relative_path} missing closeout mode protocol snippet `{snippet}`")


def assert_hotcp_stale_active_closeout_regression_fixture(tmp: Path) -> None:
    target = tmp / "hotcp-stale-active-root"
    target.mkdir()
    item = "WI-hotcp-root"
    write_host_complete_active_repair_target(target, item)
    env = write_fake_closed_host_gh(tmp / "fake-hotcp-gh-bin")
    fixture_home = tmp / "hotcp-stale-active-codex-home"
    fixture_home.mkdir()
    with isolated_codex_workstation(fixture_home):
        register_fixture_codex_plugin()
    env.update({"HOME": str(fixture_home), "CODEX_HOME": str(fixture_home / ".codex")})

    progress = target / ".loom" / "progress" / f"{item}.md"
    status = target / ".loom" / "status" / "current.md"
    init_result = target / ".loom" / "bootstrap" / "init-result.json"
    before = {
        "progress": progress.read_text(encoding="utf-8"),
        "status": status.read_text(encoding="utf-8"),
        "init_result": init_result.read_text(encoding="utf-8"),
    }

    _, active_fact_chain = run_json(["fact-chain", "--target", str(target), "--json", "--full-output"], expect=0, env_overrides=env)
    active_entry_points = active_fact_chain.get("report", {}).get("fact_chain", {}).get("entry_points", {})
    if (
        active_fact_chain.get("result") != "pass"
        or active_fact_chain.get("report", {}).get("repository_execution_state") == "idle"
        or active_entry_points.get("current_item_id") != item
        or "- Current Checkpoint: build" not in before["progress"]
    ):
        raise AssertionError("HotCP fixture did not start as a stale active carrier pointing at the completed Work Item")

    _, retire = run_json(["workspace", "retire", "--target", str(target), "--item", item, "--json"], expect=0, env_overrides=env)
    if (
        retire.get("result") != "pass"
        or retire.get("retire_scope") != "local_only"
        or retire.get("versioned_carrier_updates") != []
        or progress.read_text(encoding="utf-8") != before["progress"]
        or status.read_text(encoding="utf-8") != before["status"]
        or init_result.read_text(encoding="utf-8") != before["init_result"]
    ):
        raise AssertionError("workspace retire mutated versioned stale active carriers or did not report local_only scope")

    _, post_retire_plan = run_json(
        ["repair", "plan", "--target", str(target), "--issue", "2002", "--json"],
        expect=0,
        env_overrides=env,
    )
    carrier_action = next(
        (action for action in post_retire_plan.get("actions", []) if isinstance(action, dict) and action.get("kind") == "carrier_closeout_sync"),
        None,
    )
    update_kinds = {update.get("kind") for update in carrier_action.get("versioned_carrier_updates", [])} if isinstance(carrier_action, dict) else set()
    if (
        post_retire_plan.get("result") != "pass"
        or carrier_action is None
        or carrier_action.get("host_mutations") is not False
        or carrier_action.get("host_actions") != []
        or not {"terminal-closeout-metadata", "idle-status-surface", "idle-init-result-fact-chain"}.issubset(update_kinds)
    ):
        raise AssertionError("HotCP fixture did not require carrier closeout sync after local workspace retire")

    _, applied = run_json(
        ["repair", "apply", "--target", str(target), "--issue", "2002", "--json"],
        expect=0,
        env_overrides=env,
    )
    _, idle_fact_chain = run_json(["fact-chain", "--target", str(target), "--json", "--full-output"], expect=0, env_overrides=env)
    idle_entry_points = idle_fact_chain.get("report", {}).get("fact_chain", {}).get("entry_points", {})
    if (
        applied.get("result") != "pass"
        or applied.get("mutates") is not True
        or idle_fact_chain.get("report", {}).get("repository_execution_state") != "idle"
        or idle_entry_points.get("current_item_id") != "no_active_item"
        or "## Terminal Closeout Metadata" not in progress.read_text(encoding="utf-8")
    ):
        raise AssertionError("HotCP fixture carrier closeout sync did not terminalize stale active carrier into idle fact-chain")

    retained_target = tmp / "hotcp-retained-historical-name"
    retained_target.mkdir()
    retained_item = "GH-21-LOOM-UPGRADE-BASELINE"
    write_host_complete_active_repair_target(retained_target, retained_item)
    _, retained_plan = run_json(
        ["repair", "plan", "--target", str(retained_target), "--issue", "2002", "--json"],
        expect=0,
        env_overrides=env,
    )
    retained_action = next(
        (action for action in retained_plan.get("actions", []) if isinstance(action, dict) and action.get("kind") == "carrier_closeout_sync"),
        None,
    )
    _, retained_applied = run_json(
        ["repair", "apply", "--target", str(retained_target), "--issue", "2002", "--json"],
        expect=0,
        env_overrides=env,
    )
    _, retained_fact_chain = run_json(["fact-chain", "--target", str(retained_target), "--json", "--full-output"], expect=0, env_overrides=env)
    retained_progress = retained_target / ".loom" / "progress" / f"{retained_item}.md"
    if (
        retained_plan.get("result") != "pass"
        or retained_action is None
        or retained_applied.get("result") != "pass"
        or retained_fact_chain.get("report", {}).get("repository_execution_state") != "idle"
        or "## Terminal Closeout Metadata" not in retained_progress.read_text(encoding="utf-8")
    ):
        raise AssertionError("HotCP retained historical item naming fixture did not consume carrier closeout sync")


def assert_suite_evidence_surface_fixtures(tmp: Path, *, include_carrier: bool = True) -> None:
    evidence_target = tmp / "suite-evidence"
    evidence_suite = evidence_target / ".loom" / "specs" / "WI-evidence"
    evidence_suite.mkdir(parents=True)
    (evidence_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (evidence_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (evidence_suite / "evidence-map.md").write_text(
        "\n".join(
            [
                "# Evidence Map",
                "",
                "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                "| EV-001 | behavior_evidence | .loom/specs/WI-evidence/spec.md | Scenario S1 | current HEAD | present | merge-ready evidence | refresh behavior evidence |",
                "| EV-002 | test_evidence | .loom/specs/WI-evidence/plan.md | AC-1 | current HEAD | present | merge-ready evidence | rerun tests |",
                "| EV-003 | fresh_verification_input | python3 tools/check_cli_contract.py | EV-001 EV-002 | current HEAD | present | merge-ready evidence | rerun validation |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_evidence_inspect = run_suite_evidence_inspect_fixture(evidence_target, "WI-evidence")
    evidence_payload = suite_evidence_inspect.get("payload", {})
    if (
        evidence_payload.get("evidence_map", {}).get("status") != "present"
        or evidence_payload.get("evidence_map", {}).get("row_count") != 3
        or evidence_payload.get("evidence_map_locator") != ".loom/specs/WI-evidence/evidence-map.md"
        or len(evidence_payload.get("rows", [])) != 3
        or "docs/methodology/templates/evidence-map.md" not in evidence_payload.get("consumed_contracts", [])
    ):
        raise AssertionError("suite evidence inspect payload drifted")
    suite_evidence_validate = run_suite_evidence_validate_fixture(evidence_target, "WI-evidence")
    if (
        suite_evidence_validate.get("result") != "pass"
        or suite_evidence_validate.get("failed_layer") is not None
        or suite_evidence_validate.get("fail_closed_reason") is not None
        or suite_evidence_validate.get("blocking_gaps")
        or suite_evidence_validate.get("payload", {}).get("required_evidence_types")
        != ["behavior_evidence", "test_evidence", "fresh_verification_input"]
        or suite_evidence_validate.get("payload", {}).get("freshness_context", {}).get("validation_summary_status") != "missing"
    ):
        raise AssertionError("suite evidence validate pass payload drifted")

    evidence_missing_target = tmp / "suite-evidence-missing"
    evidence_missing_target.mkdir()
    suite_evidence_missing = run_suite_evidence_validate_fixture(evidence_missing_target, "WI-evidence-missing", expect=1)
    if (
        suite_evidence_missing.get("result") != "block"
        or suite_evidence_missing.get("failed_layer") != "evidence_map"
        or suite_evidence_missing.get("fail_closed_reason") != "missing_evidence_map"
        or "evidence_map_locator" not in suite_evidence_missing.get("missing_inputs", [])
        or not any(gap.get("failure_kind") == "missing_evidence_map" for gap in suite_evidence_missing.get("blocking_gaps", []))
    ):
        raise AssertionError("suite evidence validate missing map payload drifted")
    assert_suite_failure_taxonomy(
        suite_evidence_missing,
        "missing_evidence_map",
        result="block",
        layer="evidence_map",
    )

    evidence_stale_target = tmp / "suite-evidence-stale"
    evidence_stale_suite = evidence_stale_target / ".loom" / "specs" / "WI-evidence-stale"
    evidence_stale_suite.mkdir(parents=True)
    (evidence_stale_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (evidence_stale_suite / "evidence-map.md").write_text(
        "\n".join(
            [
                "# Evidence Map",
                "",
                "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                "| EV-001 | behavior_evidence | .loom/specs/WI-evidence-stale/spec.md | Scenario S1 | previous HEAD | stale | merge-ready evidence | refresh behavior evidence |",
                "| EV-002 | test_evidence | .loom/specs/WI-evidence-stale/plan.md | AC-1 | current HEAD | present | merge-ready evidence | rerun tests |",
                "| EV-003 | fresh_verification_input | python3 tools/check_cli_contract.py | EV-001 EV-002 | current HEAD | present | merge-ready evidence | rerun validation |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_evidence_stale = run_suite_evidence_validate_fixture(evidence_stale_target, "WI-evidence-stale", expect=1)
    if (
        suite_evidence_stale.get("result") != "block"
        or suite_evidence_stale.get("fail_closed_reason") != "stale_evidence"
        or not any(gap.get("failure_kind") == "stale_evidence" for gap in suite_evidence_stale.get("blocking_gaps", []))
        or not any(
            gap.get("failure_kind") == "missing_fresh_verification_evidence"
            for gap in suite_evidence_stale.get("blocking_gaps", [])
        )
    ):
        raise AssertionError("suite evidence validate stale payload drifted")
    assert_suite_failure_taxonomy(
        suite_evidence_stale,
        "stale_evidence",
        result="block",
        layer="evidence_map",
    )
    assert_suite_failure_taxonomy(
        suite_evidence_stale,
        "missing_fresh_verification_evidence",
        result="block",
        layer="evidence_map",
    )

    evidence_head_target = tmp / "suite-evidence-head-drift"
    evidence_head_suite = evidence_head_target / ".loom" / "specs" / "WI-evidence-head"
    evidence_head_suite.mkdir(parents=True)
    current_head = init_git_fixture(evidence_head_target)
    stale_head = "0" * 40 if current_head != "0" * 40 else "1" * 40
    (evidence_head_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (evidence_head_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (evidence_head_suite / "evidence-map.md").write_text(
        "\n".join(
            [
                "# Evidence Map",
                "",
                "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                f"| EV-001 | behavior_evidence | .loom/specs/WI-evidence-head/spec.md | Scenario S1 | head_sha={stale_head} | present | merge-ready evidence | refresh behavior evidence |",
                f"| EV-002 | test_evidence | .loom/specs/WI-evidence-head/plan.md | AC-1 | head_sha={current_head} | present | merge-ready evidence | rerun tests |",
                f"| EV-003 | fresh_verification_input | python3 tools/check_cli_contract.py | EV-001 EV-002 | head_sha={current_head} | present | merge-ready evidence | rerun validation |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_evidence_head_drift = run_suite_evidence_validate_fixture(evidence_head_target, "WI-evidence-head", expect=1)
    if (
        suite_evidence_head_drift.get("result") != "block"
        or suite_evidence_head_drift.get("fail_closed_reason") != "head_or_pr_drift"
        or not any(gap.get("failure_kind") == "head_or_pr_drift" for gap in suite_evidence_head_drift.get("blocking_gaps", []))
    ):
        raise AssertionError("suite evidence validate head binding drift payload drifted")
    assert_suite_failure_taxonomy(
        suite_evidence_head_drift,
        "head_or_pr_drift",
        result="block",
        layer="evidence_map",
    )

    evidence_pr_head_target = tmp / "suite-evidence-pr-head-drift"
    evidence_pr_head_suite = evidence_pr_head_target / ".loom" / "specs" / "WI-evidence-pr-head"
    evidence_pr_head_suite.mkdir(parents=True)
    current_pr_head = init_git_fixture(evidence_pr_head_target)
    stale_pr_head = "f" * 40 if current_pr_head != "f" * 40 else "e" * 40
    (evidence_pr_head_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (evidence_pr_head_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (evidence_pr_head_suite / "evidence-map.md").write_text(
        "\n".join(
            [
                "# Evidence Map",
                "",
                "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                f"| EV-001 | behavior_evidence | .loom/specs/WI-evidence-pr-head/spec.md | Scenario S1 | pr_head={stale_pr_head} | present | merge-ready evidence | refresh behavior evidence |",
                f"| EV-002 | test_evidence | .loom/specs/WI-evidence-pr-head/plan.md | AC-1 | pr_head={current_pr_head} | present | merge-ready evidence | rerun tests |",
                f"| EV-003 | fresh_verification_input | python3 tools/check_cli_contract.py | EV-001 EV-002 | pr_head={current_pr_head} | present | merge-ready evidence | rerun validation |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_evidence_pr_head_drift = run_suite_evidence_validate_fixture(evidence_pr_head_target, "WI-evidence-pr-head", expect=1)
    if (
        suite_evidence_pr_head_drift.get("result") != "block"
        or suite_evidence_pr_head_drift.get("fail_closed_reason") != "head_or_pr_drift"
        or not any(gap.get("failure_kind") == "head_or_pr_drift" for gap in suite_evidence_pr_head_drift.get("blocking_gaps", []))
    ):
        raise AssertionError("suite evidence validate PR head binding drift payload drifted")

    evidence_validation_target = tmp / "suite-evidence-validation-drift"
    evidence_validation_suite = evidence_validation_target / ".loom" / "specs" / "WI-evidence-validation"
    progress_dir = evidence_validation_target / ".loom" / "progress"
    evidence_validation_suite.mkdir(parents=True)
    progress_dir.mkdir(parents=True)
    validation_summary = "Passed: fixture validation"
    validation_digest = hashlib.sha256(validation_summary.encode("utf-8")).hexdigest()
    stale_validation_digest = "a" * 64 if validation_digest != "a" * 64 else "b" * 64
    (progress_dir / "WI-evidence-validation.md").write_text(
        f"# WI-evidence-validation Progress\n\n- Latest Validation Summary: {validation_summary}\n",
        encoding="utf-8",
    )
    (evidence_validation_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (evidence_validation_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (evidence_validation_suite / "evidence-map.md").write_text(
        "\n".join(
            [
                "# Evidence Map",
                "",
                "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                f"| EV-001 | behavior_evidence | .loom/specs/WI-evidence-validation/spec.md | Scenario S1 | validation_summary_sha256={stale_validation_digest} | present | merge-ready evidence | refresh behavior evidence |",
                f"| EV-002 | test_evidence | .loom/specs/WI-evidence-validation/plan.md | AC-1 | validation_summary_sha256={validation_digest} | present | merge-ready evidence | rerun tests |",
                f"| EV-003 | fresh_verification_input | python3 tools/check_cli_contract.py | EV-001 EV-002 | validation_summary_sha256={validation_digest} | present | merge-ready evidence | rerun validation |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_evidence_validation_drift = run_suite_evidence_validate_fixture(evidence_validation_target, "WI-evidence-validation", expect=1)
    if (
        suite_evidence_validation_drift.get("result") != "block"
        or suite_evidence_validation_drift.get("fail_closed_reason") != "stale_evidence"
        or suite_evidence_validation_drift.get("payload", {}).get("freshness_context", {}).get("validation_summary_sha256") != validation_digest
        or not any(gap.get("failure_kind") == "stale_evidence" for gap in suite_evidence_validation_drift.get("blocking_gaps", []))
    ):
        raise AssertionError("suite evidence validate validation summary drift payload drifted")

    evidence_missing_source_target = tmp / "suite-evidence-missing-source"
    evidence_missing_source_suite = evidence_missing_source_target / ".loom" / "specs" / "WI-evidence-missing-source"
    evidence_missing_source_suite.mkdir(parents=True)
    (evidence_missing_source_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (evidence_missing_source_suite / "evidence-map.md").write_text(
        "\n".join(
            [
                "# Evidence Map",
                "",
                "| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                "| EV-001 | behavior_evidence | tools/missing-source.py | Scenario S1 | current HEAD | present | merge-ready evidence | refresh behavior evidence |",
                "| EV-002 | test_evidence | .loom/specs/WI-evidence-missing-source/plan.md | AC-1 | current HEAD | present | merge-ready evidence | rerun tests |",
                "| EV-003 | fresh_verification_input | python3 tools/check_cli_contract.py | EV-001 EV-002 | current HEAD | present | merge-ready evidence | rerun validation |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_evidence_missing_source = run_suite_evidence_validate_fixture(evidence_missing_source_target, "WI-evidence-missing-source", expect=1)
    if (
        suite_evidence_missing_source.get("result") != "block"
        or suite_evidence_missing_source.get("fail_closed_reason") != "missing_source_locator"
        or not any(gap.get("failure_kind") == "missing_source_locator" for gap in suite_evidence_missing_source.get("blocking_gaps", []))
    ):
        raise AssertionError("suite evidence validate missing source locator payload drifted")

    if include_carrier:
        assert_suite_carrier_aggregate_fixtures(tmp)

    evidence_scaffold_target = tmp / "suite-evidence-scaffold"
    evidence_scaffold_target.mkdir()
    suite_evidence_scaffold = run_suite_evidence_scaffold_fixture(evidence_scaffold_target, "WI-evidence-scaffold")
    evidence_scaffold_payload = suite_evidence_scaffold.get("payload", {})
    evidence_scaffold_writes = {entry["artifact"]: entry for entry in evidence_scaffold_payload.get("planned_writes", [])}
    if (
        suite_evidence_scaffold.get("result") != "pass"
        or evidence_scaffold_payload.get("evidence_map_locator") != ".loom/specs/WI-evidence-scaffold/evidence-map.md"
        or evidence_scaffold_payload.get("apply_required") is not True
        or evidence_scaffold_payload.get("apply") is not False
        or evidence_scaffold_payload.get("created_locators") != []
        or evidence_scaffold_writes.get("evidence-map.md", {}).get("status") != "would_create"
        or evidence_scaffold_writes.get("evidence-map.md", {}).get("source_template")
        != "docs/methodology/templates/scaffold/evidence-map.md"
        or evidence_scaffold_writes.get("evidence-map.md", {}).get("initial_freshness") != "missing"
        or evidence_scaffold_payload.get("overwrite_policy", {}).get("mode") != "preserve_existing"
        or evidence_scaffold_payload.get("overwrite_policy", {}).get("allows_overwrite") is not False
        or evidence_scaffold_payload.get("initial_freshness_policy") != "scaffold never marks evidence present"
    ):
        raise AssertionError("suite evidence scaffold dry-run payload drifted")
    if (evidence_scaffold_target / ".loom").exists():
        raise AssertionError("suite evidence scaffold dry-run created a .loom directory")

    evidence_apply_target = tmp / "suite-evidence-scaffold-apply"
    evidence_apply_target.mkdir()
    suite_evidence_scaffold_apply = run_suite_evidence_scaffold_apply_fixture(evidence_apply_target, "WI-evidence-apply")
    evidence_apply_payload = suite_evidence_scaffold_apply.get("payload", {})
    created_evidence_map = evidence_apply_target / ".loom" / "specs" / "WI-evidence-apply" / "evidence-map.md"
    created_text = created_evidence_map.read_text(encoding="utf-8")
    if (
        suite_evidence_scaffold_apply.get("result") != "pass"
        or suite_evidence_scaffold_apply.get("mutates") is not True
        or evidence_apply_payload.get("apply") is not True
        or evidence_apply_payload.get("apply_required") is not False
        or evidence_apply_payload.get("created_locators") != [".loom/specs/WI-evidence-apply/evidence-map.md"]
        or not created_evidence_map.is_file()
        or "| EV-001 | behavior_evidence |  | .loom/specs/WI-evidence-apply/spec.md scenario / acceptance locator | WI-evidence-apply / scope / head / PR | missing |" not in created_text
        or " | present | " in created_text
    ):
        raise AssertionError("suite evidence scaffold --apply create payload drifted")
    suite_evidence_scaffold_validate = run_suite_evidence_validate_fixture(evidence_apply_target, "WI-evidence-apply", expect=1)
    if (
        suite_evidence_scaffold_validate.get("result") != "block"
        or not any(gap.get("failure_kind") == "missing_evidence_map" for gap in suite_evidence_scaffold_validate.get("blocking_gaps", []))
        or not any(gap.get("failure_kind") == "missing_fresh_verification_evidence" for gap in suite_evidence_scaffold_validate.get("blocking_gaps", []))
    ):
        raise AssertionError("suite evidence scaffold output must not validate as present evidence")
    suite_evidence_scaffold_again = run_suite_evidence_scaffold_apply_fixture(evidence_apply_target, "WI-evidence-apply")
    if (
        suite_evidence_scaffold_again.get("mutates") is not False
        or suite_evidence_scaffold_again.get("payload", {}).get("created_locators") != []
        or suite_evidence_scaffold_again.get("payload", {}).get("overwrite_policy", {}).get("existing_files")
        != [".loom/specs/WI-evidence-apply/evidence-map.md"]
    ):
        raise AssertionError("suite evidence scaffold repeat apply preservation drifted")

    evidence_existing_target = tmp / "suite-evidence-scaffold-existing"
    evidence_existing_suite = evidence_existing_target / ".loom" / "specs" / "WI-evidence-existing"
    evidence_existing_suite.mkdir(parents=True)
    (evidence_existing_suite / "evidence-map.md").write_text("# Existing evidence map\n", encoding="utf-8")
    suite_evidence_existing = run_suite_evidence_scaffold_apply_fixture(evidence_existing_target, "WI-evidence-existing")
    if (
        suite_evidence_existing.get("mutates") is not False
        or suite_evidence_existing.get("payload", {}).get("created_locators") != []
        or (evidence_existing_suite / "evidence-map.md").read_text(encoding="utf-8") != "# Existing evidence map\n"
    ):
        raise AssertionError("suite evidence scaffold existing-file preservation drifted")

    evidence_symlink_target = tmp / "suite-evidence-scaffold-symlink"
    evidence_symlink_suite = evidence_symlink_target / ".loom" / "specs" / "WI-evidence-link"
    evidence_symlink_suite.mkdir(parents=True)
    (evidence_symlink_suite / "evidence-map.md").symlink_to("../../../outside-evidence.md")
    suite_evidence_symlink = run_suite_evidence_scaffold_apply_fixture(
        evidence_symlink_target,
        "WI-evidence-link",
        expect=1,
    )
    if (
        suite_evidence_symlink.get("result") != "block"
        or suite_evidence_symlink.get("fail_closed_reason") != "missing_scaffold_inputs"
        or suite_evidence_symlink.get("mutates") is not False
        or suite_evidence_symlink.get("payload", {}).get("created_locators") != []
        or (evidence_symlink_target / "outside-evidence.md").exists()
    ):
        raise AssertionError("suite evidence scaffold symlink path did not fail closed")

    _, suite_evidence_traversal = run_json(
        [
            "suite",
            "evidence",
            "scaffold",
            "--target",
            str(evidence_scaffold_target),
            "--item",
            "../escape",
            "--json",
            "--apply",
        ],
        expect=1,
    )
    if (
        suite_evidence_traversal.get("result") != "block"
        or suite_evidence_traversal.get("fail_closed_reason") != "invalid_suite_item"
        or suite_evidence_traversal.get("mutates") is not False
        or suite_evidence_traversal.get("payload", {}).get("created_locators") != []
    ):
        raise AssertionError("suite evidence scaffold traversal item did not fail closed")


def assert_suite_carrier_aggregate_fixtures(tmp: Path) -> None:
    carrier_target = tmp / "suite-carrier"
    carrier_suite = carrier_target / ".loom" / "specs" / "WI-carrier"
    carrier_work_items = carrier_target / ".loom" / "work-items"
    carrier_tasks = carrier_target / ".loom" / "tasks"
    carrier_suite.mkdir(parents=True)
    carrier_work_items.mkdir(parents=True)
    carrier_tasks.mkdir(parents=True)
    (carrier_work_items / "WI-carrier.md").write_text("# WI-carrier\n", encoding="utf-8")
    (carrier_suite / "execution-breakdown.md").write_text("# Execution Breakdown\n", encoding="utf-8")
    (carrier_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (carrier_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (carrier_tasks / "WI-carrier.md").write_text("- [ ] Unit C4\n", encoding="utf-8")
    (carrier_suite / "task-carrier.md").write_text(
        "\n".join(
            [
                "# Task Carrier",
                "",
                "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| github_issue | https://github.com/owner/repo/issues/1131 | issue open | pending | primary | .loom/work-items/WI-carrier.md | .loom/specs/WI-carrier/execution-breakdown.md#unit-c1 | .loom/specs/WI-carrier/spec.md#scenario-s1 | .loom/specs/WI-carrier/plan.md#phase-1 | .loom/specs/WI-carrier/plan.md#validation | authored fixture | recheck before merge-ready |",
                "| github_project_item | project://loom/item/1 | In Progress | in_progress | mirror | .loom/work-items/WI-carrier.md | .loom/specs/WI-carrier/execution-breakdown.md#unit-c2 | .loom/specs/WI-carrier/spec.md#scenario-s2 | .loom/specs/WI-carrier/plan.md#phase-2 | .loom/specs/WI-carrier/plan.md#validation | project readback fixture | mirror only |",
                "| checklist_item | .loom/specs/WI-carrier/task-carrier.md | checked | done | evidence_locator | .loom/work-items/WI-carrier.md | .loom/specs/WI-carrier/execution-breakdown.md#unit-c3 | .loom/specs/WI-carrier/spec.md#scenario-s3 | .loom/specs/WI-carrier/plan.md#phase-3 | .loom/specs/WI-carrier/plan.md#validation | checklist fixture | carrier done is tracking only |",
                "| repo_tasks_md | .loom/tasks/WI-carrier.md | task row open | blocked | primary | .loom/work-items/WI-carrier.md | .loom/specs/WI-carrier/execution-breakdown.md#unit-c4 | .loom/specs/WI-carrier/spec.md#scenario-s4 | .loom/specs/WI-carrier/plan.md#phase-4 | .loom/specs/WI-carrier/plan.md#validation | tasks.md fixture | blocker locator in Work Item recovery |",
                "| external_tracker | https://tracker.example/T-1 | parked | deferred | primary | .loom/work-items/WI-carrier.md | .loom/specs/WI-carrier/execution-breakdown.md#unit-c5 | .loom/specs/WI-carrier/spec.md#scenario-s5 | .loom/specs/WI-carrier/plan.md#phase-5 | .loom/specs/WI-carrier/plan.md#validation | external fixture | activation condition: upstream ready |",
                "| not_applicable | not_applicable:unit-c6 | no carrier needed | not_applicable | not_applicable | .loom/work-items/WI-carrier.md | .loom/specs/WI-carrier/execution-breakdown.md#unit-c6 | not_applicable | .loom/specs/WI-carrier/plan.md#phase-6 | not_applicable | authored rationale | minimal path rationale recheck |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_carrier_inspect = run_suite_carrier_inspect_fixture(carrier_target, "WI-carrier")
    carrier_payload = suite_carrier_inspect.get("payload", {})
    carrier_rows = carrier_payload.get("rows", [])
    if (
        carrier_payload.get("task_carrier", {}).get("status") != "present"
        or carrier_payload.get("task_carrier", {}).get("row_count") != 6
        or carrier_payload.get("task_carrier_locator") != ".loom/specs/WI-carrier/task-carrier.md"
        or set(carrier_payload.get("recognized_carrier_types", [])) != {
            "github_issue",
            "github_project_item",
            "checklist_item",
            "repo_tasks_md",
            "external_tracker",
            "not_applicable",
        }
        or {row.get("normalized_status") for row in carrier_rows}
        != {"pending", "in_progress", "done", "blocked", "deferred", "not_applicable"}
        or carrier_payload.get("truth_boundary", {}).get("carrier_done_satisfies_work_item_done") is not False
        or "docs/methodology/harness/task-carrier-contract.md" not in carrier_payload.get("consumed_contracts", [])
    ):
        raise AssertionError("suite carrier inspect payload drifted")
    suite_carrier_validate = run_suite_carrier_validate_fixture(carrier_target, "WI-carrier")
    if (
        suite_carrier_validate.get("result") != "pass"
        or suite_carrier_validate.get("failed_layer") is not None
        or suite_carrier_validate.get("fail_closed_reason") is not None
        or suite_carrier_validate.get("blocking_gaps")
    ):
        raise AssertionError("suite carrier validate pass payload drifted")

    carrier_missing_target = tmp / "suite-carrier-missing"
    carrier_missing_target.mkdir()
    suite_carrier_missing = run_suite_carrier_validate_fixture(carrier_missing_target, "WI-carrier-missing", expect=1)
    if (
        suite_carrier_missing.get("result") != "block"
        or suite_carrier_missing.get("failed_layer") != "task_carrier"
        or suite_carrier_missing.get("fail_closed_reason") != "missing_task_carrier_locator"
        or "task_carrier_locator" not in suite_carrier_missing.get("missing_inputs", [])
        or not any(gap.get("failure_kind") == "missing_task_carrier_locator" for gap in suite_carrier_missing.get("blocking_gaps", []))
    ):
        raise AssertionError("suite carrier validate missing locator payload drifted")
    assert_suite_failure_taxonomy(
        suite_carrier_missing,
        "missing_task_carrier_locator",
        result="block",
        layer="task_carrier",
    )

    carrier_invalid_target = tmp / "suite-carrier-invalid"
    carrier_invalid_suite = carrier_invalid_target / ".loom" / "specs" / "WI-carrier-invalid"
    carrier_invalid_suite.mkdir(parents=True)
    (carrier_invalid_suite / "task-carrier.md").write_text(
        "\n".join(
            [
                "# Task Carrier",
                "",
                "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| unknown_host | host://carrier/1 | open | ready | owner | .loom/work-items/WI-carrier-invalid.md | .loom/specs/WI-carrier-invalid/execution-breakdown.md#unit | .loom/specs/WI-carrier-invalid/spec.md#scenario | .loom/specs/WI-carrier-invalid/plan.md#phase | .loom/specs/WI-carrier-invalid/plan.md#validation | invalid fixture | recheck before merge-ready |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_carrier_invalid = run_suite_carrier_validate_fixture(carrier_invalid_target, "WI-carrier-invalid", expect=1)
    if (
        suite_carrier_invalid.get("result") != "block"
        or suite_carrier_invalid.get("fail_closed_reason") != "missing_task_carrier_locator"
        or not any(gap.get("failure_kind") == "missing_task_carrier_locator" for gap in suite_carrier_invalid.get("blocking_gaps", []))
    ):
        raise AssertionError("suite carrier validate invalid type/status/relationship payload drifted")

    carrier_primary_target = tmp / "suite-carrier-primary-conflict"
    carrier_primary_suite = carrier_primary_target / ".loom" / "specs" / "WI-carrier-primary"
    carrier_primary_suite.mkdir(parents=True)
    (carrier_primary_suite / "task-carrier.md").write_text(
        "\n".join(
            [
                "# Task Carrier",
                "",
                "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| github_issue | https://github.com/owner/repo/issues/1 | open | in_progress | primary | .loom/work-items/WI-carrier-primary.md | .loom/specs/WI-carrier-primary/execution-breakdown.md#unit | .loom/specs/WI-carrier-primary/spec.md#scenario | .loom/specs/WI-carrier-primary/plan.md#phase | .loom/specs/WI-carrier-primary/plan.md#validation | primary fixture | recheck before merge-ready |",
                "| external_tracker | https://tracker.example/T-3 | open | in_progress | primary | .loom/work-items/WI-carrier-primary.md | .loom/specs/WI-carrier-primary/execution-breakdown.md#unit | .loom/specs/WI-carrier-primary/spec.md#scenario | .loom/specs/WI-carrier-primary/plan.md#phase | .loom/specs/WI-carrier-primary/plan.md#validation | primary fixture | recheck before merge-ready |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_carrier_primary = run_suite_carrier_validate_fixture(carrier_primary_target, "WI-carrier-primary", expect=1)
    if (
        suite_carrier_primary.get("result") != "block"
        or suite_carrier_primary.get("fail_closed_reason") != "carrier_truth_conflict"
        or not any(gap.get("failure_kind") == "carrier_truth_conflict" for gap in suite_carrier_primary.get("blocking_gaps", []))
    ):
        raise AssertionError("suite carrier validate primary conflict payload drifted")

    carrier_conflict_target = tmp / "suite-carrier-conflict"
    carrier_conflict_suite = carrier_conflict_target / ".loom" / "specs" / "WI-carrier-conflict"
    carrier_conflict_suite.mkdir(parents=True)
    (carrier_conflict_suite / "task-carrier.md").write_text(
        "\n".join(
            [
                "# Task Carrier",
                "",
                "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| github_project_item | project://loom/item/2 | Project Done means completed | done | mirror | .loom/work-items/WI-carrier-conflict.md | .loom/specs/WI-carrier-conflict/execution-breakdown.md#unit | .loom/specs/WI-carrier-conflict/spec.md#scenario | .loom/specs/WI-carrier-conflict/plan.md#phase | .loom/specs/WI-carrier-conflict/plan.md#validation | project readback fixture | mirror only |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_carrier_conflict = run_suite_carrier_validate_fixture(carrier_conflict_target, "WI-carrier-conflict", expect=1)
    if (
        suite_carrier_conflict.get("result") != "block"
        or suite_carrier_conflict.get("fail_closed_reason") != "carrier_truth_conflict"
        or not any(gap.get("failure_kind") == "carrier_truth_conflict" for gap in suite_carrier_conflict.get("blocking_gaps", []))
    ):
        raise AssertionError("suite carrier validate truth conflict payload drifted")

    carrier_host_conflict_target = tmp / "suite-carrier-host-conflict"
    carrier_host_conflict_suite = carrier_host_conflict_target / ".loom" / "specs" / "WI-carrier-host-conflict"
    carrier_host_conflict_suite.mkdir(parents=True)
    (carrier_host_conflict_target / ".loom" / "progress").mkdir(parents=True)
    (carrier_host_conflict_target / ".loom" / "progress" / "WI-carrier-host-conflict.md").write_text(
        "\n".join(
            [
                "# WI-carrier-host-conflict Progress",
                "",
                "## Dynamic Facts",
                "",
                "- Item ID: WI-carrier-host-conflict",
                "- Current Checkpoint: build",
                "- Current Stop: fixture",
                "- Next Step: fixture",
                "- Blockers: None",
                "- Latest Validation Summary: fixture",
                "- Recovery Boundary: fixture",
                "- Current Lane: fixture",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (carrier_host_conflict_suite / "task-carrier.md").write_text(
        "\n".join(
            [
                "# Task Carrier",
                "",
                "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| github_project_item | project://loom/item/9 | Project Done / issue open | done | mirror | .loom/work-items/WI-carrier-host-conflict.md | .loom/specs/WI-carrier-host-conflict/execution-breakdown.md#unit-project | .loom/specs/WI-carrier-host-conflict/spec.md#scenario-project | .loom/specs/WI-carrier-host-conflict/plan.md#phase-project | .loom/specs/WI-carrier-host-conflict/plan.md#validation | project fixture | mirror only |",
                "| checklist_item | .loom/specs/WI-carrier-host-conflict/task-carrier.md | checklist checked / evidence missing | done | evidence_locator | .loom/work-items/WI-carrier-host-conflict.md | .loom/specs/WI-carrier-host-conflict/execution-breakdown.md#unit-checklist | .loom/specs/WI-carrier-host-conflict/spec.md#scenario-checklist | .loom/specs/WI-carrier-host-conflict/plan.md#phase-checklist | .loom/specs/WI-carrier-host-conflict/plan.md#validation | checklist fixture | checklist mirror only |",
                "| github_issue | https://github.com/owner/repo/pull/99 | PR merged / issue open | done | mirror | .loom/work-items/WI-carrier-host-conflict.md | .loom/specs/WI-carrier-host-conflict/execution-breakdown.md#unit-pr | .loom/specs/WI-carrier-host-conflict/spec.md#scenario-pr | .loom/specs/WI-carrier-host-conflict/plan.md#phase-pr | .loom/specs/WI-carrier-host-conflict/plan.md#validation | pr fixture | PR merged is merge locator only |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_carrier_host_conflict = run_suite_carrier_validate_fixture(carrier_host_conflict_target, "WI-carrier-host-conflict", expect=1)
    host_conflict_payload = suite_carrier_host_conflict.get("payload", {})
    host_conflict_ids = {entry.get("id") for entry in host_conflict_payload.get("host_signal_conflicts", [])}
    if (
        suite_carrier_host_conflict.get("result") != "block"
        or suite_carrier_host_conflict.get("fail_closed_reason") != "carrier_truth_conflict"
        or not {"project-done-issue-open", "checklist-checked-evidence-missing", "pr-merged-issue-open"}.issubset(host_conflict_ids)
        or "project_done" not in host_conflict_payload.get("recognized_truth_signals", [])
        or not any(gap.get("failure_kind") == "carrier_truth_conflict" for gap in suite_carrier_host_conflict.get("blocking_gaps", []))
    ):
        raise AssertionError("suite carrier validate host signal conflict payload drifted")

    carrier_deferred_target = tmp / "suite-carrier-deferred"
    carrier_deferred_suite = carrier_deferred_target / ".loom" / "specs" / "WI-carrier-deferred"
    carrier_deferred_suite.mkdir(parents=True)
    (carrier_deferred_suite / "task-carrier.md").write_text(
        "\n".join(
            [
                "# Task Carrier",
                "",
                "| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| external_tracker | https://tracker.example/T-2 | completed | deferred | primary | .loom/work-items/WI-carrier-deferred.md | .loom/specs/WI-carrier-deferred/execution-breakdown.md#unit | .loom/specs/WI-carrier-deferred/spec.md#scenario | .loom/specs/WI-carrier-deferred/plan.md#phase | .loom/specs/WI-carrier-deferred/plan.md#validation | external fixture | activation condition missing |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    suite_carrier_deferred = run_suite_carrier_validate_fixture(carrier_deferred_target, "WI-carrier-deferred", expect=1)
    if (
        suite_carrier_deferred.get("result") != "block"
        or suite_carrier_deferred.get("fail_closed_reason") != "deferred_as_completed"
        or not any(gap.get("failure_kind") == "deferred_as_completed" for gap in suite_carrier_deferred.get("blocking_gaps", []))
    ):
        raise AssertionError("suite carrier validate deferred-completed payload drifted")


def assert_governance_closeout_help_contract() -> None:
    _, help_payload = run_json(["help", "--json"], expect=0)
    matrix = {entry["command"]: entry for entry in help_payload["commands"]}
    for command in ("reconcile", "gate closeout", "closeout", "closeout queue status"):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for governance closeout")
    if matrix["carrier closeout-sync"]["status"] != "implemented" or matrix["carrier closeout-sync"]["domain"] != "harness":
        raise AssertionError("carrier closeout-sync must be declared as a harness command for #1231")


def assert_active_closeout_contract(active_item: str) -> None:
    status, closeout_payload = run_json(["closeout", "--target", str(REPO_ROOT), "--json"])
    closeout_payload = runtime_payload_from_agent_safe_output(closeout_payload)
    if closeout_payload["command"] != "closeout" or closeout_payload.get("schema_version") != "loom-scenario-control/v1":
        raise AssertionError("closeout did not wrap the closeout check runtime")
    if closeout_payload.get("result") not in {"pass", "block", "fallback"}:
        raise AssertionError("closeout did not emit a structured pass/block/fallback result")
    assert_suite_gate_consumption(closeout_payload, expected_surface="closeout")
    if status == 0:
        assert_closeout_blocks_missing_suite_evidence(active_item, closeout_payload)


def assert_idle_root_self_governance_direct_contract() -> None:
    init_result = json.loads((REPO_ROOT / ".loom" / "bootstrap" / "init-result.json").read_text(encoding="utf-8"))
    fact_chain = init_result.get("fact_chain") if isinstance(init_result, dict) else {}
    entry_points = fact_chain.get("entry_points") if isinstance(fact_chain, dict) else {}
    if not isinstance(entry_points, dict) or entry_points.get("current_item_id") != "no_active_item":
        return

    runtime_status, runtime_parity = run_flow_json(["runtime-parity", "validate", "--target", str(REPO_ROOT)], expect=0)
    if runtime_status != 0 or runtime_parity.get("result") != "pass":
        raise AssertionError("idle runtime-parity direct check did not pass")
    work_item_check = next((check for check in runtime_parity.get("checks", []) if check.get("name") == "work_item"), None)
    if not isinstance(work_item_check, dict) or work_item_check.get("result") != "pass":
        raise AssertionError("idle runtime-parity did not treat no_active_item as a pass")

    _, adopt_verify = run_flow_json(["adopt", "verify", "--target", str(REPO_ROOT), "--item", "no_active_item"], expect=0)
    if adopt_verify.get("result") != "pass" or not isinstance(adopt_verify.get("idle_repository"), dict):
        raise AssertionError("idle adopt verify direct check did not pass")
    roundtrip = adopt_verify.get("producer_consumer_roundtrip")
    if not isinstance(roundtrip, dict) or roundtrip.get("bypass_check", {}).get("result") != "pass":
        raise AssertionError("idle adopt verify did not preserve producer/consumer roundtrip evidence")


def run_governance_closeout_contract() -> None:
    assert_governance_closeout_help_contract()
    assert_closeout_wrapper_argument_contract()
    assert_repo_local_closeout_runtime_argument_contract()
    assert_closeout_mode_docs_skill_protocol_contract()
    active_item = active_work_item_id()
    assert_active_closeout_contract(active_item)
    assert_idle_root_self_governance_direct_contract()
    assert_reconciliation_suite_taxonomy_contract()
    assert_issue_dependency_machine_block_contract()
    with tempfile.TemporaryDirectory(prefix="loom-governance-closeout-") as raw_tmp:
        tmp = Path(raw_tmp)
        assert_docs_contract_suite_not_applicable_gate_contract(tmp)
        assert_governance_chain_closeout_fixture(tmp)
        assert_carrier_closeout_sync_contract(tmp)
        assert_repair_apply_carrier_closeout_contract(tmp)
        assert_closeout_queue_status_contract(tmp)
        assert_hotcp_stale_active_closeout_regression_fixture(tmp)
        assert_idle_read_surface_contract(tmp)

    print("governance closeout surface checks passed")


def run_adoption_host_metadata_surface() -> None:
    with tempfile.TemporaryDirectory(prefix="loom-adoption-host-metadata-") as raw_tmp:
        tmp = Path(raw_tmp)
        assert_codex_payload_readback_contract(tmp)
        assert_version_freshness_contract(tmp)
        assert_metadata_only_adoption_contract(tmp)
    assert_install_upgrade_host_boundary_docs()

    print("adoption host metadata surface checks passed")


def run_merge_wrapper_surface() -> None:
    assert_merge_wrapper_pr_argument_contract()
    assert_merge_closeout_run_wrapper_contract()
    with tempfile.TemporaryDirectory(prefix="loom-merge-wrapper-") as raw_tmp:
        assert_controlled_merge_triggered_check_rollup_contract(Path(raw_tmp))
    print("merge wrapper surface checks passed")


def run_ship_wrapper_surface() -> None:
    assert_ship_dry_run_wrapper_contract()
    assert_ship_infers_pr_bindings_contract()
    assert_ship_pr_readback_uses_api_contract()
    assert_ship_apply_wrapper_contract()
    assert_ship_closeout_policy_admission_contract()
    assert_ship_docs_entry_contract()
    print("ship wrapper surface checks passed")


def run_closeout_wrapper_surface() -> None:
    assert_closeout_wrapper_argument_contract()
    print("closeout wrapper surface checks passed")


def run_work_item_audit_surface() -> None:
    assert_workspace_audit_wrapper_contract()
    _, payload = run_json(["workspace", "audit", "--target", str(REPO_ROOT), "--json"], expect=None)
    if payload.get("schema_version") != "loom-active-carrier-audit/v1":
        raise AssertionError("workspace audit must emit loom-active-carrier-audit/v1")
    if payload.get("command") != "workspace audit":
        raise AssertionError("workspace audit must preserve the public command label")
    if payload.get("wrapped_command") != "work-item-audit":
        raise AssertionError("workspace audit must expose the wrapped runtime command")
    if payload.get("result") not in {"pass", "block"}:
        raise AssertionError("workspace audit result drifted")
    if not isinstance(payload.get("findings"), list):
        raise AssertionError("workspace audit must expose findings")
    if "shadow_freshness" not in payload:
        raise AssertionError("workspace audit must expose shadow freshness")
    print("work item audit surface checks passed")


def run_release_readback_surface() -> None:
    _, help_payload = run_json(["help", "--json"], expect=0)
    matrix = {entry["command"]: entry for entry in help_payload["commands"]}
    for command in ("release readback", "release resume"):
        if matrix[command]["status"] != "implemented" or matrix[command]["domain"] != "delivery":
            raise AssertionError(f"{command} must be declared as an implemented delivery command")

    expected = {
        "unpublished-release-required": ("release", "readback", "unpublished"),
        "v0.14.2-manual-resume-published": ("release", "resume", "published"),
        "partial-release-missing-github-release": ("release", "readback", "partial_published"),
        "no-release-docs-only": ("release", "resume", "no_release"),
    }
    for fixture, (domain, operation, classification) in expected.items():
        args = [
            domain,
            operation,
            "--target",
            str(REPO_ROOT),
            "--fixture-file",
            str(RELEASE_READBACK_FIXTURES),
            "--fixture",
            fixture,
            "--json",
        ]
        if classification == "no_release":
            args.extend(["--release-judgment", "no_release"])
        _, payload = run_json(args, expect=0)
        if payload.get("schema") != "loom-release-readback/v1" or payload.get("mutates") is not False:
            raise AssertionError(f"{fixture} release readback did not emit the non-mutating schema contract")
        observed = payload.get("classification", {}).get("classification")
        if observed != classification:
            raise AssertionError(f"{fixture} classified as {observed}, expected {classification}")
        target = payload.get("release_target", {})
        if not all(target.get(field) for field in ("version", "tag", "npm_version", "npm_package")):
            raise AssertionError(f"{fixture} did not expose target version/tag/npm package readback context")
        readbacks = payload.get("readbacks", {})
        for surface in ("tag", "github_release", "npm_package", "workflow_run"):
            if surface not in readbacks:
                raise AssertionError(f"{fixture} missing {surface} readback")
        if operation == "resume" and not isinstance(payload.get("resume_contract"), dict):
            raise AssertionError(f"{fixture} release resume did not expose the non-mutating resume contract")

    print("release readback surface checks passed")


def run_pr_metadata_surface() -> None:
    assert_pr_metadata_wrapper_argument_contract()
    with tempfile.TemporaryDirectory(prefix="loom-pr-metadata-") as raw_tmp:
        tmp = Path(raw_tmp)
        assert_governance_metadata_render_readback_fixture(tmp)
        assert_governance_intensity_metadata_preflight_fixture(tmp)

    print("pr metadata surface checks passed")


def run_controlled_merge_surface() -> None:
    with tempfile.TemporaryDirectory(prefix="loom-controlled-merge-") as raw_tmp:
        tmp = Path(raw_tmp)
        assert_controlled_merge_ruleset_trigger_fixture(tmp)

    print("controlled merge surface checks passed")


def run_aggregate_cli_contract() -> None:
    assert_merge_wrapper_pr_argument_contract()
    assert_closeout_wrapper_argument_contract()
    assert_workspace_audit_wrapper_contract()
    assert_pr_metadata_wrapper_argument_contract()
    loom_flow = load_loom_flow_module()
    _, help_payload = run_json(["help", "--json"], expect=0)
    matrix = {entry["command"]: entry for entry in help_payload["commands"]}
    commands = set(matrix)
    missing = sorted(REQUIRED_COMMANDS - commands)
    if missing:
        raise AssertionError(f"help matrix missing commands: {missing}")
    for command in ("detect", "doctor", "repair plan", "repair apply"):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for #888")
    for command in (
        "workspace locate",
        "issue inspect",
        "project status",
        "pr gate",
        "merge check",
        "ship",
        "reconcile",
        "host list",
        "host doctor",
        "host register",
        "skills list",
        "skills check",
        "skills release-check",
    ):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for #893/#894/#895")
    for command in (
        "init",
        "adopt",
        "route",
        "status",
        "fact-chain",
        "profile status",
        "profile upgrade-plan",
        "profile upgrade",
        "checkpoint admission",
        "checkpoint build",
        "checkpoint merge",
        "gate pre-review",
        "gate spec-review",
        "gate review",
        "gate pr",
        "gate merge",
        "gate freeze check",
        "gate freeze write",
        "gate closeout",
    ):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for #890/#891")
    for command in ("release readback", "release resume"):
        if matrix[command]["status"] != "implemented" or matrix[command]["domain"] != "delivery":
            raise AssertionError(f"{command} must be implemented for #1601")
    for command in ("gate freeze check", "gate freeze write"):
        if matrix[command]["domain"] != "gate" or matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be declared as an implemented gate command for #1508")

    freeze_status, freeze_payload = run_json(["gate", "freeze", "check", "--target", str(REPO_ROOT), "--json"], expect=None)
    freeze_payload = runtime_payload_from_agent_safe_output(freeze_payload)
    if freeze_status == 0 and freeze_payload.get("result") != "pass":
        raise AssertionError("gate freeze check returned success without a pass result")
    if freeze_payload.get("schema_version") != "loom-gate-freeze/v1":
        raise AssertionError("gate freeze check must emit loom-gate-freeze/v1")
    if freeze_payload.get("mutates") is not False:
        raise AssertionError("gate freeze check must remain read-only")
    if "input_bindings" not in freeze_payload or "readiness" not in freeze_payload:
        raise AssertionError("gate freeze check must expose input_bindings and readiness diagnostics")
    classifier_payload = loom_flow.failure_classifier_payload(
        [
            {"input": "carrier_refresh", "failure_kind": "carrier_refresh_stale"},
            {"input": "shadow_freshness", "failure_kind": "shadow_source_hash_drift"},
            {"input": "review_binding", "failure_kind": "head_binding_drift"},
            {"input": "suite_evidence_validation", "failure_kind": "stale_evidence"},
            {"input": "suite_carrier_validation", "failure_kind": "carrier_truth_conflict"},
            {"input": "command_surface", "failure_kind": "unsupported_command_surface"},
            {"input": "release_requiredness", "failure_kind": "release_evidence_phase_error"},
            {"input": "host_readback", "failure_kind": "host_api_unreadable"},
            {"input": "host_readback", "failure_kind": "permission"},
            {"input": "hosted_admission", "failure_kind": "hosted_snapshot_mismatch"},
        ]
    )
    required_classifiers = {
        "carrier_refresh_needed",
        "shadow_stale",
        "review_stale",
        "suite_evidence_contract_invalid",
        "task_carrier_contract_invalid",
        "unsupported_command_surface",
        "release_evidence_phase_error",
        "host_api_unreadable",
        "permission",
        "hosted_snapshot_mismatch",
    }
    supported_classifiers = set(classifier_payload.get("supported_classifiers", []))
    if required_classifiers - supported_classifiers:
        raise AssertionError(f"failure classifier supported vocabulary missing {sorted(required_classifiers - supported_classifiers)}")
    observed_classifiers = {finding.get("classifier") for finding in classifier_payload.get("findings", [])}
    if required_classifiers - observed_classifiers:
        raise AssertionError(f"failure classifier mapping missing {sorted(required_classifiers - observed_classifiers)}")
    if not all(finding.get("next_action") for finding in classifier_payload.get("findings", [])):
        raise AssertionError("failure classifier findings must include next_action")
    if "CODEX_EXPORT_GH_TOKEN=1" not in loom_flow.FAILURE_CLASSIFIER_NEXT_ACTIONS["host_api_unreadable"]:
        raise AssertionError("host_api_unreadable next_action must expose the single-command token bridge")
    if "CODEX_EXPORT_GH_TOKEN=1" not in loom_flow.FAILURE_CLASSIFIER_NEXT_ACTIONS["permission"]:
        raise AssertionError("permission next_action must expose the single-command token bridge")
    if loom_flow.host_api_failure_classifier(["HTTP 403 Forbidden: API rate limit exceeded"]) != "host_api_unreadable":
        raise AssertionError("GitHub API rate-limit diagnostics must classify as host_api_unreadable")
    if loom_flow.host_api_failure_classifier(["HTTP 403 Forbidden: Resource not accessible by integration"]) != "permission":
        raise AssertionError("GitHub permission diagnostics must classify as permission")
    rate_limit_diagnostic = loom_flow.host_api_diagnostic_message(
        "gh api repos/example/repo",
        ["HTTP 403 Forbidden: API rate limit exceeded"],
    )
    if "classifier=host_api_unreadable" not in rate_limit_diagnostic or "CODEX_EXPORT_GH_TOKEN=1" not in rate_limit_diagnostic:
        raise AssertionError("host API diagnostics must include classifier and token bridge next_action")
    subject = freeze_payload.get("snapshot_subject")
    input_bindings = freeze_payload.get("input_bindings", {})
    pr_metadata = input_bindings.get("pr_metadata") if isinstance(input_bindings, dict) else None
    pr_body_pin = input_bindings.get("pr_body_pin") if isinstance(input_bindings, dict) else None
    carrier_refresh = input_bindings.get("carrier_refresh") if isinstance(input_bindings, dict) else None
    shadow_freshness = input_bindings.get("shadow_freshness") if isinstance(input_bindings, dict) else None
    if pr_body_pin is not None and (not isinstance(pr_body_pin, dict) or pr_body_pin.get("schema_version") != "loom-gate-freeze-pr-body-pin/v1"):
        raise AssertionError("gate freeze check must expose a PR body pin binding")
    if carrier_refresh is not None and (not isinstance(carrier_refresh, dict) or carrier_refresh.get("schema_version") != "loom-gate-freeze-carrier-refresh/v1"):
        raise AssertionError("gate freeze check must expose a carrier refresh binding")
    if shadow_freshness is not None and (not isinstance(shadow_freshness, dict) or shadow_freshness.get("schema_version") != "loom-gate-freeze-shadow-freshness/v1"):
        raise AssertionError("gate freeze check must expose a shadow freshness binding")
    if isinstance(subject, dict) and isinstance(pr_metadata, dict) and pr_metadata.get("result") == "pass":
        for contract in pr_metadata.get("metadata_contracts", []):
            if not isinstance(contract, dict):
                continue
            envelope = contract.get("envelope")
            fields = envelope.get("fields") if isinstance(envelope, dict) else None
            if not isinstance(fields, dict):
                continue
            expected_bindings = {
                "loom_work_item": subject.get("item_id"),
                "head_sha": subject.get("head_sha"),
                "branch": subject.get("branch"),
            }
            for field_name, expected_value in expected_bindings.items():
                if isinstance(expected_value, str) and expected_value and fields.get(field_name) != expected_value:
                    raise AssertionError("gate freeze must not pass stale PR metadata that is not bound to the snapshot subject")

    runtime_pr_dir = REPO_ROOT / ".loom" / "runtime" / "pr"
    runtime_pr_dir.mkdir(parents=True, exist_ok=True)
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    rendered_pr_body = runtime_pr_dir / "cli-contract-rendered.md"
    readback_pr_body = runtime_pr_dir / "cli-contract-readback.md"
    readback_pr_body_drift = runtime_pr_dir / "cli-contract-readback-drift.md"
    carrier_drift_body = runtime_pr_dir / "cli-contract-carrier-drift.md"
    try:
        freeze_item = active_work_item_id()
        branch = "work/cli-contract-fixture"
        body = governance_metadata_body(item=freeze_item, branch=branch, head_sha=head_sha)
        rendered_pr_body.write_text(body, encoding="utf-8")
        readback_pr_body.write_text(body, encoding="utf-8")
        _, body_pin_payload = run_json(
            [
                "gate",
                "freeze",
                "check",
                "--target",
                str(REPO_ROOT),
                "--item",
                freeze_item,
                "--head-sha",
                head_sha,
                "--branch",
                branch,
                "--body-file",
                ".loom/runtime/pr/cli-contract-rendered.md",
                "--compare-body-file",
                ".loom/runtime/pr/cli-contract-readback.md",
                "--json",
            ],
            expect=None,
        )
        body_pin_payload = runtime_payload_from_agent_safe_output(body_pin_payload)
        body_pin = body_pin_payload.get("input_bindings", {}).get("pr_body_pin")
        if not isinstance(body_pin, dict) or body_pin.get("result") != "pass":
            raise AssertionError(f"gate freeze PR body pin positive fixture did not pass: {body_pin}")
        if body_pin.get("rendered_body_sha256") != body_pin.get("readback_body_sha256"):
            raise AssertionError("gate freeze PR body pin did not record matching rendered/readback body hashes")
        if not body_pin.get("metadata_block_fingerprints"):
            raise AssertionError("gate freeze PR body pin did not retain metadata block fingerprints")

        readback_pr_body_drift.write_text(body + "\nOperator note added after edit.\n", encoding="utf-8")
        _, body_hash_drift_payload = run_json(
            [
                "gate",
                "freeze",
                "check",
                "--target",
                str(REPO_ROOT),
                "--item",
                freeze_item,
                "--head-sha",
                head_sha,
                "--branch",
                branch,
                "--body-file",
                ".loom/runtime/pr/cli-contract-rendered.md",
                "--compare-body-file",
                ".loom/runtime/pr/cli-contract-readback-drift.md",
                "--json",
            ],
            expect=1,
        )
        body_hash_drift_payload = runtime_payload_from_agent_safe_output(body_hash_drift_payload)
        body_hash_drift = body_hash_drift_payload.get("input_bindings", {}).get("pr_body_pin")
        if not isinstance(body_hash_drift, dict) or body_hash_drift.get("result") != "block":
            raise AssertionError("gate freeze PR body pin must block rendered/readback body hash drift")
        if "rendered PR body hash does not match GitHub readback PR body hash" not in body_hash_drift.get("missing_inputs", []):
            raise AssertionError("gate freeze PR body pin did not report rendered/readback body hash drift")
        if not any(
            blocking.get("input") == "pr_body_pin"
            and "gh pr edit --body-file" in str(blocking.get("next_action"))
            for blocking in body_hash_drift_payload.get("readiness", {}).get("blocking_inputs", [])
            if isinstance(blocking, dict)
        ):
            raise AssertionError("gate freeze PR body pin block must include the gh pr edit/readback next action")
        body_hash_drift_classifiers = {
            finding.get("classifier")
            for finding in body_hash_drift_payload.get("failure_classifier", {}).get("findings", [])
            if isinstance(finding, dict)
        }
        if "pr_metadata_drift" not in body_hash_drift_classifiers:
            raise AssertionError("gate freeze PR body hash drift must classify as pr_metadata_drift")
        if not any(
            finding.get("classifier") == "pr_metadata_drift"
            and "regenerate or update the PR body machine carrier" in str(finding.get("next_action"))
            for finding in body_hash_drift_payload.get("failure_classifier", {}).get("findings", [])
            if isinstance(finding, dict)
        ):
            raise AssertionError("gate freeze PR body hash drift must expose the classifier-specific next_action")

        carrier_drift_body.write_text(
            governance_metadata_body(item=freeze_item, branch=branch, head_sha="2" * 40),
            encoding="utf-8",
        )
        _, carrier_drift_payload = run_json(
            [
                "gate",
                "freeze",
                "check",
                "--target",
                str(REPO_ROOT),
                "--item",
                freeze_item,
                "--head-sha",
                head_sha,
                "--branch",
                branch,
                "--body-file",
                ".loom/runtime/pr/cli-contract-rendered.md",
                "--compare-body-file",
                ".loom/runtime/pr/cli-contract-carrier-drift.md",
                "--json",
            ],
            expect=1,
        )
        carrier_drift_payload = runtime_payload_from_agent_safe_output(carrier_drift_payload)
        carrier_drift = carrier_drift_payload.get("input_bindings", {}).get("pr_body_pin")
        if not isinstance(carrier_drift, dict) or carrier_drift.get("result") != "block":
            raise AssertionError("gate freeze PR body pin must block machine carrier binding drift")
        if not any("PR metadata preflight:" in str(message) for message in carrier_drift.get("missing_inputs", [])):
            raise AssertionError("gate freeze PR body pin must preserve preflight carrier mismatch messages")
        carrier_drift_classifiers = {
            finding.get("classifier")
            for finding in carrier_drift_payload.get("failure_classifier", {}).get("findings", [])
            if isinstance(finding, dict)
        }
        if "pr_metadata_drift" not in carrier_drift_classifiers:
            raise AssertionError("gate freeze carrier binding drift must classify as pr_metadata_drift")
        if not any(
            finding.get("classifier") == "pr_metadata_drift"
            and "regenerate or update the PR body machine carrier" in str(finding.get("next_action"))
            for finding in carrier_drift_payload.get("failure_classifier", {}).get("findings", [])
            if isinstance(finding, dict)
        ):
            raise AssertionError("gate freeze carrier binding drift must expose the classifier-specific next_action")
    finally:
        for path in (rendered_pr_body, readback_pr_body, readback_pr_body_drift, carrier_drift_body):
            if path.exists():
                path.unlink()
    assert_gate_freeze_carrier_shadow_bindings_contract()
    outside_freeze_path = REPO_ROOT / ".loom" / "runtime" / "gate-freeze-outside" / "probe.json"
    if outside_freeze_path.exists():
        outside_freeze_path.unlink()
    _, invalid_write = run_json(
        [
            "gate",
            "freeze",
            "write",
            "--target",
            str(REPO_ROOT),
            "--write-path",
            ".loom/runtime/gate-freeze-outside/probe.json",
            "--json",
        ],
        expect=1,
    )
    invalid_write = runtime_payload_from_agent_safe_output(invalid_write)
    if outside_freeze_path.exists():
        outside_freeze_path.unlink()
        raise AssertionError("gate freeze write must not write outside .loom/runtime/gate-freeze/")
    if invalid_write.get("write_artifact", {}).get("result") != "block":
        raise AssertionError("gate freeze write must block invalid write paths outside .loom/runtime/gate-freeze/")
    for command in (
        "install",
        "upgrade-plan",
        "upgrade",
        "rollback",
        "verify",
    ):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for #910-#914")
    for command in (
        "story",
        "spec",
        "plan",
        "build",
        "pre-review",
        "closeout",
        "closeout queue status",
        "handoff",
        "retire",
    ):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for #924-#928")
    if matrix["suite inspect"]["status"] != "implemented" or matrix["suite inspect"]["domain"] != "suite":
        raise AssertionError("suite inspect must be declared in help matrix for #1111")
    if matrix["suite scaffold"]["status"] != "implemented" or matrix["suite scaffold"]["domain"] != "suite":
        raise AssertionError("suite scaffold must be declared in help matrix for #1114")
    if matrix["suite validate"]["status"] != "implemented" or matrix["suite validate"]["domain"] != "suite":
        raise AssertionError("suite validate must be declared in help matrix for #1120")
    if matrix["suite evidence inspect"]["status"] != "implemented" or matrix["suite evidence inspect"]["domain"] != "suite":
        raise AssertionError("suite evidence inspect must be declared in help matrix for #1127")
    if matrix["suite evidence scaffold"]["status"] != "implemented" or matrix["suite evidence scaffold"]["domain"] != "suite":
        raise AssertionError("suite evidence scaffold must be declared in help matrix for #1129")
    if matrix["suite evidence validate"]["status"] != "implemented" or matrix["suite evidence validate"]["domain"] != "suite":
        raise AssertionError("suite evidence validate must be declared in help matrix for #1127")
    if matrix["suite carrier inspect"]["status"] != "implemented" or matrix["suite carrier inspect"]["domain"] != "suite":
        raise AssertionError("suite carrier inspect must be declared in help matrix for #1131")
    if matrix["suite carrier validate"]["status"] != "implemented" or matrix["suite carrier validate"]["domain"] != "suite":
        raise AssertionError("suite carrier validate must be declared in help matrix for #1131")
    assert_governance_closeout_help_contract()

    _, version_payload = run_json(["version", "--json"], expect=0)
    if version_payload["result"] != "pass" or not version_payload["versions"]["repo_version"]:
        raise AssertionError("version output did not include repo version context")

    closeout_body = Path(".loom/runtime/check-cli-contract/closeout-body.md")
    closeout_body.parent.mkdir(parents=True, exist_ok=True)
    try:
        _, render_payload = run_json(
            [
                "pr",
                "metadata-render",
                "--surface",
                "closeout",
                "--item",
                "WI-1541",
                "--branch",
                "work/1541-pr-metadata-update-v2",
                "--head-sha",
                "1" * 40,
                "--output-file",
                str(closeout_body),
                "--json",
            ],
            expect=0,
        )
        if render_payload.get("result") != "pass" or render_payload.get("effective_carrier_surface") != "closeout":
            raise AssertionError("pr metadata-render must support closeout surface and emit closeout carrier surface")

        _, readback_payload = run_json(
            [
                "pr",
                "metadata-readback",
                "--surface",
                "closeout",
                "--body-file",
                str(closeout_body),
                "--json",
            ],
            expect=0,
        )
        if readback_payload.get("schema_version") != "loom-pr-metadata-readback/v1" or readback_payload.get("result") != "pass":
            raise AssertionError("pr metadata-readback must emit a passing loom-pr-metadata-readback/v1 payload for readable body artifacts")

        _, body_file_preflight = run_json(
            [
                "pr",
                "metadata-preflight",
                "--surface",
                "closeout",
                "--body-file",
                str(closeout_body),
                "--json",
            ],
            expect=0,
        )
        if (
            body_file_preflight.get("schema_version") != "loom-pr-metadata-preflight/v1"
            or body_file_preflight.get("result") != "pass"
            or "body_artifact" not in body_file_preflight
        ):
            raise AssertionError("pr metadata-preflight must support closeout surface body-file artifact validation without requiring a live PR")
    finally:
        closeout_body.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="loom-cli-contract-") as raw_tmp:
        tmp = Path(raw_tmp)
        suite_unknown_target = tmp / "suite-unknown"
        suite_unknown_target.mkdir()
        suite_unknown = run_suite_inspect_fixture(suite_unknown_target, "WI-1109")
        if (
            suite_unknown.get("payload", {}).get("suite_path") != "unknown"
            or suite_unknown.get("payload", {}).get("artifact_inventory") != []
            or "suite_path_decision" not in suite_unknown.get("payload", {}).get("missing_inputs", [])
        ):
            raise AssertionError("suite inspect unknown-state payload drifted")
        suite_unknown_validate = run_suite_validate_fixture(suite_unknown_target, "WI-1109", expect=1)
        if (
            suite_unknown_validate.get("result") != "block"
            or suite_unknown_validate.get("failed_layer") != "suite"
            or suite_unknown_validate.get("fail_closed_reason") != "missing_suite_path_decision"
            or "suite_path_decision" not in suite_unknown_validate.get("missing_inputs", [])
            or not suite_unknown_validate.get("blocking_gaps")
            or suite_unknown_validate.get("advisory_gaps")
        ):
            raise AssertionError("suite validate unknown-state block payload drifted")
        assert_suite_failure_taxonomy(
            suite_unknown_validate,
            "missing_suite_path_decision",
            result="block",
            layer="suite",
        )

        suite_conflict_target = tmp / "suite-conflict"
        suite_conflict = suite_conflict_target / ".loom" / "specs" / "WI-conflict"
        suite_conflict.mkdir(parents=True)
        (suite_conflict / "suite-index.md").write_text("# Suite\n\n- Suite path: full\n", encoding="utf-8")
        (suite_conflict / "spec.md").write_text("# Spec\n\n- Suite path: minimal\n", encoding="utf-8")
        (suite_conflict / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_conflict_validate = run_suite_validate_fixture(suite_conflict_target, "WI-conflict", expect=1)
        conflict_missing = suite_conflict_validate.get("payload", {}).get("missing_inputs", [])
        if (
            suite_conflict_validate.get("result") != "block"
            or suite_conflict_validate.get("fail_closed_reason") != "missing_suite_path_decision"
            or "suite_path_decision" not in conflict_missing
            or not any(str(entry).startswith("conflicting_suite_path_decision:") for entry in conflict_missing)
            or not any(
                gap.get("failure_kind") == "missing_suite_path_decision"
                and gap.get("source_locator") == ".loom/specs/WI-conflict/spec.md"
                for gap in suite_conflict_validate.get("blocking_gaps", [])
            )
        ):
            raise AssertionError("suite validate conflicting path decision payload drifted")

        minimal_target = tmp / "suite-minimal"
        write_minimal_suite(minimal_target, "WI-minimal")
        assert_minimal_suite_happy_path_fixture(minimal_target, "WI-minimal")

        minimal_invalid_target = tmp / "suite-minimal-invalid-rationale"
        minimal_invalid_suite = minimal_invalid_target / ".loom" / "specs" / "WI-minimal-invalid"
        minimal_invalid_suite.mkdir(parents=True)
        (minimal_invalid_suite / "spec.md").write_text(
            "# Spec\n\n- Suite path: minimal\n\n- Full suite artifacts not_applicable.\n",
            encoding="utf-8",
        )
        (minimal_invalid_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_minimal_invalid = run_suite_validate_fixture(minimal_invalid_target, "WI-minimal-invalid", expect=1)
        assert_suite_negative_fail_closed(
            suite_minimal_invalid,
            "invalid_not_applicable_rationale",
            expected_missing_inputs=(
                "not_applicable_rationale:.loom/specs/WI-minimal-invalid/spec.md:block-3:rationale",
                "not_applicable_rationale:.loom/specs/WI-minimal-invalid/spec.md:block-3:consumer_boundary",
                "not_applicable_rationale:.loom/specs/WI-minimal-invalid/spec.md:block-3:recheck_condition",
            ),
            expected_missing_fields=("rationale", "consumer_boundary", "recheck_condition"),
        )

        minimal_deferred_target = tmp / "suite-minimal-deferred"
        minimal_deferred_suite = minimal_deferred_target / ".loom" / "specs" / "WI-minimal-deferred"
        minimal_deferred_suite.mkdir(parents=True)
        (minimal_deferred_suite / "spec.md").write_text(
            "# Spec\n\n"
            "- Suite path: minimal\n\n"
            "- Full suite artifacts deferred: activation condition: later evidence Work Item; "
            "non-blocking consumers: none for readiness.\n",
            encoding="utf-8",
        )
        (minimal_deferred_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_minimal_deferred = run_suite_validate_fixture(minimal_deferred_target, "WI-minimal-deferred", expect=1)
        if (
            suite_minimal_deferred.get("result") != "block"
            or not suite_minimal_deferred.get("payload", {}).get("deferred_items")
            or not any(
                gap.get("failure_kind") == "deferred_as_completed"
                for gap in suite_minimal_deferred.get("blocking_gaps", [])
            )
        ):
            raise AssertionError("suite validate deferred-as-not-applicable payload drifted")
        assert_suite_failure_taxonomy(
            suite_minimal_deferred,
            "deferred_as_completed",
            result="block",
            layer="suite",
        )

        not_applicable_target = tmp / "suite-not-applicable"
        not_applicable_suite = not_applicable_target / ".loom" / "specs" / "WI-not-applicable"
        not_applicable_suite.mkdir(parents=True)
        (not_applicable_suite / "spec.md").write_text(
            "# Spec\n\n"
            "- Suite path: not applicable\n\n"
            "- Suite-level not_applicable: rationale: no formal suite is needed for this fixture; "
            "consumer boundary: suite validation only records the bypass; "
            "recheck condition: a Work Item requires formal spec consumption.\n",
            encoding="utf-8",
        )
        suite_not_applicable = run_suite_inspect_fixture(not_applicable_target, "WI-not-applicable")
        not_applicable_payload = suite_not_applicable.get("payload", {})
        if (
            not_applicable_payload.get("suite_path") != "not_applicable"
            or not_applicable_payload.get("path_decision_locator") != ".loom/specs/WI-not-applicable/spec.md"
            or not_applicable_payload.get("missing_inputs")
        ):
            raise AssertionError("suite inspect not_applicable payload drifted")
        suite_not_applicable_validate = run_suite_validate_fixture(not_applicable_target, "WI-not-applicable", expect=1)
        if (
            suite_not_applicable_validate.get("result") != "not_applicable"
            or suite_not_applicable_validate.get("payload", {}).get("suite_path") != "not_applicable"
            or suite_not_applicable_validate.get("blocking_gaps")
            or not suite_not_applicable_validate.get("payload", {}).get("not_applicable_rationale")
        ):
            raise AssertionError("suite validate not_applicable payload drifted")

        full_target = tmp / "suite-full"
        write_full_suite(full_target, "WI-full")
        assert_full_suite_happy_path_fixture(full_target, "WI-full")

        assert_suite_evidence_surface_fixtures(tmp)

        full_missing_scenario_target = tmp / "suite-full-missing-scenario-mapping"
        full_missing_scenario_suite = full_missing_scenario_target / ".loom" / "specs" / "WI-full-missing-scenario"
        full_missing_scenario_suite.mkdir(parents=True)
        (full_missing_scenario_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_missing_scenario_suite / "spec.md").write_text(
            "# Spec\n\n"
            "## Key Scenarios\n\n"
            "### Scenario S1\n\nGiven a missing mapping fixture\nWhen validation runs\nThen it blocks\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] A1: Acceptance still maps\n",
            encoding="utf-8",
        )
        (full_missing_scenario_suite / "plan.md").write_text(
            "# Plan\n\n"
            "## Test Strategy\n\n"
            "- Acceptance test mapping:\n"
            "  - A1 -> manual evidence: issue closeout comment\n",
            encoding="utf-8",
        )
        suite_full_missing_scenario = run_suite_validate_fixture(
            full_missing_scenario_target,
            "WI-full-missing-scenario",
            expect=1,
        )
        if (
            suite_full_missing_scenario.get("result") != "block"
            or suite_full_missing_scenario.get("failed_layer") != "spec/plan"
            or suite_full_missing_scenario.get("fail_closed_reason") != "missing_spec_plan_mapping"
            or "S1"
            not in suite_full_missing_scenario.get("payload", {}).get("spec_plan_mapping", {}).get("missing_scenarios", [])
            or not any(
                gap.get("failure_kind") == "missing_spec_plan_mapping"
                and gap.get("surface") == "spec/plan"
                for gap in suite_full_missing_scenario.get("blocking_gaps", [])
            )
        ):
            raise AssertionError("suite validate missing scenario mapping payload drifted")
        assert_suite_failure_taxonomy(
            suite_full_missing_scenario,
            "missing_spec_plan_mapping",
            result="block",
            layer="spec/plan",
        )

        full_missing_acceptance_target = tmp / "suite-full-missing-acceptance-mapping"
        full_missing_acceptance_suite = full_missing_acceptance_target / ".loom" / "specs" / "WI-full-missing-acceptance"
        full_missing_acceptance_suite.mkdir(parents=True)
        (full_missing_acceptance_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_missing_acceptance_suite / "spec.md").write_text(
            "# Spec\n\n"
            "## Key Scenarios\n\n"
            "### Scenario S1\n\nGiven an acceptance mapping fixture\nWhen validation runs\nThen it blocks\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] A1: Acceptance must map to a test strategy\n",
            encoding="utf-8",
        )
        (full_missing_acceptance_suite / "plan.md").write_text(
            "# Plan\n\n"
            "## Validation\n\n"
            "- Scenario validation mapping:\n"
            "  - S1 -> automated: python3 tools/check_cli_contract.py\n",
            encoding="utf-8",
        )
        suite_full_missing_acceptance = run_suite_validate_fixture(
            full_missing_acceptance_target,
            "WI-full-missing-acceptance",
            expect=1,
        )
        if (
            suite_full_missing_acceptance.get("result") != "block"
            or suite_full_missing_acceptance.get("failed_layer") != "spec/plan"
            or suite_full_missing_acceptance.get("fail_closed_reason") != "missing_spec_plan_mapping"
            or "A1"
            not in suite_full_missing_acceptance.get("payload", {}).get("spec_plan_mapping", {}).get("missing_acceptance", [])
        ):
            raise AssertionError("suite validate missing acceptance mapping payload drifted")

        full_advisory_target = tmp / "suite-full-advisory"
        full_advisory_suite = full_advisory_target / ".loom" / "specs" / "WI-full-advisory"
        full_advisory_suite.mkdir(parents=True)
        (full_advisory_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_advisory_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (full_advisory_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_full_advisory_validate = run_suite_validate_fixture(full_advisory_target, "WI-full-advisory", expect=1)
        if (
            suite_full_advisory_validate.get("result") != "advisory"
            or suite_full_advisory_validate.get("blocking_gaps")
            or not suite_full_advisory_validate.get("advisory_gaps")
            or suite_full_advisory_validate.get("payload", {}).get("suite_path") != "full"
        ):
            raise AssertionError("suite validate advisory payload drifted")
        assert_suite_failure_taxonomy(
            suite_full_advisory_validate,
            "missing_optional_suite_artifact",
            result="advisory",
            layer="suite",
        )
        full_advisory_inventory = {
            entry["artifact"]: entry
            for entry in suite_full_advisory_validate.get("payload", {}).get("artifact_inventory", [])
        }
        for artifact in ("research.md", "contracts.md", "readiness-checklist.md"):
            if (
                full_advisory_inventory.get(artifact, {}).get("status") != "absent"
                or full_advisory_inventory.get(artifact, {}).get("requirement") != "conditional"
            ):
                raise AssertionError(f"suite validate conditional artifact handling drifted for {artifact}")

        full_missing_target = tmp / "suite-full-missing"
        full_missing_suite = full_missing_target / ".loom" / "specs" / "WI-full-missing"
        full_missing_suite.mkdir(parents=True)
        (full_missing_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_missing_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
        suite_full_missing = run_suite_inspect_fixture(full_missing_target, "WI-full-missing")
        full_missing_payload = suite_full_missing.get("payload", {})
        missing_inventory = {entry["artifact"]: entry for entry in full_missing_payload.get("artifact_inventory", [])}
        if (
            full_missing_payload.get("suite_path") != "full"
            or "required_artifact:.loom/specs/WI-full-missing/plan.md"
            not in full_missing_payload.get("missing_inputs", [])
            or missing_inventory.get("plan.md", {}).get("status") != "missing"
        ):
            raise AssertionError("suite inspect missing required artifact payload drifted")
        suite_full_missing_validate = run_suite_validate_fixture(full_missing_target, "WI-full-missing", expect=1)
        if suite_full_missing_validate.get("failed_layer") != "suite":
            raise AssertionError("suite validate missing required artifact layer drifted")
        assert_suite_negative_fail_closed(
            suite_full_missing_validate,
            "missing_required_artifact",
            expected_missing_inputs=("required_artifact:.loom/specs/WI-full-missing/plan.md",),
        )

        full_invalid_target = tmp / "suite-full-invalid"
        full_invalid_suite = full_invalid_target / ".loom" / "specs" / "WI-full-invalid"
        full_invalid_suite.mkdir(parents=True)
        (full_invalid_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_invalid_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (full_invalid_suite / "plan.md").mkdir()
        suite_full_invalid_validate = run_suite_validate_fixture(full_invalid_target, "WI-full-invalid", expect=1)
        invalid_inventory = {
            entry["artifact"]: entry
            for entry in suite_full_invalid_validate.get("payload", {}).get("artifact_inventory", [])
        }
        if (
            suite_full_invalid_validate.get("result") != "block"
            or suite_full_invalid_validate.get("fail_closed_reason") != "missing_required_artifact"
            or invalid_inventory.get("plan.md", {}).get("status") != "invalid"
            or "required_artifact:.loom/specs/WI-full-invalid/plan.md"
            not in suite_full_invalid_validate.get("payload", {}).get("missing_inputs", [])
        ):
            raise AssertionError("suite validate invalid required artifact payload drifted")

        scaffold_target = tmp / "suite-scaffold"
        scaffold_target.mkdir()
        suite_scaffold = run_suite_scaffold_fixture(scaffold_target, "WI-scaffold")
        scaffold_payload = suite_scaffold.get("payload", {})
        planned_writes = {entry["artifact"]: entry for entry in scaffold_payload.get("planned_writes", [])}
        source_templates = {entry["artifact"]: entry["locator"] for entry in scaffold_payload.get("source_templates", [])}
        if (
            suite_scaffold.get("result") != "pass"
            or scaffold_payload.get("suite_path") != "minimal"
            or scaffold_payload.get("artifact_root") != ".loom/specs/WI-scaffold"
            or scaffold_payload.get("apply_required") is not True
            or scaffold_payload.get("apply") is not False
            or scaffold_payload.get("created_locators") != []
            or "Dry-run only; no files were created." not in scaffold_payload.get("rollback_note", "")
            or sorted(planned_writes) != ["plan.md", "spec.md"]
            or planned_writes["spec.md"].get("locator") != ".loom/specs/WI-scaffold/spec.md"
            or planned_writes["plan.md"].get("locator") != ".loom/specs/WI-scaffold/plan.md"
            or planned_writes["spec.md"].get("status") != "would_create"
            or planned_writes["plan.md"].get("status") != "would_create"
            or planned_writes["spec.md"].get("overwrite_policy") != "preserve_existing"
            or planned_writes["plan.md"].get("overwrite_policy") != "preserve_existing"
            or source_templates.get("spec.md") != "docs/methodology/templates/scaffold/spec.md"
            or source_templates.get("plan.md") != "docs/methodology/templates/scaffold/plan.md"
            or scaffold_payload.get("overwrite_policy", {}).get("mode") != "preserve_existing"
            or scaffold_payload.get("overwrite_policy", {}).get("allows_overwrite") is not False
            or scaffold_payload.get("overwrite_policy", {}).get("ambiguous_overwrite") != "fail_closed"
            or scaffold_payload.get("overwrite_policy", {}).get("existing_files") != []
        ):
            raise AssertionError("suite scaffold dry-run payload drifted")
        if (scaffold_target / ".loom").exists():
            raise AssertionError("suite scaffold dry-run created a .loom directory")

        existing_scaffold_target = tmp / "suite-scaffold-existing"
        existing_suite = existing_scaffold_target / ".loom" / "specs" / "WI-existing"
        existing_suite.mkdir(parents=True)
        (existing_suite / "spec.md").write_text("# Existing spec\n", encoding="utf-8")
        suite_scaffold_existing = run_suite_scaffold_fixture(existing_scaffold_target, "WI-existing")
        existing_payload = suite_scaffold_existing.get("payload", {})
        existing_writes = {entry["artifact"]: entry for entry in existing_payload.get("planned_writes", [])}
        if (
            existing_writes.get("spec.md", {}).get("planned_action") != "preserve_existing"
            or existing_writes.get("spec.md", {}).get("would_write") is not False
            or existing_writes.get("plan.md", {}).get("planned_action") != "create"
            or existing_payload.get("overwrite_policy", {}).get("existing_files") != [".loom/specs/WI-existing/spec.md"]
            or existing_payload.get("created_locators") != []
        ):
            raise AssertionError("suite scaffold existing-file overwrite policy drifted")

        apply_target = tmp / "suite-scaffold-apply"
        apply_target.mkdir()
        suite_scaffold_apply = run_suite_scaffold_apply_fixture(apply_target, "WI-apply")
        apply_payload = suite_scaffold_apply.get("payload", {})
        apply_writes = {entry["artifact"]: entry for entry in apply_payload.get("planned_writes", [])}
        if (
            suite_scaffold_apply.get("mutates") is not True
            or apply_payload.get("apply") is not True
            or apply_payload.get("apply_required") is not False
            or apply_payload.get("created_locators")
            != [".loom/specs/WI-apply/spec.md", ".loom/specs/WI-apply/plan.md"]
            or "Rollback is deleting the created repo-relative locators" not in apply_payload.get("rollback_note", "")
            or apply_writes.get("spec.md", {}).get("status") != "created"
            or apply_writes.get("plan.md", {}).get("status") != "created"
            or not (apply_target / ".loom/specs/WI-apply/spec.md").is_file()
            or not (apply_target / ".loom/specs/WI-apply/plan.md").is_file()
        ):
            raise AssertionError("suite scaffold --apply create payload drifted")

        existing_apply_target = tmp / "suite-scaffold-apply-existing"
        existing_apply_suite = existing_apply_target / ".loom" / "specs" / "WI-apply-existing"
        existing_apply_suite.mkdir(parents=True)
        (existing_apply_suite / "spec.md").write_text("# Existing spec\n", encoding="utf-8")
        suite_scaffold_apply_existing = run_suite_scaffold_apply_fixture(existing_apply_target, "WI-apply-existing")
        apply_existing_payload = suite_scaffold_apply_existing.get("payload", {})
        apply_existing_writes = {entry["artifact"]: entry for entry in apply_existing_payload.get("planned_writes", [])}
        if (
            suite_scaffold_apply_existing.get("mutates") is not True
            or apply_existing_payload.get("created_locators") != [".loom/specs/WI-apply-existing/plan.md"]
            or apply_existing_writes.get("spec.md", {}).get("planned_action") != "preserve_existing"
            or apply_existing_writes.get("spec.md", {}).get("wrote") is not False
            or apply_existing_writes.get("plan.md", {}).get("status") != "created"
            or (existing_apply_suite / "spec.md").read_text(encoding="utf-8") != "# Existing spec\n"
        ):
            raise AssertionError("suite scaffold --apply existing-file preservation drifted")

        suite_scaffold_apply_again = run_suite_scaffold_apply_fixture(apply_target, "WI-apply")
        apply_again_payload = suite_scaffold_apply_again.get("payload", {})
        if (
            suite_scaffold_apply_again.get("mutates") is not False
            or apply_again_payload.get("created_locators") != []
            or apply_again_payload.get("overwrite_policy", {}).get("existing_files")
            != [".loom/specs/WI-apply/spec.md", ".loom/specs/WI-apply/plan.md"]
        ):
            raise AssertionError("suite scaffold --apply repeat preservation drifted")

        traversal_target = tmp / "suite-scaffold-traversal"
        traversal_target.mkdir()
        _, suite_scaffold_traversal = run_json(
            ["suite", "scaffold", "--target", str(traversal_target), "--item", "../escape", "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_traversal.get("result") != "block"
            or suite_scaffold_traversal.get("fail_closed_reason") != "invalid_suite_item"
            or suite_scaffold_traversal.get("mutates") is not False
            or suite_scaffold_traversal.get("payload", {}).get("created_locators") != []
            or (traversal_target / ".loom").exists()
        ):
            raise AssertionError("suite scaffold --apply traversal item did not fail closed")

        _, suite_scaffold_absolute = run_json(
            ["suite", "scaffold", "--target", str(traversal_target), "--item", str(tmp / "abs-write"), "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_absolute.get("result") != "block"
            or suite_scaffold_absolute.get("fail_closed_reason") != "invalid_suite_item"
            or suite_scaffold_absolute.get("payload", {}).get("created_locators") != []
        ):
            raise AssertionError("suite scaffold --apply absolute item did not fail closed")

        symlink_target = tmp / "suite-scaffold-symlink"
        symlink_suite = symlink_target / ".loom" / "specs" / "WI-link"
        symlink_suite.mkdir(parents=True)
        (symlink_suite / "spec.md").symlink_to("../../../outside-spec.md")
        _, suite_scaffold_symlink = run_json(
            ["suite", "scaffold", "--target", str(symlink_target), "--item", "WI-link", "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_symlink.get("result") != "block"
            or suite_scaffold_symlink.get("fail_closed_reason") != "missing_scaffold_inputs"
            or suite_scaffold_symlink.get("payload", {}).get("created_locators") != []
            or (symlink_target / "outside-spec.md").exists()
            or (symlink_suite / "plan.md").exists()
        ):
            raise AssertionError("suite scaffold --apply symlink path did not fail closed")

        directory_artifact_target = tmp / "suite-scaffold-directory-artifact"
        directory_artifact_suite = directory_artifact_target / ".loom" / "specs" / "WI-dir"
        (directory_artifact_suite / "spec.md").mkdir(parents=True)
        _, suite_scaffold_directory_artifact = run_json(
            ["suite", "scaffold", "--target", str(directory_artifact_target), "--item", "WI-dir", "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_directory_artifact.get("result") != "block"
            or suite_scaffold_directory_artifact.get("fail_closed_reason") != "missing_scaffold_inputs"
            or suite_scaffold_directory_artifact.get("payload", {}).get("created_locators") != []
            or suite_scaffold_directory_artifact.get("payload", {}).get("overwrite_policy", {}).get("ambiguous_overwrite") != "fail_closed"
            or "scaffold artifact is not a regular file" not in "\n".join(suite_scaffold_directory_artifact.get("payload", {}).get("missing_inputs", []))
            or (directory_artifact_suite / "plan.md").exists()
        ):
            raise AssertionError("suite scaffold --apply directory artifact did not fail closed")

        full_symlink_target = tmp / "suite-scaffold-full-symlink"
        full_symlink_suite = full_symlink_target / ".loom" / "specs" / "WI-full-link"
        full_symlink_suite.mkdir(parents=True)
        (full_symlink_suite / "research.md").symlink_to("../../../outside-research.md")
        _, suite_scaffold_full_symlink = run_json(
            [
                "suite",
                "scaffold",
                "--target",
                str(full_symlink_target),
                "--item",
                "WI-full-link",
                "--suite",
                "full",
                "--json",
                "--apply",
            ],
            expect=1,
        )
        if (
            suite_scaffold_full_symlink.get("result") != "block"
            or suite_scaffold_full_symlink.get("fail_closed_reason") != "missing_scaffold_inputs"
            or suite_scaffold_full_symlink.get("payload", {}).get("created_locators") != []
            or (full_symlink_target / "outside-research.md").exists()
            or (full_symlink_suite / "spec.md").exists()
        ):
            raise AssertionError("suite scaffold full-suite --apply symlink path did not fail closed")

        full_artifacts = [
            "suite-index.md",
            "spec.md",
            "plan.md",
            "research.md",
            "contracts.md",
            "readiness-checklist.md",
        ]
        full_template_locators = {
            "suite-index.md": "docs/methodology/templates/scaffold/full-suite-index.md",
            "spec.md": "docs/methodology/templates/scaffold/spec.md",
            "plan.md": "docs/methodology/templates/scaffold/plan.md",
            "research.md": "docs/methodology/templates/scaffold/research.md",
            "contracts.md": "docs/methodology/templates/scaffold/contracts.md",
            "readiness-checklist.md": "docs/methodology/templates/scaffold/readiness-checklist.md",
        }

        full_scaffold_target = tmp / "suite-scaffold-full"
        full_scaffold_target.mkdir()
        suite_scaffold_full = run_suite_scaffold_fixture(full_scaffold_target, "WI-full", ["--suite", "full"])
        full_payload = suite_scaffold_full.get("payload", {})
        full_planned_writes = {entry["artifact"]: entry for entry in full_payload.get("planned_writes", [])}
        full_source_templates = {entry["artifact"]: entry["locator"] for entry in full_payload.get("source_templates", [])}
        if (
            suite_scaffold_full.get("result") != "pass"
            or full_payload.get("suite_path") != "full"
            or full_payload.get("artifact_root") != ".loom/specs/WI-full"
            or full_payload.get("apply_required") is not True
            or full_payload.get("apply") is not False
            or full_payload.get("created_locators") != []
            or "Dry-run only; no files were created." not in full_payload.get("rollback_note", "")
            or sorted(full_planned_writes) != sorted(full_artifacts)
            or full_payload.get("required_artifacts") != ["suite-index.md", "spec.md", "plan.md"]
            or full_payload.get("conditional_artifacts") != ["research.md", "contracts.md", "readiness-checklist.md"]
            or full_source_templates != full_template_locators
            or full_planned_writes["suite-index.md"].get("locator") != ".loom/specs/WI-full/suite-index.md"
            or full_planned_writes["research.md"].get("requirement") != "conditional"
            or full_planned_writes["spec.md"].get("requirement") != "required"
            or any(full_planned_writes[artifact].get("overwrite_policy") != "preserve_existing" for artifact in full_artifacts)
            or full_payload.get("overwrite_policy", {}).get("ambiguous_overwrite") != "fail_closed"
        ):
            raise AssertionError("suite scaffold full-suite dry-run payload drifted")
        if (full_scaffold_target / ".loom").exists():
            raise AssertionError("suite scaffold full-suite dry-run created a .loom directory")

        full_apply_target = tmp / "suite-scaffold-full-apply"
        full_apply_target.mkdir()
        suite_scaffold_full_apply = run_suite_scaffold_apply_fixture(full_apply_target, "WI-full-apply", ["--suite", "full"])
        full_apply_payload = suite_scaffold_full_apply.get("payload", {})
        expected_full_created = [f".loom/specs/WI-full-apply/{artifact}" for artifact in full_artifacts]
        full_apply_writes = {entry["artifact"]: entry for entry in full_apply_payload.get("planned_writes", [])}
        if (
            suite_scaffold_full_apply.get("mutates") is not True
            or full_apply_payload.get("apply") is not True
            or full_apply_payload.get("apply_required") is not False
            or full_apply_payload.get("created_locators") != expected_full_created
            or "Rollback is deleting the created repo-relative locators" not in full_apply_payload.get("rollback_note", "")
            or any(full_apply_writes[artifact].get("status") != "created" for artifact in full_artifacts)
            or any(not (full_apply_target / ".loom" / "specs" / "WI-full-apply" / artifact).is_file() for artifact in full_artifacts)
        ):
            raise AssertionError("suite scaffold full-suite --apply create payload drifted")

        full_existing_target = tmp / "suite-scaffold-full-existing"
        full_existing_suite = full_existing_target / ".loom" / "specs" / "WI-full-existing"
        full_existing_suite.mkdir(parents=True)
        (full_existing_suite / "suite-index.md").write_text("# Existing index\n", encoding="utf-8")
        suite_scaffold_full_existing = run_suite_scaffold_apply_fixture(
            full_existing_target,
            "WI-full-existing",
            ["--suite", "full"],
        )
        full_existing_payload = suite_scaffold_full_existing.get("payload", {})
        expected_full_existing_created = [
            f".loom/specs/WI-full-existing/{artifact}"
            for artifact in full_artifacts
            if artifact != "suite-index.md"
        ]
        full_existing_writes = {entry["artifact"]: entry for entry in full_existing_payload.get("planned_writes", [])}
        if (
            suite_scaffold_full_existing.get("mutates") is not True
            or full_existing_payload.get("created_locators") != expected_full_existing_created
            or full_existing_writes["suite-index.md"].get("planned_action") != "preserve_existing"
            or full_existing_writes["suite-index.md"].get("wrote") is not False
            or (full_existing_suite / "suite-index.md").read_text(encoding="utf-8") != "# Existing index\n"
        ):
            raise AssertionError("suite scaffold full-suite --apply existing-file preservation drifted")

        suite_scaffold_full_apply_again = run_suite_scaffold_apply_fixture(
            full_apply_target,
            "WI-full-apply",
            ["--suite", "full"],
        )
        full_apply_again_payload = suite_scaffold_full_apply_again.get("payload", {})
        if (
            suite_scaffold_full_apply_again.get("mutates") is not False
            or full_apply_again_payload.get("created_locators") != []
            or full_apply_again_payload.get("overwrite_policy", {}).get("existing_files") != expected_full_created
        ):
            raise AssertionError("suite scaffold full-suite repeat preservation drifted")

        truth_dry_run_target = tmp / "suite-scaffold-truth-dry-run"
        truth_dry_run_target.mkdir()
        truth_dry_run_before = write_forbidden_truth_fixture(truth_dry_run_target)
        truth_dry_run_tree_before = snapshot_tree(truth_dry_run_target)
        suite_scaffold_truth_dry_run = run_suite_scaffold_fixture(
            truth_dry_run_target,
            "WI-truth",
            ["--suite", "full"],
        )
        truth_dry_run_payload = suite_scaffold_truth_dry_run.get("payload", {})
        assert_forbidden_truth_unchanged(truth_dry_run_target, truth_dry_run_before)
        assert_scaffold_write_boundary(truth_dry_run_payload, item="WI-truth", allowed_artifacts=full_artifacts)
        if snapshot_tree(truth_dry_run_target) != truth_dry_run_tree_before:
            raise AssertionError("suite scaffold dry-run changed host/review/closeout/generated-skill fixture tree")

        truth_minimal_target = tmp / "suite-scaffold-truth-minimal"
        truth_minimal_target.mkdir()
        truth_minimal_before = write_forbidden_truth_fixture(truth_minimal_target)
        suite_scaffold_truth_minimal = run_suite_scaffold_apply_fixture(truth_minimal_target, "WI-truth")
        truth_minimal_payload = suite_scaffold_truth_minimal.get("payload", {})
        assert_forbidden_truth_unchanged(truth_minimal_target, truth_minimal_before)
        assert_scaffold_write_boundary(truth_minimal_payload, item="WI-truth", allowed_artifacts=["spec.md", "plan.md"])
        if truth_minimal_payload.get("created_locators") != [".loom/specs/WI-truth/spec.md", ".loom/specs/WI-truth/plan.md"]:
            raise AssertionError("suite scaffold minimal truth-boundary fixture created unexpected locators")

        truth_full_target = tmp / "suite-scaffold-truth-full"
        truth_full_target.mkdir()
        truth_full_before = write_forbidden_truth_fixture(truth_full_target)
        suite_scaffold_truth_full = run_suite_scaffold_apply_fixture(truth_full_target, "WI-truth", ["--suite", "full"])
        truth_full_payload = suite_scaffold_truth_full.get("payload", {})
        expected_truth_full_created = [f".loom/specs/WI-truth/{artifact}" for artifact in full_artifacts]
        assert_forbidden_truth_unchanged(truth_full_target, truth_full_before)
        assert_scaffold_write_boundary(truth_full_payload, item="WI-truth", allowed_artifacts=full_artifacts)
        if truth_full_payload.get("created_locators") != expected_truth_full_created:
            raise AssertionError("suite scaffold full truth-boundary fixture created unexpected locators")

        missing_target = tmp / "missing"
        missing_target.mkdir()
        status, missing_payload = run_json(["installed-state", "validate", "--target", str(missing_target), "--json"])
        if status == 0 or missing_payload["result"] != "block" or missing_payload["runtime_state"] != "blocked":
            raise AssertionError("missing installed-state did not fail closed")
        _, empty_detect = run_json(["detect", "--target", str(missing_target), "--json"], expect=0)
        if empty_detect["classification"] != "uninstalled" or empty_detect["surfaces"]:
            raise AssertionError("empty target detect did not report uninstalled with no surfaces")

        legacy_target = tmp / "legacy"
        (legacy_target / ".loom" / "bin").mkdir(parents=True)
        status, legacy_payload = run_json(["installed-state", "show", "--target", str(legacy_target), "--json"])
        if status == 0 or not legacy_payload["legacy_surface_hints"]:
            raise AssertionError("legacy surface hints were not reported")
        _, legacy_detect = run_json(["detect", "--target", str(legacy_target), "--json"], expect=0)
        if legacy_detect["classification"] != "legacy" or not any(surface["kind"] == "legacy-loom-bin" for surface in legacy_detect["surfaces"]):
            raise AssertionError("legacy .loom/bin surface was not classified")
        status, legacy_doctor = run_json(["doctor", "--target", str(legacy_target), "--json"])
        if status == 0 or legacy_doctor["result"] != "block" or legacy_doctor["fallback_to"] != ["loom repair plan"]:
            raise AssertionError("legacy doctor did not fail closed to repair plan")
        _, legacy_plan = run_json(["repair", "plan", "--target", str(legacy_target), "--json"], expect=0)
        if not legacy_plan["actions"] or legacy_plan["mutates"] is not False:
            raise AssertionError("legacy repair plan did not emit non-mutating actions")

        mixed_legacy = tmp / "mixed-legacy"
        (mixed_legacy / ".agents" / "skills").mkdir(parents=True)
        (mixed_legacy / "skills").mkdir()
        (mixed_legacy / "skills" / "registry.json").write_text("{}", encoding="utf-8")
        (mixed_legacy / "plugins" / "loom" / ".codex-plugin").mkdir(parents=True)
        (mixed_legacy / "plugins" / "loom" / ".codex-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
        _, mixed_detect = run_json(["detect", "--target", str(mixed_legacy), "--json"], expect=0)
        if mixed_detect["classification"] != "mixed-legacy":
            raise AssertionError("mixed legacy surfaces were not classified as mixed-legacy")

        valid_target = tmp / "valid"
        valid_target.mkdir()
        write_state(valid_target, valid_state(valid_target))
        run_json(["installed-state", "validate", "--target", str(valid_target), "--json"], expect=0)
        valid_home = tmp / "valid-codex-home"
        valid_home.mkdir()
        with isolated_codex_workstation(valid_home):
            register_fixture_codex_plugin()
            _, valid_doctor = run_json(["doctor", "--target", str(valid_target), "--json"], expect=0)
            if valid_doctor["result"] != "pass":
                raise AssertionError("valid installed-state doctor did not pass")
            undeclared_suite_check = next((check for check in valid_doctor.get("checks", []) if check.get("name") == "suite-command-surface"), None)
            if not undeclared_suite_check or undeclared_suite_check.get("result") != "pass" or undeclared_suite_check.get("declared_support") is not False:
                raise AssertionError("doctor did not pass undeclared suite command support")
            _, valid_plan = run_json(["repair", "plan", "--target", str(valid_target), "--json"], expect=0)
            if valid_plan["actions"]:
                raise AssertionError("current installed-state repair plan should be no-op")
            _, exported = run_json(["installed-state", "export", "--target", str(valid_target), "--json"], expect=0)
            if exported["installation_graph"]["layers"] != ["adoption-metadata", "user-skills-provider", "global-cli-provider"]:
                raise AssertionError("installed-state export did not include graph")
            _, upgrade_plan = run_json(["upgrade-plan", "--target", str(valid_target), "--json"], expect=0)
            upgrade_plan = runtime_payload_from_agent_safe_output(upgrade_plan)
            if upgrade_plan["schema"] != "loom-delivery-control/v1" or not upgrade_plan["actions"]:
                raise AssertionError("upgrade-plan did not emit delivery control actions")
            _, verify_payload = run_json(["verify", "--target", str(valid_target), "--json"], expect=0)
            verify_payload = runtime_payload_from_agent_safe_output(verify_payload)
            if verify_payload["schema"] != "loom-delivery-control/v1" or verify_payload["doctor"]["result"] != "pass":
                raise AssertionError("verify did not consume doctor success")
            if verify_payload.get("suite_validation") is not None or verify_payload.get("suite_validation_requirement", {}).get("required") is not False:
                raise AssertionError("verify should not require suite validation without profile or Work Item demand")
        repo_local_target = tmp / "repo-local-wrapper-compatibility"
        repo_local_target.mkdir()
        write_state(repo_local_target, valid_state(repo_local_target))
        repo_local_bin = repo_local_target / ".loom" / "bin"
        repo_local_bin.mkdir(parents=True)
        (repo_local_bin / "loom_flow.py").write_text("# repo-local wrapper compatibility fixture\n", encoding="utf-8")
        _, repo_local_detect = run_json(["detect", "--target", str(repo_local_target), "--json"], expect=0)
        repo_local_runtime = next((surface for surface in repo_local_detect.get("surfaces", []) if surface.get("path") == ".loom/bin"), None)
        if (
            repo_local_detect.get("classification") != "mixed"
            or not repo_local_runtime
            or repo_local_runtime.get("kind") != "legacy-loom-bin"
            or repo_local_runtime.get("migration_status") != "legacy"
        ):
            raise AssertionError("repo-local-wrapper .loom/bin fixture was not classified as unsupported legacy residue")
        status, repo_local_doctor = run_json(["doctor", "--target", str(repo_local_target), "--json"])
        if status == 0 or repo_local_doctor.get("result") != "block":
            raise AssertionError("repo-local-wrapper legacy residue doctor did not block")
        status, repo_local_verify = run_json(["verify", "--target", str(repo_local_target), "--json"])
        if status == 0 or repo_local_verify.get("result") != "block" or repo_local_verify.get("doctor", {}).get("result") != "block":
            raise AssertionError("repo-local-wrapper legacy residue verify did not consume doctor block")
        _, repo_local_repair = run_json(["repair", "plan", "--target", str(repo_local_target), "--json"], expect=0)
        if not repo_local_repair.get("actions"):
            raise AssertionError("repo-local-wrapper legacy residue should produce non-mutating repair guidance")
        global_cli_target = tmp / "global-cli-no-bin"
        global_cli_target.mkdir()
        write_state(global_cli_target, global_cli_state(global_cli_target))
        write_global_cli_fact_chain_fixture(global_cli_target)
        if (global_cli_target / ".loom" / "bin").exists():
            raise AssertionError("global-cli fixture must not carry .loom/bin")
        _, global_validate = run_json(["installed-state", "validate", "--target", str(global_cli_target), "--json"], expect=0)
        if global_validate.get("runtime_state") != "ready":
            raise AssertionError("global-cli installed-state validate did not pass")
        _, global_detect = run_json(["detect", "--target", str(global_cli_target), "--json"], expect=0)
        if global_detect["classification"] != "current":
            raise AssertionError("global-cli no-bin fixture was not classified as current")
        if any(surface.get("path") == ".loom/bin" for surface in global_detect.get("surfaces", [])):
            raise AssertionError("global-cli no-bin fixture must not detect .loom/bin")
        global_cli_home = tmp / "global-cli-codex-home"
        global_cli_home.mkdir()
        with isolated_codex_workstation(global_cli_home):
            register_fixture_codex_plugin()
            _, global_doctor = run_json(["doctor", "--target", str(global_cli_target), "--json"], expect=0)
            provider_check = next((check for check in global_doctor.get("checks", []) if check.get("name") == "global-cli-runtime-provider"), None)
            if global_doctor.get("result") != "pass" or not provider_check or provider_check.get("result") != "pass":
                raise AssertionError("global-cli no-bin doctor did not pass provider diagnostics")
            _, global_verify = run_json(["verify", "--target", str(global_cli_target), "--json"], expect=0)
            if global_verify.get("result") != "pass" or global_verify.get("doctor", {}).get("result") != "pass":
                raise AssertionError("global-cli no-bin verify did not consume doctor success")
            command_mismatch_target = tmp / "global-cli-command-mismatch"
            command_mismatch_target.mkdir()
            command_mismatch_state = global_cli_state(command_mismatch_target)
            command_mismatch_state["provider_requirements"]["global_cli"]["required_commands"].append("loom imaginary")
            write_state(command_mismatch_target, command_mismatch_state)
            status, command_mismatch_doctor = run_json(["doctor", "--target", str(command_mismatch_target), "--json"])
            command_mismatch_check = next(
                (check for check in command_mismatch_doctor.get("checks", []) if check.get("name") == "global-cli-runtime-provider"),
                None,
            )
            if (
                status == 0
                or command_mismatch_doctor.get("result") != "block"
                or command_mismatch_doctor.get("failed_layer") != "global-cli-runtime-provider"
                or not command_mismatch_check
                or command_mismatch_check.get("result") != "block"
                or command_mismatch_check.get("missing_commands") != ["loom imaginary"]
            ):
                raise AssertionError("global-cli provider command mismatch did not fail closed with stable diagnostics")
        _, global_fact_chain = run_json(["fact-chain", "--target", str(global_cli_target), "--json", "--full-output"], expect=0)
        read_entry = global_fact_chain.get("report", {}).get("fact_chain", {}).get("read_entry")
        if not isinstance(read_entry, str) or ".loom/bin" in read_entry or not read_entry.startswith("loom fact-chain "):
            raise AssertionError(f"global-cli fact-chain read_entry was not a global loom command: {read_entry}")
        _, global_status = run_json(["status", "--target", str(global_cli_target), "--json", "--full-output"])
        if ".loom/bin" in str(global_status.get("current_runtime_entrypoint", "")) or not str(global_status.get("status_entrypoint", "")).startswith("loom status "):
            raise AssertionError("global-cli status did not report global loom entrypoint")
        governance_spec = importlib.util.spec_from_file_location(
            "governance_surface_contract",
            REPO_ROOT / "tools" / "governance_surface.py",
        )
        if governance_spec is None or governance_spec.loader is None:
            raise AssertionError("could not load governance_surface module")
        governance_surface = importlib.util.module_from_spec(governance_spec)
        governance_spec.loader.exec_module(governance_surface)
        if governance_surface.command_prefix(global_cli_target, "loom_flow.py") != "loom":
            raise AssertionError("global-cli governance command prefix must leave subcommand selection to the caller")
        _, global_story = run_json(["story", "--target", str(global_cli_target), "--item", "INIT-0001", "--json"], expect=0)
        if ".loom/bin" in str(global_story.get("story_carrier_entrypoint", "")) or not str(global_story.get("story_carrier_entrypoint", "")).startswith("loom story "):
            raise AssertionError("global-cli story did not report global loom entrypoint")
        stale_bin_target = tmp / "global-cli-stale-bin"
        shutil.copytree(global_cli_target, stale_bin_target)
        (stale_bin_target / ".loom" / "bin").mkdir(parents=True)
        (stale_bin_target / ".loom" / "bin" / "loom_flow.py").write_text("# stale fixture\n", encoding="utf-8")
        _, stale_detect = run_json(["detect", "--target", str(stale_bin_target), "--json"], expect=0)
        legacy_bins = [surface for surface in stale_detect.get("surfaces", []) if surface.get("kind") == "legacy-loom-bin"]
        if stale_detect.get("classification") != "mixed" or not legacy_bins:
            raise AssertionError("global-cli stale .loom/bin was not classified as unsupported legacy residue")
        with isolated_codex_workstation(global_cli_home):
            status, stale_doctor = run_json(["doctor", "--target", str(stale_bin_target), "--json"])
            if status == 0 or stale_doctor.get("result") != "block":
                raise AssertionError("global-cli stale .loom/bin did not block doctor as unsupported legacy residue")
        _, stale_repair = run_json(["repair", "plan", "--target", str(stale_bin_target), "--json"], expect=0)
        if stale_repair.get("mutates") is not False or not stale_repair.get("actions"):
            raise AssertionError("global-cli stale .loom/bin did not produce non-mutating legacy guidance")
        _, stale_upgrade = run_json(["upgrade-plan", "--target", str(stale_bin_target), "--json"], expect=0)
        if not stale_upgrade.get("actions"):
            raise AssertionError("global-cli stale .loom/bin upgrade-plan did not expose legacy guidance")
        blocked_bin_target = tmp / "global-cli-stale-bin-blocked"
        shutil.copytree(stale_bin_target, blocked_bin_target)
        write_global_cli_gate_blocker_fixture(blocked_bin_target)
        _, blocked_repair = run_json(["repair", "plan", "--target", str(blocked_bin_target), "--json"], expect=0)
        if blocked_repair.get("mutates") is not False or not blocked_repair.get("actions"):
            raise AssertionError("global-cli blocked stale .loom/bin did not fail closed with non-mutating legacy guidance")
        _, blocked_upgrade = run_json(["upgrade-plan", "--target", str(blocked_bin_target), "--json"], expect=0)
        if not blocked_upgrade.get("actions"):
            raise AssertionError("global-cli blocked stale .loom/bin upgrade-plan did not preserve legacy guidance")
        malformed_target = tmp / "global-cli-malformed"
        malformed_target.mkdir()
        malformed_state = global_cli_state(malformed_target)
        malformed_state["provider_requirements"]["global_cli"].pop("required_commands")
        write_state(malformed_target, malformed_state)
        status, malformed_validate = run_json(["installed-state", "validate", "--target", str(malformed_target), "--json"])
        if status == 0 or malformed_validate.get("result") != "block" or not any(error.get("path") == "provider_requirements.global_cli.required_commands" for error in malformed_validate.get("errors", [])):
            raise AssertionError("malformed global-cli provider requirements did not fail closed")
        declared_target = tmp / "declared-suite-support"
        declared_target.mkdir()
        declared_state = valid_state(declared_target)
        declared_state["declared_support"] = {"suite_commands": ["suite inspect", "suite validate", "suite evidence validate", "suite carrier validate"]}
        write_state(declared_target, declared_state)
        declared_home = tmp / "declared-suite-codex-home"
        declared_home.mkdir()
        with isolated_codex_workstation(declared_home):
            register_fixture_codex_plugin()
            _, declared_doctor = run_json(["doctor", "--target", str(declared_target), "--json"], expect=0)
            declared_suite_check = next((check for check in declared_doctor.get("checks", []) if check.get("name") == "suite-command-surface"), None)
            if (
                declared_doctor.get("result") != "pass"
                or not declared_suite_check
                or declared_suite_check.get("declared_support") is not True
                or declared_suite_check.get("schema_errors")
            ):
                raise AssertionError("doctor did not pass declared suite command support")
            _, declared_verify = run_json(["verify", "--target", str(declared_target), "--json"], expect=0)
            if declared_verify.get("suite_validation_requirement", {}).get("required") is not False or declared_verify.get("suite_validation") is not None:
                raise AssertionError("declared suite support alone must not make verify run suite validation")
        required_target = tmp / "verify-suite-required"
        required_target.mkdir()
        required_state = valid_state(required_target)
        required_state["profile_requirements"] = {"suite_validation": "required", "suite_item": "WI-verify"}
        write_state(required_target, required_state)
        write_minimal_suite(required_target, "WI-verify")
        assert_minimal_suite_happy_path_fixture(required_target, "WI-verify")
        required_home = tmp / "verify-suite-required-codex-home"
        required_home.mkdir()
        with isolated_codex_workstation(required_home):
            register_fixture_codex_plugin()
            _, required_verify = run_json(["verify", "--target", str(required_target), "--json"], expect=0)
            if (
                required_verify.get("suite_validation_requirement", {}).get("required") is not True
                or required_verify.get("suite_validation", {}).get("result") != "pass"
                or required_verify.get("suite_validation", {}).get("item_id") != "WI-verify"
            ):
                raise AssertionError("verify did not run required profile suite validation")
        missing_suite_target = tmp / "verify-suite-missing"
        missing_suite_target.mkdir()
        write_state(missing_suite_target, valid_state(missing_suite_target))
        missing_home = tmp / "verify-suite-missing-codex-home"
        missing_home.mkdir()
        with isolated_codex_workstation(missing_home):
            register_fixture_codex_plugin()
            status, missing_suite_verify = run_json(["verify", "--target", str(missing_suite_target), "--item", "WI-missing", "--json"])
            if (
                status == 0
                or missing_suite_verify.get("result") != "block"
                or missing_suite_verify.get("failed_layer") != "suite"
                or missing_suite_verify.get("suite_validation_requirement", {}).get("required") is not True
                or missing_suite_verify.get("suite_validation", {}).get("result") != "block"
            ):
                raise AssertionError("verify did not block when required Work Item suite validation failed")
        drift_target = tmp / "declared-suite-drift"
        drift_target.mkdir()
        drift_state = valid_state(drift_target)
        drift_state["declared_support"] = {"suite_commands": ["suite inspect", "suite imaginary"]}
        write_state(drift_target, drift_state)
        status, drift_doctor = run_json(["doctor", "--target", str(drift_target), "--json"])
        drift_suite_check = next((check for check in drift_doctor.get("checks", []) if check.get("name") == "suite-command-surface"), None)
        if (
            status == 0
            or drift_doctor.get("result") != "block"
            or drift_doctor.get("failed_layer") != "suite-command-surface"
            or not drift_suite_check
            or drift_suite_check.get("result") != "block"
            or not any(error.get("command") == "suite imaginary" for error in drift_suite_check.get("schema_errors", []))
        ):
            raise AssertionError("doctor did not fail closed on declared suite command surface drift")
        status, install_payload = run_json(["install", "--target", str(valid_target), "--json"])
        if status == 0 or install_payload["failed_layer"] != "install-apply":
            raise AssertionError("install did not fail closed without --apply")
        status, upgrade_payload = run_json(["upgrade", "--target", str(valid_target), "--json"])
        if status == 0 or upgrade_payload["failed_layer"] != "upgrade-apply":
            raise AssertionError("upgrade did not fail closed without --apply")
        status, rollback_payload = run_json(["rollback", "--target", str(valid_target), "--json"])
        if status == 0 or rollback_payload["failed_layer"] != "rollback-ownership":
            raise AssertionError("rollback did not fail closed without rollback ownership")
        _, hosts = run_json(["host", "list", "--target", str(valid_target), "--json"], expect=0)
        hosts = runtime_payload_from_agent_safe_output(hosts)
        if hosts["schema"] != "loom-host-orchestration/v1" or not any(host["id"] == "codex" for host in hosts["hosts"]):
            raise AssertionError("host list did not emit supported host adapter inventory")
        _, host_doctor = run_json(["host", "doctor", "--host", "codex", "--target", str(valid_target), "--json"], expect=0)
        if host_doctor["host"] != "codex" or host_doctor.get("scope") != "user" or host_doctor.get("provider") != "codex-user-plugin":
            raise AssertionError("host doctor did not freeze codex user-level provider output")
        status, host_install = run_json(["host", "install", "--host", "codex", "--target", str(valid_target), "--json"])
        if status == 0 or host_install["result"] != "block" or host_install["failed_layer"] != "host-install":
            raise AssertionError("host install did not fail closed without --apply")
        managed_target = tmp / "managed-host"
        managed_target.mkdir()
        managed_home = tmp / "managed-host-codex-home"
        managed_home.mkdir()
        with isolated_codex_workstation(managed_home):
            _, managed_install = run_json(["host", "install", "--host", "codex", "--target", str(managed_target), "--apply", "--json"], expect=0)
            if managed_install.get("source_kind") != "global-loom-package" or managed_install.get("workstation_install", {}).get("result") != "pass":
                raise AssertionError("user-level host plugin install did not pass readback")
            for unexpected in ("plugins/loom", "skills", ".agents/skills", ".loom/bin", ".loom/installed-state.json"):
                if (managed_target / unexpected).exists():
                    raise AssertionError(f"user-level host plugin install wrote unsupported repository payload: {unexpected}")
        _, skills_list = run_json(["skills", "list", "--json"], expect=0)
        skills_list = runtime_payload_from_agent_safe_output(skills_list)
        if skills_list["schema"] != "loom-skills-surface/v1" or skills_list["root_entry"] != "loom-init":
            raise AssertionError("skills list did not expose generated skills registry")
        status, skills_generate = run_json(["skills", "generate", "--json"])
        if status == 0 or skills_generate["failed_layer"] != "skills-surface":
            raise AssertionError("skills generate did not fail closed without --apply")
        _, skills_check = run_json(["skills", "check", "--target", str(REPO_ROOT), "--json"], expect=0)
        assert_generated_skills_surface_parity_contract(skills_check)
        _, skills_package = run_json(["skills", "package", "--json"], expect=0)
        plugin_payload = skills_package.get("plugin_payload") or {}
        if (
            skills_package.get("result") != "pass"
            or plugin_payload.get("skills_root") != "plugins/loom/skills"
            or plugin_payload.get("single_skill_packages") is not False
            or not plugin_payload.get("skills")
        ):
            raise AssertionError("skills package did not emit plugin payload metadata")
        _, skills_release_check = run_json(["skills", "release-check", "--json"], expect=0)
        release_check_commands = [
            item.get("command", "")
            for item in skills_release_check.get("checks", [])
            if isinstance(item, dict)
        ]
        for expected_check in (
            "tools/host_adapter_check.py",
            "tools/version_surface_check.py",
            "tools/check_release_surface.py",
            "tools/check_npm_package.py",
        ):
            if not any(expected_check in command for command in release_check_commands):
                raise AssertionError(f"skills release-check did not consume {expected_check}")
        release_authority = skills_release_check.get("release_authority") or {}
        if release_authority.get("active_cli_line") != "loom":
            raise AssertionError("skills release-check did not identify loom as the active CLI line")
        if release_authority.get("candidate_authority") != "VERSION":
            raise AssertionError("skills release-check did not identify VERSION as CLI candidate authority")
        if release_authority.get("published_evidence") != ["GitHub v* tag", "GitHub Release"]:
            raise AssertionError("skills release-check did not restrict published CLI evidence to GitHub tag/release")
        legacy_evidence = release_authority.get("legacy_installer_evidence") or {}
        if legacy_evidence.get("active_cli_evidence") is not False:
            raise AssertionError("skills release-check did not mark loom-installer as non-CLI evidence")
        if legacy_evidence.get("tag") != "loom-installer-v0.1.119":
            raise AssertionError("skills release-check did not keep installer tag as legacy baseline evidence")
        _, route_payload = run_json(["route", "--target", str(REPO_ROOT), "--task", "adopt existing repo", "--json"], expect=0)
        route_payload = runtime_payload_from_agent_safe_output(route_payload)
        if route_payload["command"] != "route" or route_payload["selected_skill"] != "loom-adopt":
            raise AssertionError("route did not expose CLI-first scenario routing")
        _, status_payload = run_json(["status", "--target", str(REPO_ROOT), "--json", "--full-output"])
        if status_payload["command"] != "status" or status_payload.get("result") not in {"pass", "block", "fallback"}:
            raise AssertionError("status wrapper did not emit structured status JSON")
        missing_status_target = tmp / "missing-status"
        missing_status_target.mkdir()
        status, missing_status = run_json(["status", "--target", str(missing_status_target), "--json", "--full-output"])
        if status == 0 or missing_status["result"] != "block" or not missing_status.get("blocking_failures"):
            raise AssertionError("status missing-carrier fixture did not fail closed")
        _, fact_chain_payload = run_json(["fact-chain", "--target", str(REPO_ROOT), "--json", "--full-output"], expect=0)
        if fact_chain_payload["command"] != "fact-chain" or fact_chain_payload.get("result") != "pass":
            raise AssertionError("fact-chain wrapper did not consume loom_flow fact-chain JSON")
        _, profile_status = run_json(["profile", "status", "--target", str(REPO_ROOT), "--json"], expect=0)
        profile_status = runtime_payload_from_agent_safe_output(profile_status)
        if profile_status["command"] != "profile status" or profile_status.get("wrapped_command") != "governance-profile":
            raise AssertionError("profile status did not wrap governance-profile status")
        _, profile_plan = run_json(["profile", "upgrade-plan", "--target", str(REPO_ROOT), "--json"])
        profile_plan = runtime_payload_from_agent_safe_output(profile_plan)
        if profile_plan["command"] != "profile upgrade-plan" or profile_plan.get("wrapped_command") != "governance-profile":
            raise AssertionError("profile upgrade-plan did not wrap governance-profile upgrade-plan")
        _, profile_upgrade = run_json(["profile", "upgrade", "--target", str(REPO_ROOT), "--to", "standard", "--json"])
        profile_upgrade = runtime_payload_from_agent_safe_output(profile_upgrade)
        if profile_upgrade["command"] != "profile upgrade" or profile_upgrade.get("wrapped_command") != "governance-profile":
            raise AssertionError("profile upgrade did not wrap governance-profile upgrade")
        _, adoption_verify = run_json(["adopt", "verify", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        adoption_verify = runtime_payload_from_agent_safe_output(adoption_verify)
        if adoption_verify["command"] != "adopt" or adoption_verify.get("schema_version") != "loom-adoption-verify/v1":
            raise AssertionError("adopt verify did not expose adoption verification JSON")
        _, story_payload = run_json(["story", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"], expect=0)
        story_payload = runtime_payload_from_agent_safe_output(story_payload)
        if story_payload["command"] != "story" or story_payload.get("wrapped_command") != "flow":
            raise AssertionError("story did not wrap the flow runtime")
        for command_name in ("spec", "plan"):
            status, scenario_payload = run_json([command_name, "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
            scenario_payload = runtime_payload_from_agent_safe_output(scenario_payload)
            if status == 0 or scenario_payload["schema"] != "loom-scenario-control/v1" or not scenario_payload.get("fallback_to"):
                raise AssertionError(f"{command_name} did not fail closed with a structured locator payload")
        status, build_payload = run_json(["build", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        build_payload = runtime_payload_from_agent_safe_output(build_payload)
        if (
            status == 0
            or build_payload["command"] != "build"
            or build_payload.get("wrapped_command") != "flow"
            or build_payload.get("result") != "block"
            or build_payload.get("fallback_to") != "admission"
        ):
            raise AssertionError("build did not fail closed through the flow runtime for a non-current item")
        status, pre_review_payload = run_json(["pre-review", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        pre_review_payload = runtime_payload_from_agent_safe_output(pre_review_payload)
        if (
            status == 0
            or pre_review_payload["command"] != "pre-review"
            or pre_review_payload.get("wrapped_command") != "flow"
            or pre_review_payload.get("result") != "block"
            or pre_review_payload.get("fallback_to") != "admission"
        ):
            raise AssertionError("pre-review did not fail closed through the flow runtime for a non-current item")
        active_item = active_work_item_id()
        status, active_build = run_json_preserving_attempts(
            ["build", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        active_build = runtime_payload_from_agent_safe_output(active_build)
        assert_suite_build_consumption(active_build)
        assert_review_record_consumed_locators(tmp)
        _, active_pre_review = run_json_preserving_attempts(
            ["pre-review", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        active_pre_review = runtime_payload_from_agent_safe_output(active_pre_review)
        assert_suite_gate_consumption(active_pre_review, expected_surface="pre_review")
        active_guard = active_pre_review.get("readiness_cost_guard")
        if not isinstance(active_guard, dict):
            raise AssertionError("active pre-review did not expose readiness/cost guard")
        if active_guard.get("schema_version") != "loom-pre-review-readiness-cost-guard/v1":
            raise AssertionError("active pre-review readiness/cost guard schema mismatch")
        if active_guard.get("model_profile_proof", {}).get("source_issue") != "#969":
            raise AssertionError("active pre-review readiness/cost guard did not consume #969 profile proof")
        if not isinstance(active_guard.get("post_review_carrier_policy"), dict):
            raise AssertionError("active pre-review readiness/cost guard did not expose carrier-only policy")
        drift_fixture = REPO_ROOT / ".loom" / "runtime" / "WI-957-pr-head-drift-fixture.json"
        drift_fixture.parent.mkdir(parents=True, exist_ok=True)
        drift_payload = {
            "number": 957,
            "state": "OPEN",
            "title": "WI-957 drift fixture",
            "body": f"Loom Work Item: {active_item}\n",
            "url": "https://github.com/MC-and-his-Agents/Loom/pull/957",
            "isDraft": False,
            "headRefName": "work/957-pre-review-readiness-cost-guard",
            "headRefOid": "0000000000000000000000000000000000000000",
            "baseRefName": "main",
        }
        try:
            drift_fixture.write_text(json.dumps(drift_payload, indent=2) + "\n", encoding="utf-8")
            _, drift_pre_review = run_json_preserving_attempts(
                [
                    "pre-review",
                    "--target",
                    str(REPO_ROOT),
                    "--item",
                    active_item,
                    "--pr-payload-file",
                    ".loom/runtime/WI-957-pr-head-drift-fixture.json",
                    "--json",
                ],
                item=active_item,
            )
            drift_pre_review = runtime_payload_from_agent_safe_output(drift_pre_review)
        finally:
            if drift_fixture.exists():
                drift_fixture.unlink()
        drift_guard = drift_pre_review.get("readiness_cost_guard")
        if not isinstance(drift_guard, dict) or "checkout_head_drift" not in drift_guard.get("failure_taxonomy", []):
            raise AssertionError("pre-review readiness/cost guard did not classify PR head drift")
        if drift_guard.get("fallback_to") != "push_or_refresh_pr_head":
            raise AssertionError("pre-review readiness/cost guard did not return push_or_refresh_pr_head fallback for PR head drift")
        _, active_review_gate = run_json_preserving_attempts(
            ["gate", "review", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        active_review_gate = runtime_payload_from_agent_safe_output(active_review_gate)
        assert_suite_gate_consumption(active_review_gate, expected_surface="review")
        _, active_merge_ready = run_json_preserving_attempts(
            ["merge-ready", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        active_merge_ready = runtime_payload_from_agent_safe_output(active_merge_ready)
        assert_suite_gate_consumption(active_merge_ready, expected_surface="merge_ready")
        status, handoff_payload = run_json(["handoff", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        handoff_payload = runtime_payload_from_agent_safe_output(handoff_payload)
        if handoff_payload["command"] != "handoff" or handoff_payload.get("wrapped_command") != "flow":
            raise AssertionError("handoff did not wrap the flow runtime")
        status, retire_payload = run_json(["retire", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        retire_payload = runtime_payload_from_agent_safe_output(retire_payload)
        if retire_payload["command"] != "retire" or not retire_payload.get("retire_contract"):
            raise AssertionError("retire did not expose structured non-mutating contract")
        assert_active_closeout_contract(active_item)
        assert_reconciliation_suite_taxonomy_contract()
        assert_docs_contract_suite_not_applicable_gate_contract(tmp)
        assert_governance_metadata_render_readback_fixture(tmp)
        assert_governance_intensity_metadata_preflight_fixture(tmp)
        assert_semantic_review_disposition_pr_gate_fixture(tmp)
        assert_governance_chain_closeout_fixture(tmp)
        assert_carrier_closeout_sync_contract(tmp)
        assert_repair_apply_carrier_closeout_contract(tmp)
        _, checkpoint_admission = run_json(["checkpoint", "admission", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        checkpoint_admission = runtime_payload_from_agent_safe_output(checkpoint_admission)
        if checkpoint_admission["command"] != "checkpoint admission" or checkpoint_admission.get("checkpoint") != "admission":
            raise AssertionError("checkpoint admission did not wrap checkpoint JSON")
        _, checkpoint_build = run_json(["checkpoint", "build", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        checkpoint_build = runtime_payload_from_agent_safe_output(checkpoint_build)
        if checkpoint_build["command"] != "checkpoint build" or checkpoint_build.get("checkpoint") != "build":
            raise AssertionError("checkpoint build did not wrap checkpoint JSON")
        _, checkpoint_merge = run_json(["checkpoint", "merge", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        checkpoint_merge = runtime_payload_from_agent_safe_output(checkpoint_merge)
        if checkpoint_merge["command"] != "checkpoint merge" or checkpoint_merge.get("checkpoint") != "merge":
            raise AssertionError("checkpoint merge did not wrap checkpoint JSON")
        for gate_command in (
            ["gate", "pr", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"],
            ["gate", "merge", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"],
            ["gate", "closeout", "--json"],
        ):
            status, gate_payload = run_json(gate_command)
            gate_payload = runtime_payload_from_agent_safe_output(gate_payload)
            if status == 0 or gate_payload["result"] not in {"block", "fallback"} or not gate_payload.get("fallback_to"):
                raise AssertionError(f"{gate_command} did not fail closed with structured JSON")

        mixed_target = tmp / "mixed"
        mixed_target.mkdir()
        bad_state = valid_state(mixed_target)
        bad_state["layers"][1]["version_context"]["plugin_surface_version"] = "unknown"
        write_state(mixed_target, bad_state)
        status, mixed_payload = run_json(["installed-state", "validate", "--target", str(mixed_target), "--json"])
        if status == 0 or mixed_payload["result"] != "block":
            raise AssertionError("mixed/unknown version metadata did not fail closed")
        bad_edge_target = tmp / "bad-edge"
        bad_edge_target.mkdir()
        bad_edge_state = valid_state(bad_edge_target)
        bad_edge_state["installation_graph"]["edges"] = [{"from": "skills", "to": "missing", "relationship": "consumes"}]
        write_state(bad_edge_target, bad_edge_state)
        status, bad_edge_payload = run_json(["installed-state", "validate", "--target", str(bad_edge_target), "--json"])
        if status == 0 or not any(error["path"].endswith(".to") for error in bad_edge_payload["errors"]):
            raise AssertionError("unknown graph edge endpoint did not fail closed")
        assert_legacy_fixture_contract(tmp)
        assert_downstream_plugin_layout_contract(tmp)
        assert_metadata_only_adoption_contract(tmp)

    print("cli contract checks passed")


def run_suite_evidence_surface() -> None:
    _, help_payload = run_json(["help", "--json"], expect=0)
    matrix = {entry["command"]: entry for entry in help_payload["commands"]}
    for command, source_issue in (
        ("suite evidence inspect", "#1127"),
        ("suite evidence scaffold", "#1129"),
        ("suite evidence validate", "#1127"),
    ):
        if matrix[command]["status"] != "implemented" or matrix[command]["domain"] != "suite":
            raise AssertionError(f"{command} must be declared in help matrix for {source_issue}")

    with tempfile.TemporaryDirectory(prefix="loom-suite-evidence-") as raw_tmp:
        assert_suite_evidence_surface_fixtures(Path(raw_tmp), include_carrier=False)

    print("suite evidence surface checks passed")


def run_suite_carrier_surface() -> None:
    _, help_payload = run_json(["help", "--json"], expect=0)
    matrix = {entry["command"]: entry for entry in help_payload["commands"]}
    for command, source_issue in (
        ("suite carrier inspect", "#1131"),
        ("suite carrier validate", "#1131"),
    ):
        if matrix[command]["status"] != "implemented" or matrix[command]["domain"] != "suite":
            raise AssertionError(f"{command} must be declared in help matrix for {source_issue}")

    with tempfile.TemporaryDirectory(prefix="loom-suite-carrier-") as raw_tmp:
        assert_suite_carrier_aggregate_fixtures(Path(raw_tmp))

    print("suite carrier surface checks passed")


def run_suite_contract_surface() -> None:
    _, help_payload = run_json(["help", "--json"], expect=0)
    matrix = {entry["command"]: entry for entry in help_payload["commands"]}
    for command, source_issue in (
        ("suite inspect", "#1111"),
        ("suite scaffold", "#1114"),
        ("suite validate", "#1120"),
    ):
        if matrix[command]["status"] != "implemented" or matrix[command]["domain"] != "suite":
            raise AssertionError(f"{command} must be declared in help matrix for {source_issue}")

    with tempfile.TemporaryDirectory(prefix="loom-suite-contract-") as raw_tmp:
        tmp = Path(raw_tmp)
        suite_unknown_target = tmp / "suite-unknown"
        suite_unknown_target.mkdir()
        suite_unknown = run_suite_inspect_fixture(suite_unknown_target, "WI-1109")
        if (
            suite_unknown.get("payload", {}).get("suite_path") != "unknown"
            or suite_unknown.get("payload", {}).get("artifact_inventory") != []
            or "suite_path_decision" not in suite_unknown.get("payload", {}).get("missing_inputs", [])
        ):
            raise AssertionError("suite inspect unknown-state payload drifted")
        suite_unknown_validate = run_suite_validate_fixture(suite_unknown_target, "WI-1109", expect=1)
        if (
            suite_unknown_validate.get("result") != "block"
            or suite_unknown_validate.get("failed_layer") != "suite"
            or suite_unknown_validate.get("fail_closed_reason") != "missing_suite_path_decision"
            or "suite_path_decision" not in suite_unknown_validate.get("missing_inputs", [])
            or not suite_unknown_validate.get("blocking_gaps")
            or suite_unknown_validate.get("advisory_gaps")
        ):
            raise AssertionError("suite validate unknown-state block payload drifted")
        assert_suite_failure_taxonomy(
            suite_unknown_validate,
            "missing_suite_path_decision",
            result="block",
            layer="suite",
        )

        suite_conflict_target = tmp / "suite-conflict"
        suite_conflict = suite_conflict_target / ".loom" / "specs" / "WI-conflict"
        suite_conflict.mkdir(parents=True)
        (suite_conflict / "suite-index.md").write_text("# Suite\n\n- Suite path: full\n", encoding="utf-8")
        (suite_conflict / "spec.md").write_text("# Spec\n\n- Suite path: minimal\n", encoding="utf-8")
        (suite_conflict / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_conflict_validate = run_suite_validate_fixture(suite_conflict_target, "WI-conflict", expect=1)
        conflict_missing = suite_conflict_validate.get("payload", {}).get("missing_inputs", [])
        if (
            suite_conflict_validate.get("result") != "block"
            or suite_conflict_validate.get("fail_closed_reason") != "missing_suite_path_decision"
            or "suite_path_decision" not in conflict_missing
            or not any(str(entry).startswith("conflicting_suite_path_decision:") for entry in conflict_missing)
            or not any(
                gap.get("failure_kind") == "missing_suite_path_decision"
                and gap.get("source_locator") == ".loom/specs/WI-conflict/spec.md"
                for gap in suite_conflict_validate.get("blocking_gaps", [])
            )
        ):
            raise AssertionError("suite validate conflicting path decision payload drifted")

        minimal_target = tmp / "suite-minimal"
        write_minimal_suite(minimal_target, "WI-minimal")
        assert_minimal_suite_happy_path_fixture(minimal_target, "WI-minimal")

        minimal_invalid_target = tmp / "suite-minimal-invalid-rationale"
        minimal_invalid_suite = minimal_invalid_target / ".loom" / "specs" / "WI-minimal-invalid"
        minimal_invalid_suite.mkdir(parents=True)
        (minimal_invalid_suite / "spec.md").write_text(
            "# Spec\n\n- Suite path: minimal\n\n- Full suite artifacts not_applicable.\n",
            encoding="utf-8",
        )
        (minimal_invalid_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_minimal_invalid = run_suite_validate_fixture(minimal_invalid_target, "WI-minimal-invalid", expect=1)
        assert_suite_negative_fail_closed(
            suite_minimal_invalid,
            "invalid_not_applicable_rationale",
            expected_missing_inputs=(
                "not_applicable_rationale:.loom/specs/WI-minimal-invalid/spec.md:block-3:rationale",
                "not_applicable_rationale:.loom/specs/WI-minimal-invalid/spec.md:block-3:consumer_boundary",
                "not_applicable_rationale:.loom/specs/WI-minimal-invalid/spec.md:block-3:recheck_condition",
            ),
            expected_missing_fields=("rationale", "consumer_boundary", "recheck_condition"),
        )

        minimal_deferred_target = tmp / "suite-minimal-deferred"
        minimal_deferred_suite = minimal_deferred_target / ".loom" / "specs" / "WI-minimal-deferred"
        minimal_deferred_suite.mkdir(parents=True)
        (minimal_deferred_suite / "spec.md").write_text(
            "# Spec\n\n"
            "- Suite path: minimal\n\n"
            "- Full suite artifacts deferred: activation condition: later evidence Work Item; "
            "non-blocking consumers: none for readiness.\n",
            encoding="utf-8",
        )
        (minimal_deferred_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_minimal_deferred = run_suite_validate_fixture(minimal_deferred_target, "WI-minimal-deferred", expect=1)
        if (
            suite_minimal_deferred.get("result") != "block"
            or not suite_minimal_deferred.get("payload", {}).get("deferred_items")
            or not any(
                gap.get("failure_kind") == "deferred_as_completed"
                for gap in suite_minimal_deferred.get("blocking_gaps", [])
            )
        ):
            raise AssertionError("suite validate deferred-as-not-applicable payload drifted")
        assert_suite_failure_taxonomy(
            suite_minimal_deferred,
            "deferred_as_completed",
            result="block",
            layer="suite",
        )

        not_applicable_target = tmp / "suite-not-applicable"
        not_applicable_suite = not_applicable_target / ".loom" / "specs" / "WI-not-applicable"
        not_applicable_suite.mkdir(parents=True)
        (not_applicable_suite / "spec.md").write_text(
            "# Spec\n\n"
            "- Suite path: not applicable\n\n"
            "- Suite-level not_applicable: rationale: no formal suite is needed for this fixture; "
            "consumer boundary: suite validation only records the bypass; "
            "recheck condition: a Work Item requires formal spec consumption.\n",
            encoding="utf-8",
        )
        suite_not_applicable = run_suite_inspect_fixture(not_applicable_target, "WI-not-applicable")
        not_applicable_payload = suite_not_applicable.get("payload", {})
        if (
            not_applicable_payload.get("suite_path") != "not_applicable"
            or not_applicable_payload.get("path_decision_locator") != ".loom/specs/WI-not-applicable/spec.md"
            or not_applicable_payload.get("missing_inputs")
        ):
            raise AssertionError("suite inspect not_applicable payload drifted")
        suite_not_applicable_validate = run_suite_validate_fixture(not_applicable_target, "WI-not-applicable", expect=1)
        if (
            suite_not_applicable_validate.get("result") != "not_applicable"
            or suite_not_applicable_validate.get("payload", {}).get("suite_path") != "not_applicable"
            or suite_not_applicable_validate.get("blocking_gaps")
            or not suite_not_applicable_validate.get("payload", {}).get("not_applicable_rationale")
        ):
            raise AssertionError("suite validate not_applicable payload drifted")

        full_target = tmp / "suite-full"
        write_full_suite(full_target, "WI-full")
        assert_full_suite_happy_path_fixture(full_target, "WI-full")

        full_missing_scenario_target = tmp / "suite-full-missing-scenario-mapping"
        full_missing_scenario_suite = full_missing_scenario_target / ".loom" / "specs" / "WI-full-missing-scenario"
        full_missing_scenario_suite.mkdir(parents=True)
        (full_missing_scenario_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_missing_scenario_suite / "spec.md").write_text(
            "# Spec\n\n"
            "## Key Scenarios\n\n"
            "### Scenario S1\n\nGiven a missing mapping fixture\nWhen validation runs\nThen it blocks\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] A1: Acceptance still maps\n",
            encoding="utf-8",
        )
        (full_missing_scenario_suite / "plan.md").write_text(
            "# Plan\n\n"
            "## Test Strategy\n\n"
            "- Acceptance test mapping:\n"
            "  - A1 -> manual evidence: issue closeout comment\n",
            encoding="utf-8",
        )
        suite_full_missing_scenario = run_suite_validate_fixture(
            full_missing_scenario_target,
            "WI-full-missing-scenario",
            expect=1,
        )
        if (
            suite_full_missing_scenario.get("result") != "block"
            or suite_full_missing_scenario.get("failed_layer") != "spec/plan"
            or suite_full_missing_scenario.get("fail_closed_reason") != "missing_spec_plan_mapping"
            or "S1"
            not in suite_full_missing_scenario.get("payload", {}).get("spec_plan_mapping", {}).get("missing_scenarios", [])
            or not any(
                gap.get("failure_kind") == "missing_spec_plan_mapping"
                and gap.get("surface") == "spec/plan"
                for gap in suite_full_missing_scenario.get("blocking_gaps", [])
            )
        ):
            raise AssertionError("suite validate missing scenario mapping payload drifted")
        assert_suite_failure_taxonomy(
            suite_full_missing_scenario,
            "missing_spec_plan_mapping",
            result="block",
            layer="spec/plan",
        )

        full_missing_acceptance_target = tmp / "suite-full-missing-acceptance-mapping"
        full_missing_acceptance_suite = full_missing_acceptance_target / ".loom" / "specs" / "WI-full-missing-acceptance"
        full_missing_acceptance_suite.mkdir(parents=True)
        (full_missing_acceptance_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_missing_acceptance_suite / "spec.md").write_text(
            "# Spec\n\n"
            "## Key Scenarios\n\n"
            "### Scenario S1\n\nGiven an acceptance mapping fixture\nWhen validation runs\nThen it blocks\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] A1: Acceptance must map to a test strategy\n",
            encoding="utf-8",
        )
        (full_missing_acceptance_suite / "plan.md").write_text(
            "# Plan\n\n"
            "## Validation\n\n"
            "- Scenario validation mapping:\n"
            "  - S1 -> automated: python3 tools/check_cli_contract.py\n",
            encoding="utf-8",
        )
        suite_full_missing_acceptance = run_suite_validate_fixture(
            full_missing_acceptance_target,
            "WI-full-missing-acceptance",
            expect=1,
        )
        if (
            suite_full_missing_acceptance.get("result") != "block"
            or suite_full_missing_acceptance.get("failed_layer") != "spec/plan"
            or suite_full_missing_acceptance.get("fail_closed_reason") != "missing_spec_plan_mapping"
            or "A1"
            not in suite_full_missing_acceptance.get("payload", {}).get("spec_plan_mapping", {}).get("missing_acceptance", [])
        ):
            raise AssertionError("suite validate missing acceptance mapping payload drifted")

        full_advisory_target = tmp / "suite-full-advisory"
        full_advisory_suite = full_advisory_target / ".loom" / "specs" / "WI-full-advisory"
        full_advisory_suite.mkdir(parents=True)
        (full_advisory_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_advisory_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (full_advisory_suite / "plan.md").write_text("# Plan\n", encoding="utf-8")
        suite_full_advisory_validate = run_suite_validate_fixture(full_advisory_target, "WI-full-advisory", expect=1)
        if (
            suite_full_advisory_validate.get("result") != "advisory"
            or suite_full_advisory_validate.get("blocking_gaps")
            or not suite_full_advisory_validate.get("advisory_gaps")
            or suite_full_advisory_validate.get("payload", {}).get("suite_path") != "full"
        ):
            raise AssertionError("suite validate advisory payload drifted")
        assert_suite_failure_taxonomy(
            suite_full_advisory_validate,
            "missing_optional_suite_artifact",
            result="advisory",
            layer="suite",
        )

        full_missing_target = tmp / "suite-full-missing"
        full_missing_suite = full_missing_target / ".loom" / "specs" / "WI-full-missing"
        full_missing_suite.mkdir(parents=True)
        (full_missing_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_missing_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
        suite_full_missing = run_suite_inspect_fixture(full_missing_target, "WI-full-missing")
        full_missing_payload = suite_full_missing.get("payload", {})
        missing_inventory = {entry["artifact"]: entry for entry in full_missing_payload.get("artifact_inventory", [])}
        if (
            full_missing_payload.get("suite_path") != "full"
            or "required_artifact:.loom/specs/WI-full-missing/plan.md"
            not in full_missing_payload.get("missing_inputs", [])
            or missing_inventory.get("plan.md", {}).get("status") != "missing"
        ):
            raise AssertionError("suite inspect missing required artifact payload drifted")
        suite_full_missing_validate = run_suite_validate_fixture(full_missing_target, "WI-full-missing", expect=1)
        if suite_full_missing_validate.get("failed_layer") != "suite":
            raise AssertionError("suite validate missing required artifact layer drifted")
        assert_suite_negative_fail_closed(
            suite_full_missing_validate,
            "missing_required_artifact",
            expected_missing_inputs=("required_artifact:.loom/specs/WI-full-missing/plan.md",),
        )

        full_invalid_target = tmp / "suite-full-invalid"
        full_invalid_suite = full_invalid_target / ".loom" / "specs" / "WI-full-invalid"
        full_invalid_suite.mkdir(parents=True)
        (full_invalid_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        (full_invalid_suite / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (full_invalid_suite / "plan.md").mkdir()
        suite_full_invalid_validate = run_suite_validate_fixture(full_invalid_target, "WI-full-invalid", expect=1)
        invalid_inventory = {
            entry["artifact"]: entry
            for entry in suite_full_invalid_validate.get("payload", {}).get("artifact_inventory", [])
        }
        if (
            suite_full_invalid_validate.get("result") != "block"
            or suite_full_invalid_validate.get("fail_closed_reason") != "missing_required_artifact"
            or invalid_inventory.get("plan.md", {}).get("status") != "invalid"
            or "required_artifact:.loom/specs/WI-full-invalid/plan.md"
            not in suite_full_invalid_validate.get("payload", {}).get("missing_inputs", [])
        ):
            raise AssertionError("suite validate invalid required artifact payload drifted")

        scaffold_target = tmp / "suite-scaffold"
        scaffold_target.mkdir()
        suite_scaffold = run_suite_scaffold_fixture(scaffold_target, "WI-scaffold")
        scaffold_payload = suite_scaffold.get("payload", {})
        planned_writes = {entry["artifact"]: entry for entry in scaffold_payload.get("planned_writes", [])}
        source_templates = {entry["artifact"]: entry["locator"] for entry in scaffold_payload.get("source_templates", [])}
        if (
            suite_scaffold.get("result") != "pass"
            or scaffold_payload.get("suite_path") != "minimal"
            or scaffold_payload.get("artifact_root") != ".loom/specs/WI-scaffold"
            or scaffold_payload.get("apply_required") is not True
            or scaffold_payload.get("apply") is not False
            or scaffold_payload.get("created_locators") != []
            or "Dry-run only; no files were created." not in scaffold_payload.get("rollback_note", "")
            or sorted(planned_writes) != ["plan.md", "spec.md"]
            or planned_writes["spec.md"].get("locator") != ".loom/specs/WI-scaffold/spec.md"
            or planned_writes["plan.md"].get("locator") != ".loom/specs/WI-scaffold/plan.md"
            or planned_writes["spec.md"].get("status") != "would_create"
            or planned_writes["plan.md"].get("status") != "would_create"
            or planned_writes["spec.md"].get("overwrite_policy") != "preserve_existing"
            or planned_writes["plan.md"].get("overwrite_policy") != "preserve_existing"
            or source_templates.get("spec.md") != "docs/methodology/templates/scaffold/spec.md"
            or source_templates.get("plan.md") != "docs/methodology/templates/scaffold/plan.md"
            or scaffold_payload.get("overwrite_policy", {}).get("mode") != "preserve_existing"
            or scaffold_payload.get("overwrite_policy", {}).get("allows_overwrite") is not False
            or scaffold_payload.get("overwrite_policy", {}).get("ambiguous_overwrite") != "fail_closed"
            or scaffold_payload.get("overwrite_policy", {}).get("existing_files") != []
        ):
            raise AssertionError("suite scaffold dry-run payload drifted")
        if (scaffold_target / ".loom").exists():
            raise AssertionError("suite scaffold dry-run created a .loom directory")

        existing_scaffold_target = tmp / "suite-scaffold-existing"
        existing_suite = existing_scaffold_target / ".loom" / "specs" / "WI-existing"
        existing_suite.mkdir(parents=True)
        (existing_suite / "spec.md").write_text("# Existing spec\n", encoding="utf-8")
        suite_scaffold_existing = run_suite_scaffold_fixture(existing_scaffold_target, "WI-existing")
        existing_payload = suite_scaffold_existing.get("payload", {})
        existing_writes = {entry["artifact"]: entry for entry in existing_payload.get("planned_writes", [])}
        if (
            existing_writes.get("spec.md", {}).get("planned_action") != "preserve_existing"
            or existing_writes.get("spec.md", {}).get("would_write") is not False
            or existing_writes.get("plan.md", {}).get("planned_action") != "create"
            or existing_payload.get("overwrite_policy", {}).get("existing_files") != [".loom/specs/WI-existing/spec.md"]
            or existing_payload.get("created_locators") != []
        ):
            raise AssertionError("suite scaffold existing-file overwrite policy drifted")

        apply_target = tmp / "suite-scaffold-apply"
        apply_target.mkdir()
        suite_scaffold_apply = run_suite_scaffold_apply_fixture(apply_target, "WI-apply")
        apply_payload = suite_scaffold_apply.get("payload", {})
        apply_writes = {entry["artifact"]: entry for entry in apply_payload.get("planned_writes", [])}
        if (
            suite_scaffold_apply.get("mutates") is not True
            or apply_payload.get("apply") is not True
            or apply_payload.get("apply_required") is not False
            or apply_payload.get("created_locators")
            != [".loom/specs/WI-apply/spec.md", ".loom/specs/WI-apply/plan.md"]
            or "Rollback is deleting the created repo-relative locators" not in apply_payload.get("rollback_note", "")
            or apply_writes.get("spec.md", {}).get("status") != "created"
            or apply_writes.get("plan.md", {}).get("status") != "created"
            or not (apply_target / ".loom/specs/WI-apply/spec.md").is_file()
            or not (apply_target / ".loom/specs/WI-apply/plan.md").is_file()
        ):
            raise AssertionError("suite scaffold --apply create payload drifted")

        existing_apply_target = tmp / "suite-scaffold-apply-existing"
        existing_apply_suite = existing_apply_target / ".loom" / "specs" / "WI-apply-existing"
        existing_apply_suite.mkdir(parents=True)
        (existing_apply_suite / "spec.md").write_text("# Existing spec\n", encoding="utf-8")
        suite_scaffold_apply_existing = run_suite_scaffold_apply_fixture(existing_apply_target, "WI-apply-existing")
        apply_existing_payload = suite_scaffold_apply_existing.get("payload", {})
        apply_existing_writes = {entry["artifact"]: entry for entry in apply_existing_payload.get("planned_writes", [])}
        if (
            suite_scaffold_apply_existing.get("mutates") is not True
            or apply_existing_payload.get("created_locators") != [".loom/specs/WI-apply-existing/plan.md"]
            or apply_existing_writes.get("spec.md", {}).get("planned_action") != "preserve_existing"
            or apply_existing_writes.get("spec.md", {}).get("wrote") is not False
            or apply_existing_writes.get("plan.md", {}).get("status") != "created"
            or (existing_apply_suite / "spec.md").read_text(encoding="utf-8") != "# Existing spec\n"
        ):
            raise AssertionError("suite scaffold --apply existing-file preservation drifted")

        suite_scaffold_apply_again = run_suite_scaffold_apply_fixture(apply_target, "WI-apply")
        apply_again_payload = suite_scaffold_apply_again.get("payload", {})
        if (
            suite_scaffold_apply_again.get("mutates") is not False
            or apply_again_payload.get("created_locators") != []
            or apply_again_payload.get("overwrite_policy", {}).get("existing_files")
            != [".loom/specs/WI-apply/spec.md", ".loom/specs/WI-apply/plan.md"]
        ):
            raise AssertionError("suite scaffold --apply repeat preservation drifted")

        traversal_target = tmp / "suite-scaffold-traversal"
        traversal_target.mkdir()
        _, suite_scaffold_traversal = run_json(
            ["suite", "scaffold", "--target", str(traversal_target), "--item", "../escape", "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_traversal.get("result") != "block"
            or suite_scaffold_traversal.get("fail_closed_reason") != "invalid_suite_item"
            or suite_scaffold_traversal.get("mutates") is not False
            or suite_scaffold_traversal.get("payload", {}).get("created_locators") != []
            or (traversal_target / ".loom").exists()
        ):
            raise AssertionError("suite scaffold --apply traversal item did not fail closed")

        _, suite_scaffold_absolute = run_json(
            ["suite", "scaffold", "--target", str(traversal_target), "--item", str(tmp / "abs-write"), "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_absolute.get("result") != "block"
            or suite_scaffold_absolute.get("fail_closed_reason") != "invalid_suite_item"
            or suite_scaffold_absolute.get("payload", {}).get("created_locators") != []
        ):
            raise AssertionError("suite scaffold --apply absolute item did not fail closed")

        symlink_target = tmp / "suite-scaffold-symlink"
        symlink_suite = symlink_target / ".loom" / "specs" / "WI-link"
        symlink_suite.mkdir(parents=True)
        (symlink_suite / "spec.md").symlink_to("../../../outside-spec.md")
        _, suite_scaffold_symlink = run_json(
            ["suite", "scaffold", "--target", str(symlink_target), "--item", "WI-link", "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_symlink.get("result") != "block"
            or suite_scaffold_symlink.get("fail_closed_reason") != "missing_scaffold_inputs"
            or suite_scaffold_symlink.get("payload", {}).get("created_locators") != []
            or (symlink_target / "outside-spec.md").exists()
            or (symlink_suite / "plan.md").exists()
        ):
            raise AssertionError("suite scaffold --apply symlink path did not fail closed")

        directory_artifact_target = tmp / "suite-scaffold-directory-artifact"
        directory_artifact_suite = directory_artifact_target / ".loom" / "specs" / "WI-dir"
        (directory_artifact_suite / "spec.md").mkdir(parents=True)
        _, suite_scaffold_directory_artifact = run_json(
            ["suite", "scaffold", "--target", str(directory_artifact_target), "--item", "WI-dir", "--json", "--apply"],
            expect=1,
        )
        if (
            suite_scaffold_directory_artifact.get("result") != "block"
            or suite_scaffold_directory_artifact.get("fail_closed_reason") != "missing_scaffold_inputs"
            or suite_scaffold_directory_artifact.get("payload", {}).get("created_locators") != []
            or suite_scaffold_directory_artifact.get("payload", {}).get("overwrite_policy", {}).get("ambiguous_overwrite") != "fail_closed"
            or "scaffold artifact is not a regular file" not in "\n".join(suite_scaffold_directory_artifact.get("payload", {}).get("missing_inputs", []))
            or (directory_artifact_suite / "plan.md").exists()
        ):
            raise AssertionError("suite scaffold --apply directory artifact did not fail closed")

        full_artifacts = [
            "suite-index.md",
            "spec.md",
            "plan.md",
            "research.md",
            "contracts.md",
            "readiness-checklist.md",
        ]
        full_scaffold_target = tmp / "suite-scaffold-full"
        full_scaffold_target.mkdir()
        suite_scaffold_full = run_suite_scaffold_fixture(full_scaffold_target, "WI-full", ["--suite", "full"])
        full_payload = suite_scaffold_full.get("payload", {})
        full_planned_writes = {entry["artifact"]: entry for entry in full_payload.get("planned_writes", [])}
        if (
            suite_scaffold_full.get("result") != "pass"
            or full_payload.get("suite_path") != "full"
            or full_payload.get("artifact_root") != ".loom/specs/WI-full"
            or full_payload.get("apply_required") is not True
            or full_payload.get("apply") is not False
            or full_payload.get("created_locators") != []
            or sorted(full_planned_writes) != sorted(full_artifacts)
            or full_payload.get("required_artifacts") != ["suite-index.md", "spec.md", "plan.md"]
            or full_payload.get("conditional_artifacts") != ["research.md", "contracts.md", "readiness-checklist.md"]
            or full_planned_writes["suite-index.md"].get("locator") != ".loom/specs/WI-full/suite-index.md"
            or full_planned_writes["research.md"].get("requirement") != "conditional"
            or full_planned_writes["spec.md"].get("requirement") != "required"
            or any(full_planned_writes[artifact].get("overwrite_policy") != "preserve_existing" for artifact in full_artifacts)
            or full_payload.get("overwrite_policy", {}).get("ambiguous_overwrite") != "fail_closed"
        ):
            raise AssertionError("suite scaffold full-suite dry-run payload drifted")
        if (full_scaffold_target / ".loom").exists():
            raise AssertionError("suite scaffold full-suite dry-run created a .loom directory")

        truth_dry_run_target = tmp / "suite-scaffold-truth-dry-run"
        truth_dry_run_target.mkdir()
        truth_dry_run_before = write_forbidden_truth_fixture(truth_dry_run_target)
        truth_dry_run_tree_before = snapshot_tree(truth_dry_run_target)
        suite_scaffold_truth_dry_run = run_suite_scaffold_fixture(
            truth_dry_run_target,
            "WI-truth",
            ["--suite", "full"],
        )
        truth_dry_run_payload = suite_scaffold_truth_dry_run.get("payload", {})
        assert_forbidden_truth_unchanged(truth_dry_run_target, truth_dry_run_before)
        assert_scaffold_write_boundary(truth_dry_run_payload, item="WI-truth", allowed_artifacts=full_artifacts)
        if snapshot_tree(truth_dry_run_target) != truth_dry_run_tree_before:
            raise AssertionError("suite scaffold dry-run changed host/review/closeout/generated-skill fixture tree")

        truth_minimal_target = tmp / "suite-scaffold-truth-minimal"
        truth_minimal_target.mkdir()
        truth_minimal_before = write_forbidden_truth_fixture(truth_minimal_target)
        suite_scaffold_truth_minimal = run_suite_scaffold_apply_fixture(truth_minimal_target, "WI-truth")
        truth_minimal_payload = suite_scaffold_truth_minimal.get("payload", {})
        assert_forbidden_truth_unchanged(truth_minimal_target, truth_minimal_before)
        assert_scaffold_write_boundary(truth_minimal_payload, item="WI-truth", allowed_artifacts=["spec.md", "plan.md"])
        if truth_minimal_payload.get("created_locators") != [".loom/specs/WI-truth/spec.md", ".loom/specs/WI-truth/plan.md"]:
            raise AssertionError("suite scaffold minimal truth-boundary fixture created unexpected locators")

    print("suite contract surface checks passed")


def available_surface_checks() -> tuple[SurfaceCheck, ...]:
    return (
        SurfaceCheck(
            name="suite-contract",
            fixture_group="suite-contract",
            run=run_suite_contract_surface,
        ),
        SurfaceCheck(
            name="suite-evidence",
            fixture_group="suite-evidence",
            run=run_suite_evidence_surface,
        ),
        SurfaceCheck(
            name="suite-carrier",
            fixture_group="suite-carrier",
            run=run_suite_carrier_surface,
        ),
        SurfaceCheck(
            name="governance-closeout",
            fixture_group="governance-closeout",
            run=run_governance_closeout_contract,
        ),
        SurfaceCheck(
            name="adoption-host-metadata",
            fixture_group="adoption-host-metadata",
            run=run_adoption_host_metadata_surface,
        ),
        SurfaceCheck(
            name="merge-wrapper",
            fixture_group="merge-wrapper",
            run=run_merge_wrapper_surface,
        ),
        SurfaceCheck(
            name="ship-wrapper",
            fixture_group="ship-wrapper",
            run=run_ship_wrapper_surface,
        ),
        SurfaceCheck(
            name="closeout-wrapper",
            fixture_group="closeout-wrapper",
            run=run_closeout_wrapper_surface,
        ),
        SurfaceCheck(
            name="work-item-audit",
            fixture_group="work-item-audit",
            run=run_work_item_audit_surface,
        ),
        SurfaceCheck(
            name="release-readback",
            fixture_group="release-readback",
            run=run_release_readback_surface,
        ),
        SurfaceCheck(
            name="pr-metadata",
            fixture_group="pr-metadata",
            run=run_pr_metadata_surface,
        ),
        SurfaceCheck(
            name="controlled-merge",
            fixture_group="controlled-merge",
            run=run_controlled_merge_surface,
        ),
        SurfaceCheck(
            name="aggregate",
            fixture_group="check-cli-contract",
            run=run_aggregate_cli_contract,
        ),
    )


def main(argv: list[str] | None = None) -> int:
    checks = available_surface_checks()
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.list_surfaces:
        for check in checks:
            print(f"{check.name}\t{check.fixture_group}")
        return 0
    try:
        selected = selected_surface_checks(
            checks,
            surfaces=args.surfaces,
            fixture_groups=args.fixture_groups,
        )
    except ValueError as exc:
        print(f"cli contract surface selection failed: {exc}", file=sys.stderr)
        return 2
    return run_surface_checks(selected)


if __name__ == "__main__":
    sys.exit(main())
