#!/usr/bin/env python3
"""Daily execution CLI for Loom checkpoints, workspace lifecycle, and purity checks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None  # type: ignore[assignment]

sys.dont_write_bytecode = True

import closeout_flow as _closeout_flow
import delivery_control as _delivery_control
import execution_attempts as _execution_attempts
import execution_flow as _execution_flow
import flow_runtime as _flow_runtime
import github_host as _github_host
import host_profile as _host_profile
import live_smoke as _live_smoke
import review_flow as _review_flow
from live_smoke import handle_live_smoke
from execution_flow import (
    flow_governance_lint_status,
    goal_execution_contract,
    governance_lint_missing_inputs,
    handle_adopt,
    handle_carrier,
    handle_checkpoint,
    handle_fact_chain,
    handle_flow,
    handle_goal,
    handle_pr_metadata,
    handle_purity,
    handle_recovery,
    handle_repair,
    handle_runtime_evidence,
    handle_runtime_parity,
    handle_runtime_state,
    handle_shadow_parity,
    handle_state_check,
    handle_work_item,
    handle_work_item_audit,
    handle_workspace,
    report_execution_ledger,
    validate_goal_execution_contract,
)
from closeout_flow import (
    closeout_payload,
    handle_closeout,
    handle_closeout_queue,
    handle_reconciliation,
)
from review_flow import (
    fact_chain_error_contract,
    handle_review,
    implementation_review_status_payload,
    repo_specific_requirements_payload,
    report_blocking_failures,
    report_blocking_messages,
    report_provenance,
    report_recovery_readiness,
)
from host_profile import (
    handle_github_intake,
    handle_governance_profile,
    handle_host_binding,
    handle_host_lifecycle,
    project_drift_payload,
)
from delivery_control import (
    allowed_post_review_carrier_paths,
    checkpoint_payload,
    detect_github_repo,
    handle_controlled_merge,
    handle_gate_freeze,
    handle_gate_repair_pr,
    handle_pr_gate,
    load_context,
    load_fact_chain_report,
    review_head_binding,
    review_head_binding_for_head,
    spec_review_gate_payload,
)
from execution_attempts import (
    latest_execution_attempt_payload,
    latest_execution_failure_payload,
    latest_retry_evidence_payload,
)
from flow_runtime import emit, runtime_state_payload
from github_host import (
    HOST_API_NEXT_ACTIONS,
    github_issue_payload,
    github_pr_payload,
)


_COMPAT_MODULES = (
    _execution_flow,
    _closeout_flow,
    _review_flow,
    _host_profile,
    _live_smoke,
    _delivery_control,
    _execution_attempts,
    _flow_runtime,
    _github_host,
)


def __getattr__(name: str) -> Any:
    """Keep legacy Python imports working while implementations live in domains."""
    for module in _COMPAT_MODULES:
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")








TERMINAL_CLOSEOUT_STATES = {
    "not_applicable",
    "absorbed",
    "closed_out",
    "merged",
    "retired",
    "deferred",
}



CLOSEOUT_GATE_PROFILES = (
    "auto",
    "closeout-contract",
    "source-self-fixture",
    "bootstrap-regression",
    "distribution-regression",
    "strong-profile-full-gate",
)
CLOSEOUT_PR_ROLES = (
    "implementation_pr",
    "release_pr",
    "carrier_sync_pr",
    "final_closeout_pr",
)
GOVERNANCE_INTENSITY_VALUES = {"light", "standard", "reinforced"}
GOVERNANCE_CHANGE_CLASS_VALUES = {
    "docs_only",
    "docs_governance",
    "contract",
    "runtime",
    "fixture",
    "release",
    "workflow",
    "runtime_upgrade",
    "metadata_schema",
    "host_write",
    "permissions",
    "external_action",
    "mixed",
}
GOVERNANCE_SUITE_PATH_VALUES = {"full", "minimal", "not_applicable"}
GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT = "host_readback_only"
GOVERNANCE_REVIEW_REQUIREMENT_VALUES = {
    "current_head_review_required",
    "specialized_review_required",
    GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT,
}
GOVERNANCE_RELEASE_JUDGMENT_VALUES = {"release_required", "no_release", "deferred_release_judgment_blocking"}




REVIEW_DECISIONS = {"allow", "block", "fallback"}
REVIEW_KINDS = {"general_review", "code_review", "spec_review"}
DEFAULT_REVIEW_ADAPTER = "loom/default-codex-exec"
CODEX_APP_REVIEW_ADAPTER = "loom/codex-app-review"
CODEX_APP_REVIEW_SHADOW_ADAPTER = CODEX_APP_REVIEW_ADAPTER
AUTHORITATIVE_REVIEW_ADAPTERS = {DEFAULT_REVIEW_ADAPTER, CODEX_APP_REVIEW_ADAPTER}
SHADOW_REVIEW_ADAPTERS = {CODEX_APP_REVIEW_SHADOW_ADAPTER}
CODEX_APP_REVIEW_ENDPOINT_ENV = "LOOM_CODEX_APP_REVIEW_ENDPOINT"
CODEX_APP_REVIEW_THREAD_ID_ENV = "LOOM_CODEX_APP_REVIEW_THREAD_ID"
CODEX_APP_REVIEW_CWD_ENV = "LOOM_CODEX_APP_REVIEW_CWD"
CODEX_THREAD_ID_ENV = "CODEX_THREAD_ID"
REVIEW_ENGINE_PROFILE_IDS = {"default", "high-risk", "spec-review", "repeated-blocker"}
REVIEW_ENGINE_REASONING_EFFORTS = {"low", "medium", "high", "xhigh"}
GOVERNANCE_CAPABILITY_MODES = ("host-enforced", "advisory/local-enforced")
SHADOW_PARITY_SURFACES = ("admission", "review", "merge_ready", "closeout")






def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Loom daily execution checks against a target repository.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    checkpoint = subparsers.add_parser("checkpoint", help="Evaluate a Loom checkpoint against the fact chain")
    checkpoint.add_argument("stage", choices=("admission", "build", "merge"))
    checkpoint.add_argument("--target", required=True, help="Target repository root")
    checkpoint.add_argument("--item", help="Expected current item id")
    checkpoint.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    workspace = subparsers.add_parser("workspace", help="Manage Loom workspace lifecycle semantics")
    workspace.add_argument("operation", choices=("create", "locate", "attach", "cleanup", "retire"))
    workspace.add_argument("--target", required=True, help="Target repository root")
    workspace.add_argument("--item", help="Expected current item id")
    workspace.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    purity = subparsers.add_parser("purity-check", help="Evaluate Loom workspace purity from the fact chain")
    purity.add_argument("--target", required=True, help="Target repository root")
    purity.add_argument("--item", help="Expected current item id")
    purity.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    work_item_audit = subparsers.add_parser("work-item-audit", help="Audit active Work Item carrier drift before starting work")
    work_item_audit.add_argument("--target", required=True, help="Target repository root")
    work_item_audit.add_argument("--item", help="Expected current item id")
    work_item_audit.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    fact_chain = subparsers.add_parser("fact-chain", help="Read and validate the Loom fact chain")
    fact_chain.add_argument("--target", required=True, help="Target repository root")
    fact_chain.add_argument("--item", help="Expected current item id")
    fact_chain.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    runtime = subparsers.add_parser("runtime-evidence", help="Read runtime evidence from the Loom fact chain")
    runtime.add_argument("--target", required=True, help="Target repository root")
    runtime.add_argument("--item", help="Expected current item id")
    runtime.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    runtime_state = subparsers.add_parser("runtime-state", help="Read the Loom runtime scene/carrier state")
    runtime_state.add_argument("--target", required=True, help="Target repository root")
    runtime_state.add_argument("--item", help="Expected current item id")
    runtime_state.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    adopt = subparsers.add_parser("adopt", help="Validate Loom downstream adoption contracts")
    adopt.add_argument("operation", choices=("verify", "adversarial-test"))
    adopt.add_argument("--target", required=True, help="Target repository root")
    adopt.add_argument("--item", help="Expected current item id")
    adopt.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    adopt.add_argument("--record", action="store_true", help="Write adversarial adoption evidence under .loom/companion")

    carrier = subparsers.add_parser("carrier", help="Refresh Loom-owned carrier metadata")
    carrier.add_argument("operation", choices=("refresh", "closeout-sync"))
    carrier.add_argument("--target", required=True, help="Target repository root")
    carrier.add_argument("--item", help="Expected current item id")
    carrier.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    carrier.add_argument("--dry-run", action="store_true", default=True, help="Preview refresh actions without writing files; this is the default")
    carrier.add_argument("--write", dest="dry_run", action="store_false", help="Write Loom-owned carrier metadata refreshes")
    carrier.add_argument("--apply", dest="dry_run", action="store_false", help="Apply explicit versioned carrier closeout metadata writes")
    carrier.add_argument(
        "--surface",
        choices=("pre_review", "review", "merge_ready", "closeout"),
        default="merge_ready",
        help="Gate surface whose carrier refresh drift policy should be evaluated",
    )
    carrier.add_argument("--terminal-state", choices=tuple(sorted(TERMINAL_CLOSEOUT_STATES)), help="Terminal closeout state to write")
    carrier.add_argument("--issue", help="Issue locator or number bound to terminal closeout")
    carrier.add_argument("--pr", help="PR locator or number bound to terminal closeout")
    carrier.add_argument("--merge-commit", help="Merge commit SHA bound to terminal closeout")
    carrier.add_argument("--target-branch", help="Target branch containing the merge commit")
    carrier.add_argument("--closed-at", help="Closeout timestamp or not_applicable")
    carrier.add_argument("--evidence-locator", help="Repo or host locator for closeout evidence")

    repair = subparsers.add_parser("repair", help="Plan or apply safe repo-local carrier repairs")
    repair.add_argument("operation", choices=("plan", "apply"))
    repair.add_argument("--target", required=True, help="Target repository root")
    repair.add_argument("--item", help="Expected current item id")
    repair.add_argument("--issue", type=int, help="Expected GitHub issue number for retained-item disambiguation")
    repair.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    repair.add_argument("--dry-run", action="store_true", help="Preview repair apply without writing files")

    host_binding = subparsers.add_parser("host-binding", help="Validate or inspect host issue, PR, branch, SHA, Project, and dependency bindings")
    host_binding.add_argument("operation", choices=("validate", "inspect"))
    host_binding.add_argument("--target", required=True, help="Target repository root")
    host_binding.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    host_binding.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    host_binding.add_argument("--phase", type=int, help="GitHub Phase issue number")
    host_binding.add_argument("--fr", type=int, help="GitHub FR issue number")
    host_binding.add_argument("--issue", type=int, help="GitHub Work Item issue number")
    host_binding.add_argument("--pr", type=int, help="GitHub implementation PR number")
    host_binding.add_argument("--project", type=int, help="GitHub Project number")
    host_binding.add_argument("--branch", help="GitHub branch name")
    host_binding.add_argument("--head-sha", help="Implementation head SHA to validate")
    host_binding.add_argument("--base-sha", help="Base SHA used for diff validation")

    github_intake = subparsers.add_parser("github-intake", help="Read GitHub issue or Project entrypoints without writing host state")
    github_intake.add_argument("operation", choices=("issue", "admission"))
    github_intake.add_argument("--target", required=True, help="Target repository root")
    github_intake.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    github_intake.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    github_intake.add_argument("--issue", type=int, required=True, help="GitHub issue number to classify")
    github_intake.add_argument("--project", type=int, help="GitHub Project number for Project item/drift reads")
    github_intake.add_argument("--phase", type=int, help="Expected parent Phase issue number")
    github_intake.add_argument("--fr", type=int, help="Expected parent FR issue number")
    github_intake.add_argument("--pr", type=int, help="Known implementation PR number")
    github_intake.add_argument("--branch", help="Known implementation branch name")
    github_intake.add_argument("--head-sha", help="Known implementation head SHA")
    github_intake.add_argument(
        "--intent",
        choices=("planning", "branch", "build", "pr", "ship", "closeout", "completed"),
        default="planning",
        help="Requested lifecycle intent for FR-to-WI admission",
    )
    github_intake.add_argument("--task", help="Minimum Work Item proposal text for admission")
    github_intake.add_argument("--lifecycle-only", action="store_true", help=argparse.SUPPRESS)
    github_intake.add_argument("--blocked-by", type=int, action="append", default=[], help="Native blocking issue number for the proposed Work Item; may be repeated")
    github_intake.add_argument("--work-item", type=int, help="Existing Work Item number for a partial admission recovery")
    github_intake.add_argument("--apply", action="store_true", help="Apply host-native Work Item reconciliation after an explicit proposal")

    goal = subparsers.add_parser("goal", help="Derive or validate Loom /goal execution contracts")
    goal.add_argument("operation", choices=("derive", "validate"))
    goal.add_argument("--target", required=True, help="Target repository root")
    goal.add_argument("--item", help="Expected current item id")
    goal.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    goal.add_argument("--goal-file", help="Optional repo-relative goal execution contract JSON")
    goal.add_argument("--issue", type=int, help="Expected source issue number")
    goal.add_argument("--pr", type=int, help="Expected PR number")
    goal.add_argument("--branch", help="Expected branch name")
    goal.add_argument("--head-sha", help="Expected head SHA")

    pr_gate = subparsers.add_parser("pr-gate", help="Evaluate PR-specific semantic approval before host merge")
    pr_gate.add_argument("operation", choices=("check",))
    pr_gate.add_argument("--target", required=True, help="Target repository root")
    pr_gate.add_argument("--item", help="Expected Loom Work Item id; must match PR body when both are present")
    pr_gate.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    pr_gate.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    pr_gate.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    pr_gate.add_argument("--issue", type=int, help="Explicit GitHub Work Item issue authority")
    pr_gate.add_argument("--pr", type=int, help="GitHub implementation PR number")
    pr_gate.add_argument("--head-sha", help="Expected PR head SHA")
    pr_gate.add_argument("--branch", help="Optional PR branch/ref used to infer a PR number")
    pr_gate.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    pr_gate.add_argument("--body-file", help="Optional repo-relative hosted PR body readback artifact")
    pr_gate.add_argument("--compare-body-file", help="Optional repo-relative PR body artifact to compare with --body-file")
    pr_gate.add_argument("--gate-freeze-snapshot-file", help="Optional repo-relative loom-gate-freeze/v1 snapshot to compare with hosted recomputation")
    pr_gate.add_argument(
        "--surface",
        choices=("pre_review", "review", "merge_ready", "closeout"),
        default=None,
        help="PR metadata surface consumed by this gate; defaults to the PR body machine surface or merge_ready",
    )

    pr_metadata = subparsers.add_parser("pr-metadata", help="Render, update, read back, or validate repo-specific PR metadata machine carriers")
    pr_metadata.add_argument("operation", choices=("render", "update", "readback", "preflight"))
    pr_metadata.add_argument("--target", required=True, help="Target repository root")
    pr_metadata.add_argument(
        "--surface",
        choices=("pre_review", "review", "merge_ready", "closeout"),
        required=True,
        help="Gate surface that consumes the metadata preflight",
    )
    pr_metadata.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    pr_metadata.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    pr_metadata.add_argument("--item", help="Expected Loom Work Item id for render, update, or readback binding")
    pr_metadata.add_argument("--issue", type=int, help="Expected GitHub Work Item issue number for safe PR body backlink repair")
    pr_metadata.add_argument("--pr", type=int, help="GitHub implementation PR number")
    pr_metadata.add_argument("--head-sha", help="Expected PR head SHA")
    pr_metadata.add_argument("--branch", help="Optional PR branch/ref used to infer a PR number")
    pr_metadata.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    pr_metadata.add_argument("--output-file", default=".loom/runtime/pr/metadata-rendered.md", help="Repo-relative rendered PR body artifact output path")
    pr_metadata.add_argument("--readback-file", default=".loom/runtime/pr/metadata-readback.md", help="Repo-relative readback artifact output path when reading the current host PR body")
    pr_metadata.add_argument("--base-body-file", default=".github/PULL_REQUEST_TEMPLATE.md", help="Repo-relative PR body template or existing body artifact to update during render")
    pr_metadata.add_argument("--body-file", help="Optional repo-relative rendered PR body markdown to validate before gh pr edit")
    pr_metadata.add_argument("--compare-body-file", help="Optional repo-relative post-edit/readback PR body markdown to compare against --body-file")
    pr_metadata.add_argument("--governance-intensity", choices=tuple(sorted(GOVERNANCE_INTENSITY_VALUES)), default="standard")
    pr_metadata.add_argument("--change-class", choices=tuple(sorted(GOVERNANCE_CHANGE_CLASS_VALUES)), default="contract")
    pr_metadata.add_argument("--suite-path", choices=tuple(sorted(GOVERNANCE_SUITE_PATH_VALUES)), default="minimal")
    pr_metadata.add_argument("--review-requirement", choices=tuple(sorted(GOVERNANCE_REVIEW_REQUIREMENT_VALUES)), default="current_head_review_required")
    pr_metadata.add_argument("--release-judgment", choices=tuple(sorted(GOVERNANCE_RELEASE_JUDGMENT_VALUES)), default="no_release")
    pr_metadata.add_argument("--fact-chain-required", dest="fact_chain_required", action="store_true", default=True, help="Require repo-local Work Item fact-chain carriers; this is the default")
    pr_metadata.add_argument("--no-fact-chain-required", dest="fact_chain_required", action="store_false", help="Declare a host-readback-only PR metadata profile without repo-local fact-chain carriers")
    pr_metadata.add_argument("--upgrade-trigger", action="append", default=[], help="Repeatable governance upgrade trigger string")
    pr_metadata.add_argument("--covered-issue", type=int, action="append", default=[], help="Repeatable GitHub issue number covered by this PR batch")
    pr_metadata.add_argument("--excluded-scope", action="append", default=[], help="Repeatable excluded scope note for this PR batch")
    pr_metadata.add_argument("--suite-na-rationale")
    pr_metadata.add_argument("--suite-na-consumer-boundary")
    pr_metadata.add_argument("--suite-na-recheck-condition")
    pr_metadata.add_argument("--suite-na-scope-proof")
    pr_metadata.add_argument("--suite-na-review-requirement")
    pr_metadata.add_argument("--dry-run", action="store_true", default=True, help="Preview metadata update/rendered preflight without writing the host PR body; this is the default")
    pr_metadata.add_argument("--apply", dest="dry_run", action="store_false", help="Write the rendered body to the host PR, then read it back and rerun metadata preflight")

    gate_freeze = subparsers.add_parser("gate-freeze", help="Generate or validate hosted gate input freeze snapshots")
    gate_freeze.add_argument("operation", choices=("check", "write"))
    gate_freeze.add_argument("--target", required=True, help="Target repository root")
    gate_freeze.add_argument("--item", help="Expected Loom Work Item id")
    gate_freeze.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    gate_freeze.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    gate_freeze.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    gate_freeze.add_argument("--pr", type=int, help="GitHub implementation PR number")
    gate_freeze.add_argument("--head-sha", help="Expected PR head SHA")
    gate_freeze.add_argument("--branch", help="Optional PR branch/ref used to infer a PR number")
    gate_freeze.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    gate_freeze.add_argument("--issue", type=int, help="GitHub issue number for closeout profile terminal fact readback")
    gate_freeze.add_argument("--issue-payload-file", help="Optional repo-relative issue payload JSON fixture for closeout profile")
    gate_freeze.add_argument("--dependency-payload-file", help="Optional repo-relative native dependency payload JSON fixture for closeout profile")
    gate_freeze.add_argument("--body-file", help="Optional repo-relative rendered PR body markdown to validate before gh pr edit")
    gate_freeze.add_argument("--compare-body-file", help="Optional repo-relative post-edit/readback PR body markdown to compare against --body-file")
    gate_freeze.add_argument(
        "--surface",
        choices=("pre_review", "review", "merge_ready", "closeout"),
        default="merge_ready",
        help="Gate surface whose PR metadata contract is consumed by the snapshot",
    )
    gate_freeze.add_argument(
        "--profile",
        choices=("hosted", "closeout"),
        default="hosted",
        help="Freeze profile to emit; `closeout` emits loom-closeout-freeze/v1 terminal admission.",
    )
    gate_freeze.add_argument(
        "--closeout-mode",
        choices=("inline", "auto_no_op", "light", "batched", "full"),
        default="light",
        help="Closeout terminal profile mode used with --profile closeout.",
    )
    gate_freeze.add_argument("--target-branch", default="main", help="Target branch used for closeout merge commit containment readback")
    gate_freeze.add_argument("--write-path", help="Repo-relative snapshot output path; defaults to .loom/runtime/gate-freeze/<item>.json")

    controlled_merge = subparsers.add_parser("controlled-merge", help="Check or execute Loom-controlled PR merge")
    controlled_merge.add_argument("operation", choices=("check", "merge"))
    controlled_merge.add_argument("--target", required=True, help="Target repository root")
    controlled_merge.add_argument("--item", help="Expected Loom Work Item id")
    controlled_merge.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    controlled_merge.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    controlled_merge.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    controlled_merge.add_argument("--issue", type=int, help="Explicit GitHub Work Item issue authority")
    controlled_merge.add_argument("--pr", type=int, required=True, help="GitHub implementation PR number")
    controlled_merge.add_argument("--head-sha", help="Expected PR head SHA")
    controlled_merge.add_argument("--merge-method", choices=("squash", "merge", "rebase"), default="squash")
    controlled_merge.add_argument("--delete-branch", action="store_true", help="Delete branch after a successful host merge")
    controlled_merge.add_argument("--execute", action="store_true", help="Actually delegate to gh pr merge when all gates pass")
    controlled_merge.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    controlled_merge.add_argument("--status-checks-file", help="Optional repo-relative statusCheckRollup JSON fixture")
    controlled_merge.add_argument("--branch-protection-file", help="Optional repo-relative branch protection JSON fixture")
    controlled_merge.add_argument("--ruleset-file", help="Optional repo-relative branch rules/ruleset JSON fixture")
    controlled_merge.add_argument("--pr-gate-result-file", help="Optional repo-relative retained pr-gate result JSON")
    controlled_merge.add_argument("--merge-gate-result-file", help="Optional repo-relative retained merge-gate or merge-ready result JSON")
    controlled_merge.add_argument("--governance-mode", choices=GOVERNANCE_CAPABILITY_MODES, default="host-enforced")
    controlled_merge.add_argument("--allow-advisory-local-enforced", action="store_true")
    controlled_merge.add_argument("--allow-high-risk-advisory", action="store_true")
    controlled_merge.add_argument("--change-class", help="Optional change class used to block high-risk advisory fallback")

    gate_repair_pr = subparsers.add_parser("gate-repair-pr", help="Record audited repair PR gate evidence without mutating host rulesets")
    gate_repair_pr.add_argument("--target", required=True, help="Target repository root")
    gate_repair_pr.add_argument("--record", action="store_true", help="Write .loom/companion/gate-repair-pr.json after validation passes")
    gate_repair_pr.add_argument("--item", help="Expected Loom Work Item id")
    gate_repair_pr.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    gate_repair_pr.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    gate_repair_pr.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    gate_repair_pr.add_argument("--pr", type=int, help="GitHub implementation PR number")
    gate_repair_pr.add_argument("--head-sha", help="Expected PR head SHA")
    gate_repair_pr.add_argument("--branch", help="Expected repair PR branch")
    gate_repair_pr.add_argument("--reason", help="Audited reason for the repair PR evidence record")
    gate_repair_pr.add_argument("--enforcement-before-file", help="Repo-relative JSON readback proving the broken enforcement state before repair")
    gate_repair_pr.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    gate_repair_pr.add_argument("--status-checks-file", help="Optional repo-relative statusCheckRollup JSON fixture")
    gate_repair_pr.add_argument("--branch-protection-file", help="Optional repo-relative branch protection JSON fixture")
    gate_repair_pr.add_argument("--ruleset-file", help="Optional repo-relative branch rules/ruleset JSON fixture")
    gate_repair_pr.add_argument("--pr-gate-result-file", help="Optional repo-relative retained pr-gate result JSON")
    gate_repair_pr.add_argument("--merge-gate-result-file", help="Optional repo-relative retained merge-gate or merge-ready result JSON")

    state = subparsers.add_parser(
        "state-check",
        help="Check active-state consistency, checkpoint completeness, and scope overflow signals",
    )
    state.add_argument("--target", required=True, help="Target repository root")
    state.add_argument("--item", help="Expected current item id")
    state.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    review = subparsers.add_parser("review", help="Read, run, or record a Loom formal review artifact")
    review.add_argument("operation", choices=("read", "run", "record"))
    review.add_argument("--target", required=True, help="Target repository root")
    review.add_argument("--item", help="Expected current item id")
    review.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    review.add_argument("--review-file", help="Optional review artifact path relative to the target root")
    review.add_argument("--owner", help="GitHub owner for light-profile host attestation")
    review.add_argument("--repo", dest="repo_name", help="GitHub repository for light-profile host attestation")
    review.add_argument("--issue", type=int, help="GitHub Work Item issue for light-profile host attestation")
    review.add_argument("--pr", type=int, help="GitHub PR for light-profile host attestation")
    review.add_argument("--host-artifact-input", type=Path, help="JSON containing only the GitHub Actions artifact_id")
    review.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    review.add_argument("--decision", choices=tuple(sorted(REVIEW_DECISIONS)))
    review.add_argument("--kind", choices=tuple(sorted(REVIEW_KINDS)))
    review.add_argument("--summary", help="Stable review conclusion summary")
    review.add_argument("--reviewer", help="Reviewer identity")
    review.add_argument("--surface", choices=("review", "closeout"), default="review", help="Review record surface; closeout is restricted to terminal carrier-only review.")
    review.add_argument("--fallback-to", choices=("admission", "build", "merge"))
    review.add_argument("--findings-file", help="Optional findings JSON path relative to the target root")
    review.add_argument(
        "--engine-adapter",
        choices=tuple(sorted(AUTHORITATIVE_REVIEW_ADAPTERS)),
        help=(
            "Optional authoritative review engine adapter for review run/record. "
            "When omitted, verified Codex App sessions use loom/codex-app-review; headless/CI fallback remains loom/default-codex-exec."
        ),
    )
    review.add_argument("--engine-evidence", help="Optional review engine evidence path relative to the target root")
    review.add_argument("--normalized-findings", help="Optional normalized findings path relative to the target root")
    review.add_argument(
        "--codex-app-review-app-server",
        help=f"Codex App app-server/session locator. Defaults to ${CODEX_APP_REVIEW_ENDPOINT_ENV} when available.",
    )
    review.add_argument(
        "--codex-app-review-thread-id",
        help=f"Codex App thread id. Defaults to ${CODEX_APP_REVIEW_THREAD_ID_ENV}, or ${CODEX_THREAD_ID_ENV} when an endpoint is present.",
    )
    review.add_argument(
        "--codex-app-review-cwd",
        help=f"Codex App thread cwd proof. Defaults to ${CODEX_APP_REVIEW_CWD_ENV}.",
    )
    review.add_argument(
        "--codex-app-review-raw-file",
        help="Optional repo-relative Codex App normalized review output captured from review/start or same-thread normalization.",
    )
    review.add_argument("--engine-profile", choices=tuple(sorted(REVIEW_ENGINE_PROFILE_IDS)), help="Optional deterministic review engine profile override for review run")
    review.add_argument("--engine-model", help="Optional review engine model override for review run")
    review.add_argument("--engine-reasoning", choices=tuple(sorted(REVIEW_ENGINE_REASONING_EFFORTS)), help="Optional review engine reasoning effort override for review run")
    review.add_argument("--engine-override-reason", help="Required reason when overriding review engine profile, model, or reasoning")
    review.add_argument(
        "--engine-use-local-codex-defaults",
        action="store_true",
        help="Explicitly opt in to local ~/.codex/config.toml model/reasoning defaults when repo policy allows it.",
    )
    review.add_argument(
        "--shadow-engine-adapter",
        choices=tuple(sorted(SHADOW_REVIEW_ADAPTERS)),
        help="Optional shadow-only review adapter. Does not replace the default authoritative review engine.",
    )
    review.add_argument(
        "--shadow-review-raw-file",
        help="Optional repo-relative captured Codex App review text to normalize as shadow evidence.",
    )
    review.add_argument("--blocking-issue", action="append", default=[], help="Blocking review finding")
    review.add_argument("--follow-up", action="append", default=[], help="Follow-up item recorded by the review")

    recovery = subparsers.add_parser("recovery", help="Write the authored Loom recovery entry")
    recovery.add_argument("operation", choices=("writeback",))
    recovery.add_argument("--target", required=True, help="Target repository root")
    recovery.add_argument("--item", help="Expected current item id")
    recovery.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    recovery.add_argument("--current-checkpoint", help="Updated checkpoint value")
    recovery.add_argument("--current-stop", help="Updated current stop")
    recovery.add_argument("--next-step", help="Updated next step")
    recovery.add_argument("--blockers", help="Updated blockers summary")
    recovery.add_argument("--latest-validation-summary", help="Updated validation summary")
    recovery.add_argument("--recovery-boundary", help="Updated recovery boundary")
    recovery.add_argument("--current-lane", help="Updated current lane")

    work_item = subparsers.add_parser("work-item", help="Create or update a Loom work item")
    work_item.add_argument("operation", choices=("create", "update"))
    work_item.add_argument("--target", required=True, help="Target repository root")
    work_item.add_argument("--item", required=True, help="Work item id")
    work_item.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    work_item.add_argument("--goal", help="Static goal")
    work_item.add_argument("--scope", help="Static scope")
    work_item.add_argument("--execution-path", help="Execution path")
    work_item.add_argument("--workspace-entry", help="Workspace entry")
    work_item.add_argument("--recovery-entry", help="Recovery entry path relative to the target root")
    work_item.add_argument("--validation-entry", help="Validation entry command")
    work_item.add_argument("--closing-condition", help="Closing condition")
    work_item.add_argument("--artifact", action="append", default=[], help="Associated artifact for create")
    work_item.add_argument("--add-artifact", action="append", default=[], help="Associated artifact to append")
    work_item.add_argument("--remove-artifact", action="append", default=[], help="Associated artifact to remove")
    work_item.add_argument("--activate", action="store_true", help="Activate this item in the current fact chain")
    work_item.add_argument("--init-recovery", action="store_true", help="Initialize the recovery entry when creating")

    host = subparsers.add_parser("host-lifecycle", help="Classify host objects against Loom lifecycle boundaries")
    host.add_argument("--target", required=True, help="Target repository root")
    host.add_argument("--item", help="Expected current item id")
    host.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    closeout = subparsers.add_parser("closeout", help="Check or sync Loom closeout state with GitHub control plane")
    closeout.add_argument("operation", choices=("check", "sync"))
    closeout.add_argument("--target", required=True, help="Target repository root")
    closeout.add_argument("--item", help="Expected retained Loom Work Item id for closeout disambiguation")
    closeout.add_argument("--issue", type=int, help="GitHub issue number to validate or sync")
    closeout.add_argument("--pr", type=int, help="GitHub pull request number to validate or sync")
    closeout.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES, help="Explicit closeout PR role consumed by this check")
    closeout.add_argument("--implementation-pr", type=int, help="Implementation PR number for the closeout subject")
    closeout.add_argument("--release-pr", type=int, help="Release PR number for the closeout subject")
    closeout.add_argument("--carrier-sync-pr", type=int, help="Carrier sync PR number for the closeout subject")
    closeout.add_argument("--final-closeout-pr", type=int, help="Final closeout PR number for the closeout subject")
    closeout.add_argument("--project", type=int, help="GitHub project number to validate or sync")
    closeout.add_argument("--phase", type=int, help="GitHub Phase issue number")
    closeout.add_argument("--fr", type=int, help="GitHub FR issue number")
    closeout.add_argument("--branch", help="GitHub branch name bound to the work item")
    closeout.add_argument("--goal-completion", help="Optional repo-relative /goal completion evidence JSON")
    closeout.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    closeout.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    closeout.add_argument("--comment", help="Optional closeout comment for issue sync")
    closeout.add_argument(
        "--gate-profile",
        choices=CLOSEOUT_GATE_PROFILES,
        default="auto",
        help="Closeout local gate profile; auto uses the lightweight closeout contract unless a heavier profile is explicit.",
    )
    closeout.add_argument("--issue-payload-file", help="Optional repo-relative issue payload JSON fixture")
    closeout.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    closeout.add_argument("--project-payload-file", help="Optional repo-relative Project status JSON fixture")
    closeout.add_argument("--status-checks-file", help="Optional repo-relative statusCheckRollup JSON fixture")
    closeout.add_argument("--branch-protection-file", help="Optional repo-relative branch protection JSON fixture")
    closeout.add_argument("--ruleset-file", help="Optional repo-relative branch rules/ruleset JSON fixture")
    closeout.add_argument("--skip-gate", action="store_true", help="Skip explicit heavyweight local gate execution during closeout")

    closeout_queue = subparsers.add_parser("closeout-queue", help="Read post-merge closeout residue queue status without writing")
    closeout_queue.add_argument("operation", choices=("status",))
    closeout_queue.add_argument("--target", required=True, help="Target repository root")
    closeout_queue.add_argument("--issue", type=int, action="append", default=[], help="Limit scan to one or more GitHub issue numbers")
    closeout_queue.add_argument("--item", action="append", default=[], help="Limit scan to one or more Work Item ids")
    closeout_queue.add_argument("--queue-file", help="Optional repo-relative JSON fixture with host completion inputs")
    closeout_queue.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root; reported for next-command context only",
    )

    reconciliation = subparsers.add_parser("reconciliation", help="Audit Loom GitHub drift before closeout reconciliation")
    reconciliation.add_argument("operation", choices=("audit", "sync"))
    reconciliation.add_argument("--target", required=True, help="Target repository root")
    reconciliation.add_argument("--item", help="Expected retained Loom Work Item id for reconciliation disambiguation")
    reconciliation.add_argument("--issue", type=int, help="GitHub issue number to audit")
    reconciliation.add_argument("--pr", type=int, help="GitHub pull request number to audit")
    reconciliation.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES, help="Explicit closeout PR role consumed by this reconciliation read")
    reconciliation.add_argument("--implementation-pr", type=int, help="Implementation PR number for the closeout subject")
    reconciliation.add_argument("--release-pr", type=int, help="Release PR number for the closeout subject")
    reconciliation.add_argument("--carrier-sync-pr", type=int, help="Carrier sync PR number for the closeout subject")
    reconciliation.add_argument("--final-closeout-pr", type=int, help="Final closeout PR number for the closeout subject")
    reconciliation.add_argument("--project", type=int, help="GitHub project number to audit")
    reconciliation.add_argument("--phase", type=int, help="GitHub Phase issue number")
    reconciliation.add_argument("--fr", type=int, help="GitHub FR issue number")
    reconciliation.add_argument("--branch", help="GitHub branch name bound to the work item")
    reconciliation.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    reconciliation.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    reconciliation.add_argument("--issue-payload-file", help="Optional repo-relative issue payload JSON fixture")
    reconciliation.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    reconciliation.add_argument("--project-payload-file", help="Optional repo-relative Project status JSON fixture")
    reconciliation.add_argument("--comment", help="Optional closeout comment for issue sync")
    reconciliation.add_argument("--comment-file", help="Read closeout comment body from a file")
    reconciliation.add_argument("--dry-run", action="store_true", default=True, help="Preview reconciliation sync actions without writing GitHub state; this is the default")
    reconciliation.add_argument("--apply", dest="dry_run", action="store_false", help="Apply the audited safe sync plan to GitHub control-plane state")

    shadow = subparsers.add_parser("shadow-parity", help="Compare Loom and repo-native parity surfaces without changing merge gates")
    shadow.add_argument("--target", required=True, help="Target repository root")
    shadow.add_argument(
        "--surface",
        choices=(*SHADOW_PARITY_SURFACES, "all"),
        default="all",
        help="Shadow surface to compare; defaults to all supported surfaces",
    )
    shadow.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    shadow.add_argument(
        "--mode",
        choices=("validation-only", "blocking"),
        default="validation-only",
        help="Shadow parity enforcement mode; defaults to validation-only.",
    )
    shadow.add_argument(
        "--blocking",
        action="store_true",
        help="Shortcut for --mode blocking. This is explicit opt-in and never the default.",
    )

    runtime_parity = subparsers.add_parser(
        "runtime-parity",
        help="Validate Loom core strong-governance runtime parity without host-specific orchestration",
    )
    runtime_parity.add_argument("operation", choices=("validate",))
    runtime_parity.add_argument("--target", required=True, help="Target repository root")
    runtime_parity.add_argument("--item", help="Expected current item id")
    runtime_parity.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    governance_profile = subparsers.add_parser(
        "governance-profile",
        help="Read Loom governance maturity and upgrade requirements",
    )
    governance_profile.add_argument("operation", choices=("status", "upgrade-plan", "upgrade", "binding"))
    governance_profile.add_argument("--target", required=True, help="Target repository root")
    governance_profile.add_argument("--host", choices=("github",), default="github", help="Host profile to evaluate")
    governance_profile.add_argument("--to", choices=("standard", "strong"), help="Target maturity for governance-profile upgrade")
    governance_profile.add_argument("--dry-run", action="store_true", default=True, help="Preview upgrade actions without writing files; this is the default")
    governance_profile.add_argument("--apply", dest="dry_run", action="store_false", help="Apply Loom-owned scaffold writes")
    governance_profile.add_argument("--force", action="store_true", help="Allow replacement of existing Loom-owned scaffold files during upgrade apply")
    governance_profile.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    governance_profile.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    governance_profile.add_argument("--phase", type=int, help="GitHub Phase issue number")
    governance_profile.add_argument("--fr", type=int, help="GitHub FR issue number")
    governance_profile.add_argument("--issue", type=int, help="GitHub Work Item issue number")
    governance_profile.add_argument("--pr", type=int, help="GitHub implementation PR number")
    governance_profile.add_argument("--branch", help="GitHub branch name bound to the work item")
    governance_profile.add_argument("--sync", action="store_true", help="Preview host binding repairs; writes are intentionally disabled in this phase")

    live_smoke = subparsers.add_parser(
        "live-smoke",
        help="Run or replay versioned adopted-repo live smoke evidence without changing core gates",
    )
    live_smoke.add_argument(
        "operation",
        choices=(
            "run",
            "replay",
            "external-result-source-readback",
            "dynamic-tool-availability",
            "hook-envelope",
            "hooks-extension",
            "external-orchestrator-interop",
        ),
    )
    live_smoke.add_argument("--target", help="Adopted repository root for live smoke run")
    live_smoke.add_argument("--item", default="INIT-0001", help="Expected current item id for the optional resume smoke")
    live_smoke.add_argument("--prior-evidence", help="Versioned prior-pass evidence to replay without running adopted-repo commands")
    live_smoke.add_argument("--dry-run", action="store_true", help="Preview the live smoke command plan without running adopted-repo commands")
    live_smoke.add_argument(
        "--surface",
        choices=("attempt_time", "review", "merge_ready", "closeout", "build", "admission", "pre_review", "all"),
        default="attempt_time",
        help="Dynamic tool live availability surface; defaults to attempt_time",
    )
    live_smoke.add_argument("--envelope", help="Repo-relative Loom hook envelope path for live-smoke hook-envelope")
    live_smoke.add_argument(
        "--requirement",
        choices=("required", "optional", "advisory"),
        default="required",
        help="Hook envelope requirement level; defaults to required",
    )
    live_smoke.add_argument(
        "--include-blocking-shadow",
        action="store_true",
        help="Explicitly include shadow-parity --blocking in the smoke command set",
    )

    flow = subparsers.add_parser("flow", help="Run a bundled high-frequency Loom flow")
    flow.add_argument("operation", choices=("build", "story", "pre-review", "review", "spec-review", "resume", "handoff", "merge-ready"))
    flow.add_argument("--target", required=True, help="Target repository root")
    flow.add_argument("--item", help="Expected current item id")
    flow.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )
    flow.add_argument("--build-evidence", help="Optional build evidence JSON path relative to the target root")
    flow.add_argument("--owner", help="GitHub owner; auto-detected from origin when omitted")
    flow.add_argument("--repo", dest="repo_name", help="GitHub repository name; auto-detected from origin when omitted")
    flow.add_argument("--issue", type=int, help="GitHub Work Item issue number for host status reads")
    flow.add_argument("--pr", type=int, help="GitHub implementation PR number for host status reads")
    flow.add_argument("--pr-payload-file", help="Optional repo-relative PR payload JSON fixture")
    flow.add_argument("--project", type=int, help="GitHub Project number for Project drift reads")
    flow.add_argument("--fr", type=int, help="GitHub FR locator for host-native lifecycle admission")
    flow.add_argument("--branch", help="GitHub branch name for host binding reads")
    flow.add_argument("--project-drift-mode", choices=("advisory", "blocking"), default="advisory")

    return parser.parse_args(argv)











































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "fact-chain":
        return handle_fact_chain(args)
    if args.command == "runtime-state":
        return handle_runtime_state(args)
    if args.command == "adopt":
        return handle_adopt(args)
    if args.command == "repair":
        return handle_repair(args)
    if args.command == "carrier":
        return handle_carrier(args)
    if args.command == "host-binding":
        return handle_host_binding(args)
    if args.command == "github-intake":
        return handle_github_intake(args)
    if args.command == "goal":
        return handle_goal(args)
    if args.command == "pr-gate":
        return handle_pr_gate(args)
    if args.command == "pr-metadata":
        return handle_pr_metadata(args)
    if args.command == "gate-freeze":
        return handle_gate_freeze(args)
    if args.command == "controlled-merge":
        return handle_controlled_merge(args)
    if args.command == "gate-repair-pr":
        return handle_gate_repair_pr(args)
    if args.command == "runtime-evidence":
        return handle_runtime_evidence(args)
    if args.command == "state-check":
        return handle_state_check(args)
    if args.command == "review":
        return handle_review(args)
    if args.command == "recovery":
        return handle_recovery(args)
    if args.command == "work-item":
        return handle_work_item(args)
    if args.command == "host-lifecycle":
        return handle_host_lifecycle(args)
    if args.command == "closeout":
        return handle_closeout(args)
    if args.command == "closeout-queue":
        return handle_closeout_queue(args)
    if args.command == "reconciliation":
        return handle_reconciliation(args)
    if args.command == "shadow-parity":
        return handle_shadow_parity(args)
    if args.command == "live-smoke":
        return handle_live_smoke(args)
    if args.command == "runtime-parity":
        return handle_runtime_parity(args)
    if args.command == "governance-profile":
        return handle_governance_profile(args)
    if args.command == "flow":
        return handle_flow(args)
    if args.command == "checkpoint":
        return handle_checkpoint(args)
    if args.command == "workspace":
        return handle_workspace(args)
    if args.command == "work-item-audit":
        return handle_work_item_audit(args)
    return handle_purity(args)


if __name__ == "__main__":
    raise SystemExit(main())
