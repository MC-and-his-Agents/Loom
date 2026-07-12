#!/usr/bin/env python3
"""Host-derived closeout and reconciliation domain."""

from __future__ import annotations
import argparse
import hashlib
import json
import re
import shlex
from pathlib import Path
from typing import Any
from urllib.parse import quote
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None  # type: ignore[assignment]
from fact_chain_support import (
    load_json_file,
    parse_recovery_entry,
    parse_work_item,
    resolve_repo_relative_path,
)
from authority_contract import authority_verdict, lifecycle_admission_verdict
from flow_runtime import emit, git_branch, git_head_sha, resolve_target_arg, run_git, runtime_state_payload
from review_flow import (
    artifact_locator_for_path,
    fact_chain_error_contract,
    repo_specific_requirements_payload,
    report_blocking_failures,
    report_blocking_messages,
    report_provenance,
    report_recovery_readiness,
)
from host_profile import (
    find_project_item,
    github_binding_payload,
    github_fr_wi_admission_payload,
    issue_tree_payload,
    project_item_for_issue,
    project_status_context,
    set_native_dependency,
    set_project_item_done,
)
from delivery_control import (
    allowed_post_review_carrier_paths,
    closeout_gate_command,
    closeout_subcheck,
    closeout_suite_gate_subchecks,
    contains_merged_commit,
    dedupe_strings,
    dependency_graph_payload,
    detect_github_repo,
    effective_closeout_gate_profile,
    is_idle_context_errors,
    load_context,
    load_optional_json_fixture,
    load_retained_item_context,
    load_review_record,
    make_reconciliation_finding,
    normalize_checkpoint,
    normalize_issue_fixture_payload,
    normalize_pr_fixture_payload,
    post_merge_review_diagnostic_payload,
    relative_to_root,
    required_check_status_payload,
    required_status_contexts_from_branch_rules,
    required_status_contexts_from_protection,
    review_head_binding_for_head,
    review_validation_summary_binding,
    runtime_state_block_payload,
    suite_gate_not_applicable_payload,
    suite_gate_reconciliation_findings,
    suite_gate_required_for_surface,
    suite_gate_unreadable_payload,
    suite_gate_validation_payload,
)
from github_host import (
    gh_json,
    gh_rest_json,
    gh_rest_list,
    github_issue_dependencies_payload,
    github_issue_payload,
    github_lifecycle_subject_readback,
    github_pr_payload,
    graphql_budget_guard,
    run_process,
)
from governance_surface import (
    build_governance_surface,
    empty_target_release_status,
)
from execution_attempts import (
    EXECUTION_ATTEMPT_SCHEMA,
    execution_attempt_directory,
)

TERMINAL_CHECKPOINTS = {
    "retired",
    "done",
    "closed",
    "closed_out",
    "merged",
    "archived",
}

GITHUB_ISSUE_URL_RE = re.compile(r"github\.com/(?P<owner>[^/\s`]+)/(?P<repo>[^/\s`]+)/issues/(?P<number>\d+)")

GITHUB_PR_URL_RE = re.compile(r"github\.com/(?P<owner>[^/\s`]+)/(?P<repo>[^/\s`]+)/pull/(?P<number>\d+)")

GITHUB_ISSUE_REF_RE = re.compile(r"(?i)\b(?:github\s+issue|issue)\s+#?(?P<number>\d+)\b")

GITHUB_PR_REF_RE = re.compile(r"(?i)\b(?:github\s+pr|github\s+pull\s+request|pull\s+request|pr)\s+#?(?P<number>\d+)\b")

GOAL_EXECUTION_CONTRACT_SCHEMA = "loom-goal-execution-contract/v1"

GOAL_COMPLETION_SCHEMA = "loom-goal-completion/v1"

CLOSEOUT_PR_ROLES = (
    "implementation_pr",
    "release_pr",
    "carrier_sync_pr",
    "final_closeout_pr",
)

CLOSEOUT_LIGHT_PROFILE = "closeout-contract"

CLOSEOUT_HEAVY_PROFILES = {
    "source-self-fixture",
    "bootstrap-regression",
    "distribution-regression",
    "strong-profile-full-gate",
}

IMPLEMENTATION_REVIEW_KINDS = {"general_review", "code_review"}

def closeout_pr_role_numbers_from_args(args: argparse.Namespace) -> dict[str, int]:
    roles: dict[str, int] = {}
    for role in CLOSEOUT_PR_ROLES:
        value = getattr(args, role, None)
        if value is not None:
            roles[role] = int(value)
    return roles

def closeout_pr_roles_payload(
    *,
    legacy_pr_number: int | None,
    role_numbers: dict[str, int],
    requested_role: str | None,
) -> dict[str, Any]:
    current_role: str | None = None
    current_number: int | None = None
    source: str | None = None

    if requested_role is not None:
        current_role = requested_role
        current_number = role_numbers.get(requested_role, legacy_pr_number)
        source = f"--{requested_role.replace('_', '-')}" if requested_role in role_numbers else "--pr plus --pr-role"
    else:
        for role in ("final_closeout_pr", "carrier_sync_pr", "release_pr", "implementation_pr"):
            if role in role_numbers:
                current_role = role
                current_number = role_numbers[role]
                source = f"--{role.replace('_', '-')}"
                break
        if current_role is None and legacy_pr_number is not None:
            current_role = "implementation_pr"
            current_number = legacy_pr_number
            source = "--pr"

    summary = (
        f"closeout check is consuming `{current_role}` PR #{current_number}."
        if current_role is not None and current_number is not None
        else "closeout check has no PR role input; host PR readback is not role-bound."
    )
    return {
        "schema_version": "loom-closeout-pr-roles/v1",
        "supported_roles": list(CLOSEOUT_PR_ROLES),
        "roles": {role: role_numbers[role] for role in CLOSEOUT_PR_ROLES if role in role_numbers},
        "legacy_pr": legacy_pr_number,
        "requested_role": requested_role,
        "current": {
            "role": current_role,
            "number": current_number,
            "source": source,
        },
        "summary": summary,
    }

def closeout_current_pr_number(pr_roles: dict[str, Any]) -> int | None:
    current = pr_roles.get("current") if isinstance(pr_roles, dict) else None
    number = current.get("number") if isinstance(current, dict) else None
    return int(number) if isinstance(number, int) else None

def closeout_role_pr_number(pr_roles: dict[str, Any], role: str) -> int | None:
    roles = pr_roles.get("roles") if isinstance(pr_roles, dict) else None
    number = roles.get(role) if isinstance(roles, dict) else None
    return int(number) if isinstance(number, int) else None

def closeout_merge_ready_pr_number(pr_roles: dict[str, Any]) -> int | None:
    current = pr_roles.get("current") if isinstance(pr_roles, dict) else None
    current_role = current.get("role") if isinstance(current, dict) else None
    if current_role in {"carrier_sync_pr", "final_closeout_pr"}:
        implementation_pr = closeout_role_pr_number(pr_roles, "implementation_pr")
        if implementation_pr is not None:
            return implementation_pr
    return closeout_current_pr_number(pr_roles)

def validation_summary_digest(summary: str | None) -> str | None:
    if not isinstance(summary, str) or not summary.strip():
        return None
    return hashlib.sha256(summary.strip().encode("utf-8")).hexdigest()

def recovery_validation_summary_at_ref(root: Path, recovery_relative: str, ref: str) -> tuple[str | None, list[str]]:
    result = run_git(root, ["show", f"{ref}:{recovery_relative}"])
    if result is None:
        return None, ["git is unavailable while reading retained recovery entry at PR head"]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git show failed"
        return None, [f"retained recovery entry is unreadable at `{ref}`: {detail}"]
    for raw_line in result.stdout.splitlines():
        match = re.match(r"^-\s+Latest Validation Summary:\s*(.*)$", raw_line.strip())
        if match:
            value = match.group(1).strip()
            if value:
                return value, []
            return None, [f"retained recovery entry `{recovery_relative}` has empty Latest Validation Summary at `{ref}`"]
    return None, [f"retained recovery entry `{recovery_relative}` is missing Latest Validation Summary at `{ref}`"]

def latest_successful_execution_attempt(
    target_root: Path,
    item_id: str,
    operation: str,
) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    attempts_dir = execution_attempt_directory(target_root, item_id)
    if not attempts_dir.exists():
        return None, None, [f"missing execution_attempt directory: {artifact_locator_for_path(attempts_dir, target_root)}"]
    versioned_candidates: list[tuple[float, str, dict[str, Any]]] = []
    latest_candidates: list[tuple[float, str, dict[str, Any]]] = []
    errors: list[str] = []
    for path in sorted(attempts_dir.glob("*.json")):
        relative = artifact_locator_for_path(path, target_root)
        try:
            payload = load_json_file(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"invalid execution_attempt `{relative}`: {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"execution_attempt `{relative}` must be a JSON object")
            continue
        if payload.get("schema_version") != EXECUTION_ATTEMPT_SCHEMA:
            continue
        if payload.get("operation") != operation or payload.get("result") != "pass":
            continue
        candidates = latest_candidates if path.name == "latest.json" else versioned_candidates
        candidates.append((path.stat().st_mtime, relative, payload))
    candidates = versioned_candidates or latest_candidates
    if not candidates:
        return None, None, errors or [f"missing successful `{operation}` execution_attempt for `{item_id}`"]
    _, relative, payload = sorted(candidates, key=lambda entry: (entry[0], entry[1]))[-1]
    return payload, relative, []

def missing_versioned_execution_attempt(errors: list[str], operation: str) -> bool:
    if not errors:
        return False
    expected_missing_success = f"missing successful `{operation}` execution_attempt"
    return all(
        error.startswith("missing execution_attempt directory:")
        or error.startswith(expected_missing_success)
        for error in errors
    )

def closeout_required_status_subcheck(
    *,
    target_root: Path,
    profile: str,
    owner: str,
    repo_name: str,
    pr_number: int | None,
    pr_payload: dict[str, Any] | None,
    pr_head: str | None,
    pr_payload_file: str | None,
    status_checks_file: str | None,
    branch_protection_file: str | None,
    ruleset_file: str | None,
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    source = "host_pr_checks"
    base_ref = pr_payload.get("baseRefName") if isinstance(pr_payload, dict) else None
    if pr_number is None:
        missing_inputs.append("pr")
    if not isinstance(pr_head, str) or not pr_head:
        missing_inputs.append("pr head SHA")
    if not isinstance(base_ref, str) or not base_ref:
        missing_inputs.append("pr baseRefName")

    protection_payload, protection_errors = load_optional_json_fixture(
        target_root,
        branch_protection_file,
        label="branch protection fixture",
    )
    if protection_payload is None and not protection_errors and owner and repo_name and isinstance(base_ref, str) and base_ref:
        protection_payload, protection_errors = gh_rest_json(
            target_root,
            f"repos/{owner}/{repo_name}/branches/{quote(base_ref, safe='')}/protection",
        )
    missing_inputs.extend(f"branch protection: {message}" for message in protection_errors)

    ruleset_payload, ruleset_errors = load_optional_json_fixture(
        target_root,
        ruleset_file,
        label="branch rules/ruleset fixture",
    )
    if ruleset_payload is None and not ruleset_errors and owner and repo_name and isinstance(base_ref, str) and base_ref:
        ruleset_payload, ruleset_errors = gh_rest_list(
            target_root,
            f"repos/{owner}/{repo_name}/rules/branches/{quote(base_ref, safe='')}",
        )
    missing_inputs.extend(f"branch rules/ruleset: {message}" for message in ruleset_errors)

    status_payload, status_errors = load_optional_json_fixture(
        target_root,
        status_checks_file,
        label="status checks fixture",
    )
    if status_payload is None and not status_errors and pr_number is not None:
        status_payload, status_errors = gh_json(
            target_root,
            ["pr", "view", str(pr_number), "--json", "statusCheckRollup"],
        )
    missing_inputs.extend(f"status checks: {message}" for message in status_errors)

    protection_contexts = required_status_contexts_from_protection(protection_payload)
    ruleset_contexts = required_status_contexts_from_branch_rules(ruleset_payload)
    required_contexts = sorted(set(protection_contexts + ruleset_contexts))
    required_checks = required_check_status_payload(
        status_payload.get("statusCheckRollup") if isinstance(status_payload, dict) else status_payload,
        required_contexts,
    )
    if protection_payload is None and ruleset_payload is None:
        missing_inputs.append("branch protection or ruleset readback is unavailable")
    for key in ("missing", "pending", "failing"):
        for context in required_checks[key]:
            missing_inputs.append(f"required check `{context}` is {key}")

    evidence_locator = status_checks_file or (f"github:pr/{pr_number}/statusCheckRollup" if pr_number is not None else None)
    return closeout_subcheck(
        check_id="host_pr_checks",
        source=source,
        profile=profile,
        required_for_closeout=True,
        trigger_reason="closeout must prove host required checks were fresh for the retained PR head",
        result="pass" if not missing_inputs else "block",
        fallback_to=None if not missing_inputs else "pr-gate",
        evidence_locator=evidence_locator,
        missing_inputs=missing_inputs,
        head_sha=pr_head,
        required_checks=required_checks,
        required_contexts=required_contexts,
        pr_payload_locator=pr_payload_file,
    )

def closeout_backlink_subchecks(
    *,
    target_root: Path,
    context: dict[str, Any] | None,
    profile: str,
    owner: str,
    repo_name: str,
    pr_number: int | None,
    pr_payload: dict[str, Any] | None,
    merge_ready_pr_number: int | None,
    merge_ready_pr_payload: dict[str, Any] | None,
    merge_ready_pr_errors: list[str] | None,
    merge_commit_sha: str | None,
    merge_commit_in_target: bool | None,
    pr_payload_file: str | None,
    status_checks_file: str | None,
    branch_protection_file: str | None,
    ruleset_file: str | None,
) -> list[dict[str, Any]]:
    subchecks: list[dict[str, Any]] = []
    if context is None:
        subchecks.append(
            closeout_subcheck(
                check_id="fact_chain",
                source="fact_chain",
                profile=profile,
                required_for_closeout=True,
                trigger_reason="closeout contract needs a readable Work Item fact chain",
                result="block",
                fallback_to="admission",
                missing_inputs=["fact-chain"],
            )
        )
        return subchecks

    item_id = context["item_id"]
    pr_head = pr_payload.get("headRefOid") if isinstance(pr_payload, dict) and isinstance(pr_payload.get("headRefOid"), str) else None
    merge_ready_expected_head = pr_head
    merge_ready_expected_source = "current_pr"
    if merge_ready_pr_number is not None and merge_ready_pr_number != pr_number:
        merge_ready_expected_source = "implementation_pr"
        merge_ready_expected_head = (
            merge_ready_pr_payload.get("headRefOid")
            if isinstance(merge_ready_pr_payload, dict) and isinstance(merge_ready_pr_payload.get("headRefOid"), str)
            else None
        )
    target_branch = pr_payload.get("baseRefName") if isinstance(pr_payload, dict) else None
    validation_summary = context["latest_validation_summary"]
    validation_summary_errors: list[str] = []
    if pr_head and context.get("retained_item_context"):
        recovery_relative = str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])
        retained_validation_summary, retained_validation_errors = recovery_validation_summary_at_ref(
            target_root,
            recovery_relative,
            pr_head,
        )
        if retained_validation_errors:
            validation_summary_errors.extend(retained_validation_errors)
        elif retained_validation_summary is not None:
            validation_summary = retained_validation_summary
    validation_digest = validation_summary_digest(validation_summary)

    review_record, review_path, review_errors = load_review_record(target_root, item_id, context["review_entry"])
    review_missing = [*review_errors, *validation_summary_errors]
    review_head_binding_payload: dict[str, Any] | None = None
    if review_record is None and not review_missing:
        review_missing.append(f"missing review artifact: {review_path}")
    if review_record is not None:
        if review_record.get("decision") != "allow":
            review_missing.append("review decision is not allow")
        if review_record.get("kind") not in IMPLEMENTATION_REVIEW_KINDS:
            review_missing.append("review kind is not an implementation review")
        if not review_validation_summary_binding(review_record, validation_summary)["matches"]:
            review_missing.append("reviewed_validation_summary does not match retained validation summary")
        if pr_head:
            review_head_binding_payload, review_head_errors = review_head_binding_for_head(
                target_root,
                reviewed_head=review_record.get("reviewed_head"),
                target_head=pr_head,
                allowed_paths=allowed_post_review_carrier_paths(context, review_path),
            )
            review_missing.extend(review_head_errors)
    post_merge_review_diagnostic = post_merge_review_diagnostic_payload(
        pr_payload=pr_payload,
        review_record=review_record,
        review_path=review_path,
    )
    if post_merge_review_diagnostic.get("result") == "block":
        review_missing.extend(
            f"post-merge review diagnostic: {message}"
            for message in post_merge_review_diagnostic.get("missing_inputs", [])
        )
    subchecks.append(
        closeout_subcheck(
            check_id="review_record",
            source="review_record",
            profile=profile,
            required_for_closeout=True,
            trigger_reason="closeout consumes authored implementation review approval instead of raw review evidence",
            result="pass" if not review_missing else "block",
            fallback_to=None if not review_missing else "review",
            evidence_locator=review_path,
            missing_inputs=review_missing,
            item_id=item_id,
            reviewed_head=review_record.get("reviewed_head") if isinstance(review_record, dict) else None,
            head_sha=pr_head,
            head_binding=review_head_binding_payload,
            validation_summary_digest=validation_digest,
            post_merge_review_diagnostic=post_merge_review_diagnostic,
        )
    )

    status_subcheck = closeout_required_status_subcheck(
        target_root=target_root,
        profile=profile,
        owner=owner,
        repo_name=repo_name,
        pr_number=pr_number,
        pr_payload=pr_payload,
        pr_head=pr_head,
        pr_payload_file=pr_payload_file,
        status_checks_file=status_checks_file,
        branch_protection_file=branch_protection_file,
        ruleset_file=ruleset_file,
    )

    merge_ready_payload, merge_ready_locator, merge_ready_errors = latest_successful_execution_attempt(target_root, item_id, "merge-ready")
    merge_ready_missing = [f"merge-ready PR: {message}" for message in merge_ready_pr_errors or []]
    merge_ready_missing.extend(merge_ready_errors)
    merge_ready_source = "execution_attempt"
    merge_ready_trigger_reason = "closeout consumes retained merge-ready pass evidence instead of rerunning the full gate chain"
    merge_ready_evidence_locator = merge_ready_locator
    merge_ready_head = merge_ready_payload.get("head_sha") if isinstance(merge_ready_payload, dict) else None
    merge_ready_fallback_reason: str | None = None
    if merge_ready_expected_head is None:
        merge_ready_missing.append("merge-ready comparison PR head SHA is unavailable")
    if (
        merge_ready_payload is not None
        and merge_ready_expected_head
        and merge_ready_payload.get("head_sha") != merge_ready_expected_head
    ):
        if merge_ready_expected_source == "implementation_pr":
            merge_ready_missing.append("merge-ready execution_attempt head_sha does not match implementation PR head")
        else:
            merge_ready_missing.append("merge-ready execution_attempt head_sha does not match PR head")
    if (
        merge_ready_missing
        and merge_ready_expected_head
        and merge_ready_expected_head == pr_head
        and missing_versioned_execution_attempt(merge_ready_errors, "merge-ready")
        and status_subcheck.get("result") == "pass"
    ):
        merge_ready_missing = []
        merge_ready_source = "host_pr_checks"
        merge_ready_trigger_reason = (
            "closeout consumes fresh host required checks as legacy merge-ready evidence "
            "when no versioned execution_attempt was retained"
        )
        merge_ready_evidence_locator = status_subcheck.get("evidence_locator") if isinstance(status_subcheck.get("evidence_locator"), str) else None
        merge_ready_head = pr_head
        merge_ready_fallback_reason = "missing_versioned_execution_attempt"
    if (
        merge_ready_missing
        and merge_ready_expected_head
        and merge_ready_expected_source == "implementation_pr"
        and missing_versioned_execution_attempt(merge_ready_errors, "merge-ready")
        and merge_ready_pr_number is not None
        and merge_ready_pr_payload is not None
    ):
        implementation_status_subcheck = closeout_required_status_subcheck(
            target_root=target_root,
            profile=profile,
            owner=owner,
            repo_name=repo_name,
            pr_number=merge_ready_pr_number,
            pr_payload=merge_ready_pr_payload,
            pr_head=merge_ready_expected_head,
            pr_payload_file=None,
            status_checks_file=status_checks_file,
            branch_protection_file=branch_protection_file,
            ruleset_file=ruleset_file,
        )
        if implementation_status_subcheck.get("result") == "pass":
            merge_ready_missing = []
            merge_ready_source = "implementation_pr_host_checks"
            merge_ready_trigger_reason = (
                "terminal closeout carrier PR consumes fresh implementation PR host required checks "
                "as legacy merge-ready evidence when no versioned execution_attempt was retained"
            )
            merge_ready_evidence_locator = (
                implementation_status_subcheck.get("evidence_locator")
                if isinstance(implementation_status_subcheck.get("evidence_locator"), str)
                else None
            )
            merge_ready_head = merge_ready_expected_head
            merge_ready_fallback_reason = "terminal_closeout_carrier_pr"
    subchecks.append(
        closeout_subcheck(
            check_id="merge_ready_attempt",
            source=merge_ready_source,
            profile=profile,
            required_for_closeout=True,
            trigger_reason=merge_ready_trigger_reason,
            result="pass" if not merge_ready_missing else "block",
            fallback_to=None if not merge_ready_missing else "merge-ready",
            evidence_locator=merge_ready_evidence_locator,
            missing_inputs=merge_ready_missing,
            item_id=item_id,
            head_sha=merge_ready_head,
            expected_head_sha=merge_ready_expected_head,
            expected_pr_number=merge_ready_pr_number,
            expected_pr_role=merge_ready_expected_source,
            fallback_reason=merge_ready_fallback_reason,
            validation_summary_digest=validation_digest,
        )
    )

    pr_missing: list[str] = []
    if pr_payload is None:
        pr_missing.append("pr payload")
    else:
        if pr_payload.get("state") != "MERGED":
            pr_missing.append("pr is not merged")
        if not pr_head:
            pr_missing.append("PR head SHA is unavailable")
        if not isinstance(target_branch, str) or not target_branch:
            pr_missing.append("pr baseRefName is missing")
        if not merge_commit_sha:
            pr_missing.append("merge commit SHA is unavailable")
        if merge_commit_in_target is not True:
            pr_missing.append("target branch does not contain merge commit")
    subchecks.append(
        closeout_subcheck(
            check_id="pr_merge_backlink",
            source="github_pr",
            profile=profile,
            required_for_closeout=True,
            trigger_reason="closeout must link PR head, merge commit, and target branch containment",
            result="pass" if not pr_missing else "block",
            fallback_to=None if not pr_missing else "merge",
            evidence_locator=pr_payload_file or (f"github:pr/{pr_number}" if pr_number is not None else None),
            missing_inputs=pr_missing,
            head_sha=pr_head,
            merge_commit_sha=merge_commit_sha,
            target_branch=target_branch,
        )
    )

    subchecks.append(status_subcheck)
    return subchecks

