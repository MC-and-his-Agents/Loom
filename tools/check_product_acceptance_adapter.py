#!/usr/bin/env python3
"""Focused contract checks for the read-only product acceptance adapter."""

from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "product_acceptance.py"
SOURCE_DIR = SOURCE.parent
WORKFLOW = ROOT / ".github" / "workflows" / "loom-product-acceptance.yml"
WRITER = ROOT / "tools" / "write_product_acceptance.py"
FIXTURES = ROOT / "tools" / "fixtures" / "product-acceptance"
GENERATED_COPIES = (
    ROOT / "skills" / "shared" / "scripts" / "product_acceptance.py",
    ROOT / "plugins" / "loom" / "skills" / "shared" / "scripts" / "product_acceptance.py",
    ROOT / ".loom" / "bin" / "product_acceptance.py",
)
NOW = datetime(2026, 7, 11, 0, 30, tzinfo=timezone.utc)


def load_adapter() -> Any:
    sys.path.insert(0, str(SOURCE_DIR))
    spec = importlib.util.spec_from_file_location("product_acceptance", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("product acceptance adapter is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def assert_result(result: dict[str, Any], *, outcome: str, verdict: str) -> None:
    if result.get("result") != outcome or result.get("product_acceptance", {}).get("verdict") != verdict:
        raise AssertionError(f"expected {outcome}/{verdict}, got {result}")
    envelope = result.get("failure_envelope")
    if (
        not isinstance(envelope, dict)
        or set(envelope) != {"schema_version", "primary_cause", "consequences", "suppressed_diagnostics", "secondary_causes"}
        or envelope.get("consequences") != []
        or envelope.get("suppressed_diagnostics") != []
        or envelope.get("secondary_causes") != []
    ):
        raise AssertionError("acceptance adapter must return exactly one primary cause")
    authority = result.get("authority_verdict", {}).get("verdict")
    if not isinstance(authority, dict) or authority.get("delivery_state") != "not_evaluated" or authority.get("reconciliation_state") != "not_evaluated":
        raise AssertionError("acceptance adapter must not infer delivery or reconciliation")
    if result.get("mutates") is not False or result.get("runtime_actions_executed") != []:
        raise AssertionError("acceptance adapter must remain non-mutating and non-executing")


def resolve(adapter: Any, record: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as bundle:
        bundle.writestr("acceptance.json", json.dumps(record))
    archive = output.getvalue()
    mapping = {
        "repos/MC-and-his-Agents/Loom": {"default_branch": "main"},
        "repos/MC-and-his-Agents/Loom/issues/225": {"number": 225},
        "repos/MC-and-his-Agents/Loom/actions/artifacts/7": {"id": 7, "name": adapter.ARTIFACT_NAME, "expired": False, "size_in_bytes": len(archive), "digest": "sha256:" + hashlib.sha256(archive).hexdigest(), "workflow_run": {"id": 9}, "created_at": "2026-07-11T00:01:00Z"},
        "repos/MC-and-his-Agents/Loom/actions/runs/9": {"id": 9, "status": "completed", "conclusion": "success", "head_sha": "a" * 40, "workflow_id": 11, "path": adapter.TRUSTED_WORKFLOW_PATH, "event": "workflow_dispatch", "head_branch": "main", "run_started_at": "2026-07-10T23:59:00Z", "updated_at": "2026-07-11T00:02:00Z", "repository": {"full_name": "MC-and-his-Agents/Loom"}, "triggering_actor": {"login": "maintainer", "id": 42}},
        "repos/MC-and-his-Agents/Loom/actions/workflows/11": {"id": 11, "path": adapter.TRUSTED_WORKFLOW_PATH, "state": "active"},
        "repos/MC-and-his-Agents/Loom/collaborators/maintainer/permission": {"permission": "write", "user": {"login": "maintainer", "id": 42}},
        "repos/MC-and-his-Agents/Loom/commits/" + "a" * 40: {"sha": "a" * 40},
    }
    mapping.update(overrides)

    def read_json(_root: Path, path: str):
        return (mapping[path], []) if path in mapping else (None, [f"unexpected path: {path}"])

    return adapter.resolve_acceptance(
        ROOT,
        "MC-and-his-Agents/Loom/issue/225",
        7,
        now=NOW,
        read_json=read_json,
        read_bytes=lambda _root, _path: (archive, []),
    )


def main() -> int:
    adapter = load_adapter()
    local = adapter.evaluate_acceptance(fixture("passed-live-readonly.json"), now=NOW)
    assert_result(local, outcome="block", verdict="blocked")
    if local["product_acceptance"]["trusted"] is not False:
        raise AssertionError("repo-authored acceptance JSON must not self-assert passed")
    passed = resolve(adapter, fixture("passed-live-readonly.json"))
    assert_result(passed, outcome="pass", verdict="passed")
    if passed["product_acceptance"]["trusted"] is not True or passed["product_acceptance"]["owns_lifecycle_closure"] is not False:
        raise AssertionError("resolved acceptance must be trusted without owning lifecycle closure")
    self_bound_record = fixture("passed-live-readonly.json")
    self_bound_record["evidence"][0]["artifact_refs"] = [adapter.SELF_ARTIFACT_REF]
    self_bound = resolve(adapter, self_bound_record)
    if self_bound["result"] != "pass" or self_bound["host_facts"]["artifact_locator"] != "MC-and-his-Agents/Loom/artifact/7":
        raise AssertionError("workflow-authored self artifact reference did not resolve to authenticated host facts")
    precision_boundary = fixture("passed-live-readonly.json")
    precision_boundary["evidence"][0]["observed_at"] = (
        datetime(2026, 7, 11, 0, 1, tzinfo=timezone.utc) + timedelta(microseconds=999999)
    ).isoformat().replace("+00:00", "Z")
    if resolve(adapter, precision_boundary)["result"] != "pass":
        raise AssertionError("GitHub second-precision artifact timestamps must tolerate same-second evidence microseconds")
    outside_precision = fixture("passed-live-readonly.json")
    outside_precision["evidence"][0]["observed_at"] = "2026-07-11T00:01:01.000001Z"
    outside_result = resolve(adapter, outside_precision)
    if outside_result["result"] != "block" or "outside the authenticated workflow run" not in outside_result["missing_inputs"][0]:
        raise AssertionError("host timestamp tolerance must remain bounded to one second")
    for name in ("fixture-insufficient.json", "blocked-write-boundary.json", "stale-live-readonly.json"):
        assert_result(resolve(adapter, fixture(name)), outcome="block", verdict="blocked")
    waived = fixture("waived.json")
    assert_result(adapter.evaluate_acceptance(waived, now=NOW), outcome="pass", verdict="waived")
    resolved_waiver = resolve(adapter, waived)
    assert_result(resolved_waiver, outcome="pass", verdict="waived")
    if resolved_waiver["product_acceptance"]["trusted"] is not True or not resolved_waiver.get("rationale"):
        raise AssertionError("host-resolved waiver must retain trusted provenance and rationale")
    if "delivery_gate" in SOURCE.read_text(encoding="utf-8"):
        raise AssertionError("product acceptance adapter must not depend on delivery gate")
    with tempfile.TemporaryDirectory(prefix="loom-acceptance-writer-") as raw_tmp:
        tmp = Path(raw_tmp)
        readback = tmp / "release-readback.json"
        output = tmp / "acceptance.json"
        writer_args = [
            sys.executable,
            str(WRITER),
            "--story", "MC-and-his-Agents/Loom/issue/2101",
            "--scenario", "v0.31-product-acceptance-2101",
            "--evidence-class", "live_readonly",
            "--provider-profile", "loom-v0.31-product-acceptance",
            "--repository", "MC-and-his-Agents/Loom",
            "--head-sha", "a" * 40,
            "--run-id", "9",
            "--verifier-login", "maintainer",
            "--verifier-id", "42",
            "--release-readback", str(readback),
            "--output", str(output),
        ]
        readback.write_text(json.dumps({"result": "pass", "classification": {"verdict": "missing", "gaps": ["tag"]}}), encoding="utf-8")
        rejected = subprocess.run(writer_args, check=False, capture_output=True, text=True)
        if rejected.returncode == 0 or output.exists():
            raise AssertionError("acceptance writer trusted an incomplete release readback")
        readback.write_text(json.dumps({"result": "pass", "classification": {"verdict": "published", "gaps": []}}), encoding="utf-8")
        accepted = subprocess.run(writer_args, check=False, capture_output=True, text=True)
        if accepted.returncode != 0 or json.loads(output.read_text(encoding="utf-8"))["evidence"][0]["evidence_class"] != "live_readonly":
            raise AssertionError("acceptance writer rejected a gap-free published release readback")
        process_output = tmp / "process-runtime.json"
        process_args = [
            sys.executable,
            str(WRITER),
            "--story", "MC-and-his-Agents/Loom/issue/2114",
            "--scenario", "v0.32-product-acceptance-2114",
            "--evidence-class", "process_runtime",
            "--provider-profile", "loom-v0.32-product-acceptance",
            "--repository", "MC-and-his-Agents/Loom",
            "--head-sha", "a" * 40,
            "--run-id", "10",
            "--verifier-login", "maintainer",
            "--verifier-id", "42",
            "--output", str(process_output),
        ]
        process_written = subprocess.run(process_args, check=False, capture_output=True, text=True)
        process_record = json.loads(process_output.read_text(encoding="utf-8")) if process_output.exists() else {}
        process_boundary = process_record.get("evidence", [{}])[0].get("operation_boundary", {})
        process_errors = adapter.evidence_errors(
            process_record.get("evidence", [{}])[0],
            minimum_class="process_runtime",
            now=datetime.now(timezone.utc),
        )
        if process_written.returncode != 0 or "launch" not in process_boundary.get("allowed_actions", []) or "launch" not in process_boundary.get("observed_actions", []) or process_errors:
            raise AssertionError("process_runtime writer evidence must prove a launched candidate runtime")
    tracked_copies = [str(path.relative_to(ROOT)) for path in GENERATED_COPIES if path.exists()]
    if tracked_copies:
        raise AssertionError("product acceptance must remain canonical-source only: " + ", ".join(tracked_copies))
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for required in (
        "workflow_dispatch:",
        "release_issue:",
        "ref: ${{ github.sha }}",
        "product acceptance must run from the default branch",
        "product acceptance must bind the current default-branch tip",
        "loom-product-acceptance-${{ github.sha }}",
        "fetch-depth: 0",
        "tools/write_product_acceptance.py",
        "name: loom-product-acceptance",
        "VERSION=$(tr -d '\\n' < VERSION)",
        '"${VERSION}-umbrella-release-acceptance"',
        '"loom-${VERSION}-umbrella"',
        "listWorkflowRuns",
        'workflow_id: "loom-check.yml"',
        "exactHeadRuns",
        "right.run_number - left.run_number",
        "latest current-head main-push loom-check aggregate",
        "tools/check_light_profile.py",
        "tools/check_release_admission.py",
        "--surface installed-global-cli-smoke",
        "--provider-profile",
        "EVIDENCE_CLASS: process_runtime",
        "actions/upload-artifact@v4",
        "id: acceptance_upload",
        "steps.acceptance_upload.outputs.artifact-id",
        "issues: write",
        "loom:product-acceptance-artifact",
        "already has current-head umbrella acceptance artifact",
        'run.path === ".github/workflows/loom-product-acceptance.yml"',
        'run.event === "workflow_dispatch"',
        "entry.stateReason !== \"COMPLETED\"",
        "milestone readback must contain the release Work Item exactly once",
        "existing acceptance locator readback failed",
        "github-actions[bot]",
        "getArtifact",
        "getComment",
        "loom:codex-e2e-attestation",
        "getCollaboratorPermissionLevel",
        'new Set(["admin", "maintain", "write"])',
        "candidate_cli_authority",
        "canonical_plugin_payload_hash",
        "semantic_review_verdict",
        "retention-days: 30",
        "workflow success 不等于 lifecycle closure completed",
    ):
        if required not in workflow:
            raise AssertionError(f"trusted product acceptance workflow is missing {required}")
    forbidden = ("story_issue", "issue_number: 2116", "inputs.story_issue", "--source-surface source-self-fixture", "--source-surface root-self-adoption", "v0.32.1-umbrella")
    if any(value in workflow for value in forbidden) or "pull_request:" in workflow or "secrets." in workflow or not WRITER.is_file():
        raise AssertionError("trusted product acceptance workflow must remain dispatch-only, credential-free, and writer-backed")
    print("product acceptance adapter checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
