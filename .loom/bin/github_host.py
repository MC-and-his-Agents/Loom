"""GitHub CLI and API transport used by Loom host-facing flows."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


LOOM_RUNTIME_ENV_KEYS = (
    "LOOM_SOURCE_REPO_ROOT",
    "LOOM_INSTALLED_SKILLS_ROOT",
    "LOOM_PACKAGE_SKILL_ID",
    "LOOM_RUNTIME_SCENE",
)
HOST_API_NEXT_ACTIONS = {
    "host_api_unreadable": (
        "rerun the same command as `CODEX_EXPORT_GH_TOKEN=1 <same loom command>` so the wrapper can bridge "
        "the local gh keyring token into GH_TOKEN for this process only; do not export GH_TOKEN/GITHUB_TOKEN globally."
    ),
    "permission": (
        "fix host permissions or rerun the same command as `CODEX_EXPORT_GH_TOKEN=1 <same loom command>` "
        "so the wrapper can bridge the local gh keyring token into GH_TOKEN for this process only."
    ),
}


def run_process(
    args: list[str],
    cwd: Path,
    *,
    timeout_seconds: float | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key in LOOM_RUNTIME_ENV_KEYS:
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_seconds,
        input=input_text,
    )


def host_api_env_token_present() -> bool:
    return bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))


def host_api_gh_logged_in(root: Path) -> bool:
    try:
        result = run_process(["gh", "auth", "status"], root, timeout_seconds=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def host_api_failure_classifier(messages: list[str]) -> str:
    text = " ".join(str(message) for message in messages).lower()
    if any(token in text for token in ("rate limit", "api rate limit exceeded", "secondary rate limit")):
        return "host_api_unreadable"
    if any(token in text for token in ("resource not accessible", "permission", "forbidden", "403")):
        return "permission"
    return "host_api_unreadable"


def host_api_diagnostic_message(subject: str, messages: list[str]) -> str:
    classifier = host_api_failure_classifier(messages)
    detail = "; ".join(str(message).strip() for message in messages if str(message).strip()) or "host API read failed"
    return f"{subject} failed (classifier={classifier}; next_action={HOST_API_NEXT_ACTIONS[classifier]}): {detail}"


def host_api_anonymous_fallback_blocked(root: Path, path: str, gh_errors: list[str]) -> list[str]:
    if host_api_env_token_present() or not host_api_gh_logged_in(root):
        return []
    return [
        host_api_diagnostic_message(
            f"gh api {path}",
            [
                *gh_errors,
                "refusing anonymous public REST fallback because local gh auth is available but GH_TOKEN/GITHUB_TOKEN is not present in this process",
            ],
        )
    ]


def gh_json(root: Path, args: list[str]) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        result = run_process(["gh", *args], root, timeout_seconds=20)
    except FileNotFoundError:
        return None, [host_api_diagnostic_message(f"gh {' '.join(args)}", ["gh command is unavailable in PATH"])]
    except subprocess.TimeoutExpired:
        return None, [host_api_diagnostic_message(f"gh {' '.join(args)}", [f"gh {' '.join(args)} timed out after 20s"])]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh command failed"
        if args and args[0] in {"api", "pr", "project"}:
            detail = host_api_diagnostic_message(f"gh {' '.join(args)}", [detail])
        return None, [detail]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON from gh {' '.join(args)}: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"gh {' '.join(args)} did not return a JSON object"]
    return payload, []


def gh_json_input(root: Path, args: list[str], request_payload: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Send a JSON request on stdin without exposing untrusted strings to gh -F."""
    command_label = f"gh {' '.join(args)}"
    try:
        result = run_process(
            ["gh", *args],
            root,
            timeout_seconds=20,
            input_text=json.dumps(request_payload, ensure_ascii=False),
        )
    except FileNotFoundError:
        return None, [host_api_diagnostic_message(command_label, ["gh command is unavailable in PATH"])]
    except subprocess.TimeoutExpired:
        return None, [host_api_diagnostic_message(command_label, [f"{command_label} timed out after 20s"])]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh command failed"
        return None, [host_api_diagnostic_message(command_label, [detail])]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON from {command_label}: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"{command_label} did not return a JSON object"]
    return payload, []


