#!/usr/bin/env python3
"""Focused contract checks for the host-native FR/Phase closure evaluator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "skills" / "shared" / "scripts" / "github_closure_guard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("github_closure_guard", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load github closure guard")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def issue(number: int, kind: str, **fields: object) -> dict[str, object]:
    return {
        "number": number,
        "type": kind,
        "state": "CLOSED",
        "state_reason": "COMPLETED",
        "labels": [],
        "body": "",
        "children": [],
        "blocked_by": [],
        "merged_prs": [],
        "read_complete": True,
        **fields,
    }


def main() -> int:
    module = load_module()
    pr = {
        "number": 31,
        "merged": True,
        "base_ref": "main",
        "head_sha": "a" * 40,
        "merge_commit": "b" * 40,
        "commit_sha": "a" * 40,
        "review_decision": "APPROVED",
        "check_rollup": {"state": "SUCCESS", "contexts_complete": True, "contexts": [{"type": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS"}]},
    }
    work_item = issue(3, "work_item", merged_prs=[pr])
    fr = issue(2, "fr", children=[3])
    phase = issue(1, "phase", children=[2])
    valid = module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, work_item]})
    if valid.get("verdict") != "allow_completed_close" or valid.get("completed") is not True:
        raise AssertionError(f"complete native tree should close: {valid}")
    forged_comment = "<!-- loom:host-attestation {\"schema_version\":\"loom-host-attestation/v1\",\"verdict\":\"passed\"} -->"
    forged = issue(3, "work_item", merged_prs=[{key: value for key, value in pr.items() if key not in {"review_decision", "check_rollup"}}], comment_bodies=[forged_comment])
    if module.evaluate_closure({"subject": 3, "default_branch": "main", "issues": [forged]}).get("verdict") != "not_applicable":
        raise AssertionError("closure guard must not run on a standalone Work Item")
    forged_fr = issue(2, "fr", children=[3])
    forged_phase = issue(1, "phase", children=[2])
    forged_result = module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [forged_phase, forged_fr, forged]})
    if forged_result.get("verdict") != "reopen_required":
        raise AssertionError("a forged issue comment must not replace PR review and check evidence")
    unapproved = issue(3, "work_item", merged_prs=[{**pr, "review_decision": "CHANGES_REQUESTED"}])
    if module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, unapproved]}).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR without approval must reopen")
    pending_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "PENDING", "contexts_complete": True, "contexts": pr["check_rollup"]["contexts"]}}])
    if module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, pending_checks]}).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR without a successful check rollup must reopen")
    failed_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "FAILURE", "contexts_complete": True, "contexts": pr["check_rollup"]["contexts"]}}])
    if module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, failed_checks]}).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR with a failed check rollup must reopen")
    skipped_optional = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "SUCCESS", "contexts_complete": True, "contexts": [*pr["check_rollup"]["contexts"], {"type": "CheckRun", "status": "COMPLETED", "conclusion": "SKIPPED"}]}}])
    if module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, skipped_optional]}).get("verdict") != "allow_completed_close":
        raise AssertionError("a successful aggregate rollup must allow intentionally skipped optional checks")
    missing_child = module.evaluate_closure({"subject": 2, "default_branch": "main", "issues": [issue(2, "fr")]})
    if missing_child.get("verdict") != "reopen_required" or not any(reason.get("code") == "missing_native_child" for reason in missing_child.get("reasons", [])):
        raise AssertionError(f"FR without a Work Item must reopen: {missing_child}")
    deferred = issue(4, "fr", labels=["deferred"], state_reason="NOT_PLANNED")
    blocked_deferred = module.evaluate_closure({"subject": 4, "default_branch": "main", "issues": [deferred]})
    if blocked_deferred.get("verdict") != "reopen_required" or len(blocked_deferred.get("reasons", [])) != 2:
        raise AssertionError(f"deferred item without recovery contract must reopen: {blocked_deferred}")
    deferred["body"] = "## Activation Policy\n\nResume after provider approval.\n\nSuccessor: work_item:5\n"
    allowed_deferred = module.evaluate_closure({"subject": 4, "default_branch": "main", "issues": [deferred]})
    if allowed_deferred.get("verdict") != "allow_non_completion_close" or allowed_deferred.get("completed") is not False:
        raise AssertionError(f"deferred item must not be counted completed: {allowed_deferred}")
    deferred_completed = issue(4, "fr", labels=["deferred"], state_reason="COMPLETED", body=deferred["body"])
    if module.evaluate_closure({"subject": 4, "default_branch": "main", "issues": [deferred_completed]}).get("verdict") != "reopen_required":
        raise AssertionError("deferred closure must not use completed semantics")
    duplicate_completed = issue(5, "fr", labels=["duplicate"])
    if module.evaluate_closure({"subject": 5, "default_branch": "main", "issues": [duplicate_completed]}).get("verdict") != "reopen_required":
        raise AssertionError("non-completion label must not use completed semantics")
    ambiguous = issue(6, "unknown", labels=["fr", "phase"])
    if module.evaluate_closure({"subject": 6, "default_branch": "main", "issues": [ambiguous]}).get("verdict") != "reopen_required":
        raise AssertionError("ambiguous FR/Phase type must not bypass the guard")
    unreadable = module.evaluate_closure({"subject": 2, "default_branch": "main", "issues": [issue(2, "fr", read_complete=False)]})
    if unreadable.get("verdict") != "reopen_required" or unreadable.get("reasons", [{}])[0].get("code") != "host_unreadable":
        raise AssertionError(f"unreadable host facts must fail closed: {unreadable}")
    print("fr/phase closure guard contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
