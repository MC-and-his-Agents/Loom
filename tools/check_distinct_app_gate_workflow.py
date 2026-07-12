#!/usr/bin/env python3
"""Static contract for the dormant distinct-App delivery-gate attestor."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "loom-delivery-gate-attestor.yml"
SOURCE_WORKFLOW = ROOT / ".github" / "workflows" / "loom-delivery-gate.yml"
CASES = ROOT / "tools" / "fixtures" / "delivery-gate" / "distinct-app-attestor-cases.json"


def evaluate_case(case: dict[str, object]) -> tuple[str, str | None]:
    run_head = case.get("run_head_sha")
    pulls = case.get("pull_head_shas")
    jobs = case.get("native_jobs")
    source_run_id = case.get("source_run_id")
    eligible_run_ids = case.get("eligible_run_ids")
    if not isinstance(run_head, str) or not re.fullmatch(r"[0-9a-f]{40}", run_head):
        return "blocked", None
    if (
        not isinstance(source_run_id, int)
        or case.get("event_run_attempt") != case.get("source_run_attempt")
        or case.get("source_run_attempt") != case.get("latest_run_attempt")
        or not isinstance(eligible_run_ids, list)
        or not eligible_run_ids
        or not isinstance(pulls, list)
        or not isinstance(jobs, list)
        or len(jobs) != 1
        or not isinstance(jobs[0], dict)
    ):
        return "blocked", None
    if case.get("event") == "pull_request_target":
        if len(pulls) != 1 or not isinstance(pulls[0], str) or not re.fullmatch(r"[0-9a-f]{40}", pulls[0]):
            return "blocked", None
        head = pulls[0]
    elif case.get("event") == "merge_group":
        head = run_head
    else:
        return "blocked", None
    if case.get("event_action", "completed") in {"requested", "in_progress"}:
        if any(isinstance(run_id, int) and run_id > source_run_id for run_id in eligible_run_ids):
            return "ignored", None
        if isinstance(case.get("newer_check_run_id"), int) and case["newer_check_run_id"] > source_run_id:
            return "ignored", None
        if case.get("existing_check_status") == "completed":
            return "terminal", head
        return "pending", head
    if case.get("source_workflow_sha") != case.get("trusted_workflow_sha"):
        return "blocked", None
    if source_run_id != max(eligible_run_ids):
        return "blocked", None
    job = jobs[0]
    if job.get("head_sha") != run_head:
        return "blocked", None
    return ("success" if job.get("status") == "completed" and job.get("conclusion") == "success" else "failure"), head


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "workflow_run:",
        "workflows: [loom-delivery-gate]",
        "types: [requested, in_progress, completed]",
        "cancel-in-progress: true",
        "if: ${{ vars.LOOM_DELIVERY_GATE_APP_ID != '' }}",
        "actions/create-github-app-token@fee1f7d63c2ff003460e3d139729b119787bc349",
        "actions/github-script@f28e40c7f34bde8b3046d885e986cb6290c5673b",
        "secrets.LOOM_DELIVERY_GATE_APP_PRIVATE_KEY",
        'workflow.path !== ".github/workflows/loom-delivery-gate.yml"',
        "sourceWorkflow.sha !== trustedWorkflow.sha",
        "sourceRun.run_attempt !== sourceRunAttempt",
        '["pull_request_target", "merge_group"]',
        'pulls.length !== 1',
        'name: "loom-delivery-gate-strong"',
        "head_sha: eventHeadSha",
        "const externalId = `loom-delivery-gate-strong:${sourceRunId}:${sourceRunAttempt}:${eventHeadSha}`",
        "listJobsForWorkflowRun",
        "listWorkflowRuns",
        "latestRun.id !== sourceRunId",
        "latestRun.run_attempt !== sourceRunAttempt",
        "finalLatestRun.id !== sourceRunId",
        'filter: "latest"',
        'status: "in_progress"',
        '["requested", "in_progress"].includes(sourceRunAction)',
        "latestPendingRun.id > sourceRunId",
        "check.app?.id === expectedAppId",
        "newerCheckExists",
        'pendingCheck?.status === "completed"',
        "Ignoring stale pending event for a superseded candidate run.",
        "checks.listForRef",
        "check.external_id === externalId",
        "check_run_id: pendingCheck.id",
        'conclusion: "failure"',
        'job.name === "isolated candidate native validation"',
        "nativeJobs.length !== 1",
        "nativeJobs[0].head_sha !== sourceRun.head_sha",
        'native.status === "completed" && native.conclusion === "success"',
        'product_acceptance: "not_evaluated"',
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("distinct-App attestor contract missing: " + ", ".join(missing))
    forbidden = (
        "pull_request:\n",
        "pull_request_target:\n",
        "github.token",
        "GITHUB_TOKEN",
        "continue-on-error: true",
        "NATIVE_RESULT_PATH",
        "download-artifact",
    )
    present = [item for item in forbidden if item in text]
    if present:
        raise AssertionError("distinct-App attestor contains spoofable/fail-open surface: " + ", ".join(present))
    source = SOURCE_WORKFLOW.read_text(encoding="utf-8")
    native = source[
        source.index("      - name: Run selected native validation with read-only token") :
        source.index("      - name: Upload isolated native validation artifact")
    ]
    if "continue-on-error" in native or 'exit "$EXIT_CODE"' not in native:
        raise AssertionError("source native-validation job must propagate failure to its GitHub job conclusion")
    catalog = json.loads(CASES.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != "loom-distinct-app-attestor-cases/v1":
        raise AssertionError("distinct-App attestor fixture schema drifted")
    for case in catalog.get("cases", []):
        verdict, head = evaluate_case(case)
        if verdict != case.get("expected") or head != case.get("expected_head_sha"):
            raise AssertionError(f"distinct-App attestor fixture drifted: {case.get('name')}: {verdict}/{head}")
    print("distinct App gate workflow contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