def read_repo_relative_text_file(root: Path, path_str: str, *, label: str) -> tuple[str | None, list[str]]:
    path, errors = resolve_repo_relative_path(root, path_str, label=label)
    if errors:
        return None, errors
    if path is None:
        return None, [f"{label} is unavailable"]
    if not path.exists() or not path.is_file():
        return None, [f"{label} points to a missing file: {path_str}"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"failed to read {path_str}: {exc.strerror or exc}"]
    return text, []

def text_mentions_issue_number(text: object, issue_number: int) -> bool:
    if not isinstance(text, str) or not text:
        return False
    patterns = (
        rf"(?<![A-Za-z0-9])#\s*{issue_number}(?![A-Za-z0-9])",
        rf"(?i)\b(?:github\s+issue|issue|gh)\s*#?\s*{issue_number}\b",
        rf"(?i)\b(?:github:)?issue[/:#-]\s*{issue_number}\b",
        rf"(?i)\bWI-{issue_number}\b",
        rf"(?i)\bGH-{issue_number}(?:\b|-)",
    )
    return any(re.search(pattern, text) for pattern in patterns)

def exact_issue_locator_match(text: object, issue_number: int) -> bool:
    if not isinstance(text, str):
        return False
    normalized = text.strip().strip("`").strip()
    if not normalized:
        return False
    exact_values = {
        f"#{issue_number}",
        f"issue #{issue_number}",
        f"github issue #{issue_number}",
        f"github:issue/{issue_number}",
        f"issue/{issue_number}",
        f"issues/{issue_number}",
        f"/issues/{issue_number}",
        f"https://github.com/MC-and-his-Agents/Loom/issues/{issue_number}",
    }
    return normalized.casefold() in {value.casefold() for value in exact_values}

def retained_item_candidate_reasons(
    *,
    target_root: Path,
    work_item_path: Path,
    work_item: dict[str, object],
    issue_number: int,
) -> list[str]:
    reasons: list[str] = []
    item_id = str(work_item.get("item_id") or "")
    work_item_relative = relative_to_root(work_item_path, target_root)
    if work_item_relative == f".loom/work-items/WI-{issue_number}.md":
        reasons.append("canonical WI issue-number carrier path")
    if item_id == f"WI-{issue_number}":
        reasons.append("canonical WI issue-number item id")
    if re.match(rf"(?i)^GH-{issue_number}(?:$|-)", item_id):
        reasons.append("historical GH issue-number item id")

    metadata_fields = (
        item_id,
        work_item_path.stem,
        work_item.get("goal"),
        work_item.get("scope"),
        work_item.get("execution_path"),
        work_item.get("closing_condition"),
    )
    if any(text_mentions_issue_number(value, issue_number) for value in metadata_fields):
        reasons.append("work item title/body metadata references issue")

    artifacts = work_item.get("associated_artifacts")
    if isinstance(artifacts, list):
        if any(exact_issue_locator_match(value, issue_number) for value in artifacts):
            reasons.append("exact associated artifact issue locator")
        elif any(text_mentions_issue_number(value, issue_number) for value in artifacts):
            reasons.append("associated artifact references issue")

    recovery_relative = work_item.get("recovery_entry")
    if isinstance(recovery_relative, str) and recovery_relative:
        if text_mentions_issue_number(recovery_relative, issue_number):
            reasons.append("recovery entry locator references issue")
        recovery_path, recovery_errors = resolve_repo_relative_path(
            target_root,
            recovery_relative,
            label="retained recovery entry lookup",
        )
        if not recovery_errors and recovery_path is not None and recovery_path.exists():
            try:
                recovery_text = recovery_path.read_text(encoding="utf-8")
            except OSError:
                recovery_text = ""
            if text_mentions_issue_number(recovery_text, issue_number):
                reasons.append("recovery entry evidence references issue")

    deduped: list[str] = []
    seen: set[str] = set()
    for reason in reasons:
        if reason in seen:
            continue
        seen.add(reason)
        deduped.append(reason)
    return deduped

def retained_item_candidate_priority(reasons: list[str]) -> int:
    strong_reasons = {
        "canonical WI issue-number carrier path",
        "canonical WI issue-number item id",
        "exact associated artifact issue locator",
    }
    return 1 if any(reason in strong_reasons for reason in reasons) else 0

def explicit_retained_item_lookup(target_root: Path, item_id: str | None) -> dict[str, Any] | None:
    if item_id is None:
        return None
    item_id = item_id.strip()
    if not item_id:
        return {
            "item_id": None,
            "work_item_relative": None,
            "missing_inputs": ["explicit retained Work Item id is empty"],
            "diagnostics": [],
        }
    work_item_relative = f".loom/work-items/{item_id}.md"
    work_item_path = target_root / work_item_relative
    if not work_item_path.exists():
        return {
            "item_id": None,
            "work_item_relative": work_item_relative,
            "missing_inputs": [f"explicit retained Work Item `{item_id}` is missing: {work_item_relative}"],
            "diagnostics": [],
        }
    try:
        work_item, work_item_errors = parse_work_item(work_item_path, target_root)
    except OSError as exc:
        return {
            "item_id": None,
            "work_item_relative": work_item_relative,
            "missing_inputs": [f"explicit retained Work Item `{item_id}` is unreadable: {exc}"],
            "diagnostics": [],
        }
    if work_item_errors:
        return {
            "item_id": None,
            "work_item_relative": work_item_relative,
            "missing_inputs": [f"explicit retained Work Item `{item_id}` parse error: {message}" for message in work_item_errors],
            "diagnostics": [],
        }
    actual_item = str(work_item.get("item_id") or "")
    if actual_item != item_id:
        return {
            "item_id": None,
            "work_item_relative": work_item_relative,
            "missing_inputs": [f"explicit retained Work Item id mismatch: expected `{item_id}`, got `{actual_item}`"],
            "diagnostics": [],
        }
    return {
        "item_id": item_id,
        "work_item_relative": work_item_relative,
        "missing_inputs": [],
        "diagnostics": [
            {
                "item_id": item_id,
                "work_item_relative": work_item_relative,
                "reasons": ["explicit retained Work Item selector"],
                "priority": 2,
            }
        ],
    }

def closeout_retained_item_lookup(target_root: Path, issue_number: int | None) -> dict[str, Any]:
    if issue_number is None:
        return {"item_id": None, "work_item_relative": None, "missing_inputs": [], "diagnostics": []}

    work_items_dir = target_root / ".loom/work-items"
    if not work_items_dir.exists():
        return {"item_id": None, "work_item_relative": None, "missing_inputs": [], "diagnostics": []}

    candidates: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for work_item_path in sorted(work_items_dir.glob("*.md")):
        work_item_relative = relative_to_root(work_item_path, target_root)
        try:
            work_item, work_item_errors = parse_work_item(work_item_path, target_root)
        except OSError as exc:
            diagnostics.append(
                {
                    "work_item": work_item_relative,
                    "status": "unreadable",
                    "errors": [str(exc)],
                }
            )
            continue
        if work_item_errors:
            diagnostics.append(
                {
                    "work_item": work_item_relative,
                    "status": "parse_error",
                    "errors": work_item_errors,
                }
            )
            continue
        reasons = retained_item_candidate_reasons(
            target_root=target_root,
            work_item_path=work_item_path,
            work_item=work_item,
            issue_number=issue_number,
        )
        if not reasons:
            continue
        candidates.append(
            {
                "item_id": str(work_item["item_id"]),
                "work_item_relative": work_item_relative,
                "reasons": reasons,
                "priority": retained_item_candidate_priority(reasons),
            }
        )

    if not candidates:
        return {"item_id": None, "work_item_relative": None, "missing_inputs": [], "diagnostics": diagnostics}
    highest_priority = max(candidate["priority"] for candidate in candidates)
    prioritized_candidates = [candidate for candidate in candidates if candidate["priority"] == highest_priority]
    if len(prioritized_candidates) > 1:
        candidate_text = "; ".join(
            f"{candidate['item_id']} at {candidate['work_item_relative']} via {', '.join(candidate['reasons'])}"
            for candidate in prioritized_candidates
        )
        return {
            "item_id": None,
            "work_item_relative": None,
            "missing_inputs": [
                f"retained Work Item lookup for issue #{issue_number} is ambiguous: {candidate_text}"
            ],
            "diagnostics": [*diagnostics, *candidates],
        }
    candidate = prioritized_candidates[0]
    return {
        "item_id": candidate["item_id"],
        "work_item_relative": candidate["work_item_relative"],
        "missing_inputs": [],
        "diagnostics": [*diagnostics, *candidates],
    }

