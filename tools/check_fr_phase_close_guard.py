#!/usr/bin/env python3
"""Focused contract checks for the host-native FR/Phase closure evaluator."""

from __future__ import annotations

import importlib.util
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


def acceptance(subject: int, verdict: str = "passed", *, trusted: bool = True, rationale: str | None = None) -> dict[str, object]:
    locator = f"o/r/issue/{subject}"
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
        "default_branch": "main",
        "review_policy": {"read_complete": True, "required_approving_review_count": 1},
        "issues": issues,
        "product_acceptance": acceptance(subject) if product_acceptance is None else product_acceptance,
    }


def single_attestation(pr: dict[str, object]) -> dict[str, object]:
    return {
        "source": "github",
        "read_complete": True,
        "pr": {"number": pr["number"], "head_sha": pr["head_sha"], "base_ref": pr["base_ref"], "merge_commit_sha": pr["merge_commit"]},
        "review": {"state": "SINGLE_MAINTAINER_ATTESTED", "commit_id": pr["head_sha"]},
        "review_policy": {
            "mode": "single_maintainer", "verified": True, "maintainer_count": 1,
            "maintainer": {"id": 1, "login": "maintainer"},
            "run_started_at": "2026-07-11T00:00:00Z", "run_updated_at": "2026-07-11T00:02:00Z", "artifact_created_at": "2026-07-11T00:01:00Z",
            "assertion_verified": True, "assertion_created_at": "2026-07-11T00:02:00Z", "assertion_comment_id": 11,
        },
        "semantic_tree": {"commit_sha": pr["head_sha"], "semantic_digest": "sha256:" + "c" * 64},
        "artifact": {"name": f"loom-host-attestation-{pr['number']}", "digest": "sha256:" + "d" * 64, "run_id": 9},
        "workflow_run": {"id": 9, "head_sha": pr["head_sha"], "event": "pull_request_target", "binding": "pull_request_target", "path": ".github/workflows/host-attestation-evidence.yml", "status": "completed", "conclusion": "success"},
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
        "check_rollup": {"state": "SUCCESS", "contexts_complete": True, "contexts": [{"type": "CheckRun", "name": "py-compile", "status": "COMPLETED", "conclusion": "SUCCESS", "completed_at": "2026-07-11T00:01:00Z"}]},
    }
    work_item = issue(3, "work_item", merged_prs=[pr])
    fr = issue(2, "fr", children=[3])
    phase = issue(1, "phase", children=[2])
    valid = module.evaluate_closure(snapshot(1, [phase, fr, work_item]), host_resolved=True)
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
    zero_approval_policy = snapshot(1, [phase, fr, issue(3, "work_item", merged_prs=[{**pr, "review_decision": None}])])
    zero_approval_policy["review_policy"] = {"read_complete": True, "required_approving_review_count": 0}
    if module.evaluate_closure(zero_approval_policy, host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("a merged green PR must satisfy a host policy requiring zero approvals")
    unreadable_review_policy = snapshot(1, [phase, fr, work_item])
    unreadable_review_policy["review_policy"] = {"read_complete": False}
    if module.evaluate_closure(unreadable_review_policy, host_resolved=True).get("verdict") != "reopen_required":
        raise AssertionError("unreadable host review policy must fail closed")
    pending_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "PENDING", "contexts_complete": True, "contexts": pr["check_rollup"]["contexts"]}}])
    if module.evaluate_closure({"subject": 1, "default_branch": "main", "issues": [phase, fr, pending_checks]}).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR without a successful check rollup must reopen")
    failed_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "FAILURE", "contexts_complete": True, "contexts": [{**pr["check_rollup"]["contexts"][0], "conclusion": "FAILURE"}]}}])
    if module.evaluate_closure(snapshot(1, [phase, fr, failed_checks]), host_resolved=True).get("verdict") != "reopen_required":
        raise AssertionError("a merged PR with a failed check rollup must reopen")
    retried_checks = issue(3, "work_item", merged_prs=[{**pr, "check_rollup": {"state": "FAILURE", "contexts_complete": True, "contexts": [
        {"type": "CheckRun", "name": "loom-pr-merge-gate", "status": "COMPLETED", "conclusion": "FAILURE", "completed_at": "2026-07-11T00:00:00Z"},
        {"type": "CheckRun", "name": "loom-pr-merge-gate", "status": "COMPLETED", "conclusion": "SUCCESS", "completed_at": "2026-07-11T00:02:00Z"},
        {"type": "CheckRun", "name": "optional-demo", "status": "COMPLETED", "conclusion": "FAILURE", "completed_at": "2026-07-11T00:03:00Z"},
    ]}}])
    if module.evaluate_closure(snapshot(1, [phase, fr, retried_checks]), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("latest successful delivery check attempt must supersede stale failures and unrelated optional checks")
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
    single_pr = {**pr, "review_decision": None}
    single_pr["host_attestation"] = single_attestation(single_pr)
    single_pr["host_attestation_errors"] = []
    single_work_item = issue(3, "work_item", labels=["review-policy-single-maintainer"], merged_prs=[single_pr])
    if module.evaluate_closure(snapshot(1, [phase, fr, single_work_item]), host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError("host-authenticated sole maintainer attestation must satisfy review policy")
    forged_single = issue(3, "work_item", labels=["review-policy-single-maintainer"], merged_prs=[{**single_pr, "host_attestation": {"source": "github", "read_complete": True}}])
    if module.evaluate_closure(snapshot(1, [phase, fr, forged_single]), host_resolved=True).get("verdict") != "reopen_required":
        raise AssertionError("repo-authored or incomplete single-maintainer JSON must not self-attest")
    for bad_assertion in (None, False):
        bad_facts = single_attestation(single_pr)
        bad_facts["review_policy"]["assertion_verified"] = bad_assertion
        bad_pr = {**single_pr, "host_attestation": bad_facts}
        bad_work_item = issue(3, "work_item", labels=["review-policy-single-maintainer"], merged_prs=[bad_pr])
        if module.evaluate_closure(snapshot(1, [phase, fr, bad_work_item]), host_resolved=True).get("verdict") != "reopen_required":
            raise AssertionError("single-maintainer policy requires an explicit post-artifact assertion by the authenticated sole maintainer")
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
        labels=["review-policy-single-maintainer"],
        merged_prs=[{**pr, "review_decision": None}],
        comment_bodies=[f"<!-- loom:host-attestation-artifact pr:31 head:{pr['head_sha']} id:7 -->"],
        comments=[{"body": f"<!-- loom:host-attestation-artifact pr:31 head:{pr['head_sha']} id:7 -->", "created_at": "2026-07-11T00:02:00Z", "author_association": "OWNER", "user": {"id": 1, "login": "maintainer"}}],
    )
    raw_snapshot = {"subject": 1, "repository": "o/r", "default_branch": "main", "review_policy": {"read_complete": True, "required_approving_review_count": 1}, "host_readable": True, "issues": [locator_phase, fr, locator_work_item]}
    def fake_acceptance(root, locator, artifact_id):
        if root != ROOT or locator != "o/r/issue/1" or artifact_id != 17:
            raise AssertionError("closure acceptance locator drifted")
        return acceptance(1)
    def fake_attestation(root, owner, repo, pr_number, artifact_id, **kwargs):
        if (root, owner, repo, pr_number, artifact_id, kwargs) != (ROOT, "o", "r", 31, 7, {"work_item": 3, "allow_merged": True, "review_policy": "single_maintainer"}):
            raise AssertionError("closure attestation locator or policy drifted")
        return single_attestation(pr), []
    resolved = module.resolve_host_facts(raw_snapshot, ROOT, acceptance_resolver=fake_acceptance, attestation_reader=fake_attestation)
    if resolved.get("host_facts_resolved") is not True or module.evaluate_closure(resolved, host_resolved=True).get("verdict") != "allow_completed_close":
        raise AssertionError(f"host-resolved product acceptance and single-maintainer attestation must close: {resolved}")
    ambiguous_phase = issue(1, "phase", children=[2], comment_bodies=["<!-- loom:product-acceptance-artifact id:17 -->", "<!-- loom:product-acceptance-artifact id:18 -->"])
    ambiguous_snapshot = {"subject": 1, "repository": "o/r", "default_branch": "main", "review_policy": {"read_complete": True, "required_approving_review_count": 1}, "host_readable": True, "issues": [ambiguous_phase, fr, work_item]}
    resolved_ambiguous = module.resolve_host_facts(ambiguous_snapshot, ROOT, acceptance_resolver=fake_acceptance, attestation_reader=fake_attestation)
    if module.evaluate_closure(resolved_ambiguous).get("verdict") != "reopen_required":
        raise AssertionError("ambiguous artifact locators must fail closed")
    print("fr/phase closure guard contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
