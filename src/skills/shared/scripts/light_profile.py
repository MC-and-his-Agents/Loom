#!/usr/bin/env python3
"""Light-governance carrier invariant and host migration reconciliation."""

from __future__ import annotations

import argparse
import base64
import json
import re
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import quote

from github_host import (
    gh_rest_authenticated_json,
    gh_rest_authenticated_list,
    gh_rest_authenticated_paginated_field,
    gh_rest_write_json,
)
from failure_envelope import envelope, primary_cause
from native_validation import parse_make_targets


sys.dont_write_bytecode = True

SCHEMA = "loom-light-profile-migration-plan/v1"
RECONCILE_SCHEMA = "loom-light-profile-migration-reconcile/v1"
INSTALLED_STATE_SCHEMA = "loom-installed-state/v2"
STATE_FILENAMES = (
    ".loom/installed-state.json",
    ".loom/installed-state.v2.json",
    ".loom/installed-state/installed-state.json",
)
LIGHT_PROFILES = frozenset(("light-governance", "attach-only"))
FORBIDDEN_CARRIERS = (
    (".loom/bootstrap/", "legacy_bootstrap"),
    (".loom/status/", "current_pointer"),
    (".loom/work-items/", "execution_carrier"),
    (".loom/progress/", "execution_carrier"),
    (".loom/specs/", "execution_carrier"),
    (".loom/stories/", "execution_carrier"),
    (".loom/reviews/", "execution_carrier"),
    (".loom/shadow/", "shadow_evidence"),
    (".loom/bin/", "runtime_payload"),
    (".loom/runtime/", "runtime_cache"),
    (".loom/tmp/", "runtime_cache"),
)
ALLOWED_BOOTSTRAP_LOCATORS = {".loom/bootstrap/manifest.json"}
DECLARATION_LOCATORS = (".loom/bootstrap/init-result.json", ".loom/bootstrap/manifest.json")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$")
DELIVERY_WORKFLOW = ".github/workflows/loom-delivery-gate.yml"
COMPANION = ".loom/companion/repo-interface.json"
CAUSE_CONTRACTS = {
    "not_applicable": ("governance_metadata", "not_applicable", "loom", False, "none"),
    "passed": ("governance_metadata", "passed", "loom", False, "none"),
    "light_profile_tree_unreadable": ("git_history", "unreadable", "repository", True, "restore readable Git tree state, then rerun the migration plan"),
    "light_profile_forbidden_carrier": ("carrier", "forbidden_carrier", "repository", False, "remove the reported forbidden carriers in the profile migration PR"),
    "light_profile_state_unreadable": ("carrier", "unreadable", "repository", False, "restore valid metadata-only light-profile installed state"),
    "invalid_input": ("governance_metadata", "invalid", "repository", False, "correct the reported reconciliation inputs, then rerun"),
    "gate_enabler_unverified": ("host_service", "unverified", "github", True, "restore the gate-enabler PR and check readback, then rerun"),
    "host_readback_unavailable": ("host_service", "unavailable", "github", True, "rerun after GitHub host readback is available"),
    "host_enforcement_unavailable": ("host_service", "host_enforcement_unavailable", "github", False, "configure a supported required-check identity before mutating required checks"),
    "required_set_unreadable": ("host_service", "unreadable", "github", True, "restore readable branch protection, then rerun"),
    "required_check_app_conflict": ("governance_metadata", "conflict", "operator", False, "remove the conflicting required-check app binding"),
    "unexpected_required_checks": ("governance_metadata", "unexpected", "operator", False, "declare each required check as retained or legacy"),
    "ruleset_migration_required": ("governance_metadata", "migration_required", "operator", False, "update the owning GitHub ruleset, then rerun"),
    "profile_migration_pr_unreadable": ("host_service", "unreadable", "github", True, "restore profile-migration PR readback, then rerun"),
    "profile_migration_pr_invalid": ("governance_metadata", "invalid", "repository", False, "retarget the profile-migration PR to the declared branch"),
    "planned": ("governance_metadata", "planned", "loom", False, "run the emitted reconciliation command with --apply when ready"),
    "partial_apply": ("host_service", "partial_apply", "operator", True, "rerun the emitted reconciliation command to converge host state"),
    "host_write_unchanged": ("host_service", "unchanged", "operator", True, "restore host write authority, then rerun reconciliation"),
    "required_set_not_ready": ("governance_metadata", "not_ready", "operator", True, "converge the required check set, then rerun"),
    "profile_migration_pending": ("governance_metadata", "pending", "repository", True, "merge the profile-migration PR, then rerun"),
    "main_tree_unreconciled": ("carrier", "unreconciled", "repository", True, "fix the reported main-tree contract, then rerun"),
    "reconciled": ("governance_metadata", "reconciled", "loom", False, "none"),
}


def _primary(cause_id: str, summary: str, *, details: dict[str, Any] | None = None) -> dict[str, Any]:
    domain, code, owner, retryable, remediation = CAUSE_CONTRACTS[cause_id]
    return primary_cause(
        cause_id=cause_id,
        failure_domain=domain,
        code=code,
        locator=f"light_profile:{cause_id}",
        summary=summary,
        owner=owner,
        retryable=retryable,
        details=details,
        remediation_command=remediation,
    )


