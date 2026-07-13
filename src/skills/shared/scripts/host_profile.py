#!/usr/bin/env python3
"""GitHub host binding, governance profile, adoption, and project integration domain."""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback path
    tomllib = None  # type: ignore[assignment]
from flow_runtime import command_target, emit, git_branch, resolve_target_arg, runtime_state_payload
from delivery_control import (
    current_cwd_relative,
    dedupe_strings,
    dependency_graph_payload,
    detect_github_repo,
    git_changed_paths,
    github_commit_pulls,
    load_context,
    purity_report_from_context,
    relative_to_root,
    runtime_state_block_payload,
    text_mentions_issue,
)
from github_host import (
    gh_graphql,
    gh_graphql_json,
    gh_json,
    gh_rest_write_json,
    github_branch_payload,
    github_issue_dependencies_payload,
    github_issue_payload,
    github_native_dependency_capability,
    github_pr_payload,
    graphql_budget_guard,
    normalize_rest_issue,
    run_process,
)
from governance_surface import (
    build_governance_surface,
    workspace_lifecycle_expectations,
)

FLOW_ENTRYPOINT = Path(__file__).with_name("loom_flow.py")

HOST_BINDING_INSPECTOR_SCHEMA = "loom-host-binding-inspection/v1"

HOST_BINDING_CHAIN_SCHEMA = "loom-host-binding-chain/v1"

PROJECT_DRIFT_SCHEMA = "loom-project-drift/v1"

SHADOW_PARITY_SURFACES = ("admission", "review", "merge_ready", "closeout")

ADOPTION_DECISIONS_SCHEMA = "loom-adoption-decisions/v1"

GUIDED_ADOPTION_PLAN_SCHEMA = "loom-guided-adoption-plan/v1"

COMPANION_GENERATION_SCHEMA = "loom-companion-generation/v1"

ADOPTION_DECISION_QUESTIONS: dict[str, str] = {
    "fr_work_item_layer": "Which host planning object owns the FR layer, and how does each FR point to its Work Item?",
    "closeout_reconciliation_read": "Which repo-native or host-owned closeout and reconciliation result should Loom read without taking ownership?",
    "repo_interface": "Which repo-specific requirements, specialized gates, metadata contracts, or context fields must remain repo companion-owned?",
    "repo_interop": "Which retained host action results, repo-native carriers, and shadow parity surfaces should Loom read?",
    "github_controlled_merge": "Which GitHub-controlled merge evidence proves the host merge boundary is ready without Loom taking over the host action?",
    "repo_specific_residue": "Which repo-specific residue must stay repo-owned instead of becoming Loom core?",
    "spec_review_instruction_locator": "Where does the adopted repository declare repo-owned spec review instructions without making Loom guess a filename?",
    "implementation_review_instruction_locator": "Where does the adopted repository declare repo-owned implementation review instructions without making Loom guess a filename?",
    "authority_boundary": "Where is the authority-of-truth for repo-native results, overrides, and fallback decisions?",
    "guardian_integration_contract": "Which guardian or integration-contract verdicts should be read as repo-native evidence rather than promoted into Loom core?",
}

ADOPTION_DECISION_ORDER: list[str] = [
    "fr_work_item_layer",
    "closeout_reconciliation_read",
    "repo_interface",
    "repo_interop",
    "github_controlled_merge",
    "repo_specific_residue",
    "spec_review_instruction_locator",
    "implementation_review_instruction_locator",
    "authority_boundary",
    "guardian_integration_contract",
]

ADOPTION_DECISION_SOURCES: dict[str, str] = {
    "fr_work_item_layer": "docs/adoption/github-profile-upgrade.md",
    "closeout_reconciliation_read": "docs/adoption/repo-interop-contract.md",
    "repo_interface": "docs/adoption/repo-companion-contract.md",
    "repo_interop": "docs/adoption/repo-interop-contract.md",
    "github_controlled_merge": "docs/adoption/github-profile.md",
    "repo_specific_residue": "docs/adoption/repo-companion-contract.md",
    "spec_review_instruction_locator": "docs/adoption/repo-companion-contract.md",
    "implementation_review_instruction_locator": "docs/adoption/repo-companion-contract.md",
    "authority_boundary": "docs/adoption/repo-interop-contract.md",
    "guardian_integration_contract": "docs/adoption/repo-interop-contract.md",
}

ADOPTION_DECISION_WRITE_TARGETS: dict[str, list[str]] = {
    "fr_work_item_layer": [".loom/companion/repo-interface.json"],
    "closeout_reconciliation_read": [".loom/companion/interop.json"],
    "repo_interface": [".loom/companion/manifest.json", ".loom/companion/repo-interface.json"],
    "repo_interop": [".loom/companion/interop.json"],
    "github_controlled_merge": ["github:branch_protection.required_checks", "github:pull_request.merge_method"],
    "repo_specific_residue": [".loom/companion/README.md", ".loom/companion/repo-interface.json"],
    "spec_review_instruction_locator": [".loom/companion/repo-interface.json:review_instruction_locators.spec_review"],
    "implementation_review_instruction_locator": [".loom/companion/repo-interface.json:review_instruction_locators.implementation_review"],
    "authority_boundary": [".loom/companion/interop.json"],
    "guardian_integration_contract": [".loom/companion/interop.json"],
}

DEFAULT_GITHUB_INTAKE_OBJECT_TYPE_MAPPINGS = (
    {"loom_type": "phase", "labels": ("phase",), "title_prefixes": ("phase:",)},
    {"loom_type": "fr", "labels": ("fr",), "title_prefixes": ("fr:",)},
    {"loom_type": "work_item", "labels": ("work-item",), "title_prefixes": ("work-item:", "bug:")},
)

HOST_PLANNING_MISSING_TYPE_POLICIES = {"advisory_unknown", "infer_from_context", "block_unknown"}

def adoption_validation_commands(target_root: Path) -> list[str]:
    target = command_target(target_root)
    return [
        f"python3 tools/loom_flow.py governance-profile upgrade-plan --target {target} --host github",
        f"python3 tools/loom_flow.py adopt verify --target {target}",
    ]

def adoption_decision_reasoning(decision_id: str, detail: dict[str, Any]) -> str:
    if decision_id == "github_controlled_merge":
        return "GitHub remains the merge authority; Loom only reads required checks, PR merge state, merge commit, and closeout basis before delegating host merge."
    if decision_id == "spec_review_instruction_locator":
        return "Deep existing repositories must declare their own spec review instruction locator so Loom does not infer repo-specific filenames or review policy."
    if decision_id == "implementation_review_instruction_locator":
        return "Deep existing repositories must declare their own implementation review instruction locator so Loom can consume repo-owned guidance without moving it into core."
    if decision_id == "guardian_integration_contract":
        return "Guardian and integration-contract verdicts are repo-native evidence; Loom may read them through interop but must not promote their rules into core."
    if decision_id == "authority_boundary":
        return "Blocking ownership, fallback, override, and authority-of-truth stay outside interop; interop only declares read locators."
    if decision_id == "repo_specific_residue":
        return "Repo-specific rules and residue stay in repo companion so Loom can consume them without turning single-repo practice into defaults."
    recommended = detail.get("recommended_action")
    if isinstance(recommended, str) and recommended:
        return recommended
    return "This judgment is required before Loom can turn adoption guidance into generated writeback and verification evidence."

def adoption_judgment_status(decision_id: str, missing: set[str]) -> str:
    if decision_id in missing:
        return "blocked" if not ADOPTION_DECISION_WRITE_TARGETS.get(decision_id) else "missing"
    if decision_id == "repo_specific_residue" and "repo_interface" in missing:
        return "missing"
    if decision_id in {"spec_review_instruction_locator", "implementation_review_instruction_locator"} and "repo_interface" in missing:
        return "missing"
    if decision_id in {"authority_boundary", "guardian_integration_contract", "closeout_reconciliation_read"} and "repo_interop" in missing:
        return "missing"
    return "answered"

def adoption_decisions_payload(
    target_root: Path,
    *,
    target_level: str | None,
    maturity: dict[str, Any],
) -> dict[str, Any]:
    missing_by_level = maturity.get("missing_by_level")
    missing_details_by_level = maturity.get("missing_details_by_level")
    missing = (
        list(missing_by_level.get(target_level, []))
        if isinstance(missing_by_level, dict) and isinstance(target_level, str)
        else []
    )
    details = (
        list(missing_details_by_level.get(target_level, []))
        if isinstance(missing_details_by_level, dict) and isinstance(target_level, str)
        else []
    )
    detail_by_id = {row.get("id"): row for row in details if isinstance(row, dict)}
    missing_set = {str(item) for item in missing}
    ordered_ids = list(dict.fromkeys([*missing, *ADOPTION_DECISION_ORDER]))
    judgments: list[dict[str, Any]] = []
    for raw_id in ordered_ids:
        decision_id = str(raw_id)
        detail = detail_by_id.get(decision_id, {})
        source_locator = ADOPTION_DECISION_SOURCES.get(decision_id, "docs/adoption/github-profile-upgrade.md")
        write_targets = ADOPTION_DECISION_WRITE_TARGETS.get(decision_id, [".loom/companion/repo-interface.json"])
        verification_commands = adoption_validation_commands(target_root)
        if decision_id in {"repo_interop", "closeout_reconciliation_read", "authority_boundary", "guardian_integration_contract"}:
            verification_commands.append(f"python3 tools/loom_flow.py shadow-parity --target {command_target(target_root)}")
        judgments.append(
            {
                "id": decision_id,
                "question": ADOPTION_DECISION_QUESTIONS.get(decision_id, f"How should Loom satisfy `{decision_id}` without creating a second truth source?"),
                "source_locator": source_locator,
                "reasoning": adoption_decision_reasoning(decision_id, detail),
                "write_targets": write_targets,
                "verification_commands": verification_commands,
                "status": adoption_judgment_status(decision_id, missing_set),
                "layer": detail.get("layer"),
            }
        )
    return {
        "schema_version": ADOPTION_DECISIONS_SCHEMA,
        "target_maturity": target_level,
        "summary": "Fixed adoption judgments bind every repo-specific decision to source locators, write targets, and verification commands.",
        "judgments": judgments,
    }

