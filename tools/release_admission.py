#!/usr/bin/env python3
"""Fail-closed release admission from live GitHub facts and trusted acceptance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "skills" / "shared" / "scripts"))
from failure_envelope import envelope, primary_cause  # noqa: E402


SCHEMA = "loom-release-admission/v1"


def _labels(issue: dict[str, Any]) -> set[str]:
    values = issue.get("labels")
    return {
        str(value.get("name") if isinstance(value, dict) else value).strip().casefold().replace("_", "-")
        for value in values
        if isinstance(value, (dict, str))
    } if isinstance(values, list) else set()


def evaluate(snapshot: object, acceptance: object) -> dict[str, Any]:
    reasons: list[dict[str, str]] = []
    data = snapshot if isinstance(snapshot, dict) else {}
    release_issue = data.get("release_issue") if isinstance(data.get("release_issue"), dict) else {}
    repository = str(data.get("repository") or "")
    head_sha = str(data.get("head_sha") or "")
    default_branch = str(data.get("default_branch") or "")
    expected_ref = f"refs/heads/{default_branch}" if default_branch else ""

    def add(code: str, locator: str, message: str) -> None:
        reasons.append({"code": code, "locator": locator, "message": message})

    if data.get("read_complete") is not True:
        add("host_read_incomplete", "github:release-admission", "release admission requires complete paginated GitHub reads")
    if not default_branch or data.get("ref") != expected_ref or data.get("default_branch_tip") != head_sha:
        add("release_head_not_current", f"github:{repository or 'unknown'}/default-branch", "release must run from the current default-branch tip")
    issue_number = release_issue.get("number")
    issue_locator = f"issue:{issue_number or 'unknown'}"
    if (
        not isinstance(issue_number, int)
        or str(release_issue.get("state") or "").casefold() != "open"
        or "work-item" not in _labels(release_issue)
        or not isinstance(release_issue.get("milestone_number"), int)
    ):
        add("release_work_item_invalid", issue_locator, "release admission requires one open work-item in a milestone")
    blockers = release_issue.get("blocked_by")
    if (
        not isinstance(blockers, list)
        or any(
            str(row.get("state") or "").casefold() != "closed"
            or str(row.get("state_reason") or "").casefold() != "completed"
            for row in blockers
            if isinstance(row, dict)
        )
        or any(not isinstance(row, dict) for row in blockers or [])
    ):
        add("release_dependency_open", issue_locator, "every native release dependency must be readable and closed")
    milestone_issues = data.get("milestone_issues")
    if not isinstance(milestone_issues, list):
        add("milestone_read_incomplete", issue_locator, "milestone issue state is unreadable")
    else:
        release_rows = [issue for issue in milestone_issues if isinstance(issue, dict) and issue.get("number") == issue_number]
        if len(release_rows) != 1:
            add("milestone_read_incomplete", issue_locator, "milestone readback must contain the release Work Item exactly once")
        for issue in milestone_issues:
            if not isinstance(issue, dict):
                add("milestone_read_incomplete", issue_locator, "milestone issue state is unreadable")
                break
            number = issue.get("number")
            if number == issue_number:
                continue
            labels = _labels(issue)
            if "fr" in labels or "work-item" in labels:
                if str(issue.get("state") or "").casefold() != "closed" or str(issue.get("state_reason") or "").casefold() != "completed":
                    add("release_scope_incomplete", f"issue:{number}", "every milestone FR and release-critical Work Item must be completed")
                    break

    accepted = acceptance if isinstance(acceptance, dict) else {}
    product = accepted.get("product_acceptance") if isinstance(accepted.get("product_acceptance"), dict) else {}
    host = accepted.get("host_facts") if isinstance(accepted.get("host_facts"), dict) else {}
    expected_story = f"{repository}/issue/{issue_number}" if repository and isinstance(issue_number, int) else ""
    marker_artifact_id = data.get("acceptance_artifact_id")
    if not isinstance(marker_artifact_id, int) or marker_artifact_id <= 0:
        add("release_acceptance_locator_invalid", issue_locator, "release Work Item must expose exactly one workflow-owned acceptance artifact locator")
    if (
        accepted.get("result") != "pass"
        or product.get("verdict") != "passed"
        or product.get("trusted") is not True
        or product.get("evidence_consumed") is not True
        or product.get("owns_lifecycle_closure") is not False
        or accepted.get("story_locator") != expected_story
        or host.get("source") != "github"
        or host.get("read_complete") is not True
        or host.get("run_head_sha") != head_sha
        or host.get("artifact_id") != marker_artifact_id
    ):
        add("release_acceptance_untrusted", expected_story or issue_locator, "release requires one trusted passed umbrella acceptance bound to this release head")

    if reasons:
        first = reasons[0]
        acceptance_failure = first["code"] in {"release_acceptance_locator_invalid", "release_acceptance_untrusted"}
        cause = primary_cause(
            cause_id=first["code"],
            failure_domain="product_acceptance" if acceptance_failure else "host_service" if first["code"] in {"host_read_incomplete", "milestone_read_incomplete"} else "governance_metadata",
            code=first["code"],
            locator=first["locator"],
            summary=first["message"],
            owner="github" if first["code"] in {"host_read_incomplete", "milestone_read_incomplete"} else "operator",
            retryable=first["code"] in {"host_read_incomplete", "milestone_read_incomplete"},
            details={"reasons": reasons},
            remediation_command="loom acceptance resolve --story <owner/repo/issue/id> --artifact-id <id> --json" if acceptance_failure else "loom help --json",
        )
        return {
            "schema_version": SCHEMA,
            "result": "block",
            "summary": first["message"],
            "release_issue": issue_number,
            "head_sha": head_sha or None,
            "reasons": reasons,
            "failure_envelope": envelope(cause),
            "mutates": False,
        }
    return {
        "schema_version": SCHEMA,
        "result": "pass",
        "summary": "Live release scope and trusted umbrella acceptance admit publication.",
        "release_issue": issue_number,
        "head_sha": head_sha,
        "acceptance_artifact_id": host.get("artifact_id"),
        "reasons": [],
        "failure_envelope": None,
        "mutates": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        acceptance = json.loads(args.acceptance.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        snapshot, acceptance = {"read_complete": False, "read_error": str(exc)}, {}
    result = evaluate(snapshot, acceptance)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
