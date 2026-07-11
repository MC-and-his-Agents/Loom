"""Small, transport-neutral failure envelope for Loom host-facing gates."""

from __future__ import annotations

from typing import Any


SCHEMA = "loom-failure-envelope/v1"
FAILURE_DOMAINS = frozenset(
    {
        "product_acceptance",
        "governance_metadata",
        "carrier",
        "git_history",
        "toolchain",
        "environment",
        "permission",
        "host_service",
        "external_dependency",
    }
)
OWNERS = frozenset({"loom", "repository", "github", "ci", "operator", "external_service"})
PASS_RESULTS = frozenset({"pass", "passed", "ready", "not_applicable"})
BASE_CAUSE_FIELDS = ("id", "failure_domain", "code", "locator", "summary", "owner", "retryable", "remediation_command")


def primary_cause(
    *,
    cause_id: str,
    failure_domain: str,
    code: str,
    locator: str,
    summary: str,
    owner: str,
    retryable: bool,
    remediation_command: str,
    cause_class: str | None = None,
    transient: bool = False,
    details: dict[str, Any] | None = None,
    consequence_of: list[str] | None = None,
) -> dict[str, Any]:
    """Build one actionable primary cause; callers use fixed, reviewed vocabulary."""

    if failure_domain not in FAILURE_DOMAINS:
        raise ValueError(f"unsupported failure domain: {failure_domain}")
    if owner not in OWNERS:
        raise ValueError(f"unsupported failure owner: {owner}")
    return {
        "id": cause_id,
        "failure_domain": failure_domain,
        "code": code,
        "locator": locator,
        "summary": summary,
        "owner": owner,
        "retryable": retryable,
        "cause_class": cause_class or code,
        "transient": transient,
        "details": dict(details or {}),
        "consequence_of": list(consequence_of or []),
        "remediation_command": remediation_command,
    }


def consequence(cause: dict[str, Any], *, primary_id: str) -> dict[str, Any]:
    """Mark an additional diagnostic as downstream of the selected primary cause."""

    return {**cause, "consequence_of": [primary_id]}


def normalize_cause(value: object, *, primary: bool = False) -> dict[str, Any]:
    """Normalize a v1 cause while accepting the fields shipped before v0.30."""

    if not isinstance(value, dict):
        raise ValueError("cause must be an object")
    for field in BASE_CAUSE_FIELDS:
        field_value = value.get(field)
        if field == "retryable":
            if not isinstance(field_value, bool):
                raise ValueError("cause.retryable must be a boolean")
        elif not isinstance(field_value, str) or not field_value:
            raise ValueError(f"cause.{field} must be a non-empty string")
    if value["failure_domain"] not in FAILURE_DOMAINS or value["owner"] not in OWNERS:
        raise ValueError("cause failure_domain or owner is unsupported")
    cause_class = value.get("cause_class", value["code"])
    transient = value.get("transient", False)
    details = value.get("details", {})
    consequence_of = value.get("consequence_of", [])
    if not isinstance(cause_class, str) or not cause_class:
        raise ValueError("cause.cause_class must be a non-empty string")
    if not isinstance(transient, bool) or not isinstance(details, dict):
        raise ValueError("cause.transient must be boolean and cause.details must be an object")
    if not isinstance(consequence_of, list) or any(not isinstance(item, str) or not item for item in consequence_of):
        raise ValueError("cause.consequence_of must be a list of non-empty strings")
    if primary and consequence_of:
        raise ValueError("primary cause cannot be a consequence")
    return primary_cause(
        cause_id=value["id"],
        failure_domain=value["failure_domain"],
        code=value["code"],
        locator=value["locator"],
        summary=value["summary"],
        owner=value["owner"],
        retryable=value["retryable"],
        cause_class=cause_class,
        transient=transient,
        details=details,
        consequence_of=consequence_of,
        remediation_command=value["remediation_command"],
    )


