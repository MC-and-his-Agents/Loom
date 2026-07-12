"""GitHub CLI and API transport used by Loom host-facing flows."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from authority_contract import parse_typed_locator, typed_locator


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
SHA256_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
HOST_ATTESTATION_WORKFLOW_PATH = ".github/workflows/host-attestation-evidence.yml"
HOST_ATTESTATION_ASSERTION_RE = re.compile(
    r"<!--\s*loom:host-attestation-artifact\s+pr:(\d+)\s+head:([0-9a-f]{40})\s+id:(\d+)\s*-->",
    re.IGNORECASE,
)


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


def gh_graphql_authenticated_json(root: Path, query: str, variables: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Run an authenticated GraphQL query without any public fallback."""
    if not host_api_env_token_present() and not host_api_gh_logged_in(root):
        return None, [host_api_diagnostic_message("authenticated GitHub GraphQL read", ["no GitHub CLI login or process-local GH_TOKEN/GITHUB_TOKEN is available"])]
    return gh_graphql_json(root, query, variables)


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


def gh_rest_authenticated_json(root: Path, path: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Read one GitHub REST object without the anonymous public-API fallback.

    Attestation and closeout facts are security decisions.  A repository that is
    public today must not silently turn an unavailable authenticated read into a
    weaker unauthenticated read tomorrow.
    """
    if not host_api_env_token_present() and not host_api_gh_logged_in(root):
        return None, [host_api_diagnostic_message(f"authenticated gh api {path}", ["no GitHub CLI login or process-local GH_TOKEN/GITHUB_TOKEN is available"])]
    payload, errors = gh_json(root, ["api", path])
    if payload is not None:
        return payload, []
    return None, [host_api_diagnostic_message(f"authenticated gh api {path}", errors)]


def gh_rest_authenticated_bytes(root: Path, path: str) -> tuple[bytes | None, list[str]]:
    """Read one authenticated binary REST response without a public fallback."""
    if not host_api_env_token_present() and not host_api_gh_logged_in(root):
        return None, [host_api_diagnostic_message(f"authenticated gh api {path}", ["no GitHub CLI login or process-local GH_TOKEN/GITHUB_TOKEN is available"])]
    env = os.environ.copy()
    for key in LOOM_RUNTIME_ENV_KEYS:
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            ["gh", "api", path],
            cwd=root,
            check=False,
            capture_output=True,
            text=False,
            env=env,
            timeout=30,
        )
    except FileNotFoundError:
        return None, [host_api_diagnostic_message(f"authenticated gh api {path}", ["gh command is unavailable in PATH"])]
    except subprocess.TimeoutExpired:
        return None, [host_api_diagnostic_message(f"authenticated gh api {path}", ["request timed out after 30s"])]
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip() or "gh api failed"
        return None, [host_api_diagnostic_message(f"authenticated gh api {path}", [detail])]
    return result.stdout, []


def gh_rest_authenticated_list(root: Path, path: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Read every REST list page through authenticated ``gh`` or fail closed."""
    if not host_api_env_token_present() and not host_api_gh_logged_in(root):
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", ["no GitHub CLI login or process-local GH_TOKEN/GITHUB_TOKEN is available"])]
    try:
        result = run_process(["gh", "api", "--paginate", "--slurp", path], root, timeout_seconds=30)
    except FileNotFoundError:
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", ["gh command is unavailable in PATH"])]
    except subprocess.TimeoutExpired:
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", ["request timed out after 30s"])]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh api failed"
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", [detail])]
    try:
        pages = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [], [f"invalid JSON from authenticated gh api {path}: {exc.msg}"]
    if not isinstance(pages, list) or not all(isinstance(page, list) for page in pages):
        return [], [f"authenticated gh api {path} did not return a paginated JSON list"]
    rows: list[dict[str, Any]] = []
    for page in pages:
        rows.extend(row for row in page if isinstance(row, dict))
    return rows, []


def gh_rest_authenticated_paginated_field(
    root: Path, path: str, field: str
) -> tuple[list[dict[str, Any]], list[str]]:
    """Read and flatten one list field from every authenticated REST page."""
    if not host_api_env_token_present() and not host_api_gh_logged_in(root):
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", ["no GitHub CLI login or process-local GH_TOKEN/GITHUB_TOKEN is available"])]
    try:
        result = run_process(["gh", "api", "--paginate", "--slurp", path], root, timeout_seconds=30)
    except FileNotFoundError:
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", ["gh command is unavailable in PATH"])]
    except subprocess.TimeoutExpired:
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", ["request timed out after 30s"])]
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh api failed"
        return [], [host_api_diagnostic_message(f"authenticated gh api {path}", [detail])]
    try:
        pages = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [], [f"invalid JSON from authenticated gh api {path}: {exc.msg}"]
    if not isinstance(pages, list) or not all(isinstance(page, dict) and isinstance(page.get(field), list) for page in pages):
        return [], [f"authenticated gh api {path} did not return paginated `{field}` lists"]
    rows: list[dict[str, Any]] = []
    for page in pages:
        rows.extend(row for row in page[field] if isinstance(row, dict))
    return rows, []


def github_semantic_tree_digest(tree: list[Any]) -> tuple[str | None, list[str]]:
    """Return a stable digest of Git blobs; reject an incomplete host tree."""
    rows: list[tuple[str, str, str]] = []
    for entry in tree:
        if not isinstance(entry, dict):
            return None, ["GitHub tree contains an unreadable entry"]
        if entry.get("type") != "blob":
            continue
        path, blob, mode = entry.get("path"), entry.get("sha"), entry.get("mode")
        if not all(isinstance(value, str) and value for value in (path, blob, mode)):
            return None, ["GitHub tree blob lacks path, SHA, or mode"]
        rows.append((path, blob, mode))
    if not rows:
        return None, ["GitHub tree contains no readable blobs"]
    canonical = "".join(f"{path}\0{blob}\0{mode}\n" for path, blob, mode in sorted(rows))
    return f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}", []


