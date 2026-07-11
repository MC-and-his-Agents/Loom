"""Product acceptance validation and authenticated GitHub host readback.

Local records may be structurally validated, but only host-resolved evidence can
produce a trusted ``passed`` verdict.  This module never executes product
runtime actions and never owns issue/FR closure state.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import quote

from authority_contract import authority_verdict, parse_typed_locator
from failure_envelope import envelope as failure_envelope, primary_cause
from github_host import SHA256_DIGEST_RE, gh_rest_authenticated_bytes, gh_rest_authenticated_json


SCHEMA = "loom-product-acceptance/v1"
EVIDENCE_CLASS_ORDER = (
    "static",
    "contract_test",
    "fixture",
    "process_runtime",
    "live_readonly",
    "live_write_precheck",
    "external_visible_write",
)
EVIDENCE_CLASSES = frozenset(EVIDENCE_CLASS_ORDER)
VERDICTS = frozenset({"not_required", "pending", "passed", "failed", "blocked", "waived"})
SAFE_ACTIONS = frozenset({"launch", "provider_detect", "browser_open", "read", "capture", "external_visible_write"})
PROHIBITED_ACTIONS = frozenset({"login", "captcha_or_risk_bypass", "submit", "publish", "send", "external_visible_write"})
TRUSTED_PERMISSIONS = frozenset({"admin", "maintain", "write"})
ARTIFACT_NAME = "loom-product-acceptance"
ARTIFACT_RECORD = "acceptance.json"
TRUSTED_WORKFLOW_PATH = ".github/workflows/loom-product-acceptance.yml"
MAX_ARTIFACT_BYTES = 5 * 1024 * 1024
MAX_RECORD_BYTES = 1024 * 1024
MAX_EVIDENCE_ROWS = 20
MAX_COMPONENTS_PER_ROW = 20
MAX_UNIQUE_COMPONENTS = 50
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
COMPONENT_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?/[A-Za-z0-9_.-]+$")
CLASS_REQUIRED_ACTIONS = {
    "process_runtime": frozenset({"launch"}),
    "live_readonly": frozenset({"read"}),
    "live_write_precheck": frozenset({"provider_detect"}),
    "external_visible_write": frozenset({"external_visible_write"}),
}


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def valid_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(entry, str) and entry.strip() for entry in value)


def evidence_class_satisfies(actual: object, minimum: object) -> bool:
    """Return whether an evidence class is at least as strong as the minimum."""
    if actual not in EVIDENCE_CLASSES or minimum not in EVIDENCE_CLASSES:
        return False
    return EVIDENCE_CLASS_ORDER.index(str(actual)) >= EVIDENCE_CLASS_ORDER.index(str(minimum))


def evidence_errors(
    evidence: object,
    *,
    minimum_class: str,
    now: datetime,
    host_binding: dict[str, Any] | None = None,
) -> list[str]:
    if not isinstance(evidence, dict):
        return ["evidence must be an object"]
    errors: list[str] = []
    evidence_class = evidence.get("evidence_class")
    if evidence_class not in EVIDENCE_CLASSES:
        errors.append("evidence_class is unsupported")
    observed_at = parse_time(evidence.get("observed_at"))
    freshness = evidence.get("freshness_window_seconds")
    if observed_at is None:
        errors.append("observed_at must be RFC3339 with a timezone")
    if not isinstance(freshness, int) or isinstance(freshness, bool) or freshness <= 0:
        errors.append("freshness_window_seconds must be a positive integer")
    elif observed_at is not None and observed_at > now:
        errors.append("observed_at cannot be in the future")
    elif observed_at is not None and (now - observed_at).total_seconds() > freshness:
        errors.append("evidence is stale")
    if observed_at is not None and host_binding is not None:
        run_started_at = parse_time(host_binding.get("run_started_at"))
        artifact_created_at = parse_time(host_binding.get("artifact_created_at"))
        if run_started_at is None or artifact_created_at is None or observed_at < run_started_at or observed_at > artifact_created_at:
            errors.append("observed_at is outside the authenticated workflow run and artifact time window")
    run_id = evidence.get("run_id")
    if host_binding is None:
        if not isinstance(run_id, (str, int)) or isinstance(run_id, bool) or not str(run_id).strip():
            errors.append("run_id must be a non-empty string or positive integer")
    elif run_id != host_binding["run_id"]:
        errors.append("run_id does not match the host-readback workflow run")
    refs = evidence.get("artifact_refs")
    if not valid_string_list(refs):
        errors.append("artifact_refs must contain at least one reference")
    elif host_binding is not None and refs != [host_binding["artifact_locator"]]:
        errors.append("artifact_refs must contain only the authenticated host artifact locator")
    profile = evidence.get("provider_profile")
    if not isinstance(profile, dict) or not all(isinstance(profile.get(key), str) and profile[key].strip() for key in ("provider", "profile")) or profile.get("redacted") is not True:
        errors.append("provider_profile must be redacted and identify provider/profile")
    versions = evidence.get("component_versions")
    if not isinstance(versions, dict) or not versions or any(not isinstance(repo, str) or COMPONENT_RE.fullmatch(repo) is None or not isinstance(commit, str) or SHA_RE.fullmatch(commit) is None for repo, commit in versions.items()):
        errors.append("component_versions must bind every owner/repo component to a 40-character SHA")
    boundary = evidence.get("operation_boundary")
    if not isinstance(boundary, dict):
        errors.append("operation_boundary must be an object")
    else:
        allowed, prohibited, observed = (boundary.get(key) for key in ("allowed_actions", "prohibited_actions", "observed_actions"))
        if not all(isinstance(value, list) and all(isinstance(action, str) for action in value) for value in (allowed, prohibited, observed)):
            errors.append("operation_boundary actions must be string lists")
        else:
            required_actions = CLASS_REQUIRED_ACTIONS.get(str(evidence_class), frozenset())
            required_prohibited = frozenset({"captcha_or_risk_bypass"}) if minimum_class == "external_visible_write" else PROHIBITED_ACTIONS
            if not set(allowed).issubset(SAFE_ACTIONS) or not required_prohibited.issubset(set(prohibited)) or not set(observed).issubset(set(allowed)) or set(observed) & set(prohibited) or not required_actions.issubset(set(observed)):
                errors.append("operation_boundary permits unsafe actions or does not prove the declared evidence class")
    return errors


def _result(
    payload: dict[str, Any],
    errors: list[str],
    *,
    host_binding: dict[str, Any] | None,
    network_access: bool | None = None,
) -> dict[str, Any]:
    declared = payload.get("verdict")
    acceptance_verdict = "blocked" if errors else declared
    trusted = host_binding is not None and declared == "passed" and not errors
    cause = primary_cause(
        cause_id="product_acceptance_resolved" if trusted else "product_acceptance_record_valid" if not errors else "product_acceptance_untrusted",
        failure_domain="product_acceptance",
        code="resolved" if trusted else "accepted" if not errors else "untrusted_or_invalid",
        locator=str(payload.get("story_locator") or "product_acceptance:record"),
        summary="Authenticated GitHub host facts resolve product acceptance without owning lifecycle closure." if trusted else "Product acceptance record is structurally valid but does not assert a passed verdict." if not errors else errors[0],
        owner="github" if trusted else "repository" if not errors else "operator",
        retryable=bool(errors),
        cause_class="host_readback" if trusted else "record_validation",
        details={"diagnostics": errors},
        remediation_command="loom acceptance resolve --story <owner/repo/issue/id> --artifact-id <id> --json",
    )
    return {
        "schema_version": SCHEMA,
        "result": "pass" if not errors else "block",
        "declared_verdict": declared,
        "product_acceptance": {
            "verdict": acceptance_verdict,
            "owner": "product_acceptance_adapter",
            "trusted": trusted,
            "evidence_consumed": trusted,
            "owns_lifecycle_closure": False,
        },
        "authority_verdict": authority_verdict(product_acceptance=acceptance_verdict),
        "story_locator": payload.get("story_locator"),
        "scenario_id": payload.get("scenario_id"),
        "minimum_evidence_class": payload.get("minimum_evidence_class"),
        "host_facts": host_binding,
        "missing_inputs": errors,
        "failure_envelope": failure_envelope(cause),
        "mutates": False,
        "network_access": host_binding is not None if network_access is None else network_access,
        "runtime_actions_executed": [],
    }


def _evaluate_acceptance(
    record: object,
    *,
    now: datetime | None = None,
    host_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one record; a passed verdict requires authenticated host binding."""

    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    payload = record if isinstance(record, dict) else {}
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must be `{SCHEMA}`")
    story = parse_typed_locator(payload.get("story_locator"), allowed_types={"issue", "fr", "work_item"}, allow_legacy=host_binding is None)
    if story is None:
        errors.append("story_locator must be a typed issue, fr, or work_item locator")
    if not isinstance(payload.get("scenario_id"), str) or not payload["scenario_id"].strip():
        errors.append("scenario_id must be a non-empty string")
    declared = payload.get("verdict")
    if declared not in VERDICTS:
        errors.append("verdict is unsupported")
    minimum = payload.get("minimum_evidence_class")
    if minimum not in EVIDENCE_CLASSES:
        errors.append("minimum_evidence_class is unsupported")
    if declared in {"waived", "not_required"} and (not isinstance(payload.get("rationale"), str) or not payload["rationale"].strip()):
        errors.append("waived and not_required verdicts require a rationale")
    evidence = payload.get("evidence")
    if declared == "passed":
        if host_binding is None:
            errors.append("passed verdict requires authenticated GitHub host readback")
        if not isinstance(evidence, list) or not evidence:
            errors.append("passed verdict requires evidence")
        elif len(evidence) > MAX_EVIDENCE_ROWS:
            errors.append(f"passed verdict supports at most {MAX_EVIDENCE_ROWS} evidence rows")
        elif minimum in EVIDENCE_CLASSES:
            for index, item in enumerate(evidence):
                errors.extend(f"evidence[{index}]: {message}" for message in evidence_errors(item, minimum_class=minimum, now=current_time, host_binding=host_binding))
            if not any(isinstance(item, dict) and evidence_class_satisfies(item.get("evidence_class"), minimum) for item in evidence):
                errors.append(f"no evidence row satisfies minimum `{minimum}`")
            unique_components: set[tuple[str, str]] = set()
            for index, item in enumerate(evidence):
                versions = item.get("component_versions") if isinstance(item, dict) and isinstance(item.get("component_versions"), dict) else {}
                if len(versions) > MAX_COMPONENTS_PER_ROW:
                    errors.append(f"evidence[{index}] supports at most {MAX_COMPONENTS_PER_ROW} components")
                unique_components.update((str(component), str(commit)) for component, commit in versions.items())
            if len(unique_components) > MAX_UNIQUE_COMPONENTS:
                errors.append(f"acceptance record supports at most {MAX_UNIQUE_COMPONENTS} unique component versions")
        verifier = payload.get("verifier")
        if host_binding is not None and verifier != host_binding["verifier"]:
            errors.append("verifier does not match the authenticated workflow triggering actor")
    elif evidence is not None and not isinstance(evidence, list):
        errors.append("evidence must be a list when supplied")
    if host_binding is not None and payload.get("story_locator") != host_binding["story_locator"]:
        errors.append("story_locator does not match the host-readback issue")
    return _result(payload, errors, host_binding=host_binding)


