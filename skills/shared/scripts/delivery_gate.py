#!/usr/bin/env python3
"""Evaluate advisory delivery facts without reading Loom repository carriers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA = "loom-delivery-gate/v1"
HOST_FACTS_SCHEMA = "loom-delivery-gate-host-facts/v1"
SUPPORTED_EVENTS = {"pull_request", "merge_group", "workflow_call"}
PROFILES = {"light", "standard", "reinforced"}
LIGHT_PATH_PREFIXES = ("docs/",)
LIGHT_PATHS = {"README.md", "README.zh-CN.md"}
DEFAULT_VALIDATION_COMMAND = "make delivery-gate-check"
CAUSES = {
    "host_facts_unreadable": {
        "domain": "host_facts",
        "code": "unreadable",
        "locator": "host_facts:unreadable",
        "summary": "GitHub host facts are unreadable or incomplete.",
    },
    "profile_unsupported": {
        "domain": "delivery_profile",
        "code": "unsupported",
        "locator": "delivery_profile:unsupported",
        "summary": "The requested delivery profile is unsupported.",
    },
    "invalid_change_set": {
        "domain": "change_set",
        "code": "invalid",
        "locator": "change_set:invalid",
        "summary": "Changed paths are not a normalized repository-relative change set.",
    },
    "validation_command_missing": {
        "domain": "native_validation",
        "code": "command_missing",
        "locator": "native_validation:command_missing",
        "summary": "The selected native validation command is unavailable.",
    },
    "native_validation_failed": {
        "domain": "native_validation",
        "code": "failed",
        "locator": "native_validation:failed",
        "summary": "The selected native validation command failed.",
    },
    "passed": {
        "domain": "delivery",
        "code": "passed",
        "locator": "delivery:passed",
        "summary": "Host facts and selected native validation passed.",
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


def _cause(cause_id: str) -> dict[str, str]:
    return {"id": cause_id, **CAUSES[cause_id]}


def evaluate_host_facts(host_facts: object) -> dict[str, Any]:
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
    if host_errors:
        cause_id = "host_facts_unreadable"
    elif profile_errors:
        cause_id = "profile_unsupported"
    elif path_errors:
        cause_id = "invalid_change_set"
    elif validation_command_errors:
        cause_id = "validation_command_missing"
    else:
        cause_id = "passed"

    return {
        "schema_version": SCHEMA,
        "result": "advisory",
        "enforcement": "advisory",
        "summary": "Delivery facts were evaluated advisory-only; product acceptance remains unevaluated.",
        "primary_cause": _cause(cause_id),
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
    }


def finalize_delivery_gate(host_facts: object, validation_result: object) -> dict[str, Any]:
    """Apply the fixed delivery-cause priority after native validation."""

    payload = evaluate_host_facts(host_facts)
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
    return payload


def _read_host_facts(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"read_error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-facts-file", type=Path, required=True)
    parser.add_argument("--validation-result-file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    host_facts = _read_host_facts(args.host_facts_file)
    payload = (
        finalize_delivery_gate(host_facts, _read_host_facts(args.validation_result_file))
        if args.validation_result_file
        else evaluate_host_facts(host_facts)
    )
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
