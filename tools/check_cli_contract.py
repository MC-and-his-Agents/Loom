#!/usr/bin/env python3
"""Contract checks for the CLI-first Loom surface."""

from __future__ import annotations

import json
import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LOOM = REPO_ROOT / "tools" / "loom.py"
LEGACY_FIXTURES = REPO_ROOT / "docs" / "evidence" / "fixtures" / "legacy-migration-validation-fixtures.json"

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
    "gate closeout",
    "host list",
    "host doctor",
    "host install",
    "host verify",
    "host upgrade",
    "host remove",
    "workspace create",
    "workspace locate",
    "workspace check",
    "workspace retire",
    "issue inspect",
    "issue bind",
    "issue reconcile",
    "project status",
    "project reconcile",
    "pr inspect",
    "pr metadata-preflight",
    "pr gate",
    "merge check",
    "merge run",
    "reconcile",
    "skills list",
    "skills generate",
    "skills sync",
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


def run_json(args: list[str], *, expect: int | None = None) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, str(LOOM), *args],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if expect is not None and completed.returncode != expect:
        raise AssertionError(f"{args} returned {completed.returncode}, expected {expect}\n{completed.stderr}\n{completed.stdout}")
    raw = completed.stdout or completed.stderr
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{args} did not emit JSON: {exc}\n{raw}") from exc
    return completed.returncode, payload


def run_flow_json(args: list[str], *, cwd: Path = REPO_ROOT, expect: int | None = None) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "loom_flow.py"), *args],
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if expect is not None and completed.returncode != expect:
        raise AssertionError(f"loom_flow.py {args} returned {completed.returncode}, expected {expect}\n{completed.stderr}\n{completed.stdout}")
    raw = completed.stdout or completed.stderr
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"loom_flow.py {args} did not emit JSON: {exc}\n{raw}") from exc
    return completed.returncode, payload


def active_work_item_id() -> str:
    payload = json.loads((REPO_ROOT / ".loom" / "bootstrap" / "init-result.json").read_text(encoding="utf-8"))
    item_id = payload.get("fact_chain", {}).get("entry_points", {}).get("current_item_id")
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


def assert_suite_gate_consumption(payload: dict[str, Any], *, expected_surface: str) -> None:
    suite_gate = payload.get("suite_gate_validation")
    if not isinstance(suite_gate, dict):
        raise AssertionError(f"{expected_surface} did not expose suite gate validation")
    if suite_gate.get("schema_version") != "loom-suite-gate-validation/v1":
        raise AssertionError(f"{expected_surface} suite gate validation schema drifted")
    if suite_gate.get("surface") != expected_surface:
        raise AssertionError(f"{expected_surface} suite gate validation surface drifted")
    if suite_gate.get("result") not in {"pass", "block", "fallback"}:
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
        if command_fragment not in str(validation.get("command", "")):
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
    if (
        not isinstance(consumed, dict)
        or "evidence_map" not in consumed
        or "consistency_analysis" not in consumed
        or "task_carriers" not in consumed
    ):
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


