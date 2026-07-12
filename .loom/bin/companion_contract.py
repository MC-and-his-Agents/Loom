#!/usr/bin/env python3
"""Repo companion contract readers shared by flow domains."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fact_chain_support import load_json_file, resolve_repo_relative_path


def tool_availability_for_surface(repo_interface: object, *, surface: str) -> dict[str, Any]:
    empty_payload = {
        "schema_version": "loom-dynamic-tool-handshake/v1",
        "surface": surface,
        "result": "pass",
        "summary": "no dynamic tool handshake evidence applies to this surface.",
        "declared_tools": [],
        "blocking_tools": [],
        "advisory_tools": [],
        "failure_summary": {
            "required_blocking": [],
            "optional_advisory": [],
            "by_status": {
                "advertised": 0,
                "failed": 0,
                "unavailable": 0,
                "unsupported": 0,
            },
        },
        "missing_inputs": [],
        "fallback_to": None,
    }
    if not isinstance(repo_interface, dict):
        return empty_payload
    tool_availability = repo_interface.get("tool_availability")
    if not isinstance(tool_availability, dict):
        return empty_payload
    declared_tools = tool_availability.get("declared_tools")
    if not isinstance(declared_tools, list):
        return empty_payload

    applicable: list[dict[str, Any]] = []
    for tool in declared_tools:
        if not isinstance(tool, dict):
            continue
        tool_surface = tool.get("surface")
        if tool_surface in {surface, "attempt_time"}:
            applicable.append(tool)
    by_status = {
        "advertised": 0,
        "failed": 0,
        "unavailable": 0,
        "unsupported": 0,
    }
    blocking_tools: list[dict[str, Any]] = []
    advisory_tools: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    fallback_to: str | None = None
    for tool in applicable:
        status = tool.get("status")
        if isinstance(status, str) and status in by_status:
            by_status[status] += 1
        if tool.get("result") == "block":
            blocking_tools.append(tool)
            fallback = tool.get("fallback_to")
            if fallback_to is None and isinstance(fallback, str) and fallback:
                fallback_to = fallback
            for message in tool.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(str(message))
        elif tool.get("status") != "advertised":
            advisory_tools.append(tool)

    result = "block" if blocking_tools else "pass"
    if blocking_tools:
        summary = "required dynamic tool handshake evidence blocks this surface."
    elif advisory_tools:
        summary = "only optional or advisory dynamic tool handshake failures apply to this surface."
    elif applicable:
        summary = "dynamic tool handshake evidence is advertised for this surface."
    else:
        summary = empty_payload["summary"]
    return {
        **empty_payload,
        "result": result,
        "summary": summary,
        "declared_tools": applicable,
        "blocking_tools": blocking_tools,
        "advisory_tools": advisory_tools,
        "failure_summary": {
            "required_blocking": blocking_tools,
            "optional_advisory": advisory_tools,
            "by_status": by_status,
        },
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to if result == "block" else None,
    }


def load_repo_interop_contract(repo_interop: object, *, target_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(repo_interop, dict):
        return None, ["governance_surface.repo_interop"]
    availability = repo_interop.get("availability")
    if availability == "absent":
        return None, ["repo interop contract is absent"]
    if availability == "incomplete":
        missing_inputs = repo_interop.get("missing_inputs")
        return None, list(missing_inputs) if isinstance(missing_inputs, list) else ["repo interop contract is incomplete"]
    if availability != "present":
        return None, [f"unknown repo interop availability: {availability}"]

    contract_locator = repo_interop.get("contract")
    declared_locator = (
        contract_locator.get("locator")
        if isinstance(contract_locator, dict)
        else ".loom/companion/interop.json"
    )
    interop_path, locator_errors = resolve_repo_relative_path(
        target_root,
        str(declared_locator),
        label="repo interop contract locator",
    )
    if locator_errors:
        return None, locator_errors
    assert interop_path is not None
    try:
        payload = load_json_file(interop_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None, [f"missing repo interop contract: {interop_path}"]
    if not isinstance(payload, dict):
        return None, [f"repo interop contract is unreadable: {interop_path}"]
    return payload, []
