#!/usr/bin/env python3
"""Workspace, runtime, Work Item, recovery, and bounded execution orchestration."""

from __future__ import annotations
import argparse
import hashlib
import json
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None  # type: ignore[assignment]
from fact_chain_support import (
    load_json_file,
    markdown_sections,
    parse_key_value_section,
    parse_recovery_entry,
    parse_work_item,
    resolve_repo_relative_path,
)
from flow_runtime import command_target, current_iso_timestamp, emit, git_branch, git_head_sha, local_command_json as _local_command_json, resolve_target_arg, run_git, runtime_state_payload
from closeout_flow import (
    carrier_closeout_sync_payload,
    closeout_retained_item_lookup,
    lifecycle_admission_payload,
    retained_item_lookup_id,
    retained_item_lookup_missing_inputs,
    write_terminal_closeout_metadata,
)
from review_flow import (
    build_review_flow_payload,
    fact_chain_error_contract,
    parse_review_artifact_locators,
    pre_review_readiness_cost_guard_payload,
    repo_specific_default_fallback,
    repo_specific_requirements_payload,
    report_blocking_failures,
    report_blocking_messages,
    report_provenance,
    report_recovery_readiness,
    runtime_evidence_from_report,
    state_check_payload,
    write_runtime_text_artifact,
)
from host_profile import (
    adoption_decisions_payload,
    companion_generation_payload,
    guided_adoption_plan_payload,
    project_drift_payload,
    workspace_profile_from_context,
)
from delivery_control import (
    active_workspace_diagnostics,
    adoption_suite_path_decision_presence,
    applicable_pr_metadata_contracts,
    carrier_refresh_payload,
    check_pr_template,
    checkpoint_payload,
    dedupe_strings,
    default_review_path,
    default_spec_review_path,
    dependency_graph_payload,
    detect_github_repo,
    dirty_paths_by_owner,
    extract_github_host_context,
    git_tracked_files,
    github_host_completion_truth,
    is_idle_context_errors,
    load_context,
    load_context_with_retained_idle_fallback,
    load_fact_chain_report,
    load_optional_json_fixture,
    load_optional_text_fixture,
    load_pr_payload_for_gate,
    load_review_record,
    metadata_contract_raw_fields,
    normalize_checkpoint,
    pr_body_field_value,
    pr_body_governance_metadata_fields,
    pr_body_machine_surface,
    pr_metadata_effective_contract_surface,
    pr_metadata_issue_reference,
    pr_metadata_preflight_payload,
    purity_report_from_context,
    refresh_shadow_evidence_actions,
    relative_to_root,
    resolve_artifact_read_path,
    resolve_artifact_write_path,
    resolve_workspace_path,
    runtime_state_block_payload,
    sha256_file,
    shadow_parity_report,
    spec_suite_validation_payload,
    suite_gate_not_applicable_payload,
    suite_gate_payload_for_surface,
    suite_gate_required_for_surface,
    suite_gate_step,
    suite_gate_validation_payload,
    suite_validation_command_payload,
    suite_validation_fallback_to,
    suite_validation_missing_inputs,
    suite_validation_ready,
    validate_governance_intensity_metadata_fields,
    work_item_locator_for_metadata,
    write_json_file,
)
from github_host import (
    github_issue_dependencies_payload,
    github_issue_payload,
    github_pr_payload,
    run_process,
)
from governance_surface import (
    ADVERSARIAL_ADOPTION_EVIDENCE_LOCATOR,
    ADVERSARIAL_ADOPTION_EVIDENCE_SCHEMA,
    build_governance_surface,
    derive_execution_budget_risk,
    workspace_lifecycle_expectations,
)
from execution_attempts import (
    persist_execution_attempt,
)
from loom_init import host_derived_manifest

FLOW_ENTRYPOINT = Path(__file__).with_name("loom_flow.py")

PR_TEMPLATE_SECTIONS = (
    "## Summary",
    "## Validation",
    "## Risks And Follow-ups",
    "## Related Work",
)

ADOPTION_PR_BODY_SECTIONS = (*PR_TEMPLATE_SECTIONS, "## Review Artifacts")

OWNED_TEMP_ROOTS = (
    ".loom/.tmp",
    ".loom/tmp",
    ".loom/runtime/cache",
    ".loom/runtime/tmp",
    ".loom/flow/tmp",
)

TERMINAL_CHECKPOINTS = {
    "retired",
    "done",
    "closed",
    "closed_out",
    "merged",
    "archived",
}

GITHUB_ISSUE_URL_RE = re.compile(r"github\.com/(?P<owner>[^/\s`]+)/(?P<repo>[^/\s`]+)/issues/(?P<number>\d+)")

GITHUB_ISSUE_REF_RE = re.compile(r"(?i)\b(?:github\s+issue|issue)\s+#?(?P<number>\d+)\b")

RUNTIME_EVIDENCE_FIELDS = (
    "run_entry",
    "logs_entry",
    "diagnostics_entry",
    "verification_entry",
    "lane_entry",
)

HOST_DEPENDENCY_GRAPH_SCHEMA = "loom-host-dependency-graph/v1"

GOAL_EXECUTION_CONTRACT_SCHEMA = "loom-goal-execution-contract/v1"

GOAL_READINESS_SCHEMA = "loom-goal-readiness/v1"

GOVERNANCE_LINT_RESULT_SCHEMA = "loom-governance-lint-result/v1"

GOVERNANCE_LINT_STATUS_SCHEMA = "loom-governance-lint-status/v1"

PR_METADATA_RENDER_SCHEMA = "loom-pr-metadata-render/v1"

PR_METADATA_READBACK_SCHEMA = "loom-pr-metadata-readback/v1"

PR_METADATA_UPDATE_SCHEMA = "loom-pr-metadata-update/v1"

PR_METADATA_MACHINE_SCHEMA = "loom-repo-pr-metadata/v1"

PR_METADATA_PARSER_VERSION = "loom-pr-metadata-parser/v2"

PR_METADATA_RENDERER_ID = "renderer:loom-pr-metadata-render/v2"

GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID = "loom-governance-intensity"

RECOVERY_FIELD_LABELS = {
    "current_checkpoint": "Current Checkpoint",
    "current_stop": "Current Stop",
    "next_step": "Next Step",
    "blockers": "Blockers",
    "latest_validation_summary": "Latest Validation Summary",
    "recovery_boundary": "Recovery Boundary",
    "current_lane": "Current Lane",
}

RETAINED_HOST_SIGNAL_SCHEMA = "loom-retained-host-signal/v1"

SHADOW_PARITY_SURFACES = ("admission", "review", "merge_ready", "closeout")

REPEATED_BLOCKER_SIGNAL_SCHEMA = "loom-repeated-blocker-signal/v1"

BUILD_EVIDENCE_SCHEMA = "loom-build-evidence/v1"

SUBAGENT_OWNERSHIP_SCHEMA = "loom-subagent-ownership/v1"

NO_ACTIVE_ITEM_ID = "no_active_item"

IDLE_FACT_CHAIN_ERROR = "repository is idle; no active Work Item is selected"

def story_flow_payload(
    *,
    target_root: Path,
    runtime_state: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "command": "flow",
        "operation": "story",
        "result": "pass",
        "summary": "story intake contract summary is available; runtime does not generate product truth without caller-provided context.",
        "missing_inputs": [],
        "fallback_to": None,
        "runtime_state": runtime_state,
        "target": str(target_root),
        "steps": steps
        + [
            {
                "name": "story-contract",
                "result": "pass",
                "summary": "User Story, Story Readiness, and Story Business Confirmation contracts are separated from delivery state.",
                "missing_inputs": [],
                "fallback_to": None,
            }
        ],
        "contract_summary": {
            "mode": "contract-summary",
            "authority": "docs/methodology/governance/story-intake.md",
            "runtime_generates_story": False,
        },
        "story_contract": {
            "schema_version": "loom-user-story/v1",
            "required_fields": [
                "actor",
                "capability",
                "outcome",
                "business_value",
                "acceptance_scenarios",
                "out_of_scope",
                "provenance",
            ],
            "forbidden_fields": [
                "delivery_handoff",
                "spec_locator",
                "plan_locator",
                "recovery_state",
                "review_findings",
                "pr_summary",
                "merge_ready_result",
                "closeout_result",
            ],
            "scenario_dimensions": [
                "happy_path",
                "negative_path",
                "edge_case",
                "alternative_path",
                "security_permission",
                "environment_interruption",
            ],
        },
        "readiness_contract": {
            "schema_version": "loom-story-readiness/v1",
            "decisions": ["confirmed", "pending", "revision-requested", "not_applicable"],
            "required_fields": ["decision", "rationale", "story_locator", "checks", "missing_inputs", "fallback_to"],
            "checks": [
                "actor_specificity",
                "outcome_clarity",
                "value_signal",
                "acceptance_scenario_quality",
                "unresolved_blockers",
                "story_size",
            ],
            "authority_boundary": "readiness judges entry into spec / plan, not product strategy correctness.",
        },
        "business_confirmation_contract": {
            "schema_version": "loom-story-business-confirmation/v1",
            "decisions": ["pending", "confirmed", "revision-requested", "not_applicable"],
            "required_fields": [
                "decision",
                "confirmation_scope",
                "confirmation_source",
                "revision_request",
                "bypass_rationale",
            ],
            "confirmation_scope": [
                "actor",
                "capability",
                "outcome",
                "business_value",
                "acceptance_scenarios",
                "out_of_scope",
            ],
            "user_fast_path": "plain `确认` records confirmed when the visible story is the confirmation subject",
            "revision_rule": "revision-requested returns to story shaping before spec / plan consumption",
            "not_applicable_rule": "pure governance, maintenance, formatting, link repair, or carrier-only changes may bypass with rationale",
            "authority_boundary": "confirmation covers business semantics only, not technical solution, test strategy, review quality, or code quality.",
        },
        "delivery_consumption_contract": {
            "execution_entry": "Work Item",
            "spec_consumes": "confirmed or not_applicable story scenario id / locator as behavior contract input",
            "plan_consumes": "confirmed or not_applicable story scenario id mapped to tests, checks, manual validation, or not_applicable evidence",
            "scenario_locator_output": "story scaffold exports stable scenario ids and scenario locators for spec.md / plan.md locator-only consumption",
            "business_confirmation_locator_output": "story scaffold exports a confirmed Story Business Confirmation locator or not_applicable rationale",
            "blocks_on_confirmation": ["pending", "revision-requested"],
            "forbidden": "story must not author recovery, review, PR, merge-ready, closeout, or formal spec / plan state",
        },
        "contract": {
            "story_intake": "docs/methodology/governance/story-intake.md",
            "story_template": "docs/methodology/templates/scaffold/user-story.md",
            "story_carrier_locator": ".loom/stories/<item-id>.md",
            "spec_suite": "docs/methodology/templates/spec-suite.md",
        },
    }

def default_shadow_source(target_root: Path, *, surface: str, side: str) -> str | None:
    loom_sources = {
        "admission": [".loom/work-items/INIT-0001.md", ".loom/status/current.md", ".loom/README.md"],
        "review": [".loom/reviews/INIT-0001.json", ".loom/status/current.md", ".loom/README.md"],
        "merge_ready": [".loom/status/current.md", ".github/PULL_REQUEST_TEMPLATE.md", ".loom/README.md"],
        "closeout": [".loom/status/current.md", ".loom/README.md"],
    }
    repo_sources = {
        "admission": [".loom/companion/checkpoints.md", ".loom/companion/README.md"],
        "review": [".loom/companion/review.md", ".loom/companion/README.md"],
        "merge_ready": [".loom/companion/merge-ready.md", ".loom/companion/README.md"],
        "closeout": [".loom/companion/closeout.md", ".loom/companion/README.md"],
    }
    candidates = loom_sources.get(surface, []) if side == "loom" else repo_sources.get(surface, [])
    for candidate in candidates:
        if (target_root / candidate).exists():
            return candidate
    return None

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def shadow_evidence_payload(target_root: Path, *, source: str, value: str) -> dict[str, Any]:
    source_path = target_root / source
    return {
        "result": value,
        "source_files": [source],
        "source_sha256": {source: sha256_file(source_path)},
    }

def read_text_file(path_str: str) -> tuple[str | None, list[str]]:
    path = Path(path_str).expanduser()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"failed to read {path}: {exc.strerror or exc}"]
    return text, []

def update_markdown_bullet(path: Path, label: str, value: str) -> None:
    pattern = re.compile(rf"(?m)^- {re.escape(label)}:\s*.*$")
    replacement = f"- {label}: {value}"
    text = path.read_text(encoding="utf-8")
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"unable to update `{label}` in {path}")
    path.write_text(updated, encoding="utf-8")

def replace_markdown_section(path: Path, section_name: str, new_lines: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(?ms)(^## {re.escape(section_name)}\n\n)(.*?)(?=^## |\Z)"
    )
    replacement = "\\1" + "\n".join(new_lines).rstrip() + "\n\n"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"unable to update `{section_name}` in {path}")
    path.write_text(updated, encoding="utf-8")

def render_status_surface(report: dict[str, Any], runtime_evidence: dict[str, dict[str, Any]]) -> str:
    facts = report["facts"]
    current_checkpoint = normalize_checkpoint(str(facts["current_checkpoint"]["value"]))
    return (
        "# Current Status\n\n"
        "## Derived Fact Chain View\n\n"
        f"- Item ID: {facts['item_id']['value']}\n"
        f"- Goal: {facts['goal']['value']}\n"
        f"- Scope: {facts['scope']['value']}\n"
        f"- Execution Path: {facts['execution_path']['value']}\n"
        f"- Workspace Entry: {facts['workspace_entry']['value']}\n"
        f"- Recovery Entry: {facts['recovery_entry']['value']}\n"
        f"- Review Entry: {facts['review_entry']['value']}\n"
        f"- Validation Entry: {facts['validation_entry']['value']}\n"
        f"- Closing Condition: {facts['closing_condition']['value']}\n"
        f"- Current Checkpoint: {current_checkpoint}\n"
        f"- Current Stop: {facts['current_stop']['value']}\n"
        f"- Next Step: {facts['next_step']['value']}\n"
        f"- Blockers: {facts['blockers']['value']}\n"
        f"- Latest Validation Summary: {facts['latest_validation_summary']['value']}\n"
        f"- Recovery Boundary: {facts['recovery_boundary']['value']}\n"
        f"- Current Lane: {facts['current_lane']['value']}\n\n"
        "## Runtime Evidence\n\n"
        f"- Run Entry: {runtime_evidence['run_entry']['value']}\n"
        f"- Logs Entry: {runtime_evidence['logs_entry']['value']}\n"
        f"- Diagnostics Entry: {runtime_evidence['diagnostics_entry']['value']}\n"
        f"- Verification Entry: {runtime_evidence['verification_entry']['value']}\n"
        f"- Lane Entry: {runtime_evidence['lane_entry']['value']}\n\n"
        "## Sources\n\n"
        f"- Static Truth: {report['fact_chain']['entry_points']['work_item']}\n"
        f"- Dynamic Truth: {report['fact_chain']['entry_points']['recovery_entry']}\n"
        "- Locator Truth: .loom/bootstrap/init-result.json\n"
        f"- Fact Chain CLI: {report['fact_chain']['read_entry']}\n"
    )

