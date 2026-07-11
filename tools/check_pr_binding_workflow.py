#!/usr/bin/env python3
"""Keep the required PR binding workflow host-native and read-only."""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "pr-merge-gate.yml"


def github_script(text: str) -> str:
    marker = "          script: |\n"
    if marker not in text:
        raise SystemExit("pr binding workflow contract failed: missing github-script body")
    return textwrap.dedent(text.split(marker, 1)[1])


def assert_binding_case(script: str, body: str, *, expected_error: str | None) -> None:
    harness = """
const context = {repo: {owner: "owner", repo: "repo"}, payload: {pull_request: {body: __BODY__}}};
const github = {rest: {issues: {get: async () => ({data: {state: "open", labels: [{name: "work-item"}]}})}}};
const core = {notice: () => undefined};
(async () => {
__SCRIPT__
})().then(() => process.exit(0)).catch((error) => { console.error(error.message); process.exit(1); });
"""
    harness = harness.replace("__BODY__", json.dumps(body)).replace("__SCRIPT__", textwrap.indent(script, "  "))
    result = subprocess.run(["node", "-e", harness], text=True, capture_output=True, check=False)
    if expected_error is None and result.returncode != 0:
        raise SystemExit(f"pr binding workflow contract failed: same-repo qualified reference blocked: {result.stderr.strip()}")
    if expected_error is not None and (result.returncode == 0 or expected_error not in result.stderr):
        raise SystemExit(
            f"pr binding workflow contract failed: expected `{expected_error}` for `{body.strip()}`: {result.stderr.strip()}"
        )


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
        "Work Item: owner/repo/work_item/id",
        "locatorOwner.toLowerCase()",
        "context.repo.owner.toLowerCase()",
        "(work_item|fr|phase)",
        "github.rest.issues.get",
        '"work-item", "fr", "phase"',
        "closingReferences",
        "closingOwner.toLowerCase()",
        "closingRepo.toLowerCase()",
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
    script = github_script(text)
    primary = "- Work Item: owner/repo/work_item/1287\n"
    assert_binding_case(script, primary + "Closes foreign/repo#1287\n", expected_error="targets another repository")
    assert_binding_case(script, primary + "Closes owner/repo#1288\n", expected_error="must target its primary work_item")
    assert_binding_case(script, primary + "Closes owner/repo#1287\n", expected_error=None)
    print("pr binding workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