def resolve_target(raw_target: str) -> Path:
    target = Path(raw_target).expanduser()
    return target.resolve() if target.is_absolute() else (Path.cwd() / target).resolve()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def installed_state(target: Path) -> tuple[str, dict[str, Any] | None, str | None]:
    for locator in STATE_FILENAMES:
        path = target / locator
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            return locator, None, "installed-state must be a regular JSON file inside the target"
        payload = read_json(path)
        if payload is None or payload.get("schema_version") != INSTALLED_STATE_SCHEMA:
            return locator, None, "installed-state is unreadable or has an unsupported schema"
        return locator, payload, None
    return ".loom/installed-state.json", None, "installed-state is missing"


def observed_paths(target: Path) -> tuple[dict[str, str], str | None]:
    observed: dict[str, str] = {}
    for source, args in (
        ("tracked", ["git", "ls-files", "--cached", "-z"]),
        ("untracked", ["git", "ls-files", "--others", "--exclude-standard", "-z"]),
        ("ignored", ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"]),
    ):
        completed = subprocess.run(
            args,
            cwd=target,
            check=False,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if completed.returncode != 0:
            return {}, "target is not a readable Git working tree"
        for raw_path in completed.stdout.split(b"\0"):
            if raw_path:
                observed.setdefault(raw_path.decode("utf-8"), source)
    return dict(sorted(observed.items())), None


def forbidden_kind(path: str) -> str | None:
    if path in ALLOWED_BOOTSTRAP_LOCATORS:
        return None
    for prefix, kind in FORBIDDEN_CARRIERS:
        if path.startswith(prefix):
            return kind
    return None


def forbidden_violations(paths: dict[str, str]) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path, source in paths.items():
        kind = forbidden_kind(path)
        if kind is not None:
            violations.append(
                {
                    "locator": path,
                    "kind": kind,
                    "source": source,
                    "disposition": "remove_in_profile_migration_pr",
                }
            )
    return violations


def has_absolute_filesystem_path(value: object) -> bool:
    """Reject any portable-metadata value that is an absolute POSIX or Windows path."""

    if isinstance(value, str):
        return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()
    if isinstance(value, dict):
        return any(has_absolute_filesystem_path(entry) for entry in value.values())
    if isinstance(value, list):
        return any(has_absolute_filesystem_path(entry) for entry in value)
    return False


def metadata_violations(target: Path, paths: dict[str, str]) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in (*STATE_FILENAMES, *DECLARATION_LOCATORS):
        if path not in paths:
            continue
        source = paths[path]
        candidate = target / path
        if candidate.is_symlink() or not candidate.is_file():
            violations.append(
                {
                    "locator": path,
                    "kind": "unsafe_metadata_locator",
                    "source": source,
                    "disposition": "remove_in_profile_migration_pr",
                }
            )
            continue
        payload = read_json(candidate)
        if payload is None:
            if path in DECLARATION_LOCATORS:
                violations.append(
                    {
                        "locator": path,
                        "kind": "invalid_legacy_metadata",
                        "source": source,
                        "disposition": "remove_in_profile_migration_pr",
                    }
                )
            continue
        if has_absolute_filesystem_path(payload):
            violations.append(
                {
                    "locator": path,
                    "kind": "absolute_workstation_path",
                    "source": source,
                    "disposition": "remove_in_profile_migration_pr",
                }
            )
        if path not in DECLARATION_LOCATORS:
            continue
        for field in ("initial_artifacts", "planned_writes"):
            entries = payload.get(field)
            if not isinstance(entries, list):
                continue
            for entry in entries:
                declared = entry.get("path") if isinstance(entry, dict) else None
                if not isinstance(declared, str):
                    continue
                kind = forbidden_kind(declared)
                if kind is not None:
                    violations.append(
                        {
                            "locator": f"{path}:{field}:{declared}",
                            "kind": "forbidden_declaration",
                            "source": source,
                            "disposition": "remove_in_profile_migration_pr",
                        }
                    )
    return violations


def migration_actions(
    violations: list[dict[str, str]], state_error: str | None, profile: str | None
) -> list[dict[str, Any]]:
    if not violations and state_error is None:
        return []
    return [
        {
            "id": "gate_enabler_pr",
            "status": "required",
            "mutates": False,
            "scope": "repository-scoped advisory delivery-gate PR",
            "preserve": [".loom/installed-state.json", ".loom/companion/**", ".github/PULL_REQUEST_TEMPLATE.md", ".github/workflows/**"],
            "host_readback": {"authority": "GitHub check run", "expect": "new delivery gate passes before required-set replacement"},
        },
        {
            "id": "required_set_host_readback",
            "status": "pending_after_gate_enabler",
            "mutates": False,
            "host_mutation_authority": "repository administrator",
            "atomic": False,
            "readback": {
                "authority": "GitHub branch protection and rulesets",
                "expect": "new delivery-gate identity is required and legacy required checks are absent",
            },
        },
        {
            "id": "profile_migration_pr",
            "status": "pending_after_required_set_readback",
            "mutates": False,
            "scope": "one repository-scoped profile-migration PR",
            "remove": violations,
            "installed_state": (
                f"rewrite to metadata-only {profile}" if state_error else f"retain validated metadata-only {profile} state"
            ),
            "post_merge_readback": [
                {"authority": "GitHub main tree", "expect_absent": [prefix for prefix, _kind in FORBIDDEN_CARRIERS]},
                {"authority": "GitHub changed paths", "expect": "old branches cannot reintroduce forbidden light-profile locators"},
            ],
        },
    ]


def plan_payload(target: Path) -> dict[str, Any]:
    locator, state, state_error = installed_state(target)
    repo_payload = state.get("repo_payload") if isinstance(state, dict) else {}
    profile = repo_payload.get("adoption_mode") if isinstance(repo_payload, dict) else None
    if state_error is None and profile in LIGHT_PROFILES and repo_payload.get("mode") != "metadata-only":
        state_error = f"{profile} installed-state must use metadata-only repository payload"
    if state_error is None and profile not in LIGHT_PROFILES:
        cause = _primary("not_applicable", "target does not declare a light-profile adoption")
        return {
            "schema_version": SCHEMA,
            "command": "repair plan",
            "operation": "plan",
            "result": "pass",
            "mutates": False,
            "host_mutations": False,
            "carrier_repair_actions": [],
            "applicable": False,
            "installed_state": {"locator": locator, "adoption_mode": profile},
            "primary_cause": cause,
            "failure_envelope": envelope(cause),
            "migration": {"status": "not_applicable", "actions": []},
        }

    paths, git_error = observed_paths(target)
    if git_error:
        cause = _primary("light_profile_tree_unreadable", git_error)
        return {
            "schema_version": SCHEMA,
            "command": "repair plan",
            "operation": "plan",
            "result": "block",
            "mutates": False,
            "host_mutations": False,
            "carrier_repair_actions": [],
            "applicable": True,
            "installed_state": {"locator": locator, "adoption_mode": profile},
            "legacy_gate_blocker": True,
            "violations": [],
            "migration": {"status": "blocked_tree_read", "reentrant": True, "actions": []},
            "primary_cause": cause,
            "failure_envelope": envelope(cause),
            "failed_layer": "light-profile-tree",
            "fail_closed_reason": git_error,
        }

    violations = [*forbidden_violations(paths), *metadata_violations(target, paths)]
    violations.sort(key=lambda item: (item["locator"], item["kind"], item["source"]))
    migration = migration_actions(violations, state_error, profile)
    passed = not violations and state_error is None
    primary_id = "passed" if passed else "light_profile_forbidden_carrier" if violations else "light_profile_state_unreadable"
    summary = (
        "observed tree satisfies the light-profile carrier invariant"
        if passed
        else "observed Loom execution carriers conflict with light-profile adoption"
        if violations
        else str(state_error)
    )
    cause = _primary(primary_id, summary, details={"violation_count": len(violations)})
    return {
        "schema_version": SCHEMA,
        "command": "repair plan",
        "operation": "plan",
        "result": "pass" if passed else "block",
        "mutates": False,
        "host_mutations": False,
        "carrier_repair_actions": [],
        "applicable": True,
        "installed_state": {"locator": locator, "status": "valid" if state_error is None else "invalid", "adoption_mode": profile},
        "observed_tree": {
            "sources": {source: sum(1 for value in paths.values() if value == source) for source in ("tracked", "untracked", "ignored")},
            "file_count": len(paths),
        },
        "primary_cause": cause,
        "failure_envelope": envelope(cause),
        "legacy_gate_blocker": not passed,
        "violations": violations,
        "migration": {
            "status": "not_required" if passed else "profile_migration_required",
            "reentrant": True,
            "actions": migration,
        },
        "prohibited_actions": [
            "carrier repair",
            "carrier closeout-sync",
            "authored head repair",
            "closeout PR",
        ],
    }


def repository_parts(repository: str) -> tuple[str, str]:
    if not REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must be OWNER/REPOSITORY")
    return tuple(repository.split("/", 1))  # type: ignore[return-value]


def recovery_command(
    *,
    target: Path,
    repository: str,
    branch: str,
    work_item: int,
    gate_pr: int,
    migration_pr: int,
    context: str,
    app_id: int,
    legacy_contexts: list[str],
    retained_contexts: list[str],
    trust_mode: str,
) -> str:
    values = [
        "loom", "profile", "light-migration-reconcile",
        "--target", str(target), "--repository", repository, "--branch", branch,
        "--work-item", str(work_item), "--gate-pr", str(gate_pr),
        "--migration-pr", str(migration_pr), "--context", context,
        "--app-id", str(app_id),
        "--trust-mode", trust_mode,
    ]
    for value in legacy_contexts:
        values.extend(("--legacy-context", value))
    for value in retained_contexts:
        values.extend(("--retained-context", value))
    values.extend(("--apply", "--json"))
    return " ".join(shlex.quote(value) for value in values)


def _response(
    result: str,
    cause: str,
    summary: str,
    *,
    operation: str,
    repository: str,
    branch: str,
    work_item: int,
    next_action: str | None,
    writes: list[dict[str, Any]],
    attempts: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    mutation_attempts = attempts or []
    uncertain = any(item.get("outcome") == "indeterminate" for item in mutation_attempts)
    primary = _primary(cause, summary, details={"operation": operation, "work_item": work_item})
    payload = {
        "schema_version": RECONCILE_SCHEMA,
        "command": "profile light-migration-reconcile",
        "operation": operation,
        "result": result,
        "migration": {"status": cause, "reentrant": True, "atomic": False},
        "repository": repository,
        "branch": branch,
        "work_item": work_item,
        "mutates": bool(writes) or uncertain,
        "host_mutations": bool(writes) or uncertain,
        "host_writes": writes,
        "host_mutation_attempts": mutation_attempts,
        "primary_cause": primary,
        "failure_envelope": envelope(primary),
        "next_action": next_action,
    }
    payload.update(extra)
    return payload


def _required_set_readback(
    root: Path,
    repository: str,
    branch: str,
    context: str,
    app_id: int,
    legacy_contexts: list[str],
    retained_contexts: list[str],
    trust_mode: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]], list[str]]:
    from delivery_gate import build_required_check_identity, evaluate_required_check_identity

    owner, repo = repository_parts(repository)
    encoded = quote(branch, safe="")
    protection, protection_errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/branches/{encoded}/protection"
    )
    rules, rule_errors = gh_rest_authenticated_list(
        root, f"repos/{owner}/{repo}/rules/branches/{encoded}"
    )
    errors = [*[f"branch protection: {value}" for value in protection_errors], *[f"applicable rules: {value}" for value in rule_errors]]
    if errors or protection is None:
        return protection, None, rules, errors
    evidence = build_required_check_identity(
        {"owner": owner, "name": repo},
        branch,
        context,
        app_id,
        legacy_contexts,
        retained_contexts,
        protection,
        rules,
        datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        trust_mode=trust_mode,
    )
    return protection, evaluate_required_check_identity(evidence), rules, []


