"""Host-native guard for completed FR and Phase closures.

The evaluator consumes a complete GitHub snapshot.  It owns neither a
repository carrier nor a host write: the ``issues.closed`` workflow owns the
small reopen/comment recovery when this module returns ``reopen_required``.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from failure_envelope import envelope, primary_cause
from github_host import HOST_ATTESTATION_WORKFLOW_PATH, github_pr_attestation_readback
from product_acceptance import resolve_acceptance


SCHEMA = "loom-fr-phase-close-guard/v1"
NON_COMPLETION_LABELS = {"duplicate", "invalid", "cancelled", "canceled", "superseded"}
TYPE_LABELS = {"fr": "fr", "phase": "phase", "work-item": "work_item"}
DEFERRED_LABEL = "deferred"
EXPECTED_CHILD_TYPE = {"phase": "fr", "fr": "work_item"}
WAIVER_POLICY_LABEL = "product_acceptance_waiver_allowed"
SINGLE_MAINTAINER_LABEL = "review_policy_single_maintainer"
PRODUCT_ARTIFACT_RE = re.compile(r"<!--\s*loom:product-acceptance-artifact\s+id:(\d+)\s*-->", re.IGNORECASE)
ATTESTATION_ARTIFACT_RE = re.compile(r"<!--\s*loom:host-attestation-artifact\s+pr:(\d+)\s+head:([0-9a-f]{40})\s+id:(\d+)\s*-->", re.IGNORECASE)
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DELIVERY_CHECK_CONTEXTS = frozenset({"py-compile", "loom-delivery-gate", "loom-pr-merge-gate"})


def _text(value: object) -> str:
    return str(value or "").strip().casefold().replace("-", "_").replace(" ", "_")


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


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
    remediation = "reconcile native children, dependencies, trusted product acceptance, review attestation, and check evidence before closing again" if verdict == "reopen_required" else None
    failure = None
    if verdict == "reopen_required":
        acceptance_failure = any(reason.get("code", "").startswith("product_acceptance") for reason in reasons)
        cause = primary_cause(
            cause_id="fr_phase_product_acceptance_invalid" if acceptance_failure else "fr_phase_closure_invalid",
            failure_domain="product_acceptance" if acceptance_failure else "governance_metadata",
            code="closure_invalid",
            locator=f"issue:{subject}",
            summary=summary,
            owner="operator",
            retryable=True,
            details={"reasons": reasons},
            remediation_command=remediation,
        )
        failure = envelope(cause)
    return {
        "schema_version": SCHEMA,
        "result": "block" if verdict == "reopen_required" else "pass",
        "verdict": verdict,
        "summary": summary,
        "subject": {"number": subject, "locator": f"issue:{subject}"},
        "completed": completed,
        "reasons": reasons,
        "remediation": remediation,
        "failure_envelope": failure,
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
    merged_at = _parse_time(pr.get("merged_at"))
    if not isinstance(rollup, dict) or rollup.get("contexts_complete") is not True or merged_at is None:
        return False
    contexts = rollup.get("contexts")
    if not isinstance(contexts, list):
        return False
    latest: dict[str, tuple[datetime, int, dict[str, Any]]] = {}
    for index, context in enumerate(contexts):
        if not isinstance(context, dict):
            return False
        name = str(context.get("name") or "").strip()
        if name not in DELIVERY_CHECK_CONTEXTS:
            continue
        timestamp = (
            _parse_time(context.get("completed_at"))
            or _parse_time(context.get("started_at"))
            or _parse_time(context.get("created_at"))
            or datetime.min.replace(tzinfo=timezone.utc)
        )
        if timestamp > merged_at:
            continue
        current = latest.get(name)
        if current is None or (timestamp, index) > (current[0], current[1]):
            latest[name] = (timestamp, index, context)
    if not latest:
        return False
    for _timestamp, _index, context in latest.values():
        kind = _text(context.get("type"))
        if kind == "checkrun":
            if _text(context.get("status")) != "completed" or _text(context.get("conclusion")) not in {"success", "neutral", "skipped"}:
                return False
        elif kind == "statuscontext":
            if _text(context.get("state")) != "success":
                return False
        else:
            return False
    return True


def _comment_marker(bodies: object, pattern: re.Pattern[str], *, pr_number: int | None = None) -> tuple[int | None, list[str]]:
    if not isinstance(bodies, list) or any(not isinstance(body, str) for body in bodies):
        return None, ["host comment locator read is incomplete"]
    values: set[int] = set()
    for body in bodies:
        for match in pattern.finditer(body):
            if pr_number is None or int(match.group(1)) == pr_number:
                values.add(int(match.group(1 if pr_number is None else 2)))
    if len(values) != 1:
        return None, ["exactly one host artifact locator is required"]
    return values.pop(), []


def _attestation_marker(comments: object, pr_number: int, head_sha: str) -> tuple[int | None, list[str]]:
    if not isinstance(comments, list):
        return None, ["host attestation comment read is incomplete"]
    matches: list[int] = []
    for comment in comments:
        if not isinstance(comment, dict) or not isinstance(comment.get("body"), str):
            return None, ["host attestation comment identity is unreadable"]
        for match in ATTESTATION_ARTIFACT_RE.finditer(comment["body"]):
            if int(match.group(1)) == pr_number and match.group(2).lower() == head_sha.lower():
                matches.append(int(match.group(3)))
    if len(matches) != 1:
        return None, ["exactly one explicit single-maintainer attestation comment must bind the PR and current head"]
    return matches[0], []


def resolve_host_facts(
    snapshot: dict[str, Any],
    root: Path,
    *,
    acceptance_resolver: Any = resolve_acceptance,
    attestation_reader: Any = github_pr_attestation_readback,
) -> dict[str, Any]:
    """Resolve artifact locators through authenticated host readers before evaluation."""
    repository = snapshot.get("repository")
    subject = snapshot.get("subject")
    issues = snapshot.get("issues")
    if not isinstance(repository, str) or repository.count("/") != 1 or not isinstance(subject, int) or not isinstance(issues, list):
        snapshot["host_readable"] = False
        return snapshot
    owner, repo = repository.split("/", 1)
    by_number = {row.get("number"): row for row in issues if isinstance(row, dict) and isinstance(row.get("number"), int)}
    subject_issue = by_number.get(subject)
    if not isinstance(subject_issue, dict) or subject_issue.get("comments_complete") is not True:
        snapshot["host_readable"] = False
        return snapshot
    artifact_id, marker_errors = _comment_marker(subject_issue.get("comment_bodies"), PRODUCT_ARTIFACT_RE)
    if marker_errors or artifact_id is None:
        snapshot["product_acceptance"] = None
    else:
        snapshot["product_acceptance"] = acceptance_resolver(root, f"{owner}/{repo}/issue/{subject}", artifact_id)
    for issue in by_number.values():
        if _type(issue) != "work_item" or SINGLE_MAINTAINER_LABEL not in _labels(issue):
            continue
        if issue.get("comments_complete") is not True:
            issue["read_complete"] = False
            continue
        prs = issue.get("merged_prs") if isinstance(issue.get("merged_prs"), list) else []
        for pr in prs:
            if not isinstance(pr, dict) or not isinstance(pr.get("number"), int):
                continue
            head_sha = pr.get("head_sha")
            if not isinstance(head_sha, str):
                pr["host_attestation_errors"] = ["merged PR head is unreadable"]
                continue
            attestation_id, attestation_errors = _attestation_marker(issue.get("comments"), pr["number"], head_sha)
            if attestation_errors or attestation_id is None:
                pr["host_attestation_errors"] = attestation_errors
                continue
            facts, errors = attestation_reader(
                root,
                owner,
                repo,
                pr["number"],
                attestation_id,
                work_item=issue["number"],
                allow_merged=True,
                review_policy="single_maintainer",
            )
            pr["host_attestation"] = facts
            pr["host_attestation_errors"] = errors
    snapshot["host_facts_resolved"] = True
    return snapshot


def _trusted_product_acceptance(snapshot: dict[str, Any], subject: int, labels: set[str], reasons: list[dict[str, str]], *, host_resolved: bool) -> None:
    result = snapshot.get("product_acceptance")
    locator = f"issue:{subject}"
    if not host_resolved:
        reasons.append(_reason("product_acceptance_untrusted", locator, "completed closure must resolve host facts in the trusted workflow process"))
        return
    if not isinstance(result, dict):
        reasons.append(_reason("product_acceptance_missing", locator, "completed closure requires a host-resolved product acceptance verdict"))
        return
    acceptance = result.get("product_acceptance") if isinstance(result.get("product_acceptance"), dict) else {}
    host = result.get("host_facts") if isinstance(result.get("host_facts"), dict) else {}
    verdict = _text(acceptance.get("verdict"))
    expected_story = f"{snapshot.get('repository')}/issue/{subject}"
    if (
        result.get("result") != "pass"
        or acceptance.get("trusted") is not True
        or acceptance.get("owns_lifecycle_closure") is not False
        or result.get("story_locator") != expected_story
        or host.get("source") != "github"
        or host.get("read_complete") is not True
        or host.get("story_locator") != expected_story
    ):
        reasons.append(_reason("product_acceptance_untrusted", locator, "product acceptance is not bound to authenticated GitHub host facts for this FR/Phase"))
        return
    rationale = str(result.get("rationale") or "").strip()
    if verdict == "passed" and acceptance.get("evidence_consumed") is True:
        return
    if verdict == "not_required" and rationale:
        return
    if verdict == "waived" and rationale and WAIVER_POLICY_LABEL in labels:
        return
    reasons.append(_reason("product_acceptance_not_satisfied", locator, "completed closure requires passed, reasoned not_required, or a policy-allowed reasoned waiver"))


def _valid_single_maintainer_attestation(pr: dict[str, Any]) -> bool:
    facts = pr.get("host_attestation")
    if not isinstance(facts, dict) or pr.get("host_attestation_errors") not in (None, []):
        return False
    policy = facts.get("review_policy") if isinstance(facts.get("review_policy"), dict) else {}
    maintainer = policy.get("maintainer") if isinstance(policy.get("maintainer"), dict) else {}
    attested_pr = facts.get("pr") if isinstance(facts.get("pr"), dict) else {}
    tree = facts.get("semantic_tree") if isinstance(facts.get("semantic_tree"), dict) else {}
    artifact = facts.get("artifact") if isinstance(facts.get("artifact"), dict) else {}
    run = facts.get("workflow_run") if isinstance(facts.get("workflow_run"), dict) else {}
    review = facts.get("review") if isinstance(facts.get("review"), dict) else {}
    return (
        facts.get("source") == "github"
        and facts.get("read_complete") is True
        and policy.get("mode") == "single_maintainer"
        and policy.get("verified") is True
        and policy.get("assertion_verified") is True
        and policy.get("maintainer_count") == 1
        and isinstance(maintainer.get("id"), int)
        and not isinstance(maintainer.get("id"), bool)
        and isinstance(maintainer.get("login"), str)
        and bool(maintainer.get("login"))
        and all(isinstance(policy.get(field), str) and policy[field] for field in ("run_started_at", "run_updated_at", "artifact_created_at"))
        and attested_pr.get("number") == pr.get("number")
        and attested_pr.get("head_sha") == pr.get("head_sha")
        and attested_pr.get("base_ref") == pr.get("base_ref")
        and attested_pr.get("merge_commit_sha") == pr.get("merge_commit")
        and isinstance(tree.get("semantic_digest"), str)
        and SHA256_RE.fullmatch(tree["semantic_digest"]) is not None
        and tree.get("commit_sha") == pr.get("head_sha")
        and isinstance(artifact.get("digest"), str)
        and SHA256_RE.fullmatch(artifact["digest"]) is not None
        and artifact.get("name") == f"loom-host-attestation-{pr.get('number')}"
        and isinstance(artifact.get("run_id"), int)
        and not isinstance(artifact.get("run_id"), bool)
        and run.get("id") == artifact.get("run_id")
        and run.get("event") in {"pull_request_target", "workflow_dispatch"}
        and run.get("binding") in {"pull_request_target", "workflow_dispatch_reattest"}
        and (run.get("binding") == "workflow_dispatch_reattest" or run.get("head_sha") == pr.get("head_sha"))
        and run.get("path") == HOST_ATTESTATION_WORKFLOW_PATH
        and _text(run.get("status")) == "completed"
        and _text(run.get("conclusion")) == "success"
        and review.get("state") == "SINGLE_MAINTAINER_ATTESTED"
        and review.get("commit_id") == pr.get("head_sha")
    )


def _reviewed_green_merged_pr(issue: dict[str, Any], default_branch: str, review_policy: dict[str, Any]) -> bool:
    prs = issue.get("merged_prs")
    if not isinstance(prs, list):
        return False
    for pr in prs:
        if not isinstance(pr, dict) or pr.get("merged") is not True or pr.get("base_ref") != default_branch:
            continue
        pr_number, head_sha, merge_commit, commit_sha = pr.get("number"), pr.get("head_sha"), pr.get("merge_commit"), pr.get("commit_sha")
        if not isinstance(pr_number, int) or not all(isinstance(value, str) and value for value in (head_sha, merge_commit, commit_sha)) or commit_sha != head_sha:
            continue
        required_approvals = review_policy.get("required_approving_review_count")
        review_ready = required_approvals == 0 or _text(pr.get("review_decision")) == "approved"
        if SINGLE_MAINTAINER_LABEL in _labels(issue):
            review_ready = _valid_single_maintainer_attestation(pr)
        if review_ready and _successful_check_rollup(pr):
            return True
    return False


def _validate_completed(
    issue: dict[str, Any],
    issues: dict[int, dict[str, Any]],
    default_branch: str,
    review_policy: dict[str, Any],
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
        if not _reviewed_green_merged_pr(issue, default_branch, review_policy):
            reasons.append(_reason("missing_reviewed_merged_pr_or_green_check", locator, "Work Item needs a default-branch merged PR satisfying the host review policy and successful host check rollup"))
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
        _validate_completed(child, issues, default_branch, review_policy, reasons, next_visiting)


def evaluate_closure(snapshot: object, *, host_resolved: bool = False) -> dict[str, Any]:
    """Decide whether a closed FR/Phase may remain closed from host facts only."""
    if not isinstance(snapshot, dict):
        return _payload(0, "reopen_required", "GitHub closure snapshot is unreadable.", [_reason("host_unreadable", "issue:unknown", "closure snapshot must be an object")], completed=False)
    subject = snapshot.get("subject")
    issue_rows = snapshot.get("issues")
    default_branch = snapshot.get("default_branch")
    review_policy = snapshot.get("review_policy")
    issues = {
        row.get("number"): row
        for row in issue_rows
        if isinstance(row, dict) and isinstance(row.get("number"), int)
    } if isinstance(issue_rows, list) else {}
    subject_issue = issues.get(subject) if isinstance(subject, int) else None
    if (
        snapshot.get("host_readable", True) is not True
        or not isinstance(subject_issue, dict)
        or not isinstance(default_branch, str)
        or not default_branch
    ):
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
    if (
        not isinstance(review_policy, dict)
        or review_policy.get("read_complete") is not True
        or not isinstance(review_policy.get("required_approving_review_count"), int)
        or isinstance(review_policy.get("required_approving_review_count"), bool)
        or review_policy["required_approving_review_count"] < 0
    ):
        return _payload(subject, "reopen_required", "GitHub review policy is unreadable.", [_reason("host_unreadable", f"issue:{subject}", "required approving review policy read is missing")], completed=False)
    reasons: list[dict[str, str]] = []
    _trusted_product_acceptance(snapshot, subject, labels, reasons, host_resolved=host_resolved)
    _validate_completed(subject_issue, issues, default_branch, review_policy, reasons, set())
    if reasons:
        return _payload(subject, "reopen_required", "Completed FR/Phase closure is missing required host facts.", reasons, completed=False)
    return _payload(subject, "allow_completed_close", "Trusted product acceptance, native children, dependencies, review policy, and check evidence permit completed closure.", [], completed=True)


def main(argv: list[str] | None = None) -> int:
    """Evaluate one host snapshot without making a GitHub write."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True, help="GitHub host snapshot JSON")
    parser.add_argument("--output", type=Path, help="write the verdict JSON to this path")
    parser.add_argument("--resolve-host-facts", action="store_true", help="resolve acceptance and single-maintainer artifact locators through authenticated GitHub readback")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        verdict = _payload(0, "reopen_required", "GitHub closure snapshot is unreadable.", [_reason("host_unreadable", "issue:unknown", str(exc))], completed=False)
    else:
        if args.resolve_host_facts and isinstance(snapshot, dict):
            try:
                snapshot = resolve_host_facts(snapshot, Path.cwd())
            except Exception as exc:  # fail closed at the host boundary
                snapshot["host_readable"] = False
                snapshot["host_resolution_error"] = str(exc)
        verdict = evaluate_closure(snapshot, host_resolved=bool(args.resolve_host_facts and isinstance(snapshot, dict) and snapshot.get("host_facts_resolved") is True))
    rendered = json.dumps(verdict, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
