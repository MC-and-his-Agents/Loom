#!/usr/bin/env python3
"""Keep the FR/Phase close guard on the trusted issues.closed boundary."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "loom-fr-phase-close-guard.yml"
EVALUATOR = ROOT / "src" / "skills" / "shared" / "scripts" / "github_closure_guard.py"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "name: loom-fr-phase-close-guard",
        "issues:",
        "types: [closed]",
        "actions: read",
        "contents: read",
        "issues: write",
        "pull-requests: read",
        "concurrency:",
        "loom-fr-phase-close-guard-${{ github.repository }}-${{ github.event.issue.number }}",
        "cancel-in-progress: false",
        "actions/github-script@v7",
        "github.graphql",
        "github.paginate",
        "github_closure_guard.py",
        "--snapshot",
        "--output",
        "--resolve-host-facts",
        "GH_TOKEN: ${{ github.token }}",
        "Checkout trusted default branch evaluator",
        "ref: ${{ github.event.repository.default_branch }}",
        "github.rest.issues.update",
        "github.rest.issues.get",
        "github.rest.issues.createComment",
        "github.rest.issues.updateComment",
        "github.rest.issues.getComment",
        "comment_id: written.id",
        "comment.id !== written.id",
        'String(comment.body || "") !== body',
        "reopen_required",
        "defaultBranchRef",
        "closedByPullRequestsReferences",
        "reviewDecision",
        "statusCheckRollup",
        "closedAt",
        "event_closed_at",
        "context.payload.sender?.id",
        "context.payload.sender?.login",
        'current.state !== "closed"',
        'current.state_reason !== "completed"',
        "changed after the closure snapshot",
        "comment_bodies",
        "author_association",
        "created_at",
        "markerComments",
        "remediationMarker",
    )
    forbidden = (
        "pull_request:",
        "pull_request_target:",
        "tools/loom_flow.py",
        "current.md",
        "head.sha",
        "const evaluate",
        "validateCompleted",
        "getBranchProtection",
        "branchProtectionRule",
        "requiredApprovingReviewCount",
    )
    missing = [needle for needle in required if needle not in text]
    present = [needle for needle in forbidden if needle in text]
    evaluator = EVALUATOR.read_text(encoding="utf-8")
    evaluator_required = (
        "resolve_host_facts",
        "product_acceptance_missing",
        "product_acceptance_untrusted",
        "loom:product-acceptance-artifact",
        "loom:host-action-attestation",
        "host_only_delivery",
        "failure_envelope",
        "missing_delivery_attestation",
    )
    evaluator_missing = [needle for needle in evaluator_required if needle not in evaluator]
    if missing or present or evaluator_missing:
        details = [*(f"missing `{needle}`" for needle in missing), *(f"forbidden `{needle}`" for needle in present), *(f"evaluator missing `{needle}`" for needle in evaluator_missing)]
        raise SystemExit("FR/Phase close guard workflow contract failed: " + "; ".join(details))
    print("FR/Phase close guard workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
