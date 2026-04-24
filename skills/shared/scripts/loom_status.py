#!/usr/bin/env python3
"""Unified Loom status read surface for item, spec/review gates, and merge readiness."""

from __future__ import annotations

import argparse
from pathlib import Path

from governance_surface import build_governance_surface
from loom_flow import (
    checkpoint_payload,
    detect_github_repo,
    emit,
    gh_json,
    implementation_review_status_payload,
    load_context,
    runtime_state_payload,
    spec_review_gate_payload,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read unified Loom item/spec/review/merge status.")
    parser.add_argument("--target", required=True, help="Target repository root")
    parser.add_argument("--item", help="Expected current item id")
    parser.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    parser.add_argument("--issue", type=int, help="Optional GitHub issue number to include")
    parser.add_argument("--pr", type=int, help="Optional GitHub pull request number to include")
    parser.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    parser.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    return parser.parse_args(argv)


def github_status_payload(
    root: Path,
    *,
    issue_number: int | None,
    pr_number: int | None,
    owner: str | None,
    repo_name: str | None,
) -> tuple[dict[str, object], list[str]]:
    detected_owner, detected_repo = detect_github_repo(root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    payload: dict[str, object] = {
        "repository": f"{owner}/{repo_name}" if owner and repo_name else None,
        "issue": None,
        "pr": None,
    }
    errors: list[str] = []
    if not owner or not repo_name:
        if issue_number is not None or pr_number is not None:
            errors.append("GitHub repository could not be detected from origin")
        return payload, errors

    repo_slug = f"{owner}/{repo_name}"
    if issue_number is not None:
        issue_payload, issue_errors = gh_json(
            root,
            ["issue", "view", str(issue_number), "--repo", repo_slug, "--json", "number,state,title,url"],
        )
        if issue_errors:
            errors.extend([f"issue #{issue_number}: {message}" for message in issue_errors])
        else:
            payload["issue"] = issue_payload
    if pr_number is not None:
        pr_payload, pr_errors = gh_json(
            root,
            [
                "pr",
                "view",
                str(pr_number),
                "--repo",
                repo_slug,
                "--json",
                "number,state,title,url,isDraft,mergeStateStatus,headRefName,baseRefName",
            ],
        )
        if pr_errors:
            errors.extend([f"pr #{pr_number}: {message}" for message in pr_errors])
        else:
            payload["pr"] = pr_payload
    return payload, errors


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target_root = Path(args.target).expanduser().resolve()
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            {
                "command": "status",
                "result": "block",
                "summary": "status is blocked because the Loom runtime state is inconsistent.",
                "missing_inputs": runtime_state["missing_inputs"],
                "fallback_to": runtime_state["fallback_to"],
                "runtime_state": runtime_state,
            }
        )

    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "status",
                "result": "block",
                "summary": "status could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "runtime_state": runtime_state,
            }
        )

    spec_review = spec_review_gate_payload(context)
    review = implementation_review_status_payload(context)
    merge_ready = checkpoint_payload("merge", context)
    governance_surface = build_governance_surface(target_root)
    github_status, github_errors = github_status_payload(
        target_root,
        issue_number=args.issue,
        pr_number=args.pr,
        owner=args.owner,
        repo_name=args.repo_name,
    )

    missing_inputs: list[str] = []
    for section in (spec_review, review, merge_ready):
        for message in section.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(message)
    for message in github_errors:
        if message not in missing_inputs:
            missing_inputs.append(message)

    result = "pass" if not missing_inputs else "block"
    summary = (
        "status surface shows the current item, spec gate, implementation review, and merge checkpoint in one read."
        if result == "pass"
        else "status surface is readable, but one or more governance gates are still blocking or stale."
    )
    return emit(
        {
            "command": "status",
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": "admission" if missing_inputs else None,
            "runtime_state": runtime_state,
            "item": {
                "id": context["item_id"],
                "goal": context["goal"],
                "scope": context["scope"],
                "execution_path": context["execution_path"],
                "workspace_entry": context["workspace_entry"],
                "recovery_entry": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
                "review_entry": context["review_entry"],
                "validation_entry": context["validation_entry"],
            },
            "current_checkpoint": {
                "raw": context["current_checkpoint_raw"],
                "normalized": context["current_checkpoint"],
            },
            "recovery": {
                "current_stop": context["current_stop"],
                "next_step": context["next_step"],
                "blockers": context["blockers"],
                "latest_validation_summary": context["latest_validation_summary"],
                "recovery_boundary": context["recovery_boundary"],
                "current_lane": context["current_lane"],
            },
            "spec_review": spec_review,
            "review": review,
            "merge_ready": merge_ready,
            "governance_surface": governance_surface,
            "github": github_status,
        }
    )


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
