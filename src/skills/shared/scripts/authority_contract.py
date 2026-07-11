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
LOCATOR_RE = re.compile(
    r"^(?P<owner>[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)/"
    r"(?P<type>[a-z_][a-z0-9_]*)/"
    r"(?P<id>[1-9][0-9]*)$"
)
LEGACY_LOCATOR_RE = re.compile(r"^(?P<type>[a-z_][a-z0-9_]*):(?P<id>[1-9][0-9]*)$")
LOCATOR_TYPES = frozenset({"issue", "phase", "fr", "work_item", "pr", "project"})
LEGACY_LOCATOR_COMPATIBILITY = {
    "accepted_for_reads_through": "v0.30.x",
    "removed_in": "v0.31.0",
    "rendered": False,
}
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


def typed_locator(owner: str, repo: str, object_type: str, object_id: int) -> str:
    """Render one globally unique GitHub locator as owner/repo/type/id."""

    candidate = f"{owner}/{repo}/{object_type}/{object_id}"
    if (
        not isinstance(object_id, int)
        or object_id <= 0
        or object_type not in LOCATOR_TYPES
        or LOCATOR_RE.fullmatch(candidate) is None
    ):
        raise ValueError("typed locator requires owner/repo, a supported type, and a positive integer id")
    return candidate


def parse_typed_locator(
    value: object,
    *,
    allowed_types: set[str] | frozenset[str] | None = None,
    allow_legacy: bool = True,
) -> dict[str, Any] | None:
    """Parse a canonical locator, with time-bounded legacy read compatibility."""

    if not isinstance(value, str):
        return None
    match = LOCATOR_RE.fullmatch(value)
    legacy = False
    if match is None and allow_legacy:
        match = LEGACY_LOCATOR_RE.fullmatch(value)
        legacy = match is not None
    if match is None:
        return None
    object_type = match.group("type")
    if object_type not in LOCATOR_TYPES or (allowed_types is not None and object_type not in allowed_types):
        return None
    object_id = int(match.group("id"))
    return {
        "owner": None if legacy else match.group("owner"),
        "repo": None if legacy else match.group("repo"),
        "type": object_type,
        "id": object_id,
        "number": object_id,
        "locator": value,
        "legacy": legacy,
        "compatibility": LEGACY_LOCATOR_COMPATIBILITY if legacy else None,
    }


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