def closeout_expected_item_lookup(
    target_root: Path,
    issue_number: int | None,
    explicit_item: str | None = None,
) -> dict[str, Any]:
    explicit_lookup = explicit_retained_item_lookup(target_root, explicit_item)
    issue_lookup = closeout_retained_item_lookup(target_root, issue_number)
    if explicit_lookup is None:
        return issue_lookup
    missing_inputs = list(explicit_lookup.get("missing_inputs", []))
    explicit_item_id = retained_item_lookup_id(explicit_lookup)
    issue_item_id = retained_item_lookup_id(issue_lookup)
    if issue_number is not None and not missing_inputs:
        issue_candidates = [
            entry
            for entry in issue_lookup.get("diagnostics", [])
            if isinstance(entry, dict) and entry.get("item_id") == explicit_item_id
        ]
        if issue_item_id is not None and issue_item_id != explicit_item_id:
            missing_inputs.append(
                f"explicit retained Work Item `{explicit_item_id}` does not match retained-item lookup for issue #{issue_number}: `{issue_item_id}`"
            )
        elif issue_item_id is None and not issue_candidates:
            missing_inputs.append(
                f"explicit retained Work Item `{explicit_item_id}` could not be confirmed against issue #{issue_number}"
            )
    return {
        "item_id": explicit_item_id if not missing_inputs else None,
        "work_item_relative": retained_item_lookup_work_item_relative(explicit_lookup) if not missing_inputs else None,
        "missing_inputs": missing_inputs,
        "diagnostics": [
            {
                "kind": "explicit-retained-item-lookup",
                "lookup": explicit_lookup,
            },
            {
                "kind": "issue-retained-item-lookup",
                "issue": issue_number,
                "lookup": issue_lookup,
            },
        ],
    }

def closeout_expected_item_id(target_root: Path, issue_number: int | None) -> str | None:
    lookup = closeout_retained_item_lookup(target_root, issue_number)
    if lookup.get("missing_inputs"):
        return None
    item_id = lookup.get("item_id")
    return str(item_id) if isinstance(item_id, str) and item_id else None

def retained_item_lookup_missing_inputs(lookup: dict[str, Any]) -> list[str]:
    missing_inputs = lookup.get("missing_inputs")
    if not isinstance(missing_inputs, list):
        return []
    return [f"retained-item lookup: {message}" for message in missing_inputs]

def retained_item_lookup_id(lookup: dict[str, Any]) -> str | None:
    item_id = lookup.get("item_id")
    return str(item_id) if isinstance(item_id, str) and item_id else None

def retained_item_lookup_work_item_relative(lookup: dict[str, Any]) -> str | None:
    work_item_relative = lookup.get("work_item_relative")
    return str(work_item_relative) if isinstance(work_item_relative, str) and work_item_relative else None

def terminal_state_from_checkpoint(checkpoint: str) -> str | None:
    normalized = normalize_checkpoint(checkpoint)
    if normalized == "closed_out":
        return "closed_out"
    if normalized == "merged":
        return "merged"
    if normalized == "retired":
        return "retired"
    if normalized == "archived":
        return "deferred"
    return None

def render_terminal_closeout_metadata(metadata: dict[str, str]) -> list[str]:
    return [
        "## Terminal Closeout Metadata",
        "",
        f"- Terminal State: {metadata['terminal_state']}",
        f"- Issue: {metadata['issue']}",
        f"- PR: {metadata['pr']}",
        f"- Merge Commit: {metadata['merge_commit']}",
        f"- Target Branch: {metadata['target_branch']}",
        f"- Closed At: {metadata['closed_at']}",
        f"- Evidence Locator: {metadata['evidence_locator']}",
    ]

