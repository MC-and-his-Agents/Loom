#!/usr/bin/env python3
"""Delivery gates, PR controls, review bindings, and controlled merge domain."""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None  # type: ignore[assignment]
from fact_chain_support import (
    COMPANION_INIT_RESULT,
    DEFAULT_INIT_RESULT,
    STATUS_FIELDS,
    STATUS_SOURCE_FIELDS,
    default_init_result_fallback,
    inspect_fact_chain,
    load_json_file,
    markdown_sections,
    parse_key_value_section,
    parse_recovery_entry,
    parse_work_item,
    path_boundary_missing_details,
    resolve_repo_relative_path,
)
from authority_contract import parse_typed_locator, typed_locator
from failure_envelope import envelope as failure_envelope, primary_cause as failure_primary_cause
from companion_contract import load_repo_interop_contract
from flow_runtime import command_target, current_iso_timestamp, emit, git_branch, git_head_sha, resolve_target_arg, run_git, runtime_state_payload
from github_host import (
    HOST_API_NEXT_ACTIONS,
    gh_json,
    gh_rest_json,
    gh_rest_list,
    github_issue_dependencies_payload,
    github_issue_payload,
    github_issue_state,
    github_pr_payload,
    github_public_rest_list,
    host_api_anonymous_fallback_blocked,
    host_api_diagnostic_message,
    run_process,
)
from governance_surface import (
    build_governance_surface,
    derive_execution_budget_risk,
    empty_target_release_status,
    required_status_contexts_from_branch_rules as governance_required_status_contexts_from_branch_rules,
)
from runtime_paths import (
    global_runtime_path,
    is_global_runtime_locator,
    shared_script,
)

FLOW_ENTRYPOINT = Path(__file__).with_name("loom_flow.py")

PR_TEMPLATE_SECTIONS = (
    "## Summary",
    "## Validation",
    "## Risks And Follow-ups",
    "## Related Work",
)

OWNED_TEMP_ROOTS = (
    ".loom/.tmp",
    ".loom/tmp",
    ".loom/runtime/cache",
    ".loom/runtime/tmp",
    ".loom/flow/tmp",
)

OWNED_RUNTIME_EVIDENCE_ROOTS = (
    ".loom/runtime/review",
    ".loom/runtime/attempts",
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

GITHUB_PR_URL_RE = re.compile(r"github\.com/(?P<owner>[^/\s`]+)/(?P<repo>[^/\s`]+)/pull/(?P<number>\d+)")

GITHUB_ISSUE_REF_RE = re.compile(r"(?i)\b(?:github\s+issue|issue)\s+#?(?P<number>\d+)\b")

GITHUB_PR_REF_RE = re.compile(r"(?i)\b(?:github\s+pr|github\s+pull\s+request|pull\s+request|pr)\s+#?(?P<number>\d+)\b")

HOST_DEPENDENCY_GRAPH_SCHEMA = "loom-host-dependency-graph/v1"

GOVERNANCE_LINT_RESULT_SCHEMA = "loom-governance-lint-result/v1"

GOVERNANCE_LINT_STATUS_SCHEMA = "loom-governance-lint-status/v1"

CLOSEOUT_LIGHT_PROFILE = "closeout-contract"

PR_METADATA_PREFLIGHT_SCHEMA = "loom-pr-metadata-preflight/v1"

PR_METADATA_MACHINE_SCHEMA = "loom-repo-pr-metadata/v1"

PR_METADATA_PARSER_VERSION = "loom-pr-metadata-parser/v2"

PR_METADATA_SUPPORTED_PARSER_VERSIONS = (PR_METADATA_PARSER_VERSION, "loom-pr-metadata-parser/v1", "repo-parser/v1")

GATE_FREEZE_SCHEMA = "loom-gate-freeze/v1"

CLOSEOUT_FREEZE_SCHEMA = "loom-closeout-freeze/v1"

CLOSEOUT_SPECIFIC_GATE_SCHEMA = "loom-closeout-specific-gate/v1"

HOSTED_FREEZE_ADMISSION_SCHEMA = "loom-hosted-freeze-admission/v1"

FAILURE_CLASSIFIER_SCHEMA = "loom-failure-classifier/v1"

FAILURE_CLASSIFIER_CATEGORIES = (
    "code_semantics",
    "pr_metadata_drift",
    "carrier_refresh_needed",
    "shadow_stale",
    "review_stale",
    "host_api_unreadable",
    "ci_environment",
    "permission",
    "external_service_flake",
    "suite_evidence_contract_invalid",
    "task_carrier_contract_invalid",
    "contract_vocabulary_invalid",
    "unsupported_command_surface",
    "freeze_artifact_unreadable",
    "hosted_snapshot_mismatch",
    "release_evidence_phase_error",
)

FAILURE_CLASSIFIER_KIND_MAP = {
    "head_binding_drift": "review_stale",
    "review_stale": "review_stale",
    "validation_summary_drift": "review_stale",
    "shadow_source_hash_drift": "shadow_stale",
    "carrier_refresh_stale": "carrier_refresh_needed",
    "head_or_pr_drift": "pr_metadata_drift",
    "stale_evidence": "suite_evidence_contract_invalid",
    "missing_evidence_map": "suite_evidence_contract_invalid",
    "missing_fresh_verification_evidence": "suite_evidence_contract_invalid",
    "missing_task_carrier_locator": "task_carrier_contract_invalid",
    "carrier_truth_conflict": "task_carrier_contract_invalid",
    "invalid_not_applicable_rationale": "contract_vocabulary_invalid",
    "missing_suite_path_decision": "contract_vocabulary_invalid",
    "unsupported_command_surface": "unsupported_command_surface",
    "freeze_artifact_unreadable": "freeze_artifact_unreadable",
    "hosted_snapshot_mismatch": "hosted_snapshot_mismatch",
    "release_evidence_phase_error": "release_evidence_phase_error",
    "closeout_terminal_subject_drift": "pr_metadata_drift",
    "closeout_host_git_mismatch": "host_api_unreadable",
    "closeout_dependency_graph_drift": "host_api_unreadable",
    "closeout_carrier_drift": "carrier_refresh_needed",
    "closeout_shadow_stale": "shadow_stale",
    "closeout_release_evidence_gap": "release_evidence_phase_error",
    "closeout_retained_review_unconsumable": "review_stale",
    "closeout_allowed_paths_violation": "code_semantics",
    "closeout_batch_mixed_risk": "code_semantics",
    "host_api_unreadable": "host_api_unreadable",
    "permission": "permission",
    "ci_environment": "ci_environment",
    "external_service_flake": "external_service_flake",
}

FAILURE_CLASSIFIER_INPUT_MAP = {
    "pr_metadata": "pr_metadata_drift",
    "pr_body_pin": "pr_metadata_drift",
    "carrier_refresh": "carrier_refresh_needed",
    "shadow_parity": "shadow_stale",
    "shadow_freshness": "shadow_stale",
    "review_binding": "review_stale",
    "suite_evidence_validation": "suite_evidence_contract_invalid",
    "suite_validation": "contract_vocabulary_invalid",
    "suite_carrier_validation": "task_carrier_contract_invalid",
    "command_surface": "unsupported_command_surface",
    "release_requiredness": "release_evidence_phase_error",
}

FAILURE_CLASSIFIER_NEXT_ACTIONS = {
    "code_semantics": "fix the code or contract violation, then rerun the failing gate.",
    "pr_metadata_drift": "regenerate or update the PR body machine carrier, read it back, then rerun gate freeze.",
    "carrier_refresh_needed": "refresh Loom carriers, then rerun gate freeze.",
    "shadow_stale": "refresh or restore shadow evidence, then rerun shadow parity and gate freeze.",
    "review_stale": "rerun authored Loom review for the current head, then rerun gate freeze.",
    "host_api_unreadable": HOST_API_NEXT_ACTIONS["host_api_unreadable"],
    "ci_environment": "fix the CI/runtime environment and rerun the check.",
    "permission": HOST_API_NEXT_ACTIONS["permission"],
    "external_service_flake": "wait for the external service to recover, then rerun once.",
    "suite_evidence_contract_invalid": "fix suite evidence contract fields, then rerun suite evidence validation.",
    "task_carrier_contract_invalid": "fix Work Item/task carrier fields, then rerun suite carrier validation.",
    "contract_vocabulary_invalid": "use the supported contract vocabulary, then rerun validation.",
    "unsupported_command_surface": "use an implemented Loom command surface or update the command matrix.",
    "freeze_artifact_unreadable": "restore the freeze artifact or declared source file, then rerun gate freeze.",
    "hosted_snapshot_mismatch": "regenerate the freeze snapshot from the current PR/head/body/carriers, then rerun hosted admission.",
    "release_evidence_phase_error": "record release/no-release evidence in the correct phase, then rerun gate freeze.",
}
HOST_API_TOKEN_BRIDGE_COMMAND = "CODEX_EXPORT_GH_TOKEN=1 <same loom command>"
HOST_API_TOKEN_BRIDGE_NEXT_ACTION = FAILURE_CLASSIFIER_NEXT_ACTIONS["host_api_unreadable"]

GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID = "loom-governance-intensity"

GOVERNANCE_INTENSITY_VALUES = {"light", "standard", "reinforced"}

GOVERNANCE_CHANGE_CLASS_VALUES = {
    "docs_only",
    "docs_governance",
    "contract",
    "runtime",
    "fixture",
    "release",
    "workflow",
    "runtime_upgrade",
    "metadata_schema",
    "host_write",
    "permissions",
    "external_action",
    "mixed",
}

GOVERNANCE_SUITE_PATH_VALUES = {"full", "minimal", "not_applicable"}

GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT = "host_readback_only"

GOVERNANCE_REVIEW_REQUIREMENT_VALUES = {
    "current_head_review_required",
    "specialized_review_required",
    GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT,
}

GOVERNANCE_RELEASE_JUDGMENT_VALUES = {"release_required", "no_release", "deferred_release_judgment_blocking"}

GOVERNANCE_NOT_APPLICABLE_REQUIRED_FIELDS = (
    "rationale",
    "consumer_boundary",
    "recheck_condition",
    "scope_proof",
    "review_requirement",
)

GOVERNANCE_METADATA_FIELD_ALLOWLIST = {
    "work_item_locator",
    "governance_intensity",
    "governance_mode",
    "governance_assurance",
    "advisory_risk_label",
    "host_enforcement_required",
    "change_class",
    "suite_path",
    "suite_not_applicable",
    "review_requirement",
    "fact_chain_required",
    "pr_gate_required",
    "release_judgment",
    "closeout_required",
    "upgrade_triggers",
    "anchor_issue",
    "covered_issues",
    "excluded_scope",
}

GOVERNANCE_METADATA_HOST_OWNED_FIELDS = {
    "branch",
    "head_sha",
    "merge_commit",
    "status_checks",
    "check_runs",
    "headRefName",
    "headRefOid",
    "mergeCommit",
    "statusCheckRollup",
}

PR_METADATA_DIAGNOSTIC_ALLOWED_VALUES = {
    "parser_version": list(PR_METADATA_SUPPORTED_PARSER_VERSIONS),
    "fields.governance_intensity": sorted(GOVERNANCE_INTENSITY_VALUES),
    "fields.change_class": sorted(GOVERNANCE_CHANGE_CLASS_VALUES),
    "fields.suite_path": sorted(GOVERNANCE_SUITE_PATH_VALUES),
    "fields.review_requirement": sorted(GOVERNANCE_REVIEW_REQUIREMENT_VALUES),
    "fields.release_judgment": sorted(GOVERNANCE_RELEASE_JUDGMENT_VALUES),
    "fields.suite_not_applicable.review_requirement": sorted(GOVERNANCE_REVIEW_REQUIREMENT_VALUES),
}

GOVERNANCE_HIGH_RISK_CHANGE_CLASSES = {
    "runtime",
    "release",
    "workflow",
    "metadata_schema",
    "host_write",
    "permissions",
    "external_action",
    "mixed",
}

GOVERNANCE_LITE_ALLOWED_CHANGE_CLASSES = {"docs_only", "docs_governance", "fixture", "runtime_upgrade"}

GOVERNANCE_LITE_NOT_APPLICABLE_CHANGE_CLASSES = {"docs_only", "docs_governance", "runtime_upgrade"}

GOVERNANCE_LITE_MINIMAL_SUITE_CHANGE_CLASSES = {"fixture"}

GOVERNANCE_DOCS_LITE_CHANGE_CLASS = "docs_governance"

GOVERNANCE_LITE_ALLOWED_SUITE_PATH = "not_applicable"

GOVERNANCE_LITE_REQUIRED_RELEASE_JUDGMENT = "no_release"

GOVERNANCE_INTENSITY_NON_SKIPPABLE_GATES = [
    "fact_chain",
    "current_head_review",
    "pr_metadata_readback",
    "hosted_checks",
    "pr_gate",
    "release_judgment",
    "controlled_merge",
    "post_merge_closeout",
]

REVIEW_DECISIONS = {"allow", "block", "fallback"}

REVIEW_KINDS = {"general_review", "code_review", "spec_review"}

IMPLEMENTATION_REVIEW_KINDS = {"general_review", "code_review"}

REVIEW_FINDING_SEVERITIES = {"warn", "block"}

REVIEW_FINDING_DISPOSITION_STATUSES = {"accepted", "rejected", "deferred"}

SEMANTIC_REVIEW_DISPOSITION_STATUSES = {"required", "passed", "not_applicable", "waived"}

SEMANTIC_REVIEW_NOT_APPLICABLE_REQUIRED_FIELDS = (
    "reason",
    "change_class",
    "non_behavioral_scope",
    "substitute_validation",
    "authority",
)

SEMANTIC_REVIEW_WAIVED_REQUIRED_FIELDS = (
    "reason",
    "change_class",
    "substitute_validation",
    "authority",
    "risk_acceptance",
)

CONTROLLED_MERGE_CONSUMPTION_SCHEMA = "loom-controlled-merge-consumption/v1"

POST_MERGE_REVIEW_DIAGNOSTIC_SCHEMA = "loom-post-merge-review-diagnostic/v1"

PR_MERGE_GATE_SCHEMA = "loom-pr-merge-gate/v1"

HOSTED_DELIVERY_GATE_READBACK_SCHEMA = "loom-delivery-gate-readback/v1"

CONTROLLED_MERGE_SCHEMA = "loom-controlled-merge/v1"

GOVERNANCE_CAPABILITY_PROFILE_SCHEMA = "loom-governance-capability-profile/v1"

HIGH_RISK_GOVERNANCE_CHANGE_CLASSES = {"release", "security", "payment", "data_migration", "data-migration"}

GATE_REPAIR_PR_SCHEMA = "loom-gate-repair-pr/v1"

PR_MERGE_GATE_CHECK_NAME = "loom-delivery-gate"

HOST_MERGEABILITY_HARD_BLOCK_STATUSES = {"DIRTY", "DRAFT"}

HOST_MERGEABILITY_DELEGATED_STATUSES = {"BLOCKED"}

TRIGGERED_CHECK_ALLOWED_CONCLUSIONS = {"SUCCESS", "SKIPPED", "NEUTRAL"}

TRIGGERED_CHECK_BLOCKING_CONCLUSIONS = {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}

TRIGGERED_CHECK_PENDING_STATUSES = {"QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED", "PENDING"}

MERGE_GATE_RESULT_SCHEMAS = {"loom-flow-merge-ready/v1", "loom-merge-gate/v1"}

SHADOW_PARITY_SURFACES = ("admission", "review", "merge_ready", "closeout")

ISSUE_DEPENDENCY_MACHINE_BLOCK_MARKER = "loom:issue-dependencies"

ISSUE_DEPENDENCY_MACHINE_BLOCK_SCHEMA = "loom-issue-dependencies/v1"

SPEC_REVIEW_SUITE_READY_RESULTS = {"pass", "advisory", "not_applicable"}

SUITE_PATH_DECISION_FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?suite path(?: consumed)?\s*:\s*([A-Za-z_][A-Za-z_-]*)\b",
    re.IGNORECASE,
)

SUITE_PATH_DECISION_PLAN_LOCATOR_RE = re.compile(
    r"^\s*(?:[-*]\s*)?plan locator\s*:\s*not_applicable\s*\([^)]*\bsuite path(?: consumed)?\s*:\s*([A-Za-z_][A-Za-z_-]*)\b[^)]*\)\s*$",
    re.IGNORECASE,
)

NO_ACTIVE_ITEM_ID = "no_active_item"

IDLE_FACT_CHAIN_ERROR = "repository is idle; no active Work Item is selected"

GATE_REPAIR_PR_LOCATOR = ".loom/companion/gate-repair-pr.json"

SUITE_RECONCILIATION_FINDINGS = {
    "stale_evidence": {
        "kind": "suite_stale_evidence",
        "recommended_action": "refresh suite evidence and rerun suite evidence validation before closeout reconciliation.",
    },
    "head_or_pr_drift": {
        "kind": "suite_head_or_pr_drift",
        "recommended_action": "return to review, merge-ready, or merge gate until suite evidence is bound to the current head and PR.",
    },
    "host_state_conflict": {
        "kind": "suite_host_state_conflict",
        "recommended_action": "reconcile host issue, PR, Project, checks, branch, or merge state before closeout.",
    },
    "carrier_truth_conflict": {
        "kind": "suite_host_state_conflict",
        "recommended_action": "reconcile host carrier mirrors and keep carrier truth tracking-only before closeout.",
    },
}

def init_result_locator_matches(actual: object, expected: str) -> bool:
    if actual == expected:
        return True
    return expected == COMPANION_INIT_RESULT and actual == DEFAULT_INIT_RESULT

def dedupe_strings(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped

def runtime_state_block_payload(
    *,
    command: str,
    runtime_state: dict[str, Any],
    summary: str,
    operation: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "command": command,
        "result": "block",
        "summary": summary,
        "missing_inputs": list(runtime_state.get("missing_inputs", [])),
        "fallback_to": runtime_state.get("fallback_to"),
        "runtime_state": runtime_state,
    }
    if operation is not None:
        payload["operation"] = operation
    return payload

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def repo_relative_path(target_root: Path, relative: str) -> Path | None:
    candidate, errors = resolve_repo_relative_path(target_root, relative, label="repo locator")
    return None if errors else candidate

def path_boundary_details_from_messages(errors: list[str]) -> list[dict[str, object]]:
    details: list[dict[str, object]] = []
    for message in errors:
        if "must stay" not in message and "repo-relative" not in message and "non-empty repo-relative" not in message:
            continue
        label = message.split(" must ", 1)[0] if " must " in message else "repo locator"
        locator = message.rsplit(": ", 1)[-1] if ": " in message else ""
        details.extend(path_boundary_missing_details(label=label, locator=locator, errors=[message]))
    return details

def validate_shadow_sources(payload: dict[str, Any], *, path: Path, target_root: Path) -> tuple[dict[str, Any], list[str]]:
    source_files = payload.get("source_files")
    source_sha256 = payload.get("source_sha256")
    errors: list[str] = []
    if not isinstance(source_files, list) or not source_files:
        errors.append(f"shadow evidence `{path}` must declare non-empty `source_files`")
        source_files = []
    if not isinstance(source_sha256, dict) or not source_sha256:
        errors.append(f"shadow evidence `{path}` must declare non-empty `source_sha256`")
        source_sha256 = {}

    normalized_sources: list[str] = []
    for index, source in enumerate(source_files, start=1):
        if not isinstance(source, str) or not source.strip():
            errors.append(f"shadow evidence `{path}` source_files[{index}] must be a non-empty relative path")
            continue
        source = source.strip()
        if Path(source).is_absolute() or ".." in Path(source).parts:
            errors.append(f"shadow evidence `{path}` source `{source}` must stay inside the repository")
            continue
        source_path = repo_relative_path(target_root, source)
        if source_path is None:
            errors.append(f"shadow evidence `{path}` source `{source}` must stay inside the repository")
            continue
        if not source_path.exists() or source_path.is_dir():
            errors.append(f"shadow evidence `{path}` source `{source}` must be an existing file")
            continue
        normalized_sources.append(source)

    source_keys = set(normalized_sources)
    hash_keys = {key for key in source_sha256.keys() if isinstance(key, str)}
    if source_keys != hash_keys:
        errors.append(f"shadow evidence `{path}` source_files and source_sha256 keys must match exactly")
    for source in sorted(source_keys & hash_keys):
        expected = source_sha256.get(source)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            errors.append(f"shadow evidence `{path}` source `{source}` must declare a 64-character sha256")
            continue
        actual = sha256_file(target_root / source)
        if actual.lower() != expected.lower():
            errors.append(f"shadow evidence `{path}` source `{source}` sha256 drifted")

    return {
        "source_files": normalized_sources,
        "source_sha256": {source: source_sha256.get(source) for source in normalized_sources if isinstance(source_sha256.get(source), str)},
    }, errors

def declared_shadow_locators(interop_payload: dict[str, Any]) -> set[str]:
    shadow_surfaces = interop_payload.get("shadow_surfaces")
    declared: set[str] = set()
    if not isinstance(shadow_surfaces, dict):
        return declared
    for entry in shadow_surfaces.values():
        if not isinstance(entry, dict):
            continue
        for key in ("loom_locator", "repo_locator"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                declared.add(value.strip())
    return declared

def undeclared_shadow_evidence_errors(target_root: Path, interop_payload: dict[str, Any]) -> list[str]:
    shadow_root = target_root / ".loom/shadow"
    if not shadow_root.exists():
        return []
    declared = declared_shadow_locators(interop_payload)
    errors: list[str] = []
    for path in sorted(shadow_root.glob("*.json")):
        relative = relative_to_root(path, target_root)
        if relative == ".loom/shadow/shadow-parity.json":
            continue
        if relative not in declared:
            errors.append(f"shadow evidence `{relative}` is not declared in repo interop shadow_surfaces")
    return errors

def normalized_shadow_value(path: Path, *, target_root: Path) -> tuple[dict[str, Any], str | None]:
    try:
        if path.is_dir():
            return {"normalized_value": None}, f"shadow parity locator points to a directory: {path}"
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"normalized_value": None}, f"cannot read shadow parity locator `{path}`: {exc.strerror or exc}"
    if not raw_text.strip():
        return {"normalized_value": None}, f"shadow parity locator is empty: {path}"

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        source_evidence, source_errors = validate_shadow_sources(payload, path=path, target_root=target_root)
        for key in ("parity_value", "result", "decision", "status", "verdict", "value"):
            value = payload.get(key)
            if isinstance(value, (str, int, float, bool)) and str(value).strip():
                comparable: object = str(value).strip().lower()
                semantic_evidence = {
                    semantic_key: payload[semantic_key]
                    for semantic_key in ("source_semantics", "evidence_body")
                    if semantic_key in payload
                }
                if semantic_evidence:
                    comparable = {
                        "value": comparable,
                        **semantic_evidence,
                    }
                normalized = (
                    comparable
                    if isinstance(comparable, str)
                    else json.dumps(comparable, ensure_ascii=False, sort_keys=True)
                )
                return {**source_evidence, "normalized_value": normalized}, "; ".join(source_errors) if source_errors else None
        return {**source_evidence, "normalized_value": json.dumps(payload, ensure_ascii=False, sort_keys=True)}, "; ".join(source_errors) if source_errors else None
    if isinstance(payload, list):
        return {"normalized_value": json.dumps(payload, ensure_ascii=False, sort_keys=True)}, f"shadow evidence `{path}` must be a JSON object with source_files/source_sha256"
    if isinstance(payload, (str, int, float, bool)) and str(payload).strip():
        return {"normalized_value": str(payload).strip().lower()}, f"shadow evidence `{path}` must be a JSON object with source_files/source_sha256"

    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return {"normalized_value": stripped.lower()}, f"shadow evidence `{path}` must be a JSON object with source_files/source_sha256"
    return {"normalized_value": None}, f"shadow parity locator does not expose a comparable value: {path}"

def shadow_parity_report(
    repo_interop: object,
    *,
    target_root: Path,
    surface: str,
) -> dict[str, Any]:
    empty_report = {
        "surface": surface,
        "result": "unreadable",
        "classification": "gate_failure",
        "blocking": False,
        "summary": "shadow parity could not be evaluated for this surface.",
        "missing_inputs": [],
        "recommended_action": "restore the declared Loom and repo-native shadow parity locators before treating this surface as authoritative.",
        "host_adapters": [],
        "repo_native_carriers": [],
        "loom_surface": {
            "status": "missing",
            "locator": "unknown",
            "normalized_value": None,
        },
        "repo_surface": {
            "status": "missing",
            "locator": "unknown",
            "normalized_value": None,
        },
    }
    interop_payload, interop_errors = load_repo_interop_contract(repo_interop, target_root=target_root)
    if interop_errors:
        missing_details = path_boundary_details_from_messages(interop_errors)
        payload = {
            **empty_report,
            "summary": "shadow parity is unavailable because the repo interop contract is missing or incomplete.",
            "missing_inputs": interop_errors,
        }
        if missing_details:
            payload["missing_details"] = missing_details
        return {
            **payload,
        }
    if not isinstance(interop_payload, dict):
        return empty_report

    host_adapters = interop_payload.get("host_adapters")
    repo_native_carriers = interop_payload.get("repo_native_carriers")
    shadow_surfaces = interop_payload.get("shadow_surfaces")
    if not isinstance(host_adapters, list) or not isinstance(repo_native_carriers, list) or not isinstance(shadow_surfaces, dict):
        return {
            **empty_report,
            "summary": "shadow parity is unavailable because the repo interop contract cannot be consumed safely.",
            "missing_inputs": ["repo interop contract"],
        }

    relevant_host_adapters = [
        entry for entry in host_adapters if isinstance(entry, dict) and surface in entry.get("surfaces", [])
    ]
    relevant_repo_native_carriers = [
        entry for entry in repo_native_carriers if isinstance(entry, dict) and surface in entry.get("surfaces", [])
    ]
    declared_surface = shadow_surfaces.get(surface)
    if not isinstance(declared_surface, dict):
        return {
            **empty_report,
            "summary": "shadow parity is unavailable because this surface is not declared in the repo interop contract.",
            "missing_inputs": [f"shadow surface missing: {surface}"],
            "host_adapters": relevant_host_adapters,
            "repo_native_carriers": relevant_repo_native_carriers,
        }

    loom_locator = declared_surface.get("loom_locator")
    repo_locator = declared_surface.get("repo_locator")
    loom_path, loom_locator_errors = resolve_repo_relative_path(
        target_root,
        str(loom_locator),
        label=f"shadow surface `{surface}` loom_locator",
    )
    repo_path, repo_locator_errors = resolve_repo_relative_path(
        target_root,
        str(repo_locator),
        label=f"shadow surface `{surface}` repo_locator",
    )
    if loom_locator_errors or repo_locator_errors:
        missing_details = [
            *path_boundary_missing_details(
                label=f"shadow surface `{surface}` loom_locator",
                locator=loom_locator,
                errors=loom_locator_errors,
            ),
            *path_boundary_missing_details(
                label=f"shadow surface `{surface}` repo_locator",
                locator=repo_locator,
                errors=repo_locator_errors,
            ),
        ]
        return {
            **empty_report,
            "summary": "shadow parity is unavailable because a declared surface locator is unsafe.",
            "missing_inputs": [*loom_locator_errors, *repo_locator_errors],
            "missing_details": missing_details,
            "host_adapters": relevant_host_adapters,
            "repo_native_carriers": relevant_repo_native_carriers,
        }
    assert loom_path is not None
    assert repo_path is not None

    loom_surface = {
        "status": "missing",
        "locator": str(loom_locator),
        "normalized_value": None,
    }
    repo_surface = {
        "status": "missing",
        "locator": str(repo_locator),
        "normalized_value": None,
    }

    global_errors = undeclared_shadow_evidence_errors(target_root, interop_payload)
    loom_evidence, loom_error = normalized_shadow_value(loom_path, target_root=target_root)
    repo_evidence, repo_error = normalized_shadow_value(repo_path, target_root=target_root)
    loom_value = loom_evidence.get("normalized_value")
    repo_value = repo_evidence.get("normalized_value")

    missing_inputs: list[str] = []
    missing_inputs.extend(global_errors)
    if loom_error:
        missing_inputs.append(loom_error)
    if repo_error:
        missing_inputs.append(repo_error)

    loom_surface = {
        **loom_evidence,
        "status": "readable" if loom_error is None else "missing",
        "locator": str(loom_locator),
    }
    repo_surface = {
        **repo_evidence,
        "status": "readable" if repo_error is None else "missing",
        "locator": str(repo_locator),
    }

    if global_errors or loom_error or repo_error or loom_value is None or repo_value is None:
        return {
            **empty_report,
            "summary": "shadow parity is unreadable because one or both declared surfaces cannot be normalized.",
            "missing_inputs": missing_inputs,
            "host_adapters": relevant_host_adapters,
            "repo_native_carriers": relevant_repo_native_carriers,
            "loom_surface": loom_surface,
            "repo_surface": repo_surface,
        }
    if loom_value == repo_value:
        return {
            "surface": surface,
            "result": "match",
            "classification": None,
            "blocking": False,
            "summary": "Loom and repo-native surfaces report the same normalized result.",
            "missing_inputs": [],
            "recommended_action": "no shadow parity action required.",
            "host_adapters": relevant_host_adapters,
            "repo_native_carriers": relevant_repo_native_carriers,
            "loom_surface": loom_surface,
            "repo_surface": repo_surface,
        }
    return {
        "surface": surface,
        "result": "mismatch",
        "classification": "drift",
        "blocking": False,
        "summary": "Loom and repo-native surfaces disagree on the normalized result.",
        "missing_inputs": [],
        "recommended_action": "resolve the parity mismatch or explicitly choose the authoritative surface outside repo interop before enabling blocking consumption.",
        "host_adapters": relevant_host_adapters,
        "repo_native_carriers": relevant_repo_native_carriers,
        "loom_surface": loom_surface,
        "repo_surface": repo_surface,
    }

def normalize_checkpoint(raw: str) -> str:
    lowered = raw.strip().lower()
    if "commit checkpoint" in lowered or "admission checkpoint" in lowered:
        return "admission"
    if "build checkpoint" in lowered:
        return "build"
    if lowered in {"review", "review checkpoint", "reviewed", "reviewed checkpoint"}:
        return "merge"
    if "merge checkpoint" in lowered or lowered in {"merge gate", "merge-gate", "merge_gate"}:
        return "merge"
    if lowered in {"closed", "done", "closeout", "closed_out", "closed-out", "closed out", "closed checkpoint", "done checkpoint"}:
        return "closed_out"
    if "retired" in lowered:
        return "retired"
    return lowered.replace(" checkpoint", "").strip()

def checkpoint_rank(name: str) -> int:
    ranks = {
        "admission": 1,
        "build": 2,
        "merge": 3,
        "retired": 99,
    }
    return ranks.get(name, -1)

def suite_validation_command_payload(
    context: dict[str, Any],
    *,
    domain: str,
) -> dict[str, Any]:
    target_root = context["target_root"]
    item_id = context["item_id"]
    command_label = f"suite {domain} validate"
    display_command = f"loom {command_label} --target {target_root} --item {item_id} --json"
    if domain not in {"evidence", "carrier"}:
        return {
            "result": "block",
            "summary": f"unsupported suite validation domain `{domain}`.",
            "missing_inputs": [f"unsupported suite validation domain: {domain}"],
            "fallback_to": "build",
            "command": display_command,
            "payload": None,
        }

    errors: list[str] = []
    for invocation in suite_validate_cli_invocations(context):
        command = [
            *invocation["argv"],
            "suite",
            domain,
            "validate",
            "--target",
            str(target_root),
            "--item",
            item_id,
            "--json",
        ]
        completed = run_process(command, invocation["cwd"], timeout_seconds=60)
        raw_output = completed.stdout.strip()
        try:
            payload = json.loads(raw_output) if raw_output else {}
        except json.JSONDecodeError as exc:
            errors.append(f"{invocation['label']}: {command_label} emitted non-JSON output: {exc.msg}")
            continue
        if not isinstance(payload, dict) or payload.get("command") != command_label:
            detail = completed.stderr.strip() or raw_output or f"exit {completed.returncode}"
            errors.append(f"{invocation['label']}: {detail}")
            continue

        result = payload.get("result") if payload.get("result") in {"pass", "block", "fallback"} else "block"
        missing_inputs = list(payload.get("missing_inputs", [])) if isinstance(payload.get("missing_inputs"), list) else []
        for gap in payload.get("blocking_gaps", []) if isinstance(payload.get("blocking_gaps"), list) else []:
            if not isinstance(gap, dict):
                continue
            failure_kind = gap.get("failure_kind")
            source_locator = gap.get("source_locator")
            if failure_kind:
                detail = str(failure_kind)
                if source_locator:
                    detail = f"{detail}: {source_locator}"
                if detail not in missing_inputs:
                    missing_inputs.append(detail)
        fallback_to = payload.get("fallback_to")
        if isinstance(fallback_to, list):
            fallback_to = fallback_to[0] if fallback_to else None
        if not isinstance(fallback_to, str) or not fallback_to:
            fallback_to = None if result == "pass" else command_label
        return {
            "result": result,
            "summary": str(payload.get("summary") or f"{command_label} completed."),
            "missing_inputs": missing_inputs,
            "fallback_to": fallback_to,
            "command": " ".join(command),
            "validator": str(invocation["label"]),
            "validator_mode": str(invocation["mode"]),
            "returncode": completed.returncode,
            "payload": payload,
        }

    missing_inputs = [f"{command_label} CLI JSON unavailable"]
    missing_inputs.extend(f"suite validator unavailable: {error}" for error in errors)
    return {
        "result": "block",
        "summary": f"{command_label} must be consumed from Loom CLI JSON before this gate can pass.",
        "missing_inputs": missing_inputs,
        "fallback_to": command_label,
        "command": display_command,
        "validator": None,
        "validator_mode": "cli-json-unavailable",
        "payload": None,
    }

def suite_gate_validation_payload(context: dict[str, Any], *, surface: str) -> dict[str, Any]:
    evidence = suite_validation_command_payload(context, domain="evidence")
    carrier = suite_validation_command_payload(context, domain="carrier")
    validations = {
        "evidence": evidence,
        "carrier": carrier,
    }
    missing_inputs: list[str] = []
    result = "pass"
    fallback_to: str | None = None
    for name, validation in validations.items():
        validation_result = validation["result"]
        if validation_result == "fallback" and result == "pass":
            result = "fallback"
            fallback_to = validation.get("fallback_to") or f"suite {name} validate"
        elif validation_result == "block":
            if result == "pass":
                result = "block"
                fallback_to = validation.get("fallback_to") or f"suite {name} validate"
        if validation_result in {"block", "fallback"}:
            for message in validation.get("missing_inputs", []):
                detail = f"{name}: {message}"
                if detail not in missing_inputs:
                    missing_inputs.append(detail)
    evidence_payload = evidence.get("payload") if isinstance(evidence.get("payload"), dict) else {}
    evidence_suite_payload = evidence_payload.get("payload") if isinstance(evidence_payload.get("payload"), dict) else {}
    carrier_payload = carrier.get("payload") if isinstance(carrier.get("payload"), dict) else {}
    carrier_suite_payload = carrier_payload.get("payload") if isinstance(carrier_payload.get("payload"), dict) else {}
    task_carriers = carrier_suite_payload.get("task_carrier_locators")
    if not isinstance(task_carriers, list):
        task_carrier_locator = carrier_suite_payload.get("task_carrier_locator")
        task_carriers = [task_carrier_locator] if isinstance(task_carrier_locator, str) and task_carrier_locator else []
    return {
        "schema_version": "loom-suite-gate-validation/v1",
        "surface": surface,
        "result": result,
        "summary": (
            "suite evidence and carrier validation passed for this gate surface."
            if result == "pass"
            else "suite evidence or carrier validation found blocking gate inputs."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to,
        "authority_boundary": {
            "role": "gate_input_evidence",
            "does_not_replace": [
                "work_item",
                "review_record",
                "merge_ready_result",
                "closeout_evidence",
                "docs_source_truth",
            ],
        },
        "consumed_locators": {
            "evidence_map": evidence_suite_payload.get("evidence_map_locator"),
            "consistency_analysis": evidence_suite_payload.get("consistency_analysis_locator"),
            "task_carriers": task_carriers,
        },
        "validations": validations,
    }

def suite_gate_consumed_inputs(suite_gate_validation: dict[str, Any]) -> dict[str, Any]:
    validations = suite_gate_validation.get("validations") if isinstance(suite_gate_validation.get("validations"), dict) else {}
    evidence = validations.get("evidence") if isinstance(validations.get("evidence"), dict) else {}
    carrier = validations.get("carrier") if isinstance(validations.get("carrier"), dict) else {}
    evidence_payload = evidence.get("payload") if isinstance(evidence.get("payload"), dict) else {}
    evidence_suite_payload = evidence_payload.get("payload") if isinstance(evidence_payload.get("payload"), dict) else {}
    carrier_payload = carrier.get("payload") if isinstance(carrier.get("payload"), dict) else {}
    carrier_suite_payload = carrier_payload.get("payload") if isinstance(carrier_payload.get("payload"), dict) else {}
    consumed_locators = (
        suite_gate_validation.get("consumed_locators")
        if isinstance(suite_gate_validation.get("consumed_locators"), dict)
        else {}
    )
    task_carriers = consumed_locators.get("task_carriers")
    if not isinstance(task_carriers, list):
        task_carriers = []
    evidence_contracts = evidence_suite_payload.get("consumed_contracts")
    if not isinstance(evidence_contracts, list):
        evidence_contracts = []
    carrier_contracts = carrier_suite_payload.get("consumed_contracts")
    if not isinstance(carrier_contracts, list):
        carrier_contracts = []
    return {
        "suite_evidence_validation": evidence.get("command"),
        "suite_carrier_validation": carrier.get("command"),
        "suite_evidence_map": consumed_locators.get("evidence_map"),
        "suite_consistency_analysis": consumed_locators.get("consistency_analysis"),
        "suite_task_carriers": task_carriers,
        "suite_evidence_consumed_contracts": evidence_contracts,
        "suite_carrier_consumed_contracts": carrier_contracts,
    }

def suite_gate_step(name: str, suite_gate: dict[str, Any], domain: str) -> dict[str, Any]:
    validation = suite_gate.get("validations", {}).get(domain) if isinstance(suite_gate.get("validations"), dict) else None
    if not isinstance(validation, dict):
        return {
            "name": name,
            "result": "block",
            "summary": f"{name} validation payload is missing.",
            "missing_inputs": [name],
            "fallback_to": "build",
        }
    return {
        "name": name,
        "result": validation["result"],
        "summary": validation["summary"],
        "missing_inputs": validation["missing_inputs"],
        "fallback_to": validation["fallback_to"],
        "validation": validation.get("payload"),
        "command": validation.get("command"),
    }

def has_make_target(makefile_path: Path, target: str) -> bool:
    if not makefile_path.exists():
        return False
    try:
        text = makefile_path.read_text(encoding="utf-8")
    except OSError:
        return False
    target_pattern = re.compile(rf"^(?:[^\s:#=]+(?:\s+[^\s:#=]+)*\s+)?{re.escape(target)}\s*:(?:\s|$)", re.MULTILINE)
    return bool(target_pattern.search(text))

def closeout_gate_command(target_root: Path) -> tuple[list[str], str]:
    if has_make_target(target_root / "Makefile", "loom-check"):
        return ["make", "loom-check"], "repo_declared_make_target"
    repo_gate = target_root / ".loom/bin/loom_check.py"
    if repo_gate.exists():
        return ["python3", ".loom/bin/loom_check.py", "."], "repo_local_loom_check"
    return ["python3", str(shared_script(str(FLOW_ENTRYPOINT), "loom_check.py")), str(target_root)], "shared_loom_check"

def effective_closeout_gate_profile(profile: str | None) -> str:
    return CLOSEOUT_LIGHT_PROFILE if profile in {None, "auto"} else profile

def closeout_subcheck(
    *,
    check_id: str,
    source: str,
    profile: str,
    required_for_closeout: bool,
    trigger_reason: str,
    result: str,
    fallback_to: str | None = None,
    evidence_locator: str | None = None,
    missing_inputs: list[str] | None = None,
    **evidence: Any,
) -> dict[str, Any]:
    payload = {
        "id": check_id,
        "source": source,
        "profile": profile,
        "required_for_closeout": required_for_closeout,
        "trigger_reason": trigger_reason,
        "result": result,
        "fallback_to": fallback_to,
        "missing_inputs": missing_inputs or [],
    }
    if evidence_locator is not None:
        payload["evidence_locator"] = evidence_locator
    for key, value in evidence.items():
        if value is not None:
            payload[key] = value
    return payload

def closeout_suite_gate_subchecks(
    suite_gate_validation: dict[str, Any],
    *,
    profile: str,
) -> list[dict[str, Any]]:
    subchecks: list[dict[str, Any]] = []
    suite_required = suite_gate_validation.get("result") != "not_applicable"
    validations = (
        suite_gate_validation.get("validations")
        if isinstance(suite_gate_validation.get("validations"), dict)
        else {}
    )
    consumed_locators = (
        suite_gate_validation.get("consumed_locators")
        if isinstance(suite_gate_validation.get("consumed_locators"), dict)
        else {}
    )
    for domain in ("evidence", "carrier"):
        validation = validations.get(domain) if isinstance(validations.get(domain), dict) else None
        missing_inputs: list[str] = []
        result = "block"
        fallback_to = f"suite {domain} validate"
        command = None
        validator = None
        validator_mode = None
        summary = f"suite {domain} validation payload is missing."
        if validation is None:
            missing_inputs.append(f"suite {domain} validation")
        else:
            validation_result = validation.get("result")
            result = "pass" if validation_result in {"pass", "not_applicable"} else "block"
            fallback_value = validation.get("fallback_to")
            fallback_to = None if result == "pass" else (fallback_value if isinstance(fallback_value, str) and fallback_value else fallback_to)
            summary = str(validation.get("summary") or summary)
            raw_missing = validation.get("missing_inputs")
            if result == "pass":
                missing_inputs = []
            elif isinstance(raw_missing, list):
                missing_inputs.extend(str(message) for message in raw_missing)
            else:
                missing_inputs.append(f"suite {domain} validation did not pass")
            command = validation.get("command")
            validator = validation.get("validator")
            validator_mode = validation.get("validator_mode")
        subchecks.append(
            closeout_subcheck(
                check_id=f"suite_{domain}_validation",
                source="suite_gate",
                profile=profile,
                required_for_closeout=suite_required,
                trigger_reason=(
                    f"closeout consumes suite {domain} validation as retained evidence "
                    "instead of treating merged PR state as completion truth"
                ),
                result=result,
                fallback_to=fallback_to,
                evidence_locator=command if isinstance(command, str) and command else None,
                missing_inputs=missing_inputs,
                summary=summary,
                suite_surface=suite_gate_validation.get("surface"),
                consumed_locators=consumed_locators,
                validator=validator,
                validator_mode=validator_mode,
            )
        )
    return subchecks

def git_changed_paths(root: Path, base: str, head: str) -> tuple[list[str], list[str]]:
    result = run_git(root, ["diff", "--name-only", "--no-renames", f"{base}..{head}"])
    if result is None:
        return [], ["git is unavailable while comparing reviewed HEAD to current HEAD"]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git diff failed"
        return [], [detail]
    paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return paths, []

def git_merge_base(root: Path, base_ref: str, head_ref: str = "HEAD") -> str | None:
    result = run_git(root, ["merge-base", base_ref, head_ref])
    if result is None or result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None

def git_remote_origin(root: Path) -> str | None:
    result = run_git(root, ["remote", "get-url", "origin"])
    if result is None or result.returncode != 0:
        return None
    remote = result.stdout.strip()
    return remote or None

def detect_github_repo(root: Path) -> tuple[str | None, str | None]:
    remote = git_remote_origin(root)
    if not remote:
        return None, None
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", remote)
    if not match:
        return None, None
    return match.group("owner"), match.group("repo")

def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def issue_dependency_html_comment_blocks(body: str) -> list[str]:
    pattern = re.compile(
        rf"<!--\s*{re.escape(ISSUE_DEPENDENCY_MACHINE_BLOCK_MARKER)}\s*(.*?)\s*-->",
        flags=re.DOTALL,
    )
    return [match.group(1).strip() for match in pattern.finditer(body)]

def normalize_issue_reference(value: Any) -> int | None:
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str):
        match = re.fullmatch(r"\s*#?(\d+)\s*", value)
        if match:
            return int(match.group(1))
    if isinstance(value, dict):
        number = value.get("number")
        if isinstance(number, int) and number > 0:
            return number
    return None

def normalize_issue_reference_list(value: Any) -> list[int]:
    values = value if isinstance(value, list) else [value]
    normalized: list[int] = []
    for entry in values:
        issue_number = normalize_issue_reference(entry)
        if issue_number is not None:
            normalized.append(issue_number)
    return normalized

def issue_dependency_machine_block_payloads(issue_body: str) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for raw in issue_dependency_html_comment_blocks(issue_body):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        schema_version = payload.get("schema_version")
        if schema_version not in (None, ISSUE_DEPENDENCY_MACHINE_BLOCK_SCHEMA):
            continue
        payloads.append(payload)
    return payloads

def parse_authored_dependency_edges(issue_body: Any, issue_number: int | None) -> list[dict[str, Any]]:
    if not isinstance(issue_body, str) or issue_number is None:
        return []
    edges: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str]] = set()
    for block_index, payload in enumerate(issue_dependency_machine_block_payloads(issue_body), start=1):
        dependency_payload = payload.get("dependencies") if isinstance(payload.get("dependencies"), dict) else payload
        relation_values: list[tuple[str, int]] = []
        for relation, field_names in (
            ("blocked_by", ("blocked_by", "blockedBy", "depends_on", "dependsOn")),
            ("blocking", ("blocks", "blocking")),
        ):
            for field_name in field_names:
                if field_name not in dependency_payload:
                    continue
                for other in normalize_issue_reference_list(dependency_payload.get(field_name)):
                    relation_values.append((relation, other))
                break
        raw_edges = dependency_payload.get("edges")
        if isinstance(raw_edges, list):
            for raw_edge in raw_edges:
                if not isinstance(raw_edge, dict):
                    continue
                direction = raw_edge.get("direction")
                if direction == "blocked_by":
                    other = normalize_issue_reference(
                        raw_edge.get("blocking_issue", raw_edge.get("issue", raw_edge.get("number")))
                    )
                elif direction == "blocking":
                    other = normalize_issue_reference(
                        raw_edge.get("source_issue", raw_edge.get("issue", raw_edge.get("number")))
                    )
                else:
                    continue
                if other is not None:
                    relation_values.append((direction, other))
        for relation, other in relation_values:
            source = issue_number if relation == "blocked_by" else other
            blocker = other if relation == "blocked_by" else issue_number
            key = (source, blocker, relation)
            if key in seen or source == blocker:
                continue
            seen.add(key)
            edges.append(
                {
                    "source_issue": source,
                    "blocking_issue": blocker,
                    "direction": relation,
                    "blocker_state": "unknown",
                    "source_of_truth": "issue_body_machine_block",
                    "host_mirror_status": "requires_native_compare",
                    "native": "unknown",
                    "provenance": {
                        "source_layer": "authored_truth",
                        "source_owner": "github_issue_machine_block",
                        "source_locator": (
                            f"issue #{issue_number} {ISSUE_DEPENDENCY_MACHINE_BLOCK_MARKER} block {block_index}"
                        ),
                        "freshness": "fresh",
                    },
                }
            )
    return edges

def dependency_edge_key(edge: dict[str, Any]) -> tuple[int | None, int | None]:
    source = edge.get("source_issue")
    blocker = edge.get("blocking_issue")
    return (source if isinstance(source, int) else None, blocker if isinstance(blocker, int) else None)

def dependency_graph_payload(
    *,
    issue_number: int | None,
    issue_payload: dict[str, Any] | None,
    native_dependency_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    authored_edges = parse_authored_dependency_edges(issue_payload.get("body") if isinstance(issue_payload, dict) else None, issue_number)
    native_edges = (
        list(native_dependency_payload.get("native_edges", []))
        if isinstance(native_dependency_payload, dict)
        else []
    )
    native_by_key = {dependency_edge_key(edge): edge for edge in native_edges}
    authored_by_key = {dependency_edge_key(edge): edge for edge in authored_edges}
    findings: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    availability = (
        native_dependency_payload.get("availability")
        if isinstance(native_dependency_payload, dict)
        else "not_requested"
    )
    for edge in authored_edges:
        key = dependency_edge_key(edge)
        native = native_by_key.get(key)
        merged = dict(edge)
        if native is None:
            merged["host_mirror_status"] = "missing_native_edge" if availability == "present" else availability
            merged["native"] = "missing" if availability == "present" else availability
            findings.append(
                {
                    "category": "drift",
                    "kind": "missing_native_edge",
                    "severity": "fix-needed" if availability == "present" else "warn",
                    "subject": f"dependency edge {key[0]} blocked by {key[1]}",
                    "evidence": {"edge": merged, "native_availability": availability},
                    "fallback_to": "manual-reconciliation",
                }
            )
        else:
            merged = {**native, "source_of_truth": edge.get("source_of_truth"), "host_mirror_status": "matched"}
        edges.append(merged)

    for edge in native_edges:
        key = dependency_edge_key(edge)
        if key not in authored_by_key:
            stale_closed_blocker = edge.get("direction") == "blocked_by" and edge.get("blocker_state") == "closed"
            drift_kind = "stale_native_edge" if stale_closed_blocker else "unexpected_native_edge"
            unexpected = {**edge, "host_mirror_status": drift_kind}
            edges.append(unexpected)
            findings.append(
                {
                    "category": "drift",
                    "kind": drift_kind,
                    "severity": "fix-needed",
                    "subject": f"dependency edge {key[0]} blocked by {key[1]}",
                    "evidence": {"edge": unexpected},
                    "fallback_to": "reconciliation-sync" if stale_closed_blocker else "manual-reconciliation",
                }
            )
        if edge.get("direction") == "blocked_by" and edge.get("blocker_state") == "open":
            findings.append(
                {
                    "category": "gate_failure",
                    "kind": "open_blocker_executable_conflict",
                    "severity": "block",
                    "subject": f"issue #{issue_number} blocked by #{edge.get('blocking_issue')}",
                    "evidence": {"edge": edge},
                    "fallback_to": "manual-reconciliation",
                }
            )
    if availability in {"unsupported", "permission_denied", "unreadable"}:
        findings.append(
            {
                "category": "drift",
                "kind": "native_dependency_unreadable",
                "severity": "warn",
                "subject": f"issue #{issue_number} dependency graph",
                "evidence": {"availability": availability},
                "fallback_to": "manual-reconciliation",
            }
        )
    return {
        "schema_version": HOST_DEPENDENCY_GRAPH_SCHEMA,
        "source_issue": {
            "number": issue_number,
            "state": issue_payload.get("state") if isinstance(issue_payload, dict) else None,
        },
        "availability": availability,
        "capability": native_dependency_payload.get("capability") if isinstance(native_dependency_payload, dict) else None,
        "edges": edges,
        "native_edges": native_edges,
        "authored_edges": authored_edges,
        "findings": findings,
        "checks": native_dependency_payload.get("checks", []) if isinstance(native_dependency_payload, dict) else [],
    }

def git_dirty_entries(root: Path) -> list[dict[str, str]]:
    result = run_git(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    if result is None or result.returncode != 0:
        return []

    entries: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        remainder = line[3:]
        path_text = remainder.split(" -> ", 1)[-1].strip()
        if not path_text:
            continue
        entries.append({"status": status, "path": path_text})
    return entries

def git_tracked_files(root: Path, relative: str) -> list[str]:
    result = run_git(root, ["ls-files", "--", relative])
    if result is None or result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]

def relative_to_root(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))

def resolve_artifact_write_path(target_root: Path, locator: str, *, label: str) -> tuple[Path | None, list[str]]:
    logical_path, errors = resolve_repo_relative_path(target_root, locator, label=label)
    if errors:
        return None, errors
    assert logical_path is not None
    if is_global_runtime_locator(locator):
        try:
            return global_runtime_path(target_root, locator), []
        except ValueError as exc:
            return None, [str(exc)]
    return logical_path, []

def resolve_artifact_read_path(target_root: Path, locator: str, *, label: str) -> tuple[Path | None, list[str]]:
    logical_path, errors = resolve_repo_relative_path(target_root, locator, label=label)
    if errors:
        return None, errors
    assert logical_path is not None
    if not is_global_runtime_locator(locator):
        return logical_path, []
    try:
        runtime_path = global_runtime_path(target_root, locator)
    except ValueError as exc:
        return None, [str(exc)]
    if runtime_path.exists() or not logical_path.exists():
        return runtime_path, []
    return logical_path, []

def resolve_workspace_path(target_root: Path, workspace_entry: str) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    if not workspace_entry.strip():
        return None, ["missing workspace entry locator"]
    raw = Path(workspace_entry)
    if raw.is_absolute():
        resolved = raw.resolve()
    else:
        resolved = (target_root / raw).resolve()
    try:
        resolved.relative_to(target_root.resolve())
    except ValueError:
        return None, [f"workspace entry escapes target root: {workspace_entry}"]
    return resolved, errors

def current_cwd_relative(target_root: Path) -> str | None:
    cwd = Path.cwd().resolve()
    try:
        return str(cwd.relative_to(target_root.resolve()))
    except ValueError:
        return None

def default_review_path(item_id: str) -> str:
    return f".loom/reviews/{item_id}.json"

def default_spec_review_path(item_id: str) -> str:
    return f".loom/reviews/{item_id}.spec.json"

def shadow_evidence_paths_for_sources(target_root: Path, source_paths: set[str]) -> set[str]:
    shadow_root = target_root / ".loom/shadow"
    if not shadow_root.exists():
        return set()

    evidence_paths: set[str] = set()
    for evidence_path in sorted(shadow_root.glob("*.json")):
        relative = relative_to_root(evidence_path, target_root)
        if relative == ".loom/shadow/shadow-parity.json":
            continue
        try:
            payload = load_json_file(evidence_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        source_files = payload.get("source_files")
        if not isinstance(source_files, list):
            continue
        if any(isinstance(source, str) and source in source_paths for source in source_files):
            evidence_paths.add(relative)
    return evidence_paths

def allowed_post_review_carrier_paths(context: dict[str, Any], *review_paths: str) -> set[str]:
    item_id = context.get("item_id")
    spec_review_path = f".loom/reviews/{item_id}.spec.json" if isinstance(item_id, str) and item_id.strip() else None
    report = context.get("report")
    fact_chain = report.get("fact_chain") if isinstance(report, dict) else None
    fact_chain_entry_points = fact_chain.get("entry_points") if isinstance(fact_chain, dict) else None
    source_paths = {str(path) for path in review_paths if isinstance(path, str) and path.strip()}
    if isinstance(fact_chain_entry_points, dict):
        for key in ("work_item", "recovery_entry", "status_surface"):
            locator = fact_chain_entry_points.get(key)
            if isinstance(locator, str) and locator.strip():
                source_paths.add(locator)
    if spec_review_path:
        source_paths.add(spec_review_path)
    allowed = {
        *source_paths,
    }
    allowed.update(shadow_evidence_paths_for_sources(context["target_root"], source_paths))
    review_shadow_root = context["target_root"] / ".loom/shadow"
    if review_shadow_root.exists():
        for evidence_path in sorted(review_shadow_root.glob("review-*.json")):
            try:
                payload = load_json_file(evidence_path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict):
                allowed.add(relative_to_root(evidence_path, context["target_root"]))
    if isinstance(item_id, str) and item_id.strip():
        for runtime_root in OWNED_RUNTIME_EVIDENCE_ROOTS:
            item_runtime_root = context["target_root"] / runtime_root / item_id
            if item_runtime_root.exists():
                for evidence_path in sorted(path for path in item_runtime_root.rglob("*") if path.is_file()):
                    allowed.add(relative_to_root(evidence_path, context["target_root"]))
    return allowed

def allowed_terminal_closeout_carrier_paths(context: dict[str, Any], *review_paths: str) -> set[str]:
    allowed = allowed_post_review_carrier_paths(context, *review_paths)
    item_id = context.get("item_id")
    if isinstance(item_id, str) and item_id.strip():
        allowed.update(
            {
                f".loom/specs/{item_id}/task-carrier.md",
                f".loom/work-items/{item_id}.md",
            }
        )
    return allowed

def formal_spec_path(context: dict[str, Any]) -> str | None:
    preferred = f".loom/specs/{context['item_id']}/spec.md"
    if (context["target_root"] / preferred).exists():
        return preferred

    for artifact in context.get("associated_artifacts", []):
        if (
            isinstance(artifact, str)
            and artifact == preferred
            and (context["target_root"] / artifact).exists()
        ):
            return artifact

    fallback = context["target_root"] / ".loom/specs/INIT-0001/spec.md"
    if context["item_id"] == "INIT-0001" and fallback.exists():
        return ".loom/specs/INIT-0001/spec.md"
    return None

def formal_spec_suite_status(context: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    suite = spec_suite_paths(context)
    missing = [
        path
        for path in (suite["spec"], suite["plan"], suite["implementation_contract"])
        if not (context["target_root"] / path).is_file()
    ]
    return suite, missing

def spec_suite_paths(context: dict[str, Any]) -> dict[str, str]:
    item_id = context["item_id"]
    candidates = [
        {
            "spec": f".loom/specs/{item_id}/spec.md",
            "plan": f".loom/specs/{item_id}/plan.md",
            "implementation_contract": f".loom/specs/{item_id}/implementation-contract.md",
        },
    ]
    if item_id == "INIT-0001":
        candidates.append(
            {
                "spec": ".loom/specs/INIT-0001/spec.md",
                "plan": ".loom/specs/INIT-0001/plan.md",
                "implementation_contract": ".loom/specs/INIT-0001/implementation-contract.md",
            }
        )
    for suite in candidates:
        if (context["target_root"] / suite["spec"]).exists():
            return suite
    return candidates[0]

def suite_validate_command_candidates(context: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    roots: list[Path | None] = [context["target_root"]]
    if os.environ.get("LOOM_SOURCE_REPO_ROOT"):
        roots.append(Path(os.environ["LOOM_SOURCE_REPO_ROOT"]).expanduser().resolve())
    for parent in context["target_root"].parents:
        roots.append(parent)
    for root in roots:
        if not isinstance(root, Path):
            continue
        command = root / "tools" / "loom.py"
        contract = root / "docs" / "methodology" / "harness" / "full-spec-suite-cli-surface.md"
        if command.is_file() and contract.is_file() and command not in candidates:
            candidates.append(command)
    return candidates

def suite_validate_cli_invocations(context: dict[str, Any]) -> list[dict[str, Any]]:
    invocations: list[dict[str, Any]] = []
    for command in suite_validate_command_candidates(context):
        invocations.append(
            {
                "label": str(command),
                "mode": "repo-local-cli",
                "argv": [sys.executable, str(command)],
                "cwd": command.parents[1],
            }
        )
    if shutil.which("loom"):
        invocations.append(
            {
                "label": "loom",
                "mode": "global-cli",
                "argv": ["loom"],
                "cwd": context["target_root"],
            }
        )
    return invocations

def suite_path_decision_value_from_line(line: str) -> str:
    for pattern in (SUITE_PATH_DECISION_FIELD_RE, SUITE_PATH_DECISION_PLAN_LOCATOR_RE):
        match = pattern.search(line)
        if match:
            return match.group(1).lower().replace("-", "_")
    return ""

def suite_path_decision_presence_from_paths(context: dict[str, Any], candidates: list[str | None]) -> tuple[bool, set[str]]:
    marker_present = False
    values: set[str] = set()
    for relative in candidates:
        if not isinstance(relative, str) or not relative.strip() or relative == "not_applicable":
            continue
        path = context["target_root"] / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            marker_present = True
            continue
        for line in text.splitlines():
            value = suite_path_decision_value_from_line(line)
            if not value:
                continue
            marker_present = True
            values.add(value)
    return marker_present, values

def suite_path_decision_presence(context: dict[str, Any]) -> tuple[bool, set[str]]:
    suite = spec_suite_paths(context)
    return suite_path_decision_presence_from_paths(
        context,
        [
            suite["spec"],
            suite["plan"],
        ],
    )

def adoption_suite_path_decision_presence(context: dict[str, Any]) -> tuple[bool, set[str]]:
    marker_present, values = suite_path_decision_presence(context)
    if marker_present:
        return marker_present, values
    entry_points = context.get("report", {}).get("fact_chain", {}).get("entry_points", {})
    if not isinstance(entry_points, dict):
        return False, set()
    return suite_path_decision_presence_from_paths(
        context,
        [
            entry_points.get("recovery_entry"),
            entry_points.get("status_surface"),
        ],
    )

def suite_gate_required_for_surface(context: dict[str, Any], *, surface: str) -> bool:
    if surface == "pre_review" and checkpoint_rank(context["current_checkpoint"]) < checkpoint_rank("build"):
        return False
    marker_present, values = suite_path_decision_presence(context)
    if not marker_present:
        return False
    if values and values <= {"not_applicable"}:
        return False
    return True

def suite_gate_not_applicable_payload(context: dict[str, Any], *, surface: str) -> dict[str, Any]:
    summary = "suite evidence and carrier validation are not applicable for this gate surface."
    validation = {
        "result": "not_applicable",
        "summary": summary,
        "missing_inputs": [],
        "fallback_to": None,
        "command": "not_applicable",
        "validator": None,
        "validator_mode": "checkpoint-not-applicable",
        "payload": None,
    }
    return {
        "schema_version": "loom-suite-gate-validation/v1",
        "surface": surface,
        "result": "not_applicable",
        "summary": summary,
        "missing_inputs": [],
        "fallback_to": None,
        "authority_boundary": {
            "role": "gate_input_evidence",
            "does_not_replace": [
                "work_item",
                "review_record",
                "merge_ready_result",
                "closeout_evidence",
                "docs_source_truth",
            ],
        },
        "consumed_locators": {
            "evidence_map": None,
            "task_carriers": [],
        },
        "validations": {
            "evidence": dict(validation),
            "carrier": dict(validation),
        },
    }

def suite_gate_unreadable_payload(errors: list[str], *, surface: str) -> dict[str, Any]:
    missing_inputs = [f"fact-chain: {message}" for message in errors]
    summary = "suite evidence and carrier validation context is unreadable for this gate surface."
    validation = {
        "result": "block",
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": "fact-chain",
        "command": "not_applicable",
        "validator": None,
        "validator_mode": "fact-chain-unreadable",
        "payload": None,
    }
    return {
        "schema_version": "loom-suite-gate-validation/v1",
        "surface": surface,
        "result": "block",
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": "fact-chain",
        "authority_boundary": {
            "role": "gate_input_evidence",
            "does_not_replace": [
                "work_item",
                "review_record",
                "merge_ready_result",
                "closeout_evidence",
                "docs_source_truth",
            ],
        },
        "consumed_locators": {
            "evidence_map": None,
            "task_carriers": [],
        },
        "validations": {
            "evidence": dict(validation),
            "carrier": dict(validation),
        },
    }

def suite_gate_payload_for_surface(context: dict[str, Any], *, surface: str) -> dict[str, Any]:
    if suite_gate_required_for_surface(context, surface=surface):
        return suite_gate_validation_payload(context, surface=surface)
    return suite_gate_not_applicable_payload(context, surface=surface)

def governance_metadata_fields_from_preflight(pr_metadata_preflight: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(pr_metadata_preflight, dict):
        return {}
    carrier = pr_metadata_preflight.get("governance_intensity_carrier")
    if not isinstance(carrier, dict):
        return {}
    envelope = carrier.get("envelope")
    if not isinstance(envelope, dict):
        return {}
    fields = envelope.get("fields")
    return fields if isinstance(fields, dict) else {}

def governance_metadata_declares_host_readback_only(pr_metadata_preflight: dict[str, Any] | None) -> bool:
    if not isinstance(pr_metadata_preflight, dict) or pr_metadata_preflight.get("result") != "pass":
        return False
    fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
    return (
        fields.get("fact_chain_required") is False
        and fields.get("review_requirement") == GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT
        and fields.get("pr_gate_required") is True
    )

def governance_metadata_declares_suite_not_applicable(pr_metadata_preflight: dict[str, Any] | None) -> bool:
    fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
    if fields.get("suite_path") != "not_applicable":
        return False
    suite_not_applicable = fields.get("suite_not_applicable")
    if not isinstance(suite_not_applicable, dict):
        return False
    required_fields = ("rationale", "consumer_boundary", "recheck_condition", "scope_proof", "review_requirement")
    return all(isinstance(suite_not_applicable.get(field), str) and suite_not_applicable.get(field, "").strip() for field in required_fields)

def metadata_suite_not_applicable_payload(
    context: dict[str, Any],
    pr_metadata_preflight: dict[str, Any] | None,
    *,
    surface: str,
) -> dict[str, Any] | None:
    if not governance_metadata_declares_suite_not_applicable(pr_metadata_preflight):
        return None
    fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
    payload = suite_gate_not_applicable_payload(context, surface=surface)
    payload["summary"] = "suite evidence and carrier validation are not applicable because PR metadata declares a complete suite_not_applicable decision."
    payload["source_locator"] = "pr_metadata.governance_intensity_carrier.fields.suite_not_applicable"
    payload["payload"] = {
        "suite_path": "not_applicable",
        "path_decision_locator": "pr_metadata.governance_intensity_carrier.fields.suite_not_applicable",
        "not_applicable_rationale": fields.get("suite_not_applicable"),
        "authority_boundary": "PR metadata may declare formal suite non-applicability; review, PR gate, closeout, release judgment, and host checks remain required.",
    }
    return payload

def governance_intensity_authority_boundary() -> dict[str, Any]:
    return {
        "role": "classification_and_formal_suite_boundary",
        "does_not_replace": list(GOVERNANCE_INTENSITY_NON_SKIPPABLE_GATES),
    }

def governance_intensity_gate_payload(context: dict[str, Any], pr_metadata_preflight: dict[str, Any] | None) -> dict[str, Any]:
    fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
    missing_inputs: list[str] = []
    upgrade_reasons: list[str] = []
    if context and isinstance(context.get("target_root"), Path):
        marker_present, suite_values = suite_path_decision_presence(context)
    else:
        marker_present, suite_values = False, set()
    metadata_suite_not_applicable = governance_metadata_declares_suite_not_applicable(pr_metadata_preflight)
    authority_boundary = governance_intensity_authority_boundary()

    if not fields:
        return {
            "schema_version": "loom-governance-intensity-gate/v1",
            "result": "not_applicable",
            "summary": "governance intensity gate is not applicable because no governance intensity metadata carrier was declared for this PR.",
            "missing_inputs": [],
            "fallback_to": None,
            "metadata_fields": {},
            "declared_governance_intensity": None,
            "effective_governance_intensity": None,
            "effective_suite_path": None,
            "upgrade_reasons": [],
            "non_skippable_gates": list(GOVERNANCE_INTENSITY_NON_SKIPPABLE_GATES),
            "consumed_locators": {
                "metadata_carrier": False,
                "suite_path_decision": marker_present,
            },
            "suite_path_decision": {
                "marker_present": marker_present,
                "values": sorted(suite_values),
            },
            "authority_boundary": authority_boundary,
        }

    declared_intensity = fields.get("governance_intensity")
    change_class = fields.get("change_class")
    suite_path = fields.get("suite_path")
    host_readback_only = governance_metadata_declares_host_readback_only(pr_metadata_preflight)
    non_skippable_gates = list(GOVERNANCE_INTENSITY_NON_SKIPPABLE_GATES)
    if host_readback_only:
        non_skippable_gates = [
            gate
            for gate in non_skippable_gates
            if gate not in {"fact_chain", "current_head_review"}
        ]
        authority_boundary = {
            **authority_boundary,
            "does_not_replace": non_skippable_gates,
            "repo_local_inputs_removed_by_profile": ["fact_chain", "current_head_review"],
        }

    if fields.get("governance_intensity") == "light":
        if change_class in GOVERNANCE_HIGH_RISK_CHANGE_CLASSES:
            upgrade_reasons.append(f"change_class_requires_upgrade:{change_class}")
            missing_inputs.append(f"light governance requires standard or reinforced intensity for change_class {change_class}")
        elif change_class not in GOVERNANCE_LITE_ALLOWED_CHANGE_CLASSES:
            upgrade_reasons.append(f"change_class_not_light_eligible:{change_class}")
            missing_inputs.append(f"light governance does not support change_class {change_class}")

        if change_class in GOVERNANCE_LITE_NOT_APPLICABLE_CHANGE_CLASSES:
            if suite_path != "not_applicable":
                missing_inputs.append(f"light governance requires suite_path not_applicable for change_class {change_class}")
        elif change_class in GOVERNANCE_LITE_MINIMAL_SUITE_CHANGE_CLASSES:
            if suite_path != "minimal":
                missing_inputs.append(f"light governance requires suite_path minimal for change_class {change_class}")

        if fields.get("review_requirement") != "current_head_review_required":
            missing_inputs.append("light governance requires current-head review")
        if fields.get("release_judgment") != GOVERNANCE_LITE_REQUIRED_RELEASE_JUDGMENT:
            missing_inputs.append("light governance requires no_release judgment")
        for required_bool in ("fact_chain_required", "pr_gate_required", "closeout_required"):
            if fields.get(required_bool) is not True:
                missing_inputs.append(f"light governance requires {required_bool}")
    if fields.get("suite_path") == "not_applicable":
        if marker_present and suite_values != {"not_applicable"}:
            missing_inputs.append("repo suite path decision does not match metadata suite_path not_applicable")
        elif not marker_present and not metadata_suite_not_applicable:
            missing_inputs.append("repo suite path decision is missing")

    if missing_inputs:
        result = "block"
        summary = "governance intensity metadata or suite decision is incomplete, mismatched, or requires an intensity upgrade."
    elif declared_intensity in GOVERNANCE_INTENSITY_VALUES:
        result = "pass"
        summary = (
            "governance intensity metadata declares host-readback-only review; repo fact-chain and current-head review carriers are outside this gate boundary."
            if host_readback_only
            else "governance intensity metadata and suite decision are aligned; non-skippable gates remain required."
        )
    else:
        result = "not_applicable"
        summary = "governance intensity gate is not applicable for this governance metadata."

    effective_intensity = declared_intensity
    if declared_intensity == "light" and upgrade_reasons:
        effective_intensity = "standard"

    return {
        "schema_version": "loom-governance-intensity-gate/v1",
        "result": result,
        "summary": summary,
        "missing_inputs": dedupe_strings(missing_inputs),
        "fallback_to": None if result in {"pass", "not_applicable"} else "update_pr_body",
        "metadata_fields": fields,
        "declared_governance_intensity": declared_intensity,
        "effective_governance_intensity": effective_intensity,
        "effective_suite_path": suite_path if suite_path in GOVERNANCE_SUITE_PATH_VALUES else None,
        "upgrade_reasons": dedupe_strings(upgrade_reasons),
        "non_skippable_gates": non_skippable_gates,
        "consumed_locators": {
            "metadata_carrier": True,
            "suite_path_decision": marker_present,
            "metadata_suite_not_applicable": metadata_suite_not_applicable,
        },
        "suite_path_decision": {
            "marker_present": marker_present or metadata_suite_not_applicable,
            "values": sorted(suite_values or ({"not_applicable"} if metadata_suite_not_applicable else set())),
            "source": "repo_suite_marker" if marker_present else "pr_metadata" if metadata_suite_not_applicable else "missing",
        },
        "authority_boundary": authority_boundary,
    }

def docs_governance_lite_gate_payload(context: dict[str, Any], pr_metadata_preflight: dict[str, Any] | None) -> dict[str, Any]:
    fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
    if context and isinstance(context.get("target_root"), Path):
        marker_present, suite_values = suite_path_decision_presence(context)
    else:
        marker_present, suite_values = False, set()
    if not fields or fields.get("governance_intensity") != "light" or fields.get("change_class") != GOVERNANCE_DOCS_LITE_CHANGE_CLASS:
        return {
            "schema_version": "loom-docs-governance-lite-gate/v1",
            "result": "not_applicable",
            "summary": "docs-governance lite gate is not applicable for this governance metadata.",
            "missing_inputs": [],
            "fallback_to": None,
            "metadata_fields": fields,
            "suite_path_decision": {
                "marker_present": marker_present,
                "values": sorted(suite_values),
            },
            "authority_boundary": governance_intensity_authority_boundary(),
        }

    general_gate = governance_intensity_gate_payload(context, pr_metadata_preflight)
    result = general_gate.get("result")
    missing_inputs = [str(message).replace("light governance", "docs-governance lite") for message in general_gate.get("missing_inputs", [])]
    if result == "pass":
        summary = "docs-governance lite metadata and suite not_applicable decision are aligned; non-suite gates remain required."
    else:
        summary = "docs-governance lite metadata or suite decision is incomplete or mismatched."
    return {
        "schema_version": "loom-docs-governance-lite-gate/v1",
        "result": result,
        "summary": summary,
        "missing_inputs": dedupe_strings(missing_inputs),
        "fallback_to": None if result in {"pass", "not_applicable"} else "update_pr_body",
        "metadata_fields": fields,
        "suite_path_decision": general_gate.get("suite_path_decision"),
        "authority_boundary": general_gate.get("authority_boundary"),
    }

def spec_review_gate_ready_for_implementation_review(spec_gate: dict[str, Any]) -> bool:
    return spec_gate.get("result") in SPEC_REVIEW_SUITE_READY_RESULTS

def normalize_suite_validate_payload(payload: dict[str, Any], *, validator: str, mode: str) -> dict[str, Any]:
    normalized = dict(payload)
    nested_payload = normalized.get("payload")
    if isinstance(nested_payload, dict):
        normalized.setdefault("blocking_gaps", nested_payload.get("blocking_gaps", []))
        normalized.setdefault("advisory_gaps", nested_payload.get("advisory_gaps", []))
        normalized.setdefault("failure_taxonomy", nested_payload.get("failure_taxonomy", []))
        normalized.setdefault("supported_failure_kinds", nested_payload.get("supported_failure_kinds", []))
    normalized["validator"] = validator
    normalized["validator_mode"] = mode
    return normalized

def suite_validation_missing_inputs(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for entry in payload.get("missing_inputs", []):
        text = str(entry)
        if text not in missing:
            missing.append(text)
    for gap in payload.get("blocking_gaps", []):
        if not isinstance(gap, dict):
            continue
        failure_kind = str(gap.get("failure_kind") or "suite_validation_gap")
        locator = str(gap.get("source_locator") or "")
        remediation = str(gap.get("remediation_direction") or "")
        parts = [f"suite validation {failure_kind}"]
        if locator:
            parts.append(locator)
        if remediation:
            parts.append(remediation)
        text = ": ".join(parts)
        if text not in missing:
            missing.append(text)
    return missing

def suite_validation_fallback_to(payload: dict[str, Any]) -> str | None:
    fallback = payload.get("fallback_to")
    if isinstance(fallback, list):
        return str(fallback[0]) if fallback else "build"
    if isinstance(fallback, str) and fallback:
        return fallback
    return "build"

def suite_validation_ready(payload: dict[str, Any]) -> bool:
    return payload.get("result") in SPEC_REVIEW_SUITE_READY_RESULTS

def active_suite_not_applicable_validation_payload(context: dict[str, Any]) -> dict[str, Any] | None:
    marker_present, values = adoption_suite_path_decision_presence(context)
    if not marker_present or values != {"not_applicable"}:
        return None
    entry_points = context.get("report", {}).get("fact_chain", {}).get("entry_points", {})
    path_decision_locator = None
    if isinstance(entry_points, dict):
        for relative in (entry_points.get("recovery_entry"), entry_points.get("status_surface")):
            if not isinstance(relative, str) or not relative.strip() or relative == "not_applicable":
                continue
            present, path_values = suite_path_decision_presence_from_paths(context, [relative])
            if present and path_values == {"not_applicable"}:
                path_decision_locator = relative
                break
    return {
        "schema_version": "loom-suite-validation-consumption/v1",
        "command": "suite validate",
        "result": "not_applicable",
        "generated_at": current_iso_timestamp(),
        "target": str(context["target_root"]),
        "item_id": context["item_id"],
        "summary": "Suite validate consumed an active not_applicable suite path decision from the Loom fact chain.",
        "mutates": False,
        "validator": None,
        "validator_mode": "active-fact-chain-marker",
        "missing_inputs": [],
        "blocking_gaps": [],
        "advisory_gaps": [],
        "fallback_to": None,
        "payload": {
            "suite_path": "not_applicable",
            "suite_locator": path_decision_locator,
            "path_decision_locator": path_decision_locator,
            "path_decisions": [
                {
                    "value": "not_applicable",
                    "locator": path_decision_locator,
                    "source": "active_fact_chain",
                }
            ],
            "not_applicable_rationale": [
                "Active Loom fact chain declares the formal suite path as not_applicable for this low-friction host batch."
            ],
            "deferred_items": [],
            "missing_inputs": [],
            "advisory_gaps": [],
        },
    }

def spec_suite_validation_payload(context: dict[str, Any]) -> dict[str, Any]:
    active_not_applicable = active_suite_not_applicable_validation_payload(context)
    if active_not_applicable is not None:
        return active_not_applicable

    errors: list[str] = []
    for invocation in suite_validate_cli_invocations(context):
        try:
            completed = run_process(
                [
                    *invocation["argv"],
                    "suite",
                    "validate",
                    "--target",
                    str(context["target_root"]),
                    "--item",
                    str(context["item_id"]),
                    "--json",
                ],
                cwd=invocation["cwd"],
                timeout_seconds=30.0,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            errors.append(f"{invocation['label']}: {exc}")
            continue
        stdout = completed.stdout.strip()
        try:
            payload = json.loads(stdout) if stdout else {}
        except json.JSONDecodeError:
            errors.append(f"{invocation['label']}: emitted non-JSON suite validate output")
            continue
        if isinstance(payload, dict) and payload.get("command") == "suite validate":
            return normalize_suite_validate_payload(
                payload,
                validator=str(invocation["label"]),
                mode=str(invocation["mode"]),
            )
        detail = completed.stderr.strip() or stdout or f"exit {completed.returncode}"
        errors.append(f"{invocation['label']}: {detail}")

    missing_inputs = ["suite validate CLI JSON unavailable"]
    missing_inputs.extend(f"suite validator unavailable: {error}" for error in errors)
    return {
        "schema_version": "loom-suite-validation-consumption/v1",
        "command": "suite validate",
        "result": "block",
        "summary": "suite validation must be consumed from Loom CLI JSON; embedded skill runtime does not reimplement suite rules.",
        "target": str(context["target_root"]),
        "item_id": context["item_id"],
        "mutates": False,
        "validator": None,
        "validator_mode": "cli-json-unavailable",
        "missing_inputs": missing_inputs,
        "blocking_gaps": [
            {
                "id": "suite-validate-cli-json-unavailable",
                "classification": "missing",
                "failure_kind": "suite_cli_json_unavailable",
                "default_result": "block",
                "failed_layer": "suite",
                "source_locator": "tools/loom.py",
                "consumer_impact": "scenario skills cannot decide suite readiness without the canonical CLI JSON envelope",
                "remediation_direction": "Run the global `loom suite validate --target <repo> --item <item> --json` surface.",
                "fallback_to": "loom suite validate --target <repo> --item <item> --json",
                "binding": "scenario-skill-suite-cli-consumption",
            }
        ],
        "advisory_gaps": [],
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    }

def review_head_binding(
    target_root: Path,
    *,
    reviewed_head: str | None,
    allowed_paths: set[str],
    current_head: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    target_head = current_head or git_head_sha(target_root)
    return review_head_binding_for_head(
        target_root,
        reviewed_head=reviewed_head,
        target_head=target_head,
        allowed_paths=allowed_paths,
    )

def review_head_binding_for_head(
    target_root: Path,
    *,
    reviewed_head: str | None,
    target_head: str | None,
    allowed_paths: set[str],
) -> tuple[dict[str, Any], list[str]]:
    payload: dict[str, Any] = {
        "reviewed_head": reviewed_head,
        "current_head": target_head,
        "status": "unknown",
        "stale": None,
        "changed_paths": [],
        "disallowed_paths": [],
    }
    if not isinstance(reviewed_head, str) or not reviewed_head.strip():
        return payload, ["review artifact is missing reviewed_head"]
    if not isinstance(target_head, str) or not target_head.strip():
        return payload, ["target HEAD is unavailable"]
    if reviewed_head == target_head:
        payload["status"] = "fresh"
        payload["stale"] = False
        return payload, []

    changed_paths, head_errors = git_changed_paths(target_root, reviewed_head, target_head)
    if head_errors:
        return payload, [f"review HEAD comparison failed: {detail}" for detail in head_errors]

    payload["changed_paths"] = changed_paths
    carrier_paths = [path for path in changed_paths if path in allowed_paths]
    non_carrier_paths = [path for path in changed_paths if path not in allowed_paths]
    generated_paths = [path for path in non_carrier_paths if review_generated_only_path_metadata(path) is not None]
    semantic_paths = [path for path in non_carrier_paths if path not in generated_paths]
    payload["carrier_only_paths"] = carrier_paths
    payload["generated_only_paths"] = generated_paths
    payload["generated_only_validation_actions"] = generated_only_validation_actions(generated_paths)
    payload["semantic_drift_paths"] = semantic_paths
    payload["disallowed_paths"] = semantic_paths
    if changed_paths and not non_carrier_paths:
        payload["status"] = "carrier-only"
        payload["stale"] = False
        return payload, []

    if generated_paths and not semantic_paths:
        payload["status"] = "carrier-and-generated-only" if carrier_paths else "generated-only"
        payload["stale"] = False
        return payload, []

    if semantic_paths and len(semantic_paths) == len(changed_paths):
        payload["status"] = "implementation-drift-only"
        payload["stale"] = True
        return payload, ["review artifact has implementation drift after review"]

    payload["status"] = "stale"
    payload["stale"] = True
    if not changed_paths:
        return payload, ["review artifact was recorded against a different HEAD"]
    return payload, ["review artifact is stale for the target HEAD"]

def review_generated_only_path_metadata(path: str) -> dict[str, str] | None:
    if path == ".loom/bootstrap/init-result.json":
        return {
            "kind": "bootstrap-init-result-pointer",
            "validation_action": "python3 .loom/bin/loom_init.py verify --target .",
        }
    if path.startswith(".loom/bin/") and path.endswith(".py"):
        return {
            "kind": "repo-local-runtime-copy",
            "validation_action": "PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py carrier refresh --target . --apply",
        }
    if path.startswith("skills/"):
        return {
            "kind": "generated-skills-tree",
            "validation_action": "python3 tools/skills_surface.py check",
        }
    if path.startswith("docs/evidence/fixtures/") and ("demo" in path or "new-project" in path):
        return {
            "kind": "demo-bootstrap-fixture-output",
            "validation_action": "python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift",
        }
    if path.startswith("examples/new-project/"):
        return {
            "kind": "demo-bootstrap-example-output",
            "validation_action": "python3 tools/check_demo_bootstrap_fixture.py --surface aggregate",
        }
    return None

def generated_only_validation_actions(paths: list[str]) -> list[dict[str, Any]]:
    actions: dict[str, dict[str, Any]] = {}
    for path in paths:
        metadata = review_generated_only_path_metadata(path)
        if metadata is None:
            continue
        action = metadata["validation_action"]
        entry = actions.setdefault(
            action,
            {
                "action": action,
                "kind": metadata["kind"],
                "paths": [],
            },
        )
        entry["paths"].append(path)
    return list(actions.values())

def spec_review_head_binding(
    context: dict[str, Any],
    *,
    reviewed_head: str | None,
    review_path: str,
) -> tuple[dict[str, Any], list[str]]:
    current_head = git_head_sha(context["target_root"])
    payload: dict[str, Any] = {
        "reviewed_head": reviewed_head,
        "current_head": current_head,
        "status": "unknown",
        "stale": None,
        "changed_paths": [],
        "spec_changed_paths": [],
    }
    if not isinstance(reviewed_head, str) or not reviewed_head.strip():
        return payload, ["review artifact is missing reviewed_head"]
    if not isinstance(current_head, str) or not current_head.strip():
        return payload, ["current HEAD is unavailable"]
    if reviewed_head == current_head:
        payload["status"] = "fresh"
        payload["stale"] = False
        return payload, []

    changed_paths, head_errors = git_changed_paths(context["target_root"], reviewed_head, current_head)
    if head_errors:
        return payload, [f"review HEAD comparison failed: {detail}" for detail in head_errors]

    suite = spec_suite_paths(context)
    watched_paths = {
        suite["spec"],
        suite["plan"],
        suite["implementation_contract"],
    }
    spec_changed_paths = [path for path in changed_paths if path in watched_paths]
    payload["changed_paths"] = changed_paths
    payload["spec_changed_paths"] = spec_changed_paths
    if spec_changed_paths:
        payload["status"] = "stale"
        payload["stale"] = True
        return payload, ["spec review is stale because the formal spec path changed after approval"]

    payload["status"] = "implementation-drift-only"
    payload["stale"] = False
    return payload, []

def review_gate_payload(
    context: dict[str, Any],
    *,
    review_path: str,
    expected_kind: str,
    gate_name: str,
    required: bool,
    path_label: str | None = None,
) -> dict[str, Any]:
    review_record, _, review_errors = load_review_record(
        context["target_root"],
        context["item_id"],
        review_path,
    )
    head_binding = {
        "reviewed_head": None,
        "current_head": git_head_sha(context["target_root"]),
        "status": "unknown",
        "stale": None,
        "changed_paths": [],
        "disallowed_paths": [],
    }
    missing_inputs: list[str] = []
    result = "pass" if required else "not_applicable"
    fallback_to: str | None = None

    if path_label is not None and not path_label.strip():
        missing_inputs.append(f"missing formal {gate_name.replace('_', ' ')} path")
        result = "block"
        fallback_to = "build"

    if review_errors:
        missing_inputs.extend(review_errors)
        result = "block"
        fallback_to = "build"
    elif review_record is None:
        if required:
            missing_inputs.append(f"missing {gate_name.replace('_', ' ')} artifact: {review_path}")
            result = "block"
            fallback_to = "build"
    else:
        if review_record.get("kind") != expected_kind:
            missing_inputs.append(
                f"{gate_name.replace('_', ' ')} artifact must declare kind `{expected_kind}`"
            )
            result = "block"
            fallback_to = "build"
        decision = review_record.get("decision")
        if decision == "allow":
            if expected_kind == "spec_review":
                binding_payload, binding_errors = spec_review_head_binding(
                    context,
                    reviewed_head=review_record.get("reviewed_head"),
                    review_path=review_path,
                )
            else:
                binding_payload, binding_errors = review_head_binding(
                    context["target_root"],
                    reviewed_head=review_record.get("reviewed_head"),
                    allowed_paths=allowed_post_review_carrier_paths(context, review_path),
                )
            head_binding = binding_payload
            if binding_errors:
                missing_inputs.extend(binding_errors)
                result = "block"
                fallback_to = "build"
        elif decision == "fallback":
            missing_inputs.append(f"{gate_name.replace('_', ' ')} decision is fallback: {review_record['summary']}")
            result = "fallback"
            fallback_to = review_record.get("fallback_to") or "build"
        else:
            missing_inputs.append(f"{gate_name.replace('_', ' ')} decision is blocking: {review_record['summary']}")
            result = "block"
            fallback_to = "build"

    summary = (
        f"{gate_name.replace('_', ' ')} is not required for the current item."
        if result == "not_applicable"
        else (
            f"{gate_name.replace('_', ' ')} is approved for the current HEAD."
            if result == "pass"
            else f"{gate_name.replace('_', ' ')} is missing, stale, or not approved."
        )
    )
    return {
        "path": review_path,
        "required": required,
        **({"formal_spec_path": path_label} if path_label is not None else {}),
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to,
        "record": review_record,
        "head_binding": head_binding,
    }

def spec_review_gate_payload(context: dict[str, Any], suite_validation_override: dict[str, Any] | None = None) -> dict[str, Any]:
    suite, missing_suite_paths = formal_spec_suite_status(context)
    suite_validation = suite_validation_override or spec_suite_validation_payload(context)
    suite_not_applicable = suite_validation.get("result") == "not_applicable"
    suite_validation_payload = suite_validation.get("payload")
    suite_path = (
        str(suite_validation_payload.get("suite_path") or "").lower()
        if isinstance(suite_validation_payload, dict)
        else ""
    )
    if suite_path == "minimal" and suite_validation_ready(suite_validation):
        missing_suite_paths = [
            path for path in missing_suite_paths if path != suite["implementation_contract"]
        ]
    spec_path = suite["spec"] if not missing_suite_paths else formal_spec_path(context)
    payload = review_gate_payload(
        context,
        review_path=default_spec_review_path(context["item_id"]),
        expected_kind="spec_review",
        gate_name="spec_review",
        required=not missing_suite_paths and not suite_not_applicable,
        path_label=spec_path,
    )
    payload["formal_spec_suite"] = suite
    payload["suite_validation"] = suite_validation
    if suite_not_applicable:
        payload["result"] = "not_applicable"
        payload["summary"] = "spec review is not applicable because suite validation consumed a formal suite not_applicable path decision."
        payload["missing_inputs"] = []
        payload["fallback_to"] = None
    elif missing_suite_paths:
        payload["result"] = "block"
        payload["summary"] = "spec review is blocked until the complete formal spec suite is present."
        payload["missing_inputs"] = [
            f"missing formal spec suite file: {path}" for path in missing_suite_paths
        ] + list(payload.get("missing_inputs", []))
        payload["fallback_to"] = "build"
    elif not suite_validation_ready(suite_validation):
        payload["result"] = "block"
        payload["summary"] = "spec review is blocked until suite validation passes."
        payload["missing_inputs"] = suite_validation_missing_inputs(suite_validation) + list(payload.get("missing_inputs", []))
        payload["fallback_to"] = suite_validation_fallback_to(suite_validation)
    return payload

def compat_findings_from_lists(
    *,
    decision: str | None,
    blocking_issues: list[str],
    follow_ups: list[str],
) -> list[dict[str, Any]]:
    del decision
    findings: list[dict[str, Any]] = []
    for index, summary in enumerate(blocking_issues, start=1):
        findings.append(
            {
                "id": f"compat-block-{index}",
                "summary": summary,
                "severity": "block",
                "rebuttal": None,
                "disposition": {
                    "status": "rejected",
                    "summary": "Projected from compatibility `blocking_issues`.",
                },
            }
        )
    for index, summary in enumerate(follow_ups, start=1):
        findings.append(
            {
                "id": f"compat-follow-up-{index}",
                "summary": summary,
                "severity": "warn",
                "rebuttal": None,
                "disposition": {
                    "status": "deferred",
                    "summary": "Projected from compatibility `follow_ups`.",
                },
            }
        )
    return findings

def compat_lists_from_findings(findings: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    blocking_issues: list[str] = []
    follow_ups: list[str] = []
    for finding in findings:
        summary = finding.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            continue
        if finding.get("severity") == "block":
            blocking_issues.append(summary.strip())
        elif finding.get("severity") == "warn":
            follow_ups.append(summary.strip())
    return blocking_issues, follow_ups

def normalize_review_findings(raw_findings: Any, *, relative: str) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(raw_findings, list):
        return [], [f"review artifact `{relative}` `findings` must be a list"]

    findings: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, finding in enumerate(raw_findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"review artifact `{relative}` findings[{index}] must be a JSON object")
            continue
        normalized = dict(finding)
        finding_id = normalized.get("id")
        summary = normalized.get("summary")
        severity = normalized.get("severity")
        rebuttal = normalized.get("rebuttal")
        disposition = normalized.get("disposition")
        if not isinstance(finding_id, str) or not finding_id.strip():
            errors.append(f"review artifact `{relative}` findings[{index}] must include non-empty `id`")
        else:
            normalized["id"] = finding_id.strip()
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"review artifact `{relative}` findings[{index}] must include non-empty `summary`")
        else:
            normalized["summary"] = summary.strip()
        if severity not in REVIEW_FINDING_SEVERITIES:
            errors.append(
                f"review artifact `{relative}` findings[{index}] severity must be one of "
                f"{', '.join(sorted(REVIEW_FINDING_SEVERITIES))}"
            )
        if rebuttal is not None:
            if not isinstance(rebuttal, str) or not rebuttal.strip():
                errors.append(f"review artifact `{relative}` findings[{index}] `rebuttal` must be null or a non-empty string")
            else:
                normalized["rebuttal"] = rebuttal.strip()
        if disposition is not None:
            if not isinstance(disposition, dict):
                errors.append(f"review artifact `{relative}` findings[{index}] `disposition` must be null or an object")
            else:
                status = disposition.get("status")
                disposition_summary = disposition.get("summary")
                if status not in REVIEW_FINDING_DISPOSITION_STATUSES:
                    errors.append(
                        f"review artifact `{relative}` findings[{index}] disposition status must be one of "
                        f"{', '.join(sorted(REVIEW_FINDING_DISPOSITION_STATUSES))}"
                    )
                if not isinstance(disposition_summary, str) or not disposition_summary.strip():
                    errors.append(
                        f"review artifact `{relative}` findings[{index}] disposition must include non-empty `summary`"
                    )
                else:
                    normalized["disposition"] = {
                        **disposition,
                        "status": status,
                        "summary": disposition_summary.strip(),
                    }
        findings.append(normalized)
    return findings, errors

def load_review_record(
    target_root: Path,
    item_id: str,
    review_file: str | None = None,
) -> tuple[dict[str, Any] | None, str, list[str]]:
    relative = review_file or default_review_path(item_id)
    review_path, locator_errors = resolve_repo_relative_path(target_root, relative, label="review artifact locator")
    if locator_errors:
        return None, relative, locator_errors
    assert review_path is not None
    if not review_path.exists():
        return None, relative, []
    try:
        payload = load_json_file(review_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, relative, [f"invalid review artifact `{relative}`: {exc}"]
    if not isinstance(payload, dict):
        return None, relative, [f"review artifact `{relative}` must be a JSON object"]
    errors: list[str] = []
    if payload.get("schema_version") != "loom-review/v1":
        errors.append(f"review artifact `{relative}` schema_version must be `loom-review/v1`")
    for field in ("item_id", "decision", "kind", "summary", "reviewer", "reviewed_head", "reviewed_validation_summary"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"review artifact `{relative}` is missing `{field}`")
    if payload.get("item_id") != item_id:
        errors.append(f"review artifact `{relative}` item_id does not match `{item_id}`")
    if payload.get("decision") not in REVIEW_DECISIONS:
        errors.append(f"review artifact `{relative}` decision must be one of {', '.join(sorted(REVIEW_DECISIONS))}")
    if payload.get("kind") not in REVIEW_KINDS:
        errors.append(f"review artifact `{relative}` kind must be one of {', '.join(sorted(REVIEW_KINDS))}")
    fallback_to = payload.get("fallback_to")
    if fallback_to not in {None, "admission", "build", "merge"}:
        errors.append(f"review artifact `{relative}` fallback_to must be null, admission, build, or merge")
    compatibility_lists: dict[str, list[str]] = {}
    for list_field in ("blocking_issues", "follow_ups"):
        value = payload.get(list_field)
        if value is not None and not isinstance(value, list):
            errors.append(f"review artifact `{relative}` `{list_field}` must be a list when present")
            continue
        entries: list[str] = []
        for index, entry in enumerate(value or [], start=1):
            if not isinstance(entry, str) or not entry.strip():
                errors.append(f"review artifact `{relative}` `{list_field}`[{index}] must be a non-empty string")
                continue
            entries.append(entry.strip())
        compatibility_lists[list_field] = entries

    findings_value = payload.get("findings")
    if findings_value is None:
        findings = compat_findings_from_lists(
            decision=payload.get("decision") if isinstance(payload.get("decision"), str) else None,
            blocking_issues=compatibility_lists.get("blocking_issues", []),
            follow_ups=compatibility_lists.get("follow_ups", []),
        )
    else:
        findings, finding_errors = normalize_review_findings(findings_value, relative=relative)
        errors.extend(finding_errors)

    blocking_issues, follow_ups = compat_lists_from_findings(findings)
    normalized_payload = dict(payload)
    normalized_payload["findings"] = findings
    normalized_payload["blocking_issues"] = blocking_issues
    normalized_payload["follow_ups"] = follow_ups
    return normalized_payload, relative, errors

def check_pr_template(target_root: Path) -> tuple[dict[str, Any], list[str]]:
    path = target_root / ".github/PULL_REQUEST_TEMPLATE.md"
    if not path.exists():
        return {"exists": False, "path": ".github/PULL_REQUEST_TEMPLATE.md", "sections": {}}, ["missing PR template"]

    text = path.read_text(encoding="utf-8")
    sections = {section: (section in text) for section in PR_TEMPLATE_SECTIONS}
    missing = [f"PR template missing section: {section}" for section, present in sections.items() if not present]
    return {
        "exists": True,
        "path": ".github/PULL_REQUEST_TEMPLATE.md",
        "sections": sections,
    }, missing

def extract_github_host_context(
    target_root: Path,
    texts: list[str],
    *,
    default_owner: str | None,
    default_repo: str | None,
) -> dict[str, Any] | None:
    owner = default_owner
    repo_name = default_repo
    issue_number: int | None = None
    pr_number: int | None = None
    locators: list[str] = []

    for text in texts:
        for match in GITHUB_ISSUE_URL_RE.finditer(text):
            owner = match.group("owner")
            repo_name = match.group("repo")
            issue_number = int(match.group("number"))
            locators.append(match.group(0))
        for match in GITHUB_PR_URL_RE.finditer(text):
            owner = match.group("owner")
            repo_name = match.group("repo")
            pr_number = int(match.group("number"))
            locators.append(match.group(0))

    for text in texts:
        if issue_number is None:
            match = GITHUB_ISSUE_REF_RE.search(text)
            if match:
                issue_number = int(match.group("number"))
                locators.append(f"issue #{issue_number}")
        if pr_number is None:
            match = GITHUB_PR_REF_RE.search(text)
            if match:
                pr_number = int(match.group("number"))
                locators.append(f"PR #{pr_number}")

    if not owner or not repo_name or (issue_number is None and pr_number is None):
        return None
    return {
        "owner": owner,
        "repo": repo_name,
        "issue_number": issue_number,
        "pr_number": pr_number,
        "locators": sorted(set(locators)),
    }

def github_host_completion_truth(
    target_root: Path,
    context: dict[str, Any],
    cache: dict[tuple[str, str, int | None, int | None], dict[str, Any]],
) -> dict[str, Any]:
    owner = str(context["owner"])
    repo_name = str(context["repo"])
    issue_number = context.get("issue_number")
    pr_number = context.get("pr_number")
    cache_key = (
        owner,
        repo_name,
        int(issue_number) if isinstance(issue_number, int) else None,
        int(pr_number) if isinstance(pr_number, int) else None,
    )
    if cache_key in cache:
        return cache[cache_key]

    evidence: list[dict[str, Any]] = []
    errors: list[str] = []
    complete = False
    terminal_state: str | None = None

    if isinstance(issue_number, int):
        issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
        errors.extend(f"issue #{issue_number}: {message}" for message in issue_errors)
        if issue_payload is not None:
            state = issue_payload.get("state")
            evidence.append(
                {
                    "kind": "github_issue",
                    "number": issue_number,
                    "state": state,
                    "url": issue_payload.get("url"),
                    "closedAt": issue_payload.get("closedAt"),
                }
            )
            if state == "CLOSED":
                complete = True
                terminal_state = terminal_state or "closed_out"

    if isinstance(pr_number, int):
        pr_payload, pr_errors = github_pr_payload(target_root, owner, repo_name, pr_number)
        errors.extend(f"PR #{pr_number}: {message}" for message in pr_errors)
        if pr_payload is not None:
            state = pr_payload.get("state")
            evidence.append(
                {
                    "kind": "github_pr",
                    "number": pr_number,
                    "state": state,
                    "url": pr_payload.get("url"),
                    "mergedAt": pr_payload.get("mergedAt"),
                    "mergeCommit": pr_payload.get("mergeCommit"),
                    "baseRefName": pr_payload.get("baseRefName"),
                }
            )
            if state == "MERGED":
                complete = True
                terminal_state = "merged"

    if complete:
        status = "complete"
    elif evidence:
        status = "active"
    else:
        status = "unavailable"

    payload = {
        "status": status,
        "complete": complete,
        "terminal_state": terminal_state,
        "repository": {"owner": owner, "name": repo_name},
        "locators": context.get("locators", []),
        "evidence": evidence,
        "errors": errors,
    }
    cache[cache_key] = payload
    return payload

def carrier_closeout_sync_command(target_root: Path, other_item_id: str, host_truth: dict[str, Any]) -> str:
    issue_number: int | None = None
    pr_number: int | None = None
    merge_commit: str | None = None
    target_branch: str | None = None
    merged_at: str | None = None
    terminal_state = str(host_truth.get("terminal_state") or "closed_out")
    for entry in host_truth.get("evidence", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("kind") == "github_issue" and isinstance(entry.get("number"), int):
            issue_number = entry.get("number")
        if entry.get("kind") == "github_pr" and isinstance(entry.get("number"), int):
            pr_number = entry.get("number")
            merge_commit_entry = entry.get("mergeCommit")
            if isinstance(merge_commit_entry, dict) and isinstance(merge_commit_entry.get("oid"), str):
                merge_commit = merge_commit_entry.get("oid")
            if isinstance(entry.get("baseRefName"), str):
                target_branch = entry.get("baseRefName")
            if isinstance(entry.get("mergedAt"), str):
                merged_at = entry.get("mergedAt")
    command = [
        "python3",
        "tools/loom_flow.py",
        "carrier",
        "closeout-sync",
        "--target",
        command_target(target_root),
        "--item",
        other_item_id,
        "--terminal-state",
        terminal_state,
    ]
    if issue_number is not None:
        command.extend(["--issue", str(issue_number)])
    if pr_number is not None:
        command.extend(["--pr", str(pr_number)])
    if merge_commit:
        command.extend(["--merge-commit", merge_commit])
    if target_branch:
        command.extend(["--target-branch", target_branch])
    command.extend(["--closed-at", merged_at or "not_applicable"])
    command.extend(["--evidence-locator", ";".join(str(locator) for locator in host_truth.get("locators", [])) or "host-readback"])
    command.append("--apply")
    return shlex.join(command)

def active_workspace_diagnostics(target_root: Path, item_id: str, workspace_entry: str) -> list[dict[str, Any]]:
    work_items_dir = target_root / ".loom/work-items"
    if not work_items_dir.exists():
        return []

    diagnostics: list[dict[str, Any]] = []
    default_owner, default_repo = detect_github_repo(target_root)
    host_truth_cache: dict[tuple[str, str, int | None, int | None], dict[str, Any]] = {}
    dirty_paths = {entry["path"] for entry in git_dirty_entries(target_root)}
    for candidate in sorted(work_items_dir.glob("*.md")):
        work_item_locator = relative_to_root(candidate, target_root)
        diagnostic: dict[str, Any] = {
            "item_id": None,
            "workspace_entry": workspace_entry,
            "work_item_locator": work_item_locator,
            "binding_locator": work_item_locator,
            "checkpoint": None,
            "freshness": "unknown",
            "classification": "unknown",
            "blocking": False,
            "recommended_remediation": (
                "repair the candidate Work Item carrier through its own issue flow; it is not treated as a current workspace conflict until its workspace binding is readable."
            ),
        }
        try:
            parsed_item, errors = parse_work_item(candidate, target_root)
        except OSError:
            if candidate.stem == item_id:
                diagnostic["item_id"] = item_id
                diagnostic["blocking"] = True
                diagnostic["recommended_remediation"] = "repair the current Work Item carrier before continuing the current workspace gate."
            diagnostics.append(diagnostic)
            continue
        if errors:
            if candidate.stem == item_id:
                diagnostic["item_id"] = item_id
                diagnostic["blocking"] = True
                diagnostic["recommended_remediation"] = "repair the current Work Item carrier before continuing the current workspace gate."
            diagnostics.append(diagnostic)
            continue
        other_item_id = str(parsed_item["item_id"])
        diagnostic["item_id"] = other_item_id
        diagnostic["workspace_entry"] = str(parsed_item["workspace_entry"])
        if other_item_id == item_id:
            continue
        if str(parsed_item["workspace_entry"]) != workspace_entry:
            continue
        recovery_rel = str(parsed_item["recovery_entry"])
        diagnostic["binding_locator"] = recovery_rel
        diagnostic["blocking"] = True
        diagnostic["recommended_remediation"] = "repair this same-workspace carrier before continuing the current workspace gate."
        recovery_path, recovery_errors = resolve_repo_relative_path(
            target_root,
            recovery_rel,
            label="work item recovery entry locator",
        )
        if recovery_errors or recovery_path is None:
            diagnostic["freshness"] = "unreadable"
            diagnostics.append(diagnostic)
            continue
        if not recovery_path.exists():
            diagnostic["freshness"] = "missing"
            diagnostics.append(diagnostic)
            continue
        try:
            recovery_data, recovery_errors = parse_recovery_entry(recovery_path, target_root)
        except OSError:
            diagnostic["freshness"] = "unreadable"
            diagnostics.append(diagnostic)
            continue
        if recovery_errors:
            diagnostic["freshness"] = "unreadable"
            diagnostics.append(diagnostic)
            continue
        checkpoint = normalize_checkpoint(recovery_data["current_checkpoint"])
        diagnostic["checkpoint"] = checkpoint
        if checkpoint in TERMINAL_CHECKPOINTS:
            diagnostic["freshness"] = "terminal"
            diagnostic["classification"] = "stale_carrier"
            diagnostic["blocking"] = False
            diagnostic["recommended_remediation"] = (
                "leave this unrelated terminal carrier out of the current Work Item; audit or retire it through its own issue flow if it still appears active."
            )
        else:
            carrier_texts = [candidate.read_text(encoding="utf-8"), recovery_path.read_text(encoding="utf-8")]
            host_context = extract_github_host_context(
                target_root,
                carrier_texts,
                default_owner=default_owner,
                default_repo=default_repo,
            )
            host_truth = (
                github_host_completion_truth(target_root, host_context, host_truth_cache)
                if host_context is not None
                else None
            )
            if host_truth is not None:
                diagnostic["host_truth"] = host_truth
            if host_truth is not None and host_truth.get("complete") is True:
                diagnostic["freshness"] = "host_complete_carrier_active"
                diagnostic["classification"] = "carrier_closeout_required"
                diagnostic["blocking"] = False
                diagnostic["recommended_remediation"] = (
                    "run carrier closeout sync for this Work Item so versioned recovery/status truth consumes the completed host issue or merged PR before treating the same workspace binding as a live conflict."
                )
                diagnostic["next_command"] = carrier_closeout_sync_command(target_root, other_item_id, host_truth)
            elif (
                git_tracked_files(target_root, work_item_locator)
                and git_tracked_files(target_root, recovery_rel)
                and work_item_locator not in dirty_paths
                and recovery_rel not in dirty_paths
            ):
                diagnostic["freshness"] = "historical_active"
                diagnostic["classification"] = "stale_carrier"
                diagnostic["blocking"] = False
                diagnostic["recommended_remediation"] = (
                    "leave this unrelated historical active carrier out of the current Work Item; reconcile it through its own issue flow if it still matters."
                )
            else:
                diagnostic["freshness"] = "active"
                diagnostic["classification"] = "shared_workspace_conflict"
                diagnostic["blocking"] = True
                diagnostic["recommended_remediation"] = (
                    "finish, retire, or move this same-workspace active carrier before continuing the current workspace gate."
                )
        diagnostics.append(diagnostic)
    return diagnostics

def path_matches_owned_roots(path: str, roots: tuple[str, ...]) -> bool:
    normalized = path.rstrip("/")
    for root in roots:
        owned_root = root.rstrip("/")
        if normalized == owned_root:
            return True
        if normalized.startswith(f"{owned_root}/"):
            return True
    return False

def owned_dirty_path_kind(target_root: Path, path: str) -> str | None:
    if path_matches_owned_roots(path, OWNED_TEMP_ROOTS):
        return "temp"
    if path_matches_owned_roots(path, OWNED_RUNTIME_EVIDENCE_ROOTS):
        return "evidence"

    normalized = path.rstrip("/")
    for root in OWNED_TEMP_ROOTS:
        candidate = target_root / root
        if candidate.exists() and root.rstrip("/").startswith(f"{normalized}/"):
            return "temp"
    for root in OWNED_RUNTIME_EVIDENCE_ROOTS:
        candidate = target_root / root
        if candidate.exists() and root.rstrip("/").startswith(f"{normalized}/"):
            return "evidence"
    return None

def dirty_paths_by_owner(target_root: Path) -> tuple[list[str], list[str]]:
    owned: list[str] = []
    foreign: list[str] = []
    for entry in git_dirty_entries(target_root):
        path = entry["path"]
        if owned_dirty_path_kind(target_root, path) == "temp":
            owned.append(path)
        else:
            foreign.append(path)
    return owned, foreign

def dirty_runtime_evidence_paths(target_root: Path) -> list[str]:
    evidence: list[str] = []
    for entry in git_dirty_entries(target_root):
        path = entry["path"]
        if owned_dirty_path_kind(target_root, path) == "evidence":
            evidence.append(path)
    return evidence

def declared_current_item_dirty_paths(context: dict[str, Any]) -> set[str]:
    target_root = context["target_root"]
    report = context["report"]
    entry_points = report.get("fact_chain", {}).get("entry_points", {})
    candidates = {
        context.get("output_relative"),
        context.get("review_entry"),
    }
    if isinstance(entry_points, dict):
        candidates.update(
            entry_points.get(key)
            for key in ("work_item", "recovery_entry", "status_surface")
        )
    candidates.update(
        artifact
        for artifact in context.get("associated_artifacts", [])
        if isinstance(artifact, str)
    )

    declared: set[str] = set()
    for index, candidate in enumerate(sorted(str(value) for value in candidates if value), start=1):
        path, errors = resolve_repo_relative_path(
            target_root,
            candidate,
            label=f"declared current item artifact[{index}]",
        )
        if errors or path is None:
            continue
        declared.add(relative_to_root(path, target_root))
    return declared

def path_matches_declared_current_item(path: str, declared_paths: set[str]) -> bool:
    normalized = path.rstrip("/")
    return any(
        normalized == declared.rstrip("/")
        or normalized.startswith(f"{declared.rstrip('/')}/")
        for declared in declared_paths
    )

def declared_scope_paths(scope_text: str) -> list[str]:
    candidates: list[str] = []
    for raw in re.findall(r"`([^`]+)`", scope_text):
        token = raw.strip()
        if not token:
            continue
        if token.startswith("/"):
            token = token.lstrip("/")
        if token.startswith("./"):
            token = token[2:]
        if token in {".", ""}:
            continue
        if "/" not in token and not token.endswith(".md"):
            continue
        candidates.append(token.rstrip("/"))

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        deduped.append(candidate)
    return deduped

def path_in_scope(path: str, scope_paths: list[str]) -> bool:
    return any(path == scope_path or path.startswith(f"{scope_path}/") for scope_path in scope_paths)

def load_context(target_root: Path, output_relative: str, expected_item: str | None) -> tuple[dict[str, Any], list[str]]:
    report, errors = load_fact_chain_report(target_root, output_relative)
    if errors:
        return {}, errors

    fact_chain = report.get("fact_chain")
    entry_points = fact_chain.get("entry_points") if isinstance(fact_chain, dict) else None
    if not isinstance(entry_points, dict):
        return {}, ["fact-chain entry_points must be readable for active context"]
    item_id = entry_points.get("current_item_id")
    if fact_chain.get("mode") == "idle" or item_id == NO_ACTIVE_ITEM_ID:
        return {}, [IDLE_FACT_CHAIN_ERROR]
    if expected_item and expected_item != item_id:
        return {}, [f"current item mismatch: expected `{expected_item}`, got `{item_id}`"]

    facts = report["facts"]
    workspace_entry = str(facts["workspace_entry"]["value"])
    workspace_path, workspace_errors = resolve_workspace_path(target_root, workspace_entry)
    if workspace_errors:
        return {}, workspace_errors
    if workspace_path is None:
        return {}, [f"unable to resolve workspace entry: {workspace_entry}"]

    work_item_path, work_item_errors = resolve_repo_relative_path(
        target_root,
        str(report["fact_chain"]["entry_points"]["work_item"]),
        label="work item locator",
    )
    recovery_path, recovery_errors = resolve_repo_relative_path(
        target_root,
        str(report["fact_chain"]["entry_points"]["recovery_entry"]),
        label="recovery entry locator",
    )
    status_path, status_errors = resolve_repo_relative_path(
        target_root,
        str(report["fact_chain"]["entry_points"]["status_surface"]),
        label="status surface locator",
    )
    locator_errors = [*work_item_errors, *recovery_errors, *status_errors]
    if locator_errors:
        return {}, locator_errors
    assert work_item_path is not None
    assert recovery_path is not None
    assert status_path is not None

    context = {
        "target_root": target_root,
        "output_relative": output_relative,
        "report": report,
        "item_id": item_id,
        "work_item_path": work_item_path,
        "recovery_path": recovery_path,
        "status_path": status_path,
        "workspace_entry": workspace_entry,
        "workspace_path": workspace_path,
        "validation_entry": str(facts["validation_entry"]["value"]),
        "review_entry": str(facts["review_entry"]["value"]),
        "current_checkpoint_raw": str(facts["current_checkpoint"]["value"]),
        "current_checkpoint": normalize_checkpoint(str(facts["current_checkpoint"]["value"])),
        "goal": str(facts["goal"]["value"]),
        "scope": str(facts["scope"]["value"]),
        "execution_path": str(facts["execution_path"]["value"]),
        "associated_artifacts": list(facts["associated_artifacts"]["value"]),
        "current_stop": str(facts["current_stop"]["value"]),
        "next_step": str(facts["next_step"]["value"]),
        "blockers": str(facts["blockers"]["value"]),
        "latest_validation_summary": str(facts["latest_validation_summary"]["value"]),
        "recovery_boundary": str(facts["recovery_boundary"]["value"]),
        "current_lane": str(facts["current_lane"]["value"]),
        "closing_condition": str(facts["closing_condition"]["value"]),
        "read_entry": str(report["fact_chain"]["read_entry"]),
    }
    return context, []

def load_retained_item_context(
    target_root: Path,
    output_relative: str,
    item_id: str,
    work_item_relative: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    work_item_relative = work_item_relative or f".loom/work-items/{item_id}.md"
    work_item_path = target_root / work_item_relative
    if not work_item_path.exists():
        return {}, [f"missing retained work item: {work_item_relative}"]

    work_item, work_item_errors = parse_work_item(work_item_path, target_root)
    if work_item_errors:
        return {}, work_item_errors
    if str(work_item.get("item_id")) != item_id:
        return {}, [f"retained work item id mismatch: expected `{item_id}`, got `{work_item.get('item_id')}`"]

    recovery_relative = str(work_item["recovery_entry"])
    recovery_path, recovery_errors = resolve_repo_relative_path(
        target_root,
        recovery_relative,
        label="retained recovery entry",
    )
    if recovery_errors:
        return {}, recovery_errors
    assert recovery_path is not None
    if not recovery_path.exists():
        return {}, [f"missing retained recovery entry: {recovery_relative}"]
    recovery_entry, recovery_parse_errors = parse_recovery_entry(recovery_path, target_root, recovery_relative)
    if recovery_parse_errors:
        return {}, recovery_parse_errors
    if str(recovery_entry.get("item_id")) != item_id:
        return {}, [f"retained recovery item mismatch: expected `{item_id}`, got `{recovery_entry.get('item_id')}`"]

    workspace_path, workspace_errors = resolve_workspace_path(target_root, str(work_item["workspace_entry"]))
    if workspace_errors:
        return {}, workspace_errors
    if workspace_path is None:
        return {}, [f"unable to resolve workspace entry: {work_item['workspace_entry']}"]

    status_relative = ".loom/status/current.md"
    status_path = target_root / status_relative
    report: dict[str, Any] = {
        "fact_chain": {
            "read_entry": f"python3 .loom/bin/loom_init.py fact-chain --target . --item {item_id}",
            "entry_points": {
                "current_item_id": item_id,
                "work_item": work_item_relative,
                "recovery_entry": recovery_relative,
                "status_surface": status_relative,
            },
        },
        "facts": {
            "workspace_entry": {"value": str(work_item["workspace_entry"])},
            "validation_entry": {"value": str(work_item["validation_entry"])},
            "review_entry": {"value": str(work_item["review_entry"])},
            "current_checkpoint": {"value": str(recovery_entry["current_checkpoint"])},
            "goal": {"value": str(work_item["goal"])},
            "scope": {"value": str(work_item["scope"])},
            "execution_path": {"value": str(work_item["execution_path"])},
            "associated_artifacts": {"value": list(work_item.get("associated_artifacts", []))},
            "current_stop": {"value": str(recovery_entry["current_stop"])},
            "next_step": {"value": str(recovery_entry["next_step"])},
            "blockers": {"value": str(recovery_entry["blockers"])},
            "latest_validation_summary": {"value": str(recovery_entry["latest_validation_summary"])},
            "recovery_boundary": {"value": str(recovery_entry["recovery_boundary"])},
            "current_lane": {"value": str(recovery_entry["current_lane"])},
            "closing_condition": {"value": str(work_item["closing_condition"])},
        },
        "provenance": [
            {
                "kind": "authored_truth",
                "carrier": "work_item",
                "field": "Item ID",
                "authority": "work_item",
                "freshness": "retained",
                "path": work_item_relative,
            },
            {
                "kind": "authored_truth",
                "carrier": "recovery_entry",
                "field": "Latest Validation Summary",
                "authority": "recovery_entry",
                "freshness": "retained",
                "path": recovery_relative,
            },
        ],
        "recovery_readiness": {
            "result": "pass",
            "status": "retained",
            "summary": f"retained fact chain for `{item_id}` was loaded from authored work item and recovery carriers.",
            "missing_inputs": [],
            "fallback_to": None,
            "checks": {
                "authored_work_item": "pass",
                "authored_recovery_entry": "pass",
                "derived_status_surface": "not_applicable",
                "parallel_truth": "not_applicable",
            },
            "authoritative_carrier": "recovery_entry",
            "authoritative_path": recovery_relative,
            "parallel_truth_drift": [],
            "blocking_failures": [],
        },
        "blocking_failures": [],
    }
    context = {
        "target_root": target_root,
        "output_relative": output_relative,
        "report": report,
        "item_id": item_id,
        "work_item_path": work_item_path,
        "recovery_path": recovery_path,
        "status_path": status_path,
        "workspace_entry": str(work_item["workspace_entry"]),
        "workspace_path": workspace_path,
        "validation_entry": str(work_item["validation_entry"]),
        "review_entry": str(work_item["review_entry"]),
        "current_checkpoint_raw": str(recovery_entry["current_checkpoint"]),
        "current_checkpoint": normalize_checkpoint(str(recovery_entry["current_checkpoint"])),
        "goal": str(work_item["goal"]),
        "scope": str(work_item["scope"]),
        "execution_path": str(work_item["execution_path"]),
        "associated_artifacts": list(work_item.get("associated_artifacts", [])),
        "current_stop": str(recovery_entry["current_stop"]),
        "next_step": str(recovery_entry["next_step"]),
        "blockers": str(recovery_entry["blockers"]),
        "latest_validation_summary": str(recovery_entry["latest_validation_summary"]),
        "recovery_boundary": str(recovery_entry["recovery_boundary"]),
        "current_lane": str(recovery_entry["current_lane"]),
        "closing_condition": str(work_item["closing_condition"]),
        "read_entry": str(report["fact_chain"]["read_entry"]),
        "retained_item_context": True,
    }
    return context, []

def is_idle_context_errors(errors: list[str]) -> bool:
    return errors == [IDLE_FACT_CHAIN_ERROR]

def load_context_with_retained_idle_fallback(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
) -> tuple[dict[str, Any], list[str]]:
    context, errors = load_context(target_root, output_relative, expected_item)
    if not is_idle_context_errors(errors) or not expected_item or expected_item == NO_ACTIVE_ITEM_ID:
        return context, errors

    retained_context, retained_errors = load_retained_item_context(target_root, output_relative, expected_item)
    if retained_errors:
        return {}, [*errors, *[f"retained item: {message}" for message in retained_errors]]
    return retained_context, []

def load_fact_chain_report(target_root: Path, output_relative: str) -> tuple[dict[str, Any], list[str]]:
    report, errors = inspect_fact_chain(target_root, output_relative)
    if errors and all("missing section `Runtime Evidence`" in message for message in errors):
        report, errors = inspect_fact_chain_legacy(target_root, output_relative)
    if errors:
        return {}, errors
    if not report:
        return {}, ["no fact-chain report was produced"]
    return report, []

def inspect_fact_chain_legacy(target_root: Path, output_relative: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    output_relative = default_init_result_fallback(target_root, output_relative)
    output_path, output_errors = resolve_repo_relative_path(target_root, output_relative, label="init-result locator")
    if output_errors:
        return {}, output_errors
    assert output_path is not None
    if not output_path.exists():
        return {}, [f"missing init-result: {output_relative}"]

    try:
        init_result = load_json_file(output_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {}, [f"invalid init-result JSON: {exc}"]

    fact_chain = init_result.get("fact_chain")
    if not isinstance(fact_chain, dict):
        return {}, ["init-result is missing required section: fact_chain"]

    read_entry = fact_chain.get("read_entry")
    mode = fact_chain.get("mode")
    entry_points = fact_chain.get("entry_points")
    if not isinstance(read_entry, str) or not read_entry:
        errors.append("init-result.fact_chain.read_entry must be a non-empty string")
    if not isinstance(mode, str) or not mode:
        errors.append("init-result.fact_chain.mode must be a non-empty string")
    if not isinstance(entry_points, dict):
        errors.append("init-result.fact_chain.entry_points must be an object")
        entry_points = {}

    work_item_ref = entry_points.get("work_item")
    recovery_ref = entry_points.get("recovery_entry")
    status_ref = entry_points.get("status_surface")
    current_item_id = entry_points.get("current_item_id")
    for label, value in (
        ("work_item", work_item_ref),
        ("recovery_entry", recovery_ref),
        ("status_surface", status_ref),
        ("current_item_id", current_item_id),
    ):
        if not isinstance(value, str) or not value:
            errors.append(f"init-result.fact_chain.entry_points.{label} must be a non-empty string")
    if errors:
        return {}, errors

    work_item_path, work_item_path_errors = resolve_repo_relative_path(target_root, str(work_item_ref), label="work item locator")
    recovery_path, recovery_path_errors = resolve_repo_relative_path(target_root, str(recovery_ref), label="recovery entry locator")
    status_path, status_path_errors = resolve_repo_relative_path(target_root, str(status_ref), label="status surface locator")
    errors.extend(work_item_path_errors)
    errors.extend(recovery_path_errors)
    errors.extend(status_path_errors)
    if errors:
        return {}, errors
    assert work_item_path is not None
    assert recovery_path is not None
    assert status_path is not None
    for label, path in (
        ("work_item", work_item_path),
        ("recovery_entry", recovery_path),
        ("status_surface", status_path),
    ):
        if not path.exists():
            errors.append(f"declared fact-chain carrier is missing on disk: {label} -> {relative_to_root(path, target_root)}")
    if errors:
        return {}, errors

    work_item, work_item_errors = parse_work_item(work_item_path, target_root)
    recovery_entry, recovery_errors = parse_recovery_entry(recovery_path, target_root)
    status_sections = markdown_sections(status_path)
    status_values, status_errors = parse_key_value_section(
        status_sections,
        "Derived Fact Chain View",
        STATUS_FIELDS,
        relative_to_root(status_path, target_root),
    )
    status_sources, source_errors = parse_key_value_section(
        status_sections,
        "Sources",
        STATUS_SOURCE_FIELDS,
        relative_to_root(status_path, target_root),
    )
    errors.extend(work_item_errors)
    errors.extend(recovery_errors)
    errors.extend(status_errors)
    errors.extend(source_errors)
    if errors:
        return {}, errors

    if str(work_item["item_id"]) != str(recovery_entry["item_id"]):
        errors.append(
            "work item and recovery entry disagree on item id: "
            f"{work_item['item_id']} vs {recovery_entry['item_id']}"
        )
    if str(work_item["recovery_entry"]) != str(recovery_ref):
        errors.append(
            "work item recovery entry does not match init-result locator: "
            f"{work_item['recovery_entry']} vs {recovery_ref}"
        )
    if str(work_item["item_id"]) != str(current_item_id):
        errors.append(
            "init-result.fact_chain.entry_points.current_item_id does not match work item id: "
            f"{current_item_id} vs {work_item['item_id']}"
        )

    expected_status = {
        "item_id": str(work_item["item_id"]),
        "goal": str(work_item["goal"]),
        "scope": str(work_item["scope"]),
        "execution_path": str(work_item["execution_path"]),
        "workspace_entry": str(work_item["workspace_entry"]),
        "recovery_entry": str(work_item["recovery_entry"]),
        "review_entry": str(work_item["review_entry"]),
        "validation_entry": str(work_item["validation_entry"]),
        "closing_condition": str(work_item["closing_condition"]),
        "current_checkpoint": normalize_checkpoint(str(recovery_entry["current_checkpoint"])),
        "current_stop": recovery_entry["current_stop"],
        "next_step": recovery_entry["next_step"],
        "blockers": recovery_entry["blockers"],
        "latest_validation_summary": recovery_entry["latest_validation_summary"],
        "recovery_boundary": recovery_entry["recovery_boundary"],
        "current_lane": recovery_entry["current_lane"],
    }
    for field_name, expected_value in expected_status.items():
        actual_value = status_values.get(field_name)
        if field_name == "current_checkpoint":
            actual_value = normalize_checkpoint(str(actual_value or ""))
        if actual_value != expected_value:
            errors.append(
                "status surface mismatch for "
                f"`{field_name}`: expected `{expected_value}`, got `{actual_value}`"
            )

    expected_sources = {
        "work_item": str(work_item_ref),
        "recovery_entry": str(recovery_ref),
        "init_result": output_relative,
        "read_entry": str(read_entry),
    }
    for source_key, expected_value in expected_sources.items():
        actual_value = status_sources.get(source_key)
        if source_key == "init_result" and init_result_locator_matches(actual_value, expected_value):
            continue
        if actual_value != expected_value:
            errors.append(
                "status surface source mismatch for "
                f"`{source_key}`: expected `{expected_value}`, got `{actual_value}`"
            )
    if errors:
        return {}, errors

    report = {
        "target": str(target_root),
        "fact_chain": {
            "mode": str(mode),
            "read_entry": str(read_entry),
            "entry_points": {
                "current_item_id": str(current_item_id),
                "work_item": str(work_item_ref),
                "recovery_entry": str(recovery_ref),
                "status_surface": str(status_ref),
            },
        },
        "facts": {
            "item_id": {"value": str(work_item["item_id"])},
            "goal": {"value": str(work_item["goal"])},
            "scope": {"value": str(work_item["scope"])},
            "execution_path": {"value": str(work_item["execution_path"])},
            "associated_artifacts": {"value": list(work_item["associated_artifacts"])},
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
        "runtime_evidence": {},
        "derived_status_surface": {
            "path": str(status_ref),
            "values": expected_status,
            "runtime_evidence": {},
            "sources": expected_sources,
        },
    }
    return report, []

def purity_report_from_context(context: dict[str, Any], fact_chain_errors: list[str] | None = None) -> dict[str, Any]:
    target_root = context["target_root"]
    workspace_path = context["workspace_path"]
    workspace_entry = context["workspace_entry"]
    item_id = context["item_id"]

    hard_failures: list[str] = []
    report_only: list[str] = []

    if fact_chain_errors:
        hard_failures.extend(f"fact-chain: {message}" for message in fact_chain_errors)

    if not workspace_path.exists():
        hard_failures.append(f"declared workspace entry does not exist on disk: {workspace_entry}")
    elif not workspace_path.is_dir():
        hard_failures.append(f"declared workspace entry is not a directory: {workspace_entry}")

    cwd_relative = current_cwd_relative(target_root)
    workspace_relative = relative_to_root(workspace_path, target_root)
    if cwd_relative is not None:
        if workspace_relative != "." and cwd_relative != workspace_relative and not cwd_relative.startswith(f"{workspace_relative}/"):
            hard_failures.append(
                f"current working directory is outside the declared workspace: cwd={cwd_relative}, workspace={workspace_relative}"
            )

    owned_dirty, foreign_dirty = dirty_paths_by_owner(target_root)
    evidence_dirty = dirty_runtime_evidence_paths(target_root)
    foreign_dirty = [path for path in foreign_dirty if path not in evidence_dirty]
    declared_current_item_paths = declared_current_item_dirty_paths(context)
    declared_dirty = sorted(
        path
        for path in foreign_dirty
        if path_matches_declared_current_item(path, declared_current_item_paths)
    )
    foreign_dirty = [path for path in foreign_dirty if path not in declared_dirty]
    if foreign_dirty:
        preview = ", ".join(sorted(foreign_dirty)[:5])
        hard_failures.append(f"workspace contains untriaged residual changes: {preview}")
    if owned_dirty:
        preview = ", ".join(sorted(owned_dirty)[:5])
        hard_failures.append(f"loom-owned temporary residue is still present: {preview}")
    if evidence_dirty:
        preview = ", ".join(sorted(evidence_dirty)[:5])
        report_only.append(f"runtime review evidence is present and does not block purity on its own: {preview}")
    if declared_dirty:
        preview = ", ".join(declared_dirty[:5])
        report_only.append(f"current Work Item declares dirty artifacts and they do not block purity on their own: {preview}")

    scope_paths = declared_scope_paths(context["scope"])
    out_of_scope_changes: list[str] = []
    if scope_paths:
        for path in foreign_dirty:
            if not path_in_scope(path, scope_paths):
                out_of_scope_changes.append(path)
        if out_of_scope_changes:
            preview = ", ".join(sorted(out_of_scope_changes)[:5])
            hard_failures.append(f"scope overflow detected: {preview}")

    active_diagnostics = active_workspace_diagnostics(target_root, item_id, workspace_entry)
    conflicts = [entry for entry in active_diagnostics if entry.get("blocking")]
    stale_carriers = [entry for entry in active_diagnostics if entry.get("classification") == "stale_carrier"]
    closeout_required_carriers = [
        entry for entry in active_diagnostics if entry.get("classification") == "carrier_closeout_required"
    ]
    if conflicts:
        hard_failures.append(
            "workspace is bound to multiple active work items: "
            + ", ".join(sorted(str(entry.get("item_id") or entry.get("work_item_locator")) for entry in conflicts))
        )
    for carrier in stale_carriers:
        report_only.append(
            "stale active carrier is unrelated to the current item and does not block this workspace: "
            + str(carrier.get("item_id") or carrier.get("work_item_locator"))
        )
    for carrier in closeout_required_carriers:
        report_only.append(
            "host-complete carrier drift requires versioned carrier closeout sync before treating the same workspace binding as live execution: "
            + str(carrier.get("item_id") or carrier.get("work_item_locator"))
        )

    branch = git_branch(target_root)
    if branch:
        report_only.append(f"branch purity is host-managed and reported via host-lifecycle: current branch `{branch}`")
    else:
        report_only.append("branch purity is host-managed and reported via host-lifecycle: no branch information available")

    report_only.append("PR purity is host-managed and reported via host-lifecycle")

    state = "failed" if hard_failures else "clean"
    return {
        "state": state,
        "workspace_entry": workspace_entry,
        "workspace_path": workspace_relative,
        "scope_assessment": {
            "mode": "constrained" if scope_paths else "unconstrained",
            "declared_paths": scope_paths,
            "out_of_scope_changes": sorted(out_of_scope_changes),
        },
        "active_workspace_diagnostics": active_diagnostics,
        "hard_failures": hard_failures,
        "report_only": report_only,
    }

def blocker_text_is_clear(value: str) -> bool:
    normalized = " ".join(value.strip().lower().split())
    clear = {
        "none",
        "none.",
        "none recorded",
        "none recorded.",
    }
    if normalized in clear:
        return True
    return bool(re.fullmatch(r"(?:none|none recorded)\.? \| note: advisory:[a-z0-9][a-z0-9._-]*", normalized))


def checkpoint_payload(stage: str, context: dict[str, Any], suite_validation_override: dict[str, Any] | None = None) -> dict[str, Any]:
    purity = purity_report_from_context(context)
    missing_inputs: list[str] = []
    blocking_reasons: list[str] = []
    result = "pass"
    fallback_to: str | None = None

    if purity["hard_failures"]:
        missing_inputs.append("purity")
        result = "fallback"
        fallback_to = "admission"

    required = {
        "admission": (
            ("goal", context["goal"]),
            ("scope", context["scope"]),
            ("execution_path", context["execution_path"]),
            ("workspace_entry", context["workspace_entry"]),
            ("recovery_entry", str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])),
            ("validation_entry", context["validation_entry"]),
            ("closing_condition", context["closing_condition"]),
            ("current_checkpoint", context["current_checkpoint_raw"]),
            ("current_stop", context["current_stop"]),
            ("next_step", context["next_step"]),
        ),
        "build": (
            ("goal", context["goal"]),
            ("scope", context["scope"]),
            ("execution_path", context["execution_path"]),
            ("workspace_entry", context["workspace_entry"]),
            ("recovery_entry", str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])),
            ("status_surface", str(context["report"]["fact_chain"]["entry_points"]["status_surface"])),
            ("validation_entry", context["validation_entry"]),
            ("latest_validation_summary", context["latest_validation_summary"]),
            ("current_lane", context["current_lane"]),
            ("closing_condition", context["closing_condition"]),
        ),
        "merge": (
            ("goal", context["goal"]),
            ("scope", context["scope"]),
            ("execution_path", context["execution_path"]),
            ("workspace_entry", context["workspace_entry"]),
            ("recovery_entry", str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])),
            ("review_entry", context["review_entry"]),
            ("status_surface", str(context["report"]["fact_chain"]["entry_points"]["status_surface"])),
            ("validation_entry", context["validation_entry"]),
            ("latest_validation_summary", context["latest_validation_summary"]),
            ("current_lane", context["current_lane"]),
            ("recovery_boundary", context["recovery_boundary"]),
            ("blockers", context["blockers"]),
            ("closing_condition", context["closing_condition"]),
        ),
    }[stage]

    for label, value in required:
        if not str(value).strip():
            missing_inputs.append(label)

    current_rank = checkpoint_rank(context["current_checkpoint"])
    requested_rank = checkpoint_rank(stage)
    if context["current_checkpoint"] in TERMINAL_CHECKPOINTS:
        result = "fallback"
        fallback_to = context["current_checkpoint"]
    elif current_rank != -1 and current_rank < requested_rank:
        result = "fallback"
        fallback_to = context["current_checkpoint"]

    if not blocker_text_is_clear(context["blockers"]):
        result = "block" if result == "pass" else result
        blocker_reason = context["blockers"].strip()
        blocking_reasons.append(blocker_reason)
        missing_inputs.append(f"blocking condition: {blocker_reason}")

    pr_template: dict[str, Any] | None = None
    review_record: dict[str, Any] | None = None
    review_path: str | None = None
    spec_review: dict[str, Any] | None = None
    budget_risk: dict[str, Any] | None = None
    if stage == "merge":
        governance_surface = build_governance_surface(context["target_root"])
        github_control_plane = (
            governance_surface.get("github_control_plane")
            if isinstance(governance_surface, dict)
            else None
        )
        execution_budget = (
            github_control_plane.get("api_snapshot", {}).get("budget")
            if isinstance(github_control_plane, dict)
            else None
        )
        budget_risk = derive_execution_budget_risk(execution_budget)
        pr_template, pr_template_errors = check_pr_template(context["target_root"])
        if pr_template_errors:
            missing_inputs.extend(pr_template_errors)
            if result == "pass":
                result = "block"
        spec_review = spec_review_gate_payload(context, suite_validation_override=suite_validation_override)
        if spec_review["result"] in {"block", "fallback"}:
            missing_inputs.extend(spec_review["missing_inputs"])
            if spec_review["result"] == "fallback" and result == "pass":
                result = "fallback"
                fallback_to = spec_review["fallback_to"] or "build"
            elif result == "pass":
                result = "block"
        review_record, review_path, review_errors = load_review_record(
            context["target_root"],
            context["item_id"],
            context["review_entry"],
        )
        if review_errors:
            missing_inputs.extend(review_errors)
            if result == "pass":
                result = "block"
        elif review_record is None:
            missing_inputs.append(f"missing review artifact: {review_path}")
            if result == "pass":
                result = "block"
        else:
            decision = review_record["decision"]
            review_kind = review_record.get("kind")
            if review_kind not in IMPLEMENTATION_REVIEW_KINDS:
                missing_inputs.append(
                    "implementation review kind must be general_review or code_review; "
                    f"`{review_kind}` cannot satisfy implementation approval"
                )
                if result == "pass":
                    result = "block"
            if not review_validation_summary_binding(review_record, context["latest_validation_summary"])["matches"]:
                missing_inputs.append("review artifact does not match the latest validation summary")
                if result == "pass":
                    result = "block"
            binding_payload, binding_errors = review_head_binding(
                context["target_root"],
                reviewed_head=review_record.get("reviewed_head"),
                allowed_paths=allowed_post_review_carrier_paths(context, review_path),
            )
            review_record["head_binding"] = binding_payload
            if binding_errors:
                missing_inputs.extend(binding_errors)
                if result == "pass":
                    result = "block"
            if decision == "block":
                if result == "pass":
                    result = "block"
                missing_inputs.append(f"review decision is blocking: {review_record['summary']}")
            elif decision == "fallback":
                result = "fallback"
                fallback_to = review_record.get("fallback_to") or "build"

    if missing_inputs and result == "pass":
        result = "block"

    if result == "pass":
        summary = f"{stage} checkpoint can be consumed from the current Loom fact chain."
    elif result == "block":
        summary = (
            f"{stage} checkpoint has an explicit blocking condition and does not require a checkpoint rollback."
            if blocking_reasons
            else f"{stage} checkpoint is missing execution material but does not require a checkpoint rollback."
        )
    else:
        fallback_label = fallback_to or "admission"
        summary = f"{stage} checkpoint cannot proceed from the current state; fall back to `{fallback_label}`."
    if stage == "merge" and isinstance(budget_risk, dict) and budget_risk.get("status") == "present":
        summary = f"{summary} Budget risk remains advisory: {budget_risk.get('summary')}"

    payload = {
        "command": "checkpoint",
        "checkpoint": stage,
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
        "recovery": {
            "path": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
            "current_checkpoint": context["current_checkpoint"],
            "current_stop": context["current_stop"],
            "next_step": context["next_step"],
            "latest_validation_summary": context["latest_validation_summary"],
            "current_lane": context["current_lane"],
        },
        "review": {
            "path": context["review_entry"],
        },
        "purity": purity,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "blocking_reasons": blocking_reasons,
        "fallback_to": fallback_to,
    }
    if pr_template is not None:
        payload["pr_template"] = pr_template
    if review_path is not None:
        payload["review"] = {
            "path": review_path,
            "record": review_record,
        }
    if spec_review is not None:
        payload["spec_review"] = spec_review
    if budget_risk is not None:
        payload["budget_risk"] = budget_risk
    return payload

def runtime_artifact_updates(target_root: Path, payload: dict[str, Any], *, source: str) -> list[dict[str, Any]]:
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        artifacts = payload.get("initial_artifacts")
    if not isinstance(artifacts, list):
        return []
    updates: list[dict[str, Any]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        relative = artifact.get("path")
        if not isinstance(relative, str) or not relative.startswith(".loom/bin/"):
            continue
        path, errors = resolve_repo_relative_path(target_root, relative, label=f"{source} artifact path")
        if errors or path is None or not path.exists() or not path.is_file():
            updates.append(
                {
                    "path": relative,
                    "source": source,
                    "status": "block",
                    "missing_inputs": errors or [f"missing runtime artifact: {relative}"],
                }
            )
            continue
        expected = sha256_file(path)
        current = artifact.get("sha256")
        updates.append(
            {
                "path": relative,
                "source": source,
                "status": "current" if current == expected else "refresh-needed",
                "current_sha256": current if isinstance(current, str) else None,
                "expected_sha256": expected,
            }
        )
    return updates

def apply_runtime_artifact_updates(payload: dict[str, Any], updates: list[dict[str, Any]], *, source: str) -> None:
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        artifacts = payload.get("initial_artifacts")
    if not isinstance(artifacts, list):
        return
    expected_by_path = {
        update["path"]: update.get("expected_sha256")
        for update in updates
        if update.get("source") == source and update.get("status") == "refresh-needed"
    }
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        relative = artifact.get("path")
        if isinstance(relative, str) and relative in expected_by_path:
            artifact["sha256"] = expected_by_path[relative]

def refresh_shadow_evidence_actions(target_root: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    shadow_root = target_root / ".loom/shadow"
    if not shadow_root.exists():
        return actions
    for path in sorted(shadow_root.glob("*.json")):
        relative = relative_to_root(path, target_root)
        if relative == ".loom/shadow/shadow-parity.json":
            actions.append(
                {
                    "path": relative,
                    "kind": "shadow-evidence-summary",
                    "status": "skipped",
                    "summary": "shadow-parity.json is an aggregate command output; per-surface evidence carries source hashes.",
                }
            )
            continue
        try:
            payload = load_json_file(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            actions.append({"path": relative, "kind": "shadow-evidence", "status": "block", "missing_inputs": [str(exc)]})
            continue
        if not isinstance(payload, dict):
            actions.append({"path": relative, "kind": "shadow-evidence", "status": "block", "missing_inputs": ["shadow evidence must be a JSON object"]})
            continue
        source_files = payload.get("source_files")
        if not isinstance(source_files, list) or not source_files:
            actions.append({"path": relative, "kind": "shadow-evidence", "status": "block", "missing_inputs": ["source_files"]})
            continue
        refreshed: dict[str, str] = {}
        missing: list[str] = []
        for source in source_files:
            if not isinstance(source, str):
                missing.append("source_files entries must be strings")
                continue
            source_path, errors = resolve_repo_relative_path(target_root, source, label=f"{relative} source")
            if errors or source_path is None or not source_path.exists() or source_path.is_dir():
                missing.extend(errors or [f"missing source file: {source}"])
                continue
            refreshed[source] = sha256_file(source_path)
        if missing:
            actions.append({"path": relative, "kind": "shadow-evidence", "status": "block", "missing_inputs": missing})
            continue
        current = payload.get("source_sha256")
        actions.append(
            {
                "path": relative,
                "kind": "shadow-evidence",
                "status": "current" if current == refreshed else "refresh-needed",
                "current_source_sha256": current if isinstance(current, dict) else None,
                "expected_source_sha256": refreshed,
            }
        )
    return actions

def apply_shadow_evidence_actions(target_root: Path, actions: list[dict[str, Any]]) -> None:
    for action in actions:
        if action.get("kind") != "shadow-evidence" or action.get("status") != "refresh-needed":
            continue
        relative = action.get("path")
        expected = action.get("expected_source_sha256")
        if not isinstance(relative, str) or not isinstance(expected, dict):
            continue
        path, errors = resolve_repo_relative_path(target_root, relative, label="shadow evidence path")
        if errors or path is None:
            continue
        payload = load_json_file(path)
        if isinstance(payload, dict):
            payload["source_sha256"] = expected
            write_json_file(path, payload)

def uses_global_cli_metadata_only(target_root: Path) -> bool:
    state_path = target_root / ".loom/installed-state.json"
    if state_path.is_symlink() or not state_path.is_file():
        return False
    try:
        installed_state = load_json_file(state_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    if not isinstance(installed_state, dict):
        return False
    repo_payload = installed_state.get("repo_payload")
    return (
        installed_state.get("schema_version") == "loom-installed-state/v2"
        and installed_state.get("runtime_provider") == "global-cli"
        and isinstance(repo_payload, dict)
        and repo_payload.get("mode") == "metadata-only"
    )

def carrier_refresh_payload(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    *,
    dry_run: bool,
    surface: str = "merge_ready",
) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    context, context_errors = load_context(target_root, output_relative, expected_item)
    idle_context = is_idle_context_errors(context_errors)
    missing_inputs: list[str] = [] if idle_context else [f"fact-chain: {message}" for message in context_errors]

    manifest_path: Path | None = None
    if not uses_global_cli_metadata_only(target_root):
        manifest_path, manifest_path_errors = resolve_repo_relative_path(
            target_root,
            ".loom/bootstrap/manifest.json",
            label="bootstrap manifest",
        )
        missing_inputs.extend(manifest_path_errors)
    init_path, init_path_errors = resolve_repo_relative_path(target_root, output_relative, label="init-result locator")
    missing_inputs.extend(init_path_errors)
    manifest_payload: dict[str, Any] = {}
    init_payload: dict[str, Any] = {}
    for label, path in (("manifest", manifest_path), ("init-result", init_path)):
        if path is None:
            continue
        try:
            payload = load_json_file(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            missing_inputs.append(f"invalid {label}: {exc}")
            continue
        if label == "manifest":
            manifest_payload = payload
        else:
            init_payload = payload

    actions: list[dict[str, Any]] = []
    actions.extend(runtime_artifact_updates(target_root, manifest_payload, source="manifest"))
    actions.extend(runtime_artifact_updates(target_root, init_payload, source="init-result"))
    actions.extend(refresh_shadow_evidence_actions(target_root))
    refresh_needed_actions = [action for action in actions if action.get("status") == "refresh-needed"]
    for action in actions:
        if action.get("status") == "block":
            missing_inputs.extend(str(message) for message in action.get("missing_inputs", []))
    if runtime_state.get("result") != "pass":
        refreshable_runtime_drift = {
            f"bootstrap runtime artifact `{action.get('path')}` sha256 drifted"
            for action in actions
            if action.get("kind") is None and action.get("status") == "refresh-needed" and action.get("path")
        }
        for message in runtime_state.get("missing_inputs", []):
            if str(message) not in refreshable_runtime_drift:
                missing_inputs.append(f"runtime-state: {message}")

    review_status: dict[str, Any] = {"status": "not_checked"}
    if idle_context:
        review_status = {
            "status": "not_applicable",
            "reason": "repository is idle; no active Work Item review binding is selected",
        }
    elif not context_errors:
        assert context
        review_record, review_path, review_errors = load_review_record(target_root, context["item_id"], context["review_entry"])
        spec_review_path = default_spec_review_path(context["item_id"])
        normalized_checkpoint = normalize_checkpoint(str(context.get("current_checkpoint", "")))
        terminal_closeout_surface = surface == "closeout" and normalized_checkpoint in TERMINAL_CHECKPOINTS
        allowed_paths = (
            allowed_terminal_closeout_carrier_paths(context, review_path, spec_review_path)
            if terminal_closeout_surface
            else allowed_post_review_carrier_paths(context, review_path, spec_review_path)
        )
        if review_errors or review_record is None:
            review_status = {"status": "missing", "path": review_path, "missing_inputs": review_errors or [f"missing review artifact: {review_path}"]}
        else:
            binding, binding_errors = review_head_binding(
                target_root,
                reviewed_head=str(review_record.get("reviewed_head", "")),
                allowed_paths=allowed_paths,
            )
            review_status = {
                "path": review_path,
                "head_binding": binding,
                "missing_inputs": binding_errors,
                "surface": surface,
                "allowed_paths_policy": (
                    "terminal closeout carrier paths only; requires terminal checkpoint"
                    if terminal_closeout_surface
                    else "post-review carrier paths only"
                ),
            }
            if binding.get("status") == "implementation-drift-only":
                review_status["status"] = "block"
                missing_inputs.append("review artifact is stale because non-carrier drift is present")
            elif binding.get("status") == "stale":
                carrier_only_paths = binding.get("carrier_only_paths") if isinstance(binding.get("carrier_only_paths"), list) else []
                generated_only_paths = binding.get("generated_only_paths") if isinstance(binding.get("generated_only_paths"), list) else []
                refresh_managed_paths = [
                    str(path)
                    for path in [*carrier_only_paths, *generated_only_paths]
                    if isinstance(path, str) and path
                ]
                semantic_drift_paths = binding.get("semantic_drift_paths") if isinstance(binding.get("semantic_drift_paths"), list) else []
                semantic_drift_paths = [
                    str(path)
                    for path in semantic_drift_paths
                    if isinstance(path, str) and path
                ]
                if semantic_drift_paths:
                    review_status["status"] = "block"
                    missing_inputs.append("review artifact is stale because non-carrier drift is present")
                elif refresh_managed_paths:
                    review_status["status"] = "advisory"
                    review_status["reason"] = (
                        "carrier refresh reports stale review metadata but does not use it as merge approval; "
                        "PR gate/review surfaces enforce semantic approval separately."
                    )
                    review_status["refresh_scope"] = {
                        "pending_actions": len(refresh_needed_actions),
                        "refresh_managed_paths": refresh_managed_paths,
                    }
                else:
                    review_status["status"] = "block"
                    missing_inputs.append("review artifact is stale because non-carrier drift is present")
            elif binding.get("status") == "carrier-only":
                review_status["status"] = "refresh-needed"
            else:
                review_status["status"] = "current"

    if not dry_run and not missing_inputs:
        fixed = refresh_needed_actions
        if manifest_path is not None:
            apply_runtime_artifact_updates(manifest_payload, actions, source="manifest")
            write_json_file(manifest_path, manifest_payload)
        if init_path is not None:
            apply_runtime_artifact_updates(init_payload, actions, source="init-result")
            write_json_file(init_path, init_payload)
        apply_shadow_evidence_actions(target_root, actions)
        readback_payload = carrier_refresh_payload(
            target_root,
            output_relative,
            expected_item,
            dry_run=True,
            surface=surface,
        )
        readback_result = "pass" if readback_payload.get("result") == "pass" and not readback_payload.get("refresh_needed") else "block"
        return {
            **readback_payload,
            "result": readback_result,
            "summary": (
                "carrier refresh completed and readback found no remaining updates."
                if readback_result == "pass"
                else "carrier refresh applied updates but readback still found pending or blocking drift."
            ),
            "dry_run": False,
            "fallback_to": None if readback_result == "pass" else "adoption",
            "fixed": fixed,
            "remaining_refresh": readback_payload.get("refresh_needed", []),
        }

    refresh_needed = refresh_needed_actions
    result = "block" if missing_inputs else "pass"
    return {
        "command": "carrier",
        "operation": "refresh",
        "schema_version": "loom-carrier-refresh/v1",
        "result": result,
        "summary": (
            "carrier refresh completed." if result == "pass" and not dry_run
            else "carrier refresh dry-run completed." if result == "pass"
            else "carrier refresh found blocking drift."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "adoption",
        "dry_run": dry_run,
        "surface": surface,
        "runtime_state": runtime_state,
        "actions": actions,
        "refresh_needed": refresh_needed,
        "review": review_status,
    }

def github_commit_pulls(root: Path, owner: str, repo_name: str, head_sha: str) -> tuple[list[dict[str, Any]], list[str]]:
    path = f"repos/{owner}/{repo_name}/commits/{head_sha}/pulls"
    result = run_process(
        [
            "gh",
            "api",
            path,
            "-H",
            "Accept: application/vnd.github+json",
        ],
        root,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh api commit pulls failed"
        blocked_errors = host_api_anonymous_fallback_blocked(root, path, [detail])
        if blocked_errors:
            return [], blocked_errors
        pulls, fallback_errors = github_public_rest_list(path)
        if pulls:
            return pulls, []
        return [], [host_api_diagnostic_message(f"gh api {path}", [detail]), *[f"public REST fallback: {message}" for message in fallback_errors]]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [], [f"invalid JSON from commit pulls REST endpoint: {exc.msg}"]
    if not isinstance(payload, list):
        return [], ["commit pulls REST endpoint did not return a list"]
    return [entry for entry in payload if isinstance(entry, dict)], []

def load_optional_json_fixture(target_root: Path, fixture: str | None, *, label: str) -> tuple[Any | None, list[str]]:
    if not fixture:
        return None, []
    path, errors = resolve_artifact_read_path(target_root, fixture, label=label)
    if errors:
        return None, errors
    assert path is not None
    if not path.exists() or not path.is_file():
        return None, [f"{label} points to a missing file: {fixture}"]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid {label} `{fixture}`: {exc}"]

def load_optional_text_fixture(target_root: Path, fixture: str | None, *, label: str) -> tuple[str | None, list[str]]:
    if not fixture:
        return None, []
    path, errors = resolve_artifact_read_path(target_root, fixture, label=label)
    if errors:
        return None, errors
    assert path is not None
    if not path.exists() or not path.is_file():
        return None, [f"{label} points to a missing file: {fixture}"]
    try:
        return path.read_text(encoding="utf-8"), []
    except OSError as exc:
        return None, [f"invalid {label} `{fixture}`: {exc}"]

def pr_metadata_issue_reference(issue_number: int | None) -> str | None:
    if issue_number is None:
        return None
    return f"#{issue_number}"

def pr_metadata_body_mentions_issue(body: object, issue_number: int | None) -> bool:
    if issue_number is None:
        return True
    return text_mentions_issue(body, issue_number)

def pr_metadata_issue_backlink_repair_action(
    *,
    issue_number: int,
    pr_number: int | None,
    surface: str,
    body_file: str | None,
    compare_body_file: str | None,
    contract_results: list[dict[str, Any]],
    host_readback_available: bool,
) -> dict[str, Any] | None:
    machine_carrier_passed = bool(contract_results) and all(
        contract_result.get("result") == "pass" for contract_result in contract_results
    )
    if not machine_carrier_passed or not host_readback_available:
        return None
    command_parts = [
        "loom",
        "pr",
        "metadata-update",
        str(pr_number or "<pr>"),
        "--surface",
        surface,
        "--issue",
        str(issue_number),
        "--apply",
        "--json",
    ]
    if body_file:
        command_parts.extend(["--base-body-file", body_file])
    return {
        "kind": "missing_human_backlink",
        "action": "update_pr_body_issue_backlink",
        "target": "pr_body",
        "issue": issue_number,
        "pr": pr_number,
        "body_line": f"- Issue: #{issue_number}",
        "mode": "safe_repair",
        "allowed_when": "cli --issue, PR metadata machine carrier, and host PR body readback agree on Work Item, branch, and head SHA.",
        "required_readback": "update PR body, read back the host body, then rerun metadata preflight.",
        "next_command": shlex.join(command_parts),
        "body_artifacts": {
            "rendered_body_file": body_file,
            "readback_body_file": compare_body_file,
        },
    }

def normalize_pr_fixture_payload(payload: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(payload, dict):
        return None, ["PR payload fixture must be a JSON object"]
    normalized = dict(payload)
    if "isDraft" not in normalized and "draft" in normalized:
        normalized["isDraft"] = bool(normalized.get("draft"))
    if "headRefOid" not in normalized:
        head = normalized.get("head") if isinstance(normalized.get("head"), dict) else None
        if isinstance(head, dict) and isinstance(head.get("sha"), str):
            normalized["headRefOid"] = head.get("sha")
    if "headRefName" not in normalized:
        head = normalized.get("head") if isinstance(normalized.get("head"), dict) else None
        if isinstance(head, dict) and isinstance(head.get("ref"), str):
            normalized["headRefName"] = head.get("ref")
    if "baseRefName" not in normalized:
        base = normalized.get("base") if isinstance(normalized.get("base"), dict) else None
        if isinstance(base, dict) and isinstance(base.get("ref"), str):
            normalized["baseRefName"] = base.get("ref")
    if "mergedAt" not in normalized and isinstance(normalized.get("merged_at"), str):
        normalized["mergedAt"] = normalized.get("merged_at")
    if "mergeCommit" not in normalized and isinstance(normalized.get("merge_commit_sha"), str):
        normalized["mergeCommit"] = {"oid": normalized.get("merge_commit_sha")}
    if "state" in normalized:
        normalized["state"] = str(normalized.get("state") or "unknown").upper()
    else:
        normalized["state"] = "OPEN"
    return normalized, []

def normalize_issue_fixture_payload(payload: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(payload, dict):
        return None, ["issue payload fixture must be a JSON object"]
    normalized = dict(payload)
    if "html_url" in normalized and "url" not in normalized:
        normalized["url"] = normalized.get("html_url")
    if "node_id" in normalized and "id" not in normalized:
        normalized["id"] = normalized.get("node_id")
    if "state" in normalized:
        normalized["state"] = github_issue_state(normalized.get("state"))
    else:
        normalized["state"] = "OPEN"
    labels = normalized.get("labels")
    if isinstance(labels, list):
        normalized["labels"] = [
            str(label.get("name"))
            for label in labels
            if isinstance(label, dict) and isinstance(label.get("name"), str)
        ]
    return normalized, []

def infer_pr_number_from_ref(ref: str | None) -> int | None:
    if not isinstance(ref, str):
        return None
    for pattern in (r"(?:^|/)pr[-/](\d+)(?:[-/]|$)", r"pull/(\d+)/(?:head|merge)$"):
        match = re.search(pattern, ref, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

def pr_work_item_from_body(body: Any) -> str | None:
    if not isinstance(body, str):
        return None
    work_item_id = r"(?:[A-Z]+-\d+(?:-\d+)*|INIT-\d+)"
    patterns = (
        rf"(?im)^[ \t]*[-*]?[ \t]*Loom Work Item[ \t]*:[ \t]*`?({work_item_id})`?[ \t]*$",
        rf"(?im)^[ \t]*[-*]?[ \t]*Work Item[ \t]*:[ \t]*`?({work_item_id})`?[ \t]*$",
        rf"(?im)^[ \t]*[-*]?[ \t]*Loom-Work-Item[ \t]*:[ \t]*`?({work_item_id})`?[ \t]*$",
    )
    for pattern in patterns:
        match = re.search(pattern, body)
        if match:
            return match.group(1).strip()
    return None

def pr_body_field_value(body: Any, label: str) -> str | None:
    if not isinstance(body, str):
        return None
    pattern = rf"(?im)^[ \t]*[-*]?[ \t]*{re.escape(label)}[ \t]*:[ \t]*`?([^`\n]+?)`?[ \t]*$"
    match = re.search(pattern, body)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None

def pr_body_governance_metadata_fields(body: Any) -> dict[str, Any]:
    if not isinstance(body, str):
        return {}
    for block in pr_metadata_html_comment_blocks(body, "loom:repo-pr-metadata"):
        try:
            envelope = json.loads(block["raw"])
        except json.JSONDecodeError:
            continue
        if not isinstance(envelope, dict):
            continue
        if envelope.get("metadata_contract_id") != GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID:
            continue
        fields = envelope.get("fields")
        if isinstance(fields, dict):
            return fields
    return {}

def pr_body_machine_surface(body: Any) -> str | None:
    if not isinstance(body, str):
        return None
    for block in pr_metadata_html_comment_blocks(body, "loom:repo-pr-metadata"):
        try:
            envelope = json.loads(block["raw"])
        except json.JSONDecodeError:
            continue
        if not isinstance(envelope, dict):
            continue
        surface = envelope.get("surface")
        if isinstance(surface, str) and surface.strip():
            return surface.strip()
    return None

def pr_metadata_block_locator(body: str, start: int, end: int, marker: str) -> dict[str, Any]:
    raw_excerpt = body[start:end]
    return {
        "marker": marker,
        "start_offset": start,
        "end_offset": end,
        "start_line": body.count("\n", 0, start) + 1,
        "end_line": body.count("\n", 0, end) + 1,
        "raw_excerpt_sha256": hashlib.sha256(raw_excerpt.encode("utf-8")).hexdigest(),
    }

def pr_metadata_expected_format(marker: str) -> str:
    return (
        f"<!-- {marker}\n"
        "{\n"
        '  "schema_version": "loom-repo-pr-metadata/v1",\n'
        '  "metadata_contract_id": "<repo-specific-id>",\n'
        '  "surface": "review|merge_ready|closeout",\n'
        '  "fields": {"work_item_locator": "owner/repo/work_item/id", "<repo-field>": "<value>"},\n'
        '  "source": {"rendered_hash": "<sha256-or-repo-renderer-hash>"},\n'
        '  "parser_version": "loom-pr-metadata-parser/v2"\n'
        "}\n"
        "-->"
    )

def metadata_contract_raw_fields(
    target_root: Path,
    governance_surface: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], str | None]:
    repo_interface = governance_surface.get("repo_interface")
    if not isinstance(repo_interface, dict):
        return [], ["governance_surface.repo_interface"], None
    availability = repo_interface.get("availability")
    if availability in {"absent", "companion_docs_only"}:
        return [], [], None
    if availability == "incomplete":
        missing = repo_interface.get("missing_inputs")
        return [], list(missing) if isinstance(missing, list) else ["repo companion interface"], None
    if availability != "present":
        return [], [f"unknown repo companion availability: {availability}"], None

    locator = ".loom/companion/repo-interface.json"
    locator_entry = repo_interface.get("repo_specific_requirements")
    if isinstance(locator_entry, dict) and isinstance(locator_entry.get("locator"), str):
        locator = locator_entry["locator"]
    repo_interface_path, locator_errors = resolve_repo_relative_path(
        target_root,
        locator,
        label="repo companion metadata contract locator",
    )
    if locator_errors:
        return [], locator_errors, locator
    assert repo_interface_path is not None
    try:
        payload = load_json_file(repo_interface_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        return [], [f"repo companion metadata contract is unreadable: {exc}"], locator
    metadata_contract = payload.get("metadata_contract") if isinstance(payload, dict) else None
    fields = metadata_contract.get("fields") if isinstance(metadata_contract, dict) else None
    if fields is None:
        return [], [], locator
    if not isinstance(fields, list):
        return [], ["metadata_contract.fields must be a list"], locator
    return [field for field in fields if isinstance(field, dict)], [], locator

def pr_metadata_contract_surface(field: dict[str, Any]) -> str:
    machine_carrier = field.get("machine_carrier") if isinstance(field.get("machine_carrier"), dict) else {}
    carrier_surface = machine_carrier.get("surface")
    return carrier_surface if isinstance(carrier_surface, str) and carrier_surface else "merge_ready"

def applicable_pr_metadata_contracts(
    fields: list[dict[str, Any]],
    *,
    surface: str,
) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for field in fields:
        machine_carrier = field.get("machine_carrier")
        if not isinstance(machine_carrier, dict):
            continue
        carrier_surface = pr_metadata_contract_surface(field)
        preflight = machine_carrier.get("preflight")
        required_before = preflight.get("required_before") if isinstance(preflight, dict) else None
        if isinstance(required_before, list) and surface in required_before:
            contracts.append(field)
            continue
        if surface == "closeout" and carrier_surface == "merge_ready":
            contracts.append(field)
    return contracts

def pr_metadata_effective_contract_surface(field: dict[str, Any], requested_surface: str) -> str:
    carrier_surface = pr_metadata_contract_surface(field)
    machine_carrier = field.get("machine_carrier") if isinstance(field.get("machine_carrier"), dict) else {}
    preflight = machine_carrier.get("preflight") if isinstance(machine_carrier.get("preflight"), dict) else {}
    required_before = preflight.get("required_before")
    if requested_surface in {"review", "pre_review"} and carrier_surface == "merge_ready":
        if isinstance(required_before, list) and requested_surface in required_before:
            return "merge_ready"
    return requested_surface

def pr_metadata_candidate_contract_surfaces(field: dict[str, Any], requested_surface: str) -> list[str]:
    effective_surface = pr_metadata_effective_contract_surface(field, requested_surface)
    surfaces = [requested_surface]
    if effective_surface not in surfaces:
        surfaces.append(effective_surface)
    return surfaces

def pr_metadata_html_comment_blocks(body: str, marker: str) -> list[dict[str, Any]]:
    pattern = re.compile(rf"<!--\s*{re.escape(marker)}\s*(.*?)\s*-->", flags=re.DOTALL)
    blocks: list[dict[str, Any]] = []
    for match in pattern.finditer(body):
        blocks.append(
            {
                "raw": match.group(1).strip(),
                "locator": pr_metadata_block_locator(body, match.start(), match.end(), marker),
            }
        )
    return blocks

def pr_metadata_block_fingerprints(body: str, marker: str) -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "start_line": block["locator"].get("start_line"),
            "end_line": block["locator"].get("end_line"),
            "raw_excerpt_sha256": block["locator"].get("raw_excerpt_sha256"),
        }
        for index, block in enumerate(pr_metadata_html_comment_blocks(body, marker))
    ]

def pr_metadata_body_artifact_payload(
    *,
    body_file: str | None,
    body: str | None,
    compare_body_file: str | None,
    compare_body: str | None,
    applicable_contracts: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if body_file is None and compare_body_file is None:
        return None
    body_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest() if isinstance(body, str) else None
    compare_sha256 = hashlib.sha256(compare_body.encode("utf-8")).hexdigest() if isinstance(compare_body, str) else None
    comparisons: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    for field in applicable_contracts:
        contract_id = str(field.get("id") or "unknown")
        machine_carrier = field.get("machine_carrier") if isinstance(field.get("machine_carrier"), dict) else {}
        marker = str(machine_carrier.get("marker") or "loom:repo-pr-metadata")
        before_blocks = pr_metadata_block_fingerprints(body, marker) if isinstance(body, str) else []
        after_blocks = pr_metadata_block_fingerprints(compare_body, marker) if isinstance(compare_body, str) else []
        status = "not_compared"
        if compare_body_file is not None:
            before_hashes = [block.get("raw_excerpt_sha256") for block in before_blocks]
            after_hashes = [block.get("raw_excerpt_sha256") for block in after_blocks]
            status = "match" if before_hashes == after_hashes else "mismatch"
            if status == "mismatch":
                missing_inputs.append(f"PR metadata machine block drift after body edit: {contract_id}")
        comparisons.append(
            {
                "metadata_contract_id": contract_id,
                "marker": marker,
                "status": status,
                "rendered_blocks": before_blocks,
                "post_edit_blocks": after_blocks if compare_body_file is not None else [],
            }
        )
    result = "pass" if not missing_inputs else "block"
    return {
        "schema_version": "loom-pr-body-metadata-artifact/v1",
        "result": result,
        "summary": (
            "rendered PR body metadata artifact is readable and post-edit machine blocks match."
            if result == "pass" and compare_body_file is not None
            else "rendered PR body metadata artifact is readable."
            if result == "pass"
            else "post-edit PR body readback changed declared metadata machine blocks."
        ),
        "body_file": body_file,
        "body_sha256": body_sha256,
        "compare_body_file": compare_body_file,
        "compare_body_sha256": compare_sha256,
        "preflight_body_source": "compare_body_file" if compare_body_file else "body_file",
        "machine_block_comparisons": comparisons,
        "missing_inputs": missing_inputs,
        "fallback_to": "gh_pr_edit_body_file_readback" if missing_inputs else None,
        "safe_update_strategy": "render PR body to a file, update with `gh pr edit --body-file <file>`, read back the PR body, then rerun metadata preflight with --body-file and --compare-body-file.",
    }

def pr_metadata_allowed_values(missing_fields: list[str] | None) -> dict[str, list[str]]:
    allowed_values: dict[str, list[str]] = {}
    for field in missing_fields or []:
        values = PR_METADATA_DIAGNOSTIC_ALLOWED_VALUES.get(field)
        if values:
            allowed_values[field] = values
    return allowed_values

def pr_metadata_diagnostic_classifier(
    *,
    reason: str,
    missing_fields: list[str] | None,
    parse_error: str | None,
) -> str:
    fields = set(missing_fields or [])
    if parse_error:
        return "parse_error"
    if {"metadata_contract_id", "surface"} & fields:
        return "surface_drift"
    if {f"fields.{name}" for name in GOVERNANCE_METADATA_HOST_OWNED_FIELDS} & fields:
        return "host_owned_fact_authored"
    if "fields.work_item_locator" in fields or "work item" in reason.lower():
        return "work_item_locator_invalid"
    if any(field in PR_METADATA_DIAGNOSTIC_ALLOWED_VALUES for field in fields):
        return "enum_violation"
    if "metadata_block" in fields or "pr.body" in fields:
        return "missing_machine_block"
    return "contract_violation"

def pr_metadata_diagnostic_next_action(
    *,
    classifier: str,
    fallback_to: str,
    expected_surface: str | None,
    missing_fields: list[str] | None,
) -> str:
    fields = set(missing_fields or [])
    if classifier == "surface_drift":
        surface = expected_surface or "the requested surface"
        return f"rerender the PR metadata machine block for surface `{surface}` and replace the stale carrier before rerunning preflight."
    if classifier == "host_owned_fact_authored":
        return "remove authored branch, head, merge, and check fields from the PR metadata block; GitHub host readback owns them."
    if classifier == "work_item_locator_invalid":
        return "set the PR `Work Item` and machine field to one `owner/repo/work_item/id` locator, then rerun preflight."
    if classifier == "enum_violation":
        invalid_fields = sorted(field for field in fields if field in PR_METADATA_DIAGNOSTIC_ALLOWED_VALUES)
        field_list = ", ".join(invalid_fields) if invalid_fields else "the governance enum fields"
        return f"rewrite {field_list} to one of the allowed values, then rerun preflight."
    if classifier == "parse_error":
        return "rerender or rewrite the PR metadata HTML comment JSON block so it decodes cleanly, then rerun preflight."
    if classifier == "missing_machine_block":
        return "render or restore the declared PR metadata machine block before rerunning preflight."
    if fallback_to == "update_pr_body":
        return "regenerate or update the PR body machine carrier, then rerun preflight."
    return "repair the declared PR metadata carrier inputs, then rerun preflight."

def pr_metadata_diagnostic(
    *,
    contract_id: str,
    marker: str,
    reason: str,
    source_locator: str | None = None,
    source_range_or_hash: str | None = None,
    expected_schema: str | None = None,
    expected_parser_version: str | None = None,
    fallback_to: str = "update_pr_body",
    block_locator: dict[str, Any] | None = None,
    parse_error: str | None = None,
    missing_fields: list[str] | None = None,
    expected_surface: str | None = None,
) -> dict[str, Any]:
    normalized_missing_fields = missing_fields or []
    classifier = pr_metadata_diagnostic_classifier(
        reason=reason,
        missing_fields=normalized_missing_fields,
        parse_error=parse_error,
    )
    next_action = pr_metadata_diagnostic_next_action(
        classifier=classifier,
        fallback_to=fallback_to,
        expected_surface=expected_surface,
        missing_fields=normalized_missing_fields,
    )
    primary = failure_primary_cause(
        cause_id=f"pr_metadata_{classifier}",
        failure_domain="governance_metadata",
        code=classifier,
        locator=source_locator or "pr_metadata:body",
        summary=reason,
        owner="repository",
        retryable=False,
        remediation_command=next_action,
    )
    return {
        "classifier": classifier,
        "metadata_contract_id": contract_id,
        "block_locator": block_locator,
        "source_locator": source_locator,
        "source_range_or_hash": source_range_or_hash,
        "parse_error": parse_error,
        "missing_fields": normalized_missing_fields,
        "expected_schema": expected_schema or PR_METADATA_MACHINE_SCHEMA,
        "expected_surface": expected_surface,
        "expected_parser_version": expected_parser_version or PR_METADATA_PARSER_VERSION,
        "allowed_values": pr_metadata_allowed_values(normalized_missing_fields),
        "expected_format": pr_metadata_expected_format(marker),
        "suggested_fix": "rewrite the PR metadata HTML comment JSON block with the declared schema, surface, contract id, and required fields.",
        "fallback_to": fallback_to,
        "next_action": next_action,
        "failure_envelope": failure_envelope(primary),
        "reason": reason,
    }

def governance_metadata_string_field(fields: dict[str, Any], name: str, missing_fields: list[str]) -> str | None:
    value = fields.get(name)
    if not isinstance(value, str) or not value.strip():
        missing_fields.append(f"fields.{name}")
        return None
    return value.strip()

def governance_metadata_bool_field(fields: dict[str, Any], name: str, missing_fields: list[str]) -> bool | None:
    value = fields.get(name)
    if value is not True:
        missing_fields.append(f"fields.{name}")
        return None
    return True

def governance_metadata_optional_bool_field(fields: dict[str, Any], name: str, missing_fields: list[str]) -> bool | None:
    value = fields.get(name)
    if not isinstance(value, bool):
        missing_fields.append(f"fields.{name}")
        return None
    return value

def work_item_locator_for_metadata(
    item_id: str | None,
    issue_number: int | None,
    owner: str | None = None,
    repo: str | None = None,
) -> str | None:
    """Normalize PR metadata to the canonical repository-qualified Work Item locator."""

    parsed = parse_typed_locator(item_id, allowed_types={"work_item"})
    if parsed is not None:
        if not parsed["legacy"]:
            if owner and repo and (str(parsed["owner"]).lower(), str(parsed["repo"]).lower()) != (owner.lower(), repo.lower()):
                return None
            return str(parsed["locator"])
        if owner and repo:
            return typed_locator(owner, repo, "work_item", int(parsed["id"]))
    if isinstance(issue_number, int) and issue_number > 0 and owner and repo:
        return typed_locator(owner, repo, "work_item", issue_number)
    return None

def authoritative_work_item_locator_for_metadata(
    target_root: Path,
    item_id: str | None,
    issue_number: int | None,
    owner: str | None,
    repo: str | None,
) -> tuple[str | None, list[str]]:
    """Resolve metadata binding from explicit host authority or the Work Item carrier."""

    issue_locator = work_item_locator_for_metadata(None, issue_number, owner, repo)
    item_locator = work_item_locator_for_metadata(item_id, None, owner, repo)
    if item_locator is None and item_id and owner and repo:
        match = re.fullmatch(r"WI-([1-9]\d*)", item_id)
        carrier_path = target_root / ".loom" / "work-items" / f"{item_id}.md"
        if match is not None and carrier_path.is_file():
            carrier, carrier_errors = parse_work_item(carrier_path, target_root)
            if not carrier_errors and carrier.get("item_id") == item_id:
                item_locator = typed_locator(owner, repo, "work_item", int(match.group(1)))
    if issue_locator and item_locator and issue_locator != item_locator:
        return None, [
            f"explicit GitHub issue authority `{issue_locator}` conflicts with Work Item authority `{item_locator}`"
        ]
    return issue_locator or item_locator, []

def validate_governance_intensity_metadata_fields(fields: dict[str, Any]) -> list[str]:
    missing_fields: list[str] = []
    missing_fields.extend(
        f"fields.{name}"
        for name in sorted(set(fields) - GOVERNANCE_METADATA_FIELD_ALLOWLIST)
    )
    work_item_locator = governance_metadata_string_field(fields, "work_item_locator", missing_fields)
    governance_intensity = governance_metadata_string_field(fields, "governance_intensity", missing_fields)
    change_class = governance_metadata_string_field(fields, "change_class", missing_fields)
    suite_path = governance_metadata_string_field(fields, "suite_path", missing_fields)
    review_requirement = governance_metadata_string_field(fields, "review_requirement", missing_fields)
    release_judgment = governance_metadata_string_field(fields, "release_judgment", missing_fields)
    fact_chain_required = governance_metadata_optional_bool_field(fields, "fact_chain_required", missing_fields)
    governance_metadata_bool_field(fields, "pr_gate_required", missing_fields)
    governance_metadata_bool_field(fields, "closeout_required", missing_fields)

    if work_item_locator and parse_typed_locator(work_item_locator, allowed_types={"work_item"}, allow_legacy=False) is None:
        missing_fields.append("fields.work_item_locator")
    if governance_intensity and governance_intensity not in GOVERNANCE_INTENSITY_VALUES:
        missing_fields.append("fields.governance_intensity")
    if change_class and change_class not in GOVERNANCE_CHANGE_CLASS_VALUES:
        missing_fields.append("fields.change_class")
    if suite_path and suite_path not in GOVERNANCE_SUITE_PATH_VALUES:
        missing_fields.append("fields.suite_path")
    if review_requirement and review_requirement not in GOVERNANCE_REVIEW_REQUIREMENT_VALUES:
        missing_fields.append("fields.review_requirement")
    if release_judgment and release_judgment not in GOVERNANCE_RELEASE_JUDGMENT_VALUES:
        missing_fields.append("fields.release_judgment")
    if review_requirement == GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT and fact_chain_required is not False:
        missing_fields.append("fields.fact_chain_required")
    if fact_chain_required is False and review_requirement != GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT:
        missing_fields.append("fields.review_requirement")

    upgrade_triggers = fields.get("upgrade_triggers")
    if not isinstance(upgrade_triggers, list) or any(not isinstance(entry, str) or not entry.strip() for entry in upgrade_triggers):
        missing_fields.append("fields.upgrade_triggers")
    anchor_issue = fields.get("anchor_issue")
    if anchor_issue is not None and (not isinstance(anchor_issue, int) or anchor_issue <= 0):
        missing_fields.append("fields.anchor_issue")
    covered_issues = fields.get("covered_issues")
    if covered_issues is not None:
        if (
            not isinstance(covered_issues, list)
            or any(not isinstance(entry, int) or entry <= 0 for entry in covered_issues)
            or len(set(covered_issues)) != len(covered_issues)
        ):
            missing_fields.append("fields.covered_issues")
        elif isinstance(anchor_issue, int) and anchor_issue not in covered_issues:
            missing_fields.append("fields.covered_issues")
    excluded_scope = fields.get("excluded_scope")
    if excluded_scope is not None and (not isinstance(excluded_scope, list) or any(not isinstance(entry, str) or not entry.strip() for entry in excluded_scope)):
        missing_fields.append("fields.excluded_scope")

    suite_not_applicable = fields.get("suite_not_applicable")
    if suite_path == "not_applicable":
        if not isinstance(suite_not_applicable, dict):
            missing_fields.append("fields.suite_not_applicable")
        else:
            for required_field in GOVERNANCE_NOT_APPLICABLE_REQUIRED_FIELDS:
                value = suite_not_applicable.get(required_field)
                if not isinstance(value, str) or not value.strip():
                    missing_fields.append(f"fields.suite_not_applicable.{required_field}")
            if (
                isinstance(suite_not_applicable.get("review_requirement"), str)
                and review_requirement
                and suite_not_applicable.get("review_requirement") != review_requirement
            ):
                missing_fields.append("fields.suite_not_applicable.review_requirement")
    elif "suite_not_applicable" in fields and suite_not_applicable not in (None, {}, ""):
        missing_fields.append("fields.suite_not_applicable")

    if governance_intensity == "light" and change_class in GOVERNANCE_HIGH_RISK_CHANGE_CLASSES:
        missing_fields.append("fields.change_class")
        missing_fields.append("fields.governance_intensity")
    if governance_intensity == "light":
        if change_class not in GOVERNANCE_LITE_ALLOWED_CHANGE_CLASSES:
            missing_fields.append("fields.change_class")
        if change_class in GOVERNANCE_LITE_NOT_APPLICABLE_CHANGE_CLASSES and suite_path != GOVERNANCE_LITE_ALLOWED_SUITE_PATH:
            missing_fields.append("fields.suite_path")
        if change_class in GOVERNANCE_LITE_MINIMAL_SUITE_CHANGE_CLASSES and suite_path != "minimal":
            missing_fields.append("fields.suite_path")
        if review_requirement != "current_head_review_required":
            missing_fields.append("fields.review_requirement")
        if fact_chain_required is not True:
            missing_fields.append("fields.fact_chain_required")
        if release_judgment != GOVERNANCE_LITE_REQUIRED_RELEASE_JUDGMENT:
            missing_fields.append("fields.release_judgment")
    if release_judgment == "deferred_release_judgment_blocking":
        missing_fields.append("fields.release_judgment")
    return dedupe_strings(missing_fields)

def validate_pr_metadata_envelope(
    *,
    envelope: Any,
    field: dict[str, Any],
    surface: str,
    block_locator: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    contract_id = str(field.get("id") or "")
    machine_carrier = field.get("machine_carrier") if isinstance(field.get("machine_carrier"), dict) else {}
    marker = str(machine_carrier.get("marker") or "loom:repo-pr-metadata")
    authority_locator = field.get("authority_locator") if isinstance(field.get("authority_locator"), str) else None
    source_range_or_hash = (
        machine_carrier.get("source_range_or_hash")
        if isinstance(machine_carrier.get("source_range_or_hash"), str)
        else None
    )
    expected_schema = (
        machine_carrier.get("schema_version")
        if isinstance(machine_carrier.get("schema_version"), str) and machine_carrier.get("schema_version")
        else PR_METADATA_MACHINE_SCHEMA
    )
    diagnostics: list[dict[str, Any]] = []
    if not isinstance(envelope, dict):
        diagnostics.append(
            pr_metadata_diagnostic(
                contract_id=contract_id,
                marker=marker,
                reason="machine block JSON must decode to an object",
                source_locator=authority_locator,
                source_range_or_hash=source_range_or_hash,
                expected_schema=expected_schema,
                block_locator=block_locator,
                parse_error="decoded JSON is not an object",
                expected_surface=surface,
            )
        )
        return None, diagnostics
    if envelope.get("metadata_contract_id") != contract_id or envelope.get("surface") != surface:
        return None, []

    missing_fields: list[str] = []
    if envelope.get("schema_version") != expected_schema:
        missing_fields.append("schema_version")
    fields = envelope.get("fields")
    if not isinstance(fields, dict):
        missing_fields.append("fields")
        fields = {}
    source = envelope.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("rendered_hash"), str) or not source.get("rendered_hash"):
        missing_fields.append("source.rendered_hash")
    parser_version = envelope.get("parser_version")
    unsupported_parser_version = False
    if not isinstance(parser_version, str) or not parser_version:
        missing_fields.append("parser_version")
    elif parser_version not in PR_METADATA_SUPPORTED_PARSER_VERSIONS:
        missing_fields.append("parser_version")
        unsupported_parser_version = True
    required_fields = machine_carrier.get("required_fields")
    if isinstance(required_fields, list):
        for required_field in required_fields:
            if isinstance(required_field, str) and required_field.strip():
                if contract_id == GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID and required_field == "head_sha":
                    continue
                if required_field not in fields or fields.get(required_field) in (None, ""):
                    missing_fields.append(f"fields.{required_field}")
    if contract_id == GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID and isinstance(fields, dict):
        missing_fields.extend(validate_governance_intensity_metadata_fields(fields))
        missing_fields = dedupe_strings(missing_fields)
    if missing_fields:
        diagnostics.append(
            pr_metadata_diagnostic(
                contract_id=contract_id,
                marker=marker,
                reason=(
                    f"unsupported parser_version: {parser_version}"
                    if unsupported_parser_version
                    else "machine block is missing or violates required envelope or repo-specific fields"
                ),
                source_locator=authority_locator,
                source_range_or_hash=source_range_or_hash,
                expected_schema=expected_schema,
                block_locator=block_locator,
                missing_fields=missing_fields,
                expected_surface=surface,
            )
        )
        return None, diagnostics
    normalized = {
        "metadata_contract_id": contract_id,
        "surface": surface,
        "schema_version": envelope.get("schema_version"),
        "fields": fields,
        "source": source,
        "parser_version": envelope.get("parser_version"),
        "block_locator": block_locator,
    }
    return normalized, []

def pr_metadata_contract_preflight(
    *,
    field: dict[str, Any],
    body: str | None,
    surface: str,
    expected_item: str | None = None,
    expected_head_sha: str | None = None,
    expected_branch: str | None = None,
    owner: str | None = None,
    repo: str | None = None,
) -> dict[str, Any]:
    contract_id = str(field.get("id") or "unknown")
    candidate_surfaces = pr_metadata_candidate_contract_surfaces(field, surface)
    effective_surface = candidate_surfaces[-1]
    machine_carrier = field.get("machine_carrier") if isinstance(field.get("machine_carrier"), dict) else {}
    marker = str(machine_carrier.get("marker") or "loom:repo-pr-metadata")
    migration_mode = str(machine_carrier.get("migration_mode") or "advisory_legacy")
    authority_locator = field.get("authority_locator") if isinstance(field.get("authority_locator"), str) else None
    source_range_or_hash = (
        machine_carrier.get("source_range_or_hash")
        if isinstance(machine_carrier.get("source_range_or_hash"), str)
        else None
    )
    expected_schema = (
        machine_carrier.get("schema_version")
        if isinstance(machine_carrier.get("schema_version"), str) and machine_carrier.get("schema_version")
        else PR_METADATA_MACHINE_SCHEMA
    )
    required_fields = [
        required_field
        for required_field in machine_carrier.get("required_fields", [])
        if isinstance(required_field, str) and required_field.strip()
    ]
    base = {
        "metadata_contract_id": contract_id,
        "surface": surface,
        "effective_carrier_surface": effective_surface,
        "marker": marker,
        "required_fields": required_fields,
        "migration_mode": migration_mode,
        "schema_version": expected_schema,
        "authority_locator": authority_locator,
        "source_range_or_hash": source_range_or_hash,
        "parser_version": PR_METADATA_PARSER_VERSION,
        "diagnostics": [],
        "envelope": None,
    }
    if not isinstance(body, str):
        diagnostic = pr_metadata_diagnostic(
            contract_id=contract_id,
            marker=marker,
            reason="PR body is unavailable for metadata preflight",
            source_locator=authority_locator,
            source_range_or_hash=source_range_or_hash,
            expected_schema=expected_schema,
            missing_fields=["pr.body"],
            expected_surface=effective_surface,
        )
        result = "block" if migration_mode == "required" else "pass"
        return {
            **base,
            "result": result,
            "summary": (
                "required PR metadata machine block is absent because the PR body is unavailable."
                if result == "block"
                else "PR body is unavailable; legacy migration mode leaves metadata preflight advisory."
            ),
            "missing_inputs": ["PR body metadata machine block"] if result == "block" else [],
            "fallback_to": "update_pr_body" if result == "block" else None,
            "diagnostics": [diagnostic],
            "legacy_mode": result == "pass",
        }

    blocks = pr_metadata_html_comment_blocks(body, marker)
    if not blocks:
        diagnostic = pr_metadata_diagnostic(
            contract_id=contract_id,
            marker=marker,
            reason="PR body does not contain the declared metadata machine block",
            source_locator=authority_locator,
            source_range_or_hash=source_range_or_hash,
            expected_schema=expected_schema,
            missing_fields=["metadata_block"],
            expected_surface=effective_surface,
        )
        result = "block" if migration_mode == "required" else "pass"
        return {
            **base,
            "result": result,
            "summary": (
                "required PR metadata machine block is absent."
                if result == "block"
                else "PR metadata machine block is absent; legacy migration mode remains advisory."
            ),
            "missing_inputs": [f"PR metadata machine block missing: {contract_id}"] if result == "block" else [],
            "fallback_to": "update_pr_body" if result == "block" else None,
            "diagnostics": [diagnostic],
            "legacy_mode": result == "pass",
        }

    diagnostics: list[dict[str, Any]] = []
    for block in blocks:
        try:
            envelope = json.loads(block["raw"])
        except json.JSONDecodeError as exc:
            diagnostics.append(
                    pr_metadata_diagnostic(
                        contract_id=contract_id,
                        marker=marker,
                        reason="metadata machine block JSON is malformed",
                        source_locator=authority_locator,
                        source_range_or_hash=source_range_or_hash,
                        expected_schema=expected_schema,
                        block_locator=block["locator"],
                        parse_error=exc.msg,
                        expected_surface=effective_surface,
                    )
                )
            continue
        normalized = None
        envelope_diagnostics: list[dict[str, Any]] = []
        matched_surface = effective_surface
        for candidate_surface in candidate_surfaces:
            candidate_normalized, candidate_diagnostics = validate_pr_metadata_envelope(
                envelope=envelope,
                field=field,
                surface=candidate_surface,
                block_locator=block["locator"],
            )
            if candidate_normalized is not None:
                normalized = candidate_normalized
                matched_surface = candidate_surface
                envelope_diagnostics = candidate_diagnostics
                break
            envelope_diagnostics.extend(candidate_diagnostics)
        diagnostics.extend(envelope_diagnostics)
        if normalized is not None:
            binding_missing: list[str] = []
            if contract_id == GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID:
                normalized_fields = normalized.get("fields") if isinstance(normalized.get("fields"), dict) else {}
                body_locator = pr_body_field_value(body, "Work Item")
                normalized_body_locator = work_item_locator_for_metadata(body_locator, None, owner, repo)
                authoritative_locator = work_item_locator_for_metadata(expected_item, None, owner, repo)
                expected_bindings = {
                    "work_item_locator": authoritative_locator,
                }
                body_bindings = {
                    "work_item_locator": normalized_body_locator,
                }
                carrier_locator = normalized_fields.get("work_item_locator")
                if work_item_locator_for_metadata(
                    carrier_locator if isinstance(carrier_locator, str) else None,
                    None,
                    owner,
                    repo,
                ) != carrier_locator:
                    binding_missing.append("fields.work_item_locator")
                if body_locator and normalized_body_locator is None:
                    binding_missing.append("fields.work_item_locator")
                if expected_item and authoritative_locator is None:
                    binding_missing.append("fields.work_item_locator")
                for field_name, expected_value in expected_bindings.items():
                    carrier_value = normalized_fields.get(field_name)
                    if isinstance(expected_value, str) and expected_value and carrier_value != expected_value:
                        binding_missing.append(f"fields.{field_name}")
                for field_name, body_value in body_bindings.items():
                    carrier_value = normalized_fields.get(field_name)
                    if isinstance(body_value, str) and body_value and carrier_value != body_value:
                        binding_missing.append(f"fields.{field_name}")
                if binding_missing:
                    diagnostics.append(
                        pr_metadata_diagnostic(
                            contract_id=contract_id,
                            marker=marker,
                            reason="governance metadata carrier binding does not match the typed PR Work Item locator",
                            source_locator=authority_locator,
                            source_range_or_hash=source_range_or_hash,
                            expected_schema=expected_schema,
                            block_locator=block["locator"],
                            missing_fields=dedupe_strings(binding_missing),
                            expected_surface=matched_surface,
                        )
                    )
                    return {
                        **base,
                        "effective_carrier_surface": matched_surface,
                        "result": "block",
                        "summary": "PR metadata machine block is present but its governance binding conflicts with authoritative Work Item input.",
                        "missing_inputs": [f"PR metadata machine block invalid: {contract_id}"],
                        "fallback_to": "update_pr_body",
                        "diagnostics": diagnostics,
                        "envelope": None,
                        "legacy_mode": False,
                    }
            return {
                **base,
                "effective_carrier_surface": matched_surface,
                "result": "pass",
                "summary": "PR metadata machine block is parseable and contains the required repo-specific fields.",
                "missing_inputs": [],
                "fallback_to": None,
                "diagnostics": diagnostics,
                "envelope": normalized,
                "legacy_mode": False,
            }

    if diagnostics:
        return {
            **base,
            "result": "block",
            "summary": "PR metadata machine block is present but not parseable or complete.",
            "missing_inputs": [f"PR metadata machine block invalid: {contract_id}"],
            "fallback_to": "update_pr_body",
            "diagnostics": diagnostics,
            "legacy_mode": False,
        }
    diagnostic = pr_metadata_diagnostic(
        contract_id=contract_id,
        marker=marker,
        reason="PR metadata machine blocks did not match the expected contract id and effective carrier surface",
        source_locator=authority_locator,
        source_range_or_hash=source_range_or_hash,
        expected_schema=expected_schema,
        missing_fields=["metadata_contract_id", "surface"],
        expected_surface=effective_surface,
    )
    result = "block" if migration_mode == "required" else "pass"
    return {
        **base,
        "result": result,
        "summary": (
            "required PR metadata machine block for this contract and surface is absent."
            if result == "block"
            else "PR metadata machine block for this contract and surface is absent; legacy migration mode remains advisory."
        ),
        "missing_inputs": [f"PR metadata machine block missing: {contract_id}"] if result == "block" else [],
        "fallback_to": "update_pr_body" if result == "block" else None,
        "diagnostics": [diagnostic],
        "legacy_mode": result == "pass",
    }

def pr_metadata_preflight_payload(
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
    pr_payload: dict[str, Any] | None = None,
    effective_pr: int | None = None,
    governance_surface: dict[str, Any] | None = None,
    expected_item: str | None = None,
    expected_head_sha: str | None = None,
    expected_branch: str | None = None,
    issue_number: int | None = None,
) -> dict[str, Any]:
    governance_surface = governance_surface or build_governance_surface(target_root)
    detected_owner, detected_repo = detect_github_repo(target_root)
    locator_owner, locator_repo = owner or detected_owner, repo_name or detected_repo
    fields, contract_errors, source_locator = metadata_contract_raw_fields(target_root, governance_surface)
    applicable_contracts = applicable_pr_metadata_contracts(fields, surface=surface)
    missing_inputs: list[str] = []
    if contract_errors:
        missing_inputs.extend(str(message) for message in contract_errors)

    body_artifact, body_errors = load_optional_text_fixture(target_root, body_file, label="PR body file")
    compare_body_artifact, compare_body_errors = load_optional_text_fixture(
        target_root,
        compare_body_file,
        label="post-edit PR body file",
    )
    missing_inputs.extend(str(message) for message in body_errors)
    missing_inputs.extend(str(message) for message in compare_body_errors)
    if compare_body_file and not body_file:
        missing_inputs.append("--compare-body-file requires --body-file")

    pr_errors: list[str] = []
    inferences: list[dict[str, Any]] = []
    needs_pr_payload_for_body = body_artifact is None and compare_body_artifact is None
    if applicable_contracts and pr_payload is None and not contract_errors and (needs_pr_payload_for_body or pr_payload_file is not None):
        pr_payload, effective_pr, pr_errors, inferences = load_pr_payload_for_gate(
            target_root=target_root,
            owner=owner or detected_owner,
            repo_name=repo_name or detected_repo,
            pr_number=pr_number,
            head_sha=head_sha,
            branch_name=branch_name,
            pr_payload_file=pr_payload_file,
        )
        missing_inputs.extend(f"pr: {message}" for message in pr_errors)

    body = compare_body_artifact if compare_body_artifact is not None else body_artifact
    if body is None:
        body = pr_payload.get("body") if isinstance(pr_payload, dict) else None
    body_artifact_result = pr_metadata_body_artifact_payload(
        body_file=body_file,
        body=body_artifact,
        compare_body_file=compare_body_file,
        compare_body=compare_body_artifact,
        applicable_contracts=applicable_contracts,
    )
    if isinstance(body_artifact_result, dict):
        missing_inputs.extend(str(message) for message in body_artifact_result.get("missing_inputs", []))
    authoritative_item, authority_errors = authoritative_work_item_locator_for_metadata(
        target_root,
        expected_item,
        issue_number,
        locator_owner,
        locator_repo,
    )
    missing_inputs.extend(authority_errors)
    if expected_item and authoritative_item is None and not authority_errors:
        missing_inputs.append(
            "authoritative Work Item locator is unavailable from explicit issue authority or the Work Item carrier"
        )
    pr_head = pr_payload.get("headRefOid") if isinstance(pr_payload, dict) else head_sha
    pr_branch = pr_payload.get("headRefName") if isinstance(pr_payload, dict) else branch_name
    contract_results = [
        pr_metadata_contract_preflight(
            field=field,
            body=body if isinstance(body, str) else None,
            surface=surface,
            expected_item=authoritative_item,
            expected_branch=expected_branch or (pr_branch if isinstance(pr_branch, str) and pr_branch else None),
            owner=locator_owner,
            repo=locator_repo,
        )
        for field in applicable_contracts
    ]
    for contract_result in contract_results:
        if contract_result.get("result") == "block":
            for message in contract_result.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(str(message))

    safe_repair_actions: list[dict[str, Any]] = []
    if issue_number is not None and isinstance(body, str) and not pr_metadata_body_mentions_issue(body, issue_number):
        issue_reference = pr_metadata_issue_reference(issue_number)
        missing_inputs.append(f"PR body is missing Issue backlink: {issue_reference}")
        repair_action = pr_metadata_issue_backlink_repair_action(
            issue_number=issue_number,
            pr_number=effective_pr or pr_number,
            surface=surface,
            body_file=body_file,
            compare_body_file=compare_body_file,
            contract_results=contract_results,
            host_readback_available=isinstance(pr_payload, dict) or compare_body_artifact is not None,
        )
        if repair_action is not None:
            safe_repair_actions.append(repair_action)

    result = "pass" if not missing_inputs else "block"
    if contract_errors:
        summary = "repo companion metadata contract is incomplete or unreadable."
    elif not applicable_contracts:
        summary = "no repo-specific PR metadata machine preflight is declared for this surface."
    elif result == "pass":
        summary = "repo-specific PR metadata machine preflight passed or is in advisory legacy migration mode."
    else:
        summary = "repo-specific PR metadata machine preflight found blocking parser diagnostics."
    return {
        "command": "pr-metadata",
        "operation": "preflight",
        "schema_version": PR_METADATA_PREFLIGHT_SCHEMA,
        "surface": surface,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": "update_pr_body" if result == "block" and not contract_errors else "adoption" if result == "block" else None,
        "source_locator": source_locator,
        "metadata_contracts": contract_results,
        "governance_intensity_carrier": next(
            (
                {
                    "metadata_contract_id": contract_result.get("metadata_contract_id"),
                    "surface": contract_result.get("surface"),
                    "result": contract_result.get("result"),
                    "envelope": contract_result.get("envelope"),
                }
                for contract_result in contract_results
                if contract_result.get("metadata_contract_id") == GOVERNANCE_INTENSITY_METADATA_CONTRACT_ID
            ),
            None,
        ),
        "diagnostics": [
            diagnostic
            for contract_result in contract_results
            for diagnostic in contract_result.get("diagnostics", [])
            if isinstance(diagnostic, dict)
        ],
        "pr": {
            "number": effective_pr,
            "head_sha": pr_payload.get("headRefOid") if isinstance(pr_payload, dict) else head_sha,
            "has_body": isinstance(body, str),
        },
        "body_artifact": body_artifact_result,
        "inferences": inferences,
        "safe_repair_actions": safe_repair_actions,
        "repair_plan": safe_repair_actions,
    }

def gate_freeze_file_binding(target_root: Path, relative: str, *, label: str) -> dict[str, Any]:
    path, errors = resolve_artifact_read_path(target_root, relative, label=label)
    binding: dict[str, Any] = {
        "label": label,
        "locator": relative,
        "result": "block",
        "sha256": None,
        "size_bytes": None,
        "missing_inputs": [],
    }
    if errors:
        binding["missing_inputs"] = errors
        return binding
    assert path is not None
    if not path.exists() or not path.is_file():
        binding["missing_inputs"] = [f"{label} points to a missing file: {relative}"]
        return binding
    try:
        data = path.read_bytes()
    except OSError as exc:
        binding["missing_inputs"] = [f"failed to read {relative}: {exc.strerror or exc}"]
        return binding
    binding["result"] = "pass"
    binding["sha256"] = hashlib.sha256(data).hexdigest()
    binding["size_bytes"] = len(data)
    return binding

def gate_freeze_command_surface(context: dict[str, Any]) -> dict[str, Any]:
    required = {"gate-freeze-check", "gate-freeze-write"}
    errors: list[str] = []
    for loom_cli in suite_validate_command_candidates(context):
        completed = subprocess.run(
            [sys.executable, str(loom_cli), "help", "--internal-capabilities", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            errors.append(f"{loom_cli}: internal capability readback did not emit JSON")
            continue
        observed = set(payload.get("capabilities", []))
        if completed.returncode == 0 and payload.get("mutates") is False and required.issubset(observed):
            return {
                "result": "pass",
                "summary": "hidden gate freeze compatibility capabilities passed read-only dispatch readback.",
                "source_locator": str(loom_cli),
                "required_commands": sorted(required),
                "missing_inputs": [],
            }
        errors.append(f"{loom_cli}: unavailable hidden compatibility capabilities: {', '.join(sorted(required - observed))}")
    return {
        "result": "block",
        "summary": "hidden gate freeze compatibility commands are unavailable.",
        "source_locator": "tools/loom.py",
        "required_commands": sorted(required),
        "missing_inputs": errors or ["hidden gate freeze compatibility commands unavailable"],
    }

def gate_freeze_review_binding(context: dict[str, Any], *, head_sha: str | None, surface: str = "merge_ready") -> dict[str, Any]:
    review_entry = context.get("review_entry")
    review_relative = str(review_entry) if isinstance(review_entry, str) and review_entry else None
    review_record, review_path, review_errors = load_review_record(
        context["target_root"],
        context["item_id"],
        review_file=review_relative,
    )
    binding: dict[str, Any] = {
        "schema_version": "loom-gate-freeze-review-binding/v1",
        "result": "block",
        "locator": review_path,
        "source_locator": review_path,
        "review_record": review_record,
        "decision": None,
        "kind": None,
        "reviewed_head": None,
        "current_head": git_head_sha(context["target_root"]),
        "pr_head": head_sha,
        "binding_status": "unknown",
        "semantic_review_disposition": None,
        "carrier_only_closeout_review": None,
        "head_binding": None,
        "missing_inputs": [],
        "next_action": "run authored Loom review for the current PR head before freezing gate inputs.",
    }
    if review_errors:
        binding["missing_inputs"] = review_errors
        return binding
    if review_record is None:
        binding["missing_inputs"] = [f"review artifact missing: {review_path}"]
        return binding
    binding["decision"] = review_record.get("decision")
    binding["kind"] = review_record.get("kind")
    binding["reviewed_head"] = review_record.get("reviewed_head")
    normalized_checkpoint = normalize_checkpoint(str(context.get("current_checkpoint", "")))
    terminal_closeout_surface = surface == "closeout" and normalized_checkpoint in TERMINAL_CHECKPOINTS
    allowed_paths = (
        allowed_terminal_closeout_carrier_paths(context, review_path)
        if terminal_closeout_surface
        else allowed_post_review_carrier_paths(context, review_path)
    )
    head_binding, head_errors = review_head_binding_for_head(
        context["target_root"],
        reviewed_head=review_record.get("reviewed_head") if isinstance(review_record.get("reviewed_head"), str) else None,
        target_head=head_sha or git_head_sha(context["target_root"]),
        allowed_paths=allowed_paths,
    )
    binding["head_binding"] = head_binding
    binding["current_head"] = head_binding.get("current_head")
    binding["pr_head"] = head_sha or head_binding.get("current_head")
    binding["binding_status"] = head_binding.get("status")
    if terminal_closeout_surface:
        disposition, disposition_errors = carrier_only_closeout_review_payload(
            review_record=review_record,
            review_path=review_path,
            pr_head=head_sha or head_binding.get("current_head"),
            head_binding=head_binding,
            current_validation_summary=context.get("latest_validation_summary"),
        )
        binding["carrier_only_closeout_review"] = disposition
    else:
        disposition, disposition_errors = semantic_review_disposition_payload(
            review_record=review_record,
            review_path=review_path,
            pr_head=head_sha or head_binding.get("current_head"),
            head_binding=head_binding,
            current_validation_summary=context.get("latest_validation_summary"),
        )
        binding["semantic_review_disposition"] = disposition
    binding["surface"] = surface
    binding["allowed_paths_policy"] = (
        "terminal closeout carrier paths only; requires terminal checkpoint"
        if terminal_closeout_surface
        else "post-review carrier paths only"
    )
    binding["missing_inputs"] = [*head_errors, *disposition_errors]
    if review_record.get("decision") != "allow":
        binding["missing_inputs"].append("review artifact decision is not allow")
    if review_record.get("kind") not in IMPLEMENTATION_REVIEW_KINDS:
        binding["missing_inputs"].append("review artifact kind is not an implementation review")
    binding["result"] = "pass" if not binding["missing_inputs"] else "block"
    binding["next_action"] = gate_freeze_review_binding_next_action(binding)
    return binding

def gate_freeze_review_binding_next_action(binding: dict[str, Any]) -> str | None:
    if binding.get("result") == "pass":
        if binding.get("binding_status") == "carrier-only":
            return "carrier-only drift is allowed for this review binding; refresh carrier evidence if operator-facing metadata must be repinned."
        if binding.get("binding_status") in {"generated-only", "carrier-and-generated-only"}:
            actions = (
                binding.get("head_binding", {}).get("generated_only_validation_actions", [])
                if isinstance(binding.get("head_binding"), dict)
                else []
            )
            if actions:
                first_action = actions[0].get("action") if isinstance(actions[0], dict) else None
                if isinstance(first_action, str) and first_action:
                    return f"generated-only drift is allowed after generated surface validation; run `{first_action}` if evidence must be refreshed."
            return "generated-only drift is allowed after generated surface validation."
        return None

    messages = [str(message).lower() for message in binding.get("missing_inputs", []) if str(message).strip()]
    head_binding = binding.get("head_binding") if isinstance(binding.get("head_binding"), dict) else {}
    disallowed_paths = head_binding.get("disallowed_paths") if isinstance(head_binding, dict) else None
    if isinstance(disallowed_paths, list) and disallowed_paths:
        return "rerun authored Loom review for the current PR head; disallowed post-review paths changed."
    if any("validation summary" in message for message in messages):
        return "refresh validation evidence and rerun authored Loom review for the current recovery summary."
    if any("reviewed_head" in message or "target head" in message or "head comparison failed" in message for message in messages):
        return "fix the review record or PR head binding, then rerun gate freeze."
    if any("decision" in message or "kind" in message or "review artifact missing" in message for message in messages):
        return "run or refresh authored Loom implementation review for the current PR head."
    if any("semantic_review_disposition" in message for message in messages):
        return "fix the authored review record semantic_review_disposition, then rerun gate freeze."
    if any("carrier_only_closeout_review" in message for message in messages):
        return "fix the authored closeout carrier-only review record, then rerun gate freeze."
    return "refresh review binding inputs and rerun `loom gate freeze check --target <repo> --json`."

def gate_freeze_shadow_binding(target_root: Path, governance_surface: dict[str, Any]) -> dict[str, Any]:
    repo_interop = governance_surface.get("repo_interop")
    reports = [
        shadow_parity_report(repo_interop, target_root=target_root, surface=surface)
        for surface in SHADOW_PARITY_SURFACES
    ]
    missing_inputs: list[str] = []
    for report in reports:
        if report.get("result") == "match":
            continue
        surface = str(report.get("surface") or "unknown")
        missing_inputs.append(f"shadow parity {surface}: {report.get('summary')}")
        for message in report.get("missing_inputs", []):
            missing_inputs.append(f"shadow parity {surface}: {message}")
    return {
        "result": "pass" if not missing_inputs else "block",
        "summary": "shadow parity matches across all freeze surfaces." if not missing_inputs else "shadow parity has missing or mismatched freeze inputs.",
        "reports": reports,
        "missing_inputs": dedupe_strings(missing_inputs),
    }

def gate_freeze_shadow_locator_index(target_root: Path, governance_surface: dict[str, Any]) -> tuple[dict[str, dict[str, str]], list[str]]:
    repo_interop = governance_surface.get("repo_interop")
    interop_payload, interop_errors = load_repo_interop_contract(repo_interop, target_root=target_root)
    if interop_errors or not isinstance(interop_payload, dict):
        return {}, interop_errors or ["repo interop contract is unreadable"]
    shadow_surfaces = interop_payload.get("shadow_surfaces")
    if not isinstance(shadow_surfaces, dict):
        return {}, ["repo interop contract must expose shadow_surfaces"]

    locators: dict[str, dict[str, str]] = {}
    for surface, entry in shadow_surfaces.items():
        if not isinstance(surface, str) or not isinstance(entry, dict):
            continue
        for side, key in (("loom", "loom_locator"), ("repo", "repo_locator")):
            locator = entry.get(key)
            if isinstance(locator, str) and locator.strip():
                locators[locator.strip()] = {"surface": surface, "side": side}
    return locators, []

def gate_freeze_shadow_freshness_binding(target_root: Path, governance_surface: dict[str, Any]) -> dict[str, Any]:
    locator_index, locator_errors = gate_freeze_shadow_locator_index(target_root, governance_surface)
    records: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    if locator_errors:
        missing_inputs.extend(locator_errors)

    for action in refresh_shadow_evidence_actions(target_root):
        if action.get("kind") != "shadow-evidence":
            continue
        relative = str(action.get("path") or "")
        locator = locator_index.get(relative, {})
        status = str(action.get("status") or "unknown")
        current_sha = action.get("current_source_sha256") if isinstance(action.get("current_source_sha256"), dict) else None
        expected_sha = action.get("expected_source_sha256") if isinstance(action.get("expected_source_sha256"), dict) else None
        action_missing = [str(message) for message in action.get("missing_inputs", [])]
        if status == "current":
            freshness = "present"
            drift_kind = None
            refreshable = False
            next_action = None
        elif status == "refresh-needed":
            freshness = "stale"
            drift_kind = "shadow_source_hash_drift"
            refreshable = True
            next_action = "python3 .loom/bin/loom_flow.py carrier refresh --target <repo> --write"
            missing_inputs.append(f"shadow source hash drift: {relative}")
        else:
            freshness = "missing" if action_missing else "conflict"
            drift_kind = "shadow_source_hash_unreadable"
            refreshable = False
            next_action = "restore readable declared shadow source files, then rerun gate freeze."
            missing_inputs.extend(action_missing or [f"shadow source hash freshness could not be evaluated: {relative}"])
        records.append(
            {
                "path": relative,
                "surface": locator.get("surface", "unknown"),
                "side": locator.get("side", "unknown"),
                "freshness": freshness,
                "drift_kind": drift_kind,
                "refreshable": refreshable,
                "next_action": next_action,
                "current_source_sha256": current_sha,
                "expected_source_sha256": expected_sha,
                "missing_inputs": action_missing,
            }
        )

    missing_inputs = dedupe_strings(missing_inputs)
    result = "pass" if not missing_inputs else "block"
    return {
        "schema_version": "loom-gate-freeze-shadow-freshness/v1",
        "result": result,
        "summary": (
            "shadow source hashes are fresh for declared freeze surfaces."
            if result == "pass"
            else "shadow source hashes are stale or unreadable for declared freeze surfaces."
        ),
        "source_locator": ".loom/shadow/*.json",
        "records": records,
        "missing_inputs": missing_inputs,
        "failure_kind": "shadow_source_hash_drift"
        if any(record.get("drift_kind") == "shadow_source_hash_drift" for record in records)
        else "missing_or_stale_gate_input",
        "category": "drift",
        "severity": "block",
        "subject": "shadow_freshness",
        "why_blocking": "hosted admission cannot consume shadow evidence until source hashes match their declared inputs.",
        "fallback_to": "carrier_refresh",
        "refresh_suggestion": "python3 .loom/bin/loom_flow.py carrier refresh --target <repo> --write"
        if any(record.get("refreshable") for record in records)
        else None,
        "next_action": "python3 .loom/bin/loom_flow.py carrier refresh --target <repo> --write"
        if any(record.get("refreshable") for record in records)
        else "restore readable declared shadow source files, then rerun gate freeze."
        if result == "block"
        else None,
    }

def gate_freeze_carrier_refresh_binding(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    *,
    surface: str = "merge_ready",
) -> dict[str, Any]:
    dry_run_payload = carrier_refresh_payload(target_root, output_relative, expected_item, dry_run=True, surface=surface)
    refresh_command = "python3 .loom/bin/loom_flow.py carrier refresh --target <repo> --write"
    if surface != "merge_ready":
        refresh_command = f"{refresh_command} --surface {surface}"
    refresh_needed = [
        action for action in dry_run_payload.get("refresh_needed", []) if isinstance(action, dict)
    ]
    missing_inputs = [str(message) for message in dry_run_payload.get("missing_inputs", [])]
    for action in refresh_needed:
        relative = action.get("path")
        if relative:
            missing_inputs.append(f"carrier refresh pending: {relative}")
    missing_inputs = dedupe_strings(missing_inputs)
    result = "pass" if dry_run_payload.get("result") == "pass" and not refresh_needed and not missing_inputs else "block"
    return {
        "schema_version": "loom-gate-freeze-carrier-refresh/v1",
        "result": result,
        "summary": (
            "carrier refresh dry-run found no pending carrier updates."
            if result == "pass"
            else "carrier refresh dry-run found stale or blocking carrier inputs."
        ),
        "source_locator": ".loom/bootstrap/init-result.json",
        "dry_run_payload": dry_run_payload,
        "refresh_needed": refresh_needed,
        "missing_inputs": missing_inputs,
        "failure_kind": "carrier_refresh_stale" if refresh_needed else "missing_or_stale_gate_input",
        "category": "stale",
        "severity": "block",
        "subject": "carrier_refresh",
        "why_blocking": "hosted admission cannot trust a frozen snapshot while carrier refresh dry-run reports pending updates.",
        "fallback_to": "carrier_refresh",
        "refresh_suggestion": refresh_command
        if refresh_needed
        else None,
        "next_action": refresh_command
        if refresh_needed
        else dry_run_payload.get("fallback_to"),
    }

def gate_freeze_release_binding(pr_metadata_preflight: dict[str, Any] | None) -> dict[str, Any]:
    fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
    release_judgment = fields.get("release_judgment")
    if release_judgment in GOVERNANCE_RELEASE_JUDGMENT_VALUES:
        return {
            "result": "pass" if release_judgment != "deferred_release_judgment_blocking" else "block",
            "release_judgment": release_judgment,
            "source": "pr_metadata.governance_intensity_carrier.fields.release_judgment",
            "missing_inputs": [] if release_judgment != "deferred_release_judgment_blocking" else ["release judgment is deferred and blocking"],
        }
    return {
        "result": "block",
        "release_judgment": None,
        "source": "pr_metadata.governance_intensity_carrier.fields.release_judgment",
        "missing_inputs": ["release judgment metadata is missing"],
    }

def gate_freeze_pr_body_pin_next_action(body_file: str | None) -> str:
    body_file_arg = f" {shlex.quote(body_file)}" if body_file else " <rendered-pr-body.md>"
    return (
        f"re-run `gh pr edit --body-file{body_file_arg}`, read back the PR body into "
        "`--compare-body-file`, then rerun `loom gate freeze check --target <repo> --json`."
    )

def gate_freeze_pr_body_pin_binding(pr_metadata_preflight: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(pr_metadata_preflight, dict):
        return {
            "schema_version": "loom-gate-freeze-pr-body-pin/v1",
            "result": "not_applicable",
            "summary": "PR metadata preflight is unavailable, so PR body hash pinning is not available.",
            "source_locator": None,
            "rendered_body_sha256": None,
            "readback_body_sha256": None,
            "metadata_block_fingerprints": [],
            "missing_inputs": [],
            "next_action": None,
        }
    body_artifact = pr_metadata_preflight.get("body_artifact")
    if not isinstance(body_artifact, dict):
        return {
            "schema_version": "loom-gate-freeze-pr-body-pin/v1",
            "result": "not_applicable",
            "summary": "No rendered PR body artifact was provided for freeze pinning.",
            "source_locator": None,
            "rendered_body_sha256": None,
            "readback_body_sha256": None,
            "metadata_block_fingerprints": [],
            "missing_inputs": [],
            "next_action": None,
        }

    body_file = body_artifact.get("body_file") if isinstance(body_artifact.get("body_file"), str) else None
    compare_body_file = (
        body_artifact.get("compare_body_file") if isinstance(body_artifact.get("compare_body_file"), str) else None
    )
    rendered_body_sha256 = (
        body_artifact.get("body_sha256") if isinstance(body_artifact.get("body_sha256"), str) else None
    )
    readback_body_sha256 = (
        body_artifact.get("compare_body_sha256")
        if isinstance(body_artifact.get("compare_body_sha256"), str)
        else None
    )
    comparisons = body_artifact.get("machine_block_comparisons")
    metadata_block_fingerprints = comparisons if isinstance(comparisons, list) else []
    machine_block_statuses = [
        str(entry.get("status"))
        for entry in metadata_block_fingerprints
        if isinstance(entry, dict) and entry.get("status") is not None
    ]
    machine_blocks_match = bool(machine_block_statuses) and all(status == "match" for status in machine_block_statuses)
    full_body_hash_match = (
        bool(rendered_body_sha256)
        and bool(readback_body_sha256)
        and rendered_body_sha256 == readback_body_sha256
    )
    full_body_hash_status = (
        "match"
        if full_body_hash_match
        else "metadata_blocks_match_full_body_diff"
        if rendered_body_sha256 and readback_body_sha256 and machine_blocks_match
        else "mismatch"
        if rendered_body_sha256 and readback_body_sha256
        else "not_compared"
    )
    missing_inputs: list[str] = []

    if body_artifact.get("result") == "block":
        missing_inputs.extend(str(message) for message in body_artifact.get("missing_inputs", []))
    if body_file and not compare_body_file:
        missing_inputs.append("post-edit PR body readback file is required for gate freeze PR body pinning")
    if rendered_body_sha256 and readback_body_sha256 and rendered_body_sha256 != readback_body_sha256 and not machine_blocks_match:
        missing_inputs.append("rendered PR body hash does not match GitHub readback PR body hash")
    if pr_metadata_preflight.get("result") == "block":
        for message in pr_metadata_preflight.get("missing_inputs", []):
            missing_inputs.append(f"PR metadata preflight: {message}")

    missing_inputs = dedupe_strings(missing_inputs)
    result = "pass" if not missing_inputs else "block"
    next_action = gate_freeze_pr_body_pin_next_action(body_file)
    return {
        "schema_version": "loom-gate-freeze-pr-body-pin/v1",
        "result": result,
        "summary": (
            "PR body rendered/readback metadata machine block fingerprints are pinned."
            if result == "pass"
            else "PR body rendered/readback hash or metadata carrier pinning is stale."
        ),
        "source_locator": body_file,
        "readback_locator": compare_body_file,
        "rendered_body_sha256": rendered_body_sha256,
        "readback_body_sha256": readback_body_sha256,
        "full_body_hash_status": full_body_hash_status,
        "metadata_block_fingerprints": metadata_block_fingerprints,
        "preflight_body_source": body_artifact.get("preflight_body_source"),
        "pr_metadata_result": pr_metadata_preflight.get("result"),
        "missing_inputs": missing_inputs,
        "fallback_to": "gh_pr_edit_body_file_readback" if result == "block" else None,
        "safe_update_strategy": body_artifact.get("safe_update_strategy"),
        "next_action": next_action if result == "block" else None,
    }

def gate_freeze_blocking_inputs(input_bindings: dict[str, Any]) -> list[dict[str, Any]]:
    blocking: list[dict[str, Any]] = []
    for key, binding in input_bindings.items():
        if not isinstance(binding, dict):
            continue
        result = binding.get("result")
        if result in {"pass", "not_applicable", "advisory"}:
            continue
        messages = binding.get("missing_inputs")
        if not isinstance(messages, list):
            messages = []
        failure_kind = str(binding.get("failure_kind") or "missing_or_stale_gate_input")
        blocking.append(
            {
                "id": f"{key}-not-ready",
                "input": key,
                "failure_kind": failure_kind,
                "category": binding.get("category") or "gate_failure",
                "kind": failure_kind,
                "severity": binding.get("severity") or "block",
                "subject": binding.get("subject") or key,
                "result": result or "block",
                "source_locator": binding.get("locator") or binding.get("source_locator"),
                "consumer_impact": binding.get("consumer_impact")
                or "hosted gate admission cannot trust a frozen snapshot until this input is refreshed.",
                "why_blocking": binding.get("why_blocking")
                or "hosted gate admission cannot trust a frozen snapshot until this input is refreshed.",
                "fallback_to": binding.get("fallback_to"),
                "evidence": binding.get("evidence")
                or binding.get("refresh_needed")
                or binding.get("records")
                or binding.get("reports"),
                "messages": [str(message) for message in messages],
                "next_action": binding.get("next_action")
                or "refresh the source input and rerun `loom gate freeze check --target <repo> --json`.",
            }
        )
    return blocking

def gate_freeze_refresh_suggestions(input_bindings: dict[str, Any]) -> list[str]:
    suggestions: list[str] = []
    for binding in input_bindings.values():
        if not isinstance(binding, dict) or binding.get("result") in {"pass", "not_applicable", "advisory"}:
            continue
        suggestion = binding.get("refresh_suggestion")
        if isinstance(suggestion, str) and suggestion.strip():
            suggestions.append(suggestion.strip())
        elif isinstance(suggestion, list):
            suggestions.extend(str(entry).strip() for entry in suggestion if str(entry).strip())
    return dedupe_strings(suggestions)

def failure_classifier_category(failure_kind: str, input_name: str) -> str:
    if failure_kind in FAILURE_CLASSIFIER_KIND_MAP:
        return FAILURE_CLASSIFIER_KIND_MAP[failure_kind]
    if input_name in FAILURE_CLASSIFIER_INPUT_MAP:
        return FAILURE_CLASSIFIER_INPUT_MAP[input_name]
    return "code_semantics"

def failure_classifier_payload(findings: list[dict[str, Any]]) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        failure_kind = str(finding.get("failure_kind") or finding.get("kind") or "code_semantics")
        input_name = str(finding.get("input") or finding.get("subject") or "")
        classifier = failure_classifier_category(failure_kind, input_name)
        next_action = FAILURE_CLASSIFIER_NEXT_ACTIONS[classifier]
        normalized.append(
            {
                "classifier": classifier,
                "failure_kind": failure_kind,
                "input": input_name,
                "result": finding.get("result") or "block",
                "severity": finding.get("severity") or "block",
                "evidence_locator": finding.get("source_locator"),
                "next_action": next_action,
                "messages": list(finding.get("messages") or []),
            }
        )
    return {
        "schema_version": FAILURE_CLASSIFIER_SCHEMA,
        "supported_classifiers": list(FAILURE_CLASSIFIER_CATEGORIES),
        "findings": normalized,
    }

def closeout_specific_gate_payload(
    *,
    mode: str,
    closeout_pr_allowed: bool,
    full_review_required: bool,
    blocking_inputs: list[dict[str, Any]],
    next_action: str | None = None,
    source: str = "closeout-freeze",
) -> dict[str, Any]:
    escalation_reasons: list[str] = []
    for blocking in blocking_inputs:
        if not isinstance(blocking, dict):
            continue
        reason = blocking.get("failure_kind") or blocking.get("kind") or blocking.get("input")
        if isinstance(reason, str) and reason.strip():
            escalation_reasons.append(reason.strip())
    if mode == "full":
        escalation_reasons.append("closeout_mode_full")
    escalation_reasons = dedupe_strings(escalation_reasons)
    result = "pass" if closeout_pr_allowed and not full_review_required else "block"
    if result == "pass":
        gate_next_action = next_action or "closeout_pr_allowed"
        verdict = "closeout_pr_allowed"
    else:
        gate_next_action = next_action or "run_full_review_or_resolve_closeout_gate_blockers"
        verdict = "full_review_required" if full_review_required else "resolve_closeout_gate_blockers"
    return {
        "schema_version": CLOSEOUT_SPECIFIC_GATE_SCHEMA,
        "source": source,
        "surface": "closeout",
        "mode": mode,
        "result": result,
        "verdict": verdict,
        "closeout_pr_allowed": closeout_pr_allowed,
        "full_review_required": full_review_required,
        "escalation_required": result != "pass",
        "escalation_reason": escalation_reasons[0] if escalation_reasons else None,
        "escalation_reasons": escalation_reasons,
        "blocking_inputs": blocking_inputs,
        "next_action": gate_next_action,
    }

def closeout_freeze_load_issue(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int | None,
    issue_payload_file: str | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    fixture, fixture_errors = load_optional_json_fixture(target_root, issue_payload_file, label="issue payload fixture")
    if fixture_errors:
        return None, fixture_errors
    if fixture is not None:
        return normalize_issue_fixture_payload(fixture)
    if issue_number is None:
        return None, ["closeout issue number is required for closeout freeze"]
    if not owner or not repo_name:
        return None, ["owner/repo is required for closeout issue readback"]
    return github_issue_payload(target_root, owner, repo_name, issue_number)

def closeout_freeze_load_pr(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    pr_number: int | None,
    pr_payload_file: str | None,
) -> tuple[dict[str, Any] | None, int | None, list[str]]:
    fixture, fixture_errors = load_optional_json_fixture(target_root, pr_payload_file, label="implementation PR payload fixture")
    if fixture_errors:
        return None, pr_number, fixture_errors
    if fixture is not None:
        payload, errors = normalize_pr_fixture_payload(fixture)
        inferred_pr = pr_number
        if inferred_pr is None and isinstance(payload, dict) and isinstance(payload.get("number"), int):
            inferred_pr = int(payload["number"])
        return payload, inferred_pr, errors
    if pr_number is None:
        return None, None, ["implementation PR number is required for closeout freeze"]
    if not owner or not repo_name:
        return None, pr_number, ["owner/repo is required for implementation PR readback"]
    payload, errors = github_pr_payload(target_root, owner, repo_name, pr_number)
    return payload, pr_number, errors

def closeout_freeze_target_contains_merge(
    target_root: Path,
    merge_commit_sha: str | None,
    target_branch: str,
    *,
    owner: str | None,
    repo_name: str | None,
) -> tuple[bool | None, list[str]]:
    if not isinstance(merge_commit_sha, str) or not merge_commit_sha:
        return None, ["implementation PR merge commit is missing"]
    if contains_merged_commit(target_root, merge_commit_sha, target_branch, owner=owner, repo_name=repo_name):
        return True, []
    return False, [f"target branch `{target_branch}` does not contain merge commit `{merge_commit_sha}`"]

def closeout_freeze_terminal_subject_binding(
    context: dict[str, Any],
    *,
    issue_number: int | None,
    issue_payload: dict[str, Any] | None,
    issue_errors: list[str],
    pr_payload: dict[str, Any] | None,
    pr_number: int | None,
    pr_errors: list[str],
    merge_commit: str | None,
    target_branch: str,
) -> dict[str, Any]:
    item_id = str(context["item_id"])
    missing_inputs: list[str] = []
    pr_body = pr_payload.get("body") if isinstance(pr_payload, dict) else None
    issue_text_parts: list[str] = []
    if isinstance(issue_payload, dict):
        for key in ("title", "body"):
            value = issue_payload.get(key)
            if isinstance(value, str):
                issue_text_parts.append(value)
    issue_text = "\n".join(issue_text_parts)

    if issue_errors:
        missing_inputs.extend(f"issue: {message}" for message in issue_errors)
    elif not isinstance(issue_payload, dict):
        missing_inputs.append("closeout issue payload is missing")
    else:
        payload_issue = issue_payload.get("number")
        if issue_number is None:
            missing_inputs.append("closeout issue number is missing")
        elif payload_issue != issue_number:
            missing_inputs.append(f"closeout issue payload number `{payload_issue}` does not match --issue `{issue_number}`")
        if issue_payload.get("state") != "CLOSED":
            missing_inputs.append("closeout issue is not closed")

    if pr_errors:
        missing_inputs.extend(f"implementation PR: {message}" for message in pr_errors)
    elif not isinstance(pr_payload, dict):
        missing_inputs.append("implementation PR payload is missing")
    else:
        payload_pr = pr_payload.get("number")
        if pr_number is not None and payload_pr != pr_number:
            missing_inputs.append(f"implementation PR payload number `{payload_pr}` does not match requested PR `{pr_number}`")
        if pr_payload.get("state") != "MERGED":
            missing_inputs.append("implementation PR is not merged")
        if not merge_commit:
            missing_inputs.append("implementation PR merge commit is missing")
        if pr_payload.get("baseRefName") != target_branch:
            missing_inputs.append(f"implementation PR baseRefName `{pr_payload.get('baseRefName')}` does not match target branch `{target_branch}`")
        body_work_item_locator = pr_body_field_value(pr_body, "Work Item")
        owner, repo = detect_github_repo(context["target_root"])
        typed_body_work_item = work_item_locator_for_metadata(body_work_item_locator, None, owner, repo)
        if typed_body_work_item != body_work_item_locator:
            missing_inputs.append("implementation PR body does not bind the canonical owner/repo/work_item/id locator")
        body_item = pr_work_item_from_body(pr_body)
        if body_item and body_item != item_id:
            missing_inputs.append(f"implementation PR body Work Item `{body_item}` does not match `{item_id}`")
    issue_ref = f"#{issue_number}" if issue_number is not None else None
    pr_ref = f"#{pr_number}" if pr_number is not None else None
    linked_by_pr_body = bool(issue_ref and isinstance(pr_body, str) and re.search(rf"(?<![A-Z0-9-]){re.escape(issue_ref)}(?![0-9])", pr_body))
    linked_by_issue_text = bool(
        issue_text
        and (
            re.search(rf"(?<![A-Z0-9-]){re.escape(item_id)}(?![A-Z0-9-])", issue_text)
            or (pr_ref and re.search(rf"(?<![A-Z0-9-]){re.escape(pr_ref)}(?![0-9])", issue_text))
        )
    )
    if issue_number is not None and not linked_by_pr_body and not linked_by_issue_text:
        missing_inputs.append("closeout issue and implementation PR are not explicitly linked by PR body, issue body, or issue title")

    return {
        "result": "pass" if not missing_inputs else "block",
        "missing_inputs": dedupe_strings(missing_inputs),
        "failure_kind": "closeout_terminal_subject_drift",
        "category": "gate_failure",
        "severity": "block",
        "subject": "terminal_subject",
        "source_locator": "issue/pr terminal readback",
        "why_blocking": "closeout freeze must bind the closed issue, merged implementation PR, Work Item, and target branch to the same terminal subject.",
        "fallback_to": "manual-reconciliation",
        "next_action": "re-read and align the closeout issue, implementation PR metadata, Work Item binding, and target branch before closeout freeze.",
    }

def closeout_allowed_paths(context: dict[str, Any]) -> set[str]:
    return allowed_terminal_closeout_carrier_paths(context, context["review_entry"])

def closeout_freeze_retained_review_binding(
    context: dict[str, Any],
    *,
    pr_payload: dict[str, Any] | None,
    merge_commit: str | None,
) -> dict[str, Any]:
    review_record, review_path, review_errors = load_review_record(context["target_root"], context["item_id"], context["review_entry"])
    target_head = None
    if isinstance(pr_payload, dict) and isinstance(pr_payload.get("headRefOid"), str):
        target_head = pr_payload.get("headRefOid")
    if not target_head:
        target_head = merge_commit
    missing_inputs: list[str] = []
    if review_record is None:
        missing_inputs.extend(review_errors or [f"missing review artifact: {review_path}"])
        return {
            "result": "block",
            "source_locator": review_path,
            "missing_inputs": dedupe_strings(missing_inputs),
            "failure_kind": "closeout_retained_review_unconsumable",
            "category": "gate_failure",
            "severity": "block",
            "subject": "retained_review",
            "why_blocking": "closeout freeze requires retained implementation review evidence for the merged implementation PR.",
            "fallback_to": "review",
            "next_action": "restore retained implementation review evidence before closeout freeze.",
        }

    head_binding, head_binding_errors = review_head_binding_for_head(
        context["target_root"],
        reviewed_head=review_record.get("reviewed_head"),
        target_head=target_head,
        allowed_paths=closeout_allowed_paths(context),
    )
    disposition, disposition_errors = semantic_review_disposition_payload(
        review_record=review_record,
        review_path=review_path,
        pr_head=target_head,
        head_binding=head_binding,
        current_validation_summary=context.get("latest_validation_summary"),
    )
    if review_record.get("decision") != "allow":
        missing_inputs.append("retained review decision is not allow")
    if review_record.get("kind") not in IMPLEMENTATION_REVIEW_KINDS:
        missing_inputs.append("retained review kind is not an implementation review")
    if disposition.get("consumable") is not True:
        missing_inputs.extend(disposition_errors or ["semantic_review_disposition is not consumable"])
    missing_inputs.extend(head_binding_errors)
    return {
        "result": "pass" if not missing_inputs else "block",
        "source_locator": review_path,
        "reviewed_head": review_record.get("reviewed_head"),
        "target_head": target_head,
        "decision": review_record.get("decision"),
        "kind": review_record.get("kind"),
        "semantic_review_disposition": disposition,
        "head_binding": head_binding,
        "missing_inputs": dedupe_strings(missing_inputs),
        "failure_kind": "closeout_retained_review_unconsumable",
        "category": "gate_failure",
        "severity": "block",
        "subject": "retained_review",
        "why_blocking": "closeout freeze requires retained implementation review evidence consumable by the merged implementation PR head.",
        "fallback_to": "review",
        "next_action": "rerun or repair retained implementation review evidence before closeout freeze.",
    }

def closeout_freeze_release_evidence_locator_from_body(body: str | None) -> str | None:
    if not isinstance(body, str):
        return None
    for line in body.splitlines():
        match = re.match(
            r"\s*(?:[-*]\s*)?"
            r"(?:release/no-release evidence(?: locator)?|no-release evidence(?: locator)?|"
            r"release evidence(?: locator)?|post-merge release evidence(?: locator)?|post-merge evidence(?: locator)?)"
            r"\s*:\s*(.+?)\s*$",
            line,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        locator = match.group(1).strip().strip("`")
        if locator and locator.lower() not in {"none", "n/a", "not_applicable", "not applicable", "pending"}:
            return locator
    return None

def closeout_freeze_evidence_locator_status(target_root: Path, locator: str | None) -> dict[str, Any]:
    if not locator:
        return {"status": "missing", "locator": None, "missing_inputs": ["release/no-release evidence locator is missing"]}
    if re.match(r"^[a-z][a-z0-9+.-]*://", locator, flags=re.IGNORECASE):
        return {"status": "present", "locator": locator, "source": "external-readback-locator", "missing_inputs": []}
    path, errors = resolve_repo_relative_path(target_root, locator, label="release/no-release evidence locator")
    if errors:
        return {"status": "invalid", "locator": locator, "missing_inputs": errors}
    if path is None or not path.exists():
        return {"status": "missing", "locator": locator, "missing_inputs": [f"release/no-release evidence locator `{locator}` is missing"]}
    return {"status": "present", "locator": locator, "source": "repo-readback-locator", "missing_inputs": []}

def closeout_freeze_release_binding(
    target_root: Path,
    context: dict[str, Any],
    pr_payload: dict[str, Any] | None,
    governance_surface: dict[str, Any],
) -> dict[str, Any]:
    body = pr_payload.get("body") if isinstance(pr_payload, dict) else None
    fields = pr_body_governance_metadata_fields(body)
    release_judgment = fields.get("release_judgment")
    repo_interface = governance_surface.get("repo_interface") if isinstance(governance_surface, dict) else None
    release_targets = repo_interface.get("release_targets") if isinstance(repo_interface, dict) else None
    target_release = (
        release_targets.get("target_release")
        if isinstance(release_targets, dict) and isinstance(release_targets.get("target_release"), dict)
        else empty_target_release_status()
    )
    evidence_locator = closeout_freeze_release_evidence_locator_from_body(body)
    evidence_readback = closeout_freeze_evidence_locator_status(target_root, evidence_locator)
    missing_inputs: list[str] = []
    source_locator = evidence_readback.get("locator")

    if release_judgment not in GOVERNANCE_RELEASE_JUDGMENT_VALUES:
        missing_inputs.append("release judgment metadata is missing")
    elif release_judgment == "deferred_release_judgment_blocking":
        missing_inputs.append("release judgment is deferred and blocking")
    elif release_judgment == "release_required":
        if target_release.get("result") != "pass":
            release_missing = target_release.get("missing_inputs")
            if isinstance(release_missing, list) and release_missing:
                missing_inputs.extend(f"target_release: {message}" for message in release_missing)
            else:
                missing_inputs.append("release-required closeout requires target release readback evidence")
        provenance = target_release.get("provenance") if isinstance(target_release.get("provenance"), dict) else {}
        source_locator = provenance.get("status_locator") or provenance.get("source_locator") or source_locator
    elif release_judgment == "no_release":
        if evidence_readback.get("status") != "present":
            missing_inputs.extend(str(message) for message in evidence_readback.get("missing_inputs", []))

    result = "pass" if not missing_inputs else "block"
    return {
        "schema_version": "loom-closeout-release-boundary/v1",
        "result": result,
        "release_judgment": release_judgment if release_judgment in GOVERNANCE_RELEASE_JUDGMENT_VALUES else None,
        "source": "implementation_pr_body plus release/no-release evidence readback",
        "source_locator": source_locator,
        "release_judgment_source": "implementation_pr_body.governance_intensity_carrier.fields.release_judgment",
        "evidence_readback": evidence_readback,
        "target_release": target_release,
        "context_validation_entry": context.get("validation_entry"),
        "missing_inputs": dedupe_strings(missing_inputs),
        "failure_kind": "closeout_release_evidence_gap",
        "category": "gate_failure",
        "severity": "block",
        "subject": "release_boundary",
        "fallback_to": "release-evidence",
        "why_blocking": "closeout freeze must consume release/no-release evidence readback instead of trusting PR metadata alone.",
        "next_action": "record or read back release/no-release evidence, then rerun closeout freeze.",
    }

def closeout_freeze_dependency_binding(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int | None,
    issue_payload: dict[str, Any] | None,
    dependency_payload_file: str | None,
) -> dict[str, Any]:
    fixture, fixture_errors = load_optional_json_fixture(target_root, dependency_payload_file, label="native dependency payload fixture")
    if fixture_errors:
        graph = dependency_graph_payload(issue_number=issue_number, issue_payload=issue_payload, native_dependency_payload=None)
        return {
            "result": "block",
            "source_locator": dependency_payload_file,
            "dependency_graph": graph,
            "missing_inputs": fixture_errors,
            "failure_kind": "closeout_dependency_graph_drift",
            "category": "gate_failure",
            "severity": "block",
            "subject": "dependency_graph",
            "why_blocking": "closeout freeze must read dependency graph state before admitting terminal closeout facts.",
            "fallback_to": "manual-reconciliation",
            "next_action": "restore readable dependency graph readback, then rerun closeout freeze.",
        }

    source_locator = dependency_payload_file
    if isinstance(fixture, dict):
        native_dependencies = fixture
    elif owner and repo_name and issue_number is not None:
        native_dependencies = github_issue_dependencies_payload(target_root, owner, repo_name, issue_number)
        source_locator = f"github:issue/{issue_number}/dependencies"
    else:
        native_dependencies = {"availability": "unreadable", "checks": [], "native_edges": []}
        source_locator = "github dependency readback"

    graph = dependency_graph_payload(
        issue_number=issue_number,
        issue_payload=issue_payload,
        native_dependency_payload=native_dependencies,
    )
    blocking_kinds = {
        "missing_native_edge",
        "stale_native_edge",
        "open_blocker_executable_conflict",
        "native_dependency_unreadable",
    }
    blocking_findings = [
        finding
        for finding in graph.get("findings", [])
        if isinstance(finding, dict) and finding.get("kind") in blocking_kinds
    ]
    missing_inputs = [str(finding.get("subject") or finding.get("kind")) for finding in blocking_findings]
    if graph.get("availability") in {"unsupported", "permission_denied", "unreadable"} and not any(
        isinstance(finding, dict) and finding.get("kind") == "native_dependency_unreadable"
        for finding in blocking_findings
    ):
        missing_inputs.append(f"dependency graph availability is {graph.get('availability')}")
    result = "pass" if not missing_inputs else "block"
    return {
        "result": result,
        "source_locator": source_locator,
        "dependency_graph": graph,
        "findings": blocking_findings,
        "missing_inputs": dedupe_strings(missing_inputs),
        "failure_kind": "closeout_dependency_graph_drift",
        "category": "gate_failure",
        "severity": "block",
        "subject": "dependency_graph",
        "why_blocking": "closeout freeze cannot admit terminal facts while dependency edges are open, stale, unreadable, or out of sync.",
        "fallback_to": "manual-reconciliation",
        "next_action": "reconcile native dependency edges or resolve open blockers, then rerun closeout freeze.",
    }

def closeout_freeze_allowed_paths_binding(
    context: dict[str, Any],
    *,
    base_sha: str | None,
    head_sha: str | None,
) -> dict[str, Any]:
    allowed_paths = closeout_allowed_paths(context)
    missing_inputs: list[str] = []
    changed_paths: list[str] = []
    if not isinstance(base_sha, str) or not base_sha:
        missing_inputs.append("closeout allowed-path diff base is missing")
    if not isinstance(head_sha, str) or not head_sha:
        missing_inputs.append("closeout allowed-path current head is missing")
    if not missing_inputs:
        changed_paths, diff_errors = git_changed_paths(context["target_root"], base_sha, head_sha)
        missing_inputs.extend(f"allowed paths diff: {message}" for message in diff_errors)

    violations = [path for path in changed_paths if path not in allowed_paths]
    for path in violations:
        missing_inputs.append(f"non-closeout path changed after implementation merge: {path}")
    result = "pass" if not missing_inputs else "block"
    return {
        "result": result,
        "source_locator": "git diff --name-only <merge-commit>..HEAD",
        "allowed_paths": sorted(allowed_paths),
        "changed_paths": changed_paths,
        "violations": violations,
        "missing_inputs": dedupe_strings(missing_inputs),
        "failure_kind": "closeout_allowed_paths_violation",
        "category": "gate_failure",
        "severity": "block",
        "subject": "allowed_paths",
        "why_blocking": "closeout freeze can only admit terminal carrier/readback changes; implementation drift requires full review.",
        "fallback_to": "full_review",
        "next_action": "remove non-closeout changes or convert this closeout to the full review path.",
    }

def closeout_freeze_payload(args: argparse.Namespace, *, operation: str) -> dict[str, Any]:
    target_root = resolve_target_arg(args.target)
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = args.owner or detected_owner
    repo_name = args.repo_name or detected_repo
    hosted_args = argparse.Namespace(
        target=str(target_root),
        output=args.output,
        item=args.item,
        owner=args.owner,
        repo_name=args.repo_name,
        pr=args.pr,
        head_sha=args.head_sha,
        branch=args.branch,
        pr_payload_file=args.pr_payload_file,
        issue=None,
        issue_payload_file=None,
        dependency_payload_file=None,
        body_file=args.body_file,
        compare_body_file=args.compare_body_file,
        surface=args.surface,
        profile="hosted",
        closeout_mode=args.closeout_mode,
        target_branch=args.target_branch,
        write_path=None,
    )
    base_freeze = gate_freeze_payload(hosted_args, operation="check")
    runtime_state = base_freeze.get("runtime_state") if isinstance(base_freeze.get("runtime_state"), dict) else runtime_state_payload(target_root)
    context, context_errors = load_context(target_root, args.output, args.item)
    if context_errors:
        missing_inputs = [str(message) for message in context_errors]
        blocking_inputs = [
            {
                "id": "closeout-fact-chain-not-ready",
                "input": "fact_chain",
                "failure_kind": "closeout_terminal_subject_drift",
                "source_locator": args.output,
                "messages": missing_inputs,
                "next_action": "restore or read back the retained Work Item fact chain before closeout freeze.",
            }
        ]
        closeout_specific_gate = closeout_specific_gate_payload(
            mode=args.closeout_mode,
            closeout_pr_allowed=False,
            full_review_required=True,
            blocking_inputs=blocking_inputs,
            next_action="resolve_closeout_freeze_blockers",
        )
        return {
            "command": "gate-freeze",
            "operation": operation,
            "schema_version": CLOSEOUT_FREEZE_SCHEMA,
            "profile": "closeout",
            "mode": args.closeout_mode,
            "result": "block",
            "summary": "closeout freeze requires an active or retained Loom Work Item fact chain.",
            "missing_inputs": missing_inputs,
            "fallback_to": "loom status --target <repo> --json",
            "mutates": operation == "write",
            "runtime_state": runtime_state,
            "target": str(target_root),
            "readiness": {
                "result": "block",
                "blocking_inputs": blocking_inputs,
                "closeout_pr_allowed": False,
                "full_review_required": True,
            },
            "closeout_specific_gate": closeout_specific_gate,
            "consumed_contract_fields": [
                "carrier_refresh_result",
                "shadow_freshness",
                "hosted_freeze_admission",
                "failure_classifier_mapping",
                "readback_drift",
                "release_evidence_readback",
                "closeout_specific_gate_profile",
            ],
            "pending_contract_fields": [
                "release_no_release_final_closeout",
            ],
            "failure_classifier": failure_classifier_payload(
                [
                    {
                        "input": "fact_chain",
                        "failure_kind": "closeout_terminal_subject_drift",
                        "source_locator": args.output,
                        "messages": missing_inputs,
                    }
                ]
            ),
        }

    head_sha = args.head_sha or git_head_sha(target_root)
    branch_name = args.branch or git_branch(target_root)
    issue_payload, issue_errors = closeout_freeze_load_issue(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        issue_number=args.issue,
        issue_payload_file=args.issue_payload_file,
    )
    pr_payload, effective_pr, pr_errors = closeout_freeze_load_pr(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        pr_number=args.pr,
        pr_payload_file=args.pr_payload_file,
    )

    merge_commit = None
    if isinstance(pr_payload, dict):
        merge_entry = pr_payload.get("mergeCommit")
        if isinstance(merge_entry, dict) and isinstance(merge_entry.get("oid"), str):
            merge_commit = merge_entry["oid"]
    target_contains_merge, target_errors = closeout_freeze_target_contains_merge(
        target_root,
        merge_commit,
        args.target_branch,
        owner=owner,
        repo_name=repo_name,
    )
    dependency_binding = closeout_freeze_dependency_binding(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        issue_number=args.issue,
        issue_payload=issue_payload,
        dependency_payload_file=args.dependency_payload_file,
    )
    allowed_paths = closeout_freeze_allowed_paths_binding(context, base_sha=merge_commit, head_sha=head_sha)

    governance_surface = build_governance_surface(target_root)
    input_bindings = base_freeze.get("input_bindings") if isinstance(base_freeze.get("input_bindings"), dict) else {}
    hosted_retained_review = input_bindings.get("review_binding") if isinstance(input_bindings.get("review_binding"), dict) else {}
    retained_review = closeout_freeze_retained_review_binding(context, pr_payload=pr_payload, merge_commit=merge_commit)
    hosted_release_boundary = input_bindings.get("release_requiredness") if isinstance(input_bindings.get("release_requiredness"), dict) else {}
    release_boundary = closeout_freeze_release_binding(target_root, context, pr_payload, governance_surface)
    carrier_refresh = input_bindings.get("carrier_refresh") if isinstance(input_bindings.get("carrier_refresh"), dict) else {}
    shadow_freshness = input_bindings.get("shadow_freshness") if isinstance(input_bindings.get("shadow_freshness"), dict) else {}
    readback = input_bindings.get("pr_body_pin") if isinstance(input_bindings.get("pr_body_pin"), dict) else {}

    terminal_subject_binding = closeout_freeze_terminal_subject_binding(
        context,
        issue_number=args.issue,
        issue_payload=issue_payload,
        issue_errors=issue_errors,
        pr_payload=pr_payload,
        pr_number=effective_pr,
        pr_errors=pr_errors,
        merge_commit=merge_commit,
        target_branch=args.target_branch,
    )
    closeout_bindings: dict[str, Any] = {
        "terminal_subject": terminal_subject_binding,
        "host_git": {
            "result": "pass" if target_contains_merge is True else "block",
            "missing_inputs": target_errors,
            "failure_kind": "closeout_host_git_mismatch",
            "source_locator": f"git merge-base --is-ancestor {merge_commit or '<merge-commit>'} {args.target_branch}",
            "next_action": "re-read the merged PR, merge commit, and target branch before closeout freeze.",
        },
        "dependency_graph": dependency_binding,
        "carrier_refresh": carrier_refresh,
        "shadow_freshness": shadow_freshness,
        "readback": readback,
        "retained_review": retained_review,
        "release_boundary": release_boundary,
        "allowed_paths": allowed_paths,
    }

    blocking_inputs = gate_freeze_blocking_inputs(closeout_bindings)
    result = "pass" if not blocking_inputs else "block"
    closeout_pr_allowed = result == "pass" and args.closeout_mode in {"inline", "auto_no_op", "light", "batched"}
    terminal_subject = {
        "work_item": context["item_id"],
        "closeout_issue": args.issue,
        "implementation_pr": effective_pr,
        "closeout_pr": None,
        "merge_commit": merge_commit,
        "target_branch": args.target_branch,
        "workspace": str(target_root),
        "branch": branch_name,
        "head_sha": head_sha,
        "generated_at": current_iso_timestamp(),
        "source_commands": {
            "issue_readback": "gh api repos/:owner/:repo/issues/<issue>",
            "implementation_pr_readback": "gh api repos/:owner/:repo/pulls/<pr>",
            "target_branch_contains": "git merge-base --is-ancestor <merge-commit> <target-branch>",
            "carrier_snapshot": "loom gate freeze check --profile hosted --target <repo> --json",
        },
    }
    terminal_facts = {
        "issue_state": issue_payload.get("state") if isinstance(issue_payload, dict) else None,
        "closed_at": issue_payload.get("closedAt") if isinstance(issue_payload, dict) else None,
        "pr_merged": isinstance(pr_payload, dict) and pr_payload.get("state") == "MERGED",
        "target_contains_merge_commit": target_contains_merge,
        "dependency_graph": dependency_binding.get("result"),
        "fact_chain_idle": "pending_until_carrier_sync",
    }
    readiness = {
        "result": result,
        "blocking_inputs": blocking_inputs,
        "refresh_suggestions": gate_freeze_refresh_suggestions(closeout_bindings) if blocking_inputs else [],
        "closeout_pr_allowed": closeout_pr_allowed,
        "full_review_required": result == "block" or args.closeout_mode == "full",
        "next_action": "closeout_pr_allowed" if closeout_pr_allowed else "resolve_closeout_freeze_blockers",
    }
    closeout_specific_gate = closeout_specific_gate_payload(
        mode=args.closeout_mode,
        closeout_pr_allowed=closeout_pr_allowed,
        full_review_required=bool(readiness["full_review_required"]),
        blocking_inputs=blocking_inputs,
        next_action=str(readiness["next_action"]),
    )
    payload: dict[str, Any] = {
        "command": "gate-freeze",
        "operation": operation,
        "schema_version": CLOSEOUT_FREEZE_SCHEMA,
        "profile": "closeout",
        "mode": args.closeout_mode,
        "result": result,
        "summary": (
            "closeout freeze terminal facts are admissible."
            if result == "pass"
            else "closeout freeze found terminal fact or closeout-only path drift."
        ),
        "missing_inputs": [
            message
            for blocking in blocking_inputs
            for message in blocking.get("messages", [])
            if isinstance(blocking, dict)
        ],
        "fallback_to": None if result == "pass" else "closeout_freeze_refresh",
        "mutates": operation == "write",
        "runtime_state": runtime_state,
        "target": str(target_root),
        "terminal_subject": terminal_subject,
        "terminal_facts": terminal_facts,
        "carrier_bindings": {
            "progress_terminal_metadata": f".loom/progress/{context['item_id']}.md",
            "status_surface": ".loom/status/current.md",
            "retained_review": retained_review.get("source_locator"),
            "dependency_graph": dependency_binding,
            "carrier_refresh": carrier_refresh,
            "shadow_freshness": shadow_freshness,
            "readback": readback,
            "release_boundary": release_boundary,
            "hosted_retained_review": hosted_retained_review,
            "hosted_release_boundary": hosted_release_boundary,
        },
        "retained_review": retained_review,
        "release_boundary": release_boundary,
        "allowed_paths": allowed_paths,
        "readiness": readiness,
        "closeout_specific_gate": closeout_specific_gate,
        "consumed_contract_fields": [
            "carrier_refresh_result",
            "shadow_freshness",
            "hosted_snapshot_binding",
            "failure_classifier_mapping",
            "readback_drift",
            "release_evidence_readback",
            "closeout_specific_gate_profile",
        ],
        "pending_contract_fields": [
            "release_no_release_final_closeout",
        ],
        "base_freeze_snapshot": {
            "schema_version": base_freeze.get("schema_version"),
            "snapshot_id": base_freeze.get("snapshot_id"),
            "input_bindings": {
                "carrier_refresh": carrier_refresh,
                "shadow_freshness": shadow_freshness,
                "readback": readback,
                "failure_classifier": base_freeze.get("failure_classifier"),
            },
        },
        "failure_classifier": failure_classifier_payload(blocking_inputs),
    }
    fingerprint_payload = {
        "schema_version": CLOSEOUT_FREEZE_SCHEMA,
        "profile": payload["profile"],
        "mode": payload["mode"],
        "terminal_subject": terminal_subject,
        "terminal_facts": terminal_facts,
        "carrier_bindings": payload["carrier_bindings"],
        "allowed_paths": allowed_paths,
        "readiness": readiness,
        "closeout_specific_gate": closeout_specific_gate,
    }
    payload["snapshot_id"] = "sha256:" + hashlib.sha256(
        json.dumps(fingerprint_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return payload

def gate_freeze_payload(args: argparse.Namespace, *, operation: str) -> dict[str, Any]:
    if getattr(args, "profile", "hosted") == "closeout":
        return closeout_freeze_payload(args, operation=operation)

    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return {
            **runtime_state_block_payload(
                command="gate-freeze",
                operation=operation,
                runtime_state=runtime_state,
                summary="gate freeze is blocked because the Loom runtime state is inconsistent.",
            ),
            "schema_version": GATE_FREEZE_SCHEMA,
            "mutates": operation == "write",
        }

    context, context_errors = load_context(target_root, args.output, args.item)
    if context_errors:
        missing_inputs = [str(message) for message in context_errors]
        return {
            "command": "gate-freeze",
            "operation": operation,
            "schema_version": GATE_FREEZE_SCHEMA,
            "result": "block",
            "summary": "gate freeze requires an active Loom Work Item fact chain.",
            "missing_inputs": missing_inputs,
            "fallback_to": "loom status --target <repo> --json",
            "mutates": operation == "write",
            "runtime_state": runtime_state,
            "target": str(target_root),
            "input_bindings": {
                "fact_chain": {
                    "result": "block",
                    "source_locator": args.output,
                    "missing_inputs": missing_inputs,
                }
            },
            "readiness": {
                "result": "block",
                "blocking_inputs": [
                    {
                        "id": "fact-chain-not-ready",
                        "input": "fact_chain",
                        "failure_kind": "missing_or_stale_gate_input",
                        "source_locator": args.output,
                        "consumer_impact": "hosted gate admission cannot build a freeze snapshot without an active Work Item.",
                        "messages": missing_inputs,
                        "next_action": "resume or initialize the active Work Item before freezing gate inputs.",
                    }
                ],
                "refresh_suggestions": ["loom status --target <repo> --json"],
                "next_action": "resume or initialize the active Work Item before freezing gate inputs.",
            },
        }

    head_sha = args.head_sha or git_head_sha(target_root)
    branch_name = args.branch or git_branch(target_root)
    governance_surface = build_governance_surface(target_root)
    pr_metadata = pr_metadata_preflight_payload(
        target_root=target_root,
        surface=args.surface,
        owner=args.owner,
        repo_name=args.repo_name,
        pr_number=args.pr,
        head_sha=head_sha,
        branch_name=branch_name,
        pr_payload_file=args.pr_payload_file,
        body_file=args.body_file,
        compare_body_file=args.compare_body_file,
        governance_surface=governance_surface,
        expected_item=context["item_id"],
        expected_head_sha=head_sha,
        expected_branch=branch_name,
        issue_number=getattr(args, "issue", None),
    )
    metadata_suite_not_applicable = metadata_suite_not_applicable_payload(
        context,
        pr_metadata,
        surface=args.surface,
    )
    if metadata_suite_not_applicable is not None:
        suite_validation = metadata_suite_not_applicable
        suite_evidence_validation = metadata_suite_not_applicable
        suite_carrier_validation = metadata_suite_not_applicable
    else:
        suite_validation = spec_suite_validation_payload(context)
        suite_evidence_validation = suite_validation_command_payload(context, domain="evidence")
        suite_carrier_validation = suite_validation_command_payload(context, domain="carrier")
    work_item_binding = gate_freeze_file_binding(target_root, relative_to_root(context["work_item_path"], target_root), label="work item")
    progress_binding = gate_freeze_file_binding(target_root, relative_to_root(context["recovery_path"], target_root), label="progress carrier")
    status_binding = gate_freeze_file_binding(target_root, relative_to_root(context["status_path"], target_root), label="status surface")

    input_bindings: dict[str, Any] = {
        "fact_chain": {
            "result": "pass",
            "source_locator": args.output,
            "item_id": context["item_id"],
            "workspace_entry": context["workspace_entry"],
            "read_entry": context["read_entry"],
            "missing_inputs": [],
        },
        "work_item_carrier": work_item_binding,
        "progress_carrier": progress_binding,
        "status_surface": status_binding,
        "pr_metadata": pr_metadata,
        "pr_body_pin": gate_freeze_pr_body_pin_binding(pr_metadata),
        "review_binding": gate_freeze_review_binding(context, head_sha=head_sha, surface=args.surface),
        "shadow_parity": gate_freeze_shadow_binding(target_root, governance_surface),
        "carrier_refresh": gate_freeze_carrier_refresh_binding(target_root, args.output, context["item_id"], surface=args.surface),
        "shadow_freshness": gate_freeze_shadow_freshness_binding(target_root, governance_surface),
        "suite_validation": suite_validation,
        "suite_evidence_validation": suite_evidence_validation,
        "suite_carrier_validation": suite_carrier_validation,
        "release_requiredness": gate_freeze_release_binding(pr_metadata),
        "command_surface": gate_freeze_command_surface(context),
    }
    blocking_inputs = gate_freeze_blocking_inputs(input_bindings)
    result = "pass" if not blocking_inputs else "block"
    refresh_suggestions = gate_freeze_refresh_suggestions(input_bindings) if blocking_inputs else []
    snapshot_subject = {
        "item_id": context["item_id"],
        "workspace_entry": context["workspace_entry"],
        "branch": branch_name,
        "head_sha": head_sha,
        "base_sha": git_merge_base(target_root, "origin/main", "HEAD"),
        "pr": args.pr,
        "surface": args.surface,
        "generated_at": current_iso_timestamp(),
        "source_commands": {
            "check": "loom gate freeze check --target <repo> --json",
            "write": "loom gate freeze write --target <repo> --json",
        },
    }
    payload: dict[str, Any] = {
        "command": "gate-freeze",
        "operation": operation,
        "schema_version": GATE_FREEZE_SCHEMA,
        "result": result,
        "summary": "gate freeze snapshot inputs are ready." if result == "pass" else "gate freeze snapshot has blocking input gaps.",
        "missing_inputs": [
            message
            for blocking in blocking_inputs
            for message in blocking.get("messages", [])
            if isinstance(blocking, dict)
        ],
        "fallback_to": None if result == "pass" else "refresh_gate_inputs",
        "mutates": operation == "write",
        "runtime_state": runtime_state,
        "target": str(target_root),
        "snapshot_subject": snapshot_subject,
        "input_bindings": input_bindings,
        "readiness": {
            "result": result,
            "blocking_inputs": blocking_inputs,
            "refresh_suggestions": refresh_suggestions,
            "next_action": "hosted_admission_allowed" if result == "pass" else "refresh_gate_inputs_before_hosted_admission",
        },
        "failure_classifier": failure_classifier_payload(blocking_inputs),
    }
    fingerprint_payload = {
        "schema_version": payload["schema_version"],
        "snapshot_subject": snapshot_subject,
        "input_bindings": input_bindings,
        "readiness": payload["readiness"],
    }
    payload["snapshot_id"] = hashlib.sha256(
        json.dumps(fingerprint_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return payload

def hosted_freeze_snapshot_comparison(
    target_root: Path,
    snapshot_file: str | None,
    recomputed_freeze: dict[str, Any] | None,
) -> dict[str, Any]:
    if not snapshot_file:
        return {
            "result": "not_applicable",
            "summary": "No hosted freeze snapshot artifact was provided; comparison is not applicable.",
            "snapshot_locator": None,
            "missing_inputs": [],
            "fallback_to": None,
        }
    path, errors = resolve_artifact_read_path(target_root, snapshot_file, label="hosted freeze snapshot")
    if errors or path is None:
        return {
            "result": "block",
            "summary": "Hosted freeze snapshot artifact is unreadable.",
            "snapshot_locator": snapshot_file,
            "missing_inputs": errors,
            "failure_kind": "freeze_artifact_unreadable",
            "fallback_to": "refresh_gate_inputs",
        }
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return {
            "result": "block",
            "summary": "Hosted freeze snapshot artifact could not be read.",
            "snapshot_locator": snapshot_file,
            "missing_inputs": [f"failed to read hosted freeze snapshot: {exc.strerror or exc}"],
            "failure_kind": "freeze_artifact_unreadable",
            "fallback_to": "refresh_gate_inputs",
        }
    except json.JSONDecodeError as exc:
        return {
            "result": "block",
            "summary": "Hosted freeze snapshot artifact is not valid JSON.",
            "snapshot_locator": snapshot_file,
            "missing_inputs": [f"hosted freeze snapshot JSON is invalid: {exc.msg}"],
            "failure_kind": "freeze_artifact_unreadable",
            "fallback_to": "refresh_gate_inputs",
        }

    missing_inputs: list[str] = []
    if not isinstance(snapshot, dict):
        missing_inputs.append("hosted freeze snapshot must be a JSON object")
    elif snapshot.get("schema_version") != GATE_FREEZE_SCHEMA:
        missing_inputs.append(f"hosted freeze snapshot schema_version must be `{GATE_FREEZE_SCHEMA}`")

    recomputed_snapshot_id = recomputed_freeze.get("snapshot_id") if isinstance(recomputed_freeze, dict) else None
    retained_snapshot_id = snapshot.get("snapshot_id") if isinstance(snapshot, dict) else None
    if recomputed_snapshot_id and retained_snapshot_id and recomputed_snapshot_id != retained_snapshot_id:
        missing_inputs.append("hosted freeze snapshot_id does not match recomputed freeze")

    if isinstance(snapshot, dict) and isinstance(recomputed_freeze, dict):
        retained_subject = snapshot.get("snapshot_subject")
        recomputed_subject = recomputed_freeze.get("snapshot_subject")
        if isinstance(retained_subject, dict) and isinstance(recomputed_subject, dict):
            for key in ("item_id", "branch", "head_sha", "pr", "surface"):
                if retained_subject.get(key) != recomputed_subject.get(key):
                    missing_inputs.append(f"hosted freeze snapshot_subject.{key} does not match recomputed freeze")

    result = "pass" if not missing_inputs else "block"
    return {
        "result": result,
        "summary": (
            "Hosted freeze snapshot artifact matches the recomputed freeze."
            if result == "pass"
            else "Hosted freeze snapshot artifact does not match the recomputed freeze."
        ),
        "snapshot_locator": snapshot_file,
        "snapshot_id": retained_snapshot_id,
        "recomputed_snapshot_id": recomputed_snapshot_id,
        "missing_inputs": dedupe_strings(missing_inputs),
        "failure_kind": "hosted_snapshot_mismatch" if result == "block" else None,
        "fallback_to": None if result == "pass" else "refresh_gate_inputs",
    }

def hosted_freeze_admission_payload(
    *,
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    owner: str | None,
    repo_name: str | None,
    pr_number: int | None,
    head_sha: str | None,
    branch_name: str | None,
    pr_payload_file: str | None,
    body_file: str | None,
    compare_body_file: str | None,
    snapshot_file: str | None,
    surface: str | None,
    pr_metadata_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    hosted_inputs_present = any([body_file, compare_body_file, snapshot_file])
    if not hosted_inputs_present:
        return {
            "schema_version": HOSTED_FREEZE_ADMISSION_SCHEMA,
            "result": "not_applicable",
            "summary": "Hosted freeze admission was not requested because no hosted PR body readback or freeze snapshot input was provided.",
            "missing_inputs": [],
            "fallback_to": None,
            "recomputed_freeze": None,
            "carrier_refresh": None,
            "shadow_freshness": None,
            "readback": None,
            "artifact_comparison": {
                "result": "not_applicable",
                "summary": "No hosted freeze snapshot artifact was provided; comparison is not applicable.",
                "snapshot_locator": None,
                "missing_inputs": [],
                "fallback_to": None,
            },
            "failure_classifier": failure_classifier_payload([]),
        }

    if governance_metadata_declares_host_readback_only(pr_metadata_preflight):
        pr_body_pin = gate_freeze_pr_body_pin_binding(pr_metadata_preflight or {})
        input_bindings = {
            "pr_metadata": pr_metadata_preflight,
            "pr_body_pin": pr_body_pin,
            "fact_chain": {
                "result": "not_applicable",
                "source_locator": "pr_metadata.governance_intensity_carrier.fields.fact_chain_required",
                "missing_inputs": [],
                "summary": "PR metadata declares host_readback_only review and fact_chain_required false for this gate.",
            },
        }
        blocking_inputs = gate_freeze_blocking_inputs(input_bindings)
        recomputed = {
            "command": "gate-freeze",
            "operation": "check",
            "schema_version": GATE_FREEZE_SCHEMA,
            "result": "pass" if not blocking_inputs else "block",
            "summary": (
                "Hosted freeze admission consumed PR metadata/readback without repo fact-chain inputs."
                if not blocking_inputs
                else "Hosted freeze admission found blocking PR metadata/readback inputs."
            ),
            "missing_inputs": [
                message
                for blocking in blocking_inputs
                if isinstance(blocking, dict)
                for message in blocking.get("messages", [])
                if str(message).strip()
            ],
            "fallback_to": None if not blocking_inputs else "update_pr_body",
            "target": str(target_root),
            "snapshot_subject": {
                "item_id": expected_item,
                "branch": branch_name,
                "head_sha": head_sha,
                "pr": pr_number,
                "surface": surface,
                "generated_at": current_iso_timestamp(),
                "source_commands": {
                    "check": "loom pr-gate check --target <repo> --json",
                },
            },
            "input_bindings": input_bindings,
            "readiness": {
                "result": "pass" if not blocking_inputs else "block",
                "blocking_inputs": blocking_inputs,
                "refresh_suggestions": ["loom pr metadata-update --apply --json"] if blocking_inputs else [],
                "next_action": "hosted_admission_allowed" if not blocking_inputs else "update_pr_body",
            },
        }
        artifact_comparison = hosted_freeze_snapshot_comparison(target_root, snapshot_file, recomputed)
        comparison_missing = [
            str(message)
            for message in artifact_comparison.get("missing_inputs", [])
            if str(message).strip()
        ]
        if artifact_comparison.get("result") == "block":
            blocking_inputs.append(
                {
                    "id": "hosted-freeze-snapshot-mismatch",
                    "input": "hosted_admission",
                    "failure_kind": artifact_comparison.get("failure_kind") or "hosted_snapshot_mismatch",
                    "category": "gate_failure",
                    "kind": artifact_comparison.get("failure_kind") or "hosted_snapshot_mismatch",
                    "severity": "block",
                    "subject": "hosted_freeze_snapshot",
                    "result": "block",
                    "source_locator": snapshot_file,
                    "messages": comparison_missing,
                    "next_action": "regenerate the freeze snapshot from the current PR/head/body/carriers, then rerun hosted admission.",
                    "fallback_to": artifact_comparison.get("fallback_to"),
                }
            )
        missing_inputs = dedupe_strings(
            [
                str(message)
                for blocking in blocking_inputs
                if isinstance(blocking, dict)
                for message in blocking.get("messages", [])
                if str(message).strip()
            ]
        )
        result = "pass" if recomputed.get("result") == "pass" and artifact_comparison.get("result") in {"pass", "not_applicable"} else "block"
        return {
            "schema_version": HOSTED_FREEZE_ADMISSION_SCHEMA,
            "result": result,
            "summary": (
                "Hosted freeze admission consumed host-readback-only metadata without repo fact-chain inputs."
                if result == "pass"
                else "Hosted freeze admission found blocking host-readback-only metadata drift."
            ),
            "missing_inputs": missing_inputs,
            "fallback_to": None if result == "pass" else "update_pr_body",
            "recomputed_freeze": recomputed,
            "input_bindings": input_bindings,
            "carrier_refresh": None,
            "shadow_freshness": None,
            "readback": pr_body_pin,
            "readback_classification": failure_classifier_payload(
                [
                    {
                        "input": "pr_body_pin",
                        "failure_kind": "head_or_pr_drift",
                        "messages": pr_body_pin.get("missing_inputs", []),
                    }
                ]
                if isinstance(pr_body_pin, dict) and pr_body_pin.get("result") == "block"
                else []
            ),
            "artifact_comparison": artifact_comparison,
            "blocking_inputs": blocking_inputs,
            "failure_classifier": failure_classifier_payload(blocking_inputs),
            "profile": "host_readback_only",
        }

    freeze_surface = surface if surface in {"pre_review", "review", "merge_ready", "closeout"} else "merge_ready"
    freeze_args = argparse.Namespace(
        target=str(target_root),
        output=output_relative,
        item=expected_item,
        owner=owner,
        repo_name=repo_name,
        pr=pr_number,
        head_sha=head_sha,
        branch=branch_name,
        pr_payload_file=pr_payload_file,
        body_file=body_file,
        compare_body_file=compare_body_file,
        surface=freeze_surface,
        write_path=None,
    )
    recomputed = gate_freeze_payload(freeze_args, operation="check")
    artifact_comparison = hosted_freeze_snapshot_comparison(target_root, snapshot_file, recomputed)
    input_bindings = recomputed.get("input_bindings") if isinstance(recomputed.get("input_bindings"), dict) else {}
    blocking_inputs = list(recomputed.get("readiness", {}).get("blocking_inputs", [])) if isinstance(recomputed.get("readiness"), dict) else []

    comparison_missing = [
        str(message)
        for message in artifact_comparison.get("missing_inputs", [])
        if str(message).strip()
    ]
    if artifact_comparison.get("result") == "block":
        blocking_inputs.append(
            {
                "id": "hosted-freeze-snapshot-mismatch",
                "input": "hosted_admission",
                "failure_kind": artifact_comparison.get("failure_kind") or "hosted_snapshot_mismatch",
                "category": "gate_failure",
                "kind": artifact_comparison.get("failure_kind") or "hosted_snapshot_mismatch",
                "severity": "block",
                "subject": "hosted_freeze_snapshot",
                "result": "block",
                "source_locator": snapshot_file,
                "messages": comparison_missing,
                "next_action": "regenerate the freeze snapshot from the current PR/head/body/carriers, then rerun hosted admission.",
                "fallback_to": artifact_comparison.get("fallback_to"),
            }
        )

    missing_inputs = dedupe_strings(
        [
            str(message)
            for blocking in blocking_inputs
            if isinstance(blocking, dict)
            for message in blocking.get("messages", [])
            if str(message).strip()
        ]
    )
    result = "pass" if recomputed.get("result") == "pass" and artifact_comparison.get("result") in {"pass", "not_applicable"} else "block"
    return {
        "schema_version": HOSTED_FREEZE_ADMISSION_SCHEMA,
        "result": result,
        "summary": (
            "Hosted freeze admission recomputed current gate inputs and found them admissible."
            if result == "pass"
            else "Hosted freeze admission recomputed current gate inputs and found blocking drift."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "refresh_gate_inputs",
        "recomputed_freeze": recomputed,
        "input_bindings": input_bindings,
        "carrier_refresh": input_bindings.get("carrier_refresh"),
        "shadow_freshness": input_bindings.get("shadow_freshness"),
        "readback": input_bindings.get("pr_body_pin"),
        "readback_classification": failure_classifier_payload(
            [
                {
                    "input": "pr_body_pin",
                    "failure_kind": "head_or_pr_drift",
                    "messages": input_bindings.get("pr_body_pin", {}).get("missing_inputs", []),
                }
            ]
            if isinstance(input_bindings.get("pr_body_pin"), dict) and input_bindings.get("pr_body_pin", {}).get("result") == "block"
            else []
        ),
        "artifact_comparison": artifact_comparison,
        "blocking_inputs": blocking_inputs,
        "failure_classifier": failure_classifier_payload(blocking_inputs),
    }

def handle_gate_freeze(args: argparse.Namespace) -> int:
    payload = gate_freeze_payload(args, operation=args.operation)
    if args.operation == "write":
        target_root = resolve_target_arg(args.target)
        item_id = (
            payload.get("snapshot_subject", {}).get("item_id")
            if isinstance(payload.get("snapshot_subject"), dict)
            else None
        )
        if item_id is None and isinstance(payload.get("terminal_subject"), dict):
            item_id = payload.get("terminal_subject", {}).get("work_item")
        item_slug = str(item_id or args.item or "unknown")
        default_name = f"{item_slug}-closeout.json" if getattr(args, "profile", "hosted") == "closeout" else f"{item_slug}.json"
        relative = args.write_path or f".loom/runtime/gate-freeze/{default_name}"
        logical_path, errors = resolve_repo_relative_path(target_root, relative, label="gate freeze write path")
        allowed_root = (target_root / ".loom" / "runtime" / "gate-freeze").resolve()
        if logical_path is not None:
            resolved_path = logical_path.resolve()
            if resolved_path == allowed_root or not resolved_path.is_relative_to(allowed_root):
                errors.append("gate freeze write path must be under .loom/runtime/gate-freeze/")
        path = None
        if not errors:
            path, errors = resolve_artifact_write_path(target_root, relative, label="gate freeze write path")
        if errors or path is None:
            payload["result"] = "block"
            payload["summary"] = "gate freeze write path is invalid."
            payload.setdefault("missing_inputs", [])
            payload["missing_inputs"] = dedupe_strings([*payload["missing_inputs"], *errors])
            payload["write_artifact"] = {
                "result": "block",
                "locator": relative,
                "missing_inputs": errors,
            }
        else:
            write_json_file(path, payload)
            payload["write_artifact"] = {
                "result": "pass",
                "locator": relative,
                "mutates": "global-runtime-cache",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    return emit(payload)

def load_pr_payload_for_gate(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    pr_number: int | None,
    head_sha: str | None,
    branch_name: str | None,
    pr_payload_file: str | None,
) -> tuple[dict[str, Any] | None, int | None, list[str], list[dict[str, Any]]]:
    missing_inputs: list[str] = []
    inferences: list[dict[str, Any]] = []
    fixture, fixture_errors = load_optional_json_fixture(target_root, pr_payload_file, label="PR payload fixture")
    if fixture_errors:
        return None, pr_number, fixture_errors, inferences
    if fixture is not None:
        payload, errors = normalize_pr_fixture_payload(fixture)
        if errors:
            return None, pr_number, errors, inferences
        inferred_number = pr_number or (int(payload["number"]) if isinstance(payload.get("number"), int) else None)
        return payload, inferred_number, [], inferences

    inferred_pr = pr_number or infer_pr_number_from_ref(branch_name)
    if inferred_pr is not None and pr_number is None:
        inferences.append({"from": "branch", "to": "pr", "status": "inferred", "pr": inferred_pr})

    if inferred_pr is None and owner and repo_name and head_sha:
        pulls, pull_errors = github_commit_pulls(target_root, owner, repo_name, head_sha)
        if pull_errors:
            missing_inputs.extend(f"head_sha: {message}" for message in pull_errors)
        elif len(pulls) == 1 and isinstance(pulls[0].get("number"), int):
            inferred_pr = int(pulls[0]["number"])
            inferences.append({"from": "head_sha", "to": "pr", "status": "inferred", "pr": inferred_pr})
        elif len(pulls) > 1:
            missing_inputs.append("head_sha resolves to multiple PRs; pass --pr explicitly")

    if inferred_pr is None:
        return None, None, missing_inputs or ["pr | head-sha | branch"], inferences
    if not owner or not repo_name:
        return None, inferred_pr, ["owner/repo"], inferences
    payload, errors = github_pr_payload(target_root, owner, repo_name, inferred_pr)
    return payload, inferred_pr, errors, inferences

def pr_gate_failure_taxonomy(missing_inputs: list[str], gate_result: str) -> list[str]:
    categories: set[str] = set()
    for message in missing_inputs:
        lowered = str(message).lower()
        if (
            lowered in {"owner/repo", "pr: owner/repo"}
            or "target is unavailable" in lowered
            or "not a git repository" in lowered
            or ("fact-chain" in lowered and "missing init-result" in lowered)
        ):
            categories.add("target_readback_failed")
        if "pr" in lowered and ("unreadable" in lowered or "payload" in lowered or "head_sha" in lowered):
            categories.add("pr_unreadable")
        if "work item" in lowered or "current item mismatch" in lowered:
            categories.add("work_item_binding_conflict" if "mismatch" in lowered else "work_item_binding_missing")
        if "fact-chain" in lowered or "fact chain" in lowered:
            categories.add("fact_chain_unreadable")
        if "missing review" in lowered or "missing implementation review" in lowered or "missing review artifact" in lowered:
            categories.add("review_missing")
        if "schema_version" in lowered or "invalid review" in lowered:
            categories.add("review_schema_invalid")
        if "semantic_review_disposition missing" in lowered:
            categories.add("semantic_review_disposition_missing")
            categories.add("review_missing")
        if "semantic_review_disposition invalid" in lowered or "semantic_review_disposition unknown" in lowered:
            categories.add("semantic_review_disposition_invalid")
        if "semantic_review_disposition" in lowered and (
            "missing `" in lowered
            or "requires" in lowered
            or "not bound" in lowered
            or "validation summary" in lowered
        ):
            categories.add("semantic_review_disposition_invalid")
        if "implementation review kind" in lowered or "cannot satisfy implementation approval" in lowered:
            categories.add("review_not_approved")
        if "decision is blocking" in lowered or "decision is fallback" in lowered or "not approved" in lowered:
            categories.add("review_not_approved")
        if "stale" in lowered or "implementation drift" in lowered:
            categories.add("review_stale")
        if "validation summary" in lowered:
            categories.add("validation_summary_drift")
        if "reviewed_head" in lowered or "head binding" in lowered or "not bound to the current pr head" in lowered:
            categories.add("head_binding_drift")
        if "pr body head sha" in lowered or "pr body branch" in lowered or "payload headrefoid" in lowered:
            categories.add("head_binding_drift")
        if "checkout head" in lowered:
            categories.add("checkout_head_drift")
        if "raw" in lowered or "shadow" in lowered:
            categories.add("raw_evidence_bypass")
        if "post-merge review" in lowered or "already merged" in lowered:
            categories.add("post_merge_review")
            categories.add("post_merge_review_bypass")
        if "semantic review disposition is missing for merged pr" in lowered or "semantic review bypass" in lowered:
            categories.add("semantic_review_bypass")
            categories.add("post_merge_review_bypass")
        if "ci-only" in lowered or "ci only" in lowered:
            categories.add("ci_only_bypass")
            categories.add("ci_only_merge_bypass")
        if "required check" in lowered or "branch protection" in lowered or "ruleset" in lowered:
            categories.add("host_enforcement_unverified")
        if "pr metadata" in lowered:
            categories.add("pr_metadata_preflight_failed")
        if "hosted-freeze-admission" in lowered:
            categories.add("hosted_freeze_admission_blocked")
        if "hosted freeze snapshot" in lowered or "snapshot_id does not match" in lowered:
            categories.add("hosted_snapshot_mismatch")
    if gate_result == "fallback":
        categories.add("prior_gate_fallback")
    return sorted(categories)

def approval_boundary_payload(*, raw_evidence_present: bool) -> dict[str, Any]:
    return {
        "authored_truth": "work_item.review_entry",
        "raw_review_evidence_satisfies_approval": False,
        "shadow_evidence_satisfies_approval": False,
        "runtime_review_evidence_satisfies_approval": False,
        "pr_body_summary_satisfies_approval": False,
        "ci_success_satisfies_approval": False,
        "github_review_comments_satisfy_approval": False,
        "repo_companion_satisfies_approval": False,
        "guardian_satisfies_approval": False,
        "raw_evidence_present": raw_evidence_present,
        "required_authored_review_kinds": sorted(IMPLEMENTATION_REVIEW_KINDS),
    }

def validation_summary_hash(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def review_validation_summary_binding(review_record: dict[str, Any], current_validation_summary: str | None) -> dict[str, Any]:
    current_hash = validation_summary_hash(current_validation_summary)
    reviewed_summary = review_record.get("reviewed_validation_summary")
    reviewed_hash = None
    for field in ("reviewed_validation_summary_hash", "validation_summary_hash"):
        value = review_record.get(field)
        if isinstance(value, str) and value.strip():
            reviewed_hash = value.strip()
            break
    raw_matches = (
        isinstance(current_validation_summary, str)
        and bool(current_validation_summary)
        and isinstance(reviewed_summary, str)
        and reviewed_summary == current_validation_summary
    )
    hash_matches = bool(current_hash and reviewed_hash and current_hash == reviewed_hash)
    return {
        "current_validation_summary_hash": current_hash,
        "reviewed_validation_summary_hash": reviewed_hash,
        "raw_summary_matches": raw_matches,
        "hash_matches": hash_matches,
        "matches": current_hash is None or raw_matches or hash_matches,
        "source": review_record.get("validation_summary_source") or review_record.get("reviewed_validation_summary_source"),
        "locator": review_record.get("validation_summary_locator") or review_record.get("reviewed_validation_summary_locator"),
    }

def semantic_review_disposition_payload(
    *,
    review_record: dict[str, Any],
    review_path: str,
    pr_head: str | None,
    head_binding: dict[str, Any],
    current_validation_summary: str | None,
) -> tuple[dict[str, Any], list[str]]:
    raw_disposition = review_record.get("semantic_review_disposition")
    errors: list[str] = []
    validation_binding = review_validation_summary_binding(review_record, current_validation_summary)
    base = {
        "status": "missing",
        "source": "review_record",
        "path": review_path,
        "reviewed_head": review_record.get("reviewed_head"),
        "pr_head": pr_head,
        "reviewed_validation_summary": review_record.get("reviewed_validation_summary"),
        "current_validation_summary": current_validation_summary,
        "validation_summary_hash": validation_binding,
        "head_binding": head_binding,
        "consumable": False,
        "details": {},
    }
    if raw_disposition is None:
        return base, [f"semantic_review_disposition missing in review artifact `{review_path}`"]
    if isinstance(raw_disposition, str):
        disposition = {"status": raw_disposition}
    elif isinstance(raw_disposition, dict):
        disposition = dict(raw_disposition)
    else:
        return base, [f"semantic_review_disposition invalid in review artifact `{review_path}`"]

    status = disposition.get("status")
    if not isinstance(status, str) or status not in SEMANTIC_REVIEW_DISPOSITION_STATUSES:
        base["status"] = status if isinstance(status, str) else "invalid"
        base["details"] = disposition
        return base, [f"semantic_review_disposition unknown disposition `{status}` in review artifact `{review_path}`"]

    payload = {**base, "status": status, "details": disposition}
    if status == "required":
        return payload, [f"semantic_review_disposition required in review artifact `{review_path}`"]

    if status == "passed":
        if review_record.get("decision") != "allow":
            errors.append("semantic_review_disposition passed requires review decision allow")
        if review_record.get("kind") not in IMPLEMENTATION_REVIEW_KINDS:
            errors.append("semantic_review_disposition passed requires an implementation review kind")
        if head_binding.get("stale") is True or head_binding.get("status") not in {
            "fresh",
            "carrier-only",
            "generated-only",
            "carrier-and-generated-only",
        }:
            errors.append("semantic_review_disposition passed is not bound to the current PR head")
        if not validation_binding["matches"]:
            errors.append("semantic_review_disposition passed validation summary does not match current recovery")
        payload["consumable"] = not errors
        return payload, errors

    required = (
        SEMANTIC_REVIEW_NOT_APPLICABLE_REQUIRED_FIELDS
        if status == "not_applicable"
        else SEMANTIC_REVIEW_WAIVED_REQUIRED_FIELDS
    )
    for field in required:
        value = disposition.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"semantic_review_disposition {status} missing `{field}`")
    if status == "waived":
        expiry = disposition.get("expiry")
        one_shot = disposition.get("one_shot")
        if (not isinstance(expiry, str) or not expiry.strip()) and one_shot is not True:
            errors.append("semantic_review_disposition waived missing `expiry` or one-shot true")
    if head_binding.get("stale") is True:
        errors.append(f"semantic_review_disposition {status} is not bound to the current PR head")
    if not validation_binding["matches"]:
        errors.append(f"semantic_review_disposition {status} validation summary does not match current recovery")
    payload["consumable"] = not errors
    return payload, errors

def carrier_only_closeout_review_payload(
    *,
    review_record: dict[str, Any],
    review_path: str,
    pr_head: str | None,
    head_binding: dict[str, Any],
    current_validation_summary: str | None,
) -> tuple[dict[str, Any], list[str]]:
    raw_disposition = review_record.get("carrier_only_closeout_review")
    errors: list[str] = []
    validation_binding = review_validation_summary_binding(review_record, current_validation_summary)
    base = {
        "status": "missing",
        "source": "review_record",
        "path": review_path,
        "reviewed_head": review_record.get("reviewed_head"),
        "pr_head": pr_head,
        "reviewed_validation_summary": review_record.get("reviewed_validation_summary"),
        "current_validation_summary": current_validation_summary,
        "validation_summary_hash": validation_binding,
        "head_binding": head_binding,
        "consumable": False,
        "does_not_approve_product_implementation": True,
        "details": {},
    }
    if raw_disposition is None:
        return base, [f"carrier_only_closeout_review missing in review artifact `{review_path}`"]
    if not isinstance(raw_disposition, dict):
        return base, [f"carrier_only_closeout_review invalid in review artifact `{review_path}`"]
    status = raw_disposition.get("status")
    payload = {**base, "status": status if isinstance(status, str) else "invalid", "details": dict(raw_disposition)}
    if status != "passed":
        return payload, [f"carrier_only_closeout_review must be passed in review artifact `{review_path}`"]
    if review_record.get("decision") != "allow":
        errors.append("carrier_only_closeout_review passed requires review decision allow")
    if review_record.get("kind") not in IMPLEMENTATION_REVIEW_KINDS:
        errors.append("carrier_only_closeout_review passed requires an implementation review kind")
    if head_binding.get("stale") is True or head_binding.get("status") not in {
        "fresh",
        "carrier-only",
        "generated-only",
        "carrier-and-generated-only",
    }:
        errors.append("carrier_only_closeout_review passed is not bound to the current PR head")
    if not validation_binding["matches"]:
        errors.append("carrier_only_closeout_review passed validation summary does not match current recovery")
    payload["consumable"] = not errors
    return payload, errors

def parse_github_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

def review_record_time_value(review_record: dict[str, Any]) -> str | None:
    for field in ("authored_at", "created_at", "recorded_at", "submittedAt", "submitted_at"):
        value = review_record.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None

def post_merge_review_repair_plan(*, pr_number: int | None, review_path: str | None) -> dict[str, Any]:
    return {
        "summary": "Do not promote post-merge review evidence into merge-before-review compliance.",
        "actions": [
            {
                "kind": "closeout_evidence",
                "description": "Record explicit post-merge closeout evidence that the historical bypass was diagnosed after merge.",
                "target": f"PR #{pr_number}" if pr_number is not None else "merged PR",
            },
            {
                "kind": "forward_guard",
                "description": "Require future merges to pass `loom pr gate` and `loom merge check/run` against the current PR head before host merge.",
                "target": "controlled merge path",
            },
            {
                "kind": "review_record",
                "description": "Keep the authored review record as post-merge evidence only; rerun review before a future merge instead of rewriting history.",
                "target": review_path or "review record",
            },
        ],
        "forbidden_repairs": [
            "backdate review evidence",
            "treat GitHub review/check status as authored Loom review approval",
            "mark historical raw host merge as merge-ready compliant",
        ],
    }

def post_merge_review_diagnostic_payload(
    *,
    pr_payload: dict[str, Any] | None,
    review_record: dict[str, Any] | None,
    review_path: str | None,
) -> dict[str, Any]:
    pr_number = pr_payload.get("number") if isinstance(pr_payload, dict) and isinstance(pr_payload.get("number"), int) else None
    merged_at_raw = pr_payload.get("mergedAt") if isinstance(pr_payload, dict) else None
    review_time_raw = review_record_time_value(review_record) if isinstance(review_record, dict) else None
    merged_at = parse_github_timestamp(merged_at_raw)
    review_time = parse_github_timestamp(review_time_raw)
    missing_inputs: list[str] = []
    finding: dict[str, Any] | None = None
    result = "pass"
    summary = "review timing does not indicate post-merge review bypass."

    if not isinstance(pr_payload, dict) or pr_payload.get("state") != "MERGED":
        result = "not_applicable"
        summary = "PR is not merged; post-merge review bypass timing is not applicable yet."
    elif review_record is None:
        result = "block"
        summary = "merged PR has no authored Loom review disposition."
        missing_inputs.append("semantic review disposition is missing for merged PR")
        finding = {
            "kind": "semantic_review_bypass",
            "severity": "block",
            "subject": f"PR #{pr_number}" if pr_number is not None else "merged PR",
            "evidence": {
                "pr_state": pr_payload.get("state"),
                "mergedAt": merged_at_raw,
                "review_path": review_path,
                "review_time": None,
            },
            "recommended_action": "Record post-merge closeout evidence and keep future merges behind the PR gate; do not treat missing review as compliant.",
            "fallback_to": "manual-reconciliation",
        }
    elif merged_at is None:
        result = "fallback"
        summary = "merged PR has no readable mergedAt timestamp for review timing diagnostics."
        missing_inputs.append("mergedAt timestamp")
    elif review_time is None:
        result = "fallback"
        summary = "review record has no readable authored timestamp for post-merge diagnostics."
        missing_inputs.append("review authored timestamp")
    elif review_time > merged_at:
        result = "block"
        summary = "authored review evidence was recorded after the PR was merged."
        missing_inputs.append("post-merge review evidence cannot satisfy merge-before-review compliance")
        finding = {
            "kind": "post_merge_review_bypass",
            "severity": "block",
            "subject": f"PR #{pr_number}" if pr_number is not None else "merged PR",
            "evidence": {
                "pr_state": pr_payload.get("state"),
                "mergedAt": merged_at_raw,
                "review_path": review_path,
                "review_time": review_time_raw,
            },
            "recommended_action": "Record this as post-merge closeout evidence and rely on controlled merge for future protection.",
            "fallback_to": "manual-reconciliation",
        }

    return {
        "schema_version": POST_MERGE_REVIEW_DIAGNOSTIC_SCHEMA,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": None if result in {"pass", "not_applicable"} else "manual-reconciliation",
        "pr": {
            "number": pr_number,
            "state": pr_payload.get("state") if isinstance(pr_payload, dict) else None,
            "mergedAt": merged_at_raw,
            "headRefOid": pr_payload.get("headRefOid") if isinstance(pr_payload, dict) else None,
        },
        "review": {
            "path": review_path,
            "time": review_time_raw,
            "time_field": next(
                (
                    field
                    for field in ("authored_at", "created_at", "recorded_at", "submittedAt", "submitted_at")
                    if isinstance(review_record, dict) and isinstance(review_record.get(field), str) and review_record.get(field).strip()
                ),
                None,
            ),
            "decision": review_record.get("decision") if isinstance(review_record, dict) else None,
            "kind": review_record.get("kind") if isinstance(review_record, dict) else None,
            "reviewed_head": review_record.get("reviewed_head") if isinstance(review_record, dict) else None,
        },
        "finding": finding,
        "repair_plan": post_merge_review_repair_plan(pr_number=pr_number, review_path=review_path),
    }

def approval_boundary_lint_status(
    *,
    context: dict[str, Any],
    pr_head: str | None,
    review_approval: dict[str, Any],
    raw_evidence_present: bool,
    failure_taxonomy: list[str],
) -> dict[str, Any]:
    blocking_results: list[dict[str, Any]] = []
    not_applicable_results: list[dict[str, Any]] = []
    status = review_approval.get("status")
    review_kind = review_approval.get("kind")
    reviewed_head = review_approval.get("reviewed_head")
    head_binding = review_approval.get("head_binding") if isinstance(review_approval.get("head_binding"), dict) else {}
    stale_taxonomy = {"review_stale", "head_binding_drift", "validation_summary_drift"} & set(failure_taxonomy)
    if (
        status == "approved"
        and head_binding.get("status") == "carrier-only"
        and head_binding.get("stale") is False
    ):
        stale_taxonomy.discard("head_binding_drift")
    if (
        status == "approved"
        and head_binding.get("status") in {"generated-only", "carrier-and-generated-only"}
        and head_binding.get("stale") is False
    ):
        stale_taxonomy.discard("head_binding_drift")
    base_result = {
        "schema_version": GOVERNANCE_LINT_RESULT_SCHEMA,
        "id": "authored_review_approval_boundary",
        "kind": "approval_bypass",
        "surface": "merge_ready",
        "subject": "work_item.review_entry",
        "mapped_failure": {
            "category": "gate_failure",
            "kind": "approval_bypass",
        },
        "provenance": {
            "source_layer": "authored_truth",
            "source_owner": "loom",
            "source_locator": context.get("review_entry"),
            "source_binding": "work_item.review_entry",
            "freshness": "fresh" if status == "approved" else "missing" if status == "missing" else "stale",
        },
        "bindings": {
            "item_id": context.get("item_id"),
            "head_sha": pr_head,
            "scope": context.get("scope"),
            "reviewed_head_sha": reviewed_head,
            "pr_ref": None,
        },
        "fallback_to": "review record / approval gate",
    }
    if stale_taxonomy:
        blocking_results.append(
            {
                **base_result,
                "id": "authored_review_evidence_freshness",
                "kind": "evidence_stale",
                "strength": "blocking",
                "summary": "authored review approval exists but no longer binds to the current head or validation summary",
                "mapped_failure": {
                    "category": "stale",
                    "kind": "evidence_stale",
                },
                "provenance": {
                    **base_result["provenance"],
                    "freshness": "stale",
                },
                "evidence_freshness": "stale",
                "fallback_to": "validation / evidence refresh",
            }
        )
    elif status == "approved":
        not_applicable_results.append(
            {
                **base_result,
                "strength": "not_applicable",
                "summary": "Authored implementation review approval is present; raw, shadow, PR body, CI, and GitHub review evidence remain evidence-only.",
                "evidence_freshness": "fresh",
            }
        )
    else:
        reasons = []
        if raw_evidence_present:
            reasons.append("raw or runtime review evidence is present")
        if review_kind and review_kind not in IMPLEMENTATION_REVIEW_KINDS:
            reasons.append(f"review kind `{review_kind}` is not an implementation approval kind")
        if "raw_evidence_bypass" in failure_taxonomy:
            reasons.append("raw evidence cannot satisfy semantic approval")
        if not reasons:
            reasons.append("fresh authored implementation review approval is absent")
        blocking_results.append(
            {
                **base_result,
                "strength": "blocking",
                "summary": "; ".join(reasons),
                "evidence_freshness": "missing" if status == "missing" else "stale",
            }
        )
    return {
        "schema_version": GOVERNANCE_LINT_STATUS_SCHEMA,
        "surface": "merge_ready",
        "result": "block" if blocking_results else "pass",
        "result_summary": (
            "approval bypass lint blocks merge-ready because authored implementation review approval is absent or invalid."
            if blocking_results
            else "approval bypass lint found no raw/shadow/PR/CI/GitHub evidence promoted to semantic approval."
        ),
        "blocking_results": blocking_results,
        "advisory_results": [],
        "repo_specific_results": [],
        "not_applicable_results": not_applicable_results,
        "mapped_failures": [entry["mapped_failure"] for entry in blocking_results],
        "provenance": [entry["provenance"] for entry in [*blocking_results, *not_applicable_results]],
    }

def pr_gate_payload(
    *,
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    owner: str | None,
    repo_name: str | None,
    pr_number: int | None,
    head_sha: str | None,
    branch_name: str | None,
    pr_payload_file: str | None,
    body_file: str | None = None,
    compare_body_file: str | None = None,
    gate_freeze_snapshot_file: str | None = None,
    surface: str | None = None,
    issue_number: int | None = None,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    missing_inputs: list[str] = []
    steps: list[dict[str, Any]] = []

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
        missing_inputs.extend(str(message) for message in runtime_state.get("missing_inputs", []))

    pr_payload, effective_pr, pr_errors, inferences = load_pr_payload_for_gate(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        pr_number=pr_number,
        head_sha=head_sha,
        branch_name=branch_name,
        pr_payload_file=pr_payload_file,
    )
    if pr_errors:
        missing_inputs.extend(f"pr: {message}" for message in pr_errors)

    body_item = pr_work_item_from_body(pr_payload.get("body") if isinstance(pr_payload, dict) else None)
    body_surface = pr_body_machine_surface(pr_payload.get("body") if isinstance(pr_payload, dict) else None)
    effective_item = expected_item or body_item
    if expected_item and body_item and expected_item != body_item:
        missing_inputs.append(f"PR body Work Item `{body_item}` does not match expected `{expected_item}`")
    if effective_item is None:
        missing_inputs.append("PR body is missing `Loom Work Item: <item>`")

    pr_head = head_sha
    if isinstance(pr_payload, dict) and isinstance(pr_payload.get("headRefOid"), str):
        if pr_head and pr_payload["headRefOid"] != pr_head:
            missing_inputs.append("PR payload headRefOid does not match --head-sha")
        pr_head = pr_payload["headRefOid"]
    if not pr_head:
        missing_inputs.append("PR head SHA is unavailable")

    effective_branch_name = branch_name
    if isinstance(pr_payload, dict) and isinstance(pr_payload.get("headRefName"), str) and pr_payload.get("headRefName"):
        effective_branch_name = pr_payload["headRefName"]
    metadata_surface = surface or body_surface or "merge_ready"
    governance_surface = build_governance_surface(target_root)
    pr_metadata_preflight = pr_metadata_preflight_payload(
        target_root=target_root,
        surface=metadata_surface,
        owner=owner,
        repo_name=repo_name,
        pr_number=effective_pr,
        head_sha=pr_head,
        branch_name=effective_branch_name,
        pr_payload_file=pr_payload_file,
        body_file=body_file,
        compare_body_file=compare_body_file,
        pr_payload=pr_payload if isinstance(pr_payload, dict) else None,
        effective_pr=effective_pr,
        governance_surface=governance_surface,
        expected_item=effective_item,
        issue_number=issue_number,
        expected_head_sha=pr_head,
        expected_branch=effective_branch_name,
    )
    host_readback_only_gate = governance_metadata_declares_host_readback_only(pr_metadata_preflight)

    context: dict[str, Any] = {}
    context_errors: list[str] = []
    if host_readback_only_gate:
        context = {}
        context_errors = []
    elif effective_item is not None:
        context, context_errors = load_context_with_retained_idle_fallback(target_root, output_relative, effective_item)
    else:
        context, context_errors = load_context(target_root, output_relative, expected_item)
    if context_errors:
        missing_inputs.extend(f"fact-chain: {message}" for message in context_errors)

    pr_state = pr_payload.get("state") if isinstance(pr_payload, dict) else None
    if pr_payload is not None:
        if pr_state not in {"OPEN"}:
            missing_inputs.append(f"PR state must be OPEN before controlled merge: {pr_state}")
            if pr_state == "MERGED":
                missing_inputs.append("post-merge review consumption is not valid for pr-gate")
        if pr_payload.get("isDraft") is True:
            missing_inputs.append("PR is draft")
        if context:
            metadata_fields = governance_metadata_fields_from_preflight(pr_metadata_preflight)
            work_item_locator = metadata_fields.get("work_item_locator")
            if (
                pr_metadata_preflight.get("result") != "pass"
                or not isinstance(work_item_locator, str)
                or parse_typed_locator(work_item_locator, allowed_types={"work_item"}, allow_legacy=False) is None
            ):
                missing_inputs.append("PR metadata preflight does not bind a typed GitHub Work Item locator")

    current_head = git_head_sha(target_root)
    if pr_head and current_head and pr_head != current_head:
        missing_inputs.append("checkout head does not match PR head")
    suite_validation_override = (
        metadata_suite_not_applicable_payload(
            context,
            pr_metadata_preflight,
            surface=metadata_surface,
        )
        if context
        else None
    )
    hosted_admission = hosted_freeze_admission_payload(
        target_root=target_root,
        output_relative=output_relative,
        expected_item=effective_item,
        owner=owner,
        repo_name=repo_name,
        pr_number=effective_pr,
        head_sha=pr_head,
        branch_name=effective_branch_name,
        pr_payload_file=pr_payload_file,
        body_file=body_file,
        compare_body_file=compare_body_file,
        snapshot_file=gate_freeze_snapshot_file,
        surface=metadata_surface,
        pr_metadata_preflight=pr_metadata_preflight,
    )
    if hosted_admission.get("result") == "block":
        missing_inputs.extend(
            f"hosted-freeze-admission: {message}"
            for message in hosted_admission.get("missing_inputs", [])
        )
    steps.append(
        {
            "name": "hosted-freeze-admission",
            "result": hosted_admission["result"],
            "summary": hosted_admission["summary"],
            "missing_inputs": hosted_admission["missing_inputs"],
            "fallback_to": hosted_admission["fallback_to"],
            "hosted_freeze_admission": hosted_admission,
        }
    )

    merge_checkpoint: dict[str, Any] = {
        "result": "block",
        "summary": "merge checkpoint was not evaluated.",
        "missing_inputs": ["fact-chain"],
        "fallback_to": "admission",
    }
    review_approval: dict[str, Any] = {
        "status": "unavailable",
        "path": None,
        "decision": None,
        "reviewed_head": None,
        "head_binding": None,
        "semantic_review_disposition": None,
    }
    terminal_closeout_consumption: dict[str, Any] = {
        "result": "not_applicable",
        "summary": "PR gate is not evaluating a terminal closeout carrier PR.",
        "missing_inputs": [],
        "fallback_to": None,
    }
    if host_readback_only_gate:
        merge_checkpoint = {
            "result": "not_applicable",
            "summary": "PR metadata declares fact_chain_required false; repo merge checkpoint carriers are outside this gate boundary.",
            "missing_inputs": [],
            "fallback_to": None,
        }
        review_approval = {
            "status": GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT,
            "path": None,
            "decision": None,
            "kind": GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT,
            "reviewed_head": pr_head,
            "head_binding": {
                "status": "host-readback",
                "stale": False,
                "target_head": pr_head,
                "missing_inputs": [],
            },
            "semantic_review_disposition": {
                "status": GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT,
                "consumable": True,
                "source": "pr_metadata.governance_intensity_carrier.fields.review_requirement",
            },
            "missing_inputs": [],
        }
    timing_review_record: dict[str, Any] | None = None
    timing_review_path: str | None = None
    if context:
        merge_checkpoint = checkpoint_payload("merge", context, suite_validation_override=suite_validation_override)
        review_record, review_path, review_errors = load_review_record(target_root, context["item_id"], context["review_entry"])
        timing_review_record = review_record
        timing_review_path = review_path
        if review_record is None:
            review_approval = {
                "status": "missing",
                "path": review_path,
                "decision": None,
                "kind": None,
                "reviewed_head": None,
                "head_binding": None,
                "semantic_review_disposition": None,
                "missing_inputs": review_errors or [f"missing review artifact: {review_path}"],
            }
            missing_inputs.extend(review_approval["missing_inputs"])
        else:
            review_kind = review_record.get("kind")
            head_binding_payload, head_binding_errors = review_head_binding_for_head(
                target_root,
                reviewed_head=review_record.get("reviewed_head"),
                target_head=pr_head,
                allowed_paths=allowed_post_review_carrier_paths(context, review_path),
            )
            disposition, disposition_errors = semantic_review_disposition_payload(
                review_record=review_record,
                review_path=review_path,
                pr_head=pr_head,
                head_binding=head_binding_payload,
                current_validation_summary=context.get("latest_validation_summary"),
            )
            terminal_closeout_binding, terminal_closeout_binding_errors = review_head_binding_for_head(
                target_root,
                reviewed_head=review_record.get("reviewed_head"),
                target_head=pr_head,
                allowed_paths=allowed_terminal_closeout_carrier_paths(context, review_path),
            )
            merge_checkpoint_missing = [
                str(message)
                for message in merge_checkpoint.get("missing_inputs", [])
                if str(message).strip()
            ]
            terminal_closeout_missing: list[str] = []
            if body_surface != "closeout":
                terminal_closeout_missing.append("PR metadata surface is not closeout")
            if merge_checkpoint.get("result") != "fallback" or merge_checkpoint.get("fallback_to") not in {"closed", "closed_out"}:
                terminal_closeout_missing.append("merge checkpoint is not terminal closeout")
            if normalize_checkpoint(str(context.get("current_checkpoint", ""))) not in {"closed", "closed_out", "done"}:
                terminal_closeout_missing.append("current checkpoint is not terminal closed_out")
            if terminal_closeout_binding.get("status") not in {
                "fresh",
                "carrier-only",
                "generated-only",
                "carrier-and-generated-only",
            } or terminal_closeout_binding.get("stale") is True:
                terminal_closeout_missing.extend(terminal_closeout_binding_errors or ["terminal closeout carrier drift is not review-safe"])
            non_review_checkpoint_missing = [
                message
                for message in merge_checkpoint_missing
                if "review artifact is stale" not in message
                and "reviewed_head" not in message
                and "head binding" not in message
                and "review HEAD comparison failed" not in message
            ]
            terminal_closeout_missing.extend(non_review_checkpoint_missing)
            terminal_closeout_consumption = {
                "result": "pass" if not terminal_closeout_missing else "block",
                "summary": (
                    "terminal closeout carrier PR consumed retained implementation review and closeout-only carrier drift."
                    if not terminal_closeout_missing
                    else "terminal closeout carrier PR is not eligible to bypass current-head implementation review binding."
                ),
                "missing_inputs": terminal_closeout_missing,
                "fallback_to": None if not terminal_closeout_missing else "review",
                "surface": body_surface,
                "checkpoint": context.get("current_checkpoint"),
                "head_binding": terminal_closeout_binding,
                "retained_review": {
                    "path": review_path,
                    "reviewed_head": review_record.get("reviewed_head"),
                    "decision": review_record.get("decision"),
                    "kind": review_kind,
                },
                "allowed_paths_policy": "terminal closeout carrier paths only; does not apply to merge-ready implementation PRs",
            }
            approval_errors = [*review_errors, *head_binding_errors, *disposition_errors]
            terminal_closeout_pass = terminal_closeout_consumption.get("result") == "pass"
            approval_status = (
                "approved"
                if review_record.get("decision") == "allow"
                and not approval_errors
                and review_kind in IMPLEMENTATION_REVIEW_KINDS
                and disposition.get("consumable") is True
                else "terminal_closeout_retained"
                if terminal_closeout_pass
                else "not_approved"
            )
            review_approval = {
                "status": approval_status,
                "path": review_path,
                "decision": review_record.get("decision"),
                "kind": review_kind,
                "reviewed_head": review_record.get("reviewed_head"),
                "reviewed_validation_summary": review_record.get("reviewed_validation_summary"),
                "reviewed_validation_summary_hash": (
                    review_record.get("reviewed_validation_summary_hash")
                    or validation_summary_hash(review_record.get("reviewed_validation_summary"))
                ),
                "validation_summary_source": review_record.get("validation_summary_source"),
                "validation_summary_locator": review_record.get("validation_summary_locator"),
                "head_binding": head_binding_payload,
                "semantic_review_disposition": disposition,
                "missing_inputs": approval_errors,
            }
            if not terminal_closeout_pass:
                missing_inputs.extend(str(message) for message in approval_errors)
        terminal_closed_checkpoint = (
            merge_checkpoint.get("result") == "fallback"
            and merge_checkpoint.get("fallback_to") in {"closed", "closed_out"}
            and terminal_closeout_consumption.get("result") == "pass"
        )
        if merge_checkpoint.get("result") in {"block", "fallback"} and not terminal_closed_checkpoint:
            missing_inputs.extend(str(message) for message in merge_checkpoint.get("missing_inputs", []))
        steps.append(
            {
                "name": "checkpoint-merge",
                "result": "pass" if terminal_closed_checkpoint else merge_checkpoint.get("result"),
                "summary": merge_checkpoint.get("summary"),
                "missing_inputs": merge_checkpoint.get("missing_inputs", []),
                "fallback_to": merge_checkpoint.get("fallback_to"),
                "terminal_closed_checkpoint": terminal_closed_checkpoint,
            }
        )

    # Make the bypass boundary explicit even when raw evidence is present in the repository.
    if context:
        runtime_review_root = resolve_artifact_read_path(
            target_root,
            f".loom/runtime/review/{context['item_id']}",
            label="review runtime evidence root",
        )[0] or (target_root / ".loom/runtime/review" / context["item_id"])
        raw_evidence_present = runtime_review_root.exists() and any(runtime_review_root.glob("**/*"))
    else:
        raw_evidence_present = False

    if pr_metadata_preflight.get("result") == "block":
        missing_inputs.extend(str(message) for message in pr_metadata_preflight.get("missing_inputs", []))
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
    governance_intensity_gate = governance_intensity_gate_payload(context, pr_metadata_preflight)
    if isinstance(governance_intensity_gate, dict):
        if governance_intensity_gate.get("result") == "block":
            missing_inputs.extend(
                f"governance-intensity: {message}"
                for message in governance_intensity_gate.get("missing_inputs", [])
            )
        steps.append(
            {
                "name": "governance-intensity-gate",
                "result": governance_intensity_gate["result"],
                "summary": governance_intensity_gate["summary"],
                "missing_inputs": governance_intensity_gate["missing_inputs"],
                "fallback_to": governance_intensity_gate["fallback_to"],
                "governance_intensity_gate": governance_intensity_gate,
            }
        )
    docs_governance_lite_gate = docs_governance_lite_gate_payload(context, pr_metadata_preflight)
    if isinstance(docs_governance_lite_gate, dict):
        if docs_governance_lite_gate.get("result") == "block":
            missing_inputs.extend(
                f"docs-governance-lite: {message}"
                for message in docs_governance_lite_gate.get("missing_inputs", [])
            )
        steps.append(
            {
                "name": "docs-governance-lite-gate",
                "result": docs_governance_lite_gate["result"],
                "summary": docs_governance_lite_gate["summary"],
                "missing_inputs": docs_governance_lite_gate["missing_inputs"],
                "fallback_to": docs_governance_lite_gate["fallback_to"],
                "docs_governance_lite_gate": docs_governance_lite_gate,
            }
        )
    post_merge_review_diagnostic = post_merge_review_diagnostic_payload(
        pr_payload=pr_payload if isinstance(pr_payload, dict) else None,
        review_record=timing_review_record,
        review_path=timing_review_path,
    )
    if post_merge_review_diagnostic.get("result") in {"block", "fallback"}:
        missing_inputs.extend(
            f"post-merge review diagnostic: {message}"
            for message in post_merge_review_diagnostic.get("missing_inputs", [])
        )

    result = "pass"
    fallback_to: str | None = None
    for step in steps:
        if step.get("result") == "fallback":
            result = "fallback"
            fallback_to = step.get("fallback_to") or "build"
            break
        if step.get("result") == "block" and result == "pass":
            result = "block"
            fallback_to = step.get("fallback_to")
    if missing_inputs and result == "pass":
        result = "block"
        fallback_to = fallback_to or "build"

    failure_taxonomy = pr_gate_failure_taxonomy(missing_inputs, result)
    if raw_evidence_present and review_approval.get("status") != "approved" and "raw_evidence_bypass" not in failure_taxonomy:
        failure_taxonomy.append("raw_evidence_bypass")
    ci_or_host_review_signal_present = False
    if isinstance(pr_payload, dict):
        ci_or_host_review_signal_present = any(
            key in pr_payload and pr_payload.get(key) not in (None, [], {})
            for key in ("statusCheckRollup", "checks", "latestReviews", "reviewDecision", "mergeStateStatus")
        )
    if ci_or_host_review_signal_present and review_approval.get("status") != "approved":
        if review_approval.get("status") in {"terminal_closeout_retained", GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT}:
            pass
        else:
            missing_inputs.append("ci-only or host-review signal cannot satisfy semantic_review_disposition")
            for category in ("ci_only_bypass", "ci_only_merge_bypass"):
                if category not in failure_taxonomy:
                    failure_taxonomy.append(category)
    if missing_inputs and result == "pass":
        result = "block"
        fallback_to = fallback_to or "build"
    approval_boundary = approval_boundary_payload(raw_evidence_present=raw_evidence_present)
    governance_lint = (
        approval_boundary_lint_status(
            context=context,
            pr_head=pr_head,
            review_approval=review_approval,
            raw_evidence_present=raw_evidence_present,
            failure_taxonomy=sorted(failure_taxonomy),
        )
        if context
        else {
            "schema_version": GOVERNANCE_LINT_STATUS_SCHEMA,
            "surface": "merge_ready",
            "result": "pass" if host_readback_only_gate else "block",
            "result_summary": (
                "approval bypass lint consumed host-readback-only metadata without requiring repo fact-chain carriers."
                if host_readback_only_gate
                else "approval bypass lint cannot run until the Work Item fact chain is readable."
            ),
            "blocking_results": [],
            "advisory_results": [],
            "repo_specific_results": [],
            "not_applicable_results": [
                {
                    "schema_version": GOVERNANCE_LINT_RESULT_SCHEMA,
                    "id": "host_readback_only_review",
                    "kind": "host_readback_only",
                    "surface": "merge_ready",
                    "subject": "pr_metadata.review_requirement",
                    "strength": "not_applicable",
                    "summary": "Repo-local review artifact and active fact-chain are not gate inputs for this PR metadata profile.",
                    "mapped_failure": {
                        "category": "not_applicable",
                        "kind": "host_readback_only",
                    },
                    "provenance": {
                        "source_layer": "pr_metadata",
                        "source_owner": "host",
                        "source_locator": "pr_metadata.governance_intensity_carrier.fields.review_requirement",
                        "source_binding": "host_readback_only",
                        "freshness": "current",
                    },
                    "bindings": {
                        "work_item": effective_item,
                        "head_sha": pr_head,
                    },
                    "fallback_to": None,
                }
            ] if host_readback_only_gate else [],
            "mapped_failures": [],
            "provenance": [],
        }
    )
    if context and terminal_closeout_consumption.get("result") == "pass":
        governance_lint = {
            "schema_version": GOVERNANCE_LINT_STATUS_SCHEMA,
            "surface": "closeout",
            "result": "pass",
            "result_summary": "terminal closeout carrier PR retains implementation review evidence without promoting it to current-head merge-ready approval.",
            "blocking_results": [],
            "advisory_results": [],
            "repo_specific_results": [],
            "not_applicable_results": [
                {
                    "schema_version": GOVERNANCE_LINT_RESULT_SCHEMA,
                    "id": "terminal_closeout_retained_review",
                    "kind": "closeout_retained_review",
                    "surface": "closeout",
                    "subject": "work_item.review_entry",
                    "strength": "not_applicable",
                    "summary": "Closeout-only carrier drift is terminal and does not replace implementation PR review/head binding.",
                    "mapped_failure": {
                        "category": "not_applicable",
                        "kind": "terminal_closeout",
                    },
                    "provenance": {
                        "source_layer": "authored_truth",
                        "source_owner": "loom",
                        "source_locator": context.get("review_entry"),
                        "source_binding": "work_item.review_entry",
                        "freshness": "retained",
                    },
                    "bindings": {
                        "item_id": context.get("item_id"),
                        "head_sha": pr_head,
                        "reviewed_head_sha": review_approval.get("reviewed_head"),
                    },
                    "fallback_to": None,
                }
            ],
            "mapped_failures": [],
            "provenance": [],
        }
    closeout_specific_gate: dict[str, Any] | None = None
    if metadata_surface == "closeout" or terminal_closeout_consumption.get("result") == "pass":
        closeout_gate_messages = [
            str(message)
            for message in [
                *terminal_closeout_consumption.get("missing_inputs", []),
                *missing_inputs,
            ]
            if str(message).strip()
        ]
        closeout_gate_blocking_inputs = [
            {
                "input": "terminal_closeout_consumption",
                "failure_kind": "closeout_retained_review_unconsumable",
                "messages": closeout_gate_messages,
                "result": "block",
                "severity": "block",
                "source_locator": context.get("review_entry") if context else None,
                "next_action": "remove non-closeout changes or run full review / guardian before merging this PR.",
            }
        ] if closeout_gate_messages else []
        closeout_specific_gate = closeout_specific_gate_payload(
            mode="light",
            closeout_pr_allowed=result == "pass" and terminal_closeout_consumption.get("result") == "pass",
            full_review_required=bool(closeout_gate_blocking_inputs),
            blocking_inputs=closeout_gate_blocking_inputs,
            next_action=(
                "closeout_pr_allowed"
                if result == "pass" and terminal_closeout_consumption.get("result") == "pass"
                else "run_full_review_or_resolve_closeout_gate_blockers"
            ),
            source="pr-gate",
        )
    failure_taxonomy = sorted(failure_taxonomy)
    target_readback_failed = "target_readback_failed" in failure_taxonomy
    summary = (
        "PR gate could not read the target checkout or hosted PR binding."
        if result != "pass" and target_readback_failed
        else
        "PR merge gate consumed terminal closeout carrier drift with retained implementation review evidence."
        if result == "pass" and terminal_closeout_consumption.get("result") == "pass"
        else
        "PR merge gate consumed host-readback-only metadata without repo-local review or fact-chain carriers."
        if result == "pass" and review_approval.get("status") == GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT
        else
        "PR merge gate found fresh authored semantic review approval for the current PR head."
        if result == "pass"
        else "PR merge gate is blocked or falling back before host merge."
    )
    failed_layer = "target-readback" if result != "pass" and target_readback_failed else "pr-merge-gate" if result != "pass" else None
    return {
        "command": "pr-gate",
        "operation": "check",
        "schema_version": PR_MERGE_GATE_SCHEMA,
        "result": result,
        "summary": summary,
        "failed_layer": failed_layer,
        "missing_inputs": sorted(set(missing_inputs)),
        "fallback_to": fallback_to,
        "repository": {"owner": owner, "name": repo_name},
        "pr": {
            "number": effective_pr,
            "state": pr_state,
            "isDraft": pr_payload.get("isDraft") if isinstance(pr_payload, dict) else None,
            "headRefName": pr_payload.get("headRefName") if isinstance(pr_payload, dict) else branch_name,
            "baseRefName": pr_payload.get("baseRefName") if isinstance(pr_payload, dict) else None,
            "head_sha": pr_head,
            "url": pr_payload.get("url") if isinstance(pr_payload, dict) else None,
            "work_item_from_body": body_item,
            "mergeStateStatus": pr_payload.get("mergeStateStatus") if isinstance(pr_payload, dict) else None,
            "reviewDecision": pr_payload.get("reviewDecision") if isinstance(pr_payload, dict) else None,
            "latestReviews": pr_payload.get("latestReviews") if isinstance(pr_payload, dict) else None,
        },
        "work_item": {
            "id": context.get("item_id") if context else effective_item,
            "path": relative_to_root(context["work_item_path"], target_root) if context else None,
            "review_entry": context.get("review_entry") if context else None,
        },
        "review_approval": review_approval,
        "merge_checkpoint": merge_checkpoint,
        "pr_metadata_preflight": pr_metadata_preflight,
        "governance_intensity_gate": governance_intensity_gate,
        "docs_governance_lite_gate": docs_governance_lite_gate,
        "post_merge_review_diagnostic": post_merge_review_diagnostic,
        "terminal_closeout_consumption": terminal_closeout_consumption,
        **({"closeout_specific_gate": closeout_specific_gate} if closeout_specific_gate is not None else {}),
        "hosted_freeze_admission": hosted_admission,
        "governance_lint": governance_lint,
        "host_enforcement": {
            "stable_check_name": PR_MERGE_GATE_CHECK_NAME,
            "status": "not_checked",
            "reason": "pr-gate check proves PR-local semantic approval; controlled-merge checks host required status.",
        },
        "approval_boundary": approval_boundary,
        "failure_taxonomy": failure_taxonomy,
        "steps": steps,
        "inferences": inferences,
    }

def handle_pr_gate(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    return emit(
        pr_gate_payload(
            target_root=target_root,
            output_relative=args.output,
            expected_item=args.item,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
            pr_number=args.pr,
            head_sha=args.head_sha,
            branch_name=args.branch,
            pr_payload_file=args.pr_payload_file,
            body_file=args.body_file,
            compare_body_file=args.compare_body_file,
            gate_freeze_snapshot_file=args.gate_freeze_snapshot_file,
            surface=args.surface,
        )
    )

def required_status_contexts_from_protection(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    required_status = payload.get("required_status_checks")
    if not isinstance(required_status, dict):
        return []
    contexts = required_status.get("contexts")
    if isinstance(contexts, list):
        return [str(context) for context in contexts if isinstance(context, str) and context.strip()]
    checks = required_status.get("checks")
    if isinstance(checks, list):
        return [str(check.get("context")) for check in checks if isinstance(check, dict) and isinstance(check.get("context"), str)]
    return []

def required_status_contexts_from_branch_rules(payload: Any) -> list[str]:
    return governance_required_status_contexts_from_branch_rules(payload)

def required_check_status_payload(status_rollup: Any, required_contexts: list[str]) -> dict[str, Any]:
    runs = status_rollup if isinstance(status_rollup, list) else []
    by_name: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if not isinstance(run, dict):
            continue
        name = run.get("name") or run.get("context")
        if isinstance(name, str):
            by_name.setdefault(name, []).append(run)

    def is_success(entry: dict[str, Any]) -> bool:
        return entry.get("conclusion") == "SUCCESS" or entry.get("state") == "SUCCESS"

    def is_pending(entry: dict[str, Any]) -> bool:
        status = entry.get("status")
        state = entry.get("state")
        return status not in {None, "COMPLETED"} or state in {"EXPECTED", "PENDING"}

    missing: list[str] = []
    pending: list[str] = []
    failing: list[str] = []
    for context in required_contexts:
        entries = by_name.get(context, [])
        if not entries:
            missing.append(context)
            continue
        if any(is_success(entry) for entry in entries):
            continue
        if any(is_pending(entry) for entry in entries):
            pending.append(context)
        else:
            failing.append(context)

    result = "pass" if not missing and not pending and not failing else "block"
    return {
        "result": result,
        "required_contexts": required_contexts,
        "missing": missing,
        "pending": pending,
        "failing": failing,
    }

def triggered_check_name(run: dict[str, Any]) -> str | None:
    name = run.get("name") or run.get("context")
    return name if isinstance(name, str) and name.strip() else None

def triggered_check_workflow(run: dict[str, Any]) -> str | None:
    workflow = run.get("workflowName") or run.get("workflow")
    if isinstance(workflow, str) and workflow.strip():
        return workflow
    if isinstance(workflow, dict) and isinstance(workflow.get("name"), str):
        return workflow["name"]
    return None

def triggered_check_rollup_payload(status_rollup: Any) -> dict[str, Any]:
    if not isinstance(status_rollup, list):
        return {
            "result": "block",
            "summary": "triggered check rollup is unreadable.",
            "triggered_checks": [],
            "blocking": [],
            "pending": [],
            "allowed": [],
            "unknown": [],
            "missing_inputs": ["triggered check rollup unreadable"],
        }
    triggered_checks: list[dict[str, Any]] = []
    blocking: list[str] = []
    pending: list[str] = []
    allowed: list[str] = []
    unknown: list[str] = []
    for index, run in enumerate(status_rollup, start=1):
        if not isinstance(run, dict):
            unknown.append(f"check[{index}]")
            triggered_checks.append(
                {
                    "name": f"check[{index}]",
                    "workflow": None,
                    "status": None,
                    "conclusion": None,
                    "classification": "unknown",
                    "details_url": None,
                }
            )
            continue
        name = triggered_check_name(run) or f"check[{index}]"
        status = str(run.get("status")).upper() if isinstance(run.get("status"), str) and run.get("status") else None
        conclusion = str(run.get("conclusion")).upper() if isinstance(run.get("conclusion"), str) and run.get("conclusion") else None
        state = str(run.get("state")).upper() if isinstance(run.get("state"), str) and run.get("state") else None
        if status in TRIGGERED_CHECK_PENDING_STATUSES or (status is not None and status != "COMPLETED"):
            classification = "pending"
            pending.append(name)
        elif conclusion in TRIGGERED_CHECK_BLOCKING_CONCLUSIONS or state in TRIGGERED_CHECK_BLOCKING_CONCLUSIONS:
            classification = "failed"
            blocking.append(name)
        elif conclusion in TRIGGERED_CHECK_ALLOWED_CONCLUSIONS or state == "SUCCESS":
            classification = "allowed"
            allowed.append(name)
        else:
            classification = "unknown"
            unknown.append(name)
        triggered_checks.append(
            {
                "name": name,
                "workflow": triggered_check_workflow(run),
                "status": status,
                "conclusion": conclusion or state,
                "classification": classification,
                "details_url": run.get("detailsUrl") or run.get("details_url") or run.get("targetUrl"),
            }
        )
    missing_inputs = [f"triggered check `{name}` failed" for name in blocking]
    missing_inputs.extend(f"triggered check `{name}` is pending" for name in pending)
    missing_inputs.extend(f"triggered check `{name}` has unknown conclusion" for name in unknown)
    result = "pass" if not missing_inputs else "block"
    return {
        "result": result,
        "summary": "triggered checks are allowed." if result == "pass" else "triggered checks include blocking or unreadable states.",
        "triggered_checks": triggered_checks,
        "blocking": blocking,
        "pending": pending,
        "allowed": allowed,
        "unknown": unknown,
        "missing_inputs": missing_inputs,
    }

def load_retained_result_file(target_root: Path, fixture: str | None, *, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    payload, errors = load_optional_json_fixture(target_root, fixture, label=label)
    if errors:
        return None, errors
    if payload is None:
        return None, [f"{label} is required"]
    if not isinstance(payload, dict):
        return None, [f"{label} must expose a JSON object"]
    return payload, []

def retained_pr_gate_consumption(
    *,
    retained: dict[str, Any] | None,
    locator: str | None,
    current_pr: dict[str, Any],
    expected_item: str | None,
    pr_number: int,
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    current_head = current_pr.get("headRefOid")
    if isinstance(retained, dict) and retained.get("schema_version") == HOSTED_DELIVERY_GATE_READBACK_SCHEMA:
        retained_pr = retained.get("pr") if isinstance(retained.get("pr"), dict) else {}
        retained_work_item = retained.get("work_item") if isinstance(retained.get("work_item"), dict) else {}
        hosted_check = retained.get("hosted_check") if isinstance(retained.get("hosted_check"), dict) else {}
        review_attestation = (
            retained.get("review_attestation")
            if isinstance(retained.get("review_attestation"), dict)
            else {}
        )
        host_facts = (
            review_attestation.get("host_facts")
            if isinstance(review_attestation.get("host_facts"), dict)
            else {}
        )
        attested_pr = host_facts.get("pr") if isinstance(host_facts.get("pr"), dict) else {}
        retained_head = retained_pr.get("head_sha")
        retained_item = retained_work_item.get("locator")
        check_name = str(hosted_check.get("name") or hosted_check.get("context") or "")
        check_status = str(hosted_check.get("status") or "").upper()
        check_conclusion = str(hosted_check.get("conclusion") or hosted_check.get("state") or "").upper()
        if retained.get("result") != "pass":
            missing_inputs.append("retained hosted delivery gate result must be pass")
        if retained.get("assurance") not in {"limited", "strong"}:
            missing_inputs.append("retained hosted delivery gate assurance is not recognized")
        if retained_pr.get("number") != pr_number:
            missing_inputs.append("retained hosted delivery gate PR number does not match current PR")
        if not isinstance(retained_head, str) or not retained_head:
            missing_inputs.append("retained hosted delivery gate PR head is missing")
        elif retained_head != current_head:
            missing_inputs.append("retained hosted delivery gate PR head does not match current PR head")
        if expected_item and retained_item != expected_item:
            missing_inputs.append("retained hosted delivery gate Work Item does not match expected item")
        if check_name != "loom-delivery-gate":
            missing_inputs.append("retained hosted delivery gate check name is not loom-delivery-gate")
        if check_status != "COMPLETED" or check_conclusion not in {"SUCCESS", "EXPECTED", "PASS"}:
            missing_inputs.append("retained hosted delivery gate check is not completed successfully")
        if review_attestation.get("result") != "pass":
            missing_inputs.append("retained host review attestation must be pass")
        if expected_item and review_attestation.get("work_item_locator") != expected_item:
            missing_inputs.append("retained host review attestation Work Item does not match expected item")
        if attested_pr.get("number") != pr_number:
            missing_inputs.append("retained host review attestation PR number does not match current PR")
        if attested_pr.get("head_sha") != current_head:
            missing_inputs.append("retained host review attestation head does not match current PR head")
        result = "pass" if not missing_inputs else "block"
        return {
            "source": "retained",
            "locator": locator,
            "schema_version": retained.get("schema_version"),
            "result": result,
            "summary": (
                "retained hosted delivery gate is fresh for the current PR head."
                if result == "pass"
                else "retained hosted delivery gate is missing, stale, or not bound to the current host facts."
            ),
            "missing_inputs": missing_inputs,
            "fallback_to": None if result == "pass" else "pr gate",
            "freshness": "fresh" if result == "pass" else "stale",
            "bindings": {
                "pr": pr_number,
                "work_item": retained_item,
                "retained_head_sha": retained_head,
                "current_head_sha": current_head,
                "hosted_check": check_name,
                "assurance": retained.get("assurance"),
                "review_attestation_schema": review_attestation.get("schema_version"),
                "review_attested_head": attested_pr.get("head_sha"),
            },
        }
    retained_pr = retained.get("pr") if isinstance(retained, dict) and isinstance(retained.get("pr"), dict) else {}
    retained_work_item = (
        retained.get("work_item")
        if isinstance(retained, dict) and isinstance(retained.get("work_item"), dict)
        else {}
    )
    review_approval = (
        retained.get("review_approval")
        if isinstance(retained, dict) and isinstance(retained.get("review_approval"), dict)
        else {}
    )
    merge_checkpoint = (
        retained.get("merge_checkpoint")
        if isinstance(retained, dict) and isinstance(retained.get("merge_checkpoint"), dict)
        else {}
    )
    retained_head = retained_pr.get("head_sha")
    retained_item = retained_work_item.get("id")
    semantic_disposition = (
        review_approval.get("semantic_review_disposition")
        if isinstance(review_approval.get("semantic_review_disposition"), dict)
        else {}
    )
    terminal_closeout_consumption = (
        retained.get("terminal_closeout_consumption")
        if isinstance(retained, dict) and isinstance(retained.get("terminal_closeout_consumption"), dict)
        else {}
    )
    closeout_specific_gate = (
        retained.get("closeout_specific_gate")
        if isinstance(retained, dict) and isinstance(retained.get("closeout_specific_gate"), dict)
        else {}
    )
    terminal_closeout_allowed = (
        terminal_closeout_consumption.get("result") == "pass"
        and closeout_specific_gate.get("result") == "pass"
        and closeout_specific_gate.get("closeout_pr_allowed") is True
    )
    terminal_closeout_review_retained = (
        terminal_closeout_allowed
        and review_approval.get("status") == "terminal_closeout_retained"
        and review_approval.get("decision") == "allow"
    )

    if not isinstance(retained, dict):
        missing_inputs.append("retained pr-gate result is unreadable")
    else:
        if retained.get("schema_version") != PR_MERGE_GATE_SCHEMA:
            missing_inputs.append(f"retained pr-gate schema_version must be `{PR_MERGE_GATE_SCHEMA}`")
        if retained.get("result") != "pass":
            missing_inputs.append("retained pr-gate result must be pass")
        if retained_pr.get("number") != pr_number:
            missing_inputs.append("retained pr-gate PR number does not match current PR")
        if not isinstance(retained_head, str) or not retained_head:
            missing_inputs.append("retained pr-gate PR head is missing")
        elif isinstance(current_head, str) and current_head and retained_head != current_head:
            missing_inputs.append("retained pr-gate PR head does not match current PR head")
        if expected_item and retained_item != expected_item:
            missing_inputs.append("retained pr-gate Work Item does not match expected item")
        if (
            not terminal_closeout_review_retained
            and (review_approval.get("status") != "approved" or review_approval.get("decision") != "allow")
        ):
            missing_inputs.append("retained pr-gate does not carry authored allow review approval")
        if review_approval.get("kind") not in IMPLEMENTATION_REVIEW_KINDS:
            missing_inputs.append("retained pr-gate review kind cannot satisfy implementation approval")
        if (
            not terminal_closeout_review_retained
            and (
                semantic_disposition.get("status") not in {"passed", "not_applicable", "waived"}
                or semantic_disposition.get("consumable") is not True
            )
        ):
            missing_inputs.append("retained pr-gate semantic_review_disposition is not consumable")
        if (
            isinstance(retained_head, str)
            and retained_head
            and review_approval.get("reviewed_head") != retained_head
            and not (
                isinstance(review_approval.get("head_binding"), dict)
                and review_approval["head_binding"].get("status")
                in {"carrier-only", "generated-only", "carrier-and-generated-only"}
                and review_approval["head_binding"].get("stale") is False
            )
        ):
            missing_inputs.append("retained pr-gate reviewed_head does not bind to retained PR head")
        if merge_checkpoint.get("result") not in {None, "pass"} and not terminal_closeout_allowed:
            missing_inputs.append("retained pr-gate merge checkpoint is not pass")

    result = "pass" if not missing_inputs else "block"
    return {
        "source": "retained",
        "locator": locator,
        "schema_version": retained.get("schema_version") if isinstance(retained, dict) else None,
        "result": result,
        "summary": (
            "retained pr-gate result is fresh for the current PR head."
            if result == "pass"
            else "retained pr-gate result is missing, stale, or not an approval result."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "pr-gate",
        "freshness": "fresh" if result == "pass" else "stale",
        "bindings": {
            "pr": pr_number,
            "work_item": retained_item,
            "retained_head_sha": retained_head,
            "current_head_sha": current_head,
            "review_entry": retained_work_item.get("review_entry"),
            "reviewed_head": review_approval.get("reviewed_head"),
            "reviewed_validation_summary": review_approval.get("reviewed_validation_summary"),
            "semantic_review_disposition": semantic_disposition,
            "terminal_closeout_consumption": {
                "result": terminal_closeout_consumption.get("result"),
                "closeout_pr_allowed": closeout_specific_gate.get("closeout_pr_allowed"),
            },
        },
    }

def merge_gate_latest_validation_summary(payload: dict[str, Any]) -> str | None:
    value = payload.get("latest_validation_summary")
    if isinstance(value, str) and value.strip():
        return value
    merge_checkpoint = payload.get("merge_checkpoint") if isinstance(payload.get("merge_checkpoint"), dict) else None
    if isinstance(merge_checkpoint, dict):
        recovery = merge_checkpoint.get("recovery") if isinstance(merge_checkpoint.get("recovery"), dict) else None
        if isinstance(recovery, dict) and isinstance(recovery.get("latest_validation_summary"), str):
            return recovery["latest_validation_summary"]
    recovery = payload.get("recovery") if isinstance(payload.get("recovery"), dict) else None
    if isinstance(recovery, dict) and isinstance(recovery.get("latest_validation_summary"), str):
        return recovery["latest_validation_summary"]
    return None

def retained_merge_gate_consumption(
    *,
    retained: dict[str, Any] | None,
    locator: str | None,
    expected_item: str | None,
    pr_gate: dict[str, Any],
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    item = retained.get("item") if isinstance(retained, dict) and isinstance(retained.get("item"), dict) else {}
    retained_item = item.get("id")
    merge_checkpoint = (
        retained.get("merge_checkpoint")
        if isinstance(retained, dict) and isinstance(retained.get("merge_checkpoint"), dict)
        else retained
        if isinstance(retained, dict) and retained.get("command") == "checkpoint" and retained.get("checkpoint") == "merge"
        else {}
    )
    review_approval = pr_gate.get("review_approval") if isinstance(pr_gate.get("review_approval"), dict) else {}
    reviewed_validation_summary = review_approval.get("reviewed_validation_summary")
    retained_validation_summary = merge_gate_latest_validation_summary(retained) if isinstance(retained, dict) else None

    if not isinstance(retained, dict):
        missing_inputs.append("retained merge-gate result is unreadable")
    else:
        schema_version = retained.get("schema_version")
        command = retained.get("command")
        operation = retained.get("operation")
        checkpoint = retained.get("checkpoint")
        is_merge_ready = command == "flow" and operation == "merge-ready"
        is_checkpoint_merge = command == "checkpoint" and checkpoint == "merge"
        if schema_version is not None and schema_version not in MERGE_GATE_RESULT_SCHEMAS:
            missing_inputs.append("retained merge-gate schema_version is not recognized")
        if not is_merge_ready and not is_checkpoint_merge:
            missing_inputs.append("retained merge-gate result must be flow merge-ready or checkpoint merge")
        if retained.get("result") != "pass":
            missing_inputs.append("retained merge-gate result must be pass")
        if expected_item and retained_item and retained_item != expected_item:
            missing_inputs.append("retained merge-gate Work Item does not match expected item")
        if not isinstance(merge_checkpoint, dict) or merge_checkpoint.get("result") != "pass":
            missing_inputs.append("retained merge-gate merge checkpoint is not pass")
        if not review_validation_summary_binding(review_approval, retained_validation_summary)["matches"]:
            missing_inputs.append("retained merge-gate validation summary drifts from retained pr-gate review")

    result = "pass" if not missing_inputs else "block"
    return {
        "source": "retained",
        "locator": locator,
        "schema_version": retained.get("schema_version") if isinstance(retained, dict) else None,
        "result": result,
        "summary": (
            "retained merge-gate result is fresh for the retained pr-gate approval."
            if result == "pass"
            else "retained merge-gate result is missing, stale, or not a passing merge gate."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "merge-ready",
        "freshness": "fresh" if result == "pass" else "stale",
        "bindings": {
            "work_item": retained_item,
            "retained_validation_summary": retained_validation_summary,
            "reviewed_validation_summary": reviewed_validation_summary,
            "merge_checkpoint_result": merge_checkpoint.get("result") if isinstance(merge_checkpoint, dict) else None,
        },
    }

def current_pr_drift_readback(
    *,
    current_pr: dict[str, Any],
    pr_number: int,
    expected_head: str | None,
    merge_method: str,
    pr_gate_consumption: dict[str, Any],
    merge_gate_consumption: dict[str, Any] | None,
    required_checks: dict[str, Any],
    triggered_check_rollup: dict[str, Any],
    host_enforcement: dict[str, Any],
) -> dict[str, Any]:
    head_sha = current_pr.get("headRefOid")
    mergeability = host_mergeability_readback(current_pr.get("mergeStateStatus"))
    return {
        "mode": "drift-only",
        "summary": "controlled merge reused retained gate results and re-read only current PR and host merge-control drift surfaces.",
        "subchecks": {
            "current_pr_head": {
                "result": "pass" if not expected_head or expected_head == head_sha else "block",
                "expected_head_sha": expected_head,
                "current_head_sha": head_sha,
                "pr": pr_number,
            },
            "retained_pr_gate": pr_gate_consumption,
            "retained_merge_gate": merge_gate_consumption,
            "required_checks": required_checks,
            "triggered_check_rollup": triggered_check_rollup,
            "host_enforcement": host_enforcement,
            "mergeability": mergeability,
            "merge_method": {
                "result": "pass",
                "method": merge_method,
            },
        },
    }

def host_mergeability_readback(mergeability: Any) -> dict[str, Any]:
    status = str(mergeability).upper() if isinstance(mergeability, str) and mergeability else None
    if status in HOST_MERGEABILITY_HARD_BLOCK_STATUSES:
        return {
            "result": "block",
            "status": status,
            "interpretation": "hard_block",
            "summary": f"host mergeability is `{status}` and must be repaired before controlled merge delegation.",
        }
    if status in HOST_MERGEABILITY_DELEGATED_STATUSES:
        return {
            "result": "pass",
            "status": status,
            "interpretation": "delegated_host_policy",
            "summary": (
                "host mergeability is `BLOCKED`; Loom treats it as a host policy signal after authored "
                "review approval, required checks, PR head, and host enforcement readback pass. `gh pr merge` "
                "remains the final host delegation point."
            ),
        }
    if status:
        return {
            "result": "pass",
            "status": status,
            "interpretation": "host_readback",
            "summary": f"host mergeability is `{status}`.",
        }
    return {
        "result": "pass",
        "status": None,
        "interpretation": "not_present",
        "summary": "host mergeability is not present in the PR fixture/readback.",
    }

def governance_capability_profile_payload(
    *,
    mode: str,
    host_enforcement: dict[str, Any],
    allow_advisory: bool,
    allow_high_risk_advisory: bool,
    change_class: str | None,
) -> dict[str, Any]:
    normalized_change_class = str(change_class or "").strip().lower().replace("-", "_")
    missing_inputs: list[str] = []
    host_required = host_enforcement.get("required") is True
    host_readable = (
        host_enforcement.get("branch_protection_readable") is True
        or host_enforcement.get("ruleset_readable") is True
    )
    host_trust_verdict = host_enforcement.get("trust_verdict")

    if mode == "host-enforced":
        if not host_required:
            missing_inputs.append(f"required check `{PR_MERGE_GATE_CHECK_NAME}` is not host-enforced")
        if not host_readable:
            missing_inputs.append("branch protection or ruleset readback is unavailable")
        return {
            "schema_version": GOVERNANCE_CAPABILITY_PROFILE_SCHEMA,
            "mode": "host-enforced",
            "result": "pass" if not missing_inputs else "block",
            "assurance": "strong" if host_trust_verdict == "strong" else "limited",
            "risk_label": None,
            "host_enforcement_status": "host_enforced" if not missing_inputs else "unverified",
            "explicit_opt_in": False,
            "change_class": normalized_change_class or None,
            "summary": (
                "host-enforced governance is proven by host required checks; identity assurance remains limited unless trusted host readback proves a distinct identity."
                if not missing_inputs
                else "host-enforced governance cannot be proven from host readback."
            ),
            "missing_inputs": missing_inputs,
        }

    if mode != "advisory/local-enforced":
        return {
            "schema_version": GOVERNANCE_CAPABILITY_PROFILE_SCHEMA,
            "mode": mode,
            "result": "block",
            "assurance": "unknown",
            "risk_label": "invalid",
            "host_enforcement_status": "unknown",
            "explicit_opt_in": allow_advisory,
            "change_class": normalized_change_class or None,
            "summary": "unknown governance capability profile.",
            "missing_inputs": [f"unknown governance mode: {mode}"],
        }

    if not allow_advisory:
        missing_inputs.append("advisory/local-enforced requires --allow-advisory-local-enforced")
    if normalized_change_class in HIGH_RISK_GOVERNANCE_CHANGE_CLASSES and not allow_high_risk_advisory:
        missing_inputs.append(f"high-risk change class `{normalized_change_class}` cannot use advisory/local-enforced without explicit approval")
    return {
        "schema_version": GOVERNANCE_CAPABILITY_PROFILE_SCHEMA,
        "mode": "advisory/local-enforced",
        "result": "pass" if not missing_inputs else "block",
        "assurance": "low",
        "risk_label": "low_assurance",
        "host_enforcement_status": "not_host_enforced" if not host_required else "host_enforced_but_advisory_selected",
        "explicit_opt_in": allow_advisory,
        "high_risk_approval": allow_high_risk_advisory,
        "change_class": normalized_change_class or None,
        "summary": (
            "advisory/local-enforced governance is explicitly selected; normal review, PR gate, CI rollup, and head drift checks still apply."
            if not missing_inputs
            else "advisory/local-enforced governance is blocked until explicit approval evidence is supplied."
        ),
        "missing_inputs": missing_inputs,
    }

def controlled_merge_payload(
    *,
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    owner: str | None,
    repo_name: str | None,
    pr_number: int,
    head_sha: str | None,
    merge_method: str,
    delete_branch: bool,
    execute: bool,
    pr_payload_file: str | None,
    status_checks_file: str | None,
    branch_protection_file: str | None,
    ruleset_file: str | None,
    pr_gate_result_file: str | None,
    merge_gate_result_file: str | None,
    governance_mode: str = "host-enforced",
    allow_advisory_local_enforced: bool = False,
    allow_high_risk_advisory: bool = False,
    change_class: str | None = None,
    issue_number: int | None = None,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    retained_results: dict[str, Any] = {
        "pr_gate": {"source": "live", "locator": None, "consumption": None},
        "merge_gate": {"source": "live", "locator": None, "consumption": None},
    }
    if pr_gate_result_file:
        pr_payload_raw, effective_pr, pr_errors, _inferences = load_pr_payload_for_gate(
            target_root=target_root,
            owner=owner,
            repo_name=repo_name,
            pr_number=pr_number,
            head_sha=head_sha,
            branch_name=None,
            pr_payload_file=pr_payload_file,
        )
        pr_payload = pr_payload_raw if isinstance(pr_payload_raw, dict) else {}
        missing_inputs = [f"current PR readback: {message}" for message in pr_errors]
        if effective_pr != pr_number:
            missing_inputs.append("current PR readback does not match requested PR")
        if not pr_payload:
            missing_inputs.append("current PR readback is unavailable")
        else:
            if pr_payload.get("state") != "OPEN":
                missing_inputs.append(f"current PR state must be OPEN before controlled merge: {pr_payload.get('state')}")
            if pr_payload.get("isDraft") is True:
                missing_inputs.append("current PR is draft")
            current_head = pr_payload.get("headRefOid")
            if head_sha and current_head and head_sha != current_head:
                missing_inputs.append("current PR head does not match --head-sha")
        retained_pr_gate, retained_pr_gate_errors = load_retained_result_file(
            target_root,
            pr_gate_result_file,
            label="retained pr-gate result",
        )
        missing_inputs.extend(f"retained pr-gate: {message}" for message in retained_pr_gate_errors)
        pr_gate = retained_pr_gate or {
            "command": "pr-gate",
            "operation": "check",
            "schema_version": PR_MERGE_GATE_SCHEMA,
            "result": "block",
            "missing_inputs": retained_pr_gate_errors,
            "fallback_to": "pr-gate",
            "pr": {"number": pr_number, "head_sha": pr_payload.get("headRefOid")},
            "work_item": {"id": expected_item},
            "review_approval": {},
            "merge_checkpoint": {},
        }
        result = pr_gate.get("result") if pr_gate.get("result") in {"pass", "block", "fallback"} else "block"
        fallback_to = pr_gate.get("fallback_to")
        pr_gate_consumption = retained_pr_gate_consumption(
            retained=retained_pr_gate,
            locator=pr_gate_result_file,
            current_pr=pr_payload,
            expected_item=expected_item,
            pr_number=pr_number,
        )
        retained_results["pr_gate"] = {
            "source": "retained",
            "locator": pr_gate_result_file,
            "consumption": pr_gate_consumption,
        }
        if pr_gate_consumption["result"] != "pass":
            result = "block"
            fallback_to = pr_gate_consumption["fallback_to"]
            missing_inputs.extend(f"retained pr-gate: {message}" for message in pr_gate_consumption["missing_inputs"])
    else:
        pr_gate = pr_gate_payload(
            target_root=target_root,
            output_relative=output_relative,
            expected_item=expected_item,
            owner=owner,
            repo_name=repo_name,
            issue_number=issue_number,
            pr_number=pr_number,
            head_sha=head_sha,
            branch_name=None,
            pr_payload_file=pr_payload_file,
        )
        missing_inputs = [f"pr-gate: {message}" for message in pr_gate.get("missing_inputs", [])]
        result = pr_gate.get("result")
        fallback_to = pr_gate.get("fallback_to")
        pr_payload = pr_gate.get("pr") if isinstance(pr_gate.get("pr"), dict) else {}
        retained_results["pr_gate"]["consumption"] = {
            "source": "live",
            "result": pr_gate.get("result"),
            "summary": "controlled merge evaluated pr-gate inline because no retained pr-gate result locator was provided.",
            "missing_inputs": pr_gate.get("missing_inputs", []),
            "fallback_to": pr_gate.get("fallback_to"),
            "freshness": "fresh" if pr_gate.get("result") == "pass" else "stale",
        }

    merge_gate_consumption: dict[str, Any] | None = None
    if merge_gate_result_file:
        retained_merge_gate, retained_merge_gate_errors = load_retained_result_file(
            target_root,
            merge_gate_result_file,
            label="retained merge-gate result",
        )
        missing_inputs.extend(f"retained merge-gate: {message}" for message in retained_merge_gate_errors)
        merge_gate_consumption = retained_merge_gate_consumption(
            retained=retained_merge_gate,
            locator=merge_gate_result_file,
            expected_item=expected_item,
            pr_gate=pr_gate,
        )
        retained_results["merge_gate"] = {
            "source": "retained",
            "locator": merge_gate_result_file,
            "consumption": merge_gate_consumption,
        }
        if merge_gate_consumption["result"] != "pass":
            result = "block"
            fallback_to = merge_gate_consumption["fallback_to"]
            missing_inputs.extend(f"retained merge-gate: {message}" for message in merge_gate_consumption["missing_inputs"])
    else:
        merge_gate_consumption = {
            "source": "inline-pr-gate",
            "result": pr_gate.get("merge_checkpoint", {}).get("result") if isinstance(pr_gate.get("merge_checkpoint"), dict) else None,
            "summary": "controlled merge reused the merge checkpoint embedded in the current pr-gate evaluation.",
            "missing_inputs": pr_gate.get("merge_checkpoint", {}).get("missing_inputs", []) if isinstance(pr_gate.get("merge_checkpoint"), dict) else [],
            "fallback_to": pr_gate.get("merge_checkpoint", {}).get("fallback_to") if isinstance(pr_gate.get("merge_checkpoint"), dict) else None,
        }
        retained_results["merge_gate"]["consumption"] = merge_gate_consumption

    base_ref = pr_payload.get("baseRefName") if isinstance(pr_payload, dict) else None

    protection_payload, protection_errors = load_optional_json_fixture(
        target_root,
        branch_protection_file,
        label="branch protection fixture",
    )
    if protection_payload is None and not protection_errors and owner and repo_name and isinstance(base_ref, str) and base_ref:
        protection_payload, protection_errors = gh_rest_json(
            target_root,
            f"repos/{owner}/{repo_name}/branches/{quote(base_ref, safe='')}/protection",
        )
    if protection_errors:
        missing_inputs.extend(f"branch protection: {message}" for message in protection_errors)

    ruleset_payload, ruleset_errors = load_optional_json_fixture(
        target_root,
        ruleset_file,
        label="branch rules/ruleset fixture",
    )
    if ruleset_payload is None and not ruleset_errors and owner and repo_name and isinstance(base_ref, str) and base_ref:
        ruleset_payload, ruleset_errors = gh_rest_list(
            target_root,
            f"repos/{owner}/{repo_name}/rules/branches/{quote(base_ref, safe='')}",
        )
    if ruleset_errors:
        missing_inputs.extend(f"branch rules/ruleset: {message}" for message in ruleset_errors)

    status_payload, status_errors = load_optional_json_fixture(
        target_root,
        status_checks_file,
        label="status checks fixture",
    )
    if status_payload is None and not status_errors:
        pr_view_args = ["pr", "view", str(pr_number), "--json", "statusCheckRollup"]
        if owner and repo_name:
            pr_view_args.extend(["--repo", f"{owner}/{repo_name}"])
        status_payload, status_errors = gh_json(
            target_root,
            pr_view_args,
        )
    if status_errors:
        missing_inputs.extend(f"status checks: {message}" for message in status_errors)

    protection_contexts = required_status_contexts_from_protection(protection_payload)
    ruleset_contexts = required_status_contexts_from_branch_rules(ruleset_payload)
    required_contexts = sorted(set(protection_contexts + ruleset_contexts))
    required_checks = required_check_status_payload(
        status_payload.get("statusCheckRollup") if isinstance(status_payload, dict) else status_payload,
        required_contexts,
    )
    triggered_check_rollup = triggered_check_rollup_payload(
        status_payload.get("statusCheckRollup") if isinstance(status_payload, dict) else status_payload,
    )
    if required_checks["result"] != "pass":
        labels = {"missing": "missing", "pending": "pending", "failing": "failing"}
        for key in ("missing", "pending", "failing"):
            for context in required_checks[key]:
                missing_inputs.append(f"required check `{context}` is {labels[key]}")
    if triggered_check_rollup["result"] != "pass":
        missing_inputs.extend(str(message) for message in triggered_check_rollup.get("missing_inputs", []))
    host_enforcement = {
        "stable_check_name": PR_MERGE_GATE_CHECK_NAME,
        "required_contexts": required_contexts,
        "required": PR_MERGE_GATE_CHECK_NAME in required_contexts,
        "branch_protection_readable": protection_payload is not None,
        "branch_protection_required_contexts": protection_contexts,
        "ruleset_readable": ruleset_payload is not None,
        "ruleset_required_contexts": ruleset_contexts,
    }
    governance_capability_profile = governance_capability_profile_payload(
        mode=governance_mode,
        host_enforcement=host_enforcement,
        allow_advisory=allow_advisory_local_enforced,
        allow_high_risk_advisory=allow_high_risk_advisory,
        change_class=change_class,
    )
    if governance_capability_profile["result"] != "pass":
        missing_inputs.extend(
            f"governance capability profile: {message}"
            for message in governance_capability_profile.get("missing_inputs", [])
        )
    mergeability = host_mergeability_readback(pr_payload.get("mergeStateStatus") if isinstance(pr_payload, dict) else None)
    if mergeability["result"] == "block":
        missing_inputs.append(str(mergeability["summary"]))

    merge_result: dict[str, Any] = {
        "attempted": False,
        "executed": False,
        "dry_run": not execute,
        "method": merge_method,
        "delete_branch": delete_branch,
    }
    if missing_inputs and result == "pass":
        result = "block"
        fallback_to = fallback_to or "merge"
    drift_readback = current_pr_drift_readback(
        current_pr=pr_payload if isinstance(pr_payload, dict) else {},
        pr_number=pr_number,
        expected_head=head_sha or pr_gate.get("pr", {}).get("head_sha") if isinstance(pr_gate.get("pr"), dict) else head_sha,
        merge_method=merge_method,
        pr_gate_consumption=retained_results["pr_gate"]["consumption"],
        merge_gate_consumption=merge_gate_consumption,
        required_checks=required_checks,
        triggered_check_rollup=triggered_check_rollup,
        host_enforcement=host_enforcement,
    )

    merge_ready_consumption_missing: list[str] = []
    if pr_gate.get("result") != "pass":
        merge_ready_consumption_missing.append("fresh Loom merge-ready / PR merge gate allow result")
    pr_gate_consumption = retained_results["pr_gate"]["consumption"]
    if isinstance(pr_gate_consumption, dict) and pr_gate_consumption.get("result") != "pass":
        merge_ready_consumption_missing.append("fresh retained PR gate consumption")
    if required_checks["result"] != "pass":
        merge_ready_consumption_missing.append("required checks readback")
    if triggered_check_rollup["result"] != "pass":
        merge_ready_consumption_missing.append("triggered checks readback")
    if governance_capability_profile["result"] != "pass":
        merge_ready_consumption_missing.append("governance capability profile")
    pr_head = (
        pr_payload.get("headRefOid") or pr_payload.get("headRefName")
        if isinstance(pr_payload, dict)
        else None
    )
    if head_sha and isinstance(pr_payload, dict):
        actual_head = pr_payload.get("headRefOid") or pr_payload.get("head_sha")
        if isinstance(actual_head, str) and actual_head and actual_head != head_sha:
            merge_ready_consumption_missing.append("PR head drift after Loom merge-ready allow result")
    controlled_merge_consumption = {
        "schema_version": CONTROLLED_MERGE_CONSUMPTION_SCHEMA,
        "result": "pass" if not merge_ready_consumption_missing else "block",
        "summary": (
            "controlled merge wrapper consumed Loom merge-ready allow result and host readback."
            if not merge_ready_consumption_missing
            else "controlled merge wrapper cannot consume Loom merge-ready allow result safely."
        ),
        "missing_inputs": merge_ready_consumption_missing,
        "fallback_to": None if not merge_ready_consumption_missing else "merge_ready",
        "source_authority": "loom merge-ready result",
        "wrapper_role": "host_action_adapter",
        "merge_ready_required": True,
        "head_sha": head_sha,
        "observed_pr_head": pr_head,
        "merge_method": merge_method,
        "required_checks_snapshot": required_checks,
        "triggered_check_rollup": triggered_check_rollup,
        "fail_closed_conditions": [
            "missing-allow-result",
            "stale-head",
            "target-mismatch",
            "required-checks-drift",
            "triggered-checks-drift",
            "malformed-merge-ready-result",
        ],
    }
    if controlled_merge_consumption["result"] != "pass":
        result = "block"
        fallback_to = controlled_merge_consumption["fallback_to"] or fallback_to or "merge_ready"
        missing_inputs.extend(
            f"controlled merge consumption: {message}"
            for message in controlled_merge_consumption["missing_inputs"]
        )
    if result == "pass" and execute:
        command = ["gh", "pr", "merge", str(pr_number), f"--{merge_method}"]
        if delete_branch:
            command.append("--delete-branch")
        completed = run_process(command, target_root)
        merge_result["attempted"] = True
        merge_result["command"] = command
        merge_result["returncode"] = completed.returncode
        merge_result["stdout"] = completed.stdout.strip()
        merge_result["stderr"] = completed.stderr.strip()
        if completed.returncode == 0:
            merge_result["executed"] = True
        else:
            result = "block"
            fallback_to = "merge"
            missing_inputs.append(completed.stderr.strip() or completed.stdout.strip() or "gh pr merge failed")

    return {
        "command": "controlled-merge",
        "operation": "merge" if execute else "check",
        "schema_version": CONTROLLED_MERGE_SCHEMA,
        "result": result,
        "summary": (
            "controlled merge preconditions passed and host merge was delegated."
            if result == "pass" and execute
            else "controlled merge preconditions passed; host merge was not executed."
            if result == "pass"
            else "controlled merge is blocked before host merge delegation."
        ),
        "missing_inputs": sorted(set(str(message) for message in missing_inputs)),
        "fallback_to": fallback_to,
        "repository": {"owner": owner, "name": repo_name},
        "pr_gate": pr_gate,
        "retained_results": retained_results,
        "drift_readback": drift_readback,
        "required_checks": required_checks,
        "triggered_check_rollup": triggered_check_rollup,
        "triggered_checks": triggered_check_rollup.get("triggered_checks", []),
        "host_enforcement": host_enforcement,
        "governance_capability_profile": governance_capability_profile,
        "controlled_merge_consumption": controlled_merge_consumption,
        "merge": merge_result,
    }

def handle_controlled_merge(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    return emit(
        controlled_merge_payload(
            target_root=target_root,
            output_relative=args.output,
            expected_item=args.item,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
            pr_number=args.pr,
            head_sha=args.head_sha,
            merge_method=args.merge_method,
            delete_branch=args.delete_branch,
            execute=args.execute and args.operation == "merge",
            pr_payload_file=args.pr_payload_file,
            status_checks_file=args.status_checks_file,
            branch_protection_file=args.branch_protection_file,
            ruleset_file=args.ruleset_file,
            pr_gate_result_file=args.pr_gate_result_file,
            merge_gate_result_file=args.merge_gate_result_file,
            governance_mode=args.governance_mode,
            allow_advisory_local_enforced=args.allow_advisory_local_enforced,
            allow_high_risk_advisory=args.allow_high_risk_advisory,
            change_class=args.change_class,
        )
    )

def gate_repair_pr_value(record: dict[str, Any], dotted_path: str) -> Any:
    value: Any = record
    for part in dotted_path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value

def gate_repair_pr_record_missing_inputs(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["gate repair PR evidence must be a JSON object"]
    missing: list[str] = []
    if record.get("schema_version") != GATE_REPAIR_PR_SCHEMA:
        missing.append(f"schema_version must be `{GATE_REPAIR_PR_SCHEMA}`")
    if record.get("result") != "pass":
        missing.append("result must be `pass`")
    for path in ("reason", "review_evidence_locator"):
        value = gate_repair_pr_value(record, path)
        if not isinstance(value, str) or not value.strip():
            missing.append(path)
    pr_number = gate_repair_pr_value(record, "pr.number")
    if not isinstance(pr_number, int) or isinstance(pr_number, bool):
        missing.append("pr.number")
    for path in ("pr.head_sha", "pr.branch"):
        value = gate_repair_pr_value(record, path)
        if not isinstance(value, str) or not value.strip():
            missing.append(path)
    for path in ("broken_gate_checks", "new_gate_checks", "still_required_checks"):
        value = gate_repair_pr_value(record, path)
        if not isinstance(value, list) or not value:
            missing.append(path)
    for path in ("enforcement_before", "enforcement_after", "restored_readback"):
        value = gate_repair_pr_value(record, path)
        if not isinstance(value, dict) or not value:
            missing.append(path)
    restored_readback = gate_repair_pr_value(record, "restored_readback")
    if isinstance(restored_readback, dict):
        if restored_readback.get("result") != "pass":
            missing.append("restored_readback.result must be `pass`")
        restored_missing = restored_readback.get("missing_inputs")
        if isinstance(restored_missing, list) and restored_missing:
            missing.append("restored_readback.missing_inputs must be empty")
    still_required_checks = gate_repair_pr_value(record, "still_required_checks")
    if isinstance(still_required_checks, list):
        for index, check in enumerate(still_required_checks):
            if not isinstance(check, dict):
                missing.append(f"still_required_checks[{index}] must be an object")
                continue
            if check.get("status") != "pass":
                missing.append(f"still_required_checks[{index}].status must be `pass`")
    review_evidence = gate_repair_pr_value(record, "review_evidence")
    if isinstance(review_evidence, dict):
        if review_evidence.get("pr_gate_result") != "pass":
            missing.append("review_evidence.pr_gate_result must be `pass`")
        if review_evidence.get("approval_status") != "approved":
            missing.append("review_evidence.approval_status must be `approved`")
    return dedupe_strings(missing)

def gate_repair_pr_enforcement_payload(payload: Any, *, locator: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "schema_version": "loom-gate-repair-pr-enforcement-readback/v1",
            "source_locator": locator,
            "required_contexts": [],
            "missing_inputs": ["enforcement readback must be a JSON object"],
        }
    if isinstance(payload.get("enforcement_before"), dict):
        payload = payload["enforcement_before"]
    elif isinstance(payload.get("enforcement_after"), dict):
        payload = payload["enforcement_after"]

    direct_contexts = payload.get("required_contexts")
    contexts = [str(context) for context in direct_contexts if isinstance(context, str) and context.strip()] if isinstance(direct_contexts, list) else []
    branch_protection_payload = payload.get("branch_protection") if isinstance(payload.get("branch_protection"), dict) else payload
    ruleset_payload = payload.get("ruleset") if "ruleset" in payload else payload
    protection_contexts = required_status_contexts_from_protection(branch_protection_payload)
    ruleset_contexts = required_status_contexts_from_branch_rules(ruleset_payload)
    required_contexts = sorted(set(contexts + protection_contexts + ruleset_contexts))
    return {
        "schema_version": "loom-gate-repair-pr-enforcement-readback/v1",
        "source_locator": locator,
        "required_contexts": required_contexts,
        "branch_protection_required_contexts": protection_contexts,
        "ruleset_required_contexts": ruleset_contexts,
        "raw_schema_version": payload.get("schema_version"),
        "missing_inputs": [],
    }

def gate_repair_pr_still_required_checks(
    *,
    required_contexts: list[str],
    required_checks: dict[str, Any],
    pr_gate: dict[str, Any],
    review_locator: str | None,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    missing = set(required_checks.get("missing", [])) if isinstance(required_checks.get("missing"), list) else set()
    pending = set(required_checks.get("pending", [])) if isinstance(required_checks.get("pending"), list) else set()
    failing = set(required_checks.get("failing", [])) if isinstance(required_checks.get("failing"), list) else set()
    for context in required_contexts:
        status = "missing" if context in missing else "pending" if context in pending else "failing" if context in failing else "pass"
        checks.append({"name": context, "source": "host_enforcement", "status": status})
    review_approval = pr_gate.get("review_approval") if isinstance(pr_gate.get("review_approval"), dict) else {}
    checks.append(
        {
            "name": "semantic_review",
            "source": review_locator,
            "status": "pass" if pr_gate.get("result") == "pass" and review_approval.get("status") == "approved" else "block",
        }
    )
    return checks

def gate_repair_pr_existing_record(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, [f"{GATE_REPAIR_PR_LOCATOR} is missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid {GATE_REPAIR_PR_LOCATOR}: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{GATE_REPAIR_PR_LOCATOR} must be a JSON object"]
    return payload, []

def gate_repair_pr_payload(args: argparse.Namespace) -> dict[str, Any]:
    target_root = resolve_target_arg(args.target)
    record_path = target_root / GATE_REPAIR_PR_LOCATOR
    existing_record, existing_errors = gate_repair_pr_existing_record(record_path)
    if not args.record:
        missing_inputs = existing_errors if existing_record is None else gate_repair_pr_record_missing_inputs(existing_record)
        result = "pass" if not missing_inputs else "block"
        return {
            "command": "gate-repair-pr",
            "operation": "validate",
            "schema_version": GATE_REPAIR_PR_SCHEMA,
            "result": result,
            "summary": "gate repair PR evidence is valid." if result == "pass" else "gate repair PR evidence is missing or incomplete.",
            "missing_inputs": missing_inputs,
            "fallback_to": None if result == "pass" else "loom gate repair-pr --target <repo> --record --json",
            "target": str(target_root),
            "record_locator": GATE_REPAIR_PR_LOCATOR,
            "record_validation": {"result": result, "missing_inputs": missing_inputs},
            "mutates": False,
            "host_mutations": False,
            "ruleset_mutation": {"attempted": False, "commands": []},
        }

    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = args.owner or detected_owner
    repo_name = args.repo_name or detected_repo
    current_head = args.head_sha or git_head_sha(target_root)
    current_branch = args.branch or git_branch(target_root)
    pr_payload_raw, effective_pr, pr_errors, inferences = load_pr_payload_for_gate(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        pr_number=args.pr,
        head_sha=current_head,
        branch_name=current_branch,
        pr_payload_file=args.pr_payload_file,
    )
    pr_payload = pr_payload_raw if isinstance(pr_payload_raw, dict) else {}
    head_sha = args.head_sha or pr_payload.get("headRefOid") or current_head
    branch = args.branch or pr_payload.get("headRefName") or current_branch
    missing_inputs = [f"pr readback: {message}" for message in pr_errors]
    if effective_pr is None:
        missing_inputs.append("pr.number")
    if not isinstance(head_sha, str) or not head_sha.strip():
        missing_inputs.append("pr.head_sha")
    if not isinstance(branch, str) or not branch.strip():
        missing_inputs.append("pr.branch")

    if args.enforcement_before_file:
        before_raw, before_errors = load_optional_json_fixture(target_root, args.enforcement_before_file, label="enforcement-before readback")
        missing_inputs.extend(f"enforcement-before: {message}" for message in before_errors)
        enforcement_before = gate_repair_pr_enforcement_payload(before_raw, locator=args.enforcement_before_file)
    elif existing_record is not None:
        enforcement_before = gate_repair_pr_enforcement_payload(existing_record, locator=f"{GATE_REPAIR_PR_LOCATOR}:enforcement_before")
    else:
        enforcement_before = {
            "schema_version": "loom-gate-repair-pr-enforcement-readback/v1",
            "source_locator": None,
            "required_contexts": [],
            "missing_inputs": ["enforcement-before readback"],
        }
        missing_inputs.append("enforcement-before readback")

    if effective_pr is None:
        controlled: dict[str, Any] = {
            "result": "block",
            "missing_inputs": ["pr.number"],
            "host_enforcement": {},
            "required_checks": {},
            "triggered_check_rollup": {},
            "controlled_merge_consumption": {},
            "pr_gate": {},
        }
    else:
        controlled = controlled_merge_payload(
            target_root=target_root,
            output_relative=args.output,
            expected_item=args.item,
            owner=owner,
            repo_name=repo_name,
            pr_number=effective_pr,
            head_sha=head_sha if isinstance(head_sha, str) else None,
            merge_method="squash",
            delete_branch=False,
            execute=False,
            pr_payload_file=args.pr_payload_file,
            status_checks_file=args.status_checks_file,
            branch_protection_file=args.branch_protection_file,
            ruleset_file=args.ruleset_file,
            pr_gate_result_file=args.pr_gate_result_file,
            merge_gate_result_file=args.merge_gate_result_file,
        )

    host_enforcement = controlled.get("host_enforcement") if isinstance(controlled.get("host_enforcement"), dict) else {}
    required_contexts = [str(context) for context in host_enforcement.get("required_contexts", []) if isinstance(context, str)]
    enforcement_after = {
        "schema_version": "loom-gate-repair-pr-enforcement-readback/v1",
        "source_locator": "controlled-merge.host_enforcement",
        "required_contexts": required_contexts,
        "branch_protection_required_contexts": host_enforcement.get("branch_protection_required_contexts", []),
        "ruleset_required_contexts": host_enforcement.get("ruleset_required_contexts", []),
        "branch_protection_readable": host_enforcement.get("branch_protection_readable"),
        "ruleset_readable": host_enforcement.get("ruleset_readable"),
    }
    before_contexts = set(enforcement_before.get("required_contexts", []))
    new_contexts = sorted(set(required_contexts) - before_contexts)
    broken_gate_checks = [
        {"name": context, "before": "not_required", "after": "required", "source": "enforcement-before/after readback"}
        for context in new_contexts
    ]
    new_gate_checks = [
        {"name": context, "source": "host_enforcement", "status": "newly_required"}
        for context in new_contexts
    ]
    pr_gate = controlled.get("pr_gate") if isinstance(controlled.get("pr_gate"), dict) else {}
    work_item = pr_gate.get("work_item") if isinstance(pr_gate.get("work_item"), dict) else {}
    review_locator = work_item.get("review_entry") if isinstance(work_item.get("review_entry"), str) else None
    required_checks = controlled.get("required_checks") if isinstance(controlled.get("required_checks"), dict) else {}
    still_required_checks = gate_repair_pr_still_required_checks(
        required_contexts=required_contexts,
        required_checks=required_checks,
        pr_gate=pr_gate,
        review_locator=review_locator,
    )
    restored_readback = {
        "schema_version": "loom-gate-repair-pr-restored-readback/v1",
        "result": "pass" if controlled.get("result") == "pass" else "block",
        "source": "controlled-merge",
        "missing_inputs": controlled.get("missing_inputs", []),
        "required_checks": required_checks,
        "triggered_check_rollup": controlled.get("triggered_check_rollup", {}),
        "controlled_merge_consumption": controlled.get("controlled_merge_consumption", {}),
    }
    reason = (
        args.reason
        or (existing_record or {}).get("reason")
        or "repair PR records restored gate enforcement evidence without mutating GitHub rulesets"
    )
    record = {
        "schema_version": GATE_REPAIR_PR_SCHEMA,
        "command": "gate-repair-pr",
        "result": "pass" if controlled.get("result") == "pass" else "block",
        "recorded_at": utc_now_iso(),
        "target": str(target_root),
        "repository": {"owner": owner, "name": repo_name},
        "pr": {"number": effective_pr, "head_sha": head_sha, "branch": branch},
        "reason": reason,
        "broken_gate_checks": broken_gate_checks,
        "new_gate_checks": new_gate_checks,
        "still_required_checks": still_required_checks,
        "review_evidence_locator": review_locator,
        "review_evidence": {
            "locator": review_locator,
            "pr_gate_result": pr_gate.get("result"),
            "semantic_review_skipped": False,
            "approval_status": pr_gate.get("review_approval", {}).get("status") if isinstance(pr_gate.get("review_approval"), dict) else None,
        },
        "enforcement_before": enforcement_before,
        "enforcement_after": enforcement_after,
        "restored_readback": restored_readback,
        "bypass_policy": {
            "evidence_only": True,
            "does_not_skip_semantic_review": True,
            "does_not_mutate_github_rulesets": True,
            "does_not_replace": ["semantic_review", "pr_gate", "controlled_merge", "host_required_checks"],
        },
        "host_mutations": False,
        "ruleset_mutation": {"attempted": False, "commands": []},
    }
    record_missing = gate_repair_pr_record_missing_inputs(record)
    if controlled.get("result") != "pass":
        missing_inputs.extend(f"restored readback: {message}" for message in controlled.get("missing_inputs", []))
    missing_inputs.extend(record_missing)
    missing_inputs = dedupe_strings([str(message) for message in missing_inputs if str(message).strip()])
    result = "pass" if not missing_inputs else "block"
    record_artifact: dict[str, Any] = {"result": "not_written", "locator": GATE_REPAIR_PR_LOCATOR}
    readback_validation = {"result": result, "missing_inputs": record_missing}
    if result == "pass":
        write_json_file(record_path, record)
        readback, readback_errors = gate_repair_pr_existing_record(record_path)
        readback_missing = readback_errors if readback is None else gate_repair_pr_record_missing_inputs(readback)
        readback_validation = {"result": "pass" if not readback_missing else "block", "missing_inputs": readback_missing}
        if readback_missing:
            result = "block"
            missing_inputs.extend(readback_missing)
        record_artifact = {
            "result": "pass" if not readback_missing else "block",
            "locator": GATE_REPAIR_PR_LOCATOR,
            "mutates": "repo-local-companion-evidence-only",
            "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest() if record_path.exists() else None,
        }

    return {
        "command": "gate-repair-pr",
        "operation": "record",
        "schema_version": GATE_REPAIR_PR_SCHEMA,
        "result": result,
        "summary": (
            "gate repair PR evidence was recorded and validated."
            if result == "pass"
            else "gate repair PR evidence is missing required audit inputs."
        ),
        "missing_inputs": dedupe_strings(missing_inputs),
        "fallback_to": None if result == "pass" else "refresh_gate_repair_pr_evidence",
        "target": str(target_root),
        "record_locator": GATE_REPAIR_PR_LOCATOR,
        "record": record,
        "record_validation": readback_validation,
        "record_artifact": record_artifact,
        "controlled_merge": controlled,
        "inferences": inferences,
        "mutates": result == "pass",
        "host_mutations": False,
        "ruleset_mutation": {"attempted": False, "commands": []},
        "semantic_review": {
            "skipped": False,
            "required": True,
            "evidence_locator": review_locator,
            "pr_gate_result": pr_gate.get("result"),
        },
    }

def handle_gate_repair_pr(args: argparse.Namespace) -> int:
    return emit(gate_repair_pr_payload(args))

def text_mentions_issue(text: object, issue_number: int) -> bool:
    if not isinstance(text, str):
        return False
    pattern = re.compile(rf"(?i)(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?|related)\s+#?{issue_number}\b|#{issue_number}\b")
    return bool(pattern.search(text))

def github_compare_contains_commit(
    root: Path,
    *,
    owner: str,
    repo_name: str,
    merge_commit_sha: str,
    target_branch: str,
) -> bool:
    payload, errors = gh_rest_json(
        root,
        f"repos/{owner}/{repo_name}/compare/{quote(merge_commit_sha, safe='')}...{quote(target_branch, safe='')}",
    )
    if errors or payload is None:
        return False
    return payload.get("status") in {"ahead", "identical"}

def contains_merged_commit(
    root: Path,
    merge_commit_sha: str,
    target_branch: str = "main",
    *,
    owner: str | None = None,
    repo_name: str | None = None,
) -> bool:
    target_branch = target_branch.strip()
    if not target_branch:
        return False
    run_git(
        root,
        [
            "fetch",
            "--no-write-fetch-head",
            "origin",
            f"refs/heads/{target_branch}:refs/remotes/origin/{target_branch}",
        ],
    )
    candidate_refs = (
        target_branch,
        f"origin/{target_branch}",
        f"refs/remotes/origin/{target_branch}",
    )
    for ref in candidate_refs:
        contains = run_git(root, ["merge-base", "--is-ancestor", merge_commit_sha, ref])
        if contains is not None and contains.returncode == 0:
            return True
    if owner is None or repo_name is None:
        detected_owner, detected_repo = detect_github_repo(root)
        owner = owner or detected_owner
        repo_name = repo_name or detected_repo
    if not owner or not repo_name:
        return False
    return github_compare_contains_commit(
        root,
        owner=owner,
        repo_name=repo_name,
        merge_commit_sha=merge_commit_sha,
        target_branch=target_branch,
    )

def make_reconciliation_finding(
    *,
    kind: str,
    severity: str,
    subject: str,
    evidence: dict[str, Any],
    recommended_action: str,
    category: str = "drift",
    fallback_to: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    if fallback_to is None:
        fallback_to = "manual-reconciliation" if severity == "block" else "reconciliation-sync"
    return {
        "category": category,
        "kind": kind,
        "severity": severity,
        "subject": subject,
        "evidence": evidence,
        "recommended_action": recommended_action,
        "fallback_to": fallback_to,
        **extra,
    }

def suite_validation_blocking_entries(validation: dict[str, Any]) -> list[dict[str, Any]]:
    payload = validation.get("payload") if isinstance(validation.get("payload"), dict) else {}
    nested_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for source, source_payload in (("payload", payload), ("nested_payload", nested_payload)):
        blocking_gaps = source_payload.get("blocking_gaps")
        if not isinstance(blocking_gaps, list):
            continue
        for gap in blocking_gaps:
            if not isinstance(gap, dict):
                continue
            failure_kind = str(gap.get("failure_kind") or "")
            source_locator = str(gap.get("source_locator") or "")
            gap_id = str(gap.get("id") or "")
            key = (failure_kind, source_locator, gap_id)
            if key in seen:
                continue
            seen.add(key)
            entries.append({**gap, "source_payload": source})
    return entries

def suite_reconciliation_fallback(value: Any, default: str) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, list):
        for entry in value:
            if isinstance(entry, str) and entry:
                return entry
    return default

def suite_gate_reconciliation_findings(
    suite_gate_validation: dict[str, Any],
    *,
    subject: str,
) -> list[dict[str, Any]]:
    result = suite_gate_validation.get("result")
    if result in {"pass", "not_applicable"}:
        return []

    findings: list[dict[str, Any]] = []
    validations = (
        suite_gate_validation.get("validations")
        if isinstance(suite_gate_validation.get("validations"), dict)
        else {}
    )
    for domain in ("evidence", "carrier"):
        validation = validations.get(domain) if isinstance(validations.get(domain), dict) else None
        if validation is None:
            continue
        for gap in suite_validation_blocking_entries(validation):
            failure_kind = str(gap.get("failure_kind") or "")
            mapping = SUITE_RECONCILIATION_FINDINGS.get(failure_kind)
            if mapping is None:
                continue
            fallback_to = suite_reconciliation_fallback(
                gap.get("fallback_to") or validation.get("fallback_to"),
                f"suite {domain} validate",
            )
            findings.append(
                make_reconciliation_finding(
                    kind=str(mapping["kind"]),
                    severity="block",
                    subject=subject,
                    category="suite_drift",
                    evidence={
                        "suite_surface": suite_gate_validation.get("surface"),
                        "domain": domain,
                        "failure_kind": failure_kind,
                        "failed_layer": gap.get("failed_layer") or gap.get("surface"),
                        "source_locator": gap.get("source_locator"),
                        "classification": gap.get("classification"),
                        "binding": gap.get("binding"),
                        "consumer_impact": gap.get("consumer_impact"),
                        "remediation_direction": gap.get("remediation_direction"),
                        "validation_command": validation.get("command"),
                    },
                    recommended_action=str(mapping["recommended_action"]),
                    fallback_to=fallback_to,
                )
            )

    if not findings and result == "block":
        findings.append(
            make_reconciliation_finding(
                kind="missing_suite_gate",
                severity="block",
                subject=subject,
                category="suite_drift",
                evidence={
                    "suite_surface": suite_gate_validation.get("surface"),
                    "suite_result": suite_gate_validation.get("result"),
                    "missing_inputs": suite_gate_validation.get("missing_inputs", []),
                    "fallback_to": suite_gate_validation.get("fallback_to"),
                },
                recommended_action="restore readable suite gate evidence before closeout reconciliation.",
                fallback_to=suite_reconciliation_fallback(
                    suite_gate_validation.get("fallback_to"),
                    "suite evidence validate",
                ),
            )
        )
    return findings
