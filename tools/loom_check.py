#!/usr/bin/env python3
"""Minimal Loom repository mechanical self-check."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from fact_chain_support import inspect_fact_chain

TOP_LEVEL_DIRS = (
    "adoption",
    "docs",
    "governance",
    "harness",
    "skills",
    "templates",
)

TOP_LEVEL_FILES = (
    "AGENTS.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "VISION.md",
    "governance-design.md",
    "harness-design.md",
    "system-design.md",
)

AREA_READMES = (
    "adoption/README.md",
    "governance/README.md",
    "harness/README.md",
    "skills/README.md",
    "templates/README.md",
)

CORE_DOCS = (
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/loom-check.yml",
    "docs/roadmap.md",
    "docs/demo-new-project.md",
    "docs/complete-kernel-release.md",
    "governance/principles.md",
    "governance/review-model.md",
    "governance/maturity-and-closing.md",
    "harness/work-item-contract.md",
    "harness/fact-chain-contract.md",
    "harness/execution-context.md",
    "harness/execution-chain.md",
    "harness/daily-entry-matrix.md",
    "harness/checkpoint-model.md",
    "harness/workspace-model.md",
    "harness/workspace-lifecycle.md",
    "harness/recovery-model.md",
    "harness/status-surface.md",
    "harness/automation-frontload.md",
    "harness/merge-checkpoint.md",
    "harness/workspace-and-purity.md",
    "templates/spec-suite.md",
    "templates/pull-request.md",
    "adoption/extraction-ledger.md",
    "adoption/landing-map.md",
    "adoption/rationale.md",
    "adoption/routing-and-checkpoints.md",
    "adoption/lightweight-retrofit-default.md",
    "adoption/candidate-patterns.md",
    "adoption/demo-init-validation.md",
    "adoption/validation-record-contract.md",
    "adoption/experience-feedback-loop.md",
    "adoption/validation-new-project.md",
    "adoption/validation-devskills.md",
    "adoption/validation-hotcp.md",
    "adoption/validation-fact-chain-mail-listener.md",
    "adoption/validation-checkpoints-hotcp.md",
    "adoption/validation-workspace-lifecycle-hotcp.md",
    "adoption/validation-workspace-lifecycle-mail-listener.md",
    "adoption/validation-runtime-evidence-hotcp.md",
    "adoption/validation-automation-frontload-hotcp.md",
    "adoption/execution-entry-compatibility.md",
    "adoption/validation-complete-kernel-new-project.md",
    "adoption/validation-complete-kernel-existing-repos.md",
    "adoption/versioning-and-upgrades.md",
    "adoption/upstream-delivery-surface.md",
    "skills/distribution-and-adapter-contract.md",
    "skills/registry.json",
    "skills/upgrade-contract.json",
    "skills/route-matrix.md",
    "skills/loom-init/SKILL.md",
    "skills/loom-init/contract.json",
    "skills/loom-init/references/input-signals.md",
    "skills/loom-init/references/intake-signals.md",
    "skills/loom-init/references/output-contract.md",
    "templates/scaffold/spec.md",
    "templates/scaffold/plan.md",
    "tools/loom_init.py",
    "tools/loom_flow.py",
)

AUTOMATION_FRONTLOAD_TEMPLATES = (
    "templates/spec-suite.md",
    "templates/pull-request.md",
)

AUTOMATION_FRONTLOAD_SKILLS = (
    "skills/README.md",
    "skills/distribution-and-adapter-contract.md",
    "skills/route-matrix.md",
    "skills/loom-init/SKILL.md",
    "skills/loom-init/references/input-signals.md",
    "skills/loom-init/references/intake-signals.md",
    "skills/loom-init/references/output-contract.md",
)

AUTOMATION_FRONTLOAD_EXECUTION_SUPPORT = (
    "harness/work-item-contract.md",
    "harness/execution-context.md",
    "harness/execution-chain.md",
    "harness/daily-entry-matrix.md",
    "harness/checkpoint-model.md",
    "harness/workspace-model.md",
    "harness/workspace-lifecycle.md",
    "harness/recovery-model.md",
    "harness/status-surface.md",
    "harness/automation-frontload.md",
    "harness/merge-checkpoint.md",
    "harness/workspace-and-purity.md",
)

DEMO_ASSETS = (
    "examples/new-project/.gitkeep",
    "docs/demo-new-project.md",
    "examples/new-project/AGENTS.md",
    "examples/new-project/.loom/bootstrap/init-result.json",
    "examples/new-project/.loom/bootstrap/manifest.json",
    "examples/new-project/.loom/work-items/INIT-0001.md",
    "examples/new-project/.loom/progress/INIT-0001.md",
    "examples/new-project/.loom/status/current.md",
    "examples/new-project/.loom/bin/loom_init.py",
    "examples/new-project/.loom/bin/fact_chain_support.py",
    "examples/new-project/.loom/bin/loom_flow.py",
    "examples/new-project/.loom/specs/INIT-0001/spec.md",
    "examples/new-project/.loom/specs/INIT-0001/plan.md",
)

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$")
CODE_FENCE_RE = re.compile(r"^(```|~~~)")
EXTERNAL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


@dataclass(frozen=True)
class Failure:
    category: str
    detail: str


def repo_root_from_argv(argv: list[str]) -> Path:
    if len(argv) > 2:
        raise SystemExit("usage: loom_check.py [repo-root]")
    if len(argv) == 2:
        return Path(argv[1]).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def check_required_paths(root: Path, category: str, paths: tuple[str, ...]) -> list[Failure]:
    failures: list[Failure] = []
    for relative_path in paths:
        if not (root / relative_path).exists():
            failures.append(Failure(category, f"missing `{relative_path}`"))
    return failures


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def split_link_target(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip()
    if not target:
        return "", ""
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if " " in target:
        target = target.split(" ", 1)[0]
    if "#" in target:
        path_part, fragment = target.split("#", 1)
        return path_part, fragment
    return target, ""


def markdown_links(path: Path) -> list[tuple[int, str]]:
    results: list[tuple[int, str]] = []
    in_code_fence = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if CODE_FENCE_RE.match(line.strip()):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        for match in LINK_RE.finditer(line):
            results.append((line_no, match.group(1)))
    return results


def strip_inline_markdown(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    return text


def github_anchor_map(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    cached = cache.get(path)
    if cached is not None:
        return cached

    anchors: set[str] = set()
    duplicates: Counter[str] = Counter()
    in_code_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if CODE_FENCE_RE.match(stripped):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = github_slug(strip_inline_markdown(match.group(2)))
        if not base:
            continue
        duplicates[base] += 1
        anchor = base if duplicates[base] == 1 else f"{base}-{duplicates[base] - 1}"
        anchors.add(anchor)

    cache[path] = anchors
    return anchors


def github_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower().strip()
    slug_chars: list[str] = []
    last_was_dash = False
    for char in text:
        if char.isspace() or char == "-":
            if slug_chars and not last_was_dash:
                slug_chars.append("-")
                last_was_dash = True
            continue

        category = unicodedata.category(char)
        if category[0] in {"L", "N"} or category == "Mn":
            slug_chars.append(char)
            last_was_dash = False

    return "".join(slug_chars).strip("-")


def resolve_link_target(root: Path, source_path: Path, raw_target: str) -> tuple[Path | None, str]:
    target, fragment = split_link_target(raw_target)
    if not target:
        return source_path, fragment
    if EXTERNAL_SCHEME_RE.match(target) or target.startswith("//"):
        return None, ""
    if target.startswith("/"):
        return None, ""

    resolved = (source_path.parent / target).resolve()
    if resolved.exists():
        return resolved, fragment
    if resolved.is_dir():
        readme = resolved / "README.md"
        if readme.exists():
            return readme, fragment
    try:
        resolved.relative_to(root)
    except ValueError:
        return resolved, fragment
    return resolved, fragment


def check_markdown_links(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    anchor_cache: dict[Path, set[str]] = {}
    for markdown_path in iter_markdown_files(root):
        for line_no, raw_target in markdown_links(markdown_path):
            resolved, fragment = resolve_link_target(root, markdown_path, raw_target)
            if resolved is None:
                continue
            if not resolved.exists():
                detail = (
                    f"`{markdown_path.relative_to(root)}:{line_no}` -> `{raw_target}` "
                    f"(missing `{resolved.relative_to(root) if resolved.is_absolute() and is_within(resolved, root) else resolved}`)"
                )
                failures.append(Failure("markdown-links", detail))
                continue
            if fragment and resolved.suffix.lower() == ".md":
                anchors = github_anchor_map(resolved, anchor_cache)
                if fragment not in anchors:
                    detail = (
                        f"`{markdown_path.relative_to(root)}:{line_no}` -> `{raw_target}` "
                        f"(missing anchor `#{fragment}` in `{resolved.relative_to(root)}`)"
                    )
                    failures.append(Failure("markdown-links", detail))
    return failures


def load_json_file(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_command(root: Path, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd or root,
        check=False,
        capture_output=True,
        text=True,
    )


def load_command_json(
    root: Path,
    args: list[str],
    *,
    cwd: Path | None = None,
) -> tuple[dict[str, object] | None, str | None]:
    result = run_command(root, args, cwd=cwd)
    if not result.stdout.strip():
        detail = "command produced no JSON output"
        if result.stderr.strip():
            detail += f": {result.stderr.strip()}"
        return None, detail
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON output: {exc.msg}"
    if not isinstance(payload, dict):
        return None, "command output must be a JSON object"
    return payload, None


def check_skill_manifests(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    registry_path = root / "skills/registry.json"
    upgrade_contract_path = root / "skills/upgrade-contract.json"

    for candidate in (registry_path, upgrade_contract_path):
        if not candidate.exists():
            return failures

    try:
        registry = load_json_file(registry_path)
    except json.JSONDecodeError as exc:
        return [Failure("skill-manifests", f"`skills/registry.json` is invalid JSON: {exc.msg}")]

    try:
        upgrade_contract = load_json_file(upgrade_contract_path)
    except json.JSONDecodeError as exc:
        return [Failure("skill-manifests", f"`skills/upgrade-contract.json` is invalid JSON: {exc.msg}")]

    if not isinstance(registry, dict):
        failures.append(Failure("skill-manifests", "`skills/registry.json` must be a JSON object"))
        return failures
    if not isinstance(upgrade_contract, dict):
        failures.append(Failure("skill-manifests", "`skills/upgrade-contract.json` must be a JSON object"))
        return failures

    registry_version = registry.get("registry_version")
    root_entry = registry.get("root_entry")
    entries = registry.get("entries")
    upgrade_reference = registry.get("upgrade_contract")
    if registry_version != upgrade_contract.get("registry_version"):
        failures.append(Failure("skill-manifests", "`skills/upgrade-contract.json` registry version must match `skills/registry.json`"))
    if not isinstance(root_entry, str) or not root_entry:
        failures.append(Failure("skill-manifests", "`skills/registry.json` must declare a non-empty `root_entry`"))
        return failures
    if not isinstance(entries, list) or not entries:
        failures.append(Failure("skill-manifests", "`skills/registry.json` must declare at least one entry"))
        return failures
    if root_entry != "loom-init":
        failures.append(Failure("skill-manifests", "`skills/registry.json` root entry must remain `loom-init`"))

    root_registry_entry: dict[str, object] | None = None
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append(Failure("skill-manifests", "every registry entry must be an object"))
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            failures.append(Failure("skill-manifests", "every registry entry must declare a non-empty `id`"))
            continue
        if entry_id in seen_ids:
            failures.append(Failure("skill-manifests", f"registry declares duplicate entry `{entry_id}`"))
            continue
        seen_ids.add(entry_id)
        if entry_id == root_entry:
            root_registry_entry = entry

        for field in ("role", "contract_version", "manifest", "executable"):
            value = entry.get(field)
            if not isinstance(value, str) or not value:
                failures.append(Failure("skill-manifests", f"registry entry `{entry_id}` must declare `{field}`"))

        manifest_path = entry.get("manifest")
        if not isinstance(manifest_path, str) or not manifest_path:
            continue
        manifest_file = registry_path.parent / manifest_path
        if not manifest_file.exists():
            failures.append(Failure("skill-manifests", f"registry entry `{entry_id}` points to missing manifest `{manifest_path}`"))
            continue
        executable_path = entry.get("executable")
        if isinstance(executable_path, str) and executable_path:
            if not (registry_path.parent / executable_path).resolve().exists():
                failures.append(
                    Failure("skill-manifests", f"registry entry `{entry_id}` points to missing executable `{executable_path}`")
                )

        try:
            contract = load_json_file(manifest_file)
        except json.JSONDecodeError as exc:
            failures.append(Failure("skill-manifests", f"`{manifest_path}` is invalid JSON: {exc.msg}"))
            continue
        if not isinstance(contract, dict):
            failures.append(Failure("skill-manifests", f"`{manifest_path}` must be a JSON object"))
            continue

        if contract.get("id") != entry_id:
            failures.append(Failure("skill-manifests", f"`{manifest_path}` id must match registry entry `{entry_id}`"))
        if contract.get("role") != entry.get("role"):
            failures.append(Failure("skill-manifests", f"`{manifest_path}` role must match registry entry `{entry_id}`"))
        if contract.get("contract_version") != entry.get("contract_version"):
            failures.append(Failure("skill-manifests", f"`{manifest_path}` contract version must match registry entry `{entry_id}`"))

        contract_root = contract.get("root_entry")
        if entry_id == root_entry:
            if contract_root is not True:
                failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `root_entry: true`"))
        elif contract_root is not False:
            failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `root_entry: false`"))

        entrypoint = contract.get("entrypoint")
        if not isinstance(entrypoint, dict):
            failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `entrypoint`"))
        else:
            required_entrypoint_keys = {"skill_markdown", "adapter_metadata"}
            if entry_id == "loom-init":
                required_entrypoint_keys.add("bootstrap_cli")
                required_entrypoint_keys.add("route_cli")
            else:
                required_entrypoint_keys.add("orchestration_cli")
            for key in required_entrypoint_keys:
                value = entrypoint.get(key)
                if not isinstance(value, str) or not value:
                    failures.append(Failure("skill-manifests", f"`{manifest_path}` missing `entrypoint.{key}`"))
                    continue
                if not (manifest_file.parent / value).exists():
                    failures.append(Failure("skill-manifests", f"`{manifest_path}` points `entrypoint.{key}` to missing `{value}`"))

        for section in ("input_contract", "output_contract", "routing"):
            value = contract.get(section)
            if not isinstance(value, dict):
                failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `{section}`"))
                continue
            reference = value.get("reference")
            if not isinstance(reference, str) or not reference:
                failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `{section}.reference`"))
                continue
            if not (manifest_file.parent / reference).exists():
                failures.append(Failure("skill-manifests", f"`{manifest_path}` points `{section}.reference` to missing `{reference}`"))

        installation = contract.get("installation")
        if not isinstance(installation, dict):
            failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `installation`"))
        else:
            for field in ("registry", "upgrade_contract"):
                value = installation.get(field)
                if not isinstance(value, str) or not value:
                    failures.append(Failure("skill-manifests", f"`{manifest_path}` must declare `installation.{field}`"))
                    continue
                if not (manifest_file.parent / value).exists():
                    failures.append(Failure("skill-manifests", f"`{manifest_path}` points `installation.{field}` to missing `{value}`"))

    if root_registry_entry is None:
        failures.append(Failure("skill-manifests", f"`skills/registry.json` root entry `{root_entry}` does not match any declared entry"))
        return failures
    if upgrade_reference != "upgrade-contract.json":
        failures.append(Failure("skill-manifests", "`skills/registry.json` must point to `upgrade-contract.json`"))

    upgrade_root = upgrade_contract.get("root_entry")
    current_contract_version = upgrade_contract.get("current_contract_version")
    upgrade_policy = upgrade_contract.get("upgrade_policy")
    if upgrade_root != root_entry:
        failures.append(
            Failure(
                "skill-manifests",
                f"`skills/upgrade-contract.json` root entry `{upgrade_root}` does not match registry root `{root_entry}`",
            )
        )
    if current_contract_version != root_registry_entry.get("contract_version"):
        failures.append(
            Failure(
                "skill-manifests",
                "`skills/upgrade-contract.json` current contract version must match the registry entry version",
            )
        )
    if not isinstance(upgrade_policy, dict):
        failures.append(Failure("skill-manifests", "`skills/upgrade-contract.json` must declare `upgrade_policy`"))
    else:
        if upgrade_policy.get("mode") != "explicit":
            failures.append(Failure("skill-manifests", "`upgrade_policy.mode` must be `explicit`"))
        refresh_required = upgrade_policy.get("refresh_required")
        if not isinstance(refresh_required, list) or not refresh_required:
            failures.append(Failure("skill-manifests", "`upgrade_policy.refresh_required` must be a non-empty list"))
        else:
            required = {"registry", "root_entry", "manifest", "executable", "referenced_resources"}
            if not required.issubset(set(refresh_required)):
                failures.append(Failure("skill-manifests", "`upgrade_policy.refresh_required` must cover registry, root_entry, manifest, executable, and referenced_resources"))

    return failures


def check_skill_routing(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    target = root / "examples/new-project"
    tool_path = root / "tools/loom_init.py"
    if not tool_path.exists() or not target.exists():
        return failures

    explicit_skills = (
        "loom-init",
        "loom-adopt",
        "loom-resume",
        "loom-pre-review",
        "loom-handoff",
        "loom-retire",
        "loom-merge-ready",
    )
    for skill_id in explicit_skills:
        payload, error = load_command_json(
            root,
            ["python3", "tools/loom_init.py", "route", "--target", "examples/new-project", "--skill", skill_id],
        )
        if error:
            failures.append(Failure("skill-routing", f"explicit route for `{skill_id}` failed: {error}"))
            continue
        if payload.get("result") != "pass":
            failures.append(Failure("skill-routing", f"explicit route for `{skill_id}` must pass"))
        if payload.get("selected_skill") != skill_id:
            failures.append(Failure("skill-routing", f"explicit route for `{skill_id}` selected `{payload.get('selected_skill')}`"))
        if payload.get("mode") != "explicit":
            failures.append(Failure("skill-routing", f"explicit route for `{skill_id}` must report `mode: explicit`"))

    implicit_cases = (
        ("请初始化这个新项目并接入 Loom", "loom-adopt"),
        ("请接手当前事项并恢复上下文后继续推进", "loom-resume"),
        ("请在进入 review 前做统一检查", "loom-pre-review"),
        ("请准备交接并回写停点", "loom-handoff"),
        ("请清理并 retire 当前事项现场", "loom-retire"),
        ("请确认这个事项是否 merge-ready", "loom-merge-ready"),
    )
    for task, skill_id in implicit_cases:
        payload, error = load_command_json(
            root,
            ["python3", "tools/loom_init.py", "route", "--target", "examples/new-project", "--task", task],
        )
        if error:
            failures.append(Failure("skill-routing", f"implicit route for `{skill_id}` failed: {error}"))
            continue
        if payload.get("result") != "pass":
            failures.append(Failure("skill-routing", f"implicit route for `{skill_id}` must pass"))
        if payload.get("selected_skill") != skill_id:
            failures.append(Failure("skill-routing", f"implicit route for `{skill_id}` selected `{payload.get('selected_skill')}`"))
        if payload.get("mode") != "implicit":
            failures.append(Failure("skill-routing", f"implicit route for `{skill_id}` must report `mode: implicit`"))

    fallback_payload, error = load_command_json(
        root,
        ["python3", "tools/loom_init.py", "route", "--target", "examples/new-project", "--task", "请帮我看看这个仓库"],
    )
    if error:
        failures.append(Failure("skill-routing", f"fallback route failed: {error}"))
    else:
        if fallback_payload.get("result") != "fallback":
            failures.append(Failure("skill-routing", "ambiguous task must return `fallback`"))
        if fallback_payload.get("selected_skill") != "loom-init":
            failures.append(Failure("skill-routing", "fallback route must select `loom-init`"))

    return failures


def check_demo_assets(root: Path) -> list[Failure]:
    failures = check_required_paths(root, "demo-assets", DEMO_ASSETS)
    demo_doc = root / "docs/demo-new-project.md"
    if not demo_doc.exists():
        return failures

    text = demo_doc.read_text(encoding="utf-8")
    for needle in (
        "make loom-demo-new-project",
        "tools/loom_init.py bootstrap",
        ".loom/bin/loom_init.py verify",
        ".loom/bin/loom_init.py fact-chain",
        ".loom/bin/loom_flow.py fact-chain",
        ".loom/bin/loom_flow.py runtime-evidence",
        ".loom/bin/loom_flow.py state-check",
        ".loom/bin/loom_flow.py flow pre-review",
        ".loom/bin/loom_flow.py checkpoint admission",
        ".loom/bin/loom_flow.py workspace locate",
        ".loom/bin/loom_flow.py purity-check",
    ):
        if needle not in text:
            failures.append(Failure("demo-assets", f"`docs/demo-new-project.md` is missing `{needle}`"))

    init_result_path = root / "examples/new-project/.loom/bootstrap/init-result.json"
    if init_result_path.exists():
        try:
            init_result = load_json_file(init_result_path)
        except json.JSONDecodeError as exc:
            failures.append(Failure("demo-assets", f"demo init-result is invalid JSON: {exc.msg}"))
            return failures
        if not isinstance(init_result, dict):
            failures.append(Failure("demo-assets", "demo init-result must be a JSON object"))
            return failures
        run = init_result.get("run")
        if not isinstance(run, dict) or run.get("scenario_key") != "new":
            failures.append(Failure("demo-assets", "demo init-result must keep `scenario_key` as `new`"))
    return failures


def check_demo_fact_chain(root: Path) -> list[Failure]:
    target = root / "examples/new-project"
    if not target.exists():
        return []

    report, errors = inspect_fact_chain(target)
    failures: list[Failure] = []
    for detail in errors:
        failures.append(Failure("demo-fact-chain", detail))
    if report and report.get("fact_chain", {}).get("entry_points", {}).get("status_surface") != ".loom/status/current.md":
        failures.append(Failure("demo-fact-chain", "demo fact chain must point status_surface to `.loom/status/current.md`"))
    return failures


def check_daily_execution_cli(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    example_target = root / "examples/new-project"
    tool_path = root / "tools/loom_flow.py"
    if not tool_path.exists() or not example_target.exists():
        return failures

    demo_commands = [
        (
            "fact-chain",
            ["python3", "tools/loom_flow.py", "fact-chain", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass"},
        ),
        (
            "runtime-evidence",
            [
                "python3",
                "tools/loom_flow.py",
                "runtime-evidence",
                "--target",
                "examples/new-project",
                "--item",
                "INIT-0001",
            ],
            {"pass"},
        ),
        (
            "state-check",
            ["python3", "tools/loom_flow.py", "state-check", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass"},
        ),
        (
            "flow-pre-review",
            [
                "python3",
                "tools/loom_flow.py",
                "flow",
                "pre-review",
                "--target",
                "examples/new-project",
                "--item",
                "INIT-0001",
            ],
            {"pass", "block", "fallback"},
        ),
        (
            "admission",
            ["python3", "tools/loom_flow.py", "checkpoint", "admission", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass"},
        ),
        (
            "build",
            ["python3", "tools/loom_flow.py", "checkpoint", "build", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass", "block", "fallback"},
        ),
        (
            "merge",
            ["python3", "tools/loom_flow.py", "checkpoint", "merge", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass", "block", "fallback"},
        ),
        (
            "locate",
            ["python3", "tools/loom_flow.py", "workspace", "locate", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass"},
        ),
        (
            "purity",
            ["python3", "tools/loom_flow.py", "purity-check", "--target", "examples/new-project", "--item", "INIT-0001"],
            {"pass"},
        ),
    ]
    for label, args, allowed_results in demo_commands:
        payload, error = load_command_json(root, args)
        if error:
            failures.append(Failure("daily-execution-cli", f"`{label}` command failed: {error}"))
            continue
        result = payload.get("result")
        if result not in allowed_results:
            failures.append(
                Failure(
                    "daily-execution-cli",
                    f"`{label}` returned unexpected result `{result}`",
                )
            )
        if label == "purity":
            purity = payload.get("purity")
            if not isinstance(purity, dict):
                failures.append(Failure("daily-execution-cli", "`purity` output must include a `purity` object"))
                continue
            scope_assessment = purity.get("scope_assessment")
            if not isinstance(scope_assessment, dict):
                failures.append(Failure("daily-execution-cli", "`purity` output must include `scope_assessment`"))
                continue
            mode = scope_assessment.get("mode")
            if mode not in {"constrained", "unconstrained"}:
                failures.append(
                    Failure("daily-execution-cli", "`scope_assessment.mode` must be `constrained` or `unconstrained`")
                )

    with tempfile.TemporaryDirectory(prefix="loom-check-flow-") as tmp:
        lifecycle_target = Path(tmp) / "new-project"
        shutil.copytree(example_target, lifecycle_target)
        temp_root = lifecycle_target / ".loom/flow/tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        (temp_root / "sentinel.txt").write_text("temp\n", encoding="utf-8")

        for operation in ("create", "cleanup", "retire"):
            payload, error = load_command_json(
                root,
                [
                    "python3",
                    "tools/loom_flow.py",
                    "workspace",
                    operation,
                    "--target",
                    str(lifecycle_target),
                    "--item",
                    "INIT-0001",
                ],
            )
            if error:
                failures.append(Failure("daily-execution-cli", f"`workspace {operation}` failed: {error}"))
                continue
            if payload.get("result") != "pass":
                failures.append(
                    Failure(
                        "daily-execution-cli",
                        f"`workspace {operation}` must pass on a clean temp copy, got `{payload.get('result')}`",
                    )
                )

        locate_payload, error = load_command_json(
            root,
            [
                "python3",
                "tools/loom_flow.py",
                "workspace",
                "locate",
                "--target",
                str(lifecycle_target),
                "--item",
                "INIT-0001",
            ],
        )
        if error:
            failures.append(Failure("daily-execution-cli", f"`workspace locate` after retire failed: {error}"))
        elif (
            not isinstance(locate_payload.get("checkpoint"), dict)
            or locate_payload["checkpoint"].get("normalized") != "retired"
        ):
            failures.append(Failure("daily-execution-cli", "`workspace retire` must leave the copied sample in `retired` state"))

    if shutil.which("git") is not None:
        with tempfile.TemporaryDirectory(prefix="loom-check-purity-") as tmp:
            dirty_target = Path(tmp) / "new-project"
            shutil.copytree(example_target, dirty_target)
            run_command(root, ["git", "init"], cwd=dirty_target)
            run_command(root, ["git", "config", "user.email", "loom-check@example.com"], cwd=dirty_target)
            run_command(root, ["git", "config", "user.name", "loom-check"], cwd=dirty_target)
            run_command(root, ["git", "add", "."], cwd=dirty_target)
            run_command(root, ["git", "commit", "-m", "baseline"], cwd=dirty_target)
            (dirty_target / "untriaged.txt").write_text("pending\n", encoding="utf-8")
            payload, error = load_command_json(
                root,
                [
                    "python3",
                    "tools/loom_flow.py",
                    "purity-check",
                    "--target",
                    str(dirty_target),
                    "--item",
                    "INIT-0001",
                ],
            )
            if error:
                failures.append(Failure("daily-execution-cli", f"`purity-check` negative sample failed: {error}"))
            elif payload.get("result") != "block":
                failures.append(
                    Failure(
                        "daily-execution-cli",
                        f"`purity-check` negative sample must block, got `{payload.get('result')}`",
                    )
                )
            state_payload, error = load_command_json(
                root,
                [
                    "python3",
                    "tools/loom_flow.py",
                    "state-check",
                    "--target",
                    str(dirty_target),
                    "--item",
                    "INIT-0001",
                ],
            )
            if error:
                failures.append(Failure("daily-execution-cli", f"`state-check` negative sample failed: {error}"))
            elif state_payload.get("result") != "block":
                failures.append(
                    Failure(
                        "daily-execution-cli",
                        f"`state-check` negative sample must block, got `{state_payload.get('result')}`",
                    )
                )

    return failures


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def collect_failures(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    failures.extend(check_required_paths(root, "top-level-dirs", TOP_LEVEL_DIRS))
    failures.extend(check_required_paths(root, "top-level-files", TOP_LEVEL_FILES))
    failures.extend(check_required_paths(root, "area-readmes", AREA_READMES))
    failures.extend(check_required_paths(root, "core-docs", CORE_DOCS))
    failures.extend(
        check_required_paths(root, "automation-frontload-templates", AUTOMATION_FRONTLOAD_TEMPLATES)
    )
    failures.extend(check_required_paths(root, "automation-frontload-skills", AUTOMATION_FRONTLOAD_SKILLS))
    failures.extend(
        check_required_paths(
            root,
            "automation-frontload-execution-support",
            AUTOMATION_FRONTLOAD_EXECUTION_SUPPORT,
        )
    )
    failures.extend(check_skill_manifests(root))
    failures.extend(check_skill_routing(root))
    failures.extend(check_demo_assets(root))
    failures.extend(check_demo_fact_chain(root))
    failures.extend(check_daily_execution_cli(root))
    failures.extend(check_markdown_links(root))
    return failures


def print_report(root: Path, failures: list[Failure]) -> None:
    categories_checked = 13
    if not failures:
        print(f"loom_check: OK ({root})")
        print(f"checked {categories_checked} surfaces")
        return

    grouped: dict[str, list[str]] = defaultdict(list)
    for failure in failures:
        grouped[failure.category].append(failure.detail)

    print(f"loom_check: FAILED ({root})")
    for category in sorted(grouped):
        print(f"- {category}")
        for detail in grouped[category]:
            print(f"  - {detail}")
    print(f"failures: {len(failures)} across {len(grouped)} categories")


def main(argv: list[str]) -> int:
    root = repo_root_from_argv(argv)
    if not root.exists():
        print(f"loom_check: repo root does not exist: {root}", file=sys.stderr)
        return 2
    failures = collect_failures(root)
    print_report(root, failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
