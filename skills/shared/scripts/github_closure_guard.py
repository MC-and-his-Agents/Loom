"""Host-native guard for completed FR and Phase closures.

The evaluator consumes a complete GitHub snapshot.  It owns neither a
repository carrier nor a host write: the ``issues.closed`` workflow owns the
small reopen/comment recovery when this module returns ``reopen_required``.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCHEMA = "loom-fr-phase-close-guard/v1"
NON_COMPLETION_LABELS = {"duplicate", "invalid", "cancelled", "canceled", "superseded"}
TYPE_LABELS = {"fr": "fr", "phase": "phase", "work-item": "work_item"}
DEFERRED_LABEL = "deferred"
EXPECTED_CHILD_TYPE = {"phase": "fr", "fr": "work_item"}


def _text(value: object) -> str:
    return str(value or "").strip().casefold().replace("-", "_").replace(" ", "_")


def _labels(issue: dict[str, Any]) -> set[str]:
    labels = issue.get("labels")
    return {_text(label) for label in labels if isinstance(label, str)} if isinstance(labels, list) else set()


def _type(issue: dict[str, Any]) -> str:
    declared = _text(issue.get("type"))
    if declared in {"fr", "phase", "work_item"}:
        return declared
    inferred = {TYPE_LABELS[label.replace("_", "-")] for label in _labels(issue) if label.replace("_", "-") in TYPE_LABELS}
    return inferred.pop() if len(inferred) == 1 else "unknown"


def _reason(code: str, locator: str, message: str) -> dict[str, str]:
    return {"code": code, "locator": locator, "message": message}


def _payload(subject: int, verdict: str, summary: str, reasons: list[dict[str, str]], *, completed: bool) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA,
        "result": "block" if verdict == "reopen_required" else "pass",
        "verdict": verdict,
        "summary": summary,
        "subject": {"number": subject, "locator": f"issue:{subject}"},
        "completed": completed,
        "reasons": reasons,
        "remediation": "reconcile native children, dependencies, merged PR reviews, and check evidence before closing again"
        if verdict == "reopen_required"
        else None,
    }


def _deferred_ready(issue: dict[str, Any]) -> list[dict[str, str]]:
    body = str(issue.get("body") or "")
    number = issue.get("number", "unknown")
    reasons: list[dict[str, str]] = []
    if not re.search(r"(?im)^#{1,6}\s*activation\s+policy\s*$\n\s*\S", body):
        reasons.append(_reason("deferred_missing_activation_policy", f"issue:{number}", "deferred closure requires a non-empty Activation Policy section"))
    if not re.search(r"(?im)^\s*(?:-\s*)?successor:\s*`?(?:phase|fr|work_item):\d+`?\s*$", body):
        reasons.append(_reason("deferred_missing_typed_successor", f"issue:{number}", "deferred closure requires `Successor: phase|fr|work_item:<number>`"))
    return reasons


def _successful_check_rollup(pr: dict[str, Any]) -> bool:
    rollup = pr.get("check_rollup")
    if not isinstance(rollup, dict) or _text(rollup.get("state")) != "success" or rollup.get("contexts_complete") is not True:
        return False
    contexts = rollup.get("contexts")
    return isinstance(contexts, list) and bool(contexts)


def _approved_green_merged_pr(issue: dict[str, Any], default_branch: str) -> bool:
    prs = issue.get("merged_prs")
    if not isinstance(prs, list):
        return False
    for pr in prs:
        if not isinstance(pr, dict) or pr.get("merged") is not True or pr.get("base_ref") != default_branch:
            continue
        pr_number, head_sha, merge_commit, commit_sha = pr.get("number"), pr.get("head_sha"), pr.get("merge_commit"), pr.get("commit_sha")
        if not isinstance(pr_number, int) or not all(isinstance(value, str) and value for value in (head_sha, merge_commit, commit_sha)) or commit_sha != head_sha:
            continue
        if _text(pr.get("review_decision")) == "approved" and _successful_check_rollup(pr):
            return True
    return False


def _validate_completed(
    issue: dict[str, Any],
    issues: dict[int, dict[str, Any]],
    default_branch: str,
    reasons: list[dict[str, str]],
    visiting: set[int],
) -> None:
    number = issue.get("number")
    locator = f"issue:{number}" if isinstance(number, int) else "issue:unknown"
    if issue.get("read_complete") is not True:
        reasons.append(_reason("host_unreadable", locator, "GitHub child, dependency, PR, or comment read is incomplete"))
        return
    if _text(issue.get("state")) != "closed" or _text(issue.get("state_reason")) != "completed":
        reasons.append(_reason("child_not_completed", locator, "a completed parent requires every native child to be closed as completed"))
        return
    if not isinstance(number, int):
        reasons.append(_reason("host_unreadable", locator, "GitHub issue number is unreadable"))
        return
    if number in visiting:
        reasons.append(_reason("native_tree_cycle", locator, "native sub-issue tree must be acyclic"))
        return
    blockers = issue.get("blocked_by")
    if not isinstance(blockers, list):
        reasons.append(_reason("host_unreadable", locator, "native dependency read is incomplete"))
        return
    for blocker in blockers:
        if not isinstance(blocker, dict) or _text(blocker.get("state")) != "closed":
            reasons.append(_reason("open_native_blocker", locator, "completed closure cannot retain an open or unreadable native blocker"))
    kind = _type(issue)
    if kind == "work_item":
        if not _approved_green_merged_pr(issue, default_branch):
            reasons.append(_reason("missing_approved_merged_pr_or_green_check", locator, "Work Item needs a default-branch merged PR with an approved review and successful host check rollup"))
        return
    expected = EXPECTED_CHILD_TYPE.get(kind)
    children = issue.get("children")
    if expected is None or not isinstance(children, list) or not children:
        reasons.append(_reason("missing_native_child", locator, "completed FR/Phase requires its native child tree"))
        return
    next_visiting = {*visiting, number}
    for child_number in children:
        child = issues.get(child_number) if isinstance(child_number, int) else None
        if not isinstance(child, dict):
            reasons.append(_reason("host_unreadable", locator, "a native child cannot be read from GitHub"))
            continue
        if _type(child) != expected:
            reasons.append(_reason("invalid_native_child_type", f"issue:{child_number}", f"{kind} requires native {expected} children"))
            continue
        _validate_completed(child, issues, default_branch, reasons, next_visiting)


def evaluate_closure(snapshot: object) -> dict[str, Any]:
    """Decide whether a closed FR/Phase may remain closed from host facts only."""
    if not isinstance(snapshot, dict):
        return _payload(0, "reopen_required", "GitHub closure snapshot is unreadable.", [_reason("host_unreadable", "issue:unknown", "closure snapshot must be an object")], completed=False)
    subject = snapshot.get("subject")
    issue_rows = snapshot.get("issues")
    default_branch = snapshot.get("default_branch")
    issues = {
        row.get("number"): row
        for row in issue_rows
        if isinstance(row, dict) and isinstance(row.get("number"), int)
    } if isinstance(issue_rows, list) else {}
    subject_issue = issues.get(subject) if isinstance(subject, int) else None
    if snapshot.get("host_readable", True) is not True or not isinstance(subject_issue, dict) or not isinstance(default_branch, str) or not default_branch:
        return _payload(int(subject) if isinstance(subject, int) else 0, "reopen_required", "GitHub closure facts are unreadable.", [_reason("host_unreadable", f"issue:{subject or 'unknown'}", "subject, default branch, or native tree read is missing")], completed=False)
    kind = _type(subject_issue)
    labels = _labels(subject_issue)
    if kind not in {"fr", "phase"}:
        typed_labels = labels.intersection({"fr", "phase", "work_item"})
        if typed_labels:
            return _payload(subject, "reopen_required", "FR/Phase type labels are ambiguous.", [_reason("ambiguous_issue_type", f"issue:{subject}", "FR/Phase closure requires exactly one native type label")], completed=False)
        return _payload(subject, "not_applicable", "Closed issue is not a uniquely typed FR or Phase.", [], completed=False)
    if subject_issue.get("read_complete") is not True:
        return _payload(subject, "reopen_required", "GitHub closure facts are incomplete.", [_reason("host_unreadable", f"issue:{subject}", "GitHub read pagination or a host request was incomplete")], completed=False)
    state_reason = _text(subject_issue.get("state_reason"))
    if DEFERRED_LABEL in labels:
        if state_reason != "not_planned":
            return _payload(subject, "reopen_required", "Deferred closure must use not planned semantics.", [_reason("deferred_requires_not_planned", f"issue:{subject}", "deferred closure cannot use completed semantics")], completed=False)
        reasons = _deferred_ready(subject_issue)
        return _payload(subject, "reopen_required", "Deferred closure lacks its recovery contract.", reasons, completed=False) if reasons else _payload(subject, "allow_non_completion_close", "Deferred item remains closed as deferred, not completed.", [], completed=False)
    if state_reason == "not_planned":
        return _payload(subject, "allow_non_completion_close", "Explicit non-completion closure is not counted as completed.", [], completed=False)
    if labels.intersection(NON_COMPLETION_LABELS):
        return _payload(subject, "reopen_required", "Non-completion labels must use not planned semantics.", [_reason("non_completion_requires_not_planned", f"issue:{subject}", "non-completion labels cannot use completed semantics")], completed=False)
    reasons: list[dict[str, str]] = []
    _validate_completed(subject_issue, issues, default_branch, reasons, set())
    if reasons:
        return _payload(subject, "reopen_required", "Completed FR/Phase closure is missing required host facts.", reasons, completed=False)
    return _payload(subject, "allow_completed_close", "Native children, dependencies, merged PR reviews, and check evidence permit completed closure.", [], completed=True)


def main(argv: list[str] | None = None) -> int:
    """Evaluate one host snapshot without making a GitHub write."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True, help="GitHub host snapshot JSON")
    parser.add_argument("--output", type=Path, help="write the verdict JSON to this path")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        verdict = _payload(0, "reopen_required", "GitHub closure snapshot is unreadable.", [_reason("host_unreadable", "issue:unknown", str(exc))], completed=False)
    else:
        verdict = evaluate_closure(snapshot)
    rendered = json.dumps(verdict, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