def gh_graphql_json(root: Path, query: str, variables: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Run a GraphQL request through JSON stdin for inputs that may be user-authored."""
    payload, errors = gh_json_input(
        root,
        ["api", "graphql", "--input", "-"],
        {"query": query, "variables": variables},
    )
    if errors or payload is None:
        return None, errors
    data = payload.get("data")
    if not isinstance(data, dict):
        return None, ["gh api graphql --input - is missing `data`"]
    return data, []


def gh_rest_write_json(root: Path, *, method: str, path: str, request_payload: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    return gh_json_input(root, ["api", "--method", method, path, "--input", "-"], request_payload)


def gh_rest_json(root: Path, path: str) -> tuple[dict[str, Any] | None, list[str]]:
    payload, errors = gh_json(root, ["api", path])
    if payload is not None or not errors:
        return payload, errors
    blocked_errors = host_api_anonymous_fallback_blocked(root, path, errors)
    if blocked_errors:
        return None, blocked_errors
    fallback_payload, fallback_errors = github_public_rest_json(path)
    if fallback_payload is not None:
        return fallback_payload, []
    return None, errors + [f"public REST fallback: {message}" for message in fallback_errors]


def gh_rest_list(root: Path, path: str) -> tuple[list[dict[str, Any]], list[str]]:
    raw_payload, errors = gh_json(root, ["api", path])
    if raw_payload is not None:
        return [], [f"gh api {path} returned an object where a list was expected"]
    try:
        result = run_process(["gh", "api", path], root, timeout_seconds=20)
    except FileNotFoundError:
        result = None
        detail = "gh command is unavailable in PATH"
    except subprocess.TimeoutExpired:
        result = None
        detail = f"gh api {path} timed out after 20s"
    else:
        detail = result.stderr.strip() or result.stdout.strip() or "gh api failed"
    if result is None:
        fallback_payload, fallback_errors = github_public_rest_list(path)
        if fallback_payload:
            return fallback_payload, []
        return [], [host_api_diagnostic_message(f"gh api {path}", [detail]), *[f"public REST fallback: {message}" for message in fallback_errors]]
    if result.returncode == 0:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            return [], [f"invalid JSON from gh api {path}: {exc.msg}"]
        if not isinstance(payload, list):
            return [], [f"gh api {path} did not return a list"]
        return [entry for entry in payload if isinstance(entry, dict)], []
    blocked_errors = host_api_anonymous_fallback_blocked(root, path, [detail])
    if blocked_errors:
        return [], blocked_errors
    fallback_payload, fallback_errors = github_public_rest_list(path)
    if fallback_payload:
        return fallback_payload, []
    return [], [host_api_diagnostic_message(f"gh api {path}", [detail]), *[f"public REST fallback: {message}" for message in fallback_errors]]


def github_public_rest_json(path: str) -> tuple[dict[str, Any] | None, list[str]]:
    url = f"https://api.github.com/{path.lstrip('/')}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "loom-governance-runtime"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            text = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        return None, [host_api_diagnostic_message(f"public REST {path}", [f"HTTP {exc.code} {exc.reason}: {detail or url}"])]
    except URLError as exc:
        return None, [host_api_diagnostic_message(f"public REST {path}", [f"REST request failed: {exc.reason}"])]
    except OSError as exc:
        return None, [host_api_diagnostic_message(f"public REST {path}", [f"REST request failed: {exc}"])]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON from public REST endpoint: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, ["public REST endpoint did not return a JSON object"]
    return payload, []


def github_public_rest_list(path: str) -> tuple[list[dict[str, Any]], list[str]]:
    url = f"https://api.github.com/{path.lstrip('/')}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "loom-governance-runtime"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            text = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        return [], [host_api_diagnostic_message(f"public REST {path}", [f"HTTP {exc.code} {exc.reason}: {detail or url}"])]
    except URLError as exc:
        return [], [host_api_diagnostic_message(f"public REST {path}", [f"REST request failed: {exc.reason}"])]
    except OSError as exc:
        return [], [host_api_diagnostic_message(f"public REST {path}", [f"REST request failed: {exc}"])]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], [f"invalid JSON from public REST endpoint: {exc.msg}"]
    if not isinstance(payload, list):
        return [], ["public REST endpoint did not return a list"]
    return [entry for entry in payload if isinstance(entry, dict)], []


def github_issue_state(value: Any) -> str:
    return str(value or "unknown").upper()


def github_pr_state(payload: dict[str, Any]) -> str:
    return "MERGED" if payload.get("merged_at") else str(payload.get("state") or "unknown").upper()


def normalize_rest_issue(payload: dict[str, Any]) -> dict[str, Any]:
    labels = payload.get("labels")
    return {
        "id": payload.get("node_id"),
        "databaseId": payload.get("id"),
        "number": payload.get("number"),
        "state": github_issue_state(payload.get("state")),
        "title": payload.get("title"),
        "body": payload.get("body"),
        "url": payload.get("html_url"),
        "closedAt": payload.get("closed_at"),
        "stateReason": payload.get("state_reason"),
        "labels": [str(label.get("name")) for label in labels if isinstance(label, dict) and isinstance(label.get("name"), str)] if isinstance(labels, list) else [],
    }


def normalize_rest_pr(payload: dict[str, Any]) -> dict[str, Any]:
    head = payload.get("head") if isinstance(payload.get("head"), dict) else {}
    base = payload.get("base") if isinstance(payload.get("base"), dict) else {}
    merge_commit_sha = payload.get("merge_commit_sha")
    return {
        "number": payload.get("number"),
        "state": github_pr_state(payload),
        "title": payload.get("title"),
        "body": payload.get("body"),
        "url": payload.get("html_url"),
        "isDraft": bool(payload.get("draft")),
        "mergedAt": payload.get("merged_at"),
        "mergeCommit": {"oid": merge_commit_sha} if isinstance(merge_commit_sha, str) and merge_commit_sha else None,
        "mergeStateStatus": str(payload.get("mergeable_state")).upper() if payload.get("mergeable_state") else None,
        "headRefName": head.get("ref"),
        "headRefOid": head.get("sha"),
        "baseRefName": base.get("ref"),
    }


def github_issue_payload(root: Path, owner: str, repo_name: str, issue_number: int) -> tuple[dict[str, Any] | None, list[str]]:
    payload, errors = gh_rest_json(root, f"repos/{owner}/{repo_name}/issues/{issue_number}")
    return (normalize_rest_issue(payload), []) if payload is not None and not errors else (None, errors)


def github_pr_payload(root: Path, owner: str, repo_name: str, pr_number: int) -> tuple[dict[str, Any] | None, list[str]]:
    payload, errors = gh_rest_json(root, f"repos/{owner}/{repo_name}/pulls/{pr_number}")
    return (normalize_rest_pr(payload), []) if payload is not None and not errors else (None, errors)


def github_branch_payload(root: Path, owner: str, repo_name: str, branch_name: str) -> tuple[dict[str, Any] | None, list[str]]:
    payload, errors = gh_rest_json(root, f"repos/{owner}/{repo_name}/branches/{quote(branch_name, safe='')}")
    if errors or payload is None:
        return None, errors
    commit = payload.get("commit") if isinstance(payload.get("commit"), dict) else {}
    return {
        "name": payload.get("name") or branch_name,
        "protected": bool(payload.get("protected")),
        "commit": {"sha": commit.get("sha")} if isinstance(commit.get("sha"), str) else None,
    }, []


def normalize_dependency_issue(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": payload.get("node_id") or payload.get("id"),
        "number": payload.get("number"),
        "state": github_issue_state(payload.get("state")),
        "title": payload.get("title"),
        "url": payload.get("html_url") or payload.get("url"),
    }


def github_native_dependency_capability(root: Path, owner: str, repo_name: str, issue_number: int) -> dict[str, Any]:
    query = """
    query($owner: String!, $repo: String!, $issue: Int!) {
      issueType: __type(name: "Issue") { fields { name } }
      mutationType: __schema { mutationType { fields { name } } }
      repository(owner: $owner, name: $repo) {
        issue(number: $issue) { id blockedBy(first: 1) { totalCount } blocking(first: 1) { totalCount } }
      }
    }
    """
    payload, errors = gh_graphql_json(root, query, {"owner": owner, "repo": repo_name, "issue": issue_number})
    if errors or payload is None:
        text = " ".join(errors).lower()
        status = "unsupported" if any(token in text for token in ("could not resolve to an issue", "field 'blockedby'", "field 'blocking'", "undefinedfield")) else "permission_denied" if any(token in text for token in ("permission", "forbidden", "resource not accessible", "403")) else "unreadable"
        return {"status": status, "read": False, "write": False, "fields": [], "mutations": [], "errors": errors}
    issue_type = payload.get("issueType") if isinstance(payload.get("issueType"), dict) else {}
    fields = [str(field.get("name")) for field in issue_type.get("fields", []) if isinstance(field, dict) and isinstance(field.get("name"), str)]
    schema = payload.get("mutationType") if isinstance(payload.get("mutationType"), dict) else {}
    mutation_type = schema.get("mutationType") if isinstance(schema.get("mutationType"), dict) else {}
    mutations = [str(field.get("name")) for field in mutation_type.get("fields", []) if isinstance(field, dict) and isinstance(field.get("name"), str)]
    read_supported = {"blockedBy", "blocking"}.issubset(set(fields))
    write_supported = {"addBlockedBy", "removeBlockedBy"}.issubset(set(mutations))
    issue = payload.get("repository", {}).get("issue") if isinstance(payload.get("repository"), dict) else None
    read_ok = read_supported and isinstance(issue, dict) and isinstance(issue.get("id"), str)
    return {
        "status": "read-write" if read_ok and write_supported else "read-only" if read_ok else "unsupported",
        "read": read_ok,
        "write": read_ok and write_supported,
        "fields": sorted(field for field in fields if field in {"blockedBy", "blocking", "issueDependenciesSummary"}),
        "mutations": sorted(mutation for mutation in mutations if mutation in {"addBlockedBy", "removeBlockedBy"}),
        "errors": [],
    }


def normalize_graphql_dependency_issue(payload: dict[str, Any]) -> dict[str, Any]:
    return {"id": payload.get("id"), "number": payload.get("number"), "state": github_issue_state(payload.get("state")), "title": payload.get("title"), "url": payload.get("url")}


def github_issue_dependencies_graphql(root: Path, owner: str, repo_name: str, issue_number: int) -> tuple[dict[str, Any] | None, list[str]]:
    query = """
    query($owner: String!, $repo: String!, $issue: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issue) {
          id
          blockedBy(first: 100) { pageInfo { hasNextPage } nodes { id number state title url } }
          blocking(first: 100) { pageInfo { hasNextPage } nodes { id number state title url } }
        }
      }
    }
    """
    payload, errors = gh_graphql_json(root, query, {"owner": owner, "repo": repo_name, "issue": issue_number})
    if errors or payload is None:
        return None, errors
    issue = payload.get("repository", {}).get("issue") if isinstance(payload.get("repository"), dict) else None
    if not isinstance(issue, dict):
        return None, [f"GitHub issue #{issue_number} dependency query returned no issue"]
    checks: list[dict[str, Any]] = []
    all_edges: list[dict[str, Any]] = []
    incomplete = False
    for direction, field in (("blocked_by", "blockedBy"), ("blocking", "blocking")):
        connection = issue.get(field) if isinstance(issue.get(field), dict) else {}
        nodes = connection.get("nodes") if isinstance(connection.get("nodes"), list) else []
        source_locator = f"graphql:repository.issue.{field}"
        page_info = connection.get("pageInfo") if isinstance(connection.get("pageInfo"), dict) else None
        pagination_errors = [f"{field} exceeds the supported read page"] if isinstance(page_info, dict) and page_info.get("hasNextPage") is True else []
        incomplete = incomplete or bool(pagination_errors)
        checks.append({"direction": direction, "endpoint": source_locator, "status": "unreadable" if pagination_errors else "present", "errors": pagination_errors, "provenance": {"source_layer": "host_control_mirror", "source_owner": "github", "source_locator": source_locator, "freshness": "unreadable" if pagination_errors else "fresh"}})
        for node in nodes:
            if not isinstance(node, dict):
                continue
            normalized = normalize_graphql_dependency_issue(node)
            number = normalized.get("number")
            if not isinstance(number, int):
                continue
            all_edges.append({"source_issue": issue_number if direction == "blocked_by" else number, "blocking_issue": number if direction == "blocked_by" else issue_number, "direction": direction, "blocker_state": str(normalized.get("state") or "UNKNOWN").lower(), "source_of_truth": "github_native_edge", "host_mirror_status": "matched", "native": "present", "issue": normalized, "provenance": checks[-1]["provenance"]})
    return {"availability": "unreadable" if incomplete else "present", "complete": not incomplete, "checks": checks, "native_edges": all_edges}, []


def github_issue_dependencies_payload(root: Path, owner: str, repo_name: str, issue_number: int) -> dict[str, Any]:
    capability = github_native_dependency_capability(root, owner, repo_name, issue_number)
    if capability.get("read") is True:
        graphql_payload, graphql_errors = github_issue_dependencies_graphql(root, owner, repo_name, issue_number)
        if graphql_payload is not None:
            graphql_payload["capability"] = capability
            return graphql_payload
        capability = {**capability, "status": "unreadable", "errors": graphql_errors}
    if capability.get("status") in {"unsupported", "permission_denied"}:
        return {"availability": capability.get("status"), "capability": capability, "checks": [{"direction": "all", "endpoint": "graphql:repository.issue.blockedBy/blocking", "status": "unreadable", "errors": capability.get("errors", []), "provenance": {"source_layer": "host_control_mirror", "source_owner": "github", "source_locator": "graphql:repository.issue.blockedBy/blocking", "freshness": "unreadable"}}], "native_edges": []}
    checks: list[dict[str, Any]] = []
    all_edges: list[dict[str, Any]] = []
    unsupported = False
    permission_denied = False
    for direction, endpoint in (("blocked_by", "blocked_by"), ("blocking", "blocking")):
        path = f"repos/{owner}/{repo_name}/issues/{issue_number}/dependencies/{endpoint}"
        issues, errors = gh_rest_list(root, path)
        status = "unreadable" if errors else "present"
        text = " ".join(errors).lower()
        unsupported = unsupported or any(token in text for token in ("404", "410", "not found", "gone"))
        permission_denied = permission_denied or any(token in text for token in ("403", "permission", "resource not accessible"))
        checks.append({"direction": direction, "endpoint": path, "status": status, "errors": errors, "provenance": {"source_layer": "host_control_mirror", "source_owner": "github", "source_locator": path, "freshness": "fresh" if status == "present" else "unreadable"}})
        for issue in issues:
            normalized = normalize_dependency_issue(issue)
            number = normalized.get("number")
            if isinstance(number, int):
                all_edges.append({"source_issue": issue_number if direction == "blocked_by" else number, "blocking_issue": number if direction == "blocked_by" else issue_number, "direction": direction, "blocker_state": str(normalized.get("state") or "UNKNOWN").lower(), "source_of_truth": "github_native_edge", "host_mirror_status": "matched", "native": "present", "issue": normalized, "provenance": checks[-1]["provenance"]})
    availability = "unsupported" if unsupported else "permission_denied" if permission_denied else "unreadable" if any(check["status"] == "unreadable" for check in checks) else "present"
    return {"availability": availability, "capability": capability, "checks": checks, "native_edges": all_edges}


def gh_json_list(root: Path, args: list[str], key: str) -> tuple[list[dict[str, Any]], list[str]]:
    payload, errors = gh_json(root, args)
    if errors or payload is None:
        return [], errors
    value = payload.get(key)
    if not isinstance(value, list):
        return [], [f"gh {' '.join(args)} is missing `{key}`"]
    return [entry for entry in value if isinstance(entry, dict)], []


def gh_graphql(root: Path, query: str, variables: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args.extend(["-F", f"{key}={value}"])
    payload, errors = gh_json(root, args)
    if errors or payload is None:
        return None, errors
    data = payload.get("data")
    return (data, []) if isinstance(data, dict) else (None, ["gh api graphql is missing `data`"])


def graphql_budget_guard(scope: str, errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "graphql_only": True,
        "budget_scope": scope,
        "status": "unavailable" if errors else "guarded",
        "errors": list(errors or []),
        "fallback_to": "manual-reconciliation" if errors else None,
        "recommended_action": (
            "Retry this GraphQL-only host read with explicit operator intent, or continue with REST-backed issue/PR evidence when ProjectV2/native sub-issue data is not required."
            if errors else "Use this GraphQL-only host read sparingly; high-frequency repo, issue, and PR reads must stay on REST."
        ),
    }
