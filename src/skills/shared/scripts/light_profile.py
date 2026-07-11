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

from github_host import gh_rest_authenticated_json, gh_rest_authenticated_list, gh_rest_write_json


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
ALLOWED_BOOTSTRAP_LOCATORS = {".loom/bootstrap/init-result.json"}
DECLARATION_LOCATORS = (".loom/bootstrap/init-result.json", ".loom/bootstrap/manifest.json")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$")
DELIVERY_WORKFLOW = ".github/workflows/loom-delivery-gate.yml"
COMPANION = ".loom/companion/repo-interface.json"


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
        return {
            "schema_version": SCHEMA,
            "command": "profile light-migration-plan",
            "operation": "plan",
            "result": "pass",
            "mutates": False,
            "host_mutations": False,
            "carrier_repair_actions": [],
            "applicable": False,
            "installed_state": {"locator": locator, "adoption_mode": profile},
            "primary_cause": {
                "id": "not_applicable",
                "domain": "light_profile",
                "summary": "target does not declare a light-profile adoption",
            },
            "migration": {"status": "not_applicable", "actions": []},
        }

    paths, git_error = observed_paths(target)
    if git_error:
        return {
            "schema_version": SCHEMA,
            "command": "profile light-migration-plan",
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
            "primary_cause": {
                "id": "light_profile_tree_unreadable",
                "domain": "git_tree",
                "summary": git_error,
            },
            "failed_layer": "light-profile-tree",
            "fail_closed_reason": git_error,
        }

    violations = [*forbidden_violations(paths), *metadata_violations(target, paths)]
    violations.sort(key=lambda item: (item["locator"], item["kind"], item["source"]))
    migration = migration_actions(violations, state_error, profile)
    passed = not violations and state_error is None
    primary_id = "passed" if passed else "light_profile_forbidden_carrier" if violations else "light_profile_state_unreadable"
    return {
        "schema_version": SCHEMA,
        "command": "profile light-migration-plan",
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
        "primary_cause": {
            "id": primary_id,
            "domain": "light_profile" if primary_id != "light_profile_state_unreadable" else "installed_state",
            "summary": (
                "observed tree satisfies the light-profile carrier invariant"
                if passed
                else "observed Loom execution carriers conflict with light-profile adoption"
                if violations
                else str(state_error)
            ),
        },
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
) -> str:
    values = [
        "loom", "profile", "light-migration-reconcile",
        "--target", str(target), "--repository", repository, "--branch", branch,
        "--work-item", str(work_item), "--gate-pr", str(gate_pr),
        "--migration-pr", str(migration_pr), "--context", context,
        "--app-id", str(app_id),
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
    **extra: Any,
) -> dict[str, Any]:
    payload = {
        "schema_version": RECONCILE_SCHEMA,
        "command": "profile light-migration-reconcile",
        "operation": operation,
        "result": result,
        "migration": {"status": cause, "reentrant": True, "atomic": False},
        "repository": repository,
        "branch": branch,
        "work_item": work_item,
        "mutates": bool(writes),
        "host_mutations": bool(writes),
        "host_writes": writes,
        "primary_cause": {"id": cause, "domain": "profile_migration", "summary": summary},
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


def _pr_readback(root: Path, repository: str, number: int) -> tuple[dict[str, Any] | None, list[str]]:
    owner, repo = repository_parts(repository)
    return gh_rest_authenticated_json(root, f"repos/{owner}/{repo}/pulls/{number}")


def _gate_pr_errors(
    root: Path,
    repository: str,
    branch: str,
    number: int,
    context: str,
    app_id: int,
) -> list[str]:
    owner, repo = repository_parts(repository)
    pull, errors = _pr_readback(root, repository, number)
    if errors or pull is None:
        return [f"gate PR readback: {value}" for value in errors] or ["gate PR is unreadable"]
    base = pull.get("base") if isinstance(pull.get("base"), dict) else {}
    head = pull.get("head") if isinstance(pull.get("head"), dict) else {}
    head_sha = head.get("sha")
    failures: list[str] = []
    if not pull.get("merged_at") or base.get("ref") != branch or not isinstance(head_sha, str):
        failures.append(f"gate-enabler PR #{number} must be merged into {branch} with a readable head")
        return failures
    runs, run_errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/commits/{head_sha}/check-runs?per_page=100"
    )
    if run_errors or runs is None:
        return [f"gate check readback: {value}" for value in run_errors] or ["gate check readback is unreadable"]
    check_runs = runs.get("check_runs")
    if not isinstance(check_runs, list):
        return ["gate check readback is missing check_runs"]
    matching = [
        run for run in check_runs
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
    return failures


def _main_tree_readback(root: Path, repository: str, branch: str) -> tuple[dict[str, Any], list[str]]:
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
    paths = {
        item.get("path")
        for item in tree["tree"]
        if isinstance(item, dict) and item.get("type") == "blob" and isinstance(item.get("path"), str)
    }
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
    state, state_errors = gh_rest_authenticated_json(
        root, f"repos/{owner}/{repo}/contents/{quote(state_locator, safe='/')}?ref={quote(branch, safe='')}"
    )
    if state_errors or state is None:
        errors.extend(f"installed-state readback: {value}" for value in state_errors)
    else:
        try:
            raw = base64.b64decode("".join(str(state.get("content", "")).split()), validate=True)
            installed = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"installed-state content is unreadable: {exc}")
        else:
            repo_payload = installed.get("repo_payload") if isinstance(installed, dict) else {}
            if (
                not isinstance(installed, dict)
                or installed.get("schema_version") != INSTALLED_STATE_SCHEMA
                or not isinstance(repo_payload, dict)
                or repo_payload.get("mode") != "metadata-only"
                or repo_payload.get("adoption_mode") not in LIGHT_PROFILES
            ):
                errors.append("installed-state does not declare a metadata-only light profile")
    return {"commit": sha, "paths": len(paths), "forbidden": forbidden, "installed_state": state_locator}, errors


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
) -> dict[str, Any]:
    operation = "apply" if apply else "dry_run"
    writes: list[dict[str, Any]] = []
    recovery = recovery_command(
        target=target, repository=repository, branch=branch, work_item=work_item,
        gate_pr=gate_pr, migration_pr=migration_pr, context=context, app_id=app_id,
        legacy_contexts=legacy_contexts, retained_contexts=retained_contexts,
    )
    try:
        repository_parts(repository)
    except ValueError as exc:
        return _response("block", "invalid_input", str(exc), operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    if not branch.strip() or not context.strip() or min(work_item, gate_pr, migration_pr, app_id) <= 0:
        return _response("block", "invalid_input", "branch and context must be non-empty; numeric locators must be positive", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)
    if context in legacy_contexts or set(legacy_contexts) & set(retained_contexts):
        return _response("block", "invalid_input", "expected, legacy, and retained contexts must not conflict", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes)

    gate_errors = _gate_pr_errors(target, repository, branch, gate_pr, context, app_id)
    if gate_errors:
        return _response("block", "gate_enabler_unverified", gate_errors[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=gate_errors)

    protection, identity, rules, read_errors = _required_set_readback(
        target, repository, branch, context, app_id, legacy_contexts, retained_contexts
    )
    if read_errors or protection is None or identity is None:
        return _response("block", "host_readback_unavailable", (read_errors or ["required-set readback is incomplete"])[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=read_errors)
    branch_state = _branch_checks(protection)
    if branch_state is None:
        return _response("block", "required_set_unreadable", "branch protection required checks are unreadable", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes)
    strict, checks = branch_state
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

    endpoint = f"github:{repository}:branch:{branch}:required_status_checks"
    if add_required:
        _payload, errors = _update_branch_checks(target, repository, branch, strict=strict, checks=[*checks, expected])
        if errors:
            return _response("block", "host_write_failed", errors[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=errors)
        writes.append({"locator": endpoint, "action": "add", "context": context})
        protection, identity, _rules, errors = _required_set_readback(target, repository, branch, context, app_id, legacy_contexts, retained_contexts)
        if errors or identity is None or not any(item.get("context") == context and item.get("app_id") == app_id for item in identity.get("identity", {}).get("effective_required_checks", [])):
            return _response("partial_apply", "partial_apply", "delivery gate was written but host readback did not confirm its identity", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=errors)
        branch_state = _branch_checks(protection or {})
        if branch_state is None:
            return _response("partial_apply", "partial_apply", "delivery gate was written but branch protection readback is incomplete", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes)
        strict, checks = branch_state

    if remove_legacy:
        desired = [item for item in checks if item["context"] not in legacy_contexts]
        _payload, errors = _update_branch_checks(target, repository, branch, strict=strict, checks=desired)
        if errors:
            return _response("partial_apply" if writes else "block", "partial_apply" if writes else "host_write_failed", errors[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=errors)
        writes.append({"locator": endpoint, "action": "remove", "contexts": sorted(legacy_contexts)})

    _protection, identity, _rules, errors = _required_set_readback(target, repository, branch, context, app_id, legacy_contexts, retained_contexts)
    if errors or identity is None or identity.get("result") != "ready":
        summary = errors[0] if errors else str(identity.get("primary_cause", {}).get("summary", "required-set readback is not ready"))
        return _response("partial_apply" if writes else "block", "partial_apply" if writes else "required_set_not_ready", summary, operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, required_set=identity, missing_inputs=errors)

    if not migration_pull.get("merged_at"):
        return _response("partial_apply" if writes else "block", "partial_apply" if writes else "profile_migration_pending", f"profile migration PR #{migration_pr} must merge before main-tree readback", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, required_set=identity)
    readback, errors = _main_tree_readback(target, repository, branch)
    if errors:
        return _response("partial_apply" if writes else "block", "partial_apply" if writes else "main_tree_unreconciled", errors[0], operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=recovery, writes=writes, missing_inputs=errors, main_tree=readback, required_set=identity)
    return _response("pass", "reconciled", "light profile migration is host-readback complete", operation=operation, repository=repository, branch=branch, work_item=work_item, next_action=None, writes=writes, main_tree=readback, required_set=identity, old_branch_reintroduction_guard={"workflow": DELIVERY_WORKFLOW, "required_check": {"context": context, "app_id": app_id}, "forbidden_carrier_evaluator": "light_profile.plan_payload"})


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
            apply=args.apply,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
