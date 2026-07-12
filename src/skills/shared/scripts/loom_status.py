#!/usr/bin/env python3
"""Unified Loom status read surface for item, spec/review gates, and merge readiness."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_surface import (
    build_governance_surface,
    derive_execution_budget_risk,
    empty_target_release_status,
    normalize_execution_budget_payload,
)
from loom_flow import (
    checkpoint_payload,
    closeout_payload,
    detect_github_repo,
    emit,
    fact_chain_error_contract,
    flow_governance_lint_status,
    goal_execution_contract,
    github_issue_payload,
    github_pr_payload,
    governance_lint_missing_inputs,
    implementation_review_status_payload,
    latest_execution_failure_payload,
    latest_execution_attempt_payload,
    latest_retry_evidence_payload,
    load_fact_chain_report,
    load_context,
    project_drift_payload,
    report_blocking_failures,
    report_blocking_messages,
    report_provenance,
    report_execution_ledger,
    report_recovery_readiness,
    runtime_state_payload,
    spec_review_gate_payload,
    validate_goal_execution_contract,
)
from flow_runtime import git_branch, git_head_sha
from loom_init import validate_host_derived_manifest
from authority_contract import parse_typed_locator
from delivery_control import (
    pr_body_field_value,
    pr_body_governance_metadata_fields,
    work_item_locator_for_metadata,
)

IDLE_ITEM_ID = "no_active_item"


def host_derived_manifest(target_root: Path) -> tuple[dict[str, object] | None, list[str]]:
    path = target_root / ".loom/bootstrap/manifest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, []
    except OSError as exc:
        return None, [f"bootstrap manifest is unreadable: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"bootstrap manifest is invalid JSON: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, ["bootstrap manifest must be a JSON object"]
    if payload.get("schema_version") == "loom-bootstrap-manifest/v1":
        return None, []
    if payload.get("schema_version") != "loom-bootstrap-manifest/v2":
        return None, ["bootstrap manifest schema is unsupported"]
    return payload, validate_host_derived_manifest(target_root, payload)


def host_derived_status_payload(
    target_root: Path,
    *,
    manifest: dict[str, object],
    runtime_state: dict[str, object],
    args: argparse.Namespace,
) -> dict[str, object]:
    github, github_errors = github_status_payload(
        target_root,
        issue_number=args.issue,
        pr_number=args.pr,
        owner=args.owner,
        repo_name=args.repo_name,
    )
    branch = git_branch(target_root)
    head = git_head_sha(target_root)
    missing_inputs = list(github_errors)
    parsed_item = parse_typed_locator(args.item, allowed_types={"work_item"}, allow_legacy=False) if args.item else None
    issue = github.get("issue") if isinstance(github.get("issue"), dict) else None
    pr = github.get("pr") if isinstance(github.get("pr"), dict) else None
    if args.item:
        if parsed_item is None:
            missing_inputs.append("explicit --item must be a canonical owner/repo/work_item/id locator")
        elif args.issue is None:
            missing_inputs.append("explicit --item requires matching --issue host readback")
        else:
            detected_owner, detected_repo = detect_github_repo(target_root)
            if (
                parsed_item.get("owner") != (args.owner or detected_owner)
                or parsed_item.get("repo") != (args.repo_name or detected_repo)
                or parsed_item.get("id") != args.issue
            ):
                missing_inputs.append("explicit --item authority does not match the requested GitHub issue")
            if issue is not None:
                type_labels = {
                    str(label).strip().lower().replace("_", "-")
                    for label in issue.get("labels", [])
                } & {"work-item", "fr", "phase"}
                if issue.get("number") != args.issue or type_labels != {"work-item"}:
                    missing_inputs.append("requested GitHub issue is not uniquely typed as the Work Item")
                if issue.get("state") != "OPEN":
                    missing_inputs.append("requested GitHub Work Item is not open")
            if args.pr is not None and pr is not None:
                body = pr.get("body")
                owner = str(parsed_item.get("owner"))
                repo = str(parsed_item.get("repo"))
                human_raw = pr_body_field_value(body, "Work Item")
                human_locator = work_item_locator_for_metadata(
                    human_raw, None, owner, repo
                )
                machine_fields = pr_body_governance_metadata_fields(body)
                machine_raw = machine_fields.get("work_item_locator")
                machine_locator = work_item_locator_for_metadata(
                    machine_raw if isinstance(machine_raw, str) else None,
                    None,
                    owner,
                    repo,
                )
                if human_raw is not None and human_locator is None:
                    missing_inputs.append("requested PR human Work Item locator is invalid or belongs to another repository")
                if machine_raw is not None and machine_locator is None:
                    missing_inputs.append("requested PR machine Work Item locator is invalid or belongs to another repository")
                declared_locators = [locator for locator in (human_locator, machine_locator) if locator is not None]
                if not declared_locators or any(locator != args.item for locator in declared_locators):
                    missing_inputs.append("requested PR metadata is not bound to the canonical Work Item locator")
    github_readback_consumed = bool(args.item and parsed_item and issue is not None and not missing_inputs)
    return {
        "command": "status",
        "result": "block" if missing_inputs else "pass",
        "summary": (
            "status was derived from the current Git worktree and requested GitHub host readback."
            if github_readback_consumed and not missing_inputs
            else "status was derived from the current Git worktree; no active host item was requested."
            if not missing_inputs
            else "host-derived status is readable, but requested GitHub facts could not be read."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": "host-readback" if missing_inputs else None,
        "runtime_state": runtime_state,
        "profile": manifest.get("profile"),
        "item": {
            "id": args.item or IDLE_ITEM_ID,
            "source": "github_host_readback" if args.item and github_readback_consumed else "no_active_item" if not args.item else "unresolved",
        },
        "worktree": {
            "repository_locator": ".",
            "branch": branch,
            "head_sha": head,
            "workspace_entry": ".",
            "source": "git_worktree_readback",
        },
        "workstation": {
            "status": "not_read",
            "source": None,
            "committed_state_consumed": False,
        },
        "github": github,
        "provenance": [
            {
                "kind": "derived_observation",
                "authority": "git_and_github_readback" if github_readback_consumed else "git_worktree_readback",
                "freshness": "current_invocation",
                "locator": ".loom/bootstrap/manifest.json",
            }
        ],
        "committed_execution_state": {
            "current_status_consumed": False,
            "shadow_consumed": False,
            "init_snapshot_consumed": False,
        },
    }


def resolve_target_arg(raw_target: str) -> Path:
    target = Path(raw_target).expanduser()
    if target.is_absolute():
        return target.resolve()
    invocation_cwd = os.environ.get("LOOM_INVOCATION_CWD")
    base = Path(invocation_cwd).expanduser() if invocation_cwd else Path.cwd()
    return (base / target).resolve()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read unified Loom item/spec/review/merge status.")
    parser.add_argument("--target", required=True, help="Target repository root")
    parser.add_argument("--item", help="Expected current item id")
    parser.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    parser.add_argument("--issue", type=int, help="Optional GitHub issue number to include")
    parser.add_argument("--pr", type=int, help="Optional GitHub pull request number to include")
    parser.add_argument("--project", type=int, help="Optional GitHub project number to include in closeout")
    parser.add_argument("--phase", type=int, help="Optional GitHub phase issue number to include in closeout")
    parser.add_argument("--fr", type=int, help="Optional GitHub FR issue number to include in closeout")
    parser.add_argument("--branch", help="Optional implementation branch name to include in closeout")
    parser.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    parser.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    return parser.parse_args(argv)


def github_status_payload(
    root: Path,
    *,
    issue_number: int | None,
    pr_number: int | None,
    owner: str | None,
    repo_name: str | None,
) -> tuple[dict[str, object], list[str]]:
    detected_owner, detected_repo = detect_github_repo(root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    payload: dict[str, object] = {
        "repository": f"{owner}/{repo_name}" if owner and repo_name else None,
        "issue": None,
        "pr": None,
    }
    errors: list[str] = []
    if not owner or not repo_name:
        if issue_number is not None or pr_number is not None:
            errors.append("GitHub repository could not be detected from origin")
        return payload, errors

    if issue_number is not None:
        issue_payload, issue_errors = github_issue_payload(root, owner, repo_name, issue_number)
        if issue_errors:
            errors.extend([f"issue #{issue_number}: {message}" for message in issue_errors])
        else:
            payload["issue"] = issue_payload
    if pr_number is not None:
        pr_payload, pr_errors = github_pr_payload(root, owner, repo_name, pr_number)
        if pr_errors:
            errors.extend([f"pr #{pr_number}: {message}" for message in pr_errors])
        else:
            payload["pr"] = pr_payload
    return payload, errors


def gate_status(name: str, payload: dict[str, object] | None, *, required: bool = True) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {
            "name": name,
            "result": "block" if required else "not_applicable",
            "classification": "gate_failure" if required else None,
            "missing_inputs": [name] if required else [],
        }
    result = payload.get("result")
    missing_inputs = payload.get("missing_inputs")
    missing = missing_inputs if isinstance(missing_inputs, list) else []
    classification = None
    if result in {"block", "fallback"}:
        classification = "gate_failure"
        if any("head" in str(message).lower() for message in missing):
            classification = "head_drift"
        elif any("stale" in str(message).lower() for message in missing):
            classification = "review_stale" if name != "spec_gate" else "spec_stale"
    return {
        "name": name,
        "result": result if isinstance(result, str) else "block",
        "classification": classification,
        "missing_inputs": missing,
        "fallback_to": payload.get("fallback_to"),
    }


def governance_control_status(
    *,
    governance_surface: dict[str, object],
    governance_lint: dict[str, object],
    spec_review: dict[str, object],
    review: dict[str, object],
    merge_ready: dict[str, object],
    github_status: dict[str, object],
    github_errors: list[str],
) -> dict[str, object]:
    control_plane = governance_surface.get("governance_control_plane")
    if not isinstance(control_plane, dict):
        return {
            "schema_version": "loom-governance-status/v2",
            "result": "block",
            "current_gate": "status_surface",
            "classifications": ["gate_failure"],
            "missing_inputs": ["governance_control_plane"],
        }

    gates = [
        {
            "name": "work_item_admission",
            "result": "pass",
            "classification": None,
            "missing_inputs": [],
            "fallback_to": "admission",
        },
        gate_status("spec_gate", spec_review),
        gate_status("build_gate", merge_ready),
        gate_status("review_gate", review),
        gate_status("merge_gate", merge_ready),
        gate_status("github_controlled_merge", None, required=False),
    ]
    if github_errors:
        gates[-1] = {
            "name": "github_controlled_merge",
            "result": "block",
            "classification": "host_signal_drift",
            "missing_inputs": github_errors,
            "fallback_to": "merge",
        }
    host_binding = control_plane.get("host_binding")
    if isinstance(host_binding, dict) and host_binding.get("result") == "block":
        existing_missing = gates[-1].get("missing_inputs", [])
        merged_missing = list(existing_missing) if isinstance(existing_missing, list) else []
        for message in host_binding.get("missing_inputs", []):
            if message not in merged_missing:
                merged_missing.append(message)
        gates[-1] = {
            "name": "github_controlled_merge",
            "result": "block",
            "classification": "host_signal_drift",
            "missing_inputs": merged_missing,
            "fallback_to": "merge",
        }

    blocking = [gate for gate in gates if gate.get("result") in {"block", "fallback"}]
    classifications = [
        str(gate["classification"])
        for gate in blocking
        if isinstance(gate.get("classification"), str)
    ]
    current_gate = blocking[0]["name"] if blocking else "closeout"
    missing_inputs: list[object] = []
    for gate in blocking:
        for message in gate.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    if governance_lint.get("result") == "block":
        if "governance_lint" not in classifications:
            classifications.append("governance_lint")
        for message in governance_lint_missing_inputs(governance_lint):
            if message not in missing_inputs:
                missing_inputs.append(message)
        if not blocking:
            current_gate = "governance_lint"
    governance_lint_blocking = governance_lint.get("result") == "block"
    pr_payload = github_status.get("pr") if isinstance(github_status, dict) else None
    head_binding = {
        "status": "present" if isinstance(pr_payload, dict) and pr_payload.get("headRefName") else "host-managed",
        "head_ref": pr_payload.get("headRefName") if isinstance(pr_payload, dict) else None,
        "base_ref": pr_payload.get("baseRefName") if isinstance(pr_payload, dict) else None,
    }
    return {
        "schema_version": "loom-governance-status/v2",
        "result": "pass" if not blocking and not governance_lint_blocking else "block",
        "current_gate": current_gate,
        "classifications": list(dict.fromkeys(classifications)),
        "missing_inputs": missing_inputs,
        "head_binding": head_binding,
        "gate_chain": gates,
        "maturity": control_plane.get("maturity"),
    }


def external_orchestrator_consumer_status(
    *,
    control_status: dict[str, object],
    provenance: dict[str, object],
    recovery_readiness: dict[str, object],
) -> dict[str, object]:
    gate_chain = control_status.get("gate_chain")
    if not isinstance(gate_chain, list):
        gate_chain = []
    external_gates = []
    for gate in gate_chain:
        if not isinstance(gate, dict):
            continue
        external_gates.append(
            {
                "name": gate.get("name"),
                "result": gate.get("result"),
                "classification": gate.get("classification"),
                "missing_inputs": gate.get("missing_inputs", []),
                "fallback_to": gate.get("fallback_to"),
            }
        )

    return {
        "schema_version": control_status.get("schema_version", "loom-governance-status/v2"),
        "view": "external_orchestrator_consumer",
        "result": control_status.get("result", "block"),
        "current_gate": control_status.get("current_gate"),
        "classifications": control_status.get("classifications", []),
        "missing_inputs": control_status.get("missing_inputs", []),
        "head_binding": control_status.get("head_binding", {}),
        "gate_chain": external_gates,
        "allowed_operations": ["status_read", "gate_read"],
        "source_policy": {
            "status_source": "derived_from_status_control_plane_v2",
            "gate_source": "derived_from_governance_gate_chain",
            "writeback": "recovery_entry_only",
            "fallback_to": "current_checkpoint",
        },
        "provenance": provenance,
        "recovery_readiness": recovery_readiness,
    }


def closeout_status_payload(
    *,
    github_status: dict[str, object],
    github_errors: list[str],
) -> dict[str, object]:
    issue = github_status.get("issue")
    pr = github_status.get("pr")
    if issue is None and pr is None and not github_errors:
        return {
            "result": "not_applicable",
            "summary": "closeout is not evaluated because no host issue or PR was requested.",
            "reconciliation": {
                "result": "not_applicable",
                "findings": [],
            },
            "missing_inputs": [],
            "fallback_to": None,
        }
    missing_inputs: list[str] = []
    findings: list[dict[str, object]] = []
    if github_errors:
        missing_inputs.extend(github_errors)
        findings.append(
            {
                "category": "drift",
                "kind": "host_signal_drift",
                "severity": "block",
                "subject": "github",
                "why_blocking": "GitHub host signals could not be read for closeout.",
                "fallback_to": "manual-reconciliation",
                "evidence": github_errors,
            }
        )
    if isinstance(pr, dict) and pr.get("state") != "MERGED":
        missing_inputs.append("pr is not merged")
        findings.append(
            {
                "category": "gate_failure",
                "kind": "missing_prerequisite_gate",
                "severity": "block",
                "subject": f"pr #{pr.get('number')}",
                "why_blocking": "closeout requires a merged implementation PR.",
                "fallback_to": "merge",
                "evidence": {"pr_state": pr.get("state")},
            }
        )
    if isinstance(issue, dict) and isinstance(pr, dict) and issue.get("state") == "OPEN" and pr.get("state") == "MERGED":
        missing_inputs.append("issue is absorbed but open")
        findings.append(
            {
                "category": "drift",
                "kind": "absorbed_but_open",
                "severity": "block",
                "subject": f"issue #{issue.get('number')}",
                "why_blocking": "merged implementation appears absorbed but the issue is still open.",
                "fallback_to": "reconciliation-sync",
                "evidence": {"issue_state": issue.get("state"), "pr_state": pr.get("state")},
            }
        )
    result = "pass" if not missing_inputs else "block"
    reconciliation_result = "pass" if result == "pass" else "fix-needed"
    return {
        "result": result,
        "summary": (
            "closeout host signals are consistent for the requested issue/PR."
            if result == "pass"
            else "closeout host signals require reconciliation before closeout can pass."
        ),
        "reconciliation": {
            "result": reconciliation_result,
            "findings": findings,
        },
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "reconciliation-sync",
    }


def repository_parts(github_status: dict[str, object], owner: str | None, repo_name: str | None) -> tuple[str | None, str | None]:
    if owner and repo_name:
        return owner, repo_name
    repository = github_status.get("repository")
    if isinstance(repository, str) and "/" in repository:
        detected_owner, detected_repo = repository.split("/", 1)
        return owner or detected_owner, repo_name or detected_repo
    return owner, repo_name


def full_closeout_status_payload(
    root: Path,
    *,
    phase_number: int | None,
    fr_number: int | None,
    issue_number: int | None,
    pr_number: int | None,
    project_number: int | None,
    branch_name: str | None,
    owner: str | None,
    repo_name: str | None,
    github_status: dict[str, object],
    github_errors: list[str],
) -> dict[str, object]:
    if (
        phase_number is None
        and fr_number is None
        and issue_number is None
        and pr_number is None
        and project_number is None
        and branch_name is None
    ):
        return closeout_status_payload(github_status=github_status, github_errors=github_errors)

    owner, repo_name = repository_parts(github_status, owner, repo_name)
    if not owner or not repo_name:
        return {
            "result": "block",
            "summary": "closeout is blocked because the GitHub repository could not be detected.",
            "reconciliation": {
                "result": "block",
                "findings": [
                    {
                        "category": "gate_failure",
                        "kind": "missing_repository",
                        "severity": "block",
                        "subject": "github repository",
                        "why_blocking": "closeout requires a readable GitHub repository binding.",
                        "fallback_to": "manual-reconciliation",
                        "evidence": github_errors,
                    }
                ],
            },
            "missing_inputs": ["github repository"],
            "fallback_to": "manual-reconciliation",
        }

    payload, errors = closeout_payload(
        target_root=root,
        expected_item=None,
        phase_number=phase_number,
        fr_number=fr_number,
        issue_number=issue_number,
        pr_number=pr_number,
        project_number=project_number,
        branch_name=branch_name,
        owner=owner,
        repo_name=repo_name,
        skip_gate=False,
    )
    if errors:
        return {
            "result": "block",
            "summary": "closeout is blocked because the closeout/reconciliation gate could not complete.",
            "reconciliation": {
                "result": "block",
                "findings": [
                    {
                        "category": "gate_failure",
                        "kind": "closeout_gate_unreadable",
                        "severity": "block",
                        "subject": "closeout",
                        "why_blocking": "status closeout must consume the same fail-closed closeout gate used by Loom flow.",
                        "fallback_to": "manual-reconciliation",
                        "evidence": errors,
                    }
                ],
            },
            "missing_inputs": errors,
            "fallback_to": "manual-reconciliation",
        }

    reconciliation = payload.get("reconciliation")
    if not isinstance(reconciliation, dict):
        reconciliation = {"result": "not_applicable", "findings": []}
    return {
        "result": payload.get("result", "block"),
        "summary": payload.get("summary", "closeout consumed the full closeout/reconciliation gate."),
        "reconciliation": reconciliation,
        "missing_inputs": payload.get("missing_inputs", []),
        "fallback_to": payload.get("fallback_to"),
        "gate": payload.get("gate"),
        "issue": payload.get("issue"),
        "pr": payload.get("pr"),
        "project": payload.get("project"),
        "repo_specific_requirements": payload.get("repo_specific_requirements"),
        "target_release": payload.get("target_release"),
        "findings": payload.get("findings"),
    }


def idle_status_payload(
    root: Path,
    *,
    report: dict[str, object],
    runtime_state: dict[str, object],
    requested_item: str | None,
) -> dict[str, object]:
    blocking_failures = report_blocking_failures(report)
    missing_inputs = report_blocking_messages(report)
    result = "block" if blocking_failures else "pass"
    if requested_item and requested_item != IDLE_ITEM_ID:
        result = "block"
        message = f"current item mismatch: expected `{requested_item}`, got `{IDLE_ITEM_ID}`"
        if message not in missing_inputs:
            missing_inputs.append(message)
    governance_surface = build_governance_surface(root)
    return {
        "command": "status",
        "result": result,
        "summary": (
            "repository is idle; no active Work Item is selected."
            if result == "pass"
            else "repository is idle, but the requested active item or idle status surface is not consumable."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": "admission" if result == "block" else None,
        "runtime_state": runtime_state,
        "provenance": report_provenance(report),
        "recovery_readiness": report_recovery_readiness(report),
        "execution_ledger": report_execution_ledger(report),
        "blocking_failures": blocking_failures,
        "item": {
            "status": "idle",
            "id": IDLE_ITEM_ID,
            "goal": "not_applicable",
            "scope": "not_applicable",
            "execution_path": "not_applicable",
            "workspace_entry": "not_applicable",
            "recovery_entry": "not_applicable",
            "review_entry": "not_applicable",
            "validation_entry": "not_applicable",
        },
        "current_checkpoint": "not_applicable",
        "recovery": "not_applicable",
        "spec_review": {"result": "not_applicable", "summary": "no active Work Item is selected."},
        "review": {"result": "not_applicable", "summary": "no active Work Item is selected."},
        "merge_ready": {"result": "not_applicable", "summary": "no active Work Item is selected."},
        "closeout": {
            "result": "not_applicable",
            "summary": "closeout is not evaluated because no active Work Item is selected.",
            "missing_inputs": [],
            "fallback_to": None,
        },
        "governance_status": {
            "schema_version": "loom-governance-status/v2",
            "result": "pass" if result == "pass" else "block",
            "current_gate": "idle",
            "classifications": [] if result == "pass" else ["gate_failure"],
            "missing_inputs": missing_inputs,
            "head_binding": {"status": "not_applicable", "head_ref": None, "base_ref": None},
            "gate_chain": [],
            "maturity": (
                governance_surface.get("governance_control_plane", {}).get("maturity")
                if isinstance(governance_surface.get("governance_control_plane"), dict)
                else None
            ),
        },
        "external_orchestrator": {
            "schema_version": "loom-governance-status/v2",
            "view": "external_orchestrator_consumer",
            "result": "pass" if result == "pass" else "block",
            "current_gate": "idle",
            "classifications": [] if result == "pass" else ["gate_failure"],
            "missing_inputs": missing_inputs,
            "allowed_operations": ["status_read", "gate_read"],
            "source_policy": {
                "status_source": "derived_from_fact_chain_idle",
                "gate_source": "not_applicable_without_active_item",
                "writeback": "not_applicable",
                "fallback_to": "admission",
            },
            "provenance": report_provenance(report),
            "recovery_readiness": report_recovery_readiness(report),
        },
        "governance_surface": governance_surface,
        "github": {"repository": None, "issue": None, "pr": None},
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            {
                "command": "status",
                "result": "block",
                "summary": "status is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": runtime_state["missing_inputs"],
                "fallback_to": runtime_state["fallback_to"],
                "runtime_state": runtime_state,
            }
        )

    derived_manifest, derived_manifest_errors = host_derived_manifest(target_root)
    if derived_manifest_errors:
        return emit(
            {
                "command": "status",
                "result": "block",
                "summary": "status is blocked because the bootstrap manifest is invalid or unreadable.",
                "missing_inputs": derived_manifest_errors,
                "fallback_to": "adoption",
                "runtime_state": runtime_state,
            }
        )
    if derived_manifest is not None:
        return emit(
            host_derived_status_payload(
                target_root,
                manifest=derived_manifest,
                runtime_state=runtime_state,
                args=args,
            )
        )

    fact_report, fact_errors = load_fact_chain_report(target_root, args.output)
    if not fact_errors:
        fact_chain = fact_report.get("fact_chain")
        entry_points = fact_chain.get("entry_points") if isinstance(fact_chain, dict) else None
        if (
            isinstance(fact_chain, dict)
            and fact_chain.get("mode") == "idle"
            and isinstance(entry_points, dict)
            and entry_points.get("current_item_id") == IDLE_ITEM_ID
        ):
            return emit(
                idle_status_payload(
                    target_root,
                    report=fact_report,
                    runtime_state=runtime_state,
                    requested_item=args.item,
                )
            )

    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "status",
                "result": "block",
                "summary": "status could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "runtime_state": runtime_state,
                **fact_chain_error_contract(errors, output_relative=args.output),
            }
        )

    spec_review = spec_review_gate_payload(context)
    review = implementation_review_status_payload(context)
    merge_ready = checkpoint_payload("merge", context)
    governance_surface = build_governance_surface(target_root)
    workspace_profile = governance_surface.get("workspace_profile")
    gate_starter = governance_surface.get("gate_starter")
    github_control_plane = governance_surface.get("github_control_plane")
    repo_interface = governance_surface.get("repo_interface")
    tool_availability = (
        repo_interface.get("tool_availability")
        if isinstance(repo_interface, dict)
        else None
    )
    policy_readiness = (
        repo_interface.get("policy_readiness")
        if isinstance(repo_interface, dict)
        else None
    )
    release_targets = (
        repo_interface.get("release_targets")
        if isinstance(repo_interface, dict)
        else None
    )
    target_release = (
        release_targets.get("target_release")
        if isinstance(release_targets, dict)
        else None
    )
    if not isinstance(target_release, dict):
        target_release = empty_target_release_status()
    ci_check_presence = github_control_plane.get("ci_check_presence") if isinstance(github_control_plane, dict) else None
    host_enforcement = github_control_plane.get("host_enforcement") if isinstance(github_control_plane, dict) else None
    execution_budget = (
        github_control_plane.get("api_snapshot", {}).get("budget")
        if isinstance(github_control_plane, dict)
        else None
    )
    execution_budget = normalize_execution_budget_payload(
        execution_budget,
        fallback_status="not_applicable",
        fallback_summary="execution budget is not available for this execution path",
        fallback_provenance={"source": "github_control_plane"},
    )
    execution_budget_risk = derive_execution_budget_risk(execution_budget)
    github_status, github_errors = github_status_payload(
        target_root,
        issue_number=args.issue,
        pr_number=args.pr,
        owner=args.owner,
        repo_name=args.repo_name,
    )
    project_drift = project_drift_payload(
        target_root=target_root,
        owner=args.owner,
        repo_name=args.repo_name,
        issue_number=args.issue,
        pr_number=args.pr,
        project_number=args.project,
        mode="advisory",
    )
    goal_contract = goal_execution_contract(context)
    goal_readiness = validate_goal_execution_contract(
        goal_contract,
        context,
        issue_number=args.issue,
        pr_number=args.pr,
        branch_name=args.branch,
    )
    governance_lint = flow_governance_lint_status(context, surface="status")
    control_status = governance_control_status(
        governance_surface=governance_surface,
        governance_lint=governance_lint,
        spec_review=spec_review,
        review=review,
        merge_ready=merge_ready,
        github_status=github_status,
        github_errors=github_errors,
    )
    fact_chain_failures = report_blocking_failures(context["report"])
    if fact_chain_failures:
        classifications = control_status.get("classifications")
        if not isinstance(classifications, list):
            classifications = []
        for failure in fact_chain_failures:
            if not isinstance(failure, dict):
                continue
            classification = failure.get("kind") or failure.get("category")
            if isinstance(classification, str) and classification not in classifications:
                classifications.append(classification)
        control_status["classifications"] = classifications
        control_status["result"] = "block"
    closeout = full_closeout_status_payload(
        target_root,
        phase_number=args.phase,
        fr_number=args.fr,
        issue_number=args.issue,
        pr_number=args.pr,
        project_number=args.project,
        branch_name=args.branch,
        owner=args.owner,
        repo_name=args.repo_name,
        github_status=github_status,
        github_errors=github_errors,
    )
    latest_execution_attempt = latest_execution_attempt_payload(target_root, context["item_id"])
    execution_failure = latest_execution_failure_payload(latest_execution_attempt)
    retry_evidence = latest_retry_evidence_payload(target_root, context["item_id"])

    missing_inputs: list[str] = []
    for section in (spec_review, review, merge_ready):
        for message in section.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    for message in github_errors:
        if message not in missing_inputs:
            missing_inputs.append(message)
    for message in control_status.get("missing_inputs", []):
        if message not in missing_inputs:
            missing_inputs.append(str(message))
    for message in governance_surface.get("missing_inputs", []) if isinstance(governance_surface, dict) else []:
        if message not in missing_inputs:
            missing_inputs.append(str(message))
    for message in report_blocking_messages(context["report"]):
        if message not in missing_inputs:
            missing_inputs.append(message)
    for message in governance_lint_missing_inputs(governance_lint):
        if message not in missing_inputs:
            missing_inputs.append(message)

    result = "pass" if not missing_inputs else "block"
    summary = (
        "status surface shows the current item, spec gate, implementation review, and merge checkpoint in one read."
        if result == "pass"
        else "status surface is readable, but one or more governance gates are still blocking or stale."
    )
    provenance = report_provenance(context["report"])
    recovery_readiness = report_recovery_readiness(context["report"])
    external_orchestrator = external_orchestrator_consumer_status(
        control_status=control_status,
        provenance=provenance,
        recovery_readiness=recovery_readiness,
    )

    return emit(
        {
            "command": "status",
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": "admission" if missing_inputs else None,
            "runtime_state": runtime_state,
            "provenance": provenance,
            "recovery_readiness": recovery_readiness,
            "execution_ledger": report_execution_ledger(context["report"]),
            "latest_execution_attempt": latest_execution_attempt,
            "execution_failure": execution_failure,
            "retry_evidence": retry_evidence,
            "tool_availability": tool_availability,
            "policy_readiness": policy_readiness,
            "execution_budget": execution_budget,
            "execution_budget_risk": execution_budget_risk,
            "goal_execution_contract": goal_contract,
            "goal_readiness": goal_readiness,
            "project_drift": project_drift,
            "governance_lint": governance_lint,
            "blocking_failures": report_blocking_failures(context["report"]),
            "item": {
                "id": context["item_id"],
                "goal": context["goal"],
                "scope": context["scope"],
                "execution_path": context["execution_path"],
                "workspace_entry": context["workspace_entry"],
                "recovery_entry": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
                "review_entry": context["review_entry"],
                "validation_entry": context["validation_entry"],
            },
            "current_checkpoint": {
                "raw": context["current_checkpoint_raw"],
                "normalized": context["current_checkpoint"],
            },
            "recovery": {
                "current_stop": context["current_stop"],
                "next_step": context["next_step"],
                "blockers": context["blockers"],
                "latest_validation_summary": context["latest_validation_summary"],
                "recovery_boundary": context["recovery_boundary"],
                "current_lane": context["current_lane"],
            },
            "spec_review": spec_review,
            "review": review,
            "merge_ready": merge_ready,
            "closeout": closeout,
            "target_release": target_release,
            "workspace_profile": workspace_profile,
            "gate_starter": gate_starter,
            "ci_check_presence": ci_check_presence,
            "host_enforcement": host_enforcement,
            "governance_status": control_status,
            "external_orchestrator": external_orchestrator,
            "governance_surface": governance_surface,
            "github": github_status,
        }
    )


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
