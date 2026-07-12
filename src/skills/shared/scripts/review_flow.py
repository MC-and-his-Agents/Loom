#!/usr/bin/env python3
"""Semantic review execution, adapter selection, and review evidence domain."""

from __future__ import annotations
import argparse
import json
import os
import re
import select
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None  # type: ignore[assignment]
from fact_chain_support import (
    load_json_file,
    resolve_repo_relative_path,
)
from companion_contract import tool_availability_for_surface
from flow_runtime import emit, git_branch, git_head_sha, resolve_target_arg, run_git, runtime_state_payload
from delivery_control import (
    allowed_post_review_carrier_paths,
    allowed_terminal_closeout_carrier_paths,
    checkpoint_payload,
    checkpoint_rank,
    compat_findings_from_lists,
    compat_lists_from_findings,
    declared_scope_paths,
    dedupe_strings,
    default_spec_review_path,
    detect_github_repo,
    formal_spec_path,
    git_changed_paths,
    git_dirty_entries,
    git_merge_base,
    load_context_with_retained_idle_fallback,
    load_pr_payload_for_gate,
    load_review_record,
    normalize_review_findings,
    pr_metadata_preflight_payload,
    purity_report_from_context,
    relative_to_root,
    resolve_artifact_read_path,
    resolve_artifact_write_path,
    review_gate_payload,
    review_head_binding,
    spec_review_gate_payload,
    spec_review_gate_ready_for_implementation_review,
    spec_suite_validation_payload,
    suite_gate_consumed_inputs,
    suite_gate_payload_for_surface,
    suite_gate_step,
    suite_validation_fallback_to,
    suite_validation_missing_inputs,
    suite_validation_ready,
    utc_now_iso,
    validation_summary_hash,
    write_json_file,
)
from governance_surface import (
    build_governance_surface,
    derive_execution_budget_risk,
)
from runtime_paths import (
    global_runtime_locator_for_path,
    shared_asset,
)

FLOW_ENTRYPOINT = Path(__file__).with_name("loom_flow.py")

ADOPTION_REVIEW_ARTIFACT_LABELS = (
    "Active Work Item",
    "Active Recovery Entry",
    "Status Surface",
    "Review Record",
    "Spec Review Record",
)

TERMINAL_CHECKPOINTS = {
    "retired",
    "done",
    "closed",
    "closed_out",
    "merged",
    "archived",
}

RUNTIME_EVIDENCE_FIELDS = (
    "run_entry",
    "logs_entry",
    "diagnostics_entry",
    "verification_entry",
    "lane_entry",
)

REVIEW_DECISIONS = {"allow", "block", "fallback"}

IMPLEMENTATION_REVIEW_KINDS = {"general_review", "code_review"}

DEFAULT_REVIEW_ENGINE = "codex"

DEFAULT_REVIEW_ADAPTER = "loom/default-codex-exec"

CODEX_APP_REVIEW_ADAPTER = "loom/codex-app-review"

CODEX_APP_REVIEW_ENGINE = "codex-app-review"

CODEX_APP_REVIEW_SHADOW_ADAPTER = CODEX_APP_REVIEW_ADAPTER

AUTHORITATIVE_REVIEW_ADAPTERS = {DEFAULT_REVIEW_ADAPTER, CODEX_APP_REVIEW_ADAPTER}

CODEX_APP_REVIEW_ENDPOINT_ENV = "LOOM_CODEX_APP_REVIEW_ENDPOINT"

CODEX_APP_REVIEW_THREAD_ID_ENV = "LOOM_CODEX_APP_REVIEW_THREAD_ID"

CODEX_APP_REVIEW_CWD_ENV = "LOOM_CODEX_APP_REVIEW_CWD"

CODEX_APP_REVIEW_SESSION_FILE_ENV = "LOOM_CODEX_APP_REVIEW_SESSION_FILE"

CODEX_THREAD_ID_ENV = "CODEX_THREAD_ID"

CODEX_SESSION_ID_ENV = "CODEX_SESSION_ID"

CODEX_APP_REVIEW_NEW_THREAD_IDS = {"new", "new-thread", "start"}

CODEX_APP_REVIEW_LIVE_TIMEOUT_SECONDS = 900

LOOM_RUNTIME_ENV_KEYS = (
    "LOOM_SOURCE_REPO_ROOT",
    "LOOM_INSTALLED_SKILLS_ROOT",
    "LOOM_PACKAGE_SKILL_ID",
    "LOOM_RUNTIME_SCENE",
)

DEFAULT_REVIEW_ENGINE_TIMEOUT_SECONDS: int | None = None

REVIEW_ENGINE_PROFILE_SCHEMA = "loom-review-engine-profile/v1"

ADOPTED_REVIEW_ENGINE_ADAPTER_SCHEMA = "loom-adopted-review-engine-adapter/v1"

REVIEW_AUTHORITY_MIGRATION_SCHEMA = "loom-review-authority-migration/v1"

SPEC_REVIEW_AUTHORITY_MIGRATION_SCHEMA = "loom-spec-review-authority-migration/v1"

REVIEW_ENGINE_POLICY_SCHEMA = "loom-review-profiles/v1"

REVIEW_ENGINE_POLICY_RELATIVE = ".loom/review-profiles.json"

REVIEW_ENGINE_PROFILE_IDS = {"default", "high-risk", "spec-review", "repeated-blocker"}

REVIEW_ENGINE_REASONING_EFFORTS = {"low", "medium", "high", "xhigh"}

REVIEW_PROMPT_DIFF_MAX_CHARS = 60_000

REVIEW_PROMPT_DIFF_PATHS = (
    ".loom/bootstrap/init-result.json",
    ".loom/progress",
    ".loom/reviews",
    ".loom/specs",
    ".loom/status/current.md",
    ".loom/work-items",
    "docs/methodology/harness/review-execution.md",
    "src/skills/loom-review/SKILL.md",
    "src/skills/loom-spec-review/SKILL.md",
    "src/skills/shared/scripts/loom_check.py",
    "src/skills/shared/scripts/loom_flow.py",
    "skills/loom-review/SKILL.md",
    "skills/loom-spec-review/SKILL.md",
    "skills/shared/scripts/loom_check.py",
    "skills/shared/scripts/loom_flow.py",
)

REVIEW_ENGINE_PROFILES: dict[str, dict[str, Any]] = {
    "default": {
        "profile_id": "default",
        "model": "gpt-5.5",
        "reasoning_effort": "medium",
        "timeout_seconds": DEFAULT_REVIEW_ENGINE_TIMEOUT_SECONDS,
        "context_policy": "minimal-review-baseline",
        "selection_reason": "default implementation review profile for normal-risk changes",
    },
    "high-risk": {
        "profile_id": "high-risk",
        "model": "gpt-5.5",
        "reasoning_effort": "high",
        "timeout_seconds": DEFAULT_REVIEW_ENGINE_TIMEOUT_SECONDS,
        "context_policy": "expanded-risk-baseline",
        "selection_reason": "high-risk review profile for shared contracts, security, permissions, sandbox, or host-boundary changes",
    },
    "spec-review": {
        "profile_id": "spec-review",
        "model": "gpt-5.5",
        "reasoning_effort": "high",
        "timeout_seconds": DEFAULT_REVIEW_ENGINE_TIMEOUT_SECONDS,
        "context_policy": "formal-spec-suite-baseline",
        "selection_reason": "formal spec review profile",
    },
    "repeated-blocker": {
        "profile_id": "repeated-blocker",
        "model": "gpt-5.5",
        "reasoning_effort": "high",
        "timeout_seconds": DEFAULT_REVIEW_ENGINE_TIMEOUT_SECONDS,
        "context_policy": "recent-findings-and-dispositions",
        "selection_reason": "repeated blocker review profile",
    },
}

REVIEW_CONTEXT_PACK_SCHEMA = "loom-review-context-pack/v1"

REPEATED_BLOCKER_SIGNAL_SCHEMA = "loom-repeated-blocker-signal/v1"

PRE_REVIEW_REQUIRED_VALIDATION_TOKENS = (
    "git diff --check",
    "tools/skills_surface.py check",
    "tools/loom_check.py --profile source --source-surface contract-only",
)

PRE_REVIEW_RUNTIME_VALIDATION_TOKENS = (
    "tools/check_cli_contract.py",
)

PRE_REVIEW_RELEASE_VALIDATION_TOKENS = (
    "tools/check_release_surface.py",
    "tools/version_surface_check.py",
    "tools/check_npm_package.py",
)

PRE_REVIEW_RUNTIME_PATH_PREFIXES = (
    "tools/",
    "src/skills/",
    "skills/",
)

PRE_REVIEW_RELEASE_PATH_PREFIXES = (
    "VERSION",
    "package.json",
    "package-lock.json",
    "packages/",
    "plugins/",
    "skills/registry.json",
)

def repo_specific_default_fallback(surface: str) -> str:
    return {
        "spec_review": "build",
        "pre_review": "build",
        "review": "build",
        "merge_ready": "merge",
        "closeout": "merge",
    }[surface]

def policy_readiness_for_surface(repo_interface: object, *, surface: str) -> dict[str, Any]:
    empty_payload = {
        "schema_version": "loom-policy-readiness/v1",
        "surface": surface,
        "result": "pass",
        "summary": "no approval or sandbox policy evidence applies to this surface.",
        "declared_policies": [],
        "blocking_policies": [],
        "advisory_policies": [],
        "approval_policy": None,
        "sandbox_policy": None,
        "risk_summary": {
            "blocking": [],
            "advisory": [],
            "by_status": {
                "conflict": 0,
                "declared": 0,
                "missing": 0,
                "unsafe": 0,
            },
            "by_policy": {
                "approval": "missing",
                "sandbox": "missing",
            },
        },
        "missing_inputs": [],
        "fallback_to": None,
    }
    if not isinstance(repo_interface, dict):
        return empty_payload
    policy_readiness = repo_interface.get("policy_readiness")
    if not isinstance(policy_readiness, dict):
        return empty_payload
    declared_policies = policy_readiness.get("declared_policies")
    if not isinstance(declared_policies, list):
        return empty_payload

    applicable: list[dict[str, Any]] = []
    for policy in declared_policies:
        if not isinstance(policy, dict):
            continue
        policy_surface = policy.get("surface")
        if policy_surface in {surface, "attempt_time"}:
            applicable.append(policy)

    by_status = {
        "conflict": 0,
        "declared": 0,
        "missing": 0,
        "unsafe": 0,
    }
    by_policy = {
        "approval": "missing",
        "sandbox": "missing",
    }
    blocking_policies: list[dict[str, Any]] = []
    advisory_policies: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    fallback_to: str | None = None
    latest_by_policy: dict[str, dict[str, Any]] = {}
    for policy in applicable:
        status = policy.get("status")
        if isinstance(status, str) and status in by_status:
            by_status[status] += 1
        policy_type = policy.get("policy")
        if isinstance(policy_type, str) and policy_type in by_policy:
            by_policy[policy_type] = str(status or "missing")
            latest_by_policy[policy_type] = policy
        if policy.get("result") == "block":
            blocking_policies.append(policy)
            fallback = policy.get("fallback_to")
            if fallback_to is None and isinstance(fallback, str) and fallback:
                fallback_to = fallback
            for message in policy.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(str(message))
        elif policy.get("status") != "declared":
            advisory_policies.append(policy)

    result = "block" if blocking_policies else "pass"
    if blocking_policies:
        summary = "required approval or sandbox policy evidence blocks this surface."
    elif advisory_policies:
        summary = "only optional or advisory approval/sandbox policy risk applies to this surface."
    elif applicable:
        summary = "approval and sandbox policy evidence is declared for this surface."
    else:
        summary = empty_payload["summary"]
    return {
        **empty_payload,
        "result": result,
        "summary": summary,
        "declared_policies": applicable,
        "blocking_policies": blocking_policies,
        "advisory_policies": advisory_policies,
        "approval_policy": latest_by_policy.get("approval"),
        "sandbox_policy": latest_by_policy.get("sandbox"),
        "risk_summary": {
            "blocking": blocking_policies,
            "advisory": advisory_policies,
            "by_status": by_status,
            "by_policy": by_policy,
        },
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to if result == "block" else None,
    }