def _github_commit_tree_readback(
    root: Path,
    owner: str,
    repo_name: str,
    commit_sha: str,
    *,
    read_json: Any = gh_rest_authenticated_json,
) -> tuple[dict[str, Any] | None, list[str]]:
    commit, errors = read_json(root, f"repos/{owner}/{repo_name}/git/commits/{commit_sha}")
    if errors or not isinstance(commit, dict):
        return None, errors or ["GitHub commit read returned no object"]
    tree_info = commit.get("tree") if isinstance(commit.get("tree"), dict) else {}
    tree_sha = tree_info.get("sha")
    if not isinstance(tree_sha, str) or not tree_sha:
        return None, ["GitHub commit lacks a tree SHA"]
    tree_payload, tree_errors = read_json(root, f"repos/{owner}/{repo_name}/git/trees/{tree_sha}?recursive=1")
    if tree_errors or not isinstance(tree_payload, dict):
        return None, tree_errors or ["GitHub recursive tree read returned no object"]
    if tree_payload.get("truncated") is True:
        return None, ["GitHub recursive tree is truncated; refusing incomplete semantic-tree attestation"]
    tree_rows = tree_payload.get("tree")
    if not isinstance(tree_rows, list):
        return None, ["GitHub recursive tree is missing its entries"]
    digest, digest_errors = github_semantic_tree_digest(tree_rows)
    if digest_errors or digest is None:
        return None, digest_errors
    return {"commit_sha": commit_sha, "tree_sha": tree_sha, "semantic_digest": digest}, []


