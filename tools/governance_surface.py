#!/usr/bin/env python3
"""Shared governance-surface detection for Loom bootstrap, route, and resume."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

CARRIER_KEYS = (
    "work_item",
    "recovery",
    "review",
    "status_surface",
    "spec_path",
    "plan_path",
)

PLANNED_LOCATORS = {
    "work_item": ".loom/work-items/INIT-0001.md",
    "recovery": ".loom/progress/INIT-0001.md",
    "review": ".loom/reviews/INIT-0001.json",
    "status_surface": ".loom/status/current.md",
    "spec_path": ".loom/specs/INIT-0001/spec.md",
    "plan_path": ".loom/specs/INIT-0001/plan.md",
}


def run_process(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)


def file_exists(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def relative_locator(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def safe_read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def command_prefix(root: Path, tool_name: str) -> str:
    installed_state = safe_read_json(root / ".loom" / "installed-state.json")
    if isinstance(installed_state, dict) and installed_state.get("runtime_provider") == "global-cli":
        return "loom"
    loom_tool = root / ".loom/bin" / tool_name
    repo_tool = root / "tools" / tool_name
    if loom_tool.exists():
        return f"python3 .loom/bin/{tool_name}"
    if repo_tool.exists():
        return f"python3 tools/{tool_name}"
    return f"python3 tools/{tool_name}"


def git_remote_origin(root: Path) -> str | None:
    result = run_process(["git", "remote", "get-url", "origin"], root)
    if result.returncode != 0:
        return None
    remote = result.stdout.strip()
    return remote or None


def detect_github_repo(root: Path) -> tuple[str | None, str | None]:
    remote = git_remote_origin(root)
    if not remote:
        return None, None
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", remote)
    if not match:
        return None, None
    return match.group("owner"), match.group("repo")


def gh_json(root: Path, args: list[str]) -> tuple[dict[str, Any] | None, list[str]]:
    result = run_process(["gh", *args], root)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "gh command failed"
        return None, [detail]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON from gh {' '.join(args)}: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"gh {' '.join(args)} did not return a JSON object"]
    return payload, []


def gh_rest_json(root: Path, path: str) -> tuple[dict[str, Any] | None, list[str]]:
    return gh_json(root, ["api", path])


def detect_loom_state(root: Path) -> str:
    active_requirements = (
        root / ".loom/bootstrap/init-result.json",
        root / ".loom/work-items",
        root / ".loom/progress",
        root / ".loom/status/current.md",
    )
    if all(path.exists() for path in active_requirements):
        return "active"

    partial_markers = (
        root / ".loom",
        root / "AGENTS.md",
        root / ".github/PULL_REQUEST_TEMPLATE.md",
    )
    if any(path.exists() for path in partial_markers):
        return "partial"
    return "absent"


def detect_repository_mode(root: Path, loom_state: str, scenario_override: str | None = None) -> str:
    if scenario_override in {"new", "small-existing", "complex-existing"}:
        return scenario_override

    init_result = safe_read_json(root / ".loom/bootstrap/init-result.json")
    if isinstance(init_result, dict):
        run = init_result.get("run")
        if isinstance(run, dict):
            scenario_key = run.get("scenario_key")
            if scenario_key in {"new", "small-existing", "complex-existing"}:
                return str(scenario_key)

    code_dirs = ("src", "app", "lib", "cmd", "pkg", "services", "packages")
    boundary_files = (
        "README.md",
        "AGENTS.md",
        "WORKFLOW.md",
        "docs/WORKFLOW.md",
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "Makefile",
        ".github/workflows",
    )
    baseline_count = sum(1 for entry in boundary_files if file_exists(root, entry))
    code_count = sum(1 for entry in code_dirs if file_exists(root, entry))

    meaningful_entries = 0
    for path in root.iterdir():
        if path.name in {".git", ".DS_Store"}:
            continue
        if path.name == ".loom" and loom_state != "absent":
            continue
        meaningful_entries += 1

    if loom_state == "absent" and meaningful_entries <= 2 and baseline_count <= 1 and code_count == 0:
        return "new"
    if baseline_count + code_count >= 4 or meaningful_entries >= 8:
        return "complex-existing"
    return "small-existing"


def carrier_entry(status: str, locator: str, source: str) -> dict[str, str]:
    return {"status": status, "locator": locator, "source": source}


def first_match(directory: Path, suffix: str, root: Path) -> str:
    for path in sorted(directory.glob(f"*{suffix}")):
        return relative_locator(path, root)
    return ""


def detect_carrier_summary(root: Path, *, repository_mode: str, planning_mode: bool) -> dict[str, dict[str, str]]:
    item_dir = root / ".loom/work-items"
    recovery_dir = root / ".loom/progress"
    review_dir = root / ".loom/reviews"
    status_path = root / ".loom/status/current.md"
    spec_path = root / ".loom/specs/INIT-0001/spec.md"
    plan_path = root / ".loom/specs/INIT-0001/plan.md"

    present_locators = {
        "work_item": first_match(item_dir, ".md", root) if item_dir.exists() else "",
        "recovery": first_match(recovery_dir, ".md", root) if recovery_dir.exists() else "",
        "review": first_match(review_dir, ".json", root) if review_dir.exists() else "",
        "status_surface": relative_locator(status_path, root) if status_path.exists() else "",
        "spec_path": relative_locator(spec_path, root) if spec_path.exists() else "",
        "plan_path": relative_locator(plan_path, root) if plan_path.exists() else "",
    }

    summary: dict[str, dict[str, str]] = {}
    for key in CARRIER_KEYS:
        locator = present_locators[key]
        if locator:
            summary[key] = carrier_entry("present", locator, "repository scan")
        elif planning_mode and repository_mode == "new":
            summary[key] = carrier_entry("planned", PLANNED_LOCATORS[key], "bootstrap plan")
        else:
            summary[key] = carrier_entry("missing", "unknown", "repository scan")
    return summary


def detect_execution_entry(root: Path, loom_state: str, *, bootstrap_mode: bool) -> str:
    if bootstrap_mode:
        return "python3 .loom/bin/loom_flow.py flow resume --target . --item INIT-0001"
    if loom_state == "active":
        return f"{command_prefix(root, 'loom_flow.py')} flow resume --target . --item INIT-0001"
    if loom_state == "partial":
        return "python3 tools/loom_init.py route --target <repo> --task \"请接手当前事项并恢复上下文后继续推进\""
    return "unknown"


def detect_validation_entry(loom_state: str, *, bootstrap_mode: bool) -> str:
    if bootstrap_mode:
        return "python3 .loom/bin/loom_init.py verify --target ."
    if loom_state == "active":
        return "python3 .loom/bin/loom_init.py verify --target ."
    if loom_state == "partial":
        return "python3 tools/loom_init.py verify --target <repo>"
    return "unknown"


def detect_review_merge_surface(root: Path, loom_state: str, *, bootstrap_mode: bool) -> dict[str, str]:
    pr_template = ".github/PULL_REQUEST_TEMPLATE.md" if file_exists(root, ".github/PULL_REQUEST_TEMPLATE.md") else "unknown"
    validation_surface = ".loom/status/current.md" if file_exists(root, ".loom/status/current.md") else "unknown"
    if bootstrap_mode and validation_surface == "unknown":
        validation_surface = ".loom/status/current.md"

    if bootstrap_mode:
        merge_surface = "python3 .loom/bin/loom_flow.py checkpoint merge --target . --item INIT-0001"
    elif loom_state == "active":
        merge_surface = f"{command_prefix(root, 'loom_flow.py')} checkpoint merge --target . [--item <id>]"
    else:
        merge_surface = "unknown"
    return {
        "pr_template": pr_template,
        "validation_surface": validation_surface,
        "merge_surface": merge_surface,
    }


def detect_github_control_plane(root: Path) -> tuple[dict[str, Any], list[str]]:
    owner, repo = detect_github_repo(root)
    surface: dict[str, Any] = {
        "repository": f"{owner}/{repo}" if owner and repo else "unknown",
        "default_branch": "unknown",
        "branch_protection": "unknown",
        "required_checks": "unknown",
        "pr_reviews": "unknown",
    }
    missing_inputs: list[str] = []

    if not owner or not repo:
        missing_inputs.append("cannot resolve GitHub repository from git origin")
        return surface, missing_inputs

    repo_payload, repo_errors = gh_rest_json(root, f"repos/{owner}/{repo}")
    if repo_errors or repo_payload is None:
        missing_inputs.extend(f"github control plane: {message}" for message in repo_errors)
        return surface, missing_inputs

    full_name = repo_payload.get("full_name")
    if isinstance(full_name, str) and full_name:
        surface["repository"] = full_name
    branch_name = repo_payload.get("default_branch")
    if isinstance(branch_name, str) and branch_name:
        surface["default_branch"] = branch_name
    if surface["default_branch"] == "unknown":
        missing_inputs.append("github control plane: default branch is unavailable")
        return surface, missing_inputs

    branch_payload, branch_errors = gh_json(root, ["api", f"repos/{owner}/{repo}/branches/{surface['default_branch']}"])
    if branch_errors or branch_payload is None:
        missing_inputs.extend(f"github control plane: {message}" for message in branch_errors)
        return surface, missing_inputs

    protected = branch_payload.get("protected")
    if isinstance(protected, bool):
        surface["branch_protection"] = "enabled" if protected else "disabled"
    protection = branch_payload.get("protection")
    if isinstance(protection, dict):
        required_status = protection.get("required_status_checks")
        if isinstance(required_status, dict):
            contexts = required_status.get("contexts")
            if isinstance(contexts, list) and all(isinstance(item, str) for item in contexts):
                surface["required_checks"] = contexts
            else:
                surface["required_checks"] = []
        pull_request_reviews = protection.get("required_pull_request_reviews")
        if isinstance(pull_request_reviews, dict):
            surface["pr_reviews"] = "required"
        elif surface["branch_protection"] == "enabled":
            surface["pr_reviews"] = "not_required"
    return surface, missing_inputs


def build_governance_surface(
    root: Path,
    *,
    bootstrap_mode: bool = False,
    scenario_override: str | None = None,
) -> dict[str, Any]:
    loom_state = detect_loom_state(root)
    repository_mode = detect_repository_mode(root, loom_state, scenario_override=scenario_override)
    planning_mode = bootstrap_mode and repository_mode == "new" and loom_state != "active"
    carrier_summary = detect_carrier_summary(root, repository_mode=repository_mode, planning_mode=planning_mode)
    github_control_plane, github_missing = detect_github_control_plane(root)
    execution_entry = detect_execution_entry(root, loom_state, bootstrap_mode=bootstrap_mode)
    validation_entry = detect_validation_entry(loom_state, bootstrap_mode=bootstrap_mode)
    review_merge_surface = detect_review_merge_surface(root, loom_state, bootstrap_mode=bootstrap_mode)

    missing_inputs: list[str] = []
    if bootstrap_mode and repository_mode == "new":
        missing_inputs.extend(github_missing)
        summary = "repository is treated as new; Loom can plan the first governance carriers and bootstrap entrypoints without adding a second truth source."
    else:
        present_carriers = [key for key, value in carrier_summary.items() if value["status"] == "present"]
        if not present_carriers:
            missing_inputs.append("no stable Loom carriers are readable yet")
        missing_inputs.extend(github_missing)
        control_plane_ready = github_control_plane["default_branch"] != "unknown"
        carrier_ready = bool(present_carriers)
        summary = (
            "resume chain is readable and the current governance carriers can support continued execution."
            if carrier_ready and control_plane_ready
            else "resume chain is only partially supported because governance carriers or GitHub control-plane signals are incomplete."
        )

    return {
        "repository_mode": repository_mode,
        "loom_state": loom_state,
        "carrier_summary": carrier_summary,
        "execution_entry": execution_entry,
        "validation_entry": validation_entry,
        "review_merge_surface": review_merge_surface,
        "github_control_plane": github_control_plane,
        "summary": summary,
        "missing_inputs": list(dict.fromkeys(missing_inputs)),
    }
