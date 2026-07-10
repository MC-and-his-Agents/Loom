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
        "consequence_of": list(consequence_of or []),
        "remediation_command": remediation_command,
    }


def envelope(primary: dict[str, Any], *, secondary_causes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Expose exactly one primary cause; secondary facts are never co-primary."""

    return {
        "schema_version": SCHEMA,
        "primary_cause": primary,
        "secondary_causes": list(secondary_causes or []),
    }
