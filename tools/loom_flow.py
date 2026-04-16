#!/usr/bin/env python3
"""Daily execution CLI for Loom checkpoints, workspace lifecycle, and purity checks."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from fact_chain_support import (
    STATUS_FIELDS,
    STATUS_SOURCE_FIELDS,
    inspect_fact_chain,
    load_json_file,
    markdown_sections,
    parse_key_value_section,
    parse_recovery_entry,
    parse_work_item,
)

PR_TEMPLATE_SECTIONS = (
    "## Summary",
    "## Validation",
    "## Risks And Follow-ups",
    "## Related Work",
)

OWNED_TEMP_ROOTS = (
    ".loom/.tmp",
    ".loom/tmp",
    ".loom/runtime/cache",
    ".loom/runtime/tmp",
    ".loom/flow/tmp",
)

TERMINAL_CHECKPOINTS = {
    "retired",
    "done",
    "closed",
    "merged",
    "archived",
}

RUNTIME_EVIDENCE_FIELDS = (
    "run_entry",
    "logs_entry",
    "diagnostics_entry",
    "verification_entry",
    "lane_entry",
)


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
    workspace.add_argument("operation", choices=("create", "locate", "cleanup", "retire"))
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

    flow = subparsers.add_parser("flow", help="Run a bundled high-frequency Loom flow")
    flow.add_argument("operation", choices=("pre-review", "resume", "handoff", "merge-ready"))
    flow.add_argument("--target", required=True, help="Target repository root")
    flow.add_argument("--item", help="Expected current item id")
    flow.add_argument(
        "--output",
        default=".loom/bootstrap/init-result.json",
        help="Init-result path relative to the target root",
    )

    return parser.parse_args(argv)


def emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    result = payload.get("result")
    return 0 if result == "pass" else 1


def normalize_checkpoint(raw: str) -> str:
    lowered = raw.strip().lower()
    if "commit checkpoint" in lowered or "admission checkpoint" in lowered:
        return "admission"
    if "build checkpoint" in lowered:
        return "build"
    if "merge checkpoint" in lowered:
        return "merge"
    if "retired" in lowered:
        return "retired"
    return lowered.replace(" checkpoint", "").strip()


def checkpoint_rank(name: str) -> int:
    ranks = {
        "admission": 1,
        "build": 2,
        "merge": 3,
        "retired": 99,
    }
    return ranks.get(name, -1)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None


def git_branch(root: Path) -> str | None:
    result = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if result is None or result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def git_dirty_entries(root: Path) -> list[dict[str, str]]:
    result = run_git(root, ["status", "--porcelain=v1"])
    if result is None or result.returncode != 0:
        return []

    entries: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        remainder = line[3:]
        path_text = remainder.split(" -> ", 1)[-1].strip()
        if not path_text:
            continue
        entries.append({"status": status, "path": path_text})
    return entries


def git_tracked_files(root: Path, relative: str) -> list[str]:
    result = run_git(root, ["ls-files", "--", relative])
    if result is None or result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def relative_to_root(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def resolve_workspace_path(target_root: Path, workspace_entry: str) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    raw = Path(workspace_entry)
    if raw.is_absolute():
        resolved = raw.resolve()
    else:
        resolved = (target_root / raw).resolve()
    try:
        resolved.relative_to(target_root.resolve())
    except ValueError:
        return None, [f"workspace entry escapes target root: {workspace_entry}"]
    return resolved, errors


def current_cwd_relative(target_root: Path) -> str | None:
    cwd = Path.cwd().resolve()
    try:
        return str(cwd.relative_to(target_root.resolve()))
    except ValueError:
        return None


def update_markdown_bullet(path: Path, label: str, value: str) -> None:
    pattern = re.compile(rf"(?m)^- {re.escape(label)}:\s*.*$")
    replacement = f"- {label}: {value}"
    text = path.read_text(encoding="utf-8")
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"unable to update `{label}` in {path}")
    path.write_text(updated, encoding="utf-8")


def check_pr_template(target_root: Path) -> tuple[dict[str, Any], list[str]]:
    path = target_root / ".github/PULL_REQUEST_TEMPLATE.md"
    if not path.exists():
        return {"exists": False, "path": ".github/PULL_REQUEST_TEMPLATE.md", "sections": {}}, ["missing PR template"]

    text = path.read_text(encoding="utf-8")
    sections = {section: (section in text) for section in PR_TEMPLATE_SECTIONS}
    missing = [f"PR template missing section: {section}" for section, present in sections.items() if not present]
    return {
        "exists": True,
        "path": ".github/PULL_REQUEST_TEMPLATE.md",
        "sections": sections,
    }, missing


def active_workspace_conflicts(target_root: Path, item_id: str, workspace_entry: str) -> list[str]:
    work_items_dir = target_root / ".loom/work-items"
    if not work_items_dir.exists():
        return []

    conflicts: list[str] = []
    for candidate in sorted(work_items_dir.glob("*.md")):
        try:
            parsed_item, errors = parse_work_item(candidate, target_root)
        except OSError:
            continue
        if errors:
            continue
        other_item_id = str(parsed_item["item_id"])
        if other_item_id == item_id:
            continue
        if str(parsed_item["workspace_entry"]) != workspace_entry:
            continue
        recovery_rel = str(parsed_item["recovery_entry"])
        recovery_path = target_root / recovery_rel
        if not recovery_path.exists():
            conflicts.append(other_item_id)
            continue
        try:
            recovery_data, recovery_errors = parse_recovery_entry(recovery_path, target_root)
        except OSError:
            conflicts.append(other_item_id)
            continue
        if recovery_errors:
            conflicts.append(other_item_id)
            continue
        if normalize_checkpoint(recovery_data["current_checkpoint"]) not in TERMINAL_CHECKPOINTS:
            conflicts.append(other_item_id)
    return conflicts


def collect_temp_paths(target_root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in OWNED_TEMP_ROOTS:
        candidate = target_root / relative
        if candidate.exists():
            paths.append(candidate)
    return paths


def dirty_paths_by_owner(target_root: Path) -> tuple[list[str], list[str]]:
    owned: list[str] = []
    foreign: list[str] = []
    for entry in git_dirty_entries(target_root):
        path = entry["path"]
        if any(path == root or path.startswith(f"{root}/") for root in OWNED_TEMP_ROOTS):
            owned.append(path)
        else:
            foreign.append(path)
    return owned, foreign


def declared_scope_paths(scope_text: str) -> list[str]:
    candidates: list[str] = []
    for raw in re.findall(r"`([^`]+)`", scope_text):
        token = raw.strip()
        if not token:
            continue
        if token.startswith("/"):
            token = token.lstrip("/")
        if token.startswith("./"):
            token = token[2:]
        if token in {".", ""}:
            continue
        if "/" not in token and not token.endswith(".md"):
            continue
        candidates.append(token.rstrip("/"))

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        deduped.append(candidate)
    return deduped


def path_in_scope(path: str, scope_paths: list[str]) -> bool:
    return any(path == scope_path or path.startswith(f"{scope_path}/") for scope_path in scope_paths)


def load_context(target_root: Path, output_relative: str, expected_item: str | None) -> tuple[dict[str, Any], list[str]]:
    report, errors = load_fact_chain_report(target_root, output_relative)
    if errors:
        return {}, errors

    item_id = report["fact_chain"]["entry_points"]["current_item_id"]
    if expected_item and expected_item != item_id:
        return {}, [f"current item mismatch: expected `{expected_item}`, got `{item_id}`"]

    facts = report["facts"]
    workspace_entry = str(facts["workspace_entry"]["value"])
    workspace_path, workspace_errors = resolve_workspace_path(target_root, workspace_entry)
    if workspace_errors:
        return {}, workspace_errors
    if workspace_path is None:
        return {}, [f"unable to resolve workspace entry: {workspace_entry}"]

    context = {
        "target_root": target_root,
        "output_relative": output_relative,
        "report": report,
        "item_id": item_id,
        "work_item_path": target_root / report["fact_chain"]["entry_points"]["work_item"],
        "recovery_path": target_root / report["fact_chain"]["entry_points"]["recovery_entry"],
        "status_path": target_root / report["fact_chain"]["entry_points"]["status_surface"],
        "workspace_entry": workspace_entry,
        "workspace_path": workspace_path,
        "validation_entry": str(facts["validation_entry"]["value"]),
        "current_checkpoint_raw": str(facts["current_checkpoint"]["value"]),
        "current_checkpoint": normalize_checkpoint(str(facts["current_checkpoint"]["value"])),
        "goal": str(facts["goal"]["value"]),
        "scope": str(facts["scope"]["value"]),
        "execution_path": str(facts["execution_path"]["value"]),
        "current_stop": str(facts["current_stop"]["value"]),
        "next_step": str(facts["next_step"]["value"]),
        "blockers": str(facts["blockers"]["value"]),
        "latest_validation_summary": str(facts["latest_validation_summary"]["value"]),
        "recovery_boundary": str(facts["recovery_boundary"]["value"]),
        "current_lane": str(facts["current_lane"]["value"]),
        "closing_condition": str(facts["closing_condition"]["value"]),
        "read_entry": str(report["fact_chain"]["read_entry"]),
    }
    return context, []


def load_fact_chain_report(target_root: Path, output_relative: str) -> tuple[dict[str, Any], list[str]]:
    report, errors = inspect_fact_chain(target_root, output_relative)
    if errors and all("Runtime Evidence" in message for message in errors):
        report, errors = inspect_fact_chain_legacy(target_root, output_relative)
    if errors:
        return {}, errors
    if not report:
        return {}, ["no fact-chain report was produced"]
    return report, []


def inspect_fact_chain_legacy(target_root: Path, output_relative: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    output_path = target_root / output_relative
    if not output_path.exists():
        return {}, [f"missing init-result: {output_relative}"]

    try:
        init_result = load_json_file(output_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {}, [f"invalid init-result JSON: {exc}"]

    fact_chain = init_result.get("fact_chain")
    if not isinstance(fact_chain, dict):
        return {}, ["init-result is missing required section: fact_chain"]

    read_entry = fact_chain.get("read_entry")
    mode = fact_chain.get("mode")
    entry_points = fact_chain.get("entry_points")
    if not isinstance(read_entry, str) or not read_entry:
        errors.append("init-result.fact_chain.read_entry must be a non-empty string")
    if not isinstance(mode, str) or not mode:
        errors.append("init-result.fact_chain.mode must be a non-empty string")
    if not isinstance(entry_points, dict):
        errors.append("init-result.fact_chain.entry_points must be an object")
        entry_points = {}

    work_item_ref = entry_points.get("work_item")
    recovery_ref = entry_points.get("recovery_entry")
    status_ref = entry_points.get("status_surface")
    current_item_id = entry_points.get("current_item_id")
    for label, value in (
        ("work_item", work_item_ref),
        ("recovery_entry", recovery_ref),
        ("status_surface", status_ref),
        ("current_item_id", current_item_id),
    ):
        if not isinstance(value, str) or not value:
            errors.append(f"init-result.fact_chain.entry_points.{label} must be a non-empty string")
    if errors:
        return {}, errors

    work_item_path = target_root / str(work_item_ref)
    recovery_path = target_root / str(recovery_ref)
    status_path = target_root / str(status_ref)
    for label, path in (
        ("work_item", work_item_path),
        ("recovery_entry", recovery_path),
        ("status_surface", status_path),
    ):
        if not path.exists():
            errors.append(f"declared fact-chain carrier is missing on disk: {label} -> {path.relative_to(target_root)}")
    if errors:
        return {}, errors

    work_item, work_item_errors = parse_work_item(work_item_path, target_root)
    recovery_entry, recovery_errors = parse_recovery_entry(recovery_path, target_root)
    status_sections = markdown_sections(status_path)
    status_values, status_errors = parse_key_value_section(
        status_sections,
        "Derived Fact Chain View",
        STATUS_FIELDS,
        str(status_path.relative_to(target_root)),
    )
    status_sources, source_errors = parse_key_value_section(
        status_sections,
        "Sources",
        STATUS_SOURCE_FIELDS,
        str(status_path.relative_to(target_root)),
    )
    errors.extend(work_item_errors)
    errors.extend(recovery_errors)
    errors.extend(status_errors)
    errors.extend(source_errors)
    if errors:
        return {}, errors

    if str(work_item["item_id"]) != str(recovery_entry["item_id"]):
        errors.append(
            "work item and recovery entry disagree on item id: "
            f"{work_item['item_id']} vs {recovery_entry['item_id']}"
        )
    if str(work_item["recovery_entry"]) != str(recovery_ref):
        errors.append(
            "work item recovery entry does not match init-result locator: "
            f"{work_item['recovery_entry']} vs {recovery_ref}"
        )
    if str(work_item["item_id"]) != str(current_item_id):
        errors.append(
            "init-result.fact_chain.entry_points.current_item_id does not match work item id: "
            f"{current_item_id} vs {work_item['item_id']}"
        )

    expected_status = {
        "item_id": str(work_item["item_id"]),
        "goal": str(work_item["goal"]),
        "scope": str(work_item["scope"]),
        "execution_path": str(work_item["execution_path"]),
        "workspace_entry": str(work_item["workspace_entry"]),
        "recovery_entry": str(work_item["recovery_entry"]),
        "validation_entry": str(work_item["validation_entry"]),
        "closing_condition": str(work_item["closing_condition"]),
        "current_checkpoint": recovery_entry["current_checkpoint"],
        "current_stop": recovery_entry["current_stop"],
        "next_step": recovery_entry["next_step"],
        "blockers": recovery_entry["blockers"],
        "latest_validation_summary": recovery_entry["latest_validation_summary"],
        "recovery_boundary": recovery_entry["recovery_boundary"],
        "current_lane": recovery_entry["current_lane"],
    }
    for field_name, expected_value in expected_status.items():
        actual_value = status_values.get(field_name)
        if actual_value != expected_value:
            errors.append(
                "status surface mismatch for "
                f"`{field_name}`: expected `{expected_value}`, got `{actual_value}`"
            )

    expected_sources = {
        "work_item": str(work_item_ref),
        "recovery_entry": str(recovery_ref),
        "init_result": output_relative,
        "read_entry": str(read_entry),
    }
    for source_key, expected_value in expected_sources.items():
        actual_value = status_sources.get(source_key)
        if actual_value != expected_value:
            errors.append(
                "status surface source mismatch for "
                f"`{source_key}`: expected `{expected_value}`, got `{actual_value}`"
            )
    if errors:
        return {}, errors

    report = {
        "target": str(target_root),
        "fact_chain": {
            "mode": str(mode),
            "read_entry": str(read_entry),
            "entry_points": {
                "current_item_id": str(current_item_id),
                "work_item": str(work_item_ref),
                "recovery_entry": str(recovery_ref),
                "status_surface": str(status_ref),
            },
        },
        "facts": {
            "item_id": {"value": str(work_item["item_id"])},
            "goal": {"value": str(work_item["goal"])},
            "scope": {"value": str(work_item["scope"])},
            "execution_path": {"value": str(work_item["execution_path"])},
            "associated_artifacts": {"value": list(work_item["associated_artifacts"])},
            "workspace_entry": {"value": str(work_item["workspace_entry"])},
            "recovery_entry": {"value": str(work_item["recovery_entry"])},
            "validation_entry": {"value": str(work_item["validation_entry"])},
            "closing_condition": {"value": str(work_item["closing_condition"])},
            "current_checkpoint": {"value": recovery_entry["current_checkpoint"]},
            "current_stop": {"value": recovery_entry["current_stop"]},
            "next_step": {"value": recovery_entry["next_step"]},
            "blockers": {"value": recovery_entry["blockers"]},
            "latest_validation_summary": {"value": recovery_entry["latest_validation_summary"]},
            "recovery_boundary": {"value": recovery_entry["recovery_boundary"]},
            "current_lane": {"value": recovery_entry["current_lane"]},
        },
        "runtime_evidence": {},
        "derived_status_surface": {
            "path": str(status_ref),
            "values": expected_status,
            "runtime_evidence": {},
            "sources": expected_sources,
        },
    }
    return report, []


def purity_report_from_context(context: dict[str, Any], fact_chain_errors: list[str] | None = None) -> dict[str, Any]:
    target_root = context["target_root"]
    workspace_path = context["workspace_path"]
    workspace_entry = context["workspace_entry"]
    item_id = context["item_id"]

    hard_failures: list[str] = []
    report_only: list[str] = []

    if fact_chain_errors:
        hard_failures.extend(f"fact-chain: {message}" for message in fact_chain_errors)

    if not workspace_path.exists():
        hard_failures.append(f"declared workspace entry does not exist on disk: {workspace_entry}")
    elif not workspace_path.is_dir():
        hard_failures.append(f"declared workspace entry is not a directory: {workspace_entry}")

    cwd_relative = current_cwd_relative(target_root)
    workspace_relative = relative_to_root(workspace_path, target_root)
    if cwd_relative is not None:
        if workspace_relative != "." and cwd_relative != workspace_relative and not cwd_relative.startswith(f"{workspace_relative}/"):
            hard_failures.append(
                f"current working directory is outside the declared workspace: cwd={cwd_relative}, workspace={workspace_relative}"
            )

    owned_dirty, foreign_dirty = dirty_paths_by_owner(target_root)
    if foreign_dirty:
        preview = ", ".join(sorted(foreign_dirty)[:5])
        hard_failures.append(f"workspace contains untriaged residual changes: {preview}")
    if owned_dirty:
        preview = ", ".join(sorted(owned_dirty)[:5])
        hard_failures.append(f"loom-owned temporary residue is still present: {preview}")

    scope_paths = declared_scope_paths(context["scope"])
    out_of_scope_changes: list[str] = []
    if scope_paths:
        for path in foreign_dirty:
            if not path_in_scope(path, scope_paths):
                out_of_scope_changes.append(path)
        if out_of_scope_changes:
            preview = ", ".join(sorted(out_of_scope_changes)[:5])
            hard_failures.append(f"scope overflow detected: {preview}")

    conflicts = active_workspace_conflicts(target_root, item_id, workspace_entry)
    if conflicts:
        hard_failures.append(
            "workspace is bound to multiple active work items: " + ", ".join(sorted(conflicts))
        )

    branch = git_branch(target_root)
    if branch:
        report_only.append(f"branch purity is report-only in v1: current branch `{branch}`")
    else:
        report_only.append("branch purity is report-only in v1: no branch information available")

    report_only.append("PR purity is report-only in v1")

    state = "failed" if hard_failures else "clean"
    return {
        "state": state,
        "workspace_entry": workspace_entry,
        "workspace_path": workspace_relative,
        "scope_assessment": {
            "mode": "constrained" if scope_paths else "unconstrained",
            "declared_paths": scope_paths,
            "out_of_scope_changes": sorted(out_of_scope_changes),
        },
        "hard_failures": hard_failures,
        "report_only": report_only,
    }


def base_workspace_payload(context: dict[str, Any], operation: str) -> dict[str, Any]:
    purity = purity_report_from_context(context)
    return {
        "command": "workspace",
        "operation": operation,
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
            "exists": context["workspace_path"].exists(),
        },
        "recovery": {
            "path": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
            "current_stop": context["current_stop"],
            "next_step": context["next_step"],
            "latest_validation_summary": context["latest_validation_summary"],
        },
        "checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": context["current_checkpoint"],
        },
        "purity": purity,
        "missing_inputs": [],
        "fallback_to": None,
    }


def checkpoint_payload(stage: str, context: dict[str, Any]) -> dict[str, Any]:
    purity = purity_report_from_context(context)
    missing_inputs: list[str] = []
    result = "pass"
    fallback_to: str | None = None

    if purity["hard_failures"]:
        missing_inputs.append("purity")
        result = "fallback"
        fallback_to = "admission"

    required = {
        "admission": (
            ("goal", context["goal"]),
            ("scope", context["scope"]),
            ("execution_path", context["execution_path"]),
            ("workspace_entry", context["workspace_entry"]),
            ("recovery_entry", str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])),
            ("validation_entry", context["validation_entry"]),
            ("closing_condition", context["closing_condition"]),
            ("current_checkpoint", context["current_checkpoint_raw"]),
            ("current_stop", context["current_stop"]),
            ("next_step", context["next_step"]),
        ),
        "build": (
            ("goal", context["goal"]),
            ("scope", context["scope"]),
            ("execution_path", context["execution_path"]),
            ("workspace_entry", context["workspace_entry"]),
            ("recovery_entry", str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])),
            ("status_surface", str(context["report"]["fact_chain"]["entry_points"]["status_surface"])),
            ("validation_entry", context["validation_entry"]),
            ("latest_validation_summary", context["latest_validation_summary"]),
            ("current_lane", context["current_lane"]),
            ("closing_condition", context["closing_condition"]),
        ),
        "merge": (
            ("goal", context["goal"]),
            ("scope", context["scope"]),
            ("execution_path", context["execution_path"]),
            ("workspace_entry", context["workspace_entry"]),
            ("recovery_entry", str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"])),
            ("status_surface", str(context["report"]["fact_chain"]["entry_points"]["status_surface"])),
            ("validation_entry", context["validation_entry"]),
            ("latest_validation_summary", context["latest_validation_summary"]),
            ("current_lane", context["current_lane"]),
            ("recovery_boundary", context["recovery_boundary"]),
            ("blockers", context["blockers"]),
            ("closing_condition", context["closing_condition"]),
        ),
    }[stage]

    for label, value in required:
        if not str(value).strip():
            missing_inputs.append(label)

    current_rank = checkpoint_rank(context["current_checkpoint"])
    requested_rank = checkpoint_rank(stage)
    if context["current_checkpoint"] in TERMINAL_CHECKPOINTS:
        result = "fallback"
        fallback_to = context["current_checkpoint"]
    elif current_rank != -1 and current_rank < requested_rank:
        result = "fallback"
        fallback_to = context["current_checkpoint"]

    blocker_text = context["blockers"].strip().lower()
    if blocker_text not in {"none", "none recorded", "none recorded."}:
        result = "block" if result == "pass" else result

    pr_template: dict[str, Any] | None = None
    if stage == "merge":
        pr_template, pr_template_errors = check_pr_template(context["target_root"])
        if pr_template_errors:
            missing_inputs.extend(pr_template_errors)
            if result == "pass":
                result = "block"

    if missing_inputs and result == "pass":
        result = "block"

    if result == "pass":
        summary = f"{stage} checkpoint can be consumed from the current Loom fact chain."
    elif result == "block":
        summary = f"{stage} checkpoint is missing execution material but does not require a checkpoint rollback."
    else:
        fallback_label = fallback_to or "admission"
        summary = f"{stage} checkpoint cannot proceed from the current state; fall back to `{fallback_label}`."

    payload = {
        "command": "checkpoint",
        "checkpoint": stage,
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
        },
        "recovery": {
            "path": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
            "current_checkpoint": context["current_checkpoint_raw"],
            "current_stop": context["current_stop"],
            "next_step": context["next_step"],
            "latest_validation_summary": context["latest_validation_summary"],
            "current_lane": context["current_lane"],
        },
        "purity": purity,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": fallback_to,
    }
    if pr_template is not None:
        payload["pr_template"] = pr_template
    return payload


def handle_checkpoint(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "checkpoint",
                "checkpoint": args.stage,
                "result": "fallback",
                "summary": "checkpoint evaluation could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )
    return emit(checkpoint_payload(args.stage, context))


def handle_workspace(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "workspace",
                "operation": args.operation,
                "result": "fallback",
                "summary": "workspace lifecycle command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )

    payload = base_workspace_payload(context, args.operation)
    workspace_path = context["workspace_path"]
    purity = payload["purity"]

    if args.operation == "locate":
        payload["result"] = "pass" if not purity["hard_failures"] else "block"
        payload["summary"] = "workspace location was resolved from the fact chain."
        if purity["hard_failures"]:
            payload["summary"] = "workspace location resolved, but the workspace is not execution-ready."
            payload["missing_inputs"] = list(purity["hard_failures"])
        return emit(payload)

    if args.operation == "create":
        if purity["hard_failures"] and any("does not exist on disk" not in failure for failure in purity["hard_failures"]):
            payload["result"] = "block"
            payload["summary"] = "workspace creation is blocked until the current workspace state is clean."
            payload["missing_inputs"] = list(purity["hard_failures"])
            return emit(payload)

        created = False
        if not workspace_path.exists():
            workspace_path.mkdir(parents=True, exist_ok=True)
            created = True

        refreshed, refresh_errors = load_context(target_root, args.output, args.item)
        if refresh_errors:
            payload["result"] = "block"
            payload["summary"] = "workspace path was created, but the fact chain could not be reloaded."
            payload["missing_inputs"] = [f"fact-chain: {message}" for message in refresh_errors]
            return emit(payload)

        payload = base_workspace_payload(refreshed, args.operation)
        payload["created"] = created
        payload["result"] = "pass"
        payload["summary"] = "workspace semantics are established from `workspace_entry`."
        return emit(payload)

    if args.operation == "cleanup":
        owned_dirty, foreign_dirty = dirty_paths_by_owner(target_root)
        temp_paths = collect_temp_paths(target_root)
        if foreign_dirty:
            payload["result"] = "block"
            payload["summary"] = "cleanup stopped because the workspace contains non-Loom changes."
            payload["missing_inputs"] = [f"non-loom residue: {path}" for path in foreign_dirty]
            return emit(payload)

        removed: list[str] = []
        for temp_path in temp_paths:
            relative = relative_to_root(temp_path, target_root)
            tracked = git_tracked_files(target_root, relative)
            if tracked:
                payload["result"] = "block"
                payload["summary"] = "cleanup refused to delete tracked files from a Loom temporary path."
                payload["missing_inputs"] = [f"tracked temp path: {relative}"]
                return emit(payload)
            if temp_path.is_dir():
                shutil.rmtree(temp_path)
                removed.append(relative)
            else:
                temp_path.unlink()
                removed.append(relative)

        if owned_dirty and not removed:
            payload["result"] = "block"
            payload["summary"] = "cleanup found Loom temporary residue in git status, but no owned temp paths could be removed."
            payload["missing_inputs"] = [f"owned temp residue: {path}" for path in owned_dirty]
            return emit(payload)

        payload["removed_paths"] = removed
        payload["result"] = "pass"
        payload["summary"] = "cleanup removed Loom-owned temporary residue." if removed else "cleanup found no Loom-owned temporary residue."
        payload["purity"] = purity_report_from_context(context)
        return emit(payload)

    cleanup_payload = base_workspace_payload(context, "cleanup")
    owned_dirty, foreign_dirty = dirty_paths_by_owner(target_root)
    if foreign_dirty:
        cleanup_payload["result"] = "block"
        cleanup_payload["summary"] = "retire cannot proceed because cleanup is blocked by non-Loom changes."
        cleanup_payload["missing_inputs"] = [f"non-loom residue: {path}" for path in foreign_dirty]
        return emit(cleanup_payload)

    for temp_path in collect_temp_paths(target_root):
        relative = relative_to_root(temp_path, target_root)
        tracked = git_tracked_files(target_root, relative)
        if tracked:
            cleanup_payload["result"] = "block"
            cleanup_payload["summary"] = "retire cannot proceed because cleanup would need to delete tracked files."
            cleanup_payload["missing_inputs"] = [f"tracked temp path: {relative}"]
            return emit(cleanup_payload)
        if temp_path.is_dir():
            shutil.rmtree(temp_path)
        else:
            temp_path.unlink()

    update_markdown_bullet(context["recovery_path"], "Current Checkpoint", "retired")
    if context["status_path"].exists():
        update_markdown_bullet(context["status_path"], "Current Checkpoint", "retired")

    refreshed, refresh_errors = load_context(target_root, args.output, args.item)
    if refresh_errors:
        return emit(
            {
                "command": "workspace",
                "operation": "retire",
                "result": "block",
                "summary": "retire wrote `retired`, but the fact chain no longer reads cleanly.",
                "missing_inputs": [f"fact-chain: {message}" for message in refresh_errors],
                "fallback_to": "admission",
            }
        )

    payload = base_workspace_payload(refreshed, "retire")
    payload["result"] = "pass"
    payload["summary"] = "workspace was retired by updating the recovery entry checkpoint to `retired`."
    payload["retired"] = True
    payload["removed_paths"] = [path for path in owned_dirty if any(path == root or path.startswith(f"{root}/") for root in OWNED_TEMP_ROOTS)]
    return emit(payload)


def handle_purity(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        payload = {
            "command": "purity-check",
            "result": "block",
            "summary": "purity-check could not read a valid Loom fact chain.",
            "missing_inputs": [f"fact-chain: {message}" for message in errors],
            "fallback_to": "admission",
            "purity": {
                "state": "failed",
                "hard_failures": [f"fact-chain: {message}" for message in errors],
                "report_only": [
                    "branch purity is report-only in v1",
                    "PR purity is report-only in v1",
                ],
            },
        }
        return emit(payload)

    purity = purity_report_from_context(context)
    result = "pass" if not purity["hard_failures"] else "block"
    summary = "workspace purity is compatible with continued execution." if result == "pass" else "workspace purity requires cleanup or re-scoping before review."
    payload = {
        "command": "purity-check",
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
        },
        "checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": context["current_checkpoint"],
        },
        "purity": purity,
        "result": result,
        "summary": summary,
        "missing_inputs": list(purity["hard_failures"]),
        "fallback_to": "admission" if purity["hard_failures"] else None,
    }
    return emit(payload)


def handle_fact_chain(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    report, errors = load_fact_chain_report(target_root, args.output)
    if errors:
        return emit(
            {
                "command": "fact-chain",
                "result": "block",
                "summary": "fact-chain command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )

    item_id = report["fact_chain"]["entry_points"]["current_item_id"]
    if args.item and args.item != item_id:
        return emit(
            {
                "command": "fact-chain",
                "result": "block",
                "summary": "fact-chain command found an item mismatch.",
                "missing_inputs": [f"current item mismatch: expected `{args.item}`, got `{item_id}`"],
                "fallback_to": "admission",
            }
        )

    return emit(
        {
            "command": "fact-chain",
            "result": "pass",
            "summary": "fact chain can be read and validated from a single entry.",
            "missing_inputs": [],
            "fallback_to": None,
            "report": report,
        }
    )


def runtime_evidence_from_report(report: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    runtime_evidence = report.get("runtime_evidence")
    missing_inputs: list[str] = []
    fields: dict[str, Any] = {}
    if not isinstance(runtime_evidence, dict):
        missing_inputs.append("runtime_evidence is missing from fact-chain report")
        return fields, missing_inputs

    for key in RUNTIME_EVIDENCE_FIELDS:
        entry = runtime_evidence.get(key)
        if not isinstance(entry, dict):
            missing_inputs.append(f"runtime_evidence.{key} is missing")
            continue
        value = entry.get("value")
        status = entry.get("status")
        if not isinstance(value, str) or not value.strip():
            missing_inputs.append(f"runtime_evidence.{key}.value must be a non-empty string")
        if status not in {"present", "not_applicable"}:
            missing_inputs.append(f"runtime_evidence.{key}.status must be `present` or `not_applicable`")
        elif status == "present" and value == "not_applicable":
            missing_inputs.append(f"runtime_evidence.{key} is `present` but uses `not_applicable`")
        elif status == "not_applicable" and value != "not_applicable":
            missing_inputs.append(f"runtime_evidence.{key} is `not_applicable` but value is `{value}`")
        fields[key] = {
            "value": value,
            "status": status,
            "source": entry.get("source"),
        }
    return fields, missing_inputs


def handle_runtime_evidence(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    report, errors = load_fact_chain_report(target_root, args.output)
    if errors:
        return emit(
            {
                "command": "runtime-evidence",
                "result": "block",
                "summary": "runtime-evidence command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )

    item_id = report["fact_chain"]["entry_points"]["current_item_id"]
    if args.item and args.item != item_id:
        return emit(
            {
                "command": "runtime-evidence",
                "result": "block",
                "summary": "runtime-evidence command found an item mismatch.",
                "missing_inputs": [f"current item mismatch: expected `{args.item}`, got `{item_id}`"],
                "fallback_to": "admission",
            }
        )

    fields, missing_inputs = runtime_evidence_from_report(report)

    result = "pass" if not missing_inputs else "block"
    summary = (
        "runtime evidence entries are readable and distinguish `present` from `not_applicable`."
        if result == "pass"
        else "runtime evidence entries are incomplete or inconsistent."
    )
    return emit(
        {
            "command": "runtime-evidence",
            "item_id": item_id,
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": "admission" if missing_inputs else None,
            "runtime_evidence": fields,
        }
    )


def state_check_payload(context: dict[str, Any]) -> dict[str, Any]:
    purity = purity_report_from_context(context)
    active_state_failures: list[str] = []
    checkpoint_failures: list[str] = []
    scope_failures: list[str] = []

    current_checkpoint = context["current_checkpoint"]
    if current_checkpoint in TERMINAL_CHECKPOINTS:
        active_state_failures.append(f"current checkpoint is terminal: `{current_checkpoint}`")

    active_conflicts = active_workspace_conflicts(context["target_root"], context["item_id"], context["workspace_entry"])
    if active_conflicts:
        active_state_failures.append(
            "workspace is shared by multiple active items: " + ", ".join(sorted(active_conflicts))
        )

    known_checkpoints = {"admission", "build", "merge", "retired"} | TERMINAL_CHECKPOINTS
    if current_checkpoint not in known_checkpoints:
        checkpoint_failures.append(f"unknown checkpoint value: `{context['current_checkpoint_raw']}`")
    if current_checkpoint in {"admission", "build", "merge"}:
        for field_name in ("current_stop", "next_step", "latest_validation_summary", "recovery_boundary", "current_lane"):
            value = str(context[field_name]).strip()
            if not value:
                checkpoint_failures.append(f"checkpoint integrity missing `{field_name}`")

    scope_assessment = purity.get("scope_assessment")
    if isinstance(scope_assessment, dict):
        out_of_scope_changes = scope_assessment.get("out_of_scope_changes")
        if isinstance(out_of_scope_changes, list) and out_of_scope_changes:
            preview = ", ".join(out_of_scope_changes[:5])
            scope_failures.append(f"out-of-scope changes detected: {preview}")

    missing_inputs: list[str] = []
    for collection in (purity["hard_failures"], active_state_failures, checkpoint_failures, scope_failures):
        for message in collection:
            if message not in missing_inputs:
                missing_inputs.append(message)

    result = "pass" if not missing_inputs else "block"
    summary = (
        "active state, checkpoint integrity, and scope signals are consistent."
        if result == "pass"
        else "state-check found active-state conflicts, checkpoint gaps, or scope overflow signals."
    )
    return {
        "command": "state-check",
        "item": {
            "id": context["item_id"],
            "goal": context["goal"],
            "scope": context["scope"],
            "execution_path": context["execution_path"],
        },
        "checkpoint": {
            "raw": context["current_checkpoint_raw"],
            "normalized": current_checkpoint,
        },
        "workspace": {
            "entry": context["workspace_entry"],
            "path": relative_to_root(context["workspace_path"], context["target_root"]),
        },
        "checks": {
            "active_state_failures": active_state_failures,
            "checkpoint_failures": checkpoint_failures,
            "scope_failures": scope_failures,
        },
        "purity": purity,
        "result": result,
        "summary": summary,
        "missing_inputs": missing_inputs,
        "fallback_to": "admission" if missing_inputs else None,
    }


def handle_state_check(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "state-check",
                "result": "block",
                "summary": "state-check could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
            }
        )
    return emit(state_check_payload(context))


def handle_flow(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    context, errors = load_context(target_root, args.output, args.item)
    if errors:
        return emit(
            {
                "command": "flow",
                "operation": args.operation,
                "result": "block",
                "summary": "flow command could not read a valid Loom fact chain.",
                "missing_inputs": [f"fact-chain: {message}" for message in errors],
                "fallback_to": "admission",
                "steps": [],
            }
        )

    if args.operation not in {"pre-review", "resume", "handoff", "merge-ready"}:
        return emit(
            {
                "command": "flow",
                "operation": args.operation,
                "result": "block",
                "summary": f"unsupported flow operation: {args.operation}",
                "missing_inputs": [f"unsupported operation: {args.operation}"],
                "fallback_to": None,
                "steps": [],
            }
        )

    steps: list[dict[str, Any]] = [
        {
            "name": "fact-chain",
            "result": "pass",
            "summary": "fact chain is readable from a single entry.",
            "missing_inputs": [],
            "fallback_to": None,
        }
    ]

    state_payload = state_check_payload(context)
    steps.append(
        {
            "name": "state-check",
            "result": state_payload["result"],
            "summary": state_payload["summary"],
            "missing_inputs": state_payload["missing_inputs"],
            "fallback_to": state_payload["fallback_to"],
        }
    )

    if args.operation in {"resume", "handoff"}:
        locate_payload = base_workspace_payload(context, "locate")
        locate_result = "pass" if not locate_payload["purity"]["hard_failures"] else "block"
        locate_step = {
            "name": "workspace-locate",
            "result": locate_result,
            "summary": (
                "workspace is location-resolved and execution-ready."
                if locate_result == "pass"
                else "workspace is location-resolved but not execution-ready."
            ),
            "missing_inputs": list(locate_payload["purity"]["hard_failures"]),
            "fallback_to": "admission" if locate_payload["purity"]["hard_failures"] else None,
        }
        steps.append(locate_step)
    else:
        runtime_fields, runtime_missing = runtime_evidence_from_report(context["report"])
        runtime_result = "pass" if not runtime_missing else "block"
        steps.append(
            {
                "name": "runtime-evidence",
                "result": runtime_result,
                "summary": (
                    "runtime evidence entries are readable."
                    if runtime_result == "pass"
                    else "runtime evidence entries are incomplete or inconsistent."
                ),
                "missing_inputs": runtime_missing,
                "fallback_to": "admission" if runtime_missing else None,
                "runtime_evidence": runtime_fields,
            }
        )
        if args.operation == "merge-ready":
            build_payload = checkpoint_payload("build", context)
            merge_payload = checkpoint_payload("merge", context)
            steps.extend(
                [
                    {
                        "name": "checkpoint-build",
                        "result": build_payload["result"],
                        "summary": build_payload["summary"],
                        "missing_inputs": build_payload["missing_inputs"],
                        "fallback_to": build_payload["fallback_to"],
                    },
                    {
                        "name": "checkpoint-merge",
                        "result": merge_payload["result"],
                        "summary": merge_payload["summary"],
                        "missing_inputs": merge_payload["missing_inputs"],
                        "fallback_to": merge_payload["fallback_to"],
                    },
                ]
            )
        else:
            admission_payload = checkpoint_payload("admission", context)
            locate_payload = base_workspace_payload(context, "locate")
            locate_result = "pass" if not locate_payload["purity"]["hard_failures"] else "block"
            locate_step = {
                "name": "workspace-locate",
                "result": locate_result,
                "summary": (
                    "workspace is location-resolved and execution-ready."
                    if locate_result == "pass"
                    else "workspace is location-resolved but not execution-ready."
                ),
                "missing_inputs": list(locate_payload["purity"]["hard_failures"]),
                "fallback_to": "admission" if locate_payload["purity"]["hard_failures"] else None,
            }
            steps.append(
                {
                    "name": "checkpoint-admission",
                    "result": admission_payload["result"],
                    "summary": admission_payload["summary"],
                    "missing_inputs": admission_payload["missing_inputs"],
                    "fallback_to": admission_payload["fallback_to"],
                }
            )
            steps.append(locate_step)

    result = "pass"
    fallback_to: str | None = None
    for step in steps:
        step_result = step["result"]
        if step_result == "fallback":
            result = "fallback"
            fallback_to = step.get("fallback_to") or "admission"
            break
        if step_result == "block" and result == "pass":
            result = "block"
            fallback_to = step.get("fallback_to")

    if args.operation == "resume":
        summary = (
            "resume flow rebuilt the current execution context and next step."
            if result == "pass"
            else "resume flow rebuilt context but found blocking signals before execution can continue."
        )
    elif args.operation == "handoff":
        summary = (
            "handoff flow produced the minimum writeback checklist and locator set."
            if result == "pass"
            else "handoff flow produced the minimum writeback checklist, but blocking signals remain before transfer."
        )
    elif args.operation == "merge-ready":
        summary = (
            "merge-ready flow found the required evidence and checkpoint state for host merge."
            if result == "pass"
            else "merge-ready flow found fallback or blocking signals before host merge."
        )
    else:
        summary = (
            "pre-review flow is ready to proceed."
            if result == "pass"
            else "pre-review flow found blocking signals before review."
        )
    missing_inputs: list[str] = []
    for step in steps:
        if step["result"] in {"block", "fallback"}:
            for message in step.get("missing_inputs", []):
                if message not in missing_inputs:
                    missing_inputs.append(message)

    return emit(
        {
            "command": "flow",
            "operation": args.operation,
            "item": {
                "id": context["item_id"],
                "goal": context["goal"],
                "scope": context["scope"],
                "execution_path": context["execution_path"],
            },
            "result": result,
            "summary": summary,
            "missing_inputs": missing_inputs,
            "fallback_to": fallback_to,
            "steps": steps,
            **(
                {
                    "workspace": {
                        "entry": locate_payload["workspace"]["entry"],
                        "path": locate_payload["workspace"]["path"],
                        "exists": locate_payload["workspace"]["exists"],
                    },
                    "checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                }
                if args.operation in {"resume", "handoff"}
                else {}
            ),
            **(
                {
                    "recovery": {
                        "path": locate_payload["recovery"]["path"],
                        "current_stop": locate_payload["recovery"]["current_stop"],
                        "next_step": context["next_step"],
                        "blockers": context["blockers"],
                        "latest_validation_summary": context["latest_validation_summary"],
                    },
                }
                if args.operation == "resume"
                else {}
            ),
            **(
                {
                    "recovery_entry": str(context["report"]["fact_chain"]["entry_points"]["recovery_entry"]),
                    "status_surface": str(context["report"]["fact_chain"]["entry_points"]["status_surface"]),
                    "current_stop": context["current_stop"],
                    "next_step": context["next_step"],
                    "blockers": context["blockers"],
                    "latest_validation_summary": context["latest_validation_summary"],
                    "fallback_target": fallback_to,
                    "writeback_fields": [
                        "current_stop",
                        "next_step",
                        "blockers",
                        "latest_validation_summary",
                    ],
                }
                if args.operation == "handoff"
                else {}
            ),
            **(
                {
                    "state_check": {
                        "result": state_payload["result"],
                        "summary": state_payload["summary"],
                        "missing_inputs": state_payload["missing_inputs"],
                        "fallback_to": state_payload["fallback_to"],
                        "checks": state_payload["checks"],
                    },
                    "runtime_evidence": runtime_fields,
                    "build_checkpoint": {
                        "result": build_payload["result"],
                        "summary": build_payload["summary"],
                        "missing_inputs": build_payload["missing_inputs"],
                        "fallback_to": build_payload["fallback_to"],
                    },
                    "merge_checkpoint": {
                        "result": merge_payload["result"],
                        "summary": merge_payload["summary"],
                        "missing_inputs": merge_payload["missing_inputs"],
                        "fallback_to": merge_payload["fallback_to"],
                        "pr_template": merge_payload.get("pr_template"),
                    },
                    "current_checkpoint": {
                        "raw": context["current_checkpoint_raw"],
                        "normalized": context["current_checkpoint"],
                    },
                    "current_lane": context["current_lane"],
                    "latest_validation_summary": context["latest_validation_summary"],
                }
                if args.operation == "merge-ready"
                else {}
            ),
        }
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "fact-chain":
        return handle_fact_chain(args)
    if args.command == "runtime-evidence":
        return handle_runtime_evidence(args)
    if args.command == "state-check":
        return handle_state_check(args)
    if args.command == "flow":
        return handle_flow(args)
    if args.command == "checkpoint":
        return handle_checkpoint(args)
    if args.command == "workspace":
        return handle_workspace(args)
    return handle_purity(args)


if __name__ == "__main__":
    raise SystemExit(main())