def assert_review_record_consumed_locators(active_item: str) -> None:
    spec_review = REPO_ROOT / ".loom" / "reviews" / f"{active_item}.spec.json"
    implementation_review = REPO_ROOT / ".loom" / "reviews" / f"{active_item}.json"
    with preserved_repo_paths((spec_review.relative_to(REPO_ROOT).as_posix(), implementation_review.relative_to(REPO_ROOT).as_posix())):
        _, spec_record_payload = run_json(
            [
                "review",
                "record",
                "--target",
                str(REPO_ROOT),
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
        expected_spec = f".loom/specs/{active_item}/spec.md"
        expected_plan = f".loom/specs/{active_item}/plan.md"
        expected_evidence = f".loom/specs/{active_item}/evidence-map.md"
        expected_carrier = f".loom/specs/{active_item}/task-carrier.md"
        if (
            spec_consumed.get("suite_validation") != "suite validate"
            or spec_consumed.get("suite_validator_mode") != "repo-local-cli"
            or spec_consumed.get("suite_spec") != expected_spec
            or spec_consumed.get("suite_plan") != expected_plan
            or spec_consumed.get("suite_evidence_map") != expected_evidence
            or "suite_consistency_analysis" not in spec_consumed
            or expected_carrier not in spec_consumed.get("suite_task_carriers", [])
        ):
            raise AssertionError("spec review record consumed suite locators drifted")
        _, implementation_record_payload = run_json(
            [
                "review",
                "record",
                "--target",
                str(REPO_ROOT),
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
        if (
            "suite evidence validate" not in str(implementation_consumed.get("suite_evidence_validation", ""))
            or "suite carrier validate" not in str(implementation_consumed.get("suite_carrier_validation", ""))
            or implementation_consumed.get("suite_evidence_map") != expected_evidence
            or "suite_consistency_analysis" not in implementation_consumed
            or expected_carrier not in implementation_consumed.get("suite_task_carriers", [])
            or not isinstance(implementation_consumed.get("suite_evidence_consumed_contracts"), list)
            or not isinstance(implementation_consumed.get("suite_carrier_consumed_contracts"), list)
        ):
            raise AssertionError("implementation review record consumed suite/evidence locators drifted")


def assert_closeout_blocks_missing_suite_evidence(active_item: str) -> None:
    evidence_map = f".loom/specs/{active_item}/evidence-map.md"
    with preserved_repo_paths((evidence_map,)):
        path = REPO_ROOT / evidence_map
        if path.exists():
            path.unlink()
        status, payload = run_json(["closeout", "--target", str(REPO_ROOT), "--json"])
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


def assert_legacy_fixture_contract(tmp: Path) -> None:
    fixture_data = json.loads(LEGACY_FIXTURES.read_text(encoding="utf-8"))
    if fixture_data.get("schema_version") != "loom-legacy-migration-validation-fixtures/v1":
        raise AssertionError("legacy migration fixture schema drifted")
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


def valid_state(target: Path) -> dict[str, Any]:
    return {
        "schema_version": "loom-installed-state/v2",
        "installation_id": "fixture-valid",
        "target": str(target),
        "upgrade_eligibility": "current",
        "layers": [
            {
                "id": "runtime",
                "layer_type": "full-repo-runtime",
                "installed_path": ".loom/bin",
                "version_context": {
                    "repo_version": "v0.13.0",
                    "runtime_core_version": "1.0.0",
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["loom runtime wrappers"],
                "consumes": [],
            },
            {
                "id": "skills",
                "layer_type": "generated-skills",
                "installed_path": "skills",
                "version_context": {
                    "skills_registry_version": "1.7.0",
                    "skill_package_version": "1.0.0",
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["scenario skills"],
                "consumes": ["runtime"],
            },
        ],
        "installation_graph": {
            "layers": ["runtime", "skills"],
            "edges": [{"from": "skills", "to": "runtime", "relationship": "consumes"}],
        },
    }


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
        package_root = REPO_ROOT / "skills" / skill_id
        runtime_root = package_root / ".loom-runtime"
        for relative in ("registry.json", "install-layout.json", "route-matrix.md"):
            source = REPO_ROOT / "src" / "skills" / relative
            runtime = runtime_root / relative
            if not runtime.is_file():
                raise AssertionError(f"{skill_id} package runtime missing {relative}")
            if source.read_bytes() != runtime.read_bytes():
                raise AssertionError(f"{skill_id} package runtime drifted for {relative}")


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
                "reviewed_head": head_sha,
                "reviewed_validation_summary": validation_summary,
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


def assert_governance_chain_closeout_fixture(tmp: Path) -> None:
    pass_target = tmp / "governance-chain-pass"
    pass_target.mkdir()
    fixture = write_governance_chain_fixture(pass_target)
    command = [
        "closeout",
        "check",
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


def main() -> int:
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
        "reconcile",
        "host list",
        "host doctor",
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
        "gate closeout",
    ):
        if matrix[command]["status"] != "implemented":
            raise AssertionError(f"{command} must be implemented for #890/#891")
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

    _, version_payload = run_json(["version", "--json"], expect=0)
    if version_payload["result"] != "pass" or not version_payload["versions"]["repo_version"]:
        raise AssertionError("version output did not include repo version context")

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
        if exported["installation_graph"]["layers"] != ["runtime", "skills"]:
            raise AssertionError("installed-state export did not include graph")
        _, upgrade_plan = run_json(["upgrade-plan", "--target", str(valid_target), "--json"], expect=0)
        if upgrade_plan["schema"] != "loom-delivery-control/v1" or not upgrade_plan["actions"]:
            raise AssertionError("upgrade-plan did not emit delivery control actions")
        _, verify_payload = run_json(["verify", "--target", str(valid_target), "--json"], expect=0)
        if verify_payload["schema"] != "loom-delivery-control/v1" or verify_payload["doctor"]["result"] != "pass":
            raise AssertionError("verify did not consume doctor success")
        if verify_payload.get("suite_validation") is not None or verify_payload.get("suite_validation_requirement", {}).get("required") is not False:
            raise AssertionError("verify should not require suite validation without profile or Work Item demand")
        declared_target = tmp / "declared-suite-support"
        declared_target.mkdir()
        declared_state = valid_state(declared_target)
        declared_state["declared_support"] = {"suite_commands": ["suite inspect", "suite validate", "suite evidence validate", "suite carrier validate"]}
        write_state(declared_target, declared_state)
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
        if hosts["schema"] != "loom-host-orchestration/v1" or not any(host["id"] == "codex" for host in hosts["hosts"]):
            raise AssertionError("host list did not emit supported host adapter inventory")
        _, host_doctor = run_json(["host", "doctor", "--host", "codex", "--target", str(valid_target), "--json"], expect=0)
        if host_doctor["host"] != "codex" or host_doctor["mode"] != "plugin":
            raise AssertionError("host doctor did not freeze host/mode output")
        status, host_install = run_json(["host", "install", "--host", "codex", "--target", str(valid_target), "--json"])
        if status == 0 or host_install["result"] != "block" or host_install["failed_layer"] != "host-install":
            raise AssertionError("host install did not fail closed without --apply")
        managed_target = tmp / "managed-host"
        managed_target.mkdir()
        _, managed_install = run_json(["host", "install", "--host", "codex", "--target", str(managed_target), "--apply", "--json"], expect=0)
        managed_writes = set(managed_install.get("managed_writes", []))
        for expected_write in ("skills", "plugins/loom/.codex-plugin/plugin.json", "plugins/loom/skills", ".loom/installed-state.json"):
            if expected_write not in managed_writes:
                raise AssertionError(f"host install did not write {expected_write}")
        _, managed_verify = run_json(["host", "verify", "--host", "codex", "--target", str(managed_target), "--json"], expect=0)
        if managed_verify["result"] != "pass" or any(check["status"] != "pass" for check in managed_verify["checks"]):
            raise AssertionError("host verify did not validate CLI-managed plugin/SKILLS payload")
        _, managed_skills = run_json(["skills", "check", "--target", str(managed_target), "--json"], expect=0)
        if managed_skills["result"] != "pass":
            raise AssertionError("skills check did not validate CLI-managed target payload")
        _, managed_detect = run_json(["detect", "--target", str(managed_target), "--json"], expect=0)
        if managed_detect["classification"] != "current":
            raise AssertionError("CLI-managed host install was not classified as current")
        _, skills_list = run_json(["skills", "list", "--json"], expect=0)
        if skills_list["schema"] != "loom-skills-surface/v1" or skills_list["root_entry"] != "loom-init":
            raise AssertionError("skills list did not expose generated skills registry")
        status, skills_generate = run_json(["skills", "generate", "--json"])
        if status == 0 or skills_generate["failed_layer"] != "skills-surface":
            raise AssertionError("skills generate did not fail closed without --apply")
        _, skills_check = run_json(["skills", "check", "--target", str(REPO_ROOT), "--json"], expect=0)
        assert_generated_skills_surface_parity_contract(skills_check)
        _, skills_package = run_json(["skills", "package", "--json"], expect=0)
        if not skills_package["packages"]:
            raise AssertionError("skills package did not emit package metadata")
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
        if route_payload["command"] != "route" or route_payload["selected_skill"] != "loom-adopt":
            raise AssertionError("route did not expose CLI-first scenario routing")
        _, status_payload = run_json(["status", "--target", str(REPO_ROOT), "--json"])
        if status_payload["command"] != "status" or status_payload.get("result") not in {"pass", "block", "fallback"}:
            raise AssertionError("status wrapper did not emit structured status JSON")
        missing_status_target = tmp / "missing-status"
        missing_status_target.mkdir()
        status, missing_status = run_json(["status", "--target", str(missing_status_target), "--json"])
        if status == 0 or missing_status["result"] != "block" or not missing_status.get("blocking_failures"):
            raise AssertionError("status missing-carrier fixture did not fail closed")
        _, fact_chain_payload = run_json(["fact-chain", "--target", str(REPO_ROOT), "--json"], expect=0)
        if fact_chain_payload["command"] != "fact-chain" or fact_chain_payload.get("result") != "pass":
            raise AssertionError("fact-chain wrapper did not consume loom_flow fact-chain JSON")
        _, profile_status = run_json(["profile", "status", "--target", str(REPO_ROOT), "--json"], expect=0)
        if profile_status["command"] != "profile status" or profile_status.get("wrapped_command") != "governance-profile":
            raise AssertionError("profile status did not wrap governance-profile status")
        _, profile_plan = run_json(["profile", "upgrade-plan", "--target", str(REPO_ROOT), "--json"])
        if profile_plan["command"] != "profile upgrade-plan" or profile_plan.get("wrapped_command") != "governance-profile":
            raise AssertionError("profile upgrade-plan did not wrap governance-profile upgrade-plan")
        _, profile_upgrade = run_json(["profile", "upgrade", "--target", str(REPO_ROOT), "--to", "standard", "--json"])
        if profile_upgrade["command"] != "profile upgrade" or profile_upgrade.get("wrapped_command") != "governance-profile":
            raise AssertionError("profile upgrade did not wrap governance-profile upgrade")
        _, adoption_verify = run_json(["adopt", "verify", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        if adoption_verify["command"] != "adopt" or adoption_verify.get("schema_version") != "loom-adoption-verify/v1":
            raise AssertionError("adopt verify did not expose adoption verification JSON")
        _, story_payload = run_json(["story", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"], expect=0)
        if story_payload["command"] != "story" or story_payload.get("wrapped_command") != "flow":
            raise AssertionError("story did not wrap the flow runtime")
        for command_name in ("spec", "plan"):
            status, scenario_payload = run_json([command_name, "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
            if status == 0 or scenario_payload["schema"] != "loom-scenario-control/v1" or not scenario_payload.get("fallback_to"):
                raise AssertionError(f"{command_name} did not fail closed with a structured locator payload")
        status, build_payload = run_json(["build", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        if build_payload["command"] != "build" or build_payload.get("wrapped_command") != "flow":
            raise AssertionError("build did not wrap the flow runtime")
        status, pre_review_payload = run_json(["pre-review", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        if pre_review_payload["command"] != "pre-review" or pre_review_payload.get("wrapped_command") != "flow":
            raise AssertionError("pre-review did not wrap the flow runtime")
        active_item = active_work_item_id()
        status, active_build = run_json_preserving_attempts(
            ["build", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        assert_suite_build_consumption(active_build)
        assert_review_record_consumed_locators(active_item)
        _, active_pre_review = run_json_preserving_attempts(
            ["pre-review", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        assert_suite_gate_consumption(active_pre_review, expected_surface="pre_review")
        _, active_review_gate = run_json_preserving_attempts(
            ["gate", "review", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        assert_suite_gate_consumption(active_review_gate, expected_surface="review")
        _, active_merge_ready = run_json_preserving_attempts(
            ["merge-ready", "--target", str(REPO_ROOT), "--item", active_item, "--json"],
            item=active_item,
        )
        assert_suite_gate_consumption(active_merge_ready, expected_surface="merge_ready")
        status, handoff_payload = run_json(["handoff", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        if handoff_payload["command"] != "handoff" or handoff_payload.get("wrapped_command") != "flow":
            raise AssertionError("handoff did not wrap the flow runtime")
        status, retire_payload = run_json(["retire", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        if retire_payload["command"] != "retire" or not retire_payload.get("retire_contract"):
            raise AssertionError("retire did not expose structured non-mutating contract")
        _, closeout_payload = run_json(["closeout", "--target", str(REPO_ROOT), "--json"], expect=0)
        if closeout_payload["command"] != "closeout" or closeout_payload.get("schema_version") != "loom-scenario-control/v1":
            raise AssertionError("closeout did not wrap the closeout check runtime")
        assert_suite_gate_consumption(closeout_payload, expected_surface="closeout")
        assert_closeout_blocks_missing_suite_evidence(active_item)
        assert_reconciliation_suite_taxonomy_contract()
        assert_governance_chain_closeout_fixture(tmp)
        _, checkpoint_admission = run_json(["checkpoint", "admission", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        if checkpoint_admission["command"] != "checkpoint admission" or checkpoint_admission.get("checkpoint") != "admission":
            raise AssertionError("checkpoint admission did not wrap checkpoint JSON")
        _, checkpoint_build = run_json(["checkpoint", "build", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        if checkpoint_build["command"] != "checkpoint build" or checkpoint_build.get("checkpoint") != "build":
            raise AssertionError("checkpoint build did not wrap checkpoint JSON")
        _, checkpoint_merge = run_json(["checkpoint", "merge", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"])
        if checkpoint_merge["command"] != "checkpoint merge" or checkpoint_merge.get("checkpoint") != "merge":
            raise AssertionError("checkpoint merge did not wrap checkpoint JSON")
        for gate_command in (
            ["gate", "pr", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"],
            ["gate", "merge", "--target", str(REPO_ROOT), "--item", "WI-915", "--json"],
            ["gate", "closeout", "--json"],
        ):
            status, gate_payload = run_json(gate_command)
            if status == 0 or gate_payload["result"] not in {"block", "fallback"} or not gate_payload.get("fallback_to"):
                raise AssertionError(f"{gate_command} did not fail closed with structured JSON")

        mixed_target = tmp / "mixed"
        mixed_target.mkdir()
        bad_state = valid_state(mixed_target)
        bad_state["layers"][1]["version_context"]["skill_package_version"] = "unknown"
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

    print("cli contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
