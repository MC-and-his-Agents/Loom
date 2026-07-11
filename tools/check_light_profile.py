#!/usr/bin/env python3
"""Targeted contract checks for light-profile migration and reconciliation."""

from __future__ import annotations

import base64
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "light_profile.py"
FIXTURES = ROOT / "tools" / "fixtures" / "light-profile" / "fixtures.json"
LOOM = ROOT / "tools" / "loom.py"


def load_module() -> Any:
    sys.path.insert(0, str(SOURCE.parent))
    spec = importlib.util.spec_from_file_location("light_profile", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("light-profile evaluator is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_paginated_host_readback() -> None:
    import github_host

    pages = [
        {"check_runs": [{"id": value} for value in range(100)]},
        {"check_runs": [{"id": 100}]},
    ]
    original_token = github_host.host_api_env_token_present
    original_run = github_host.run_process
    github_host.host_api_env_token_present = lambda: True
    github_host.run_process = lambda *_args, **_kwargs: subprocess.CompletedProcess(
        args=["gh"], returncode=0, stdout=json.dumps(pages), stderr=""
    )
    try:
        rows, errors = github_host.gh_rest_authenticated_paginated_field(
            ROOT, "repos/owner/repo/commits/head/check-runs?per_page=100", "check_runs"
        )
        if errors or [row.get("id") for row in rows] != list(range(101)):
            raise AssertionError(f"paginated check-runs readback lost later pages: {rows} / {errors}")
    finally:
        github_host.host_api_env_token_present = original_token
        github_host.run_process = original_run


def assert_reconciliation(evaluator: Any, root: Path) -> None:
    target = root / "reconcile"
    target.mkdir()
    state: dict[str, Any] = {}
    installed = {
        "schema_version": "loom-installed-state/v2",
        "repo_payload": {"mode": "metadata-only", "adoption_mode": "light-governance"},
    }
    companion = {
        "schema_version": "loom-repo-interface/v2",
        "repo_specific_requirements": {"review": [], "merge_ready": [], "closeout": []},
        "specialized_gates": [],
    }
    workflow = (
        "name: loom-delivery-gate\n"
        "on: [pull_request, merge_group]\n"
        "jobs:\n"
        "  gate:\n"
        "    uses: MC-and-his-Agents/Loom/.github/workflows/loom-delivery-gate.yml@"
        + "a" * 40
        + "\n"
    )

    def reset(checks: list[dict[str, Any]], write_modes: list[str] | None = None) -> None:
        state.clear()
        state.update(
            checks=list(checks),
            write_modes=list(write_modes or []),
            mutation_calls=[],
            readback_error=False,
            invalid_companion=False,
            noop_workflow=False,
            workflow_sha="workflow-blob",
        )

    def fake_json(_root: Path, path: str) -> tuple[dict[str, Any] | None, list[str]]:
        if path.endswith("/pulls/10"):
            return {"merged_at": "2026-01-01T00:00:00Z", "merge_commit_sha": "gate-merge", "base": {"ref": "main"}, "head": {"sha": "gate-head"}}, []
        if "git/trees/gate-merge" in path:
            return {"truncated": False, "tree": [{"type": "blob", "path": ".github/workflows/loom-delivery-gate.yml", "sha": "workflow-blob"}]}, []
        if path.endswith("/protection"):
            if state["readback_error"]:
                state["readback_error"] = False
                return None, ["simulated readback timeout"]
            return {"required_status_checks": {"strict": True, "checks": list(state["checks"])}}, []
        if path.endswith("/pulls/11"):
            return {"merged_at": "2026-01-02T00:00:00Z", "base": {"ref": "main"}, "head": {"sha": "migration-head"}}, []
        if path.endswith("/branches/main"):
            return {"commit": {"sha": "main-head"}}, []
        if "git/trees/main-head" in path:
            return {
                "truncated": False,
                "tree": [
                    {"type": "blob", "path": ".loom/installed-state.json"},
                    {"type": "blob", "path": ".loom/companion/repo-interface.json", "sha": "companion-blob"},
                    {"type": "blob", "path": ".github/workflows/loom-delivery-gate.yml", "sha": state["workflow_sha"]},
                ],
            }, []
        if "/contents/.loom/installed-state.json" in path:
            encoded = base64.b64encode(json.dumps(installed).encode()).decode()
            return {"content": encoded}, []
        if "/contents/.loom/companion/repo-interface.json" in path:
            value: object = {} if state["invalid_companion"] else companion
            return {"content": base64.b64encode(json.dumps(value).encode()).decode()}, []
        if "/contents/.github/workflows/loom-delivery-gate.yml" in path:
            value = "name: no-op\n" if state["noop_workflow"] else workflow
            return {"content": base64.b64encode(value.encode()).decode()}, []
        return None, [f"unexpected fake JSON endpoint: {path}"]

    def fake_list(_root: Path, path: str) -> tuple[list[dict[str, Any]], list[str]]:
        if "/rules/branches/main" in path:
            return [], []
        return [], [f"unexpected fake list endpoint: {path}"]

    def fake_paginated(_root: Path, path: str, field: str) -> tuple[list[dict[str, Any]], list[str]]:
        if "commits/gate-head/check-runs" not in path or field != "check_runs":
            return [], [f"unexpected paginated endpoint: {path}#{field}"]
        noise = [{"name": f"noise-{index}", "conclusion": "success", "app": {"id": 1}} for index in range(100)]
        return [*noise, {"name": "loom-delivery-gate", "conclusion": "success", "app": {"id": 15368}}], []

    def fake_write(
        _root: Path, *, method: str, path: str, request_payload: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, list[str]]:
        if method != "PATCH" or not path.endswith("/protection/required_status_checks"):
            return None, ["unexpected write"]
        mode = state["write_modes"].pop(0) if state["write_modes"] else "success"
        state["mutation_calls"].append({"mode": mode, "payload": request_payload})
        if mode in {"success", "apply_timeout", "indeterminate_timeout"}:
            state["checks"] = list(request_payload["checks"])
        if mode == "indeterminate_timeout":
            state["readback_error"] = True
        if mode.endswith("timeout"):
            return None, [f"simulated {mode}"]
        return {"checks": state["checks"]}, []

    original = (
        evaluator.gh_rest_authenticated_json,
        evaluator.gh_rest_authenticated_list,
        evaluator.gh_rest_authenticated_paginated_field,
        evaluator.gh_rest_write_json,
    )
    evaluator.gh_rest_authenticated_json = fake_json
    evaluator.gh_rest_authenticated_list = fake_list
    evaluator.gh_rest_authenticated_paginated_field = fake_paginated
    evaluator.gh_rest_write_json = fake_write
    args = {
        "repository": "owner/repo",
        "branch": "main",
        "work_item": 2040,
        "gate_pr": 10,
        "migration_pr": 11,
        "context": "loom-delivery-gate",
        "app_id": 15368,
        "legacy_contexts": ["legacy-check"],
        "retained_contexts": [],
    }
    try:
        reset([{"context": "legacy-check", "app_id": 1}])
        dry_run = evaluator.reconcile_payload(target, apply=False, **args)
        if dry_run.get("result") != "pass" or dry_run.get("migration", {}).get("status") != "planned" or state["mutation_calls"]:
            raise AssertionError(f"reconcile dry-run must be non-mutating and actionable: {dry_run}")

        reset([{"context": "legacy-check", "app_id": 1}], ["success", "unchanged_timeout"])
        partial = evaluator.reconcile_payload(target, apply=True, **args)
        if partial.get("result") != "partial_apply" or len(partial.get("host_writes", [])) != 1:
            raise AssertionError(f"partial host success must return partial_apply: {partial}")
        if "--work-item 2040" not in str(partial.get("next_action")):
            raise AssertionError(f"partial_apply recovery must reuse the Work Item: {partial}")

        reset([{"context": "legacy-check", "app_id": 1}], ["apply_timeout", "success"])
        reconciled = evaluator.reconcile_payload(target, apply=True, **args)
        if reconciled.get("result") != "pass" or reconciled.get("host_mutation_attempts", [])[0].get("outcome") != "applied":
            raise AssertionError(f"timeout followed by applied readback must converge: {reconciled}")
        repeated = evaluator.reconcile_payload(target, apply=True, **args)
        if repeated.get("result") != "pass":
            raise AssertionError(f"reconcile apply must converge: {reconciled} / {repeated}")
        if repeated.get("host_writes") != [] or repeated.get("main_tree", {}).get("commit") != "main-head":
            raise AssertionError(f"repeated reconcile must be a read-only host readback: {repeated}")

        reset([{"context": "legacy-check", "app_id": 1}], ["unchanged_timeout"])
        unchanged = evaluator.reconcile_payload(target, apply=True, **args)
        if unchanged.get("primary_cause", {}).get("id") != "host_write_unchanged" or unchanged.get("mutates") is not False or unchanged.get("host_mutation_attempts", [])[0].get("outcome") != "unchanged":
            raise AssertionError(f"unchanged timeout must be classified from readback: {unchanged}")

        reset([{"context": "legacy-check", "app_id": 1}], ["indeterminate_timeout"])
        indeterminate = evaluator.reconcile_payload(target, apply=True, **args)
        if indeterminate.get("result") != "partial_apply" or indeterminate.get("mutates") is not True or not indeterminate.get("host_writes") or indeterminate.get("host_mutation_attempts", [])[0].get("outcome") != "indeterminate":
            raise AssertionError(f"indeterminate timeout must preserve uncertain mutation truth: {indeterminate}")

        reset([{"context": "loom-delivery-gate", "app_id": 15368}, {"context": "loom-delivery-gate", "app_id": 9}])
        conflict = evaluator.reconcile_payload(target, apply=False, **args)
        if conflict.get("primary_cause", {}).get("id") != "required_check_app_conflict":
            raise AssertionError(f"same-context conflicting app identity must block: {conflict}")

        reset([{"context": "loom-delivery-gate", "app_id": 15368}])
        state["invalid_companion"] = True
        invalid_companion = evaluator.reconcile_payload(target, apply=True, **args)
        if invalid_companion.get("primary_cause", {}).get("id") != "main_tree_unreconciled" or "companion" not in " ".join(invalid_companion.get("missing_inputs", [])):
            raise AssertionError(f"invalid companion must block main-tree reconciliation: {invalid_companion}")

        reset([{"context": "loom-delivery-gate", "app_id": 15368}])
        state["noop_workflow"] = True
        noop_workflow = evaluator.reconcile_payload(target, apply=True, **args)
        if noop_workflow.get("primary_cause", {}).get("id") != "main_tree_unreconciled" or "workflow" not in " ".join(noop_workflow.get("missing_inputs", [])):
            raise AssertionError(f"no-op workflow must block main-tree reconciliation: {noop_workflow}")

        reset([{"context": "loom-delivery-gate", "app_id": 15368}])
        state["workflow_sha"] = "drifted-workflow-blob"
        workflow_drift = evaluator.reconcile_payload(target, apply=True, **args)
        if workflow_drift.get("primary_cause", {}).get("id") != "main_tree_unreconciled" or "blob" not in " ".join(workflow_drift.get("missing_inputs", [])):
            raise AssertionError(f"workflow drift from gate-enabler identity must block: {workflow_drift}")
    finally:
        (
            evaluator.gh_rest_authenticated_json,
            evaluator.gh_rest_authenticated_list,
            evaluator.gh_rest_authenticated_paginated_field,
            evaluator.gh_rest_write_json,
        ) = original


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def commit_all(target: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def materialize_case(root: Path, fixture: dict[str, Any]) -> Path:
    target = root / str(fixture["id"])
    target.mkdir()
    subprocess.run(["git", "init"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=target, check=True)
    if not fixture.get("without_installed_state"):
        state = {
            "schema_version": "loom-installed-state/v2",
            "repo_payload": {
                "mode": "metadata-only",
                "adoption_mode": fixture["adoption_mode"],
            },
            "contract": {"minimum_loom_version": "v0.29.0"},
        }
        state["repo_payload"].update(fixture.get("repo_payload_extra", {}))
        state.update(fixture.get("installed_state_extra", {}))
        write_json(target / ".loom" / "installed-state.json", state)
    for relative, content in fixture.get("tracked_files", {}).items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if fixture.get("ignored_files"):
        (target / ".gitignore").write_text(".loom/tmp/\n", encoding="utf-8")
    commit_all(target)
    for collection_name in ("untracked_files", "ignored_files"):
        for relative, content in fixture.get(collection_name, {}).items():
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return target


def assert_case(evaluator: Any, root: Path, fixture: dict[str, Any]) -> None:
    target = materialize_case(root, fixture)
    status_before = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=target, check=True, text=True, stdout=subprocess.PIPE).stdout
    first = evaluator.plan_payload(target)
    second = evaluator.plan_payload(target)
    status_after = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=target, check=True, text=True, stdout=subprocess.PIPE).stdout
    if status_before != status_after:
        raise AssertionError(f"{fixture['id']} plan wrote to the target")
    if first != second:
        raise AssertionError(f"{fixture['id']} plan is not reentrant")
    expected = fixture["expected"]
    cause = first.get("primary_cause", {})
    if first.get("result") != expected["result"] or cause.get("id") != expected["primary_cause"]:
        raise AssertionError(f"{fixture['id']} result drifted: {first}")
    if bool(first.get("legacy_gate_blocker")) != expected["legacy_gate_blocker"]:
        raise AssertionError(f"{fixture['id']} legacy blocker drifted: {first}")
    if len(first.get("violations", [])) != expected["violation_count"]:
        raise AssertionError(f"{fixture['id']} violation count drifted: {first}")
    if first.get("mutates") is not False or first.get("host_mutations") is not False or first.get("carrier_repair_actions") != []:
        raise AssertionError(f"{fixture['id']} plan is not read-only: {first}")
    for action in first.get("migration", {}).get("actions", []):
        if action.get("mutates") is not False or "repair" in str(action.get("id", "")) or "closeout" in str(action.get("id", "")):
            raise AssertionError(f"{fixture['id']} proposed a forbidden remediation: {action}")

    if fixture["id"] == "heavy-tree":
        paths = {entry.get("locator") for entry in first.get("violations", [])}
        expected_files = {
            path
            for path in fixture["tracked_files"]
            if evaluator.forbidden_kind(path) is not None
        }
        if not expected_files.issubset(paths) or not any(":initial_artifacts:.loom/status/current.md" in str(path) for path in paths):
            raise AssertionError(f"heavy-tree fixture missed forbidden paths: {paths}")
        action_ids = [action.get("id") for action in first.get("migration", {}).get("actions", [])]
        if action_ids != ["gate_enabler_pr", "required_set_host_readback", "profile_migration_pr"]:
            raise AssertionError(f"heavy-tree migration order drifted: {action_ids}")
        actions = first["migration"]["actions"]
        if actions[1].get("atomic") is not False or actions[2].get("post_merge_readback", [])[0].get("authority") != "GitHub main tree":
            raise AssertionError(f"heavy-tree migration host-readback contract drifted: {actions}")
        completed = subprocess.run(
            [sys.executable, str(LOOM), "profile", "light-migration-plan", "--target", str(target), "--json", "--full-output"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout or completed.stderr)
        if completed.returncode == 0 or payload.get("command") != "profile light-migration-plan" or payload.get("primary_cause", {}).get("id") != "light_profile_forbidden_carrier":
            raise AssertionError(f"CLI route did not preserve light-profile failure semantics: {payload}")


def main() -> int:
    catalog = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != "loom-light-profile-fixtures/v1":
        raise AssertionError("light-profile fixture schema drifted")
    fixtures = catalog.get("cases")
    if not isinstance(fixtures, list) or {item.get("id") for item in fixtures if isinstance(item, dict)} != {
        "heavy-tree",
        "absolute-workspace-entry",
        "absolute-private-workspace-entry",
        "absolute-windows-workspace-entry",
        "clean-light",
        "attach-only-forbidden-carrier",
        "old-branch-reintroduction",
        "untracked-and-ignored",
        "legacy-missing-state",
        "light-nonmetadata-state",
        "non-light",
    }:
        raise AssertionError("light-profile fixture catalog is incomplete")
    evaluator = load_module()
    assert_paginated_host_readback()
    copies = [
        ROOT / "skills" / "shared" / "scripts" / "light_profile.py",
        ROOT / "plugins" / "loom" / "skills" / "shared" / "scripts" / "light_profile.py",
    ]
    if any(not path.is_file() or path.read_bytes() != SOURCE.read_bytes() for path in copies):
        raise AssertionError("light-profile evaluator distribution copies drifted")
    if (ROOT / ".loom" / "bin" / "light_profile.py").exists():
        raise AssertionError("light-profile evaluator must not become a repo-local runtime carrier")
    with tempfile.TemporaryDirectory(prefix="loom-light-profile-") as raw_tmp:
        for fixture in fixtures:
            assert_case(evaluator, Path(raw_tmp), fixture)
        assert_reconciliation(evaluator, Path(raw_tmp))
    print("light-profile migration contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