def evaluate_acceptance(record: object, *, now: datetime | None = None) -> dict[str, Any]:
    """Structurally validate a local record without accepting host assertions."""
    return _evaluate_acceptance(record, now=now)


def _artifact_record(archive: bytes) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            files = [entry for entry in bundle.infolist() if not entry.is_dir()]
            if len(files) != 1 or files[0].filename != ARTIFACT_RECORD:
                return None, [f"GitHub Actions artifact must contain only `{ARTIFACT_RECORD}`"]
            entry = files[0]
            if entry.file_size > MAX_RECORD_BYTES or entry.flag_bits & 0x1:
                return None, ["acceptance record is oversized or encrypted"]
            raw = bundle.read(entry)
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        return None, [f"GitHub Actions artifact is not a readable ZIP: {exc}"]
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"acceptance record is not valid UTF-8 JSON: {exc}"]
    return (payload, []) if isinstance(payload, dict) else (None, ["acceptance record must be a JSON object"])


def resolve_acceptance(
    root: Path,
    story_locator: str,
    artifact_id: int,
    *,
    now: datetime | None = None,
    read_json: Any = gh_rest_authenticated_json,
    read_bytes: Any = gh_rest_authenticated_bytes,
) -> dict[str, Any]:
    """Resolve a product acceptance verdict exclusively from authenticated GitHub facts."""

    parsed = parse_typed_locator(story_locator, allowed_types={"issue", "fr", "work_item"}, allow_legacy=False)
    if parsed is None or not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id <= 0:
        return _result({"story_locator": story_locator}, ["canonical story locator and positive artifact_id are required"], host_binding=None)
    owner, repo, number = parsed["owner"], parsed["repo"], parsed["id"]
    errors: list[str] = []
    repository, repository_errors = read_json(root, f"repos/{owner}/{repo}")
    if repository_errors or not isinstance(repository, dict) or not isinstance(repository.get("default_branch"), str):
        errors.extend(repository_errors or ["acceptance repository default branch is unreadable"])
        repository = {}
    issue, issue_errors = read_json(root, f"repos/{owner}/{repo}/issues/{number}")
    if issue_errors or not isinstance(issue, dict) or issue.get("number") != number or "pull_request" in issue:
        errors.extend(issue_errors or ["story locator is not a readable GitHub issue"])
    elif parsed["type"] in {"fr", "work_item"}:
        labels = issue.get("labels") if isinstance(issue.get("labels"), list) else []
        label_names = {str(label.get("name") or "").strip().lower().replace("_", "-") for label in labels if isinstance(label, dict)}
        expected_label = "fr" if parsed["type"] == "fr" else "work-item"
        if expected_label not in label_names:
            errors.append(f"story locator type `{parsed['type']}` is not confirmed by GitHub issue labels")
    artifact, artifact_errors = read_json(root, f"repos/{owner}/{repo}/actions/artifacts/{artifact_id}")
    if artifact_errors or not isinstance(artifact, dict):
        errors.extend(artifact_errors or ["GitHub Actions artifact is unreadable"])
        artifact = {}
    digest = artifact.get("digest")
    run_info = artifact.get("workflow_run") if isinstance(artifact.get("workflow_run"), dict) else {}
    run_id = run_info.get("id")
    size = artifact.get("size_in_bytes")
    artifact_created_at = parse_time(artifact.get("created_at"))
    if artifact.get("id") != artifact_id or artifact.get("name") != ARTIFACT_NAME or artifact.get("expired") is True:
        errors.append(f"GitHub Actions artifact must be active and named `{ARTIFACT_NAME}`")
    if not isinstance(digest, str) or SHA256_DIGEST_RE.fullmatch(digest) is None or not isinstance(run_id, int) or run_id <= 0:
        errors.append("GitHub Actions artifact lacks a host digest or workflow run")
    if not isinstance(size, int) or size <= 0 or size > MAX_ARTIFACT_BYTES or artifact_created_at is None:
        errors.append("GitHub Actions artifact size is missing or exceeds the resolver limit")
    run, run_errors = read_json(root, f"repos/{owner}/{repo}/actions/runs/{run_id}") if isinstance(run_id, int) else (None, [])
    if run_errors or not isinstance(run, dict):
        errors.extend(run_errors or ["GitHub Actions workflow run is unreadable"])
        run = {}
    run_repository = run.get("repository") if isinstance(run.get("repository"), dict) else {}
    verifier = run.get("triggering_actor") if isinstance(run.get("triggering_actor"), dict) else run.get("actor") if isinstance(run.get("actor"), dict) else {}
    verifier_login, verifier_id = verifier.get("login"), verifier.get("id")
    workflow_id, workflow_path, head_sha = run.get("workflow_id"), run.get("path"), run.get("head_sha")
    run_started_at, run_updated_at = parse_time(run.get("run_started_at")), parse_time(run.get("updated_at"))
    if run.get("id") != run_id or run_repository.get("full_name") != f"{owner}/{repo}" or run.get("status") != "completed" or run.get("conclusion") != "success":
        errors.append("workflow run is not a completed successful run for the acceptance repository")
    if (
        not isinstance(head_sha, str)
        or SHA_RE.fullmatch(head_sha) is None
        or not isinstance(workflow_id, int)
        or workflow_path != TRUSTED_WORKFLOW_PATH
        or run.get("event") != "workflow_dispatch"
        or run.get("head_branch") != repository.get("default_branch")
    ):
        errors.append("workflow run is not the trusted default-branch product acceptance producer")
    if run_started_at is None or run_updated_at is None or artifact_created_at is None or run_started_at > artifact_created_at or artifact_created_at > run_updated_at + timedelta(minutes=5):
        errors.append("workflow run and artifact host timestamps are missing or inconsistent")
    workflow, workflow_errors = read_json(root, f"repos/{owner}/{repo}/actions/workflows/{workflow_id}") if isinstance(workflow_id, int) else (None, [])
    if workflow_errors or not isinstance(workflow, dict) or workflow.get("id") != workflow_id or workflow.get("path") != workflow_path or workflow.get("state") != "active":
        errors.extend(workflow_errors or ["workflow identity is not an active host-readback workflow"])
    permission, permission_errors = read_json(root, f"repos/{owner}/{repo}/collaborators/{quote(str(verifier_login), safe='')}/permission") if isinstance(verifier_login, str) and verifier_login else (None, [])
    permission_user = permission.get("user") if isinstance(permission, dict) and isinstance(permission.get("user"), dict) else {}
    if permission_errors or not isinstance(permission, dict) or permission.get("permission") not in TRUSTED_PERMISSIONS or permission_user.get("id") != verifier_id or permission_user.get("login") != verifier_login:
        errors.extend(permission_errors or ["workflow verifier is not an authenticated write-level repository collaborator"])
    archive, archive_errors = read_bytes(root, f"repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip") if not errors else (None, [])
    if archive_errors or archive is None:
        errors.extend(archive_errors or (["GitHub Actions artifact bytes are unreadable"] if not errors else []))
    elif len(archive) > MAX_ARTIFACT_BYTES or f"sha256:{sha256(archive).hexdigest()}" != digest:
        errors.append("downloaded artifact does not match the host digest or size limit")
    record, record_errors = _artifact_record(archive) if archive is not None and not errors else (None, [])
    errors.extend(record_errors)
    artifact_locator = f"{owner}/{repo}/artifact/{artifact_id}"
    host_binding = {
        "source": "github",
        "read_complete": True,
        "story_locator": story_locator,
        "artifact_locator": artifact_locator,
        "artifact_id": artifact_id,
        "artifact_digest": digest,
        "run_id": run_id,
        "run_head_sha": head_sha,
        "run_started_at": run.get("run_started_at"),
        "run_updated_at": run.get("updated_at"),
        "artifact_created_at": artifact.get("created_at"),
        "workflow_id": workflow_id,
        "workflow_path": workflow_path,
        "verifier": {"login": verifier_login, "id": verifier_id},
        "verifier_permission": permission.get("permission") if isinstance(permission, dict) else None,
    }
    if isinstance(record, dict) and not errors:
        structural = _evaluate_acceptance(record, now=now, host_binding=host_binding)
        if structural["result"] != "pass":
            return structural
        evidence_rows = record.get("evidence") if isinstance(record.get("evidence"), list) else []
        components: set[tuple[str, str]] = set()
        for evidence in evidence_rows:
            component_versions = evidence.get("component_versions") if isinstance(evidence, dict) and isinstance(evidence.get("component_versions"), dict) else {}
            for component, commit in component_versions.items():
                if not isinstance(component, str) or COMPONENT_RE.fullmatch(component) is None or not isinstance(commit, str) or SHA_RE.fullmatch(commit) is None:
                    continue
                components.add((component, commit))
            if component_versions.get(f"{owner}/{repo}") != head_sha:
                errors.append("acceptance repository component version does not match the workflow head SHA")
        for component, commit in sorted(components):
            component_commit, component_errors = read_json(root, f"repos/{component}/commits/{commit}")
            if component_errors or not isinstance(component_commit, dict) or component_commit.get("sha") != commit:
                errors.extend(component_errors or [f"component version `{component}@{commit}` is not host-readable"])
    if errors or record is None:
        return _result(record or {"story_locator": story_locator}, errors or ["acceptance record is unreadable"], host_binding=None, network_access=True)
    return _evaluate_acceptance(record, now=now, host_binding=host_binding)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loom acceptance")
    parser.add_argument("action", choices=("validate", "resolve"))
    parser.add_argument("--input")
    parser.add_argument("--story")
    parser.add_argument("--artifact-id", type=int)
    parser.add_argument("--now")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    now = parse_time(args.now) if args.now else None
    if args.now and now is None:
        parser.error("--now must be RFC3339 with a timezone")
    if args.action == "resolve":
        if not args.story or args.artifact_id is None:
            parser.error("resolve requires --story and --artifact-id")
        result = resolve_acceptance(Path.cwd(), args.story, args.artifact_id, now=now)
    else:
        if not args.input:
            parser.error("validate requires --input")
        try:
            record = json.loads(Path(args.input).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result = _result({}, [f"acceptance input is unreadable: {exc}"], host_binding=None)
        else:
            result = evaluate_acceptance(record, now=now)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
