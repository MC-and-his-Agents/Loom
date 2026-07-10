"""Read-only product acceptance record validation.

This module deliberately never reads delivery, PR, CI, or repository carriers.
It validates only a supplied record and does not execute product actions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from authority_contract import authority_verdict, parse_typed_locator
from failure_envelope import envelope as failure_envelope, primary_cause


SCHEMA = "loom-product-acceptance/v1"
EVIDENCE_CLASSES = frozenset({"static", "contract_test", "fixture", "process_runtime", "live_readonly", "live_write_precheck", "external_visible_write"})
VERDICTS = frozenset({"not_required", "pending", "passed", "failed", "blocked", "waived"})
SAFE_ACTIONS = frozenset({"launch", "provider_detect", "browser_open", "read", "capture"})
PROHIBITED_ACTIONS = frozenset({"login", "captcha_or_risk_bypass", "submit", "publish", "send", "external_visible_write"})
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def valid_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(entry, str) and entry.strip() for entry in value)


def evidence_errors(evidence: object, *, minimum_class: str, now: datetime) -> list[str]:
    if not isinstance(evidence, dict):
        return ["evidence must be an object"]
    errors: list[str] = []
    evidence_class = evidence.get("evidence_class")
    if evidence_class not in EVIDENCE_CLASSES:
        errors.append("evidence_class is unsupported")
    elif evidence_class != minimum_class:
        errors.append(f"evidence_class `{evidence_class}` does not satisfy exact minimum `{minimum_class}`")
    observed_at = parse_time(evidence.get("observed_at"))
    freshness = evidence.get("freshness_window_seconds")
    if observed_at is None:
        errors.append("observed_at must be RFC3339 with a timezone")
    if not isinstance(freshness, int) or freshness <= 0:
        errors.append("freshness_window_seconds must be a positive integer")
    elif observed_at is not None and observed_at > now:
        errors.append("observed_at cannot be in the future")
    elif observed_at is not None and (now - observed_at).total_seconds() > freshness:
        errors.append("evidence is stale")
    if not isinstance(evidence.get("run_id"), str) or not evidence["run_id"].strip():
        errors.append("run_id must be a non-empty string")
    if not valid_string_list(evidence.get("artifact_refs")):
        errors.append("artifact_refs must contain at least one reference")
    profile = evidence.get("provider_profile")
    if not isinstance(profile, dict) or not all(isinstance(profile.get(key), str) and profile[key].strip() for key in ("provider", "profile")) or profile.get("redacted") is not True:
        errors.append("provider_profile must be redacted and identify provider/profile")
    versions = evidence.get("component_versions")
    if not isinstance(versions, dict) or not versions or any(not isinstance(repo, str) or not repo or not isinstance(sha, str) or SHA_RE.fullmatch(sha) is None for repo, sha in versions.items()):
        errors.append("component_versions must bind every component to a 40-character SHA")
    boundary = evidence.get("operation_boundary")
    if not isinstance(boundary, dict):
        errors.append("operation_boundary must be an object")
    else:
        allowed, prohibited, observed = (boundary.get(key) for key in ("allowed_actions", "prohibited_actions", "observed_actions"))
        if not all(isinstance(value, list) and all(isinstance(action, str) for action in value) for value in (allowed, prohibited, observed)):
            errors.append("operation_boundary actions must be string lists")
        elif not set(allowed).issubset(SAFE_ACTIONS) or not PROHIBITED_ACTIONS.issubset(set(prohibited)) or not set(observed).issubset(set(allowed)) or set(observed) & set(prohibited):
            errors.append("operation_boundary permits or observed an unsafe action")
    return errors


def evaluate_acceptance(record: object, *, now: datetime | None = None) -> dict[str, Any]:
    """Validate one externally-owned acceptance record without cross-state inference."""

    current_time = now or datetime.now(timezone.utc)
    current_time = current_time.astimezone(timezone.utc)
    payload = record if isinstance(record, dict) else {}
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must be `{SCHEMA}`")
    if parse_typed_locator(payload.get("story_locator"), allowed_types={"issue", "fr", "work_item"}) is None:
        errors.append("story_locator must be a typed issue, fr, or work_item locator")
    if not isinstance(payload.get("scenario_id"), str) or not payload["scenario_id"].strip():
        errors.append("scenario_id must be a non-empty string")
    declared = payload.get("verdict")
    if declared not in VERDICTS:
        errors.append("verdict is unsupported")
    minimum = payload.get("minimum_evidence_class")
    if minimum not in EVIDENCE_CLASSES:
        errors.append("minimum_evidence_class is unsupported")
    if declared in {"waived", "not_required"} and (not isinstance(payload.get("rationale"), str) or not payload["rationale"].strip()):
        errors.append("waived and not_required verdicts require a rationale")
    evidence = payload.get("evidence")
    if declared == "passed":
        if not isinstance(evidence, list) or not evidence:
            errors.append("passed verdict requires evidence")
        elif minimum in EVIDENCE_CLASSES:
            for index, item in enumerate(evidence):
                errors.extend(f"evidence[{index}]: {message}" for message in evidence_errors(item, minimum_class=minimum, now=current_time))
    elif evidence is not None and not isinstance(evidence, list):
        errors.append("evidence must be a list when supplied")

    acceptance_verdict = "blocked" if errors else declared
    cause = primary_cause(
        cause_id="product_acceptance_valid" if not errors else "product_acceptance_record_invalid",
        failure_domain="product_acceptance",
        code="accepted" if not errors else "record_invalid",
        locator=str(payload.get("story_locator") or "product_acceptance:record"),
        summary="product acceptance record is valid and remains independently owned." if not errors else errors[0],
        owner="repository" if not errors else "operator",
        retryable=bool(errors),
        remediation_command="loom acceptance validate --input <record.json> --json",
    )
    return {
        "schema_version": SCHEMA,
        "result": "pass" if not errors else "block",
        "declared_verdict": declared,
        "product_acceptance": {"verdict": acceptance_verdict, "owner": "product_acceptance_adapter", "evidence_consumed": bool(declared == "passed" and not errors)},
        "authority_verdict": authority_verdict(product_acceptance=acceptance_verdict),
        "story_locator": payload.get("story_locator"),
        "scenario_id": payload.get("scenario_id"),
        "minimum_evidence_class": minimum,
        "missing_inputs": errors,
        "failure_envelope": failure_envelope(cause),
        "mutates": False,
        "network_access": False,
        "runtime_actions_executed": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loom acceptance validate")
    parser.add_argument("action", choices=("validate",))
    parser.add_argument("--input", required=True)
    parser.add_argument("--now")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    now = parse_time(args.now) if args.now else None
    if args.now and now is None:
        parser.error("--now must be RFC3339 with a timezone")
    try:
        record = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record = None
        now = None
        result = evaluate_acceptance(record)
        result["missing_inputs"] = [f"acceptance input is unreadable: {exc}"]
        result["result"] = "block"
        result["product_acceptance"]["verdict"] = "blocked"
    else:
        result = evaluate_acceptance(record, now=now)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
