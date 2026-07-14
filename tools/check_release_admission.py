#!/usr/bin/env python3
"""Focused fail-closed checks for host-native release admission."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "release_admission.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("release_admission", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("release admission evaluator is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot() -> dict[str, Any]:
    return {
        "repository": "MC-and-his-Agents/Loom",
        "ref": "refs/heads/main",
        "head_sha": "a" * 40,
        "default_branch": "main",
        "default_branch_tip": "a" * 40,
        "read_complete": True,
        "release_issue": {
            "number": 2130,
            "state": "OPEN",
            "state_reason": None,
            "labels": ["work-item"],
            "milestone_number": 31,
            "blocked_by": [{"number": 2137, "state": "CLOSED", "state_reason": "COMPLETED"}],
        },
        "acceptance_artifact_id": 7,
        "milestone_issues": [
            {"number": 2114, "state": "CLOSED", "state_reason": "COMPLETED", "labels": ["fr"]},
            {"number": 2137, "state": "CLOSED", "state_reason": "COMPLETED", "labels": ["work-item"]},
            {"number": 2130, "state": "OPEN", "state_reason": None, "labels": ["work-item"]},
        ],
    }


def acceptance() -> dict[str, Any]:
    return {
        "result": "pass",
        "story_locator": "MC-and-his-Agents/Loom/issue/2130",
        "product_acceptance": {
            "verdict": "passed",
            "trusted": True,
            "evidence_consumed": True,
            "owns_lifecycle_closure": False,
        },
        "host_facts": {
            "source": "github",
            "read_complete": True,
            "artifact_id": 7,
            "run_head_sha": "a" * 40,
        },
    }


def assert_block(module: Any, facts: dict[str, Any], accepted: dict[str, Any], code: str) -> None:
    result = module.evaluate(facts, accepted)
    primary = result.get("failure_envelope", {}).get("primary_cause", {})
    if result.get("result") != "block" or primary.get("id") != code or result.get("failure_envelope", {}).get("consequences") != []:
        raise AssertionError(f"release admission must fail once with {code}: {result}")


def main() -> int:
    module = load_module()
    valid = module.evaluate(snapshot(), acceptance())
    if valid.get("result") != "pass" or valid.get("acceptance_artifact_id") != 7 or valid.get("mutates") is not False:
        raise AssertionError(f"valid live release facts must admit publication: {valid}")
    assert_block(module, {**snapshot(), "read_complete": False}, acceptance(), "host_read_incomplete")
    assert_block(module, {**snapshot(), "ref": "refs/heads/old"}, acceptance(), "release_head_not_current")
    assert_block(module, {**snapshot(), "default_branch_tip": "b" * 40}, acceptance(), "release_head_not_current")
    closed_issue = {**snapshot(), "release_issue": {**snapshot()["release_issue"], "state": "CLOSED"}}
    assert_block(module, closed_issue, acceptance(), "release_work_item_invalid")
    open_dependency = {**snapshot(), "release_issue": {**snapshot()["release_issue"], "blocked_by": [{"number": 2137, "state": "OPEN", "state_reason": None}]}}
    assert_block(module, open_dependency, acceptance(), "release_dependency_open")
    not_planned_dependency = {**snapshot(), "release_issue": {**snapshot()["release_issue"], "blocked_by": [{"number": 2137, "state": "CLOSED", "state_reason": "NOT_PLANNED"}]}}
    assert_block(module, not_planned_dependency, acceptance(), "release_dependency_open")
    open_fr = {**snapshot(), "milestone_issues": [{**snapshot()["milestone_issues"][0], "state": "OPEN"}, *snapshot()["milestone_issues"][1:]]}
    assert_block(module, open_fr, acceptance(), "release_scope_incomplete")
    missing_release_row = {**snapshot(), "milestone_issues": [row for row in snapshot()["milestone_issues"] if row["number"] != 2130]}
    assert_block(module, missing_release_row, acceptance(), "milestone_read_incomplete")
    missing_marker = {**snapshot(), "acceptance_artifact_id": None}
    assert_block(module, missing_marker, acceptance(), "release_acceptance_locator_invalid")
    mismatched_marker = {**snapshot(), "acceptance_artifact_id": 8}
    assert_block(module, mismatched_marker, acceptance(), "release_acceptance_untrusted")
    for rejected in (
        {},
        {**acceptance(), "result": "block"},
        {**acceptance(), "story_locator": "MC-and-his-Agents/Loom/issue/1"},
        {**acceptance(), "host_facts": {**acceptance()["host_facts"], "run_head_sha": "b" * 40}},
        {**acceptance(), "product_acceptance": {**acceptance()["product_acceptance"], "trusted": False}},
    ):
        assert_block(module, snapshot(), rejected, "release_acceptance_untrusted")
    print("release admission contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
