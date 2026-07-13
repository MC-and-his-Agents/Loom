#!/usr/bin/env python3
"""Live orchestration probes for adopted Loom repositories."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any

from companion_contract import load_repo_interop_contract, tool_availability_for_surface
from fact_chain_support import load_json_file, markdown_sections, resolve_repo_relative_path
from flow_runtime import command_target, current_iso_timestamp, emit, git_branch, git_head_sha, local_command_json as _local_command_json, resolve_target_arg, runtime_state_payload
from governance_surface import EXTERNAL_ORCHESTRATOR_OPERATIONS, build_governance_surface, empty_hook_extension_profile, empty_tool_availability


def local_command_json(target_root: Path, args: list[str]) -> tuple[dict[str, Any] | None, list[str]]:
    return _local_command_json(target_root, args, entrypoint=discover_loom_flow_entrypoint())


LIVE_SMOKE_SCHEMA = "loom-live-smoke/v1"
EXTERNAL_RESULT_SOURCE_READBACK_SCHEMA = "loom-external-result-source-readback/v1"
DYNAMIC_TOOL_LIVE_AVAILABILITY_SCHEMA = "loom-dynamic-tool-live-availability/v1"
HOOK_ENVELOPE_SCHEMA = "loom-hook-envelope/v2"
HOOK_ENVELOPE_LIVE_CHECK_SCHEMA = "loom-hook-envelope-check/v1"
HOOKS_EXTENSION_PROFILE_SCHEMA = "loom-hooks-extension-profile/v1"
EXTERNAL_ORCHESTRATOR_CONFORMANCE_SCHEMA = "loom-external-orchestrator-conformance/v1"
LIVE_SMOKE_RETRY_FALLBACK = "live-smoke-retry-or-record-unavailable"
LIVE_SMOKE_REPLAY_FALLBACK = "record-prior-evidence"
LIVE_SMOKE_CONFIG_FALLBACK = "live-smoke-config-repair"
HOOK_ENVELOPE_CATEGORIES = {"context_injection", "blocking_decision", "runtime_evidence"}
HOOK_ENVELOPE_FAILURE_CLASSIFICATIONS = {
    "invalid_envelope",
    "missing_required_input",
    "unsupported",
    "not_applicable",
    "permission_unavailable",
    "unsafe",
    "harness_mapping_failed",
}
HOOK_ENVELOPE_FALLBACKS = {
    None,
    "admission",
    "pre_review",
    "review",
    "build",
    "merge_ready",
    "closeout",
    "manual_repair",
    "workspace cleanup|retire",
}
HOOK_ENVELOPE_FORBIDDEN_FIELDS = {
    "authored_progress",
    "recovery_truth",
    "status_truth",
    "review_verdict",
    "validation_summary",
    "host_action_result",
    "closeout_basis",
    "current_stop",
    "next_step",
    "blockers",
    "latest_validation_summary",
    "current_checkpoint",
    "current_lane",
    "recovery_boundary",
    "closing_condition",
}
EXTERNAL_ORCHESTRATOR_FORBIDDEN_FIELDS = {
    "scheduler_state",
    "attempt_ownership",
    "authored_progress",
    "current_checkpoint",
    "next_step",
    "blockers",
    "latest_validation_summary",
    "status_truth",
    "gate_verdict",
    "review_verdict",
    "validation_summary",
    "host_action_result",
    "closeout_basis",
    "daemon",
    "scheduler_queue",
    "branch_ownership",
    "pr_ownership",
    "worktree_ownership",
    "worker_lifecycle",
}
EXTERNAL_ORCHESTRATOR_ALLOWED_FALLBACKS = {
    "work_item",
    "admission",
    "binding_repair",
    "current_checkpoint",
    "spec_gate",
    "build_gate",
    "review_gate",
    "merge_gate",
    "build",
    "review",
    "merge_ready",
    "closeout",
}
HOOK_CLEANUP_ALLOWED_OWNERSHIPS = {"loom_owned"}
HOOK_LIFECYCLES = {"before-run", "after-run", "cleanup"}
HARNESS_SUPPORT_RESULTS = {"supported", "not_applicable", "advisory", "unsafe"}

def discover_loom_flow_entrypoint() -> Path:
    source_repo_root = os.environ.get("LOOM_SOURCE_REPO_ROOT")
    if source_repo_root:
        candidate = Path(source_repo_root).expanduser().resolve() / "tools/loom_flow.py"
        if candidate.exists():
            return candidate
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "tools/loom_flow.py"
        if candidate.exists():
            return candidate
    return current.with_name("loom_flow.py")

def live_smoke_command(args: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in [sys.executable, str(discover_loom_flow_entrypoint()), *args])

def live_smoke_target_metadata(target_root: Path) -> dict[str, Any]:
    return {
        "path": str(target_root),
        "exists": target_root.exists(),
        "worktree": str(target_root),
        "git_branch": git_branch(target_root),
        "head_sha": git_head_sha(target_root),
    }

def live_smoke_release_interpretation(status: str) -> str:
    if status == "passed":
        return "fresh live smoke evidence raises release confidence and remains non-blocking by default."
    if status == "replayed":
        return "versioned prior-pass evidence can be consumed as release confidence input without rerunning adopted-repo commands."
    if status == "dry_run":
        return "dry-run only previews the live smoke command plan and does not create fresh adopted-repo evidence."
    if status == "unavailable":
        return "explicit unavailable evidence is a non-blocking confidence input and does not silently pass."
    return "profile-local live smoke failure lowers release confidence but does not replace orchestration-core gate results."

def external_result_source_readback_command(target_root: Path) -> str:
    return live_smoke_command(["live-smoke", "external-result-source-readback", "--target", str(target_root)])

def dynamic_tool_live_availability_command(target_root: Path, *, surface: str) -> str:
    return live_smoke_command(["live-smoke", "dynamic-tool-availability", "--target", str(target_root), "--surface", surface])

def hook_envelope_command(target_root: Path, *, envelope: str, requirement: str) -> str:
    return live_smoke_command(
        [
            "live-smoke",
            "hook-envelope",
            "--target",
            str(target_root),
            "--envelope",
            envelope,
            "--requirement",
            requirement,
        ]
    )

def external_result_source_readback_command_plan(
    target_root: Path,
    external_result_sources: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    target = command_target(target_root)
    plan = [
        {
            "id": "target-check",
            "command": f"test -d {target}",
            "description": "Confirm the adopted-repo target path exists before reading external result locators.",
        },
        {
            "id": "repo-interop-contract",
            "command": f"read {target_root / '.loom/companion/interop.json'}",
            "description": "Read the repo interop contract and discover declared external result locators.",
        },
    ]
    for index, entry in enumerate(external_result_sources or []):
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        locator = entry.get("locator") if isinstance(entry, dict) else None
        plan.append(
            {
                "id": str(entry_id or f"external-result-source-{index}"),
                "command": f"read {locator if isinstance(locator, str) and locator else '<missing-locator>'}",
                "description": "Read the retained external result envelope declared in repo interop.",
            }
        )
    return plan

def dynamic_tool_live_availability_command_plan(
    target_root: Path,
    *,
    surface: str,
    declared_tools: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    target = command_target(target_root)
    plan = [
        {
            "id": "target-check",
            "command": f"test -d {target}",
            "description": "Confirm the adopted-repo target path exists before reading dynamic tool handshake declarations.",
        },
        {
            "id": "repo-interface-contract",
            "command": f"read {target_root / '.loom/companion/repo-interface.json'}",
            "description": "Read the repo companion interface and discover declared dynamic tool availability locators.",
        },
    ]
    for index, entry in enumerate(declared_tools or []):
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        locator = entry.get("locator") if isinstance(entry, dict) else None
        plan.append(
            {
                "id": str(entry_id or f"dynamic-tool-{index}"),
                "command": f"read {locator if isinstance(locator, str) and locator else '<missing-locator>'}",
                "description": f"Read the dynamic tool handshake declaration for surface `{surface}`.",
            }
        )
    return plan

def hook_envelope_command_plan(target_root: Path, *, envelope: str | None) -> list[dict[str, Any]]:
    target = command_target(target_root)
    return [
        {
            "id": "target-check",
            "command": f"test -d {target}",
            "description": "Confirm the adopted-repo target path exists before reading the mapped hook envelope.",
        },
        {
            "id": "hook-envelope",
            "command": f"read {envelope if isinstance(envelope, str) and envelope else '<missing-envelope>'}",
            "description": "Read the repo-relative Loom-mapped hook envelope without executing any hook.",
        },
    ]

def hooks_extension_command_plan(target_root: Path) -> list[dict[str, Any]]:
    target = command_target(target_root)
    return [
        {
            "id": "target-check",
            "command": f"test -d {target}",
            "description": "Confirm the adopted-repo target path exists before reading hooks extension declarations.",
        },
        {
            "id": "repo-interface-contract",
            "command": f"read {target_root / '.loom/companion/repo-interface.json'}",
            "description": "Read hook_locators from repo companion without executing hooks or writing host state.",
        },
    ]

def external_orchestrator_conformance_command_plan(
    target_root: Path,
    external_orchestrators: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    target = command_target(target_root)
    plan = [
        {
            "id": "target-check",
            "command": f"test -d {target}",
            "description": "Confirm the adopted-repo target path exists before reading external orchestrator declarations.",
        },
        {
            "id": "repo-interop-contract",
            "command": f"read {target_root / '.loom/companion/interop.json'} external_orchestrators",
            "description": "Read external orchestrator locator declarations without starting a scheduler or daemon.",
        },
        {
            "id": "status-consumer-view",
            "command": f"{shlex.quote(sys.executable)} tools/loom_status.py --target {shlex.quote(str(target_root))} --item INIT-0001",
            "description": "Confirm status/gate consumption reuses Loom status control plane v2 and the existing gate chain.",
        },
    ]
    for index, entry in enumerate(external_orchestrators or []):
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        locator = entry.get("locator") if isinstance(entry, dict) else None
        plan.append(
            {
                "id": str(entry_id or f"external-orchestrator-{index}"),
                "command": f"read {locator if isinstance(locator, str) and locator else '<missing-locator>'}",
                "description": "Read external orchestrator retained evidence without accepting scheduler-owned status or gate truth.",
            }
        )
    return plan

def find_forbidden_hook_envelope_fields(value: object, *, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_label = str(key)
            nested_prefix = f"{prefix}.{key_label}"
            if key_label in HOOK_ENVELOPE_FORBIDDEN_FIELDS:
                found.append(nested_prefix)
            found.extend(find_forbidden_hook_envelope_fields(nested, prefix=nested_prefix))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(find_forbidden_hook_envelope_fields(nested, prefix=f"{prefix}[{index}]"))
    return found

def find_forbidden_external_orchestrator_fields(value: object, *, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_label = str(key)
            nested_prefix = f"{prefix}.{key_label}"
            if key_label in EXTERNAL_ORCHESTRATOR_FORBIDDEN_FIELDS:
                found.append(nested_prefix)
            found.extend(find_forbidden_external_orchestrator_fields(nested, prefix=nested_prefix))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(find_forbidden_external_orchestrator_fields(nested, prefix=f"{prefix}[{index}]"))
    return found

def find_unsafe_hook_cleanup_targets(value: object, *, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        targets = value.get("cleanup_targets")
        if isinstance(targets, list):
            for index, target in enumerate(targets):
                target_prefix = f"{prefix}.cleanup_targets[{index}]"
                if not isinstance(target, dict):
                    found.append(f"{target_prefix} must be an object")
                    continue
                ownership = target.get("ownership")
                if ownership not in HOOK_CLEANUP_ALLOWED_OWNERSHIPS:
                    found.append(f"{target_prefix}.ownership must be `loom_owned`")
        for key_label, nested in value.items():
            found.extend(find_unsafe_hook_cleanup_targets(nested, prefix=f"{prefix}.{key_label}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(find_unsafe_hook_cleanup_targets(nested, prefix=f"{prefix}[{index}]"))
    return found

def validate_hook_envelope_payload(envelope: object) -> dict[str, Any]:
    missing_inputs: list[str] = []
    evidence: dict[str, Any] = {
        "schema_status": "unknown",
        "output_category": None,
        "failure_classification": None,
    }
    if not isinstance(envelope, dict):
        return {
            "result": "block",
            "classification": "invalid_envelope",
            "summary": "hook envelope must be a JSON object.",
            "missing_inputs": ["hook envelope must be a JSON object"],
            "fallback_to": "manual_repair",
            "evidence": evidence,
        }

    if envelope.get("schema_version") == "loom-hook-envelope/v1" or (
        isinstance(envelope.get("input"), dict) and "host_adapter_mapping" in envelope["input"]
    ):
        return {
            "result": "block",
            "classification": "invalid_envelope",
            "summary": "hook envelope uses the removed host adapter mapping contract.",
            "missing_inputs": ["migrate to `loom-hook-envelope/v2` and `input.agent_harness_mapping`"],
            "migration_diagnostics": [
                {
                    "code": "legacy_hook_host_adapter_mapping",
                    "replacement": "input.agent_harness_mapping",
                }
            ],
            "fallback_to": "manual_repair",
            "evidence": evidence,
        }

    if envelope.get("schema_version") != HOOK_ENVELOPE_SCHEMA:
        missing_inputs.append("schema_version must be `loom-hook-envelope/v2`")
    else:
        evidence["schema_status"] = "valid"

    hook = envelope.get("hook")
    if not isinstance(hook, dict):
        missing_inputs.append("hook envelope missing `hook` object")
    else:
        for field in ("id", "locator"):
            value = hook.get(field)
            if not isinstance(value, str) or not value.strip():
                missing_inputs.append(f"hook missing `{field}`")
        lifecycle = hook.get("lifecycle")
        if lifecycle not in HOOK_LIFECYCLES:
            missing_inputs.append("hook.lifecycle must be `before-run`, `after-run`, or `cleanup`")

    input_payload = envelope.get("input")
    support_result = None
    if not isinstance(input_payload, dict):
        missing_inputs.append("hook envelope missing `input` object")
    else:
        for field in ("item_locator", "workspace_locator", "attempt_locator"):
            value = input_payload.get(field)
            if not isinstance(value, str) or not value.strip():
                missing_inputs.append(f"input missing `{field}`")
        mapping = input_payload.get("agent_harness_mapping")
        if not isinstance(mapping, dict):
            missing_inputs.append("input missing `agent_harness_mapping` object")
        else:
            for field in ("host", "event"):
                value = mapping.get(field)
                if not isinstance(value, str) or not value.strip():
                    missing_inputs.append(f"agent_harness_mapping missing `{field}`")
            if mapping.get("support_result") not in HARNESS_SUPPORT_RESULTS:
                missing_inputs.append(
                    "agent_harness_mapping.support_result must be `supported`, `not_applicable`, `advisory`, or `unsafe`"
                )
            else:
                support_result = mapping.get("support_result")

    output = envelope.get("output")
    output_category = None
    if not isinstance(output, dict):
        missing_inputs.append("hook envelope missing `output` object")
    else:
        output_category = output.get("category")
        evidence["output_category"] = output_category
        if output_category not in HOOK_ENVELOPE_CATEGORIES:
            missing_inputs.append("output.category must be `context_injection`, `blocking_decision`, or `runtime_evidence`")
        summary = output.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            missing_inputs.append("output missing `summary`")

    forbidden_fields = find_forbidden_hook_envelope_fields(envelope)
    if forbidden_fields:
        missing_inputs.append(f"hook envelope must not carry authored or host truth fields: {', '.join(forbidden_fields)}")
    unsafe_cleanup_targets = find_unsafe_hook_cleanup_targets(envelope)
    if unsafe_cleanup_targets:
        missing_inputs.append(
            "hook envelope cleanup intent must target Loom-owned residue only: "
            + ", ".join(unsafe_cleanup_targets)
        )

    failure = envelope.get("failure")
    failure_classification = None
    fallback_to = None
    if failure is not None:
        if not isinstance(failure, dict):
            missing_inputs.append("failure must be an object when present")
        else:
            failure_classification = failure.get("classification")
            evidence["failure_classification"] = failure_classification
            if failure_classification not in HOOK_ENVELOPE_FAILURE_CLASSIFICATIONS:
                missing_inputs.append("failure.classification is outside the stable hook envelope vocabulary")
            fallback_to = failure.get("fallback_to")
            if fallback_to not in HOOK_ENVELOPE_FALLBACKS:
                missing_inputs.append("failure.fallback_to must point to a Loom surface or manual repair path")
            summary = failure.get("summary")
            if failure_classification and (not isinstance(summary, str) or not summary.strip()):
                missing_inputs.append("failure with classification must include `summary`")

    if missing_inputs:
        return {
            "result": "block",
            "classification": "invalid_envelope",
            "summary": "hook envelope is invalid or truth-polluting.",
            "missing_inputs": missing_inputs,
            "fallback_to": "manual_repair",
            "evidence": evidence,
        }

    if support_result == "unsafe":
        return {
            "result": "block",
            "classification": "unsafe",
            "summary": "hook harness mapping reports unsafe.",
            "missing_inputs": ["agent_harness_mapping.support_result is unsafe"],
            "fallback_to": "manual_repair",
            "evidence": evidence,
        }
    if support_result == "not_applicable":
        return {
            "result": "warn",
            "classification": "not_applicable",
            "summary": "hook harness mapping reports not_applicable.",
            "missing_inputs": [],
            "fallback_to": None,
            "evidence": evidence,
        }
    if support_result == "advisory":
        return {
            "result": "warn",
            "classification": "unsupported",
            "summary": "hook harness mapping is advisory and remains profile-local evidence.",
            "missing_inputs": [],
            "fallback_to": None,
            "evidence": evidence,
        }

    if failure_classification == "not_applicable":
        return {
            "result": "warn",
            "classification": "not_applicable",
            "summary": "hook envelope reports not_applicable.",
            "missing_inputs": [],
            "fallback_to": None,
            "evidence": evidence,
        }
    if failure_classification:
        result = "block" if failure_classification in {"permission_unavailable", "unsafe", "harness_mapping_failed"} else "warn"
        return {
            "result": result,
            "classification": failure_classification,
            "summary": str(failure.get("summary") if isinstance(failure, dict) else "hook envelope reports failure."),
            "missing_inputs": [f"hook envelope reported {failure_classification}"] if result == "block" else [],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": evidence,
        }
    return {
        "result": "pass",
        "classification": "none",
        "summary": f"hook envelope maps output as `{output_category}`.",
        "missing_inputs": [],
        "fallback_to": None,
        "evidence": evidence,
    }

def external_result_permission_unavailable(payload: dict[str, Any]) -> bool:
    candidates: list[str] = []
    for key in ("status", "result", "classification", "failure_category"):
        value = payload.get(key)
        if isinstance(value, str):
            candidates.append(value)
    read_status = payload.get("read_status")
    if isinstance(read_status, dict):
        for key in ("status", "result", "classification", "failure_category"):
            value = read_status.get(key)
            if isinstance(value, str):
                candidates.append(value)
    normalized = {value.strip().lower().replace("-", "_") for value in candidates if value.strip()}
    return "permission_unavailable" in normalized

def external_result_source_envelope_issue(
    target_root: Path,
    envelope: dict[str, Any],
    *,
    surfaces: list[str],
) -> tuple[str, str] | None:
    if not isinstance(envelope.get("schema_version"), str) or not envelope.get("schema_version"):
        return "invalid_envelope", "external result source envelope is missing `schema_version`"

    raw_result = envelope.get("result") if isinstance(envelope.get("result"), str) else envelope.get("status")
    if not isinstance(raw_result, str) or not raw_result:
        return "invalid_result", "external result source envelope is missing `result` or `status`"
    normalized_result = raw_result.strip().lower().replace("-", "_")
    if normalized_result in {
        "block", "blocked", "deny", "denied", "error", "fail", "failed", "failure",
        "invalid", "mismatch", "rejected", "stale", "unavailable", "unsafe",
    }:
        return "retained_result_failed", f"external result source reported `{raw_result}`"
    if normalized_result not in {"allow", "pass", "passed", "ready", "success", "succeeded"}:
        return "invalid_result", f"external result source reported unsupported result `{raw_result}`"

    head_bound = bool({"pre_review", "review", "merge_ready", "closeout"}.intersection(surfaces))
    freshness = envelope.get("freshness")
    if head_bound:
        if not isinstance(freshness, str) or freshness.strip().lower() not in {"current", "fresh"}:
            return "stale_result", "head-bound external result source must report current freshness"
        expected_head = git_head_sha(target_root)
        observed_head = envelope.get("head_sha")
        if not expected_head or not isinstance(observed_head, str) or not re.fullmatch(r"[0-9a-f]{40}", observed_head):
            return "binding_unavailable", "head-bound external result source is missing a verifiable head SHA"
        if observed_head != expected_head:
            return "binding_mismatch", "external result source is bound to another head SHA"
    elif isinstance(freshness, str) and freshness.strip().lower() not in {"current", "fresh"}:
        return "stale_result", "external result source reports stale freshness"
    return None

def external_result_source_check(
    target_root: Path,
    *,
    entry: object,
    index: int,
) -> dict[str, Any]:
    prefix = f"external_result_sources[{index}]"
    if not isinstance(entry, dict):
        return {
            "id": f"invalid-{index}",
            "owner": "unknown",
            "requirement": "required",
            "surfaces": [],
            "locator": None,
            "result": "block",
            "classification": "invalid_declaration",
            "summary": f"{prefix} must be an object.",
            "missing_inputs": [f"{prefix} must be an object"],
            "fallback_to": "admission",
            "evidence": {"locator_status": "invalid"},
        }

    entry_id = str(entry.get("id") or f"external-result-source-{index}")
    requirement = str(entry.get("requirement") or "required")
    fallback_to = entry.get("fallback_to") if isinstance(entry.get("fallback_to"), str) and entry.get("fallback_to") else "admission"
    owner = str(entry.get("owner") or "unknown")
    surfaces = entry.get("surfaces")
    locator_value = entry.get("locator")
    missing_inputs: list[str] = []
    if not isinstance(entry.get("summary"), str) or not entry.get("summary"):
        missing_inputs.append(f"{prefix} missing `summary`")
    if owner not in {"repo", "repo-companion", "host", "host-adapter", "platform", "external-tool"}:
        missing_inputs.append(f"{prefix} owner must stay repo/host/platform-owned, not Loom core")
    if requirement not in {"required", "optional", "advisory"}:
        missing_inputs.append(f"{prefix} requirement must be `required`, `optional`, or `advisory`")
    if not isinstance(surfaces, list) or not surfaces:
        missing_inputs.append(f"{prefix} must include `surfaces` as a non-empty list")
    else:
        for surface_index, surface in enumerate(surfaces):
            if surface not in {"admission", "pre_review", "review", "build", "merge_ready", "closeout"}:
                missing_inputs.append(
                    f"{prefix}.surfaces[{surface_index}] must be one of `admission`, `pre_review`, `review`, `build`, `merge_ready`, `closeout`"
                )
    if not isinstance(locator_value, str) or not locator_value.strip():
        classification = "locator_missing"
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": surfaces if isinstance(surfaces, list) else [],
            "locator": locator_value,
            "result": result,
            "classification": classification,
            "summary": "external result source locator is missing.",
            "missing_inputs": [*missing_inputs, f"{prefix} `{entry_id}` locator missing `locator`"],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": {"locator_status": "missing"},
        }
    if missing_inputs:
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": surfaces if isinstance(surfaces, list) else [],
            "locator": locator_value,
            "result": "block",
            "classification": "invalid_declaration",
            "summary": "external result source declaration is incomplete or invalid.",
            "missing_inputs": missing_inputs,
            "fallback_to": fallback_to,
            "evidence": {"locator_status": "invalid"},
        }

    locator_path, locator_errors = resolve_repo_relative_path(
        target_root,
        locator_value,
        label=f"{prefix} `{entry_id}` locator",
    )
    if locator_errors:
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": "block",
            "classification": "unsafe_locator",
            "summary": "external result source locator is outside the repository boundary or otherwise unsafe.",
            "missing_inputs": locator_errors,
            "fallback_to": fallback_to,
            "evidence": {"locator_status": "unsafe"},
        }
    assert locator_path is not None
    if not locator_path.exists():
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": result,
            "classification": "locator_missing",
            "summary": "external result source locator points to a missing retained result path.",
            "missing_inputs": [f"{prefix} locator points to missing path `{locator_value}`"],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": {"locator_status": "missing"},
        }
    if locator_path.is_dir():
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": result,
            "classification": "locator_unreadable",
            "summary": "external result source locator points to a directory, not a retained result envelope.",
            "missing_inputs": [f"{prefix} locator points to a directory `{locator_value}`"],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": {"locator_status": "directory"},
        }
    try:
        envelope = load_json_file(locator_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": result,
            "classification": "locator_unreadable",
            "summary": "external result source envelope is unreadable.",
            "missing_inputs": [f"{prefix} locator is unreadable: {exc}"],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": {"locator_status": "unreadable"},
        }
    if not isinstance(envelope, dict):
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": result,
            "classification": "locator_unreadable",
            "summary": "external result source envelope must be a JSON object.",
            "missing_inputs": [f"{prefix} locator must expose a JSON object envelope"],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": {"locator_status": "invalid-envelope"},
        }

    evidence = {
        "locator_status": "readable",
        "envelope_status": str(envelope.get("status") or envelope.get("result") or "present"),
    }
    summary = str(envelope.get("summary") or "external result source envelope is readable.")
    if external_result_permission_unavailable(envelope):
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": result,
            "classification": "permission_unavailable",
            "summary": summary,
            "missing_inputs": [f"external result source `{entry_id}` reported permission_unavailable"],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": evidence,
        }
    envelope_issue = external_result_source_envelope_issue(target_root, envelope, surfaces=list(surfaces))
    if envelope_issue is not None:
        classification, issue = envelope_issue
        result = "block" if requirement == "required" else "warn"
        return {
            "id": entry_id,
            "owner": owner,
            "requirement": requirement,
            "surfaces": list(surfaces),
            "locator": locator_value,
            "result": result,
            "classification": classification,
            "summary": summary,
            "missing_inputs": [issue],
            "fallback_to": fallback_to if result == "block" else None,
            "evidence": evidence,
        }
    return {
        "id": entry_id,
        "owner": owner,
        "requirement": requirement,
        "surfaces": list(surfaces),
        "locator": locator_value,
        "result": "pass",
        "classification": "none",
        "summary": summary,
        "missing_inputs": [],
        "fallback_to": None,
        "evidence": evidence,
    }

def external_result_source_readback_payload(target_root: Path) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    target = live_smoke_target_metadata(target_root)
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "external-result-source-readback",
        "schema_version": EXTERNAL_RESULT_SOURCE_READBACK_SCHEMA,
        "runtime_state": runtime_state,
        "target": target,
        "command_plan": external_result_source_readback_command_plan(target_root),
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if runtime_state.get("result") != "pass":
        payload.update(
            {
                "result": "block",
                "summary": "external result source readback is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "profile_check": {"id": "external-result-source-readback", "result": "block"},
                "external_result_source_readback": {
                    "contract_locator": ".loom/companion/interop.json",
                    "availability": "runtime-blocked",
                    "checks": [],
                },
            }
        )
        return payload

    target_report = live_smoke_target_check_report(target_root)
    payload["reports"] = [target_report]
    payload["missing_inputs"] = list(target_report.get("missing_inputs", []))
    if target_report["result"] != "pass":
        payload.update(
            {
                "result": "warn",
                "summary": "external result source readback recorded explicit unavailable evidence for the adopted-repo target.",
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "external-result-source-readback", "result": "warn"},
                "external_result_source_readback": {
                    "contract_locator": ".loom/companion/interop.json",
                    "availability": "target-unavailable",
                    "checks": [],
                },
            }
        )
        return payload

    governance_surface = build_governance_surface(target_root)
    repo_interop = governance_surface.get("repo_interop")
    contract_locator = ".loom/companion/interop.json"
    availability = "absent"
    if isinstance(repo_interop, dict):
        availability = str(repo_interop.get("availability") or "absent")
        contract = repo_interop.get("contract")
        if isinstance(contract, dict) and isinstance(contract.get("locator"), str) and contract.get("locator"):
            contract_locator = str(contract["locator"])
    interop_report = {
        "id": "repo-interop-contract",
        "attempted": True,
        "command": f"read {target_root / contract_locator}",
        "reported_command": "repo-interop-contract",
        "reported_result": availability,
        "result": "pass",
        "summary": "repo interop contract is readable.",
        "missing_inputs": [],
        "fallback_to": None,
    }
    payload["reports"].append(interop_report)

    if availability == "absent":
        interop_report.update(
            {
                "result": "warn",
                "summary": "repo interop contract is absent, so no external result source can be consumed.",
                "missing_inputs": ["repo interop contract is absent"],
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "warn",
                "summary": interop_report["summary"],
                "missing_inputs": interop_report["missing_inputs"],
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "external-result-source-readback", "result": "warn"},
                "external_result_source_readback": {
                    "contract_locator": contract_locator,
                    "availability": "absent",
                    "checks": [],
                },
            }
        )
        return payload

    interop_payload, interop_errors = load_repo_interop_contract(repo_interop, target_root=target_root)
    if interop_errors or not isinstance(interop_payload, dict):
        interop_report.update(
            {
                "result": "block",
                "summary": "repo interop contract is incomplete or unreadable for external result source readback.",
                "missing_inputs": interop_errors or ["repo interop contract is unreadable"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": interop_report["summary"],
                "missing_inputs": list(interop_report["missing_inputs"]),
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "external-result-source-readback", "result": "block"},
                "migration_diagnostics": (
                    list(repo_interop.get("migration_diagnostics", []))
                    if isinstance(repo_interop, dict) and isinstance(repo_interop.get("migration_diagnostics"), list)
                    else []
                ),
                "external_result_source_readback": {
                    "contract_locator": contract_locator,
                    "availability": "incomplete",
                    "checks": [],
                },
            }
        )
        return payload

    external_result_sources = interop_payload.get("external_result_sources", [])
    if not isinstance(external_result_sources, list):
        interop_report.update(
            {
                "result": "block",
                "summary": "repo interop contract does not expose a readable external_result_sources list.",
                "missing_inputs": ["repo interop contract `external_result_sources` must be a list when present"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": interop_report["summary"],
                "missing_inputs": list(interop_report["missing_inputs"]),
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "external-result-source-readback", "result": "block"},
                "external_result_source_readback": {
                    "contract_locator": contract_locator,
                    "availability": "incomplete",
                    "checks": [],
                },
            }
        )
        return payload

    payload["command_plan"] = external_result_source_readback_command_plan(
        target_root,
        external_result_sources=external_result_sources,
    )
    if not external_result_sources:
        interop_report.update(
            {
                "result": "pass",
                "summary": "repo interop contract declares no external result sources; readback is not applicable.",
                "missing_inputs": [],
                "fallback_to": None,
            }
        )
        payload.update(
            {
                "result": "pass",
                "summary": interop_report["summary"],
                "missing_inputs": [],
                "fallback_to": None,
                "profile_check": {"id": "external-result-source-readback", "result": "pass"},
                "external_result_source_readback": {
                    "contract_locator": contract_locator,
                    "availability": "not-declared",
                    "checks": [],
                },
            }
        )
        return payload

    checks = [
        external_result_source_check(
            target_root,
            entry=entry,
            index=index,
        )
        for index, entry in enumerate(external_result_sources)
    ]
    for check in checks:
        payload["reports"].append(
            {
                "id": str(check["id"]),
                "attempted": True,
                "command": f"read {check.get('locator') or '<missing-locator>'}",
                "reported_command": "external-result-source",
                "reported_result": str(check["classification"]),
                "result": str(check["result"]),
                "summary": str(check["summary"]),
                "missing_inputs": list(check.get("missing_inputs", [])),
                "fallback_to": check.get("fallback_to"),
            }
        )
    missing_inputs = live_smoke_missing_inputs(
        [message for report in payload["reports"] for message in report.get("missing_inputs", [])]
    )
    has_block = any(check["result"] == "block" for check in checks)
    has_warn = any(check["result"] == "warn" for check in checks)
    result = "block" if has_block else "warn" if has_warn else "pass"
    summary = "external result source locators are readable."
    if result == "warn":
        summary = "external result source readback produced profile-local warnings."
    if result == "block":
        summary = "external result source readback found blocking declaration or readability gaps."
    payload.update(
        {
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else None,
            "profile_check": {"id": "external-result-source-readback", "result": result},
            "external_result_source_readback": {
                "contract_locator": contract_locator,
                "availability": "present",
                "checks": checks,
            },
        }
    )
    return payload

def hook_envelope_payload(target_root: Path, *, envelope: str, requirement: str) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    target = live_smoke_target_metadata(target_root)
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "hook-envelope",
        "schema_version": HOOK_ENVELOPE_LIVE_CHECK_SCHEMA,
        "runtime_state": runtime_state,
        "target": target,
        "command_plan": hook_envelope_command_plan(target_root, envelope=envelope),
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if requirement not in {"required", "optional", "advisory"}:
        payload.update(
            {
                "result": "block",
                "summary": "hook envelope check requires requirement to be required, optional, or advisory.",
                "missing_inputs": ["--requirement must be `required`, `optional`, or `advisory`"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "hook-envelope", "result": "block"},
                "hook_envelope": {
                    "contract_locator": envelope,
                    "availability": "invalid-declaration",
                    "requirement": requirement,
                    "checks": [],
                },
            }
        )
        return payload
    if runtime_state.get("result") != "pass":
        payload.update(
            {
                "result": "block",
                "summary": "hook envelope check is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "profile_check": {"id": "hook-envelope", "result": "block"},
                "hook_envelope": {
                    "contract_locator": envelope,
                    "availability": "runtime-blocked",
                    "requirement": requirement,
                    "checks": [],
                },
            }
        )
        return payload

    target_report = live_smoke_target_check_report(target_root)
    payload["reports"] = [target_report]
    payload["missing_inputs"] = list(target_report.get("missing_inputs", []))
    if target_report["result"] != "pass":
        payload.update(
            {
                "result": "warn",
                "summary": "hook envelope check recorded explicit unavailable evidence for the adopted-repo target.",
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "hook-envelope", "result": "warn"},
                "hook_envelope": {
                    "contract_locator": envelope,
                    "availability": "target-unavailable",
                    "requirement": requirement,
                    "checks": [],
                },
            }
        )
        return payload

    envelope_path, envelope_errors = resolve_repo_relative_path(target_root, envelope, label="hook envelope locator")
    if envelope_errors:
        check = {
            "id": "hook-envelope",
            "requirement": requirement,
            "locator": envelope,
            "result": "block",
            "classification": "unsafe",
            "summary": "hook envelope locator is outside the repository boundary or otherwise unsafe.",
            "missing_inputs": envelope_errors,
            "fallback_to": "manual_repair",
            "evidence": {"locator_status": "unsafe"},
        }
        payload["reports"].append(
            {
                "id": "hook-envelope",
                "attempted": True,
                "command": f"read {envelope}",
                "reported_command": "hook-envelope",
                "reported_result": "unsafe",
                "result": "block",
                "summary": check["summary"],
                "missing_inputs": envelope_errors,
                "fallback_to": "manual_repair",
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": "hook envelope check found an unsafe locator.",
                "missing_inputs": live_smoke_missing_inputs(envelope_errors),
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "hook-envelope", "result": "block"},
                "hook_envelope": {
                    "contract_locator": envelope,
                    "availability": "incomplete",
                    "requirement": requirement,
                    "checks": [check],
                },
            }
        )
        return payload
    assert envelope_path is not None

    if not envelope_path.exists():
        result = "block" if requirement == "required" else "warn"
        missing_inputs = [f"hook envelope locator points to missing path `{envelope}`"]
        check = {
            "id": "hook-envelope",
            "requirement": requirement,
            "locator": envelope,
            "result": result,
            "classification": "missing_required_input" if result == "block" else "not_applicable",
            "summary": "hook envelope locator is missing.",
            "missing_inputs": missing_inputs,
            "fallback_to": "manual_repair" if result == "block" else None,
            "evidence": {"locator_status": "missing"},
        }
        payload["reports"].append(
            {
                "id": "hook-envelope",
                "attempted": True,
                "command": f"read {envelope}",
                "reported_command": "hook-envelope",
                "reported_result": "missing",
                "result": result,
                "summary": check["summary"],
                "missing_inputs": missing_inputs,
                "fallback_to": check["fallback_to"],
            }
        )
        payload.update(
            {
                "result": result,
                "summary": "hook envelope locator is missing.",
                "missing_inputs": live_smoke_missing_inputs(missing_inputs) if result == "block" else [],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else None,
                "profile_check": {"id": "hook-envelope", "result": result},
                "hook_envelope": {
                    "contract_locator": envelope,
                    "availability": "incomplete",
                    "requirement": requirement,
                    "checks": [check],
                },
            }
        )
        return payload

    try:
        envelope_payload = load_json_file(envelope_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        result = "block" if requirement == "required" else "warn"
        missing_inputs = [f"hook envelope locator is unreadable: {exc}"]
        check = {
            "id": "hook-envelope",
            "requirement": requirement,
            "locator": envelope,
            "result": result,
            "classification": "invalid_envelope",
            "summary": "hook envelope locator is unreadable.",
            "missing_inputs": missing_inputs,
            "fallback_to": "manual_repair" if result == "block" else None,
            "evidence": {"locator_status": "unreadable"},
        }
    else:
        check = {
            "id": "hook-envelope",
            "requirement": requirement,
            "locator": envelope,
            **validate_hook_envelope_payload(envelope_payload),
        }
        check["evidence"] = {"locator_status": "readable", **dict(check.get("evidence", {}))}
        if requirement in {"optional", "advisory"} and check["result"] == "block":
            check["result"] = "warn"
            check["fallback_to"] = None
            check["missing_inputs"] = []

    payload["reports"].append(
        {
            "id": "hook-envelope",
            "attempted": True,
            "command": f"read {envelope}",
            "reported_command": "hook-envelope",
            "reported_result": str(check["classification"]),
            "result": str(check["result"]),
            "summary": str(check["summary"]),
            "missing_inputs": list(check.get("missing_inputs", [])),
            "fallback_to": check.get("fallback_to"),
        }
    )
    result = str(check["result"])
    payload.update(
        {
            "result": result,
            "summary": "hook envelope is valid." if result == "pass" else "hook envelope check produced warnings." if result == "warn" else "hook envelope check found blocking errors.",
            "missing_inputs": live_smoke_missing_inputs(list(check.get("missing_inputs", []))) if result == "block" else [],
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else None,
            "profile_check": {"id": "hook-envelope", "result": result},
            "hook_envelope": {
                "contract_locator": envelope,
                "availability": "present",
                "requirement": requirement,
                "checks": [check],
            },
        }
    )
    return payload

def hooks_extension_payload(target_root: Path) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    target = live_smoke_target_metadata(target_root)
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "hooks-extension",
        "schema_version": HOOKS_EXTENSION_PROFILE_SCHEMA,
        "runtime_state": runtime_state,
        "target": target,
        "command_plan": hooks_extension_command_plan(target_root),
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if runtime_state.get("result") != "pass":
        hook_profile = empty_hook_extension_profile()
        hook_profile.update({"status": "runtime-blocked", "result": "block"})
        payload.update(
            {
                "result": "block",
                "summary": "hooks extension profile is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "profile_check": {"id": "hooks-extension", "result": "block"},
                "core_profile": {"id": "orchestration-core", "hook_enforcement": "not_applicable", "result": "pass"},
                "hooks_extension": hook_profile,
            }
        )
        return payload

    target_report = live_smoke_target_check_report(target_root)
    payload["reports"] = [target_report]
    if target_report["result"] != "pass":
        hook_profile = empty_hook_extension_profile()
        hook_profile.update({"status": "target-unavailable", "result": "warn"})
        payload.update(
            {
                "result": "warn",
                "summary": "hooks extension profile recorded explicit unavailable evidence for the adopted-repo target.",
                "missing_inputs": list(target_report.get("missing_inputs", [])),
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "hooks-extension", "result": "warn"},
                "core_profile": {"id": "orchestration-core", "hook_enforcement": "not_applicable", "result": "pass"},
                "hooks_extension": hook_profile,
            }
        )
        return payload

    governance_surface = build_governance_surface(target_root)
    repo_interface = governance_surface.get("repo_interface")
    if not isinstance(repo_interface, dict):
        hook_profile = empty_hook_extension_profile()
    else:
        hook_profile = repo_interface.get("hook_profile")
        if not isinstance(hook_profile, dict):
            hook_profile = empty_hook_extension_profile()

    result = str(hook_profile.get("result") or "pass")
    if result not in {"pass", "warn", "block"}:
        result = "block"
    payload["reports"].append(
        {
            "id": "hooks-extension",
            "attempted": True,
            "command": f"read {target_root / '.loom/companion/repo-interface.json'}",
            "reported_command": "repo-interface.hook_locators",
            "reported_result": str(hook_profile.get("status") or "not_applicable"),
            "result": result,
            "summary": str(hook_profile.get("summary") or "hooks extension profile is not enabled."),
            "missing_inputs": list(hook_profile.get("missing_inputs", [])) if result == "block" else [],
            "fallback_to": "manual_repair" if result == "block" else None,
        }
    )
    payload.update(
        {
            "result": result,
            "summary": str(hook_profile.get("summary") or "hooks extension profile is not enabled."),
            "missing_inputs": live_smoke_missing_inputs(list(hook_profile.get("missing_inputs", []))) if result == "block" else [],
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else None,
            "profile_check": {"id": "hooks-extension", "result": result},
            "core_profile": {"id": "orchestration-core", "hook_enforcement": "not_applicable", "result": "pass"},
            "hooks_extension": hook_profile,
        }
    )
    return payload

def empty_external_orchestrator_conformance() -> dict[str, Any]:
    return {
        "schema_version": EXTERNAL_ORCHESTRATOR_CONFORMANCE_SCHEMA,
        "profile_id": "orchestration-extension/external-orchestrator",
        "enabled": False,
        "result": "pass",
        "status": "not_applicable",
        "summary": "external orchestrator interop profile is not enabled for this repository.",
        "missing_inputs": [],
        "missing_optional": [],
        "checks": [],
        "non_goals": {
            "daemon": False,
            "scheduler_state_machine": False,
            "tracker_polling_product": False,
            "second_status_surface": False,
            "host_lifecycle_ownership": False,
        },
    }

def external_orchestrator_conformance_check(
    target_root: Path,
    *,
    entry: object,
    index: int,
) -> dict[str, Any]:
    prefix = f"external_orchestrators[{index}]"
    if not isinstance(entry, dict):
        return {
            "id": f"invalid-{index}",
            "requirement": "required",
            "operations": [],
            "locator": "",
            "result": "block",
            "classification": "invalid_declaration",
            "summary": f"{prefix} must be an object.",
            "missing_inputs": [f"{prefix} must be an object"],
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            "evidence": {"locator_status": "invalid-declaration"},
        }

    entry_id = entry.get("id") if isinstance(entry.get("id"), str) and entry.get("id") else f"external-orchestrator-{index}"
    requirement = entry.get("requirement") if isinstance(entry.get("requirement"), str) else "required"
    locator = entry.get("locator") if isinstance(entry.get("locator"), str) else ""
    fallback_to = entry.get("fallback_to") if isinstance(entry.get("fallback_to"), str) else "admission"
    operations = entry.get("operations") if isinstance(entry.get("operations"), list) else []
    blocking: list[str] = []
    optional: list[str] = []

    if requirement not in {"required", "optional", "advisory"}:
        blocking.append(f"{prefix}.requirement must be required, optional, or advisory")
        requirement = "required"
    if not operations:
        blocking.append(f"{prefix}.operations must be a non-empty list")
    unsupported = [str(operation) for operation in operations if operation not in EXTERNAL_ORCHESTRATOR_OPERATIONS]
    if unsupported:
        blocking.append(f"{prefix}.operations contains unsupported operations: {', '.join(unsupported)}")
    if isinstance(fallback_to, str) and fallback_to not in EXTERNAL_ORCHESTRATOR_ALLOWED_FALLBACKS:
        blocking.append(f"{prefix}.fallback_to must point back to a Loom checkpoint or gate repair surface")

    locator_path, locator_errors = resolve_repo_relative_path(target_root, locator, label=f"{prefix} locator")
    if locator_errors:
        blocking.extend(locator_errors)
    elif locator_path is None or not locator_path.exists() or locator_path.is_dir():
        message = f"{prefix} locator points to missing or unreadable retained evidence `{locator}`"
        if requirement in {"optional", "advisory"}:
            optional.append(message)
        else:
            blocking.append(message)

    payload: object = None
    if locator_path is not None and locator_path.exists() and locator_path.is_file():
        try:
            payload = load_json_file(locator_path)
        except (json.JSONDecodeError, OSError) as exc:
            blocking.append(f"{prefix} retained evidence is not readable JSON: {exc}")
    if payload is not None and not isinstance(payload, dict):
        blocking.append(f"{prefix} retained evidence must be a JSON object")
    if isinstance(payload, dict):
        forbidden = find_forbidden_external_orchestrator_fields(payload)
        if forbidden:
            blocking.append(f"{prefix} retained evidence contains forbidden authored/scheduler fields: {', '.join(forbidden)}")
        payload_operation = payload.get("operation")
        if isinstance(payload_operation, str) and operations and payload_operation not in operations:
            blocking.append(f"{prefix} retained evidence operation is not declared by the locator")
        if payload.get("operation") in {"status_read", "gate_read"}:
            if payload.get("source_layer") != "derived_surface":
                blocking.append(f"{prefix} status/gate reads must consume the derived status surface")
            if payload.get("consumed_as") != "summary":
                blocking.append(f"{prefix} status/gate reads must be consumed as summary")
        if payload.get("host_lifecycle_ownership") not in {None, "host", "external"}:
            blocking.append(f"{prefix} retained evidence must not claim Loom owns host lifecycle")
        payload_fallback = payload.get("fallback_to")
        if isinstance(payload_fallback, str) and payload_fallback not in EXTERNAL_ORCHESTRATOR_ALLOWED_FALLBACKS:
            blocking.append(f"{prefix} retained evidence fallback_to must point back to Loom")

    result = "block" if blocking else "warn" if optional else "pass"
    if result == "warn" and requirement in {"required"}:
        result = "block"
    return {
        "id": entry_id,
        "requirement": requirement,
        "operations": operations,
        "locator": locator,
        "result": result,
        "classification": "truth_pollution" if blocking and isinstance(payload, dict) and find_forbidden_external_orchestrator_fields(payload) else "locator_or_contract",
        "summary": (
            "external orchestrator retained evidence is readable and respects Loom truth boundaries."
            if result == "pass"
            else "external orchestrator retained evidence has profile-local warnings."
            if result == "warn"
            else "external orchestrator retained evidence violates interop conformance boundaries."
        ),
        "missing_inputs": blocking if result == "block" else [],
        "missing_optional": optional,
        "fallback_to": fallback_to if result == "block" else None,
        "evidence": {
            "locator_status": "readable" if isinstance(payload, dict) else "missing_or_invalid",
            "payload_schema_version": payload.get("schema_version") if isinstance(payload, dict) else None,
            "payload_operation": payload.get("operation") if isinstance(payload, dict) else None,
        },
    }

def external_orchestrator_conformance_payload(target_root: Path) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    target = live_smoke_target_metadata(target_root)
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "external-orchestrator-interop",
        "schema_version": EXTERNAL_ORCHESTRATOR_CONFORMANCE_SCHEMA,
        "runtime_state": runtime_state,
        "target": target,
        "command_plan": external_orchestrator_conformance_command_plan(target_root),
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if runtime_state.get("result") != "pass":
        conformance = empty_external_orchestrator_conformance()
        conformance.update({"status": "runtime-blocked", "result": "block"})
        payload.update(
            {
                "result": "block",
                "summary": "external orchestrator conformance is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "profile_check": {"id": "external-orchestrator-interop", "result": "block"},
                "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
                "external_orchestrator": conformance,
            }
        )
        return payload

    target_report = live_smoke_target_check_report(target_root)
    payload["reports"] = [target_report]
    if target_report["result"] != "pass":
        conformance = empty_external_orchestrator_conformance()
        conformance.update({"status": "target-unavailable", "result": "warn"})
        payload.update(
            {
                "result": "warn",
                "summary": "external orchestrator conformance recorded explicit unavailable evidence for the adopted-repo target.",
                "missing_inputs": list(target_report.get("missing_inputs", [])),
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "external-orchestrator-interop", "result": "warn"},
                "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
                "external_orchestrator": conformance,
            }
        )
        return payload

    interop_path = target_root / ".loom" / "companion" / "interop.json"
    if not interop_path.exists():
        conformance = empty_external_orchestrator_conformance()
        payload["reports"].append(
            {
                "id": "external-orchestrator-interop",
                "attempted": True,
                "command": f"read {interop_path}",
                "reported_command": "repo-interop.external_orchestrators",
                "reported_result": "not_applicable",
                "result": "pass",
                "summary": "repo interop does not declare external orchestrators.",
                "missing_inputs": [],
                "fallback_to": None,
            }
        )
        payload.update(
            {
                "result": "pass",
                "summary": conformance["summary"],
                "profile_check": {"id": "external-orchestrator-interop", "result": "pass"},
                "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
                "external_orchestrator": conformance,
            }
        )
        return payload

    try:
        interop_payload = load_json_file(interop_path)
    except (json.JSONDecodeError, OSError) as exc:
        conformance = empty_external_orchestrator_conformance()
        conformance.update(
            {
                "enabled": True,
                "result": "block",
                "status": "invalid_declaration",
                "summary": "repo interop contract is unreadable for external orchestrator conformance.",
                "missing_inputs": [f"repo interop contract is unreadable: {exc}"],
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": conformance["summary"],
                "missing_inputs": conformance["missing_inputs"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "external-orchestrator-interop", "result": "block"},
                "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
                "external_orchestrator": conformance,
            }
        )
        return payload
    external_orchestrators = interop_payload.get("external_orchestrators", []) if isinstance(interop_payload, dict) else []
    if not isinstance(external_orchestrators, list) or not external_orchestrators:
        conformance = empty_external_orchestrator_conformance()
        payload["reports"].append(
            {
                "id": "external-orchestrator-interop",
                "attempted": True,
                "command": f"read {interop_path}",
                "reported_command": "repo-interop.external_orchestrators",
                "reported_result": "not_applicable",
                "result": "pass",
                "summary": "repo interop is readable but declares no external orchestrators.",
                "missing_inputs": [],
                "fallback_to": None,
            }
        )
        payload.update(
            {
                "result": "pass",
                "summary": conformance["summary"],
                "profile_check": {"id": "external-orchestrator-interop", "result": "pass"},
                "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
                "external_orchestrator": conformance,
            }
        )
        return payload

    checks = [
        external_orchestrator_conformance_check(target_root, entry=entry, index=index)
        for index, entry in enumerate(external_orchestrators)
    ]
    for check in checks:
        payload["reports"].append(
            {
                "id": str(check["id"]),
                "attempted": True,
                "command": f"read {check.get('locator') or '<missing-locator>'}",
                "reported_command": "repo-interop.external_orchestrator",
                "reported_result": str(check["classification"]),
                "result": str(check["result"]),
                "summary": str(check["summary"]),
                "missing_inputs": list(check.get("missing_inputs", [])),
                "fallback_to": check.get("fallback_to"),
            }
        )

    has_block = any(check["result"] == "block" for check in checks)
    has_warn = any(check["result"] == "warn" for check in checks)
    result = "block" if has_block else "warn" if has_warn else "pass"
    conformance = empty_external_orchestrator_conformance()
    conformance.update(
        {
            "enabled": True,
            "result": result,
            "status": "present",
            "summary": (
                "external orchestrator conformance passed without introducing a daemon, scheduler state, or second status surface."
                if result == "pass"
                else "external orchestrator conformance produced profile-local warnings."
                if result == "warn"
                else "external orchestrator conformance found blocking interop drift."
            ),
            "missing_inputs": live_smoke_missing_inputs([message for check in checks for message in check.get("missing_inputs", [])]),
            "missing_optional": [message for check in checks for message in check.get("missing_optional", [])],
            "checks": checks,
        }
    )
    payload.update(
        {
            "result": result,
            "summary": conformance["summary"],
            "missing_inputs": conformance["missing_inputs"],
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else None,
            "profile_check": {"id": "external-orchestrator-interop", "result": result},
            "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
            "external_orchestrator": conformance,
            "command_plan": external_orchestrator_conformance_command_plan(target_root, external_orchestrators=external_orchestrators),
        }
    )
    return payload

def dynamic_tool_live_availability_payload(target_root: Path, *, surface: str) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    target = live_smoke_target_metadata(target_root)
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "dynamic-tool-availability",
        "schema_version": DYNAMIC_TOOL_LIVE_AVAILABILITY_SCHEMA,
        "runtime_state": runtime_state,
        "target": target,
        "command_plan": dynamic_tool_live_availability_command_plan(target_root, surface=surface),
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if runtime_state.get("result") != "pass":
        payload.update(
            {
                "result": "block",
                "summary": "dynamic tool live availability is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "block"},
                "dynamic_tool_availability": {
                    "contract_locator": ".loom/companion/repo-interface.json",
                    "availability": "runtime-blocked",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    target_report = live_smoke_target_check_report(target_root)
    payload["reports"] = [target_report]
    payload["missing_inputs"] = list(target_report.get("missing_inputs", []))
    if target_report["result"] != "pass":
        payload.update(
            {
                "result": "warn",
                "summary": "dynamic tool live availability recorded explicit unavailable evidence for the adopted-repo target.",
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "warn"},
                "dynamic_tool_availability": {
                    "contract_locator": ".loom/companion/repo-interface.json",
                    "availability": "target-unavailable",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    governance_surface = build_governance_surface(target_root)
    repo_interface = governance_surface.get("repo_interface")
    contract_locator = ".loom/companion/repo-interface.json"
    availability = "absent"
    if isinstance(repo_interface, dict):
        availability = str(repo_interface.get("availability") or "absent")
    interface_report = {
        "id": "repo-interface-contract",
        "attempted": True,
        "command": f"read {target_root / contract_locator}",
        "reported_command": "repo-interface-contract",
        "reported_result": availability,
        "result": "pass",
        "summary": "repo companion interface is readable.",
        "missing_inputs": [],
        "fallback_to": None,
    }
    payload["reports"].append(interface_report)

    if availability in {"absent", "companion_docs_only"}:
        summary = "repo companion interface is absent, so no dynamic tool live evidence can be consumed."
        if availability == "companion_docs_only":
            summary = "legacy companion docs are present, but no machine-readable repo companion interface declares dynamic tools."
        interface_report.update(
            {
                "result": "warn",
                "summary": summary,
                "missing_inputs": ["repo companion interface is absent"],
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "warn",
                "summary": summary,
                "missing_inputs": ["repo companion interface is absent"],
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "warn"},
                "dynamic_tool_availability": {
                    "contract_locator": contract_locator,
                    "availability": "absent",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    if not isinstance(repo_interface, dict) or availability == "incomplete":
        missing_inputs = []
        if isinstance(repo_interface, dict) and isinstance(repo_interface.get("missing_inputs"), list):
            missing_inputs = [str(message) for message in repo_interface.get("missing_inputs", [])]
        if not missing_inputs:
            missing_inputs = ["repo companion interface is unreadable"]
        interface_report.update(
            {
                "result": "block",
                "summary": "repo companion interface is incomplete or unreadable for dynamic tool live availability.",
                "missing_inputs": missing_inputs,
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": interface_report["summary"],
                "missing_inputs": live_smoke_missing_inputs(missing_inputs),
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "block"},
                "dynamic_tool_availability": {
                    "contract_locator": contract_locator,
                    "availability": "incomplete",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    if availability != "present":
        interface_report.update(
            {
                "result": "block",
                "summary": "repo companion interface returned an unknown availability state for dynamic tool live availability.",
                "missing_inputs": [f"unknown repo companion availability: {availability}"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": interface_report["summary"],
                "missing_inputs": interface_report["missing_inputs"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "block"},
                "dynamic_tool_availability": {
                    "contract_locator": contract_locator,
                    "availability": "incomplete",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    tool_availability = repo_interface.get("tool_availability") if surface == "all" else tool_availability_for_surface(repo_interface, surface=surface)
    if not isinstance(tool_availability, dict):
        interface_report.update(
            {
                "result": "block",
                "summary": "repo companion interface does not expose readable dynamic tool availability evidence.",
                "missing_inputs": ["repo companion interface must expose `tool_availability`"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": interface_report["summary"],
                "missing_inputs": interface_report["missing_inputs"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "block"},
                "dynamic_tool_availability": {
                    "contract_locator": contract_locator,
                    "availability": "incomplete",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    declared_tools = tool_availability.get("declared_tools")
    if not isinstance(declared_tools, list):
        interface_report.update(
            {
                "result": "block",
                "summary": "dynamic tool live availability did not expose a readable declared_tools list.",
                "missing_inputs": ["tool_availability must include `declared_tools` as a list"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
            }
        )
        payload.update(
            {
                "result": "block",
                "summary": interface_report["summary"],
                "missing_inputs": interface_report["missing_inputs"],
                "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "block"},
                "dynamic_tool_availability": {
                    "contract_locator": contract_locator,
                    "availability": "incomplete",
                    "surface": surface,
                    "tool_availability": empty_tool_availability(),
                },
            }
        )
        return payload

    payload["command_plan"] = dynamic_tool_live_availability_command_plan(
        target_root,
        surface=surface,
        declared_tools=declared_tools,
    )
    if not declared_tools:
        interface_report.update(
            {
                "result": "pass",
                "summary": "repo companion interface is readable and no dynamic tools apply to this live profile.",
                "missing_inputs": [],
                "fallback_to": None,
            }
        )
        payload.update(
            {
                "result": "pass",
                "summary": interface_report["summary"],
                "missing_inputs": [],
                "fallback_to": None,
                "profile_check": {"id": "dynamic-tool-live-availability", "result": "pass"},
                "dynamic_tool_availability": {
                    "contract_locator": contract_locator,
                    "availability": "present",
                    "surface": surface,
                    "tool_availability": tool_availability,
                },
            }
        )
        return payload

    advisory_messages: list[str] = []
    for tool in declared_tools:
        if not isinstance(tool, dict):
            continue
        report_result = "pass"
        if tool.get("result") == "block":
            report_result = "block"
        elif tool.get("status") != "advertised":
            report_result = "warn"
        report_missing_inputs = [str(message) for message in tool.get("missing_inputs", [])]
        if report_result == "warn":
            report_missing_inputs = [str(message) for message in tool.get("advisory", [])]
            for message in report_missing_inputs:
                if message not in advisory_messages:
                    advisory_messages.append(message)
        payload["reports"].append(
            {
                "id": str(tool.get("id") or "dynamic-tool"),
                "attempted": True,
                "command": f"read {tool.get('locator') or '<missing-locator>'}",
                "reported_command": "dynamic-tool-handshake",
                "reported_result": str(tool.get("status") or tool.get("failure_category") or "unknown"),
                "result": report_result,
                "summary": str(tool.get("summary") or "dynamic tool handshake declaration was read."),
                "missing_inputs": report_missing_inputs,
                "fallback_to": tool.get("fallback_to") if report_result == "block" else None,
            }
        )

    blocking_messages = [
        message
        for report in payload["reports"]
        if report.get("result") == "block"
        for message in report.get("missing_inputs", [])
    ]
    missing_inputs = live_smoke_missing_inputs([*blocking_messages, *advisory_messages])
    has_block = tool_availability.get("result") == "block"
    has_warn = any(report.get("result") == "warn" for report in payload["reports"])
    result = "block" if has_block else "warn" if has_warn else "pass"
    summary = "dynamic tool handshake declarations are readable and advertised for this live profile."
    if result == "warn":
        summary = "dynamic tool live availability produced profile-local warnings."
    if result == "block":
        summary = "dynamic tool live availability found blocking handshake declaration or availability gaps."
    payload.update(
        {
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else None,
            "profile_check": {"id": "dynamic-tool-live-availability", "result": result},
            "dynamic_tool_availability": {
                "contract_locator": contract_locator,
                "availability": "present",
                "surface": surface,
                "tool_availability": tool_availability,
            },
        }
    )
    return payload

def live_smoke_command_plan(target_root: Path, *, item: str, include_blocking_shadow: bool) -> list[dict[str, Any]]:
    target = command_target(target_root)
    plan = [
        {
            "id": "target-check",
            "command": f"test -d {target}",
            "description": "Confirm the adopted-repo target path exists before running live smoke checks.",
        },
        {
            "id": "governance-profile-status",
            "command": live_smoke_command(["governance-profile", "status", "--target", str(target_root)]),
            "description": "Read the adopted repo governance maturity surface.",
        },
        {
            "id": "governance-profile-upgrade-plan",
            "command": live_smoke_command(["governance-profile", "upgrade-plan", "--target", str(target_root)]),
            "description": "Record upgrade requirements as live confidence input.",
        },
        {
            "id": "runtime-parity",
            "command": live_smoke_command(["runtime-parity", "validate", "--target", str(target_root)]),
            "description": "Check Loom core runtime parity against the adopted repo surface.",
        },
        {
            "id": "shadow-parity",
            "command": live_smoke_command(["shadow-parity", "--target", str(target_root)]),
            "description": "Read validation-only shadow parity without changing merge gates.",
        },
        {
            "id": "flow-resume",
            "command": live_smoke_command(["flow", "resume", "--target", str(target_root), "--item", item]),
            "description": "Exercise resume flow on the adopted repo when the requested item exists.",
        },
    ]
    if include_blocking_shadow:
        plan.append(
            {
                "id": "shadow-parity-blocking",
                "command": live_smoke_command(["shadow-parity", "--target", str(target_root), "--blocking"]),
                "description": "Optional explicit blocking-mode shadow parity check; not sufficient blocking-upgrade evidence on its own.",
            }
        )
    return plan

def live_smoke_missing_inputs(messages: list[str]) -> list[str]:
    return list(dict.fromkeys(message for message in messages if isinstance(message, str) and message))

def live_smoke_target_check_report(target_root: Path) -> dict[str, Any]:
    if target_root.exists():
        return {
            "id": "target-check",
            "attempted": True,
            "command": f"test -d {command_target(target_root)}",
            "reported_command": "target-check",
            "reported_result": "pass",
            "result": "pass",
            "summary": "adopted-repo target root exists.",
            "missing_inputs": [],
            "fallback_to": None,
        }
    return {
        "id": "target-check",
        "attempted": True,
        "command": f"test -d {command_target(target_root)}",
        "reported_command": "target-check",
        "reported_result": "unavailable",
        "result": "warn",
        "summary": "adopted-repo target root is unavailable.",
        "missing_inputs": [f"adopted repo target is unavailable: {target_root}"],
        "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
    }

def live_smoke_command_report(target_root: Path, *, report_id: str, args: list[str]) -> dict[str, Any]:
    payload, errors = local_command_json(target_root, args)
    command = live_smoke_command(args)
    if payload is None:
        return {
            "id": report_id,
            "attempted": True,
            "command": command,
            "reported_command": args[0],
            "reported_result": "invalid-output",
            "result": "block",
            "summary": f"{args[0]} did not return readable JSON output.",
            "missing_inputs": live_smoke_missing_inputs(errors),
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
        }
    reported_result = str(payload.get("result") or "unknown")
    return {
        "id": report_id,
        "attempted": True,
        "command": command,
        "reported_command": payload.get("command"),
        "reported_result": reported_result,
        "result": "pass" if reported_result == "pass" else "warn",
        "summary": str(payload.get("summary") or f"{args[0]} completed without a summary."),
        "missing_inputs": live_smoke_missing_inputs([str(message) for message in payload.get("missing_inputs", [])]),
        "fallback_to": payload.get("fallback_to"),
    }

def parse_live_smoke_code_block(lines: list[str]) -> list[str]:
    commands: list[str] = []
    in_block = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            if in_block:
                break
            in_block = True
            continue
        if in_block and stripped:
            commands.append(stripped)
    return commands

def strip_inline_code(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        return stripped[1:-1]
    return stripped or None

def live_smoke_replay_payload(prior_evidence_path: Path, *, runtime_state: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "replay",
        "schema_version": LIVE_SMOKE_SCHEMA,
        "runtime_state": runtime_state,
        "command_plan": [],
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if runtime_state.get("result") != "pass":
        payload.update(
            {
                "result": "block",
                "summary": "live smoke replay is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "live_smoke": {
                    "status": "failed",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("failed"),
                },
            }
        )
        return payload
    if not prior_evidence_path.exists():
        payload.update(
            {
                "result": "block",
                "summary": "live smoke replay could not read the requested prior evidence.",
                "missing_inputs": [f"prior evidence path is unavailable: {prior_evidence_path}"],
                "fallback_to": LIVE_SMOKE_REPLAY_FALLBACK,
                "live_smoke": {
                    "status": "failed",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("failed"),
                },
                "prior_evidence": {
                    "path": str(prior_evidence_path),
                    "status": "missing",
                },
            }
        )
        return payload

    relative_path = str(prior_evidence_path)
    if prior_evidence_path.is_absolute():
        relative_path = str(prior_evidence_path.resolve())
    sections = markdown_sections(prior_evidence_path)
    commands = parse_live_smoke_code_block(sections.get("2. Commands", []))
    target_lines = sections.get("1. Target", [])
    availability_lines = sections.get("4. Current PR Availability Evidence", [])
    text = prior_evidence_path.read_text(encoding="utf-8")
    status_match = re.search(r"Current release evidence status:\s*`([^`]+)`", text)
    if status_match is None or "Release interpretation:" not in text:
        payload.update(
            {
                "result": "block",
                "summary": "live smoke replay evidence is missing required status or interpretation fields.",
                "missing_inputs": [f"{relative_path}: missing Current release evidence status or Release interpretation"],
                "fallback_to": LIVE_SMOKE_REPLAY_FALLBACK,
                "live_smoke": {
                    "status": "failed",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("failed"),
                },
                "prior_evidence": {
                    "path": relative_path,
                    "status": "invalid",
                },
            }
        )
        return payload

    def find_prefix(lines: list[str], prefix: str) -> str | None:
        for raw_line in lines:
            stripped = raw_line.strip()
            if stripped.startswith(prefix):
                return stripped[len(prefix) :].strip()
        return None

    prior_status = status_match.group(1).strip()
    release_interpretation = find_prefix(availability_lines, "- Release interpretation:") or live_smoke_release_interpretation("replayed")
    replay_report = {
        "id": "prior-evidence",
        "attempted": False,
        "command": f"read {relative_path}",
        "reported_command": "prior-evidence",
        "reported_result": prior_status,
        "result": "pass",
        "summary": "versioned prior-pass live smoke evidence was replayed without rerunning adopted-repo commands.",
        "missing_inputs": [],
        "fallback_to": None,
    }
    payload.update(
        {
            "result": "pass",
            "summary": "versioned prior-pass live smoke evidence was replayed.",
            "command_plan": [
                {
                    "id": "prior-evidence-read",
                    "command": live_smoke_command(["live-smoke", "replay", "--prior-evidence", relative_path]),
                    "description": "Replay versioned prior-pass evidence without rerunning adopted-repo commands.",
                }
            ],
            "reports": [replay_report],
            "live_smoke": {
                "status": "replayed",
                "executed_at": current_iso_timestamp(),
                "release_interpretation": release_interpretation,
            },
            "prior_evidence": {
                "path": relative_path,
                "status": prior_status,
                "target_family": find_prefix(target_lines, "- Adopted repo family:"),
                "smoke_branch": strip_inline_code(find_prefix(target_lines, "- Smoke branch recorded there:")),
                "smoke_commit": strip_inline_code(find_prefix(target_lines, "- Smoke commit recorded there:")),
                "smoke_worktree": strip_inline_code(find_prefix(target_lines, "- Smoke worktree recorded there:")),
                "commands": commands,
            },
        }
    )
    return payload

def live_smoke_run_payload(
    target_root: Path,
    *,
    item: str,
    dry_run: bool,
    include_blocking_shadow: bool,
) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    command_plan = live_smoke_command_plan(target_root, item=item, include_blocking_shadow=include_blocking_shadow)
    target = live_smoke_target_metadata(target_root)
    payload: dict[str, Any] = {
        "command": "live-smoke",
        "operation": "run",
        "schema_version": LIVE_SMOKE_SCHEMA,
        "runtime_state": runtime_state,
        "target": target,
        "command_plan": command_plan,
        "reports": [],
        "missing_inputs": [],
        "fallback_to": None,
    }
    if runtime_state.get("result") != "pass":
        payload.update(
            {
                "result": "block",
                "summary": "live smoke is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": live_smoke_missing_inputs([str(message) for message in runtime_state.get("missing_inputs", [])]),
                "fallback_to": runtime_state.get("fallback_to"),
                "live_smoke": {
                    "status": "failed",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("failed"),
                },
            }
        )
        return payload

    target_report = live_smoke_target_check_report(target_root)
    payload["reports"] = [target_report]
    payload["missing_inputs"] = list(target_report.get("missing_inputs", []))
    if target_report["result"] != "pass":
        payload.update(
            {
                "result": "warn",
                "summary": "live smoke recorded explicit unavailable evidence for the adopted-repo target.",
                "fallback_to": LIVE_SMOKE_RETRY_FALLBACK,
                "live_smoke": {
                    "status": "unavailable",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("unavailable"),
                },
            }
        )
        return payload

    if dry_run:
        payload.update(
            {
                "result": "pass",
                "summary": "live smoke command plan was generated without running adopted-repo commands.",
                "live_smoke": {
                    "status": "dry_run",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("dry_run"),
                },
            }
        )
        return payload

    reports = [target_report]
    for report_id, args in (
        ("governance-profile-status", ["governance-profile", "status", "--target", str(target_root)]),
        ("governance-profile-upgrade-plan", ["governance-profile", "upgrade-plan", "--target", str(target_root)]),
        ("runtime-parity", ["runtime-parity", "validate", "--target", str(target_root)]),
        ("shadow-parity", ["shadow-parity", "--target", str(target_root)]),
        ("flow-resume", ["flow", "resume", "--target", str(target_root), "--item", item]),
    ):
        reports.append(live_smoke_command_report(target_root, report_id=report_id, args=args))
    if include_blocking_shadow:
        reports.append(
            live_smoke_command_report(
                target_root,
                report_id="shadow-parity-blocking",
                args=["shadow-parity", "--target", str(target_root), "--blocking"],
            )
        )

    missing_inputs = live_smoke_missing_inputs(
        [message for report in reports for message in report.get("missing_inputs", [])]
    )
    has_internal_block = any(report.get("result") == "block" for report in reports)
    has_warning = any(report.get("result") == "warn" for report in reports)
    result = "block" if has_internal_block else "warn" if has_warning else "pass"
    status = "failed" if has_warning else "passed"
    summary = "live smoke produced explicit profile-local warnings." if result == "warn" else "live smoke completed across the planned command set."
    if result == "block":
        summary = "live smoke failed to produce stable command output."
    payload.update(
        {
            "result": result,
            "summary": summary,
            "reports": reports,
            "missing_inputs": missing_inputs,
            "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK if result == "block" else LIVE_SMOKE_RETRY_FALLBACK if result == "warn" else None,
            "live_smoke": {
                "status": status,
                "executed_at": current_iso_timestamp(),
                "release_interpretation": live_smoke_release_interpretation(status),
            },
        }
    )
    return payload

def handle_live_smoke(args: argparse.Namespace) -> int:
    if args.operation == "run":
        if not args.target:
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "run",
                    "schema_version": LIVE_SMOKE_SCHEMA,
                    "result": "block",
                    "summary": "live smoke run requires --target.",
                    "missing_inputs": ["pass --target <adopted_repo_root>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(Path.cwd()),
                    "command_plan": [],
                    "reports": [],
                    "live_smoke": {
                        "status": "failed",
                        "executed_at": current_iso_timestamp(),
                        "release_interpretation": live_smoke_release_interpretation("failed"),
                    },
                }
            )
        return emit(
            live_smoke_run_payload(
                resolve_target_arg(args.target),
                item=args.item,
                dry_run=args.dry_run,
                include_blocking_shadow=args.include_blocking_shadow,
            )
        )
    if args.operation == "external-result-source-readback":
        if not args.target:
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "external-result-source-readback",
                    "schema_version": EXTERNAL_RESULT_SOURCE_READBACK_SCHEMA,
                    "result": "block",
                    "summary": "external result source readback requires --target.",
                    "missing_inputs": ["pass --target <adopted_repo_root>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(Path.cwd()),
                    "command_plan": [],
                    "reports": [],
                    "profile_check": {"id": "external-result-source-readback", "result": "block"},
                    "external_result_source_readback": {
                        "contract_locator": ".loom/companion/interop.json",
                        "availability": "missing-target",
                        "checks": [],
                    },
                }
            )
        return emit(external_result_source_readback_payload(resolve_target_arg(args.target)))
    if args.operation == "dynamic-tool-availability":
        if not args.target:
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "dynamic-tool-availability",
                    "schema_version": DYNAMIC_TOOL_LIVE_AVAILABILITY_SCHEMA,
                    "result": "block",
                    "summary": "dynamic tool live availability requires --target.",
                    "missing_inputs": ["pass --target <adopted_repo_root>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(Path.cwd()),
                    "command_plan": [],
                    "reports": [],
                    "profile_check": {"id": "dynamic-tool-live-availability", "result": "block"},
                    "dynamic_tool_availability": {
                        "contract_locator": ".loom/companion/repo-interface.json",
                        "availability": "missing-target",
                        "surface": args.surface,
                        "tool_availability": empty_tool_availability(),
                    },
                }
            )
        return emit(
            dynamic_tool_live_availability_payload(
                resolve_target_arg(args.target),
                surface=args.surface,
            )
        )
    if args.operation == "hook-envelope":
        if not args.target:
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "hook-envelope",
                    "schema_version": HOOK_ENVELOPE_LIVE_CHECK_SCHEMA,
                    "result": "block",
                    "summary": "hook envelope check requires --target.",
                    "missing_inputs": ["pass --target <adopted_repo_root>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(Path.cwd()),
                    "target": live_smoke_target_metadata(Path.cwd()),
                    "command_plan": [],
                    "reports": [],
                    "profile_check": {"id": "hook-envelope", "result": "block"},
                    "hook_envelope": {
                        "contract_locator": args.envelope,
                        "availability": "missing-target",
                        "requirement": args.requirement,
                        "checks": [],
                    },
                }
            )
        if not args.envelope:
            target_root = resolve_target_arg(args.target)
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "hook-envelope",
                    "schema_version": HOOK_ENVELOPE_LIVE_CHECK_SCHEMA,
                    "result": "block",
                    "summary": "hook envelope check requires --envelope.",
                    "missing_inputs": ["pass --envelope <repo_relative_envelope_path>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(target_root),
                    "target": live_smoke_target_metadata(target_root),
                    "command_plan": hook_envelope_command_plan(target_root, envelope=args.envelope),
                    "reports": [],
                    "profile_check": {"id": "hook-envelope", "result": "block"},
                    "hook_envelope": {
                        "contract_locator": args.envelope,
                        "availability": "missing-envelope",
                        "requirement": args.requirement,
                        "checks": [],
                    },
                }
            )
        return emit(
            hook_envelope_payload(
                resolve_target_arg(args.target),
                envelope=args.envelope,
                requirement=args.requirement,
            )
        )
    if args.operation == "hooks-extension":
        if not args.target:
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "hooks-extension",
                    "schema_version": HOOKS_EXTENSION_PROFILE_SCHEMA,
                    "result": "block",
                    "summary": "hooks extension profile requires --target.",
                    "missing_inputs": ["pass --target <adopted_repo_root>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(Path.cwd()),
                    "target": live_smoke_target_metadata(Path.cwd()),
                    "command_plan": [],
                    "reports": [],
                    "profile_check": {"id": "hooks-extension", "result": "block"},
                    "core_profile": {"id": "orchestration-core", "hook_enforcement": "not_applicable", "result": "pass"},
                    "hooks_extension": {
                        **empty_hook_extension_profile(),
                        "status": "missing-target",
                        "result": "block",
                    },
                }
            )
        return emit(hooks_extension_payload(resolve_target_arg(args.target)))
    if args.operation == "external-orchestrator-interop":
        if not args.target:
            return emit(
                {
                    "command": "live-smoke",
                    "operation": "external-orchestrator-interop",
                    "schema_version": EXTERNAL_ORCHESTRATOR_CONFORMANCE_SCHEMA,
                    "result": "block",
                    "summary": "external orchestrator conformance requires --target.",
                    "missing_inputs": ["pass --target <adopted_repo_root>"],
                    "fallback_to": LIVE_SMOKE_CONFIG_FALLBACK,
                    "runtime_state": runtime_state_payload(Path.cwd()),
                    "target": live_smoke_target_metadata(Path.cwd()),
                    "command_plan": [],
                    "reports": [],
                    "profile_check": {"id": "external-orchestrator-interop", "result": "block"},
                    "core_profile": {"id": "orchestration-core", "external_orchestrator_enforcement": "not_applicable", "result": "pass"},
                    "external_orchestrator": {
                        **empty_external_orchestrator_conformance(),
                        "status": "missing-target",
                        "result": "block",
                    },
                }
            )
        return emit(external_orchestrator_conformance_payload(resolve_target_arg(args.target)))

    repo_root = Path(os.environ.get("LOOM_SOURCE_REPO_ROOT", Path.cwd())).expanduser().resolve()
    runtime_state = runtime_state_payload(repo_root)
    if not args.prior_evidence:
        return emit(
            {
                "command": "live-smoke",
                "operation": "replay",
                "schema_version": LIVE_SMOKE_SCHEMA,
                "result": "block",
                "summary": "live smoke replay requires --prior-evidence.",
                "missing_inputs": ["pass --prior-evidence <versioned_evidence_path>"],
                "fallback_to": LIVE_SMOKE_REPLAY_FALLBACK,
                "runtime_state": runtime_state,
                "command_plan": [],
                "reports": [],
                "live_smoke": {
                    "status": "failed",
                    "executed_at": current_iso_timestamp(),
                    "release_interpretation": live_smoke_release_interpretation("failed"),
                },
            }
        )
    return emit(live_smoke_replay_payload(Path(args.prior_evidence).expanduser().resolve(), runtime_state=runtime_state))
