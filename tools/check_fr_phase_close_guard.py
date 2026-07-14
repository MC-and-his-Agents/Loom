#!/usr/bin/env python3
"""Focused contract checks for the host-native FR/Phase closure evaluator."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "skills" / "shared" / "scripts" / "github_closure_guard.py"
sys.path.insert(0, str(MODULE_PATH.parent))


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
        "comment_bodies": [],
        "comments": [],
        "comments_complete": True,
        "read_complete": True,
        **fields,
    }


def acceptance(subject: int, verdict: str = "passed", *, trusted: bool = True, rationale: str | None = None, repository: str = "o/r") -> dict[str, object]:
    locator = f"{repository}/issue/{subject}"
    return {
        "schema_version": "loom-product-acceptance/v1",
        "result": "pass",
        "story_locator": locator,
        "rationale": rationale,
        "product_acceptance": {
            "verdict": verdict,
            "trusted": trusted,
            "evidence_consumed": verdict == "passed" and trusted,
            "owns_lifecycle_closure": False,
        },
        "host_facts": {"source": "github", "read_complete": True, "story_locator": locator},
    }


def snapshot(subject: int, issues: list[dict[str, object]], *, product_acceptance: object = None) -> dict[str, object]:
    return {
        "subject": subject,
        "repository": "o/r",
        "actor": {"id": 1, "login": "maintainer"},
        "default_branch": "main",
        "issues": issues,
        "product_acceptance": acceptance(subject) if product_acceptance is None else product_acceptance,
    }


def main() -> int:
    module = load_module()
    pr = {
        "number": 31,
        "merged": True,
        "merged_at": "2026-07-11T00:02:30Z",
        "base_ref": "main",
        "head_sha": "a" * 40,
        "merge_commit": "b" * 40,
        "commit_sha": "a" * 40,
        "review_decision": "APPROVED",
        "check_rollup": {"state": "SUCCESS", "contexts_complete": True, "contexts": [{"type": "CheckRun", "name": "py-compile", "status": "COMPLETED", "conclusion": "SUCCESS", "completed_at": "2026-07-11T00:01:00Z"}]},
    }
    work_item = issue(3, "work_item", merged_prs=[pr])
    fr = issue(2, "fr", children=[3])
    phase = issue(1, "phase", children=[2])
    valid = module.evaluate_closure(snapshot(1, [phase, fr, work_item]), host_resolved=True)
    if valid.get("verdict") != "allow_completed_close" or valid.get("completed") is not True:
        raise AssertionError(f"complete native tree should close: {valid}")
    problem = issue(7, "product_problem", labels=["product-problem"], children=[2])
    release_work_item = issue(8, "work_item", merged_prs=[pr])
    phase_with_problem = issue(1, "phase", children=[7, 8])
    nested = module.evaluate_closure(snapshot(1, [phase_with_problem, problem, fr, work_item, release_work_item]), host_resolved=True)
    if nested.get("verdict") != "allow_completed_close":
        raise AssertionError(f"Phase must accept a Product Problem subtree and a phase-scoped release WI: {nested}")
    host_marker = '<!-- loom:host-action-attestation {"schema_version":"loom-host-action-attestation/v1","action_locator":"github://o/r/host-action/branch-protection/main","observed_at":"2026-07-11T00:02:00Z","verdict":"passed"} -->'
    host_comment = {"body": host_marker, "created_at": "2026-07-11T00:02:00Z", "author_association": "NONE", "user": {"id": 1, "login": "maintainer"}}
    host_only = issue(3, "work_item", labels=["host-only-delivery"], comments=[host_comment])
    if module.evaluate_closure(snapshot(1, [phase, fr, host_only]), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("authenticated host-only delivery attestation must replace a fabricated implementation PR")
    for invalid_comment in (
        {**host_comment, "author_association": "NONE", "user": {"id": 2, "login": "outsider"}},
        {**host_comment, "body": host_marker.replace("github://o/r/", "github://other/repo/")},
        {**host_comment, "body": host_marker + "\n" + host_marker},
    ):
        invalid_host_only = issue(3, "work_item", labels=["host-only-delivery"], comments=[invalid_comment])
        result = module.evaluate_closure(snapshot(1, [phase, fr, invalid_host_only]), host_resolved=True)
        if result.get("verdict") != "reopen_required" or not any(reason.get("code") == "missing_delivery_attestation" for reason in result.get("reasons", [])):
            raise AssertionError("untrusted, cross-repo, or ambiguous host-action attestation must fail closed")
    forged_comment = "<!-- loom:host-attestation {\"schema_version\":\"loom-host-attestation/v1\",\"verdict\":\"passed\"} -->"
    forged = issue(3, "work_item", merged_prs=[{key: value for key, value in pr.items() if key not in {"review_decision", "check_rollup"}}], comment_bodies=[forged_comment])
    if module.evaluate_closure({"subject": 3, "default_branch": "main", "issues": [forged]}).get("verdict") != "not_applicable":
        raise AssertionError("closure guard must not run on a standalone Work Item")
    forged_fr = issue(2, "fr", children=[3])
    forged_phase = issue(1, "phase", children=[2])
    forged_result = module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [forged_phase, forged_fr, forged]})
    if forged_result.get("verdict") != "reopen_required":
        raise AssertionError("a forged issue comment must not replace merged PR and check evidence")
    unapproved = issue(3, "work_item", merged_prs=[{**pr, "review_decision": "CHANGES_REQUESTED"}])
    if module.evaluate_closure(snapshot(1, [phase, fr, unapproved]), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("closure must consume merge-time delivery evidence without re-evaluating PR review policy")
    pending_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "PENDING", "contexts_complete": True, "contexts": pr["check_rollup"]["contexts"]}}])
    if module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, pending_checks]}).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR without a successful check rollup must reopen")
    failed_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "FAILURE", "contexts_complete": True, "contexts": [{**pr["check_rollup"]["contexts"][0], "conclusion": "FAILURE"}]}}])
    if module.evaluate_closure(snapshot(1, [phase, fr, failed_checks]), host_resolved=True).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR with a failed check rollup must reopen")
    retried_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "FAILURE", "contexts_complete": True, "contexts": [
        {"type": "CheckRun", "name": "loom-pr-merge-gate", "status": "COMPLETED", "conclusion": "FAILURE", "completed_at": "2026-07-11T00:00:00Z"},
        {"type": "CheckRun", "name": "loom-pr-merge-gate", "status": "COMPLETED", "conclusion": "SUCCESS", "completed_at": "2026-07-11T00:02:00Z"},
        {"type": "CheckRun", "name": "loom-pr-merge-gate", "status": "COMPLETED", "conclusion": "FAILURE", "completed_at": "2026-07-11T00:03:00Z"},
        {"type": "CheckRun", "name": "optional-demo", "status": "COMPLETED", "conclusion": "FAILURE", "completed_at": "2026-07-11T00:03:00Z"},
    ]}}])
    if module.evaluate_closure(snapshot(1, [phase, fr, retried_checks]), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("latest pre-merge successful delivery attempt must supersede stale failures, post-merge checks, and unrelated optional checks")
    skipped_optional = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "SUCCESS", "contexts_complete": True, "contexts": [*pr["check_rollup"]["contexts"], {"type": "CheckRun", "status": "COMPLETED", "conclusion": "SKIPPED"}]}}])
    if module.evaluate_closure(snapshot(1, [phase, fr, skipped_optional]), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("a successful aggregate rollup must allow intentionally skipped optional checks")
    missing_acceptance = module.evaluate_closure(snapshot(1, [phase, fr, work_item], product_acceptance=False), host_resolved=True)
    if missing_acceptance.get("verdict") != "reopen_required" or missing_acceptance.get("reasons", [{}])[0].get("code") != "product_acceptance_missing":
        raise AssertionError(f"completed closure must consume product acceptance: {missing_acceptance}")
    if missing_acceptance.get("failure_envelope", {}).get("primary_cause", {}).get("failure_domain") != "product_acceptance" or missing_acceptance.get("failure_envelope", {}).get("consequences") != []:
        raise AssertionError("acceptance closure failure must expose one product_acceptance primary cause")
    for rejected in (
        acceptance(1, "pending"),
        acceptance(1, "blocked"),
        acceptance(1, "failed"),
        acceptance(1, trusted=False),
    ):
        if module.evaluate_closure(snapshot(1, [phase, fr, work_item], product_acceptance=rejected), host_resolved=True).get("verdict") != "reopen_required":
            raise AssertionError("pending, blocked, failed, or untrusted acceptance must reopen")
    not_required = module.evaluate_closure(snapshot(1, [phase, fr, work_item], product_acceptance=acceptance(1, "not_required", rationale="no product behavior changed")), host_resolved=True)
    if not_required.get("verdict") != "allow_completed_close":
        raise AssertionError(f"trusted reasoned not_required must close: {not_required}")
    waived = acceptance(1, "waived", rationale="owner accepted the bounded risk")
    if module.evaluate_closure(snapshot(1, [phase, fr, work_item], product_acceptance=waived), host_resolved=True).get("verdict") != "reopen_required":
        raise AssertionError("waiver without host policy label must reopen")
    phase_with_waiver = issue(1, "phase", children=[2], labels=["product-acceptance-waiver-allowed"])
    if module.evaluate_closure(snapshot(1, [phase_with_waiver, fr, work_item], product_acceptance=waived), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("trusted reasoned policy-allowed waiver must close")
    missing_child = module.evaluate_closure(snapshot(2, [issue(2, "fr")]))
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
    locator_phase = issue(1, "phase", children=[2], comment_bodies=["<!-- loom:product-acceptance-artifact id:17 -->"])
    locator_work_item = issue(
        3,
        "work_item",
        merged_prs=[{**pr, "review_decision": None}],
    )
    raw_snapshot = {"subject": 1, "repository": "o/r", "actor": {"id": 1, "login": "maintainer"}, "default_branch": "main", "host_readable": True, "issues": [locator_phase, fr, locator_work_item]}
    def fake_acceptance(root, locator, artifact_id):
        if root != ROOT or locator != "o/r/issue/1" or artifact_id != 17:
            raise AssertionError("closure acceptance locator drifted")
        return acceptance(1)
    resolved = module.resolve_host_facts(raw_snapshot, ROOT, acceptance_resolver=fake_acceptance)
    if resolved.get("host_facts_resolved") is not True or module.evaluate_closure(resolved, host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError(f"host-resolved product acceptance and merged delivery must close: {resolved}")
    ambiguous_phase = issue(1, "phase", children=[2], comment_bodies=["<!-- loom:product-acceptance-artifact id:17 -->", "<!-- loom:product-acceptance-artifact id:18 -->"])
    ambiguous_snapshot = {"subject": 1, "repository": "o/r", "actor": {"id": 1, "login": "maintainer"}, "default_branch": "main", "host_readable": True, "issues": [ambiguous_phase, fr, work_item]}
    resolved_ambiguous = module.resolve_host_facts(ambiguous_snapshot, ROOT, acceptance_resolver=fake_acceptance)
    if module.evaluate_closure(resolved_ambiguous).get("verdict") != "reopen_required":
        raise AssertionError("ambiguous artifact locators must fail closed")
    frozen = json.loads((ROOT / "tools" / "fixtures" / "fr-phase-close-guard" / "2127-bootstrap-batch.json").read_text(encoding="utf-8"))
    raw_frozen_pr = frozen["pr"]
    authorization = raw_frozen_pr["comments"][0]
    if hashlib.sha256(authorization["body"].encode("utf-8")).hexdigest() != "486ca70bea8f4fe51eee2523629c907fdce82bdea57a7cc49b4f8c9bd29d37d9":
        raise AssertionError("#2127 bootstrap authorization comment fixture drifted")
    if hashlib.sha256(raw_frozen_pr["body"].encode("utf-8")).hexdigest() != "e6164372caa7d0f2de60b424336e913019576db6681799288bfeedbf709d86c2":
        raise AssertionError("#2127 PR metadata body fixture drifted")
    normalized_authorization = {
        "id": authorization["id"],
        "body_sha256": hashlib.sha256(authorization["body"].encode("utf-8")).hexdigest(),
        "created_at": authorization["created_at"],
        "updated_at": authorization["updated_at"],
        "author_association": authorization["author_association"],
        "user": authorization["user"],
    }
    frozen_pr = {
        **raw_frozen_pr,
        "authorization_comment": normalized_authorization,
        "failed_run": raw_frozen_pr["workflow_runs"][0],
        "closing_issues_complete": True,
        "closing_issues": [{"number": 2125, "repository": frozen["repository"]}],
    }
    def frozen_snapshot(subject: int, work_item: int, *, delivery_pr: dict[str, object] = frozen_pr, repository: str = frozen["repository"]) -> dict[str, object]:
        child = issue(
            work_item,
            "work_item",
            merged_prs=[delivery_pr] if work_item == 2125 else [],
            historical_delivery_prs=[delivery_pr],
        )
        return {
            "subject": subject,
            "repository": repository,
            "actor": {"id": 1, "login": "closer"},
            "default_branch": "main",
            "host_readable": True,
            "issues": [issue(subject, "fr", children=[work_item]), child],
            "product_acceptance": acceptance(subject, repository=repository),
        }
    for subject, work_item in ((2115, 2125), (2116, 2126)):
        frozen_result = module.evaluate_closure(frozen_snapshot(subject, work_item), host_resolved=True)
        if frozen_result.get("verdict") != "allow_completed_close":
            raise AssertionError(f"real #2127 delivery fixture must close FR #{subject}: {frozen_result}")
    def with_delivery_check(**updates: object) -> dict[str, object]:
        contexts = [
            {**context, **updates} if context.get("name") == "loom-delivery-gate" else context
            for context in frozen_pr["check_rollup"]["contexts"]
        ]
        return {**frozen_pr, "check_rollup": {**frozen_pr["check_rollup"], "contexts": contexts}}
    negatives = (
        ("delivery_binding_invalid", {**frozen_pr, "number": 2128}),
        ("delivery_binding_invalid", {**frozen_pr, "head_sha": "0" * 40}),
        ("delivery_binding_invalid", {**frozen_pr, "merge_commit": "0" * 40}),
        ("delivery_binding_invalid", {**frozen_pr, "body": frozen_pr["body"] + "\n"}),
        ("delivery_binding_invalid", {**frozen_pr, "last_edited_at": "2026-07-13T22:05:00Z"}),
        ("delivery_relation_invalid", {**frozen_pr, "closing_issues": []}),
        ("delivery_relation_invalid", {**frozen_pr, "closing_issues_complete": False}),
        ("bootstrap_authorization_invalid", {**frozen_pr, "authorization_comment": {**normalized_authorization, "body_sha256": "0" * 64}}),
        ("bootstrap_authorization_invalid", {**frozen_pr, "authorization_comment": {**normalized_authorization, "id": 1}}),
        ("bootstrap_authorization_invalid", {**frozen_pr, "authorization_comment": {**normalized_authorization, "user": {"id": 1, "login": "outsider"}}}),
        ("bootstrap_authorization_invalid", {**frozen_pr, "authorization_comment": {**normalized_authorization, "updated_at": "2026-07-13T22:05:00Z"}}),
        ("bootstrap_authorization_invalid", {**frozen_pr, "authorization_comment": {**normalized_authorization, "created_at": "2026-07-13T22:00:00Z", "updated_at": "2026-07-13T21:59:55Z"}}),
        ("bootstrap_run_mismatch", {**frozen_pr, "failed_run": {**frozen_pr["failed_run"], "id": 1}}),
        ("bootstrap_run_mismatch", {**frozen_pr, "failed_run": {**frozen_pr["failed_run"], "head_sha": "0" * 40}}),
        ("bootstrap_run_mismatch", {**frozen_pr, "failed_run": {**frozen_pr["failed_run"], "workflow_path": ".github/workflows/other.yml"}}),
        ("bootstrap_run_mismatch", {**frozen_pr, "failed_run": {**frozen_pr["failed_run"], "updated_at": "2026-07-13T22:05:00Z"}}),
        ("bootstrap_run_mismatch", with_delivery_check(name="other")),
        ("bootstrap_run_mismatch", with_delivery_check(type="StatusContext")),
        ("bootstrap_run_mismatch", with_delivery_check(status="IN_PROGRESS")),
        ("bootstrap_run_mismatch", with_delivery_check(conclusion="SUCCESS")),
        ("bootstrap_run_mismatch", with_delivery_check(started_at="2026-07-13T20:00:00Z", completed_at="2026-07-13T20:00:01Z")),
        ("bootstrap_run_mismatch", with_delivery_check(started_at="2026-07-13T21:54:56Z", completed_at="2026-07-13T21:54:46Z")),
        ("bootstrap_run_mismatch", with_delivery_check(details_url="https://github.com/MC-and-his-Agents/Loom/actions/runs/1/job/1")),
    )
    for expected_code, invalid_pr in negatives:
        invalid_result = module.evaluate_closure(frozen_snapshot(2116, 2126, delivery_pr=invalid_pr), host_resolved=True)
        primary = invalid_result.get("failure_envelope", {}).get("primary_cause", {})
        if invalid_result.get("verdict") != "reopen_required" or primary.get("code") != expected_code or invalid_result.get("failure_envelope", {}).get("consequences") != []:
            raise AssertionError(f"frozen delivery mutation must fail with {expected_code}: {invalid_result}")
    for repository, work_item in (("other/repo", 2126), (frozen["repository"], 2124)):
        unrelated = module.evaluate_closure(frozen_snapshot(2116, work_item, repository=repository), host_resolved=True)
        if unrelated.get("verdict") != "reopen_required" or unrelated.get("failure_envelope", {}).get("primary_cause", {}).get("code") != "missing_delivery_attestation":
            raise AssertionError("the historical exception must not apply to another repository or Work Item")
    print("fr/phase closure guard contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