def _branch_checks(protection: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]] | None:
    required = protection.get("required_status_checks")
    checks = required.get("checks") if isinstance(required, dict) else None
    if not isinstance(required, dict) or not isinstance(checks, list):
        return None
    normalized = [
        {"context": item.get("context"), "app_id": item.get("app_id")}
        for item in checks
        if isinstance(item, dict) and isinstance(item.get("context"), str) and isinstance(item.get("app_id"), int)
    ]
    if len(normalized) != len(checks):
        return None
    return bool(required.get("strict")), normalized


def _update_branch_checks(
    root: Path,
    repository: str,
    branch: str,
    *,
    strict: bool,
    checks: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, list[str]]:
    owner, repo = repository_parts(repository)
    return gh_rest_write_json(
        root,
        method="PATCH",
        path=f"repos/{owner}/{repo}/branches/{quote(branch, safe='')}/protection/required_status_checks",
        request_payload={"strict": strict, "checks": checks},
    )


def _checks_key(checks: list[dict[str, Any]]) -> list[tuple[str, int]]:
    return sorted((str(item["context"]), int(item["app_id"])) for item in checks)


def _attempt_required_set_mutation(
    root: Path,
    repository: str,
    branch: str,
    context: str,
    app_id: int,
    legacy_contexts: list[str],
    retained_contexts: list[str],
    trust_mode: str,
    *,
    strict: bool,
    before: list[dict[str, Any]],
    desired: list[dict[str, Any]],
    action: str,
) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None, list[str], dict[str, Any]]:
    _payload, transport_errors = _update_branch_checks(
        root, repository, branch, strict=strict, checks=desired
    )
    protection, identity, _rules, read_errors = _required_set_readback(
        root, repository, branch, context, app_id, legacy_contexts, retained_contexts, trust_mode
    )
    state = _branch_checks(protection or {})
    if state is not None and _checks_key(state[1]) == _checks_key(desired):
        outcome = "applied"
    elif state is not None and _checks_key(state[1]) == _checks_key(before):
        outcome = "unchanged"
    else:
        outcome = "indeterminate"
    errors = [*transport_errors, *read_errors]
    attempt = {
        "locator": f"github:{repository}:branch:{branch}:required_status_checks",
        "action": action,
        "outcome": outcome,
        "transport_errors": transport_errors,
        "readback_errors": read_errors,
    }
    return outcome, protection, identity, errors, attempt


