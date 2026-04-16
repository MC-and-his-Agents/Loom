#!/usr/bin/env python3
"""Minimal executable bootstrap entry for Loom adoption."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL_VERSION = "1.0.0"
CONTRACT_VERSION = "1.0.0"
WORK_ITEM_ID = "INIT-0001"

ROOT_BOUNDARY_FILES = (
    "AGENTS.md",
    "WORKFLOW.md",
    "docs/WORKFLOW.md",
)

CI_DIRS = (
    ".github/workflows",
    ".gitlab-ci.yml",
)

CODE_DIR_HINTS = (
    "src",
    "app",
    "lib",
    "cmd",
    "pkg",
)

GENERATED_ROOT_ENTRY = (
    "# Loom Root Entry\n\n"
    "This repository was initialized with Loom bootstrap artifacts.\n\n"
    "Read `.loom/README.md` first, then `.loom/bootstrap/init-result.json` "
    "for the current initialization truth.\n"
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap Loom into a target repository.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap", help="Analyze and optionally scaffold a target repo")
    bootstrap.add_argument("--target", required=True, help="Target repository root")
    bootstrap.add_argument(
        "--scenario",
        default="auto",
        choices=("auto", "new", "small-existing", "complex-existing"),
        help="Override scenario detection",
    )
    bootstrap.add_argument("--intake", help="Optional intake JSON file")
    bootstrap.add_argument(
        "--output",
        help="Output path for init-result.json relative to target root",
        default=".loom/bootstrap/init-result.json",
    )
    bootstrap.add_argument("--write", action="store_true", help="Write bootstrap artifacts into the target repo")
    bootstrap.add_argument("--verify", action="store_true", help="Verify written artifacts after scaffolding")
    bootstrap.add_argument("--force", action="store_true", help="Overwrite Loom-managed artifacts when needed")
    bootstrap.add_argument(
        "--install-pr-template",
        action="store_true",
        help="Install the Loom PR template when the target repo does not already provide one",
    )

    verify = subparsers.add_parser("verify", help="Verify Loom bootstrap artifacts in a target repo")
    verify.add_argument("--target", required=True, help="Target repository root")
    verify.add_argument(
        "--output",
        help="Expected init-result.json path relative to target root",
        default=".loom/bootstrap/init-result.json",
    )

    return parser.parse_args(argv)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_output_path(target_root: Path, raw_output: str) -> Path:
    output_path = Path(raw_output)
    if output_path.is_absolute():
        raise RuntimeError("--output must be relative to the target root")
    return target_root / output_path


def write_text(path: Path, content: str, force: bool) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == content:
            return False
        if not force:
            raise RuntimeError(f"refusing to overwrite existing file without --force: {path}")
    path.write_text(content, encoding="utf-8")
    return True


def write_json(path: Path, payload: object, force: bool) -> bool:
    return write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n", force=force)


def file_exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


@lru_cache(maxsize=None)
def bootstrap_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / ".loom/bootstrap/manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = read_json(manifest_path)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


@lru_cache(maxsize=None)
def generated_paths(root: Path) -> tuple[str, ...]:
    manifest = bootstrap_manifest(root)
    paths: set[str] = {".loom"}
    artifacts = manifest.get("artifacts")
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if isinstance(artifact, str) and artifact:
                paths.add(artifact)
    if file_exists(root, "AGENTS.md"):
        try:
            if (root / "AGENTS.md").read_text(encoding="utf-8") == GENERATED_ROOT_ENTRY:
                paths.add("AGENTS.md")
        except OSError:
            pass
    return tuple(sorted(paths))


def is_generated_path(root: Path, path: Path) -> bool:
    try:
        relative = str(path.relative_to(root))
    except ValueError:
        return False
    for generated in generated_paths(root):
        if relative == generated or relative.startswith(f"{generated}/"):
            return True
    return False


def count_meaningful_entries(root: Path) -> int:
    ignored = {".git", ".DS_Store"}
    count = 0
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.name == ".gitkeep":
            continue
        if is_generated_path(root, path):
            continue
        count += 1
    return count


def detect_root_boundary(root: Path) -> str:
    generated = generated_paths(root)
    if any(file_exists(root, candidate) and candidate not in generated for candidate in ROOT_BOUNDARY_FILES):
        return "clear"
    if file_exists(root, "README.md"):
        return "partial"
    return "missing"


def has_make_target(makefile_path: Path, targets: tuple[str, ...]) -> bool:
    if not makefile_path.exists():
        return False
    text = makefile_path.read_text(encoding="utf-8")
    return any(re.search(rf"^{re.escape(target)}\s*:", text, re.MULTILINE) for target in targets)


def detect_package_scripts(root: Path) -> dict[str, object]:
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    try:
        data = read_json(package_json)
    except json.JSONDecodeError:
        return {}
    scripts = data.get("scripts")
    return scripts if isinstance(scripts, dict) else {}


def detect_ci_or_tests(root: Path) -> bool:
    if any(file_exists(root, candidate) for candidate in CI_DIRS):
        return True
    if (root / "tests").exists() or (root / "test").exists():
        return True
    if has_make_target(root / "Makefile", ("test", "check", "lint", "loom-check")):
        return True
    scripts = detect_package_scripts(root)
    return any(name in scripts for name in ("test", "check", "lint"))


def detect_validation_entry(root: Path) -> bool:
    if has_make_target(root / "Makefile", ("check", "test", "lint", "loom-check")):
        return True
    if file_exists(root, "justfile") or file_exists(root, "Taskfile.yml"):
        return True
    scripts = detect_package_scripts(root)
    return any(name in scripts for name in ("check", "test", "lint"))


def detect_primary_gap(root: Path, root_boundary_docs: str, validation_entry: bool) -> str:
    if root_boundary_docs != "clear":
        return "governance"
    if not validation_entry:
        return "execution-support"
    if not file_exists(root, ".github/PULL_REQUEST_TEMPLATE.md"):
        return "review"
    if not (root / "specs").exists() and not (root / "docs/specs").exists():
        return "spec-path"
    return "execution-support"


def detect_recovery_pain(root: Path) -> bool:
    markers = (
        ".loom/progress",
        ".loom/work-items",
        "progress",
        "checkpoint",
        "exec-plan",
    )
    present = 0
    for marker in markers:
        if any(
            path
            for path in root.rglob("*")
            if not is_generated_path(root, path) and marker in str(path.relative_to(root))
        ):
            present += 1
    return present >= 2


def detect_shared_or_high_risk(root: Path) -> bool:
    hints = ("contract", "schema", "proto", "api", "sdk", "skills", "governance")
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if is_generated_path(root, path):
            continue
        lowered = path.name.lower()
        if any(hint in lowered for hint in hints):
            return True
    return False


def git_dirty_count(root: Path) -> int:
    if not (root / ".git").exists():
        return 0
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 0
    if result.returncode != 0:
        return 0
    return len([line for line in result.stdout.splitlines() if line.strip()])


def detect_purity(root: Path) -> str:
    dirty = git_dirty_count(root)
    if dirty >= 8:
        return "severe"
    if dirty >= 2:
        return "mixed"
    return "clean"


def detect_merge_review_overload(root: Path, validation_entry: bool) -> bool:
    code_dirs = sum(1 for hint in CODE_DIR_HINTS if (root / hint).exists())
    if code_dirs == 0:
        return False
    if not validation_entry and not file_exists(root, ".github/PULL_REQUEST_TEMPLATE.md"):
        return True
    return False


def detect_repository_type(root: Path) -> str:
    meaningful_entries = count_meaningful_entries(root)
    has_readme = file_exists(root, "README.md")
    has_code = any((root / hint).exists() and not is_generated_path(root, root / hint) for hint in CODE_DIR_HINTS)
    if meaningful_entries <= 2 and not has_readme and not has_code:
        return "new"
    return "existing"


def load_or_detect_intake(root: Path, intake_path: str | None) -> dict[str, object]:
    if intake_path:
        payload = read_json(Path(intake_path).expanduser().resolve())
        payload.setdefault("schema_version", "loom-init-intake/v1")
        return payload

    repository_type = detect_repository_type(root)
    root_boundary_docs = detect_root_boundary(root)
    validation_entry = detect_validation_entry(root)
    payload = {
        "schema_version": "loom-init-intake/v1",
        "repository_type": repository_type,
        "root_boundary_docs": root_boundary_docs,
        "ci_or_basic_tests": detect_ci_or_tests(root),
        "repository_level_validation_entry": validation_entry,
        "primary_gap_category": detect_primary_gap(root, root_boundary_docs, validation_entry),
        "long_running_recovery_pain": detect_recovery_pain(root),
        "shared_contract_or_high_risk_boundary": detect_shared_or_high_risk(root),
        "purity_or_scope_signals": detect_purity(root),
        "merge_review_semantic_overload": detect_merge_review_overload(root, validation_entry),
        "notes": "autodetected by loom_init.py",
    }
    return payload


def classify_scenario(intake: dict[str, object], override: str) -> str:
    if override != "auto":
        return override

    repository_type = intake["repository_type"]
    root_boundary_docs = intake["root_boundary_docs"]
    ci_or_basic_tests = bool(intake["ci_or_basic_tests"])
    validation_entry = bool(intake["repository_level_validation_entry"])
    primary_gap_category = str(intake["primary_gap_category"])
    recovery_pain = bool(intake["long_running_recovery_pain"])
    shared_boundary = bool(intake["shared_contract_or_high_risk_boundary"])
    purity = str(intake["purity_or_scope_signals"])
    merge_overload = bool(intake["merge_review_semantic_overload"])

    if repository_type == "new":
        return "new"
    if (
        root_boundary_docs == "clear"
        and ci_or_basic_tests
        and validation_entry
        and primary_gap_category in {"governance", "review", "spec-path"}
        and not recovery_pain
        and not shared_boundary
        and purity == "clean"
        and not merge_overload
    ):
        return "small-existing"
    return "complex-existing"


def scenario_label(scenario: str) -> str:
    return {
        "new": "新项目",
        "small-existing": "小型既有仓库",
        "complex-existing": "复杂既有仓库",
    }[scenario]


def intensity_label(scenario: str, intake: dict[str, object]) -> str:
    if scenario in {"new", "small-existing"}:
        return "轻量"
    if bool(intake["shared_contract_or_high_risk_boundary"]) or bool(intake["long_running_recovery_pain"]):
        return "强化"
    return "标准"


def integration_mode(scenario: str) -> str:
    return "root" if scenario == "new" else "companion"


def recovery_mode(scenario: str) -> str:
    return "checkpoint-lite" if scenario in {"new", "small-existing"} else "standard"


def rule_refs_for_capabilities(scenario: str) -> list[dict[str, object]]:
    common = [
        {
            "name": "bootstrap/root",
            "rules": [
                "skills/loom-init/SKILL.md",
                "skills/loom-init/references/intake-signals.md",
                "skills/loom-init/references/output-contract.md",
            ],
        },
        {
            "name": "formal-templates",
            "rules": [
                "templates/spec-suite.md",
                "templates/pull-request.md",
            ],
        },
    ]
    if scenario == "new":
        common.append(
            {
                "name": "minimal-governance-entry",
                "rules": [
                    "governance/principles.md",
                    "governance/review-model.md",
                ],
            }
        )
    elif scenario == "small-existing":
        common.append(
            {
                "name": "lightweight-retrofit",
                "rules": [
                    "adoption/lightweight-retrofit-default.md",
                    "adoption/routing-and-checkpoints.md",
                ],
            }
        )
    else:
        common.append(
            {
                "name": "execution-support",
                "rules": [
                    "harness/work-item-contract.md",
                    "harness/recovery-model.md",
                    "harness/status-surface.md",
                    "harness/workspace-and-purity.md",
                ],
            }
        )
    return common


def deferred_capabilities(scenario: str) -> list[dict[str, str]]:
    if scenario == "new":
        return [
            {
                "name": "full-status-surface",
                "reason": "no runnable system or multi-lane environment is visible yet",
                "upgrade_trigger": "a runtime lane, logs, metrics, or UI verification path becomes required",
            },
            {
                "name": "merge-checkpoint-hardening",
                "reason": "implementation has not entered regular merge flow yet",
                "upgrade_trigger": "multiple contributors or repeated merge reviews begin to consume the same facts",
            },
        ]
    if scenario == "small-existing":
        return [
            {
                "name": "standard-recovery",
                "reason": "the repo still fits checkpoint-lite for low-cost recovery",
                "upgrade_trigger": "recovery spans multiple rounds or more than one status carrier starts competing",
            },
            {
                "name": "full-workspace-purity",
                "reason": "lightweight retrofit is still the default path",
                "upgrade_trigger": "mixed work, shared boundaries, or review overload becomes structural",
            },
        ]
    return [
        {
            "name": "host-specific-skill-regression-matrix",
            "reason": "Loom core should not absorb a full host test matrix",
            "upgrade_trigger": "a host adapter or marketplace package is added",
        }
    ]


def initial_work_items(scenario: str, target_root: Path) -> list[dict[str, object]]:
    checkpoint = "commit checkpoint" if scenario != "complex-existing" else "build checkpoint"
    artifacts = [
        ".loom/bootstrap/init-result.json",
        ".loom/work-items/INIT-0001.md",
        ".loom/progress/INIT-0001.md",
        ".loom/specs/INIT-0001/spec.md",
        ".loom/specs/INIT-0001/plan.md",
    ]
    if not (target_root / ".github/PULL_REQUEST_TEMPLATE.md").exists():
        artifacts.append(".github/PULL_REQUEST_TEMPLATE.md")
    return [
        {
            "id": WORK_ITEM_ID,
            "goal": "Bootstrap the first executable Loom path for this repository",
            "scope": "Establish rule entry, first work item, progress carrier, spec/plan, and verification entry",
            "execution_path": "bootstrap/root",
            "artifacts": artifacts,
            "closing_condition": "The generated entry, work item, progress carrier, and templates are readable and verified",
            "checkpoint": checkpoint,
            "post_build_continuation": "Promote the first real downstream issue after the bootstrap artifacts are accepted",
            "owner_for_checkpoint_lite": "repository owner or current bootstrap operator",
        }
    ]


def initial_artifacts(target_root: Path, install_pr_template: bool) -> list[dict[str, str]]:
    artifacts = [
        {
            "path": "AGENTS.md",
            "kind": "root-entry",
            "source": "generated",
        },
        {
            "path": ".loom/README.md",
            "kind": "rule-entry",
            "source": "generated",
        },
        {
            "path": ".loom/bootstrap/intake.snapshot.json",
            "kind": "intake",
            "source": "generated",
        },
        {
            "path": ".loom/bootstrap/init-result.json",
            "kind": "init-result",
            "source": "generated",
        },
        {
            "path": ".loom/bootstrap/manifest.json",
            "kind": "manifest",
            "source": "generated",
        },
        {
            "path": ".loom/bootstrap/capability-map.md",
            "kind": "capability-map",
            "source": "generated",
        },
        {
            "path": ".loom/work-items/INIT-0001.md",
            "kind": "work-item",
            "source": "generated",
        },
        {
            "path": ".loom/progress/INIT-0001.md",
            "kind": "progress",
            "source": "generated",
        },
        {
            "path": ".loom/status/current.md",
            "kind": "status-surface",
            "source": "generated",
        },
        {
            "path": ".loom/specs/INIT-0001/spec.md",
            "kind": "spec",
            "source": "templates/scaffold/spec.md",
        },
        {
            "path": ".loom/specs/INIT-0001/plan.md",
            "kind": "plan",
            "source": "templates/scaffold/plan.md",
        },
    ]
    if install_pr_template or not (target_root / ".github/PULL_REQUEST_TEMPLATE.md").exists():
        artifacts.append(
            {
                "path": ".github/PULL_REQUEST_TEMPLATE.md",
                "kind": "pr-template",
                "source": ".github/PULL_REQUEST_TEMPLATE.md",
            }
        )
    return artifacts


def build_result(target_root: Path, scenario: str, intake: dict[str, object], install_pr_template: bool) -> dict[str, object]:
    main_problem = {
        "new": "the repository has no controlled Loom entry yet",
        "small-existing": "the repo has a baseline but still lacks a stable Loom adoption entry and explicit first artifacts",
        "complex-existing": "the repo needs execution support, recovery, and status carriers instead of more ad hoc guidance",
    }[scenario]

    reason = {
        "new": "the repo is still establishing its first baseline, so the bootstrap should create the smallest stable entry and first artifacts",
        "small-existing": "the repo already has a baseline, so Loom should enter through companion artifacts instead of rewriting the root",
        "complex-existing": "the repo shows execution-support pressure, so the bootstrap must materialize recovery and status carriers immediately",
    }[scenario]

    result = {
        "schema_version": "loom-init-output/v1",
        "generator": {
            "tool": "tools/loom_init.py",
            "tool_version": TOOL_VERSION,
            "root_entry": "loom-init",
            "contract_version": CONTRACT_VERSION,
        },
        "run": {
            "target": str(target_root),
            "scenario": scenario_label(scenario),
            "scenario_key": scenario,
            "integration_mode": integration_mode(scenario),
            "recovery_mode": recovery_mode(scenario),
        },
        "intake": intake,
        "project_judgment": {
            "scenario": scenario_label(scenario),
            "intensity": intensity_label(scenario, intake),
            "primary_structural_problem": main_problem,
            "why_this_path": reason,
        },
        "recommended_adoption": {
            "path": {
                "new": "minimal-bootstrap",
                "small-existing": "lightweight-retrofit",
                "complex-existing": "full-bootstrap",
            }[scenario],
            "integration_mode": integration_mode(scenario),
            "recovery_mode": recovery_mode(scenario),
            "capabilities": rule_refs_for_capabilities(scenario),
        },
        "deferred_capabilities": deferred_capabilities(scenario),
        "initial_artifacts": initial_artifacts(target_root, install_pr_template),
        "initial_work_items": initial_work_items(scenario, target_root),
        "validation_and_closing": {
            "validation_entry": "python3 tools/loom_init.py verify --target <repo> && make loom-check",
            "checkpoint_relationship": [
                "commit checkpoint confirms the bootstrap work item and first artifacts are readable",
                "build checkpoint confirms generated carriers and templates are internally consistent",
                "merge checkpoint should only pass after downstream repo truth, docs, and delivery state align",
            ],
            "clean_state": "all generated Loom artifacts are readable, verified, and free of conflicting duplicates",
            "close_when": [
                "the target repo has a readable root or companion Loom entry",
                "the first work item, progress carrier, and spec/plan artifacts exist",
                "the bootstrap manifest and init-result are verifiable",
            ],
        },
    }
    return result


def render_loom_readme(result: dict[str, object]) -> str:
    run = result["run"]
    return (
        "# Loom Bootstrap\n\n"
        "This directory was generated by `tools/loom_init.py`.\n\n"
        "## Current Path\n\n"
        f"- Scenario: {run['scenario']}\n"
        f"- Integration mode: {run['integration_mode']}\n"
        f"- Recovery mode: {run['recovery_mode']}\n\n"
        "## Main Entry Points\n\n"
        "- Bootstrap manifest: `.loom/bootstrap/manifest.json`\n"
        "- Bootstrap result: `.loom/bootstrap/init-result.json`\n"
        "- First work item: `.loom/work-items/INIT-0001.md`\n"
        "- Progress carrier: `.loom/progress/INIT-0001.md`\n"
        "- Status surface: `.loom/status/current.md`\n"
    )


def render_root_agents() -> str:
    return GENERATED_ROOT_ENTRY


def render_capability_map(result: dict[str, object]) -> str:
    lines = [
        "# Capability Map",
        "",
        "The bootstrap entry maps each enabled capability to Loom source-of-truth documents.",
        "",
    ]
    for capability in result["recommended_adoption"]["capabilities"]:
        lines.append(f"## {capability['name']}")
        lines.append("")
        for rule in capability["rules"]:
            lines.append(f"- `{rule}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_work_item(result: dict[str, object]) -> str:
    item = result["initial_work_items"][0]
    run = result["run"]
    return (
        f"# {item['id']}\n\n"
        "## Goal\n\n"
        f"- {item['goal']}\n\n"
        "## Scope\n\n"
        f"- {item['scope']}\n\n"
        "## Execution Path\n\n"
        f"- {item['execution_path']}\n"
        f"- Integration mode: {run['integration_mode']}\n"
        f"- Recovery mode: {run['recovery_mode']}\n\n"
        "## Associated Artifacts\n\n"
        + "\n".join(f"- `{artifact}`" for artifact in item["artifacts"])
        + "\n\n## Checkpoint Status\n\n"
        f"- Current checkpoint: {item['checkpoint']}\n"
        f"- Continue after build checkpoint: {item['post_build_continuation']}\n\n"
        "## Closing Condition\n\n"
        f"- {item['closing_condition']}\n"
    )


def render_progress(result: dict[str, object]) -> str:
    item = result["initial_work_items"][0]
    return (
        f"# {item['id']} Progress\n\n"
        "## Current Stop\n\n"
        "- Bootstrap artifacts have been generated and are awaiting downstream review.\n\n"
        "## Next Step\n\n"
        "- Accept the generated Loom entry and promote the first real repository work item.\n\n"
        "## Checkpoint\n\n"
        f"- Current checkpoint: {item['checkpoint']}\n\n"
        "## Verified Facts\n\n"
        "- Bootstrap manifest exists.\n"
        "- Init-result JSON can be read mechanically.\n"
        "- The first work item, status surface, and spec/plan artifacts exist.\n\n"
        "## Blockers\n\n"
        "- None recorded yet.\n\n"
        "## Recovery Boundary\n\n"
        "- Bootstrap result: `.loom/bootstrap/init-result.json`\n"
        "- Bootstrap manifest: `.loom/bootstrap/manifest.json`\n"
    )


def render_status(result: dict[str, object]) -> str:
    run = result["run"]
    return (
        "# Current Status\n\n"
        f"- Scenario: {run['scenario']}\n"
        "- Runtime evidence: not_applicable\n"
        "- Validation lane: bootstrap verification only\n"
        "- Latest recovery source: `.loom/progress/INIT-0001.md`\n"
    )


def copy_file(source: Path, target: Path, force: bool) -> bool:
    target.parent.mkdir(parents=True, exist_ok=True)
    content = source.read_text(encoding="utf-8")
    return write_text(target, content, force=force)


def manifest_payload(result: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "loom-bootstrap-manifest/v1",
        "tool": "tools/loom_init.py",
        "tool_version": TOOL_VERSION,
        "root_entry": "loom-init",
        "contract_version": CONTRACT_VERSION,
        "output": ".loom/bootstrap/init-result.json",
        "artifacts": [artifact["path"] for artifact in result["initial_artifacts"]],
    }


def scaffold_target(
    target_root: Path,
    result: dict[str, object],
    output_path: Path,
    force: bool,
    install_pr_template: bool,
) -> tuple[int, list[str]]:
    written = 0
    touched: list[str] = []

    writes: list[tuple[Path, str | dict[str, object], str]] = [
        (target_root / ".loom/README.md", render_loom_readme(result), "text"),
        (target_root / ".loom/bootstrap/intake.snapshot.json", result["intake"], "json"),
        (output_path, result, "json"),
        (target_root / ".loom/bootstrap/manifest.json", manifest_payload(result), "json"),
        (target_root / ".loom/bootstrap/capability-map.md", render_capability_map(result), "text"),
        (target_root / ".loom/work-items/INIT-0001.md", render_work_item(result), "text"),
        (target_root / ".loom/progress/INIT-0001.md", render_progress(result), "text"),
        (target_root / ".loom/status/current.md", render_status(result), "text"),
    ]

    for path, payload, kind in writes:
        changed = write_json(path, payload, force=force) if kind == "json" else write_text(path, payload, force=force)
        if changed:
            written += 1
            touched.append(str(path.relative_to(target_root)))

    for source, destination in (
        (ROOT / "templates/scaffold/spec.md", target_root / ".loom/specs/INIT-0001/spec.md"),
        (ROOT / "templates/scaffold/plan.md", target_root / ".loom/specs/INIT-0001/plan.md"),
    ):
        if copy_file(source, destination, force=force):
            written += 1
            touched.append(str(destination.relative_to(target_root)))

    pr_template_target = target_root / ".github/PULL_REQUEST_TEMPLATE.md"
    if install_pr_template or not pr_template_target.exists():
        if copy_file(ROOT / ".github/PULL_REQUEST_TEMPLATE.md", pr_template_target, force=force):
            written += 1
            touched.append(str(pr_template_target.relative_to(target_root)))

    root_agents = target_root / "AGENTS.md"
    if not root_agents.exists():
        if write_text(root_agents, render_root_agents(), force=force):
            written += 1
            touched.append(str(root_agents.relative_to(target_root)))

    return written, touched


def verify_target(target_root: Path, output_path: Path) -> list[str]:
    required_paths = [
        "AGENTS.md",
        ".loom/README.md",
        ".loom/bootstrap/intake.snapshot.json",
        str(output_path.relative_to(target_root)),
        ".loom/bootstrap/manifest.json",
        ".loom/bootstrap/capability-map.md",
        ".loom/work-items/INIT-0001.md",
        ".loom/progress/INIT-0001.md",
        ".loom/status/current.md",
        ".loom/specs/INIT-0001/spec.md",
        ".loom/specs/INIT-0001/plan.md",
    ]
    errors: list[str] = []
    for relative in required_paths:
        if not (target_root / relative).exists():
            errors.append(f"missing required artifact: {relative}")

    if output_path.exists():
        try:
            result = read_json(output_path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid init-result JSON: {exc.msg}")
            return errors
        for key in (
            "project_judgment",
            "recommended_adoption",
            "deferred_capabilities",
            "initial_artifacts",
            "initial_work_items",
            "validation_and_closing",
        ):
            if key not in result:
                errors.append(f"init-result is missing required section: {key}")
        initial_artifacts = result.get("initial_artifacts")
        if isinstance(initial_artifacts, list):
            for artifact in initial_artifacts:
                if not isinstance(artifact, dict):
                    errors.append("every initial artifact must be an object")
                    continue
                artifact_path = artifact.get("path")
                if not isinstance(artifact_path, str) or not artifact_path:
                    errors.append("every initial artifact must declare a non-empty `path`")
                    continue
                if not (target_root / artifact_path).exists():
                    errors.append(f"declared initial artifact is missing on disk: {artifact_path}")
        initial_work_items = result.get("initial_work_items")
        if isinstance(initial_work_items, list):
            for work_item in initial_work_items:
                if not isinstance(work_item, dict):
                    errors.append("every initial work item must be an object")
                    continue
                for field in ("id", "goal", "scope", "execution_path", "closing_condition", "checkpoint"):
                    value = work_item.get(field)
                    if not isinstance(value, str) or not value:
                        errors.append(f"initial work item is missing required field: {field}")

    pr_template = target_root / ".github/PULL_REQUEST_TEMPLATE.md"
    if pr_template.exists():
        text = pr_template.read_text(encoding="utf-8")
        for needle in ("## Summary", "## Validation", "## Risks And Follow-ups", "## Related Work"):
            if needle not in text:
                errors.append(f"PR template is missing section: {needle}")

    return errors


def bootstrap(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    if not target_root.exists():
        print(f"loom-init: target does not exist: {target_root}", file=sys.stderr)
        return 2
    if not target_root.is_dir():
        print(f"loom-init: target is not a directory: {target_root}", file=sys.stderr)
        return 2

    intake = load_or_detect_intake(target_root, args.intake)
    scenario = classify_scenario(intake, args.scenario)
    result = build_result(target_root, scenario, intake, args.install_pr_template)
    try:
        output_path = resolve_output_path(target_root, args.output)
    except RuntimeError as exc:
        print(f"loom-init: {exc}", file=sys.stderr)
        return 2

    if args.write:
        try:
            written, touched = scaffold_target(
                target_root=target_root,
                result=result,
                output_path=output_path,
                force=args.force,
                install_pr_template=args.install_pr_template,
            )
        except RuntimeError as exc:
            print(f"loom-init: {exc}", file=sys.stderr)
            return 2
        result["write"] = {
            "enabled": True,
            "written_files": written,
            "touched": touched,
        }
        if args.verify:
            errors = verify_target(target_root, output_path)
            result["verification"] = {"ok": not errors, "errors": errors}
            if errors:
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 1
    else:
        result["write"] = {"enabled": False, "written_files": 0, "touched": []}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    target_root = Path(args.target).expanduser().resolve()
    try:
        output_path = resolve_output_path(target_root, args.output)
    except RuntimeError as exc:
        print(f"loom-init: {exc}", file=sys.stderr)
        return 2
    errors = verify_target(target_root, output_path)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "target": str(target_root)}, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.command == "bootstrap":
        return bootstrap(args)
    return verify(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
