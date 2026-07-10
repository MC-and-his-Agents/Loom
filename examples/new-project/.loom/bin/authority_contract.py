"""Field authority and host-native lifecycle verdict contract.

This module deliberately validates independent facts.  It never derives
delivery, product acceptance, or reconciliation from another fact, and it
does not read or write repository carriers.
"""

from __future__ import annotations

import re
from typing import Any


SCHEMA = "loom-field-authority-verdict/v1"
LIFECYCLE_SCHEMA = "loom-host-lifecycle-admission/v1"
LOCATOR_RE = re.compile(r"^(?P<type>[a-z_][a-z0-9_]*):(?P<number>[1-9][0-9]*)$")
LOCATOR_TYPES = frozenset({"issue", "phase", "fr", "work_item", "pr", "project"})
DELIVERY_STATES = frozenset({"not_evaluated", "implementing", "pr_ready", "merged", "delivery_closed_out"})
PRODUCT_ACCEPTANCE_STATES = frozenset({"not_evaluated", "not_required", "pending", "passed", "failed", "blocked", "waived"})
RECONCILIATION_STATES = frozenset({"not_evaluated", "pending", "consistent", "drifted"})

FIELD_AUTHORITIES = {
    "work_item_scope": {"owner": "github_issue", "freshness": "live_readback"},
    "delivery_state": {"owner": "github_delivery_host", "freshness": "live_readback"},
    "product_acceptance": {"owner": "product_acceptance_adapter", "freshness": "adapter_declared"},
    "reconciliation_state": {"owner": "reconciliation_evaluator", "freshness": "current_evaluation"},
    "pr_head_checks_merge": {"owner": "github_pull_request", "freshness": "live_readback"},
    "workstation_session": {"owner": "workstation", "freshness": "session_local"},
    "historical_audit": {"owner": "git_or_actions_history", "freshness": "immutable_history"},
}


def typed_locator(object_type: str, number: int) -> str:
    """Render one validated typed GitHub-style locator."""

    if object_type not in LOCATOR_TYPES or not isinstance(number, int) or number <= 0:
        raise ValueError("typed locator requires a supported type and positive integer")
    return f"{object_type}:{number}"


def parse_typed_locator(value: object, *, allowed_types: set[str] | frozenset[str] | None = None) -> dict[str, Any] | None:
    """Parse a typed locator without accepting a bare number or ambiguous kind."""

    if not isinstance(value, str):
        return None
    match = LOCATOR_RE.fullmatch(value)
    if match is None:
        return None
    object_type = match.group("type")
    if object_type not in LOCATOR_TYPES or (allowed_types is not None and object_type not in allowed_types):
        return None
    return {"type": object_type, "number": int(match.group("number")), "locator": value}


def authority_verdict(
    *,
    delivery_state: object = "not_evaluated",
    product_acceptance: object = "not_evaluated",
    reconciliation_state: object = "not_evaluated",
) -> dict[str, Any]:
    """Validate independent verdict fields without creating cross-state implications."""

    values = {
        "delivery_state": delivery_state,
        "product_acceptance": product_acceptance,
        "reconciliation_state": reconciliation_state,
    }
    allowed = {
        "delivery_state": DELIVERY_STATES,
        "product_acceptance": PRODUCT_ACCEPTANCE_STATES,
        "reconciliation_state": RECONCILIATION_STATES,
    }
    errors = [f"{name} must be one of {', '.join(sorted(allowed[name]))}" for name, value in values.items() if value not in allowed[name]]
    return {
        "schema_version": SCHEMA,
        "result": "pass" if not errors else "block",
        "field_authority": FIELD_AUTHORITIES,
        "verdict": values,
        "missing_inputs": errors,
        "primary_remediation": None if not errors else "supply valid independent authority verdict values",
    }


def lifecycle_admission_verdict(admission: object) -> dict[str, Any]:
    """Expose one carrier-free lifecycle result from an existing admission readback."""

    payload = admission if isinstance(admission, dict) else {}
    subject = payload.get("subject") if isinstance(payload.get("subject"), dict) else {}
    subject_type = subject.get("type")
    subject_locator = subject.get("locator")
    admission_state = payload.get("admission_state")
    admission_result = payload.get("result")
    authority = authority_verdict()
    intent = payload.get("intent")
    if subject_type == "work_item" and admission_result == "pass":
        result, lifecycle_state, remediation = "pass", "not_applicable", None
    elif admission_state == "unsupported_subject":
        result, lifecycle_state, remediation = "pass", "not_applicable", None
    elif admission_result == "pass" and admission_state in {"planning", "admitted"}:
        result, lifecycle_state, remediation = "pass", str(admission_state), None
    elif admission_state == "not_planned":
        result = "pass" if intent == "planning" else "block"
        lifecycle_state = "not_planned"
        remediation = None if result == "pass" else "select or reopen a Work Item before entering execution"
    else:
        result = "block"
        lifecycle_state = str(admission_state or "host_unreadable")
        remediation = payload.get("next_action") if isinstance(payload.get("next_action"), str) and payload.get("next_action") else "run loom route --target <repo> --issue <fr> --task <work-item scope> --intent build --apply --json"
    return {
        "schema_version": LIFECYCLE_SCHEMA,
        "result": result,
        "lifecycle_state": lifecycle_state,
        "subject": {"type": subject_type, "locator": subject_locator},
        "admission_state": admission_state,
        "authority_verdict": authority,
        "primary_remediation": remediation,
        "carrier_mutations": False,
    }
