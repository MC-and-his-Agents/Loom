#!/usr/bin/env python3
"""Evaluate delivery facts without reading Loom repository carriers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from failure_envelope import envelope, primary_cause


SCHEMA = "loom-delivery-gate/v1"
HOST_FACTS_SCHEMA = "loom-delivery-gate-host-facts/v1"
REQUIRED_CHECK_IDENTITY_SCHEMA = "loom-delivery-gate-required-check-identity/v3"
REQUIRED_CHECK_IDENTITY_READINESS_SCHEMA = "loom-delivery-gate-required-check-readiness/v3"
SUPPORTED_EVENTS = {"pull_request", "merge_group", "workflow_call"}
PROFILES = {"light", "standard", "reinforced"}
ENFORCEMENTS = {"advisory", "enforce"}
LIGHT_PATH_PREFIXES = ("docs/",)
LIGHT_PATHS = {"README.md", "README.zh-CN.md"}
DEFAULT_VALIDATION_COMMAND = "make delivery-gate-check"
CAUSES = {
    "host_facts_unreadable": {
        "failure_domain": "host_service",
        "code": "unreadable",
        "locator": "host_facts:unreadable",
        "summary": "GitHub host facts are unreadable or incomplete.",
        "owner": "github",
        "retryable": True,
        "remediation_command": "rerun loom-delivery-gate after GitHub host fact readback succeeds",
    },
    "profile_unsupported": {
        "failure_domain": "governance_metadata",
        "code": "unsupported",
        "locator": "delivery_profile:unsupported",
        "summary": "The requested delivery profile is unsupported.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "set host_facts.profile to light, standard, or reinforced",
    },
    "invalid_change_set": {
        "failure_domain": "governance_metadata",
        "code": "invalid",
        "locator": "change_set:invalid",
        "summary": "Changed paths are not a normalized repository-relative change set.",
        "owner": "github",
        "retryable": True,
        "remediation_command": "rerun loom-delivery-gate with normalized GitHub changed paths",
    },
    "validation_command_missing": {
        "failure_domain": "toolchain",
        "code": "command_missing",
        "locator": "native_validation:command_missing",
        "summary": "The selected native validation command is unavailable.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "declare an installed native validation command for this delivery profile",
    },
    "native_validation_failed": {
        "failure_domain": "toolchain",
        "code": "failed",
        "locator": "native_validation:failed",
        "summary": "The selected native validation command failed.",
        "owner": "repository",
        "retryable": True,
        "remediation_command": "fix the reported native validation failure, then rerun loom-delivery-gate",
    },
    "enforcement_unsupported": {
        "failure_domain": "governance_metadata",
        "code": "enforcement_unsupported",
        "locator": "delivery_gate:enforcement_unsupported",
        "summary": "The requested delivery-gate enforcement mode is unsupported.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "set delivery-gate enforcement to advisory or enforce",
    },
    "passed": {
        "failure_domain": "governance_metadata",
        "code": "passed",
        "locator": "delivery:passed",
        "summary": "Host facts and selected native validation passed.",
        "owner": "loom",
        "retryable": False,
        "remediation_command": "none",
    },
}

IDENTITY_CAUSES = {
    "required_check_identity_unreadable": {
        "failure_domain": "host_service",
        "code": "unreadable",
        "locator": "required_check_identity:unreadable",
        "summary": "The required-check host readback is malformed or incomplete.",
        "owner": "github",
        "retryable": True,
        "remediation_command": "rerun required-check identity readback after GitHub branch controls are readable",
    },
    "required_check_identity_unknown": {
        "failure_domain": "governance_metadata",
        "code": "unknown",
        "locator": "required_check_identity:unknown",
        "summary": "GitHub does not show the expected delivery check as required with an app identity.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "configure the expected delivery check and GitHub App identity in branch protection",
    },
    "required_check_identity_invalid": {
        "failure_domain": "governance_metadata",
        "code": "invalid",
        "locator": "required_check_identity:invalid",
        "summary": "GitHub requires the expected delivery-check context from a different app identity.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "replace the required check with loom-delivery-gate from the expected GitHub App",
    },
    "legacy_required_checks_present": {
        "failure_domain": "governance_metadata",
        "code": "legacy_required_checks_present",
        "locator": "required_check_identity:legacy_required_checks_present",
        "summary": "Configured legacy required checks remain enforced by GitHub branch controls.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "remove the listed legacy required checks from GitHub branch controls",
    },
    "unexpected_required_checks_present": {
        "failure_domain": "governance_metadata",
        "code": "unexpected_required_checks_present",
        "locator": "required_check_identity:unexpected_required_checks_present",
        "summary": "Undeclared required checks remain enforced by GitHub branch controls.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "declare or remove the unexpected required checks in GitHub branch controls",
    },
    "passed": {
        "failure_domain": "governance_metadata",
        "code": "passed",
        "locator": "required_check_identity:passed",
        "summary": "GitHub requires the expected delivery-check context from the expected app identity.",
        "owner": "loom",
        "retryable": False,
        "remediation_command": "none",
    },
}


def _paths(value: object) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], ["changed_paths must be a list"]
    paths: list[str] = []
    errors: list[str] = []
    for raw_path in value:
        if not isinstance(raw_path, str) or not raw_path or raw_path.startswith("/") or ".." in raw_path.split("/"):
            errors.append("changed_paths must contain normalized repository-relative paths")
            continue
        paths.append(raw_path)
    return paths, list(dict.fromkeys(errors))


def _profile(facts: dict[str, Any], paths: list[str]) -> tuple[str, str]:
    requested = facts.get("profile")
    if isinstance(requested, str) and requested in PROFILES:
        return requested, "host_facts"
    if paths and all(path in LIGHT_PATHS or path.startswith(LIGHT_PATH_PREFIXES) for path in paths):
        return "light", "changed_paths"
    return "standard", "default"


def _validation_command(facts: dict[str, Any]) -> tuple[str, list[str]]:
    value = facts.get("validation_command", DEFAULT_VALIDATION_COMMAND)
    if not isinstance(value, str) or not value.strip():
        return "", ["validation_command must be a non-empty string"]
    return value.strip(), []


def _enforcement(value: object) -> tuple[str, list[str]]:
    if value in ENFORCEMENTS:
        return str(value), []
    return "invalid", ["enforcement must be advisory or enforce"]


def _cause(cause_id: str) -> dict[str, Any]:
    return primary_cause(cause_id=cause_id, **CAUSES[cause_id])


def _identity_cause(cause_id: str) -> dict[str, Any]:
    return primary_cause(cause_id=cause_id, **IDENTITY_CAUSES[cause_id])


def _result(enforcement: str, cause_id: str) -> str:
    if enforcement == "advisory":
        return "advisory"
    return "passed" if enforcement == "enforce" and cause_id == "passed" else "blocked"


def evaluate_host_facts(host_facts: object, enforcement: object = "advisory") -> dict[str, Any]:
    """Evaluate host facts before the selected native validation runs."""

    host_errors: list[str] = []
    facts = host_facts if isinstance(host_facts, dict) else {}
    if not isinstance(host_facts, dict):
        host_errors.append("host facts must be a JSON object")
    if facts.get("schema_version") != HOST_FACTS_SCHEMA:
        host_errors.append(f"schema_version must be `{HOST_FACTS_SCHEMA}`")
    if any(isinstance(facts.get(key), str) and facts[key] for key in ("host_read_error", "read_error")):
        host_errors.append("host facts could not be read from GitHub")
    event = facts.get("event")
    if event not in SUPPORTED_EVENTS:
        host_errors.append("event must be pull_request, merge_group, or workflow_call")
    repository = facts.get("repository")
    if not isinstance(repository, dict) or not all(isinstance(repository.get(key), str) and repository[key] for key in ("owner", "name")):
        host_errors.append("repository.owner and repository.name are required")
        repository = {}
    paths, path_errors = _paths(facts.get("changed_paths"))
    profile_errors = ["profile must be light, standard, or reinforced when supplied"] if "profile" in facts and facts.get("profile") not in PROFILES else []
    profile, profile_source = _profile(facts, paths)
    validation_command, validation_command_errors = _validation_command(facts)
    enforcement_mode, enforcement_errors = _enforcement(enforcement)
    if host_errors:
        cause_id = "host_facts_unreadable"
    elif enforcement_errors:
        cause_id = "enforcement_unsupported"
    elif profile_errors:
        cause_id = "profile_unsupported"
    elif path_errors:
        cause_id = "invalid_change_set"
    elif validation_command_errors:
        cause_id = "validation_command_missing"
    else:
        cause_id = "passed"

    primary = _cause(cause_id)
    return {
        "schema_version": SCHEMA,
        "result": _result(enforcement_mode, cause_id),
        "enforcement": enforcement_mode,
        "summary": "Delivery facts were evaluated without inferring product acceptance.",
        "primary_cause": primary,
        "failure_envelope": envelope(primary),
        "product_acceptance": {"verdict": "not_evaluated"},
        "host_facts": {
            "status": "valid" if not host_errors else "unreadable",
            "event": event if isinstance(event, str) else "unknown",
            "repository": repository,
            "input_errors": list(dict.fromkeys(host_errors)),
        },
        "delivery": {
            "profile": profile,
            "profile_source": profile_source,
            "changed_paths": paths,
            "profile_errors": profile_errors,
            "change_set_errors": path_errors,
        },
        "native_validation": {
            "command": validation_command,
            "command_errors": validation_command_errors,
            "status": "pending",
            "security_boundary": "untrusted_execution_read_token_only",
        },
        "enforcement_errors": enforcement_errors,
    }


def finalize_delivery_gate(host_facts: object, validation_result: object, enforcement: object = "advisory") -> dict[str, Any]:
    """Apply the fixed delivery-cause priority after native validation."""

    payload = evaluate_host_facts(host_facts, enforcement)
    result = validation_result if isinstance(validation_result, dict) else {}
    status = result.get("status")
    payload["native_validation"]["status"] = status if isinstance(status, str) else "command_missing"
    if payload["primary_cause"]["id"] == "passed":
        if status == "command_missing":
            cause_id = "validation_command_missing"
        elif status == "failed":
            cause_id = "native_validation_failed"
        elif status == "passed":
            cause_id = "passed"
        else:
            cause_id = "validation_command_missing"
        payload["primary_cause"] = _cause(cause_id)
    payload["failure_envelope"] = envelope(payload["primary_cause"])
    payload["result"] = _result(payload["enforcement"], payload["primary_cause"]["id"])
    return payload


def build_required_check_identity(
    repository: dict[str, str],
    branch: str,
    expected_context: str,
    expected_app_id: int,
    legacy_contexts: object,
    retained_contexts: object,
    branch_protection: object,
    branch_rules: object,
    observed_at: str,
    branch_protection_read_error: str | None = None,
    branch_rules_read_error: str | None = None,
) -> dict[str, Any]:
    """Normalize effective required checks from GitHub branch protection and applicable rulesets."""

    errors: list[str] = []
    branch_protection_checks: list[dict[str, Any]] = []
    if branch_protection == {}:
        pass
    elif not isinstance(branch_protection, dict):
        errors.append("branch protection readback must be an object when present")
    else:
        status_checks = branch_protection.get("required_status_checks")
        checks = status_checks.get("checks") if isinstance(status_checks, dict) else None
        if not isinstance(checks, list):
            errors.append("branch protection required_status_checks.checks must be a list")
        else:
            for check in checks:
                if not isinstance(check, dict) or not isinstance(check.get("context"), str) or not check["context"]:
                    errors.append("branch protection required checks must contain non-empty contexts")
                    continue
                if not isinstance(check.get("app_id"), int) or check["app_id"] <= 0:
                    errors.append("branch protection required checks must contain positive app_id values")
                    continue
                branch_protection_checks.append({"context": check["context"], "app_id": check["app_id"], "plane": "branch_protection"})

    ruleset_checks: list[dict[str, Any]] = []
    if not isinstance(branch_rules, list):
        errors.append("applicable branch rules readback must be a list")
    else:
        for rule in branch_rules:
            if not isinstance(rule, dict) or rule.get("type") != "required_status_checks":
                continue
            parameters = rule.get("parameters")
            checks = parameters.get("required_status_checks") if isinstance(parameters, dict) else None
            if not isinstance(checks, list):
                errors.append("applicable required-status-checks rules must expose required_status_checks as a list")
                continue
            for check in checks:
                if not isinstance(check, dict) or not isinstance(check.get("context"), str) or not check["context"]:
                    errors.append("applicable ruleset required checks must contain non-empty contexts")
                    continue
                ruleset_checks.append(
                    {
                        "context": check["context"],
                        "app_id": None,
                        "plane": "ruleset",
                        "ruleset_id": rule.get("ruleset_id"),
                    }
                )
    return {
        "schema_version": REQUIRED_CHECK_IDENTITY_SCHEMA,
        "source": "github_branch_controls",
        "repository": repository,
        "branch": branch,
        "observed_at": observed_at,
        "required_check": {"context": expected_context, "app_id": expected_app_id},
        "legacy_contexts": legacy_contexts,
        "retained_contexts": retained_contexts,
        "branch_protection_checks": branch_protection_checks,
        "ruleset_checks": ruleset_checks,
        "normalization_errors": errors,
        "host_read_errors": {
            "branch_protection": branch_protection_read_error,
            "applicable_rulesets": branch_rules_read_error,
        },
    }


def evaluate_required_check_identity(evidence: object) -> dict[str, Any]:
    """Fail closed unless all GitHub branch-control planes require the expected check and no legacy check remains."""

    value = evidence if isinstance(evidence, dict) else {}
    errors: list[str] = []
    if value.get("schema_version") != REQUIRED_CHECK_IDENTITY_SCHEMA:
        errors.append(f"schema_version must be `{REQUIRED_CHECK_IDENTITY_SCHEMA}`")
    if value.get("source") != "github_branch_controls":
        errors.append("source must be github_branch_controls")
    repository = value.get("repository")
    if not isinstance(repository, dict) or not all(isinstance(repository.get(key), str) and repository[key] for key in ("owner", "name")):
        errors.append("repository.owner and repository.name are required")
        repository = {}
    if not isinstance(value.get("branch"), str) or not value["branch"]:
        errors.append("branch is required")
    if not isinstance(value.get("observed_at"), str) or not value["observed_at"]:
        errors.append("observed_at is required")
    required_check = value.get("required_check")
    if (
        not isinstance(required_check, dict)
        or not isinstance(required_check.get("context"), str)
        or not required_check["context"].strip()
        or not isinstance(required_check.get("app_id"), int)
        or required_check["app_id"] <= 0
    ):
        errors.append("required_check must name a non-empty context and a positive expected app_id")
        required_check = {"context": None, "app_id": None}
    legacy_contexts = value.get("legacy_contexts")
    retained_contexts = value.get("retained_contexts")
    if not isinstance(legacy_contexts, list) or any(not isinstance(context, str) or not context.strip() for context in legacy_contexts):
        errors.append("legacy_contexts must be a list of non-empty contexts")
        legacy_contexts = []
    if not isinstance(retained_contexts, list) or any(not isinstance(context, str) or not context.strip() for context in retained_contexts):
        errors.append("retained_contexts must be a list of non-empty contexts")
        retained_contexts = []
    if isinstance(required_check["context"], str) and required_check["context"] in legacy_contexts:
        errors.append("legacy_contexts must not contain the expected check context")
    if set(legacy_contexts) & set(retained_contexts):
        errors.append("legacy_contexts and retained_contexts must not overlap")
    branch_protection_checks = value.get("branch_protection_checks")
    ruleset_checks = value.get("ruleset_checks")
    if not isinstance(branch_protection_checks, list) or not isinstance(ruleset_checks, list):
        errors.append("branch_protection_checks and ruleset_checks must be lists")
        branch_protection_checks = []
        ruleset_checks = []
    checks = [*branch_protection_checks, *ruleset_checks]
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("context"), str) or not check["context"] or check.get("plane") not in {"branch_protection", "ruleset"}:
            errors.append("effective required checks must carry a non-empty context and known plane")
            break
    normalization_errors = value.get("normalization_errors")
    if not isinstance(normalization_errors, list) or any(not isinstance(error, str) for error in normalization_errors):
        errors.append("normalization_errors must be a list of strings")
    else:
        errors.extend(normalization_errors)
    host_read_errors = value.get("host_read_errors")
    if not isinstance(host_read_errors, dict) or any(
        key not in host_read_errors or host_read_errors[key] is not None and not isinstance(host_read_errors[key], str)
        for key in ("branch_protection", "applicable_rulesets")
    ):
        errors.append("host_read_errors must describe branch protection and applicable rulesets")
        host_read_errors = {}

    expected_context = required_check["context"]
    matching_app_ids = [item.get("app_id") for item in checks if isinstance(item, dict) and item.get("context") == expected_context]
    matching_known_app_ids = [app_id for app_id in matching_app_ids if isinstance(app_id, int) and app_id > 0]
    matching_app_identity_unavailable = any(app_id is None for app_id in matching_app_ids)
    legacy_required_checks = [
        item
        for item in checks
        if isinstance(item, dict) and item.get("context") in legacy_contexts
    ]
    allowed_contexts = {expected_context, *retained_contexts}
    unexpected_required_checks = [
        item
        for item in checks
        if isinstance(item, dict) and item.get("context") not in allowed_contexts
    ]
    if errors:
        cause_id = "required_check_identity_unreadable"
    elif any(host_read_errors.values()):
        cause_id = "required_check_identity_unknown"
    elif legacy_required_checks:
        cause_id = "legacy_required_checks_present"
    elif unexpected_required_checks:
        cause_id = "unexpected_required_checks_present"
    elif not matching_app_ids:
        cause_id = "required_check_identity_unknown"
    elif required_check["app_id"] in matching_known_app_ids:
        cause_id = "passed"
    elif matching_app_identity_unavailable:
        cause_id = "required_check_identity_unknown"
    else:
        cause_id = "required_check_identity_invalid"

    primary = _identity_cause(cause_id)
    return {
        "schema_version": REQUIRED_CHECK_IDENTITY_READINESS_SCHEMA,
        "result": "ready" if cause_id == "passed" else "blocked",
        "primary_cause": primary,
        "failure_envelope": envelope(primary),
        "identity": {
            "source": value.get("source"),
            "repository": repository,
            "branch": value.get("branch"),
            "observed_at": value.get("observed_at"),
            "required_check": required_check,
            "observed_app_ids": matching_known_app_ids,
            "effective_required_checks": checks,
            "legacy_required_checks": legacy_required_checks,
            "retained_contexts": sorted(allowed_contexts),
            "unexpected_required_checks": unexpected_required_checks,
        },
        "input_errors": errors,
    }


def _read_host_facts(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"read_error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-facts-file", type=Path, required=True)
    parser.add_argument("--validation-result-file", type=Path)
    parser.add_argument("--enforcement", default="advisory")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    host_facts = _read_host_facts(args.host_facts_file)
    payload = (
        finalize_delivery_gate(host_facts, _read_host_facts(args.validation_result_file), args.enforcement)
        if args.validation_result_file
        else evaluate_host_facts(host_facts, args.enforcement)
    )
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
