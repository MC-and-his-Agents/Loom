#!/usr/bin/env python3
"""Keep the FR/Phase close guard on the trusted issues.closed boundary."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "loom-fr-phase-close-guard.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "name: loom-fr-phase-close-guard",
        "issues:",
        "types: [closed]",
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
        "Checkout trusted default branch evaluator",
        "ref: ${{ github.event.repository.default_branch }}",
        "github.rest.issues.update",
        "github.rest.issues.get",
        "github.rest.issues.createComment",
        "github.rest.issues.getComment",
        "comment_id: created.id",
        "reopen_required",
        "defaultBranchRef",
        "closedByPullRequestsReferences",
        "reviewDecision",
        "statusCheckRollup",
        "comment_bodies",
        "hasSnapshotMarker",
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
    )
    missing = [needle for needle in required if needle not in text]
    present = [needle for needle in forbidden if needle in text]
    if missing or present:
        details = [*(f"missing `{needle}`" for needle in missing), *(f"forbidden `{needle}`" for needle in present)]
        raise SystemExit("FR/Phase close guard workflow contract failed: " + "; ".join(details))
    print("FR/Phase close guard workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
