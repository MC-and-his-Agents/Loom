#!/usr/bin/env python3
"""CLI-first Loom control-plane entry.

The command surface is intentionally broader than the implementation surface.
Commands that are not implemented in this phase fail closed with a structured
JSON block instead of silently falling back to legacy wrappers.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_ROOT = REPO_ROOT / "tools"
VERSION_FILE = REPO_ROOT / "VERSION"
SKILLS_ROOT = REPO_ROOT / "skills"
PLUGIN_MANIFEST = REPO_ROOT / "plugins" / "loom" / ".codex-plugin" / "plugin.json"

OUTPUT_SCHEMA = "loom-cli-output/v1"
INSTALLED_STATE_SCHEMA = "loom-installed-state/v2"
DETECT_SCHEMA = "loom-installed-surface-detect/v1"
DOCTOR_SCHEMA = "loom-installed-surface-doctor/v1"
REPAIR_PLAN_SCHEMA = "loom-installed-surface-repair-plan/v1"
WORKSPACE_SCHEMA = "loom-workspace-control/v1"
HOST_OBJECT_SCHEMA = "loom-host-object-control/v1"
HOST_SCHEMA = "loom-host-orchestration/v1"
SKILLS_SCHEMA = "loom-skills-surface/v1"
SCENARIO_SCHEMA = "loom-scenario-control/v1"
PROFILE_SCHEMA = "loom-governance-profile-control/v1"
GATE_SCHEMA = "loom-gate-control/v1"
DELIVERY_SCHEMA = "loom-delivery-control/v1"


COMMANDS: list[dict[str, Any]] = [
    {
        "command": "version",
        "domain": "core",
        "status": "implemented",
        "json": True,
        "summary": "Show Loom CLI and distribution version context.",
    },
    {
        "command": "help",
        "domain": "core",
        "status": "implemented",
        "json": True,
        "summary": "Show the frozen CLI command matrix.",
    },
    {
        "command": "installed-state show",
        "domain": "installation",
        "status": "implemented",
        "json": True,
        "summary": "Read the target repository loom-installed-state/v2 object.",
    },
    {
        "command": "installed-state validate",
        "domain": "installation",
        "status": "implemented",
        "json": True,
        "summary": "Validate installed-state schema, layers, graph, and fail-closed metadata.",
    },
    {
        "command": "installed-state export",
        "domain": "installation",
        "status": "implemented",
        "json": True,
        "summary": "Export installed-state plus its installation graph for upgrade consumers.",
    },
    {
        "command": "detect",
        "domain": "diagnostics",
        "status": "implemented",
        "json": True,
        "summary": "Detect installed Loom surfaces, legacy layouts, symlinks, and mixed installations.",
    },
    {
        "command": "doctor",
        "domain": "diagnostics",
        "status": "implemented",
        "json": True,
        "summary": "Diagnose detected surfaces and installed-state readiness.",
    },
    {
        "command": "repair plan",
        "domain": "repair",
        "status": "implemented",
        "json": True,
        "summary": "Emit a non-mutating repair plan for detected legacy or drifted surfaces.",
    },
    {
        "command": "repair apply",
        "domain": "repair",
        "status": "implemented",
        "json": True,
        "summary": "Fail closed until a later Work Item enables mutating repair execution.",
    },
    {"command": "install", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "upgrade-plan", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "upgrade", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "rollback", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "verify", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "init", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "adopt", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "route", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "status", "domain": "harness", "status": "implemented", "json": True},
    {"command": "fact-chain", "domain": "harness", "status": "implemented", "json": True},
    {"command": "profile status", "domain": "profile", "status": "implemented", "json": True},
    {"command": "profile upgrade-plan", "domain": "profile", "status": "implemented", "json": True},
    {"command": "profile upgrade", "domain": "profile", "status": "implemented", "json": True},
    {"command": "story", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "spec", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "plan", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "build", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "pre-review", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "spec-review", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "review", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "merge-ready", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "closeout", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "resume", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "handoff", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "retire", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "checkpoint admission", "domain": "gate", "status": "implemented", "json": True},
    {"command": "checkpoint build", "domain": "gate", "status": "implemented", "json": True},
    {"command": "checkpoint merge", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate pre-review", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate spec-review", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate review", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate pr", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate merge", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate closeout", "domain": "gate", "status": "implemented", "json": True},
    {"command": "workspace create", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace locate", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace check", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace retire", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "issue inspect", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "issue bind", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "issue reconcile", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "project status", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "project reconcile", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr inspect", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr metadata-preflight", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr gate", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "merge check", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "merge run", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "reconcile", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "host list", "domain": "host", "status": "implemented", "json": True},
    {"command": "host doctor", "domain": "host", "status": "implemented", "json": True},
    {"command": "host install", "domain": "host", "status": "implemented", "json": True},
    {"command": "host verify", "domain": "host", "status": "implemented", "json": True},
    {"command": "host upgrade", "domain": "host", "status": "implemented", "json": True},
    {"command": "host remove", "domain": "host", "status": "implemented", "json": True},
    {"command": "skills list", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills generate", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills sync", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills check", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills doctor", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills package", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills release-check", "domain": "skills", "status": "implemented", "json": True},
]

COMMAND_INDEX = {entry["command"]: entry for entry in COMMANDS}

COMMAND_ROUTES: dict[str, tuple[str, tuple[str, ...]]] = {
    "init": ("loom_init.py", ()),
    "adopt": ("loom_flow.py", ("adopt",)),
    "route": ("loom_init.py", ("route",)),
    "flow": ("loom_flow.py", ()),
    "resume": ("loom_flow.py", ("flow", "resume")),
    "merge-ready": ("loom_flow.py", ("flow", "merge-ready")),
    "spec-review": ("loom_flow.py", ("flow", "spec-review")),
    "review": ("loom_flow.py", ("review",)),
    "check": ("loom_check.py", ()),
    "status": ("loom_status.py", ()),
    "fact-chain": ("loom_init.py", ("fact-chain",)),
}

STATE_FILENAMES = (
    ".loom/installed-state.json",
    ".loom/installed-state.v2.json",
    ".loom/installed-state/installed-state.json",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_optional_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return read_json(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {"__pycache__", ".DS_Store"} or name.endswith(".pyc")}

    shutil.copytree(source, target, ignore=ignore)


def repo_version() -> str:
    if not VERSION_FILE.exists():
        return "unknown"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def version_context() -> dict[str, Any]:
    registry = read_optional_json(SKILLS_ROOT / "registry.json") or {}
    plugin = read_optional_json(PLUGIN_MANIFEST) or {}
    package = read_optional_json(SKILLS_ROOT / "loom-init" / "loom-package.json") or {}
    return {
        "repo_version": repo_version(),
        "skills_registry_version": registry.get("registry_version", "unknown"),
        "plugin_surface_version": plugin.get("x-loom", {}).get("plugin_surface_version", plugin.get("version", "unknown")),
        "host_adapter_version": plugin.get("x-loom", {}).get("host_adapter_version", "unknown"),
        "runtime_core_version": package.get("runtime_core_version", "unknown"),
        "skill_package_version": package.get("skill_package_version", "unknown"),
        "version_authority": "docs/adoption/version-authority-map.md",
    }


def emit(payload: dict[str, Any], *, stream=sys.stdout) -> int:
    stream.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0 if payload.get("result") == "pass" else 1


def output(command: str, result: str, **fields: Any) -> dict[str, Any]:
    return {
        "schema_version": OUTPUT_SCHEMA,
        "command": command,
        "result": result,
        "generated_at": now_iso(),
        **fields,
    }


def run_capture(args: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def parse_json_or_block(command: str, completed: subprocess.CompletedProcess[str], *, failed_layer: str, fallback_to: list[str]) -> dict[str, Any]:
    raw = completed.stdout or completed.stderr
    if raw:
        try:
            payload = json.loads(raw)
            if payload.get("command") and payload.get("command") != command:
                payload["wrapped_command"] = payload.get("command")
            payload["command"] = command
            return payload
        except json.JSONDecodeError:
            pass
    if completed.returncode != 0:
        return output(
            command,
            "block",
            summary="Delegated command failed.",
            failed_layer=failed_layer,
            fail_closed_reason=raw.strip() if raw else f"{completed.args} failed",
            fallback_to=fallback_to,
        )
    return output(
        command,
        "block",
        summary="Delegated command did not emit JSON.",
        failed_layer=failed_layer,
        fail_closed_reason="invalid JSON from delegated command",
        fallback_to=fallback_to,
    )


def flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str]) -> dict[str, Any]:
    completed = run_capture([sys.executable, str(TOOLS_ROOT / "loom_flow.py"), *flow_args])
    return parse_json_or_block(command, completed, failed_layer="loom-flow", fallback_to=fallback_to)


def emit_flow(command: str, flow_args: list[str], *, fallback_to: list[str]) -> int:
    payload = flow_payload(command, flow_args, fallback_to=fallback_to)
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(payload)


def delegated_payload(command: str, tool_name: str, delegated_args: list[str], *, failed_layer: str, fallback_to: list[str]) -> dict[str, Any]:
    completed = run_capture([sys.executable, str(TOOLS_ROOT / tool_name), *delegated_args])
    return parse_json_or_block(command, completed, failed_layer=failed_layer, fallback_to=fallback_to)


def emit_delegated(command: str, tool_name: str, delegated_args: list[str], *, failed_layer: str, fallback_to: list[str]) -> int:
    payload = delegated_payload(command, tool_name, delegated_args, failed_layer=failed_layer, fallback_to=fallback_to)
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(payload)


def strip_json_flag(argv: list[str]) -> list[str]:
    return [arg for arg in argv if arg != "--json"]


def command_matrix() -> list[dict[str, Any]]:
    return [
        {
            "command": entry["command"],
            "domain": entry["domain"],
            "status": entry["status"],
            "json": entry.get("json", True),
            "summary": entry.get("summary", ""),
        }
        for entry in COMMANDS
    ]


def print_usage(stream) -> None:
    stream.write(
        "usage: loom <command> [args ...]\n\n"
        "CLI-first Loom control-plane entry.\n\n"
        "core commands:\n"
        "  version [--json]\n"
        "  help [--json]\n"
        "  installed-state show|validate|export --target <repo> [--json]\n\n"
        "scenario and gate commands:\n"
        "  init, adopt, route, status, fact-chain, profile, checkpoint, gate\n"
        "  resume, spec-review, review, merge-ready, check\n\n"
        "Use `loom help --json` for the full frozen command matrix, including reserved commands.\n"
    )


def handle_version(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom version")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = output(
        "version",
        "pass",
        summary="Loom CLI version context resolved.",
        versions=version_context(),
        command_contract="docs/methodology/harness/cli-command-matrix.md",
    )
    if args.json:
        return emit(payload)
    versions = payload["versions"]
    print(f"loom repo {versions['repo_version']}")
    print(f"skills registry {versions['skills_registry_version']}")
    print(f"plugin surface {versions['plugin_surface_version']}")
    return 0


def handle_help(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom help")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = output(
        "help",
        "pass",
        summary="Frozen CLI command matrix.",
        command_count=len(COMMANDS),
        commands=command_matrix(),
        fail_closed_on=[
            "unknown command",
            "reserved command invoked before implementation",
            "delegated wrapper missing",
            "installed-state metadata missing or invalid",
        ],
        fallback_to=[
            "loom help --json",
            "loom installed-state validate --target <repo> --json",
            "legacy delegated wrapper only when command status is delegated",
        ],
    )
    if args.json:
        return emit(payload)
    print_usage(sys.stdout)
    print("\ncommands:")
    for entry in COMMANDS:
        print(f"  {entry['command']:<32} {entry['status']:<11} {entry['domain']}")
    return 0


def resolve_target(raw_target: str) -> Path:
    return Path(raw_target).expanduser().resolve()


def installed_state_path(target: Path) -> Path | None:
    for filename in STATE_FILENAMES:
        path = target / filename
        if path.exists():
            return path
    return None


def build_installed_state(target: Path, *, host: str, mode: str, skill_id: str | None = None) -> dict[str, Any]:
    versions = version_context()
    layers: list[dict[str, Any]] = [
        {
            "id": "runtime",
            "layer_type": "full-repo-runtime",
            "installed_path": ".loom/bin",
            "version_context": {
                "repo_version": versions["repo_version"],
                "runtime_core_version": versions["runtime_core_version"],
            },
            "runtime_state": "ready",
            "upgrade_eligibility": "current",
            "provides": ["loom runtime wrappers", "CLI-first control-plane entry"],
            "consumes": [],
        },
        {
            "id": "skills",
            "layer_type": "generated-skills",
            "installed_path": "skills",
            "version_context": {
                "skills_registry_version": versions["skills_registry_version"],
                "skill_package_version": versions["skill_package_version"],
            },
            "runtime_state": "ready",
            "upgrade_eligibility": "current",
            "provides": ["scenario skills"],
            "consumes": ["runtime"],
        },
    ]
    graph_layers = ["runtime", "skills"]
    graph_edges = [{"from": "skills", "to": "runtime", "relationship": "consumes"}]
    if mode in {"plugin", "skill"}:
        layer_id = "host-adapter" if mode == "plugin" else "single-skill"
        layers.append(
            {
                "id": layer_id,
                "layer_type": "host-adapter-plugin" if mode == "plugin" else "generated-single-skill",
                "installed_path": "plugins/loom" if mode == "plugin" else f".agents/skills/{skill_id or 'loom-init'}",
                "version_context": {
                    "plugin_surface_version": versions["plugin_surface_version"],
                    "host_adapter_version": versions["host_adapter_version"],
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": [f"{host} {mode} discovery surface"],
                "consumes": ["skills"],
            }
        )
        graph_layers.append(layer_id)
        graph_edges.append({"from": layer_id, "to": "skills", "relationship": "consumes"})
    return {
        "schema_version": INSTALLED_STATE_SCHEMA,
        "installation_id": f"loom-{target.name or 'repo'}",
        "target": str(target),
        "installed_at": now_iso(),
        "installing_command": "loom install",
        "upgrade_eligibility": "current",
        "layers": layers,
        "installation_graph": {
            "layers": graph_layers,
            "edges": graph_edges,
        },
    }


def installed_layer_paths(target: Path) -> set[str]:
    path = installed_state_path(target)
    if path is None:
        return set()
    try:
        state = read_json(path)
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(state, dict) or state.get("schema_version") != INSTALLED_STATE_SCHEMA:
        return set()
    paths: set[str] = set()
    for layer in state.get("layers", []):
        if not isinstance(layer, dict):
            continue
        installed_path = layer.get("installed_path")
        if isinstance(installed_path, str) and installed_path:
            paths.add(installed_path.rstrip("/"))
    return paths


def is_managed_path(relative: str, managed_paths: set[str]) -> bool:
    relative = relative.rstrip("/")
    for managed in managed_paths:
        if relative == managed or relative.startswith(f"{managed}/"):
            return True
    return False


def legacy_surface_hints(target: Path) -> list[dict[str, str]]:
    candidates = [
        (".loom/bin", "repo-local-runtime-bin"),
        (".loom/companion/manifest.json", "repo-companion"),
        (".agents/skills", "repo-local-skills"),
        ("skills/registry.json", "full-repo-skills"),
        ("plugins/loom/.codex-plugin/plugin.json", "codex-plugin"),
        ("plugins/loom/.loom-install-status.json", "legacy-installed-surface-status"),
        ("packages/loom-installer/package.json", "legacy-installer-package"),
    ]
    hints = []
    for relative, kind in candidates:
        if (target / relative).exists():
            hints.append({"kind": kind, "path": relative})
    return hints


def relative_to_target(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def surface(path: Path, target: Path, *, kind: str, layer: str, authority: str, migration: str, summary: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "layer": layer,
        "path": relative_to_target(path, target),
        "authority": authority,
        "migration_status": migration,
        "is_symlink": path.is_symlink(),
        "summary": summary,
    }


def detect_surfaces(target: Path) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    state_path = installed_state_path(target)
    managed_paths = installed_layer_paths(target)
    if state_path is not None:
        surfaces.append(
            surface(
                state_path,
                target,
                kind="installed-state-v2",
                layer="installation-metadata",
                authority="loom-cli",
                migration="current",
                summary="Versioned installed-state metadata is present.",
            )
        )

    candidates = (
        (
            ".loom/bin",
            "legacy-loom-bin",
            "runtime",
            "repo-local-runtime",
            "legacy",
            "Legacy bootstrapped runtime wrappers are present.",
        ),
        (
            ".loom/bootstrap/manifest.json",
            "bootstrap-manifest",
            "runtime",
            "repo-local-runtime",
            "legacy",
            "Bootstrap manifest is present without being authoritative installed-state metadata.",
        ),
        (
            ".loom/companion/manifest.json",
            "repo-companion",
            "governance-residue",
            "repo-companion",
            "read-only",
            "Repo companion residue is present and must remain repo-owned.",
        ),
        (
            ".agents/skills",
            "repo-local-agents-skills",
            "skills",
            "repo-local",
            "legacy",
            "Repo-local .agents/skills layout is present.",
        ),
        (
            "skills/registry.json",
            "full-repo-skills",
            "skills",
            "loom-distribution",
            "legacy",
            "Full-repo skills registry is present.",
        ),
        (
            "plugins/loom/.codex-plugin/plugin.json",
            "codex-plugin",
            "plugin",
            "codex-plugin",
            "legacy",
            "Codex plugin manifest is present.",
        ),
        (
            "plugins/loom/.loom-install-status.json",
            "legacy-installed-surface-status",
            "installation-metadata",
            "installer-shim",
            "legacy",
            "Legacy installer status file is present.",
        ),
        (
            "packages/loom-installer/package.json",
            "legacy-installer-package",
            "installer",
            "installer-shim",
            "legacy",
            "Legacy installer package surface is present.",
        ),
        (
            "SKILL.md",
            "single-skill",
            "skills",
            "single-skill",
            "legacy",
            "Single-skill installation surface is present.",
        ),
    )
    for relative, kind, layer, authority, migration, summary in candidates:
        path = target / relative
        if path.exists():
            if is_managed_path(relative, managed_paths):
                migration = "current"
                authority = "loom-cli"
                summary = f"CLI-managed {summary[0].lower()}{summary[1:]}"
            surfaces.append(surface(path, target, kind=kind, layer=layer, authority=authority, migration=migration, summary=summary))

    skill_dirs = target / "skills"
    if skill_dirs.exists() and skill_dirs.is_dir():
        for skill_path in sorted(skill_dirs.glob("*/SKILL.md")):
            relative = relative_to_target(skill_path, target)
            managed = is_managed_path(relative, managed_paths)
            surfaces.append(
                surface(
                    skill_path,
                    target,
                    kind="single-skill",
                    layer="skills",
                    authority="loom-cli" if managed else "skill-package",
                    migration="current" if managed else "legacy",
                    summary="CLI-managed skill package is present under skills/." if managed else "Standalone skill package is present under skills/.",
                )
            )

    for entry in surfaces:
        if entry["is_symlink"]:
            entry["kind"] = f"symlink-{entry['kind']}"
            entry["migration_status"] = "legacy"
            entry["summary"] = f"Symlinked {entry['summary'][0].lower()}{entry['summary'][1:]}"
    return surfaces


def classify_installation(surfaces: list[dict[str, Any]]) -> tuple[str, str]:
    if not surfaces:
        return "uninstalled", "No Loom installation surfaces were detected."
    has_current = any(item["kind"] == "installed-state-v2" for item in surfaces)
    legacy = [item for item in surfaces if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")]
    authorities = {item.get("authority") for item in surfaces if item.get("authority")}
    if has_current and not legacy:
        return "current", "Versioned installed-state is present and no legacy surface was detected."
    if has_current and legacy:
        return "mixed", "Versioned installed-state and legacy surfaces are both present."
    if len(authorities) > 1 or len(legacy) > 1:
        return "mixed-legacy", "Multiple legacy Loom surface families are present."
    return "legacy", "Only legacy Loom installation surfaces were detected."


def block_target(command: str, target: Path, reason: str) -> dict[str, Any]:
    return output(
        command,
        "block",
        summary="Target cannot be inspected.",
        target=str(target),
        failed_layer="target",
        fail_closed_reason=reason,
        fallback_to=["loom help --json"],
    )


def detect_payload(target: Path) -> dict[str, Any]:
    surfaces = detect_surfaces(target)
    classification, summary = classify_installation(surfaces)
    return output(
        "detect",
        "pass",
        schema=DETECT_SCHEMA,
        summary=summary,
        target=str(target),
        classification=classification,
        surface_count=len(surfaces),
        surfaces=surfaces,
        installed_state_path=str(installed_state_path(target)) if installed_state_path(target) else None,
        fallback_to=None if surfaces else ["loom install"],
    )


def handle_detect(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom detect")
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("detect", target, "target path does not exist"))
    return emit(detect_payload(target))


def doctor_payload(target: Path) -> dict[str, Any]:
    detection = detect_payload(target)
    path, state, installed_error = load_installed_state(target)
    validation_errors = validate_installed_state(state) if installed_error is None else []
    checks: list[dict[str, Any]] = [
        {
            "name": "surface-detection",
            "result": "pass" if detection["surface_count"] else "block",
            "summary": detection["summary"],
        }
    ]
    if installed_error is not None:
        checks.append(
            {
                "name": "installed-state",
                "result": "block",
                "summary": installed_error["fail_closed_reason"],
                "failed_layer": "installed-state",
                "fallback_to": ["loom repair plan"],
            }
        )
    elif validation_errors:
        checks.append(
            {
                "name": "installed-state",
                "result": "block",
                "summary": "Installed-state metadata is present but invalid.",
                "errors": validation_errors,
                "failed_layer": "installed-state",
                "fallback_to": ["loom repair plan"],
            }
        )
    else:
        checks.append(
            {
                "name": "installed-state",
                "result": "pass",
                "summary": "Installed-state metadata is valid.",
                "installed_state_path": str(path),
            }
        )
    legacy_surfaces = [item for item in detection["surfaces"] if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")]
    if legacy_surfaces:
        checks.append(
            {
                "name": "legacy-surfaces",
                "result": "block",
                "summary": "Legacy surfaces require an explicit repair plan before upgrade or apply.",
                "surfaces": legacy_surfaces,
                "fallback_to": ["loom repair plan"],
            }
        )
    result = "pass" if all(check["result"] == "pass" for check in checks) else "block"
    return output(
        "doctor",
        result,
        schema=DOCTOR_SCHEMA,
        summary="Installed surface diagnostics passed." if result == "pass" else "Installed surface diagnostics found blocking repair inputs.",
        target=str(target),
        detection=detection,
        checks=checks,
        failed_layer=None if result == "pass" else "installed-surface",
        fail_closed_reason=None if result == "pass" else "target has missing, invalid, mixed, or legacy installed surfaces",
        fallback_to=None if result == "pass" else ["loom repair plan"],
    )


def handle_doctor(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom doctor")
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("doctor", target, "target path does not exist"))
    return emit(doctor_payload(target))


def repair_actions(detection: dict[str, Any], installed_errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if installed_errors:
        actions.append(
            {
                "id": "repair-installed-state-v2",
                "kind": "write-installed-state",
                "status": "planned",
                "writes": [".loom/installed-state.json"],
                "reason": "installed-state metadata is missing or invalid",
                "command": "loom installed-state validate --target <repo> --json",
            }
        )
    legacy = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]
    for index, item in enumerate(legacy, start=1):
        actions.append(
            {
                "id": f"classify-legacy-surface-{index}",
                "kind": "manual-migration-judgment",
                "status": "planned",
                "surface": item,
                "reason": "legacy surface must be classified before Loom can apply mutating repair",
                "command": "loom doctor --target <repo> --json",
            }
        )
    return actions


def repair_plan_payload(target: Path) -> dict[str, Any]:
    detection = detect_payload(target)
    _, state, installed_error = load_installed_state(target)
    installed_errors = [{"path": "installed-state", "reason": installed_error["fail_closed_reason"]}] if installed_error else validate_installed_state(state)
    actions = repair_actions(detection, installed_errors)
    result = "pass" if detection["surface_count"] or actions else "block"
    return output(
        "repair plan",
        result,
        schema=REPAIR_PLAN_SCHEMA,
        summary="Repair plan generated without mutating target state." if result == "pass" else "No installed surface exists to repair.",
        target=str(target),
        mutates=False,
        detection=detection,
        actions=actions,
        failed_layer=None if result == "pass" else "installed-surface",
        fail_closed_reason=None if result == "pass" else "target has no detectable Loom surface",
        fallback_to=None if result == "pass" else ["loom install"],
    )


def handle_repair(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom repair")
    parser.add_argument("action", choices=("plan", "apply"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(f"repair {args.action}", target, "target path does not exist"))
    plan = repair_plan_payload(target)
    if args.action == "plan":
        return emit(plan)
    return emit(
        output(
            "repair apply",
            "block",
            schema=REPAIR_PLAN_SCHEMA,
            summary="Mutating repair apply is intentionally disabled until an explicit apply contract is approved.",
            target=str(target),
            mutates=False,
            dry_run=args.dry_run,
            plan=plan,
            failed_layer="repair-apply",
            fail_closed_reason="repair apply requires a later Work Item to approve write ownership and rollback semantics",
            fallback_to=["loom repair plan", "loom doctor"],
        )
    )


def host_plugin_path(target: Path, host: str) -> Path:
    if host == "claude":
        return target / ".claude" / "marketplaces" / "loom-local" / "plugins" / "loom"
    return target / "plugins" / "loom"


def sync_skills_payload(target: Path) -> list[str]:
    target_skills = target / "skills"
    if target.resolve() == REPO_ROOT.resolve():
        completed = run_capture([sys.executable, str(TOOLS_ROOT / "skills_surface.py"), "generate"])
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "skills generation failed")
        return ["skills"]
    copy_tree(SKILLS_ROOT, target_skills)
    return ["skills"]


def install_host_plugin_payload(target: Path, host: str) -> list[str]:
    if host != "codex":
        raise RuntimeError(f"host plugin install is implemented for codex only in this Work Item: {host}")
    plugin_root = host_plugin_path(target, host)
    manifest_target = plugin_root / ".codex-plugin" / "plugin.json"
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PLUGIN_MANIFEST, manifest_target)
    copy_tree(SKILLS_ROOT, plugin_root / "skills")
    return [relative_to_target(manifest_target, target), relative_to_target(plugin_root / "skills", target)]


def install_cli_managed_surfaces(target: Path, *, host: str, mode: str, skill_id: str | None = None) -> list[str]:
    writes = sync_skills_payload(target)
    if mode == "plugin":
        writes.extend(install_host_plugin_payload(target, host))
    elif mode == "skill":
        if not skill_id:
            raise RuntimeError("skill mode requires --skill-id")
        skill_source = SKILLS_ROOT / skill_id
        if not skill_source.exists():
            raise RuntimeError(f"unknown skill id: {skill_id}")
        skill_target = target / ".agents" / "skills" / skill_id
        copy_tree(skill_source, skill_target)
        writes.append(relative_to_target(skill_target, target))
    return writes


def planned_cli_managed_writes(*, mode: str, skill_id: str | None = None) -> list[str]:
    writes = ["skills"]
    if mode == "plugin":
        writes.append("plugins/loom")
    elif mode == "skill":
        writes.append(f".agents/skills/{skill_id or '<skill-id>'}")
    return writes


def verify_cli_managed_surfaces(target: Path, *, host: str, mode: str, skill_id: str | None = None) -> tuple[bool, list[dict[str, str]]]:
    checks: list[dict[str, str]] = []

    def check(relative: str, kind: str) -> None:
        path = target / relative
        checks.append({"kind": kind, "path": relative, "status": "pass" if path.exists() else "missing"})

    check(".loom/installed-state.json", "installed-state")
    check("skills/registry.json", "skills-registry")
    registry_path = target / "skills" / "registry.json"
    if registry_path.exists():
        try:
            registry = read_json(registry_path)
            entries = registry.get("entries", []) if isinstance(registry, dict) else []
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                    check(f"skills/{entry['id']}/SKILL.md", "skill")
        except (OSError, json.JSONDecodeError):
            checks.append({"kind": "skills-registry-json", "path": "skills/registry.json", "status": "invalid"})
    if mode == "plugin":
        if host == "codex":
            check("plugins/loom/.codex-plugin/plugin.json", "host-plugin")
            check("plugins/loom/skills/registry.json", "host-plugin-skills")
        else:
            checks.append({"kind": "host-plugin", "path": host, "status": "unsupported"})
    if mode == "skill":
        check(f".agents/skills/{skill_id or 'missing'}/SKILL.md", "single-skill")
    return all(item["status"] == "pass" for item in checks), checks


def handle_delivery(command: str, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--host", default="codex", choices=("codex", "claude", "opencode", "gemini", "cursor"))
    parser.add_argument("--mode", default="full-repo", choices=("full-repo", "plugin", "skill"))
    parser.add_argument("--skill-id")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(command, target, "target path does not exist"))

    detection = detect_payload(target)
    path, state, installed_error = load_installed_state(target)
    validation_errors = validate_installed_state(state) if installed_error is None else []
    installed_ready = installed_error is None and not validation_errors
    legacy_surfaces = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]

    if command == "install":
        planned_state = build_installed_state(target, host=args.host, mode=args.mode, skill_id=args.skill_id)
        state_path = target / ".loom" / "installed-state.json"
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Install is mutating and requires --apply before writing installed-state metadata.",
                    target=str(target),
                    host=args.host,
                    mode=args.mode,
                    mutates=True,
                    planned_writes=[relative_to_target(state_path, target), *planned_cli_managed_writes(mode=args.mode, skill_id=args.skill_id)],
                    detection=detection,
                    failed_layer="install-apply",
                    fail_closed_reason="explicit --apply is required before install writes installed-state",
                    fallback_to=["loom install --target <repo> --apply --json", "loom repair plan --target <repo> --json"],
                )
            )
        if installed_ready and not args.force:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Valid installed-state already exists; use upgrade-plan or --force for reinstall.",
                    target=str(target),
                    installed_state_path=str(path),
                    detection=detection,
                    failed_layer="installed-state",
                    fail_closed_reason="current installed-state exists",
                    fallback_to=["loom upgrade-plan --target <repo> --json", "loom install --target <repo> --apply --force --json"],
                )
            )
        try:
            managed_writes = install_cli_managed_surfaces(target, host=args.host, mode=args.mode, skill_id=args.skill_id)
        except RuntimeError as exc:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="CLI-managed install payload could not be written.",
                    target=str(target),
                    host=args.host,
                    mode=args.mode,
                    failed_layer="cli-managed-install",
                    fail_closed_reason=str(exc),
                    fallback_to=["loom host doctor --host <host> --json", "loom skills check --target <repo> --json"],
                )
            )
        write_json(state_path, planned_state)
        return emit(
            output(
                command,
                "pass",
                schema=DELIVERY_SCHEMA,
                summary="CLI-managed plugin/SKILLS payload and installed-state metadata were written.",
                target=str(target),
                host=args.host,
                mode=args.mode,
                mutates=True,
                managed_writes=[*managed_writes, relative_to_target(state_path, target)],
                installed_state_path=str(state_path),
                installed_state=planned_state,
                detection=detection,
                fallback_to=None,
            )
        )

    if command == "upgrade-plan":
        actions: list[dict[str, Any]] = []
        if installed_error is not None or validation_errors:
            actions.append(
                {
                    "id": "repair-installed-state",
                    "kind": "repair-plan",
                    "status": "required",
                    "reason": installed_error["fail_closed_reason"] if installed_error else "installed-state validation failed",
                    "command": "loom repair plan --target <repo> --json",
                }
            )
        if legacy_surfaces:
            actions.append(
                {
                    "id": "classify-legacy-surfaces",
                    "kind": "manual-migration-judgment",
                    "status": "required",
                    "surface_count": len(legacy_surfaces),
                    "command": "loom repair plan --target <repo> --json",
                }
            )
        if installed_ready and not legacy_surfaces:
            actions.append(
                {
                    "id": "installed-state-current",
                    "kind": "no-op",
                    "status": "current",
                    "reason": "installed-state validates and no legacy surfaces are blocking",
                    "command": "loom verify --target <repo> --json",
                }
            )
        return emit(
            output(
                command,
                "pass",
                schema=DELIVERY_SCHEMA,
                summary="Upgrade plan generated without mutating target state.",
                target=str(target),
                mutates=False,
                installed_state_path=str(path) if path else None,
                detection=detection,
                installed_state_errors=validation_errors,
                actions=actions,
                fallback_to=None if installed_ready and not legacy_surfaces else ["loom repair plan --target <repo> --json"],
            )
        )

    if command == "verify":
        doctor = doctor_payload(target)
        result = "pass" if doctor["result"] == "pass" else "block"
        return emit(
            output(
                command,
                result,
                schema=DELIVERY_SCHEMA,
                summary="Installed Loom delivery layers verified." if result == "pass" else "Installed Loom delivery layers are not ready.",
                target=str(target),
                mutates=False,
                doctor=doctor,
                installed_state_path=str(path) if path else None,
                failed_layer=None if result == "pass" else "delivery-verify",
                fail_closed_reason=None if result == "pass" else "doctor reported missing, invalid, mixed, or legacy installed surfaces",
                fallback_to=None if result == "pass" else ["loom upgrade-plan --target <repo> --json", "loom repair plan --target <repo> --json"],
            )
        )

    if command == "upgrade":
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Upgrade is mutating and requires --apply.",
                    target=str(target),
                    mutates=True,
                    plan=handle_delivery_payload_for_upgrade_plan(target),
                    failed_layer="upgrade-apply",
                    fail_closed_reason="explicit --apply is required before upgrade mutates installed-state or adapter surfaces",
                    fallback_to=["loom upgrade-plan --target <repo> --json", "loom verify --target <repo> --json"],
                )
            )
        if not installed_ready or legacy_surfaces:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Upgrade cannot apply while installed-state is invalid or legacy surfaces remain unclassified.",
                    target=str(target),
                    mutates=True,
                    detection=detection,
                    installed_state_errors=validation_errors,
                    failed_layer="upgrade-preflight",
                    fail_closed_reason="repair plan must be consumed before mutating upgrade",
                    fallback_to=["loom repair plan --target <repo> --json"],
                )
            )
        state["upgraded_at"] = now_iso()
        state["upgrade_eligibility"] = "current"
        write_json(path, state)
        return emit(
            output(
                command,
                "pass",
                schema=DELIVERY_SCHEMA,
                summary="Installed-state metadata was refreshed for the current Loom version surface.",
                target=str(target),
                mutates=True,
                installed_state_path=str(path),
                installed_state=state,
                fallback_to=None,
            )
        )

    return emit(
        output(
            command,
            "block",
            schema=DELIVERY_SCHEMA,
            summary="Rollback requires an explicit rollback artifact and remains fail-closed in this phase.",
            target=str(target),
            mutates=False,
            detection=detection,
            failed_layer="rollback-ownership",
            fail_closed_reason="rollback/delete ownership is not inferred from installed surface detection",
            fallback_to=["loom upgrade-plan --target <repo> --json", "loom repair plan --target <repo> --json"],
        )
    )


def handle_delivery_payload_for_upgrade_plan(target: Path) -> dict[str, Any]:
    detection = detect_payload(target)
    path, state, installed_error = load_installed_state(target)
    validation_errors = validate_installed_state(state) if installed_error is None else []
    legacy_surfaces = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]
    actions = []
    if installed_error is not None or validation_errors:
        actions.append({"id": "repair-installed-state", "status": "required"})
    if legacy_surfaces:
        actions.append({"id": "classify-legacy-surfaces", "status": "required", "surface_count": len(legacy_surfaces)})
    return output(
        "upgrade-plan",
        "pass",
        schema=DELIVERY_SCHEMA,
        summary="Upgrade plan generated without mutating target state.",
        target=str(target),
        mutates=False,
        installed_state_path=str(path) if path else None,
        detection=detection,
        installed_state_errors=validation_errors,
        actions=actions,
    )


def block_installed_state(command: str, target: Path, reason: str, *, hints: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return output(
        command,
        "block",
        summary="Installed-state cannot be trusted.",
        target=str(target),
        runtime_state="blocked",
        upgrade_eligibility="incompatible",
        failed_layer="installed-state",
        fail_closed_reason=reason,
        legacy_surface_hints=hints or legacy_surface_hints(target),
        fallback_to=["loom detect", "loom doctor", "loom repair plan"],
    )


def validate_installed_state(state: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(state, dict):
        return [{"path": "$", "reason": "installed-state must be a JSON object"}]
    if state.get("schema_version") != INSTALLED_STATE_SCHEMA:
        errors.append({"path": "schema_version", "reason": f"expected {INSTALLED_STATE_SCHEMA}"})
    for key in ("installation_id", "target", "layers", "installation_graph"):
        if key not in state:
            errors.append({"path": key, "reason": "required field is missing"})
    layers = state.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append({"path": "layers", "reason": "must be a non-empty array"})
        return errors
    layer_ids: set[str] = set()
    for index, layer in enumerate(layers):
        path = f"layers[{index}]"
        if not isinstance(layer, dict):
            errors.append({"path": path, "reason": "layer must be an object"})
            continue
        for key in ("id", "layer_type", "installed_path", "version_context", "runtime_state", "upgrade_eligibility"):
            if key not in layer:
                errors.append({"path": f"{path}.{key}", "reason": "required field is missing"})
        layer_id = layer.get("id")
        if isinstance(layer_id, str) and layer_id:
            if layer_id in layer_ids:
                errors.append({"path": f"{path}.id", "reason": "duplicate layer id"})
            layer_ids.add(layer_id)
        if layer.get("runtime_state") not in {"ready", "blocked", "unknown"}:
            errors.append({"path": f"{path}.runtime_state", "reason": "must be ready, blocked, or unknown"})
        if layer.get("upgrade_eligibility") not in {"current", "upgrade-available", "drift", "incompatible", "unknown"}:
            errors.append({"path": f"{path}.upgrade_eligibility", "reason": "unsupported upgrade eligibility"})
        version = layer.get("version_context")
        if not isinstance(version, dict) or not version:
            errors.append({"path": f"{path}.version_context", "reason": "must be a non-empty object"})
        elif any(value in (None, "", "unknown") for value in version.values()):
            errors.append({"path": f"{path}.version_context", "reason": "version metadata must not be missing or unknown"})
        if layer.get("runtime_state") != "ready":
            if not layer.get("fail_closed_reason") or not layer.get("failed_layer"):
                errors.append({"path": path, "reason": "non-ready layers must include failed_layer and fail_closed_reason"})
    graph = state.get("installation_graph")
    if isinstance(graph, dict):
        graph_layers = graph.get("layers")
        if isinstance(graph_layers, list):
            missing = sorted(set(graph_layers) - layer_ids)
            if missing:
                errors.append({"path": "installation_graph.layers", "reason": f"unknown layer ids: {', '.join(missing)}"})
        edges = graph.get("edges", [])
        if isinstance(edges, list):
            for index, edge in enumerate(edges):
                edge_path = f"installation_graph.edges[{index}]"
                if not isinstance(edge, dict):
                    errors.append({"path": edge_path, "reason": "edge must be an object"})
                    continue
                for endpoint in ("from", "to"):
                    if edge.get(endpoint) not in layer_ids:
                        errors.append({"path": f"{edge_path}.{endpoint}", "reason": "edge endpoint must reference a known layer id"})
        else:
            errors.append({"path": "installation_graph.edges", "reason": "must be an array when present"})
    else:
        errors.append({"path": "installation_graph", "reason": "must be an object"})
    return errors


def load_installed_state(target: Path) -> tuple[Path | None, Any | None, dict[str, Any] | None]:
    path = installed_state_path(target)
    if path is None:
        return None, None, block_installed_state(
            "installed-state",
            target,
            f"missing {INSTALLED_STATE_SCHEMA} metadata at one of: {', '.join(STATE_FILENAMES)}",
        )
    try:
        return path, read_json(path), None
    except (OSError, json.JSONDecodeError) as exc:
        return path, None, block_installed_state("installed-state", target, f"installed-state is unreadable: {exc}")


def handle_installed_state(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom installed-state")
    parser.add_argument("action", choices=("show", "validate", "export"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    command = f"installed-state {args.action}"
    path, state, error = load_installed_state(target)
    if error:
        error["command"] = command
        return emit(error)

    errors = validate_installed_state(state)
    if errors:
        return emit(
            output(
                command,
                "block",
                summary="Installed-state failed validation.",
                target=str(target),
                installed_state_path=str(path),
                runtime_state="blocked",
                upgrade_eligibility="incompatible",
                failed_layer="installed-state",
                fail_closed_reason="installed-state schema or version metadata is invalid",
                errors=errors,
                fallback_to=["loom repair plan", "loom installed-state export --target <repo> --json"],
            )
        )

    payload = output(
        command,
        "pass",
        summary="Installed-state is valid.",
        target=str(target),
        installed_state_path=str(path),
        runtime_state="ready",
        upgrade_eligibility=state.get("upgrade_eligibility", "current"),
        installed_state=state,
    )
    if args.action == "export":
        payload["installation_graph"] = state.get("installation_graph")
        payload["export_contract"] = "docs/adoption/loom-installed-state-v2.md"
    if args.action == "validate":
        payload.pop("installed_state")
        payload["validated_schema"] = INSTALLED_STATE_SCHEMA

    if args.json or True:
        return emit(payload)
    return 0


def workspace_payload(action: str, args: argparse.Namespace) -> dict[str, Any]:
    command = f"workspace {action}"
    target = resolve_target(args.target)
    item_args = ["--item", args.item] if getattr(args, "item", None) else []
    if action in {"locate", "create", "retire"}:
        operation = "retire" if action == "retire" else action
        payload = flow_payload(command, ["workspace", operation, "--target", str(target), *item_args], fallback_to=["admission", "loom workspace check --target <repo> --json"])
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return payload
    if action == "check":
        payload = flow_payload(command, ["purity-check", "--target", str(target), *item_args], fallback_to=["admission", "loom workspace locate --target <repo> --json"])
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return payload
    return output(command, "block", schema=WORKSPACE_SCHEMA, summary="Unsupported workspace action.", failed_layer="cli-router", fail_closed_reason=action, fallback_to=["loom help --json"])


def handle_workspace(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom workspace")
    parser.add_argument("action", choices=("create", "locate", "check", "retire"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--path")
    parser.add_argument("--branch")
    parser.add_argument("--item")
    parser.add_argument("--start-point", default="origin/main")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return emit(workspace_payload(args.action, args))


def handle_issue(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom issue")
    parser.add_argument("action", choices=("inspect", "bind", "reconcile"))
    parser.add_argument("issue", nargs="?")
    parser.add_argument("--work-item")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"issue {args.action}"
    if args.action == "inspect":
        if not args.issue:
            return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Issue inspect requires an issue number.", failed_layer="issue-input", fail_closed_reason="missing issue number", fallback_to=["loom help --json"]))
        return emit_flow(command, ["github-intake", "issue", "--target", ".", "--issue", args.issue], fallback_to=["github-intake", "manual-reconciliation"])
    if args.action == "bind":
        if not args.issue or not args.work_item:
            return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Issue bind requires issue and --work-item.", failed_layer="issue-binding", fail_closed_reason="missing issue or work item", fallback_to=["loom issue inspect <issue> --json"]))
        return emit_flow(command, ["host-binding", "inspect", "--target", ".", "--issue", args.issue], fallback_to=["loom issue inspect <issue> --json", "manual-reconciliation"])
    flow_args = ["reconciliation", "audit", "--target", "."]
    if args.issue:
        flow_args.extend(["--issue", args.issue])
    return emit_flow(command, flow_args, fallback_to=["manual-reconciliation"])


def handle_project(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom project")
    parser.add_argument("action", choices=("status", "reconcile"))
    parser.add_argument("--issue")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"project {args.action}"
    if args.issue:
        flow_args = ["github-intake", "issue", "--target", ".", "--issue", args.issue]
        return emit_flow(command, flow_args, fallback_to=["loom issue inspect <issue> --json", "manual-reconciliation"])
    return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Project status requires --issue for this CLI contract.", failed_layer="project-input", fail_closed_reason="missing --issue", fallback_to=["loom issue inspect <issue> --json"]))


def handle_pr(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom pr")
    parser.add_argument("action", choices=("inspect", "metadata-preflight", "gate"))
    parser.add_argument("pr", nargs="?")
    parser.add_argument("--head-sha")
    parser.add_argument("--work-item")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"pr {args.action}"
    if not args.pr:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="PR command requires a PR number.", failed_layer="pr-input", fail_closed_reason="missing PR number", fallback_to=["loom help --json"]))
    if args.action == "inspect":
        flow_args = ["host-binding", "inspect", "--target", ".", "--pr", args.pr]
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        return emit_flow(command, flow_args, fallback_to=["loom pr gate <pr> --json", "manual-reconciliation"])
    if args.action == "metadata-preflight":
        flow_args = ["pr-metadata", "preflight", "--target", ".", "--surface", "merge_ready", "--pr", args.pr]
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        return emit_flow(command, flow_args, fallback_to=["update PR body", "loom pr inspect <pr> --json"])
    flow_args = ["pr-gate", "check", "--target", ".", "--pr", args.pr]
    if args.head_sha:
        flow_args.extend(["--head-sha", args.head_sha])
    if args.work_item:
        flow_args.extend(["--item", args.work_item])
    return emit_flow(command, flow_args, fallback_to=["loom pr inspect <pr> --json", "manual-reconciliation"])


def handle_merge(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom merge")
    parser.add_argument("action", choices=("check", "run"))
    parser.add_argument("pr")
    parser.add_argument("--head-sha")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"merge {args.action}"
    flow_args = ["controlled-merge", "merge" if args.action == "run" else "check", "--target", ".", "--pr", args.pr, "--merge-method", "merge", "--delete-branch"]
    if args.head_sha:
        flow_args.extend(["--head-sha", args.head_sha])
    if args.action == "run" and args.apply:
        flow_args.append("--execute")
    return emit_flow(command, flow_args, fallback_to=["loom pr gate <pr> --json", "loom merge check <pr> --json"])


def handle_reconcile(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom reconcile")
    parser.add_argument("--issue")
    parser.add_argument("--pr")
    parser.add_argument("--work-item")
    parser.add_argument("--head-sha")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    flow_args = ["reconciliation", "audit", "--target", "."]
    if args.issue:
        flow_args.extend(["--issue", args.issue])
    if args.pr:
        flow_args.extend(["--pr", args.pr])
    return emit_flow("reconcile", flow_args, fallback_to=["manual-reconciliation"])


def supported_hosts(target: Path) -> list[dict[str, Any]]:
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    hosts = [
        {
            "id": "codex",
            "support_status": "primary",
            "detected": codex_home.exists(),
            "default_mode": "full-repo",
            "native_skill_path": str(home / ".agents" / "skills"),
            "plugin_path": str(target / "plugins" / "loom"),
        },
        {
            "id": "claude",
            "support_status": "adapter",
            "detected": claude_home.exists(),
            "default_mode": "plugin",
            "native_skill_path": str(claude_home / "skills"),
            "plugin_path": str(target / ".claude" / "marketplaces" / "loom-local" / "plugins" / "loom"),
        },
        {"id": "opencode", "support_status": "adapter-contract", "detected": False, "default_mode": "full-repo"},
        {"id": "gemini", "support_status": "adapter-contract", "detected": False, "default_mode": "full-repo"},
        {"id": "cursor", "support_status": "adapter-contract", "detected": False, "default_mode": "full-repo"},
    ]
    return hosts


def handle_host(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom host")
    parser.add_argument("action", choices=("list", "doctor", "install", "verify", "upgrade", "remove"))
    parser.add_argument("--host", default="auto", choices=("auto", "codex", "claude", "opencode", "gemini", "cursor"))
    parser.add_argument("--mode", default="plugin", choices=("full-repo", "plugin", "skill"))
    parser.add_argument("--skill-id")
    parser.add_argument("--target", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"host {args.action}"
    target = resolve_target(args.target)
    hosts = supported_hosts(target)
    selected = [host for host in hosts if args.host == "auto" or host["id"] == args.host]
    if args.action == "list":
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Supported host adapters listed.", target=str(target), hosts=hosts, fallback_to=None))
    detected = [host for host in selected if host.get("detected")]
    if args.host == "auto" and len(detected) != 1:
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Host auto-detection is ambiguous or unavailable.", target=str(target), hosts=hosts, failed_layer="host-detection", fail_closed_reason="pass --host explicitly when zero or multiple supported hosts are detected", fallback_to=["loom host list --json", "loom host doctor --host <host> --json"]))
    host = detected[0]["id"] if args.host == "auto" else args.host
    if args.action == "doctor":
        warnings = []
        if host == "codex" and args.mode == "plugin":
            warnings.append("Codex default remains full-repo/native skills discovery; plugin mode is adapter-managed.")
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Host adapter contract is readable.", target=str(target), host=host, mode=args.mode, hosts=hosts, warnings=warnings, verification=["docs/adoption/host-adapter-matrix.md", "tools/host_adapter_check.py"], fallback_to=None))
    if args.mode == "full-repo" and args.action in {"install", "upgrade", "remove"}:
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Full-repo host lifecycle remains operator-owned.", target=str(target), host=host, mode=args.mode, mutates=args.action != "verify", failed_layer="host-lifecycle", fail_closed_reason="CLI does not mutate full-repo clone/discovery state", fallback_to=["docs/adoption/host-adapter-matrix.md", "loom host verify --host <host> --mode plugin --json"]))
    if args.action in {"install", "upgrade", "remove"} and not args.apply:
        return emit(output(command, "block", schema=HOST_SCHEMA, summary=f"Host {args.action} is mutating and requires --apply.", target=str(target), host=host, mode=args.mode, mutates=True, failed_layer=f"host-{args.action}", fail_closed_reason="explicit --apply is required before adapter-managed host mutation", fallback_to=["loom host verify --host <host> --json", "loom host doctor --host <host> --json"]))
    if args.action == "remove":
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Host remove only reports verified installed surfaces in this phase.", target=str(target), host=host, mode=args.mode, mutates=False, failed_layer="host-remove", fail_closed_reason="removal requires later rollback/delete ownership contract", fallback_to=["loom host verify --host <host> --json"]))
    if args.mode == "skill" and not args.skill_id:
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Skill mode requires --skill-id.", failed_layer="host-input", fail_closed_reason="missing --skill-id", fallback_to=["loom skills list --json"]))
    if args.action in {"install", "upgrade"}:
        try:
            managed_writes = install_cli_managed_surfaces(target, host=host, mode=args.mode, skill_id=args.skill_id)
        except RuntimeError as exc:
            return emit(output(command, "block", schema=HOST_SCHEMA, summary="Host adapter payload could not be installed by the Loom CLI.", target=str(target), host=host, mode=args.mode, mutates=True, failed_layer="host-payload", fail_closed_reason=str(exc), fallback_to=["loom host doctor --host <host> --json", "loom skills check --target <repo> --json"]))
        state_path = target / ".loom" / "installed-state.json"
        write_json(state_path, build_installed_state(target, host=host, mode=args.mode, skill_id=args.skill_id))
        managed_writes.append(relative_to_target(state_path, target))
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Host plugin/SKILLS payload installed by the Loom CLI.", target=str(target), host=host, mode=args.mode, mutates=True, managed_writes=managed_writes, installed_state_path=str(state_path), fallback_to=None))
    ok, checks = verify_cli_managed_surfaces(target, host=host, mode=args.mode, skill_id=args.skill_id)
    return emit(output(command, "pass" if ok else "block", schema=HOST_SCHEMA, summary="Host plugin/SKILLS payload verified." if ok else "Host plugin/SKILLS payload is incomplete.", target=str(target), host=host, mode=args.mode, mutates=False, checks=checks, failed_layer=None if ok else "host-payload", fail_closed_reason=None if ok else "one or more CLI-managed host payload checks failed", fallback_to=None if ok else ["loom host install --host <host> --apply --json", "loom skills sync --target <repo> --apply --json"]))


def handle_skills(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom skills")
    parser.add_argument("action", choices=("list", "generate", "sync", "check", "doctor", "package", "release-check"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"skills {args.action}"
    target = resolve_target(args.target)
    registry = read_optional_json(SKILLS_ROOT / "registry.json") or {}
    entries = registry.get("entries") if isinstance(registry, dict) else []
    if args.action == "list":
        return emit(output(command, "pass", schema=SKILLS_SCHEMA, summary="Generated skills registry listed.", registry_version=registry.get("registry_version"), root_entry=registry.get("root_entry"), skills=entries, fallback_to=None))
    if args.action in {"generate", "sync"} and not args.apply:
        return emit(output(command, "block", schema=SKILLS_SCHEMA, summary=f"`loom {command}` mutates the generated skills surface and requires --apply.", target=str(target), mutates=True, failed_layer="skills-surface", fail_closed_reason="explicit --apply is required before rewriting skills/", fallback_to=["loom skills check --target <repo> --json"]))
    if args.action in {"generate", "sync"}:
        try:
            managed_writes = sync_skills_payload(target)
        except RuntimeError as exc:
            return emit(output(command, "block", schema=SKILLS_SCHEMA, summary="Skills payload sync failed.", target=str(target), mutates=True, failed_layer="skills-surface", fail_closed_reason=str(exc), fallback_to=["python3 tools/skills_surface.py check"]))
        return emit(output(command, "pass", schema=SKILLS_SCHEMA, summary="CLI-managed skills payload synchronized.", target=str(target), mutates=True, managed_writes=managed_writes, fallback_to=None))
    if args.action in {"check", "doctor", "release-check"}:
        checks = []
        if target.resolve() == REPO_ROOT.resolve():
            checks.append([sys.executable, str(TOOLS_ROOT / "skills_surface.py"), "check"])
        else:
            ok, managed_checks = verify_cli_managed_surfaces(target, host="codex", mode="full-repo")
            checks.append({"command": "loom skills check installed payload", "returncode": 0 if ok else 1, "stdout": json.dumps(managed_checks, ensure_ascii=False), "stderr": "" if ok else "installed skills payload is incomplete"})
        if args.action == "release-check":
            checks.extend(
                [
                    [sys.executable, str(TOOLS_ROOT / "host_adapter_check.py")],
                    [sys.executable, str(TOOLS_ROOT / "version_surface_check.py")],
                    [sys.executable, str(TOOLS_ROOT / "check_release_surface.py")],
                ]
            )
        results = []
        for check in checks:
            if isinstance(check, dict):
                results.append(check)
            else:
                completed = run_capture(check)
                results.append({"command": " ".join(check), "returncode": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()})
        failures = [item for item in results if item["returncode"] != 0]
        result = "pass" if not failures else "block"
        release_authority = None
        if args.action == "release-check":
            release_authority = {
                "active_cli_line": "loom",
                "candidate_authority": "VERSION",
                "published_evidence": ["GitHub v* tag", "GitHub Release"],
                "legacy_installer_evidence": {
                    "package": "@mc-and-his-agents/loom-installer",
                    "final_active_baseline": "0.1.119",
                    "tag": "loom-installer-v0.1.119",
                    "active_cli_evidence": False,
                },
            }
        return emit(output(command, result, schema=SKILLS_SCHEMA, summary="Skills surface checks passed." if result == "pass" else "Skills surface checks failed.", registry_version=registry.get("registry_version"), root_entry=registry.get("root_entry"), checks=results, release_authority=release_authority, failed_layer=None if result == "pass" else "skills-surface", fail_closed_reason=None if result == "pass" else "one or more skills checks failed", fallback_to=None if result == "pass" else ["loom skills generate --apply --json"]))
    package_records = []
    for entry in entries or []:
        package_path = SKILLS_ROOT / entry["id"] / "loom-package.json"
        package_records.append(read_optional_json(package_path) or {"package_id": entry["id"], "missing": str(package_path)})
    return emit(output(command, "pass", schema=SKILLS_SCHEMA, summary="Skill package metadata collected without packing artifacts.", mutates=False, registry_version=registry.get("registry_version"), packages=package_records, fallback_to=["npm run check:release --prefix packages/loom-installer"]))


def handle_init(argv: list[str]) -> int:
    if not argv:
        return emit(output("init", "block", schema=SCENARIO_SCHEMA, summary="Init requires an operation.", failed_layer="scenario-input", fail_closed_reason="missing init operation", fallback_to=["loom init bootstrap --target <repo> --json", "loom init verify --target <repo> --json"]))
    return emit_delegated("init", "loom_init.py", strip_json_flag(argv), failed_layer="loom-init", fallback_to=["loom init verify --target <repo> --json", "loom doctor --target <repo> --json"])


def handle_adopt(argv: list[str]) -> int:
    if not argv:
        return emit(output("adopt", "block", schema=SCENARIO_SCHEMA, summary="Adopt requires an operation.", failed_layer="adoption-input", fail_closed_reason="missing adopt operation", fallback_to=["loom adopt verify --target <repo> --item <item> --json", "loom init bootstrap --target <repo> --json"]))
    operation = argv[0]
    if operation != "verify":
        return emit(output("adopt", "block", schema=SCENARIO_SCHEMA, summary="Only `loom adopt verify` is implemented for the CLI-first adoption contract.", failed_layer="adoption-input", fail_closed_reason=f"unsupported adopt operation: {operation}", fallback_to=["loom adopt verify --target <repo> --item <item> --json", "loom init bootstrap --target <repo> --json"]))
    return emit_flow("adopt", ["adopt", "verify", *strip_json_flag(argv[1:])], fallback_to=["loom init verify --target <repo> --json", "loom profile status --target <repo> --json"])


def handle_route(argv: list[str]) -> int:
    return emit_delegated("route", "loom_init.py", ["route", *strip_json_flag(argv)], failed_layer="loom-route", fallback_to=["loom route --target <repo> --task <task> --json", "loom init verify --target <repo> --json"])


def handle_status(argv: list[str]) -> int:
    return emit_delegated("status", "loom_status.py", strip_json_flag(argv), failed_layer="loom-status", fallback_to=["loom fact-chain --target <repo> --json", "loom checkpoint admission --target <repo> --json"])


def handle_fact_chain(argv: list[str]) -> int:
    return emit_flow("fact-chain", ["fact-chain", *strip_json_flag(argv)], fallback_to=["loom init verify --target <repo> --json", "loom status --target <repo> --json"])


def handle_profile(argv: list[str]) -> int:
    if not argv:
        return emit(output("profile", "block", schema=PROFILE_SCHEMA, summary="Profile requires an operation.", failed_layer="profile-input", fail_closed_reason="missing profile operation", fallback_to=["loom profile status --target <repo> --json", "loom profile upgrade-plan --target <repo> --json"]))
    operation = argv[0]
    if operation not in {"status", "upgrade-plan", "upgrade"}:
        return emit(output("profile", "block", schema=PROFILE_SCHEMA, summary="Unsupported profile operation.", failed_layer="profile-input", fail_closed_reason=f"unsupported profile operation: {operation}", fallback_to=["loom profile status --target <repo> --json", "loom profile upgrade-plan --target <repo> --json"]))
    return emit_flow(f"profile {operation}", ["governance-profile", operation, *strip_json_flag(argv[1:])], fallback_to=["loom profile status --target <repo> --json", "docs/adoption/github-profile-upgrade.md"])


def handle_checkpoint(argv: list[str]) -> int:
    if not argv:
        return emit(output("checkpoint", "block", schema=GATE_SCHEMA, summary="Checkpoint requires a stage.", failed_layer="checkpoint-input", fail_closed_reason="missing checkpoint stage", fallback_to=["loom checkpoint admission --target <repo> --json", "loom checkpoint build --target <repo> --json", "loom checkpoint merge --target <repo> --json"]))
    stage = argv[0]
    if stage not in {"admission", "build", "merge"}:
        return emit(output("checkpoint", "block", schema=GATE_SCHEMA, summary="Unsupported checkpoint stage.", failed_layer="checkpoint-input", fail_closed_reason=f"unsupported checkpoint stage: {stage}", fallback_to=["loom checkpoint admission --target <repo> --json", "loom checkpoint build --target <repo> --json", "loom checkpoint merge --target <repo> --json"]))
    return emit_flow(f"checkpoint {stage}", ["checkpoint", stage, *strip_json_flag(argv[1:])], fallback_to=["loom status --target <repo> --json", "loom fact-chain --target <repo> --json"])


def handle_gate(argv: list[str]) -> int:
    if not argv:
        return emit(output("gate", "block", schema=GATE_SCHEMA, summary="Gate requires a gate name.", failed_layer="gate-input", fail_closed_reason="missing gate name", fallback_to=["loom gate pre-review --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"]))
    gate = argv[0]
    rest = strip_json_flag(argv[1:])
    if gate in {"pre-review", "spec-review", "review"}:
        return emit_flow(f"gate {gate}", ["flow", gate, *rest], fallback_to=["loom status --target <repo> --json", f"loom {gate} --target <repo> --json"])
    if gate == "pr":
        return emit_flow("gate pr", ["pr-gate", "check", *rest], fallback_to=["loom pr gate <pr> --json", "loom review --target <repo> --json"])
    if gate == "merge":
        return emit_flow("gate merge", ["controlled-merge", "check", *rest], fallback_to=["loom checkpoint merge --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"])
    if gate == "closeout":
        return emit_flow("gate closeout", ["closeout", "check", *rest], fallback_to=["loom merge check <pr> --json", "loom status --target <repo> --json"])
    return emit(output("gate", "block", schema=GATE_SCHEMA, summary="Unsupported gate name.", failed_layer="gate-input", fail_closed_reason=f"unsupported gate name: {gate}", fallback_to=["loom gate pre-review --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"]))


def handle_scenario(command: str, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--output")
    parser.add_argument("--build-evidence")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--project", type=int)
    parser.add_argument("--branch")
    parser.add_argument("--project-drift-mode", choices=("advisory", "blocking"), default="advisory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(command, target, "target path does not exist"))

    flow_operations = {
        "story": "story",
        "build": "build",
        "pre-review": "pre-review",
        "handoff": "handoff",
        "retire": "handoff",
    }
    if command in flow_operations:
        flow_args = ["flow", flow_operations[command], "--target", str(target)]
        for flag, value in (
            ("--item", args.item),
            ("--output", args.output),
            ("--build-evidence", args.build_evidence),
            ("--owner", args.owner),
            ("--repo", args.repo_name),
            ("--issue", args.issue),
            ("--pr", args.pr),
            ("--pr-payload-file", args.pr_payload_file),
            ("--project", args.project),
            ("--branch", args.branch),
            ("--project-drift-mode", args.project_drift_mode if command in {"pre-review"} else None),
        ):
            if value is not None:
                flow_args.extend([flag, str(value)])
        payload = flow_payload(command, flow_args, fallback_to=["loom status --target <repo> --json", "loom checkpoint build --target <repo> --json"])
        payload.setdefault("schema_version", SCENARIO_SCHEMA)
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        if command == "retire":
            payload["retire_contract"] = {
                "mutates": False,
                "summary": "Retire currently exposes the handoff/cleanup checklist and does not delete worktrees or host objects.",
                "fallback_to": ["loom workspace retire --target <repo> --json", "loom handoff --target <repo> --json"],
            }
        return emit(payload)

    if command in {"spec", "plan"}:
        item = args.item or "unknown-item"
        relative = f".loom/specs/{item}/{'spec.md' if command == 'spec' else 'plan.md'}"
        locator = target / relative
        return emit(
            output(
                command,
                "block" if not locator.exists() else "pass",
                schema=SCENARIO_SCHEMA,
                summary=f"{command} scenario locator {'exists' if locator.exists() else 'is missing'}; authoring remains caller-owned.",
                target=str(target),
                item=item,
                locator=relative,
                mutates=False,
                failed_layer=None if locator.exists() else f"{command}-carrier",
                fail_closed_reason=None if locator.exists() else f"missing {relative}",
                fallback_to=None if locator.exists() else ["loom story --target <repo> --item <item> --json", "docs/methodology/templates/spec-suite.md"],
            )
        )

    if command == "closeout":
        flow_args = ["closeout", "check", "--target", str(target)]
        if args.item:
            flow_args.extend(["--item", args.item])
        if args.issue is not None:
            flow_args.extend(["--issue", str(args.issue)])
        if args.pr is not None:
            flow_args.extend(["--pr", str(args.pr)])
        payload = flow_payload(command, flow_args, fallback_to=["loom merge check <pr> --json", "loom reconcile --issue <issue> --pr <pr> --json"])
        payload.setdefault("schema_version", SCENARIO_SCHEMA)
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return emit(payload)

    return emit(output(command, "block", schema=SCENARIO_SCHEMA, summary="Unsupported scenario command.", failed_layer="scenario-input", fail_closed_reason=command, fallback_to=["loom help --json"]))


def dispatch(command: str, forwarded_args: list[str]) -> int:
    tool_name, prefix = COMMAND_ROUTES[command]
    tool_path = TOOLS_ROOT / tool_name
    if not tool_path.exists():
        return emit(
            output(
                command,
                "block",
                summary="Delegated compatibility wrapper is missing.",
                failed_layer="delegated-wrapper",
                fail_closed_reason=f"missing delegated tool: {tool_path}",
                fallback_to=["loom help --json"],
            ),
            stream=sys.stderr,
        )
    completed = subprocess.run([sys.executable, str(tool_path), *prefix, *forwarded_args], check=False)
    return completed.returncode


def reserved_command(command: str, argv: list[str]) -> int:
    entry = COMMAND_INDEX[command]
    wants_json = "--json" in argv or True
    payload = output(
        command,
        "block",
        summary="Command is reserved by the CLI-first contract but not implemented in this Work Item.",
        command_status=entry["status"],
        domain=entry["domain"],
        failed_layer="cli-command-implementation",
        fail_closed_reason="reserved command has no executable implementation yet",
        fallback_to=["loom help --json"],
    )
    if wants_json:
        return emit(payload)
    print(f"loom: {command} is reserved but not implemented", file=sys.stderr)
    return 2


def resolve_command(argv: list[str]) -> tuple[str, list[str]] | None:
    if not argv:
        return None
    for length in (3, 2, 1):
        if len(argv) < length:
            continue
        candidate = " ".join(argv[:length])
        if candidate in COMMAND_INDEX or candidate in COMMAND_ROUTES or candidate in {"flow", "check", "suite"}:
            return candidate, argv[length:]
    return argv[0], argv[1:]


def handle_suite(argv: list[str]) -> int:
    if not argv:
        return emit(
            output(
                "suite",
                "block",
                summary="Suite command requires an action.",
                mutates=False,
                failed_layer="suite-input",
                fail_closed_reason="missing suite action",
                fallback_to=["loom suite inspect --target <repo> --item <item> --json"],
            )
        )

    action = argv[0]
    if action != "inspect":
        return emit(
            output(
                f"suite {action}",
                "block",
                summary="Unsupported suite action.",
                mutates=False,
                failed_layer="suite-input",
                fail_closed_reason=f"unsupported suite action: {action}",
                fallback_to=["loom suite inspect --target <repo> --item <item> --json"],
            )
        )

    parser = argparse.ArgumentParser(prog="loom suite inspect")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv[1:])
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("suite inspect", target, "target path does not exist"))

    payload = output(
        "suite inspect",
        "pass",
        target=str(target),
        item_id=args.item,
        summary="Suite state is unknown; no suite path decision was derived.",
        mutates=False,
        payload={
            "suite_path": "unknown",
            "suite_locator": None,
            "path_decision_locator": None,
            "artifact_inventory": [],
            "missing_inputs": ["suite_path_decision"],
            "advisory_gaps": [
                {
                    "id": "suite-inspect-unknown-path",
                    "classification": "missing",
                    "failure_kind": "missing_suite_path_decision",
                    "surface": "suite",
                    "source_locator": None,
                    "consumer_impact": "inspect-only",
                    "remediation_direction": "Author or link a suite path decision before readiness validation.",
                    "fallback_to": "loom suite inspect --target <repo> --item <item> --json",
                }
            ],
        },
    )
    return emit(payload)


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        print_usage(sys.stderr)
        return 2

    resolved = resolve_command(argv[1:])
    if resolved is None:
        print_usage(sys.stderr)
        return 2
    command, forwarded = resolved

    if command in {"-h", "--help", "help"}:
        return handle_help(forwarded)
    if command == "version":
        return handle_version(forwarded)
    if command == "detect":
        return handle_detect(forwarded)
    if command == "doctor":
        return handle_doctor(forwarded)
    if command == "installed-state":
        return handle_installed_state(forwarded)
    if command.startswith("installed-state "):
        return handle_installed_state(command.split()[1:] + forwarded)
    if command == "repair" or command.startswith("repair "):
        repair_args = command.split()[1:] + forwarded if command.startswith("repair ") else forwarded
        return handle_repair(repair_args)
    if command in {"install", "upgrade-plan", "upgrade", "rollback", "verify"}:
        return handle_delivery(command, forwarded)
    if command == "workspace" or command.startswith("workspace "):
        workspace_args = command.split()[1:] + forwarded if command.startswith("workspace ") else forwarded
        return handle_workspace(workspace_args)
    if command == "issue" or command.startswith("issue "):
        issue_args = command.split()[1:] + forwarded if command.startswith("issue ") else forwarded
        return handle_issue(issue_args)
    if command == "project" or command.startswith("project "):
        project_args = command.split()[1:] + forwarded if command.startswith("project ") else forwarded
        return handle_project(project_args)
    if command == "pr" or command.startswith("pr "):
        pr_args = command.split()[1:] + forwarded if command.startswith("pr ") else forwarded
        return handle_pr(pr_args)
    if command == "merge" or command.startswith("merge "):
        merge_args = command.split()[1:] + forwarded if command.startswith("merge ") else forwarded
        return handle_merge(merge_args)
    if command == "reconcile":
        return handle_reconcile(forwarded)
    if command == "host" or command.startswith("host "):
        host_args = command.split()[1:] + forwarded if command.startswith("host ") else forwarded
        return handle_host(host_args)
    if command == "skills" or command.startswith("skills "):
        skills_args = command.split()[1:] + forwarded if command.startswith("skills ") else forwarded
        return handle_skills(skills_args)
    if command == "suite":
        return handle_suite(forwarded)
    if command == "init":
        return handle_init(forwarded)
    if command == "adopt":
        return handle_adopt(forwarded)
    if command == "route":
        return handle_route(forwarded)
    if command == "status":
        return handle_status(forwarded)
    if command == "fact-chain":
        return handle_fact_chain(forwarded)
    if command == "profile" or command.startswith("profile "):
        profile_args = command.split()[1:] + forwarded if command.startswith("profile ") else forwarded
        return handle_profile(profile_args)
    if command == "checkpoint" or command.startswith("checkpoint "):
        checkpoint_args = command.split()[1:] + forwarded if command.startswith("checkpoint ") else forwarded
        return handle_checkpoint(checkpoint_args)
    if command == "gate" or command.startswith("gate "):
        gate_args = command.split()[1:] + forwarded if command.startswith("gate ") else forwarded
        return handle_gate(gate_args)
    if command in {"story", "spec", "plan", "build", "pre-review", "closeout", "handoff", "retire"}:
        return handle_scenario(command, forwarded)
    if command in COMMAND_ROUTES:
        return dispatch(command, forwarded)
    if command in COMMAND_INDEX:
        return reserved_command(command, forwarded)

    payload = output(
        command,
        "block",
        summary="Unknown Loom command.",
        failed_layer="cli-command-router",
        fail_closed_reason=f"unknown command: {command}",
        fallback_to=["loom help --json"],
    )
    emit(payload, stream=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
