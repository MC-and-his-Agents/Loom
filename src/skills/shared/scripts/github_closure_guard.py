"""Host-native guard for completed FR and Phase closures.

The evaluator consumes a complete GitHub snapshot.  It owns neither a
repository carrier nor a host write: the ``issues.closed`` workflow owns the
small reopen/comment recovery when this module returns ``reopen_required``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from failure_envelope import envelope, primary_cause
from product_acceptance import resolve_acceptance


SCHEMA = "loom-fr-phase-close-guard/v1"
NON_COMPLETION_LABELS = {"duplicate", "invalid", "cancelled", "canceled", "superseded"}
TYPE_LABELS = {"fr": "fr", "phase": "phase", "product-problem": "product_problem", "work-item": "work_item"}
DEFERRED_LABEL = "deferred"
EXPECTED_CHILD_TYPE = {"product_problem": "fr", "fr": "work_item"}
PHASE_CHILD_TYPES = {"product_problem", "fr", "work_item"}
WAIVER_POLICY_LABEL = "product_acceptance_waiver_allowed"
PRODUCT_ARTIFACT_RE = re.compile(r"<!--\s*loom:product-acceptance-artifact\s+id:(\d+)\s*-->", re.IGNORECASE)
HOST_ACTION_ARTIFACT_RE = re.compile(r"<!--\s*loom:host-action-attestation\s+(\{.*?\})\s*-->", re.IGNORECASE | re.DOTALL)
PR_METADATA_RE = re.compile(r"<!--\s*loom:repo-pr-metadata\s*(\{.*?\})\s*-->", re.IGNORECASE | re.DOTALL)
HOST_ONLY_DELIVERY_LABEL = "host_only_delivery"
TRUSTED_AUTHOR_ASSOCIATIONS = {"owner", "member", "collaborator"}
DELIVERY_CHECK_CONTEXTS = frozenset({"py-compile", "loom-delivery-gate", "loom-pr-merge-gate"})
V032_RUNTIME_EOL_EXCEPTION = {
    "repository": "MC-and-his-Agents/Loom",
    "pr": 2127,
    "anchor_issue": 2125,
    "covered_issues": (2125, 2126),
    "head_sha": "78b79de68d963a0dca14823a050bd09838403a45",
    "merge_commit": "37a6fa55a6f0819d9f9a93f1bc102445c99b38db",
    "pr_body_sha256": "e6164372caa7d0f2de60b424336e913019576db6681799288bfeedbf709d86c2",
    "authorization_comment_id": 4963151713,
    "authorization_comment_sha256": "486ca70bea8f4fe51eee2523629c907fdce82bdea57a7cc49b4f8c9bd29d37d9",
    "authorization_user_id": 9820018,
    "authorization_login": "mcontheway",
    "failed_run_id": 29288032023,
}
DELIVERY_FAILURE_CODES = {
    "delivery_relation_invalid",
    "delivery_binding_invalid",
    "bootstrap_authorization_invalid",
    "bootstrap_run_mismatch",
}


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
    if declared in {"fr", "phase", "product_problem", "work_item"}:
        return declared
    inferred = {TYPE_LABELS[label.replace("_", "-")] for label in _labels(issue) if label.replace("_", "-") in TYPE_LABELS}
    return inferred.pop() if len(inferred) == 1 else "unknown"


def _reason(code: str, locator: str, message: str) -> dict[str, str]:
    return {"code": code, "locator": locator, "message": message}


def _payload(subject: int, verdict: str, summary: str, reasons: list[dict[str, str]], *, completed: bool) -> dict[str, Any]:
    remediation = "reconcile native children, dependencies, trusted product acceptance, merged delivery, and check evidence before closing again" if verdict == "reopen_required" else None
    failure = None
    if verdict == "reopen_required":
        acceptance_failure = any(reason.get("code", "").startswith("product_acceptance") for reason in reasons)
        delivery_reason = next((reason for reason in reasons if reason.get("code") in DELIVERY_FAILURE_CODES or reason.get("code") == "missing_delivery_attestation"), None)
        delivery_failure = not acceptance_failure and delivery_reason is not None
        failure_code = str(delivery_reason.get("code")) if delivery_reason else "closure_invalid"
        cause = primary_cause(
            cause_id="fr_phase_product_acceptance_invalid" if acceptance_failure else "fr_phase_delivery_attestation_invalid" if delivery_failure else "fr_phase_closure_invalid",
            failure_domain="product_acceptance" if acceptance_failure else "governance_metadata",
            code="product_acceptance_invalid" if acceptance_failure else failure_code,
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


def resolve_host_facts(
    snapshot: dict[str, Any],
    root: Path,
    *,
    acceptance_resolver: Any = resolve_acceptance,
) -> dict[str, Any]:
    """Resolve artifact locators through authenticated host readers before evaluation."""
    repository = str(snapshot.get("repository") or "")
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


def _green_merged_pr(issue: dict[str, Any], default_branch: str) -> bool:
    prs = issue.get("merged_prs")
    if not isinstance(prs, list):
        return False
    for pr in prs:
        if not isinstance(pr, dict) or pr.get("merged") is not True or pr.get("base_ref") != default_branch:
            continue
        pr_number, head_sha, merge_commit, commit_sha = pr.get("number"), pr.get("head_sha"), pr.get("merge_commit"), pr.get("commit_sha")
        if not isinstance(pr_number, int) or not all(isinstance(value, str) and value for value in (head_sha, merge_commit, commit_sha)) or commit_sha != head_sha:
            continue
        if _successful_check_rollup(pr):
            return True
    return False


def _pr_metadata_fields(body: object, repository: str) -> dict[str, Any] | None:
    if not isinstance(body, str):
        return None
    matches = list(PR_METADATA_RE.finditer(body))
    if len(matches) != 1:
        return None
    try:
        payload = json.loads(matches[0].group(1))
    except json.JSONDecodeError:
        return None
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != "loom-repo-pr-metadata/v1"
        or payload.get("metadata_contract_id") != "loom-governance-intensity"
        or payload.get("surface") != "merge_ready"
        or payload.get("parser_version") != "loom-pr-metadata-parser/v2"
    ):
        return None
    fields = payload.get("fields")
    if not isinstance(fields, dict):
        return None
    anchor = fields.get("anchor_issue")
    covered = fields.get("covered_issues")
    if (
        not isinstance(anchor, int)
        or isinstance(anchor, bool)
        or not isinstance(covered, list)
        or any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in covered)
        or len(set(covered)) != len(covered)
        or anchor not in covered
        or fields.get("work_item_locator") != f"{repository}/work_item/{anchor}"
    ):
        return None
    return fields


def _v032_runtime_eol_delivery_exception(
    issue: dict[str, Any],
    repository: str,
    default_branch: str,
) -> tuple[bool, str | None]:
    """Consume one frozen historical exception without creating a reusable waiver."""
    expected = V032_RUNTIME_EOL_EXCEPTION
    number = issue.get("number")
    if repository != expected["repository"] or number not in expected["covered_issues"]:
        return False, None
    pulls = issue.get("historical_delivery_prs")
    if not isinstance(pulls, list) or len(pulls) != 1 or not isinstance(pulls[0], dict):
        return True, "delivery_binding_invalid"
    pr = pulls[0]
    body = pr.get("body")
    created_at = _parse_time(pr.get("created_at"))
    edited_at = _parse_time(pr.get("last_edited_at"))
    merged_at = _parse_time(pr.get("merged_at"))
    if (
        pr.get("number") != expected["pr"]
        or pr.get("merged") is not True
        or pr.get("base_ref") != default_branch
        or pr.get("head_repository") != expected["repository"]
        or pr.get("head_sha") != expected["head_sha"]
        or pr.get("commit_sha") != expected["head_sha"]
        or pr.get("merge_commit") != expected["merge_commit"]
        or not isinstance(body, str)
        or hashlib.sha256(body.encode("utf-8")).hexdigest() != expected["pr_body_sha256"]
        or created_at is None
        or edited_at is None
        or merged_at is None
        or created_at > edited_at
        or edited_at > merged_at
    ):
        return True, "delivery_binding_invalid"
    fields = _pr_metadata_fields(body, repository)
    if (
        fields is None
        or fields.get("anchor_issue") != expected["anchor_issue"]
        or tuple(fields.get("covered_issues", ())) != expected["covered_issues"]
        or pr.get("closing_issues_complete") is not True
        or pr.get("closing_issues") != [{"number": expected["anchor_issue"], "repository": expected["repository"]}]
    ):
        return True, "delivery_relation_invalid"
    comment = pr.get("authorization_comment")
    user = comment.get("user") if isinstance(comment, dict) and isinstance(comment.get("user"), dict) else {}
    comment_body = comment.get("body") if isinstance(comment, dict) else None
    comment_created_at = _parse_time(comment.get("created_at")) if isinstance(comment, dict) else None
    comment_updated_at = _parse_time(comment.get("updated_at")) if isinstance(comment, dict) else None
    if (
        not isinstance(comment, dict)
        or comment.get("id") != expected["authorization_comment_id"]
        or not isinstance(comment_body, str)
        or hashlib.sha256(comment_body.encode("utf-8")).hexdigest() != expected["authorization_comment_sha256"]
        or user.get("id") != expected["authorization_user_id"]
        or user.get("login") != expected["authorization_login"]
        or _text(comment.get("author_association")) not in {"owner", "member"}
        or comment_created_at is None
        or comment_updated_at is None
        or comment_created_at != comment_updated_at
        or comment_updated_at > merged_at
    ):
        return True, "bootstrap_authorization_invalid"
    run = pr.get("failed_run")
    run_created_at = _parse_time(run.get("created_at")) if isinstance(run, dict) else None
    run_updated_at = _parse_time(run.get("updated_at")) if isinstance(run, dict) else None
    if (
        not isinstance(run, dict)
        or run.get("id") != expected["failed_run_id"]
        or run.get("head_sha") != expected["head_sha"]
        or run.get("head_branch") != pr.get("head_ref")
        or run.get("head_repository") != expected["repository"]
        or _text(run.get("event")) != "pull_request_target"
        or _text(run.get("status")) != "completed"
        or _text(run.get("conclusion")) != "failure"
        or run.get("workflow_path") != ".github/workflows/loom-delivery-gate.yml"
        or run.get("html_url") != f"https://github.com/{expected['repository']}/actions/runs/{expected['failed_run_id']}"
        or run_created_at is None
        or run_updated_at is None
        or run_created_at < edited_at
        or run_updated_at < run_created_at
        or comment_created_at < run_updated_at
        or run_updated_at > merged_at
    ):
        return True, "bootstrap_run_mismatch"
    rollup = pr.get("check_rollup")
    contexts = rollup.get("contexts") if isinstance(rollup, dict) else None
    delivery_gate = [
        context for context in contexts
        if isinstance(context, dict) and context.get("name") == "loom-delivery-gate"
    ] if isinstance(contexts, list) else []
    gate_started_at = _parse_time(delivery_gate[0].get("started_at")) if len(delivery_gate) == 1 else None
    gate_completed_at = _parse_time(delivery_gate[0].get("completed_at")) if len(delivery_gate) == 1 else None
    run_details_prefix = f"https://github.com/{expected['repository']}/actions/runs/{expected['failed_run_id']}/"
    if (
        not isinstance(rollup, dict)
        or rollup.get("contexts_complete") is not True
        or len(delivery_gate) != 1
        or _text(delivery_gate[0].get("type")) != "checkrun"
        or _text(delivery_gate[0].get("status")) != "completed"
        or _text(delivery_gate[0].get("conclusion")) != "failure"
        or not isinstance(delivery_gate[0].get("details_url"), str)
        or not delivery_gate[0]["details_url"].startswith(run_details_prefix)
        or gate_started_at is None
        or gate_completed_at is None
        or gate_started_at < run_created_at
        or gate_completed_at < gate_started_at
        or gate_completed_at > run_updated_at
    ):
        return True, "bootstrap_run_mismatch"
    return True, None


def _host_action_attestation_errors(issue: dict[str, Any], repository: str, actor: dict[str, Any]) -> list[str]:
    comments = issue.get("comments")
    if issue.get("comments_complete") is not True or not isinstance(comments, list):
        return ["comments_unreadable"]
    matches: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for comment in comments:
        if not isinstance(comment, dict) or not isinstance(comment.get("body"), str):
            return ["comment_identity_unreadable"]
        for match in HOST_ACTION_ARTIFACT_RE.finditer(comment["body"]):
            try:
                payload = json.loads(match.group(1))
            except json.JSONDecodeError:
                return ["marker_json_invalid"]
            if isinstance(payload, dict):
                matches.append((comment, payload))
    if len(matches) != 1:
        return [f"marker_count:{len(matches)}"]
    comment, payload = matches[0]
    user = comment.get("user") if isinstance(comment.get("user"), dict) else {}
    observed_at = _parse_time(payload.get("observed_at"))
    errors: list[str] = []
    if set(payload) != {"schema_version", "action_locator", "observed_at", "verdict"} or payload.get("schema_version") != "loom-host-action-attestation/v1":
        errors.append("schema_invalid")
    action_locator = payload.get("action_locator")
    if not isinstance(action_locator, str) or not action_locator.casefold().startswith(f"github://{repository}/host-action/".casefold()):
        errors.append("action_locator_invalid")
    if observed_at is None:
        errors.append("observed_at_invalid")
    if _text(payload.get("verdict")) != "passed":
        errors.append("verdict_not_passed")
    actor_matches = (
        isinstance(user.get("id"), int)
        and not isinstance(user.get("id"), bool)
        and user.get("id") == actor.get("id")
        and isinstance(user.get("login"), str)
        and isinstance(actor.get("login"), str)
        and user["login"].casefold() == actor["login"].casefold()
    )
    if _text(comment.get("author_association")) not in TRUSTED_AUTHOR_ASSOCIATIONS and not actor_matches:
        errors.append("author_association_untrusted")
    if not isinstance(user.get("login"), str) or not user.get("login"):
        errors.append("author_login_unreadable")
    return errors


def _valid_host_action_attestation(issue: dict[str, Any], repository: str, actor: dict[str, Any]) -> bool:
    return not _host_action_attestation_errors(issue, repository, actor)


def _validate_completed(
    issue: dict[str, Any],
    issues: dict[int, dict[str, Any]],
    repository: str,
    actor: dict[str, Any],
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
        if _green_merged_pr(issue, default_branch):
            return
        exception_applies, exception_error = _v032_runtime_eol_delivery_exception(issue, repository, default_branch)
        if exception_applies:
            if exception_error is None:
                return
            reasons.append(_reason(exception_error, locator, "the frozen v0.32 runtime-EOL delivery exception no longer matches authenticated GitHub facts"))
            return
        if HOST_ONLY_DELIVERY_LABEL in _labels(issue):
            attestation_errors = _host_action_attestation_errors(issue, repository, actor)
            if not attestation_errors:
                return
            reasons.append(_reason("missing_delivery_attestation", locator, "host-only-delivery attestation is invalid: " + ", ".join(attestation_errors)))
            return
        reasons.append(_reason("missing_delivery_attestation", locator, "Work Item needs merged delivery checks, or an authenticated host-action attestation when explicitly labeled host-only-delivery"))
        return
    children = issue.get("children")
    if not isinstance(children, list) or not children:
        reasons.append(_reason("missing_native_child", locator, "completed Phase, Product Problem, or FR requires its native child tree"))
        return
    expected = EXPECTED_CHILD_TYPE.get(kind)
    allowed_types = PHASE_CHILD_TYPES if kind == "phase" else {expected} if expected else set()
    next_visiting = {*visiting, number}
    for child_number in children:
        child = issues.get(child_number) if isinstance(child_number, int) else None
        if not isinstance(child, dict):
            reasons.append(_reason("host_unreadable", locator, "a native child cannot be read from GitHub"))
            continue
        child_type = _type(child)
        if child_type not in allowed_types:
            expected_label = ", ".join(sorted(allowed_types)) or "no child"
            reasons.append(_reason("invalid_native_child_type", f"issue:{child_number}", f"{kind} requires native children of type: {expected_label}"))
            continue
        _validate_completed(child, issues, repository, actor, default_branch, reasons, next_visiting)


def evaluate_closure(snapshot: object, *, host_resolved: bool = False) -> dict[str, Any]:
    """Decide whether a closed FR/Phase may remain closed from host facts only."""
    if not isinstance(snapshot, dict):
        return _payload(0, "reopen_required", "GitHub closure snapshot is unreadable.", [_reason("host_unreadable", "issue:unknown", "closure snapshot must be an object")], completed=False)
    subject = snapshot.get("subject")
    issue_rows = snapshot.get("issues")
    repository = snapshot.get("repository")
    actor = snapshot.get("actor") if isinstance(snapshot.get("actor"), dict) else {}
    default_branch = snapshot.get("default_branch")
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
    reasons: list[dict[str, str]] = []
    _trusted_product_acceptance(snapshot, subject, labels, reasons, host_resolved=host_resolved)
    _validate_completed(subject_issue, issues, repository, actor, default_branch, reasons, set())
    if reasons:
        return _payload(subject, "reopen_required", "Completed FR/Phase closure is missing required host facts.", reasons, completed=False)
    return _payload(subject, "allow_completed_close", "Trusted product acceptance, native children, dependencies, merged delivery, and check evidence permit completed closure.", [], completed=True)


def main(argv: list[str] | None = None) -> int:
    """Evaluate one host snapshot without making a GitHub write."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True, help="GitHub host snapshot JSON")
    parser.add_argument("--output", type=Path, help="write the verdict JSON to this path")
    parser.add_argument("--resolve-host-facts", action="store_true", help="resolve acceptance artifact locators through authenticated GitHub readback")
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