def write_terminal_closeout_metadata(path: Path, metadata: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    rendered = "\n".join(render_terminal_closeout_metadata(metadata)).rstrip() + "\n"
    pattern = re.compile(r"(?ms)^## Terminal Closeout Metadata\n\n.*?(?=^## |\Z)")
    if pattern.search(text):
        updated = pattern.sub(rendered, text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + rendered
    path.write_text(updated, encoding="utf-8")

def carrier_closeout_sync_payload(target_root: Path, output_relative: str, expected_item: str | None, args: argparse.Namespace) -> dict[str, Any]:
    context, context_errors = load_context(target_root, output_relative, expected_item)
    missing_inputs: list[str] = [f"fact-chain: {message}" for message in context_errors]
    if context_errors:
        return {
            "command": "carrier",
            "operation": "closeout-sync",
            "schema_version": "loom-carrier-closeout-sync/v1",
            "result": "block",
            "summary": "carrier closeout sync could not read the target progress carrier.",
            "missing_inputs": missing_inputs,
            "fallback_to": "admission",
            "dry_run": args.dry_run,
            "host_mutations": False,
            "host_actions": [],
            "versioned_carrier_updates": [],
        }
    assert context
    inferred_state = terminal_state_from_checkpoint(context["current_checkpoint"])
    terminal_state = args.terminal_state or inferred_state
    if terminal_state is None:
        missing_inputs.append("terminal-state is required when current checkpoint is not terminal")
    metadata = {
        "terminal_state": terminal_state or "not_applicable",
        "issue": args.issue or "not_applicable",
        "pr": args.pr or "not_applicable",
        "merge_commit": args.merge_commit or "not_applicable",
        "target_branch": args.target_branch or "not_applicable",
        "closed_at": args.closed_at or "not_applicable",
        "evidence_locator": args.evidence_locator or "not_applicable",
    }
    if metadata["terminal_state"] in {"closed_out", "merged", "absorbed"}:
        for field_name in ("issue", "pr", "merge_commit", "target_branch", "closed_at", "evidence_locator"):
            if metadata[field_name] == "not_applicable":
                missing_inputs.append(f"{field_name.replace('_', '-')} is required for terminal state `{metadata['terminal_state']}`")
    update = {
        "path": relative_to_root(context["recovery_path"], target_root),
        "kind": "terminal-closeout-metadata",
        "planned_action": "write" if not args.dry_run else "preview",
        "metadata": metadata,
    }
    if not args.dry_run and not missing_inputs:
        write_terminal_closeout_metadata(context["recovery_path"], metadata)
    result = "block" if missing_inputs else "pass"
    return {
        "command": "carrier",
        "operation": "closeout-sync",
        "schema_version": "loom-carrier-closeout-sync/v1",
        "result": result,
        "summary": (
            "carrier closeout sync wrote structured terminal metadata to versioned progress carriers."
            if result == "pass" and not args.dry_run
            else "carrier closeout sync dry-run produced versioned progress carrier updates."
            if result == "pass"
            else "carrier closeout sync is blocked until terminal metadata inputs are explicit."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "closeout",
        "dry_run": args.dry_run,
        "host_mutations": False,
        "host_actions": [],
        "versioned_carrier_updates": [update],
        "item": {"id": context["item_id"]},
    }

def parse_terminal_closeout_metadata(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    in_section = False
    metadata: dict[str, str] = {}
    for line in lines:
        if line.strip() == "## Terminal Closeout Metadata":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        normalized = key.strip().lower().replace(" ", "_").replace("-", "_")
        metadata[normalized] = value.strip()
    return metadata

def parse_optional_number(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group(0))
    return None

def extract_single_number(pattern: re.Pattern[str], texts: list[str]) -> int | None:
    values: set[int] = set()
    for text in texts:
        values.update(int(match.group("number")) for match in pattern.finditer(text))
    return next(iter(values)) if len(values) == 1 else None

def closeout_queue_fixture_by_item(target_root: Path, queue_file: str | None) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not queue_file:
        return {}, []
    payload, errors = load_optional_json_fixture(target_root, queue_file, label="closeout queue fixture")
    if errors:
        return {}, errors
    if isinstance(payload, dict):
        raw_items = payload.get("items")
        if raw_items is None:
            raw_items = payload.get("queue")
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raw_items = None
    if not isinstance(raw_items, list):
        return {}, ["closeout queue fixture must contain an items array"]
    by_item: dict[str, dict[str, Any]] = {}
    fixture_errors: list[str] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            fixture_errors.append(f"closeout queue fixture item {index} must be an object")
            continue
        item_id = raw_item.get("item_id") or raw_item.get("item")
        if not isinstance(item_id, str) or not item_id:
            fixture_errors.append(f"closeout queue fixture item {index} is missing item_id")
            continue
        by_item[item_id] = raw_item
    return by_item, fixture_errors

def normalize_host_completion(raw: Any, metadata: dict[str, str]) -> dict[str, Any]:
    if isinstance(raw, dict):
        host = dict(raw)
        source = str(host.get("source") or "fixture")
    else:
        host = {}
        source = "terminal_metadata" if metadata else "local_scan"
    merge_commit = str(host.get("merge_commit") or host.get("mergeCommit") or metadata.get("merge_commit") or "").strip()
    target_branch = str(host.get("target_branch") or host.get("baseRefName") or metadata.get("target_branch") or "").strip()
    closed_at = str(host.get("closed_at") or host.get("closedAt") or host.get("mergedAt") or metadata.get("closed_at") or "").strip()
    evidence_locator = str(host.get("evidence_locator") or metadata.get("evidence_locator") or "").strip()
    issue_closed = host.get("issue_closed")
    pr_merged = host.get("pr_merged")
    if issue_closed is None and str(host.get("issue_state") or host.get("state") or "").lower() == "closed":
        issue_closed = True
    if pr_merged is None and str(host.get("pr_state") or "").upper() == "MERGED":
        pr_merged = True
    if pr_merged is None and merge_commit:
        pr_merged = True
    if issue_closed is None and metadata.get("issue") and metadata.get("issue") != "not_applicable":
        issue_closed = True
    if pr_merged is None and metadata.get("pr") and metadata.get("pr") != "not_applicable" and merge_commit:
        pr_merged = True
    missing: list[str] = []
    if issue_closed is not True:
        missing.append("issue_closed")
    if pr_merged is not True:
        missing.append("pr_merged")
    for field_name, value in (
        ("merge_commit", merge_commit),
        ("target_branch", target_branch),
        ("closed_at", closed_at),
        ("evidence_locator", evidence_locator),
    ):
        if not value or value == "not_applicable":
            missing.append(field_name)
    if not raw and not metadata:
        result = "unknown"
        missing = ["host_completion"]
    else:
        result = "pass" if not missing else "block"
    return {
        "result": result,
        "source": source,
        "issue_closed": issue_closed if issue_closed is not None else "unknown",
        "pr_merged": pr_merged if pr_merged is not None else "unknown",
        "merge_commit": merge_commit or None,
        "target_branch": target_branch or None,
        "closed_at": closed_at or None,
        "evidence_locator": evidence_locator or None,
        "missing_inputs": missing,
    }

def terminal_metadata_complete(metadata: dict[str, str]) -> bool:
    if not metadata:
        return False
    terminal_state = metadata.get("terminal_state")
    if terminal_state in {None, "", "not_applicable"}:
        return False
    required = ("issue", "pr", "merge_commit", "target_branch", "closed_at", "evidence_locator")
    return all(metadata.get(field) and metadata.get(field) != "not_applicable" for field in required)

def closeout_queue_next_command(
    *,
    mode: str,
    item_id: str,
    issue_number: int | None,
    pr_number: int | None,
    host_completion: dict[str, Any],
) -> str | None:
    if mode == "light_carrier_sync":
        if issue_number is None or pr_number is None:
            return None
        merge_commit = host_completion.get("merge_commit")
        target_branch = host_completion.get("target_branch")
        closed_at = host_completion.get("closed_at")
        evidence_locator = host_completion.get("evidence_locator")
        if not all(isinstance(value, str) and value for value in (merge_commit, target_branch, closed_at, evidence_locator)):
            return None
        return (
            "loom carrier closeout-sync --target <repo> "
            f"--item {item_id} --issue {issue_number} --pr {pr_number} "
            f"--merge-commit {merge_commit} --target-branch {target_branch} "
            f"--closed-at {closed_at} --evidence-locator {shlex.quote(evidence_locator)} --json"
        )
    if mode == "batched_closeout" and issue_number is not None:
        return f"loom repair plan --target <repo> --issue {issue_number} --json"
    if mode == "full_closeout" and issue_number is not None:
        command = f"loom closeout --target <repo> --issue {issue_number}"
        if pr_number is not None:
            command += f" --pr {pr_number}"
        return command + " --json"
    return None

def classify_closeout_queue_item(
    *,
    item_id: str,
    work_item_relative: str,
    recovery_relative: str | None,
    checkpoint: str | None,
    terminal_metadata: dict[str, str],
    host_completion: dict[str, Any],
    issue_number: int | None,
    pr_number: int | None,
) -> dict[str, Any]:
    carrier_checkpoint = normalize_checkpoint(checkpoint or "")
    carrier_terminal = carrier_checkpoint in TERMINAL_CHECKPOINTS or terminal_state_from_checkpoint(carrier_checkpoint) is not None
    metadata_present = bool(terminal_metadata)
    metadata_complete = terminal_metadata_complete(terminal_metadata)
    missing_inputs = list(host_completion.get("missing_inputs", []))
    host_result = host_completion.get("result")
    if issue_number is None:
        missing_inputs.append("issue_number")
    if pr_number is None and host_result in {"pass", "block"}:
        missing_inputs.append("pr_number")

    if metadata_complete and carrier_terminal and host_result in {"pass", "unknown"}:
        mode = "auto_no_op"
        next_action = "none"
        fallback_to = None
        missing_inputs = []
    elif host_result == "pass" and carrier_terminal:
        mode = "light_carrier_sync"
        next_action = "preview terminal carrier metadata sync"
        fallback_to = "loom carrier closeout-sync --target <repo> --json"
    elif host_result == "pass" and not carrier_terminal:
        mode = "batched_closeout"
        next_action = "plan stale active carrier closeout"
        fallback_to = "loom repair plan --target <repo> --issue <issue> --json"
    elif host_result == "block" and issue_number is not None and pr_number is not None:
        mode = "full_closeout"
        next_action = "run full closeout check with host readback"
        fallback_to = "loom closeout --target <repo> --issue <issue> --pr <pr> --json"
    else:
        mode = "blocked"
        next_action = "provide retained host completion evidence before queue classification"
        fallback_to = "manual-reconciliation"
        if host_result == "unknown" and "host_completion" not in missing_inputs:
            missing_inputs.append("host_completion")

    next_command = closeout_queue_next_command(
        mode=mode,
        item_id=item_id,
        issue_number=issue_number,
        pr_number=pr_number,
        host_completion=host_completion,
    )
    if mode != "auto_no_op" and next_command is None:
        if "next_command_inputs" not in missing_inputs:
            missing_inputs.append("next_command_inputs")
        if mode != "blocked":
            mode = "blocked"
            next_action = "provide missing inputs before queue classification"
            fallback_to = "manual-reconciliation"

    return {
        "item_id": item_id,
        "work_item_relative": work_item_relative,
        "issue_number": issue_number,
        "pr_number": pr_number,
        "host_completion": host_completion,
        "carrier_checkpoint": carrier_checkpoint or None,
        "terminal_metadata_present": metadata_present,
        "merge_commit": host_completion.get("merge_commit") or terminal_metadata.get("merge_commit"),
        "target_branch": host_completion.get("target_branch") or terminal_metadata.get("target_branch"),
        "closed_at": host_completion.get("closed_at") or terminal_metadata.get("closed_at"),
        "reconciliation_result": "not_run",
        "closeout_mode": mode,
        "evidence_locator": host_completion.get("evidence_locator") or terminal_metadata.get("evidence_locator"),
        "next_action": next_action,
        "next_command": next_command,
        "missing_inputs": dedupe_strings(missing_inputs),
        "fallback_to": fallback_to,
        **({"recovery_relative": recovery_relative} if recovery_relative else {}),
    }

def closeout_queue_status_payload(
    *,
    target_root: Path,
    output_relative: str,
    issue_filters: list[int],
    item_filters: list[str],
    queue_file: str | None,
) -> dict[str, Any]:
    if not issue_filters and not item_filters and not queue_file:
        return {
            "command": "closeout-queue",
            "operation": "status",
            "schema_version": "loom-closeout-queue-status/v1",
            "result": "block",
            "mode": "blocked",
            "summary": "closeout queue status requires an explicit queue input before scanning retained Work Items.",
            "target": str(target_root),
            "output": output_relative,
            "mutates": False,
            "host_mutations": False,
            "carrier_mutations": False,
            "item_count": 0,
            "mode_counts": {
                "auto_no_op": 0,
                "light_carrier_sync": 0,
                "batched_closeout": 0,
                "full_closeout": 0,
                "blocked": 0,
            },
            "items": [],
            "diagnostics": [],
            "missing_inputs": ["queue_input"],
            "fallback_to": "manual-reconciliation",
            "next_action": "provide --issue, --item, or --queue-file before reading closeout queue status",
            "next_command": "loom closeout queue status --target <repo> --issue <issue> --json",
        }
    fixture_by_item, fixture_errors = closeout_queue_fixture_by_item(target_root, queue_file)
    work_items_dir = target_root / ".loom" / "work-items"
    items: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    if not work_items_dir.exists():
        return {
            "command": "closeout-queue",
            "operation": "status",
            "schema_version": "loom-closeout-queue-status/v1",
            "result": "pass" if not fixture_errors else "block",
            "mode": "auto_no_op" if not fixture_errors else "blocked",
            "summary": "closeout queue status found no retained Work Items.",
            "target": str(target_root),
            "mutates": False,
            "host_mutations": False,
            "carrier_mutations": False,
            "items": [],
            "missing_inputs": fixture_errors,
            "fallback_to": "manual-reconciliation" if fixture_errors else None,
            "next_action": "none" if not fixture_errors else "fix closeout queue fixture inputs",
            "next_command": None,
        }

    requested_items = set(item_filters)
    requested_issues = set(issue_filters)
    for work_item_path in sorted(work_items_dir.glob("*.md")):
        work_item_relative = relative_to_root(work_item_path, target_root)
        try:
            work_item, work_item_errors = parse_work_item(work_item_path, target_root)
        except OSError as exc:
            diagnostics.append({"work_item_relative": work_item_relative, "status": "unreadable", "missing_inputs": [str(exc)]})
            continue
        if work_item_errors:
            diagnostics.append({"work_item_relative": work_item_relative, "status": "parse_error", "missing_inputs": work_item_errors})
            continue
        item_id = str(work_item.get("item_id") or work_item_path.stem)
        if requested_items and item_id not in requested_items:
            continue
        recovery_relative = str(work_item.get("recovery_entry") or "")
        recovery_path = target_root / recovery_relative if recovery_relative else None
        recovery_entry: dict[str, Any] = {}
        recovery_errors: list[str] = []
        recovery_text = ""
        if recovery_path is None or not recovery_path.exists():
            recovery_errors.append(f"missing recovery entry: {recovery_relative or '<missing>'}")
        else:
            recovery_text = recovery_path.read_text(encoding="utf-8")
            recovery_entry, recovery_errors = parse_recovery_entry(recovery_path, target_root, recovery_relative)
        fixture = fixture_by_item.get(item_id, {})
        terminal_metadata = parse_terminal_closeout_metadata(recovery_path) if recovery_path is not None else {}
        texts = [work_item_path.read_text(encoding="utf-8"), recovery_text]
        issue_number = (
            parse_optional_number(fixture.get("issue_number"))
            or parse_optional_number(terminal_metadata.get("issue"))
            or extract_single_number(GITHUB_ISSUE_URL_RE, texts)
            or extract_single_number(GITHUB_ISSUE_REF_RE, texts)
            or (int(item_id.removeprefix("WI-")) if re.fullmatch(r"WI-\d+", item_id) else None)
        )
        pr_number = (
            parse_optional_number(fixture.get("pr_number"))
            or parse_optional_number(terminal_metadata.get("pr"))
            or extract_single_number(GITHUB_PR_URL_RE, texts)
            or extract_single_number(GITHUB_PR_REF_RE, texts)
        )
        if requested_issues and issue_number not in requested_issues:
            continue
        host_completion = normalize_host_completion(fixture.get("host_completion"), terminal_metadata)
        if recovery_errors:
            host_completion["result"] = "block"
            host_completion["missing_inputs"] = dedupe_strings([*host_completion.get("missing_inputs", []), *recovery_errors])
        item_payload = classify_closeout_queue_item(
            item_id=item_id,
            work_item_relative=work_item_relative,
            recovery_relative=recovery_relative or None,
            checkpoint=str(recovery_entry.get("current_checkpoint") or ""),
            terminal_metadata=terminal_metadata,
            host_completion=host_completion,
            issue_number=issue_number,
            pr_number=pr_number,
        )
        items.append(item_payload)

    mode_rank = {
        "blocked": 5,
        "full_closeout": 4,
        "batched_closeout": 3,
        "light_carrier_sync": 2,
        "auto_no_op": 1,
    }
    actionable_items = [item for item in items if item.get("closeout_mode") != "auto_no_op"]
    blocked_items = [item for item in items if item.get("closeout_mode") == "blocked"]
    unmatched_filters: list[str] = []
    matched_item_ids = {str(item.get("item_id")) for item in items if item.get("item_id")}
    matched_issue_numbers = {item.get("issue_number") for item in items if item.get("issue_number") is not None}
    for requested_item in sorted(requested_items):
        if requested_item not in matched_item_ids:
            unmatched_filters.append(f"item not found: {requested_item}")
    for requested_issue in sorted(requested_issues):
        if requested_issue not in matched_issue_numbers:
            unmatched_filters.append(f"issue not found: {requested_issue}")

    if fixture_errors:
        mode = "blocked"
        next_action = "fix closeout queue fixture inputs"
        next_command = None
    elif unmatched_filters:
        mode = "blocked"
        next_action = "correct closeout queue filters before treating the queue as empty"
        next_command = None
    elif not items or not actionable_items:
        mode = "auto_no_op"
        next_action = "none"
        next_command = None
    elif blocked_items:
        mode = "blocked"
        next_action = "resolve blocked queue items before applying closeout sync"
        next_command = None
    elif len(actionable_items) > 1:
        mode = "batched_closeout"
        next_action = "process actionable queue items in listed order"
        next_command = "review items[].next_command"
    else:
        only = actionable_items[0]
        mode = str(only.get("closeout_mode"))
        next_action = str(only.get("next_action"))
        next_command = only.get("next_command")
    result = "block" if mode == "blocked" else "pass"
    missing_inputs = dedupe_strings(
        [
            *fixture_errors,
            *unmatched_filters,
            *[
                f"{item.get('item_id')}: {message}"
                for item in items
                for message in item.get("missing_inputs", [])
                if item.get("closeout_mode") == "blocked"
            ],
        ]
    )
    return {
        "command": "closeout-queue",
        "operation": "status",
        "schema_version": "loom-closeout-queue-status/v1",
        "result": result,
        "mode": mode,
        "summary": (
            "closeout queue status found no post-merge residue requiring action."
            if mode == "auto_no_op"
            else "closeout queue status classified retained post-merge residue."
            if result == "pass"
            else "closeout queue status is blocked until required retained host inputs are available."
        ),
        "target": str(target_root),
        "output": output_relative,
        "mutates": False,
        "host_mutations": False,
        "carrier_mutations": False,
        "item_count": len(items),
        "mode_counts": {name: sum(1 for item in items if item.get("closeout_mode") == name) for name in sorted(mode_rank, key=mode_rank.get)},
        "items": items,
        "diagnostics": diagnostics,
        "missing_inputs": missing_inputs,
        "fallback_to": "manual-reconciliation" if result == "block" else None,
        "next_action": next_action,
        "next_command": next_command,
    }

def handle_closeout_queue(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    payload = closeout_queue_status_payload(
        target_root=target_root,
        output_relative=args.output,
        issue_filters=args.issue,
        item_filters=args.item,
        queue_file=args.queue_file,
    )
    return emit(payload)

def lifecycle_admission_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int | None,
    fr_number: int | None = None,
    pr_number: int | None = None,
    branch_name: str | None = None,
    intent: str,
) -> dict[str, Any]:
    """Consume native admission before an execution entrypoint, never a carrier."""

    detected_owner, detected_repo = detect_github_repo(target_root)
    effective_owner = owner or detected_owner
    effective_repo = repo_name or detected_repo
    if not detected_owner or not detected_repo or not effective_owner or not effective_repo:
        return {
            "schema_version": "loom-host-lifecycle-admission/v1",
            "result": "block",
            "lifecycle_state": "missing_subject",
            "subject": None,
            "admission_state": "host_subject_required",
            "authority_verdict": authority_verdict(),
            "primary_remediation": "restore a readable target origin GitHub owner/repo binding before entering execution",
            "carrier_mutations": False,
            "missing_inputs": ["target origin GitHub owner/repo"],
        }
    subject_readback = github_lifecycle_subject_readback(
        target_root,
        effective_owner,
        effective_repo,
        issue_number=issue_number,
        fr_number=fr_number,
        pr_number=pr_number,
        branch_name=branch_name or (git_branch(target_root) if issue_number is None and fr_number is None and pr_number is None else None),
        intent=intent,
        target_owner=detected_owner,
        target_repo=detected_repo,
    )
    issue_number = subject_readback.get("issue_number") if isinstance(subject_readback.get("issue_number"), int) else None
    if subject_readback.get("result") != "pass" or issue_number is None:
        return {
            "schema_version": "loom-host-lifecycle-admission/v1",
            "result": "block",
            "lifecycle_state": "missing_subject",
            "subject": None,
            "subject_readback": subject_readback,
            "admission_state": "host_subject_required",
            "authority_verdict": authority_verdict(),
            "primary_remediation": "provide --issue <work-item-or-fr> or bind the branch to one PR with exactly one native closing Work Item",
            "carrier_mutations": False,
            "missing_inputs": list(subject_readback.get("errors") or ["host lifecycle subject"]),
        }
    admission = github_fr_wi_admission_payload(
        target_root=target_root,
        owner=effective_owner,
        repo_name=effective_repo,
        issue_number=issue_number,
        intent=intent,
        task=None,
        blocked_by=[],
        work_item_number=None,
        apply=False,
        lifecycle_only=True,
    )
    verdict = admission.get("lifecycle_verdict")
    if not isinstance(verdict, dict):
        verdict = lifecycle_admission_verdict(admission)
    return {**verdict, "subject_readback": subject_readback, "admission": admission}

def reconciliation_result(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "pass"
    rank = {"warn": 1, "fix-needed": 2, "block": 3}
    highest = max(rank.get(str(finding.get("severity")), 0) for finding in findings)
    if highest == 3:
        return "block"
    if highest == 2:
        return "fix-needed"
    return "warn"

def reconciliation_audit_payload(
    *,
    target_root: Path,
    expected_item: str | None,
    phase_number: int | None,
    fr_number: int | None,
    issue_number: int | None,
    pr_number: int | None,
    project_number: int | None,
    branch_name: str | None,
    owner: str,
    repo_name: str,
    issue_payload_file: str | None = None,
    pr_payload_file: str | None = None,
    project_payload_file: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    missing_inputs: list[str] = []
    findings: list[dict[str, Any]] = []

    if issue_number is None and pr_number is None and project_number is None:
        missing_inputs.append("issue/pr/project")

    suite_gate_validation: dict[str, Any] | None = None
    expected_reconciliation_lookup = closeout_expected_item_lookup(target_root, issue_number, expected_item)
    missing_inputs.extend(retained_item_lookup_missing_inputs(expected_reconciliation_lookup))
    expected_reconciliation_item = retained_item_lookup_id(expected_reconciliation_lookup)
    expected_reconciliation_work_item = retained_item_lookup_work_item_relative(expected_reconciliation_lookup)
    if expected_reconciliation_item is not None:
        suite_context, suite_context_errors = load_retained_item_context(
            target_root,
            ".loom/bootstrap/init-result.json",
            expected_reconciliation_item,
            expected_reconciliation_work_item,
        )
        if suite_context_errors:
            suite_gate_validation = {
                "schema_version": "loom-suite-gate-validation/v1",
                "surface": "closeout",
                "result": "block",
                "summary": "suite gate context is unreadable for reconciliation audit.",
                "missing_inputs": suite_context_errors,
                "fallback_to": "fact-chain",
                "authority_boundary": {
                    "role": "gate_input_evidence",
                    "does_not_replace": [
                        "work_item",
                        "review_record",
                        "merge_ready_result",
                        "closeout_evidence",
                        "docs_source_truth",
                    ],
                },
                "consumed_locators": {"evidence_map": None, "task_carriers": []},
                "validations": {},
            }
        elif suite_gate_required_for_surface(suite_context, surface="closeout"):
            suite_gate_validation = suite_gate_validation_payload(suite_context, surface="closeout")
        else:
            suite_gate_validation = suite_gate_not_applicable_payload(suite_context, surface="closeout")
        findings.extend(
            suite_gate_reconciliation_findings(
                suite_gate_validation,
                subject=f"issue #{issue_number}" if issue_number is not None else expected_reconciliation_item,
            )
        )

    binding_payload = github_binding_payload(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        phase_number=phase_number,
        fr_number=fr_number,
        issue_number=issue_number,
        pr_number=pr_number,
        branch_name=branch_name,
        sync=False,
        dry_run=False,
        require_complete_chain=False,
    )
    binding = binding_payload.get("binding") if isinstance(binding_payload.get("binding"), dict) else None
    binding_findings = binding.get("findings") if isinstance(binding, dict) else None
    if isinstance(binding_findings, list):
        for finding in binding_findings:
            if isinstance(finding, dict):
                findings.append(
                    make_reconciliation_finding(
                        kind="binding_failure",
                        severity="block",
                        subject=str(finding.get("subject") or "github profile binding"),
                        evidence={"binding": finding.get("evidence", {}), "binding_result": binding_payload.get("result")},
                        recommended_action="repair the GitHub profile binding chain before reconciliation or closeout.",
                        category="gate_failure",
                        fallback_to="manual-reconciliation",
                    )
                )

    issue_payload: dict[str, Any] | None = None
    issue_id: str | None = None
    parent_payload: dict[str, Any] | None = None
    if issue_number is not None:
        fixture_issue_payload, fixture_issue_errors = load_optional_json_fixture(
            target_root,
            issue_payload_file,
            label="issue payload fixture",
        )
        if fixture_issue_errors:
            issue_payload = None
            issue_errors = fixture_issue_errors
        elif isinstance(fixture_issue_payload, dict):
            issue_payload, issue_errors = normalize_issue_fixture_payload(fixture_issue_payload)
        else:
            issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
        if issue_errors:
            missing_inputs.extend(f"issue: {message}" for message in issue_errors)
        elif issue_payload is not None:
            raw_issue_id = issue_payload.get("id")
            if isinstance(raw_issue_id, str) and raw_issue_id:
                issue_id = raw_issue_id
            if fixture_issue_payload is None:
                issue_tree, issue_tree_errors = issue_tree_payload(target_root, owner, repo_name, issue_number)
                if issue_tree_errors:
                    issue_payload["sub_issue_tree"] = {
                        "status": "unavailable",
                        "reason": "GraphQL-only parent/sub-issue tree could not be read.",
                        "errors": issue_tree_errors,
                        "budget_guard": graphql_budget_guard("native_parent_sub_issue_tree", issue_tree_errors),
                    }
                elif issue_tree is not None:
                    issue_payload = {**issue_payload, **issue_tree}
                    parent = issue_payload.get("parent")
                    if isinstance(parent, dict):
                        parent_payload = parent
                native_dependencies = github_issue_dependencies_payload(target_root, owner, repo_name, issue_number)
                dependency_graph = dependency_graph_payload(
                    issue_number=issue_number,
                    issue_payload=issue_payload,
                    native_dependency_payload=native_dependencies,
                )
                for finding in dependency_graph.get("findings", []):
                    if isinstance(finding, dict) and finding.get("kind") in {
                        "missing_native_edge",
                        "stale_native_edge",
                        "open_blocker_executable_conflict",
                        "native_dependency_unreadable",
                    }:
                        findings.append(finding)

    pr_payload: dict[str, Any] | None = None
    merge_commit_sha: str | None = None
    merge_commit_in_main = False
    if pr_number is not None:
        fixture_pr_payload, fixture_pr_errors = load_optional_json_fixture(
            target_root,
            pr_payload_file,
            label="PR payload fixture",
        )
        if fixture_pr_errors:
            pr_payload = None
            pr_errors = fixture_pr_errors
        elif isinstance(fixture_pr_payload, dict):
            pr_payload, pr_errors = normalize_pr_fixture_payload(fixture_pr_payload)
        else:
            pr_payload, pr_errors = github_pr_payload(target_root, owner, repo_name, pr_number)
        if pr_errors:
            missing_inputs.extend(f"pr: {message}" for message in pr_errors)
        elif pr_payload is not None:
            merge_commit = pr_payload.get("mergeCommit")
            if isinstance(merge_commit, dict):
                oid = merge_commit.get("oid")
                if isinstance(oid, str) and oid:
                    merge_commit_sha = oid
                    base_ref = pr_payload.get("baseRefName")
                    if isinstance(base_ref, str) and base_ref:
                        merge_commit_in_main = contains_merged_commit(target_root, merge_commit_sha, base_ref)
                    else:
                        findings.append(
                            make_reconciliation_finding(
                                kind="merge_signal_drift",
                                severity="block",
                                subject=f"PR #{pr_number} merge signal",
                                evidence={
                                    "pr_state": pr_payload.get("state"),
                                    "merge_commit": merge_commit_sha,
                                    "baseRefName": base_ref,
                                },
                                recommended_action="re-read the PR base branch before closeout or reconciliation.",
                                category="binding_failure",
                                fallback_to="manual-reconciliation",
                            )
                        )
            if pr_payload.get("state") == "MERGED" and (not merge_commit_sha or not merge_commit_in_main):
                findings.append(
                    make_reconciliation_finding(
                        kind="merge_signal_drift",
                        severity="block",
                        subject=f"PR #{pr_number} merge signal",
                        evidence={
                            "pr_state": pr_payload.get("state"),
                            "merge_commit": merge_commit_sha,
                            "merge_commit_in_main": merge_commit_in_main,
                        },
                        recommended_action="repair or re-read the merge commit basis before closeout.",
                        category="drift",
                        fallback_to="manual-reconciliation",
                    )
                )
            if pr_payload.get("state") == "MERGED" and expected_reconciliation_item is not None:
                review_context, review_context_errors = load_retained_item_context(
                    target_root,
                    ".loom/bootstrap/init-result.json",
                    expected_reconciliation_item,
                    expected_reconciliation_work_item,
                )
                review_record = None
                review_path = None
                if not review_context_errors:
                    review_record, review_path, _review_errors = load_review_record(
                        target_root,
                        expected_reconciliation_item,
                        review_context["review_entry"],
                    )
                diagnostic = post_merge_review_diagnostic_payload(
                    pr_payload=pr_payload,
                    review_record=review_record,
                    review_path=review_path,
                )
                if isinstance(diagnostic.get("finding"), dict):
                    findings.append(
                        make_reconciliation_finding(
                            kind=str(diagnostic["finding"].get("kind") or "post_merge_review_bypass"),
                            severity="block",
                            subject=str(diagnostic["finding"].get("subject") or f"PR #{pr_number}"),
                            evidence=diagnostic["finding"].get("evidence", {}),
                            recommended_action=str(diagnostic["finding"].get("recommended_action")),
                            category="review_bypass",
                            fallback_to="manual-reconciliation",
                            repair_plan=diagnostic.get("repair_plan"),
                        )
                    )

    merged_issue_open = False
    if issue_payload is not None and pr_payload is not None:
        if issue_payload.get("state") == "OPEN" and pr_payload.get("state") == "MERGED" and merge_commit_sha and merge_commit_in_main:
            merged_issue_open = True
            findings.append(
                make_reconciliation_finding(
                    kind="merged_but_open",
                    severity="fix-needed",
                    subject=f"issue #{issue_number}",
                    evidence={
                        "issue_state": issue_payload.get("state"),
                        "pr_number": pr_number,
                        "pr_state": pr_payload.get("state"),
                        "merge_commit": merge_commit_sha,
                        "merge_commit_in_main": merge_commit_in_main,
                    },
                    recommended_action="close the merged issue or run reconciliation sync after reviewing the evidence.",
                )
            )

    parent_scope: dict[str, Any] | None = None
    if parent_payload is not None:
        parent_scope = parent_payload
    elif isinstance(issue_payload, dict):
        sub_issues = issue_payload.get("subIssues")
        if isinstance(sub_issues, dict) and isinstance(sub_issues.get("nodes"), list) and sub_issues.get("nodes"):
            parent_scope = issue_payload

    if parent_scope is not None:
        raw_children = parent_scope.get("subIssues")
        child_nodes = raw_children.get("nodes") if isinstance(raw_children, dict) else None
        unresolved_children: list[dict[str, Any]] = []
        resolved_children: list[dict[str, Any]] = []
        if isinstance(child_nodes, list):
            for child in child_nodes:
                if not isinstance(child, dict):
                    continue
                child_number = child.get("number")
                child_state = child.get("state")
                if child_state == "CLOSED":
                    resolved_children.append(child)
                    continue
                if child_number == issue_number and merged_issue_open:
                    resolved_children.append(child)
                    continue
                unresolved_children.append(child)
        parent_number = parent_scope.get("number")
        parent_state = parent_scope.get("state")
        if parent_state == "CLOSED" and unresolved_children:
            findings.append(
                make_reconciliation_finding(
                    kind="parent_drift",
                    severity="block",
                    subject=f"parent issue #{parent_number}",
                    evidence={
                        "parent_state": parent_state,
                        "unresolved_children": [
                            {"number": child.get("number"), "state": child.get("state"), "title": child.get("title")}
                            for child in unresolved_children
                        ],
                    },
                    recommended_action="reopen the parent issue or finish the unresolved child issues before treating the parent as closed out.",
                )
            )
        elif parent_state == "OPEN" and child_nodes and not unresolved_children:
            findings.append(
                make_reconciliation_finding(
                    kind="parent_drift",
                    severity="fix-needed",
                    subject=f"parent issue #{parent_number}",
                    evidence={
                        "parent_state": parent_state,
                        "resolved_children": [
                            {"number": child.get("number"), "state": child.get("state"), "title": child.get("title")}
                            for child in resolved_children
                        ],
                    },
                    recommended_action="reconcile the parent issue because all child gaps are already closed or absorbed.",
                )
            )

    project_payload: dict[str, Any] | None = None
    project_drift_details: list[dict[str, Any]] = []
    if project_number is not None:
        fixture_project_payload, fixture_project_errors = load_optional_json_fixture(
            target_root,
            project_payload_file,
            label="Project payload fixture",
        )
        if fixture_project_errors:
            project_context = {}
            project_errors = fixture_project_errors
        elif isinstance(fixture_project_payload, dict):
            project_context = {
                "project_id": fixture_project_payload.get("project_id") or fixture_project_payload.get("id") or f"fixture-project-{project_number}",
                "status_field_id": fixture_project_payload.get("status_field_id") or "fixture-status-field",
                "done_option_id": fixture_project_payload.get("done_option_id") or "fixture-done",
                "items": fixture_project_payload.get("items") if isinstance(fixture_project_payload.get("items"), list) else [],
            }
            project_errors = []
        else:
            project_context, project_errors = project_status_context(target_root, owner, project_number)
        if project_errors:
            if any("unknown owner type" in message for message in project_errors):
                project_payload = {
                    "number": project_number,
                    "status": "unavailable",
                    "reason": "GitHub ProjectV2 CLI owner resolution is unavailable in this environment.",
                    "errors": project_errors,
                    "budget_guard": graphql_budget_guard("project_v2_status_surface", project_errors),
                }
            else:
                missing_inputs.extend(f"project: {message}" for message in project_errors)
        else:
            items = project_context["items"]
            issue_item = find_project_item(items, issue_number, "issue") if issue_number is not None else None
            issue_item_budget_guard: dict[str, Any] | None = None
            if issue_item is None and issue_id is not None and issue_number is not None:
                issue_item, issue_item_errors = project_item_for_issue(target_root, issue_id, project_number)
                if issue_item_errors:
                    issue_item_budget_guard = graphql_budget_guard(
                        "project_v2_issue_item_lookup",
                        issue_item_errors,
                    )
            pr_item = find_project_item(items, pr_number, "pr") if pr_number is not None else None
            project_payload = {
                "number": project_number,
                "project_id": project_context["project_id"],
                "status_field_id": project_context["status_field_id"],
                "done_option_id": project_context["done_option_id"],
                "issue_item": issue_item,
                "pr_item": pr_item,
            }
            if issue_item_budget_guard is not None:
                project_payload["issue_item_budget_guard"] = issue_item_budget_guard

            if issue_number is not None:
                expected_done = issue_payload is not None and (issue_payload.get("state") == "CLOSED" or merged_issue_open)
                if issue_item is None:
                    project_drift_details.append(
                        {
                            "subject": f"issue #{issue_number}",
                            "reason": "issue is missing from project",
                            "expected_done": expected_done,
                        }
                    )
                else:
                    status = issue_item.get("status")
                    if expected_done and status != "Done":
                        project_drift_details.append(
                            {
                                "subject": f"issue #{issue_number}",
                                "reason": "issue project status is not Done",
                                "expected_done": True,
                                "actual_status": status,
                            }
                        )
                    if not expected_done and status == "Done":
                        project_drift_details.append(
                            {
                                "subject": f"issue #{issue_number}",
                                "reason": "issue project status is Done while the issue still has an open gap",
                                "expected_done": False,
                                "actual_status": status,
                            }
                        )

            if pr_number is not None:
                expected_done = pr_payload is not None and pr_payload.get("state") == "MERGED"
                if pr_item is not None:
                    status = pr_item.get("status")
                    if expected_done and status != "Done":
                        project_drift_details.append(
                            {
                                "subject": f"pr #{pr_number}",
                                "reason": "pr project status is not Done",
                                "expected_done": True,
                                "actual_status": status,
                            }
                        )
                    if not expected_done and status == "Done":
                        project_drift_details.append(
                            {
                                "subject": f"pr #{pr_number}",
                                "reason": "pr project status is Done while the PR is not merged",
                                "expected_done": False,
                                "actual_status": status,
                            }
                        )

    if project_drift_details:
        findings.append(
            make_reconciliation_finding(
                kind="project_drift",
                severity="fix-needed",
                subject=f"project {project_number}",
                evidence={"drifts": project_drift_details},
                recommended_action="align the project items with the audited issue/PR state before closeout.",
            )
        )

    if missing_inputs:
        findings.append(
            make_reconciliation_finding(
                kind="host_signal_drift",
                severity="block",
                subject="github control plane",
                evidence={"missing_inputs": missing_inputs},
                recommended_action="restore readable GitHub issue, PR, project, or repository signals before closeout.",
                category="drift",
                fallback_to="manual-reconciliation",
            )
        )
        result = "block"
        summary = "reconciliation audit could not complete because required GitHub inputs were missing."
    else:
        result = reconciliation_result(findings)
        summary = (
            "reconciliation audit found no merged-but-open, absorbed-but-open, parent-drift, host-signal-drift, or project-drift findings."
            if result == "pass"
            else "reconciliation audit found GitHub drift that must be reviewed before closeout."
        )
    return (
        {
            "command": "reconciliation",
            "operation": "audit",
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": None if result == "pass" else "manual-reconciliation",
            "repo": {"owner": owner, "name": repo_name},
            "issue": issue_payload,
            "parent": parent_payload,
            "pr": pr_payload,
            "project": project_payload,
            "binding": binding,
            **({"suite_gate_validation": suite_gate_validation} if suite_gate_validation is not None else {}),
            "findings": findings,
        },
        [],
    )

def reconciliation_action_source(finding: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index,
        "kind": finding.get("kind"),
        "severity": finding.get("severity"),
        "subject": finding.get("subject"),
        "evidence": finding.get("evidence") if isinstance(finding.get("evidence"), dict) else {},
        "proof_locator": f"audit.findings[{index}].evidence",
    }

def reconciliation_planned_action(
    *,
    action: str,
    finding: dict[str, Any],
    finding_index: int,
    subject: object,
    write_target: dict[str, Any],
    rollback_note: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "kind": finding.get("kind"),
        "subject": subject,
        "action": action,
        "source_finding": reconciliation_action_source(finding, finding_index),
        "proof_locator": f"audit.findings[{finding_index}].evidence",
        "write_target": write_target,
        "rollback_note": rollback_note,
        **extra,
    }

def reconciliation_skipped_action(
    *,
    action: str,
    finding: dict[str, Any],
    finding_index: int,
    subject: object,
    reason: str,
    manual: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "kind": finding.get("kind"),
        "subject": subject,
        "action": action,
        "reason": reason,
        "source_finding": reconciliation_action_source(finding, finding_index),
        "proof_locator": f"audit.findings[{finding_index}].evidence",
        "manual": manual,
        **extra,
    }

def reconciliation_sync_plan(audit_payload: dict[str, Any], *, include_closeout_comment: bool = False) -> dict[str, Any]:
    planned_actions: list[dict[str, Any]] = []
    skipped_actions: list[dict[str, Any]] = []
    manual_actions: list[dict[str, Any]] = []
    findings = audit_payload.get("findings")
    proof = {
        "audit_result": audit_payload.get("result"),
        "audit_operation": audit_payload.get("operation"),
        "finding_count": len(findings) if isinstance(findings, list) else 0,
        "planned_action_count": 0,
        "skipped_action_count": 0,
        "manual_action_count": 0,
    }
    if not isinstance(findings, list):
        return {
            "schema_version": "loom-safe-sync-plan/v1",
            "result": "block",
            "planned_actions": planned_actions,
            "skipped_actions": skipped_actions,
            "manual_actions": [
                {
                    "action": "manual_reconciliation",
                    "reason": "audit payload does not expose findings as a list",
                    "manual": True,
                }
            ],
            "proof": proof,
        }
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        severity = finding.get("severity")
        kind = finding.get("kind")
        subject = finding.get("subject")
        evidence = finding.get("evidence")
        if severity == "block":
            manual_actions.append(
                reconciliation_skipped_action(
                    action="manual_reconciliation",
                    finding=finding,
                    finding_index=index,
                    subject=subject,
                    reason="block findings must be resolved manually before reconciliation sync can write host state",
                    manual=True,
                )
            )
            continue
        if severity == "warn":
            skipped_actions.append(
                reconciliation_skipped_action(
                    action="none",
                    finding=finding,
                    finding_index=index,
                    subject=subject,
                    reason="warn findings are retained as evidence and do not trigger host writes",
                )
            )
            continue
        if severity != "fix-needed":
            continue
        if kind in {"missing_native_edge", "stale_native_edge"}:
            edge = evidence.get("edge") if isinstance(evidence, dict) else None
            if not isinstance(edge, dict):
                skipped_actions.append(
                    reconciliation_skipped_action(
                        action="sync_native_dependency",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        reason="dependency drift is missing edge proof",
                    )
                )
                continue
            source_issue = edge.get("source_issue")
            blocking_issue = edge.get("blocking_issue")
            edge_proof = edge.get("provenance") if isinstance(edge.get("provenance"), dict) else {}
            proof_owner = edge_proof.get("source_owner")
            proof_locator = edge_proof.get("source_locator")
            proof_is_mechanical = proof_owner in {"github_issue_machine_block", "repo_authored_dependency"}
            if kind == "stale_native_edge":
                proof_is_mechanical = edge.get("source_of_truth") == "github_native_edge" and edge.get("blocker_state") == "closed"
                proof_locator = proof_locator or f"issue #{blocking_issue}"
            if not all(isinstance(value, int) for value in (source_issue, blocking_issue)) or not proof_is_mechanical:
                skipped_actions.append(
                    reconciliation_skipped_action(
                        action="sync_native_dependency",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        reason="native dependency write requires mechanical proof from repo-authored or issue-authored dependency truth",
                    )
                )
                continue
            action = "add_blocked_by" if kind == "missing_native_edge" else "remove_blocked_by"
            mutation = "addBlockedBy" if kind == "missing_native_edge" else "removeBlockedBy"
            planned_actions.append(
                reconciliation_planned_action(
                    action=action,
                    finding=finding,
                    finding_index=index,
                    subject=subject,
                    write_target={
                        "host": "github",
                        "type": "native_dependency",
                        "mutation": mutation,
                        "issue_number": source_issue,
                        "blocking_issue_number": blocking_issue,
                    },
                    rollback_note=(
                        f"run removeBlockedBy for issue #{source_issue} blocked by #{blocking_issue} if the add is reverted."
                        if action == "add_blocked_by"
                        else f"run addBlockedBy for issue #{source_issue} blocked by #{blocking_issue} if the removal is reverted."
                    ),
                    issue_number=source_issue,
                    blocking_issue_number=blocking_issue,
                    proof_source=proof_locator,
                    verification_step=f"read GitHub native dependency edge issue #{source_issue} blocked by #{blocking_issue}",
                )
            )
            continue
        if kind in {"merged_but_open", "absorbed_but_open"}:
            issue_number = audit_payload.get("issue", {}).get("number")
            if not isinstance(issue_number, int):
                skipped_actions.append(
                    reconciliation_skipped_action(
                        action="close_issue",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        reason="cannot close issue because audit proof is missing issue.number",
                    )
                )
                continue
            if include_closeout_comment:
                planned_actions.append(
                    reconciliation_planned_action(
                        action="add_closeout_comment",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        write_target={"host": "github", "type": "issue_comment", "issue_number": issue_number},
                        rollback_note="delete the closeout comment from the GitHub issue if the sync is reverted.",
                        issue_number=issue_number,
                    )
                )
            planned_actions.append(
                reconciliation_planned_action(
                    action="close_issue",
                    finding=finding,
                    finding_index=index,
                    subject=subject,
                    write_target={"host": "github", "type": "issue", "issue_number": issue_number, "field": "state"},
                    rollback_note="reopen the GitHub issue if the closeout basis is later invalidated.",
                    issue_number=issue_number,
                )
            )
            continue
        if kind == "project_drift":
            project = audit_payload.get("project")
            if not isinstance(project, dict):
                skipped_actions.append(
                    reconciliation_skipped_action(
                        action="set_project_done",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        reason="project_drift is missing project context",
                    )
                )
                continue
            drifts = evidence.get("drifts") if isinstance(evidence, dict) else None
            if not isinstance(drifts, list):
                skipped_actions.append(
                    reconciliation_skipped_action(
                        action="set_project_done",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        reason="project_drift is missing drift details",
                    )
                )
                continue
            for drift in drifts:
                if not isinstance(drift, dict):
                    continue
                drift_subject = drift.get("subject")
                reason = str(drift.get("reason", ""))
                expected_done = drift.get("expected_done")
                if expected_done is not True:
                    manual_actions.append(
                        reconciliation_skipped_action(
                            action="set_project_done",
                            finding=finding,
                            finding_index=index,
                            subject=drift_subject,
                            reason=f"requires manual reconciliation: {reason}",
                            manual=True,
                        )
                    )
                    continue
                item_key = None
                if isinstance(drift_subject, str) and drift_subject.startswith("issue #"):
                    item_key = "issue_item"
                elif isinstance(drift_subject, str) and drift_subject.startswith("pr #"):
                    item_key = "pr_item"
                item = project.get(item_key) if item_key else None
                if not isinstance(item, dict):
                    skipped_actions.append(
                        reconciliation_skipped_action(
                            action="set_project_done",
                            finding=finding,
                            finding_index=index,
                            subject=drift_subject,
                            reason="cannot be synced because the project item is missing",
                        )
                    )
                    continue
                item_id = item.get("id")
                project_id = project.get("project_id")
                status_field_id = project.get("status_field_id")
                done_option_id = project.get("done_option_id")
                if not all(isinstance(value, str) and value for value in (item_id, project_id, status_field_id, done_option_id)):
                    skipped_actions.append(
                        reconciliation_skipped_action(
                            action="set_project_done",
                            finding=finding,
                            finding_index=index,
                            subject=drift_subject,
                            reason="is missing project status identifiers",
                        )
                    )
                    continue
                planned_actions.append(
                    reconciliation_planned_action(
                        action="set_project_done",
                        finding=finding,
                        finding_index=index,
                        subject=drift_subject,
                        write_target={
                            "host": "github",
                            "type": "project_item",
                            "project_number": project.get("number"),
                            "item_id": item_id,
                            "field": "Status",
                            "value": "Done",
                        },
                        rollback_note="set the Project item Status back to its prior value if the closeout basis is invalidated.",
                        project_number=project.get("number"),
                        project_id=project_id,
                        item_id=item_id,
                        status_field_id=status_field_id,
                        done_option_id=done_option_id,
                    )
                )
            continue
        if kind == "parent_drift":
            parent = audit_payload.get("parent")
            parent_number = parent.get("number") if isinstance(parent, dict) else None
            if parent_number is None:
                skipped_actions.append(
                    reconciliation_skipped_action(
                        action="close_issue",
                        finding=finding,
                        finding_index=index,
                        subject=subject,
                        reason="parent_drift is missing parent issue context",
                    )
                )
                continue
            planned_actions.append(
                reconciliation_planned_action(
                    action="close_issue",
                    finding=finding,
                    finding_index=index,
                    subject=subject,
                    write_target={"host": "github", "type": "issue", "issue_number": parent_number, "field": "state"},
                    rollback_note="reopen the parent issue if a child gap is later found unresolved.",
                    issue_number=parent_number,
                )
            )
            continue
        manual_actions.append(
            reconciliation_skipped_action(
                action="manual_reconciliation",
                finding=finding,
                finding_index=index,
                subject=subject,
                reason=f"unsupported reconciliation finding `{kind}`",
                manual=True,
            )
        )
    proof["planned_action_count"] = len(planned_actions)
    proof["skipped_action_count"] = len(skipped_actions)
    proof["manual_action_count"] = len(manual_actions)
    result = "block" if manual_actions or skipped_actions else "pass"
    return {
        "schema_version": "loom-safe-sync-plan/v1",
        "result": result,
        "planned_actions": planned_actions,
        "skipped_actions": skipped_actions,
        "manual_actions": manual_actions,
        "proof": proof,
    }

def closeout_reconciliation_result(
    audit_payload: dict[str, Any] | None,
) -> tuple[str | None, str | None]:
    if not isinstance(audit_payload, dict):
        return None, None
    result = audit_payload.get("result")
    if result == "fix-needed":
        return "reconciliation-sync", "closeout requires reconciliation sync before it can pass."
    if result == "block":
        return "manual-reconciliation", "closeout requires manual reconciliation because the audit itself is blocked."
    return None, None

def goal_completion_payload(target_root: Path, completion_file: str | None, context: dict[str, Any] | None) -> dict[str, Any]:
    if not completion_file:
        return {
            "schema_version": GOAL_COMPLETION_SCHEMA,
            "status": "missing",
            "result": "not_applicable",
            "summary": "/goal completion evidence was not provided and was not required by this closeout invocation.",
            "missing_inputs": [],
            "fallback_to": None,
        }
    payload, errors = load_optional_json_fixture(target_root, completion_file, label="goal completion evidence")
    if errors or not isinstance(payload, dict):
        return {
            "schema_version": GOAL_COMPLETION_SCHEMA,
            "status": "unreadable",
            "result": "block",
            "summary": "/goal completion evidence is unreadable.",
            "missing_inputs": errors or ["goal completion must be a JSON object"],
            "fallback_to": "closeout",
        }
    missing: list[str] = []
    if payload.get("schema_version") not in {GOAL_COMPLETION_SCHEMA, GOAL_EXECUTION_CONTRACT_SCHEMA}:
        missing.append("schema_version")
    if context is not None:
        work_item = payload.get("work_item")
        item_id = work_item.get("id") if isinstance(work_item, dict) else payload.get("item_id")
        if item_id not in {context["item_id"], None}:
            missing.append("work_item mismatch")
        if payload.get("head_sha") not in {git_head_sha(target_root), None}:
            missing.append("head_sha mismatch")
    return {
        "schema_version": GOAL_COMPLETION_SCHEMA,
        "status": "valid" if not missing else "mismatch",
        "result": "pass" if not missing else "block",
        "summary": "/goal completion evidence is bound to the closeout context." if not missing else "/goal completion evidence does not match the closeout context.",
        "missing_inputs": missing,
        "fallback_to": None if not missing else "closeout",
        "completion": payload,
    }

def closeout_payload(
    *,
    target_root: Path,
    expected_item: str | None,
    phase_number: int | None,
    fr_number: int | None,
    issue_number: int | None,
    pr_number: int | None,
    project_number: int | None,
    branch_name: str | None,
    owner: str,
    repo_name: str,
    skip_gate: bool,
    goal_completion_file: str | None = None,
    gate_profile: str = "auto",
    issue_payload_file: str | None = None,
    pr_payload_file: str | None = None,
    project_payload_file: str | None = None,
    status_checks_file: str | None = None,
    branch_protection_file: str | None = None,
    ruleset_file: str | None = None,
    pr_role: str | None = None,
    pr_role_numbers: dict[str, int] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    missing_inputs: list[str] = []
    pr_roles = closeout_pr_roles_payload(
        legacy_pr_number=pr_number,
        role_numbers=pr_role_numbers or {},
        requested_role=pr_role,
    )
    effective_pr_number = closeout_current_pr_number(pr_roles)
    merge_ready_pr_number = closeout_merge_ready_pr_number(pr_roles)
    effective_profile = effective_closeout_gate_profile(gate_profile)
    expected_closeout_lookup = closeout_expected_item_lookup(target_root, issue_number, expected_item)
    missing_inputs.extend(retained_item_lookup_missing_inputs(expected_closeout_lookup))
    expected_closeout_item = retained_item_lookup_id(expected_closeout_lookup)
    expected_closeout_work_item = retained_item_lookup_work_item_relative(expected_closeout_lookup)
    context, context_errors = load_context(target_root, ".loom/bootstrap/init-result.json", None)
    if (
        expected_closeout_item is not None
        and (context_errors or context.get("item_id") != expected_closeout_item)
    ):
        context, context_errors = load_retained_item_context(
            target_root,
            ".loom/bootstrap/init-result.json",
            expected_closeout_item,
            expected_closeout_work_item,
        )
    fact_chain_context: dict[str, Any] | None = context if not context_errors else None
    if context_errors:
        missing_inputs.extend(f"fact-chain: {message}" for message in context_errors)
    elif fact_chain_context is not None:
        missing_inputs.extend(report_blocking_messages(fact_chain_context["report"]))
    governance_surface = build_governance_surface(target_root)
    repo_interface = governance_surface.get("repo_interface")
    repo_specific_requirements = repo_specific_requirements_payload(
        repo_interface,
        target_root=target_root,
        surface="closeout",
    )
    release_targets = repo_interface.get("release_targets") if isinstance(repo_interface, dict) else None
    target_release = (
        release_targets.get("target_release")
        if isinstance(release_targets, dict)
        else empty_target_release_status()
    )
    release_enforcement = (
        release_targets.get("enforcement")
        if isinstance(release_targets, dict) and isinstance(release_targets.get("enforcement"), str)
        else "unknown"
    )
    closeout_findings: list[dict[str, Any]] = []
    gate: dict[str, Any] = {
        "skipped": skip_gate and effective_profile in CLOSEOUT_HEAVY_PROFILES,
        "profile": effective_profile,
        "requested_profile": gate_profile,
        "source": "closeout_contract",
        "trigger_reason": "ordinary closeout defaults to retained evidence backlink checks",
        "required_for_closeout": True,
        "subchecks": [],
    }
    suite_gate_validation: dict[str, Any] | None = None
    if fact_chain_context is not None:
        if suite_gate_required_for_surface(fact_chain_context, surface="closeout"):
            suite_gate_validation = suite_gate_validation_payload(fact_chain_context, surface="closeout")
        else:
            suite_gate_validation = suite_gate_not_applicable_payload(fact_chain_context, surface="closeout")
    elif is_idle_context_errors(context_errors):
        suite_gate_validation = suite_gate_not_applicable_payload({}, surface="closeout")
    elif context_errors:
        suite_gate_validation = suite_gate_unreadable_payload(context_errors, surface="closeout")
    if suite_gate_validation is not None:
        suite_subchecks = closeout_suite_gate_subchecks(suite_gate_validation, profile=CLOSEOUT_LIGHT_PROFILE)
        gate["subchecks"].extend(suite_subchecks)
        for subcheck in suite_subchecks:
            if subcheck.get("required_for_closeout") is True and subcheck.get("result") == "block":
                for message in subcheck.get("missing_inputs", []):
                    missing_inputs.append(f"{subcheck.get('id')}: {message}")
    if effective_profile in CLOSEOUT_HEAVY_PROFILES and not skip_gate:
        gate_command, gate_source = closeout_gate_command(target_root)
        gate_result = run_process(gate_command, target_root)
        gate["source"] = gate_source
        gate["trigger_reason"] = f"`{effective_profile}` explicitly requires the heavier local gate"
        gate["required_for_closeout"] = effective_profile == "strong-profile-full-gate"
        gate["command"] = " ".join(gate_command)
        gate["exit_code"] = gate_result.returncode
        gate["stdout"] = gate_result.stdout.strip()
        gate["stderr"] = gate_result.stderr.strip()
        gate["subchecks"].append(
            closeout_subcheck(
                check_id=effective_profile,
                source=gate_source,
                profile=effective_profile,
                required_for_closeout=gate["required_for_closeout"],
                trigger_reason=gate["trigger_reason"],
                result="pass" if gate_result.returncode == 0 else "block",
                fallback_to=None if gate_result.returncode == 0 else "merge",
                evidence_locator=gate["command"],
                missing_inputs=[] if gate_result.returncode == 0 else [f"loom_check:{gate_source}"],
            )
        )
        if gate_result.returncode != 0:
            missing_inputs.append(f"loom_check:{gate_source}")
    elif effective_profile in CLOSEOUT_HEAVY_PROFILES and skip_gate:
        gate["source"] = "skipped_heavy_gate"
        gate["trigger_reason"] = f"`{effective_profile}` was requested but --skip-gate suppressed heavyweight execution"
        gate["required_for_closeout"] = False
        gate["subchecks"].append(
            closeout_subcheck(
                check_id=effective_profile,
                source="skipped_heavy_gate",
                profile=effective_profile,
                required_for_closeout=False,
                trigger_reason=gate["trigger_reason"],
                result="pass",
                fallback_to=None,
            )
        )

    reconciliation_payload: dict[str, Any] | None = None
    closeout_fallback: str | None = None
    closeout_summary_override: str | None = None
    if issue_number is not None or effective_pr_number is not None or project_number is not None:
        reconciliation_payload, reconciliation_errors = reconciliation_audit_payload(
            target_root=target_root,
            expected_item=expected_closeout_item,
            phase_number=phase_number,
            fr_number=fr_number,
            issue_number=issue_number,
            pr_number=effective_pr_number,
            project_number=project_number,
            branch_name=branch_name,
            owner=owner,
            repo_name=repo_name,
            issue_payload_file=issue_payload_file,
            pr_payload_file=pr_payload_file,
            project_payload_file=project_payload_file,
        )
        if reconciliation_errors:
            missing_inputs.extend(f"reconciliation: {message}" for message in reconciliation_errors)
        else:
            closeout_fallback, closeout_summary_override = closeout_reconciliation_result(reconciliation_payload)
            if closeout_fallback == "reconciliation-sync":
                missing_inputs.append("reconciliation audit requires sync")
            if closeout_fallback == "manual-reconciliation":
                missing_inputs.append("reconciliation audit is blocked")

    issue_payload: dict[str, Any] | None = None
    issue_id: str | None = None
    dependency_graph: dict[str, Any] | None = None
    if issue_number is not None:
        fixture_issue_payload, fixture_issue_errors = load_optional_json_fixture(
            target_root,
            issue_payload_file,
            label="issue payload fixture",
        )
        if fixture_issue_errors:
            issue_payload = None
            issue_errors = fixture_issue_errors
        elif isinstance(fixture_issue_payload, dict):
            issue_payload, issue_errors = normalize_issue_fixture_payload(fixture_issue_payload)
        else:
            issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
        if issue_errors:
            missing_inputs.extend(f"issue: {message}" for message in issue_errors)
        elif issue_payload is not None:
            raw_issue_id = issue_payload.get("id")
            if isinstance(raw_issue_id, str) and raw_issue_id:
                issue_id = raw_issue_id
            if fixture_issue_payload is None:
                native_dependencies = github_issue_dependencies_payload(target_root, owner, repo_name, issue_number)
                dependency_graph = dependency_graph_payload(
                    issue_number=issue_number,
                    issue_payload=issue_payload,
                    native_dependency_payload=native_dependencies,
                )
                for finding in dependency_graph.get("findings", []):
                    if not isinstance(finding, dict):
                        continue
                    if finding.get("kind") in {"open_blocker_executable_conflict", "stale_native_edge"}:
                        missing_inputs.append(str(finding.get("subject") or finding.get("kind")))
                        closeout_findings.append(
                            {
                                **finding,
                                "why_blocking": (
                                    "closeout is blocked because an open native dependency blocker remains."
                                    if finding.get("kind") == "open_blocker_executable_conflict"
                                    else "closeout is blocked because the native dependency mirror is stale."
                                ),
                                "fallback_to": finding.get("fallback_to") or "manual-reconciliation",
                            }
                        )
                    elif finding.get("kind") == "native_dependency_unreadable":
                        closeout_findings.append({**finding, "severity": "warn"})

    pr_payload: dict[str, Any] | None = None
    merge_ready_pr_payload: dict[str, Any] | None = None
    merge_ready_pr_errors: list[str] = []
    merge_commit_sha: str | None = None
    merge_commit_in_target: bool | None = None
    if effective_pr_number is not None:
        fixture_pr_payload, fixture_pr_errors = load_optional_json_fixture(
            target_root,
            pr_payload_file,
            label="PR payload fixture",
        )
        if fixture_pr_errors:
            pr_payload = None
            pr_errors = fixture_pr_errors
        elif isinstance(fixture_pr_payload, dict):
            pr_payload = fixture_pr_payload
            pr_errors = []
        else:
            pr_payload, pr_errors = github_pr_payload(target_root, owner, repo_name, effective_pr_number)
        if pr_errors:
            missing_inputs.extend(f"pr: {message}" for message in pr_errors)
        elif pr_payload is not None:
            merge_commit = pr_payload.get("mergeCommit")
            if isinstance(merge_commit, dict):
                oid = merge_commit.get("oid")
                if isinstance(oid, str) and oid:
                    merge_commit_sha = oid
            if pr_payload.get("state") != "MERGED":
                missing_inputs.append("pr is not merged")
            if merge_commit_sha:
                base_ref = pr_payload.get("baseRefName")
                if isinstance(base_ref, str) and base_ref:
                    merge_commit_in_target = contains_merged_commit(target_root, merge_commit_sha, base_ref)
                    if not merge_commit_in_target:
                        missing_inputs.append(f"origin/{base_ref} does not contain the merged PR commit")
                else:
                    missing_inputs.append("pr baseRefName is missing")
        if merge_ready_pr_number is not None and merge_ready_pr_number != effective_pr_number:
            merge_ready_pr_payload, merge_ready_pr_errors = github_pr_payload(
                target_root,
                owner,
                repo_name,
                merge_ready_pr_number,
            )
            if merge_ready_pr_errors:
                missing_inputs.extend(f"merge-ready-pr: {message}" for message in merge_ready_pr_errors)
        else:
            merge_ready_pr_payload = pr_payload

    if effective_pr_number is not None:
        backlink_subchecks = closeout_backlink_subchecks(
            target_root=target_root,
            context=fact_chain_context,
            profile=CLOSEOUT_LIGHT_PROFILE,
            owner=owner,
            repo_name=repo_name,
            pr_number=effective_pr_number,
            pr_payload=pr_payload,
            merge_ready_pr_number=merge_ready_pr_number,
            merge_ready_pr_payload=merge_ready_pr_payload,
            merge_ready_pr_errors=merge_ready_pr_errors,
            merge_commit_sha=merge_commit_sha,
            merge_commit_in_target=merge_commit_in_target,
            pr_payload_file=pr_payload_file,
            status_checks_file=status_checks_file,
            branch_protection_file=branch_protection_file,
            ruleset_file=ruleset_file,
        )
        gate["subchecks"].extend(backlink_subchecks)
        for subcheck in backlink_subchecks:
            if subcheck.get("required_for_closeout") is True and subcheck.get("result") == "block":
                for message in subcheck.get("missing_inputs", []):
                    missing_inputs.append(f"{subcheck.get('id')}: {message}")
            diagnostic = subcheck.get("post_merge_review_diagnostic")
            if isinstance(diagnostic, dict) and isinstance(diagnostic.get("finding"), dict):
                closeout_findings.append(
                    {
                        **diagnostic["finding"],
                        "category": "review_bypass",
                        "why_blocking": diagnostic.get("summary"),
                        "repair_plan": diagnostic.get("repair_plan"),
                    }
                )

    project_payload: dict[str, Any] | None = None
    if project_number is not None:
        fixture_project_payload, fixture_project_errors = load_optional_json_fixture(
            target_root,
            project_payload_file,
            label="Project payload fixture",
        )
        if fixture_project_errors:
            project_context = {}
            project_errors = fixture_project_errors
        elif isinstance(fixture_project_payload, dict):
            project_context = {
                "project_id": fixture_project_payload.get("project_id") or fixture_project_payload.get("id") or f"fixture-project-{project_number}",
                "status_field_id": fixture_project_payload.get("status_field_id") or "fixture-status-field",
                "done_option_id": fixture_project_payload.get("done_option_id") or "fixture-done",
                "items": fixture_project_payload.get("items") if isinstance(fixture_project_payload.get("items"), list) else [],
            }
            project_errors = []
        else:
            project_context, project_errors = project_status_context(target_root, owner, project_number)
        if project_errors:
            if any("unknown owner type" in message for message in project_errors):
                project_payload = {
                    "number": project_number,
                    "status": "unavailable",
                    "reason": "GitHub ProjectV2 CLI owner resolution is unavailable in this environment.",
                    "errors": project_errors,
                    "budget_guard": graphql_budget_guard("project_v2_status_surface", project_errors),
                }
            else:
                missing_inputs.extend(f"project: {message}" for message in project_errors)
        else:
            items = project_context["items"]
            issue_item = find_project_item(items, issue_number, "issue") if issue_number is not None else None
            issue_item_budget_guard: dict[str, Any] | None = None
            if issue_item is None and issue_id is not None and issue_number is not None:
                issue_item, issue_item_errors = project_item_for_issue(target_root, issue_id, project_number)
                if issue_item_errors:
                    issue_item_budget_guard = graphql_budget_guard(
                        "project_v2_issue_item_lookup",
                        issue_item_errors,
                    )
            pr_item = find_project_item(items, effective_pr_number, "pr") if effective_pr_number is not None else None
            if issue_number is not None and issue_item is None:
                missing_inputs.append("issue is missing from project")
            project_payload = {
                "number": project_number,
                "project_id": project_context["project_id"],
                "status_field_id": project_context["status_field_id"],
                "done_option_id": project_context["done_option_id"],
                "issue_item": issue_item,
                "pr_item": pr_item,
            }
            if issue_item_budget_guard is not None:
                project_payload["issue_item_budget_guard"] = issue_item_budget_guard
            for label, item in (("issue", issue_item), ("pr", pr_item)):
                if item is None:
                    continue
                status = item.get("status")
                if isinstance(status, str) and status != "Done":
                    missing_inputs.append(f"{label} project status is not Done")

    if issue_payload is not None and issue_payload.get("state") != "CLOSED":
        missing_inputs.append("issue is not closed")

    target_release_gaps = target_release.get("closeout_gaps") if isinstance(target_release, dict) else []
    if not isinstance(target_release_gaps, list):
        target_release_gaps = []
    delivery_chain = target_release.get("delivery_chain") if isinstance(target_release, dict) else {}
    unreleased = delivery_chain.get("unreleased") if isinstance(delivery_chain, dict) else []
    unreconciled = delivery_chain.get("unreconciled") if isinstance(delivery_chain, dict) else []
    if not isinstance(unreleased, list):
        unreleased = []
    if not isinstance(unreconciled, list):
        unreconciled = []
    if isinstance(target_release, dict) and target_release.get("result") == "block" and release_enforcement == "blocking":
        missing_inputs.extend(
            f"target_release: {message}"
            for message in target_release.get("missing_inputs", [])
        )
        closeout_findings.append(
            {
                "category": "gate_failure",
                "kind": "target_release_unreadable",
                "severity": "block",
                "subject": target_release.get("release_id") or "target release",
                "why_blocking": "target repository release/version truth is declared as blocking but unreadable.",
                "fallback_to": "closeout",
                "evidence": {"missing_inputs": target_release.get("missing_inputs", [])},
            }
        )
    if target_release_gaps and release_enforcement == "blocking":
        missing_inputs.extend(f"target_release gap: {gap}" for gap in target_release_gaps)
        closeout_findings.append(
            {
                "category": "gate_failure",
                "kind": "release_evidence_gap",
                "severity": "block",
                "subject": target_release.get("release_id") or "target release",
                "why_blocking": "target release closeout evidence is incomplete.",
                "fallback_to": "merge",
                "evidence": {"gaps": target_release_gaps},
            }
        )
    if unreleased:
        missing_inputs.append("target release contains merged but unreleased work")
        closeout_findings.append(
            {
                "category": "gate_failure",
                "kind": "merged_but_unreleased",
                "severity": "block",
                "subject": target_release.get("release_id") or "target release",
                "why_blocking": "merged work is still marked unreleased in the target release surface.",
                "fallback_to": "merge",
                "evidence": {"unreleased": unreleased},
            }
        )
    if unreconciled:
        missing_inputs.append("target release contains released but unreconciled work")
        closeout_findings.append(
            {
                "category": "drift",
                "kind": "released_but_unreconciled",
                "severity": "block",
                "subject": target_release.get("release_id") or "target release",
                "why_blocking": "released work is still marked unreconciled in the target release surface.",
                "fallback_to": "reconciliation-sync",
                "evidence": {"unreconciled": unreconciled},
            }
        )

    result = "pass" if not missing_inputs else "block"
    summary = (
        "closeout state is consistent across gate, GitHub issue/PR, project, and main."
        if result == "pass"
        else "closeout state is not yet consistent across gate, GitHub issue/PR, project, and main."
    )
    fallback_to = None if result == "pass" else "merge"
    blocking_subcheck = next(
        (
            subcheck
            for subcheck in gate.get("subchecks", [])
            if isinstance(subcheck, dict)
            and subcheck.get("required_for_closeout") is True
            and subcheck.get("result") == "block"
        ),
        None,
    )
    if result == "block" and closeout_summary_override is not None:
        summary = closeout_summary_override
        fallback_to = closeout_fallback
    elif result == "block" and isinstance(blocking_subcheck, dict):
        fallback_value = blocking_subcheck.get("fallback_to")
        fallback_to = fallback_value if isinstance(fallback_value, str) and fallback_value else fallback_to
        summary = f"closeout retained evidence backlink failed at `{blocking_subcheck.get('id')}`."
    elif result == "block" and closeout_findings:
        primary_finding = closeout_findings[0]
        summary = str(primary_finding.get("why_blocking") or summary)
        fallback_value = primary_finding.get("fallback_to")
        if isinstance(fallback_value, str) and fallback_value:
            fallback_to = fallback_value
    elif result == "pass" and isinstance(reconciliation_payload, dict) and reconciliation_payload.get("result") == "warn":
        summary = "closeout state is consistent, but reconciliation audit reported non-blocking warnings that still need review."
    if result == "pass" and repo_specific_requirements["result"] == "block":
        result = "block"
        summary = repo_specific_requirements["summary"]
        fallback_to = repo_specific_requirements["fallback_to"]
        missing_inputs.extend(repo_specific_requirements["missing_inputs"])
    goal_completion = goal_completion_payload(target_root, goal_completion_file, fact_chain_context)
    if goal_completion_file and goal_completion["result"] == "block":
        result = "block"
        summary = goal_completion["summary"]
        fallback_to = goal_completion["fallback_to"]
        missing_inputs.extend(f"goal_completion: {message}" for message in goal_completion.get("missing_inputs", []))
    return (
        {
            "command": "closeout",
            "operation": "check",
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": fallback_to,
            "repo": {"owner": owner, "name": repo_name},
            "pr_roles": pr_roles,
            "current_pr_role": pr_roles["current"],
            "gate": gate,
            **({"suite_gate_validation": suite_gate_validation} if suite_gate_validation is not None else {}),
            "issue": issue_payload,
            "pr": pr_payload,
            "project": project_payload,
            "repo_specific_requirements": repo_specific_requirements,
            "dependency_graph": dependency_graph,
            "goal_completion": goal_completion,
            "target_release": target_release,
            "findings": closeout_findings,
            **(
                {
                    "provenance": report_provenance(fact_chain_context["report"]),
                    "recovery_readiness": report_recovery_readiness(fact_chain_context["report"]),
                    "blocking_failures": report_blocking_failures(fact_chain_context["report"]),
                }
                if fact_chain_context is not None
                else fact_chain_error_contract(context_errors)
            ),
            **({"reconciliation": reconciliation_payload} if reconciliation_payload is not None else {}),
        },
        [],
    )

def handle_closeout(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    lifecycle_admission = lifecycle_admission_payload(
        target_root=target_root,
        owner=args.owner,
        repo_name=args.repo_name,
        issue_number=args.issue,
        fr_number=args.fr,
        pr_number=args.pr,
        branch_name=args.branch,
        intent="closeout",
    )
    if lifecycle_admission["result"] != "pass":
        return emit(
            {
                "command": "closeout",
                "operation": args.operation,
                "result": "block",
                "summary": "closeout stopped before repository carriers because the host-native lifecycle admission is blocked.",
                "missing_inputs": lifecycle_admission.get("missing_inputs") or lifecycle_admission.get("admission", {}).get("missing_inputs", []),
                "fallback_to": lifecycle_admission.get("primary_remediation"),
                "lifecycle_admission": lifecycle_admission,
            }
        )
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            runtime_state_block_payload(
                command="closeout",
                operation=args.operation,
                runtime_state=runtime_state,
                summary="closeout is blocked because the Loom runtime state is inconsistent.",
            )
        )
    owner = args.owner
    repo_name = args.repo_name
    if not owner or not repo_name:
        detected_owner, detected_repo = detect_github_repo(target_root)
        owner = owner or detected_owner
        repo_name = repo_name or detected_repo
    if not owner or not repo_name:
        return emit(
            {
                "command": "closeout",
                "operation": args.operation,
                "result": "block",
                "summary": "closeout could not determine the GitHub repository.",
                "missing_inputs": ["owner/repo"],
                "fallback_to": "merge",
                "runtime_state": runtime_state,
            }
        )

    payload, errors = closeout_payload(
        target_root=target_root,
        expected_item=args.item,
        phase_number=args.phase,
        fr_number=args.fr,
        issue_number=args.issue,
        pr_number=args.pr,
        project_number=args.project,
        branch_name=args.branch,
        owner=owner,
        repo_name=repo_name,
        skip_gate=args.skip_gate,
        goal_completion_file=args.goal_completion,
        gate_profile=args.gate_profile,
        issue_payload_file=args.issue_payload_file,
        pr_payload_file=args.pr_payload_file,
        project_payload_file=args.project_payload_file,
        status_checks_file=args.status_checks_file,
        branch_protection_file=args.branch_protection_file,
        ruleset_file=args.ruleset_file,
        pr_role=args.pr_role,
        pr_role_numbers=closeout_pr_role_numbers_from_args(args),
    )
    if errors:
        return emit(
            {
                "command": "closeout",
                "operation": args.operation,
                "result": "block",
                "summary": "closeout command hit an unexpected internal error.",
                "missing_inputs": errors,
                "fallback_to": "merge",
                "runtime_state": runtime_state,
            }
        )

    payload["runtime_state"] = runtime_state
    payload["lifecycle_admission"] = lifecycle_admission
    if args.operation == "check":
        return emit(payload)

    reconciliation = payload.get("reconciliation")
    repo_specific_requirements = payload.get("repo_specific_requirements")
    if isinstance(repo_specific_requirements, dict) and repo_specific_requirements.get("result") == "block":
        return emit(
            {
                **payload,
                "operation": "sync",
                "result": "block",
                "summary": "closeout sync is blocked until companion-declared blocking requirements are handled.",
                "fallback_to": repo_specific_requirements.get("fallback_to") or "merge",
                "runtime_state": runtime_state,
            }
        )
    if isinstance(reconciliation, dict):
        reconciliation_result = reconciliation.get("result")
        if reconciliation_result in {"fix-needed", "block"}:
            return emit(
                {
                    **payload,
                    "operation": "sync",
                    "result": "block",
                    "summary": (
                        "closeout sync is blocked until reconciliation sync repairs the audited drift."
                        if reconciliation_result == "fix-needed"
                        else "closeout sync is blocked because reconciliation audit could not complete."
                    ),
                    "fallback_to": "reconciliation-sync" if reconciliation_result == "fix-needed" else "manual-reconciliation",
                    "runtime_state": runtime_state,
                }
            )

    sync_missing: list[str] = []
    if args.issue is not None:
        issue = payload.get("issue")
        if isinstance(issue, dict) and issue.get("state") != "CLOSED":
            if args.comment:
                comment_result = run_process(
                    [
                        "gh",
                        "issue",
                        "comment",
                        str(args.issue),
                        "--repo",
                        f"{owner}/{repo_name}",
                        "--body",
                        args.comment,
                    ],
                    target_root,
                )
                if comment_result.returncode != 0:
                    sync_missing.append(comment_result.stderr.strip() or "failed to comment on issue")
            close_result = run_process(
                ["gh", "issue", "close", str(args.issue), "--repo", f"{owner}/{repo_name}"],
                target_root,
            )
            if close_result.returncode != 0:
                sync_missing.append(close_result.stderr.strip() or "failed to close issue")

    if args.project is not None:
        project = payload.get("project")
        if isinstance(project, dict):
            for key in ("issue_item", "pr_item"):
                item = project.get(key)
                if not isinstance(item, dict):
                    continue
                status = item.get("status")
                item_id = item.get("id")
                if not isinstance(item_id, str) or not item_id:
                    continue
                if status != "Done":
                    sync_missing.extend(
                        set_project_item_done(
                            target_root,
                            project["project_id"],
                            item_id,
                            project["status_field_id"],
                            project["done_option_id"],
                        )
                    )

    refreshed_payload, errors = closeout_payload(
        target_root=target_root,
        expected_item=args.item,
        phase_number=args.phase,
        fr_number=args.fr,
        issue_number=args.issue,
        pr_number=args.pr,
        project_number=args.project,
        branch_name=args.branch,
        owner=owner,
        repo_name=repo_name,
        skip_gate=args.skip_gate,
        goal_completion_file=args.goal_completion,
        gate_profile=args.gate_profile,
        issue_payload_file=args.issue_payload_file,
        pr_payload_file=args.pr_payload_file,
        project_payload_file=args.project_payload_file,
        status_checks_file=args.status_checks_file,
        branch_protection_file=args.branch_protection_file,
        ruleset_file=args.ruleset_file,
        pr_role=args.pr_role,
        pr_role_numbers=closeout_pr_role_numbers_from_args(args),
    )
    if errors:
        sync_missing.extend(errors)
    refreshed_payload["operation"] = "sync"

    if sync_missing:
        refreshed_payload["result"] = "block"
        refreshed_payload["summary"] = "closeout sync could not fully align GitHub control-plane state."
        refreshed_payload["missing_inputs"] = list(dict.fromkeys(sync_missing + list(refreshed_payload.get("missing_inputs", []))))
        refreshed_payload["fallback_to"] = "merge"
    refreshed_payload["runtime_state"] = runtime_state
    return emit(refreshed_payload)

def handle_reconciliation(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            runtime_state_block_payload(
                command="reconciliation",
                operation=args.operation,
                runtime_state=runtime_state,
                summary="reconciliation is blocked because the Loom runtime state is inconsistent.",
            )
        )
    if args.comment and args.comment_file:
        return emit(
            {
                "command": "reconciliation",
                "operation": args.operation,
                "result": "block",
                "summary": "reconciliation sync accepts either --comment or --comment-file, not both.",
                "missing_inputs": ["choose one comment source"],
                "fallback_to": "manual-reconciliation",
                "runtime_state": runtime_state,
            }
        )

    comment_body = args.comment
    if args.comment_file:
        comment_body, comment_errors = read_repo_relative_text_file(target_root, args.comment_file, label="reconciliation comment file")
        if comment_errors:
            return emit(
                {
                    "command": "reconciliation",
                    "operation": args.operation,
                    "result": "block",
                    "summary": "reconciliation sync could not read the requested comment file.",
                    "missing_inputs": comment_errors,
                    "fallback_to": "manual-reconciliation",
                    "runtime_state": runtime_state,
                }
            )
    owner = args.owner
    repo_name = args.repo_name
    if not owner or not repo_name:
        detected_owner, detected_repo = detect_github_repo(target_root)
        owner = owner or detected_owner
        repo_name = repo_name or detected_repo
    if not owner or not repo_name:
        return emit(
            {
                "command": "reconciliation",
                "operation": args.operation,
                "result": "block",
                "summary": "reconciliation could not determine the GitHub repository.",
                "missing_inputs": ["owner/repo"],
                "fallback_to": "manual-reconciliation",
                "runtime_state": runtime_state,
            }
        )

    pr_roles = closeout_pr_roles_payload(
        legacy_pr_number=args.pr,
        role_numbers=closeout_pr_role_numbers_from_args(args),
        requested_role=args.pr_role,
    )
    effective_pr_number = closeout_current_pr_number(pr_roles)
    payload, errors = reconciliation_audit_payload(
        target_root=target_root,
        expected_item=args.item,
        phase_number=args.phase,
        fr_number=args.fr,
        issue_number=args.issue,
        pr_number=effective_pr_number,
        project_number=args.project,
        branch_name=args.branch,
        owner=owner,
        repo_name=repo_name,
        issue_payload_file=args.issue_payload_file,
        pr_payload_file=args.pr_payload_file,
        project_payload_file=args.project_payload_file,
    )
    if errors:
        return emit(
            {
                "command": "reconciliation",
                "operation": args.operation,
                "result": "block",
                "summary": "reconciliation command hit an unexpected internal error.",
                "missing_inputs": errors,
                "fallback_to": "manual-reconciliation",
                "runtime_state": runtime_state,
            }
        )
    payload["runtime_state"] = runtime_state
    payload["pr_roles"] = pr_roles
    payload["current_pr_role"] = pr_roles["current"]
    if args.operation == "audit":
        return emit(payload)

    if payload.get("result") == "block":
        sync_plan = reconciliation_sync_plan(payload, include_closeout_comment=bool(comment_body))
        return emit(
            {
                **payload,
                "operation": "sync",
                "summary": "reconciliation sync stopped because audit returned block findings or missing inputs.",
                "sync_plan": sync_plan,
                "applied_actions": [],
                "skipped_actions": sync_plan["skipped_actions"],
                "manual_actions": sync_plan["manual_actions"],
                "remaining_findings": list(payload.get("findings", [])),
                "audit": payload,
                "refreshed_audit": payload,
                "dry_run": args.dry_run,
                "runtime_state": runtime_state,
            }
        )

    sync_plan = reconciliation_sync_plan(payload, include_closeout_comment=bool(comment_body))
    planned_actions = sync_plan["planned_actions"]
    skipped_actions = list(sync_plan["skipped_actions"])
    manual_actions = list(sync_plan["manual_actions"])
    remaining_findings = [
        finding
        for finding in payload.get("findings", [])
        if isinstance(finding, dict) and finding.get("severity") == "warn"
    ]
    sync_missing: list[str] = []

    if args.dry_run:
        dry_run_actions = [{**action, "dry_run": True} for action in planned_actions]
        has_unresolved_fix_needed = any(
            isinstance(finding, dict) and finding.get("severity") == "fix-needed"
            for finding in payload.get("findings", [])
        ) and (bool(skipped_actions) or bool(manual_actions))
        return emit(
            {
                **payload,
                "operation": "sync",
                "result": "block" if has_unresolved_fix_needed else "pass",
                "summary": (
                    "reconciliation sync dry-run produced the planned control-plane actions."
                    if not has_unresolved_fix_needed
                    else "reconciliation sync dry-run found fix-needed drift that still requires manual reconciliation."
                ),
                "sync_plan": {**sync_plan, "planned_actions": dry_run_actions},
                "applied_actions": [],
                "planned_actions": dry_run_actions,
                "skipped_actions": skipped_actions,
                "manual_actions": manual_actions,
                "remaining_findings": list(payload.get("findings", [])),
                "audit": payload,
                "refreshed_audit": payload,
                "dry_run": True,
                "fallback_to": None if not has_unresolved_fix_needed else "manual-reconciliation",
                "runtime_state": runtime_state,
            }
        )

    executed_actions: list[dict[str, Any]] = []
    for action in planned_actions:
        step_kind = action.get("action")
        subject = action.get("subject")
        if not isinstance(action.get("source_finding"), dict) or not isinstance(action.get("write_target"), dict) or not isinstance(action.get("proof_locator"), str):
            sync_missing.append(f"{subject} is missing safe sync proof for `{step_kind}`")
            skipped_actions.append(
                {
                    **action,
                    "reason": "missing safe sync proof, write target, or source finding",
                }
            )
            continue
        if step_kind == "add_closeout_comment":
            issue_number = action.get("issue_number")
            if not isinstance(issue_number, int):
                sync_missing.append(f"{subject} is missing an issue number for closeout comment sync")
                skipped_actions.append(
                    {
                        **action,
                        "reason": "missing issue number for closeout comment sync",
                    }
                )
                continue
            if not comment_body:
                sync_missing.append(f"{subject} has an add_closeout_comment plan action without comment body")
                skipped_actions.append({**action, "reason": "missing closeout comment body"})
                continue
            comment_result = run_process(
                [
                    "gh",
                    "issue",
                    "comment",
                    str(issue_number),
                    "--repo",
                    f"{owner}/{repo_name}",
                    "--body",
                    comment_body,
                ],
                target_root,
            )
            if comment_result.returncode != 0:
                sync_missing.append(comment_result.stderr.strip() or f"failed to comment on issue #{issue_number}")
                skipped_actions.append({**action, "reason": f"failed to comment on issue #{issue_number}"})
                continue
            executed_actions.append(action)
            continue
        if step_kind == "close_issue":
            issue_number = action.get("issue_number")
            if not isinstance(issue_number, int):
                sync_missing.append(f"{subject} is missing an issue number for reconciliation sync")
                skipped_actions.append({**action, "reason": "missing issue number for reconciliation sync"})
                continue
            close_result = run_process(
                ["gh", "issue", "close", str(issue_number), "--repo", f"{owner}/{repo_name}"],
                target_root,
            )
            if close_result.returncode != 0:
                sync_missing.append(close_result.stderr.strip() or f"failed to close issue #{issue_number}")
                skipped_actions.append(
                    {
                        **action,
                        "reason": close_result.stderr.strip() or f"failed to close issue #{issue_number}",
                    }
                )
                continue
            executed_actions.append(action)
            continue
        if step_kind == "set_project_done":
            step_errors = set_project_item_done(
                target_root,
                action["project_id"],
                action["item_id"],
                action["status_field_id"],
                action["done_option_id"],
            )
            if step_errors:
                sync_missing.extend(step_errors)
                skipped_actions.append(
                    {
                        **action,
                        "reason": "; ".join(step_errors),
                    }
                )
                continue
            executed_actions.append(action)
            continue
        if step_kind in {"add_blocked_by", "remove_blocked_by"}:
            issue_number = action.get("issue_number")
            blocking_issue_number = action.get("blocking_issue_number")
            write_target = action.get("write_target") if isinstance(action.get("write_target"), dict) else {}
            mutation = write_target.get("mutation") or ("addBlockedBy" if step_kind == "add_blocked_by" else "removeBlockedBy")
            if not isinstance(issue_number, int) or not isinstance(blocking_issue_number, int) or not isinstance(mutation, str):
                sync_missing.append(f"{subject} is missing native dependency mutation inputs")
                skipped_actions.append({**action, "reason": "missing native dependency mutation inputs"})
                continue
            step_errors = set_native_dependency(target_root, owner, repo_name, issue_number, blocking_issue_number, mutation)
            if step_errors:
                sync_missing.extend(step_errors)
                skipped_actions.append({**action, "reason": "; ".join(step_errors)})
                continue
            executed_actions.append(action)
            continue
        sync_missing.append(f"{subject} uses unsupported sync action `{step_kind}`")
        skipped_actions.append(
            {
                **action,
                "reason": f"unsupported sync action `{step_kind}`",
            }
        )

    refreshed_payload, refreshed_errors = reconciliation_audit_payload(
        target_root=target_root,
        expected_item=args.item,
        phase_number=args.phase,
        fr_number=args.fr,
        issue_number=args.issue,
        pr_number=args.pr,
        project_number=args.project,
        branch_name=args.branch,
        owner=owner,
        repo_name=repo_name,
        issue_payload_file=args.issue_payload_file,
        pr_payload_file=args.pr_payload_file,
        project_payload_file=args.project_payload_file,
    )
    if refreshed_errors:
        sync_missing.extend(refreshed_errors)
        refreshed_payload = payload
    remaining_findings = [finding for finding in refreshed_payload.get("findings", []) if isinstance(finding, dict)]
    unresolved_fix_needed = any(finding.get("severity") == "fix-needed" for finding in remaining_findings)

    result = "pass"
    summary = "reconciliation sync aligned the requested GitHub control-plane state."
    fallback_to = None
    if sync_missing or unresolved_fix_needed:
        result = "block"
        summary = "reconciliation sync could not fully align the requested GitHub control-plane state."
        fallback_to = "manual-reconciliation"

    return emit(
        {
            **refreshed_payload,
            "operation": "sync",
            "result": result,
            "summary": summary,
            "missing_inputs": list(dict.fromkeys(sync_missing + list(refreshed_payload.get("missing_inputs", [])))),
            "fallback_to": fallback_to,
            "sync_plan": sync_plan,
            "applied_actions": executed_actions,
            "skipped_actions": skipped_actions,
            "manual_actions": manual_actions,
            "remaining_findings": remaining_findings,
            "audit": payload,
            "refreshed_audit": refreshed_payload,
            "dry_run": False,
            "runtime_state": runtime_state,
        }
    )