def guided_adoption_plan_payload(decisions: dict[str, Any]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    for judgment in decisions.get("judgments", []):
        if not isinstance(judgment, dict):
            continue
        for phase, action in (
            ("read", f"Read `{judgment.get('source_locator')}` and the target repository surface that motivated `{judgment.get('id')}`."),
            ("judge", str(judgment.get("question"))),
            ("write", "Apply only the declared write targets; leave repo-owned residue repo-owned."),
            ("verify", "Run the declared verification commands and keep the evidence with the adoption closeout."),
        ):
            steps.append(
                {
                    "phase": phase,
                    "judgment_id": judgment.get("id"),
                    "action": action,
                    "source_locator": judgment.get("source_locator"),
                    "write_targets": list(judgment.get("write_targets", [])),
                    "verification_commands": list(judgment.get("verification_commands", [])),
                    "status": judgment.get("status"),
                }
            )
    return {
        "schema_version": GUIDED_ADOPTION_PLAN_SCHEMA,
        "phase_order": ["read", "judge", "write", "verify"],
        "summary": "Agent-assisted adoption proceeds through read, judge, write, and verify without requiring hand-authored companion or interop evidence.",
        "steps": steps,
    }

def default_companion_manifest() -> dict[str, Any]:
    return {
        "schema_version": "loom-repo-companion-manifest/v1",
        "companion_entry": ".loom/companion/README.md",
        "repo_interface": ".loom/companion/repo-interface.json",
    }

def default_repo_interface() -> dict[str, Any]:
    return {
        "schema_version": "loom-repo-interface/v2",
        "companion_entry": ".loom/companion/README.md",
        "repo_specific_requirements": {"review": [], "merge_ready": [], "closeout": []},
        "specialized_gates": [],
        "review_instruction_locators": {
            "spec_review": {"locator": "loom_default", "mode": "loom_default"},
            "implementation_review": {"locator": "loom_default", "mode": "loom_default"},
        },
        "metadata_contract": {"fields": []},
        "context_schema": {"fields": []},
        "dynamic_tool_locators": [],
        "policy_locators": [],
        "hook_locators": [],
    }

def default_repo_interop() -> dict[str, Any]:
    return {
        "schema_version": "loom-repo-interop/v2",
        "repo_native_carriers": [
            {
                "id": "generated-companion-residue",
                "summary": "Repo-owned adoption residue generated as explicit write targets; Loom reads it without promoting the repo-specific rules into core.",
                "surfaces": list(SHADOW_PARITY_SURFACES),
                "locator": ".loom/companion",
                "owner": "repo-companion",
                "requirement": "required",
                "fallback_to": "adoption",
            }
        ],
        "shadow_surfaces": {
            surface: {
                "summary": f"Compare {surface} parity between Loom and the repo-native result.",
                "loom_locator": f".loom/shadow/{surface.replace('_', '-')}-loom.json",
                "repo_locator": f".loom/shadow/{surface.replace('_', '-')}-repo.json",
            }
            for surface in SHADOW_PARITY_SURFACES
        },
    }

def companion_text_payloads() -> dict[str, str]:
    return {
        ".loom/companion/README.md": (
            "# Repo Companion\n\n"
            "This companion records repo-specific adoption residue while Loom core remains the upstream governance source.\n"
        ),
        ".loom/companion/review.md": "# Companion Review Surface\n",
        ".loom/companion/merge-ready.md": "# Companion Merge-Ready Surface\n",
        ".loom/companion/closeout.md": "# Companion Closeout Surface\n",
        ".loom/companion/checkpoints.md": "# Companion Checkpoints\n",
    }

def companion_json_payloads() -> dict[str, dict[str, Any]]:
    return {
        ".loom/companion/manifest.json": default_companion_manifest(),
        ".loom/companion/repo-interface.json": default_repo_interface(),
        ".loom/companion/interop.json": default_repo_interop(),
    }

UPGRADE_SCAFFOLD: dict[str, str] = {
    **companion_text_payloads(),
    **{
        relative: json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        for relative, payload in companion_json_payloads().items()
    },
}

def companion_artifact_rows(target_root: Path, *, written_files: list[str] | None = None) -> list[dict[str, Any]]:
    written = set(written_files or [])
    paths = [
        *companion_text_payloads().keys(),
        *companion_json_payloads().keys(),
    ]
    rows = []
    for relative in paths:
        path = target_root / relative
        rows.append(
            {
                "path": relative,
                "kind": "json" if relative.endswith(".json") else "text",
                "owner": "repo-owned" if relative.startswith(".loom/companion/") else "loom-owned",
                "action": "keep_existing" if path.exists() and relative not in written else "write_scaffold",
                "status": "written" if relative in written else "present" if path.exists() else "planned",
                "source_judgment": "repo_interop" if "interop" in relative or "/shadow/" in relative else "repo_interface",
            }
        )
    return rows

def apply_companion_generation(target_root: Path, *, force: bool) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    written: list[str] = []
    for relative, content in companion_text_payloads().items():
        path = target_root / relative
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                blockers.append(f"refusing to overwrite repo-owned adoption artifact: {relative}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(relative)
    for relative, payload in companion_json_payloads().items():
        path = target_root / relative
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                blockers.append(f"refusing to overwrite repo-owned adoption artifact: {relative}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(relative)
    return written, blockers

def companion_generation_payload(
    target_root: Path,
    decisions: dict[str, Any],
    *,
    dry_run: bool,
    written_files: list[str] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    missing_inputs = blockers or []
    return {
        "schema_version": COMPANION_GENERATION_SCHEMA,
        "result": "block" if missing_inputs else "pass",
        "summary": "repo companion and interop artifacts are generated from bounded adoption decisions.",
        "dry_run": dry_run,
        "source_decisions": [
            judgment.get("id")
            for judgment in decisions.get("judgments", [])
            if isinstance(judgment, dict)
        ],
        "artifacts": companion_artifact_rows(target_root, written_files=written_files),
        "missing_inputs": missing_inputs,
        "verification_commands": adoption_validation_commands(target_root),
    }

def select_workspace_profile_name(workspace_entry: str, item_id: str) -> tuple[str, str]:
    normalized = workspace_entry.strip().replace("\\", "/")
    if normalized == ".":
        return "single-workspace", "workspace_entry points at the repository root"
    if normalized.startswith(".worktrees/") or (item_id and item_id in normalized):
        return "per-item-worktree", "workspace_entry is item-scoped or under `.worktrees/`"
    return "attach-existing", "workspace_entry points at an existing repo-defined workspace"

def workspace_profile_from_context(context: dict[str, Any]) -> dict[str, Any]:
    selected, reason = select_workspace_profile_name(context["workspace_entry"], context["item_id"])
    return {
        "schema_version": "loom-workspace-profile/v1",
        "selected": selected,
        "selection_reason": reason,
        "workspace_entry": context["workspace_entry"],
        "workspace_path": relative_to_root(context["workspace_path"], context["target_root"]),
        "workspace_exists": context["workspace_path"].exists(),
        "host_worktree": {
            "ownership": "host",
            "cwd_within_repo": current_cwd_relative(context["target_root"]) or "outside_target_repo",
            "status": "host_managed",
        },
        "recommended_action": (
            "keep workspace_entry as `.` unless isolation becomes necessary"
            if selected == "single-workspace"
            else "ensure workspace, branch, Work Item, and PR bindings stay aligned"
            if selected == "per-item-worktree"
            else "keep repo-specific workspace locator declared and host lifecycle ownership external"
        ),
    }

def host_binding_validate_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int | str | None,
    fr_number: int | str | None = None,
    pr_number: int | None,
    branch_name: str | None,
    head_sha: str | None,
    base_sha: str | None,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    missing_inputs: list[str] = []
    inferences: list[dict[str, Any]] = []

    if not owner or not repo_name:
        missing_inputs.append("owner/repo")

    inferred_pr = pr_number
    inferred_branch = branch_name
    if owner and repo_name and head_sha and inferred_pr is None:
        pulls, pull_errors = github_commit_pulls(target_root, owner, repo_name, head_sha)
        if pull_errors:
            missing_inputs.extend(f"head_sha: {message}" for message in pull_errors)
        elif len(pulls) == 1:
            inferred_pr = int(pulls[0].get("number"))
            head = pulls[0].get("head")
            if inferred_branch is None and isinstance(head, dict) and isinstance(head.get("ref"), str):
                inferred_branch = head.get("ref")
            inferences.append({"from": "head_sha", "to": "pr", "status": "inferred", "pr": inferred_pr})
        elif len(pulls) > 1:
            missing_inputs.append("head_sha resolves to multiple PRs; pass --pr explicitly")
        else:
            missing_inputs.append("issue_or_pr_binding")

    if inferred_branch is None and head_sha is None and inferred_pr is None and issue_number is None:
        missing_inputs.append("branch | head-sha | pr | issue")

    branch_payload: dict[str, Any] | None = None
    branch_errors: list[str] = []
    if owner and repo_name and inferred_branch:
        branch_payload, branch_errors = github_branch_payload(target_root, owner, repo_name, inferred_branch)
        missing_inputs.extend(f"branch: {message}" for message in branch_errors)

    binding_payload = github_binding_payload(
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        phase_number=None,
        fr_number=None,
        issue_number=issue_number,
        pr_number=inferred_pr,
        branch_name=inferred_branch,
        sync=False,
        dry_run=True,
        require_complete_chain=False,
    )
    binding_missing = [
        message
        for message in binding_payload.get("missing_inputs", [])
        if message not in {"work_item issue", "binding_chain"}
    ]
    if issue_number is not None or inferred_pr is not None:
        missing_inputs.extend(str(message) for message in binding_missing)
    findings = binding_payload.get("binding", {}).get("findings") if isinstance(binding_payload.get("binding"), dict) else []
    if findings:
        missing_inputs.append("binding_findings")

    sha_validation: dict[str, Any] = {
        "head_sha": head_sha,
        "base_sha": base_sha,
        "status": "not_requested" if not head_sha else "validated",
    }
    if head_sha and branch_payload is not None:
        branch_head = branch_payload.get("commit", {}).get("sha") if isinstance(branch_payload.get("commit"), dict) else None
        sha_validation["branch_head_sha"] = branch_head
        if branch_head and branch_head != head_sha:
            sha_validation["status"] = "drift"
            missing_inputs.append("head_sha does not match branch head")
    if base_sha and head_sha:
        changed_paths, diff_errors = git_changed_paths(target_root, base_sha, head_sha)
        sha_validation["diff"] = {"changed_paths": changed_paths, "errors": diff_errors}
        if diff_errors:
            missing_inputs.extend(f"diff: {message}" for message in diff_errors)

    result = "pass" if not missing_inputs else "block"
    return {
        "command": "host-binding",
        "operation": "validate",
        "schema_version": "loom-host-binding/v1",
        "result": result,
        "summary": (
            "host binding inputs are readable and sufficiently bound."
            if result == "pass"
            else "host binding inputs are missing or ambiguous."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "github-profile-binding",
        "repository": {"owner": owner, "name": repo_name},
        "inputs": {
            "issue": issue_number,
            "pr": pr_number,
            "branch": branch_name,
            "head_sha": head_sha,
            "base_sha": base_sha,
        },
        "inferences": inferences,
        "binding": binding_payload.get("binding"),
        "branch": {
            "name": inferred_branch,
            "status": "present" if branch_payload is not None else ("unreadable" if branch_errors else "not_requested"),
            "errors": branch_errors,
        },
        "sha_validation": sha_validation,
    }

def binding_node(
    *,
    role: str,
    locator: str | None,
    freshness: str,
    source_layer: str,
    source_owner: str,
    value: dict[str, Any] | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "role": role,
        "locator": locator,
        "freshness": freshness,
        "value": value,
        "errors": list(errors or []),
        "provenance": [
            {
                "source_layer": source_layer,
                "source_owner": source_owner,
                "source_locator": locator,
                "freshness": freshness,
            }
        ],
    }

def host_binding_inspection_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    phase_number: int | None,
    fr_number: int | None,
    issue_number: int | None,
    pr_number: int | None,
    project_number: int | None,
    branch_name: str | None,
    head_sha: str | None,
    base_sha: str | None,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    missing_inputs: list[str] = []
    findings: list[dict[str, Any]] = []
    if not owner or not repo_name:
        missing_inputs.append("owner/repo")

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
        dry_run=True,
        require_complete_chain=False,
    )
    binding = binding_payload.get("binding") if isinstance(binding_payload.get("binding"), dict) else {}
    objects = binding.get("objects") if isinstance(binding, dict) else {}
    if not isinstance(objects, dict):
        objects = {}

    issue_payload: dict[str, Any] | None = None
    issue_errors: list[str] = []
    if owner and repo_name and issue_number is not None:
        issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
        missing_inputs.extend(f"work_item: {message}" for message in issue_errors)

    native_dependencies = (
        github_issue_dependencies_payload(target_root, owner, repo_name, issue_number)
        if owner and repo_name and issue_number is not None
        else {"availability": "not_requested", "checks": [], "native_edges": []}
    )
    dependency_graph = dependency_graph_payload(
        issue_number=issue_number,
        issue_payload=issue_payload,
        native_dependency_payload=native_dependencies,
    )
    findings.extend(dependency_graph.get("findings", []))

    project_item: dict[str, Any] | None = None
    project_errors: list[str] = []
    if project_number is not None and owner:
        project_context, project_errors = project_status_context(target_root, owner, project_number)
        if not project_errors:
            project_item = find_project_item(project_context["items"], issue_number, "issue") if issue_number is not None else None
        else:
            missing_inputs.extend(f"project: {message}" for message in project_errors)

    def object_node(role: str, fallback_locator: str | None = None) -> dict[str, Any]:
        value = objects.get(role)
        if isinstance(value, dict):
            status = value.get("status")
            errors = value.get("errors") if isinstance(value.get("errors"), list) else []
            freshness = "fresh" if status in {"present", "host-managed", "profile-defined"} else "missing"
            if errors:
                freshness = "unreadable"
            locator = (
                str(value.get("url"))
                if isinstance(value.get("url"), str)
                else str(value.get("name"))
                if isinstance(value.get("name"), str)
                else fallback_locator
            )
            return binding_node(
                role=role,
                locator=locator,
                freshness=freshness,
                source_layer="host_control_mirror",
                source_owner="github",
                value=value,
                errors=[str(error) for error in errors],
            )
        return binding_node(
            role=role,
            locator=fallback_locator,
            freshness="missing",
            source_layer="host_control_mirror",
            source_owner="github",
            value=None,
        )

    nodes = {
        "phase": object_node("phase", f"issue #{phase_number}" if phase_number else None),
        "fr": object_node("fr", f"issue #{fr_number}" if fr_number else None),
        "work_item": object_node("work_item", f"issue #{issue_number}" if issue_number else None),
        "branch": object_node("branch", branch_name),
        "target_branch": object_node("target_branch", branch_name),
        "implementation_pr": object_node("implementation_pr", f"PR #{pr_number}" if pr_number else None),
        "pr": object_node("implementation_pr", f"PR #{pr_number}" if pr_number else None),
        "merge_commit": object_node("merge_commit"),
        "project_item": binding_node(
            role="project_item",
            locator=f"Project #{project_number}" if project_number is not None else None,
            freshness="fresh" if project_item is not None else ("unreadable" if project_errors else "missing"),
            source_layer="host_control_mirror",
            source_owner="github_project",
            value=project_item,
            errors=project_errors,
        ),
    }
    if head_sha:
        branch_head = nodes["branch"].get("value", {}).get("head_sha") if isinstance(nodes["branch"].get("value"), dict) else None
        if branch_head and branch_head != head_sha:
            nodes["branch"]["freshness"] = "conflict"
            findings.append(
                {
                    "category": "drift",
                    "kind": "conflicting_binding",
                    "severity": "block",
                    "subject": "branch head SHA",
                    "evidence": {"expected_head_sha": head_sha, "branch_head_sha": branch_head},
                    "fallback_to": "github-profile-binding",
                }
            )
    for role, node in nodes.items():
        freshness = node.get("freshness")
        if freshness in {"missing", "unreadable", "conflict"} and role in {"work_item", "branch", "pr", "project_item"}:
            kind = "unreadable_host_signal" if freshness == "unreadable" else "conflicting_binding" if freshness == "conflict" else "missing_binding"
            findings.append(
                {
                    "category": "drift" if kind != "missing_binding" else "gate_failure",
                    "kind": kind,
                    "severity": "block" if role in {"work_item", "pr"} else "warn",
                    "subject": role,
                    "evidence": {"node": node},
                    "fallback_to": "github-profile-binding",
                }
            )
    binding_findings = binding.get("findings") if isinstance(binding, dict) else []
    if isinstance(binding_findings, list):
        findings.extend(finding for finding in binding_findings if isinstance(finding, dict))

    blocking_findings = [finding for finding in findings if finding.get("severity") == "block"]
    result = "pass" if not missing_inputs and not blocking_findings else "block"
    return {
        "command": "host-binding",
        "operation": "inspect",
        "schema_version": HOST_BINDING_INSPECTOR_SCHEMA,
        "result": result,
        "summary": (
            "host binding inspector found a consumable binding chain."
            if result == "pass"
            else "host binding inspector found missing, stale, unreadable, or conflicting host signals."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "github-profile-binding",
        "repository": {"owner": owner, "name": repo_name},
        "inputs": {
            "phase": phase_number,
            "fr": fr_number,
            "issue": issue_number,
            "pr": pr_number,
            "project": project_number,
            "branch": branch_name,
            "head_sha": head_sha,
            "base_sha": base_sha,
        },
        "binding_chain": {
            "schema_version": HOST_BINDING_CHAIN_SCHEMA,
            "nodes": nodes,
            "edges": binding.get("chain", []) if isinstance(binding, dict) else [],
        },
        "dependency_graph": dependency_graph,
        "provenance": [
            {
                "source_layer": "host_control_mirror",
                "source_owner": "github",
                "source_locator": f"{owner}/{repo_name}" if owner and repo_name else None,
                "freshness": "fresh" if not missing_inputs else "unreadable",
            }
        ],
        "findings": findings,
    }

def handle_host_binding(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    if args.operation == "inspect":
        return emit(
            host_binding_inspection_payload(
                target_root=target_root,
                owner=args.owner,
                repo_name=args.repo_name,
                phase_number=args.phase,
                fr_number=args.fr,
                issue_number=args.issue,
                pr_number=args.pr,
                project_number=args.project,
                branch_name=args.branch,
                head_sha=args.head_sha,
                base_sha=args.base_sha,
            )
        )
    return emit(
        host_binding_validate_payload(
            target_root=target_root,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
            pr_number=args.pr,
            branch_name=args.branch,
            head_sha=args.head_sha,
            base_sha=args.base_sha,
        )
    )

def host_lifecycle_payload(context: dict[str, Any]) -> dict[str, Any]:
    branch = git_branch(context["target_root"])
    purity = purity_report_from_context(context)
    workspace_profile = workspace_profile_from_context(context)
    lifecycle_expectations = workspace_lifecycle_expectations(workspace_profile)
    worktree_root = current_cwd_relative(context["target_root"])
    branch_status = "report_only" if branch else "host_managed_without_local_branch"
    pr_status = "report_only"
    worktree_status = "host_managed"
    missing_inputs: list[str] = []
    if worktree_root is None:
        worktree_observation = "current process is outside the target repository"
    else:
        worktree_observation = worktree_root
    if any(message.startswith("branch purity") for message in purity["report_only"]):
        branch_next = "keep branch lifecycle on the host platform; Loom only reports purity and closeout dependencies."
    else:
        branch_next = "branch lifecycle remains host-managed."
    return {
        "command": "host-lifecycle",
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "result": "pass",
        "summary": "workspace is Loom-managed; branch, PR, and git worktree lifecycles remain host-managed with explicit boundary checks.",
        "missing_inputs": missing_inputs,
        "fallback_to": None,
        "objects": {
            "workspace": {
                "ownership": "loom",
                "entry": context["workspace_entry"],
                "path": relative_to_root(context["workspace_path"], context["target_root"]),
                "profile": workspace_profile,
                "lifecycle_entry": "python3 .loom/bin/loom_flow.py workspace create|locate|attach|cleanup|retire",
                "lifecycle_expectations": lifecycle_expectations,
            },
            "branch": {
                "ownership": "host",
                "current_branch": branch,
                "purity_status": branch_status,
                "next_action": branch_next,
            },
            "pr": {
                "ownership": "host",
                "purity_status": pr_status,
                "next_action": "use host PR lifecycle; Loom only consumes PR template, required checks, and closeout sync state.",
            },
            "worktree": {
                "ownership": "host",
                "cwd_within_repo": worktree_observation,
                "next_action": "Loom models execution workspace semantics and does not create or retire git worktrees itself.",
                "status": worktree_status,
            },
        },
        "purity": purity,
        "lifecycle_expectations": lifecycle_expectations,
    }

def governance_profile_payload(target_root: Path, operation: str, *, host: str = "github") -> dict[str, Any]:
    governance_surface = build_governance_surface(target_root)
    control_plane = governance_surface.get("governance_control_plane")
    maturity = control_plane.get("maturity") if isinstance(control_plane, dict) else None
    if not isinstance(maturity, dict):
        return {
            "command": "governance-profile",
            "operation": operation,
            "host": host,
            "result": "block",
            "summary": "governance profile maturity could not be read from the unified control plane.",
            "missing_inputs": ["governance_control_plane.maturity"],
            "fallback_to": "admission",
            "governance_surface": governance_surface,
        }

    current = maturity.get("current")
    next_level = maturity.get("next")
    target_level = next_level if isinstance(next_level, str) else current if isinstance(current, str) else None
    gate_rollout = maturity.get("gate_rollout")
    workspace_profile = control_plane.get("workspace_profile") if isinstance(control_plane, dict) else None
    gate_starter = control_plane.get("gate_starter") if isinstance(control_plane, dict) else None
    github_control_plane = governance_surface.get("github_control_plane")
    ci_check_presence = (
        github_control_plane.get("ci_check_presence")
        if isinstance(github_control_plane, dict)
        else None
    )
    host_enforcement = (
        github_control_plane.get("host_enforcement")
        if isinstance(github_control_plane, dict)
        else None
    )
    host_governance_capability = (
        github_control_plane.get("host_governance_capability")
        if isinstance(github_control_plane, dict)
        else None
    )
    api_snapshot = (
        github_control_plane.get("api_snapshot")
        if isinstance(github_control_plane, dict)
        else None
    )
    host_verification_status = (
        api_snapshot.get("verification_status")
        if isinstance(api_snapshot, dict)
        else "unverified"
    )
    missing_by_level = maturity.get("missing_by_level")
    missing_details_by_level = maturity.get("missing_details_by_level")
    missing_inputs: list[Any] = []
    missing_details: list[Any] = []
    if operation == "upgrade-plan" and isinstance(next_level, str) and isinstance(missing_by_level, dict):
        raw_missing = missing_by_level.get(next_level, [])
        if isinstance(raw_missing, list):
            missing_inputs = raw_missing
        if isinstance(missing_details_by_level, dict):
            raw_details = missing_details_by_level.get(next_level, [])
            if isinstance(raw_details, list):
                missing_details = raw_details
    result = "pass" if not missing_inputs else "block"
    summary = (
        f"governance profile is already at `{current}` maturity."
        if operation == "status" or result == "pass"
        else f"governance profile can upgrade toward `{next_level}` after the missing contracts are installed."
    )
    decisions = adoption_decisions_payload(target_root, target_level=target_level, maturity=maturity)
    guided_plan = guided_adoption_plan_payload(decisions)
    generation = companion_generation_payload(target_root, decisions, dry_run=True)
    return {
        "command": "governance-profile",
        "operation": operation,
        "host": host,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "missing_details": missing_details,
        "recommended_action": "run governance-profile upgrade --dry-run" if result == "block" else None,
        "fallback_to": None if result == "pass" else "adoption",
        "maturity": maturity,
        "workspace_profile": workspace_profile,
        "gate_starter": gate_starter,
        "ci_check_presence": ci_check_presence,
        "host_enforcement": host_enforcement,
        "host_governance_capability": host_governance_capability,
        "host_verification_status": host_verification_status,
        "gate_rollout": gate_rollout,
        "governance_control_plane": control_plane,
        "adoption_decisions": decisions,
        "guided_adoption_plan": guided_plan,
        "companion_generation": generation,
    }

def governance_upgrade_actions(target_root: Path, target_level: str, maturity: dict[str, Any]) -> list[dict[str, Any]]:
    missing_by_level = maturity.get("missing_by_level")
    missing_details_by_level = maturity.get("missing_details_by_level")
    missing = missing_by_level.get(target_level, []) if isinstance(missing_by_level, dict) else []
    missing_details = missing_details_by_level.get(target_level, []) if isinstance(missing_details_by_level, dict) else []
    actions: list[dict[str, Any]] = []
    for relative, content in UPGRADE_SCAFFOLD.items():
        path = target_root / relative
        owner = "loom-owned" if relative.startswith(".loom/") else "repo-owned"
        actions.append(
            {
                "action": "write_scaffold" if not path.exists() else "keep_existing",
                "path": relative,
                "owner": owner,
                "status": "present" if path.exists() else "planned",
                "reason": "required by governance profile upgrade path",
                "bytes": len(content.encode("utf-8")),
            }
        )
    for item in missing if isinstance(missing, list) else []:
        detail = next((row for row in missing_details if isinstance(row, dict) and row.get("id") == item), {})
        actions.append(
            {
                "action": "satisfy_missing_input",
                "id": item,
                "owner": (
                    "loom-owned"
                    if str(item) in {"repo_interface", "repo_interop"}
                    else "profile"
                ),
                "status": "planned",
                "layer": detail.get("layer"),
                "recommended_action": detail.get("recommended_action"),
                "reason": f"`{target_level}` maturity currently reports this missing input.",
            }
        )
    return actions

def governance_profile_upgrade_payload(
    *,
    target_root: Path,
    target_level: str | None,
    dry_run: bool,
    force: bool,
    host: str = "github",
) -> dict[str, Any]:
    if target_level is None:
        return {
            "command": "governance-profile",
            "operation": "upgrade",
            "host": host,
            "result": "block",
            "summary": "governance profile upgrade requires `--to standard` or `--to strong`.",
            "missing_inputs": ["to"],
            "fallback_to": "adoption",
        }
    base = governance_profile_payload(target_root, "upgrade-plan", host=host)
    maturity = base.get("maturity") if isinstance(base.get("maturity"), dict) else {}
    workspace_profile = base.get("workspace_profile")
    gate_starter = base.get("gate_starter")
    ci_check_presence = base.get("ci_check_presence")
    host_enforcement = base.get("host_enforcement")
    host_verification_status = base.get("host_verification_status")
    actions = governance_upgrade_actions(target_root, target_level, maturity if isinstance(maturity, dict) else {})
    blockers: list[str] = []
    written_files: list[str] = []
    decisions = adoption_decisions_payload(target_root, target_level=target_level, maturity=maturity if isinstance(maturity, dict) else {})
    if not dry_run:
        written_files, companion_blockers = apply_companion_generation(target_root, force=force)
        blockers.extend(companion_blockers)
    result = "block" if blockers else "pass"
    guided_plan = guided_adoption_plan_payload(decisions)
    generation = companion_generation_payload(
        target_root,
        decisions,
        dry_run=dry_run,
        written_files=written_files,
        blockers=blockers,
    )
    return {
        "command": "governance-profile",
        "operation": "upgrade",
        "host": host,
        "schema_version": "loom-governance-upgrade/v1",
        "result": result,
        "summary": (
            f"governance profile upgrade toward `{target_level}` produced a dry-run action plan."
            if dry_run and result == "pass"
            else f"governance profile upgrade toward `{target_level}` applied Loom-owned scaffold writes."
            if result == "pass"
            else f"governance profile upgrade toward `{target_level}` is blocked by unsafe writes."
        ),
        "missing_inputs": blockers,
        "fallback_to": None if result == "pass" else "adoption",
        "target_maturity": target_level,
        "dry_run": dry_run,
        "force": force,
        "actions": actions,
        "written_files": written_files,
        "maturity": maturity,
        "workspace_profile": workspace_profile,
        "gate_starter": gate_starter,
        "ci_check_presence": ci_check_presence,
        "host_enforcement": host_enforcement,
        "host_verification_status": host_verification_status,
        "gate_rollout": maturity.get("gate_rollout") if isinstance(maturity, dict) else None,
        "adoption_decisions": decisions,
        "guided_adoption_plan": guided_plan,
        "companion_generation": generation,
    }

def native_dependency_capability_for_args(
    target_root: Path,
    *,
    owner: str | None,
    repo_name: str | None,
    issue_number: int | None,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    if not owner or not repo_name or issue_number is None:
        return {
            "status": "unverified",
            "read": False,
            "write": False,
            "reason": "owner/repo and --issue are required to verify native dependency capability.",
        }
    return github_native_dependency_capability(target_root, owner, repo_name, issue_number)

def native_dependency_upgrade_plan_payload() -> dict[str, str]:
    return {
        "read": "query GitHub issue blockedBy/blocking before resume, merge-ready, and closeout.",
        "judge": "treat native dependencies as host mirror and compare with issue/repo-authored dependency truth.",
        "write": "generate dry-run addBlockedBy/removeBlockedBy actions only from mechanical proof.",
        "verify": "re-read blockedBy/blocking after any approved host sync.",
    }

def issue_binding_entry(
    role: str,
    number: int | None,
    payload: dict[str, Any] | None,
    errors: list[str],
    *,
    closing_pull_requests: list[dict[str, Any]] | None = None,
    closing_pull_request_errors: list[str] | None = None,
) -> dict[str, Any]:
    status = "present" if payload is not None else "missing"
    if errors:
        status = "unreadable"
    entry = {
        "role": role,
        "number": number,
        "status": status,
        "state": payload.get("state") if payload else None,
        "title": payload.get("title") if payload else None,
        "url": payload.get("url") if payload else None,
        "closedAt": payload.get("closedAt") if payload else None,
        "errors": errors,
    }
    if closing_pull_requests is not None:
        entry["closingPullRequests"] = closing_pull_requests
    if closing_pull_request_errors:
        entry["closingPullRequestErrors"] = closing_pull_request_errors
    return entry

def normalize_closing_pr_reference(payload: dict[str, Any]) -> dict[str, Any]:
    merge_commit = payload.get("mergeCommit") if isinstance(payload.get("mergeCommit"), dict) else None
    return {
        "number": payload.get("number"),
        "state": payload.get("state"),
        "title": payload.get("title"),
        "url": payload.get("url"),
        "mergedAt": payload.get("mergedAt"),
        "baseRefName": payload.get("baseRefName"),
        "headRefName": payload.get("headRefName"),
        "mergeCommit": {"oid": merge_commit.get("oid")} if isinstance(merge_commit, dict) and merge_commit.get("oid") else None,
    }

def github_issue_closing_pull_requests_graphql(root: Path, owner: str, repo_name: str, issue_number: int) -> tuple[list[dict[str, Any]], list[str]]:
    query = """
    query($owner: String!, $repo: String!, $issue: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issue) {
          closedByPullRequestsReferences(first: 10) {
            nodes {
              number
              state
              title
              url
              mergedAt
              baseRefName
              headRefName
              mergeCommit { oid }
            }
          }
        }
      }
    }
    """
    payload, errors = gh_graphql(root, query, {"owner": owner, "repo": repo_name, "issue": issue_number})
    if errors or payload is None:
        return [], errors
    issue = payload.get("repository", {}).get("issue") if isinstance(payload.get("repository"), dict) else None
    if not isinstance(issue, dict):
        return [], [f"GitHub issue #{issue_number} closing PR query returned no issue"]
    refs = issue.get("closedByPullRequestsReferences") if isinstance(issue.get("closedByPullRequestsReferences"), dict) else {}
    nodes = refs.get("nodes") if isinstance(refs.get("nodes"), list) else []
    return [normalize_closing_pr_reference(node) for node in nodes if isinstance(node, dict)], []

def github_binding_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    phase_number: int | None,
    fr_number: int | None,
    issue_number: int | None,
    pr_number: int | None,
    branch_name: str | None,
    sync: bool,
    dry_run: bool,
    require_complete_chain: bool = True,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    missing_inputs: list[str] = []
    findings: list[dict[str, Any]] = []
    repair_plan: list[dict[str, Any]] = []

    if not owner or not repo_name:
        missing_inputs.append("owner/repo")
    if issue_number is None:
        missing_inputs.append("work_item issue")
    if sync and not dry_run:
        missing_inputs.append("dry-run")
        findings.append(
            {
                "category": "gate_failure",
                "kind": "binding_failure",
                "severity": "block",
                "subject": "governance-profile binding sync",
                "why_blocking": "binding sync is read-only in this phase unless --dry-run is set.",
                "fallback_to": "github-profile-binding",
                "evidence": {"sync": sync, "dry_run": dry_run},
            }
        )

    phase_payload: dict[str, Any] | None = None
    fr_payload: dict[str, Any] | None = None
    issue_payload: dict[str, Any] | None = None
    pr_payload: dict[str, Any] | None = None
    branch_payload: dict[str, Any] | None = None
    phase_errors: list[str] = []
    fr_errors: list[str] = []
    issue_errors: list[str] = []
    pr_errors: list[str] = []
    branch_errors: list[str] = []
    closing_pull_requests: list[dict[str, Any]] = []
    closing_pull_request_errors: list[str] = []

    if owner and repo_name:
        if phase_number is not None:
            phase_payload, phase_errors = github_issue_payload(target_root, owner, repo_name, phase_number)
            missing_inputs.extend(f"phase: {message}" for message in phase_errors)
        if fr_number is not None:
            fr_payload, fr_errors = github_issue_payload(target_root, owner, repo_name, fr_number)
            missing_inputs.extend(f"fr: {message}" for message in fr_errors)
        if issue_number is not None:
            issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
            missing_inputs.extend(f"work_item: {message}" for message in issue_errors)
        if pr_number is not None:
            pr_payload, pr_errors = github_pr_payload(target_root, owner, repo_name, pr_number)
            missing_inputs.extend(f"pr: {message}" for message in pr_errors)
        if issue_payload is not None and issue_payload.get("state") == "CLOSED" and issue_number is not None:
            closing_pull_requests, closing_pull_request_errors = github_issue_closing_pull_requests_graphql(target_root, owner, repo_name, issue_number)

    inferred_branch = branch_name
    if inferred_branch is None and pr_payload is not None and isinstance(pr_payload.get("headRefName"), str):
        inferred_branch = pr_payload.get("headRefName")
    if owner and repo_name and inferred_branch:
        branch_payload, branch_errors = github_branch_payload(target_root, owner, repo_name, inferred_branch)
        missing_inputs.extend(f"branch: {message}" for message in branch_errors)

    if issue_payload is not None and pr_payload is not None:
        pr_body = pr_payload.get("body")
        if not text_mentions_issue(pr_body, int(issue_payload.get("number") or issue_number or 0)):
            findings.append(
                {
                    "category": "gate_failure",
                    "kind": "binding_failure",
                    "severity": "block",
                    "subject": f"PR #{pr_number} -> Work Item #{issue_number}",
                    "why_blocking": "implementation PR body does not mention the Work Item issue.",
                    "fallback_to": "github-profile-binding",
                    "evidence": {
                        "pr_number": pr_number,
                        "issue_number": issue_number,
                        "expected_reference": f"#{issue_number}",
                    },
                }
            )
            repair_plan.append(
                {
                    "action": "update_pr_body",
                    "subject": f"PR #{pr_number}",
                    "body_append": f"\n\nRelated Work\n\n- Closes #{issue_number}\n",
                    "mode": "dry-run" if dry_run else "not-applied",
                }
            )
    if issue_payload is not None and fr_payload is not None and not text_mentions_issue(issue_payload.get("body"), int(fr_number or 0)):
        findings.append(
            {
                "category": "gate_failure",
                "kind": "binding_failure",
                "severity": "block",
                "subject": f"Work Item #{issue_number} -> FR #{fr_number}",
                "why_blocking": "Work Item issue body does not mention the FR issue.",
                "fallback_to": "github-profile-binding",
                "evidence": {"work_item": issue_number, "fr": fr_number, "expected_reference": f"#{fr_number}"},
            }
        )
    if fr_payload is not None and phase_payload is not None and not text_mentions_issue(fr_payload.get("body"), int(phase_number or 0)):
        findings.append(
            {
                "category": "gate_failure",
                "kind": "binding_failure",
                "severity": "block",
                "subject": f"FR #{fr_number} -> Phase #{phase_number}",
                "why_blocking": "FR issue body does not mention the Phase issue.",
                "fallback_to": "github-profile-binding",
                "evidence": {"fr": fr_number, "phase": phase_number, "expected_reference": f"#{phase_number}"},
            }
        )

    merge_commit = pr_payload.get("mergeCommit") if isinstance(pr_payload, dict) else None
    merge_commit_sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
    target_branch = pr_payload.get("baseRefName") if isinstance(pr_payload, dict) else None
    binding = {
        "schema_version": "loom-github-binding/v1",
        "repository": {"owner": owner, "name": repo_name},
        "objects": {
            "phase": issue_binding_entry("phase", phase_number, phase_payload, phase_errors),
            "fr": issue_binding_entry("fr", fr_number, fr_payload, fr_errors),
            "work_item": issue_binding_entry(
                "work_item",
                issue_number,
                issue_payload,
                issue_errors,
                closing_pull_requests=closing_pull_requests if issue_payload is not None and issue_payload.get("state") == "CLOSED" else None,
                closing_pull_request_errors=closing_pull_request_errors,
            ),
            "branch": {
                "role": "branch",
                "name": inferred_branch,
                "status": "present" if branch_payload is not None else ("unreadable" if branch_errors else "missing"),
                "head_sha": branch_payload.get("commit", {}).get("sha") if isinstance(branch_payload, dict) and isinstance(branch_payload.get("commit"), dict) else None,
                "errors": branch_errors,
            },
            "implementation_pr": {
                "role": "implementation_pr",
                "number": pr_number,
                "status": "present" if pr_payload is not None else ("unreadable" if pr_errors else "missing"),
                "state": pr_payload.get("state") if pr_payload else None,
                "isDraft": pr_payload.get("isDraft") if pr_payload else None,
                "headRefName": pr_payload.get("headRefName") if pr_payload else None,
                "baseRefName": pr_payload.get("baseRefName") if pr_payload else None,
                "url": pr_payload.get("url") if pr_payload else None,
                "errors": pr_errors,
            },
            "merge_commit": {
                "role": "merge_commit",
                "sha": merge_commit_sha,
                "status": "present" if merge_commit_sha else "missing",
            },
            "target_branch": {
                "role": "target_branch",
                "name": target_branch,
                "status": "present" if target_branch else "missing",
            },
        },
        "chain": [
            {"from": "phase", "to": "fr", "status": "present" if phase_payload and fr_payload else "missing"},
            {"from": "fr", "to": "work_item", "status": "present" if fr_payload and issue_payload else "missing"},
            {"from": "work_item", "to": "implementation_pr", "status": "present" if issue_payload and pr_payload else "missing"},
            {"from": "implementation_pr", "to": "merge_commit", "status": "present" if merge_commit_sha else "missing"},
            {"from": "merge_commit", "to": "target_branch", "status": "present" if merge_commit_sha and target_branch else "missing"},
        ],
        "findings": findings,
        "repair_plan": repair_plan if sync or dry_run else [],
    }
    if require_complete_chain:
        chain_complete = all(entry.get("status") == "present" for entry in binding["chain"])
    else:
        required_edges = []
        if issue_number is not None and pr_number is not None:
            required_edges.append(("work_item", "implementation_pr"))
        if pr_number is not None and pr_payload is not None and pr_payload.get("state") == "MERGED":
            required_edges.extend([("implementation_pr", "merge_commit"), ("merge_commit", "target_branch")])
        chain_complete = all(
            entry.get("status") == "present"
            for entry in binding["chain"]
            if (entry.get("from"), entry.get("to")) in required_edges
        )
    if not chain_complete and "binding_chain" not in missing_inputs:
        missing_inputs.append("binding_chain")
    result = "pass" if not missing_inputs and not findings and chain_complete else "block"
    return {
        "command": "governance-profile",
        "operation": "binding",
        "schema_version": "loom-github-binding/v1",
        "result": result,
        "summary": (
            "GitHub profile binding chain is readable."
            if result == "pass"
            else "GitHub profile binding chain is incomplete or inconsistent."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "github-profile-binding",
        "binding": binding,
    }

def handle_governance_profile(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    if args.operation == "upgrade":
        payload = governance_profile_upgrade_payload(
            target_root=target_root,
            target_level=args.to,
            dry_run=args.dry_run,
            force=args.force,
            host=args.host,
        )
        payload["native_dependency_capability"] = native_dependency_capability_for_args(
            target_root,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
        )
        payload["native_dependency_upgrade_plan"] = native_dependency_upgrade_plan_payload()
        return emit(payload)
    if args.operation == "binding":
        return emit(
            github_binding_payload(
                target_root=target_root,
                owner=args.owner,
                repo_name=args.repo_name,
                phase_number=args.phase,
                fr_number=args.fr,
                issue_number=args.issue,
                pr_number=args.pr,
                branch_name=args.branch,
                sync=args.sync,
                dry_run=args.dry_run,
            )
        )
    payload = governance_profile_payload(target_root, args.operation, host=args.host)
    payload["native_dependency_capability"] = native_dependency_capability_for_args(
        target_root,
        owner=args.owner,
        repo_name=args.repo_name,
        issue_number=args.issue,
    )
    payload["native_dependency_upgrade_plan"] = native_dependency_upgrade_plan_payload()
    return emit(payload)

def handle_host_lifecycle(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "host-lifecycle",
                "result": "block",
                "summary": "host-lifecycle could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )
    return emit(host_lifecycle_payload(context))

def project_status_context(root: Path, owner: str, project_number: int) -> tuple[dict[str, Any], list[str]]:
    project_view, view_errors = gh_json(root, ["project", "view", str(project_number), "--owner", owner, "--format", "json"])
    if view_errors or project_view is None:
        return {}, view_errors
    field_list_payload, field_errors = gh_json(root, ["project", "field-list", str(project_number), "--owner", owner, "--format", "json"])
    if field_errors or field_list_payload is None:
        return {}, field_errors
    fields = field_list_payload.get("fields")
    if not isinstance(fields, list):
        return {}, ["project field list is missing `fields`"]
    status_field_id: str | None = None
    done_option_id: str | None = None
    for field in fields:
        if not isinstance(field, dict):
            continue
        if field.get("name") != "Status":
            continue
        status_field_id = str(field.get("id"))
        options = field.get("options")
        if isinstance(options, list):
            for option in options:
                if isinstance(option, dict) and option.get("name") == "Done":
                    done_option_id = str(option.get("id"))
    project_id = project_view.get("id")
    if not isinstance(project_id, str) or not project_id:
        return {}, ["project view is missing `id`"]
    if not status_field_id or not done_option_id:
        return {}, ["project is missing a `Status` field with a `Done` option"]
    item_list = run_process(["gh", "project", "item-list", str(project_number), "--owner", owner, "--format", "json"], root)
    if item_list.returncode != 0:
        detail = item_list.stderr.strip() or item_list.stdout.strip() or "gh project item-list failed"
        return {}, [detail]
    try:
        payload = json.loads(item_list.stdout)
    except json.JSONDecodeError as exc:
        return {}, [f"invalid JSON from gh project item-list: {exc.msg}"]
    items = payload.get("items")
    if not isinstance(items, list):
        return {}, ["project item list is missing `items`"]
    return {
        "project_id": project_id,
        "status_field_id": status_field_id,
        "done_option_id": done_option_id,
        "items": items,
    }, []

def find_project_item(items: list[dict[str, Any]], number: int, kind: str) -> dict[str, Any] | None:
    for item in items:
        content = item.get("content")
        if not isinstance(content, dict):
            continue
        if content.get("number") != number:
            continue
        item_type = content.get("type")
        if kind == "issue" and item_type == "Issue":
            return item
        if kind == "pr" and item_type == "PullRequest":
            return item
    return None

def project_item_for_issue(root: Path, issue_id: str, project_number: int) -> tuple[dict[str, Any] | None, list[str]]:
    # GraphQL-only for now: GitHub ProjectV2 item field values are not covered by the REST budget-hardening pass.
    query = """
query($id: ID!) {
  node(id: $id) {
    ... on Issue {
      projectItems(first: 50) {
        nodes {
          id
          project {
            number
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
                name
              }
            }
          }
        }
      }
    }
  }
}
"""
    data, errors = gh_graphql(root, query, {"id": issue_id})
    if errors or data is None:
        return None, errors
    node = data.get("node")
    if not isinstance(node, dict):
        return None, ["issue graphql payload is missing `node`"]
    project_items = node.get("projectItems")
    if not isinstance(project_items, dict):
        return None, ["issue graphql payload is missing `projectItems`"]
    nodes = project_items.get("nodes")
    if not isinstance(nodes, list):
        return None, ["issue graphql payload is missing `projectItems.nodes`"]
    for entry in nodes:
        if not isinstance(entry, dict):
            continue
        project = entry.get("project")
        if not isinstance(project, dict) or project.get("number") != project_number:
            continue
        status_name = None
        field_values = entry.get("fieldValues")
        if isinstance(field_values, dict):
            values = field_values.get("nodes")
            if isinstance(values, list):
                for value in values:
                    if not isinstance(value, dict):
                        continue
                    field = value.get("field")
                    if isinstance(field, dict) and field.get("name") == "Status":
                        name = value.get("name")
                        if isinstance(name, str) and name:
                            status_name = name
        return {
            "id": entry.get("id"),
            "content": {"number": None, "type": "Issue"},
            "status": status_name,
            "budget_guard": graphql_budget_guard("project_v2_item_field_values"),
        }, []
    return None, []

def set_project_item_done(root: Path, project_id: str, item_id: str, status_field_id: str, done_option_id: str) -> list[str]:
    result = run_process(
        [
            "gh",
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            project_id,
            "--field-id",
            status_field_id,
            "--single-select-option-id",
            done_option_id,
        ],
        root,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh project item-edit failed"
        return [detail]
    return []

def set_native_dependency(root: Path, owner: str, repo_name: str, issue_number: int, blocking_issue_number: int, mutation: str) -> list[str]:
    if mutation not in {"addBlockedBy", "removeBlockedBy"}:
        return [f"unsupported native dependency mutation `{mutation}`"]
    query = """
query($owner:String!, $name:String!, $issue:Int!, $blockingIssue:Int!) {
  repository(owner:$owner, name:$name) {
    issue(number:$issue) { id }
    blockingIssue: issue(number:$blockingIssue) { id }
  }
}
"""
    data, errors = gh_graphql_json(
        root,
        query,
        {"owner": owner, "name": repo_name, "issue": issue_number, "blockingIssue": blocking_issue_number},
    )
    if errors or data is None:
        return errors or ["GitHub native dependency issue id readback failed"]
    repo = data.get("repository") if isinstance(data.get("repository"), dict) else {}
    issue = repo.get("issue") if isinstance(repo.get("issue"), dict) else {}
    blocking_issue = repo.get("blockingIssue") if isinstance(repo.get("blockingIssue"), dict) else {}
    issue_id = issue.get("id")
    blocking_issue_id = blocking_issue.get("id")
    if not isinstance(issue_id, str) or not isinstance(blocking_issue_id, str):
        return [f"GitHub native dependency mutation missing issue ids for #{issue_number} blocked by #{blocking_issue_number}"]
    mutation_query = f"""
mutation($issueId:ID!, $blockingIssueId:ID!, $clientMutationId:String!) {{
  {mutation}(input:{{issueId:$issueId, blockingIssueId:$blockingIssueId, clientMutationId:$clientMutationId}}) {{
    clientMutationId
  }}
}}
"""
    client_mutation_id = f"loom-reconciliation-{mutation}-{issue_number}-{blocking_issue_number}"
    _, mutation_errors = gh_graphql_json(
        root,
        mutation_query,
        {"issueId": issue_id, "blockingIssueId": blocking_issue_id, "clientMutationId": client_mutation_id},
    )
    return mutation_errors

def issue_tree_payload(root: Path, owner: str, repo_name: str, issue_number: int) -> tuple[dict[str, Any] | None, list[str]]:
    # GraphQL-only for now: native parent/sub-issue tree shape is outside the high-frequency REST replacement scope.
    query = """
query($owner:String!, $name:String!, $number:Int!) {
  repository(owner:$owner, name:$name) {
    issue(number:$number) {
      id
      number
      title
      state
      url
      parent {
        id
        number
        title
        state
        url
        subIssues(first:100) {
          totalCount
          pageInfo { hasNextPage }
          nodes {
            id
            number
            title
            body
            state
            url
            labels(first:20) { nodes { name } }
          }
        }
      }
      subIssues(first:100) {
        totalCount
        pageInfo { hasNextPage }
        nodes {
          id
          number
          title
          body
          state
          url
          labels(first:20) { nodes { name } }
        }
      }
    }
  }
}
"""
    data, errors = gh_graphql_json(root, query, {"owner": owner, "name": repo_name, "number": issue_number})
    if errors or data is None:
        return None, errors
    repository = data.get("repository")
    if not isinstance(repository, dict):
        return None, ["issue tree graphql payload is missing `repository`"]
    issue = repository.get("issue")
    if not isinstance(issue, dict):
        return None, [f"issue #{issue_number} is missing from GraphQL payload"]
    issue["budget_guard"] = graphql_budget_guard("native_parent_sub_issue_tree")
    return issue, []

def github_fr_wi_admission_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int,
    intent: str,
    task: str | None,
    blocked_by: list[int],
    work_item_number: int | None,
    apply: bool,
    lifecycle_only: bool = False,
) -> dict[str, Any]:
    """Delegate host-native admission to the focused policy module."""
    from types import SimpleNamespace

    module_dir = str(Path(str(FLOW_ENTRYPOINT)).resolve().parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    from github_admission import github_fr_wi_admission_payload as evaluate_admission

    host = SimpleNamespace(
        detect_github_repo=detect_github_repo,
        github_issue_payload=github_issue_payload,
        build_governance_surface=build_governance_surface,
        github_intake_object_type=github_intake_object_type,
        normalize_taxonomy_match_text=normalize_taxonomy_match_text,
        normalized_issue_labels=normalized_issue_labels,
        github_intake_taxonomy_mapping=github_intake_taxonomy_mapping,
        issue_tree_payload=issue_tree_payload,
        gh_graphql_json=gh_graphql_json,
        gh_rest_write_json=gh_rest_write_json,
        normalize_rest_issue=normalize_rest_issue,
        github_issue_dependencies_payload=github_issue_dependencies_payload,
        set_native_dependency=set_native_dependency,
    )
    return evaluate_admission(
        host=host,
        target_root=target_root,
        owner=owner,
        repo_name=repo_name,
        issue_number=issue_number,
        intent=intent,
        task=task,
        blocked_by=blocked_by,
        work_item_number=work_item_number,
        apply=apply,
        lifecycle_only=lifecycle_only,
    )

def project_drift_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int | None,
    pr_number: int | None,
    project_number: int | None,
    mode: str = "advisory",
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    missing_inputs: list[str] = []
    findings: list[dict[str, Any]] = []
    project_payload: dict[str, Any] | None = None
    issue_payload: dict[str, Any] | None = None
    pr_payload: dict[str, Any] | None = None
    dependency_graph: dict[str, Any] | None = None

    if project_number is None:
        return {
            "schema_version": PROJECT_DRIFT_SCHEMA,
            "result": "pass",
            "mode": mode,
            "summary": "Project drift read is not applicable because no Project number was provided.",
            "missing_inputs": [],
            "fallback_to": None,
            "project": None,
            "dependency_drift": None,
            "findings": [],
            "provenance": [],
        }
    if not owner or not repo_name:
        missing_inputs.append("owner/repo")
    if owner and repo_name and issue_number is not None:
        issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
        missing_inputs.extend(f"issue: {message}" for message in issue_errors)
        native_dependencies = github_issue_dependencies_payload(target_root, owner, repo_name, issue_number)
        dependency_graph = dependency_graph_payload(
            issue_number=issue_number,
            issue_payload=issue_payload,
            native_dependency_payload=native_dependencies,
        )
        for finding in dependency_graph.get("findings", []):
            if not isinstance(finding, dict):
                continue
            kind = str(finding.get("kind"))
            if kind in {"missing_native_edge", "unexpected_native_edge"}:
                findings.append({**finding, "drift_kind": kind})
            if kind == "open_blocker_executable_conflict":
                findings.append({**finding, "drift_kind": "open_blocker_executable_conflict"})
    if owner and repo_name and pr_number is not None:
        pr_payload, pr_errors = github_pr_payload(target_root, owner, repo_name, pr_number)
        missing_inputs.extend(f"pr: {message}" for message in pr_errors)
    if owner:
        project_context, project_errors = project_status_context(target_root, owner, project_number)
        if project_errors:
            findings.append(
                {
                    "category": "drift",
                    "kind": "project_unreadable",
                    "drift_kind": "project_unreadable",
                    "severity": "block" if mode == "blocking" else "warn",
                    "subject": f"Project #{project_number}",
                    "evidence": {"errors": project_errors},
                    "fallback_to": "manual-reconciliation",
                }
            )
        else:
            items = project_context["items"]
            issue_item = find_project_item(items, issue_number, "issue") if issue_number is not None else None
            pr_item = find_project_item(items, pr_number, "pr") if pr_number is not None else None
            project_payload = {
                "number": project_number,
                "project_id": project_context["project_id"],
                "status_field_id": project_context["status_field_id"],
                "done_option_id": project_context["done_option_id"],
                "issue_item": issue_item,
                "pr_item": pr_item,
            }
            if issue_number is not None and issue_item is None:
                findings.append(
                    {
                        "category": "drift",
                        "kind": "project_missing_item",
                        "drift_kind": "project_missing_item",
                        "severity": "block" if mode == "blocking" else "warn",
                        "subject": f"issue #{issue_number}",
                        "evidence": {"project": project_number},
                        "fallback_to": "manual-reconciliation",
                    }
                )
            for label, item, payload in (("issue", issue_item, issue_payload), ("pr", pr_item, pr_payload)):
                if item is None:
                    continue
                status = item.get("status")
                expected_done = False
                subject_number = None
                if isinstance(payload, dict):
                    subject_number = payload.get("number")
                    if label == "issue":
                        expected_done = payload.get("state") == "CLOSED"
                    if label == "pr":
                        expected_done = payload.get("state") == "MERGED"
                if expected_done and status != "Done":
                    findings.append(
                        {
                            "category": "drift",
                            "kind": "project_status_mismatch",
                            "drift_kind": "project_status_mismatch",
                            "severity": "block" if mode == "blocking" else "warn",
                            "subject": f"{label} #{subject_number or 'unknown'}",
                            "evidence": {"expected_status": "Done", "actual_status": status},
                            "fallback_to": "manual-reconciliation",
                        }
                    )
                if not expected_done and status == "Done":
                    findings.append(
                        {
                            "category": "drift",
                            "kind": "project_stale_mirror",
                            "drift_kind": "project_stale_mirror",
                            "severity": "block" if mode == "blocking" else "warn",
                            "subject": f"{label} #{subject_number or 'unknown'}",
                            "evidence": {"expected_done": False, "actual_status": status},
                            "fallback_to": "manual-reconciliation",
                        }
                    )
    blocking = [finding for finding in findings if finding.get("severity") == "block"]
    result = "block" if blocking or missing_inputs else "pass"
    return {
        "schema_version": PROJECT_DRIFT_SCHEMA,
        "result": result,
        "mode": mode,
        "summary": (
            "Project drift read found no blocking Project or dependency drift."
            if result == "pass"
            else "Project drift read found Project or dependency drift that must be reconciled."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "manual-reconciliation",
        "project": project_payload,
        "dependency_drift": dependency_graph,
        "findings": findings,
        "provenance": [
            {
                "source_layer": "host_control_mirror",
                "source_owner": "github_project",
                "source_locator": f"Project #{project_number}",
                "freshness": "fresh" if not missing_inputs else "unreadable",
            }
        ],
    }

def normalize_taxonomy_match_text(value: Any) -> str:
    return str(value or "").strip().lower()

def normalized_issue_labels(issue_payload: dict[str, Any] | None) -> set[str]:
    if not isinstance(issue_payload, dict):
        return set()
    raw_labels = issue_payload.get("labels")
    if isinstance(raw_labels, dict):
        raw_labels = raw_labels.get("nodes")
    if not isinstance(raw_labels, list):
        return set()
    labels: set[str] = set()
    for label in raw_labels:
        if isinstance(label, dict):
            label = label.get("name")
        normalized = normalize_taxonomy_match_text(label)
        if normalized:
            labels.add(normalized)
    return labels

def github_intake_taxonomy_mapping(repo_interface: dict[str, Any] | None) -> tuple[list[dict[str, Any]], str, str]:
    if not isinstance(repo_interface, dict):
        return [], "advisory_unknown", "absent"
    taxonomy = repo_interface.get("host_planning_taxonomy")
    if not isinstance(taxonomy, dict) or taxonomy.get("availability") != "present":
        return [], "advisory_unknown", str(taxonomy.get("availability") if isinstance(taxonomy, dict) else "absent")
    raw_policy = taxonomy.get("missing_type_policy")
    policy = raw_policy if isinstance(raw_policy, str) and raw_policy in HOST_PLANNING_MISSING_TYPE_POLICIES else "advisory_unknown"
    mappings = [
        mapping
        for mapping in taxonomy.get("object_type_mapping", [])
        if isinstance(mapping, dict) and mapping.get("loom_type") in {"phase", "fr", "work_item"}
    ]
    return mappings, policy, "present"

def github_intake_object_type_match(
    issue_payload: dict[str, Any] | None,
    mappings: list[dict[str, Any]],
) -> tuple[str, str]:
    if not isinstance(issue_payload, dict):
        return "unknown", "unreadable_issue"
    labels = normalized_issue_labels(issue_payload)
    title = normalize_taxonomy_match_text(issue_payload.get("title"))
    for source, mapping_group in (("repo_companion", mappings), ("loom_default", list(DEFAULT_GITHUB_INTAKE_OBJECT_TYPE_MAPPINGS))):
        for mapping in mapping_group:
            loom_type = mapping.get("loom_type")
            mapping_labels = {
                normalize_taxonomy_match_text(label)
                for label in mapping.get("labels", [])
                if normalize_taxonomy_match_text(label)
            }
            if labels and mapping_labels and labels.intersection(mapping_labels):
                return str(loom_type), source
            for prefix in mapping.get("title_prefixes", []):
                normalized_prefix = normalize_taxonomy_match_text(prefix)
                if normalized_prefix and title.startswith(normalized_prefix):
                    return str(loom_type), source
    return "unknown", "unknown"

def github_intake_context_inferred_object_type(
    *,
    phase_number: int | None,
    fr_number: int | None,
) -> str | None:
    if fr_number is not None:
        return "work_item"
    if phase_number is not None:
        return "fr"
    return None

def github_intake_object_type(
    issue_payload: dict[str, Any] | None,
    *,
    repo_interface: dict[str, Any] | None = None,
    phase_number: int | None = None,
    fr_number: int | None = None,
) -> tuple[str, dict[str, Any]]:
    mappings, missing_type_policy, taxonomy_availability = github_intake_taxonomy_mapping(repo_interface)
    object_type, source = github_intake_object_type_match(issue_payload, mappings)
    if object_type == "unknown" and missing_type_policy == "infer_from_context":
        inferred = github_intake_context_inferred_object_type(phase_number=phase_number, fr_number=fr_number)
        if inferred:
            object_type = inferred
            source = "context"
    return object_type, {
        "source": source,
        "taxonomy_availability": taxonomy_availability,
        "missing_type_policy": missing_type_policy,
        "repo_mapping_count": len(mappings),
    }

def github_intake_route(object_type: str, issue_payload: dict[str, Any] | None, dependency_graph: dict[str, Any]) -> str:
    state = issue_payload.get("state") if isinstance(issue_payload, dict) else None
    if any(finding.get("kind") == "open_blocker_executable_conflict" for finding in dependency_graph.get("findings", []) if isinstance(finding, dict)):
        return "manual-reconciliation"
    if state == "CLOSED":
        return "closeout"
    if object_type == "work_item":
        return "loom-resume"
    if object_type in {"phase", "fr"}:
        return "loom-story"
    return "manual-reconciliation"

def github_intake_payload(
    *,
    target_root: Path,
    owner: str | None,
    repo_name: str | None,
    issue_number: int,
    project_number: int | None,
    phase_number: int | None,
    fr_number: int | None,
    pr_number: int | None,
    branch_name: str | None,
    head_sha: str | None,
) -> dict[str, Any]:
    detected_owner, detected_repo = detect_github_repo(target_root)
    owner = owner or detected_owner
    repo_name = repo_name or detected_repo
    missing_inputs: list[str] = []
    provenance = [
        {
            "source_layer": "host_control_mirror",
            "source_owner": "github",
            "source_locator": f"issue #{issue_number}",
            "freshness": "fresh",
        }
    ]
    if not owner or not repo_name:
        missing_inputs.append("owner/repo")
        owner = owner or "unknown"
        repo_name = repo_name or "unknown"

    issue_payload: dict[str, Any] | None = None
    issue_errors: list[str] = []
    if owner != "unknown" and repo_name != "unknown":
        issue_payload, issue_errors = github_issue_payload(target_root, owner, repo_name, issue_number)
        missing_inputs.extend(f"issue: {message}" for message in issue_errors)

    native_dependencies = (
        github_issue_dependencies_payload(target_root, owner, repo_name, issue_number)
        if owner != "unknown" and repo_name != "unknown" and issue_payload is not None
        else {"availability": "not_requested", "checks": [], "native_edges": []}
    )
    dependency_graph = dependency_graph_payload(
        issue_number=issue_number,
        issue_payload=issue_payload,
        native_dependency_payload=native_dependencies,
    )
    governance_surface = build_governance_surface(target_root)
    repo_interface = governance_surface.get("repo_interface")
    object_type, type_inference = github_intake_object_type(
        issue_payload,
        repo_interface=repo_interface if isinstance(repo_interface, dict) else None,
        phase_number=phase_number,
        fr_number=fr_number,
    )
    route = github_intake_route(object_type, issue_payload, dependency_graph)
    findings: list[dict[str, Any]] = []

    binding = host_binding_inspection_payload(
        target_root=target_root,
        owner=owner if owner != "unknown" else None,
        repo_name=repo_name if repo_name != "unknown" else None,
        phase_number=phase_number,
        fr_number=fr_number,
        issue_number=issue_number,
        pr_number=pr_number,
        project_number=project_number,
        branch_name=branch_name,
        head_sha=head_sha,
        base_sha=None,
    )
    project_drift = project_drift_payload(
        target_root=target_root,
        owner=owner if owner != "unknown" else None,
        repo_name=repo_name if repo_name != "unknown" else None,
        issue_number=issue_number,
        pr_number=pr_number,
        project_number=project_number,
        mode="blocking",
    )
    for message in binding.get("missing_inputs", []):
        if message not in missing_inputs:
            missing_inputs.append(f"binding: {message}")
    if object_type == "unknown":
        finding = {
            "kind": "unrecognized_type_label",
            "severity": "warn",
            "subject": f"issue #{issue_number}",
            "summary": "GitHub issue type is not mapped by Loom defaults or repo companion host_planning_taxonomy.",
            "fallback_to": "manual-reconciliation",
        }
        findings.append(finding)
        if type_inference.get("missing_type_policy") == "block_unknown":
            missing_inputs.append("object_type")
    for finding in dependency_graph.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("severity") == "block":
            missing_inputs.append(str(finding.get("subject") or finding.get("kind")))
        if finding.get("kind") == "native_dependency_unreadable":
            missing_inputs.append("native dependency capability")
    if project_number is not None and project_drift.get("result") == "block":
        for message in project_drift.get("missing_inputs", []):
            if message not in missing_inputs:
                missing_inputs.append(f"project: {message}")
        for finding in project_drift.get("findings", []):
            if isinstance(finding, dict):
                missing_inputs.append(str(finding.get("subject") or finding.get("kind")))

    result = "pass" if not missing_inputs else "block"
    return {
        "command": "github-intake",
        "operation": "issue",
        "schema_version": "loom-github-intake/v1",
        "result": result,
        "summary": (
            "GitHub issue intake produced a read-only route for Loom execution."
            if result == "pass"
            else "GitHub issue intake found host-control gaps that must be reconciled before execution."
        ),
        "missing_inputs": dedupe_strings(missing_inputs),
        "fallback_to": None if result == "pass" else route,
        "object_type": object_type,
        "type_inference": type_inference,
        "route": route,
        "issue": issue_payload,
        "bindings": binding,
        "dependency_graph": dependency_graph,
        "project_drift": project_drift,
        "findings": findings,
        "provenance": provenance,
    }

def handle_github_intake(args: argparse.Namespace) -> int:
    target_root = resolve_target_arg(args.target)
    if args.operation == "admission":
        return emit(
            github_fr_wi_admission_payload(
                target_root=target_root,
                owner=args.owner,
                repo_name=args.repo_name,
                issue_number=args.issue,
                intent=args.intent,
                task=args.task,
                blocked_by=args.blocked_by,
                work_item_number=args.work_item,
                apply=args.apply,
                lifecycle_only=args.lifecycle_only,
            )
        )
    runtime_state = runtime_state_payload(target_root)
    if runtime_state["result"] != "pass":
        return emit(
            runtime_state_block_payload(
                command="github-intake",
                operation=args.operation,
                runtime_state=runtime_state,
                summary="GitHub intake is blocked because the Loom runtime state is inconsistent.",
            )
        )
    return emit(
        github_intake_payload(
            target_root=target_root,
            owner=args.owner,
            repo_name=args.repo_name,
            issue_number=args.issue,
            project_number=args.project,
            phase_number=args.phase,
            fr_number=args.fr,
            pr_number=args.pr,
            branch_name=args.branch,
            head_sha=args.head_sha,
        )
    )
PROJECT_DRIFT_KINDS = {
    "project_missing_item",
    "project_status_mismatch",
    "project_unreadable",
    "project_stale_mirror",
    "missing_native_edge",
    "unexpected_native_edge",
    "stale_native_edge",
    "open_blocker_executable_conflict",
}
