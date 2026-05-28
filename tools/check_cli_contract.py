#!/usr/bin/env python3
"""Contract checks for the CLI-first Loom surface."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
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

        minimal_target = tmp / "suite-minimal"
        minimal_suite = minimal_target / ".loom" / "specs" / "WI-minimal"
        minimal_suite.mkdir(parents=True)
        (minimal_suite / "spec.md").write_text("# Spec\n\n- Suite path: minimal\n", encoding="utf-8")
        (minimal_suite / "plan.md").write_text("# Plan\n\nConsumes Suite path: minimal\n", encoding="utf-8")
        suite_minimal = run_suite_inspect_fixture(minimal_target, "WI-minimal")
        minimal_payload = suite_minimal.get("payload", {})
        minimal_inventory = {entry["artifact"]: entry for entry in minimal_payload.get("artifact_inventory", [])}
        if (
            minimal_payload.get("suite_path") != "minimal"
            or minimal_payload.get("path_decision_locator") != ".loom/specs/WI-minimal/spec.md"
            or minimal_payload.get("spec_locator") != ".loom/specs/WI-minimal/spec.md"
            or minimal_payload.get("plan_locator") != ".loom/specs/WI-minimal/plan.md"
            or minimal_inventory.get("spec.md", {}).get("locator") != ".loom/specs/WI-minimal/spec.md"
            or minimal_inventory.get("plan.md", {}).get("locator") != ".loom/specs/WI-minimal/plan.md"
            or minimal_payload.get("missing_inputs")
        ):
            raise AssertionError("suite inspect minimal locator payload drifted")

        not_applicable_target = tmp / "suite-not-applicable"
        not_applicable_suite = not_applicable_target / ".loom" / "specs" / "WI-not-applicable"
        not_applicable_suite.mkdir(parents=True)
        (not_applicable_suite / "spec.md").write_text("# Spec\n\n- Suite path: not applicable\n", encoding="utf-8")
        suite_not_applicable = run_suite_inspect_fixture(not_applicable_target, "WI-not-applicable")
        not_applicable_payload = suite_not_applicable.get("payload", {})
        if (
            not_applicable_payload.get("suite_path") != "not_applicable"
            or not_applicable_payload.get("path_decision_locator") != ".loom/specs/WI-not-applicable/spec.md"
            or not_applicable_payload.get("missing_inputs")
        ):
            raise AssertionError("suite inspect not_applicable payload drifted")

        full_target = tmp / "suite-full"
        full_suite = full_target / ".loom" / "specs" / "WI-full"
        full_suite.mkdir(parents=True)
        (full_suite / "suite-index.md").write_text(
            "# Full Suite Index\n\n- Schema marker: loom-full-suite-index/v1\n- Suite path: full\n",
            encoding="utf-8",
        )
        for name in (
            "spec.md",
            "plan.md",
            "evidence-map.md",
            "consistency-analysis.md",
            "execution-breakdown.md",
            "task-carrier.md",
        ):
            (full_suite / name).write_text(f"# {name}\n", encoding="utf-8")
        suite_full = run_suite_inspect_fixture(full_target, "WI-full")
        full_payload = suite_full.get("payload", {})
        full_inventory = {entry["artifact"]: entry for entry in full_payload.get("artifact_inventory", [])}
        expected_full_locators = {
            "suite-index.md": ".loom/specs/WI-full/suite-index.md",
            "spec.md": ".loom/specs/WI-full/spec.md",
            "plan.md": ".loom/specs/WI-full/plan.md",
            "evidence-map.md": ".loom/specs/WI-full/evidence-map.md",
            "consistency-analysis.md": ".loom/specs/WI-full/consistency-analysis.md",
            "execution-breakdown.md": ".loom/specs/WI-full/execution-breakdown.md",
            "task-carrier": ".loom/specs/WI-full/task-carrier.md",
        }
        if full_payload.get("suite_path") != "full" or full_payload.get("missing_inputs"):
            raise AssertionError("suite inspect full path decision drifted")
        for artifact, locator in expected_full_locators.items():
            if full_inventory.get(artifact, {}).get("locator") != locator:
                raise AssertionError(f"suite inspect full locator drifted for {artifact}")
            if full_inventory[artifact]["locator"].startswith("/"):
                raise AssertionError("suite inspect emitted absolute artifact locator")
        if full_payload.get("task_carrier_locators") != [".loom/specs/WI-full/task-carrier.md"]:
            raise AssertionError("suite inspect task carrier locators drifted")

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
        _, skills_package = run_json(["skills", "package", "--json"], expect=0)
        if not skills_package["packages"]:
            raise AssertionError("skills package did not emit package metadata")
        _, skills_release_check = run_json(["skills", "release-check", "--json"], expect=0)
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
        status, handoff_payload = run_json(["handoff", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        if handoff_payload["command"] != "handoff" or handoff_payload.get("wrapped_command") != "flow":
            raise AssertionError("handoff did not wrap the flow runtime")
        status, retire_payload = run_json(["retire", "--target", str(REPO_ROOT), "--item", "WI-924", "--json"])
        if retire_payload["command"] != "retire" or not retire_payload.get("retire_contract"):
            raise AssertionError("retire did not expose structured non-mutating contract")
        _, closeout_payload = run_json(["closeout", "--target", str(REPO_ROOT), "--json"], expect=0)
        if closeout_payload["command"] != "closeout" or closeout_payload.get("schema_version") != "loom-scenario-control/v1":
            raise AssertionError("closeout did not wrap the closeout check runtime")
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
