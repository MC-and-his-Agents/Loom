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


def envelope(primary: dict[str, Any], *, consequences: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Expose exactly one primary cause; every additional diagnostic is a consequence."""

    return {
        "schema_version": SCHEMA,
        "primary_cause": primary,
        "consequences": [consequence(item, primary_id=str(primary.get("id"))) for item in consequences or []],
    }


def public_cli_failure_envelope(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Create the shared envelope at the public CLI boundary without rewriting command payloads."""

    existing = payload.get("failure_envelope")
    if isinstance(existing, dict):
        return existing
    result = str(payload.get("result") or "block")
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
    consequences = []
    if isinstance(diagnostics, list):
        for index, diagnostic in enumerate(diagnostics):
            consequences.append(
                primary_cause(
                    cause_id=f"{primary['id']}.diagnostic.{index + 1}",
                    failure_domain=domain,
                    code="diagnostic",
                    locator=f"cli:{command.replace(' ', '-')}:diagnostic:{index + 1}",
                    summary=str(diagnostic.get("summary") if isinstance(diagnostic, dict) else diagnostic),
                    owner=primary["owner"],
                    retryable=primary["retryable"],
                    transient=primary["transient"],
                    cause_class="consequence",
                    details={"diagnostic": diagnostic},
                    remediation_command=primary["remediation_command"],
                )
            )
    return envelope(primary, consequences=consequences)
