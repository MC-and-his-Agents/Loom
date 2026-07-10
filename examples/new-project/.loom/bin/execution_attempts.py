#!/usr/bin/env python3
"""Execution-attempt evidence ledger without flow orchestration dependencies."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fact_chain_support import load_json_file, resolve_repo_relative_path
from runtime_paths import global_runtime_path, is_global_runtime_locator

sys.dont_write_bytecode = True

EXECUTION_ATTEMPT_SCHEMA = "loom-execution-attempt/v1"
EXECUTION_ATTEMPT_RESULTS = {"pass", "block", "fallback"}
EXECUTION_FAILURE_SCHEMA = "loom-execution-failure/v1"
EXECUTION_FAILURE_STATUSES = {"present", "not_applicable", "stale", "missing", "invalid"}
EXECUTION_FAILURE_CLASSIFICATIONS = {"none", "stall", "timeout", "retry_exhaustion", "unknown"}
RETRY_EVIDENCE_SCHEMA = "loom-retry-evidence/v1"
RETRY_EVIDENCE_STATUSES = {"present", "not_applicable", "stale", "missing", "invalid"}
EXECUTION_ATTEMPT_FAILURE_CATEGORIES = {
    "none", "runtime_state", "fact_chain", "state_check", "runtime_evidence",
    "checkpoint", "review", "repo_specific", "recovery_readiness", "unknown",
}
EXECUTION_ATTEMPT_FORBIDDEN_AUTHORED_FIELDS = {
    "current_stop", "next_step", "blockers", "latest_validation_summary",
    "current_checkpoint", "current_lane", "recovery_boundary", "closing_condition",
}


def _git_value(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip() if result.returncode == 0 else ""
    return value or None


def _git_branch(root: Path) -> str | None:
    return _git_value(root, "rev-parse", "--abbrev-ref", "HEAD")


def _git_head_sha(root: Path) -> str | None:
    return _git_value(root, "rev-parse", "HEAD")


def _relative_to_root(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def _resolve_artifact_write_path(target_root: Path, locator: str, *, label: str) -> tuple[Path | None, list[str]]:
    logical_path, errors = resolve_repo_relative_path(target_root, locator, label=label)
    if errors:
        return None, errors
    assert logical_path is not None
    if not is_global_runtime_locator(locator):
        return logical_path, []
    try:
        return global_runtime_path(target_root, locator), []
    except ValueError as exc:
        return None, [str(exc)]


def _resolve_artifact_read_path(target_root: Path, locator: str, *, label: str) -> tuple[Path | None, list[str]]:
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
    return (runtime_path if runtime_path.exists() or not logical_path.exists() else logical_path), []


def _write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def execution_attempt_directory(target_root: Path, item_id: str) -> Path:
    return _resolve_artifact_read_path(
        target_root,
        f".loom/runtime/attempts/{item_id}",
        label="execution_attempt directory",
    )[0] or (target_root / ".loom/runtime/attempts" / item_id)


def execution_attempt_locator(item_id: str, filename: str = "latest.json") -> str:
    return f".loom/runtime/attempts/{item_id}/{filename}"


def collect_forbidden_execution_attempt_paths(payload: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in EXECUTION_ATTEMPT_FORBIDDEN_AUTHORED_FIELDS:
                found.append(path)
            found.extend(collect_forbidden_execution_attempt_paths(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.extend(collect_forbidden_execution_attempt_paths(value, f"{prefix}[{index}]"))
    return found


def execution_attempt_failure_category(payload: dict[str, Any]) -> str:
    if payload.get("result") == "pass":
        return "none"
    missing_inputs = payload.get("missing_inputs")
    haystack = " ".join(str(item).lower() for item in missing_inputs if isinstance(missing_inputs, list))
    steps = payload.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict) or step.get("result") not in {"block", "fallback"}:
                continue
            name = str(step.get("name") or "")
            if "runtime-state" in name:
                return "runtime_state"
            if "fact-chain" in name:
                return "fact_chain"
            if "state-check" in name:
                return "state_check"
            if "runtime-evidence" in name:
                return "runtime_evidence"
            if "checkpoint" in name:
                return "checkpoint"
            if "review" in name:
                return "review"
    if "runtime state" in haystack:
        return "runtime_state"
    if "fact-chain" in haystack or "fact chain" in haystack:
        return "fact_chain"
    if "runtime_evidence" in haystack or "runtime evidence" in haystack:
        return "runtime_evidence"
    if "checkpoint" in haystack:
        return "checkpoint"
    if "review" in haystack:
        return "review"
    if "repo-specific" in haystack or "companion" in haystack:
        return "repo_specific"
    if "recovery readiness" in haystack:
        return "recovery_readiness"
    return "unknown"


def classify_execution_failure_text(text: str) -> str:
    lowered = text.strip().lower()
    if not lowered:
        return "unknown"
    if "retry_exhaustion" in lowered or "retry exhaustion" in lowered or "retries exhausted" in lowered:
        return "retry_exhaustion"
    if "timed out" in lowered or re.search(r"\btimeout\b", lowered):
        return "timeout"
    if "stall" in lowered or "stalled" in lowered:
        return "stall"
    return "unknown"


def execution_failure_details(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("result") == "pass":
        return {
            "classification": "none",
            "summary": "latest execution attempt completed without an execution failure classification.",
            "fallback_to": None,
        }

    explicit = payload.get("execution_failure")
    if isinstance(explicit, dict):
        classification = explicit.get("classification") or explicit.get("kind")
        summary = explicit.get("summary")
        fallback_to = explicit.get("fallback_to")
        if isinstance(classification, str) and classification in EXECUTION_FAILURE_CLASSIFICATIONS:
            normalized_summary = (
                str(summary).strip()
                if isinstance(summary, str) and str(summary).strip()
                else f"execution failure classified as `{classification}`."
            )
            return {
                "classification": classification,
                "summary": normalized_summary,
                "fallback_to": str(fallback_to) if isinstance(fallback_to, str) and fallback_to.strip() else payload.get("fallback_to"),
            }

    texts: list[str] = []
    summary = payload.get("summary")
    if isinstance(summary, str) and summary.strip():
        texts.append(summary.strip())
    missing_inputs = payload.get("missing_inputs")
    if isinstance(missing_inputs, list):
        texts.extend(str(item).strip() for item in missing_inputs if str(item).strip())
    steps = payload.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict):
                continue
            for field in ("summary", "name"):
                value = step.get(field)
                if isinstance(value, str) and value.strip():
                    texts.append(value.strip())
            step_missing = step.get("missing_inputs")
            if isinstance(step_missing, list):
                texts.extend(str(item).strip() for item in step_missing if str(item).strip())
    engine = payload.get("engine")
    if isinstance(engine, dict):
        failure_reason = engine.get("failure_reason")
        if isinstance(failure_reason, str) and failure_reason.strip():
            texts.append(failure_reason.strip())

    classification = "unknown"
    matched_summary: str | None = None
    for candidate in texts:
        classification = classify_execution_failure_text(candidate)
        if classification != "unknown":
            matched_summary = candidate
            break

    summary_text = next((candidate for candidate in texts if candidate), None)
    return {
        "classification": classification,
        "summary": matched_summary or summary_text or "execution attempt blocked without a classified execution failure.",
        "fallback_to": payload.get("fallback_to"),
    }
def execution_attempt_summary_from_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    evidence = envelope.get("evidence") if isinstance(envelope.get("evidence"), dict) else {}
    failure = envelope.get("failure") if isinstance(envelope.get("failure"), dict) else {}
    return {
        "schema_version": EXECUTION_ATTEMPT_SCHEMA,
        "attempt_id": envelope.get("attempt_id"),
        "item_id": envelope.get("item_id"),
        "command": envelope.get("command"),
        "operation": envelope.get("operation"),
        "result": envelope.get("result"),
        "failure_category": failure.get("category"),
        "execution_classification": failure.get("execution_classification"),
        "execution_summary": failure.get("execution_summary"),
        "fallback_to": failure.get("fallback_to"),
        "evidence": {
            "status": evidence.get("status"),
            "locator": evidence.get("locator"),
            "latest_locator": evidence.get("latest_locator"),
        },
    }


def build_execution_attempt_envelope(
    context: dict[str, Any],
    *,
    command: str,
    operation: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    head_sha = _git_head_sha(context["target_root"]) or "unknown-head"
    created_at = _utc_now_iso()
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "item_id": context["item_id"],
                "command": command,
                "operation": operation,
                "head_sha": head_sha,
                "created_at": created_at,
                "result": payload.get("result"),
            },
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()[:12]
    attempt_id = f"{context['item_id']}-{operation}-{head_sha[:12]}-{fingerprint}".replace("/", "-")
    attempt_locator = execution_attempt_locator(context["item_id"], f"{attempt_id}.json")
    latest_locator = execution_attempt_locator(context["item_id"])
    result = payload.get("result") if payload.get("result") in EXECUTION_ATTEMPT_RESULTS else "block"
    missing_inputs = payload.get("missing_inputs")
    if not isinstance(missing_inputs, list):
        missing_inputs = []
    failure_category = execution_attempt_failure_category(payload)
    if failure_category not in EXECUTION_ATTEMPT_FAILURE_CATEGORIES:
        failure_category = "unknown"
    execution_failure = execution_failure_details(payload)
    steps = payload.get("steps")
    step_summary = []
    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_summary.append(
                {
                    "name": step.get("name"),
                    "result": step.get("result"),
                    "fallback_to": step.get("fallback_to"),
                    "missing_count": len(step.get("missing_inputs", [])) if isinstance(step.get("missing_inputs"), list) else 0,
                }
            )
    return {
        "schema_version": EXECUTION_ATTEMPT_SCHEMA,
        "attempt_id": attempt_id,
        "item_id": context["item_id"],
        "command": command,
        "operation": operation,
        "result": result,
        "created_at": created_at,
        "head_sha": head_sha,
        "branch": _git_branch(context["target_root"]) or "unknown-branch",
        "workspace": {
            "entry": context["workspace_entry"],
            "path": _relative_to_root(context["workspace_path"], context["target_root"]),
        },
        "failure": {
            "category": failure_category,
            "execution_classification": execution_failure["classification"],
            "execution_summary": execution_failure["summary"],
            "missing_inputs": missing_inputs,
            "fallback_to": execution_failure["fallback_to"],
        },
        "steps": step_summary,
        "evidence": {
            "status": "present",
            "locator": attempt_locator,
            "latest_locator": latest_locator,
        },
    }


def persist_execution_attempt(
    context: dict[str, Any],
    *,
    command: str,
    operation: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    envelope = build_execution_attempt_envelope(context, command=command, operation=operation, payload=payload)
    forbidden = collect_forbidden_execution_attempt_paths(envelope)
    if forbidden:
        envelope["evidence"] = {
            "status": "invalid",
            "locator": None,
            "latest_locator": execution_attempt_locator(context["item_id"]),
            "missing_inputs": [f"execution_attempt includes authored progress field `{path}`" for path in forbidden],
        }
        return execution_attempt_summary_from_envelope(envelope)

    evidence = envelope["evidence"]
    try:
        attempt_path, attempt_errors = _resolve_artifact_write_path(
            context["target_root"],
            str(evidence["locator"]),
            label="execution_attempt evidence locator",
        )
        latest_path, latest_errors = _resolve_artifact_write_path(
            context["target_root"],
            str(evidence["latest_locator"]),
            label="execution_attempt latest locator",
        )
        if attempt_errors or latest_errors:
            raise ValueError("; ".join([*attempt_errors, *latest_errors]))
        assert attempt_path is not None
        assert latest_path is not None
        _write_json_file(attempt_path, envelope)
        _write_json_file(latest_path, envelope)
    except Exception as exc:
        envelope["evidence"] = {
            "status": "missing",
            "locator": evidence.get("locator"),
            "latest_locator": evidence.get("latest_locator"),
            "missing_inputs": [f"execution_attempt evidence could not be written: {exc}"],
        }
    return execution_attempt_summary_from_envelope(envelope)


def validate_execution_attempt_envelope(
    payload: Any,
    *,
    target_root: Path,
    expected_item: str,
    expected_head: str | None = None,
) -> tuple[dict[str, Any] | None, list[str], str]:
    if not isinstance(payload, dict):
        return None, ["execution_attempt evidence must be a JSON object"], "invalid"
    errors: list[str] = []
    if payload.get("schema_version") != EXECUTION_ATTEMPT_SCHEMA:
        errors.append(f"execution_attempt schema_version must be `{EXECUTION_ATTEMPT_SCHEMA}`")
    for field in ("attempt_id", "item_id", "command", "operation", "created_at", "head_sha"):
        if not isinstance(payload.get(field), str) or not str(payload.get(field)).strip():
            errors.append(f"execution_attempt `{field}` must be a non-empty string")
    if payload.get("item_id") != expected_item:
        errors.append(f"execution_attempt item_id does not match `{expected_item}`")
    if payload.get("result") not in EXECUTION_ATTEMPT_RESULTS:
        errors.append("execution_attempt result must be pass, block, or fallback")
    workspace = payload.get("workspace")
    if not isinstance(workspace, dict):
        errors.append("execution_attempt workspace must be an object")
    else:
        for field in ("entry", "path"):
            if not isinstance(workspace.get(field), str) or not workspace.get(field):
                errors.append(f"execution_attempt workspace.{field} must be a non-empty string")
    failure = payload.get("failure")
    if not isinstance(failure, dict):
        errors.append("execution_attempt failure must be an object")
    else:
        if failure.get("category") not in EXECUTION_ATTEMPT_FAILURE_CATEGORIES:
            errors.append("execution_attempt failure.category is outside the stable vocabulary")
        if failure.get("execution_classification") not in EXECUTION_FAILURE_CLASSIFICATIONS:
            errors.append("execution_attempt failure.execution_classification is outside the stable vocabulary")
        if not isinstance(failure.get("execution_summary"), str) or not str(failure.get("execution_summary")).strip():
            errors.append("execution_attempt failure.execution_summary must be a non-empty string")
        if not isinstance(failure.get("missing_inputs"), list):
            errors.append("execution_attempt failure.missing_inputs must be a list")
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("execution_attempt evidence must be an object")
    else:
        locator = evidence.get("locator")
        if not isinstance(locator, str) or not locator.strip():
            errors.append("execution_attempt evidence.locator must be a non-empty string")
        elif resolve_repo_relative_path(target_root, locator, label="execution_attempt evidence locator")[1]:
            errors.append("execution_attempt evidence.locator must stay inside the target root")
        if evidence.get("status") not in {"present", "missing", "invalid"}:
            errors.append("execution_attempt evidence.status must be present, missing, or invalid")
    forbidden = collect_forbidden_execution_attempt_paths(payload)
    for path in forbidden:
        errors.append(f"execution_attempt must not include authored progress field `{path}`")
    if errors:
        return payload, errors, "invalid"
    if expected_head and payload.get("head_sha") != expected_head:
        return payload, [], "stale"
    return payload, [], "fresh"


def latest_execution_attempt_payload(target_root: Path, item_id: str) -> dict[str, Any]:
    locator = execution_attempt_locator(item_id)
    path, path_errors = _resolve_artifact_read_path(target_root, locator, label="execution_attempt latest locator")
    if path_errors:
        return {
            "schema_version": EXECUTION_ATTEMPT_SCHEMA,
            "status": "missing",
            "freshness": "missing",
            "summary": "latest execution attempt evidence locator is invalid.",
            "evidence": {"locator": locator, "status": "missing"},
            "missing_inputs": path_errors,
            "attempt": None,
        }
    assert path is not None
    if not path.exists():
        return {
            "schema_version": EXECUTION_ATTEMPT_SCHEMA,
            "status": "missing",
            "freshness": "missing",
            "summary": "latest execution attempt evidence is not present.",
            "evidence": {"locator": locator, "status": "missing"},
            "missing_inputs": [f"missing execution_attempt evidence: {locator}"],
            "attempt": None,
        }
    try:
        raw = load_json_file(path)
    except Exception as exc:
        return {
            "schema_version": EXECUTION_ATTEMPT_SCHEMA,
            "status": "invalid",
            "freshness": "unreadable",
            "summary": "latest execution attempt evidence is unreadable.",
            "evidence": {"locator": locator, "status": "invalid"},
            "missing_inputs": [str(exc)],
            "attempt": None,
        }
    current_head = _git_head_sha(target_root) or "unknown-head"
    envelope, errors, freshness = validate_execution_attempt_envelope(
        raw,
        target_root=target_root,
        expected_item=item_id,
        expected_head=current_head,
    )
    status = "present" if freshness == "fresh" else ("stale" if freshness == "stale" else "invalid")
    summary = (
        "latest execution attempt evidence is fresh for the current item and HEAD."
        if freshness == "fresh"
        else "latest execution attempt evidence exists but is stale for the current HEAD."
        if freshness == "stale"
        else "latest execution attempt evidence is invalid."
    )
    return {
        "schema_version": EXECUTION_ATTEMPT_SCHEMA,
        "status": status,
        "freshness": freshness,
        "summary": summary,
        "evidence": {"locator": locator, "status": "present" if freshness in {"fresh", "stale"} else "invalid"},
        "missing_inputs": errors,
        "attempt": envelope,
    }


def execution_attempt_history_payload(target_root: Path, item_id: str) -> list[dict[str, Any]]:
    directory = execution_attempt_directory(target_root, item_id)
    if not directory.exists():
        return []
    attempts: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        if path.name == "latest.json":
            continue
        try:
            payload = load_json_file(path)
        except Exception:
            continue
        envelope, errors, _ = validate_execution_attempt_envelope(
            payload,
            target_root=target_root,
            expected_item=item_id,
            expected_head=None,
        )
        if errors or envelope is None:
            continue
        attempts.append(envelope)
    attempts.sort(key=lambda entry: (str(entry.get("created_at") or ""), str(entry.get("attempt_id") or "")))
    return attempts


def latest_execution_failure_payload(latest_attempt: dict[str, Any]) -> dict[str, Any]:
    evidence = latest_attempt.get("evidence") if isinstance(latest_attempt, dict) else {}
    locator = evidence.get("locator") if isinstance(evidence, dict) else None
    freshness = latest_attempt.get("freshness") if isinstance(latest_attempt, dict) else None
    status = latest_attempt.get("status") if isinstance(latest_attempt, dict) else None
    provenance = {
        "source_layer": "derived_surface",
        "source_locator": locator,
        "source_binding": "latest_execution_attempt",
        "freshness": freshness if isinstance(freshness, str) else "missing",
        "conflict": "none",
    }
    if status == "missing":
        return {
            "schema_version": EXECUTION_FAILURE_SCHEMA,
            "status": "missing",
            "classification": "unknown",
            "summary": latest_attempt.get("summary") if isinstance(latest_attempt.get("summary"), str) else "latest execution attempt evidence is missing.",
            "fallback_to": None,
            "provenance": provenance,
        }
    if status == "invalid":
        return {
            "schema_version": EXECUTION_FAILURE_SCHEMA,
            "status": "invalid",
            "classification": "unknown",
            "summary": latest_attempt.get("summary") if isinstance(latest_attempt.get("summary"), str) else "latest execution attempt evidence is invalid.",
            "fallback_to": None,
            "provenance": provenance,
        }

    attempt = latest_attempt.get("attempt") if isinstance(latest_attempt, dict) else None
    failure = attempt.get("failure") if isinstance(attempt, dict) else None
    classification = failure.get("execution_classification") if isinstance(failure, dict) else None
    if not isinstance(classification, str) or classification not in EXECUTION_FAILURE_CLASSIFICATIONS:
        classification = "unknown"
    summary = failure.get("execution_summary") if isinstance(failure, dict) else None
    fallback_to = failure.get("fallback_to") if isinstance(failure, dict) else None
    normalized_summary = (
        str(summary).strip()
        if isinstance(summary, str) and str(summary).strip()
        else "latest execution attempt did not record a readable execution failure summary."
    )
    if freshness == "stale":
        return {
            "schema_version": EXECUTION_FAILURE_SCHEMA,
            "status": "stale",
            "classification": classification,
            "summary": "latest execution failure evidence exists but is stale for the current HEAD.",
            "fallback_to": str(fallback_to) if isinstance(fallback_to, str) and fallback_to.strip() else None,
            "provenance": provenance,
        }
    if classification == "none":
        return {
            "schema_version": EXECUTION_FAILURE_SCHEMA,
            "status": "not_applicable",
            "classification": "none",
            "summary": normalized_summary,
            "fallback_to": None,
            "provenance": provenance,
        }
    return {
        "schema_version": EXECUTION_FAILURE_SCHEMA,
        "status": "present",
        "classification": classification,
        "summary": normalized_summary,
        "fallback_to": str(fallback_to) if isinstance(fallback_to, str) and fallback_to.strip() else None,
        "provenance": provenance,
    }

def latest_retry_evidence_payload(target_root: Path, item_id: str) -> dict[str, Any]:
    latest_attempt = latest_execution_attempt_payload(target_root, item_id)
    history = execution_attempt_history_payload(target_root, item_id)
    evidence = latest_attempt.get("evidence") if isinstance(latest_attempt, dict) else {}
    locator = evidence.get("locator") if isinstance(evidence, dict) else None
    freshness = latest_attempt.get("freshness") if isinstance(latest_attempt, dict) else None
    provenance = {
        "source_layer": "derived_surface",
        "source_locator": locator,
        "source_binding": "execution_attempt_history",
        "freshness": freshness if isinstance(freshness, str) else "missing",
        "conflict": "none",
    }
    if latest_attempt.get("status") == "missing":
        return {
            "schema_version": RETRY_EVIDENCE_SCHEMA,
            "status": "missing",
            "attempt_count": 0,
            "retry_count": 0,
            "latest_attempt_id": None,
            "latest_attempt_result": None,
            "latest_failure_classification": "unknown",
            "latest_failure_summary": latest_attempt.get("summary"),
            "exhausted": False,
            "scheduler_ownership": "external",
            "stale_attempt_count": 0,
            "provenance": provenance,
        }
    if latest_attempt.get("status") == "invalid":
        return {
            "schema_version": RETRY_EVIDENCE_SCHEMA,
            "status": "invalid",
            "attempt_count": 0,
            "retry_count": 0,
            "latest_attempt_id": None,
            "latest_attempt_result": None,
            "latest_failure_classification": "unknown",
            "latest_failure_summary": latest_attempt.get("summary"),
            "exhausted": False,
            "scheduler_ownership": "external",
            "stale_attempt_count": 0,
            "provenance": provenance,
        }

    latest_envelope = latest_attempt.get("attempt") if isinstance(latest_attempt.get("attempt"), dict) else {}
    current_head = _git_head_sha(target_root) or "unknown-head"
    current_attempts = [entry for entry in history if entry.get("head_sha") == current_head]
    stale_attempts = [entry for entry in history if entry.get("head_sha") != current_head]
    failure = latest_envelope.get("failure") if isinstance(latest_envelope, dict) else {}
    classification = failure.get("execution_classification") if isinstance(failure, dict) else None
    if not isinstance(classification, str) or classification not in EXECUTION_FAILURE_CLASSIFICATIONS:
        classification = "unknown"
    summary = failure.get("execution_summary") if isinstance(failure, dict) else latest_attempt.get("summary")
    latest_attempt_id = latest_envelope.get("attempt_id") if isinstance(latest_envelope, dict) else None
    latest_attempt_result = latest_envelope.get("result") if isinstance(latest_envelope, dict) else None
    attempt_count = len(current_attempts)
    retry_count = max(0, attempt_count - 1)
    if latest_attempt.get("freshness") == "stale":
        status = "stale"
    elif attempt_count <= 1 and classification == "none":
        status = "not_applicable"
    else:
        status = "present"
    return {
        "schema_version": RETRY_EVIDENCE_SCHEMA,
        "status": status,
        "attempt_count": attempt_count,
        "retry_count": retry_count,
        "latest_attempt_id": latest_attempt_id if isinstance(latest_attempt_id, str) and latest_attempt_id else None,
        "latest_attempt_result": latest_attempt_result if isinstance(latest_attempt_result, str) else None,
        "latest_failure_classification": classification,
        "latest_failure_summary": str(summary).strip() if isinstance(summary, str) and str(summary).strip() else None,
        "exhausted": classification == "retry_exhaustion",
        "scheduler_ownership": "external",
        "stale_attempt_count": len(stale_attempts),
        "provenance": provenance,
    }