def envelope(
    primary: dict[str, Any],
    *,
    consequences: list[dict[str, Any]] | None = None,
    suppressed_diagnostics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Expose one primary, causal consequences, and independent suppressed diagnostics."""

    normalized_primary = normalize_cause(primary, primary=True)
    primary_id = normalized_primary["id"]
    normalized_consequences = [consequence(normalize_cause(item), primary_id=primary_id) for item in consequences or []]
    normalized_suppressed = [{**normalize_cause(item), "consequence_of": []} for item in suppressed_diagnostics or []]
    secondary_alias = [*normalized_consequences, *normalized_suppressed]

    return {
        "schema_version": SCHEMA,
        "primary_cause": normalized_primary,
        "consequences": normalized_consequences,
        "suppressed_diagnostics": normalized_suppressed,
        "secondary_causes": secondary_alias,
    }


def normalize_envelope(value: object, *, fallback_primary: object = None) -> dict[str, Any]:
    """Read current or legacy v1 without trusting arbitrary nested dictionaries."""

    if value is None:
        return envelope(normalize_cause(fallback_primary, primary=True))
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA:
        raise ValueError(f"failure envelope must use {SCHEMA}")
    primary = normalize_cause(value.get("primary_cause"), primary=True)
    primary_id = primary["id"]
    current_consequences = value.get("consequences", [])
    current_suppressed = value.get("suppressed_diagnostics", [])
    legacy_secondary = value.get("secondary_causes", [])
    for name, collection in (
        ("consequences", current_consequences),
        ("suppressed_diagnostics", current_suppressed),
        ("secondary_causes", legacy_secondary),
    ):
        if not isinstance(collection, list):
            raise ValueError(f"failure envelope {name} must be a list")
    causal = [normalize_cause(item) for item in current_consequences]
    suppressed = [normalize_cause(item) for item in current_suppressed]
    seen = {item["id"] for item in [*causal, *suppressed]}
    for item in legacy_secondary:
        normalized = normalize_cause(item)
        if normalized["id"] in seen:
            continue
        (causal if primary_id in normalized["consequence_of"] else suppressed).append(normalized)
        seen.add(normalized["id"])
    return envelope(primary, consequences=causal, suppressed_diagnostics=suppressed)


def malformed_envelope(payload: dict[str, Any], reason: str) -> dict[str, Any]:
    """Replace malformed caller assertions with one fail-closed public CLI cause."""

    payload["result"] = "block"
    command = str(payload.get("command") or "loom")
    primary = primary_cause(
        cause_id="malformed_failure_envelope",
        failure_domain="governance_metadata",
        code="malformed",
        locator=f"cli:{command.replace(' ', '-')}:failure-envelope",
        summary="The delegated failure envelope is malformed and cannot be trusted.",
        owner="loom",
        retryable=False,
        cause_class="contract_violation",
        details={"validation_error": reason},
        remediation_command="repair the delegated command failure envelope, then rerun the command",
    )
    return envelope(primary)


def public_cli_failure_envelope(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Create the shared envelope at the public CLI boundary without rewriting command payloads."""

    result = str(payload.get("result") or "block")
    existing = payload.get("failure_envelope")
    asserted_primary = payload.get("primary_cause")
    if existing is not None or asserted_primary is not None:
        try:
            normalized = normalize_envelope(existing, fallback_primary=asserted_primary)
            if asserted_primary is not None and normalize_cause(asserted_primary, primary=True) != normalized["primary_cause"]:
                raise ValueError("payload primary_cause conflicts with failure_envelope.primary_cause")
            return normalized
        except ValueError as exc:
            return malformed_envelope(payload, str(exc))
    if result in PASS_RESULTS:
        return None
    command = str(payload.get("command") or "loom")
    failed_layer = str(payload.get("failed_layer") or "public-cli")
    requested_domain = payload.get("failure_domain")
    if requested_domain in FAILURE_DOMAINS:
        domain = str(requested_domain)
    elif command.startswith("acceptance") or "product_acceptance" in payload:
        domain = "product_acceptance"
    elif any(token in failed_layer for token in ("permission", "authorization", "authentication")):
        domain = "permission"
    elif any(token in failed_layer for token in ("git-history", "git_history", "revision")):
        domain = "git_history"
    elif any(token in failed_layer for token in ("carrier", "shadow")):
        domain = "carrier"
    elif any(token in failed_layer for token in ("environment", "workspace", "runtime-provider")):
        domain = "environment"
    else:
        domain = "governance_metadata"
    cause_class = str(payload.get("cause_class") or f"{domain}_failure")
    summary = str(payload.get("summary") or payload.get("fail_closed_reason") or f"{command} failed")
    owner = payload.get("failure_owner")
    owner = str(owner) if owner in OWNERS else "operator"
    remediation = payload.get("remediation_command") or payload.get("fallback_to") or "loom help --json"
    if isinstance(remediation, list):
        remediation = remediation[0] if remediation else "loom help --json"
    primary = primary_cause(
        cause_id=str(payload.get("primary_error_code") or f"{command.replace(' ', '_')}_{cause_class}"),
        failure_domain=domain,
        code=str(payload.get("primary_error_code") or cause_class),
        locator=str(payload.get("failure_locator") or f"cli:{command.replace(' ', '-')}"),
        summary=summary,
        owner=owner,
        retryable=bool(payload.get("retryable", False)),
        transient=bool(payload.get("transient", False)),
        cause_class=cause_class,
        details={
            "failed_layer": failed_layer,
            "result": result,
            **({"fail_closed_reason": payload["fail_closed_reason"]} if payload.get("fail_closed_reason") else {}),
        },
        remediation_command=str(remediation),
    )
    diagnostics = payload.get("actionable_findings")
    suppressed = []
    if isinstance(diagnostics, list):
        for index, diagnostic in enumerate(diagnostics):
            suppressed.append(
                primary_cause(
                    cause_id=f"{primary['id']}.diagnostic.{index + 1}",
                    failure_domain=domain,
                    code="diagnostic",
                    locator=f"cli:{command.replace(' ', '-')}:diagnostic:{index + 1}",
                    summary=str(diagnostic.get("summary") if isinstance(diagnostic, dict) else diagnostic),
                    owner=primary["owner"],
                    retryable=primary["retryable"],
                    transient=primary["transient"],
                    cause_class="additional_diagnostic",
                    details={"diagnostic": diagnostic},
                    remediation_command=primary["remediation_command"],
                )
            )
    return envelope(primary, suppressed_diagnostics=suppressed)