def _current_approved_review(reviews: list[dict[str, Any]], head_sha: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Use each reviewer's latest state and bind approval to the current PR head."""
    current, errors = _current_head_reviews(reviews, head_sha)
    if errors:
        return None, errors
    approved = [row for row in current if str(row.get("state") or "").upper() == "APPROVED"]
    if not approved:
        return None, ["no GitHub APPROVED review is bound to the current head"]
    approved.sort(key=lambda row: int(row.get("id") or 0), reverse=True)
    return approved[0], []


def _current_head_reviews(reviews: list[dict[str, Any]], head_sha: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Return every reviewer's latest current-head state and reject objections."""
    latest: dict[str, dict[str, Any]] = {}
    for row in reviews:
        reviewer = row.get("user") if isinstance(row.get("user"), dict) else {}
        key = str(reviewer.get("id") or reviewer.get("login") or row.get("id") or "")
        if not key:
            return None, ["GitHub review lacks a stable reviewer identity"]
        prior = latest.get(key)
        if prior is None or int(row.get("id") or 0) > int(prior.get("id") or 0):
            latest[key] = row
    current = [row for row in latest.values() if row.get("commit_id") == head_sha]
    if any(str(row.get("state") or "").upper() == "CHANGES_REQUESTED" for row in current):
        return [], ["a current-head GitHub review requests changes"]
    return current, []


def _host_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _has_write_access(collaborator: dict[str, Any]) -> bool:
    permissions = collaborator.get("permissions") if isinstance(collaborator.get("permissions"), dict) else {}
    return any(permissions.get(name) is True for name in ("admin", "maintain", "push")) or str(collaborator.get("role_name") or "").lower() in {"admin", "maintain", "write"}


def github_pr_attestation_readback(
    root: Path,
    owner: str,
    repo_name: str,
    pr_number: int,
    artifact_id: int,
    *,
    work_item: int | None = None,
    allow_merged: bool = False,
    review_policy: str = "approved",
    read_json: Any = gh_rest_authenticated_json,
    read_list: Any = gh_rest_authenticated_list,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Read all review-attestation facts from GitHub; no body/comment/carrier input."""
    pr, errors = read_json(root, f"repos/{owner}/{repo_name}/pulls/{pr_number}")
    if errors or not isinstance(pr, dict):
        return None, errors or ["GitHub PR read returned no object"]
    if (not allow_merged and (str(pr.get("state") or "").lower() != "open" or pr.get("draft") is True or pr.get("merged_at") is not None)):
        return None, ["GitHub PR must be open, non-draft, and unmerged for review attestation"]
    head = pr.get("head") if isinstance(pr.get("head"), dict) else {}
    base = pr.get("base") if isinstance(pr.get("base"), dict) else {}
    head_sha, base_ref = head.get("sha"), base.get("ref")
    if not isinstance(head_sha, str) or not head_sha or not isinstance(base_ref, str) or not base_ref:
        return None, ["GitHub PR lacks its head SHA or base branch"]
    repository, repository_errors = read_json(root, f"repos/{owner}/{repo_name}")
    if repository_errors or not isinstance(repository, dict):
        return None, repository_errors or ["GitHub repository read returned no object"]
    if repository.get("default_branch") != base_ref:
        return None, ["GitHub PR base branch is not the repository default branch for trusted workflow attestation"]
    if review_policy not in {"approved", "single_maintainer"}:
        return None, ["host attestation review policy is unsupported"]
    reviews, review_errors = read_list(root, f"repos/{owner}/{repo_name}/pulls/{pr_number}/reviews")
    if review_errors:
        return None, review_errors
    if review_policy == "approved":
        review, approval_errors = _current_approved_review(reviews, head_sha)
        if approval_errors or review is None:
            return None, approval_errors
    else:
        _current, objection_errors = _current_head_reviews(reviews, head_sha)
        if objection_errors:
            return None, objection_errors
        review = None
    tree, tree_errors = _github_commit_tree_readback(root, owner, repo_name, head_sha, read_json=read_json)
    if tree_errors or tree is None:
        return None, tree_errors
    artifact, artifact_errors = read_json(root, f"repos/{owner}/{repo_name}/actions/artifacts/{artifact_id}")
    if artifact_errors or not isinstance(artifact, dict):
        return None, artifact_errors or ["GitHub Actions artifact read returned no object"]
    digest = artifact.get("digest")
    run_info = artifact.get("workflow_run") if isinstance(artifact.get("workflow_run"), dict) else {}
    run_id = run_info.get("id")
    if artifact.get("expired") is not False or not isinstance(digest, str) or SHA256_DIGEST_RE.fullmatch(digest) is None or not isinstance(run_id, int) or isinstance(run_id, bool):
        return None, ["GitHub Actions artifact is expired or lacks a host digest/workflow run; re-run the trusted host-attestation workflow_dispatch for the exact PR/head and update the Work Item assertion"]
    run, run_errors = read_json(root, f"repos/{owner}/{repo_name}/actions/runs/{run_id}")
    if run_errors or not isinstance(run, dict):
        return None, run_errors or ["GitHub Actions workflow run read returned no object"]
    pull_requests = run.get("pull_requests")
    run_pr_numbers = {row.get("number") for row in pull_requests if isinstance(row, dict)} if isinstance(pull_requests, list) else set()
    run_event = run.get("event")
    pull_target_binding = run_event == "pull_request_target" and run.get("head_sha") == head_sha and pr_number in run_pr_numbers
    dispatch_binding = (
        review_policy == "single_maintainer"
        and run_event == "workflow_dispatch"
        and not run_pr_numbers
        and run.get("head_branch") == base_ref
    )
    if (
        not (pull_target_binding or dispatch_binding)
        or str(run.get("status") or "").lower() != "completed"
        or str(run.get("conclusion") or "").lower() != "success"
        or run.get("path") != HOST_ATTESTATION_WORKFLOW_PATH
    ):
        return None, ["GitHub Actions workflow run is not a completed trusted host-attestation run bound to this PR head"]
    policy_facts: dict[str, Any] = {"mode": "approved", "verified": True}
    if review_policy == "single_maintainer":
        author = pr.get("user") if isinstance(pr.get("user"), dict) else {}
        actor = run.get("triggering_actor") if isinstance(run.get("triggering_actor"), dict) else run.get("actor") if isinstance(run.get("actor"), dict) else {}
        collaborators, collaborator_errors = read_list(root, f"repos/{owner}/{repo_name}/collaborators?affiliation=all&per_page=100")
        if collaborator_errors:
            return None, collaborator_errors
        maintainers = [row for row in collaborators if _has_write_access(row)]
        author_identity = (author.get("id"), author.get("login"))
        actor_identity = (actor.get("id"), actor.get("login"))
        maintainer_identity = (maintainers[0].get("id"), maintainers[0].get("login")) if len(maintainers) == 1 else (None, None)
        artifact_created = _host_time(artifact.get("created_at"))
        run_started, run_updated = _host_time(run.get("run_started_at")), _host_time(run.get("updated_at"))
        if artifact.get("name") != f"loom-host-attestation-{pr_number}":
            return None, ["single-maintainer attestation artifact name does not bind the target PR"]
        if (
            len(maintainers) != 1
            or not isinstance(author_identity[0], int)
            or isinstance(author_identity[0], bool)
            or not isinstance(author_identity[1], str)
            or author_identity != actor_identity
            or author_identity != maintainer_identity
        ):
            return None, ["single-maintainer attestation requires the sole write maintainer to author and trigger the PR run"]
        if run_started is None or run_updated is None or artifact_created is None or run_started > artifact_created or artifact_created > run_updated + timedelta(minutes=5):
            return None, ["single-maintainer attestation lacks a fresh host-bound run and artifact time window"]
        if not isinstance(work_item, int) or isinstance(work_item, bool) or work_item <= 0:
            return None, ["single-maintainer attestation requires a typed Work Item host comment locator"]
        work_item_issue, issue_errors = read_json(root, f"repos/{owner}/{repo_name}/issues/{work_item}")
        if issue_errors or not isinstance(work_item_issue, dict):
            return None, issue_errors or ["GitHub Work Item read returned no object"]
        labels = work_item_issue.get("labels")
        type_labels = {
            str(row.get("name") or "").strip().lower().replace("_", "-")
            for row in labels
            if isinstance(row, dict)
        } & {"work-item", "fr", "phase"} if isinstance(labels, list) else set()
        if type_labels != {"work-item"}:
            return None, ["single-maintainer attestation assertion issue is not uniquely typed as a work-item"]
        comments, comment_errors = read_list(root, f"repos/{owner}/{repo_name}/issues/{work_item}/comments?per_page=100")
        if comment_errors:
            return None, comment_errors
        assertions: list[tuple[dict[str, Any], re.Match[str]]] = []
        for comment in comments:
            if not isinstance(comment, dict) or not isinstance(comment.get("body"), str):
                return None, ["single-maintainer attestation comment identity is unreadable"]
            for match in HOST_ATTESTATION_ASSERTION_RE.finditer(comment["body"]):
                if int(match.group(1)) == pr_number and match.group(2).lower() == head_sha.lower():
                    assertions.append((comment, match))
        if len(assertions) != 1:
            return None, ["exactly one explicit single-maintainer attestation comment must bind the PR and current head"]
        assertion, assertion_match = assertions[0]
        assertion_user = assertion.get("user") if isinstance(assertion.get("user"), dict) else {}
        assertion_identity = (assertion_user.get("id"), assertion_user.get("login"))
        assertion_created = _host_time(assertion.get("created_at"))
        if (
            int(assertion_match.group(3)) != artifact_id
            or assertion_identity != maintainer_identity
            or assertion.get("author_association") not in {"OWNER", "MEMBER", "COLLABORATOR"}
            or assertion_created is None
            or assertion_created < artifact_created
        ):
            return None, ["single-maintainer attestation comment is not a host-authenticated post-artifact assertion"]
        policy_facts = {
            "mode": "single_maintainer",
            "verified": True,
            "maintainer_count": 1,
            "maintainer": {"id": author_identity[0], "login": author_identity[1]},
            "run_started_at": run.get("run_started_at"),
            "run_updated_at": run.get("updated_at"),
            "artifact_created_at": artifact.get("created_at"),
            "assertion_verified": True,
            "assertion_created_at": assertion.get("created_at"),
            "assertion_comment_id": assertion.get("id"),
        }
    return {
        "source": "github",
        "read_complete": True,
        "pr": {"number": pr_number, "head_sha": head_sha, "base_ref": base_ref, "merged_at": pr.get("merged_at"), "merge_commit_sha": pr.get("merge_commit_sha")},
        "review": {"id": review.get("id"), "state": review.get("state"), "commit_id": review.get("commit_id")} if review is not None else {"id": None, "state": "SINGLE_MAINTAINER_ATTESTED", "commit_id": head_sha},
        "review_policy": policy_facts,
        "semantic_tree": tree,
        "artifact": {"id": artifact_id, "digest": digest, "run_id": run_id, "name": artifact.get("name")},
        "workflow_run": {"id": run_id, "event": run.get("event"), "status": run.get("status"), "conclusion": run.get("conclusion"), "head_sha": run.get("head_sha"), "workflow_id": run.get("workflow_id"), "path": run.get("path"), "binding": "pull_request_target" if pull_target_binding else "workflow_dispatch_reattest"},
    }, []


def github_work_item_closed_by_pr_readback(
    root: Path,
    owner: str,
    repo_name: str,
    pr_number: int,
    work_item: int,
    *,
    read_graphql: Any = gh_graphql_authenticated_json,
) -> list[str]:
    """Require the GitHub-native Work-Item-to-merged-PR closing relation, paginated."""
    query = """
    query($owner: String!, $repo: String!, $workItem: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $workItem) {
          closedByPullRequestsReferences(first: 100) {
            pageInfo { hasNextPage }
            nodes { number merged }
          }
        }
      }
    }
    """
    payload, errors = read_graphql(root, query, {"owner": owner, "repo": repo_name, "workItem": work_item})
    if errors or not isinstance(payload, dict):
        return errors or ["GitHub PR closing-reference read returned no object"]
    repository = payload.get("repository") if isinstance(payload.get("repository"), dict) else {}
    issue = repository.get("issue") if isinstance(repository.get("issue"), dict) else {}
    references = issue.get("closedByPullRequestsReferences") if isinstance(issue.get("closedByPullRequestsReferences"), dict) else {}
    page = references.get("pageInfo") if isinstance(references.get("pageInfo"), dict) else {}
    if page.get("hasNextPage") is True:
        return ["GitHub Work Item closing PR references are paginated beyond the trusted read limit"]
    nodes = references.get("nodes")
    if not isinstance(nodes, list):
        return ["GitHub Work Item closing PR references are unreadable"]
    if pr_number not in {node.get("number") for node in nodes if isinstance(node, dict) and node.get("merged") is True}:
        return ["GitHub Work Item is not natively closed by the merged PR"]
    return []


def github_pr_closeout_readback(
    root: Path,
    owner: str,
    repo_name: str,
    pr_number: int,
    work_item: int,
    artifact_id: int,
    *,
    review_policy: str = "approved",
    read_json: Any = gh_rest_authenticated_json,
    read_list: Any = gh_rest_authenticated_list,
    read_graphql: Any = gh_graphql_authenticated_json,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Read a post-merge closeout from host facts, including default-branch containment."""
    attestation, errors = github_pr_attestation_readback(
        root,
        owner,
        repo_name,
        pr_number,
        artifact_id,
        work_item=work_item,
        allow_merged=True,
        review_policy=review_policy,
        read_json=read_json,
        read_list=read_list,
    )
    if errors or attestation is None:
        return None, errors
    pr = attestation["pr"]
    merge_sha, base_ref = pr.get("merge_commit_sha"), pr.get("base_ref")
    if not isinstance(pr.get("merged_at"), str) or not isinstance(merge_sha, str) or not merge_sha:
        return None, ["GitHub PR is not merged or lacks its merge commit"]
    compare, compare_errors = read_json(root, f"repos/{owner}/{repo_name}/compare/{merge_sha}...{quote(base_ref, safe='')}")
    if compare_errors or not isinstance(compare, dict):
        return None, compare_errors or ["GitHub base-branch containment read returned no object"]
    if compare.get("status") not in {"ahead", "identical"}:
        return None, ["GitHub base branch does not contain the merge commit"]
    merge_tree, tree_errors = _github_commit_tree_readback(root, owner, repo_name, merge_sha, read_json=read_json)
    if tree_errors or merge_tree is None:
        return None, tree_errors
    issue, issue_errors = read_json(root, f"repos/{owner}/{repo_name}/issues/{work_item}")
    if issue_errors or not isinstance(issue, dict):
        return None, issue_errors or ["GitHub Work Item read returned no object"]
    if str(issue.get("state") or "").lower() != "closed" or str(issue.get("state_reason") or "").lower() != "completed":
        return None, ["typed Work Item is not closed as completed"]
    labels = issue.get("labels")
    label_names = {str(row.get("name") or "").strip().lower().replace("_", "-") for row in labels if isinstance(row, dict)} if isinstance(labels, list) else set()
    if "work-item" not in label_names:
        return None, ["GitHub issue is not typed as a work-item"]
    relation_errors = github_work_item_closed_by_pr_readback(root, owner, repo_name, pr_number, work_item, read_graphql=read_graphql)
    if relation_errors:
        return None, relation_errors
    return {**attestation, "closeout": {"work_item_locator": typed_locator(owner, repo_name, "work_item", work_item), "merge_commit_sha": merge_sha, "base_contains_merge": True, "merge_semantic_tree": merge_tree, "issue_state": issue.get("state"), "issue_state_reason": issue.get("state_reason"), "work_item_closed_by_pr": pr_number}}, []


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


def github_lifecycle_subject_readback(
    root: Path,
    owner: str,
    repo_name: str,
    *,
    issue_number: int | str | None = None,
    fr_number: int | str | None = None,
    pr_number: int | None = None,
    branch_name: str | None = None,
    intent: str = "build",
    target_owner: str | None = None,
    target_repo: str | None = None,
) -> dict[str, Any]:
    """Resolve and reconcile every supplied lifecycle authority from GitHub."""

    errors: list[str] = []
    if target_owner and target_repo and (owner.lower(), repo_name.lower()) != (target_owner.lower(), target_repo.lower()):
        errors.append(f"explicit repository `{owner}/{repo_name}` does not match target origin `{target_owner}/{target_repo}`")

    def explicit_number(value: int | str | None, expected_type: str) -> int | None:
        if isinstance(value, int) and value > 0:
            return value
        parsed = parse_typed_locator(value, allowed_types={expected_type, "issue"}, allow_legacy=False)
        if parsed is None:
            if value is not None:
                errors.append(f"invalid canonical {expected_type} locator")
            return None
        if (str(parsed["owner"]).lower(), str(parsed["repo"]).lower()) != (owner.lower(), repo_name.lower()):
            errors.append(f"foreign canonical locator `{value}` does not belong to `{owner}/{repo_name}`")
            return None
        return int(parsed["id"])

    issue = explicit_number(issue_number, "work_item")
    fr = explicit_number(fr_number, "fr")
    if issue is not None and fr is not None and issue != fr:
        errors.append(f"explicit --issue #{issue} and --fr #{fr} disagree")
    explicit_subject = issue if issue is not None else fr

    execution_intent = intent in {"branch", "build", "pr", "pre-review", "ship", "implementation"}
    branch_pr: int | None = None
    if branch_name and pr_number is None:
        pulls, branch_errors = gh_rest_authenticated_list(
            root,
            f"repos/{quote(owner, safe='')}/{quote(repo_name, safe='')}/pulls?state=all&head={quote(f'{owner}:{branch_name}', safe='')}&per_page=100",
        )
        errors.extend(branch_errors)
        candidates = [
            row for row in pulls
            if isinstance(row.get("number"), int)
            and (
                (execution_intent and str(row.get("state") or "").lower() == "open")
                or (intent == "closeout" and str(row.get("state") or "").lower() == "closed")
                or (not execution_intent and intent != "closeout")
            )
        ]
        if not branch_errors and len(candidates) != 1:
            errors.append(f"branch `{branch_name}` resolves to {len(candidates)} eligible pull requests; exactly one authenticated, paginated result is required")
        elif candidates:
            branch_pr = int(candidates[0]["number"])
    effective_pr = pr_number if pr_number is not None else branch_pr

    pr_subject: int | None = None
    pull_request: dict[str, Any] | None = None
    if effective_pr is not None:
        query = """
        query($owner: String!, $repo: String!, $pr: Int!) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              number state headRefName
              closingIssuesReferences(first: 100) {
                pageInfo { hasNextPage }
                nodes { number }
              }
            }
          }
        }
        """
        data, pr_errors = gh_graphql_authenticated_json(root, query, {"owner": owner, "repo": repo_name, "pr": effective_pr})
        errors.extend(pr_errors)
        repository = data.get("repository") if isinstance(data, dict) and isinstance(data.get("repository"), dict) else {}
        pull_request = repository.get("pullRequest") if isinstance(repository.get("pullRequest"), dict) else None
        if not pr_errors and pull_request is None:
            errors.append(f"pull request #{effective_pr} is unreadable")
        if pull_request is not None:
            pr_state = str(pull_request.get("state") or "").upper()
            if execution_intent and pr_state != "OPEN":
                errors.append(f"execution intent requires an open PR; PR #{effective_pr} is {pr_state or 'UNKNOWN'}")
            if intent == "closeout" and pr_state not in {"CLOSED", "MERGED"}:
                errors.append(f"closeout intent requires a merged or closed PR; PR #{effective_pr} is {pr_state or 'UNKNOWN'}")
            if branch_name and pull_request.get("headRefName") != branch_name:
                errors.append(f"pull request #{effective_pr} head does not match branch `{branch_name}`")
            connection = pull_request.get("closingIssuesReferences") if isinstance(pull_request.get("closingIssuesReferences"), dict) else {}
            page_info = connection.get("pageInfo") if isinstance(connection.get("pageInfo"), dict) else {}
            if page_info.get("hasNextPage") is not False:
                errors.append("closing issue pagination is unreadable or incomplete")
            issues = [node for node in connection.get("nodes", []) if isinstance(node, dict) and isinstance(node.get("number"), int)]
            if len(issues) != 1:
                errors.append(f"pull request #{effective_pr} has {len(issues)} native closing issues; exactly one primary Work Item is required")
            else:
                pr_subject = int(issues[0]["number"])

    if explicit_subject is not None and pr_subject is not None and explicit_subject != pr_subject:
        errors.append(f"explicit issue #{explicit_subject} and PR #{effective_pr} closing issue #{pr_subject} disagree")
    subject = explicit_subject if explicit_subject is not None else pr_subject
    if subject is None and not errors:
        errors.append("no explicit issue, PR, or branch context is available")
    if errors or subject is None:
        return {
            "result": "block",
            "issue_number": subject,
            "pr_number": effective_pr,
            "branch": branch_name,
            "source": "authority_reconciliation",
            "errors": list(dict.fromkeys(errors)),
        }
    sources = [name for name, value in (("explicit_issue", explicit_subject), ("pr_closing_issue", pr_subject), ("branch_pr", branch_pr)) if value is not None]
    return {
        "result": "pass",
        "issue_number": subject,
        "issue_locator": typed_locator(owner, repo_name, "issue", subject),
        "pr_number": effective_pr,
        "pr_locator": typed_locator(owner, repo_name, "pr", effective_pr) if effective_pr is not None else None,
        "pr_state": pull_request.get("state") if pull_request else None,
        "branch": pull_request.get("headRefName") if pull_request else branch_name,
        "source": "+".join(sources),
        "errors": [],
    }


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