def sync_status_surface(target_root: Path, output_relative: str, runtime_evidence: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    output_path, output_errors = resolve_repo_relative_path(target_root, output_relative, label="init-result locator")
    if output_errors:
        return {}, output_errors
    assert output_path is not None
    try:
        init_result = load_json_file(output_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {}, [f"invalid init-result JSON: {exc}"]

    fact_chain = init_result.get("fact_chain")
    if not isinstance(fact_chain, dict):
        return {}, ["init-result is missing required section: fact_chain"]
    entry_points = fact_chain.get("entry_points")
    if not isinstance(entry_points, dict):
        return {}, ["init-result.fact_chain.entry_points must be an object"]

    work_item_ref = str(entry_points.get("work_item", ""))
    recovery_ref = str(entry_points.get("recovery_entry", ""))
    status_ref = str(entry_points.get("status_surface", ""))
    work_item_path, work_item_errors = resolve_repo_relative_path(target_root, work_item_ref, label="work item locator")
    recovery_path, recovery_errors = resolve_repo_relative_path(target_root, recovery_ref, label="recovery entry locator")
    status_path, status_errors = resolve_repo_relative_path(target_root, status_ref, label="status surface locator")
    locator_errors = [*work_item_errors, *recovery_errors, *status_errors]
    if locator_errors:
        return {}, locator_errors
    assert work_item_path is not None
    assert recovery_path is not None
    assert status_path is not None
    if not work_item_path.exists() or not recovery_path.exists():
        return {}, ["fact-chain carrier is missing during status sync"]
    work_item, work_item_errors = parse_work_item(work_item_path, target_root)
    recovery_entry, recovery_errors = parse_recovery_entry(recovery_path, target_root)
    errors = [*work_item_errors, *recovery_errors]
    if errors:
        return {}, errors
    pseudo_report = {
        "fact_chain": {
            "read_entry": str(fact_chain.get("read_entry", "python3 .loom/bin/loom_init.py fact-chain --target .")),
            "entry_points": {
                "work_item": work_item_ref,
                "recovery_entry": recovery_ref,
                "status_surface": status_ref,
            },
        },
        "facts": {
            "item_id": {"value": str(work_item["item_id"])},
            "goal": {"value": str(work_item["goal"])},
            "scope": {"value": str(work_item["scope"])},
            "execution_path": {"value": str(work_item["execution_path"])},
            "workspace_entry": {"value": str(work_item["workspace_entry"])},
            "recovery_entry": {"value": str(work_item["recovery_entry"])},
            "review_entry": {"value": str(work_item["review_entry"])},
            "validation_entry": {"value": str(work_item["validation_entry"])},
            "closing_condition": {"value": str(work_item["closing_condition"])},
            "current_checkpoint": {"value": recovery_entry["current_checkpoint"]},
            "current_stop": {"value": recovery_entry["current_stop"]},
            "next_step": {"value": recovery_entry["next_step"]},
            "blockers": {"value": recovery_entry["blockers"]},
            "latest_validation_summary": {"value": recovery_entry["latest_validation_summary"]},
            "recovery_boundary": {"value": recovery_entry["recovery_boundary"]},
            "current_lane": {"value": recovery_entry["current_lane"]},
        },
    }
    status_path.write_text(render_status_surface(pseudo_report, runtime_evidence), encoding="utf-8")
    refreshed, refresh_errors = load_fact_chain_report(target_root, output_relative)
    if refresh_errors:
        return {}, refresh_errors
    return refreshed, []

def read_runtime_evidence(target_root: Path, status_relative: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    status_path, locator_errors = resolve_repo_relative_path(target_root, status_relative, label="status surface locator")
    if locator_errors:
        return {}, locator_errors
    assert status_path is not None
    if not status_path.exists():
        return {}, [f"missing status surface: {status_relative}"]
    sections = markdown_sections(status_path)
    values, errors = parse_key_value_section(
        sections,
        "Runtime Evidence",
        {
            "Run Entry": "run_entry",
            "Logs Entry": "logs_entry",
            "Diagnostics Entry": "diagnostics_entry",
            "Verification Entry": "verification_entry",
            "Lane Entry": "lane_entry",
        },
        status_relative,
    )
    if errors:
        return {}, errors
    return {
        key: {
            "value": values[key],
            "status": "not_applicable" if values[key] == "not_applicable" else "present",
        }
        for key in RUNTIME_EVIDENCE_FIELDS
    }, []

def retained_host_signals_payload(
    *,
    target_root: Path,
    governance_surface: dict[str, Any],
    surface: str,
    current_head: str | None,
) -> dict[str, Any]:
    repo_interop = governance_surface.get("repo_interop")
    availability = repo_interop.get("availability") if isinstance(repo_interop, dict) else "absent"
    if availability in {None, "absent"}:
        return {
            "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
            "surface": surface,
            "result": "pass",
            "summary": "no retained host signals are declared for this surface.",
            "missing_inputs": [],
            "fallback_to": None,
            "signals": [],
        }
    if availability != "present":
        return {
            "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "repo interop is incomplete, so retained host signals cannot be consumed.",
            "missing_inputs": list(repo_interop.get("missing_inputs", [])) if isinstance(repo_interop, dict) else ["repo interop"],
            "fallback_to": "adoption",
            "signals": [],
        }

    interop_path = target_root / ".loom/companion/interop.json"
    missing_inputs: list[str] = []
    signals: list[dict[str, Any]] = []
    try:
        interop_payload = load_json_file(interop_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "repo interop is present but unreadable.",
            "missing_inputs": [f".loom/companion/interop.json: {exc}"],
            "fallback_to": "adoption",
            "signals": [],
        }
    if isinstance(interop_payload, dict) and "host_adapters" in interop_payload:
        return {
            "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "repo interop uses the removed host_adapters field.",
            "missing_inputs": ["rename `.loom/companion/interop.json#host_adapters` to `external_result_sources`"],
            "migration_diagnostics": [{
                "code": "legacy_repo_interop_host_adapters",
                "locator": ".loom/companion/interop.json#host_adapters",
                "replacement": "external_result_sources",
            }],
            "fallback_to": "adoption",
            "signals": [],
        }
    external_result_sources = interop_payload.get("external_result_sources", []) if isinstance(interop_payload, dict) else None
    if not isinstance(external_result_sources, list):
        return {
            "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "repo interop external_result_sources must be a list when present.",
            "missing_inputs": ["repo interop external_result_sources"],
            "fallback_to": "adoption",
            "signals": [],
        }

    for index, entry in enumerate(external_result_sources):
        if not isinstance(entry, dict):
            continue
        surfaces = entry.get("surfaces")
        if not isinstance(surfaces, list) or surface not in surfaces:
            continue
        signal_missing: list[str] = []
        locator = str(entry.get("locator") or "")
        requirement = entry.get("requirement")
        resolved_path, locator_errors = resolve_repo_relative_path(
            target_root,
            locator,
            label=f"retained host signal {entry.get('id') or index}",
        )
        signal_missing.extend(locator_errors)
        payload: dict[str, Any] | None = None
        freshness = "unknown"
        observed_result = None
        if resolved_path is None or locator_errors:
            freshness = "unreadable"
        elif not resolved_path.exists() or resolved_path.is_dir():
            freshness = "missing"
            signal_missing.append(f"retained host signal locator is missing: {locator}")
        else:
            try:
                loaded = load_json_file(resolved_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                freshness = "unreadable"
                signal_missing.append(f"retained host signal `{locator}` is unreadable: {exc}")
            else:
                if not isinstance(loaded, dict):
                    freshness = "schema_drift"
                    signal_missing.append(f"retained host signal `{locator}` must be a JSON object")
                else:
                    payload = loaded
                    observed_result = (
                        loaded.get("result")
                        or loaded.get("decision")
                        or loaded.get("status")
                        or loaded.get("verdict")
                    )
                    bound_head = loaded.get("head_sha") or loaded.get("reviewed_head") or loaded.get("head")
                    if isinstance(bound_head, str) and current_head and bound_head != current_head:
                        freshness = "stale"
                        signal_missing.append(f"retained host signal `{locator}` is bound to stale head `{bound_head}`")
                    elif loaded.get("schema_version") not in {None, RETAINED_HOST_SIGNAL_SCHEMA}:
                        freshness = "schema_drift"
                        signal_missing.append(f"retained host signal `{locator}` schema drift")
                    else:
                        freshness = "current"
                    if observed_result not in {"pass", "allow", "success", "ok", True}:
                        signal_missing.append(f"retained host signal `{entry.get('id') or locator}` is not passing")
        blocking = requirement == "required" and bool(signal_missing)
        if blocking:
            missing_inputs.extend(signal_missing)
        signals.append(
            {
                "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
                "id": entry.get("id") or f"external-result-source-{index + 1}",
                "summary": entry.get("summary"),
                "surface": surface,
                "locator": locator,
                "requirement": requirement,
                "owner": entry.get("owner"),
                "result": "block" if blocking else "pass" if not signal_missing else "warn",
                "observed_result": observed_result,
                "freshness": freshness,
                "missing_inputs": signal_missing,
                "fallback_to": entry.get("fallback_to") or "merge_ready",
                "provenance": {
                    "interop_locator": ".loom/companion/interop.json",
                    "payload_schema": payload.get("schema_version") if isinstance(payload, dict) else None,
                },
            }
        )

    return {
        "schema_version": RETAINED_HOST_SIGNAL_SCHEMA,
        "surface": surface,
        "result": "pass" if not missing_inputs else "block",
        "summary": (
            "retained host signals are readable and current."
            if not missing_inputs
            else "required retained host signals are missing, stale, failing, or schema-drifted."
        ),
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
        "fallback_to": None if not missing_inputs else "merge_ready",
        "signals": signals,
        "fail_closed_conditions": [
            "missing-applicable-signal",
            "failed-signal",
            "stale-signal",
            "schema-drift",
            "head-mismatch",
        ],
    }

def render_work_item(data: dict[str, Any]) -> str:
    return (
        f"# {data['item_id']}\n\n"
        "## Static Facts\n\n"
        f"- Item ID: {data['item_id']}\n"
        f"- Goal: {data['goal']}\n"
        f"- Scope: {data['scope']}\n"
        f"- Execution Path: {data['execution_path']}\n"
        f"- Workspace Entry: {data['workspace_entry']}\n"
        f"- Recovery Entry: {data['recovery_entry']}\n"
        f"- Review Entry: {data['review_entry']}\n"
        f"- Validation Entry: {data['validation_entry']}\n"
        f"- Closing Condition: {data['closing_condition']}\n\n"
        "## Associated Artifacts\n\n"
        + "".join(f"- `{artifact}`\n" for artifact in data["associated_artifacts"])
    )

def render_recovery_entry(item_id: str, values: dict[str, str]) -> str:
    current_checkpoint = normalize_checkpoint(values["current_checkpoint"])
    return (
        f"# {item_id} Progress\n\n"
        "## Dynamic Facts\n\n"
        f"- Item ID: {item_id}\n"
        f"- Current Checkpoint: {current_checkpoint}\n"
        f"- Current Stop: {values['current_stop']}\n"
        f"- Next Step: {values['next_step']}\n"
        f"- Blockers: {values['blockers']}\n"
        f"- Latest Validation Summary: {values['latest_validation_summary']}\n"
        f"- Recovery Boundary: {values['recovery_boundary']}\n"
        f"- Current Lane: {values['current_lane']}\n\n"
        "## Execution Ledger\n\n"
        "- Ledger Binding: recovery_entry\n"
        "- Plan Locator: not_applicable (suite path: not_applicable)\n"
        "- Acceptance Locator: not_applicable\n"
        "- Validation Evidence Locator: not_applicable\n"
        "- Handoff Notes Locator: not_applicable\n"
        "- Evidence Freshness: not_applicable\n"
    )

def render_adoption_pr_body(context: dict[str, Any]) -> str:
    item_id = context["item_id"]
    review_record = context["review_entry"]
    _, suite_path_values = adoption_suite_path_decision_presence(context)
    suite_not_applicable = bool(suite_path_values) and suite_path_values <= {"not_applicable"}
    spec_review_record = "not_applicable" if suite_not_applicable else default_spec_review_path(item_id)
    spec_plan_locator = (
        f".loom/specs/{item_id}/spec.md (suite path: not_applicable)"
        if suite_not_applicable
        else f".loom/specs/{item_id}/spec.md"
    )
    return (
        "## Summary\n\n"
        f"- Problem: Adopt Loom governance carriers for `{item_id}`.\n"
        "- Scope: Loom-owned carrier and review metadata only.\n\n"
        "## Validation\n\n"
        "- [x] Verified by Loom adoption round-trip.\n\n"
        "## Risks And Follow-ups\n\n"
        "- Risks: None identified by the generated adoption body.\n"
        "- Follow-ups: Keep repo-specific gates repo-owned.\n\n"
        "## Related Work\n\n"
        f"- Issue: {item_id}\n"
        f"- Spec / plan: {spec_plan_locator}\n\n"
        "## Review Artifacts\n\n"
        f"- Active Work Item: {context['report']['fact_chain']['entry_points']['work_item']}\n"
        f"- Active Recovery Entry: {context['report']['fact_chain']['entry_points']['recovery_entry']}\n"
        f"- Status Surface: {context['report']['fact_chain']['entry_points']['status_surface']}\n"
        f"- Review Record: {review_record}\n"
        f"- Spec Review Record: {spec_review_record}\n"
    )

def adoption_pr_body_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line.strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line.rstrip())
    return {section: "\n".join(lines).strip() for section, lines in sections.items()}

def validate_adoption_pr_body(body: str, *, target_root: Path) -> dict[str, Any]:
    sections = adoption_pr_body_sections(body)
    missing_sections = [section for section in ADOPTION_PR_BODY_SECTIONS if section not in sections]
    missing_inputs: list[str] = [f"PR body missing section: {section}" for section in missing_sections]
    artifact_section = sections.get("## Review Artifacts", "")
    locators, locator_errors = parse_review_artifact_locators(artifact_section)
    missing_inputs.extend(locator_errors)

    locator_status: dict[str, dict[str, Any]] = {}
    for label, locator in locators.items():
        if label == "Spec Review Record" and locator == "not_applicable":
            locator_status[label] = {
                "locator": locator,
                "status": "not_applicable",
            }
            continue
        path, errors = resolve_repo_relative_path(target_root, locator, label=f"Review Artifacts `{label}`")
        exists = bool(path and path.exists() and path.is_file())
        if errors:
            missing_inputs.extend(errors)
        elif not exists:
            missing_inputs.append(f"Review Artifacts `{label}` points to missing file: {locator}")
        locator_status[label] = {
            "locator": locator,
            "status": "present" if exists and not errors else "missing",
        }

    return {
        "result": "pass" if not missing_inputs else "block",
        "missing_inputs": missing_inputs,
        "sections": {section: section in sections for section in ADOPTION_PR_BODY_SECTIONS},
        "review_artifacts": locator_status,
    }

def judgment_closure_payload(
    target_root: Path,
    decisions: dict[str, Any],
    companion_generation: dict[str, Any],
    governance_surface: dict[str, Any],
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    required_fields = {"id", "question", "source_locator", "reasoning", "write_targets", "verification_commands", "status"}
    for judgment in decisions.get("judgments", []):
        if not isinstance(judgment, dict):
            missing_inputs.append("judgment is not an object")
            continue
        missing = sorted(required_fields - set(judgment))
        if missing:
            missing_inputs.append(f"judgment `{judgment.get('id')}` missing fields: {', '.join(missing)}")
        for target in judgment.get("write_targets", []):
            if not isinstance(target, str):
                missing_inputs.append(f"judgment `{judgment.get('id')}` has non-string write target")
                continue
            if target.startswith("github:"):
                continue
            target_locator = target.split(":", 1)[0] if ":" in target else target
            path, errors = resolve_repo_relative_path(target_root, target_locator, label=f"judgment `{judgment.get('id')}` write target")
            missing_inputs.extend(errors)
            if path is not None and not path.exists():
                missing_inputs.append(f"judgment `{judgment.get('id')}` write target missing: {target}")
        if not judgment.get("verification_commands"):
            missing_inputs.append(f"judgment `{judgment.get('id')}` missing verification commands")
    repo_interface = governance_surface.get("repo_interface")
    if isinstance(repo_interface, dict) and repo_interface.get("availability") not in {"present", "absent"}:
        missing_inputs.extend(f"repo_interface: {message}" for message in repo_interface.get("missing_inputs", []))
    repo_interop = governance_surface.get("repo_interop")
    if isinstance(repo_interop, dict) and repo_interop.get("availability") not in {"present", "absent"}:
        missing_inputs.extend(f"repo_interop: {message}" for message in repo_interop.get("missing_inputs", []))
    if companion_generation.get("result") != "pass":
        missing_inputs.extend(str(message) for message in companion_generation.get("missing_inputs", []))
    return {
        "result": "pass" if not missing_inputs else "block",
        "summary": (
            "adoption judgments have source locators, reasoning, write targets, and verification evidence."
            if not missing_inputs
            else "adoption judgment closure is incomplete."
        ),
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
    }

def local_command_json(target_root: Path, args: list[str]) -> tuple[dict[str, Any] | None, list[str]]:
    return _local_command_json(target_root, args, entrypoint=Path(str(FLOW_ENTRYPOINT)))

def generated_companion_consumption_payload(
    target_root: Path,
    expected_item: str | None,
    governance_surface: dict[str, Any],
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    repo_interface = governance_surface.get("repo_interface")
    repo_interop = governance_surface.get("repo_interop")
    governance_status = "pass"
    if not isinstance(repo_interface, dict) or repo_interface.get("availability") != "present":
        governance_status = "block"
        missing_inputs.append("governance_surface did not consume generated repo companion interface")
    if not isinstance(repo_interop, dict) or repo_interop.get("availability") != "present":
        governance_status = "block"
        missing_inputs.append("governance_surface did not consume generated repo interop contract")

    item_args = ["--item", expected_item] if expected_item else []
    review_payload, review_errors = local_command_json(
        target_root,
        ["flow", "review", "--target", str(target_root), *item_args],
    )
    merge_payload, merge_errors = local_command_json(
        target_root,
        ["flow", "merge-ready", "--target", str(target_root), *item_args],
    )
    shadow_payload, shadow_errors = local_command_json(
        target_root,
        ["shadow-parity", "--target", str(target_root)],
    )

    def flow_consumption(payload: dict[str, Any] | None, errors: list[str], *, surface: str) -> dict[str, Any]:
        if errors or payload is None:
            return {"status": "block", "missing_inputs": errors or [f"{surface} flow did not return JSON"]}
        requirements = payload.get("repo_specific_requirements")
        if not isinstance(requirements, dict):
            return {
                "status": "block",
                "result": payload.get("result"),
                "missing_inputs": [f"{surface} flow did not expose repo_specific_requirements"],
            }
        if requirements.get("source_locator") != ".loom/companion/repo-interface.json":
            return {
                "status": "block",
                "result": payload.get("result"),
                "repo_specific_requirements": requirements,
                "missing_inputs": [f"{surface} flow did not consume .loom/companion/repo-interface.json"],
            }
        return {
            "status": "pass" if payload.get("result") == "pass" else "consumed",
            "result": payload.get("result"),
            "summary": payload.get("summary"),
            "repo_specific_requirements": requirements,
            "missing_inputs": [],
        }

    review = flow_consumption(review_payload, review_errors, surface="review")
    merge_ready = flow_consumption(merge_payload, merge_errors, surface="merge_ready")
    if shadow_errors or shadow_payload is None:
        shadow_parity = {"status": "block", "missing_inputs": shadow_errors or ["shadow parity did not return JSON"]}
    else:
        reports = shadow_payload.get("reports")
        shadow_missing = list(shadow_payload.get("missing_inputs", [])) if isinstance(shadow_payload.get("missing_inputs"), list) else []
        if shadow_payload.get("result") != "pass":
            shadow_missing.append(f"shadow parity result was {shadow_payload.get('result')}")
        if not isinstance(reports, list) or not reports:
            shadow_parity = {
                "status": "block",
                "result": shadow_payload.get("result"),
                "missing_inputs": ["shadow parity did not expose per-surface reports"],
            }
        elif shadow_missing:
            shadow_parity = {
                "status": "block",
                "result": shadow_payload.get("result"),
                "summary": shadow_payload.get("summary"),
                "missing_inputs": shadow_missing,
            }
        else:
            report_rows = [
                {
                    "surface": report.get("surface"),
                    "result": report.get("result"),
                    "loom_locator": report.get("loom_surface", {}).get("locator") if isinstance(report.get("loom_surface"), dict) else None,
                    "repo_locator": report.get("repo_surface", {}).get("locator") if isinstance(report.get("repo_surface"), dict) else None,
                }
                for report in reports
                if isinstance(report, dict)
            ]
            report_missing = [
                f"shadow parity surface {row.get('surface')} did not match"
                for row in report_rows
                if row.get("result") != "match"
            ]
            shadow_parity = {
                "status": "pass" if not report_missing else "block",
                "result": shadow_payload.get("result"),
                "summary": shadow_payload.get("summary"),
                "reports": report_rows,
                "missing_inputs": report_missing,
            }

    for label, entry in (("review", review), ("merge_ready", merge_ready), ("shadow_parity", shadow_parity)):
        if entry.get("status") not in {"pass", "consumed"}:
            for message in entry.get("missing_inputs", []):
                missing_inputs.append(f"{label}: {message}")

    return {
        "schema_version": "loom-generated-companion-consumption/v1",
        "result": "pass" if not missing_inputs else "block",
        "summary": "generated companion and interop carriers were consumed through governance_surface, review, merge-ready, and shadow parity.",
        "missing_inputs": missing_inputs,
        "governance_surface": {
            "status": governance_status,
            "repo_interface_availability": repo_interface.get("availability") if isinstance(repo_interface, dict) else None,
            "repo_interop_availability": repo_interop.get("availability") if isinstance(repo_interop, dict) else None,
        },
        "review": review,
        "merge_ready": merge_ready,
        "shadow_parity": shadow_parity,
    }

def active_workspace_conflicts(target_root: Path, item_id: str, workspace_entry: str) -> list[str]:
    conflicts: list[str] = []
    for diagnostic in active_workspace_diagnostics(target_root, item_id, workspace_entry):
        if not diagnostic.get("blocking"):
            continue
        other_item_id = diagnostic.get("item_id")
        conflicts.append(str(other_item_id) if other_item_id else str(diagnostic.get("work_item_locator", "unknown")))
    return conflicts

def collect_temp_paths(target_root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in OWNED_TEMP_ROOTS:
        candidate = target_root / relative
        if candidate.exists():
            paths.append(candidate)
    return paths

def cleanup_candidates(target_root: Path) -> tuple[list[Path], list[str]]:
    candidates: list[Path] = []
    unsafe: list[str] = []
    for temp_root in collect_temp_paths(target_root):
        if temp_root.is_file():
            unsafe.append(relative_to_root(temp_root, target_root))
            continue
        for child in sorted(temp_root.iterdir(), key=lambda path: path.name):
            marker = child / ".loom-owned" if child.is_dir() else child.with_name(f"{child.name}.loom-owned")
            if marker.exists():
                candidates.append(child)
            else:
                unsafe.append(relative_to_root(child, target_root))
    return candidates, unsafe

def expected_idle_item(expected_item: str | None) -> bool:
    return expected_item is None or expected_item == NO_ACTIVE_ITEM_ID

def base_workspace_payload(context: dict[str, Any], operation: str) -> dict[str, Any]:
    purity = purity_report_from_context(context)
    workspace_profile = workspace_profile_from_context(context)
    lifecycle_expectations = workspace_lifecycle_expectations(workspace_profile)
    return {
        "command": "workspace",
        "operation": operation,
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
            "exists": context["workspace_path"].exists(),
            "profile": workspace_profile,
        },
        "recovery": {
            "path": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
            "current_stop": context["current_stop"],
            "next_step": context["next_step"],
            "latest_validation_summary": context["latest_validation_summary"],
        },
        "checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": context["current_checkpoint"],
        },
        "purity": purity,
        "lifecycle_expectations": lifecycle_expectations,
        "missing_inputs": [],
        "fallback_to": None,
    }

def handle_checkpoint(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    context, errors = load_context_with_retained_idle_fallback(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "checkpoint",
                "checkpoint": args.stage,
                "result": "fallback",
                "summary": "checkpoint evaluation could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )
    return emit(checkpoint_payload(args.stage, context))

def handle_workspace(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            runtime_state_block_payload(
                command="workspace",
                operation=args.operation,
                runtime_state=runtime_state,
                summary="workspace lifecycle command is blocked because the Loom runtime state is inconsistent.",
            )
        )
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "workspace",
                "operation": args.operation,
                "result": "block",
                "summary": "workspace lifecycle command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "runtime_state": runtime_state,
            }
        )

    def emit_workspace(payload: dict[str, Any]) -> int:
        payload["runtime_state"] = runtime_state
        return emit(payload)

    payload = base_workspace_payload(context, args.operation)
    workspace_path = context["workspace_path"]
    purity = payload["purity"]

    if args.operation in {"locate", "attach"}:
        payload["result"] = "pass" if not purity["hard_failures"] else "block"
        payload["summary"] = (
            "workspace was attached by resolving an existing workspace_entry binding."
            if args.operation == "attach"
            else "workspace location was resolved from the fact chain."
        )
        if purity["hard_failures"]:
            payload["summary"] = (
                "workspace attachment resolved, but the workspace is not execution-ready."
                if args.operation == "attach"
                else "workspace location resolved, but the workspace is not execution-ready."
            )
            payload["missing_inputs"] = list(purity["hard_failures"])
        return emit_workspace(payload)

    if args.operation == "create":
        if purity["hard_failures"] and any("does not exist on disk" not in failure for failure in purity["hard_failures"]):
            payload["result"] = "block"
            payload["summary"] = "workspace creation is blocked until the current workspace state is clean."
            payload["missing_inputs"] = list(purity["hard_failures"])
            return emit_workspace(payload)

        created = False
        if not workspace_path.exists():
            workspace_path.mkdir(parents=True, exist_ok=True)
            created = True

        refreshed, refresh_errors = load_context_with_retained_idle_fallback(target_root, args.output, args.item)
        if refresh_errors:
            payload["result"] = "block"
            payload["summary"] = "workspace path was created, but the fact chain could not be reloaded."
            payload["missing_inputs"] = [f"fact-chain: {message}" for message in refresh_errors]
            return emit_workspace(payload)

        payload = base_workspace_payload(refreshed, args.operation)
        payload["created"] = created
        payload["result"] = "pass"
        payload["summary"] = "workspace semantics are established from `workspace_entry`."
        return emit_workspace(payload)

    if args.operation == "cleanup":
        owned_dirty, foreign_dirty = dirty_paths_by_owner(target_root)
        temp_paths, unsafe_temp_paths = cleanup_candidates(target_root)
        if foreign_dirty:
            payload["result"] = "block"
            payload["summary"] = "cleanup stopped because the workspace contains non-Loom changes."
            payload["missing_inputs"] = [f"non-loom residue: {path}" for path in foreign_dirty]
            return emit_workspace(payload)
        if unsafe_temp_paths:
            payload["result"] = "block"
            payload["summary"] = "cleanup stopped because a Loom temp root contains unmarked content."
            payload["missing_inputs"] = [f"unmarked temp content: {path}" for path in unsafe_temp_paths]
            payload["retained_paths"] = unsafe_temp_paths
            return emit_workspace(payload)

        removed: list[str] = []
        for temp_path in temp_paths:
            relative = relative_to_root(temp_path, target_root)
            tracked = git_tracked_files(target_root, relative)
            if tracked:
                payload["result"] = "block"
                payload["summary"] = "cleanup refused to delete tracked files from a Loom temporary path."
                payload["missing_inputs"] = [f"tracked temp path: {relative}"]
                return emit_workspace(payload)
            if temp_path.is_dir():
                shutil.rmtree(temp_path)
                removed.append(relative)
            else:
                temp_path.unlink()
                removed.append(relative)

        if owned_dirty and not removed:
            payload["result"] = "block"
            payload["summary"] = "cleanup found Loom temporary residue in git status, but no owned temp paths could be removed."
            payload["missing_inputs"] = [f"owned temp residue: {path}" for path in owned_dirty]
            return emit_workspace(payload)

        payload["removed_paths"] = removed
        payload["result"] = "pass"
        payload["summary"] = "cleanup removed Loom-owned temporary residue." if removed else "cleanup found no Loom-owned temporary residue."
        payload["purity"] = purity_report_from_context(context)
        return emit_workspace(payload)

    cleanup_payload = base_workspace_payload(context, "cleanup")
    owned_dirty, foreign_dirty = dirty_paths_by_owner(target_root)
    if foreign_dirty:
        cleanup_payload["result"] = "block"
        cleanup_payload["summary"] = "retire cannot proceed because cleanup is blocked by non-Loom changes."
        cleanup_payload["missing_inputs"] = [f"non-loom residue: {path}" for path in foreign_dirty]
        return emit_workspace(cleanup_payload)

    temp_paths, unsafe_temp_paths = cleanup_candidates(target_root)
    if unsafe_temp_paths:
        cleanup_payload["result"] = "block"
        cleanup_payload["summary"] = "retire cannot proceed because cleanup would touch unmarked temp content."
        cleanup_payload["missing_inputs"] = [f"unmarked temp content: {path}" for path in unsafe_temp_paths]
        cleanup_payload["retained_paths"] = unsafe_temp_paths
        return emit_workspace(cleanup_payload)

    removed: list[str] = []
    for temp_path in temp_paths:
        relative = relative_to_root(temp_path, target_root)
        tracked = git_tracked_files(target_root, relative)
        if tracked:
            cleanup_payload["result"] = "block"
            cleanup_payload["summary"] = "retire cannot proceed because cleanup would need to delete tracked files."
            cleanup_payload["missing_inputs"] = [f"tracked temp path: {relative}"]
            return emit_workspace(cleanup_payload)
        if temp_path.is_dir():
            shutil.rmtree(temp_path)
            removed.append(relative)
        else:
            temp_path.unlink()
            removed.append(relative)

    payload = base_workspace_payload(context, "retire")
    payload["result"] = "pass"
    payload["summary"] = "workspace retire completed local cleanup without writing versioned recovery or status carriers."
    payload["retired"] = True
    payload["retire_scope"] = "local_only"
    payload["versioned_carrier_updates"] = []
    payload["removed_paths"] = removed
    return emit_workspace(payload)

def handle_purity(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            runtime_state_block_payload(
                command="purity-check",
                runtime_state=runtime_state,
                summary="purity-check is blocked because the Loom runtime state is inconsistent.",
            )
        )
    context, errors = load_context_with_retained_idle_fallback(target_root, args.output, args.item)
    if errors:
        payload = {
            "command": "purity-check",
            "result": "block",
            "summary": "purity-check could not read a valid Loom fact chain.",
            "missing_inputs": [f"fact-chain: {message}" for message in errors],
            "fallback_to": "admission",
            "runtime_state": runtime_state,
            "purity": {
                "state": "failed",
                "hard_failures": [f"fact-chain: {message}" for message in errors],
                "report_only": [
                    "branch purity is report-only in v1",
                    "PR purity is report-only in v1",
                ],
            },
        }
        return emit(payload)

    purity = purity_report_from_context(context)
    result = "pass" if not purity["hard_failures"] else "block"
    summary = "workspace purity is compatible with continued execution." if result == "pass" else "workspace purity requires cleanup or re-scoping before review."
    payload = {
        "command": "purity-check",
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
        },
        "checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": context["current_checkpoint"],
        },
        "purity": purity,
        "result": result,
        "summary": summary,
        "missing_inputs": list(purity["hard_failures"]),
        "fallback_to": "admission" if purity["hard_failures"] else None,
        "runtime_state": runtime_state,
    }
    return emit(payload)

def work_item_audit_finding_from_diagnostic(diagnostic: dict[str, Any]) -> dict[str, Any]:
    classification = str(diagnostic.get("classification") or "unknown")
    freshness = str(diagnostic.get("freshness") or "unknown")
    audit_blocking = bool(diagnostic.get("blocking")) or classification == "carrier_closeout_required"
    kind_by_classification = {
        "stale_carrier": "unrelated_terminal_stale_carrier",
        "carrier_closeout_required": "host_complete_carrier_not_terminalized",
        "shared_workspace_conflict": "multiple_active_work_items",
    }
    classifier_by_classification = {
        "stale_carrier": "stale_carrier",
        "carrier_closeout_required": "carrier_refresh_needed",
        "shared_workspace_conflict": "carrier_truth_conflict",
    }
    next_action_by_classification = {
        "stale_carrier": "leave unrelated terminal carriers out of the current Work Item, or retire them through their own flow if they still appear active.",
        "carrier_closeout_required": "run the reported carrier closeout-sync command, then rerun work-item audit before starting the next Work Item.",
        "shared_workspace_conflict": "move one active Work Item to its own branch/worktree or close its recovery path before continuing.",
    }
    finding = {
        "kind": kind_by_classification.get(classification, "active_carrier_drift"),
        "item_id": diagnostic.get("item_id"),
        "classification": classification,
        "classifier": classifier_by_classification.get(classification, "carrier_truth_conflict" if audit_blocking else "not_applicable"),
        "freshness": freshness,
        "blocking": audit_blocking,
        "purity_blocking": bool(diagnostic.get("blocking")),
        "work_item_locator": diagnostic.get("work_item_locator"),
        "binding_locator": diagnostic.get("binding_locator"),
        "checkpoint": diagnostic.get("checkpoint"),
        "next_action": next_action_by_classification.get(
            classification,
            str(diagnostic.get("recommended_remediation") or "inspect the retained Work Item carrier before continuing."),
        ),
    }
    if diagnostic.get("next_command"):
        finding["next_command"] = diagnostic.get("next_command")
    if diagnostic.get("host_truth"):
        finding["host_truth"] = diagnostic.get("host_truth")
    return finding

def work_item_audit_payload(target_root: Path, output_relative: str, expected_item: str | None) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return runtime_state_block_payload(
            command="work-item-audit",
            runtime_state=runtime_state,
            summary="work-item audit is blocked because the Loom runtime state is inconsistent.",
        )

    context, errors = load_context(target_root, output_relative, expected_item)
    if errors:
        return {
            "command": "work-item-audit",
            "schema_version": "loom-active-carrier-audit/v1",
            "result": "block",
            "summary": "work-item audit could not read a valid Loom fact chain.",
            "missing_inputs": [f"fact-chain: {message}" for message in errors],
            "fallback_to": "admission",
            "runtime_state": runtime_state,
            "findings": [],
            "current_item": None,
            "shadow_freshness": {"status": "not_checked"},
        }

    assert context is not None
    purity = purity_report_from_context(context)
    diagnostics = list(purity.get("active_workspace_diagnostics", []))
    diagnostic_findings = [work_item_audit_finding_from_diagnostic(entry) for entry in diagnostics if isinstance(entry, dict)]
    diagnostic_counts: dict[str, int] = {}
    for finding in diagnostic_findings:
        classification = str(finding.get("classification") or "unknown")
        diagnostic_counts[classification] = diagnostic_counts.get(classification, 0) + 1

    current_checkpoint = str(context.get("current_checkpoint") or "")
    current_item = {
        "kind": "current_item_legitimate_active_carrier"
        if current_checkpoint not in TERMINAL_CHECKPOINTS
        else "current_item_terminal_carrier",
        "item_id": context["item_id"],
        "workspace_entry": context["workspace_entry"],
        "checkpoint": current_checkpoint,
        "blocking": False,
        "classifier": "not_applicable",
        "next_action": "continue with the selected Work Item after resolving any blocking audit findings.",
    }

    shadow_actions = refresh_shadow_evidence_actions(target_root)
    shadow_blocking = [
        action
        for action in shadow_actions
        if action.get("kind") == "shadow-evidence" and action.get("status") in {"block", "refresh-needed"}
    ]
    shadow_freshness = {
        "schema_version": "loom-work-item-audit-shadow-freshness/v1",
        "result": "block" if shadow_blocking else "pass",
        "actions": shadow_actions,
        "blocking_paths": [action.get("path") for action in shadow_blocking if action.get("path")],
        "next_action": "refresh shadow evidence source hashes with the supported carrier refresh/write path, then rerun work-item audit."
        if shadow_blocking
        else "no shadow freshness action required.",
    }

    blocking_findings = [finding for finding in diagnostic_findings if finding.get("blocking")]
    if shadow_blocking:
        blocking_findings.append(
            {
                "kind": "current_item_shadow_source_hash_drift",
                "item_id": context["item_id"],
                "classification": "shadow_source_hash_drift",
                "classifier": "shadow_stale",
                "freshness": "refresh_needed",
                "blocking": True,
                "paths": [action.get("path") for action in shadow_blocking if action.get("path")],
                "next_action": "refresh shadow evidence source hashes with the supported carrier refresh/write path, then rerun work-item audit.",
            }
        )

    result = "block" if blocking_findings else "pass"
    nonblocking_samples = [finding for finding in diagnostic_findings if not finding.get("blocking")][:20]
    fallback_to = None
    if blocking_findings:
        classifiers = {str(finding.get("classifier") or "") for finding in blocking_findings}
        fallback_to = "carrier_closeout_sync" if "carrier_refresh_needed" in classifiers else "carrier_refresh"
    return {
        "command": "work-item-audit",
        "schema_version": "loom-active-carrier-audit/v1",
        "result": result,
        "summary": (
            "work-item audit found active carrier drift that must be resolved before starting work."
            if result == "block"
            else "work-item audit found no blocking active carrier drift before starting work."
        ),
        "missing_inputs": [
            f"{finding.get('kind')}: {finding.get('item_id') or ','.join(str(path) for path in finding.get('paths', []))}"
            for finding in blocking_findings
        ],
        "fallback_to": fallback_to,
        "runtime_state": runtime_state,
        "current_item": current_item,
        "findings": blocking_findings,
        "nonblocking_samples": nonblocking_samples,
        "diagnostic_summary": {
            "total": len(diagnostic_findings),
            "blocking": len(blocking_findings),
            "by_classification": diagnostic_counts,
            "nonblocking_samples_limited_to": 20,
        },
        "shadow_freshness": shadow_freshness,
        "purity_summary": {
            "state": purity.get("state"),
            "hard_failure_count": len(purity.get("hard_failures", [])),
            "report_only_count": len(purity.get("report_only", [])),
        },
        "next_actions": [finding.get("next_action") for finding in blocking_findings if finding.get("next_action")],
    }

def handle_work_item_audit(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    return emit(work_item_audit_payload(target_root, args.output, args.item))

def handle_fact_chain(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    report, errors = load_fact_chain_report(target_root, args.output)
    if errors:
        return emit(
            {
                "command": "fact-chain",
                "result": "block",
                "summary": "fact-chain command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                **fact_chain_error_contract(errors, output_relative=args.output),
            }
        )

    item_id = report["fact_chain"]["entry_points"]["current_item_id"]
    if args.item and args.item != item_id:
        return emit(
            {
                "command": "fact-chain",
                "result": "block",
                "summary": "fact-chain command found an item mismatch.",
                "missing_inputs": [f"current item mismatch: expected `{args.item}`, got `{item_id}`"],
                "fallback_to": "admission",
            }
        )

    blocking_failures = report_blocking_failures(report)
    result = "block" if blocking_failures else "pass"
    return emit(
        {
            "command": "fact-chain",
            "result": result,
            "summary": (
                "fact chain can be read and validated from a single entry."
                if result == "pass"
                else "fact chain is readable, but provenance or derived-surface drift is blocking."
            ),
            "missing_inputs": report_blocking_messages(report),
            "fallback_to": "admission" if result == "block" else None,
            "provenance": report_provenance(report),
            "recovery_readiness": report_recovery_readiness(report),
            "derived_status_surface": report.get("derived_status_surface"),
            "blocking_failures": blocking_failures,
            "report": report,
        }
    )

def report_execution_ledger(report: dict[str, Any]) -> dict[str, Any]:
    ledger = report.get("execution_ledger")
    if isinstance(ledger, dict):
        return ledger
    return {
        "authoritative_carrier": "recovery_entry",
        "status": "missing",
        "completeness": "missing",
        "freshness": "missing",
        "fields": {},
        "missing_fields": ["execution_ledger"],
        "forbidden_authored_fields": [],
    }

def governance_lint_kind_from_failure(failure: dict[str, Any]) -> str:
    text = " ".join(
        str(failure.get(field, ""))
        for field in ("category", "kind", "surface", "message", "summary")
    ).lower()
    if "companion" in text or "interop" in text:
        return "companion_boundary_bypass"
    if "hardcod" in text:
        return "core_hardcoding_leak"
    if "stale" in text or "freshness" in text or "head" in text:
        return "evidence_stale"
    return "fact_chain_broken"

def flow_governance_lint_status(
    context: dict[str, Any],
    *,
    surface: str,
    repo_specific_requirements: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bindings = {
        "item_id": context["item_id"],
        "head_sha": git_head_sha(context["target_root"]),
        "scope": context["scope"],
        "reviewed_head_sha": None,
        "pr_ref": None,
    }
    blocking_results: list[dict[str, Any]] = []
    advisory_results: list[dict[str, Any]] = []
    repo_specific_results: list[dict[str, Any]] = []
    for index, failure in enumerate(report_blocking_failures(context["report"]), start=1):
        if not isinstance(failure, dict):
            continue
        kind = governance_lint_kind_from_failure(failure)
        summary = str(
            failure.get("message")
            or failure.get("summary")
            or failure.get("kind")
            or "fact-chain blocking failure"
        )
        blocking_results.append(
            {
                "schema_version": GOVERNANCE_LINT_RESULT_SCHEMA,
                "id": f"fact_chain_blocking_{index}",
                "kind": kind,
                "strength": "blocking",
                "surface": surface,
                "subject": failure.get("carrier") or failure.get("field") or "fact_chain",
                "summary": summary,
                "mapped_failure": {
                    "category": failure.get("category") or "drift",
                    "kind": failure.get("kind") or kind,
                },
                "provenance": {
                    "source_layer": "fact_chain",
                    "source_owner": "loom",
                    "source_locator": failure.get("path") or failure.get("locator"),
                    "source_binding": failure.get("field") or failure.get("carrier") or "fact_chain",
                    "freshness": failure.get("freshness") or "stale",
                },
                "bindings": bindings,
                "evidence_freshness": failure.get("freshness") or "stale",
                "fallback_to": failure.get("fallback_to") or "admission",
            }
        )

    if isinstance(repo_specific_requirements, dict):
        source_locator = repo_specific_requirements.get("source_locator")
        for field in ("blocking_requirements", "advisory_requirements"):
            entries = repo_specific_requirements.get(field)
            if not isinstance(entries, list):
                continue
            for index, entry in enumerate(entries, start=1):
                if not isinstance(entry, dict):
                    continue
                enforcement = entry.get("enforcement")
                result = {
                    "schema_version": GOVERNANCE_LINT_RESULT_SCHEMA,
                    "id": f"repo_specific_{field}_{index}",
                    "kind": "companion_boundary_bypass",
                    "strength": "repo_specific",
                    "surface": surface,
                    "subject": "repo_companion_requirement",
                    "summary": str(entry.get("summary") or entry.get("id") or "repo companion requirement"),
                    "mapped_failure": {
                        "category": "gate_failure",
                        "kind": "repo_specific_requirement",
                    },
                    "provenance": {
                        "source_layer": "repo_companion",
                        "source_owner": "repo",
                        "source_locator": source_locator,
                        "source_binding": entry.get("id") or "repo_specific_requirements",
                        "freshness": "current",
                    },
                    "bindings": bindings,
                    "evidence_freshness": "current",
                    "fallback_to": repo_specific_requirements.get("fallback_to") or repo_specific_default_fallback(surface),
                    "enforcement": enforcement,
                }
                repo_specific_results.append(result)
                if enforcement == "blocking":
                    blocking_results.append(result)
                elif enforcement == "advisory":
                    advisory_results.append(result)

    result = "block" if blocking_results else "pass"
    return {
        "schema_version": GOVERNANCE_LINT_STATUS_SCHEMA,
        "surface": surface,
        "result": result,
        "result_summary": (
            "Governance Lint blocks this surface because derived lint evidence found blocking failures."
            if result == "block"
            else "Governance Lint found no blocking derived lint evidence for this surface."
        ),
        "blocking_results": blocking_results,
        "advisory_results": advisory_results,
        "repo_specific_results": repo_specific_results,
        "not_applicable_results": [],
        "mapped_failures": [entry["mapped_failure"] for entry in blocking_results],
        "provenance": [
            entry["provenance"]
            for entry in [*blocking_results, *advisory_results, *repo_specific_results]
        ],
    }

def governance_lint_missing_inputs(payload: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    entries = payload.get("blocking_results")
    if not isinstance(entries, list):
        return messages
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        summary = entry.get("summary") or entry.get("kind") or "blocking lint result"
        message = f"governance lint {entry.get('kind', 'unknown')}: {summary}"
        if message not in messages:
            messages.append(message)
    return messages

def governance_lint_fallback(payload: dict[str, Any]) -> str | None:
    entries = payload.get("blocking_results")
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        fallback_to = entry.get("fallback_to")
        if isinstance(fallback_to, str) and fallback_to:
            return fallback_to
    return None

def handle_runtime_evidence(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            {
                "command": "runtime-evidence",
                "result": "block",
                "summary": "runtime-evidence is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": runtime_state["missing_inputs"],
                "fallback_to": runtime_state["fallback_to"],
                "runtime_state": runtime_state,
            }
        )
    report, errors = load_fact_chain_report(target_root, args.output)
    if errors:
        return emit(
            {
                "command": "runtime-evidence",
                "result": "block",
                "summary": "runtime-evidence command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "runtime_state": runtime_state,
            }
        )

    item_id = report["fact_chain"]["entry_points"]["current_item_id"]
    if args.item and args.item != item_id:
        return emit(
            {
                "command": "runtime-evidence",
                "result": "block",
                "summary": "runtime-evidence command found an item mismatch.",
                "missing_inputs": [f"current item mismatch: expected `{args.item}`, got `{item_id}`"],
                "fallback_to": "admission",
                "runtime_state": runtime_state,
            }
        )

    fields, missing_inputs = runtime_evidence_from_report(report)

    result = "pass" if not missing_inputs else "block"
    summary = (
        "runtime evidence entries are readable and distinguish `present` from `not_applicable`."
        if result == "pass"
        else "runtime evidence entries are incomplete or inconsistent."
    )
    return emit(
        {
            "command": "runtime-evidence",
            "item_id": item_id,
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": "admission" if missing_inputs else None,
            "runtime_evidence": fields,
            "runtime_state": runtime_state,
        }
    )

def handle_state_check(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            {
                "command": "state-check",
                "result": "block",
                "summary": "state-check is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": runtime_state["missing_inputs"],
                "fallback_to": runtime_state["fallback_to"],
                "runtime_state": runtime_state,
            }
        )
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "state-check",
                "result": "block",
                "summary": "state-check could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "runtime_state": runtime_state,
            }
        )
    payload = state_check_payload(context)
    payload["runtime_state"] = runtime_state
    return emit(payload)

def handle_runtime_state(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    return emit(
        {
            "command": "runtime-state",
            "result": runtime_state["result"],
            "summary": runtime_state["summary"],
            "missing_inputs": runtime_state["missing_inputs"],
            "fallback_to": runtime_state["fallback_to"],
            "runtime_state": runtime_state,
        }
    )

def adoption_verify_payload(target_root: Path, output_relative: str, expected_item: str | None) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    context, context_errors = load_context(target_root, output_relative, expected_item)
    pr_template, pr_template_errors = check_pr_template(target_root)
    governance_surface = build_governance_surface(target_root)

    if context_errors:
        if is_idle_context_errors(context_errors) and expected_idle_item(expected_item):
            missing_inputs: list[str] = []
            if runtime_state.get("result") != "pass":
                missing_inputs.extend(str(message) for message in runtime_state.get("missing_inputs", []))
            missing_inputs.extend(pr_template_errors)
            result = "pass" if not missing_inputs else "block"
            return {
                "command": "adopt",
                "operation": "verify",
                "schema_version": "loom-adoption-verify/v1",
                "result": result,
                "summary": (
                    "adoption verify is satisfied for an idle repository with no active Work Item."
                    if result == "pass"
                    else "idle adoption verify found blocking runtime or template gaps."
                ),
                "missing_inputs": missing_inputs,
                "fallback_to": None if result == "pass" else "adoption",
                "runtime_state": runtime_state,
                "governance_surface": governance_surface,
                "pr_template": pr_template,
                "producer_consumer_roundtrip": {
                    "producer": {
                        "status": "not_applicable",
                        "body_sections": [],
                    },
                    "consumer": {
                        "result": "not_applicable",
                        "summary": "idle repositories have no active adoption PR body to validate.",
                        "missing_inputs": [],
                    },
                    "bypass_check": {
                        "scenario": "Review Artifacts section omitted while repository is idle",
                        "result": "pass",
                        "consumer_result": "block",
                        "missing_inputs": ["idle repository has no active adoption review artifacts"],
                    },
                },
                "idle_repository": {
                    "result": "pass",
                    "current_item_id": NO_ACTIVE_ITEM_ID,
                    "fact_chain_error": IDLE_FACT_CHAIN_ERROR,
                },
            }
        return {
            "command": "adopt",
            "operation": "verify",
            "schema_version": "loom-adoption-verify/v1",
            "result": "block",
            "summary": "adoption verify could not read the Loom fact chain.",
            "missing_inputs": [f"fact-chain: {message}" for message in context_errors],
            "fallback_to": "adoption",
            "runtime_state": runtime_state,
            "governance_surface": governance_surface,
            "pr_template": pr_template,
        }

    produced_body = render_adoption_pr_body(context)
    produced_validation = validate_adoption_pr_body(produced_body, target_root=target_root)
    bypass_body = produced_body.replace("\n## Review Artifacts\n\n", "\n## Omitted Review Artifacts\n\n", 1)
    bypass_validation = validate_adoption_pr_body(bypass_body, target_root=target_root)

    review_record, review_path, review_errors = load_review_record(target_root, context["item_id"], context["review_entry"])
    _, suite_path_values = adoption_suite_path_decision_presence(context)
    suite_not_applicable = bool(suite_path_values) and suite_path_values <= {"not_applicable"}
    if suite_not_applicable:
        spec_review_record = None
        spec_review_path = "not_applicable"
        spec_review_errors: list[str] = []
    else:
        spec_review_record, spec_review_path, spec_review_errors = load_review_record(
            target_root,
            context["item_id"],
            default_spec_review_path(context["item_id"]),
        )
    review_missing = list(review_errors)
    if review_record is None and not review_errors:
        review_missing.append(f"missing review artifact: {review_path}")
    spec_review_missing = list(spec_review_errors)
    if spec_review_record is None and not spec_review_errors and not suite_not_applicable:
        spec_review_missing.append(f"missing spec review artifact: {spec_review_path}")

    missing_inputs: list[str] = []
    if runtime_state.get("result") != "pass":
        missing_inputs.extend(str(message) for message in runtime_state.get("missing_inputs", []))
    missing_inputs.extend(pr_template_errors)
    missing_inputs.extend(produced_validation["missing_inputs"])
    missing_inputs.extend(review_missing)
    missing_inputs.extend(spec_review_missing)
    if bypass_validation["result"] != "block":
        missing_inputs.append("consumer bypass check failed: removing Review Artifacts must block")

    control_plane = governance_surface.get("governance_control_plane")
    maturity = control_plane.get("maturity") if isinstance(control_plane, dict) else {}
    target_level = maturity.get("next") if isinstance(maturity, dict) and isinstance(maturity.get("next"), str) else maturity.get("current") if isinstance(maturity, dict) and isinstance(maturity.get("current"), str) else None
    decisions = adoption_decisions_payload(target_root, target_level=target_level, maturity=maturity if isinstance(maturity, dict) else {})
    guided_plan = guided_adoption_plan_payload(decisions)
    generation = companion_generation_payload(target_root, decisions, dry_run=True)
    closure = judgment_closure_payload(target_root, decisions, generation, governance_surface)
    consumption = generated_companion_consumption_payload(target_root, context["item_id"], governance_surface)
    missing_inputs.extend(closure["missing_inputs"])
    missing_inputs.extend(consumption["missing_inputs"])

    result = "pass" if not missing_inputs else "block"
    return {
        "command": "adopt",
        "operation": "verify",
        "schema_version": "loom-adoption-verify/v1",
        "result": result,
        "summary": (
            "downstream adoption producer/consumer round-trip is valid."
            if result == "pass"
            else "downstream adoption round-trip has blocking contract gaps."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "adoption",
        "runtime_state": runtime_state,
        "governance_surface": governance_surface,
        "pr_template": pr_template,
        "producer_consumer_roundtrip": {
            "producer": {
                "status": "pass",
                "body_sections": list(ADOPTION_PR_BODY_SECTIONS),
            },
            "consumer": produced_validation,
            "bypass_check": {
                "scenario": "Review Artifacts section omitted",
                "result": "pass" if bypass_validation["result"] == "block" else "block",
                "consumer_result": bypass_validation["result"],
                "missing_inputs": bypass_validation["missing_inputs"],
            },
        },
        "reviews": {
            "implementation": {
                "path": review_path,
                "status": "present" if review_record is not None and not review_errors else "missing",
            },
            "spec": {
                "path": spec_review_path,
                "status": "not_applicable" if suite_not_applicable else "present" if spec_review_record is not None and not spec_review_errors else "missing",
            },
        },
        "adoption_decisions": decisions,
        "guided_adoption_plan": guided_plan,
        "companion_generation": generation,
        "generated_companion_consumption": consumption,
        "judgment_closure": closure,
    }

def adversarial_check_summary(check_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    raw_result = payload.get("result")
    result = raw_result if raw_result in {"pass", "block", "warn", "not_applicable"} else "block"
    missing_inputs = payload.get("missing_inputs")
    return {
        "id": check_id,
        "result": result,
        "schema_version": payload.get("schema_version"),
        "operation": payload.get("operation"),
        "summary": str(payload.get("summary") or f"{check_id} returned {result}"),
        "missing_inputs": [str(message) for message in missing_inputs] if isinstance(missing_inputs, list) else [],
        "fallback_to": payload.get("fallback_to"),
    }

def adversarial_adoption_evidence_payload(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    *,
    record: bool,
) -> dict[str, Any]:
    head_sha = git_head_sha(target_root)
    governance_surface = build_governance_surface(target_root)
    control_plane = governance_surface.get("governance_control_plane")
    maturity = control_plane.get("maturity") if isinstance(control_plane, dict) else {}
    current_maturity = maturity.get("current") if isinstance(maturity, dict) else None
    adoption = adoption_verify_payload(target_root, output_relative, expected_item)
    runtime_parity = runtime_parity_payload(
        target_root=target_root,
        output_relative=output_relative,
        expected_item=expected_item,
    )
    checks = [
        adversarial_check_summary("adopt_verify", adoption),
        adversarial_check_summary("runtime_parity", runtime_parity),
        {
            "id": "strong_maturity",
            "result": "pass" if current_maturity == "strong" else "block",
            "schema_version": "loom-governance-maturity/v1",
            "operation": "status",
            "summary": (
                "governance profile is at strong maturity."
                if current_maturity == "strong"
                else "governance profile must reach strong maturity before blocking rollout."
            ),
            "missing_inputs": [] if current_maturity == "strong" else [f"current governance maturity is `{current_maturity or 'unknown'}`"],
            "fallback_to": None if current_maturity == "strong" else "adoption",
            "evidence": {"current": current_maturity},
        },
    ]
    missing_inputs = [
        str(message)
        for check in checks
        if check.get("result") != "pass"
        for message in (check.get("missing_inputs") if isinstance(check.get("missing_inputs"), list) else [])
    ]
    if not head_sha:
        missing_inputs.append("current git head is unavailable")

    result = "pass" if not missing_inputs else "block"
    payload: dict[str, Any] = {
        "command": "adopt",
        "operation": "adversarial-test",
        "schema_version": ADVERSARIAL_ADOPTION_EVIDENCE_SCHEMA,
        "result": result,
        "summary": (
            "adversarial adoption evidence is fresh and satisfies strong-governance rollout checks."
            if result == "pass"
            else "adversarial adoption evidence is blocked by missing or failing strong-governance checks."
        ),
        "target": str(target_root),
        "branch": git_branch(target_root),
        "head_sha": head_sha,
        "generated_at": current_iso_timestamp(),
        "evidence_locator": ADVERSARIAL_ADOPTION_EVIDENCE_LOCATOR,
        "record": {
            "requested": record,
            "written": False,
            "locator": ADVERSARIAL_ADOPTION_EVIDENCE_LOCATOR,
        },
        "checks": checks,
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
        "fallback_to": None if result == "pass" else "adoption",
    }
    if not record:
        return payload

    evidence_path, path_errors = resolve_repo_relative_path(
        target_root,
        ADVERSARIAL_ADOPTION_EVIDENCE_LOCATOR,
        label="adversarial adoption evidence locator",
    )
    if path_errors or evidence_path is None:
        payload["result"] = "block"
        payload["summary"] = "adversarial adoption evidence could not be written safely."
        payload["missing_inputs"] = list(dict.fromkeys([*payload["missing_inputs"], *path_errors]))
        payload["fallback_to"] = "adoption"
        return payload
    try:
        payload["record"]["written"] = True
        write_json_file(evidence_path, payload)
    except OSError as exc:
        payload["result"] = "block"
        payload["summary"] = "adversarial adoption evidence could not be written."
        payload["record"]["written"] = False
        payload["missing_inputs"] = list(dict.fromkeys([*payload["missing_inputs"], f"failed to write {ADVERSARIAL_ADOPTION_EVIDENCE_LOCATOR}: {exc.strerror or exc}"]))
        payload["fallback_to"] = "adoption"
    return payload

def handle_adopt(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    if args.operation == "adversarial-test":
        return emit(
            adversarial_adoption_evidence_payload(
                target_root,
                args.output,
                args.item,
                record=args.record,
            )
        )
    return emit(adoption_verify_payload(target_root, args.output, args.item))

def terminal_metadata_from_host_truth(host_truth: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    issue_number: int | None = None
    pr_number: int | None = None
    merge_commit: str | None = None
    target_branch: str | None = None
    closed_at: str | None = None
    terminal_state = str(host_truth.get("terminal_state") or "closed_out")
    for entry in host_truth.get("evidence", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("kind") == "github_issue" and isinstance(entry.get("number"), int):
            issue_number = entry.get("number")
            if isinstance(entry.get("closedAt"), str):
                closed_at = entry.get("closedAt")
        if entry.get("kind") == "github_pr" and isinstance(entry.get("number"), int):
            pr_number = entry.get("number")
            merge_commit_entry = entry.get("mergeCommit")
            if isinstance(merge_commit_entry, dict) and isinstance(merge_commit_entry.get("oid"), str):
                merge_commit = merge_commit_entry.get("oid")
            if isinstance(entry.get("baseRefName"), str):
                target_branch = entry.get("baseRefName")
            if isinstance(entry.get("mergedAt"), str):
                closed_at = entry.get("mergedAt")
    metadata = {
        "terminal_state": terminal_state,
        "issue": str(issue_number) if issue_number is not None else "not_applicable",
        "pr": str(pr_number) if pr_number is not None else "not_applicable",
        "merge_commit": merge_commit or "not_applicable",
        "target_branch": target_branch or "not_applicable",
        "closed_at": closed_at or "not_applicable",
        "evidence_locator": ";".join(str(locator) for locator in host_truth.get("locators", [])) or "host-readback",
    }
    missing_inputs: list[str] = []
    for field_name in ("issue", "pr", "merge_commit", "target_branch", "closed_at", "evidence_locator"):
        if metadata[field_name] == "not_applicable":
            missing_inputs.append(f"{field_name.replace('_', '-')} is required for safe carrier repair")
    return metadata, missing_inputs

def render_idle_status_surface(*, read_entry: str, output_relative: str) -> str:
    lines = [
        "# Current Status",
        "",
        "## Derived Fact Chain View",
        "",
        "- Item ID: no_active_item",
        "- Goal: not_applicable",
        "- Scope: not_applicable",
        "- Execution Path: not_applicable",
        "- Workspace Entry: not_applicable",
        "- Recovery Entry: not_applicable",
        "- Review Entry: not_applicable",
        "- Validation Entry: not_applicable",
        "- Closing Condition: not_applicable",
        "- Current Checkpoint: not_applicable",
        "- Current Stop: not_applicable",
        "- Next Step: not_applicable",
        "- Blockers: not_applicable",
        "- Latest Validation Summary: not_applicable",
        "- Recovery Boundary: not_applicable",
        "- Current Lane: not_applicable",
        "",
        "## Runtime Evidence",
        "",
        "- Run Entry: not_applicable",
        "- Logs Entry: not_applicable",
        "- Diagnostics Entry: not_applicable",
        "- Verification Entry: not_applicable",
        "- Lane Entry: not_applicable",
        "",
        "## Sources",
        "",
        "- Static Truth: not_applicable",
        "- Dynamic Truth: not_applicable",
        f"- Locator Truth: {output_relative}",
        f"- Fact Chain CLI: {read_entry}",
    ]
    return "\n".join(lines).rstrip() + "\n"

def load_idle_init_result_payload(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json_file(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, [f"invalid init-result JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, ["init-result must be a JSON object"]
    return payload, []

def write_idle_init_result(path: Path, payload: dict[str, Any], *, read_entry: str) -> None:
    fact_chain = payload.get("fact_chain")
    if not isinstance(fact_chain, dict):
        fact_chain = {}
        payload["fact_chain"] = fact_chain
    fact_chain["mode"] = "idle"
    fact_chain["read_entry"] = read_entry
    fact_chain["entry_points"] = {
        "current_item_id": "no_active_item",
        "work_item": "not_applicable",
        "recovery_entry": "not_applicable",
        "status_surface": ".loom/status/current.md",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def carrier_repair_candidate(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    issue_number: int | None,
) -> tuple[dict[str, Any] | None, list[str], list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    context, context_errors = load_context(target_root, output_relative, expected_item)
    if context_errors:
        diagnostics.append(
            {
                "kind": "fact-chain-unavailable",
                "missing_inputs": context_errors,
                "repairable": False,
            }
        )
        if expected_item is not None or issue_number is not None:
            return None, [f"fact-chain: {message}" for message in context_errors], diagnostics
        return None, [], diagnostics
    if context["current_checkpoint"] in TERMINAL_CHECKPOINTS:
        diagnostics.append(
            {
                "kind": "current-carrier-terminal",
                "item_id": context["item_id"],
                "checkpoint": context["current_checkpoint"],
                "repairable": False,
            }
        )
        return None, [], diagnostics

    missing_inputs: list[str] = []
    if issue_number is None:
        diagnostics.append(
            {
                "kind": "retained-item-lookup",
                "issue": None,
                "item_id": None,
                "diagnostics": [],
                "missing_inputs": ["issue selector is required for safe carrier repair"],
            }
        )
        return None, ["issue selector is required for safe carrier repair"], diagnostics
    if issue_number is not None:
        lookup = closeout_retained_item_lookup(target_root, issue_number)
        missing_inputs.extend(retained_item_lookup_missing_inputs(lookup))
        lookup_item = retained_item_lookup_id(lookup)
        if not missing_inputs and lookup_item and lookup_item != context["item_id"]:
            missing_inputs.append(
                f"retained-item lookup resolved issue #{issue_number} to `{lookup_item}`, but current fact-chain item is `{context['item_id']}`"
            )
        if not missing_inputs and lookup_item is None:
            missing_inputs.append(f"retained-item lookup found no Work Item for issue #{issue_number}")
        diagnostics.append(
            {
                "kind": "retained-item-lookup",
                "issue": issue_number,
                "item_id": lookup_item,
                "diagnostics": lookup.get("diagnostics", []),
                "missing_inputs": retained_item_lookup_missing_inputs(lookup),
            }
        )
        if missing_inputs:
            return None, missing_inputs, diagnostics

    default_owner, default_repo = detect_github_repo(target_root)
    carrier_texts = [
        context["work_item_path"].read_text(encoding="utf-8"),
        context["recovery_path"].read_text(encoding="utf-8"),
    ]
    extracted_issue_numbers: set[int] = set()
    for text in carrier_texts:
        extracted_issue_numbers.update(int(match.group("number")) for match in GITHUB_ISSUE_URL_RE.finditer(text))
        extracted_issue_numbers.update(int(match.group("number")) for match in GITHUB_ISSUE_REF_RE.finditer(text))
    if not extracted_issue_numbers:
        missing_inputs.append(f"carrier text does not contain GitHub issue #{issue_number}")
    elif extracted_issue_numbers != {issue_number}:
        missing_inputs.append(
            "carrier GitHub issue locators must resolve exactly to "
            f"#{issue_number}; found {', '.join(f'#{number}' for number in sorted(extracted_issue_numbers))}"
        )
    if missing_inputs:
        diagnostics.append(
            {
                "kind": "host-locator-ownership",
                "issue": issue_number,
                "extracted_issue_numbers": sorted(extracted_issue_numbers),
                "missing_inputs": missing_inputs,
            }
        )
        return None, missing_inputs, diagnostics
    host_context = extract_github_host_context(
        target_root,
        carrier_texts,
        default_owner=default_owner,
        default_repo=default_repo,
    )
    if host_context is None:
        diagnostics.append(
            {
                "kind": "host-context-unavailable",
                "item_id": context["item_id"],
                "repairable": False,
            }
        )
        return None, [], diagnostics
    if host_context.get("issue_number") != issue_number:
        return (
            None,
            [f"host context issue #{host_context.get('issue_number')} does not match requested issue #{issue_number}"],
            diagnostics,
        )
    host_truth = github_host_completion_truth(target_root, host_context, {})
    diagnostics.append(
        {
            "kind": "host-completion-truth",
            "item_id": context["item_id"],
            "host_truth": host_truth,
        }
    )
    if host_truth.get("errors"):
        return None, [f"host truth: {message}" for message in host_truth.get("errors", [])], diagnostics
    if host_truth.get("complete") is not True:
        diagnostics.append(
            {
                "kind": "host-not-complete",
                "item_id": context["item_id"],
                "host_truth_status": host_truth.get("status"),
                "repairable": False,
            }
        )
        return None, [], diagnostics

    metadata, metadata_missing = terminal_metadata_from_host_truth(host_truth)
    missing_inputs.extend(metadata_missing)
    if missing_inputs:
        return None, missing_inputs, diagnostics
    return {
        "context": context,
        "host_truth": host_truth,
        "metadata": metadata,
    }, [], diagnostics

def carrier_repair_payload(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    issue_number: int | None,
    *,
    apply: bool,
    dry_run: bool,
) -> dict[str, Any]:
    candidate, missing_inputs, diagnostics = carrier_repair_candidate(target_root, output_relative, expected_item, issue_number)
    versioned_carrier_updates: list[dict[str, Any]] = []
    item: dict[str, Any] | None = None
    if candidate is not None:
        context = candidate["context"]
        metadata = candidate["metadata"]
        item = {"id": context["item_id"]}
        init_result_path: Path | None = None
        init_result_payload: dict[str, Any] | None = None
        planned_action = "write" if apply and not dry_run else "preview"
        versioned_carrier_updates = [
            {
                "path": relative_to_root(context["recovery_path"], target_root),
                "kind": "terminal-closeout-metadata",
                "planned_action": planned_action,
                "metadata": metadata,
            },
            {
                "path": relative_to_root(context["status_path"], target_root),
                "kind": "idle-status-surface",
                "planned_action": planned_action,
                "item_id": "no_active_item",
            },
            {
                "path": output_relative,
                "kind": "idle-init-result-fact-chain",
                "planned_action": planned_action,
                "entry_points": {
                    "current_item_id": "no_active_item",
                    "work_item": "not_applicable",
                    "recovery_entry": "not_applicable",
                    "status_surface": ".loom/status/current.md",
                },
            },
        ]
        if apply and not dry_run and not missing_inputs:
            init_result_path, init_result_errors = resolve_repo_relative_path(
                target_root,
                output_relative,
                label="init-result locator",
            )
            missing_inputs.extend(init_result_errors)
            if init_result_path is not None and not missing_inputs:
                init_result_payload, init_result_payload_errors = load_idle_init_result_payload(init_result_path)
                missing_inputs.extend(init_result_payload_errors)
        if apply and not dry_run and not missing_inputs:
            assert init_result_path is not None
            assert init_result_payload is not None
            write_terminal_closeout_metadata(context["recovery_path"], metadata)
            context["status_path"].write_text(
                render_idle_status_surface(read_entry=context["read_entry"], output_relative=output_relative),
                encoding="utf-8",
            )
            write_idle_init_result(init_result_path, init_result_payload, read_entry=context["read_entry"])

    action = {
        "id": "carrier-closeout-active-to-idle",
        "kind": "carrier_closeout_sync",
        "status": "planned" if versioned_carrier_updates and not missing_inputs else "blocked" if missing_inputs else "not_applicable",
        "scope": "repo-local-versioned-carriers",
        "mutates": bool(apply and not dry_run and versioned_carrier_updates and not missing_inputs),
        "host_mutations": False,
        "host_actions": [],
        "versioned_carrier_updates": versioned_carrier_updates,
        "reason": (
            "current active carrier is host-complete and can be terminalized before switching the repository to idle."
            if versioned_carrier_updates
            else "no host-complete active carrier repair was detected."
        ),
        "command": "loom repair apply --target <repo> --json" if versioned_carrier_updates else "loom repair plan --target <repo> --json",
    }
    actions = [action] if versioned_carrier_updates or missing_inputs else []
    result = "block" if missing_inputs else "pass"
    return {
        "command": "repair",
        "operation": "apply" if apply else "plan",
        "schema_version": "loom-carrier-repair-plan/v1",
        "result": result,
        "summary": (
            "safe carrier repair applied versioned progress, status, and init-result updates."
            if result == "pass" and apply and not dry_run and versioned_carrier_updates
            else "safe carrier repair plan generated without mutating target state."
            if result == "pass"
            else "safe carrier repair is blocked until host-complete carrier ownership is unambiguous."
        ),
        "target": str(target_root),
        "mutates": bool(apply and not dry_run and versioned_carrier_updates and not missing_inputs),
        "dry_run": not apply or dry_run,
        "missing_inputs": missing_inputs,
        "actions": actions,
        "diagnostics": diagnostics,
        "item": item,
        "host_mutations": False,
        "host_actions": [],
        "versioned_carrier_updates": versioned_carrier_updates,
        "fallback_to": None if result == "pass" else "manual-carrier-closeout-review",
    }

def handle_repair(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    return emit(
        carrier_repair_payload(
            target_root,
            args.output,
            args.item,
            args.issue,
            apply=args.operation == "apply",
            dry_run=bool(args.dry_run),
        )
    )

def handle_carrier(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    if args.operation == "closeout-sync":
        return emit(carrier_closeout_sync_payload(target_root, args.output, args.item, args))
    return emit(carrier_refresh_payload(target_root, args.output, args.item, dry_run=args.dry_run, surface=args.surface))

def handle_goal(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    return emit(
        goal_payload(
            target_root=target_root,
            output_relative=args.output,
            expected_item=args.item,
            operation=args.operation,
            goal_file=args.goal_file,
            issue_number=args.issue,
            pr_number=args.pr,
            branch_name=args.branch,
            head_sha=args.head_sha,
        )
    )

def pr_metadata_replace_or_insert_binding_line(body: str, *, label: str, value: str, insert_after: str | None = None) -> str:
    pattern = re.compile(rf"(?im)^([ \t]*[-*]?[ \t]*{re.escape(label)}[ \t]*:[ \t]*)(`?[^`\n]*`?)[ \t]*$")
    if pattern.search(body):
        return pattern.sub(lambda match: f"{match.group(1).rstrip()} {value}", body, count=1)

    lines = body.splitlines()
    insert_at: int | None = None
    if insert_after:
        anchor_pattern = re.compile(rf"(?im)^[ \t]*[-*]?[ \t]*{re.escape(insert_after)}[ \t]*:")
        for index, line in enumerate(lines):
            if anchor_pattern.search(line):
                insert_at = index + 1
                break
    if insert_at is None:
        in_related = False
        for index, line in enumerate(lines):
            if line.startswith("## "):
                if line.strip() == "## Related Work":
                    in_related = True
                    continue
                if in_related:
                    insert_at = index
                    break
            if in_related and line.strip().startswith("- "):
                insert_at = index + 1
        if insert_at is None and in_related:
            insert_at = len(lines)
    if insert_at is None:
        lines.extend(["", "## Related Work", ""])
        insert_at = len(lines)
    lines.insert(insert_at, f"- {label}: {value}")
    return "\n".join(lines) + ("\n" if body.endswith("\n") else "")

def pr_metadata_replace_machine_block(body: str, *, marker: str, rendered_block: str) -> str:
    pattern = re.compile(rf"<!--\s*{re.escape(marker)}\s*.*?-->", flags=re.DOTALL)
    if pattern.search(body):
        updated = pattern.sub(rendered_block.rstrip(), body, count=1)
    else:
        updated = body.rstrip() + "\n\n" + rendered_block.rstrip() + "\n"
    return updated if updated.endswith("\n") else updated + "\n"

def pr_body_binding_value(body: Any, *, label: str, metadata_field: str) -> str | None:
    legacy_value = pr_body_field_value(body, label)
    if legacy_value:
        return legacy_value
    fields = pr_body_governance_metadata_fields(body)
    value = fields.get(metadata_field)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None

def pr_body_mentions_item(body: Any, item_id: str) -> bool:
    if not isinstance(body, str):
        return False
    return bool(re.search(rf"(?<![A-Z0-9-]){re.escape(item_id)}(?![A-Z0-9-])", body))

def path_safe_work_item_id(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value))

def render_governance_intensity_metadata_body(
    *,
    base_body: str,
    field: dict[str, Any],
    requested_surface: str,
    item_id: str,
    branch_name: str,
    head_sha: str | None,
    governance_intensity: str,
    change_class: str,
    suite_path: str,
    review_requirement: str,
    release_judgment: str,
    fact_chain_required: bool,
    upgrade_triggers: list[str],
    suite_not_applicable: dict[str, str] | None,
    issue_number: int | None,
    covered_issues: list[int],
    excluded_scope: list[str],
) -> tuple[str, dict[str, Any], list[str]]:
    contract_id = str(field.get("id") or GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID)
    machine_carrier = field.get("machine_carrier") if isinstance(field.get("machine_carrier"), dict) else {}
    marker = str(machine_carrier.get("marker") or "loom:repo-pr-metadata")
    effective_surface = pr_metadata_effective_contract_surface(field, requested_surface)
    work_item_locator = work_item_locator_for_metadata(item_id, issue_number)
    fields = {
        "work_item_locator": work_item_locator,
        "governance_intensity": governance_intensity,
        "governance_mode": "host-enforced",
        "governance_assurance": "limited",
        "advisory_risk_label": None,
        "host_enforcement_required": True,
        "change_class": change_class,
        "suite_path": suite_path,
        "suite_not_applicable": suite_not_applicable if suite_path == "not_applicable" else None,
        "review_requirement": review_requirement,
        "fact_chain_required": fact_chain_required,
        "pr_gate_required": True,
        "release_judgment": release_judgment,
        "closeout_required": True,
        "upgrade_triggers": upgrade_triggers,
        "anchor_issue": issue_number,
        "covered_issues": covered_issues or None,
        "excluded_scope": excluded_scope or None,
    }
    missing_inputs = validate_governance_intensity_metadata_fields(fields)
    if missing_inputs:
        return base_body, {}, missing_inputs
    envelope = {
        "schema_version": PR_METADATA_MACHINE_SCHEMA,
        "metadata_contract_id": contract_id,
        "surface": effective_surface,
        "fields": fields,
        "source": {"rendered_hash": PR_METADATA_RENDERER_ID},
        "parser_version": PR_METADATA_PARSER_VERSION,
    }
    rendered_block = "<!-- " + marker + "\n" + json.dumps(envelope, indent=2, ensure_ascii=False) + "\n-->\n"
    assert work_item_locator is not None
    updated = pr_metadata_replace_or_insert_binding_line(base_body, label="Work Item", value=work_item_locator)
    issue_reference = pr_metadata_issue_reference(issue_number)
    if issue_reference:
        updated = pr_metadata_replace_or_insert_binding_line(updated, label="Issue", value=issue_reference, insert_after="Work Item")
    if covered_issues:
        covered_text = ", ".join(f"#{number}" for number in covered_issues)
        updated = pr_metadata_replace_or_insert_binding_line(updated, label="Covered Issues", value=covered_text, insert_after="Issue")
    if excluded_scope:
        excluded_text = "; ".join(excluded_scope)
        updated = pr_metadata_replace_or_insert_binding_line(updated, label="Excluded Scope", value=excluded_text, insert_after="Covered Issues")
    updated = pr_metadata_replace_machine_block(updated, marker=marker, rendered_block=rendered_block)
    return updated, envelope, []

def pr_metadata_render_payload(
    *,
    target_root: Path,
    surface: str,
    output_file: str,
    base_body_file: str,
    item_id: str | None,
    issue_number: int | None,
    head_sha: str | None,
    branch_name: str | None,
    governance_intensity: str,
    change_class: str,
    suite_path: str,
    review_requirement: str,
    release_judgment: str,
    fact_chain_required: bool,
    upgrade_triggers: list[str],
    covered_issues: list[int],
    excluded_scope: list[str],
    suite_na_rationale: str | None,
    suite_na_consumer_boundary: str | None,
    suite_na_recheck_condition: str | None,
    suite_na_scope_proof: str | None,
    suite_na_review_requirement: str | None,
) -> dict[str, Any]:
    base_body, base_errors = load_optional_text_fixture(target_root, base_body_file, label="PR metadata render base body")
    output_path, output_errors = resolve_artifact_write_path(target_root, output_file, label="PR metadata render output")
    effective_item = item_id
    locator_owner, locator_repo = detect_github_repo(target_root)
    work_item_locator = work_item_locator_for_metadata(effective_item, issue_number, locator_owner, locator_repo)

    missing_inputs = list(base_errors) + list(output_errors)
    if work_item_locator is None:
        missing_inputs.append("pass --item owner/repo/work_item/id or --issue <GitHub Work Item>; legacy type:number is read-only through v0.30.x and local current-item carriers are not accepted")

    suite_not_applicable: dict[str, str] | None = None
    if suite_path == "not_applicable":
        suite_not_applicable = {
            "rationale": suite_na_rationale or "",
            "consumer_boundary": suite_na_consumer_boundary or "",
            "recheck_condition": suite_na_recheck_condition or "",
            "scope_proof": suite_na_scope_proof or "",
            "review_requirement": suite_na_review_requirement or review_requirement,
        }
    normalized_covered_issues = sorted({*(covered_issues or []), *([issue_number] if isinstance(issue_number, int) else [])})
    normalized_excluded_scope = dedupe_strings([entry.strip() for entry in excluded_scope if isinstance(entry, str) and entry.strip()])

    governance_surface = build_governance_surface(target_root)
    fields, contract_errors, source_locator = metadata_contract_raw_fields(target_root, governance_surface)
    contracts = applicable_pr_metadata_contracts(fields, surface=surface)
    missing_inputs.extend(str(message) for message in contract_errors)
    contract = next((field for field in contracts if field.get("id") == GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID), None)
    if contract is None and not contract_errors:
        missing_inputs.append(f"no applicable PR metadata machine carrier is declared for surface {surface}")
    if missing_inputs:
        return {
            "command": "pr-metadata",
            "operation": "render",
            "schema_version": PR_METADATA_RENDER_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata render is missing required bindings, carrier declarations, or output locators.",
            "missing_inputs": dedupe_strings(missing_inputs),
            "fallback_to": "adoption" if contract is None else "manual_pr_metadata_inputs",
            "source_locator": source_locator,
        }

    assert base_body is not None
    assert output_path is not None
    rendered_body, envelope, render_errors = render_governance_intensity_metadata_body(
        base_body=base_body,
        field=contract,
        requested_surface=surface,
        item_id=work_item_locator or "",
        branch_name=branch_name or "",
        head_sha=head_sha,
        governance_intensity=governance_intensity,
        change_class=change_class,
        suite_path=suite_path,
        review_requirement=review_requirement,
        release_judgment=release_judgment,
        fact_chain_required=fact_chain_required,
        upgrade_triggers=[entry for entry in upgrade_triggers if isinstance(entry, str) and entry.strip()],
        suite_not_applicable=suite_not_applicable,
        issue_number=issue_number,
        covered_issues=normalized_covered_issues,
        excluded_scope=normalized_excluded_scope,
    )
    if render_errors:
        return {
            "command": "pr-metadata",
            "operation": "render",
            "schema_version": PR_METADATA_RENDER_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata render inputs do not satisfy the governance metadata contract.",
            "missing_inputs": dedupe_strings(render_errors),
            "fallback_to": "manual_pr_metadata_inputs",
            "source_locator": source_locator,
        }

    write_runtime_text_artifact(output_path, rendered_body)
    relative_output = output_file.strip()
    preflight = pr_metadata_preflight_payload(
        target_root=target_root,
        surface=surface,
        body_file=relative_output,
        expected_item=work_item_locator,
        governance_surface=governance_surface,
        issue_number=issue_number,
    )
    result = "pass" if preflight.get("result") == "pass" else "block"
    return {
        "command": "pr-metadata",
        "operation": "render",
        "schema_version": PR_METADATA_RENDER_SCHEMA,
        "surface": surface,
        "result": result,
        "summary": (
            "PR metadata render produced a repo-relative PR body artifact and validated it with local preflight."
            if result == "pass"
            else "PR metadata render produced an artifact but local preflight still found blocking diagnostics."
        ),
        "missing_inputs": preflight.get("missing_inputs", []),
        "fallback_to": preflight.get("fallback_to"),
        "source_locator": source_locator,
        "rendered_body": {
            "body_file": relative_output,
            "body_sha256": hashlib.sha256(rendered_body.encode("utf-8")).hexdigest(),
            "base_body_file": base_body_file,
            "intent_metadata": {"work_item_locator": work_item_locator},
            "host_readback_authority": ["headRefOid", "headRefName", "mergeCommit", "statusCheckRollup"],
        },
        "metadata_contract_id": envelope.get("metadata_contract_id"),
        "effective_carrier_surface": envelope.get("surface"),
        "envelope": envelope,
        "preflight": preflight,
        "next_actions": [
            f"loom pr metadata-preflight --surface {surface} --body-file {shlex.quote(relative_output)} --json",
            f"loom pr metadata-update --surface {surface} --output-file {shlex.quote(relative_output)} --apply --json",
        ],
    }

def gh_pr_view_body(root: Path, pr_number: int) -> tuple[str | None, list[str]]:
    owner, repo_name = detect_github_repo(root)
    if not owner or not repo_name:
        return None, ["owner/repo"]
    payload, errors = github_pr_payload(root, owner, repo_name, pr_number)
    if errors or payload is None:
        return None, errors
    body = payload.get("body")
    if not isinstance(body, str):
        return None, [f"gh api repos/{owner}/{repo_name}/pulls/{pr_number} is missing `body`"]
    return body, []

def gh_pr_edit_body_file(root: Path, pr_number: int, body_path: Path) -> list[str]:
    try:
        result = run_process(["gh", "pr", "edit", str(pr_number), "--body-file", str(body_path)], root, timeout_seconds=30)
    except FileNotFoundError:
        return ["gh command is unavailable in PATH"]
    except subprocess.TimeoutExpired:
        return [f"gh pr edit {pr_number} --body-file timed out after 30s"]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh pr edit failed"
        return [detail]
    return []

def pr_metadata_readback_payload(
    *,
    target_root: Path,
    surface: str,
    owner: str | None = None,
    repo_name: str | None = None,
    pr_number: int | None = None,
    head_sha: str | None = None,
    branch_name: str | None = None,
    pr_payload_file: str | None = None,
    body_file: str | None = None,
    compare_body_file: str | None = None,
    readback_file: str | None = None,
    expected_item: str | None = None,
    issue_number: int | None = None,
) -> dict[str, Any]:
    governance_surface = build_governance_surface(target_root)
    effective_body_file = body_file
    effective_compare_file = compare_body_file
    source_body: str | None = None
    effective_pr = pr_number
    host_errors: list[str] = []
    inferences: list[dict[str, Any]] = []

    if effective_body_file is None and effective_compare_file is None:
        detected_owner, detected_repo = detect_github_repo(target_root)
        pr_payload, inferred_pr, payload_errors, payload_inferences = load_pr_payload_for_gate(
            target_root=target_root,
            owner=owner or detected_owner,
            repo_name=repo_name or detected_repo,
            pr_number=pr_number,
            head_sha=head_sha,
            branch_name=branch_name,
            pr_payload_file=pr_payload_file,
        )
        effective_pr = inferred_pr
        inferences.extend(payload_inferences)
        if payload_errors:
            host_errors.extend(f"pr: {message}" for message in payload_errors)
        elif isinstance(pr_payload, dict):
            source_body = pr_payload.get("body") if isinstance(pr_payload.get("body"), str) else None
        if source_body is None and effective_pr is not None:
            source_body, view_errors = gh_pr_view_body(target_root, effective_pr)
            host_errors.extend(view_errors)
        if source_body is not None and readback_file:
            readback_path, path_errors = resolve_artifact_write_path(target_root, readback_file, label="PR metadata readback output")
            if path_errors:
                host_errors.extend(path_errors)
            else:
                assert readback_path is not None
                write_runtime_text_artifact(readback_path, source_body)
                effective_body_file = readback_file.strip()

    preflight = pr_metadata_preflight_payload(
        target_root=target_root,
        surface=surface,
        owner=owner,
        repo_name=repo_name,
        pr_number=effective_pr,
        head_sha=head_sha,
        branch_name=branch_name,
        pr_payload_file=pr_payload_file,
        body_file=effective_body_file,
        compare_body_file=effective_compare_file,
        governance_surface=governance_surface,
        expected_item=expected_item,
        expected_head_sha=head_sha,
        expected_branch=branch_name,
        issue_number=issue_number,
    )
    body = source_body
    if effective_compare_file:
        body, _ = load_optional_text_fixture(target_root, effective_compare_file, label="post-edit PR body file")
    elif effective_body_file:
        body, _ = load_optional_text_fixture(target_root, effective_body_file, label="PR body file")
    result = "pass" if preflight.get("result") == "pass" and isinstance(body, str) and not host_errors else "block"
    missing_inputs = [*host_errors, *[str(message) for message in preflight.get("missing_inputs", [])]]
    return {
        "command": "pr-metadata",
        "operation": "readback",
        "schema_version": PR_METADATA_READBACK_SCHEMA,
        "surface": surface,
        "result": result,
        "summary": (
            "PR metadata readback parsed the current body artifact and matched the declared machine carrier."
            if result == "pass"
            else "PR metadata readback could not prove the current body artifact matches the declared machine carrier."
        ),
        "missing_inputs": dedupe_strings(missing_inputs),
        "fallback_to": preflight.get("fallback_to"),
        "pr": effective_pr,
        "body_file": effective_compare_file or effective_body_file,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest() if isinstance(body, str) else None,
        "intent_metadata": {
            "work_item_locator": pr_body_binding_value(body, label="Work Item", metadata_field="work_item_locator") if isinstance(body, str) else None,
        },
        "machine_surface": pr_body_machine_surface(body) if isinstance(body, str) else None,
        "governance_fields": pr_body_governance_metadata_fields(body) if isinstance(body, str) else {},
        "preflight": preflight,
        "inferences": inferences,
        "next_actions": [
            f"loom pr metadata-preflight --surface {surface} --body-file {shlex.quote(effective_compare_file or effective_body_file or '<body-file>')} --json",
        ],
    }

def pr_metadata_update_payload(
    *,
    target_root: Path,
    surface: str,
    owner: str | None,
    repo_name: str | None,
    pr_number: int | None,
    head_sha: str | None,
    branch_name: str | None,
    pr_payload_file: str | None,
    output_file: str,
    readback_file: str,
    base_body_file: str,
    item_id: str | None,
    issue_number: int | None,
    governance_intensity: str,
    change_class: str,
    suite_path: str,
    review_requirement: str,
    release_judgment: str,
    fact_chain_required: bool,
    upgrade_triggers: list[str],
    covered_issues: list[int],
    excluded_scope: list[str],
    suite_na_rationale: str | None,
    suite_na_consumer_boundary: str | None,
    suite_na_recheck_condition: str | None,
    suite_na_scope_proof: str | None,
    suite_na_review_requirement: str | None,
    dry_run: bool,
) -> dict[str, Any]:
    render_payload = pr_metadata_render_payload(
        target_root=target_root,
        surface=surface,
        output_file=output_file,
        base_body_file=base_body_file,
        item_id=item_id,
        issue_number=issue_number,
        head_sha=head_sha,
        branch_name=branch_name,
        governance_intensity=governance_intensity,
        change_class=change_class,
        suite_path=suite_path,
        review_requirement=review_requirement,
        release_judgment=release_judgment,
        fact_chain_required=fact_chain_required,
        upgrade_triggers=upgrade_triggers,
        covered_issues=covered_issues,
        excluded_scope=excluded_scope,
        suite_na_rationale=suite_na_rationale,
        suite_na_consumer_boundary=suite_na_consumer_boundary,
        suite_na_recheck_condition=suite_na_recheck_condition,
        suite_na_scope_proof=suite_na_scope_proof,
        suite_na_review_requirement=suite_na_review_requirement,
    )
    if render_payload.get("result") != "pass":
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata update did not start because render/preflight prerequisites are still blocking.",
            "missing_inputs": render_payload.get("missing_inputs", []),
            "fallback_to": render_payload.get("fallback_to"),
            "render": render_payload,
        }

    rendered_relative = render_payload.get("rendered_body", {}).get("body_file")
    if not isinstance(rendered_relative, str) or not rendered_relative:
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata update could not locate the rendered body artifact after local preflight.",
            "missing_inputs": ["render output path is unavailable"],
            "fallback_to": "manual_pr_metadata_inputs",
            "render": render_payload,
            "dry_run": dry_run,
            "host_mutations": False,
        }
    if dry_run:
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "pass",
            "summary": "PR metadata update dry-run rendered the body artifact and passed local preflight without mutating the host PR.",
            "missing_inputs": [],
            "fallback_to": None,
            "dry_run": True,
            "host_mutations": False,
            "apply_required": True,
            "pr": pr_number,
            "render": render_payload,
            "readback": None,
            "next_actions": [
                f"loom pr metadata-preflight --surface {surface} --body-file {shlex.quote(rendered_relative)} --json",
                f"loom pr metadata-update --surface {surface} --output-file {shlex.quote(rendered_relative)} --apply --json",
            ],
        }

    detected_owner, detected_repo = detect_github_repo(target_root)
    pr_payload, effective_pr, payload_errors, inferences = load_pr_payload_for_gate(
        target_root=target_root,
        owner=owner or detected_owner,
        repo_name=repo_name or detected_repo,
        pr_number=pr_number,
        head_sha=head_sha,
        branch_name=branch_name,
        pr_payload_file=pr_payload_file,
    )
    missing_inputs = [str(message) for message in payload_errors]
    if effective_pr is None:
        missing_inputs.append("unable to determine target PR for metadata update")
    rendered_path = None
    rendered_path, rendered_errors = resolve_artifact_read_path(target_root, rendered_relative, label="PR metadata rendered body")
    missing_inputs.extend(rendered_errors)
    if missing_inputs:
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata update is missing the rendered body artifact or a resolvable target PR.",
            "missing_inputs": dedupe_strings(missing_inputs),
            "fallback_to": "manual_pr_metadata_inputs",
            "render": render_payload,
            "inferences": inferences,
            "dry_run": False,
            "host_mutations": False,
        }

    assert rendered_path is not None
    update_errors = gh_pr_edit_body_file(target_root, effective_pr, rendered_path)
    if update_errors:
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata update could not write the rendered body to the host PR.",
            "missing_inputs": update_errors,
            "fallback_to": "gh_pr_edit_body_file_readback",
            "render": render_payload,
            "pr": effective_pr,
            "inferences": inferences,
            "dry_run": False,
            "host_mutations": True,
        }

    host_body, view_errors = gh_pr_view_body(target_root, effective_pr)
    if view_errors:
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata update wrote the host PR body but could not read it back for verification.",
            "missing_inputs": view_errors,
            "fallback_to": "gh_pr_edit_body_file_readback",
            "render": render_payload,
            "pr": effective_pr,
            "inferences": inferences,
            "dry_run": False,
            "host_mutations": True,
        }
    readback_path, readback_errors = resolve_artifact_write_path(target_root, readback_file, label="PR metadata readback output")
    if readback_errors:
        return {
            "command": "pr-metadata",
            "operation": "update",
            "schema_version": PR_METADATA_UPDATE_SCHEMA,
            "surface": surface,
            "result": "block",
            "summary": "PR metadata update wrote the host PR body but could not persist the readback artifact.",
            "missing_inputs": readback_errors,
            "fallback_to": "gh_pr_edit_body_file_readback",
            "render": render_payload,
            "pr": effective_pr,
            "inferences": inferences,
            "dry_run": False,
            "host_mutations": True,
        }
    assert readback_path is not None
    write_runtime_text_artifact(readback_path, host_body)
    readback_relative = readback_file.strip()

    readback_payload = pr_metadata_readback_payload(
        target_root=target_root,
        surface=surface,
        owner=owner or detected_owner,
        repo_name=repo_name or detected_repo,
        pr_number=effective_pr,
        head_sha=head_sha or (pr_payload.get("headRefOid") if isinstance(pr_payload, dict) else None),
        branch_name=branch_name or (pr_payload.get("headRefName") if isinstance(pr_payload, dict) else None),
        pr_payload_file=None,
        body_file=rendered_relative,
        compare_body_file=readback_relative,
        readback_file=readback_relative,
        expected_item=item_id,
        issue_number=issue_number,
    )
    result = "pass" if readback_payload.get("result") == "pass" else "block"
    return {
        "command": "pr-metadata",
        "operation": "update",
        "schema_version": PR_METADATA_UPDATE_SCHEMA,
        "surface": surface,
        "result": result,
        "summary": (
            "PR metadata update rendered, wrote, read back, and revalidated the host PR body."
            if result == "pass"
            else "PR metadata update wrote the host PR body but readback or revalidation still found blocking drift."
        ),
        "missing_inputs": readback_payload.get("missing_inputs", []),
        "fallback_to": readback_payload.get("fallback_to"),
        "dry_run": False,
        "host_mutations": True,
        "pr": effective_pr,
        "render": render_payload,
        "readback": readback_payload,
        "inferences": inferences,
        "next_actions": [
            f"loom pr metadata-readback {effective_pr} --surface {surface} --body-file {shlex.quote(rendered_relative)} --readback-file {shlex.quote(readback_file)} --json",
        ],
    }

def handle_pr_metadata(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    if args.operation == "render":
        return emit(
            pr_metadata_render_payload(
                target_root=target_root,
                surface=args.surface,
                output_file=args.output_file,
                base_body_file=args.base_body_file,
                item_id=args.item,
                issue_number=args.issue,
                head_sha=args.head_sha,
                branch_name=args.branch,
                governance_intensity=args.governance_intensity,
                change_class=args.change_class,
                suite_path=args.suite_path,
                review_requirement=args.review_requirement,
                release_judgment=args.release_judgment,
                fact_chain_required=args.fact_chain_required,
                upgrade_triggers=args.upgrade_trigger,
                covered_issues=args.covered_issue,
                excluded_scope=args.excluded_scope,
                suite_na_rationale=args.suite_na_rationale,
                suite_na_consumer_boundary=args.suite_na_consumer_boundary,
                suite_na_recheck_condition=args.suite_na_recheck_condition,
                suite_na_scope_proof=args.suite_na_scope_proof,
                suite_na_review_requirement=args.suite_na_review_requirement,
            )
        )
    if args.operation == "update":
        return emit(
            pr_metadata_update_payload(
                target_root=target_root,
                surface=args.surface,
                owner=args.owner,
                repo_name=args.repo_name,
                pr_number=args.pr,
                head_sha=args.head_sha,
                branch_name=args.branch,
                pr_payload_file=args.pr_payload_file,
                output_file=args.output_file,
                readback_file=args.readback_file,
                base_body_file=args.base_body_file,
                item_id=args.item,
                issue_number=args.issue,
                governance_intensity=args.governance_intensity,
                change_class=args.change_class,
                suite_path=args.suite_path,
                review_requirement=args.review_requirement,
                release_judgment=args.release_judgment,
                fact_chain_required=args.fact_chain_required,
                upgrade_triggers=args.upgrade_trigger,
                covered_issues=args.covered_issue,
                excluded_scope=args.excluded_scope,
                suite_na_rationale=args.suite_na_rationale,
                suite_na_consumer_boundary=args.suite_na_consumer_boundary,
                suite_na_recheck_condition=args.suite_na_recheck_condition,
                suite_na_scope_proof=args.suite_na_scope_proof,
                suite_na_review_requirement=args.suite_na_review_requirement,
                dry_run=args.dry_run,
            )
        )
    if args.operation == "readback":
        return emit(
            pr_metadata_readback_payload(
                target_root=target_root,
                surface=args.surface,
                owner=args.owner,
                repo_name=args.repo_name,
                pr_number=args.pr,
                head_sha=args.head_sha,
                branch_name=args.branch,
                pr_payload_file=args.pr_payload_file,
                body_file=args.body_file,
                compare_body_file=args.compare_body_file,
                readback_file=args.readback_file,
                expected_item=args.item,
                issue_number=args.issue,
            )
        )
    return emit(
        pr_metadata_preflight_payload(
            target_root=target_root,
            surface=args.surface,
            owner=args.owner,
            repo_name=args.repo_name,
            pr_number=args.pr,
            head_sha=args.head_sha,
            branch_name=args.branch,
            pr_payload_file=args.pr_payload_file,
            body_file=args.body_file,
            compare_body_file=args.compare_body_file,
            expected_item=args.item,
            expected_head_sha=args.head_sha,
            expected_branch=args.branch,
            issue_number=args.issue,
        )
    )

def maturity_upgrade_path(governance_surface: dict[str, Any], target_root: Path) -> dict[str, Any]:
    control_plane = governance_surface.get("governance_control_plane")
    maturity = control_plane.get("maturity") if isinstance(control_plane, dict) else None
    if not isinstance(maturity, dict):
        return {
            "result": "block",
            "current": "unknown",
            "next": None,
            "missing_inputs": ["governance_control_plane.maturity"],
            "missing_details": [],
            "fallback_to": "admission",
            "upgrade_entry": None,
            "validation_entries": [],
        }
    current = maturity.get("current")
    next_level = maturity.get("next")
    target_level = next_level if isinstance(next_level, str) else current if isinstance(current, str) else None
    gate_rollout = maturity.get("gate_rollout")
    missing_by_level = maturity.get("missing_by_level")
    missing_details_by_level = maturity.get("missing_details_by_level")
    missing_inputs = []
    missing_details = []
    if isinstance(next_level, str):
        if isinstance(missing_by_level, dict) and isinstance(missing_by_level.get(next_level), list):
            missing_inputs = list(missing_by_level[next_level])
        if isinstance(missing_details_by_level, dict) and isinstance(missing_details_by_level.get(next_level), list):
            missing_details = list(missing_details_by_level[next_level])
    decisions = adoption_decisions_payload(target_root, target_level=target_level, maturity=maturity)
    guided_plan = guided_adoption_plan_payload(decisions)
    return {
        "result": "pass" if next_level is None else "block",
        "current": current,
        "next": next_level,
        "missing_inputs": missing_inputs,
        "missing_details": missing_details,
        "fallback_to": None if next_level is None else "adoption",
        "upgrade_entry": (
            f"python3 tools/loom_flow.py governance-profile upgrade --target {command_target(target_root)} --to {next_level} --dry-run"
            if isinstance(next_level, str)
            else None
        ),
        "validation_entries": [
            f"python3 tools/loom_flow.py governance-profile status --target {command_target(target_root)}",
            f"python3 tools/loom_flow.py governance-profile upgrade-plan --target {command_target(target_root)}",
        ],
        "gate_rollout": gate_rollout,
        "adoption_decisions": decisions,
        "guided_adoption_plan": guided_plan,
    }

def lifecycle_intent_for_operation(operation: str) -> str | None:
    return {"build": "build", "pre-review": "pr", "closeout": "closeout"}.get(operation)


def host_derived_flow_payload(
    *,
    target_root: Path,
    args: argparse.Namespace,
    manifest: dict[str, object],
    runtime_state: dict[str, Any],
    lifecycle_admission: dict[str, Any] | None,
) -> dict[str, Any]:
    """Route light-profile flows without reading committed execution state."""

    admission = lifecycle_admission
    if admission is None:
        intent = "ship" if args.operation == "merge-ready" else "build"
        admission = lifecycle_admission_payload(
            target_root=target_root,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
            fr_number=args.fr,
            pr_number=args.pr,
            branch_name=args.branch,
            intent=intent,
        )
    admission_passed = admission.get("result") == "pass"
    missing_inputs = list(admission.get("missing_inputs", [])) if not admission_passed else []
    if not admission_passed and not missing_inputs:
        missing_inputs.append(str(admission.get("summary") or admission.get("admission_state") or "host lifecycle admission blocked"))
    fallback_to: str | None = admission.get("primary_remediation") if missing_inputs else None
    result = "pass" if admission_passed else "block"
    if args.operation in {"review", "spec-review"}:
        result = "block"
        missing_inputs.append("current GitHub host attestation artifact")
        fallback_to = "loom attestation readback --repo <owner/repo> --pr <n> --work-item <n> --artifact-input <file> --json"
    elif args.operation == "merge-ready" and result == "pass":
        result = "block"
        missing_inputs.append("current-head PR gate and merge check host readback")
        fallback_to = "loom pr gate <pr> --json && loom merge check <pr> --json"

    return {
        "command": "flow",
        "operation": args.operation,
        "result": result,
        "summary": (
            "light-profile flow consumed GitHub lifecycle admission and current worktree facts without repository execution carriers."
            if result == "pass"
            else "light-profile flow stopped at a missing host fact without falling back to repository execution carriers."
        ),
        "profile": manifest.get("profile"),
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
        "fallback_to": fallback_to,
        "runtime_state": runtime_state,
        "lifecycle_admission": admission,
        "worktree": {
            "repository_locator": ".",
            "branch": git_branch(target_root),
            "head_sha": git_head_sha(target_root),
            "workspace_entry": ".",
            "source": "git_worktree_readback",
        },
        "steps": [
            {"name": "runtime-state", "result": runtime_state["result"]},
            {"name": "host-lifecycle-admission", "result": admission.get("result")},
            {"name": "git-worktree-readback", "result": "pass"},
        ],
        "carrier_mutations": False,
        "repo_execution_carriers_consumed": False,
        "committed_current_consumed": False,
        "committed_status_consumed": False,
        "committed_progress_consumed": False,
        "committed_review_consumed": False,
        "committed_shadow_consumed": False,
    }

def runtime_parity_check(
    name: str,
    *,
    result: str,
    summary: str,
    evidence: dict[str, Any] | None = None,
    missing_inputs: list[str] | None = None,
    fallback_to: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "result": result,
        "summary": summary,
        "evidence": evidence or {},
        "missing_inputs": missing_inputs or [],
        "fallback_to": fallback_to,
    }

def runtime_parity_payload(
    *,
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    checks: list[dict[str, Any]] = []
    if runtime_state["result"] != "pass":
        checks.append(
            runtime_parity_check(
                "runtime_state",
                result="block",
                summary="runtime carrier is not consistent enough to prove runtime parity.",
                missing_inputs=list(runtime_state.get("missing_inputs", [])),
                fallback_to=runtime_state.get("fallback_to"),
                evidence={"runtime_state": runtime_state},
            )
        )
        return {
            "command": "runtime-parity",
            "operation": "validate",
            "schema_version": "loom-runtime-parity/v1",
            "result": "block",
            "summary": "Loom core runtime parity validation is blocked by runtime-state drift.",
            "missing_inputs": list(runtime_state.get("missing_inputs", [])),
            "fallback_to": runtime_state.get("fallback_to"),
            "runtime_state": runtime_state,
            "checks": checks,
        }

    context, context_errors = load_context(target_root, output_relative, expected_item)
    governance_surface = build_governance_surface(target_root)
    control_plane = governance_surface.get("governance_control_plane")
    carrier_summary = governance_surface.get("carrier_summary")

    if context_errors:
        if is_idle_context_errors(context_errors) and expected_idle_item(expected_item):
            checks.append(
                runtime_parity_check(
                    "work_item",
                    result="pass",
                    summary="Repository is idle; no active Work Item is required for runtime parity.",
                    evidence={
                        "current_item_id": NO_ACTIVE_ITEM_ID,
                        "fact_chain": "idle",
                    },
                )
            )
        else:
            checks.append(
                runtime_parity_check(
                    "work_item",
                    result="block",
                    summary="runtime parity could not read the Work Item fact chain.",
                    missing_inputs=[f"fact-chain: {message}" for message in context_errors],
                    fallback_to="admission",
                )
            )
    else:
        checks.append(
            runtime_parity_check(
                "work_item",
                result="pass",
                summary="Work Item is readable as the single execution entry.",
                evidence={
                    "item_id": context["item_id"],
                    "work_item": context["report"]["fact_chain"]["entry_points"]["work_item"],
                    "recovery_entry": context["report"]["fact_chain"]["entry_points"]["recovery_entry"],
                    "status_surface": context["report"]["fact_chain"]["entry_points"]["status_surface"],
                },
            )
        )

    if isinstance(control_plane, dict) and control_plane.get("schema_version") == "loom-governance-control/v1":
        checks.append(
            runtime_parity_check(
                "status_control_plane",
                result="pass",
                summary="governance control plane is available as a machine-readable runtime surface.",
                evidence={
                    "schema_version": control_plane.get("schema_version"),
                    "taxonomy": sorted((control_plane.get("taxonomy") or {}).keys())
                    if isinstance(control_plane.get("taxonomy"), dict)
                    else [],
                    "maturity": (control_plane.get("maturity") or {}).get("current")
                    if isinstance(control_plane.get("maturity"), dict)
                    else None,
                },
            )
        )
    else:
        checks.append(
            runtime_parity_check(
                "status_control_plane",
                result="block",
                summary="governance control plane is missing or unreadable.",
                missing_inputs=["governance_control_plane"],
                fallback_to="admission",
            )
        )

    expected_gate_order = [
        "work_item_admission",
        "spec_gate",
        "build_gate",
        "review_gate",
        "merge_gate",
        "github_controlled_merge",
        "closeout",
    ]
    gate_chain = control_plane.get("gate_chain") if isinstance(control_plane, dict) else None
    actual_gate_order = [entry.get("id") for entry in gate_chain if isinstance(entry, dict)] if isinstance(gate_chain, (list, tuple)) else []
    checks.append(
        runtime_parity_check(
            "gate_chain",
            result="pass" if actual_gate_order == expected_gate_order else "block",
            summary=(
                "strong governance gate chain is available in runtime order."
                if actual_gate_order == expected_gate_order
                else "strong governance gate chain does not match the runtime parity contract."
            ),
            evidence={"gate_order": actual_gate_order, "expected_gate_order": expected_gate_order},
            missing_inputs=[] if actual_gate_order == expected_gate_order else ["governance_control_plane.gate_chain"],
            fallback_to=None if actual_gate_order == expected_gate_order else "admission",
        )
    )

    host_binding = control_plane.get("host_binding") if isinstance(control_plane, dict) else None
    required_objects = host_binding.get("required_objects") if isinstance(host_binding, dict) else None
    controlled_merge_ready = (
        isinstance(host_binding, dict)
        and isinstance(required_objects, dict)
        and {"implementation_pr", "merge_commit", "closeout"}.issubset(required_objects.keys())
    )
    checks.append(
        runtime_parity_check(
            "controlled_merge_contract",
            result="pass" if controlled_merge_ready else "block",
            summary=(
                "controlled merge contract exposes PR, merge commit, and closeout host-owned bindings."
                if controlled_merge_ready
                else "controlled merge contract is missing required host-owned bindings."
            ),
            evidence={
                "host_binding_result": host_binding.get("result") if isinstance(host_binding, dict) else None,
                "required_objects": sorted(required_objects.keys()) if isinstance(required_objects, dict) else [],
            },
            missing_inputs=[] if controlled_merge_ready else ["governance_control_plane.host_binding"],
            fallback_to=None if controlled_merge_ready else "merge",
        )
    )

    closeout_gate = next((entry for entry in gate_chain or [] if isinstance(entry, dict) and entry.get("id") == "closeout"), {})
    closeout_requires = closeout_gate.get("requires") if isinstance(closeout_gate, dict) else None
    closeout_ready = isinstance(closeout_requires, (list, tuple)) and "reconciliation_audit" in closeout_requires
    checks.append(
        runtime_parity_check(
            "closeout_reconciliation",
            result="pass" if closeout_ready else "block",
            summary=(
                "closeout gate consumes reconciliation audit as a runtime prerequisite."
                if closeout_ready
                else "closeout gate does not expose reconciliation audit as a runtime prerequisite."
            ),
            evidence={
                "closeout_requires": closeout_requires if isinstance(closeout_requires, (list, tuple)) else [],
                "repo_interop_availability": (governance_surface.get("repo_interop") or {}).get("availability")
                if isinstance(governance_surface.get("repo_interop"), dict)
                else None,
            },
            missing_inputs=[] if closeout_ready else ["governance_control_plane.gate_chain.closeout"],
            fallback_to=None if closeout_ready else "reconciliation-sync",
        )
    )

    checks.append(
        runtime_parity_check(
            "shadow_parity_boundary",
            result="pass",
            summary="shadow parity remains validation-only in Loom core runtime parity.",
            evidence={
                "default_result_contract": ["pass", "warn"],
                "blocking_default": False,
                "surfaces": list(SHADOW_PARITY_SURFACES),
            },
        )
    )

    if not isinstance(carrier_summary, dict):
        checks.append(
            runtime_parity_check(
                "carrier_summary",
                result="block",
                summary="carrier summary is missing from governance surface.",
                missing_inputs=["governance_surface.carrier_summary"],
                fallback_to="admission",
            )
        )

    missing_inputs: list[str] = []
    fallback_to: str | None = None
    for check in checks:
        if check["result"] == "block":
            fallback_to = fallback_to or check.get("fallback_to")
            for message in check.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(message)

    result = "pass" if not missing_inputs else "block"
    return {
        "command": "runtime-parity",
        "operation": "validate",
        "schema_version": "loom-runtime-parity/v1",
        "result": result,
        "summary": (
            "Loom core runtime parity is machine-readable across Work Item, status, gates, controlled merge, closeout, and shadow boundary."
            if result == "pass"
            else "Loom core runtime parity validation found missing or unreadable runtime surfaces."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to,
        "runtime_state": runtime_state,
        "checks": checks,
    }

def goal_execution_contract(context: dict[str, Any]) -> dict[str, Any]:
    current_branch = run_git(context["target_root"], ["branch", "--show-current"])
    branch = current_branch.stdout.strip() if current_branch is not None and current_branch.returncode == 0 else None
    head_sha = git_head_sha(context["target_root"])
    return {
        "schema_version": GOAL_EXECUTION_CONTRACT_SCHEMA,
        "objective": context["goal"],
        "source_issue": None,
        "work_item": {
            "id": context["item_id"],
            "locator": str(context["report"]["fact_chain"]["entry_points"]["work_item"]),
        },
        "scope": [context["scope"]],
        "non_goals": [],
        "source_locators": [
            str(context["report"]["fact_chain"]["entry_points"]["work_item"]),
            str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
        ],
        "branch": branch,
        "formal_worktree": context["workspace_entry"],
        "pr": None,
        "head_sha": head_sha,
        "expected_validation": [context["validation_entry"]],
        "stop_conditions": [context["closing_condition"]],
        "return_path": "flow resume -> review -> merge-ready -> closeout",
        "derived_from": "work_item_goal",
        "derivation_source": str(context["report"]["fact_chain"]["entry_points"]["work_item"]),
    }

def validate_goal_execution_contract(
    contract: dict[str, Any],
    context: dict[str, Any],
    *,
    issue_number: int | None = None,
    pr_number: int | None = None,
    branch_name: str | None = None,
    head_sha: str | None = None,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if contract.get("schema_version") != GOAL_EXECUTION_CONTRACT_SCHEMA:
        failures.append({"class": "missing", "field": "schema_version", "expected": GOAL_EXECUTION_CONTRACT_SCHEMA})
    work_item = contract.get("work_item")
    if not isinstance(work_item, dict) or work_item.get("id") != context["item_id"]:
        failures.append({"class": "scope_mismatch", "field": "work_item", "expected": context["item_id"], "actual": work_item})
    if issue_number is not None and contract.get("source_issue") not in {issue_number, f"#{issue_number}", f"issue #{issue_number}"}:
        failures.append({"class": "scope_mismatch", "field": "source_issue", "expected": issue_number, "actual": contract.get("source_issue")})
    current_branch = run_git(context["target_root"], ["branch", "--show-current"])
    actual_branch = current_branch.stdout.strip() if current_branch is not None and current_branch.returncode == 0 else None
    expected_branch = branch_name or actual_branch
    if expected_branch and contract.get("branch") not in {expected_branch, None}:
        failures.append({"class": "unbound_workspace", "field": "branch", "expected": expected_branch, "actual": contract.get("branch")})
    expected_head = head_sha or git_head_sha(context["target_root"])
    if expected_head and contract.get("head_sha") not in {expected_head, None}:
        failures.append({"class": "stale", "field": "head_sha", "expected": expected_head, "actual": contract.get("head_sha")})
    if pr_number is not None and contract.get("pr") not in {pr_number, f"#{pr_number}", f"PR #{pr_number}", None}:
        failures.append({"class": "scope_mismatch", "field": "pr", "expected": pr_number, "actual": contract.get("pr")})
    validation = contract.get("expected_validation")
    if not isinstance(validation, list) or not validation:
        failures.append({"class": "unverifiable_validation", "field": "expected_validation"})
    source_locators = contract.get("source_locators")
    if not isinstance(source_locators, list) or not source_locators:
        failures.append({"class": "missing", "field": "source_locators"})
    result = "pass" if not failures else "block"
    return {
        "schema_version": GOAL_READINESS_SCHEMA,
        "result": result,
        "summary": "goal execution contract is aligned with the current work item." if result == "pass" else "goal execution contract is missing, stale, or mismatched.",
        "missing_inputs": [f"{failure['class']}:{failure['field']}" for failure in failures],
        "fallback_to": None if result == "pass" else "admission",
        "failure_classifications": failures,
    }

def goal_payload(
    *,
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    operation: str,
    goal_file: str | None = None,
    issue_number: int | None = None,
    pr_number: int | None = None,
    branch_name: str | None = None,
    head_sha: str | None = None,
) -> dict[str, Any]:
    context, errors = load_context(target_root, output_relative, expected_item)
    if errors:
        return {
            "command": "goal",
            "operation": operation,
            "result": "block",
            "summary": "goal command could not read a valid Loom fact chain.",
            "missing_inputs": [f"fact-chain: {message}" for message in errors],
            "fallback_to": "admission",
            **fact_chain_error_contract(errors, output_relative=output_relative),
        }
    contract = goal_execution_contract(context)
    if goal_file:
        loaded, load_errors = load_optional_json_fixture(target_root, goal_file, label="goal execution contract")
        if load_errors:
            return {
                "command": "goal",
                "operation": operation,
                "result": "block",
                "summary": "goal command could not read the requested goal contract.",
                "missing_inputs": load_errors,
                "fallback_to": "admission",
                "goal_execution_contract": contract,
            }
        if isinstance(loaded, dict):
            contract = loaded
    readiness = validate_goal_execution_contract(
        contract,
        context,
        issue_number=issue_number,
        pr_number=pr_number,
        branch_name=branch_name,
        head_sha=head_sha,
    )
    return {
        "command": "goal",
        "operation": operation,
        "result": readiness["result"],
        "summary": "goal execution contract was derived and validated." if readiness["result"] == "pass" else readiness["summary"],
        "missing_inputs": readiness["missing_inputs"],
        "fallback_to": readiness["fallback_to"],
        "goal_execution_contract": contract,
        "goal_readiness": readiness,
    }

def handle_recovery(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "recovery",
                "operation": args.operation,
                "result": "block",
                "summary": "recovery command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                **fact_chain_error_contract(errors, output_relative=args.output),
            }
        )

    updates = {
        "current_checkpoint": args.current_checkpoint,
        "current_stop": args.current_stop,
        "next_step": args.next_step,
        "blockers": args.blockers,
        "latest_validation_summary": args.latest_validation_summary,
        "recovery_boundary": args.recovery_boundary,
        "current_lane": args.current_lane,
    }
    provided = {field: value for field, value in updates.items() if isinstance(value, str) and value.strip()}
    if not provided:
        return emit(
            {
                "command": "recovery",
                "operation": "writeback",
                "result": "block",
                "summary": "recovery writeback requires at least one authored field.",
                "missing_inputs": ["current-stop | next-step | blockers | latest-validation-summary | current-checkpoint | recovery-boundary | current-lane"],
                "fallback_to": "admission",
            }
        )

    status_relative = str(context["report"]["fact_chain"]["entry_points"]["status_surface"])
    runtime_evidence, runtime_errors = read_runtime_evidence(target_root, status_relative)
    if runtime_errors:
        return emit(
            {
                "command": "recovery",
                "operation": "writeback",
                "result": "block",
                "summary": "recovery writeback could not read runtime evidence for status sync.",
                "missing_inputs": runtime_errors,
                "fallback_to": "admission",
            }
        )

    for field_name, value in provided.items():
        if field_name == "current_checkpoint":
            value = normalize_checkpoint(value)
        update_markdown_bullet(context["recovery_path"], RECOVERY_FIELD_LABELS[field_name], value)

    refreshed, refresh_errors = sync_status_surface(target_root, args.output, runtime_evidence)
    if refresh_errors:
        return emit(
            {
                "command": "recovery",
                "operation": "writeback",
                "result": "block",
                "summary": "recovery writeback updated the recovery entry, but fact-chain verification failed during status sync.",
                "missing_inputs": refresh_errors,
                "fallback_to": "admission",
            }
        )

    return emit(
        {
            "command": "recovery",
            "operation": "writeback",
            "item": {"id": context["item_id"]},
            "result": "pass",
            "summary": "recovery authored fields were updated and the derived status surface was resynchronized.",
            "missing_inputs": [],
            "fallback_to": None,
            "updated_fields": sorted(provided),
            "recovery_entry": str(refreshed["fact_chain"]["entry_points"]["recovery_entry"]),
            "status_surface": str(refreshed["fact_chain"]["entry_points"]["status_surface"]),
        }
    )

def update_active_entry_points(
    target_root: Path,
    output_relative: str,
    *,
    item_id: str,
    work_item: str,
    recovery_entry: str,
    status_surface: str,
) -> None:
    output_path, output_errors = resolve_repo_relative_path(target_root, output_relative, label="init-result locator")
    if output_errors:
        raise RuntimeError("; ".join(output_errors))
    assert output_path is not None
    payload = load_json_file(output_path)
    fact_chain = payload.get("fact_chain")
    if not isinstance(fact_chain, dict):
        raise RuntimeError("init-result is missing `fact_chain`")
    entry_points = fact_chain.get("entry_points")
    if not isinstance(entry_points, dict):
        raise RuntimeError("init-result.fact_chain is missing `entry_points`")
    entry_points["current_item_id"] = item_id
    entry_points["work_item"] = work_item
    entry_points["recovery_entry"] = recovery_entry
    entry_points["status_surface"] = status_surface
    if item_id != NO_ACTIVE_ITEM_ID:
        fact_chain["mode"] = "work-item + recovery-entry + derived status-surface"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def validate_work_item_payload_locators(
    target_root: Path,
    work_item_payload: dict[str, Any],
) -> tuple[dict[str, Path], list[str]]:
    """Validate final authored locator truth before any Work Item carrier write."""
    locators: dict[str, str] = {
        "recovery_entry": str(work_item_payload.get("recovery_entry", "")),
        "review_entry": str(work_item_payload.get("review_entry", "")),
    }
    associated_artifacts = work_item_payload.get("associated_artifacts", [])
    if isinstance(associated_artifacts, list):
        for index, artifact in enumerate(associated_artifacts, start=1):
            locators[f"associated_artifacts[{index}]"] = str(artifact)
    else:
        return {}, ["associated_artifacts must be a list of repo-relative locators"]

    resolved: dict[str, Path] = {}
    errors: list[str] = []
    workspace_path, workspace_errors = resolve_workspace_path(
        target_root,
        str(work_item_payload.get("workspace_entry", "")),
    )
    errors.extend(f"work item workspace_entry: {message}" for message in workspace_errors)
    if workspace_path is not None:
        resolved["workspace_entry"] = workspace_path
    for label, locator in locators.items():
        path, locator_errors = resolve_repo_relative_path(target_root, locator, label=f"work item {label}")
        errors.extend(locator_errors)
        if path is not None:
            resolved[label] = path
    return resolved, errors

def handle_work_item(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    output_path, output_errors = resolve_repo_relative_path(target_root, args.output, label="init-result locator")
    if output_errors:
        return emit(
            {
                "command": "work-item",
                "operation": args.operation,
                "result": "block",
                "summary": "work-item command requires a safe init-result fact-chain locator.",
                "missing_inputs": output_errors,
                "fallback_to": "admission",
            }
        )
    assert output_path is not None
    if not output_path.exists():
        return emit(
            {
                "command": "work-item",
                "operation": args.operation,
                "result": "block",
                "summary": "work-item command requires an existing init-result fact-chain locator.",
                "missing_inputs": [f"missing init-result: {args.output}"],
                "fallback_to": "admission",
            }
        )

    work_item_relative = f".loom/work-items/{args.item}.md"
    work_item_path, work_item_path_errors = resolve_repo_relative_path(
        target_root,
        work_item_relative,
        label="work item locator",
    )
    recovery_relative = args.recovery_entry or f".loom/progress/{args.item}.md"
    recovery_path, recovery_path_errors = resolve_repo_relative_path(
        target_root,
        recovery_relative,
        label="recovery entry locator",
    )
    review_relative = default_review_path(args.item)
    review_path, review_path_errors = resolve_repo_relative_path(target_root, review_relative, label="review locator")
    status_relative = ".loom/status/current.md"
    status_path, status_path_errors = resolve_repo_relative_path(target_root, status_relative, label="status surface locator")
    locator_errors = [*work_item_path_errors, *recovery_path_errors, *review_path_errors, *status_path_errors]
    if locator_errors:
        return emit(
            {
                "command": "work-item",
                "operation": args.operation,
                "result": "block",
                "summary": "work-item command refused unsafe repo locator input.",
                "missing_inputs": locator_errors,
                "fallback_to": "admission",
            }
        )
    assert work_item_path is not None
    assert recovery_path is not None
    assert review_path is not None
    assert status_path is not None
    runtime_evidence: dict[str, dict[str, Any]] | None = None

    if args.operation == "create":
        required_fields = {
            "goal": args.goal,
            "scope": args.scope,
            "execution_path": args.execution_path,
            "workspace_entry": args.workspace_entry,
            "validation_entry": args.validation_entry,
            "closing_condition": args.closing_condition,
        }
        missing = [field for field, value in required_fields.items() if not isinstance(value, str) or not value.strip()]
        if missing:
            return emit(
                {
                    "command": "work-item",
                    "operation": "create",
                    "result": "block",
                    "summary": "work-item create is missing required static fields.",
                    "missing_inputs": missing,
                    "fallback_to": "admission",
                }
            )
        if work_item_path.exists():
            return emit(
                {
                    "command": "work-item",
                    "operation": "create",
                    "result": "block",
                    "summary": "work-item create refused to overwrite an existing work item.",
                    "missing_inputs": [f"work item already exists: {work_item_relative}"],
                    "fallback_to": "admission",
                }
            )

        artifacts = [work_item_relative, recovery_relative, review_relative, status_relative, *args.artifact]
        deduped_artifacts: list[str] = []
        seen: set[str] = set()
        for artifact in artifacts:
            if artifact in seen:
                continue
            seen.add(artifact)
            deduped_artifacts.append(artifact)

        work_item_payload = {
            "item_id": args.item,
            "goal": args.goal,
            "scope": args.scope,
            "execution_path": args.execution_path,
            "workspace_entry": args.workspace_entry,
            "recovery_entry": recovery_relative,
            "review_entry": review_relative,
            "validation_entry": args.validation_entry,
            "closing_condition": args.closing_condition,
            "associated_artifacts": deduped_artifacts,
        }
        resolved_payload_locators, payload_locator_errors = validate_work_item_payload_locators(
            target_root,
            work_item_payload,
        )
        if payload_locator_errors:
            return emit(
                {
                    "command": "work-item",
                    "operation": "create",
                    "result": "block",
                    "summary": "work-item create refused unsafe authored locator input.",
                    "missing_inputs": payload_locator_errors,
                    "fallback_to": "admission",
                }
            )
        recovery_path = resolved_payload_locators["recovery_entry"]
        review_path = resolved_payload_locators["review_entry"]
        work_item_path.parent.mkdir(parents=True, exist_ok=True)
        work_item_path.write_text(render_work_item(work_item_payload), encoding="utf-8")
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(
            json.dumps(
                {
                    "schema_version": "loom-review/v1",
                    "item_id": args.item,
                    "decision": "fallback",
                    "kind": "general_review",
                    "summary": "Formal review has not been recorded yet.",
                    "reviewer": "not yet assigned",
                    "reviewed_head": git_head_sha(target_root) or "unknown",
                    "reviewed_validation_summary": "No validation recorded yet.",
                    "fallback_to": "admission",
                    "findings": [
                        {
                            "id": "scaffolded-block-1",
                            "summary": "Review artifact scaffolded but not yet concluded.",
                            "severity": "block",
                            "rebuttal": None,
                            "disposition": {
                                "status": "rejected",
                                "summary": "Scaffold placeholder must be replaced by a real formal review conclusion.",
                            },
                        },
                        {
                            "id": "scaffolded-warn-1",
                            "summary": "Record a real review before asking merge checkpoint to consume it.",
                            "severity": "warn",
                            "rebuttal": None,
                            "disposition": {
                                "status": "deferred",
                                "summary": "This follow-up stays open until a real review is recorded.",
                            },
                        },
                    ],
                    "blocking_issues": ["Review artifact scaffolded but not yet concluded."],
                    "follow_ups": ["Record a real review before asking merge checkpoint to consume it."],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        if args.init_recovery:
            recovery_path.parent.mkdir(parents=True, exist_ok=True)
            recovery_path.write_text(
                render_recovery_entry(
                    args.item,
                    {
                        "current_checkpoint": "admission",
                        "current_stop": "Work item scaffolded and waiting for the first execution pass.",
                        "next_step": "Write the first recovery update for this work item.",
                        "blockers": "None recorded.",
                        "latest_validation_summary": "No validation recorded yet.",
                        "recovery_boundary": f"Work item scaffolded at `{work_item_relative}`.",
                        "current_lane": "not yet assigned",
                    },
                ),
                encoding="utf-8",
            )

    else:
        if not work_item_path.exists():
            return emit(
                {
                    "command": "work-item",
                    "operation": "update",
                    "result": "block",
                    "summary": "work-item update requires an existing work item file.",
                    "missing_inputs": [f"missing work item: {work_item_relative}"],
                    "fallback_to": "admission",
                }
            )
        parsed_work_item, parse_errors = parse_work_item(work_item_path, target_root)
        if parse_errors:
            return emit(
                {
                    "command": "work-item",
                    "operation": "update",
                    "result": "block",
                    "summary": "work-item update could not parse the current work item.",
                    "missing_inputs": parse_errors,
                    "fallback_to": "admission",
                }
            )
        work_item_payload = {
            "item_id": args.item,
            "goal": args.goal or str(parsed_work_item["goal"]),
            "scope": args.scope or str(parsed_work_item["scope"]),
            "execution_path": args.execution_path or str(parsed_work_item["execution_path"]),
            "workspace_entry": args.workspace_entry or str(parsed_work_item["workspace_entry"]),
            "recovery_entry": args.recovery_entry or str(parsed_work_item["recovery_entry"]),
            "review_entry": str(parsed_work_item["review_entry"]),
            "validation_entry": args.validation_entry or str(parsed_work_item["validation_entry"]),
            "closing_condition": args.closing_condition or str(parsed_work_item["closing_condition"]),
            "associated_artifacts": list(parsed_work_item["associated_artifacts"]),
        }
        for artifact in args.add_artifact:
            if artifact not in work_item_payload["associated_artifacts"]:
                work_item_payload["associated_artifacts"].append(artifact)
        for artifact in args.remove_artifact:
            work_item_payload["associated_artifacts"] = [
                entry for entry in work_item_payload["associated_artifacts"] if entry != artifact
            ]
        recovery_relative = work_item_payload["recovery_entry"]
        resolved_payload_locators, payload_locator_errors = validate_work_item_payload_locators(
            target_root,
            work_item_payload,
        )
        if payload_locator_errors:
            return emit(
                {
                    "command": "work-item",
                    "operation": "update",
                    "result": "block",
                    "summary": "work-item update refused unsafe authored locator input.",
                    "missing_inputs": payload_locator_errors,
                    "fallback_to": "admission",
                }
            )
        recovery_path = resolved_payload_locators["recovery_entry"]
        work_item_path.write_text(render_work_item(work_item_payload), encoding="utf-8")

    if args.activate:
        if not recovery_path.exists():
            return emit(
                {
                    "command": "work-item",
                    "operation": args.operation,
                    "result": "block",
                    "summary": "work-item activation requires an existing recovery entry.",
                    "missing_inputs": [f"missing recovery entry: {recovery_relative}"],
                    "fallback_to": "admission",
                }
            )
        runtime_evidence, runtime_errors = read_runtime_evidence(target_root, status_relative)
        if runtime_errors:
            return emit(
                {
                    "command": "work-item",
                    "operation": args.operation,
                    "result": "block",
                    "summary": "work-item activation could not read runtime evidence from the current status surface.",
                    "missing_inputs": runtime_errors,
                    "fallback_to": "admission",
                }
            )
        update_active_entry_points(
            target_root,
            args.output,
            item_id=args.item,
            work_item=work_item_relative,
            recovery_entry=recovery_relative,
            status_surface=status_relative,
        )
        _, sync_errors = sync_status_surface(target_root, args.output, runtime_evidence)
        if sync_errors:
            return emit(
                {
                    "command": "work-item",
                    "operation": args.operation,
                    "result": "block",
                    "summary": "work-item activation updated the locator truth, but fact-chain sync failed.",
                    "missing_inputs": sync_errors,
                    "fallback_to": "admission",
                }
            )
    else:
        init_result = load_json_file(output_path)
        fact_chain = init_result.get("fact_chain")
        entry_points = fact_chain.get("entry_points") if isinstance(fact_chain, dict) else None
        if isinstance(entry_points, dict) and entry_points.get("current_item_id") == args.item:
            runtime_evidence, runtime_errors = read_runtime_evidence(target_root, status_relative)
            if runtime_errors:
                return emit(
                    {
                        "command": "work-item",
                        "operation": args.operation,
                        "result": "block",
                        "summary": "work-item authoring updated the active item, but runtime evidence could not be read for status sync.",
                        "missing_inputs": runtime_errors,
                        "fallback_to": "admission",
                    }
                )
            _, sync_errors = sync_status_surface(target_root, args.output, runtime_evidence)
            if sync_errors:
                return emit(
                    {
                        "command": "work-item",
                        "operation": args.operation,
                        "result": "block",
                        "summary": "work-item authoring updated the active item, but fact-chain sync failed.",
                        "missing_inputs": sync_errors,
                        "fallback_to": "admission",
                    }
                )

    context, context_errors = load_context(target_root, args.output, args.item if args.activate else None)
    payload: dict[str, Any] = {
        "command": "work-item",
        "operation": args.operation,
        "result": "pass",
        "summary": (
            "work item was authored successfully."
            if not args.activate
            else "work item was authored and activated as the current Loom fact chain entry."
        ),
        "missing_inputs": [],
        "fallback_to": None,
        "work_item": {
            "id": args.item,
            "path": work_item_relative,
            "recovery_entry": recovery_relative,
            "review_entry": review_relative if args.operation == "create" else work_item_payload["review_entry"],
            "activated": args.activate,
        },
    }
    if context_errors:
        payload["result"] = "block"
        payload["summary"] = "work-item authoring completed, but the fact chain no longer reads cleanly."
        payload["missing_inputs"] = context_errors
        payload["fallback_to"] = "admission"
    else:
        payload["current_fact_chain"] = {
            "current_item_id": context["item_id"],
            "work_item": str(context["report"]["fact_chain"]["entry_points"]["work_item"]),
            "recovery_entry": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
            "status_surface": str(context["report"]["fact_chain"]["entry_points"]["status_surface"]),
        }
    return emit(payload)

def build_required_inputs(context: dict[str, Any]) -> list[dict[str, Any]]:
    plan_path = context["target_root"] / ".loom/specs" / context["item_id"] / "plan.md"
    spec_path = context["target_root"] / ".loom/specs" / context["item_id"] / "spec.md"
    validation_summary = context["latest_validation_summary"].strip()
    return [
        {
            "id": "work_item",
            "status": "present" if context["work_item_path"].exists() else "missing",
            "locator": relative_to_root(context["work_item_path"], context["target_root"]),
        },
        {
            "id": "spec",
            "status": "present" if spec_path.exists() else "missing",
            "locator": relative_to_root(spec_path, context["target_root"]),
        },
        {
            "id": "plan",
            "status": "present" if plan_path.exists() else "missing",
            "locator": relative_to_root(plan_path, context["target_root"]),
        },
        {
            "id": "recovery_baseline",
            "status": "present" if context["recovery_path"].exists() else "missing",
            "locator": relative_to_root(context["recovery_path"], context["target_root"]),
        },
        {
            "id": "validation_baseline",
            "status": "present" if validation_summary and validation_summary.lower() != "not yet run for wi-706." else "missing",
            "locator": "Latest Validation Summary",
        },
        {
            "id": "workspace",
            "status": "present" if context["workspace_path"].exists() else "missing",
            "locator": context["workspace_entry"],
        },
        {
            "id": "ownership_constraints",
            "status": "present" if "ownership" in context["scope"].lower() or "ownership" in context["closing_condition"].lower() else "missing",
            "locator": "Work Item Scope / Closing Condition",
        },
    ]

def delegation_required_field_errors(delegation: dict[str, Any], index: int) -> list[str]:
    required = (
        "task_goal",
        "context_locators",
        "read_scope",
        "write_ownership",
        "non_goals",
        "validation_expectation",
        "output_format",
        "integration_target",
    )
    errors: list[str] = []
    for field in required:
        value = delegation.get(field)
        if value in (None, "", [], {}):
            errors.append(f"delegation[{index}] missing `{field}`")
    if not isinstance(delegation.get("context_locators"), list):
        errors.append(f"delegation[{index}] context_locators must be a list")
    if not isinstance(delegation.get("read_scope"), list):
        errors.append(f"delegation[{index}] read_scope must be a list")
    if not isinstance(delegation.get("write_ownership"), list):
        errors.append(f"delegation[{index}] write_ownership must be a list")
    return errors

def overlap_write_ownership(delegations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    owners: dict[str, list[str]] = {}
    for index, delegation in enumerate(delegations):
        name = str(delegation.get("id") or f"delegation[{index}]")
        write_ownership = delegation.get("write_ownership")
        if not isinstance(write_ownership, list):
            continue
        for path in write_ownership:
            if isinstance(path, str) and path:
                owners.setdefault(path, []).append(name)
    return [
        {
            "path": path,
            "owners": names,
            "result": "block",
            "summary": "overlapping write ownership must be integrated locally before review or merge-ready",
        }
        for path, names in sorted(owners.items())
        if len(names) > 1
    ]

def repeated_blocker_signal(delegations: list[dict[str, Any]]) -> dict[str, Any]:
    by_signature: dict[str, list[str]] = {}
    for index, delegation in enumerate(delegations):
        signature = delegation.get("blocker_signature") or delegation.get("blocker")
        if not isinstance(signature, str) or not signature:
            continue
        name = str(delegation.get("id") or f"delegation[{index}]")
        by_signature.setdefault(signature, []).append(name)
    repeated = [
        {
            "signature": signature,
            "sources": sources,
            "count": len(sources),
            "recommended_action": "pause delegation retries and resolve root cause in the main execution lane",
        }
        for signature, sources in sorted(by_signature.items())
        if len(sources) > 1
    ]
    return {
        "schema_version": REPEATED_BLOCKER_SIGNAL_SCHEMA,
        "result": "block" if repeated else "pass",
        "summary": (
            "repeated blocker candidates require root-cause escalation."
            if repeated
            else "no repeated blocker candidates were detected."
        ),
        "repeated": repeated,
    }

def read_build_evidence(target_root: Path, relative_path: str | None) -> tuple[dict[str, Any] | None, list[str], str | None]:
    if not relative_path:
        return None, ["build evidence is required before build readiness can be claimed"], None
    evidence_path, errors = resolve_repo_relative_path(target_root, relative_path, label="build evidence")
    if errors:
        return None, errors, relative_path
    assert evidence_path is not None
    if not evidence_path.exists():
        return None, [f"build evidence is missing: {relative_path}"], relative_path
    try:
        payload = load_json_file(evidence_path)
    except json.JSONDecodeError as exc:
        return None, [f"build evidence is invalid JSON: {exc.msg}"], relative_path
    if not isinstance(payload, dict):
        return None, ["build evidence must be a JSON object"], relative_path
    return payload, [], relative_path

def build_execution_payload(context: dict[str, Any], evidence_relative: str | None) -> dict[str, Any]:
    required_inputs = build_required_inputs(context)
    missing_inputs = [
        f"required build input `{entry['id']}` is missing"
        for entry in required_inputs
        if entry.get("status") != "present"
    ]
    evidence, evidence_errors, evidence_locator = read_build_evidence(context["target_root"], evidence_relative)
    missing_inputs.extend(evidence_errors)

    delegations: list[dict[str, Any]] = []
    integration_evidence: list[dict[str, Any]] = []
    ownership_conflicts: list[dict[str, Any]] = []
    repeated_signal = {
        "schema_version": REPEATED_BLOCKER_SIGNAL_SCHEMA,
        "result": "pass",
        "summary": "no delegation evidence was available.",
        "repeated": [],
    }
    delegation_errors: list[str] = []
    unintegrated: list[str] = []

    if evidence is not None:
        if evidence.get("schema_version") != BUILD_EVIDENCE_SCHEMA:
            missing_inputs.append(f"build evidence schema must be `{BUILD_EVIDENCE_SCHEMA}`")
        raw_delegations = evidence.get("delegations")
        if not isinstance(raw_delegations, list):
            missing_inputs.append("build evidence must declare `delegations`")
        else:
            delegations = [entry for entry in raw_delegations if isinstance(entry, dict)]
            if len(delegations) != len(raw_delegations):
                missing_inputs.append("every delegation entry must be an object")
            for index, delegation in enumerate(delegations):
                delegation_errors.extend(delegation_required_field_errors(delegation, index))
                status = delegation.get("status")
                if status != "integrated":
                    unintegrated.append(str(delegation.get("id") or f"delegation[{index}]"))
        raw_integration = evidence.get("integration_evidence")
        if isinstance(raw_integration, list):
            integration_evidence = [entry for entry in raw_integration if isinstance(entry, dict)]
        elif raw_integration is not None:
            missing_inputs.append("build evidence `integration_evidence` must be a list when present")
        ownership_conflicts = overlap_write_ownership(delegations)
        repeated_signal = repeated_blocker_signal(delegations)

    missing_inputs.extend(delegation_errors)
    missing_inputs.extend(f"delegation `{name}` output is not integrated into Loom carriers" for name in unintegrated)
    missing_inputs.extend(f"overlapping write ownership for `{conflict['path']}`" for conflict in ownership_conflicts)
    if repeated_signal.get("result") == "block":
        missing_inputs.append("repeated blocker candidates require root-cause escalation before build readiness")

    result = "pass" if not missing_inputs else "block"
    return {
        "schema_version": "loom-build-execution/v1",
        "result": result,
        "summary": (
            "build execution evidence is integrated and ready for review."
            if result == "pass"
            else "build execution evidence is missing, unintegrated, overlapping, or repeatedly blocked."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "build",
        "required_inputs": required_inputs,
        "ownership_contract": {
            "schema_version": SUBAGENT_OWNERSHIP_SCHEMA,
            "required_fields": [
                "task_goal",
                "context_locators",
                "read_scope",
                "write_ownership",
                "non_goals",
                "validation_expectation",
                "output_format",
                "integration_target",
            ],
            "main_executor_responsibilities": [
                "integrate delegated output into implementation",
                "record validation evidence",
                "update recovery and status carriers",
                "feed integrated evidence into later review inputs",
            ],
        },
        "delegation_evidence": {
            "locator": evidence_locator,
            "delegations": delegations,
            "unintegrated": unintegrated,
        },
        "integration_evidence": integration_evidence,
        "ownership_conflicts": ownership_conflicts,
        "repeated_blocker_signal": repeated_signal,
    }

def handle_flow(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    lifecycle_intent = lifecycle_intent_for_operation(args.operation)
    lifecycle_admission = (
        lifecycle_admission_payload(
            target_root=target_root,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
            fr_number=args.fr,
            pr_number=args.pr,
            branch_name=args.branch,
            intent=lifecycle_intent,
        )
        if lifecycle_intent is not None
        else None
    )
    steps: list[dict[str, Any]] = []
    if lifecycle_admission is not None:
        if lifecycle_admission["result"] != "pass":
            return emit(
                {
                    "command": "flow",
                    "operation": args.operation,
                    "result": "block",
                    "summary": "flow stopped before repository carriers because the host-native lifecycle admission is blocked.",
                    "missing_inputs": lifecycle_admission.get("missing_inputs") or lifecycle_admission.get("admission", {}).get("missing_inputs", []),
                    "fallback_to": lifecycle_admission.get("primary_remediation"),
                    "steps": steps,
                    "lifecycle_admission": lifecycle_admission,
                }
            )
    runtime_state = runtime_state_payload(target_root)
    steps.append(
        {
            "name": "runtime-state",
            "result": runtime_state["result"],
            "summary": runtime_state["summary"],
            "missing_inputs": runtime_state["missing_inputs"],
            "fallback_to": runtime_state["fallback_to"],
        }
    )
    if runtime_state["result"] != "pass":
        return emit(
            {
                "command": "flow",
                "operation": args.operation,
                "result": "block",
                "summary": "flow command is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": runtime_state["missing_inputs"],
                "fallback_to": runtime_state["fallback_to"],
                "steps": steps,
                "runtime_state": runtime_state,
            }
        )

    if args.operation == "story":
        return emit(story_flow_payload(target_root=target_root, runtime_state=runtime_state, steps=steps))

    derived_manifest, manifest_errors = host_derived_manifest(target_root)
    if manifest_errors:
        return emit(
            {
                "command": "flow",
                "operation": args.operation,
                "result": "block",
                "summary": "light-profile manifest is invalid; legacy carriers are not a fallback.",
                "missing_inputs": manifest_errors,
                "fallback_to": "adoption",
                "runtime_state": runtime_state,
                "carrier_mutations": False,
                "repo_execution_carriers_consumed": False,
            }
        )
    if derived_manifest is not None:
        return emit(
            host_derived_flow_payload(
                target_root=target_root,
                args=args,
                manifest=derived_manifest,
                runtime_state=runtime_state,
                lifecycle_admission=lifecycle_admission,
            )
        )

    context, errors = load_context_with_retained_idle_fallback(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "flow",
                "operation": args.operation,
                "result": "block",
                "summary": "flow command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "steps": steps,
                "runtime_state": runtime_state,
                **fact_chain_error_contract(errors, output_relative=args.output),
            }
        )

    if args.operation not in {"build", "pre-review", "review", "spec-review", "resume", "handoff", "merge-ready"}:
        return emit(
            {
                "command": "flow",
                "operation": args.operation,
                "result": "block",
                "summary": f"unsupported flow operation: {args.operation}",
                "missing_inputs": [f"unsupported operation: {args.operation}"],
                "fallback_to": None,
                "steps": steps,
                "runtime_state": runtime_state,
            }
        )
    if args.operation in {"review", "spec-review"}:
        payload = build_review_flow_payload(
            target_root,
            args.output,
            args.item,
            operation=args.operation,
            owner=args.owner,
            repo_name=args.repo_name,
            pr_number=args.pr,
            branch_name=args.branch,
            pr_payload_file=args.pr_payload_file,
        )
        payload["execution_attempt"] = persist_execution_attempt(
            context,
            command="flow",
            operation=args.operation,
            payload=payload,
        )
        return emit(payload)

    steps.append(
        {
            "name": "fact-chain",
            "result": "block" if report_blocking_failures(context["report"]) else "pass",
            "summary": (
                "fact chain is readable from a single entry."
                if not report_blocking_failures(context["report"])
                else "fact chain is readable, but provenance or derived-surface drift is blocking."
            ),
            "missing_inputs": report_blocking_messages(context["report"]),
            "fallback_to": "admission" if report_blocking_failures(context["report"]) else None,
            "blocking_failures": report_blocking_failures(context["report"]),
        }
    )

    state_payload = state_check_payload(context)
    steps.append(
        {
            "name": "state-check",
            "result": state_payload["result"],
            "summary": state_payload["summary"],
            "missing_inputs": state_payload["missing_inputs"],
            "fallback_to": state_payload["fallback_to"],
        }
    )

    review_payload: dict[str, Any] | None = None
    build_execution: dict[str, Any] | None = None
    build_suite_validation: dict[str, Any] | None = None
    build_suite_carrier_validation: dict[str, Any] | None = None
    governance_lint: dict[str, Any] | None = None
    retained_host_signals: dict[str, Any] | None = None
    pr_metadata_preflight: dict[str, Any] | None = None
    suite_gate_validation: dict[str, Any] | None = None
    readiness_cost_guard: dict[str, Any] | None = None
    governance_surface = build_governance_surface(target_root)
    upgrade_path = maturity_upgrade_path(governance_surface, target_root)
    repo_interface = governance_surface.get("repo_interface")
    repo_specific_requirements: dict[str, Any] | None = None
    detected_owner, detected_repo = detect_github_repo(target_root)
    flow_owner = args.owner or detected_owner
    flow_repo_name = args.repo_name or detected_repo
    flow_project_drift = project_drift_payload(
        target_root=target_root,
        owner=flow_owner,
        repo_name=flow_repo_name,
        issue_number=args.issue,
        pr_number=args.pr,
        project_number=args.project,
        mode=args.project_drift_mode if args.operation == "merge-ready" else "advisory",
    )
    goal_contract = goal_execution_contract(context) if args.operation == "resume" else None
    goal_readiness = (
        validate_goal_execution_contract(
            goal_contract,
            context,
            issue_number=args.issue,
            pr_number=args.pr,
            branch_name=args.branch,
        )
        if isinstance(goal_contract, dict)
        else None
    )

    if args.operation in {"resume", "handoff"}:
        locate_payload = base_workspace_payload(context, "locate")
        locate_result = "pass" if not locate_payload["purity"]["hard_failures"] else "block"
        locate_step = {
            "name": "workspace-locate",
            "result": locate_result,
            "summary": (
                "workspace is location-resolved and execution-ready."
                if locate_result == "pass"
                else "workspace is location-resolved but not execution-ready."
            ),
            "missing_inputs": list(locate_payload["purity"]["hard_failures"]),
            "fallback_to": "admission" if locate_payload["purity"]["hard_failures"] else None,
        }
        steps.append(locate_step)
    else:
        runtime_fields, runtime_missing = runtime_evidence_from_report(context["report"])
        runtime_result = "pass" if not runtime_missing else "block"
        steps.append(
            {
                "name": "runtime-evidence",
                "result": runtime_result,
                "summary": (
                    "runtime evidence entries are readable."
                    if runtime_result == "pass"
                    else "runtime evidence entries are incomplete or inconsistent."
                ),
                "missing_inputs": runtime_missing,
                "fallback_to": "admission" if runtime_missing else None,
                "runtime_evidence": runtime_fields,
            }
        )
        if args.operation == "build":
            admission_payload = checkpoint_payload("admission", context)
            locate_payload = base_workspace_payload(context, "locate")
            locate_result = "pass" if not locate_payload["purity"]["hard_failures"] else "block"
            build_execution = build_execution_payload(context, args.build_evidence)
            build_suite_validation = spec_suite_validation_payload(context)
            build_suite_step_result = "pass" if suite_validation_ready(build_suite_validation) else "block"
            build_suite_carrier_validation = suite_validation_command_payload(context, domain="carrier")
            steps.extend(
                [
                    {
                        "name": "checkpoint-admission",
                        "result": admission_payload["result"],
                        "summary": admission_payload["summary"],
                        "missing_inputs": admission_payload["missing_inputs"],
                        "fallback_to": admission_payload["fallback_to"],
                    },
                    {
                        "name": "workspace-locate",
                        "result": locate_result,
                        "summary": (
                            "workspace is location-resolved and execution-ready."
                            if locate_result == "pass"
                            else "workspace is location-resolved but not execution-ready."
                        ),
                        "missing_inputs": list(locate_payload["purity"]["hard_failures"]),
                        "fallback_to": "admission" if locate_payload["purity"]["hard_failures"] else None,
                    },
                    {
                        "name": "suite-validate",
                        "result": build_suite_step_result,
                        "summary": str(build_suite_validation.get("summary") or "suite validation was consumed before build readiness."),
                        "missing_inputs": [] if build_suite_step_result == "pass" else suite_validation_missing_inputs(build_suite_validation),
                        "fallback_to": None if build_suite_step_result == "pass" else suite_validation_fallback_to(build_suite_validation),
                        "validation": build_suite_validation,
                    },
                    {
                        "name": "suite-carrier-validate",
                        "result": build_suite_carrier_validation["result"],
                        "summary": build_suite_carrier_validation["summary"],
                        "missing_inputs": build_suite_carrier_validation["missing_inputs"],
                        "fallback_to": build_suite_carrier_validation["fallback_to"],
                        "validation": build_suite_carrier_validation.get("payload"),
                    },
                    {
                        "name": "build-execution",
                        "result": build_execution["result"],
                        "summary": build_execution["summary"],
                        "missing_inputs": build_execution["missing_inputs"],
                        "fallback_to": build_execution["fallback_to"],
                    },
                ]
            )
        elif args.operation == "merge-ready":
            build_payload = checkpoint_payload("build", context)
            merge_payload = checkpoint_payload("merge", context)
            suite_gate_validation = suite_gate_payload_for_surface(context, surface="merge_ready")
            repo_specific_requirements = repo_specific_requirements_payload(
                repo_interface,
                target_root=target_root,
                surface="merge_ready",
            )
            retained_host_signals = retained_host_signals_payload(
                target_root=target_root,
                governance_surface=governance_surface,
                surface="merge_ready",
                current_head=git_head_sha(target_root),
            )
            pr_metadata_preflight = pr_metadata_preflight_payload(
                target_root=target_root,
                surface="merge_ready",
                owner=flow_owner,
                repo_name=flow_repo_name,
                pr_number=args.pr,
                head_sha=None,
                branch_name=args.branch,
                pr_payload_file=args.pr_payload_file,
                governance_surface=governance_surface,
            )
            governance_lint = flow_governance_lint_status(
                context,
                surface="merge_ready",
                repo_specific_requirements=repo_specific_requirements,
            )
            steps.extend(
                [
                    {
                        "name": "checkpoint-build",
                        "result": build_payload["result"],
                        "summary": build_payload["summary"],
                        "missing_inputs": build_payload["missing_inputs"],
                        "fallback_to": build_payload["fallback_to"],
                    },
                    {
                        "name": "checkpoint-merge",
                        "result": merge_payload["result"],
                        "summary": merge_payload["summary"],
                        "missing_inputs": merge_payload["missing_inputs"],
                        "fallback_to": merge_payload["fallback_to"],
                    },
                    suite_gate_step("suite-evidence-validate", suite_gate_validation, "evidence"),
                    suite_gate_step("suite-carrier-validate", suite_gate_validation, "carrier"),
                    {
                        "name": "governance-lint",
                        "result": governance_lint["result"],
                        "summary": governance_lint["result_summary"],
                        "missing_inputs": governance_lint_missing_inputs(governance_lint),
                        "fallback_to": governance_lint_fallback(governance_lint),
                        "governance_lint": governance_lint,
                    },
                    {
                        "name": "pr-metadata-preflight",
                        "result": pr_metadata_preflight["result"],
                        "summary": pr_metadata_preflight["summary"],
                        "missing_inputs": pr_metadata_preflight["missing_inputs"],
                        "fallback_to": pr_metadata_preflight["fallback_to"],
                        "pr_metadata_preflight": pr_metadata_preflight,
                    },
                ]
            )
        elif args.operation == "review":
            build_payload = checkpoint_payload("build", context)
            repo_specific_requirements = repo_specific_requirements_payload(
                repo_interface,
                target_root=target_root,
                surface="review",
            )
            review_record, review_path, review_errors = load_review_record(
                target_root,
                context["item_id"],
                context["review_entry"],
            )
            review_step = {
                "name": "review-entry",
                "result": "pass" if review_record and not review_errors else "block",
                "summary": (
                    "formal review artifact is readable."
                    if review_record and not review_errors
                    else "formal review artifact is missing or invalid."
                ),
                "missing_inputs": review_errors or ([] if review_record else [f"missing review artifact: {review_path}"]),
                "fallback_to": "build" if (review_errors or review_record is None) else None,
            }
            suite_gate_validation = suite_gate_payload_for_surface(context, surface="review")
            steps.extend(
                [
                    {
                        "name": "checkpoint-build",
                        "result": build_payload["result"],
                        "summary": build_payload["summary"],
                        "missing_inputs": build_payload["missing_inputs"],
                        "fallback_to": build_payload["fallback_to"],
                    },
                    suite_gate_step("suite-evidence-validate", suite_gate_validation, "evidence"),
                    suite_gate_step("suite-carrier-validate", suite_gate_validation, "carrier"),
                    review_step,
                ]
            )
            review_payload = {
                "path": review_path,
                "record": review_record,
            }
        else:
            admission_payload = checkpoint_payload("admission", context)
            if args.operation == "pre-review":
                if suite_gate_required_for_surface(context, surface="pre_review"):
                    suite_gate_validation = suite_gate_validation_payload(context, surface="pre_review")
                else:
                    suite_gate_validation = suite_gate_not_applicable_payload(context, surface="pre_review")
                repo_specific_requirements = repo_specific_requirements_payload(
                    repo_interface,
                    target_root=target_root,
                    surface="pre_review",
                )
                pr_metadata_preflight = pr_metadata_preflight_payload(
                    target_root=target_root,
                    surface="pre_review",
                    owner=flow_owner,
                    repo_name=flow_repo_name,
                    pr_number=args.pr,
                    branch_name=args.branch,
                    pr_payload_file=args.pr_payload_file,
                    governance_surface=governance_surface,
                )
                governance_lint = flow_governance_lint_status(
                    context,
                    surface="pre_review",
                    repo_specific_requirements=repo_specific_requirements,
                )
                readiness_cost_guard = pre_review_readiness_cost_guard_payload(
                    context,
                    target_root=target_root,
                    owner=flow_owner,
                    repo_name=flow_repo_name,
                    pr_number=args.pr,
                    branch_name=args.branch,
                    pr_payload_file=args.pr_payload_file,
                    pr_metadata_preflight=pr_metadata_preflight,
                )
            locate_payload = base_workspace_payload(context, "locate")
            locate_result = "pass" if not locate_payload["purity"]["hard_failures"] else "block"
            locate_step = {
                "name": "workspace-locate",
                "result": locate_result,
                "summary": (
                    "workspace is location-resolved and execution-ready."
                    if locate_result == "pass"
                    else "workspace is location-resolved but not execution-ready."
                ),
                "missing_inputs": list(locate_payload["purity"]["hard_failures"]),
                "fallback_to": "admission" if locate_payload["purity"]["hard_failures"] else None,
            }
            steps.append(
                {
                    "name": "checkpoint-admission",
                    "result": admission_payload["result"],
                    "summary": admission_payload["summary"],
                    "missing_inputs": admission_payload["missing_inputs"],
                    "fallback_to": admission_payload["fallback_to"],
                }
            )
            steps.append(locate_step)
            if args.operation == "pre-review" and isinstance(governance_lint, dict):
                if isinstance(suite_gate_validation, dict):
                    steps.append(suite_gate_step("suite-evidence-validate", suite_gate_validation, "evidence"))
                    steps.append(suite_gate_step("suite-carrier-validate", suite_gate_validation, "carrier"))
                steps.append(
                    {
                        "name": "governance-lint",
                        "result": governance_lint["result"],
                        "summary": governance_lint["result_summary"],
                        "missing_inputs": governance_lint_missing_inputs(governance_lint),
                        "fallback_to": governance_lint_fallback(governance_lint),
                        "governance_lint": governance_lint,
                    }
                )
                if isinstance(pr_metadata_preflight, dict):
                    steps.append(
                        {
                            "name": "pr-metadata-preflight",
                            "result": pr_metadata_preflight["result"],
                            "summary": pr_metadata_preflight["summary"],
                            "missing_inputs": pr_metadata_preflight["missing_inputs"],
                            "fallback_to": pr_metadata_preflight["fallback_to"],
                            "pr_metadata_preflight": pr_metadata_preflight,
                        }
                    )
                if isinstance(readiness_cost_guard, dict):
                    steps.append(
                        {
                            "name": "pre-review-readiness-cost-guard",
                            "result": readiness_cost_guard["result"],
                            "summary": readiness_cost_guard["summary"],
                            "missing_inputs": readiness_cost_guard["missing_inputs"],
                            "fallback_to": readiness_cost_guard["fallback_to"],
                            "readiness_cost_guard": readiness_cost_guard,
                        }
                    )

    if args.operation in {"resume", "pre-review", "merge-ready"} and args.project is not None:
        project_step_result = (
            "block"
            if args.operation == "merge-ready" and flow_project_drift.get("mode") == "blocking" and flow_project_drift.get("result") == "block"
            else "pass"
        )
        steps.append(
            {
                "name": "project-drift",
                "result": project_step_result,
                "summary": flow_project_drift["summary"],
                "missing_inputs": flow_project_drift.get("missing_inputs", []) if project_step_result == "block" else [],
                "fallback_to": flow_project_drift.get("fallback_to") if project_step_result == "block" else None,
                "project_drift": flow_project_drift,
            }
        )
    if args.operation in {"resume", "merge-ready"} and args.issue is not None:
        detected_owner, detected_repo = detect_github_repo(target_root)
        dependency_owner = args.owner or detected_owner
        dependency_repo = args.repo_name or detected_repo
        dependency_missing: list[str] = []
        issue_payload_for_dependency: dict[str, Any] | None = None
        dependency_graph: dict[str, Any] = {
            "schema_version": HOST_DEPENDENCY_GRAPH_SCHEMA,
            "availability": "not_requested",
            "edges": [],
            "findings": [],
        }
        if not dependency_owner or not dependency_repo:
            dependency_missing.append("owner/repo")
        else:
            issue_payload_for_dependency, issue_errors = github_issue_payload(
                target_root,
                dependency_owner,
                dependency_repo,
                args.issue,
            )
            dependency_missing.extend(f"issue: {message}" for message in issue_errors)
            if issue_payload_for_dependency is not None:
                dependency_graph = dependency_graph_payload(
                    issue_number=args.issue,
                    issue_payload=issue_payload_for_dependency,
                    native_dependency_payload=github_issue_dependencies_payload(
                        target_root,
                        dependency_owner,
                        dependency_repo,
                        args.issue,
                    ),
                )
        dependency_blocking = [
            finding
            for finding in dependency_graph.get("findings", [])
            if isinstance(finding, dict)
            and (
                finding.get("severity") == "block"
                or (args.operation == "merge-ready" and finding.get("kind") == "stale_native_edge")
            )
        ]
        dependency_step_result = "block" if dependency_missing or dependency_blocking else "pass"
        steps.append(
            {
                "name": "native-dependency",
                "result": dependency_step_result,
                "summary": (
                    "native dependency mirror is readable and has no open blocker for this issue."
                    if dependency_step_result == "pass"
                    else "native dependency mirror has blockers or unreadable host signals."
                ),
                "missing_inputs": [
                    *dependency_missing,
                    *[str(finding.get("subject") or finding.get("kind")) for finding in dependency_blocking],
                ],
                "fallback_to": "manual-reconciliation" if dependency_step_result == "block" else None,
                "dependency_graph": dependency_graph,
            }
        )
    if args.operation == "resume" and isinstance(goal_readiness, dict):
        steps.append(
            {
                "name": "goal-bootstrap",
                "result": goal_readiness["result"],
                "summary": goal_readiness["summary"],
                "missing_inputs": goal_readiness["missing_inputs"],
                "fallback_to": goal_readiness["fallback_to"],
            }
        )

    result = "pass"
    fallback_to: str | None = None
    for step in steps:
        step_result = step["result"]
        if step_result == "fallback":
            result = "fallback"
            fallback_to = step.get("fallback_to") or "admission"
            break
        if step_result == "block" and result == "pass":
            result = "block"
            fallback_to = step.get("fallback_to")
    if (
        args.operation in {"pre-review", "merge-ready"}
        and isinstance(governance_lint, dict)
        and governance_lint.get("result") == "block"
    ):
        result = "block"
        fallback_to = governance_lint_fallback(governance_lint) or fallback_to
    if (
        args.operation == "merge-ready"
        and isinstance(retained_host_signals, dict)
        and retained_host_signals.get("result") == "block"
    ):
        result = "block"
        fallback_to = retained_host_signals.get("fallback_to") or fallback_to
    if (
        args.operation in {"pre-review", "merge-ready"}
        and isinstance(pr_metadata_preflight, dict)
        and pr_metadata_preflight.get("result") == "block"
    ):
        result = "block"
        fallback_to = pr_metadata_preflight.get("fallback_to") or fallback_to
    if (
        args.operation == "pre-review"
        and isinstance(readiness_cost_guard, dict)
        and readiness_cost_guard.get("result") == "block"
    ):
        result = "block"
        fallback_to = readiness_cost_guard.get("fallback_to") or fallback_to
    if result != "block" and isinstance(repo_specific_requirements, dict) and repo_specific_requirements["result"] == "block":
        result = "block"
        fallback_to = fallback_to or repo_specific_requirements["fallback_to"]

    if args.operation == "resume":
        summary = (
            "resume flow rebuilt the current execution context and next step."
            if result == "pass"
            else "resume flow rebuilt context but found blocking signals before execution can continue."
        )
    elif args.operation == "handoff":
        summary = (
            "handoff flow produced the minimum writeback checklist and locator set."
            if result == "pass"
            else "handoff flow produced the minimum writeback checklist, but blocking signals remain before transfer."
        )
    elif args.operation == "build":
        summary = (
            "build flow found integrated execution evidence and can proceed toward review."
            if result == "pass"
            else "build flow found missing, unintegrated, overlapping, or repeatedly blocked execution evidence."
        )
        if build_execution and build_execution["result"] == "block":
            fallback_to = fallback_to or "build"
    elif args.operation == "merge-ready":
        if isinstance(repo_specific_requirements, dict) and result == "block" and repo_specific_requirements["result"] == "block":
            summary = "merge-ready flow found companion-declared blocking requirements that Loom core does not satisfy on its own."
        else:
            summary = (
                "merge-ready flow found the required evidence and checkpoint state for host merge."
                if result == "pass"
                else "merge-ready flow found fallback or blocking signals before host merge."
            )
    elif args.operation == "review":
        if isinstance(repo_specific_requirements, dict) and result == "block" and repo_specific_requirements["result"] == "block":
            summary = "review flow exposed companion-declared blocking requirements instead of pretending Loom core already covers them."
        else:
            summary = (
                "review flow prepared the semantic review context and exposed the formal review artifact."
                if result == "pass"
                else "review flow found missing review material or earlier blocking signals."
            )
    else:
        summary = (
            "pre-review flow is ready to proceed."
            if result == "pass"
            else "pre-review flow found blocking signals before review."
        )
    missing_inputs: list[str] = []
    for step in steps:
        if step["result"] in {"block", "fallback"}:
            for message in step.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(message)
    if isinstance(repo_specific_requirements, dict) and repo_specific_requirements["result"] == "block":
        for message in repo_specific_requirements.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    if args.operation == "merge-ready" and isinstance(retained_host_signals, dict) and retained_host_signals.get("result") == "block":
        for message in retained_host_signals.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    if (
        args.operation in {"pre-review", "merge-ready"}
        and isinstance(pr_metadata_preflight, dict)
        and pr_metadata_preflight.get("result") == "block"
    ):
        for message in pr_metadata_preflight.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    if (
        args.operation == "pre-review"
        and isinstance(readiness_cost_guard, dict)
        and readiness_cost_guard.get("result") == "block"
    ):
        for message in readiness_cost_guard.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    if args.operation == "resume":
        repo_interface = governance_surface.get("repo_interface")
        repo_interop = governance_surface.get("repo_interop")
        adoption_workflow_active = (
            isinstance(repo_interface, dict)
            and repo_interface.get("availability") in {"companion_docs_only", "incomplete"}
        ) or (
            isinstance(repo_interop, dict)
            and repo_interop.get("availability") == "incomplete"
        )
        if adoption_workflow_active:
            for message in governance_surface.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(message)
            for message in upgrade_path.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(message)
        if adoption_workflow_active and missing_inputs and result == "pass":
            result = "block"
            fallback_to = fallback_to or "adoption"
            summary = "resume flow rebuilt context but found adoption guidance gaps before execution can continue."
    adoption_guidance = None
    if args.operation == "resume":
        guided = upgrade_path.get("guided_adoption_plan") if isinstance(upgrade_path, dict) else None
        decisions = upgrade_path.get("adoption_decisions") if isinstance(upgrade_path, dict) else None
        next_step = None
        if isinstance(guided, dict):
            for step in guided.get("steps", []):
                if isinstance(step, dict) and step.get("status") in {"missing", "blocked"}:
                    next_step = step
                    break
        adoption_guidance = {
            "schema_version": "loom-adoption-resume-guidance/v1",
            "result": upgrade_path.get("result") if isinstance(upgrade_path, dict) else "block",
            "summary": "resume exposes the next adoption read/judge/write/verify step without writing adoption state.",
            "next_step": next_step,
            "adoption_decisions": decisions,
            "guided_adoption_plan": guided,
        }

    fact_chain_provenance = report_provenance(context["report"])
    recovery_readiness = report_recovery_readiness(context["report"])
    execution_ledger = report_execution_ledger(context["report"])
    blocking_failures = report_blocking_failures(context["report"])
    if recovery_readiness.get("result") == "block" and result == "pass":
        result = "block"
        fallback_to = fallback_to or recovery_readiness.get("fallback_to") or "admission"
        summary = "flow rebuilt context but recovery readiness is blocking."

    payload = {
            "command": "flow",
            "operation": args.operation,
            "item": {
                "id": context["item_id"],
                "goal": context["goal"],
                "scope": context["scope"],
                "execution_path": context["execution_path"],
            },
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": fallback_to,
            "steps": steps,
            "runtime_state": runtime_state,
            **({"lifecycle_admission": lifecycle_admission} if lifecycle_admission is not None else {}),
            "provenance": fact_chain_provenance,
            "recovery_readiness": recovery_readiness,
            "execution_ledger": execution_ledger,
            "blocking_failures": blocking_failures,
            "project_drift": flow_project_drift,
            **({"governance_lint": governance_lint} if args.operation in {"pre-review", "merge-ready"} else {}),
            **({"pr_metadata_preflight": pr_metadata_preflight} if args.operation in {"pre-review", "merge-ready"} else {}),
            **({"readiness_cost_guard": readiness_cost_guard} if args.operation == "pre-review" else {}),
            **({"goal_execution_contract": goal_contract, "goal_readiness": goal_readiness} if args.operation == "resume" else {}),
            **({"governance_surface": governance_surface} if args.operation == "resume" else {}),
            **({"maturity_upgrade_path": upgrade_path} if args.operation == "resume" else {}),
            **({"adoption_guidance": adoption_guidance} if args.operation == "resume" else {}),
            **(
                {
                    "workspace": {
                        "entry": locate_payload["workspace"]["entry"],
                        "path": locate_payload["workspace"]["path"],
                        "exists": locate_payload["workspace"]["exists"],
                    },
                    "checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                    "lifecycle_expectations": locate_payload["lifecycle_expectations"],
                }
                if args.operation in {"resume", "handoff"}
                else {}
            ),
            **(
                {
                    "recovery": {
                        "path": locate_payload["recovery"]["path"],
                        "current_stop": locate_payload["recovery"]["current_stop"],
                        "next_step": context["next_step"],
                        "blockers": context["blockers"],
                        "latest_validation_summary": context["latest_validation_summary"],
                        "adoption_source": "maturity_upgrade_path",
                        "companion_locator": ".loom/companion/repo-interface.json",
                        "interop_locator": ".loom/companion/interop.json",
                        "post_adoption_next_step": adoption_guidance.get("next_step") if isinstance(adoption_guidance, dict) else None,
                        "adoption_verify_summary": (
                            f"python3 tools/loom_flow.py adopt verify --target {command_target(target_root)} --item {context['item_id']}"
                        ),
                    },
                }
                if args.operation == "resume"
                else {}
            ),
            **(
                {
                    "recovery_entry": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
                    "status_surface": str(context["report"]["fact_chain"]["entry_points"]["status_surface"]),
                    "current_stop": context["current_stop"],
                    "next_step": context["next_step"],
                    "blockers": context["blockers"],
                    "latest_validation_summary": context["latest_validation_summary"],
                    "fallback_target": fallback_to,
                    "writeback_fields": [
                        "current_stop",
                        "next_step",
                        "blockers",
                        "latest_validation_summary",
                    ],
                }
                if args.operation == "handoff"
                else {}
            ),
            **(
                {
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                    "runtime_evidence": runtime_fields,
                    "suite_validation": build_suite_validation,
                    "suite_carrier_validation": build_suite_carrier_validation,
                    "build_execution": build_execution,
                    "current_checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                    "current_lane": context["current_lane"],
                }
                if args.operation == "build"
                else {}
            ),
            **(
                {
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                    "runtime_evidence": runtime_fields,
                    "build_checkpoint": {
                        "result": build_payload["result"],
                        "summary": build_payload["summary"],
                        "missing_inputs": build_payload["missing_inputs"],
                        "fallback_to": build_payload["fallback_to"],
                    },
                    "budget_risk": derive_execution_budget_risk(
                        governance_surface.get("github_control_plane", {}).get("api_snapshot", {}).get("budget")
                        if isinstance(governance_surface.get("github_control_plane"), dict)
                        else None
                    ),
                    "review": review_payload,
                    "repo_specific_requirements": repo_specific_requirements,
                    "suite_gate_validation": suite_gate_validation,
                    "readiness_cost_guard": readiness_cost_guard,
                    "current_checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                }
                if args.operation == "review"
                else {}
            ),
            **(
                {
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                    "runtime_evidence": runtime_fields,
                    "admission_checkpoint": {
                        "result": admission_payload["result"],
                        "summary": admission_payload["summary"],
                        "missing_inputs": admission_payload["missing_inputs"],
                        "fallback_to": admission_payload["fallback_to"],
                    },
                    "repo_specific_requirements": repo_specific_requirements,
                    "suite_gate_validation": suite_gate_validation,
                    "current_checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                    "current_lane": context["current_lane"],
                }
                if args.operation == "pre-review"
                else {}
            ),
            **(
                {
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                    "runtime_evidence": runtime_fields,
                    "build_checkpoint": {
                        "result": build_payload["result"],
                        "summary": build_payload["summary"],
                        "missing_inputs": build_payload["missing_inputs"],
                        "fallback_to": build_payload["fallback_to"],
                    },
                    "merge_checkpoint": {
                        "result": merge_payload["result"],
                        "summary": merge_payload["summary"],
                        "missing_inputs": merge_payload["missing_inputs"],
                        "fallback_to": merge_payload["fallback_to"],
                        "pr_template": merge_payload.get("pr_template"),
                    },
                    "budget_risk": merge_payload.get("budget_risk"),
                    "spec_review": merge_payload.get("spec_review"),
                    "retained_host_signals": retained_host_signals,
                    "merge_ready_authority": {
                        "authority_after": "loom merge-ready result",
                        "host_signal_role": "retained_input_only",
                        "no_dual_authority": bool(
                            isinstance(retained_host_signals, dict)
                            and retained_host_signals.get("result") == "pass"
                        ),
                    },
                    "current_checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                    "current_lane": context["current_lane"],
                    "latest_validation_summary": context["latest_validation_summary"],
                    "repo_specific_requirements": repo_specific_requirements,
                    "suite_gate_validation": suite_gate_validation,
                }
                if args.operation == "merge-ready"
                else {}
            ),
        }
    payload["execution_attempt"] = persist_execution_attempt(
        context,
        command="flow",
        operation=args.operation,
        payload=payload,
    )
    return emit(payload)

def handle_shadow_parity(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            runtime_state_block_payload(
                command="shadow-parity",
                runtime_state=runtime_state,
                summary="shadow parity is blocked because the Loom runtime state is inconsistent.",
            )
        )

    governance_surface = build_governance_surface(target_root)
    repo_interop = governance_surface.get("repo_interop")
    requested_surfaces = SHADOW_PARITY_SURFACES if args.surface == "all" else (args.surface,)
    mode = "blocking" if args.blocking else args.mode
    reports = [
        shadow_parity_report(
            repo_interop,
            target_root=target_root,
            surface=surface,
        )
        for surface in requested_surfaces
    ]

    all_match = bool(reports) and all(report["result"] == "match" for report in reports)
    blocking_reports = [report for report in reports if report.get("result") != "match"]
    if mode == "blocking":
        result = "pass" if all_match else "block"
        for report in blocking_reports:
            report["blocking"] = True
    else:
        result = "pass" if all_match else "warn"
    if result == "pass":
        summary = "shadow parity matches across all requested surfaces."
    elif mode == "blocking":
        summary = "shadow parity blocking mode found mismatch or unreadable surfaces."
    else:
        summaries = {report["result"] for report in reports}
        if "mismatch" in summaries:
            summary = "shadow parity found mismatches between Loom and repo-native governance surfaces."
        else:
            summary = "shadow parity could not fully read the declared governance surfaces."

    missing_inputs: list[str] = []
    missing_details: list[Any] = []
    for report in reports:
        for message in report.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
        details = report.get("missing_details")
        if isinstance(details, list):
            for detail in details:
                if detail not in missing_details:
                    missing_details.append(detail)
    blocking_failures = [
        {
            "category": "drift" if report.get("classification") == "drift" else "gate_failure",
            "kind": "parallel_truth_drift" if report.get("result") == "mismatch" else "shadow_parity_unreadable",
            "surface": report.get("surface"),
            "message": report.get("summary"),
            "blocking": mode == "blocking",
            "fallback_to": "manual-reconciliation",
        }
        for report in blocking_reports
        if isinstance(report, dict)
    ]

    payload = {
        "command": "shadow-parity",
        "mode": mode,
        "blocking": mode == "blocking",
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": "manual-reconciliation" if result == "block" else None,
        "runtime_state": runtime_state,
        "governance_surface": governance_surface,
        "reports": reports,
        "blocking_failures": blocking_failures,
    }
    if missing_details:
        payload["missing_details"] = missing_details
    return emit(payload)

def handle_runtime_parity(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    return emit(
        runtime_parity_payload(
            target_root=target_root,
            output_relative=args.output,
            expected_item=args.item,
        )
    )
WORK_ITEM_FIELD_LABELS = {
    "item_id": "Item ID",
    "goal": "Goal",
    "scope": "Scope",
    "execution_path": "Execution Path",
    "workspace_entry": "Workspace Entry",
    "recovery_entry": "Recovery Entry",
    "validation_entry": "Validation Entry",
    "closing_condition": "Closing Condition",
}