def repo_specific_requirements_payload(
    repo_interface: object,
    *,
    target_root: Path,
    surface: str,
) -> dict[str, Any]:
    empty_payload = {
        "surface": surface,
        "result": "pass",
        "source_locator": None,
        "declared_requirements": [],
        "blocking_requirements": [],
        "advisory_requirements": [],
        "summary": "no repo companion requirements are declared for this surface.",
        "missing_inputs": [],
        "fallback_to": None,
        "tool_availability": tool_availability_for_surface(repo_interface, surface=surface),
        "policy_readiness": policy_readiness_for_surface(repo_interface, surface=surface),
    }
    if not isinstance(repo_interface, dict):
        return {
            **empty_payload,
            "result": "block",
            "summary": "repo companion interface could not be read from governance_surface.",
            "missing_inputs": ["governance_surface.repo_interface"],
            "fallback_to": repo_specific_default_fallback(surface),
        }

    availability = repo_interface.get("availability")
    if availability == "absent":
        return {
            **empty_payload,
            "summary": "no repo companion interface is declared for this repository.",
        }
    if availability == "companion_docs_only":
        return {
            **empty_payload,
            "summary": "legacy companion docs are present, but no machine-readable repo companion requirements are declared.",
        }
    if availability == "incomplete":
        missing_inputs = repo_interface.get("missing_inputs")
        return {
            **empty_payload,
            "result": "block",
            "summary": "repo companion interface is incomplete, so Loom cannot safely consume repo-specific requirements.",
            "missing_inputs": list(missing_inputs) if isinstance(missing_inputs, list) else ["repo companion interface"],
            "fallback_to": repo_specific_default_fallback(surface),
        }
    if availability != "present":
        return {
            **empty_payload,
            "result": "block",
            "summary": "repo companion interface returned an unknown availability state.",
            "missing_inputs": [f"unknown repo companion availability: {availability}"],
            "fallback_to": repo_specific_default_fallback(surface),
        }

    repo_specific_locator = repo_interface.get("repo_specific_requirements")
    declared_locator = (
        repo_specific_locator.get("locator")
        if isinstance(repo_specific_locator, dict)
        else ".loom/companion/repo-interface.json"
    )
    repo_specific_path, locator_errors = resolve_repo_relative_path(
        target_root,
        str(declared_locator),
        label="repo companion requirements locator",
    )
    if locator_errors:
        return {
            **empty_payload,
            "result": "block",
            "summary": "repo companion requirements locator is unsafe.",
            "missing_inputs": locator_errors,
            "fallback_to": repo_specific_default_fallback(surface),
        }
    assert repo_specific_path is not None
    blocking: list[dict[str, Any]] = []
    advisory: list[dict[str, Any]] = []
    declared: list[dict[str, Any]] = []
    try:
        payload = load_json_file(repo_specific_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {
            **empty_payload,
            "result": "block",
            "summary": "repo companion requirements are declared, but the machine-readable interface could not be loaded.",
            "missing_inputs": [f"missing repo companion interface: {repo_specific_path}"],
            "fallback_to": repo_specific_default_fallback(surface),
        }

    requirements = payload.get("repo_specific_requirements") if isinstance(payload, dict) else None
    entries = requirements.get(surface) if isinstance(requirements, dict) else None
    if not isinstance(entries, list):
        if surface == "pre_review":
            return {
                **empty_payload,
                "source_locator": declared_locator,
                "summary": "no repo companion requirements are declared for the pre-review surface.",
            }
        return {
            **empty_payload,
            "result": "block",
            "summary": "repo companion interface is missing the requested surface requirements.",
            "missing_inputs": [f"repo companion surface missing: {surface}"],
            "fallback_to": repo_specific_default_fallback(surface),
        }

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        declared.append(entry)
        if entry.get("enforcement") == "blocking":
            blocking.append(entry)
        elif entry.get("enforcement") == "advisory":
            advisory.append(entry)

    if blocking:
        summary = (
            "companion-declared blocking requirements remain outside Loom core and must be handled before this surface can pass."
        )
        result = "block"
        fallback_to = repo_specific_default_fallback(surface)
        missing_inputs = [f"repo companion requirement: {entry.get('id', 'unknown')}" for entry in blocking]
    elif advisory:
        summary = "only companion-declared advisory requirements are present for this surface."
        result = "pass"
        fallback_to = None
        missing_inputs = []
    else:
        summary = "no repo companion requirements are declared for this surface."
        result = "pass"
        fallback_to = None
        missing_inputs = []

    tool_availability = tool_availability_for_surface(repo_interface, surface=surface)
    if tool_availability.get("result") == "block":
        result = "block"
        fallback_to = fallback_to or tool_availability.get("fallback_to") or repo_specific_default_fallback(surface)
        for message in tool_availability.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(str(message))
        if not blocking:
            summary = "required dynamic tool handshake evidence blocks this surface."
    policy_readiness = policy_readiness_for_surface(repo_interface, surface=surface)
    if policy_readiness.get("result") == "block":
        result = "block"
        fallback_to = fallback_to or policy_readiness.get("fallback_to") or repo_specific_default_fallback(surface)
        for message in policy_readiness.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(str(message))
        if not blocking and tool_availability.get("result") != "block":
            summary = "required approval or sandbox policy evidence blocks this surface."
    return {
        "surface": surface,
        "result": result,
        "source_locator": declared_locator,
        "declared_requirements": declared,
        "blocking_requirements": blocking,
        "advisory_requirements": advisory,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to,
        "tool_availability": tool_availability,
        "policy_readiness": policy_readiness,
    }

def suite_validation_consumed_inputs(suite_validation: dict[str, Any]) -> dict[str, Any]:
    suite_payload = suite_validation.get("payload") if isinstance(suite_validation.get("payload"), dict) else {}
    task_carriers = suite_payload.get("task_carrier_locators")
    if not isinstance(task_carriers, list):
        task_carriers = []
    consumed_contracts = suite_payload.get("consumed_contracts")
    if not isinstance(consumed_contracts, list):
        consumed_contracts = []
    return {
        "suite_validation": suite_validation.get("command"),
        "suite_validator": suite_validation.get("validator"),
        "suite_validator_mode": suite_validation.get("validator_mode"),
        "suite_spec": suite_payload.get("spec_locator"),
        "suite_plan": suite_payload.get("plan_locator"),
        "suite_evidence_map": suite_payload.get("evidence_map_locator"),
        "suite_consistency_analysis": suite_payload.get("consistency_analysis_locator"),
        "suite_task_carriers": task_carriers,
        "suite_consumed_contracts": consumed_contracts,
    }

def git_tracked_diff_fingerprint(root: Path) -> tuple[str | None, list[str]]:
    result = run_git(root, ["diff", "--binary", "--no-ext-diff", "HEAD", "--"])
    if result is None:
        return None, ["git is unavailable while fingerprinting tracked changes"]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git diff failed"
        return None, [detail]
    return result.stdout, []

def write_runtime_text_artifact(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = "\n".join(line.rstrip(" \t") for line in text.splitlines()).rstrip("\n") + "\n"
    path.write_text(normalized, encoding="utf-8")

def truthy_env(name: str) -> bool:
    value = os.environ.get(name)
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "off"}

def non_empty_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None

def cleanup_scratch_tree(target_root: Path, scratch_dir: Path) -> None:
    shutil.rmtree(scratch_dir, ignore_errors=True)
    for candidate in (scratch_dir.parent, scratch_dir.parent.parent):
        try:
            candidate.resolve().relative_to(target_root.resolve())
        except ValueError:
            continue
        try:
            candidate.rmdir()
        except OSError:
            pass

def artifact_locator_for_path(path: Path, root: Path) -> str:
    runtime_locator = global_runtime_locator_for_path(root, path)
    if runtime_locator is not None:
        return runtime_locator
    return relative_to_root(path, root)

def implementation_review_status_payload(context: dict[str, Any]) -> dict[str, Any]:
    review_record, review_path, review_errors = load_review_record(
        context["target_root"],
        context["item_id"],
        context["review_entry"],
    )
    missing_inputs = list(review_errors)
    head_binding = {
        "reviewed_head": None,
        "current_head": git_head_sha(context["target_root"]),
        "status": "unknown",
        "stale": None,
        "changed_paths": [],
        "disallowed_paths": [],
    }
    result = "pass"
    fallback_to: str | None = None
    if review_record is None and not review_errors:
        missing_inputs.append(f"missing implementation review artifact: {review_path}")
        result = "block"
        fallback_to = "build"
    elif review_record is not None:
        if review_record.get("kind") not in {"general_review", "code_review"}:
            missing_inputs.append("implementation review artifact must declare kind `general_review` or `code_review`")
            result = "block"
            fallback_to = "build"
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
    if review_record is not None and review_record.get("decision") == "block":
        missing_inputs.append(f"implementation review decision is blocking: {review_record['summary']}")
        result = "block"
        fallback_to = "build"
    elif review_record is not None and review_record.get("decision") == "fallback":
        missing_inputs.append(f"implementation review decision is fallback: {review_record['summary']}")
        result = "fallback"
        fallback_to = review_record.get("fallback_to") or "build"
    return {
        "path": review_path,
        "result": result,
        "summary": (
            "implementation review is approved for the current HEAD."
            if result == "pass"
            else "implementation review is missing, stale, or not approved."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to,
        "record": review_record,
        "head_binding": head_binding,
    }

def review_authority_migration_payload(
    *,
    review_payload: dict[str, Any] | None,
    review_kind: str,
    authority_before: str,
    authority_after: str,
) -> dict[str, Any]:
    record = review_payload.get("record") if isinstance(review_payload, dict) else None
    head_binding = review_payload.get("head_binding") if isinstance(review_payload, dict) else None
    missing_inputs: list[str] = []
    if not isinstance(review_payload, dict):
        missing_inputs.append("review authority payload")
    else:
        missing_inputs.extend(str(message) for message in review_payload.get("missing_inputs", []) if message)
    if not isinstance(record, dict):
        missing_inputs.append("loom review record")
    elif record.get("decision") != "allow":
        missing_inputs.append("loom review record decision is not allow")
    if isinstance(head_binding, dict) and head_binding.get("stale") is True:
        missing_inputs.append("loom review record head binding is stale")
    if isinstance(review_payload, dict) and review_payload.get("host_verdict_role") == "independent_blocker":
        missing_inputs.append("host verdict remains an independent blocker")
    if review_kind == "spec_review":
        schema = SPEC_REVIEW_AUTHORITY_MIGRATION_SCHEMA
        unique_authority = "loom spec review record"
        if isinstance(review_payload, dict):
            record_spec_locator = review_payload.get("record_spec_locator")
            current_spec_locator = review_payload.get("current_spec_locator")
            if isinstance(record, dict):
                record_spec_locator = record_spec_locator or record.get("spec_locator") or record.get("spec_path")
            if record_spec_locator and current_spec_locator and record_spec_locator != current_spec_locator:
                missing_inputs.append("loom spec review record locator does not match current spec locator")
    else:
        schema = REVIEW_AUTHORITY_MIGRATION_SCHEMA
        unique_authority = "loom review record"
    result = "pass" if not missing_inputs else "block"
    return {
        "schema_version": schema,
        "result": result,
        "summary": (
            f"{unique_authority} is the only current-head verdict authority."
            if result == "pass"
            else f"{unique_authority} is not yet safe to consume as the only verdict authority."
        ),
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
        "fallback_to": None if result == "pass" else "review",
        "review_kind": review_kind,
        "authority_before": authority_before,
        "authority_after": authority_after,
        "unique_verdict_authority": unique_authority,
        "host_status": "compatibility_mirror_or_rollback_only",
        "no_dual_authority": result == "pass",
        "fail_closed_conditions": [
            "missing-record",
            "malformed-record",
            "stale-head",
            "target-mismatch",
            "schema-drift",
            "contradictory-host-verdict",
            "dual-independent-blocker",
        ],
        "rollback": "restore the host-native verdict as the only blocker and mark the Loom record advisory until a fresh migration record is authored.",
        "record_locator": review_payload.get("path") if isinstance(review_payload, dict) else None,
        "head_binding": head_binding if isinstance(head_binding, dict) else None,
    }

def adopted_review_engine_adapter_payload(
    *,
    adapter_selection: dict[str, Any],
    engine_profile: dict[str, Any] | None,
    review_kind: str,
    reviewed_head: str,
    engine_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_adapter = adapter_selection.get("adapter")
    missing_inputs: list[str] = []
    if selected_adapter not in AUTHORITATIVE_REVIEW_ADAPTERS:
        missing_inputs.append(f"unsupported authoritative review adapter: {selected_adapter}")
    if engine_profile is None:
        missing_inputs.append("resolved review engine profile")
    if isinstance(adapter_selection.get("missing_host_proof"), list) and selected_adapter == CODEX_APP_REVIEW_ADAPTER:
        missing_inputs.extend(str(message) for message in adapter_selection["missing_host_proof"])
    if isinstance(engine_payload, dict):
        missing_inputs.extend(str(message) for message in engine_payload.get("missing_inputs", []) if message)
        if engine_payload.get("result") != "pass":
            missing_inputs.append(str(engine_payload.get("engine", {}).get("failure_reason") or "review engine did not pass"))
    result = "pass" if not missing_inputs else "block"
    return {
        "schema_version": ADOPTED_REVIEW_ENGINE_ADAPTER_SCHEMA,
        "result": result,
        "summary": (
            "adopted-repo review engine adapter can produce normalized review record input."
            if result == "pass"
            else "adopted-repo review engine adapter is blocked before authority consumption."
        ),
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
        "fallback_to": None if result == "pass" else "review",
        "review_kind": review_kind,
        "adapter": selected_adapter,
        "selection_source": adapter_selection.get("selection_source"),
        "fallback_reason": adapter_selection.get("fallback_reason"),
        "reviewed_head": reviewed_head,
        "engine_profile": engine_profile,
        "proof": adapter_selection.get("binding_summary"),
        "normalized_output": {
            "target": "review_record_input",
            "present": isinstance(engine_payload, dict) and isinstance(engine_payload.get("review_record_input"), dict),
            "locator": (
                engine_payload.get("review_record_input", {}).get("normalized_findings")
                if isinstance(engine_payload, dict) and isinstance(engine_payload.get("review_record_input"), dict)
                else None
            ),
        },
        "authority_phase": "execution_adapter_only",
        "fail_closed_conditions": [
            "proof-missing",
            "proof-conflict",
            "cwd-target-mismatch",
            "head-mismatch",
            "schema-drift",
            "output-missing",
            "tracked-file-mutation",
        ],
    }

def target_relative_label(target_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(target_root.resolve()))
    except ValueError:
        return str(path.resolve())

def load_findings_file(target_root: Path, findings_file: str) -> tuple[list[dict[str, Any]] | None, list[str]]:
    findings_path, locator_errors = resolve_artifact_read_path(target_root, findings_file, label="findings file locator")
    if locator_errors:
        return None, locator_errors
    assert findings_path is not None
    label = target_relative_label(target_root, findings_path)
    try:
        payload = json.loads(findings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid findings file `{label}`: {exc}"]

    if isinstance(payload, dict):
        payload = payload.get("findings")

    findings, errors = normalize_review_findings(payload, relative=label)
    if errors:
        return None, errors
    return findings, []

def repeated_blocker_key(finding: dict[str, Any]) -> str:
    finding_id = finding.get("id")
    if isinstance(finding_id, str) and finding_id.strip():
        return re.sub(r"[^a-z0-9]+", "-", finding_id.lower()).strip("-")
    summary = str(finding.get("summary", "")).lower()
    words = re.findall(r"[a-z0-9]+", summary)
    return "-".join(words[:10]) or "unknown"

def review_context_finding_entry(
    *,
    source: str,
    source_kind: str,
    reviewed_head: str | None,
    validation_summary: str | None,
    finding: dict[str, Any],
) -> dict[str, Any]:
    disposition = finding.get("disposition")
    disposition_status = disposition.get("status") if isinstance(disposition, dict) else None
    disposition_summary = disposition.get("summary") if isinstance(disposition, dict) else None
    return {
        "source": source,
        "source_kind": source_kind,
        "reviewed_head": reviewed_head,
        "validation_summary": validation_summary,
        "id": finding.get("id"),
        "summary": finding.get("summary"),
        "severity": finding.get("severity"),
        "disposition": {
            "status": disposition_status,
            "summary": disposition_summary,
        } if disposition_status or disposition_summary else None,
        "repeat_key": repeated_blocker_key(finding),
    }

def build_review_context_pack(context: dict[str, Any], review_path: str) -> dict[str, Any]:
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
    recent_findings: list[dict[str, Any]] = []
    review_record, _, review_errors = load_review_record(context["target_root"], context["item_id"], review_path)
    if review_record and not review_errors:
        for finding in review_record.get("findings", []):
            if isinstance(finding, dict):
                recent_findings.append(
                    review_context_finding_entry(
                        source=review_path,
                        source_kind="review_record",
                        reviewed_head=review_record.get("reviewed_head"),
                        validation_summary=review_record.get("reviewed_validation_summary"),
                        finding=finding,
                    )
                )

    runtime_history_root = resolve_artifact_read_path(
        context["target_root"],
        f".loom/runtime/review/{context['item_id']}",
        label="review runtime history",
    )[0] or (context["target_root"] / ".loom/runtime/review" / context["item_id"])
    if runtime_history_root.exists():
        for findings_path in sorted(runtime_history_root.glob("*/normalized-findings.json")):
            try:
                payload = load_json_file(findings_path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            raw_findings = payload.get("findings") if isinstance(payload, dict) else None
            findings_locator = artifact_locator_for_path(findings_path, context["target_root"])
            findings, errors = normalize_review_findings(raw_findings, relative=findings_locator)
            if errors:
                continue
            metadata_path = findings_path.parent / "engine-metadata.json"
            metadata: dict[str, Any] = {}
            if metadata_path.exists():
                try:
                    loaded = load_json_file(metadata_path)
                    if isinstance(loaded, dict):
                        metadata = loaded
                except (OSError, ValueError, json.JSONDecodeError):
                    metadata = {}
            for finding in findings:
                recent_findings.append(
                    review_context_finding_entry(
                        source=findings_locator,
                        source_kind="normalized_findings",
                        reviewed_head=metadata.get("reviewed_head") if isinstance(metadata.get("reviewed_head"), str) else None,
                        validation_summary=metadata.get("validation_summary") if isinstance(metadata.get("validation_summary"), str) else None,
                        finding=finding,
                    )
                )

    groups: dict[str, list[dict[str, Any]]] = {}
    for finding in recent_findings:
        if finding.get("severity") == "block":
            groups.setdefault(str(finding.get("repeat_key") or "unknown"), []).append(finding)
    candidates = [
        {
            "repeat_key": key,
            "count": len(entries),
            "sources": [entry["source"] for entry in entries],
            "summaries": [entry["summary"] for entry in entries if entry.get("summary")],
            "recommended_action": "treat as a root-cause candidate before repeating another local patch",
        }
        for key, entries in sorted(groups.items())
        if len(entries) >= 2
    ]
    return {
        "schema_version": REVIEW_CONTEXT_PACK_SCHEMA,
        "item_id": context["item_id"],
        "review_path": review_path,
        "current_head": git_head_sha(context["target_root"]) or "unknown-head",
        "validation_summary": context["latest_validation_summary"],
        "history_available": bool(recent_findings),
        "history_policy": "not_applicable when no prior review record or normalized findings are available",
        "recent_findings": recent_findings[-20:],
        "budget_risk": budget_risk,
        "repeated_blocker_signal": {
            "schema_version": REPEATED_BLOCKER_SIGNAL_SCHEMA,
            "result": "present" if candidates else "absent",
            "enforcement": "advisory",
            "summary": (
                "Repeated blocker candidates are present; reviewer should classify root-cause risk."
                if candidates
                else "No repeated blocker candidates detected in available review history."
            ),
            "candidates": candidates,
        },
    }

def build_review_flow_payload(
    target_root: Path,
    output_relative: str,
    expected_item: str | None,
    *,
    operation: str = "review",
    require_review_entry: bool = True,
    owner: str | None = None,
    repo_name: str | None = None,
    pr_number: int | None = None,
    branch_name: str | None = None,
    pr_payload_file: str | None = None,
) -> dict[str, Any]:
    runtime_state = runtime_state_payload(target_root)
    steps: list[dict[str, Any]] = [
        {
            "name": "runtime-state",
            "result": runtime_state["result"],
            "summary": runtime_state["summary"],
            "missing_inputs": runtime_state["missing_inputs"],
            "fallback_to": runtime_state["fallback_to"],
        }
    ]
    if runtime_state["result"] != "pass":
        return {
            "command": "flow",
            "operation": operation,
            "result": "block",
            "summary": "flow command is blocked because the Loom runtime state is inconsistent.",
            "missing_inputs": runtime_state["missing_inputs"],
            "fallback_to": runtime_state["fallback_to"],
            "steps": steps,
            "runtime_state": runtime_state,
        }

    context, errors = load_context_with_retained_idle_fallback(target_root, output_relative, expected_item)
    if errors:
        return {
            "command": "flow",
            "operation": operation,
            "result": "block",
            "summary": "flow command could not read a valid Loom fact chain.",
            "missing_inputs": [f"fact-chain: {message}" for message in errors],
            "fallback_to": "admission",
            "steps": steps,
            "runtime_state": runtime_state,
            **fact_chain_error_contract(errors, output_relative=output_relative),
        }

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

    build_payload = checkpoint_payload("build", context)
    governance_surface = build_governance_surface(target_root)
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
    surface_name = "review"
    repo_specific_requirements = repo_specific_requirements_payload(
        governance_surface.get("repo_interface"),
        target_root=target_root,
        surface=surface_name,
    )
    pr_metadata_preflight = (
        pr_metadata_preflight_payload(
            target_root=target_root,
            surface="review",
            owner=owner,
            repo_name=repo_name,
            pr_number=pr_number,
            branch_name=branch_name,
            pr_payload_file=pr_payload_file,
            governance_surface=governance_surface,
        )
        if operation == "review"
        else None
    )
    suite_gate_validation: dict[str, Any] | None = None
    if operation == "spec-review":
        review_path = default_spec_review_path(context["item_id"])
        review_record, _, review_errors = load_review_record(target_root, context["item_id"], review_path)
        suite_validation = spec_suite_validation_payload(context)
        suite_step_result = "pass" if suite_validation_ready(suite_validation) else "block"
        suite_step_missing = [] if suite_step_result == "pass" else suite_validation_missing_inputs(suite_validation)
        review_step_name = "spec-review-entry"
        review_step_result = "pass" if review_record and not review_errors else "block"
        review_step_summary = (
            "spec review artifact is readable and ready for authoring."
            if review_record and not review_errors
            else "spec review artifact is missing or invalid."
        )
        review_step_missing = review_errors or ([] if review_record else [f"missing review artifact: {review_path}"])
        review_step_fallback = "build" if (review_errors or review_record is None) else None
        review_payload = {
            "path": review_path,
            "record": review_record,
        }
        review_authority = review_authority_migration_payload(
            review_payload=review_payload,
            review_kind="spec_review",
            authority_before="repo-owned spec review gate or guardian compatibility verdict",
            authority_after="loom spec review record",
        )
        extra_steps: list[dict[str, Any]] = [
            {
                "name": "suite-validate",
                "result": suite_step_result,
                "summary": str(suite_validation.get("summary") or "suite validation was consumed before spec review."),
                "missing_inputs": suite_step_missing,
                "fallback_to": None if suite_step_result == "pass" else suite_validation_fallback_to(suite_validation),
            }
        ]
    else:
        review_path = context["review_entry"]
        review_record, _, review_errors = load_review_record(target_root, context["item_id"], review_path)
        review_payload = review_gate_payload(
            context,
            review_path=review_path,
            expected_kind=implementation_review_kind(context),
            gate_name="implementation_review",
            required=True,
        )
        review_authority = review_authority_migration_payload(
            review_payload=review_payload,
            review_kind=implementation_review_kind(context),
            authority_before="host guardian or repo-native implementation review verdict",
            authority_after="loom review record",
        )
        spec_gate = spec_review_gate_payload(context)
        suite_gate_validation = suite_gate_payload_for_surface(context, surface="review")
        extra_steps = [
            {
                "name": "spec-review-gate",
                "result": (
                    "pass"
                    if spec_gate["result"] in {"pass", "not_applicable"}
                    else ("fallback" if spec_gate["result"] == "fallback" else "block")
                ),
                "summary": spec_gate["summary"],
                "missing_inputs": spec_gate["missing_inputs"],
                "fallback_to": spec_gate["fallback_to"],
            },
            suite_gate_step("suite-evidence-validate", suite_gate_validation, "evidence"),
            suite_gate_step("suite-carrier-validate", suite_gate_validation, "carrier"),
        ]
        if isinstance(pr_metadata_preflight, dict):
            extra_steps.append(
                {
                    "name": "pr-metadata-preflight",
                    "result": pr_metadata_preflight["result"],
                    "summary": pr_metadata_preflight["summary"],
                    "missing_inputs": pr_metadata_preflight["missing_inputs"],
                    "fallback_to": pr_metadata_preflight["fallback_to"],
                    "pr_metadata_preflight": pr_metadata_preflight,
                }
            )
        review_step_name = "review-entry"
        review_step_result = "pass" if (review_record and not review_errors) or not require_review_entry else "block"
        review_step_summary = (
            "formal review artifact is readable."
            if review_record and not review_errors
            else "formal review artifact will be authored from this review run."
            if not require_review_entry
            else "formal review artifact is missing or invalid."
        )
        review_step_missing = [] if not require_review_entry and not review_errors else review_errors or ([] if review_record else [f"missing review artifact: {review_path}"])
        review_step_fallback = "build" if require_review_entry and (review_errors or review_record is None) else None
    steps.extend(
        [
            {
                "name": "checkpoint-build",
                "result": build_payload["result"],
                "summary": build_payload["summary"],
                "missing_inputs": build_payload["missing_inputs"],
                "fallback_to": build_payload["fallback_to"],
            },
            *extra_steps,
            {
                "name": review_step_name,
                "result": review_step_result,
                "summary": review_step_summary,
                "missing_inputs": review_step_missing,
                "fallback_to": review_step_fallback,
            },
        ]
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
    if result != "block" and repo_specific_requirements["result"] == "block":
        result = "block"
        fallback_to = fallback_to or repo_specific_requirements["fallback_to"]
    if (
        operation == "review"
        and isinstance(pr_metadata_preflight, dict)
        and pr_metadata_preflight.get("result") == "block"
    ):
        result = "block"
        fallback_to = pr_metadata_preflight.get("fallback_to") or fallback_to

    if result == "block" and repo_specific_requirements["result"] == "block":
        summary = (
            "spec-review flow exposed companion-declared blocking requirements instead of pretending Loom core already covers them."
            if operation == "spec-review"
            else "review flow exposed companion-declared blocking requirements instead of pretending Loom core already covers them."
        )
    else:
        summary = (
            "spec-review flow prepared the formal spec review context and exposed the spec gate artifact."
            if operation == "spec-review" and result == "pass"
            else (
                "spec-review flow found missing spec review material or earlier blocking signals."
                if operation == "spec-review"
                else (
                    "review flow prepared the semantic review context and exposed the formal review artifact."
                    if result == "pass"
                    else "review flow found missing review material or earlier blocking signals."
                )
            )
        )

    missing_inputs: list[str] = []
    for step in steps:
        if step["result"] in {"block", "fallback"}:
            for message in step.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(message)
    if repo_specific_requirements["result"] == "block":
        for message in repo_specific_requirements.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    if (
        operation == "review"
        and isinstance(pr_metadata_preflight, dict)
        and pr_metadata_preflight.get("result") == "block"
    ):
        for message in pr_metadata_preflight.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    recovery_readiness = report_recovery_readiness(context["report"])
    if recovery_readiness.get("result") == "block" and result == "pass":
        result = "block"
        fallback_to = fallback_to or recovery_readiness.get("fallback_to") or "admission"
        summary = f"{operation} flow rebuilt context but recovery readiness is blocking."

    return {
        "command": "flow",
        "operation": operation,
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
        "provenance": report_provenance(context["report"]),
        "recovery_readiness": recovery_readiness,
        "blocking_failures": report_blocking_failures(context["report"]),
        "state_check": {
            "result": state_payload["result"],
            "summary": state_payload["summary"],
            "missing_inputs": state_payload["missing_inputs"],
            "fallback_to": state_payload["fallback_to"],
            "checks": state_payload["checks"],
        },
        "runtime_evidence": runtime_fields,
        "budget_risk": budget_risk,
        "build_checkpoint": {
            "result": build_payload["result"],
            "summary": build_payload["summary"],
            "missing_inputs": build_payload["missing_inputs"],
            "fallback_to": build_payload["fallback_to"],
        },
        **(
            {
                "spec_review": review_payload,
                "suite_validation": suite_validation,
                "spec_review_authority_migration": review_authority,
            }
            if operation == "spec-review"
            else {
                "review": {
                    "path": review_path,
                    "record": review_record,
                },
                "spec_review": spec_gate,
                "suite_gate_validation": suite_gate_validation,
                "review_authority_migration": review_authority,
            }
        ),
        "repo_specific_requirements": repo_specific_requirements,
        **({"pr_metadata_preflight": pr_metadata_preflight} if isinstance(pr_metadata_preflight, dict) else {}),
        "current_checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": context["current_checkpoint"],
        },
    }

def run_default_review_engine(
    context: dict[str, Any],
    build_payload: dict[str, Any],
    review_path: str,
    engine_profile: dict[str, Any],
    *,
    review_kind: str | None = None,
    adapter_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reviewed_head = git_head_sha(context["target_root"]) or "unknown-head"
    selection_metadata = review_adapter_selection_metadata(
        adapter_selection
        or {
            "adapter": DEFAULT_REVIEW_ADAPTER,
            "selection_source": "explicit-or-legacy-default",
            "fallback_reason": None,
            "binding_summary": codex_app_binding_summary(
                context["target_root"],
                app_server=None,
                thread_id=None,
                thread_cwd=None,
                reviewed_head=reviewed_head,
                raw_file=None,
            ),
        },
        reviewed_head=reviewed_head,
    )
    runtime_root = review_runtime_root(context, reviewed_head)
    prompt_path = runtime_root / "prompt.txt"
    result_path = runtime_root / "engine-result.json"
    findings_path = runtime_root / "normalized-findings.json"
    metadata_path = runtime_root / "engine-metadata.json"
    context_pack_path = runtime_root / "context-pack.json"
    scratch_dir = resolve_artifact_write_path(
        context["target_root"],
        f".loom/runtime/tmp/review-engine/{context['item_id']}",
        label="review engine scratch directory",
    )[0] or (context["target_root"] / ".loom/runtime/tmp" / "review-engine" / context["item_id"])
    context_pack = build_review_context_pack(context, review_path)
    runtime_root.mkdir(parents=True, exist_ok=True)
    write_json_file(context_pack_path, context_pack)
    prompt_text = build_default_review_prompt(
        context=context,
        build_payload=build_payload,
        runtime_fields=runtime_evidence_from_report(context["report"])[0],
        review_path=review_path,
        context_pack=context_pack,
    )
    write_runtime_text_artifact(prompt_path, prompt_text)

    effective_kind = review_kind or default_review_kind(context)
    raw_timeout_seconds = engine_profile.get("timeout_seconds")
    timeout_seconds = int(raw_timeout_seconds) if raw_timeout_seconds is not None else None

    before_fingerprint, fingerprint_errors = git_tracked_diff_fingerprint(context["target_root"])
    if fingerprint_errors:
        cleanup_scratch_tree(context["target_root"], scratch_dir)
        return {
            "result": "block",
            "summary": "default review engine could not verify tracked-change purity before execution.",
            "missing_inputs": [f"engine preflight: {message}" for message in fingerprint_errors],
            "fallback_to": None,
            "engine": {
                "engine": DEFAULT_REVIEW_ENGINE,
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "profile": engine_profile,
                "result": "block",
                "failure_reason": "runtime_conflict",
                "reviewed_head": reviewed_head,
                "evidence": {
                    "runtime_root": artifact_locator_for_path(runtime_root, context["target_root"]),
                    "prompt": artifact_locator_for_path(prompt_path, context["target_root"]),
                    "raw_result": artifact_locator_for_path(result_path, context["target_root"]),
                    "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
                    "metadata": artifact_locator_for_path(metadata_path, context["target_root"]),
                    "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
                },
            },
            "engine_metadata": selection_metadata,
        }

    scratch_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    scratch_dir_text = str(scratch_dir.resolve())
    env["TMPDIR"] = scratch_dir_text
    env["TMP"] = scratch_dir_text
    env["TEMP"] = scratch_dir_text

    failure_reason: str | None = None
    failure_detail: str | None = None
    raw_payload: dict[str, Any] | None = None
    try:
        completed = subprocess.run(
            [
                DEFAULT_REVIEW_ENGINE,
                "exec",
                "-C",
                str(context["target_root"]),
                "-m",
                str(engine_profile["model"]),
                "-c",
                f"model_reasoning_effort={json.dumps(engine_profile['reasoning_effort'])}",
                "-s",
                "workspace-write",
                "--output-schema",
                str(review_engine_schema_path()),
                "-o",
                str(result_path),
                "-",
            ],
            cwd=context["target_root"],
            env=env,
            input=prompt_text,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError:
        failure_reason = "engine_unavailable"
        failure_detail = f"default review engine `{DEFAULT_REVIEW_ENGINE}` is unavailable in PATH"
    except subprocess.TimeoutExpired:
        failure_reason = "runtime_conflict"
        failure_detail = f"default review engine timed out after {timeout_seconds}s"
    else:
        if completed.returncode != 0:
            failure_reason = "runtime_conflict"
            failure_detail = completed.stderr.strip() or completed.stdout.strip() or "default review engine returned a non-zero exit status"
        else:
            try:
                if result_path.exists():
                    raw_payload = load_json_file(result_path)
                elif completed.stdout.strip():
                    raw_payload = json.loads(completed.stdout)
                else:
                    failure_reason = "schema_drift"
                    failure_detail = "default review engine did not emit a structured result"
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                failure_reason = "schema_drift"
                failure_detail = f"default review engine returned invalid JSON: {exc}"

    after_fingerprint, after_errors = git_tracked_diff_fingerprint(context["target_root"])
    if after_errors and failure_reason is None:
        failure_reason = "runtime_conflict"
        failure_detail = after_errors[0]
    elif failure_reason is None and before_fingerprint != after_fingerprint:
        failure_reason = "repo_diff_detected"
        failure_detail = "default review engine modified tracked repository content"

    if failure_reason is None and raw_payload is None:
        failure_reason = "schema_drift"
        failure_detail = "default review engine did not produce a readable review result"

    engine_evidence = {
        "runtime_root": artifact_locator_for_path(runtime_root, context["target_root"]),
        "prompt": artifact_locator_for_path(prompt_path, context["target_root"]),
        "raw_result": artifact_locator_for_path(result_path, context["target_root"]),
        "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
        "metadata": artifact_locator_for_path(metadata_path, context["target_root"]),
        "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
    }

    if failure_reason is not None:
        write_json_file(
            metadata_path,
            {
                "engine": DEFAULT_REVIEW_ENGINE,
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "profile": engine_profile,
                **selection_metadata,
                "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
                "failure_reason": failure_reason,
                "summary": failure_detail,
                "reviewed_head": reviewed_head,
            },
        )
        cleanup_scratch_tree(context["target_root"], scratch_dir)
        return {
            "result": "block",
            "summary": "default review engine failed closed before a formal review record could be authored.",
            "missing_inputs": [failure_detail or f"default review engine failed: {failure_reason}"],
            "fallback_to": None,
            "engine": {
                "engine": DEFAULT_REVIEW_ENGINE,
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "profile": engine_profile,
                "result": "block",
                "failure_reason": failure_reason,
                "reviewed_head": reviewed_head,
                "evidence": engine_evidence,
            },
            "engine_metadata": selection_metadata,
        }

    if raw_payload is not None and not result_path.exists():
        write_json_file(result_path, raw_payload)

    normalized_payload, normalization_errors = normalize_engine_review_result(
        raw_payload,
        relative=artifact_locator_for_path(result_path, context["target_root"]),
    )
    if normalization_errors or normalized_payload is None:
        write_json_file(
            metadata_path,
            {
                "engine": DEFAULT_REVIEW_ENGINE,
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "profile": engine_profile,
                **selection_metadata,
                "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
                "failure_reason": "schema_drift",
                "summary": "normalized engine output did not satisfy Loom review schema",
                "errors": normalization_errors,
                "reviewed_head": reviewed_head,
            },
        )
        cleanup_scratch_tree(context["target_root"], scratch_dir)
        return {
            "result": "block",
            "summary": "default review engine returned a structured payload that Loom could not safely normalize.",
            "missing_inputs": normalization_errors,
            "fallback_to": None,
            "engine": {
                "engine": DEFAULT_REVIEW_ENGINE,
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "profile": engine_profile,
                "result": "block",
                "failure_reason": "schema_drift",
                "reviewed_head": reviewed_head,
                "evidence": engine_evidence,
            },
            "engine_metadata": selection_metadata,
        }

    write_json_file(findings_path, {"findings": normalized_payload["findings"]})
    write_json_file(
        metadata_path,
            {
                "engine": DEFAULT_REVIEW_ENGINE,
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "profile": engine_profile,
                **selection_metadata,
                "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
                "result": "pass",
                "reviewed_head": reviewed_head,
                "decision": normalized_payload["decision"],
                "summary": normalized_payload["summary"],
                "kind": effective_kind,
                "validation_summary": context["latest_validation_summary"],
            },
        )
    cleanup_scratch_tree(context["target_root"], scratch_dir)
    return {
        "result": "pass",
        "summary": "default review engine produced a Loom-normalized formal review draft.",
        "missing_inputs": [],
        "fallback_to": None,
        "engine": {
            "engine": DEFAULT_REVIEW_ENGINE,
            "adapter": DEFAULT_REVIEW_ADAPTER,
            "profile": engine_profile,
            "result": "pass",
            "failure_reason": None,
            "reviewed_head": reviewed_head,
            "evidence": engine_evidence,
        },
        "engine_metadata": {
            **selection_metadata,
            "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
            "raw_result": artifact_locator_for_path(result_path, context["target_root"]),
            "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
            "metadata": artifact_locator_for_path(metadata_path, context["target_root"]),
        },
        "review_record_input": {
            "decision": normalized_payload["decision"],
            "summary": normalized_payload["summary"],
            "reviewer": DEFAULT_REVIEW_ADAPTER,
            "kind": effective_kind,
            "findings_file": artifact_locator_for_path(findings_path, context["target_root"]),
            "engine_adapter": DEFAULT_REVIEW_ADAPTER,
            "engine_evidence": artifact_locator_for_path(result_path, context["target_root"]),
            "engine_profile": engine_profile,
            "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
            "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
            "budget_risk": context_pack.get("budget_risk"),
        },
    }

def parse_review_artifact_locators(section: str) -> tuple[dict[str, str], list[str]]:
    locators: dict[str, str] = {}
    errors: list[str] = []
    for raw_line in section.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        match = re.match(r"^- ([^:]+):\s*(.+?)\s*$", stripped)
        if not match:
            errors.append(f"invalid Review Artifacts bullet: {stripped}")
            continue
        label = match.group(1).strip()
        value = match.group(2).strip().strip("`")
        if label in locators:
            errors.append(f"duplicate Review Artifacts field: {label}")
            continue
        locators[label] = value
    for label in ADOPTION_REVIEW_ARTIFACT_LABELS:
        if label not in locators:
            errors.append(f"Review Artifacts missing `{label}`")
    return locators, errors

def review_runtime_root(context: dict[str, Any], reviewed_head: str | None = None) -> Path:
    head = (reviewed_head or git_head_sha(context["target_root"]) or "unknown-head").strip() or "unknown-head"
    safe_head = re.sub(r"[^A-Za-z0-9_.-]", "-", head)
    return resolve_artifact_write_path(
        context["target_root"],
        f".loom/runtime/review/{context['item_id']}/{safe_head}",
        label="review runtime root",
    )[0] or (context["target_root"] / ".loom/runtime/review" / context["item_id"] / safe_head)

def default_review_kind(context: dict[str, Any]) -> str:
    scope_paths = declared_scope_paths(context["scope"])
    if scope_paths and all(path.endswith(".md") or path.startswith(".loom/") for path in scope_paths):
        return "general_review"
    return "code_review"

def implementation_review_kind(context: dict[str, Any]) -> str:
    scope_paths = declared_scope_paths(context["scope"])
    if scope_paths and all(path.endswith(".md") or path.startswith(".loom/") for path in scope_paths):
        return "general_review"
    return "code_review"

def review_engine_profile_selection(context: dict[str, Any], review_kind: str) -> tuple[str, str]:
    if review_kind == "spec_review":
        return "spec-review", "spec review requires the formal spec profile instead of inheriting host defaults"
    haystack = " ".join(
        str(context.get(key, ""))
        for key in (
            "goal",
            "scope",
            "execution_path",
            "current_stop",
            "next_step",
            "blockers",
            "latest_validation_summary",
        )
    ).lower()
    high_risk_terms = (
        "security",
        "permission",
        "approval",
        "sandbox",
        "host",
        "adapter",
        "shared contract",
        "contract",
        "runtime",
        "release",
    )
    if any(term in haystack for term in high_risk_terms):
        return "high-risk", "risk terms in the active item require the high-risk formal review profile"
    if "repeated blocker" in haystack or "repeated-blocker" in haystack:
        return "repeated-blocker", "active item references repeated blocker review handling"
    return "default", "default implementation review profile for normal-risk changes"

def review_profile_summary(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": profile.get("profile_id"),
        "model": profile.get("model"),
        "reasoning_effort": profile.get("reasoning_effort"),
        "timeout_seconds": profile.get("timeout_seconds"),
        "context_policy": profile.get("context_policy"),
    }

def validate_review_profile_fields(profile: dict[str, Any], *, context: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile.get("model"), str) or not profile["model"].strip():
        errors.append(f"{context} model must be non-empty")
    if profile.get("reasoning_effort") not in REVIEW_ENGINE_REASONING_EFFORTS:
        errors.append(f"{context} reasoning_effort is outside the stable vocabulary")
    timeout_seconds = profile.get("timeout_seconds")
    if timeout_seconds is not None:
        if not isinstance(timeout_seconds, int) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
            errors.append(f"{context} timeout_seconds must be a positive integer or null")
    if not isinstance(profile.get("context_policy"), str) or not profile["context_policy"].strip():
        errors.append(f"{context} context_policy must be non-empty")
    if not isinstance(profile.get("selection_reason"), str) or not profile["selection_reason"].strip():
        errors.append(f"{context} selection_reason must be non-empty")
    return errors

def load_repo_review_profile_policy(target_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    policy_path = target_root / REVIEW_ENGINE_POLICY_RELATIVE
    if not policy_path.exists():
        return None, []
    try:
        payload = load_json_file(policy_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, [f"{REVIEW_ENGINE_POLICY_RELATIVE}: invalid JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{REVIEW_ENGINE_POLICY_RELATIVE}: policy must be a JSON object"]
    errors: list[str] = []
    if payload.get("schema_version") != REVIEW_ENGINE_POLICY_SCHEMA:
        errors.append(f"{REVIEW_ENGINE_POLICY_RELATIVE}: schema_version must be `{REVIEW_ENGINE_POLICY_SCHEMA}`")
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        errors.append(f"{REVIEW_ENGINE_POLICY_RELATIVE}: profiles must be an object")
    else:
        for profile_id, profile in profiles.items():
            if profile_id not in REVIEW_ENGINE_PROFILE_IDS:
                errors.append(f"{REVIEW_ENGINE_POLICY_RELATIVE}: unknown profile `{profile_id}`")
                continue
            if not isinstance(profile, dict):
                errors.append(f"{REVIEW_ENGINE_POLICY_RELATIVE}: profile `{profile_id}` must be an object")
                continue
            candidate = {
                **REVIEW_ENGINE_PROFILES[profile_id],
                **profile,
                "profile_id": profile_id,
            }
            errors.extend(validate_review_profile_fields(candidate, context=f"{REVIEW_ENGINE_POLICY_RELATIVE} profile `{profile_id}`"))
    return (None if errors else payload), errors

def repo_policy_allows_local_codex_config_in_ci(policy: dict[str, Any] | None) -> bool:
    if not isinstance(policy, dict):
        return False
    if policy.get("allow_local_codex_config_in_ci") is True:
        return True
    local_config = policy.get("local_codex_config")
    return isinstance(local_config, dict) and local_config.get("allow_ci") is True

def apply_repo_review_profile_policy(
    base_profile: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    profiles = policy.get("profiles") if isinstance(policy.get("profiles"), dict) else {}
    profile_id = str(base_profile["profile_id"])
    policy_profile = profiles.get(profile_id)
    if not isinstance(policy_profile, dict):
        return base_profile, None
    selected = {
        **base_profile,
        **policy_profile,
        "profile_id": profile_id,
    }
    source = {
        "kind": "repo-owned-policy",
        "locator": REVIEW_ENGINE_POLICY_RELATIVE,
        "profile_id": profile_id,
    }
    return selected, source

def local_codex_config_path() -> Path:
    codex_home = non_empty_str(os.environ.get("CODEX_HOME"))
    if codex_home:
        return Path(codex_home).expanduser() / "config.toml"
    return Path.home() / ".codex" / "config.toml"

def load_local_codex_config_profile(base_profile: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    path = local_codex_config_path()
    if not path.exists():
        return None, None, [f"local Codex config opt-in points to a missing file: {path}"]
    if tomllib is None:
        return None, None, ["local Codex config opt-in requires Python tomllib support"]
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:  # type: ignore[union-attr]
        return None, None, [f"local Codex config opt-in could not read {path}: {exc}"]
    model = non_empty_str(payload.get("model")) if isinstance(payload, dict) else None
    reasoning = (
        non_empty_str(payload.get("model_reasoning_effort"))
        or non_empty_str(payload.get("reasoning_effort"))
        if isinstance(payload, dict)
        else None
    )
    selected = dict(base_profile)
    if model:
        selected["model"] = model
    if reasoning:
        selected["reasoning_effort"] = reasoning
    if not model and not reasoning:
        return None, None, [f"local Codex config opt-in found no model or reasoning defaults in {path}"]
    source = {
        "kind": "local-codex-config-opt-in",
        "locator": str(path),
        "fields": sorted(field for field, value in (("model", model), ("reasoning_effort", reasoning)) if value),
    }
    return selected, source, []

def resolve_review_engine_profile(
    context: dict[str, Any],
    review_kind: str,
    *,
    adapter: str = DEFAULT_REVIEW_ADAPTER,
    requested_profile: str | None = None,
    requested_model: str | None = None,
    requested_reasoning: str | None = None,
    override_reason: str | None = None,
    use_local_codex_defaults: bool = False,
) -> tuple[dict[str, Any] | None, list[str]]:
    if adapter not in AUTHORITATIVE_REVIEW_ADAPTERS:
        return None, [f"unsupported authoritative review adapter: {adapter}"]
    selected_profile, selection_reason = review_engine_profile_selection(context, review_kind)
    if requested_profile:
        if requested_profile not in REVIEW_ENGINE_PROFILES:
            return None, [f"unknown review engine profile: {requested_profile}"]
        selected_profile = requested_profile
        selection_reason = f"profile override requested `{requested_profile}`"
    base_profile = dict(REVIEW_ENGINE_PROFILES[selected_profile])
    base_profile["selection_reason"] = selection_reason
    previous_profile = dict(base_profile)
    profile_source = {"kind": "loom-built-in", "locator": "src/skills/shared/scripts/loom_flow.py"}
    policy, policy_errors = load_repo_review_profile_policy(context["target_root"])
    if policy_errors:
        return None, policy_errors
    explicit_cli_override = any(value for value in (requested_profile, requested_model, requested_reasoning))
    override_requested = explicit_cli_override or use_local_codex_defaults
    reason = override_reason.strip() if isinstance(override_reason, str) else ""
    if override_requested and not reason:
        return None, ["review engine profile override requires --engine-override-reason"]
    if not explicit_cli_override and isinstance(policy, dict):
        base_profile, policy_source = apply_repo_review_profile_policy(base_profile, policy)
        if policy_source is not None:
            profile_source = policy_source
    if not explicit_cli_override and profile_source["kind"] == "loom-built-in" and use_local_codex_defaults:
        ci_env_present = truthy_env("CI") or truthy_env("CODEX_CI") or truthy_env("GITHUB_ACTIONS")
        headless_or_gate = adapter == DEFAULT_REVIEW_ADAPTER or ci_env_present
        if headless_or_gate and not repo_policy_allows_local_codex_config_in_ci(policy):
            return None, ["local Codex config opt-in is disabled for CI/headless/merge gate without repo policy allow_local_codex_config_in_ci"]
        local_profile, local_source, local_errors = load_local_codex_config_profile(base_profile)
        if local_errors:
            return None, local_errors
        assert local_profile is not None
        assert local_source is not None
        base_profile = local_profile
        profile_source = local_source
    if requested_model:
        base_profile["model"] = requested_model.strip()
    if requested_reasoning:
        base_profile["reasoning_effort"] = requested_reasoning
    if explicit_cli_override:
        profile_source = {"kind": "explicit-cli-override", "locator": "review run CLI flags"}
    field_errors = validate_review_profile_fields(base_profile, context="review engine profile")
    if field_errors:
        return None, field_errors
    resolved = {
        "schema_version": REVIEW_ENGINE_PROFILE_SCHEMA,
        "profile_id": base_profile["profile_id"],
        "adapter": adapter,
        "engine": CODEX_APP_REVIEW_ENGINE if adapter == CODEX_APP_REVIEW_ADAPTER else DEFAULT_REVIEW_ENGINE,
        "model": base_profile["model"],
        "reasoning_effort": base_profile["reasoning_effort"],
        "timeout_seconds": int(base_profile["timeout_seconds"]) if base_profile["timeout_seconds"] is not None else None,
        "context_policy": base_profile["context_policy"],
        "selection_reason": base_profile["selection_reason"],
        "override_reason": reason or None,
        "profile_source": profile_source,
    }
    if explicit_cli_override or profile_source["kind"] == "local-codex-config-opt-in":
        resolved["override"] = {
            "previous_profile": review_profile_summary(previous_profile),
            "selected_profile": review_profile_summary(resolved),
            "reason": reason,
            "source": profile_source,
        }
    return resolved, []

def review_focus_paths(context: dict[str, Any]) -> list[str]:
    result = run_git(context["target_root"], ["diff", "--name-only", "--no-renames", "HEAD", "--"])
    if result is not None and result.returncode == 0:
        tracked_paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if tracked_paths:
            return tracked_paths
    scope_paths = declared_scope_paths(context["scope"])
    if scope_paths:
        return scope_paths
    artifact_paths = [
        artifact.strip()
        for artifact in context.get("associated_artifacts", [])
        if isinstance(artifact, str) and artifact.strip()
    ]
    if artifact_paths:
        return artifact_paths
    return [relative_to_root(context["workspace_path"], context["target_root"])]

def review_engine_schema_path() -> Path:
    return shared_asset(str(FLOW_ENTRYPOINT), "review/loom-review-result-schema.json")

def normalize_engine_review_result(payload: Any, *, relative: str) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(payload, dict):
        return None, [f"engine result `{relative}` must be a JSON object"]

    decision = payload.get("decision")
    summary = payload.get("summary")
    findings_payload = payload.get("findings")
    errors: list[str] = []
    if decision not in REVIEW_DECISIONS:
        errors.append(f"engine result `{relative}` decision must be one of {', '.join(sorted(REVIEW_DECISIONS))}")
    if not isinstance(summary, str) or not summary.strip():
        errors.append(f"engine result `{relative}` must include non-empty `summary`")
    findings, finding_errors = normalize_review_findings(findings_payload, relative=relative)
    errors.extend(finding_errors)
    if errors:
        return None, errors

    return {
        **payload,
        "decision": decision,
        "summary": summary.strip(),
        "findings": findings,
    }, []

def normalize_codex_app_review_text(raw_text: str, *, relative: str) -> tuple[dict[str, Any] | None, list[str]]:
    text = raw_text.strip()
    if not text:
        return None, [f"Codex App review raw output `{relative}` is empty"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        normalized, errors = normalize_engine_review_result(parsed, relative=relative)
        if normalized is not None and not errors:
            return normalized, []

    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    summary = first_line[:240] if first_line else "Codex App review returned raw text."
    return {
        "decision": "fallback",
        "summary": "Codex App review raw output was captured as shadow evidence and normalized for comparison only.",
        "findings": [
            {
                "id": "codex-app-review-raw-output",
                "summary": summary,
                "severity": "warn",
                "rebuttal": None,
                "disposition": {
                    "status": "deferred",
                    "summary": "Shadow-only finding; formal disposition must still be authored through the single review record.",
                },
                "details": text[:4000],
            }
        ],
    }, []

def normalize_authoritative_codex_app_review_text(raw_text: str, *, relative: str) -> tuple[dict[str, Any] | None, list[str]]:
    text = raw_text.strip()
    if not text:
        return None, [f"Codex App authoritative review output `{relative}` is empty"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"Codex App authoritative review output `{relative}` must be normalized JSON: {exc}"]
    normalized, errors = normalize_engine_review_result(parsed, relative=relative)
    if errors or normalized is None:
        return None, errors
    return normalized, []

def codex_app_endpoint_socket_path(app_server: str | None) -> Path | None:
    endpoint = non_empty_str(app_server)
    if endpoint is None:
        return None
    if endpoint == "stdio://":
        return None
    if endpoint.startswith("unix://"):
        path_text = endpoint.removeprefix("unix://")
    elif endpoint.startswith("/"):
        path_text = endpoint
    else:
        return None
    if not path_text:
        return None
    return Path(path_text).expanduser()

def codex_app_endpoint_is_stdio(app_server: str | None) -> bool:
    return non_empty_str(app_server) == "stdio://"

def codex_app_review_requests_new_thread(thread_id: str | None) -> bool:
    value = non_empty_str(thread_id)
    return value.lower() in CODEX_APP_REVIEW_NEW_THREAD_IDS if value else False

def codex_app_endpoint_is_live_capable(app_server: str | None) -> bool:
    if codex_app_endpoint_is_stdio(app_server):
        return True
    socket_path = codex_app_endpoint_socket_path(app_server)
    return socket_path is not None and socket_path.exists()

def default_codex_app_control_socket() -> Path | None:
    candidates: list[Path] = []
    home = Path.home()
    candidates.append(home / ".codex/app-server-control/app-server-control.sock")
    try:
        uid = os.getuid()
    except AttributeError:
        uid = None
    if uid is not None:
        candidates.append(Path(tempfile.gettempdir()) / "codex-ipc" / f"ipc-{uid}.sock")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

def discover_codex_app_endpoint() -> tuple[str | None, dict[str, Any]]:
    socket_path = default_codex_app_control_socket()
    if socket_path is None:
        return None, {
            "source": "default-control-socket",
            "result": "missing",
            "searched": [
                str(Path.home() / ".codex/app-server-control/app-server-control.sock"),
                str(Path(tempfile.gettempdir()) / "codex-ipc" / f"ipc-{os.getuid()}.sock")
                if hasattr(os, "getuid")
                else None,
            ],
        }
    return f"unix://{socket_path}", {
        "source": "default-control-socket",
        "result": "found",
        "locator": str(socket_path),
    }

def load_codex_session_meta(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "session_meta":
                    continue
                payload = entry.get("payload")
                return payload if isinstance(payload, dict) else None
    except OSError:
        return None
    return None

def codex_session_file_for_id(session_id: str, *, updated_at: str | None = None) -> Path | None:
    sessions_root = Path.home() / ".codex/sessions"
    if not sessions_root.exists():
        return None
    pattern = f"rollout-*{session_id}.jsonl"
    search_roots: list[Path] = []
    timestamp = non_empty_str(updated_at)
    if timestamp:
        date_match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", timestamp)
        if date_match:
            year, month, day = date_match.groups()
            dated_root = sessions_root / year / month / day
            if dated_root.exists():
                search_roots.append(dated_root)
    if not search_roots:
        search_roots.append(sessions_root)
    try:
        matches: list[Path] = []
        for search_root in search_roots:
            matches.extend(search_root.rglob(pattern))
        matches = sorted(matches, key=lambda path: path.stat().st_mtime, reverse=True)
    except OSError:
        return None
    return matches[0] if matches else None

def discover_codex_app_session_meta(target_root: Path) -> tuple[dict[str, str | None], dict[str, Any]]:
    session_file_text = non_empty_str(os.environ.get(CODEX_APP_REVIEW_SESSION_FILE_ENV))
    session_id = non_empty_str(os.environ.get(CODEX_SESSION_ID_ENV)) or non_empty_str(os.environ.get(CODEX_THREAD_ID_ENV))
    candidates: list[Path] = []
    if session_file_text:
        candidates.append(Path(session_file_text).expanduser())
    if session_id:
        session_path = codex_session_file_for_id(session_id)
        if session_path is not None:
            candidates.append(session_path)

    index_path = Path.home() / ".codex/session_index.jsonl"
    if not candidates and index_path.exists():
        try:
            lines = index_path.read_text(encoding="utf-8").splitlines()[-20:]
        except OSError:
            lines = []
        for line in reversed(lines):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            indexed_id = non_empty_str(entry.get("id") if isinstance(entry, dict) else None)
            if not indexed_id:
                continue
            updated_at = non_empty_str(entry.get("updated_at")) if isinstance(entry, dict) else None
            session_path = codex_session_file_for_id(indexed_id, updated_at=updated_at)
            if session_path is not None:
                candidates.append(session_path)

    seen: set[Path] = set()
    inspected: list[str] = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        if resolved in seen:
            continue
        seen.add(resolved)
        inspected.append(str(resolved))
        meta = load_codex_session_meta(resolved)
        if not isinstance(meta, dict):
            continue
        cwd = non_empty_str(meta.get("cwd"))
        thread_id = non_empty_str(meta.get("id"))
        originator = non_empty_str(meta.get("originator"))
        if not cwd or not thread_id:
            continue
        try:
            cwd_path = Path(cwd).expanduser().resolve()
        except OSError:
            continue
        if cwd_path != target_root:
            continue
        return (
            {"thread_id": thread_id, "thread_cwd": str(cwd_path)},
            {
                "source": "codex-session-meta",
                "result": "found",
                "session_file": str(resolved),
                "originator": originator,
            },
        )
    return (
        {"thread_id": None, "thread_cwd": None},
        {
            "source": "codex-session-meta",
            "result": "missing",
            "inspected": inspected[:10],
            "target_root": str(target_root),
        },
    )

def codex_app_missing_host_proof(bindings: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if not non_empty_str(bindings.get("app_server")):
        missing.append("app-server endpoint locator")
    if not non_empty_str(bindings.get("thread_id")):
        missing.append("thread id")
    if not non_empty_str(bindings.get("thread_cwd")):
        missing.append("thread cwd proof")
    return missing

def codex_app_review_bindings_from_args_env(args: argparse.Namespace, target_root: Path) -> dict[str, Any]:
    proof_sources: dict[str, str] = {}
    discovery: dict[str, Any] = {}

    app_server = non_empty_str(args.codex_app_review_app_server)
    if app_server:
        proof_sources["app_server"] = "cli"
    if not app_server:
        app_server = non_empty_str(os.environ.get(CODEX_APP_REVIEW_ENDPOINT_ENV))
        if app_server:
            proof_sources["app_server"] = CODEX_APP_REVIEW_ENDPOINT_ENV
    if not app_server:
        app_server, endpoint_discovery = discover_codex_app_endpoint()
        discovery["app_server"] = endpoint_discovery
        if app_server:
            proof_sources["app_server"] = "default-control-socket"

    thread_id = non_empty_str(args.codex_app_review_thread_id)
    if thread_id:
        proof_sources["thread_id"] = "cli"
    if not thread_id:
        thread_id = non_empty_str(os.environ.get(CODEX_APP_REVIEW_THREAD_ID_ENV))
        if thread_id:
            proof_sources["thread_id"] = CODEX_APP_REVIEW_THREAD_ID_ENV
    if not thread_id and app_server:
        thread_id = non_empty_str(os.environ.get(CODEX_THREAD_ID_ENV)) or non_empty_str(os.environ.get(CODEX_SESSION_ID_ENV))
        if thread_id:
            proof_sources["thread_id"] = f"{CODEX_THREAD_ID_ENV}/{CODEX_SESSION_ID_ENV}"

    thread_cwd = non_empty_str(args.codex_app_review_cwd)
    if thread_cwd:
        proof_sources["thread_cwd"] = "cli"
    if not thread_cwd:
        thread_cwd = non_empty_str(os.environ.get(CODEX_APP_REVIEW_CWD_ENV))
        if thread_cwd:
            proof_sources["thread_cwd"] = CODEX_APP_REVIEW_CWD_ENV

    if (not thread_id or not thread_cwd) and app_server:
        session_bindings, session_discovery = discover_codex_app_session_meta(target_root)
        discovery["session_meta"] = session_discovery
        if not thread_id and session_bindings.get("thread_id"):
            thread_id = session_bindings["thread_id"]
            proof_sources["thread_id"] = "codex-session-meta"
        if not thread_cwd and session_bindings.get("thread_cwd"):
            thread_cwd = session_bindings["thread_cwd"]
            proof_sources["thread_cwd"] = "codex-session-meta"

    raw_file = non_empty_str(args.codex_app_review_raw_file)
    if raw_file:
        proof_sources["raw_file"] = "cli"
    missing_host_proof = codex_app_missing_host_proof(
        {"app_server": app_server, "thread_id": thread_id, "thread_cwd": thread_cwd}
    )
    return {
        "app_server": app_server,
        "thread_id": thread_id,
        "thread_cwd": thread_cwd,
        "raw_file": raw_file,
        "proof_sources": proof_sources,
        "host_discovery": discovery,
        "missing_host_proof": missing_host_proof,
    }

def codex_app_binding_summary(
    target_root: Path,
    *,
    app_server: str | None,
    thread_id: str | None,
    thread_cwd: str | None,
    reviewed_head: str,
    raw_file: str | None,
) -> dict[str, Any]:
    cwd_match: bool | None = None
    cwd_summary: str | None = thread_cwd
    if non_empty_str(thread_cwd):
        try:
            cwd_path = Path(str(thread_cwd)).expanduser().resolve()
        except OSError:
            cwd_match = False
        else:
            cwd_match = cwd_path == target_root
            cwd_summary = str(cwd_path)
    raw_source: str | None = None
    if non_empty_str(raw_file):
        raw_path, raw_errors = resolve_repo_relative_path(target_root, str(raw_file), label="Codex App authoritative review raw file")
        if raw_path is not None and not raw_errors:
            raw_source = artifact_locator_for_path(raw_path, target_root)
        else:
            raw_source = str(raw_file)
    return {
        "app_server": app_server,
        "thread_id": thread_id,
        "thread_cwd": cwd_summary,
        "thread_cwd_matches_target_root": cwd_match,
        "target_root": str(target_root),
        "reviewed_head": reviewed_head,
        "raw_source": raw_source,
        "live_endpoint_capable": codex_app_endpoint_is_live_capable(app_server),
    }

def codex_app_thread_cwd_matches_target(target_root: Path, thread_cwd: str | None) -> bool:
    if not non_empty_str(thread_cwd):
        return False
    try:
        return Path(str(thread_cwd)).expanduser().resolve() == target_root
    except OSError:
        return False

def select_review_adapter(
    args: argparse.Namespace,
    target_root: Path,
    *,
    reviewed_head: str,
) -> dict[str, Any]:
    bindings = codex_app_review_bindings_from_args_env(args, target_root)
    binding_values = {
        "app_server": bindings.get("app_server"),
        "thread_id": bindings.get("thread_id"),
        "thread_cwd": bindings.get("thread_cwd"),
        "raw_file": bindings.get("raw_file"),
    }
    explicit_adapter = non_empty_str(args.engine_adapter)
    if explicit_adapter:
        return {
            "adapter": explicit_adapter,
            "selection_source": "explicit-cli",
            "fallback_reason": None,
            **bindings,
            "binding_summary": codex_app_binding_summary(target_root, reviewed_head=reviewed_head, **binding_values),
        }

    app_server = bindings["app_server"]
    thread_id = bindings["thread_id"]
    thread_cwd = bindings["thread_cwd"]
    raw_file = bindings["raw_file"]
    missing_host_proof = codex_app_missing_host_proof(bindings)
    ci_env_present = truthy_env("CI") or truthy_env("CODEX_CI")
    if not missing_host_proof:
        if not raw_file and not codex_app_thread_cwd_matches_target(target_root, thread_cwd):
            return {
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "selection_source": "host-proof-fallback",
                "fallback_reason": "thread-cwd-target-mismatch",
                **bindings,
                "ci_env_present": ci_env_present,
                "missing_host_proof": ["thread cwd matching target root"],
                "binding_summary": codex_app_binding_summary(target_root, reviewed_head=reviewed_head, **binding_values),
            }
        if not raw_file and not codex_app_endpoint_is_live_capable(app_server):
            return {
                "adapter": DEFAULT_REVIEW_ADAPTER,
                "selection_source": "host-proof-fallback",
                "fallback_reason": "app-server-unavailable",
                **bindings,
                "ci_env_present": ci_env_present,
                "missing_host_proof": ["live app-server endpoint or raw review file"],
                "binding_summary": codex_app_binding_summary(target_root, reviewed_head=reviewed_head, **binding_values),
            }
        return {
            "adapter": CODEX_APP_REVIEW_ADAPTER,
            "selection_source": "codex-app-host-default",
            "fallback_reason": None,
            **bindings,
            "ci_env_present": ci_env_present,
            "binding_summary": codex_app_binding_summary(target_root, reviewed_head=reviewed_head, **binding_values),
        }

    if ci_env_present:
        return {
            "adapter": DEFAULT_REVIEW_ADAPTER,
            "selection_source": "headless-fallback",
            "fallback_reason": "ci-or-codex-ci",
            **bindings,
            "ci_env_present": True,
            "missing_host_proof": missing_host_proof,
            "binding_summary": codex_app_binding_summary(target_root, reviewed_head=reviewed_head, **binding_values),
        }

    return {
        "adapter": DEFAULT_REVIEW_ADAPTER,
        "selection_source": "host-proof-fallback",
        "fallback_reason": "missing-codex-app-host-proof",
        **bindings,
        "ci_env_present": False,
        "missing_host_proof": missing_host_proof,
        "binding_summary": codex_app_binding_summary(target_root, reviewed_head=reviewed_head, **binding_values),
    }

def review_adapter_selection_metadata(selection: dict[str, Any], *, reviewed_head: str) -> dict[str, Any]:
    return {
        "selected_adapter": selection["adapter"],
        "selection_source": selection.get("selection_source"),
        "fallback_reason": selection.get("fallback_reason"),
        "app_server": selection.get("app_server"),
        "thread_id": selection.get("thread_id"),
        "thread_cwd": selection.get("thread_cwd"),
        "target_root": selection.get("binding_summary", {}).get("target_root")
        if isinstance(selection.get("binding_summary"), dict)
        else None,
        "reviewed_head": reviewed_head,
        "thread_target_binding": selection.get("binding_summary"),
        "proof_sources": selection.get("proof_sources") if isinstance(selection.get("proof_sources"), dict) else {},
        "host_discovery": selection.get("host_discovery") if isinstance(selection.get("host_discovery"), dict) else {},
        "missing_host_proof": selection.get("missing_host_proof")
        if isinstance(selection.get("missing_host_proof"), list)
        else [],
        "ci_env_present": bool(selection.get("ci_env_present")),
    }

def jsonrpc_send_request(stdin: Any, *, request_id: int, method: str, params: dict[str, Any]) -> None:
    stdin.write(json.dumps({"id": request_id, "method": method, "params": params}) + "\n")
    stdin.flush()

def jsonrpc_send_notification(stdin: Any, *, method: str, params: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"method": method}
    if params is not None:
        payload["params"] = params
    stdin.write(json.dumps(payload) + "\n")
    stdin.flush()

def jsonrpc_readline(stdout: Any, *, deadline: float | None, close_error: str, timeout_error: str) -> tuple[str | None, str | None]:
    if deadline is None:
        line = stdout.readline()
        if not line:
            return None, close_error
        return line, None
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return None, timeout_error
    readable, _, _ = select.select([stdout], [], [], remaining)
    if not readable:
        return None, timeout_error
    line = stdout.readline()
    if not line:
        return None, close_error
    return line, None

def jsonrpc_read_response(
    stdout: Any,
    *,
    request_id: int,
    deadline: float | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[str]]:
    notifications: list[dict[str, Any]] = []
    while True:
        line, line_error = jsonrpc_readline(
            stdout,
            deadline=deadline,
            close_error=f"app-server closed before response id {request_id}",
            timeout_error=f"Codex App review timed out before response id {request_id}",
        )
        if line_error:
            return None, notifications, [line_error]
        assert line is not None
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("id") == request_id:
            return payload, notifications, []
        notifications.append(payload)

def jsonrpc_read_until_review_text(
    stdout: Any,
    *,
    turn_id: str | None,
    deadline: float | None,
) -> tuple[str | None, list[dict[str, Any]], list[str]]:
    notifications: list[dict[str, Any]] = []
    while True:
        line, line_error = jsonrpc_readline(
            stdout,
            deadline=deadline,
            close_error="app-server closed before Codex App review completed",
            timeout_error="Codex App review timed out before review text was produced",
        )
        if line_error:
            return None, notifications, [line_error]
        assert line is not None
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        notifications.append(payload)
        review_text = find_exited_review_text(payload)
        if isinstance(review_text, str) and review_text.strip():
            return review_text, notifications, []
        if payload.get("method") == "turn/completed":
            params = payload.get("params")
            if not isinstance(params, dict):
                continue
            if turn_id and params.get("turnId") not in {turn_id, None}:
                continue
            return None, notifications, []

def jsonrpc_read_until_normalized_review(
    stdout: Any,
    *,
    turn_id: str | None,
    deadline: float | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[str]]:
    notifications: list[dict[str, Any]] = []
    while True:
        line, line_error = jsonrpc_readline(
            stdout,
            deadline=deadline,
            close_error="app-server closed before Codex App normalization completed",
            timeout_error="Codex App review timed out before normalized review was produced",
        )
        if line_error:
            return None, notifications, [line_error]
        assert line is not None
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        notifications.append(payload)
        normalized = find_normalized_review_payload(payload)
        if normalized is not None:
            return normalized, notifications, []
        if payload.get("method") == "turn/completed":
            params = payload.get("params")
            if not isinstance(params, dict):
                continue
            if turn_id and params.get("turnId") not in {turn_id, None}:
                continue
            return None, notifications, ["Codex App turn/start did not return a Loom review result"]

def terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        try:
            process.terminate()
        except OSError:
            return
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        try:
            process.kill()
        except OSError:
            return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass

def find_exited_review_text(payload: Any) -> str | None:
    if isinstance(payload, dict):
        if payload.get("type") == "exitedReviewMode" and isinstance(payload.get("review"), str):
            return payload["review"]
        for value in payload.values():
            found = find_exited_review_text(value)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = find_exited_review_text(value)
            if found is not None:
                return found
    return None

def find_normalized_review_payload(payload: Any) -> dict[str, Any] | None:
    normalized, errors = normalize_engine_review_result(payload, relative="app-server turn/start output")
    if normalized is not None and not errors:
        return normalized
    if isinstance(payload, str):
        text = payload.strip()
        if not text or not text.startswith("{"):
            return None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        if parsed is payload:
            return None
        return find_normalized_review_payload(parsed)
    if isinstance(payload, dict):
        for value in payload.values():
            found = find_normalized_review_payload(value)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = find_normalized_review_payload(value)
            if found is not None:
                return found
    return None

def app_server_proxy_command(app_server: str) -> list[str] | None:
    if codex_app_endpoint_is_stdio(app_server):
        return ["codex", "app-server", "--listen", "stdio://"]
    socket_path = codex_app_endpoint_socket_path(app_server)
    if socket_path is None:
        return None
    return ["codex", "app-server", "proxy", "--sock", str(socket_path)]

def find_first_key_value(payload: Any, keys: set[str]) -> str | None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in keys:
                text = non_empty_str(value)
                if text:
                    return text
        for value in payload.values():
            found = find_first_key_value(value, keys)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = find_first_key_value(value, keys)
            if found:
                return found
    return None

def extract_model_reasoning_proof(*payloads: Any) -> dict[str, str]:
    model_keys = {"actual_model", "model", "modelSlug", "model_slug"}
    reasoning_keys = {
        "actual_reasoning",
        "reasoning_effort",
        "model_reasoning_effort",
        "reasoningEffort",
        "reasoning",
    }
    proof: dict[str, str] = {}
    for payload in payloads:
        if "actual_model" not in proof:
            model = find_first_key_value(payload, model_keys)
            if model:
                proof["actual_model"] = model
        if "actual_reasoning" not in proof:
            reasoning = find_first_key_value(payload, reasoning_keys)
            if reasoning:
                proof["actual_reasoning"] = reasoning
        if "actual_model" in proof and "actual_reasoning" in proof:
            break
    return proof

def review_model_proof(
    engine_profile: dict[str, Any],
    *,
    live_metadata: dict[str, Any],
    source_path: Path | None,
) -> dict[str, Any]:
    requested_model = str(engine_profile["model"])
    requested_reasoning = str(engine_profile["reasoning_effort"])
    actual_model = non_empty_str(live_metadata.get("actual_model")) if live_metadata else None
    actual_reasoning = non_empty_str(live_metadata.get("actual_reasoning")) if live_metadata else None
    proof_source = non_empty_str(live_metadata.get("model_proof_source")) if live_metadata else None
    if proof_source is None:
        proof_source = "codex-app-live-response" if source_path is None else "raw-file-unverified"
    if actual_model == requested_model and actual_reasoning == requested_reasoning:
        result = "verified"
        enforcement_mode = "verified"
    elif actual_model or actual_reasoning:
        result = "mismatch"
        enforcement_mode = "fail-closed"
    else:
        result = "unverified"
        enforcement_mode = "unverified"
    return {
        "schema_version": "loom-review-model-proof/v1",
        "requested_model": requested_model,
        "requested_reasoning": requested_reasoning,
        "actual_model": actual_model,
        "actual_reasoning": actual_reasoning,
        "proof_source": proof_source,
        "enforcement_mode": enforcement_mode,
        "result": result,
    }

def review_model_proof_errors(model_proof: dict[str, Any], engine_profile: dict[str, Any]) -> list[str]:
    if model_proof.get("result") == "verified":
        return []
    profile_id = str(engine_profile.get("profile_id") or "")
    if model_proof.get("result") == "mismatch":
        return [
            "Codex App actual model/reasoning proof does not match the resolved review engine profile"
        ]
    if profile_id in {"high-risk", "spec-review", "repeated-blocker"}:
        return [
            f"Codex App actual model/reasoning proof is unverified for `{profile_id}` review profile"
        ]
    return []

def run_codex_app_live_review(
    *,
    app_server: str,
    thread_id: str,
    reviewed_head: str,
    thread_cwd: str,
    prompt_text: str,
    timeout_seconds: int | None,
    requested_model: str,
    requested_reasoning: str,
) -> tuple[str | None, dict[str, Any], list[str]]:
    command = app_server_proxy_command(app_server)
    if command is None:
        return None, {}, [f"unsupported Codex App review endpoint: {app_server}"]
    deadline = time.monotonic() + timeout_seconds if timeout_seconds is not None else None
    try:
        env = os.environ.copy()
        for key in LOOM_RUNTIME_ENV_KEYS:
            env.pop(key, None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            start_new_session=True,
        )
    except OSError as exc:
        return None, {}, [f"Codex App review endpoint is unavailable: {exc}"]
    assert process.stdin is not None
    assert process.stdout is not None
    metadata: dict[str, Any] = {
        "review_target": {"type": "commit", "sha": reviewed_head},
        "timeout_seconds": timeout_seconds,
        "requested_model": requested_model,
        "requested_reasoning": requested_reasoning,
        "model_request_source": "resolved-review-engine-profile",
    }
    try:
        jsonrpc_send_request(process.stdin, request_id=1, method="initialize", params={"clientInfo": {"name": "loom", "version": "stage3"}, "capabilities": {}})
        initialize_response, _, initialize_errors = jsonrpc_read_response(process.stdout, request_id=1, deadline=deadline)
        if initialize_errors:
            return None, metadata, initialize_errors
        if isinstance(initialize_response, dict) and isinstance(initialize_response.get("error"), dict):
            return None, metadata, [f"Codex App initialize failed: {initialize_response['error']}"]
        jsonrpc_send_notification(process.stdin, method="initialized")

        new_thread_requested = codex_app_review_requests_new_thread(thread_id)
        if new_thread_requested:
            jsonrpc_send_request(
                process.stdin,
                request_id=2,
                method="thread/start",
                params={
                    "cwd": thread_cwd,
                    "approvalPolicy": "never",
                    "sandbox": "danger-full-access",
                    "baseInstructions": "Loom Codex App review host proof thread.",
                    "ephemeral": False,
                },
            )
            start_response, _, start_errors = jsonrpc_read_response(process.stdout, request_id=2, deadline=deadline)
            if start_errors:
                return None, metadata, start_errors
            if isinstance(start_response, dict) and isinstance(start_response.get("error"), dict):
                return None, metadata, [f"Codex App thread/start failed: {start_response['error']}"]
            start_result = start_response.get("result") if isinstance(start_response, dict) else None
            thread = start_result.get("thread") if isinstance(start_result, dict) else None
            if not isinstance(thread, dict) or not non_empty_str(thread.get("id")):
                return None, metadata, ["Codex App thread/start did not return a thread id"]
            thread_id = str(thread["id"])
            metadata["started_thread_id"] = thread_id
            metadata["started_thread_cwd"] = thread.get("cwd")
            metadata["started_thread_source"] = thread.get("source")
            metadata["started_thread_cli_version"] = thread.get("cliVersion")
            resumed_cwd = non_empty_str(thread.get("cwd"))
        else:
            jsonrpc_send_request(
                process.stdin,
                request_id=2,
                method="thread/resume",
                params={
                    "threadId": thread_id,
                    "cwd": thread_cwd,
                },
            )
            resume_response, _, resume_errors = jsonrpc_read_response(process.stdout, request_id=2, deadline=deadline)
            if resume_errors:
                return None, metadata, resume_errors
            if isinstance(resume_response, dict) and isinstance(resume_response.get("error"), dict):
                return None, metadata, [f"Codex App thread/resume failed: {resume_response['error']}"]
            resume_result = resume_response.get("result") if isinstance(resume_response, dict) else None
            thread = resume_result.get("thread") if isinstance(resume_result, dict) else None
            if isinstance(thread, dict):
                metadata["resumed_thread_cwd"] = thread.get("cwd")
                metadata["resumed_thread_source"] = thread.get("source")
                metadata["resumed_thread_cli_version"] = thread.get("cliVersion")
            resumed_cwd = non_empty_str(thread.get("cwd")) if isinstance(thread, dict) else None
        if resumed_cwd:
            try:
                resumed_cwd_path = Path(resumed_cwd).expanduser().resolve()
                expected_cwd_path = Path(thread_cwd).expanduser().resolve()
            except OSError as exc:
                return None, metadata, [f"Codex App thread cwd proof could not be resolved: {exc}"]
            if resumed_cwd_path != expected_cwd_path:
                return None, metadata, [
                    f"Codex App thread cwd `{resumed_cwd_path}` does not match expected review cwd `{expected_cwd_path}`"
                ]
        metadata["effective_thread_id"] = thread_id

        if new_thread_requested:
            jsonrpc_send_request(
                process.stdin,
                request_id=3,
                method="turn/start",
                params={
                    "threadId": thread_id,
                    "cwd": thread_cwd,
                    "input": [{"type": "text", "text": prompt_text}],
                    "model": requested_model,
                    "reasoningEffort": requested_reasoning,
                    "outputSchema": load_json_file(review_engine_schema_path()),
                },
            )
            turn_response, turn_notifications, turn_errors = jsonrpc_read_response(process.stdout, request_id=3, deadline=deadline)
            if turn_errors:
                return None, metadata, turn_errors
            if isinstance(turn_response, dict) and isinstance(turn_response.get("error"), dict):
                return None, metadata, [f"Codex App turn/start review failed: {turn_response['error']}"]
            turn_result = turn_response.get("result") if isinstance(turn_response, dict) else None
            review_turn_id: str | None = None
            if isinstance(turn_result, dict):
                turn = turn_result.get("turn")
                if isinstance(turn, dict):
                    review_turn_id = non_empty_str(turn.get("id"))
                    metadata["review_turn_id"] = review_turn_id
            normalized = find_normalized_review_payload(turn_result)
            if normalized is None:
                normalized = find_normalized_review_payload(turn_notifications)
            if normalized is None:
                normalized, normalization_notifications, normalization_wait_errors = jsonrpc_read_until_normalized_review(
                    process.stdout,
                    turn_id=review_turn_id,
                    deadline=deadline,
                )
                turn_notifications.extend(normalization_notifications)
                if normalization_wait_errors:
                    return None, metadata, normalization_wait_errors
            if normalized is None:
                return None, metadata, ["Codex App turn/start review did not return a Loom review result"]
            proof = extract_model_reasoning_proof(turn_response, turn_notifications)
            if proof:
                metadata.update(proof)
                metadata["model_proof_source"] = "turn-start-response"
            metadata["normalization_source"] = "turn-start-output-schema"
            raw_text = json.dumps(normalized, ensure_ascii=False, indent=2)
            return raw_text, {**metadata, "normalized": normalized}, []

        jsonrpc_send_request(
            process.stdin,
            request_id=3,
            method="review/start",
            params={
                "threadId": thread_id,
                "delivery": "inline",
                "target": {"type": "commit", "sha": reviewed_head},
                "model": requested_model,
                "reasoningEffort": requested_reasoning,
            },
        )
        review_response, review_notifications, review_errors = jsonrpc_read_response(process.stdout, request_id=3, deadline=deadline)
        if review_errors:
            return None, metadata, review_errors
        if isinstance(review_response, dict) and isinstance(review_response.get("error"), dict):
            return None, metadata, [f"Codex App review/start failed: {review_response['error']}"]
        result = review_response.get("result") if isinstance(review_response, dict) else None
        review_turn_id: str | None = None
        if isinstance(result, dict):
            metadata["review_thread_id"] = result.get("reviewThreadId")
            turn = result.get("turn")
            if isinstance(turn, dict):
                review_turn_id = non_empty_str(turn.get("id"))
                metadata["review_turn_id"] = review_turn_id
        proof = extract_model_reasoning_proof(review_response, review_notifications)
        if proof:
            metadata.update(proof)
            metadata["model_proof_source"] = "review-start-response"
        review_text = find_exited_review_text(result) or find_exited_review_text(review_notifications)
        if not isinstance(review_text, str) or not review_text.strip():
            review_text, completion_notifications, completion_errors = jsonrpc_read_until_review_text(
                process.stdout,
                turn_id=review_turn_id,
                deadline=deadline,
            )
            review_notifications.extend(completion_notifications)
            if completion_errors:
                return None, metadata, completion_errors
        if not isinstance(review_text, str) or not review_text.strip():
            jsonrpc_send_request(
                process.stdin,
                request_id=4,
                method="thread/read",
                params={
                    "threadId": metadata.get("review_thread_id") or thread_id,
                    "includeTurns": True,
                },
            )
            thread_response, thread_notifications, thread_errors = jsonrpc_read_response(process.stdout, request_id=4, deadline=deadline)
            review_notifications.extend(thread_notifications)
            if thread_errors:
                return None, metadata, thread_errors
            if isinstance(thread_response, dict) and isinstance(thread_response.get("error"), dict):
                return None, metadata, [f"Codex App thread/read failed: {thread_response['error']}"]
            review_text = find_exited_review_text(thread_response)
        if not isinstance(review_text, str) or not review_text.strip():
            return None, metadata, ["Codex App review/start did not return exitedReviewMode.review"]

        parsed_review, parsed_errors = normalize_authoritative_codex_app_review_text(review_text, relative="app-server review/start output")
        if parsed_review is not None and not parsed_errors:
            metadata["normalization_source"] = "review-start-json"
            return review_text, {**metadata, "normalized": parsed_review}, []

        jsonrpc_send_request(
            process.stdin,
            request_id=5,
            method="turn/start",
            params={
                "threadId": metadata.get("review_thread_id") or thread_id,
                "cwd": thread_cwd,
                "input": [
                    {
                        "type": "text",
                        "text": (
                            "Normalize this Codex App review output into the provided JSON schema. "
                            "Return only the structured review result.\n\n"
                            f"{review_text}"
                        ),
                    }
                ],
                "model": requested_model,
                "reasoningEffort": requested_reasoning,
                "outputSchema": load_json_file(review_engine_schema_path()),
            },
        )
        turn_response, turn_notifications, turn_errors = jsonrpc_read_response(process.stdout, request_id=5, deadline=deadline)
        if turn_errors:
            return review_text, metadata, turn_errors
        if isinstance(turn_response, dict) and isinstance(turn_response.get("error"), dict):
            return review_text, metadata, [f"Codex App turn/start normalization failed: {turn_response['error']}"]
        turn_result = turn_response.get("result") if isinstance(turn_response, dict) else None
        normalization_turn_id: str | None = None
        if isinstance(turn_result, dict):
            turn = turn_result.get("turn")
            if isinstance(turn, dict):
                normalization_turn_id = non_empty_str(turn.get("id"))
                metadata["normalization_turn_id"] = normalization_turn_id
        normalized = find_normalized_review_payload(turn_result)
        if normalized is None:
            normalized = find_normalized_review_payload(turn_notifications)
        if normalized is None:
            normalized, normalization_notifications, normalization_wait_errors = jsonrpc_read_until_normalized_review(
                process.stdout,
                turn_id=normalization_turn_id,
                deadline=deadline,
            )
            turn_notifications.extend(normalization_notifications)
            if normalization_wait_errors:
                return review_text, metadata, normalization_wait_errors
        if normalized is None:
            return review_text, metadata, ["Codex App turn/start did not return a Loom review result"]
        proof = extract_model_reasoning_proof(turn_response, turn_notifications)
        if proof:
            metadata.update(proof)
            metadata["model_proof_source"] = "normalization-turn-start-response"
        metadata["normalization_source"] = "turn-start-output-schema"
        return review_text, {**metadata, "normalized": normalized}, []
    finally:
        terminate_process_group(process)

def shadow_adapter_slug(adapter: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "-", adapter).strip("-") or "unknown-adapter"

def compare_review_findings(default_findings: list[dict[str, Any]], shadow_findings: list[dict[str, Any]]) -> dict[str, Any]:
    default_ids = {str(finding.get("id")) for finding in default_findings if isinstance(finding, dict) and finding.get("id")}
    shadow_ids = {str(finding.get("id")) for finding in shadow_findings if isinstance(finding, dict) and finding.get("id")}
    shared = sorted(default_ids & shadow_ids)
    default_only = sorted(default_ids - shadow_ids)
    shadow_only = sorted(shadow_ids - default_ids)
    result = "match" if not default_only and not shadow_only else "difference"
    return {
        "schema_version": "loom-review-shadow-diff/v1",
        "result": result,
        "summary": (
            "Shadow review findings match the default review finding ids."
            if result == "match"
            else "Shadow review findings differ from the default review finding ids."
        ),
        "default_finding_ids": sorted(default_ids),
        "shadow_finding_ids": sorted(shadow_ids),
        "shared_finding_ids": shared,
        "default_only_finding_ids": default_only,
        "shadow_only_finding_ids": shadow_only,
    }

def run_codex_app_review_shadow_adapter(
    context: dict[str, Any],
    *,
    adapter: str | None,
    raw_file: str | None,
    default_engine_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not adapter:
        return None
    reviewed_head = git_head_sha(context["target_root"]) or "unknown-head"
    runtime_root = review_runtime_root(context, reviewed_head)
    shadow_root = runtime_root / "shadow" / shadow_adapter_slug(adapter)
    raw_path = shadow_root / "raw-review.txt"
    findings_path = shadow_root / "normalized-findings.json"
    metadata_path = shadow_root / "metadata.json"
    diff_path = shadow_root / "parity-diff.json"
    evidence = {
        "runtime_root": artifact_locator_for_path(shadow_root, context["target_root"]),
        "raw_review": artifact_locator_for_path(raw_path, context["target_root"]),
        "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
        "metadata": artifact_locator_for_path(metadata_path, context["target_root"]),
        "parity_diff": artifact_locator_for_path(diff_path, context["target_root"]),
    }

    if adapter != CODEX_APP_REVIEW_SHADOW_ADAPTER:
        return {
            "adapter": adapter,
            "result": "unavailable",
            "summary": "Unsupported shadow review adapter.",
            "missing_inputs": [f"unsupported shadow review adapter: {adapter}"],
            "blocking": False,
            "authoritative": False,
            "evidence": evidence,
        }

    if not raw_file:
        metadata = {
            "schema_version": "loom-review-shadow-metadata/v1",
            "adapter": adapter,
            "result": "unavailable",
            "reviewed_head": reviewed_head,
            "summary": "Codex App review shadow adapter requires captured raw review text or a future live app-server runner.",
            "missing_inputs": ["--shadow-review-raw-file"],
            "authoritative": False,
        }
        shadow_root.mkdir(parents=True, exist_ok=True)
        write_json_file(metadata_path, metadata)
        return {
            "adapter": adapter,
            "result": "unavailable",
            "summary": "Codex App review shadow adapter was requested but no raw review evidence was provided.",
            "missing_inputs": ["--shadow-review-raw-file"],
            "blocking": False,
            "authoritative": False,
            "evidence": evidence,
        }

    source_path, source_errors = resolve_repo_relative_path(context["target_root"], raw_file, label="shadow review raw file")
    if source_errors or source_path is None:
        shadow_root.mkdir(parents=True, exist_ok=True)
        write_json_file(
            metadata_path,
            {
                "schema_version": "loom-review-shadow-metadata/v1",
                "adapter": adapter,
                "result": "block",
                "reviewed_head": reviewed_head,
                "missing_inputs": source_errors,
                "authoritative": False,
            },
        )
        return {
            "adapter": adapter,
            "result": "block",
            "summary": "Codex App review shadow adapter refused an unsafe raw review locator.",
            "missing_inputs": source_errors,
            "blocking": False,
            "authoritative": False,
            "evidence": evidence,
        }

    try:
        raw_text = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "adapter": adapter,
            "result": "block",
            "summary": "Codex App review shadow adapter could not read raw review evidence.",
            "missing_inputs": [f"shadow review raw file: {exc.strerror or exc}"],
            "blocking": False,
            "authoritative": False,
            "evidence": evidence,
        }

    shadow_root.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw_text, encoding="utf-8")
    normalized, normalization_errors = normalize_codex_app_review_text(
        raw_text,
        relative=relative_to_root(source_path, context["target_root"]),
    )
    if normalization_errors or normalized is None:
        write_json_file(
            metadata_path,
            {
                "schema_version": "loom-review-shadow-metadata/v1",
                "adapter": adapter,
                "result": "block",
                "reviewed_head": reviewed_head,
                "missing_inputs": normalization_errors,
                "raw_source": relative_to_root(source_path, context["target_root"]),
                "authoritative": False,
            },
        )
        return {
            "adapter": adapter,
            "result": "block",
            "summary": "Codex App review shadow output could not be normalized safely.",
            "missing_inputs": normalization_errors,
            "blocking": False,
            "authoritative": False,
            "evidence": evidence,
        }

    write_json_file(findings_path, {"findings": normalized["findings"]})
    default_findings: list[dict[str, Any]] = []
    review_record_input = default_engine_payload.get("review_record_input")
    if isinstance(review_record_input, dict):
        default_findings_file = review_record_input.get("findings_file")
        if isinstance(default_findings_file, str):
            loaded_findings, _ = load_findings_file(context["target_root"], default_findings_file)
            if isinstance(loaded_findings, list):
                default_findings = loaded_findings
    parity_diff = compare_review_findings(default_findings, normalized["findings"])
    write_json_file(diff_path, parity_diff)
    write_json_file(
        metadata_path,
        {
            "schema_version": "loom-review-shadow-metadata/v1",
            "adapter": adapter,
            "result": "pass",
            "reviewed_head": reviewed_head,
            "raw_source": relative_to_root(source_path, context["target_root"]),
            "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
            "parity_diff": artifact_locator_for_path(diff_path, context["target_root"]),
            "authoritative": False,
            "summary": normalized["summary"],
        },
    )
    return {
        "adapter": adapter,
        "result": "pass",
        "summary": "Codex App review shadow evidence was captured and normalized for comparison only.",
        "missing_inputs": [],
        "blocking": False,
        "authoritative": False,
        "evidence": evidence,
        "decision": normalized["decision"],
        "parity_diff": parity_diff,
    }

def run_codex_app_review_authoritative_adapter(
    context: dict[str, Any],
    build_payload: dict[str, Any],
    review_path: str,
    engine_profile: dict[str, Any],
    *,
    review_kind: str,
    app_server: str | None,
    thread_id: str | None,
    thread_cwd: str | None,
    raw_file: str | None,
    adapter_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reviewed_head = git_head_sha(context["target_root"]) or "unknown-head"
    selection_metadata = review_adapter_selection_metadata(
        adapter_selection
        or {
            "adapter": CODEX_APP_REVIEW_ADAPTER,
            "selection_source": "explicit-cli",
            "fallback_reason": None,
            "app_server": app_server,
            "thread_id": thread_id,
            "thread_cwd": thread_cwd,
            "raw_file": raw_file,
            "binding_summary": codex_app_binding_summary(
                context["target_root"],
                app_server=app_server,
                thread_id=thread_id,
                thread_cwd=thread_cwd,
                reviewed_head=reviewed_head,
                raw_file=raw_file,
            ),
        },
        reviewed_head=reviewed_head,
    )
    runtime_root = review_runtime_root(context, reviewed_head)
    raw_path = runtime_root / "engine-result.json"
    findings_path = runtime_root / "normalized-findings.json"
    metadata_path = runtime_root / "engine-metadata.json"
    context_pack_path = runtime_root / "context-pack.json"
    instructions_path = runtime_root / "prompt.txt"
    context_pack = build_review_context_pack(context, review_path)
    evidence = {
        "runtime_root": artifact_locator_for_path(runtime_root, context["target_root"]),
        "prompt": artifact_locator_for_path(instructions_path, context["target_root"]),
        "raw_result": artifact_locator_for_path(raw_path, context["target_root"]),
        "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
        "metadata": artifact_locator_for_path(metadata_path, context["target_root"]),
        "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
    }
    runtime_root.mkdir(parents=True, exist_ok=True)
    write_json_file(context_pack_path, context_pack)
    write_runtime_text_artifact(
        instructions_path,
        build_default_review_prompt(
            context=context,
            build_payload=build_payload,
            runtime_fields=runtime_evidence_from_report(context["report"])[0],
            review_path=review_path,
            context_pack=context_pack,
        ),
    )

    missing_inputs: list[str] = []
    for label, value in (
        ("--codex-app-review-app-server", app_server),
        ("--codex-app-review-thread-id", thread_id),
        ("--codex-app-review-cwd", thread_cwd),
    ):
        if not isinstance(value, str) or not value.strip():
            missing_inputs.append(label)

    cwd_relative: str | None = None
    if isinstance(thread_cwd, str) and thread_cwd.strip():
        try:
            cwd_path = Path(thread_cwd).expanduser().resolve()
        except OSError as exc:
            missing_inputs.append(f"Codex App review cwd could not be resolved: {exc}")
        else:
            if cwd_path != context["target_root"]:
                missing_inputs.append(
                    f"Codex App review cwd `{cwd_path}` does not match target root `{context['target_root']}`"
                )
            else:
                cwd_relative = relative_to_root(cwd_path, context["target_root"])

    source_path: Path | None = None
    source_relative: str | None = None
    if isinstance(raw_file, str) and raw_file.strip():
        source_path, source_errors = resolve_repo_relative_path(
            context["target_root"],
            raw_file,
            label="Codex App authoritative review raw file",
        )
        missing_inputs.extend(source_errors)
        if source_path is not None:
            source_relative = relative_to_root(source_path, context["target_root"])
    elif not codex_app_endpoint_is_live_capable(app_server):
        missing_inputs.append("--codex-app-review-raw-file or live app-server endpoint")

    if missing_inputs:
        write_json_file(
            metadata_path,
            {
                "schema_version": "loom-review-engine-metadata/v1",
                "engine": CODEX_APP_REVIEW_ENGINE,
                "adapter": CODEX_APP_REVIEW_ADAPTER,
                "profile": engine_profile,
                **selection_metadata,
                "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
                "result": "block",
                "failure_reason": "runtime_conflict",
                "summary": "Codex App authoritative review adapter is missing required live binding proof.",
                "missing_inputs": missing_inputs,
                "reviewed_head": reviewed_head,
                "app_server": app_server,
                "thread_id": thread_id,
                "thread_cwd": cwd_relative or thread_cwd,
            },
        )
        return {
            "result": "block",
            "summary": "Codex App authoritative review adapter failed closed before a formal review record could be authored.",
            "missing_inputs": missing_inputs,
            "fallback_to": None,
            "engine": {
                "engine": CODEX_APP_REVIEW_ENGINE,
                "adapter": CODEX_APP_REVIEW_ADAPTER,
                "profile": engine_profile,
                "result": "block",
                "failure_reason": "runtime_conflict",
                "reviewed_head": reviewed_head,
                "evidence": evidence,
            },
            "engine_metadata": {
                **selection_metadata,
                "app_server": app_server,
                "thread_id": thread_id,
                "thread_cwd": cwd_relative or thread_cwd,
                "raw_source": source_relative,
            },
        }

    live_metadata: dict[str, Any] = {}
    if source_path is not None:
        try:
            raw_text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raw_text = ""
            normalization_errors = [f"Codex App authoritative review raw file: {exc.strerror or exc}"]
            normalized = None
        else:
            normalized, normalization_errors = normalize_authoritative_codex_app_review_text(
                raw_text,
                relative=source_relative or str(raw_file),
            )
    else:
        raw_timeout_seconds = engine_profile.get("timeout_seconds")
        live_timeout_seconds = (
            int(raw_timeout_seconds)
            if raw_timeout_seconds is not None
            else CODEX_APP_REVIEW_LIVE_TIMEOUT_SECONDS
        )
        raw_text, live_metadata, normalization_errors = run_codex_app_live_review(
            app_server=str(app_server),
            thread_id=str(thread_id),
            reviewed_head=reviewed_head,
            thread_cwd=str(thread_cwd),
            prompt_text=instructions_path.read_text(encoding="utf-8"),
            timeout_seconds=live_timeout_seconds,
            requested_model=str(engine_profile["model"]),
            requested_reasoning=str(engine_profile["reasoning_effort"]),
        )
        normalized = live_metadata.get("normalized") if isinstance(live_metadata.get("normalized"), dict) else None
        if raw_text is None:
            raw_text = ""

    model_proof = review_model_proof(
        engine_profile,
        live_metadata=live_metadata,
        source_path=source_path,
    )
    proof_errors = [] if normalization_errors or normalized is None else review_model_proof_errors(model_proof, engine_profile)
    proof_blocked = bool(proof_errors)
    if proof_errors:
        normalization_errors = proof_errors

    if normalization_errors or normalized is None:
        if raw_text:
            raw_path.write_text(raw_text, encoding="utf-8")
        write_json_file(
            metadata_path,
            {
                "schema_version": "loom-review-engine-metadata/v1",
                "engine": CODEX_APP_REVIEW_ENGINE,
                "adapter": CODEX_APP_REVIEW_ADAPTER,
                "profile": engine_profile,
                **selection_metadata,
                "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
                "result": "block",
                "failure_reason": "runtime_conflict" if proof_blocked else "schema_drift",
                "summary": (
                    "Codex App authoritative review actual model proof did not satisfy the resolved profile contract."
                    if proof_blocked
                    else "Codex App authoritative review output did not satisfy the Loom review result schema."
                ),
                "errors": normalization_errors,
                "reviewed_head": reviewed_head,
                "app_server": app_server,
                "thread_id": thread_id,
                "thread_cwd": cwd_relative,
                "raw_source": source_relative,
                "requested_model": model_proof["requested_model"],
                "requested_reasoning": model_proof["requested_reasoning"],
                "actual_model": model_proof["actual_model"],
                "actual_reasoning": model_proof["actual_reasoning"],
                "proof_source": model_proof["proof_source"],
                "enforcement_mode": model_proof["enforcement_mode"],
                "model_proof": model_proof,
                **({"live_review": live_metadata} if live_metadata else {}),
            },
        )
        return {
            "result": "block",
            "summary": "Codex App authoritative review output could not be normalized safely.",
            "missing_inputs": normalization_errors,
            "fallback_to": None,
            "engine": {
                "engine": CODEX_APP_REVIEW_ENGINE,
                "adapter": CODEX_APP_REVIEW_ADAPTER,
                "profile": engine_profile,
                "result": "block",
                "failure_reason": "runtime_conflict" if proof_blocked else "schema_drift",
                "reviewed_head": reviewed_head,
                "evidence": evidence,
            },
            "engine_metadata": {
                **selection_metadata,
                "app_server": app_server,
                "thread_id": thread_id,
                "thread_cwd": cwd_relative,
                "raw_source": source_relative,
                "requested_model": model_proof["requested_model"],
                "requested_reasoning": model_proof["requested_reasoning"],
                "actual_model": model_proof["actual_model"],
                "actual_reasoning": model_proof["actual_reasoning"],
                "proof_source": model_proof["proof_source"],
                "enforcement_mode": model_proof["enforcement_mode"],
                "model_proof": model_proof,
                **({"live_review": live_metadata} if live_metadata else {}),
            },
        }

    raw_path.write_text(raw_text, encoding="utf-8")
    write_json_file(findings_path, {"findings": normalized["findings"]})
    effective_thread_id = (
        non_empty_str(live_metadata.get("effective_thread_id")) if live_metadata else None
    ) or thread_id
    metadata = {
        "schema_version": "loom-review-engine-metadata/v1",
        "engine": CODEX_APP_REVIEW_ENGINE,
        "adapter": CODEX_APP_REVIEW_ADAPTER,
        "profile": engine_profile,
        **selection_metadata,
        "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
        "result": "pass",
        "reviewed_head": reviewed_head,
        "decision": normalized["decision"],
        "summary": normalized["summary"],
        "kind": review_kind,
        "validation_summary": context["latest_validation_summary"],
        "app_server": app_server,
        "thread_id": effective_thread_id,
        "thread_cwd": cwd_relative,
        "raw_source": source_relative,
        "requested_model": model_proof["requested_model"],
        "requested_reasoning": model_proof["requested_reasoning"],
        "actual_model": model_proof["actual_model"],
        "actual_reasoning": model_proof["actual_reasoning"],
        "proof_source": model_proof["proof_source"],
        "enforcement_mode": model_proof["enforcement_mode"],
        "model_proof": model_proof,
        "raw_result": artifact_locator_for_path(raw_path, context["target_root"]),
        "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
        "metadata": artifact_locator_for_path(metadata_path, context["target_root"]),
        "review_thread_id": live_metadata.get("review_thread_id") if live_metadata else (effective_thread_id if source_path is not None else None),
        **({"live_review": {key: value for key, value in live_metadata.items() if key != "normalized"}} if live_metadata else {}),
        "authority_boundary": "normalized review_record_input only; raw Codex App output remains runtime evidence",
    }
    write_json_file(metadata_path, metadata)
    return {
        "result": "pass",
        "summary": "Codex App authoritative review adapter produced a Loom-normalized formal review draft.",
        "missing_inputs": [],
        "fallback_to": None,
        "engine": {
            "engine": CODEX_APP_REVIEW_ENGINE,
            "adapter": CODEX_APP_REVIEW_ADAPTER,
            "profile": engine_profile,
            "result": "pass",
            "failure_reason": None,
            "reviewed_head": reviewed_head,
            "evidence": evidence,
        },
        "engine_metadata": metadata,
        "review_record_input": {
            "decision": normalized["decision"],
            "summary": normalized["summary"],
            "reviewer": CODEX_APP_REVIEW_ADAPTER,
            "kind": review_kind,
            "findings_file": artifact_locator_for_path(findings_path, context["target_root"]),
            "engine_adapter": CODEX_APP_REVIEW_ADAPTER,
            "engine_evidence": artifact_locator_for_path(raw_path, context["target_root"]),
            "engine_profile": engine_profile,
            "engine_model_proof": model_proof,
            "context_pack": artifact_locator_for_path(context_pack_path, context["target_root"]),
            "normalized_findings": artifact_locator_for_path(findings_path, context["target_root"]),
            "budget_risk": context_pack.get("budget_risk"),
        },
    }

def manual_review_payload(
    *,
    context: dict[str, Any],
    findings_file: str | None,
    kind: str,
    review_record_path: str,
) -> dict[str, Any]:
    command = [
        "python3",
        "tools/loom_flow.py",
        "review",
        "record",
        "--target",
        str(context["target_root"]),
        "--item",
        context["item_id"],
        "--decision",
        "<allow|block|fallback>",
        "--kind",
        kind,
        "--summary",
        "<stable review summary>",
        "--reviewer",
        "<reviewer-id>",
    ]
    if findings_file:
        command.extend(["--findings-file", findings_file])
    return {
        "summary": "If the default engine is blocked, complete formal review by writing the same review record manually.",
        "review_record_path": review_record_path,
        "findings_file": findings_file,
        "recommended_kind": kind,
        "command": command,
    }

def review_prompt_change_snapshot(context: dict[str, Any]) -> list[str]:
    root = context["target_root"]
    base_result = run_git(root, ["merge-base", "HEAD", "origin/main"])
    if base_result.returncode != 0:
        return [
            "Change Evidence Snapshot：",
            "- Base: unavailable; `git merge-base HEAD origin/main` failed.",
            f"- Error: {(base_result.stderr.strip() or base_result.stdout.strip() or 'unknown')[:240]}",
            "- Focused Diff Excerpt:",
            "```diff",
            "unavailable: origin/main could not be resolved in this review fixture.",
            "```",
        ]

    base_sha = base_result.stdout.strip()
    head_sha = git_head_sha(root) or "unknown-head"
    focused_diff_args = ["--", *REVIEW_PROMPT_DIFF_PATHS]
    stat_result = run_git(root, ["diff", "--stat", f"{base_sha}..HEAD", *focused_diff_args])
    names_result = run_git(root, ["diff", "--name-only", "--no-renames", f"{base_sha}..HEAD", *focused_diff_args])
    diff_result = run_git(
        root,
        [
            "diff",
            "--no-ext-diff",
            "--unified=12",
            f"{base_sha}..HEAD",
            *focused_diff_args,
        ],
    )

    stat_text = stat_result.stdout.strip() if stat_result.returncode == 0 else f"unavailable: {stat_result.stderr.strip() or stat_result.stdout.strip()}"
    names = [line.strip() for line in names_result.stdout.splitlines() if line.strip()] if names_result.returncode == 0 else []
    name_lines = [f"- {path}" for path in names[:80]]
    if len(names) > 80:
        name_lines.append(f"- ... ({len(names) - 80} more paths omitted)")
    if not name_lines:
        name_lines = ["- not_applicable: no changed paths were detected against origin/main."]

    diff_text = diff_result.stdout if diff_result.returncode == 0 else f"unavailable: {diff_result.stderr.strip() or diff_result.stdout.strip()}"
    diff_text = diff_text.strip()
    if len(diff_text) > REVIEW_PROMPT_DIFF_MAX_CHARS:
        diff_text = (
            diff_text[:REVIEW_PROMPT_DIFF_MAX_CHARS]
            + f"\n\n[diff excerpt truncated at {REVIEW_PROMPT_DIFF_MAX_CHARS} characters]"
        )
    if not diff_text:
        diff_text = "not_applicable: no focused diff was available."

    return [
        "Change Evidence Snapshot：",
        f"- Base: {base_sha}",
        f"- Head: {head_sha}",
        "- Changed Paths:",
        *name_lines,
        "- Diff Stat:",
        "```text",
        stat_text or "not_applicable",
        "```",
        "- Focused Diff Excerpt:",
        "```diff",
        diff_text,
        "```",
    ]

def build_default_review_prompt(
    *,
    context: dict[str, Any],
    build_payload: dict[str, Any],
    runtime_fields: dict[str, dict[str, Any]],
    review_path: str,
    context_pack: dict[str, Any],
) -> str:
    focus_paths = review_focus_paths(context)
    is_spec_review = review_path == default_spec_review_path(context["item_id"])
    spec_path = formal_spec_path(context) if is_spec_review else None
    if spec_path and spec_path not in focus_paths:
        focus_paths = [spec_path, *focus_paths]
    workspace_path = relative_to_root(context["workspace_path"], context["target_root"])
    runtime_lines = [
        f"- {field}: {runtime_fields[field]['value']}"
        for field in RUNTIME_EVIDENCE_FIELDS
    ]
    path_lines = [f"- `{path}`" for path in focus_paths[:20]]
    if len(focus_paths) > 20:
        path_lines.append(f"- ... ({len(focus_paths) - 20} more paths omitted)")
    recent_findings = context_pack.get("recent_findings") if isinstance(context_pack.get("recent_findings"), list) else []
    recent_lines = [
        f"- {entry.get('severity')}: {entry.get('summary')} (disposition={((entry.get('disposition') or {}).get('status') if isinstance(entry.get('disposition'), dict) else None) or 'none'}, source={entry.get('source')})"
        for entry in recent_findings[:10]
        if isinstance(entry, dict)
    ]
    if not recent_lines:
        recent_lines = ["- not_applicable: no prior review findings were available."]
    repeated_signal = context_pack.get("repeated_blocker_signal") if isinstance(context_pack.get("repeated_blocker_signal"), dict) else {}
    budget_risk = context_pack.get("budget_risk") if isinstance(context_pack.get("budget_risk"), dict) else {}
    repeated_candidates = repeated_signal.get("candidates") if isinstance(repeated_signal.get("candidates"), list) else []
    repeated_lines = [
        f"- {candidate.get('repeat_key')}: count={candidate.get('count')}, sources={', '.join(str(source) for source in candidate.get('sources', []))}"
        for candidate in repeated_candidates[:10]
        if isinstance(candidate, dict)
    ]
    if not repeated_lines:
        repeated_lines = ["- absent: no repeated blocker candidate detected."]
    change_snapshot_lines = review_prompt_change_snapshot(context)
    return "\n".join(
        [
            "你是 Loom 默认 formal reviewer。",
            "请基于当前仓库工作树做正式语义审查，并只输出符合 schema 的 JSON 结果。",
            "优先阅读当前事项直接相关的文件与差异，不要做整仓广播式探索。",
            "若宿主工具不可用或 outputSchema 限制工具调用，请使用本 prompt 中的 Change Evidence Snapshot 与 Runtime Evidence 形成结论，不要仅因未运行工具而 fallback。",
            "不要重跑 full `tools/loom_check.py .`、`make check`、merge-ready、PR gate 或其他长耗时全量门禁；这些属于调用方提供的验证摘要与后续 gate 职责。只有当前输入互相矛盾时，才运行局部、低成本、可解释的 focused check。",
            "",
            "Loom 审查边界：",
            "- 你负责 reviewer rubric：判断方向、边界、语义正确性、风险与验证充分性。",
            "- 你不是 merge gate；不要输出 safe_to_merge、guardian verdict 或宿主按钮决策。",
            "- 你的输出只是 review evidence；最终正式真相会被回写到单一 review record。",
            "- 若阻断项成立，decision 设为 `block`；若当前输入不足以形成正式结论，decision 设为 `fallback`。",
            "- 运行 Python 验证命令时必须设置 `PYTHONDONTWRITEBYTECODE=1`；如果验证过程产生 `__pycache__` 或 `.pyc`，先删除这些运行副作用并重跑对应检查，不要把 reviewer 自己产生的缓存污染当作实现缺陷。",
            *(
                [
                    "- 当前任务是 spec review；必须优先判断 formal spec 是否完整、边界是否清晰、接受条件是否足以支撑后续实现 review。",
                    f"- Formal Spec Path: {spec_path}",
                ]
                if spec_path
                else []
            ),
            "",
            "当前事项：",
            f"- Item ID: {context['item_id']}",
            f"- Goal: {context['goal']}",
            f"- Scope: {context['scope']}",
            f"- Execution Path: {context['execution_path']}",
            f"- Workspace Entry: {context['workspace_entry']}",
            f"- Workspace Path: {workspace_path}",
            f"- Review Record Path: {review_path}",
            f"- Latest Validation Summary: {context['latest_validation_summary']}",
            "",
            "Build Checkpoint：",
            f"- Result: {build_payload['result']}",
            f"- Summary: {build_payload['summary']}",
            "",
            "Runtime Evidence Entrypoints：",
            *runtime_lines,
            "",
            "优先审查这些路径：",
            *path_lines,
            "",
            "Recent Review Context Pack：",
            f"- Schema: {context_pack.get('schema_version')}",
            f"- History Available: {context_pack.get('history_available')}",
            (
                "- Budget Risk: "
                f"{budget_risk.get('highest_risk', 'none')} "
                f"(status={budget_risk.get('status', 'not_applicable')}, "
                f"enforcement={budget_risk.get('enforcement', 'advisory')})"
            ),
            f"- Budget Risk Summary: {budget_risk.get('summary', 'not_applicable')}",
            f"- Repeated Blocker Signal: {repeated_signal.get('result', 'absent')} ({repeated_signal.get('enforcement', 'advisory')})",
            "Recent Findings:",
            *recent_lines,
            "Repeated Blocker Candidates:",
            *repeated_lines,
            "- 请将发现分类为 new、unresolved 或 repeated/root-cause candidate；不要在没有证据时把 repeat 自动升级成 hard gate。",
            "- 若既有 review record 的 reviewed_head 落后于当前 HEAD，请只把它当作历史输入；本次 review run 正在生成替代 evidence，不能仅因既有 record stale 而 block，除非存在未解决 finding、验证漂移或当前差异本身未被审查覆盖。",
            "- 本次 review run 的 normalized 输出就是将被写入 `review_record_input` 的候选正式结论；不要要求 `.loom/reviews/<item>.json` 在本次 review run 结束前已经刷新到当前 HEAD。",
            "- 如果当前 prompt 的 Head、Change Evidence Snapshot、Runtime Evidence 和验证摘要足以审查当前差异，请直接对当前 HEAD 给出 allow/block/fallback；只有这些当前输入本身缺失、互相矛盾或无法覆盖当前差异时，才把 current-head evidence gap 作为 blocker。",
            "",
            *change_snapshot_lines,
            "",
            "Findings 写作要求：",
            "- 每条 finding 必须包含 `id`、`summary`、`severity`、`rebuttal`、`disposition`。",
            "- `severity` 只允许 `warn` 或 `block`。",
            "- `disposition.status` 只允许 `accepted`、`rejected`、`deferred`。",
            "- 若没有阻断项但仍有后续动作，可输出 `warn` findings。",
            "",
            "Decision 规则：",
            "- `allow`: 当前事项已通过 formal review。",
            "- `block`: 存在明确阻断项。",
            "- `fallback`: 当前输入不足或需要先回到前序 checkpoint 再继续。",
        ]
    ).rstrip() + "\n"

def runtime_evidence_from_report(report: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    runtime_evidence = report.get("runtime_evidence")
    missing_inputs: list[str] = []
    fields: dict[str, Any] = {}
    if not isinstance(runtime_evidence, dict):
        missing_inputs.append("runtime_evidence is missing from fact-chain report")
        return fields, missing_inputs

    for key in RUNTIME_EVIDENCE_FIELDS:
        entry = runtime_evidence.get(key)
        if not isinstance(entry, dict):
            missing_inputs.append(f"runtime_evidence.{key} is missing")
            continue
        value = entry.get("value")
        status = entry.get("status")
        if not isinstance(value, str) or not value.strip():
            missing_inputs.append(f"runtime_evidence.{key}.value must be a non-empty string")
        if status not in {"present", "not_applicable"}:
            missing_inputs.append(f"runtime_evidence.{key}.status must be `present` or `not_applicable`")
        elif status == "present" and value == "not_applicable":
            missing_inputs.append(f"runtime_evidence.{key} is `present` but uses `not_applicable`")
        elif status == "not_applicable" and value != "not_applicable":
            missing_inputs.append(f"runtime_evidence.{key} is `not_applicable` but value is `{value}`")
        fields[key] = {
            "value": value,
            "status": status,
            "source": entry.get("source"),
        }
    return fields, missing_inputs

def report_provenance(report: dict[str, Any]) -> list[dict[str, Any]]:
    provenance = report.get("provenance")
    return provenance if isinstance(provenance, list) else []

def report_recovery_readiness(report: dict[str, Any]) -> dict[str, Any]:
    readiness = report.get("recovery_readiness")
    if isinstance(readiness, dict):
        return readiness
    return {
        "result": "block",
        "summary": "recovery readiness was not reported by the fact-chain reader.",
        "missing_inputs": ["fact-chain recovery_readiness"],
        "fallback_to": "admission",
        "checks": {},
    }

def report_blocking_failures(report: dict[str, Any]) -> list[dict[str, Any]]:
    failures = report.get("blocking_failures")
    return failures if isinstance(failures, list) else []

def report_blocking_messages(report: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for failure in report_blocking_failures(report):
        if not isinstance(failure, dict):
            continue
        message = failure.get("message") or failure.get("summary") or failure.get("kind")
        if isinstance(message, str) and message and message not in messages:
            messages.append(message)
    readiness = report_recovery_readiness(report)
    if readiness.get("result") == "block":
        for message in readiness.get("missing_inputs", []):
            if isinstance(message, str) and message not in messages:
                messages.append(message)
    return messages

def fact_chain_error_contract(
    errors: list[str],
    *,
    output_relative: str = ".loom/bootstrap/init-result.json",
) -> dict[str, Any]:
    missing_inputs = [f"fact-chain: {message}" for message in errors]
    blocking_failures = [
        {
            "category": "gate_failure",
            "kind": "fact_chain_unreadable",
            "carrier": "init_result",
            "field": "fact_chain",
            "authority": "locator_discovery",
            "message": message,
            "blocking": True,
            "fallback_to": "admission",
            "locator": output_relative,
        }
        for message in missing_inputs
    ]
    return {
        "provenance": [
            {
                "kind": "host_control_mirror",
                "carrier": "init_result",
                "field": "fact_chain",
                "authority": "locator_discovery",
                "freshness": "unreadable",
                "trusted_because": "init-result must be readable before authored truth carriers can be selected.",
                "locator": output_relative,
            }
        ],
        "recovery_readiness": {
            "result": "block",
            "status": "blocked",
            "summary": "recovery is blocked because fact-chain locator discovery failed.",
            "missing_inputs": missing_inputs,
            "fallback_to": "admission",
            "checks": {
                "locator_discovery": "block",
                "authored_work_item": "unknown",
                "authored_recovery_entry": "unknown",
                "derived_status_surface": "unknown",
                "parallel_truth": "unknown",
            },
            "authoritative_carrier": "recovery_entry",
            "authoritative_path": None,
            "parallel_truth_drift": [],
            "blocking_failures": blocking_failures,
        },
        "blocking_failures": blocking_failures,
    }

def state_check_payload(context: dict[str, Any]) -> dict[str, Any]:
    purity = purity_report_from_context(context)
    active_state_failures: list[str] = []
    checkpoint_failures: list[str] = []
    scope_failures: list[str] = []

    current_checkpoint = context["current_checkpoint"]
    if current_checkpoint in TERMINAL_CHECKPOINTS:
        active_state_failures.append(f"current checkpoint is terminal: `{current_checkpoint}`")

    active_diagnostics = purity.get("active_workspace_diagnostics", [])
    active_conflicts = [
        entry
        for entry in active_diagnostics
        if isinstance(entry, dict) and entry.get("blocking")
    ]
    if active_conflicts:
        active_state_failures.append(
            "workspace is shared by multiple active items: "
            + ", ".join(sorted(str(entry.get("item_id") or entry.get("work_item_locator")) for entry in active_conflicts))
        )

    known_checkpoints = {"admission", "build", "merge", "retired"} | TERMINAL_CHECKPOINTS
    if current_checkpoint not in known_checkpoints:
        checkpoint_failures.append(f"unknown checkpoint value: `{context['current_checkpoint_raw']}`")
    if current_checkpoint in {"admission", "build", "merge"}:
        for field_name in ("current_stop", "next_step", "latest_validation_summary", "recovery_boundary", "current_lane"):
            value = str(context[field_name]).strip()
            if not value:
                checkpoint_failures.append(f"checkpoint integrity missing `{field_name}`")

    scope_assessment = purity.get("scope_assessment")
    if isinstance(scope_assessment, dict):
        out_of_scope_changes = scope_assessment.get("out_of_scope_changes")
        if isinstance(out_of_scope_changes, list) and out_of_scope_changes:
            preview = ", ".join(out_of_scope_changes[:5])
            scope_failures.append(f"out-of-scope changes detected: {preview}")

    missing_inputs: list[str] = []
    for collection in (purity["hard_failures"], active_state_failures, checkpoint_failures, scope_failures):
        for message in collection:
            if message not in missing_inputs:
                missing_inputs.append(message)

    result = "pass" if not missing_inputs else "block"
    summary = (
        "active state, checkpoint integrity, and scope signals are consistent."
        if result == "pass"
        else "state-check found active-state conflicts, checkpoint gaps, or scope overflow signals."
    )
    return {
        "command": "state-check",
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": current_checkpoint,
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
        },
        "checks": {
            "active_state_failures": active_state_failures,
            "checkpoint_failures": checkpoint_failures,
            "scope_failures": scope_failures,
            "active_workspace_diagnostics": active_diagnostics,
        },
        "purity": purity,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": "admission" if missing_inputs else None,
    }

def validation_summary_token_status(summary: str, token: str) -> dict[str, Any]:
    present = token in summary
    return {
        "token": token,
        "status": "present" if present else "missing",
        "evidence_locator": "Latest Validation Summary",
    }

def changed_paths_for_readiness(target_root: Path) -> dict[str, Any]:
    head = git_head_sha(target_root)
    base = git_merge_base(target_root, "origin/main", "HEAD")
    changed_paths: list[str] = []
    errors: list[str] = []
    if head and base:
        changed_paths, errors = git_changed_paths(target_root, base, head)
    return {
        "base_ref": "origin/main",
        "base_sha": base,
        "head_sha": head,
        "changed_paths": changed_paths,
        "errors": errors,
    }

def pre_review_required_validation_tokens(changed_paths: list[str]) -> list[str]:
    tokens = list(PRE_REVIEW_REQUIRED_VALIDATION_TOKENS)
    if any(path.startswith(PRE_REVIEW_RUNTIME_PATH_PREFIXES) for path in changed_paths):
        tokens.extend(PRE_REVIEW_RUNTIME_VALIDATION_TOKENS)
    if any(path == prefix or path.startswith(prefix) for path in changed_paths for prefix in PRE_REVIEW_RELEASE_PATH_PREFIXES):
        tokens.extend(PRE_REVIEW_RELEASE_VALIDATION_TOKENS)
    return dedupe_strings(tokens)

def pre_review_failure_taxonomy(missing_inputs: list[str]) -> list[str]:
    categories: set[str] = set()
    for message in missing_inputs:
        lowered = str(message).lower()
        if "dirty worktree" in lowered or "uncommitted" in lowered:
            categories.add("dirty_worktree")
        if "checkout head" in lowered or "pr head" in lowered or "head sha" in lowered:
            categories.add("checkout_head_drift")
        if "validation summary" in lowered or "deterministic" in lowered:
            categories.add("deterministic_validation_missing")
        if "skills_surface" in lowered or "generated skills" in lowered:
            categories.add("generated_skills_surface_unverified")
        if "version_surface" in lowered or "check_npm_package" in lowered or "release surface" in lowered:
            categories.add("release_or_package_surface_unverified")
        if "pr metadata" in lowered:
            categories.add("pr_metadata_preflight_failed")
        if "closeout" in lowered or "reconciliation" in lowered:
            categories.add("closeout_preview_gap")
        if "model proof" in lowered or "review engine profile" in lowered:
            categories.add("review_model_proof_unavailable")
    return sorted(categories)

def pre_review_readiness_cost_guard_payload(
    context: dict[str, Any],
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    pr_number: int | None,
    branch_name: str | None,
    pr_payload_file: str | None,
    pr_metadata_preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    advisory_inputs: list[str] = []
    current_head = git_head_sha(target_root)
    current_branch = git_branch(target_root)
    checkpoint_requires_review_readiness = checkpoint_rank(context["current_checkpoint"]) >= checkpoint_rank("build")
    pr_intent = bool(pr_number or branch_name or pr_payload_file)
    enforce = checkpoint_requires_review_readiness or pr_intent

    detected_owner, detected_repo = detect_github_repo(target_root)
    if pr_intent:
        pr_payload, effective_pr, pr_errors, inferences = load_pr_payload_for_gate(
            target_root=target_root,
            owner=owner or detected_owner,
            repo_name=repo_name or detected_repo,
            pr_number=pr_number,
            head_sha=None,
            branch_name=branch_name,
            pr_payload_file=pr_payload_file,
        )
    else:
        pr_payload, effective_pr, pr_errors, inferences = None, None, [], []
    if pr_errors and pr_intent:
        missing_inputs.extend(f"pr: {message}" for message in pr_errors)
    elif pr_errors:
        advisory_inputs.extend(f"pr: {message}" for message in pr_errors)

    pr_head = pr_payload.get("headRefOid") if isinstance(pr_payload, dict) else None
    if isinstance(pr_head, str) and current_head and pr_head != current_head:
        missing_inputs.append("checkout head does not match PR head; push_or_refresh_pr_head before review")
    elif enforce and pr_intent and not isinstance(pr_head, str):
        missing_inputs.append("PR head SHA is unavailable before review")

    dirty_entries = git_dirty_entries(target_root)
    if dirty_entries:
        dirty_paths = [entry["path"] for entry in dirty_entries if isinstance(entry, dict) and entry.get("path")]
        dirty_message = "dirty worktree has uncommitted paths before review: " + ", ".join(dirty_paths[:8])
        if enforce:
            missing_inputs.append(dirty_message)
        else:
            advisory_inputs.append(dirty_message)

    changed = changed_paths_for_readiness(target_root)
    changed_paths = changed["changed_paths"] if isinstance(changed.get("changed_paths"), list) else []
    validation_summary = str(context.get("latest_validation_summary") or "")
    required_tokens = pre_review_required_validation_tokens(changed_paths)
    validation_checks = [validation_summary_token_status(validation_summary, token) for token in required_tokens]
    missing_tokens = [check["token"] for check in validation_checks if check.get("status") == "missing"]
    deterministic_checks_are_blocking = enforce and (pr_intent or bool(changed_paths))
    if deterministic_checks_are_blocking and missing_tokens:
        missing_inputs.append(
            "Latest Validation Summary is missing deterministic review-readiness evidence: "
            + ", ".join(missing_tokens)
        )
    elif missing_tokens:
        advisory_inputs.append(
            "Latest Validation Summary has not yet recorded deterministic review-readiness evidence: "
            + ", ".join(missing_tokens)
        )

    metadata_result = pr_metadata_preflight.get("result") if isinstance(pr_metadata_preflight, dict) else "unavailable"
    if metadata_result == "block":
        missing_inputs.extend(str(message) for message in pr_metadata_preflight.get("missing_inputs", []))

    engine_profile, profile_errors = resolve_review_engine_profile(
        context,
        "implementation",
        adapter=DEFAULT_REVIEW_ADAPTER,
    )
    model_proof_contract = {
        "schema_version": "loom-review-model-proof-consumption/v1",
        "source_issue": "#969",
        "status": "profile_resolved" if not profile_errors else "profile_unresolved",
        "resolved_profile": engine_profile,
        "missing_inputs": profile_errors,
        "authority_boundary": "pre-review consumes profile proof but does not own model policy",
    }
    if profile_errors:
        missing_inputs.extend(f"review engine profile: {message}" for message in profile_errors)

    closeout_preview = {
        "schema_version": "loom-closeout-preview/v1",
        "result": "advisory",
        "summary": "closeout preview is limited to early branch/PR/head/readiness signals; closeout remains authoritative later.",
        "dry_run": True,
        "checks": {
            "work_item": context["item_id"],
            "branch": branch_name or current_branch,
            "pr": effective_pr,
            "head_sha": current_head,
            "project_status_authority": "closeout/reconciliation",
        },
        "does_not_replace": ["closeout_gate", "reconciliation_audit", "issue_closeout_comment"],
    }

    result = "block" if missing_inputs else "pass"
    failure_taxonomy = pre_review_failure_taxonomy(missing_inputs)
    if result == "pass" and not enforce:
        summary = "pre-review readiness/cost guard is advisory until a PR binding or build checkpoint is present."
    elif result == "pass":
        summary = "pre-review readiness/cost guard passed; deterministic inputs are stable enough to spend semantic review."
    else:
        summary = "pre-review readiness/cost guard blocked before spending semantic review."
    return {
        "schema_version": "loom-pre-review-readiness-cost-guard/v1",
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "advisory_inputs": advisory_inputs,
        "failure_taxonomy": failure_taxonomy,
        "fallback_to": "push_or_refresh_pr_head" if "checkout_head_drift" in failure_taxonomy else "build" if result == "block" else None,
        "enforcement": {
            "mode": "blocking" if enforce else "advisory",
            "reason": "build checkpoint or PR binding present" if enforce else "no PR binding and current checkpoint is before build",
        },
        "authority_boundary": {
            "role": "review_cost_guard_input",
            "does_not_replace": [
                "work_item",
                "review_record",
                "merge_ready_result",
                "closeout_evidence",
                "docs_source_truth",
            ],
        },
        "head_alignment": {
            "current_head": current_head,
            "current_branch": current_branch,
            "pr": effective_pr,
            "pr_head": pr_head,
            "inferences": inferences,
            "status": (
                "aligned"
                if isinstance(pr_head, str) and current_head == pr_head
                else "drift"
                if isinstance(pr_head, str) and current_head and current_head != pr_head
                else "not_applicable"
            ),
        },
        "dirty_state": {
            "result": "block" if dirty_entries else "pass",
            "entries": dirty_entries,
        },
        "changed_paths": changed,
        "deterministic_checks": {
            "source": "Latest Validation Summary",
            "required_tokens": required_tokens,
            "checks": validation_checks,
            "missing_tokens": missing_tokens,
            "generated_skills_surface_required": "tools/skills_surface.py check" in required_tokens,
            "release_or_package_surface_required": any(token in required_tokens for token in PRE_REVIEW_RELEASE_VALIDATION_TOKENS),
        },
        "pr_metadata_preflight": pr_metadata_preflight,
        "post_review_carrier_policy": {
            "schema_version": "loom-post-review-carrier-policy/v1",
            "allowed_paths_source": "allowed_post_review_carrier_paths(context, review_path)",
            "carrier_only_status": "retained_review_allowed",
            "generated_only_status": "generated_surface_validation_then_retained_review_allowed",
            "semantic_path_drift_status": "review_required",
        },
        "model_profile_proof": model_proof_contract,
        "closeout_preview": closeout_preview,
    }

def handle_review(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    context, errors = load_context_with_retained_idle_fallback(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "review",
                "operation": args.operation,
                "result": "block",
                "summary": "review command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                **fact_chain_error_contract(errors, output_relative=args.output),
            }
        )

    requested_review_file = args.review_file
    if args.operation == "record" and args.kind == "spec_review" and not requested_review_file:
        requested_review_file = default_spec_review_path(context["item_id"])

    review_record, review_path, review_errors = load_review_record(
        target_root,
        context["item_id"],
        requested_review_file or context["review_entry"],
    )
    inferred_spec_review = review_path == default_spec_review_path(context["item_id"])
    if args.operation == "read":
        missing_inputs = list(review_errors)
        if review_record is None and not review_errors:
            missing_inputs.append(f"missing review artifact: {review_path}")
        result = "pass" if not missing_inputs else "block"
        return emit(
            {
                "command": "review",
                "operation": "read",
                "item": {"id": context["item_id"]},
                "result": result,
                "summary": (
                    "review artifact is readable and can be consumed by merge checkpoint."
                    if result == "pass"
                    else "review artifact is missing or invalid."
                ),
                "missing_inputs": missing_inputs,
                "fallback_to": "build" if missing_inputs else None,
                "review": {"path": review_path, "record": review_record},
            }
        )

    if args.operation == "run":
        flow_operation = "spec-review" if inferred_spec_review else "review"
        review_kind = "spec_review" if inferred_spec_review else implementation_review_kind(context)
        current_head = git_head_sha(target_root) or "unknown-head"
        adapter_selection = select_review_adapter(args, target_root, reviewed_head=current_head)
        requested_engine_adapter = str(adapter_selection["adapter"])
        engine_profile, engine_profile_errors = resolve_review_engine_profile(
            context,
            review_kind,
            adapter=requested_engine_adapter,
            requested_profile=args.engine_profile,
            requested_model=args.engine_model,
            requested_reasoning=args.engine_reasoning,
            override_reason=args.engine_override_reason,
            use_local_codex_defaults=bool(args.engine_use_local_codex_defaults),
        )
        if engine_profile_errors or engine_profile is None:
            manual_review = manual_review_payload(
                context=context,
                findings_file=None,
                kind=review_kind,
                review_record_path=review_path,
            )
            adopted_adapter = adopted_review_engine_adapter_payload(
                adapter_selection=adapter_selection,
                engine_profile=None,
                review_kind=review_kind,
                reviewed_head=current_head,
            )
            return emit(
                {
                    "command": "review",
                    "operation": "run",
                    "item": {"id": context["item_id"]},
                    "result": "block",
                    "summary": "default review engine profile could not be resolved safely.",
                    "missing_inputs": engine_profile_errors,
                    "fallback_to": None,
                    "engine": {
                        "engine": CODEX_APP_REVIEW_ENGINE if requested_engine_adapter == CODEX_APP_REVIEW_ADAPTER else DEFAULT_REVIEW_ENGINE,
                        "adapter": requested_engine_adapter,
                        "profile": None,
                        "result": "not_run",
                        "failure_reason": "runtime_conflict",
                        "reviewed_head": current_head,
                        "evidence": None,
                    },
                    "engine_metadata": review_adapter_selection_metadata(adapter_selection, reviewed_head=current_head),
                    "adopted_review_engine_adapter": adopted_adapter,
                    "manual_review": manual_review,
                }
            )
        flow_payload = build_review_flow_payload(
            target_root,
            args.output,
            args.item,
            operation=flow_operation,
            require_review_entry=inferred_spec_review,
        )
        review_surface = flow_payload.get("review") or (flow_payload.get("spec_review") if inferred_spec_review else None)
        if flow_payload["result"] != "pass":
            manual_review = manual_review_payload(
                context=context,
                findings_file=None,
                kind=review_kind,
                review_record_path=review_path,
            )
            adopted_adapter = adopted_review_engine_adapter_payload(
                adapter_selection=adapter_selection,
                engine_profile=engine_profile,
                review_kind=review_kind,
                reviewed_head=current_head,
            )
            return emit(
                {
                    "command": "review",
                    "operation": "run",
                    "item": flow_payload.get("item"),
                    "result": flow_payload["result"],
                    "summary": "default review engine was not started because the Loom review baseline is not ready.",
                    "missing_inputs": flow_payload["missing_inputs"],
                    "fallback_to": flow_payload["fallback_to"],
                    "steps": flow_payload.get("steps", []),
                    "runtime_state": flow_payload.get("runtime_state"),
                    "state_check": flow_payload.get("state_check"),
                    "runtime_evidence": flow_payload.get("runtime_evidence"),
                    "budget_risk": flow_payload.get("budget_risk"),
                    "build_checkpoint": flow_payload.get("build_checkpoint"),
                    "review": review_surface,
                    "spec_review": flow_payload.get("spec_review"),
                    "repo_specific_requirements": flow_payload.get("repo_specific_requirements"),
                    "current_checkpoint": flow_payload.get("current_checkpoint"),
                    "engine": {
                        "engine": CODEX_APP_REVIEW_ENGINE if requested_engine_adapter == CODEX_APP_REVIEW_ADAPTER else DEFAULT_REVIEW_ENGINE,
                        "adapter": requested_engine_adapter,
                        "profile": engine_profile,
                        "result": "not_run",
                        "failure_reason": None,
                        "reviewed_head": current_head,
                        "evidence": None,
                    },
                    "engine_metadata": review_adapter_selection_metadata(adapter_selection, reviewed_head=current_head),
                    "adopted_review_engine_adapter": adopted_adapter,
                    "manual_review": manual_review,
                }
            )

        build_payload = flow_payload["build_checkpoint"]
        if requested_engine_adapter == CODEX_APP_REVIEW_ADAPTER:
            engine_payload = run_codex_app_review_authoritative_adapter(
                context,
                build_payload,
                review_path,
                engine_profile,
                review_kind=review_kind,
                app_server=adapter_selection.get("app_server") if isinstance(adapter_selection.get("app_server"), str) else None,
                thread_id=adapter_selection.get("thread_id") if isinstance(adapter_selection.get("thread_id"), str) else None,
                thread_cwd=adapter_selection.get("thread_cwd") if isinstance(adapter_selection.get("thread_cwd"), str) else None,
                raw_file=adapter_selection.get("raw_file") if isinstance(adapter_selection.get("raw_file"), str) else None,
                adapter_selection=adapter_selection,
            )
        else:
            engine_payload = run_default_review_engine(
                context,
                build_payload,
                review_path,
                engine_profile,
                review_kind=review_kind,
                adapter_selection=adapter_selection,
            )
        shadow_engine_payload = run_codex_app_review_shadow_adapter(
            context,
            adapter=args.shadow_engine_adapter,
            raw_file=args.shadow_review_raw_file,
            default_engine_payload=engine_payload,
        )
        review_record_input = engine_payload.get("review_record_input")
        findings_file = (
            review_record_input.get("findings_file")
            if isinstance(review_record_input, dict)
            else None
        )
        manual_review = manual_review_payload(
            context=context,
            findings_file=findings_file if isinstance(findings_file, str) else None,
            kind=review_kind,
            review_record_path=review_path,
        )
        result = engine_payload["result"]
        adopted_adapter = adopted_review_engine_adapter_payload(
            adapter_selection=adapter_selection,
            engine_profile=engine_profile,
            review_kind=review_kind,
            reviewed_head=current_head,
            engine_payload=engine_payload,
        )
        summary = (
            engine_payload["summary"]
            if result == "pass"
            else f"{requested_engine_adapter} review engine failed closed; record any formal review conclusion through the single review record."
        )
        return emit(
            {
                "command": "review",
                "operation": "run",
                "item": flow_payload.get("item"),
                "result": result,
                "summary": summary,
                "missing_inputs": engine_payload["missing_inputs"],
                "fallback_to": None if result == "block" else engine_payload["fallback_to"],
                "steps": flow_payload.get("steps", []),
                "runtime_state": flow_payload.get("runtime_state"),
                "state_check": flow_payload.get("state_check"),
                "runtime_evidence": flow_payload.get("runtime_evidence"),
                "budget_risk": flow_payload.get("budget_risk"),
                "build_checkpoint": flow_payload.get("build_checkpoint"),
                "review": review_surface,
                "spec_review": flow_payload.get("spec_review"),
                "repo_specific_requirements": flow_payload.get("repo_specific_requirements"),
                "current_checkpoint": flow_payload.get("current_checkpoint"),
                "engine": engine_payload["engine"],
                **({"engine_metadata": engine_payload["engine_metadata"]} if isinstance(engine_payload.get("engine_metadata"), dict) else {}),
                "adopted_review_engine_adapter": adopted_adapter,
                **({"shadow_engine": shadow_engine_payload} if isinstance(shadow_engine_payload, dict) else {}),
                "manual_review": manual_review,
                **({"review_record_input": review_record_input} if isinstance(review_record_input, dict) else {}),
            }
        )

    missing_inputs: list[str] = []
    for field in ("decision", "kind", "summary", "reviewer"):
        value = getattr(args, field.replace("-", "_"), None)
        if not isinstance(value, str) or not value.strip():
            missing_inputs.append(field)
    if args.decision == "fallback" and args.fallback_to is None:
        missing_inputs.append("fallback-to")
    if missing_inputs:
        return emit(
            {
        "command": "review",
            "operation": "record",
                "result": "block",
                "summary": "review record command is missing required authored fields.",
                "missing_inputs": missing_inputs,
                "fallback_to": "build",
            }
        )

    if args.findings_file and (args.blocking_issue or args.follow_up):
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "review record must not mix `--findings-file` with compatibility finding flags.",
                "missing_inputs": ["choose either `--findings-file` or compatibility finding flags"],
                "fallback_to": "build",
            }
        )

    terminal_closeout_review = (
        args.surface == "closeout"
        and context["current_checkpoint"] in TERMINAL_CHECKPOINTS
    )
    if args.surface == "closeout" and not terminal_closeout_review:
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "closeout review record is only allowed for terminal closeout carrier-only review.",
                "missing_inputs": ["closed_out checkpoint"],
                "fallback_to": "closeout",
            }
        )
    if terminal_closeout_review and args.kind not in IMPLEMENTATION_REVIEW_KINDS:
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "closeout carrier-only review must use an implementation review kind without approving product behavior.",
                "missing_inputs": ["general_review or code_review"],
                "fallback_to": "closeout",
            }
        )

    build_payload = (
        {
            "result": "pass",
            "summary": "terminal closeout carrier-only review does not consume build checkpoint as product implementation approval.",
            "missing_inputs": [],
            "fallback_to": None,
        }
        if terminal_closeout_review
        else checkpoint_payload("build", context)
    )
    if args.decision == "allow" and build_payload["result"] != "pass":
        missing = list(build_payload["missing_inputs"])
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "review cannot be recorded as `allow` before build checkpoint passes.",
                "missing_inputs": missing,
                "fallback_to": build_payload["fallback_to"] or "build",
                "build_checkpoint": build_payload,
            }
        )
    suite_validation: dict[str, Any] | None = None
    if args.decision == "allow" and args.kind == "spec_review":
        suite_validation = spec_suite_validation_payload(context)
        if not suite_validation_ready(suite_validation):
            return emit(
                {
                    "command": "review",
                    "operation": "record",
                    "result": "block",
                    "summary": "spec review cannot be recorded as `allow` until suite validation passes.",
                    "missing_inputs": suite_validation_missing_inputs(suite_validation),
                    "fallback_to": suite_validation_fallback_to(suite_validation),
                    "build_checkpoint": build_payload,
                    "suite_validation": suite_validation,
                }
            )
    suite_gate_validation: dict[str, Any] | None = None
    if args.decision == "allow" and args.kind != "spec_review" and not terminal_closeout_review:
        spec_gate = spec_review_gate_payload(context)
        if not spec_review_gate_ready_for_implementation_review(spec_gate):
            return emit(
                {
                    "command": "review",
                    "operation": "record",
                    "result": "block",
                    "summary": "implementation review cannot be recorded as `allow` before spec review passes.",
                    "missing_inputs": list(spec_gate["missing_inputs"]),
                    "fallback_to": spec_gate["fallback_to"] or "build",
                    "build_checkpoint": build_payload,
                    "spec_review": spec_gate,
                }
            )
        suite_gate_validation = suite_gate_payload_for_surface(context, surface="review")
        if suite_gate_validation["result"] not in {"pass", "not_applicable"}:
            return emit(
                {
                    "command": "review",
                    "operation": "record",
                    "result": "block",
                    "summary": "implementation review cannot be recorded as `allow` until suite evidence and carrier validation pass.",
                    "missing_inputs": list(suite_gate_validation["missing_inputs"]),
                    "fallback_to": suite_gate_validation["fallback_to"] or "build",
                    "build_checkpoint": build_payload,
                    "spec_review": spec_gate,
                    "suite_gate_validation": suite_gate_validation,
                }
            )

    findings: list[dict[str, Any]]
    findings_errors: list[str] = []
    if args.findings_file:
        findings, findings_errors = load_findings_file(target_root, args.findings_file)
        if findings is None:
            findings = []
    else:
        findings = compat_findings_from_lists(
            decision=args.decision,
            blocking_issues=[entry.strip() for entry in args.blocking_issue if entry.strip()],
            follow_ups=[entry.strip() for entry in args.follow_up if entry.strip()],
        )
    if findings_errors:
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "review record could not load a valid authoritative findings file.",
                "missing_inputs": findings_errors,
                "fallback_to": "build",
            }
        )

    blocking_issues, follow_ups = compat_lists_from_findings(findings)
    governance_surface = build_governance_surface(target_root)
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
    latest_validation_summary = context["latest_validation_summary"]
    validation_locator = str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])
    review_payload = {
        "schema_version": "loom-review/v1",
        "item_id": context["item_id"],
        "decision": args.decision,
        "kind": args.kind,
        "summary": args.summary,
        "reviewer": args.reviewer,
        "authored_at": utc_now_iso(),
        "reviewed_head": git_head_sha(target_root) or "unknown",
        "reviewed_validation_summary": latest_validation_summary,
        "reviewed_validation_summary_hash": validation_summary_hash(latest_validation_summary),
        "validation_summary_source": "recovery.latest_validation_summary",
        "validation_summary_locator": validation_locator,
        "fallback_to": args.fallback_to,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "follow_ups": follow_ups,
        "consumed_inputs": {
            "work_item": str(context["report"]["fact_chain"]["entry_points"]["work_item"]),
            "recovery_entry": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
            "status_surface": str(context["report"]["fact_chain"]["entry_points"]["status_surface"]),
            "build_checkpoint": build_payload["result"],
            "budget_risk": budget_risk,
            "engine_adapter": args.engine_adapter,
            "engine_evidence": args.engine_evidence,
            "normalized_findings": args.normalized_findings,
        },
    }
    if args.decision == "allow" and args.kind in IMPLEMENTATION_REVIEW_KINDS:
        if terminal_closeout_review:
            review_payload["carrier_only_closeout_review"] = {
                "status": "passed",
                "reason": "Authored closeout review approved only terminal carrier metadata consumption; it does not approve product implementation behavior.",
            }
        else:
            review_payload["semantic_review_disposition"] = {
                "status": "passed",
                "reason": "Authored implementation review approved the current head for merge checkpoint consumption.",
            }
    if isinstance(suite_gate_validation, dict):
        review_payload["consumed_inputs"].update(suite_gate_consumed_inputs(suite_gate_validation))
    if isinstance(suite_validation, dict):
        review_payload["consumed_inputs"].update(suite_validation_consumed_inputs(suite_validation))
    review_abs, review_path_errors = resolve_repo_relative_path(target_root, review_path, label="review artifact path")
    if review_path_errors:
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "review record refused an unsafe review artifact locator.",
                "missing_inputs": review_path_errors,
                "fallback_to": "build",
            }
        )
    assert review_abs is not None
    if terminal_closeout_review:
        allowed_paths = allowed_terminal_closeout_carrier_paths(context, review_path)
        if review_path not in allowed_paths:
            return emit(
                {
                    "command": "review",
                    "operation": "record",
                    "result": "block",
                    "summary": "closeout carrier-only review refused a review artifact outside terminal closeout carrier surfaces.",
                    "missing_inputs": [f"review artifact outside closeout carrier surfaces: {review_path}"],
                    "fallback_to": "closeout",
                    "allowed_paths": sorted(allowed_paths),
                }
            )
    review_abs.parent.mkdir(parents=True, exist_ok=True)
    write_json_file(review_abs, review_payload)

    verified_record, _, verified_errors = load_review_record(target_root, context["item_id"], review_path)
    if verified_errors or verified_record is None:
        return emit(
            {
                "command": "review",
                "operation": "record",
                "result": "block",
                "summary": "review artifact was written but could not be re-read cleanly.",
                "missing_inputs": verified_errors or [f"missing review artifact: {review_path}"],
                "fallback_to": "build",
            }
        )

    return emit(
        {
            "command": "review",
            "operation": "record",
            "item": {"id": context["item_id"]},
            "result": "pass",
            "summary": (
                "formal spec review conclusion was recorded and is ready for spec gate consumption."
                if args.kind == "spec_review"
                else "formal closeout carrier-only review conclusion was recorded; it does not approve product implementation behavior."
                if terminal_closeout_review
                else "formal review conclusion was recorded and is ready for merge checkpoint consumption."
            ),
            "missing_inputs": [],
            "fallback_to": None,
            "review": {"path": review_path, "record": verified_record},
            "budget_risk": budget_risk,
            "build_checkpoint": {
                "result": build_payload["result"],
                "summary": build_payload["summary"],
            },
            **({"suite_gate_validation": suite_gate_validation} if isinstance(suite_gate_validation, dict) else {}),
        }
    )
ENGINE_FAILURE_REASONS = {
    "engine_unavailable",
    "schema_drift",
    "runtime_conflict",
    "repo_diff_detected",
}