def _pr_readback(root: Path, repository: str, number: int) -> tuple[dict[str, Any] | None, list[str]]:
    owner, repo = repository_parts(repository)
    return gh_rest_authenticated_json(root, f"repos/{owner}/{repo}/pulls/{number}")


def _gate_pr_readback(
    root: Path,
    repository: str,
    branch: str,
    number: int,
    context: str,
    app_id: int,
) -> tuple[dict[str, Any], list[str]]:
    owner, repo = repository_parts(repository)
    pull, errors = _pr_readback(root, repository, number)
    if errors or pull is None:
        return {}, [f"gate PR readback: {value}" for value in errors] or ["gate PR is unreadable"]
    base = pull.get("base") if isinstance(pull.get("base"), dict) else {}
    head = pull.get("head") if isinstance(pull.get("head"), dict) else {}
    head_sha = head.get("sha")
    failures: list[str] = []
    if not pull.get("merged_at") or base.get("ref") != branch or not isinstance(head_sha, str):
        failures.append(f"gate-enabler PR #{number} must be merged into {branch} with a readable head")
        return {}, failures
    runs, run_errors = gh_rest_authenticated_paginated_field(
        root, f"repos/{owner}/{repo}/commits/{head_sha}/check-runs?per_page=100", "check_runs"
    )
    if run_errors:
        return {}, [f"gate check readback: {value}" for value in run_errors]
    matching = [
        run for run in runs
        if isinstance(run, dict)
        and (
            run.get("name") == context
            or context.endswith(" / " + str(run.get("name")))
        )
        and run.get("conclusion") == "success"
        and isinstance(run.get("app"), dict)
        and run["app"].get("id") == app_id
    ]
    if not matching:
        failures.append(f"gate-enabler PR #{number} has no successful {context!r} check from app {app_id}")
        return {}, failures
    merge_sha = pull.get("merge_commit_sha")
    if not isinstance(merge_sha, str):
        return {}, [f"gate-enabler PR #{number} is missing merge commit sha"]
    tree, tree_errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/git/trees/{merge_sha}?recursive=1"
    )
    if tree_errors or tree is None or tree.get("truncated") is True or not isinstance(tree.get("tree"), list):
        return {}, [f"gate-enabler tree readback: {value}" for value in tree_errors] or ["gate-enabler tree readback is incomplete"]
    workflow = next(
        (
            item for item in tree["tree"]
            if isinstance(item, dict) and item.get("type") == "blob" and item.get("path") == DELIVERY_WORKFLOW
        ),
        None,
    )
    if not isinstance(workflow, dict) or not isinstance(workflow.get("sha"), str):
        return {}, [f"gate-enabler merge commit does not contain {DELIVERY_WORKFLOW}"]
    return {
        "pr": number,
        "head_sha": head_sha,
        "merge_commit_sha": merge_sha,
        "workflow_blob_sha": workflow["sha"],
        "check": {"context": context, "app_id": app_id},
    }, []


