"""Host-native, just-in-time FR-to-Work-Item admission.

This module deliberately owns no repository carrier.  The caller supplies the
small GitHub host surface it already owns, which keeps this policy independent
of Loom's large execution-flow module and avoids a circular import.
"""

from __future__ import annotations

import hashlib
import json
import re
import shlex
from pathlib import Path
from typing import Any
from urllib.parse import quote


SCHEMA = "loom-fr-wi-admission/v1"
MARKER = "loom:fr-wi-admission"
EXCEPTION_LABELS = {"duplicate", "invalid", "cancelled", "canceled", "superseded", "deferred", "not planned"}
MARKER_RE = re.compile(r"<!--\s*loom:fr-wi-admission\s+(?P<payload>\{.*?\})\s*-->", re.DOTALL)


def typed_locator(object_type: str, number: int) -> str:
    return f"{object_type}:{number}"


def _task(raw: str | None) -> tuple[str | None, list[str]]:
    value = " ".join(str(raw or "").split())
    if not value:
        return None, ["admission task"]
    if len(value) > 220:
        return None, ["admission task must be at most 220 characters"]
    return value, []


def _plan_key(owner: str, repo: str, fr: int, task: str) -> str:
    value = json.dumps({"owner": owner.lower(), "repo": repo.lower(), "fr": fr, "task": task}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _marker(fr: int, plan_key: str) -> str:
    payload = {"schema_version": SCHEMA, "fr": typed_locator("fr", fr), "plan_key": plan_key}
    return f"<!-- {MARKER} {json.dumps(payload, ensure_ascii=False, sort_keys=True)} -->"


def marker_payload(body: object) -> dict[str, Any] | None:
    if not isinstance(body, str):
        return None
    match = MARKER_RE.search(body)
    if not match:
        return None
    try:
        value = json.loads(match.group("payload"))
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA:
        return None
    if not isinstance(value.get("fr"), str) or not isinstance(value.get("plan_key"), str):
        return None
    return value


def _work_item_label(host: Any, repo_interface: dict[str, Any] | None) -> str:
    mappings, _, _ = host.github_intake_taxonomy_mapping(repo_interface)
    for mapping in mappings:
        if mapping.get("loom_type") == "work_item":
            for label in mapping.get("labels", []):
                if isinstance(label, str) and label.strip():
                    return label.strip()
    return "work-item"


def _exception(host: Any, issue: dict[str, Any]) -> str | None:
    if host.normalize_taxonomy_match_text(issue.get("stateReason")) == "not_planned":
        return "not_planned"
    labels = host.normalized_issue_labels(issue)
    matches = sorted(labels.intersection(EXCEPTION_LABELS))
    return matches[0] if matches else None


def _subissues(tree: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    connection = tree.get("subIssues")
    if not isinstance(connection, dict):
        return [], ["native sub-issue tree is missing `subIssues`"]
    page_info = connection.get("pageInfo")
    if not isinstance(page_info, dict) or not isinstance(page_info.get("hasNextPage"), bool):
        return [], ["native sub-issue tree pagination is unreadable"]
    if page_info.get("hasNextPage"):
        return [], ["native sub-issue tree exceeds the supported read page; reconcile it before admission"]
    nodes = connection.get("nodes")
    if not isinstance(nodes, list):
        return [], ["native sub-issue tree is missing `subIssues.nodes`"]
    return [node for node in nodes if isinstance(node, dict)], []


def _search_candidates(host: Any, root: Path, owner: str, repo: str, plan_key: str) -> tuple[list[dict[str, Any]] | None, list[str]]:
    query = """
query($query:String!) {
  search(query:$query, type:ISSUE, first:100) {
    pageInfo { hasNextPage }
    nodes {
      ... on Issue {
        id number title body state url
        labels(first:20) { nodes { name } }
        parent { id number title state url }
      }
    }
  }
}
"""
    data, errors = host.gh_graphql_json(root, query, {"query": f'repo:{owner}/{repo} is:issue "{plan_key}"'})
    if errors or data is None:
        return None, errors or ["GitHub admission candidate read failed"]
    search = data.get("search") if isinstance(data.get("search"), dict) else None
    if not isinstance(search, dict):
        return None, ["GitHub admission candidate read is missing `search`"]
    page_info = search.get("pageInfo")
    if not isinstance(page_info, dict) or not isinstance(page_info.get("hasNextPage"), bool):
        return None, ["GitHub admission candidate pagination is unreadable"]
    if page_info.get("hasNextPage"):
        return None, ["GitHub admission candidate search exceeds the supported read page; reconcile it before admission"]
    nodes = search.get("nodes")
    if not isinstance(nodes, list):
        return None, ["GitHub admission candidate read is missing `nodes`"]
    return [node for node in nodes if isinstance(node, dict) and (marker := marker_payload(node.get("body"))) and marker.get("plan_key") == plan_key], []


def _requested_candidate(host: Any, root: Path, owner: str, repo: str, number: int, plan_key: str) -> tuple[list[dict[str, Any]] | None, list[str]]:
    candidate, errors = host.github_issue_payload(root, owner, repo, number)
    if errors or candidate is None:
        return None, [f"Work Item #{number}: {message}" for message in errors]
    tree, tree_errors = host.issue_tree_payload(root, owner, repo, number)
    if tree_errors or tree is None:
        return None, [f"Work Item #{number} native tree: {message}" for message in tree_errors]
    candidate["parent"] = tree.get("parent")
    marker = marker_payload(candidate.get("body"))
    if marker is None or marker.get("plan_key") != plan_key:
        return None, [f"Work Item #{number} does not match the admission plan key"]
    return [candidate], []


def _create(host: Any, root: Path, owner: str, repo: str, fr: int, task: str, plan_key: str, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    body = "\n".join(("## Loom admission", "", f"Source FR: `{typed_locator('fr', fr)}`", "", f"Scope: {task}", "", _marker(fr, plan_key), ""))
    path = f"repos/{quote(owner, safe='')}/{quote(repo, safe='')}/issues"
    payload, errors = host.gh_rest_write_json(root, method="POST", path=path, request_payload={"title": f"WI: {task}", "body": body, "labels": [label]})
    if errors or payload is None:
        return None, errors or ["GitHub Work Item create failed"]
    issue = host.normalize_rest_issue(payload)
    if not isinstance(issue.get("number"), int):
        return None, ["GitHub Work Item create response is missing an issue number"]
    return issue, []


def _attach(host: Any, root: Path, owner: str, repo: str, parent: int, child: int) -> list[str]:
    lookup = """
query($owner:String!, $name:String!, $parent:Int!, $child:Int!) {
  repository(owner:$owner, name:$name) {
    parent: issue(number:$parent) { id }
    child: issue(number:$child) { id }
  }
}
"""
    data, errors = host.gh_graphql_json(root, lookup, {"owner": owner, "name": repo, "parent": parent, "child": child})
    if errors or data is None:
        return errors or ["GitHub native sub-issue id readback failed"]
    repository = data.get("repository") if isinstance(data.get("repository"), dict) else {}
    parent_id = repository.get("parent", {}).get("id") if isinstance(repository.get("parent"), dict) else None
    child_id = repository.get("child", {}).get("id") if isinstance(repository.get("child"), dict) else None
    if not isinstance(parent_id, str) or not isinstance(child_id, str):
        return [f"GitHub native sub-issue mutation is missing issue ids for parent #{parent} and child #{child}"]
    mutation = """
mutation($issueId:ID!, $subIssueId:ID!, $clientMutationId:String!) {
  addSubIssue(input:{issueId:$issueId, subIssueId:$subIssueId, replaceParent:false, clientMutationId:$clientMutationId}) { clientMutationId }
}
"""
    _, mutation_errors = host.gh_graphql_json(
        root,
        mutation,
        {"issueId": parent_id, "subIssueId": child_id, "clientMutationId": f"loom-fr-wi-admission-{parent}-{child}"},
    )
    return mutation_errors


def _result(
    *,
    result: str,
    admission_state: str,
    summary: str,
    owner: str,
    repo: str,
    issue: int,
    object_type: str,
    intent: str,
    apply: bool,
    proposal: dict[str, Any] | None,
    missing_inputs: list[str] | None = None,
    locators: list[str] | None = None,
    writes: list[dict[str, Any]] | None = None,
    next_action: str | None = None,
    failed_layer: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "command": "github-intake",
        "operation": "admission",
        "schema_version": SCHEMA,
        "result": result,
        "admission_state": admission_state,
        "summary": summary,
        "intent": intent,
        "apply": apply,
        "mutates": bool(writes),
        "repository": {"owner": owner, "name": repo},
        "subject": {"type": object_type, "number": issue, "locator": typed_locator(object_type, issue)},
        "proposal": proposal,
        "missing_inputs": list(dict.fromkeys(missing_inputs or [])),
        "created_locators": list(locators or []),
        "host_writes": list(writes or []),
        "next_action": next_action,
        "failed_layer": failed_layer,
        "provenance": [{"source_layer": "host_control_mirror", "source_owner": "github", "source_locator": f"issue #{issue}", "freshness": "fresh"}],
        "evidence": evidence or {},
    }


def github_fr_wi_admission_payload(
    *,
    host: Any,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int,
    intent: str,
    task: str | None,
    blocked_by: list[int],
    work_item_number: int | None,
    apply: bool,
) -> dict[str, Any]:
    detected_owner, detected_repo = host.detect_github_repo(target_root)
    owner, repo = owner or detected_owner, repo_name or detected_repo
    object_type = "unknown"
    proposal_payload: dict[str, Any] | None = None
    task, task_errors = _task(task)

    def respond(result: str, state: str, summary: str, **fields: Any) -> dict[str, Any]:
        return _result(
            result=result,
            admission_state=state,
            summary=summary,
            owner=owner or "unknown",
            repo=repo or "unknown",
            issue=issue_number,
            object_type=object_type,
            intent=intent,
            apply=apply,
            proposal=fields.pop("proposal", proposal_payload),
            **fields,
        )

    if not owner or not repo:
        return respond("block", "host_unreadable", "FR-to-WI admission requires a GitHub repository locator.", missing_inputs=["owner/repo"], failed_layer="host-input")
    if task_errors or task is None:
        return respond("block", "invalid_proposal", "FR-to-WI admission requires one bounded Work Item proposal.", missing_inputs=task_errors, failed_layer="admission-input")
    blockers = sorted({number for number in blocked_by if isinstance(number, int) and number > 0})
    if len(blockers) != len(blocked_by) or len(blockers) != len(set(blocked_by)):
        return respond("block", "invalid_proposal", "FR-to-WI admission received an invalid native dependency locator.", missing_inputs=["--blocked-by must contain distinct positive issue numbers"], failed_layer="admission-input")

    fr, errors = host.github_issue_payload(target_root, owner, repo, issue_number)
    if errors or fr is None:
        return respond("block", "host_unreadable", "FR-to-WI admission could not read the requested GitHub issue.", missing_inputs=[f"issue: {message}" for message in errors], failed_layer="host-readback")
    surface = host.build_governance_surface(target_root)
    repo_interface = surface.get("repo_interface") if isinstance(surface.get("repo_interface"), dict) else None
    object_type, inference = host.github_intake_object_type(fr, repo_interface=repo_interface)
    if object_type == "work_item":
        return respond("pass", "admitted", "The requested GitHub issue is already a Work Item and may enter execution.", evidence={"type_inference": inference})
    if object_type != "fr":
        return respond("block", "unsupported_subject", "FR-to-WI admission only accepts an explicitly typed FR or Work Item.", missing_inputs=["typed FR or Work Item"], failed_layer="host-planning-taxonomy", evidence={"type_inference": inference})
    if exception := _exception(host, fr):
        return respond("pass", "not_planned", "The FR has an explicit non-completion exception and is not treated as product completion.", evidence={"exception": exception, "type_inference": inference})

    plan_key = _plan_key(owner, repo, issue_number, task)
    proposal_payload = {
        "schema_version": SCHEMA,
        "parent": {"type": "fr", "number": issue_number, "locator": typed_locator("fr", issue_number)},
        "work_items": [{"plan_key": plan_key, "title": f"WI: {task}", "type": "work_item", "labels": [_work_item_label(host, repo_interface)], "blocked_by": [typed_locator("issue", number) for number in blockers]}],
    }
    command = ["loom route --target .", f"--issue {issue_number}", f"--task {shlex.quote(task)}", f"--intent {intent}"]
    command.extend(f"--blocked-by {number}" for number in blockers)
    command.extend(("--apply", "--json"))
    resume = " ".join(command)

    tree, tree_errors = host.issue_tree_payload(target_root, owner, repo, issue_number)
    if tree_errors or tree is None:
        return respond("block", "host_unreadable", "FR-to-WI admission could not read the native sub-issue tree.", missing_inputs=[f"native tree: {message}" for message in tree_errors], next_action=resume, failed_layer="host-readback")
    children, children_errors = _subissues(tree)
    if children_errors:
        return respond("block", "host_unreadable", "FR-to-WI admission cannot treat an incomplete native sub-issue tree as empty.", missing_inputs=children_errors, next_action=resume, failed_layer="host-readback")
    candidates, candidate_errors = (
        _requested_candidate(host, target_root, owner, repo, work_item_number, plan_key)
        if work_item_number is not None
        else _search_candidates(host, target_root, owner, repo, plan_key)
    )
    if candidate_errors or candidates is None:
        return respond("block", "host_unreadable", "FR-to-WI admission could not reconcile prior host writes safely.", missing_inputs=[f"admission candidates: {message}" for message in candidate_errors], next_action=resume, failed_layer="host-readback")
    if len(candidates) > 1:
        return respond("block", "ambiguous_reconciliation", "FR-to-WI admission found multiple Work Item candidates for one plan key and will not guess.", missing_inputs=["multiple host Work Items match the admission plan key"], next_action="manually resolve the duplicate host Work Items, then rerun admission", failed_layer="host-reconciliation", evidence={"candidate_numbers": [item.get("number") for item in candidates]})

    candidate = candidates[0] if candidates else None
    if candidate is None and not apply:
        if intent == "planning" and fr.get("state") != "CLOSED":
            return respond("pass", "planning", "The FR remains in planning; no Work Item or host mutation is required yet.", next_action=resume, evidence={"type_inference": inference, "native_subissue_count": len(children)})
        return respond("block", "needs_breakdown", "This FR cannot enter execution or completion until a native Work Item is admitted.", missing_inputs=["native Work Item breakdown"], next_action=resume, failed_layer="fr-wi-admission", evidence={"type_inference": inference, "native_subissue_count": len(children)})

    writes: list[dict[str, Any]] = []
    created = False
    if candidate is None:
        candidate, create_errors = _create(host, target_root, owner, repo, issue_number, task, plan_key, _work_item_label(host, repo_interface))
        if create_errors or candidate is None:
            return respond("block", "host_write_failed", "FR-to-WI admission could not create the proposed host Work Item.", missing_inputs=[f"create Work Item: {message}" for message in create_errors], next_action=resume, failed_layer="host-write")
        created = True
    candidate_number = candidate.get("number") if isinstance(candidate, dict) else None
    if not isinstance(candidate_number, int):
        return respond("partial_apply" if created else "block", "partial_apply" if created else "host_unreadable", "FR-to-WI admission could not determine the Work Item candidate number.", locators=[], next_action=resume, failed_layer="host-readback")
    locator = typed_locator("work_item", candidate_number)
    if created:
        writes.append({"action": "create_issue", "locator": locator})
    candidate_type, _ = host.github_intake_object_type(candidate, repo_interface=repo_interface)
    if not created and candidate_type != "work_item":
        return respond("block", "type_conflict", "FR-to-WI admission found a plan marker on a host issue that is not typed as a Work Item.", missing_inputs=[f"candidate #{candidate_number} must be typed work_item"], next_action="fix the candidate issue type, then rerun admission", failed_layer="host-reconciliation")
    parent = candidate.get("parent") if isinstance(candidate.get("parent"), dict) else None
    parent_number = parent.get("number") if isinstance(parent, dict) else None
    if parent_number not in {None, issue_number}:
        return respond("block", "parent_conflict", "FR-to-WI admission found a Work Item plan marker under a different native parent and will not reparent it.", missing_inputs=[f"candidate #{candidate_number} has parent #{parent_number}"], next_action="manually resolve the native parent conflict, then rerun admission", failed_layer="host-reconciliation")
    child_numbers = {node.get("number") for node in children if isinstance(node.get("number"), int)}
    if parent_number == issue_number and candidate_number not in child_numbers:
        return respond("block", "tree_conflict", "FR-to-WI admission found inconsistent native parent and sub-issue readback and will not continue.", missing_inputs=[f"candidate #{candidate_number} is absent from FR #{issue_number} native sub-issues"], next_action="reconcile the GitHub native tree, then rerun admission", failed_layer="host-reconciliation")
    recovery = f"{resume} --work-item {candidate_number}"
    if parent_number is None:
        if not apply:
            return respond("partial_apply", "partial_apply", "A previous admission created a Work Item but did not attach its native parent relation.", locators=[locator], next_action=recovery, failed_layer="host-reconciliation")
        parent_errors = _attach(host, target_root, owner, repo, issue_number, candidate_number)
        if parent_errors:
            return respond("partial_apply", "partial_apply", "FR-to-WI admission created or found a Work Item but could not attach its native parent relation.", locators=[locator], writes=writes, missing_inputs=[f"attach native parent: {message}" for message in parent_errors], next_action=recovery, failed_layer="host-write")
        writes.append({"action": "add_sub_issue", "parent": typed_locator("fr", issue_number), "locator": locator})

    if blockers:
        dependencies = host.github_issue_dependencies_payload(target_root, owner, repo, candidate_number)
        if dependencies.get("availability") != "present" or dependencies.get("complete") is not True:
            return respond("partial_apply" if writes else "block", "partial_apply" if writes else "host_unreadable", "FR-to-WI admission cannot verify the requested native dependency relation.", locators=[locator] if writes else [], writes=writes, missing_inputs=["native dependency capability"], next_action=recovery, failed_layer="host-readback")
        existing = {edge.get("blocking_issue") for edge in dependencies.get("native_edges", []) if isinstance(edge, dict) and edge.get("direction") == "blocked_by" and edge.get("source_issue") == candidate_number}
        missing = [number for number in blockers if number not in existing]
        if missing and not apply:
            return respond("partial_apply", "partial_apply", "A Work Item exists but its requested native dependency relation is incomplete.", locators=[locator], next_action=recovery, failed_layer="host-reconciliation")
        for blocker in missing:
            dependency_errors = host.set_native_dependency(target_root, owner, repo, candidate_number, blocker, "addBlockedBy")
            if dependency_errors:
                return respond("partial_apply", "partial_apply", "FR-to-WI admission could not finish the requested native dependency relation.", locators=[locator], writes=writes, missing_inputs=[f"add blocked-by #{blocker}: {message}" for message in dependency_errors], next_action=recovery, failed_layer="host-write")
            writes.append({"action": "add_blocked_by", "locator": locator, "blocking_issue": typed_locator("issue", blocker)})

    if writes:
        readback = github_fr_wi_admission_payload(host=host, target_root=target_root, owner=owner, repo_name=repo, issue_number=issue_number, intent=intent, task=task, blocked_by=blockers, work_item_number=candidate_number, apply=False)
        if readback.get("result") != "pass" or readback.get("admission_state") != "admitted":
            return respond("partial_apply", "partial_apply", "FR-to-WI admission wrote host state but the required GitHub readback is not yet consistent.", locators=[locator], writes=writes, missing_inputs=[str(value) for value in readback.get("missing_inputs", [])], next_action=recovery, failed_layer="host-readback", evidence={"readback": readback})
        readback.update({"apply": True, "mutates": True, "created_locators": [locator] if created else [], "host_writes": writes})
        return readback
    return respond("pass", "admitted", "The FR has a host-native Work Item breakdown that is ready for the requested lifecycle intent.", evidence={"work_item": locator, "native_subissue_count": len(children), "type_inference": inference})
