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
        'comment.user?.login === "github-actions[bot]"',
        "author_association",
        "created_at",
        "markerComments",
        "remediationMarker",
    )
    forbidden = (
        "pull_request:",
        "pull_request_target:",
        "BOOTSTRAP_EXCEPTION_POLICY",
        "loom:work-item-delivery-attestation",
        "attested_prs",
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
        "product_problem",
        "PHASE_CHILD_TYPES",
    )
    evaluator_missing = [needle for needle in evaluator_required if needle not in evaluator]
    transition_workflow_required = (
        'const crypto = require("crypto")',
        'body_sha256: crypto.createHash("sha256")',
        "v032RuntimeEolException",
        'repository: "MC-and-his-Agents/Loom"',
        "workItems: new Set([2125, 2126])",
        "pullRequest(number:$number)",
        "closingIssuesReferences(first:100)",
        "detailsUrl",
        "details_url: context.detailsUrl",
        "lastEditedAt",
        "github.rest.actions.getWorkflowRun",
        "html_url: run.html_url",
        "historical_delivery_prs",
        "workflow_path",
    )
    transition_evaluator_required = (
        "V032_RUNTIME_EOL_EXCEPTION",
        '"pr": 2127',
        '"covered_issues": (2125, 2126)',
        '"failed_run_id": 29288032023',
        "pr_body_sha256",
        "delivery_relation_invalid",
        "bootstrap_authorization_invalid",
        "bootstrap_run_mismatch",
    )
    workflow_transition = "v032RuntimeEolException" in text
    evaluator_transition = "V032_RUNTIME_EOL_EXCEPTION" in evaluator
    transition_missing = [needle for needle in transition_workflow_required if workflow_transition and needle not in text]
    transition_evaluator_missing = [needle for needle in transition_evaluator_required if evaluator_transition and needle not in evaluator]
    removed_surface = [
        needle
        for needle in (*transition_workflow_required, *transition_evaluator_required, "2127-bootstrap-batch")
        if not workflow_transition and not evaluator_transition and (needle in text or needle in evaluator)
    ]
    transition_mismatch = workflow_transition != evaluator_transition
    fixture_present = (ROOT / "tools" / "fixtures" / "fr-phase-close-guard" / "2127-bootstrap-batch.json").exists()
    if missing or present or evaluator_missing or transition_missing or transition_evaluator_missing or removed_surface or transition_mismatch or fixture_present:
        details = [
            *(f"missing `{needle}`" for needle in missing),
            *(f"forbidden `{needle}`" for needle in present),
            *(f"evaluator missing `{needle}`" for needle in evaluator_missing),
            *(f"transition workflow missing `{needle}`" for needle in transition_missing),
            *(f"transition evaluator missing `{needle}`" for needle in transition_evaluator_missing),
            *(f"removed surface present `{needle}`" for needle in removed_surface),
            *(("workflow/evaluator transition mismatch",) if transition_mismatch else ()),
            *(("removed #2127 fixture returned",) if fixture_present else ()),
        ]
        raise SystemExit("FR/Phase close guard workflow contract failed: " + "; ".join(details))
    print("FR/Phase close guard workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