def _remote_file_bytes(
    root: Path, repository: str, branch: str, locator: str
) -> tuple[bytes | None, list[str]]:
    owner, repo = repository_parts(repository)
    payload, errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/contents/{quote(locator, safe='/')}?ref={quote(branch, safe='')}"
    )
    if errors or payload is None:
        return None, errors or [f"{locator} content is unreadable"]
    try:
        return base64.b64decode("".join(str(payload.get("content", "")).split()), validate=True), []
    except ValueError as exc:
        return None, [f"{locator} content is not valid base64: {exc}"]


def _workflow_contract_errors(content: bytes) -> list[str]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"delivery workflow is not UTF-8: {exc}"]
    stack: list[tuple[int, str]] = []
    triggers: set[str] = set()
    pinned_jobs: dict[str, str] = {}
    job_inputs: dict[str, dict[str, str]] = {}
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", raw_line).rstrip()
        indent = len(line) - len(line.lstrip())
        match = re.match(r"^\s*([\w.'\"-]+)\s*:\s*(.*)$", line)
        if not match:
            continue
        key = match.group(1).strip("'\"")
        value = match.group(2).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = [item[1] for item in stack]
        if key == "on" and not path and value.startswith("[") and value.endswith("]"):
            triggers.update(item.strip().strip("'\"") for item in value[1:-1].split(","))
        elif path == ["on"] and key in {"pull_request_target", "merge_group"}:
            triggers.add(key)
        if key == "uses" and len(path) == 2 and path[0] == "jobs":
            pinned = re.fullmatch(
                r"\S*/\.github/workflows/loom-delivery-gate\.yml@([0-9a-fA-F]{40})",
                value,
            )
            if pinned:
                pinned_jobs[path[1]] = pinned.group(1).lower()
        elif len(path) == 3 and path[0] == "jobs" and path[2] == "with":
            job_inputs.setdefault(path[1], {})[key] = value.strip("'\"")
        stack.append((indent, key))

    errors: list[str] = []
    missing = sorted({"pull_request_target", "merge_group"} - triggers)
    if missing:
        errors.append("delivery workflow is missing active triggers: " + ", ".join(missing))
    if not pinned_jobs:
        errors.append("delivery workflow does not use the SHA-pinned reusable gate at job level")
    for job, pinned_sha in sorted(pinned_jobs.items()):
        inputs = job_inputs.get(job, {})
        host_facts = inputs.get("host_facts", "").strip()
        if not host_facts or host_facts in {">", "|", ">-", "|-"}:
            errors.append(f"delivery workflow job {job!r} must declare host_facts")
        loom_ref = inputs.get("loom_ref", "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{40}", loom_ref) or loom_ref != pinned_sha:
            errors.append(f"delivery workflow job {job!r} loom_ref must equal its job-level uses SHA")
        _targets, validation_errors = parse_make_targets(inputs.get("validation_command"))
        errors.extend(f"delivery workflow job {job!r} {error}" for error in validation_errors)
        if inputs.get("enforcement") != "enforce":
            errors.append(f"delivery workflow job {job!r} must declare enforcement: enforce")
        if inputs.get("profile") != "light":
            errors.append(f"delivery workflow job {job!r} must declare profile: light")
    return errors


