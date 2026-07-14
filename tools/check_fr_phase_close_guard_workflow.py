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
        'const crypto = require("crypto")',
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
        'body_sha256: crypto.createHash("sha256")',
        "comment_id: written.id",
        "comment.id !== written.id",
        'String(comment.body || "") !== body',
        "reopen_required",
        "defaultBranchRef",
        "closedByPullRequestsReferences",
        "reviewDecision",
        "statusCheckRollup",
        "v032RuntimeEolException",
        'repository: "MC-and-his-Agents/Loom"',
        "workItems: new Set([2125, 2126])",
        "pullRequest(number:$number)",
        "closingIssuesReferences(first:100)",
        "detailsUrl",
        "details_url: context.detailsUrl",
        "lastEditedAt",
        "createdAt",
        "github.rest.issues.getComment",
        "github.rest.actions.getWorkflowRun",
        "html_url: run.html_url",
        "historical_delivery_prs",
        "workflow_path",
        "closedAt",
        "event_closed_at",
        "context.payload.sender?.id",
        "context.payload.sender?.login",
        'current.state !== "closed"',
        'current.state_reason !== "completed"',
        "changed after the closure snapshot",
        "comment_bodies",
        'comment.user?.login === "github-actions[bot]"',
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
        "loom:repo-pr-metadata",
        "V032_RUNTIME_EOL_EXCEPTION",
        '"pr": 2127',
        '"covered_issues": (2125, 2126)',
        '"failed_run_id": 29288032023',
        "pr_body_sha256",
        "delivery_relation_invalid",
        "bootstrap_authorization_invalid",
        "bootstrap_run_mismatch",
        "product_problem",
        "PHASE_CHILD_TYPES",
    )
    evaluator_missing = [needle for needle in evaluator_required if needle not in evaluator]
    generic_waiver_surface = [
        needle for needle in ("loom:work-item-delivery-attestation", "BOOTSTRAP_EXCEPTION_POLICY", "attested_prs")
        if needle in text or needle in evaluator
    ]
    if missing or present or evaluator_missing or generic_waiver_surface:
        details = [*(f"missing `{needle}`" for needle in missing), *(f"forbidden `{needle}`" for needle in present), *(f"evaluator missing `{needle}`" for needle in evaluator_missing), *(f"generic waiver surface `{needle}`" for needle in generic_waiver_surface)]
        raise SystemExit("FR/Phase close guard workflow contract failed: " + "; ".join(details))
    print("FR/Phase close guard workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
