#!/usr/bin/env python3
"""Keep the required PR binding workflow host-native and read-only."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "pr-merge-gate.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "name: loom-pr-merge-gate",
        "pull_request:",
        "- opened",
        "- edited",
        "- reopened",
        "- synchronize",
        "contents: read",
        "pull-requests: read",
        "issues: read",
        "actions/github-script@v7",
        "Work Item: work_item:<number>",
        "(work_item|fr|phase)",
        "github.rest.issues.get",
        '"work-item", "fr", "phase"',
        "closingReferences",
    )
    forbidden = (
        "pull_request_target",
        "actions/checkout",
        "tools/loom_flow.py",
        "current.md",
        "head.sha",
        "run:",
    )
    missing = [needle for needle in required if needle not in text]
    present = [needle for needle in forbidden if needle in text]
    if missing or present:
        details = [*(f"missing `{needle}`" for needle in missing), *(f"forbidden `{needle}`" for needle in present)]
        raise SystemExit("pr binding workflow contract failed: " + "; ".join(details))
    print("pr binding workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