def _main_tree_readback(
    root: Path,
    repository: str,
    branch: str,
    expected_workflow_sha: str,
) -> tuple[dict[str, Any], list[str]]:
    owner, repo = repository_parts(repository)
    branch_payload, branch_errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/branches/{quote(branch, safe='')}"
    )
    if branch_errors or branch_payload is None:
        return {}, [f"main branch readback: {value}" for value in branch_errors] or ["main branch is unreadable"]
    commit = branch_payload.get("commit") if isinstance(branch_payload.get("commit"), dict) else {}
    sha = commit.get("sha")
    if not isinstance(sha, str):
        return {}, ["main branch readback is missing commit sha"]
    tree, tree_errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
    )
    if tree_errors or tree is None:
        return {}, [f"main tree readback: {value}" for value in tree_errors] or ["main tree is unreadable"]
    if tree.get("truncated") is True or not isinstance(tree.get("tree"), list):
        return {}, ["main tree recursive readback is incomplete"]
    blobs = {
        item.get("path"): item.get("sha")
        for item in tree["tree"]
        if isinstance(item, dict) and item.get("type") == "blob" and isinstance(item.get("path"), str)
    }
    paths = set(blobs)
    errors: list[str] = []
    for required in (COMPANION, DELIVERY_WORKFLOW):
        if required not in paths:
            errors.append(f"main tree is missing {required}")
    forbidden = sorted(path for path in paths if forbidden_kind(path) is not None)
    if forbidden:
        errors.append("main tree still contains forbidden light-profile carriers: " + ", ".join(forbidden))
    state_locator = next((value for value in STATE_FILENAMES if value in paths), None)
    if state_locator is None:
        errors.append("main tree is missing installed-state")
        return {"commit": sha, "paths": len(paths), "forbidden": forbidden}, errors
    state_content, state_errors = _remote_file_bytes(root, repository, branch, state_locator)
    installed: dict[str, Any] | None = None
    if state_errors or state_content is None:
        errors.extend(f"installed-state readback: {value}" for value in state_errors)
    else:
        try:
            value = json.loads(state_content.decode("utf-8"))
            installed = value if isinstance(value, dict) else None
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"installed-state content is unreadable: {exc}")
        if installed is not None:
            repo_payload = installed.get("repo_payload") if isinstance(installed, dict) else {}
            if (
                not isinstance(installed, dict)
                or installed.get("schema_version") != INSTALLED_STATE_SCHEMA
                or not isinstance(repo_payload, dict)
                or repo_payload.get("mode") != "metadata-only"
                or repo_payload.get("adoption_mode") not in LIGHT_PROFILES
            ):
                errors.append("installed-state does not declare a metadata-only light profile")
        elif not errors:
            errors.append("installed-state content must be a JSON object")

    companion_content, companion_errors = _remote_file_bytes(root, repository, branch, COMPANION)
    companion: dict[str, Any] | None = None
    if companion_errors or companion_content is None:
        errors.extend(f"companion readback: {value}" for value in companion_errors)
    else:
        try:
            value = json.loads(companion_content.decode("utf-8"))
            companion = value if isinstance(value, dict) else None
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"companion content is unreadable: {exc}")
        requirements = companion.get("repo_specific_requirements") if isinstance(companion, dict) else None
        if (
            not isinstance(companion, dict)
            or companion.get("schema_version") != "loom-repo-interface/v2"
            or not isinstance(requirements, dict)
            or any(not isinstance(requirements.get(key), list) for key in ("review", "merge_ready", "closeout"))
            or not isinstance(companion.get("specialized_gates"), list)
        ):
            errors.append("companion does not satisfy the loom-repo-interface/v2 profile contract")

    workflow_content, workflow_errors = _remote_file_bytes(root, repository, branch, DELIVERY_WORKFLOW)
    if workflow_errors or workflow_content is None:
        errors.extend(f"delivery workflow readback: {value}" for value in workflow_errors)
    else:
        errors.extend(_workflow_contract_errors(workflow_content))
    if blobs.get(DELIVERY_WORKFLOW) != expected_workflow_sha:
        errors.append("delivery workflow blob does not match the verified gate-enabler merge commit")
    return {
        "commit": sha,
        "paths": len(paths),
        "forbidden": forbidden,
        "installed_state": state_locator,
        "companion_schema": companion.get("schema_version") if isinstance(companion, dict) else None,
        "workflow_blob_sha": blobs.get(DELIVERY_WORKFLOW),
        "workflow_bound_to_gate_enabler": blobs.get(DELIVERY_WORKFLOW) == expected_workflow_sha,
    }, errors


def reconcile_payload(
    target: Path,
    *,
    repository: str,
    branch: str,
    work_item: int,
    gate_pr: int,
    migration_pr: int,
    context: str,
    app_id: int,
    legacy_contexts: list[str],
    retained_contexts: list[str],
    apply: bool,
    trust_mode: str = "pull_request_target_same_app",
) -> dict[str, Any]:
    operation = "apply" if apply else "dry_run"
    writes: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    recovery = recovery_command(
        target=target, repository=repository, branch=branch, work_item=work_item,
        gate_pr=gate_pr, migration_pr=migration_pr, context=context, app_id=app_id,
        legacy_contexts=legacy_contexts, retained_contexts=retained_contexts, trust_mode=trust_mode,
    )
    try:
        repository_parts(repository)
    except ValueError as exc:
        return _response("block", "invalid_input", str(exc), operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    if not branch.strip() or not context.strip() or min(work_item, gate_pr, migration_pr, app_id) <= 0:
        return _response("block", "invalid_input", "branch and context must be non-empty; numeric locators must be positive", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    if context in legacy_contexts or set(legacy_contexts) & set(retained_contexts):
        return _response("block", "invalid_input", "expected, legacy, and retained contexts must not conflict", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    if trust_mode == "distinct_app_check" and app_id == 15368:
        return _response(
            "block",
            "host_enforcement_unavailable",
            "distinct_app_check requires an app identity different from GitHub Actions",
            operation=operation,
            repository=repository,
            branch=branch,
            work_item=work_item,
            next_action="use the distinct App id or select pull_request_target_same_app with explicit limited assurance",
            writes=writes,
        )
    if trust_mode == "required_workflow":
        return _response(
            "block",
            "host_enforcement_unavailable",
            "required-workflow migration is not implemented; use the base-owned same-app gate or an optional distinct App",
            operation=operation,
            repository=repository,
            branch=branch,
            work_item=work_item,
            next_action="rerun with --trust-mode pull_request_target_same_app or distinct_app_check and the matching app id",
            writes=writes,
        )

    gate_readback, gate_errors = _gate_pr_readback(target, repository, branch, gate_pr, context, app_id)
    if gate_errors:
        return _response("block", "gate_enabler_unverified", gate_errors[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=gate_errors)

    protection, identity, rules, read_errors = _required_set_readback(
        target, repository, branch, context, app_id, legacy_contexts, retained_contexts, trust_mode
    )
    if read_errors or protection is None or identity is None:
        return _response("block", "host_readback_unavailable", (read_errors or ["required-set readback is incomplete"])[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=read_errors)
    branch_state = _branch_checks(protection)
    if branch_state is None:
        return _response("block", "required_set_unreadable", "branch protection required checks are unreadable", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes)
    strict, checks = branch_state
    context_bindings = [item for item in checks if item["context"] == context]
    conflicting_apps = sorted({
        int(item["app_id"])
        for item in context_bindings
        if item["app_id"] != app_id
    })
    if conflicting_apps or len(context_bindings) > 1:
        detail = ", ".join(str(value) for value in conflicting_apps) or "duplicate intended bindings"
        return _response("block", "required_check_app_conflict", f"{context!r} must have exactly one app binding; observed: {detail}", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    allowed = {context, *legacy_contexts, *retained_contexts}
    unexpected = sorted({item["context"] for item in checks if item["context"] not in allowed})
    if unexpected:
        return _response("block", "unexpected_required_checks", f"required checks need an explicit retained or legacy disposition: {', '.join(unexpected)}", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    ruleset_unexpected = sorted({
        item.get("context")
        for item in identity.get("identity", {}).get("unexpected_required_checks", [])
        if isinstance(item, dict) and item.get("plane") == "ruleset" and isinstance(item.get("context"), str)
    })
    if ruleset_unexpected:
        return _response("block", "unexpected_required_checks", f"applicable ruleset checks need an explicit retained or legacy disposition: {', '.join(ruleset_unexpected)}", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    ruleset_legacy = sorted({
        item.get("context")
        for item in identity.get("identity", {}).get("legacy_required_checks", [])
        if isinstance(item, dict) and item.get("plane") == "ruleset" and isinstance(item.get("context"), str)
    })
    if ruleset_legacy:
        return _response("block", "ruleset_migration_required", f"legacy checks are still owned by an applicable ruleset: {', '.join(ruleset_legacy)}", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action="update the named GitHub ruleset, then rerun " + recovery, writes=writes, applicable_rules=rules)

    expected = {"context": context, "app_id": app_id}
    add_required = not any(item == expected for item in checks)
    remove_legacy = any(item["context"] in legacy_contexts for item in checks)
    migration_pull, migration_errors = _pr_readback(target, repository, migration_pr)
    if migration_errors or migration_pull is None:
        return _response("block", "profile_migration_pr_unreadable", (migration_errors or ["profile migration PR is unreadable"])[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=migration_errors)
    migration_base = migration_pull.get("base") if isinstance(migration_pull.get("base"), dict) else {}
    if migration_base.get("ref") != branch:
        return _response("block", "profile_migration_pr_invalid", f"profile migration PR #{migration_pr} does not target {branch}", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    planned = [
        *([{"id": "add_delivery_gate_required_check", "atomic": False}] if add_required else []),
        *([{"id": "remove_legacy_required_checks", "atomic": False}] if remove_legacy else []),
        {"id": "profile_migration_main_readback", "atomic": False},
    ]
    if not apply:
        return _response("pass", "planned", "profile migration reconciliation is ready for explicit apply", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, planned_actions=planned, migration_pr={"number": migration_pr, "merged": bool(migration_pull.get("merged_at"))}, required_set=identity)

    if add_required:
        desired = [*checks, expected]
        outcome, protection, identity, errors, attempt = _attempt_required_set_mutation(
            target, repository, branch, context, app_id, legacy_contexts, retained_contexts,
            trust_mode,
            strict=strict, before=checks, desired=desired, action="add_delivery_gate_required_check",
        )
        attempts.append(attempt)
        if outcome == "indeterminate":
            writes.append(attempt)
            return _response("partial_apply", "partial_apply", "delivery gate mutation outcome is indeterminate after mandatory host readback", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, missing_inputs=errors)
        if outcome == "unchanged":
            return _response("block", "host_write_unchanged", (errors or ["delivery gate mutation was not applied"])[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, missing_inputs=errors)
        writes.append({**attempt, "context": context})
        branch_state = _branch_checks(protection or {})
        if branch_state is None or identity is None:
            return _response("partial_apply", "partial_apply", "delivery gate was applied but required-set readback is incomplete", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, missing_inputs=errors)
        strict, checks = branch_state

    if remove_legacy:
        desired = [item for item in checks if item["context"] not in legacy_contexts]
        outcome, _protection, _identity, errors, attempt = _attempt_required_set_mutation(
            target, repository, branch, context, app_id, legacy_contexts, retained_contexts,
            trust_mode,
            strict=strict, before=checks, desired=desired, action="remove_legacy_required_checks",
        )
        attempts.append(attempt)
        if outcome == "indeterminate":
            writes.append(attempt)
            return _response("partial_apply", "partial_apply", "legacy required-check mutation outcome is indeterminate after mandatory host readback", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, missing_inputs=errors)
        if outcome == "unchanged":
            return _response("partial_apply" if writes else "block", "partial_apply" if writes else "host_write_unchanged", (errors or ["legacy required-check mutation was not applied"])[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, missing_inputs=errors)
        writes.append({**attempt, "contexts": sorted(legacy_contexts)})

    final_protection, identity, _rules, errors = _required_set_readback(target, repository, branch, context, app_id, legacy_contexts, retained_contexts, trust_mode)
    final_state = _branch_checks(final_protection or {})
    final_bindings = [item for item in final_state[1] if item["context"] == context] if final_state is not None else []
    if final_bindings != [expected]:
        errors = [*errors, "required check context is not bound exactly once to the intended app identity"]
    if errors or identity is None or identity.get("result") != "ready":
        summary = errors[0] if errors else str(identity.get("primary_cause", {}).get("summary", "required-set readback is not ready"))
        return _response("partial_apply" if writes else "block", "partial_apply" if writes else "required_set_not_ready", summary, operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, required_set=identity, missing_inputs=errors)

    if not migration_pull.get("merged_at"):
        return _response("partial_apply" if writes else "block", "partial_apply" if writes else "profile_migration_pending", f"profile migration PR #{migration_pr} must merge before main-tree readback", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, required_set=identity)
    readback, errors = _main_tree_readback(target, repository, branch, str(gate_readback["workflow_blob_sha"]))
    if errors:
        return _response("partial_apply" if writes else "block", "partial_apply" if writes else "main_tree_unreconciled", errors[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, attempts=attempts, missing_inputs=errors, main_tree=readback, required_set=identity)
    return _response("pass", "reconciled", "light profile migration is host-readback complete", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes, attempts=attempts, main_tree=readback, required_set=identity, gate_enabler=gate_readback, old_branch_reintroduction_guard={"workflow": DELIVERY_WORKFLOW, "workflow_blob_sha": gate_readback["workflow_blob_sha"], "required_check": {"context": context, "app_id": app_id}, "forbidden_carrier_evaluator": "light_profile.plan_payload"})


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("plan", "reconcile"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--repository")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--work-item", type=int)
    parser.add_argument("--gate-pr", type=int)
    parser.add_argument("--migration-pr", type=int)
    parser.add_argument("--context")
    parser.add_argument("--app-id", type=int)
    parser.add_argument("--trust-mode", choices=("required_workflow", "distinct_app_check", "pull_request_target_same_app"), default="pull_request_target_same_app")
    parser.add_argument("--legacy-context", action="append", default=[])
    parser.add_argument("--retained-context", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target = resolve_target(args.target)
    if args.operation == "plan":
        payload = plan_payload(target)
    else:
        missing = [name for name in ("repository", "work_item", "gate_pr", "migration_pr", "context", "app_id") if getattr(args, name) is None]
        if missing:
            raise SystemExit("reconcile requires " + ", ".join("--" + name.replace("_", "-") for name in missing))
        payload = reconcile_payload(
            target,
            repository=args.repository,
            branch=args.branch,
            work_item=args.work_item,
            gate_pr=args.gate_pr,
            migration_pr=args.migration_pr,
            context=args.context,
            app_id=args.app_id,
            legacy_contexts=args.legacy_context,
            retained_contexts=args.retained_context,
            trust_mode=args.trust_mode,
            apply=args.apply,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
