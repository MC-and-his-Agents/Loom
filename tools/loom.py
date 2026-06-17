#!/usr/bin/env python3
"""CLI-first Loom control-plane entry.

The command surface is intentionally broader than the implementation surface.
Commands that are not implemented in this phase fail closed with a structured
JSON block instead of silently falling back to legacy wrappers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib as _tomllib
except ModuleNotFoundError:
    _tomllib = None
    try:
        import tomli as _tomli
    except ModuleNotFoundError:
        _tomli = None
else:
    _tomli = None


class TomlDecodeError(ValueError):
    pass


def parse_toml_text(raw: str) -> dict[str, Any]:
    if _tomllib is not None:
        return _tomllib.loads(raw)
    if _tomli is not None:
        return _tomli.loads(raw)
    raise TomlDecodeError("TOML parsing requires Python 3.11+ tomllib or the tomli package")


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
WORKSTATION_SCHEMA = "loom-workstation-registration/v1"
SKILLS_SCHEMA = "loom-skills-surface/v1"
SCENARIO_SCHEMA = "loom-scenario-control/v1"
PROFILE_SCHEMA = "loom-governance-profile-control/v1"
GATE_SCHEMA = "loom-gate-control/v1"
DELIVERY_SCHEMA = "loom-delivery-control/v1"

RUNTIME_PROVIDER_GLOBAL_CLI = "global-cli"
RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER = "repo-local-wrapper"
GLOBAL_CLI_PROVIDER_LAYER = "global-cli-runtime-provider"
GLOBAL_CLI_REQUIRED_COMMANDS = [
    "installed-state validate",
    "detect",
    "doctor",
    "verify",
    "fact-chain",
    "status",
    "story",
]


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
        "summary": "Validate installed-state schema, layers, graph, runtime-provider declarations, and fail-closed metadata.",
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
        "summary": "Diagnose installed-state readiness and runtime provider mode: global-cli without .loom/bin, or repo-local-wrapper with declared .loom/bin carriers.",
    },
    {
        "command": "repair plan",
        "domain": "repair",
        "status": "implemented",
        "json": True,
        "summary": "Emit a non-mutating repair plan for legacy, drifted, runtime-provider, or host-complete active carrier surfaces; it does not mutate host state.",
    },
    {
        "command": "repair apply",
        "domain": "repair",
        "status": "implemented",
        "json": True,
        "summary": "Apply explicit safe repo carrier closeout repairs for host-complete active carriers; fail closed for installed-surface repair actions and do not close host objects.",
    },
    {
        "command": "install",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Install explicit repository adoption metadata, embedded payload, compatibility skills surfaces, or declared runtime-provider mode.",
    },
    {
        "command": "upgrade-plan",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Plan non-mutating upgrades across installed-state, legacy surfaces, and runtime-provider carriers.",
    },
    {"command": "upgrade", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "rollback", "domain": "delivery", "status": "implemented", "json": True},
    {
        "command": "verify",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Verify the same readiness boundary as doctor, including global-cli versus repo-local-wrapper runtime provider mode.",
    },
    {"command": "init", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "adopt", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "route", "domain": "scenario", "status": "implemented", "json": True},
    {
        "command": "carrier closeout-sync",
        "domain": "harness",
        "status": "implemented",
        "json": True,
        "summary": "Explicitly write structured terminal closeout metadata to versioned progress carriers without mutating host state.",
    },
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
    {
        "command": "closeout",
        "domain": "scenario",
        "status": "implemented",
        "json": True,
        "summary": "Check closeout readiness; host closeout sync remains separate from local retire and carrier closeout-sync.",
    },
    {
        "command": "closeout queue status",
        "domain": "scenario",
        "status": "implemented",
        "json": True,
        "summary": "Read retained post-merge closeout residue queue status and suggest the next read-only command.",
    },
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
    {
        "command": "gate freeze check",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Read-only validation of the loom-gate-freeze/v1 hosted gate admission input snapshot.",
    },
    {
        "command": "gate freeze write",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Write a repo-local loom-gate-freeze/v1 snapshot under .loom/runtime/gate-freeze without mutating host truth.",
    },
    {
        "command": "gate closeout",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Run the closeout gate over host readback, release/no-release evidence, and repo carrier consistency without performing host writes.",
    },
    {"command": "workspace create", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace locate", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace check", "domain": "host-control", "status": "implemented", "json": True},
    {
        "command": "workspace retire",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Emit local-only worksite retirement evidence; does not close host objects or write versioned terminal carriers.",
    },
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
    {
        "command": "reconcile",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Read or align host closeout control-plane state; repo carrier closeout-sync remains a separate versioned-carrier write.",
    },
    {"command": "host list", "domain": "host", "status": "implemented", "json": True},
    {"command": "host doctor", "domain": "host", "status": "implemented", "json": True},
    {"command": "host install", "domain": "host", "status": "implemented", "json": True},
    {"command": "host verify", "domain": "host", "status": "implemented", "json": True},
    {
        "command": "host register",
        "domain": "host",
        "status": "implemented",
        "json": True,
        "summary": "Inspect or explicitly register a Codex Loom plugin provider with the local workstation.",
    },
    {"command": "host upgrade", "domain": "host", "status": "implemented", "json": True},
    {"command": "host remove", "domain": "host", "status": "implemented", "json": True},
    {"command": "skills list", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills generate", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills sync", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills check", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills doctor", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills package", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills release-check", "domain": "skills", "status": "implemented", "json": True},
    {
        "command": "suite inspect",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Inspect suite path decision and repo-relative artifact inventory.",
    },
    {
        "command": "suite scaffold",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Plan or explicitly apply repo-local minimal or full spec suite scaffold writes.",
    },
    {
        "command": "suite validate",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Validate the current suite path decision and core readiness envelope without mutating files.",
    },
    {
        "command": "suite evidence inspect",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Inspect evidence-map locator, rows, freshness, and repo-local evidence bindings.",
    },
    {
        "command": "suite evidence scaffold",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Plan or explicitly apply repo-local evidence-map scaffold writes without marking evidence present.",
    },
    {
        "command": "suite evidence validate",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Validate behavior, test, and fresh verification evidence-map freshness without mutating files.",
    },
    {
        "command": "suite carrier inspect",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Inspect task-carrier locators, normalized status, relationships, and Work Item backlinks.",
    },
    {
        "command": "suite carrier validate",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Validate task-carrier locator/status/backlink consistency without promoting carrier truth.",
    },
]

COMMAND_INDEX = {entry["command"]: entry for entry in COMMANDS}
IMPLEMENTED_SUITE_COMMANDS = tuple(
    entry["command"]
    for entry in COMMANDS
    if entry.get("domain") == "suite" and entry.get("status") == "implemented"
)
SUITE_SUPPORT_MARKERS = {
    "suite-command-surface",
    "suite-commands",
    "loom-suite-commands",
    "full-spec-suite-cli",
    "full-spec-suite-cli-surface",
}

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
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(args, cwd=cwd, env=env, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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


def target_from_args(argv: list[str]) -> Path:
    for index, arg in enumerate(argv):
        if arg == "--target" and index + 1 < len(argv):
            return resolve_target(argv[index + 1])
        if arg.startswith("--target="):
            return resolve_target(arg.split("=", 1)[1])
    return resolve_target(".")


def global_cli_command_entry(command: str, target: Path, argv: list[str]) -> str:
    forwarded = strip_json_flag(argv)
    if "--target" not in forwarded and not any(arg.startswith("--target=") for arg in forwarded):
        forwarded = [*forwarded, "--target", str(target)]
    return " ".join(["loom", command, *forwarded, "--json"])


def annotate_global_cli_runtime_entrypoint(payload: dict[str, Any], *, command: str, target: Path, argv: list[str]) -> None:
    if target_runtime_provider(target) != RUNTIME_PROVIDER_GLOBAL_CLI:
        return
    entry = global_cli_command_entry(command, target, argv)
    payload["runtime_provider"] = RUNTIME_PROVIDER_GLOBAL_CLI
    payload["current_runtime_entrypoint"] = entry
    if command == "fact-chain":
        fact_chain = payload.get("fact_chain")
        if isinstance(fact_chain, dict):
            old_read_entry = fact_chain.get("read_entry")
            if isinstance(old_read_entry, str) and old_read_entry and old_read_entry != entry:
                payload.setdefault("retained_provenance", []).append(
                    {
                        "kind": "historical-runtime-entrypoint",
                        "locator": old_read_entry,
                        "classification": "retained-provenance",
                        "reason": "installed-state declares global-cli as the current runtime provider",
                    }
                )
            fact_chain["read_entry"] = entry
    elif command == "status":
        payload["status_entrypoint"] = entry
    elif command == "story":
        payload["story_carrier_entrypoint"] = entry


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


def normalize_support_marker(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    marker = value.strip().lower().replace("_", "-")
    return marker or None


def extract_declared_support_entries(raw: Any) -> tuple[list[str], list[str]]:
    markers: list[str] = []
    suite_commands: list[str] = []
    if raw is None:
        return markers, suite_commands
    if isinstance(raw, str):
        marker = normalize_support_marker(raw)
        if marker:
            markers.append(marker)
        return markers, suite_commands
    if isinstance(raw, list):
        for item in raw:
            item_markers, item_commands = extract_declared_support_entries(item)
            markers.extend(item_markers)
            suite_commands.extend(item_commands)
        return markers, suite_commands
    if isinstance(raw, dict):
        for key in ("suite_commands", "suite-command-surface", "suite_command_surface"):
            commands = raw.get(key)
            if isinstance(commands, list):
                suite_commands.extend(command for command in commands if isinstance(command, str) and command.strip())
        for key in ("surface", "support", "id", "name"):
            marker = normalize_support_marker(raw.get(key))
            if marker:
                markers.append(marker)
        for key in ("supports", "declared_support", "provided_surfaces"):
            item_markers, item_commands = extract_declared_support_entries(raw.get(key))
            markers.extend(item_markers)
            suite_commands.extend(item_commands)
    return markers, suite_commands


def suite_support_declaration(state: Any) -> tuple[bool, list[str], list[str]]:
    declarations: list[str] = []
    declared_commands: list[str] = []
    if not isinstance(state, dict):
        return False, declarations, declared_commands
    for key in ("declared_support", "supported_surfaces", "provides"):
        markers, commands = extract_declared_support_entries(state.get(key))
        declarations.extend(markers)
        declared_commands.extend(commands)
    layers = state.get("layers", [])
    if isinstance(layers, list):
        for layer in layers:
            if not isinstance(layer, dict):
                continue
            for key in ("declared_support", "supported_surfaces", "provides"):
                markers, commands = extract_declared_support_entries(layer.get(key))
                declarations.extend(markers)
                declared_commands.extend(commands)
    declaration_set = set(declarations)
    declares_surface = bool(declaration_set & SUITE_SUPPORT_MARKERS) or bool(declared_commands)
    required_commands = sorted(set(declared_commands)) if declared_commands else list(IMPLEMENTED_SUITE_COMMANDS)
    return declares_surface, sorted(declaration_set), required_commands


def suite_command_surface_check(state: Any) -> dict[str, Any]:
    declared, declarations, required_commands = suite_support_declaration(state)
    matrix = {entry["command"]: entry for entry in command_matrix()}
    exposed_suite_commands = sorted(command for command, entry in matrix.items() if entry.get("domain") == "suite")
    if not declared:
        return {
            "name": "suite-command-surface",
            "result": "pass",
            "summary": "Suite command support is not declared for this installed-state; doctor does not require the suite surface.",
            "declared_support": False,
            "declarations": declarations,
            "required_commands": [],
            "exposed_commands": exposed_suite_commands,
        }

    schema_errors: list[dict[str, str]] = []
    for command in required_commands:
        entry = matrix.get(command)
        if entry is None:
            schema_errors.append({"command": command, "reason": "missing from loom help --json command matrix"})
            continue
        if entry.get("domain") != "suite":
            schema_errors.append({"command": command, "reason": "command matrix domain is not suite"})
        if entry.get("status") != "implemented":
            schema_errors.append({"command": command, "reason": "declared suite command is not implemented"})
        if entry.get("json") is not True:
            schema_errors.append({"command": command, "reason": "declared suite command does not expose json=true"})
    result = "pass" if not schema_errors else "block"
    return {
        "name": "suite-command-surface",
        "result": result,
        "summary": "Declared suite command surface matches loom help --json." if result == "pass" else "Declared suite command surface disagrees with loom help --json.",
        "declared_support": True,
        "declarations": declarations,
        "required_commands": required_commands,
        "exposed_commands": exposed_suite_commands,
        "help_schema": "loom help --json",
        "schema_errors": schema_errors,
        **({} if result == "pass" else {
            "failed_layer": "suite-command-surface",
            "fallback_to": ["loom repair plan", "loom help --json", "loom suite inspect --target <repo> --item <item> --json"],
        }),
    }


def suite_verify_requirement(state: Any, item: str | None) -> dict[str, Any]:
    required = bool(item)
    sources: list[str] = ["work-item-gate"] if item else []
    configured_item: str | None = None

    def consume(raw: Any, source: str) -> None:
        nonlocal required, configured_item
        if not isinstance(raw, dict):
            return
        suite_value = raw.get("suite_validation", raw.get("suite"))
        if isinstance(suite_value, str) and suite_value.strip().lower() in {"required", "blocking", "full"}:
            required = True
            sources.append(source)
        elif suite_value is True:
            required = True
            sources.append(source)
        candidate_item = raw.get("suite_item") or raw.get("work_item") or raw.get("item")
        if isinstance(candidate_item, str) and candidate_item.strip() and configured_item is None:
            configured_item = candidate_item.strip()

    if isinstance(state, dict):
        for key in ("verify_requirements", "profile_requirements", "gate_requirements"):
            consume(state.get(key), f"installed-state.{key}")
        profile = state.get("profile")
        if isinstance(profile, dict):
            consume(profile.get("requirements"), "installed-state.profile.requirements")
        layers = state.get("layers", [])
        if isinstance(layers, list):
            for index, layer in enumerate(layers, start=1):
                if not isinstance(layer, dict):
                    continue
                layer_id = layer.get("id") if isinstance(layer.get("id"), str) else f"layer[{index}]"
                for key in ("verify_requirements", "profile_requirements", "gate_requirements"):
                    consume(layer.get(key), f"installed-state.{layer_id}.{key}")

    return {
        "required": required,
        "item_id": item or configured_item,
        "sources": sorted(set(sources)),
        "summary": "suite validation is required for this verify invocation." if required else "suite validation is not required for this verify invocation.",
    }


def suite_validation_check(target: Path, item: str | None) -> dict[str, Any]:
    if not item:
        return {
            "name": "suite-validation",
            "result": "block",
            "summary": "Suite validation is required but no Work Item was provided.",
            "missing_inputs": ["suite_validation_item"],
            "failed_layer": "suite-verify-requirement",
            "fail_closed_reason": "suite validation requires --item or installed-state suite_item",
            "fallback_to": ["loom verify --target <repo> --item <item> --json", "loom suite validate --target <repo> --item <item> --json"],
        }
    summary, result, payload, failed_layer, fail_closed_reason, fallback_to = suite_validate_payload(target, item)
    return {
        "name": "suite-validation",
        "result": result,
        "summary": summary,
        "item_id": item,
        "command": "loom suite validate",
        "mutates": False,
        "failed_layer": failed_layer,
        "fail_closed_reason": fail_closed_reason,
        "missing_inputs": payload.get("missing_inputs", []),
        "blocking_gaps": payload.get("blocking_gaps", []),
        "advisory_gaps": payload.get("advisory_gaps", []),
        "fallback_to": fallback_to,
        "payload": payload,
    }


def print_usage(stream) -> None:
    stream.write(
        "usage: loom <command> [args ...]\n\n"
        "CLI-first Loom control-plane entry.\n\n"
        "core commands:\n"
        "  version [--json]\n"
        "  help [--json]\n"
        "  installed-state show|validate|export --target <repo> [--json]\n\n"
        "install, provider, and repair commands:\n"
        "  install, doctor, verify, upgrade-plan, repair plan\n"
        "  global-cli repos use the root loom provider and do not expect .loom/bin\n"
        "  repo-local-wrapper repos keep declared .loom/bin carriers as valid wrappers\n\n"
        "scenario and gate commands:\n"
        "  init, adopt, route, status, fact-chain, profile, checkpoint, gate\n"
        "  resume, spec-review, review, merge-ready, check\n"
        "  suite inspect --target <repo> --item <item> [--json]\n"
        "  suite scaffold --target <repo> --item <item> [--suite minimal|full] [--apply] [--json]\n\n"
        "  suite validate --target <repo> --item <item> [--json]\n\n"
        "  suite evidence inspect|scaffold|validate --target <repo> --item <item> [--apply] [--json]\n\n"
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
    layers: list[dict[str, Any]] = []
    graph_layers: list[str] = []
    graph_edges: list[dict[str, str]] = []
    runtime_provider = RUNTIME_PROVIDER_GLOBAL_CLI if mode == "metadata-only" else RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER
    if mode == "metadata-only":
        layers.extend(
            [
                {
                    "id": "adoption-metadata",
                    "layer_type": "repository-adoption-metadata",
                    "installed_path": ".loom/installed-state.json",
                    "version_context": {
                        "repo_version": versions["repo_version"],
                        "installed_state_schema": INSTALLED_STATE_SCHEMA,
                    },
                    "runtime_state": "ready",
                    "upgrade_eligibility": "current",
                    "provides": ["repository adoption truth"],
                    "consumes": ["user-skills-provider", "global-cli-provider"],
                },
                {
                    "id": "user-skills-provider",
                    "layer_type": "user-level-skills-provider",
                    "installed_path": "workstation:codex-loom-plugin",
                    "version_context": {
                        "plugin_surface_version": versions["plugin_surface_version"],
                        "host_adapter_version": versions["host_adapter_version"],
                    },
                    "runtime_state": "ready",
                    "upgrade_eligibility": "current",
                    "provides": ["Loom scenario skills from user-level Codex plugin"],
                    "consumes": [],
                },
                {
                    "id": "global-cli-provider",
                    "layer_type": GLOBAL_CLI_PROVIDER_LAYER,
                    "installed_path": "workstation:loom-cli",
                    "version_context": {
                        "package": "@mc-and-his-agents/loom",
                        "version_requirement": versions["repo_version"],
                    },
                    "runtime_state": "unknown",
                    "upgrade_eligibility": "unknown",
                    "provides": ["loom command semantics", "runtime provider"],
                    "declared_support": {"commands": GLOBAL_CLI_REQUIRED_COMMANDS},
                    "consumes": [],
                },
            ]
        )
        graph_layers.extend(["adoption-metadata", "user-skills-provider", "global-cli-provider"])
        graph_edges.append({"from": "adoption-metadata", "to": "user-skills-provider", "relationship": "requires-external-provider"})
        graph_edges.append({"from": "adoption-metadata", "to": "global-cli-provider", "relationship": "requires-runtime-provider"})
    else:
        layers.append(
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
                "declared_support": {
                    "suite_commands": list(IMPLEMENTED_SUITE_COMMANDS),
                },
                "consumes": [],
            }
        )
        graph_layers.append("runtime")
    if mode in {"full-repo", "skill"}:
        layers.append(
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
            }
        )
        graph_layers.append("skills")
        graph_edges.append({"from": "skills", "to": "runtime", "relationship": "consumes"})
    if mode == "plugin":
        layers.append(
            {
                "id": "plugin-embedded-skills",
                "layer_type": "plugin-embedded-skills",
                "installed_path": "plugins/loom/skills",
                "version_context": {
                    "skills_registry_version": versions["skills_registry_version"],
                    "skill_package_version": versions["skill_package_version"],
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["scenario skills embedded in the Codex plugin payload"],
                "consumes": ["runtime"],
            }
        )
        graph_layers.append("plugin-embedded-skills")
        graph_edges.append({"from": "plugin-embedded-skills", "to": "runtime", "relationship": "consumes"})
    if mode in {"plugin", "skill"}:
        layer_id = "host-adapter" if mode == "plugin" else "single-skill"
        consumed_layer = "plugin-embedded-skills" if mode == "plugin" else "runtime"
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
                "consumes": [consumed_layer],
            }
        )
        graph_layers.append(layer_id)
        graph_edges.append({"from": layer_id, "to": consumed_layer, "relationship": "consumes"})
    return {
        "schema_version": INSTALLED_STATE_SCHEMA,
        "installation_id": f"loom-{target.name or 'repo'}",
        "target": str(target),
        "installed_at": now_iso(),
        "installing_command": f"loom install --mode {mode}",
        "upgrade_eligibility": "current",
        "runtime_provider": runtime_provider,
        "provider_requirements": {
            "global_cli": {
                "required": runtime_provider == RUNTIME_PROVIDER_GLOBAL_CLI,
                "provider": "loom-cli",
                "authority": "workstation",
                "package": "@mc-and-his-agents/loom",
                "executable": "loom",
                "version_requirement": versions["repo_version"],
                "required_commands": GLOBAL_CLI_REQUIRED_COMMANDS,
                "compatibility_mode_allowed": True,
            }
        },
        "repo_payload": {
            "mode": "metadata-only" if mode == "metadata-only" else "embedded" if mode == "plugin" else mode,
            "intentional_absent_paths": ["plugins/loom/skills", ".agents/skills", "skills", ".loom/bin"] if mode == "metadata-only" else [],
        },
        "skills_provider": {
            "provider": "codex-loom-plugin",
            "scope": "user" if mode == "metadata-only" else "repository",
            "required": mode in {"metadata-only", "plugin"},
            "registration_authority": "workstation" if mode == "metadata-only" else "repository-payload",
        },
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


def installed_state_runtime_provider(state: Any) -> str | None:
    if not isinstance(state, dict):
        return None
    provider = state.get("runtime_provider")
    if isinstance(provider, str) and provider.strip():
        return provider.strip()
    layers = state.get("layers", [])
    if isinstance(layers, list):
        if any(isinstance(layer, dict) and layer.get("layer_type") == GLOBAL_CLI_PROVIDER_LAYER for layer in layers):
            return RUNTIME_PROVIDER_GLOBAL_CLI
        if any(isinstance(layer, dict) and layer.get("installed_path") == ".loom/bin" for layer in layers):
            return RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER
    return None


def target_runtime_provider(target: Path) -> str | None:
    path = installed_state_path(target)
    if path is None:
        return None
    try:
        return installed_state_runtime_provider(read_json(path))
    except (OSError, json.JSONDecodeError):
        return None


def global_cli_provider_requirement(state: Any) -> dict[str, Any] | None:
    if not isinstance(state, dict):
        return None
    requirements = state.get("provider_requirements")
    if not isinstance(requirements, dict):
        return None
    global_cli = requirements.get("global_cli")
    return global_cli if isinstance(global_cli, dict) else None


def global_cli_provider_check(state: Any) -> dict[str, Any]:
    requirement = global_cli_provider_requirement(state)
    if installed_state_runtime_provider(state) != RUNTIME_PROVIDER_GLOBAL_CLI and not (
        requirement and requirement.get("required") is True
    ):
        return {
            "name": "global-cli-runtime-provider",
            "result": "pass",
            "summary": "Global CLI runtime provider is not required by this installed-state.",
            "required": False,
        }
    command_names = {entry["command"] for entry in COMMANDS if entry.get("status") == "implemented"}
    required_commands = requirement.get("required_commands") if isinstance(requirement, dict) else None
    missing_commands = [
        command
        for command in (required_commands if isinstance(required_commands, list) else GLOBAL_CLI_REQUIRED_COMMANDS)
        if not isinstance(command, str) or command not in command_names
    ]
    return {
        "name": "global-cli-runtime-provider",
        "result": "pass" if not missing_commands else "block",
        "summary": (
            "Global CLI runtime provider requirement is declared and the current CLI exposes the required command surface."
            if not missing_commands
            else "Global CLI runtime provider requirement is declared but required commands are missing."
        ),
        "required": True,
        "authority": "workstation",
        "runtime_provider": RUNTIME_PROVIDER_GLOBAL_CLI,
        "required_commands": required_commands if isinstance(required_commands, list) else GLOBAL_CLI_REQUIRED_COMMANDS,
        "missing_commands": missing_commands,
        "failed_layer": None if not missing_commands else "global-cli-runtime-provider",
        "fallback_to": None if not missing_commands else ["loom help --json", "loom installed-state validate --target <repo> --json"],
    }


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
    runtime_provider = target_runtime_provider(target)
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
            "target-repo-namespace",
            "legacy",
            "Top-level skills registry is present in the target repository namespace.",
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
            elif relative == ".loom/bin" and runtime_provider == RUNTIME_PROVIDER_GLOBAL_CLI:
                kind = "retained-loom-bin"
                authority = "repo-runtime-carrier"
                migration = "repairable-residue"
                summary = "Repo-local runtime wrappers are retained residue while installed-state declares global-cli as the active runtime provider."
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
    repairable = [item for item in surfaces if item.get("migration_status") == "repairable-residue"]
    authorities = {item.get("authority") for item in surfaces if item.get("authority")}
    if has_current and not legacy:
        if repairable:
            return "current-with-repairable-residue", "Versioned installed-state is present with repairable runtime-carrier residue."
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
        checks.append(global_cli_provider_check(state))
        checks.append(suite_command_surface_check(state))
    has_codex_plugin_payload = (target / "plugins" / "loom" / ".codex-plugin" / "plugin.json").exists()
    declares_host_adapter = any(isinstance(layer, dict) and layer.get("layer_type") == "host-adapter-plugin" for layer in (state or {}).get("layers", [])) if isinstance(state, dict) else False
    declares_user_provider = declares_metadata_only_mode(target)
    if has_codex_plugin_payload or declares_host_adapter or declares_user_provider:
        provider_source = Path(codex_workstation_paths()["plugin_cache_path"]) if declares_user_provider and not has_codex_plugin_payload else host_plugin_path(target, "codex")
        codex_registration = codex_workstation_registration_status(provider_source)
        checks.append(
            {
                "name": "codex-workstation-registration",
                "result": codex_registration["result"],
                "summary": "Codex Desktop workstation registration is present." if codex_registration["result"] == "pass" else "Codex Desktop workstation registration is missing or incomplete.",
                "workstation_registration": codex_registration,
                "failed_layer": None if codex_registration["result"] == "pass" else "workstation-registration",
                "fallback_to": None if codex_registration["result"] == "pass" else ["loom host register --host codex --source <plugin-source> --scope user --dry-run --json"],
            }
        )
    legacy_surfaces = [item for item in detection["surfaces"] if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")]
    repairable_surfaces = [item for item in detection["surfaces"] if item.get("migration_status") == "repairable-residue"]
    if repairable_surfaces:
        checks.append(
            {
                "name": "repairable-runtime-residue",
                "result": "pass",
                "summary": "Runtime-carrier residue is present but installed-state declares global-cli as the active provider; repair planning may classify or retire it later.",
                "surfaces": repairable_surfaces,
                "fallback_to": ["loom repair plan"],
            }
        )
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
    blocking_checks = [check for check in checks if check["result"] != "pass"]
    result = "pass" if not blocking_checks else "block"
    failed_layer = None if result == "pass" else next((check.get("failed_layer") for check in blocking_checks if check.get("failed_layer")), "installed-surface")
    return output(
        "doctor",
        result,
        schema=DOCTOR_SCHEMA,
        summary="Installed surface diagnostics passed." if result == "pass" else "Installed surface diagnostics found blocking repair inputs.",
        target=str(target),
        detection=detection,
        checks=checks,
        failed_layer=failed_layer,
        fail_closed_reason=None if result == "pass" else "doctor found blocking checks: " + ", ".join(check["name"] for check in blocking_checks),
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


RUNTIME_CARRIER_BLOCKER_LOCATORS = {
    ".loom/bootstrap/init-result.json",
    ".loom/status/current.md",
    "Makefile",
}

RUNTIME_CARRIER_SCAN_DIRS = (
    ".loom/bootstrap",
    ".loom/status",
    ".loom/work-items",
    ".loom/progress",
    ".loom/specs",
    ".github/workflows",
    "docs",
)

RUNTIME_CARRIER_SCAN_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}


def runtime_carrier_reference_records(path: Path, target: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    matches: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if "python3 .loom/bin/" not in line:
            continue
        matches.append(
            {
                "line": line_number,
                "locator": line.strip(),
            }
        )
    if not matches:
        return []
    relative = relative_to_target(path, target)
    classification = "repo-local-gate-blocker" if relative in RUNTIME_CARRIER_BLOCKER_LOCATORS or relative.startswith(".github/workflows/") else "runtime-carrier-guidance"
    return [
        {
            "path": relative,
            "classification": classification,
            "references": matches,
        }
    ]


def runtime_carrier_reference_scan(target: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blocker_records: list[dict[str, Any]] = []
    guidance_records: list[dict[str, Any]] = []
    seen: set[str] = set()
    explicit_files = [target / locator for locator in sorted(RUNTIME_CARRIER_BLOCKER_LOCATORS) if locator != "Makefile"]
    explicit_files.append(target / "Makefile")
    for candidate in explicit_files:
        if not candidate.exists() or not candidate.is_file():
            continue
        relative = relative_to_target(candidate, target)
        seen.add(relative)
        for record in runtime_carrier_reference_records(candidate, target):
            (blocker_records if record["classification"] == "repo-local-gate-blocker" else guidance_records).append(record)
    for relative_dir in RUNTIME_CARRIER_SCAN_DIRS:
        root = target / relative_dir
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else sorted(path for path in root.rglob("*") if path.is_file())
        for candidate in candidates:
            relative = relative_to_target(candidate, target)
            if relative in seen:
                continue
            if candidate.suffix.lower() not in RUNTIME_CARRIER_SCAN_SUFFIXES:
                continue
            seen.add(relative)
            for record in runtime_carrier_reference_records(candidate, target):
                (blocker_records if record["classification"] == "repo-local-gate-blocker" else guidance_records).append(record)
    return blocker_records, guidance_records


def global_cli_runtime_carrier_migration_actions(
    target: Path,
    detection: dict[str, Any],
    *,
    installed_ready: bool,
    state_path: Path | None,
) -> list[dict[str, Any]]:
    if not installed_ready or target_runtime_provider(target) != RUNTIME_PROVIDER_GLOBAL_CLI:
        return []
    retained_surfaces = [
        item for item in detection["surfaces"]
        if item.get("kind") == "retained-loom-bin" and item.get("migration_status") == "repairable-residue"
    ]
    if not retained_surfaces:
        return []
    blocker_records, guidance_records = runtime_carrier_reference_scan(target)
    carrier_update_paths = sorted({record["path"] for record in [*blocker_records, *guidance_records]})
    tracked_runtime_paths = sorted({item.get("path") for item in retained_surfaces if isinstance(item.get("path"), str) and item.get("path")})
    action: dict[str, Any] = {
        "id": "plan-global-cli-runtime-carrier-migration",
        "kind": "runtime-carrier-migration",
        "status": "blocked" if blocker_records else "recommended",
        "reason": (
            "repo-local gate carriers still reference .loom/bin; rewrite those entrypoints before proposing retained runtime deletion."
            if blocker_records
            else "installed-state already declares global-cli as the active runtime provider; retained .loom/bin can only be removed through an explicit apply/confirmation flow."
        ),
        "runtime_provider": RUNTIME_PROVIDER_GLOBAL_CLI,
        "installed_state_path": relative_to_target(state_path, target) if state_path is not None else None,
        "tracked_runtime_paths": tracked_runtime_paths,
        "carrier_update_paths": carrier_update_paths,
        "blocking_references": blocker_records,
        "guidance_references": guidance_records,
        "deletes": tracked_runtime_paths,
        "requires_confirmation": True,
        "command": (
            "rewrite listed repo-local gate carriers to `loom ... --json` entrypoints before planning deletion"
            if blocker_records
            else "review retained runtime residue and require explicit apply/confirmation language before deleting .loom/bin"
        ),
        "mutates": False,
    }
    actions = [action]
    if blocker_records:
        actions.append(
            {
                "id": "block-retained-loom-bin-deletion",
                "kind": "repo-local-gate-blocker",
                "status": "required",
                "blocked_paths": tracked_runtime_paths,
                "blocking_references": blocker_records,
                "reason": "retained .loom/bin cannot be proposed for deletion while repo-local gate carriers still point to repo-local runtime wrappers",
                "command": "rewrite the listed blockers first; keep deletion proposal-only until an explicit apply contract is approved",
                "mutates": False,
            }
        )
    return actions


def repair_actions(target: Path, detection: dict[str, Any], installed_errors: list[dict[str, str]], state_path: Path | None) -> list[dict[str, Any]]:
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
    repairable = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "repairable-residue"
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
    if repairable:
        actions.extend(
            global_cli_runtime_carrier_migration_actions(
                target,
                detection,
                installed_ready=not installed_errors,
                state_path=state_path,
            )
        )
    return actions


def repair_plan_payload(target: Path) -> dict[str, Any]:
    return repair_plan_payload_with_carrier(target, item=None, issue=None, output_relative=".loom/bootstrap/init-result.json")


def carrier_repair_flow_payload(
    target: Path,
    action: str,
    *,
    item: str | None,
    issue: int | None,
    output_relative: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    flow_args = ["repair", action, "--target", str(target), "--output", output_relative]
    if item:
        flow_args.extend(["--item", item])
    if issue is not None:
        flow_args.extend(["--issue", str(issue)])
    if dry_run:
        flow_args.append("--dry-run")
    return flow_payload(f"repair {action}", flow_args, fallback_to=["loom carrier closeout-sync --target <repo> --json"])


def repair_plan_payload_with_carrier(
    target: Path,
    *,
    item: str | None,
    issue: int | None,
    output_relative: str,
) -> dict[str, Any]:
    detection = detect_payload(target)
    state_path, state, installed_error = load_installed_state(target)
    installed_errors = [{"path": "installed-state", "reason": installed_error["fail_closed_reason"]}] if installed_error else validate_installed_state(state)
    actions = repair_actions(target, detection, installed_errors, state_path)
    migration_action = downstream_top_level_skills_migration_action(target)
    if migration_action:
        actions.append(migration_action)
    registration_action = workstation_registration_action(target)
    if registration_action:
        actions.append(registration_action)
    has_installed_surface_actions = bool(actions)
    carrier_repair = carrier_repair_flow_payload(
        target,
        "plan",
        item=item,
        issue=issue,
        output_relative=output_relative,
    )
    carrier_missing_inputs = carrier_repair.get("missing_inputs")
    carrier_missing_issue_only = (
        item is None
        and issue is None
        and isinstance(carrier_missing_inputs, list)
        and carrier_missing_inputs == ["issue selector is required for safe carrier repair"]
    )
    carrier_actions = carrier_repair.get("actions") if isinstance(carrier_repair.get("actions"), list) else []
    if not (has_installed_surface_actions and carrier_missing_issue_only):
        actions.extend(action for action in carrier_actions if isinstance(action, dict))
    carrier_blocks_plan = carrier_repair.get("result") == "block" and not (has_installed_surface_actions and carrier_missing_issue_only)
    result = "block" if carrier_blocks_plan else "pass" if detection["surface_count"] or actions else "block"
    return output(
        "repair plan",
        result,
        schema=REPAIR_PLAN_SCHEMA,
        summary=(
            "Repair plan generated without mutating target state."
            if result == "pass"
            else "Repair planning is blocked until installed-surface or carrier ownership is unambiguous."
            if carrier_blocks_plan
            else "No installed surface exists to repair."
        ),
        target=str(target),
        mutates=False,
        detection=detection,
        carrier_repair=carrier_repair,
        actions=actions,
        failed_layer=None if result == "pass" else "carrier-repair" if carrier_blocks_plan else "installed-surface",
        fail_closed_reason=None
        if result == "pass"
        else "; ".join(str(message) for message in carrier_repair.get("missing_inputs", []))
        if carrier_blocks_plan
        else "target has no detectable Loom surface",
        fallback_to=None if result == "pass" else ["loom install"],
    )


def handle_repair(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom repair")
    parser.add_argument("action", choices=("plan", "apply"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--output", default=".loom/bootstrap/init-result.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(f"repair {args.action}", target, "target path does not exist"))
    plan = repair_plan_payload_with_carrier(
        target,
        item=args.item,
        issue=args.issue,
        output_relative=args.output,
    )
    if args.action == "plan":
        return emit(plan)
    non_carrier_actions = [
        action
        for action in plan.get("actions", [])
        if isinstance(action, dict) and action.get("kind") != "carrier_closeout_sync"
    ]
    planned_carrier_repair = plan.get("carrier_repair") if isinstance(plan.get("carrier_repair"), dict) else {}
    planned_carrier_updates = planned_carrier_repair.get("versioned_carrier_updates")
    has_planned_carrier_apply = isinstance(planned_carrier_updates, list) and bool(planned_carrier_updates)
    if non_carrier_actions and has_planned_carrier_apply:
        return emit(
            output(
                "repair apply",
                "block",
                schema=REPAIR_PLAN_SCHEMA,
                summary="Safe carrier repair apply is blocked until installed-surface repair actions are resolved.",
                target=str(target),
                mutates=False,
                dry_run=args.dry_run,
                plan=plan,
                carrier_repair=planned_carrier_repair,
                unapplied_actions=non_carrier_actions,
                failed_layer="installed-surface",
                fail_closed_reason="repair apply cannot combine carrier closeout writes with installed-surface repair actions",
                fallback_to=["loom repair plan", "loom installed-state validate --target <repo> --json", "loom doctor"],
            )
        )
    carrier_apply = carrier_repair_flow_payload(
        target,
        "apply",
        item=args.item,
        issue=args.issue,
        output_relative=args.output,
        dry_run=args.dry_run,
    )
    carrier_updates = carrier_apply.get("versioned_carrier_updates")
    has_carrier_apply = isinstance(carrier_updates, list) and bool(carrier_updates)
    if carrier_apply.get("result") == "pass" and has_carrier_apply:
        return emit(
            output(
                "repair apply",
                "pass",
                schema=REPAIR_PLAN_SCHEMA,
                summary=(
                    "Safe carrier repair applied versioned carrier updates."
                    if carrier_apply.get("mutates")
                    else "Safe carrier repair apply dry-run generated versioned carrier updates without mutating target state."
                ),
                target=str(target),
                mutates=bool(carrier_apply.get("mutates")),
                dry_run=bool(carrier_apply.get("dry_run")),
                plan=plan,
                carrier_repair=carrier_apply,
                host_mutations=False,
                host_actions=[],
                versioned_carrier_updates=carrier_updates,
                unapplied_actions=non_carrier_actions,
                failed_layer=None,
                fail_closed_reason=None,
                fallback_to=None,
            )
        )
    if carrier_apply.get("result") == "block":
        return emit(
            output(
                "repair apply",
                "block",
                schema=REPAIR_PLAN_SCHEMA,
                summary="Safe carrier repair apply is blocked until host-complete carrier ownership is unambiguous.",
                target=str(target),
                mutates=False,
                dry_run=args.dry_run,
                plan=plan,
                carrier_repair=carrier_apply,
                failed_layer="carrier-repair",
                fail_closed_reason="; ".join(str(message) for message in carrier_apply.get("missing_inputs", [])),
                fallback_to=["loom repair plan", "loom carrier closeout-sync --target <repo> --json"],
            )
        )
    return emit(
        output(
            "repair apply",
            "block",
            schema=REPAIR_PLAN_SCHEMA,
            summary="Mutating installed-surface repair apply remains disabled; no safe carrier closeout repair action was available.",
            target=str(target),
            mutates=False,
            dry_run=args.dry_run,
            plan=plan,
            failed_layer="repair-apply",
            fail_closed_reason="repair apply is currently limited to safe carrier closeout sync actions",
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
    if mode == "metadata-only":
        return []
    if mode == "plugin":
        return install_host_plugin_payload(target, host)
    writes = sync_skills_payload(target)
    if mode == "skill":
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
    writes = [] if mode in {"metadata-only", "plugin"} else ["skills"]
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
    if mode == "metadata-only":
        for relative in ("plugins/loom/skills", ".agents/skills", "skills"):
            path = target / relative
            checks.append(
                {
                    "kind": "intentional-absent-surface",
                    "path": relative,
                    "status": "unexpected" if path.exists() else "pass",
                }
            )
        return all(item["status"] == "pass" for item in checks), checks

    skills_root = target / "plugins" / "loom" / "skills" if mode == "plugin" else target / "skills"
    registry_relative = "plugins/loom/skills/registry.json" if mode == "plugin" else "skills/registry.json"
    check(registry_relative, "host-plugin-skills" if mode == "plugin" else "skills-registry")
    registry_path = skills_root / "registry.json"
    if registry_path.exists():
        try:
            registry = read_json(registry_path)
            entries = registry.get("entries", []) if isinstance(registry, dict) else []
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                    skill_relative = f"plugins/loom/skills/{entry['id']}/SKILL.md" if mode == "plugin" else f"skills/{entry['id']}/SKILL.md"
                    check(skill_relative, "host-plugin-skill" if mode == "plugin" else "skill")
        except (OSError, json.JSONDecodeError):
            checks.append({"kind": "skills-registry-json", "path": registry_relative, "status": "invalid"})
    if mode == "plugin":
        if host == "codex":
            check("plugins/loom/.codex-plugin/plugin.json", "host-plugin")
        else:
            checks.append({"kind": "host-plugin", "path": host, "status": "unsupported"})
    if mode == "skill":
        check(f".agents/skills/{skill_id or 'missing'}/SKILL.md", "single-skill")
    return all(item["status"] == "pass" for item in checks), checks


def installed_state_declared_mode(target: Path) -> str | None:
    state_path = installed_state_path(target)
    if state_path is None:
        return None
    try:
        state = read_json(state_path)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict):
        return None
    repo_payload = state.get("repo_payload")
    if isinstance(repo_payload, dict):
        mode = repo_payload.get("mode")
        if mode in {"metadata-only", "embedded", "plugin", "full-repo", "skill"}:
            return "plugin" if mode == "embedded" else str(mode)
    layers = state.get("layers", []) if isinstance(state, dict) else []
    if any(
        isinstance(layer, dict)
        and layer.get("layer_type") == "user-level-skills-provider"
        and str(layer.get("installed_path", "")).startswith("workstation:")
        for layer in layers
    ):
        return "metadata-only"
    if any(
        isinstance(layer, dict)
        and layer.get("layer_type") in {"plugin-embedded-skills", "host-adapter-plugin"}
        and str(layer.get("installed_path", "")).startswith("plugins/loom")
        for layer in layers
    ):
        return "plugin"
    return None


def declares_plugin_mode(target: Path) -> bool:
    return installed_state_declared_mode(target) == "plugin"


def declares_metadata_only_mode(target: Path) -> bool:
    return installed_state_declared_mode(target) == "metadata-only"


def skills_check_mode(target: Path) -> str:
    return installed_state_declared_mode(target) or "full-repo"


def top_level_skills_assessment(target: Path) -> dict[str, Any] | None:
    skills_root = target / "skills"
    registry_path = skills_root / "registry.json"
    if not registry_path.exists():
        return None
    expected_registry = read_optional_json(SKILLS_ROOT / "registry.json") or {}
    actual_registry = read_optional_json(registry_path) or {}
    expected_ids = {
        entry.get("id")
        for entry in expected_registry.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    actual_ids = {
        entry.get("id")
        for entry in actual_registry.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    skill_dirs = {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }
    unknown_ids = sorted((actual_ids | skill_dirs) - expected_ids)
    missing_ids = sorted(expected_ids - actual_ids)
    if actual_ids == expected_ids and skill_dirs <= expected_ids:
        ownership = "loom-generated"
        result = "migration-recommended"
        summary = "Top-level skills appears to be Loom-generated residue from the old downstream plugin layout."
    else:
        ownership = "mixed-or-target-owned"
        result = "manual-review-required"
        summary = "Top-level skills cannot be proven Loom-owned and must not be removed automatically."
    return {
        "path": "skills",
        "ownership": ownership,
        "result": result,
        "unknown_skill_ids": unknown_ids,
        "missing_loom_skill_ids": missing_ids,
        "summary": summary,
    }


def downstream_top_level_skills_migration_action(target: Path) -> dict[str, Any] | None:
    if not declares_plugin_mode(target):
        return None
    assessment = top_level_skills_assessment(target)
    if assessment is None:
        return None
    if assessment["ownership"] == "loom-generated":
        return {
            "id": "plan-top-level-loom-skills-migration",
            "kind": "legacy-plugin-layout-migration",
            "status": "recommended",
            "surface": assessment,
            "reason": "plugin mode now uses plugins/loom/skills; downstream top-level Loom skills is legacy residue",
            "command": "review target-owned skills/ before any explicit removal; do not delete automatically",
            "mutates": False,
        }
    return {
        "id": "review-top-level-skills-ownership",
        "kind": "manual-migration-judgment",
        "status": "required",
        "surface": assessment,
        "reason": "target repository skills/ ownership is mixed or unknown",
        "command": "inspect skills/ before planning any migration",
        "mutates": False,
    }


def codex_workstation_paths(home: Path | None = None, codex_home: Path | None = None) -> dict[str, Path | str]:
    resolved_home = (home or Path.home()).expanduser().resolve()
    resolved_codex_home = Path(os.environ.get("CODEX_HOME", str(resolved_home / ".codex"))).expanduser().resolve()
    if codex_home is not None:
        resolved_codex_home = codex_home.expanduser().resolve()
    marketplace_name = "local-user-plugins"
    return {
        "home": resolved_home,
        "codex_home": resolved_codex_home,
        "marketplace_name": marketplace_name,
        "marketplace_root": resolved_home,
        "marketplace_path": resolved_home / ".agents" / "plugins" / "marketplace.json",
        "plugin_cache_path": resolved_home / "plugins" / "loom",
        "config_path": resolved_codex_home / "config.toml",
        "config_plugin_key": f"loom@{marketplace_name}",
    }


def codex_marketplace_plugin_entry() -> dict[str, Any]:
    return {
        "name": "loom",
        "source": {
            "source": "local",
            "path": "./plugins/loom",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }


def codex_workstation_registration_status(source: Path) -> dict[str, Any]:
    paths = codex_workstation_paths()
    marketplace_path = paths["marketplace_path"]
    plugin_cache_path = paths["plugin_cache_path"]
    config_path = paths["config_path"]
    marketplace_name = str(paths["marketplace_name"])
    config_plugin_key = str(paths["config_plugin_key"])
    expected_source = codex_marketplace_plugin_entry()["source"]

    source_manifest = source / ".codex-plugin" / "plugin.json"
    plugin_cache_manifest = Path(plugin_cache_path) / ".codex-plugin" / "plugin.json"
    checks: list[dict[str, Any]] = [
        {
            "name": "source-payload",
            "result": "pass" if source_manifest.exists() else "block",
            "path": str(source_manifest),
            "summary": "Repo-local Codex plugin payload is readable." if source_manifest.exists() else "Repo-local Codex plugin payload is missing.",
        }
    ]

    marketplace_entry = None
    marketplace_error = None
    marketplace = None
    if Path(marketplace_path).exists():
        try:
            marketplace = read_json(Path(marketplace_path))
            plugins = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
            marketplace_entry = next((entry for entry in plugins if isinstance(entry, dict) and entry.get("name") == "loom"), None)
        except (OSError, json.JSONDecodeError) as exc:
            marketplace_error = str(exc)
    marketplace_ok = (
        isinstance(marketplace, dict)
        and marketplace.get("name") == marketplace_name
        and isinstance(marketplace_entry, dict)
        and marketplace_entry.get("source") == expected_source
    )
    checks.append(
        {
            "name": "user-marketplace-entry",
            "result": "pass" if marketplace_ok else "block",
            "path": str(marketplace_path),
            "marketplace_name": marketplace.get("name") if isinstance(marketplace, dict) else None,
            "entry": marketplace_entry,
            "summary": "Codex personal marketplace contains the Loom plugin entry." if marketplace_ok else "Codex personal marketplace is missing the Loom plugin entry.",
            "error": marketplace_error,
        }
    )

    cache_ok = plugin_cache_manifest.exists()
    checks.append(
        {
            "name": "user-plugin-cache",
            "result": "pass" if cache_ok else "block",
            "path": str(plugin_cache_path),
            "summary": "User plugin cache contains a Loom plugin payload." if cache_ok else "User plugin cache is missing the Loom plugin payload.",
        }
    )

    config_data = None
    config_error = None
    if Path(config_path).exists():
        try:
            config_data = parse_toml_text(Path(config_path).read_text(encoding="utf-8"))
        except (OSError, TomlDecodeError, ValueError) as exc:
            config_error = str(exc)
    marketplaces = config_data.get("marketplaces", {}) if isinstance(config_data, dict) else {}
    plugins = config_data.get("plugins", {}) if isinstance(config_data, dict) else {}
    marketplace_config = marketplaces.get(marketplace_name) if isinstance(marketplaces, dict) else None
    plugin_config = plugins.get(config_plugin_key) if isinstance(plugins, dict) else None
    config_enabled = isinstance(plugin_config, dict) and plugin_config.get("enabled") is True
    config_marketplace_ok = isinstance(marketplace_config, dict) and marketplace_config.get("source_type") == "local" and str(marketplace_config.get("source")) == str(paths["marketplace_root"])
    checks.append(
        {
            "name": "codex-config-marketplace",
            "result": "pass" if config_marketplace_ok else "block",
            "path": str(config_path),
            "marketplace": marketplace_name,
            "summary": "Codex config points at the local user plugin marketplace." if config_marketplace_ok else "Codex config is missing the local user plugin marketplace.",
            "error": config_error,
        }
    )
    checks.append(
        {
            "name": "codex-config-enabled",
            "result": "pass" if config_enabled else "block",
            "path": str(config_path),
            "plugin": config_plugin_key,
            "enabled": config_enabled,
            "summary": "Codex config enables the Loom plugin." if config_enabled else "Codex config does not enable the Loom plugin.",
            "error": config_error,
        }
    )

    blocking = [check for check in checks if check["result"] != "pass"]
    return {
        "schema": WORKSTATION_SCHEMA,
        "host": "codex",
        "scope": "user",
        "source": str(source),
        "status": "registered" if not blocking else "missing",
        "result": "pass" if not blocking else "block",
        "paths": {key: str(value) for key, value in paths.items() if isinstance(value, Path)},
        "marketplace_name": marketplace_name,
        "config_plugin_key": config_plugin_key,
        "checks": checks,
        "reload_required": True,
        "reload_guidance": "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded.",
        "authority_boundary": {
            "kind": "developer-workstation-registration-state",
            "does_not_write_repo_truth": True,
            "repo_payload_verify_command": "loom host verify --host codex --mode plugin --target <repo> --json",
        },
    }


def update_codex_marketplace(marketplace_path: Path) -> None:
    if marketplace_path.exists():
        marketplace = read_json(marketplace_path)
        if not isinstance(marketplace, dict):
            raise RuntimeError(f"marketplace is not a JSON object: {marketplace_path}")
    else:
        marketplace = {
            "name": "local-user-plugins",
            "interface": {
                "displayName": "Local User Plugins",
            },
            "plugins": [],
        }
    marketplace.setdefault("name", "local-user-plugins")
    marketplace.setdefault("interface", {"displayName": "Local User Plugins"})
    plugins = marketplace.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise RuntimeError(f"marketplace plugins must be an array: {marketplace_path}")
    entry = codex_marketplace_plugin_entry()
    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == "loom":
            plugins[index] = entry
            break
    else:
        plugins.append(entry)
    write_json(marketplace_path, marketplace)


def set_toml_table_value(text: str, table: str, assignments: dict[str, str]) -> str:
    lines = text.splitlines()
    header = f"[{table}]"
    start = next((index for index, line in enumerate(lines) if line.strip() == header), None)
    rendered = [f"{key} = {value}" for key, value in assignments.items()]
    if start is None:
        prefix = lines + ([""] if lines and lines[-1] else [])
        return "\n".join([*prefix, header, *rendered]) + "\n"
    end = start + 1
    while end < len(lines) and not (lines[end].startswith("[") and lines[end].endswith("]")):
        end += 1
    body = lines[start + 1 : end]
    remaining = dict(assignments)
    updated_body = []
    for line in body:
        stripped = line.strip()
        key = stripped.split("=", 1)[0].strip() if "=" in stripped else None
        if key in remaining:
            updated_body.append(f"{key} = {remaining.pop(key)}")
        else:
            updated_body.append(line)
    updated_body.extend(f"{key} = {value}" for key, value in remaining.items())
    return "\n".join([*lines[: start + 1], *updated_body, *lines[end:]]) + "\n"


def update_codex_config(config_path: Path, marketplace_root: Path, marketplace_name: str, plugin_key: str) -> None:
    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    text = set_toml_table_value(
        text,
        f"marketplaces.{marketplace_name}",
        {
            "last_updated": json.dumps(now_iso()),
            "source_type": json.dumps("local"),
            "source": json.dumps(str(marketplace_root)),
        },
    )
    text = set_toml_table_value(text, f'plugins."{plugin_key}"', {"enabled": "true"})
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(text, encoding="utf-8")


def register_codex_workstation(source: Path) -> list[str]:
    paths = codex_workstation_paths()
    if not (source / ".codex-plugin" / "plugin.json").exists():
        raise RuntimeError(f"Codex plugin source is missing .codex-plugin/plugin.json: {source}")
    plugin_cache_path = Path(paths["plugin_cache_path"])
    copy_tree(source, plugin_cache_path)
    update_codex_marketplace(Path(paths["marketplace_path"]))
    update_codex_config(Path(paths["config_path"]), Path(paths["marketplace_root"]), str(paths["marketplace_name"]), str(paths["config_plugin_key"]))
    return [
        str(plugin_cache_path),
        str(paths["marketplace_path"]),
        str(paths["config_path"]),
    ]


def workstation_registration_action(target: Path, source: Path | None = None) -> dict[str, Any] | None:
    mode = skills_check_mode(target)
    plugin_source = source or (Path(codex_workstation_paths()["plugin_cache_path"]) if mode == "metadata-only" else host_plugin_path(target, "codex"))
    repo_ok, _ = verify_cli_managed_surfaces(target, host="codex", mode=mode)
    registration = codex_workstation_registration_status(plugin_source)
    if repo_ok and registration["result"] != "pass":
        return {
            "id": "register-codex-workstation-plugin",
            "kind": "workstation-registration",
            "status": "recommended",
            "reason": "repository adoption metadata is current, but Codex Desktop workstation registration is missing" if mode == "metadata-only" else "target repository plugin payload is current, but Codex Desktop workstation registration is missing",
            "command": f"loom host register --host codex --source {relative_to_target(plugin_source, target)} --scope user --dry-run --json",
            "apply_command": f"loom host register --host codex --source {relative_to_target(plugin_source, target)} --scope user --apply --json",
            "mutates": False,
            "apply_mutates": True,
            "reload_required": registration["reload_required"],
            "reload_note": registration["reload_guidance"],
        }
    return None


def handle_delivery(command: str, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--host", default="codex", choices=("codex", "claude", "opencode", "gemini", "cursor"))
    parser.add_argument("--mode", default="full-repo", choices=("full-repo", "metadata-only", "plugin", "skill"))
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
                summary="CLI-managed plugin payload and installed-state metadata were written.",
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
        actions.extend(
            global_cli_runtime_carrier_migration_actions(
                target,
                detection,
                installed_ready=installed_ready,
                state_path=path,
            )
        )
        migration_action = downstream_top_level_skills_migration_action(target)
        if migration_action:
            actions.append(migration_action)
        if installed_ready and not legacy_surfaces and not any(action.get("id") == "plan-global-cli-runtime-carrier-migration" for action in actions):
            actions.append(
                {
                    "id": "installed-state-current",
                    "kind": "no-op",
                    "status": "current",
                    "reason": "installed-state validates and no legacy surfaces are blocking",
                    "command": "loom verify --target <repo> --json",
                }
            )
        registration_action = workstation_registration_action(target)
        if registration_action:
            actions.append(registration_action)
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
        requirement = suite_verify_requirement(state, args.item)
        suite_check = None
        if doctor["result"] == "pass" and requirement["required"]:
            suite_check = suite_validation_check(target, requirement["item_id"])
        blocking_checks = []
        if doctor["result"] != "pass":
            blocking_checks.append({"name": "doctor", "failed_layer": "delivery-verify", "summary": "doctor reported missing, invalid, mixed, or legacy installed surfaces"})
        if suite_check and suite_check["result"] != "pass":
            blocking_checks.append(suite_check)
        result = "pass" if not blocking_checks else "block"
        failed_layer = None if result == "pass" else next((check.get("failed_layer") for check in blocking_checks if check.get("failed_layer")), "delivery-verify")
        return emit(
            output(
                command,
                result,
                schema=DELIVERY_SCHEMA,
                summary="Installed Loom delivery layers verified." if result == "pass" else "Installed Loom delivery layers or required suite validation are not ready.",
                target=str(target),
                mutates=False,
                doctor=doctor,
                suite_validation_requirement=requirement,
                suite_validation=suite_check,
                installed_state_path=str(path) if path else None,
                failed_layer=failed_layer,
                fail_closed_reason=None if result == "pass" else "; ".join(str(check.get("summary", check.get("name"))) for check in blocking_checks),
                fallback_to=None if result == "pass" else ["loom upgrade-plan --target <repo> --json", "loom repair plan --target <repo> --json", "loom suite validate --target <repo> --item <item> --json"],
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
    installed_ready = installed_error is None and not validation_errors
    legacy_surfaces = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]
    actions = []
    if installed_error is not None or validation_errors:
        actions.append({"id": "repair-installed-state", "status": "required"})
    if legacy_surfaces:
        actions.append({"id": "classify-legacy-surfaces", "status": "required", "surface_count": len(legacy_surfaces)})
    actions.extend(
        global_cli_runtime_carrier_migration_actions(
            target,
            detection,
            installed_ready=installed_ready,
            state_path=path,
        )
    )
    registration_action = workstation_registration_action(target)
    if registration_action:
        actions.append(registration_action)
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
    layer_types: set[str] = set()
    layer_paths: set[str] = set()
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
        layer_type = layer.get("layer_type")
        if isinstance(layer_type, str) and layer_type:
            layer_types.add(layer_type)
        installed_path = layer.get("installed_path")
        if isinstance(installed_path, str) and installed_path:
            layer_paths.add(installed_path.rstrip("/"))
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
            if layer.get("layer_type") == GLOBAL_CLI_PROVIDER_LAYER and layer.get("runtime_state") == "unknown":
                pass
            elif not layer.get("fail_closed_reason") or not layer.get("failed_layer"):
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
    runtime_provider = state.get("runtime_provider")
    if runtime_provider is not None and runtime_provider not in {RUNTIME_PROVIDER_GLOBAL_CLI, RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER}:
        errors.append({"path": "runtime_provider", "reason": "unsupported runtime provider"})
    inferred_runtime_provider = installed_state_runtime_provider(state)
    requires_global_cli = runtime_provider == RUNTIME_PROVIDER_GLOBAL_CLI or GLOBAL_CLI_PROVIDER_LAYER in layer_types
    global_cli_requirement = global_cli_provider_requirement(state)
    if requires_global_cli:
        if global_cli_requirement is None:
            errors.append({"path": "provider_requirements.global_cli", "reason": "global-cli runtime provider must declare provider requirements"})
        else:
            expected_scalars = {
                "required": True,
                "provider": "loom-cli",
                "authority": "workstation",
                "package": "@mc-and-his-agents/loom",
                "executable": "loom",
            }
            for key, expected in expected_scalars.items():
                if global_cli_requirement.get(key) != expected:
                    errors.append({"path": f"provider_requirements.global_cli.{key}", "reason": f"must be {expected!r}"})
            version_requirement = global_cli_requirement.get("version_requirement")
            if not isinstance(version_requirement, str) or not version_requirement.strip():
                errors.append({"path": "provider_requirements.global_cli.version_requirement", "reason": "must be a non-empty string"})
            required_commands = global_cli_requirement.get("required_commands")
            if not isinstance(required_commands, list) or not required_commands:
                errors.append({"path": "provider_requirements.global_cli.required_commands", "reason": "must be a non-empty array"})
            else:
                command_set = {command for command in required_commands if isinstance(command, str)}
                missing_commands = sorted(set(GLOBAL_CLI_REQUIRED_COMMANDS) - command_set)
                if missing_commands:
                    errors.append({"path": "provider_requirements.global_cli.required_commands", "reason": f"missing required commands: {', '.join(missing_commands)}"})
    if inferred_runtime_provider == RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER and GLOBAL_CLI_PROVIDER_LAYER in layer_types and runtime_provider != RUNTIME_PROVIDER_GLOBAL_CLI:
        errors.append({"path": "runtime_provider", "reason": "global-cli provider layer requires runtime_provider global-cli"})
    repo_payload = state.get("repo_payload")
    if isinstance(repo_payload, dict):
        mode = repo_payload.get("mode")
        if mode not in {"metadata-only", "embedded", "full-repo", "skill"}:
            errors.append({"path": "repo_payload.mode", "reason": "unsupported repo payload mode"})
        if mode == "metadata-only":
            if "plugins/loom/skills" in layer_paths or "plugin-embedded-skills" in layer_types:
                errors.append({"path": "repo_payload.mode", "reason": "metadata-only mode must not declare embedded plugin skills payload"})
            provider = state.get("skills_provider")
            if not isinstance(provider, dict):
                errors.append({"path": "skills_provider", "reason": "metadata-only mode must declare a skills provider"})
            else:
                if provider.get("scope") != "user":
                    errors.append({"path": "skills_provider.scope", "reason": "metadata-only mode requires user scoped skills provider"})
                if provider.get("registration_authority") != "workstation":
                    errors.append({"path": "skills_provider.registration_authority", "reason": "metadata-only provider registration authority must be workstation"})
        if mode == "embedded" and "plugins/loom/skills" not in layer_paths:
            errors.append({"path": "repo_payload.mode", "reason": "embedded mode must declare plugins/loom/skills payload"})
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
    parser.add_argument("--surface", choices=("pre_review", "review", "merge_ready"), default="merge_ready")
    parser.add_argument("--body-file")
    parser.add_argument("--compare-body-file")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"pr {args.action}"
    if not args.pr and not (args.action == "metadata-preflight" and args.body_file):
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="PR command requires a PR number.", failed_layer="pr-input", fail_closed_reason="missing PR number", fallback_to=["loom help --json"]))
    if args.action == "inspect":
        flow_args = ["host-binding", "inspect", "--target", ".", "--pr", args.pr]
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        return emit_flow(command, flow_args, fallback_to=["loom pr gate <pr> --json", "manual-reconciliation"])
    if args.action == "metadata-preflight":
        flow_args = ["pr-metadata", "preflight", "--target", ".", "--surface", args.surface]
        if args.pr:
            flow_args.extend(["--pr", args.pr])
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        if args.body_file:
            flow_args.extend(["--body-file", args.body_file])
        if args.compare_body_file:
            flow_args.extend(["--compare-body-file", args.compare_body_file])
        if args.pr_payload_file:
            flow_args.extend(["--pr-payload-file", args.pr_payload_file])
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
    parser.add_argument("--work-item")
    parser.add_argument("--merge-method", choices=("squash", "merge", "rebase"), default="merge")
    parser.add_argument("--delete-branch", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--branch-protection-file")
    parser.add_argument("--ruleset-file")
    parser.add_argument("--pr-gate-result-file")
    parser.add_argument("--merge-gate-result-file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"merge {args.action}"
    flow_args = [
        "controlled-merge",
        "merge" if args.action == "run" else "check",
        "--target",
        ".",
        "--pr",
        args.pr,
        "--merge-method",
        args.merge_method,
    ]
    if args.delete_branch:
        flow_args.append("--delete-branch")
    if args.head_sha:
        flow_args.extend(["--head-sha", args.head_sha])
    if args.work_item:
        flow_args.extend(["--item", args.work_item])
    for option, value in (
        ("--pr-payload-file", args.pr_payload_file),
        ("--status-checks-file", args.status_checks_file),
        ("--branch-protection-file", args.branch_protection_file),
        ("--ruleset-file", args.ruleset_file),
        ("--pr-gate-result-file", args.pr_gate_result_file),
        ("--merge-gate-result-file", args.merge_gate_result_file),
    ):
        if value:
            flow_args.extend([option, value])
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


def handle_carrier(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom carrier")
    parser.add_argument("action", choices=("closeout-sync",))
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--output")
    parser.add_argument("--terminal-state")
    parser.add_argument("--issue")
    parser.add_argument("--pr")
    parser.add_argument("--merge-commit")
    parser.add_argument("--target-branch")
    parser.add_argument("--closed-at")
    parser.add_argument("--evidence-locator")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", dest="dry_run", action="store_false")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    flow_args = ["carrier", args.action, "--target", str(target)]
    for flag, value in (
        ("--item", args.item),
        ("--output", args.output),
        ("--terminal-state", args.terminal_state),
        ("--issue", args.issue),
        ("--pr", args.pr),
        ("--merge-commit", args.merge_commit),
        ("--target-branch", args.target_branch),
        ("--closed-at", args.closed_at),
        ("--evidence-locator", args.evidence_locator),
    ):
        if value is not None:
            flow_args.extend([flag, str(value)])
    if not args.dry_run:
        flow_args.append("--apply")
    command = f"carrier {args.action}"
    payload = flow_payload(command, flow_args, fallback_to=["loom closeout --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(payload)


def supported_hosts(target: Path) -> list[dict[str, Any]]:
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    codex_paths = codex_workstation_paths(home=home, codex_home=codex_home)
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    hosts = [
        {
            "id": "codex",
            "support_status": "primary",
            "detected": codex_home.exists(),
            "default_mode": "plugin",
            "native_skill_path": str(home / ".agents" / "skills"),
            "repo_payload_plugin_path": str(target / "plugins" / "loom"),
            "workstation_plugin_cache_path": str(codex_paths["plugin_cache_path"]),
            "workstation_marketplace_path": str(codex_paths["marketplace_path"]),
            "workstation_config_path": str(codex_paths["config_path"]),
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
    parser.add_argument("action", choices=("list", "doctor", "install", "verify", "register", "upgrade", "remove"))
    parser.add_argument("--host", default="auto", choices=("auto", "codex", "claude", "opencode", "gemini", "cursor"))
    parser.add_argument("--mode", default="plugin", choices=("full-repo", "metadata-only", "plugin", "skill"))
    parser.add_argument("--skill-id")
    parser.add_argument("--target", default=".")
    parser.add_argument("--source")
    parser.add_argument("--scope", default="user", choices=("user",))
    parser.add_argument("--dry-run", action="store_true")
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
            warnings.append("Codex repo payload verification is separate from Codex Desktop workstation registration.")
        registration = codex_workstation_registration_status(resolve_target(args.source) if args.source else host_plugin_path(target, "codex")) if host == "codex" else None
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Host adapter contract is readable.", target=str(target), host=host, mode=args.mode, hosts=hosts, warnings=warnings, workstation_registration=registration, verification=["docs/adoption/host-adapter-matrix.md", "tools/host_adapter_check.py"], fallback_to=None))
    if args.action == "register":
        if host != "codex":
            return emit(output(command, "block", schema=HOST_SCHEMA, summary="Workstation registration is implemented for Codex only.", target=str(target), host=host, scope=args.scope, mutates=False, failed_layer="workstation-registration", fail_closed_reason="unsupported host for workstation registration", fallback_to=["docs/adoption/host-adapter-matrix.md"]))
        source = resolve_target(args.source) if args.source else host_plugin_path(target, "codex")
        registration = codex_workstation_registration_status(source)
        paths = codex_workstation_paths()
        planned_writes = [str(paths["plugin_cache_path"]), str(paths["marketplace_path"]), str(paths["config_path"])]
        if args.dry_run and not args.apply:
            return emit(
                output(
                    command,
                    "pass",
                    schema=HOST_SCHEMA,
                    summary="Codex workstation registration plan generated without mutating user state.",
                    target=str(target),
                    host=host,
                    scope=args.scope,
                    source=str(source),
                    mutates=False,
                    planned_writes=planned_writes,
                    workstation_registration=registration,
                    reload_required=True,
                    reload_guidance=registration["reload_guidance"],
                    fallback_to=["loom host register --host codex --source <repo>/plugins/loom --scope user --apply --json"],
                )
            )
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=HOST_SCHEMA,
                    summary="Codex workstation registration is mutating and requires --apply or --dry-run.",
                    target=str(target),
                    host=host,
                    scope=args.scope,
                    source=str(source),
                    mutates=True,
                    planned_writes=planned_writes,
                    workstation_registration=registration,
                    failed_layer="workstation-registration",
                    fail_closed_reason="explicit --apply is required before writing user Codex registration state",
                    fallback_to=["loom host register --host codex --source <repo>/plugins/loom --scope user --dry-run --json"],
                )
            )
        try:
            writes = register_codex_workstation(source)
        except RuntimeError as exc:
            return emit(output(command, "block", schema=HOST_SCHEMA, summary="Codex workstation registration could not be applied.", target=str(target), host=host, scope=args.scope, source=str(source), mutates=True, failed_layer="workstation-registration", fail_closed_reason=str(exc), fallback_to=["loom host verify --host codex --mode plugin --target <repo> --json"]))
        updated = codex_workstation_registration_status(source)
        return emit(
            output(
                command,
                "pass" if updated["result"] == "pass" else "block",
                schema=HOST_SCHEMA,
                summary="Codex workstation registration applied." if updated["result"] == "pass" else "Codex workstation registration writes completed but verification still failed.",
                target=str(target),
                host=host,
                scope=args.scope,
                source=str(source),
                mutates=True,
                writes=writes,
                workstation_registration=updated,
                reload_required=True,
                reload_guidance=updated["reload_guidance"],
                failed_layer=None if updated["result"] == "pass" else "workstation-registration",
                fail_closed_reason=None if updated["result"] == "pass" else "workstation registration verification failed after apply",
                fallback_to=None if updated["result"] == "pass" else ["loom host doctor --host codex --target <repo> --json"],
            )
        )
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
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Host plugin payload installed by the Loom CLI.", target=str(target), host=host, mode=args.mode, mutates=True, managed_writes=managed_writes, installed_state_path=str(state_path), fallback_to=None))
    ok, checks = verify_cli_managed_surfaces(target, host=host, mode=args.mode, skill_id=args.skill_id)
    verifies = "repository-adoption-metadata" if args.mode == "metadata-only" else "target-repository-payload"
    summary = (
        "Metadata-only repository adoption verified; workstation provider registration is reported separately."
        if ok and args.mode == "metadata-only"
        else "Target repository plugin payload verified; workstation registration is reported separately."
        if ok
        else "Metadata-only repository adoption metadata is incomplete or has unexpected payload surfaces."
        if args.mode == "metadata-only"
        else "Target repository plugin payload is incomplete."
    )
    return emit(output(command, "pass" if ok else "block", schema=HOST_SCHEMA, summary=summary, target=str(target), host=host, mode=args.mode, mutates=False, verifies=verifies, workstation_registration_command="loom host register --host codex --source <plugin-source> --scope user --dry-run --json" if host == "codex" and args.mode in {"metadata-only", "plugin"} else None, checks=checks, failed_layer=None if ok else "host-payload", fail_closed_reason=None if ok else "one or more CLI-managed target repository payload checks failed", fallback_to=None if ok else ["loom host install --host <host> --apply --json", "loom skills sync --target <repo> --apply --json"]))


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
            mode = skills_check_mode(target)
            ok, managed_checks = verify_cli_managed_surfaces(target, host="codex", mode=mode)
            checks.append({"command": "loom skills check installed payload", "returncode": 0 if ok else 1, "stdout": json.dumps(managed_checks, ensure_ascii=False), "stderr": "" if ok else "installed skills payload is incomplete"})
        if args.action == "release-check":
            checks.extend(
                [
                    [sys.executable, str(TOOLS_ROOT / "host_adapter_check.py")],
                    [sys.executable, str(TOOLS_ROOT / "version_surface_check.py")],
                    [sys.executable, str(TOOLS_ROOT / "check_release_surface.py")],
                    [sys.executable, str(TOOLS_ROOT / "check_npm_package.py")],
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
    target = target_from_args(argv)
    payload = delegated_payload("status", "loom_status.py", strip_json_flag(argv), failed_layer="loom-status", fallback_to=["loom fact-chain --target <repo> --json", "loom checkpoint admission --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != "status":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "status"
    annotate_global_cli_runtime_entrypoint(payload, command="status", target=target, argv=argv)
    return emit(payload)


def handle_fact_chain(argv: list[str]) -> int:
    target = target_from_args(argv)
    payload = flow_payload("fact-chain", ["fact-chain", *strip_json_flag(argv)], fallback_to=["loom init verify --target <repo> --json", "loom status --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != "fact-chain":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "fact-chain"
    annotate_global_cli_runtime_entrypoint(payload, command="fact-chain", target=target, argv=argv)
    return emit(payload)


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
    if gate == "freeze":
        if not rest:
            return emit(output("gate freeze", "block", schema=GATE_SCHEMA, summary="Gate freeze requires an operation.", failed_layer="gate-input", fail_closed_reason="missing gate freeze operation", fallback_to=["loom gate freeze check --target <repo> --json", "loom gate freeze write --target <repo> --json"]))
        operation = rest[0]
        if operation not in {"check", "write"}:
            return emit(output("gate freeze", "block", schema=GATE_SCHEMA, summary="Unsupported gate freeze operation.", failed_layer="gate-input", fail_closed_reason=f"unsupported gate freeze operation: {operation}", fallback_to=["loom gate freeze check --target <repo> --json", "loom gate freeze write --target <repo> --json"]))
        return emit_flow(f"gate freeze {operation}", ["gate-freeze", operation, *rest[1:]], fallback_to=["loom pr metadata-preflight --surface merge_ready --target <repo> --json", "loom shadow-parity --target <repo> --surface all --blocking --json"])
    if gate == "closeout":
        return emit_flow("gate closeout", ["closeout", "check", *rest], fallback_to=["loom merge check <pr> --json", "loom status --target <repo> --json"])
    return emit(output("gate", "block", schema=GATE_SCHEMA, summary="Unsupported gate name.", failed_layer="gate-input", fail_closed_reason=f"unsupported gate name: {gate}", fallback_to=["loom gate pre-review --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"]))


def handle_closeout_queue_status(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom closeout queue status")
    parser.add_argument("--target", default=".")
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--item", action="append", default=[])
    parser.add_argument("--queue-file")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        payload = block_target("closeout queue status", target, "target path does not exist")
        payload.update(
            {
                "schema_version": "loom-closeout-queue-status/v1",
                "operation": "status",
                "mode": "blocked",
                "mutates": False,
                "host_mutations": False,
                "carrier_mutations": False,
                "item_count": 0,
                "items": [],
                "next_action": "provide an existing target repository before reading closeout queue status",
                "next_command": None,
            }
        )
        return emit(payload)
    flow_args = ["closeout-queue", "status", "--target", str(target)]
    for issue in args.issue:
        flow_args.extend(["--issue", str(issue)])
    for item in args.item:
        flow_args.extend(["--item", item])
    for flag, value in (
        ("--queue-file", args.queue_file),
        ("--output", args.output),
    ):
        if value is not None:
            flow_args.extend([flag, value])
    payload = flow_payload(
        "closeout queue status",
        flow_args,
        fallback_to=["loom closeout --target <repo> --json", "loom reconcile --issue <issue> --pr <pr> --json"],
    )
    payload.setdefault("schema_version", SCENARIO_SCHEMA)
    if payload.get("command") and payload.get("command") != "closeout queue status":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "closeout queue status"
    return emit(payload)


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
        if command == "story":
            annotate_global_cli_runtime_entrypoint(payload, command="story", target=target, argv=argv)
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
    completed = subprocess.run([sys.executable, str(tool_path), *prefix, *strip_json_flag(forwarded_args)], check=False)
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


def repo_locator(path: Path, target_root: Path) -> str:
    return path.relative_to(target_root).as_posix()


def suite_item_segment_error(item: str) -> str | None:
    if not item or item in {".", ".."} or "/" in item or "\\" in item or Path(item).is_absolute():
        return "suite item must be a single repo-local path segment"
    if Path(item).name != item:
        return "suite item must be a single repo-local path segment"
    return None


def first_existing_locator(paths: list[Path], target_root: Path) -> str | None:
    for path in paths:
        if path.exists() and path.is_file() and not path.is_symlink():
            return repo_locator(path, target_root)
    return None


def suite_path_marker_values(text: str) -> tuple[list[str], list[str]]:
    lowered = text.lower()
    values: list[str] = []
    invalid_values: list[str] = []
    for line in lowered.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if stripped.startswith("suite path:"):
            value = stripped.split(":", 1)[1].strip().replace(" ", "_").replace("-", "_")
            if value in {"full", "minimal", "not_applicable", "unknown"}:
                values.append(value)
            else:
                invalid_values.append(value)
    if "loom-full-suite-index/v1" in lowered:
        values.append("full")
    return values, invalid_values


def read_suite_path_marker_values(path: Path) -> tuple[list[str], list[str]]:
    if not path.exists() or path.is_symlink() or not path.is_file():
        return [], []
    try:
        return suite_path_marker_values(path.read_text(encoding="utf-8"))
    except OSError:
        return [], ["unreadable"]


def first_artifact_locator_or_invalid(paths: list[Path], target_root: Path) -> tuple[str | None, str | None]:
    for path in paths:
        if not path.exists():
            continue
        locator = repo_locator(path, target_root)
        if path.is_symlink() or not path.is_file():
            return None, locator
        return locator, None
    return None, None


def suite_artifact_paths(target: Path, item: str | None) -> dict[str, list[Path]]:
    if not item:
        return {}
    suite_root = target / ".loom" / "specs" / item
    return {
        "suite-index.md": [suite_root / "suite-index.md"],
        "spec.md": [suite_root / "spec.md"],
        "plan.md": [suite_root / "plan.md"],
        "research.md": [suite_root / "research.md"],
        "contracts.md": [suite_root / "contracts.md"],
        "readiness-checklist.md": [suite_root / "readiness-checklist.md"],
        "evidence-map.md": [suite_root / "evidence-map.md"],
        "consistency-analysis.md": [suite_root / "consistency-analysis.md"],
        "execution-breakdown.md": [suite_root / "execution-breakdown.md"],
        "task-carrier": [
            suite_root / "task-carrier.md",
            suite_root / "tasks.md",
            target / ".loom" / "tasks" / f"{item}.md",
            target / "tasks.md",
        ],
    }


SUITE_SCAFFOLD_TEMPLATE_LOCATORS = {
    "suite-index.md": "docs/methodology/templates/scaffold/full-suite-index.md",
    "spec.md": "docs/methodology/templates/scaffold/spec.md",
    "plan.md": "docs/methodology/templates/scaffold/plan.md",
    "research.md": "docs/methodology/templates/scaffold/research.md",
    "contracts.md": "docs/methodology/templates/scaffold/contracts.md",
    "readiness-checklist.md": "docs/methodology/templates/scaffold/readiness-checklist.md",
}

SUITE_SCAFFOLD_TEMPLATES = {
    artifact: REPO_ROOT / locator
    for artifact, locator in SUITE_SCAFFOLD_TEMPLATE_LOCATORS.items()
}

SUITE_SCAFFOLD_ARTIFACTS = {
    "minimal": ("spec.md", "plan.md"),
    "full": (
        "suite-index.md",
        "spec.md",
        "plan.md",
        "research.md",
        "contracts.md",
        "readiness-checklist.md",
    ),
}

SUITE_SCAFFOLD_REQUIRED_ARTIFACTS = {
    "minimal": ("spec.md", "plan.md"),
    "full": ("suite-index.md", "spec.md", "plan.md"),
}

SUITE_SCAFFOLD_CONDITIONAL_ARTIFACTS = {
    "minimal": (),
    "full": ("research.md", "contracts.md", "readiness-checklist.md"),
}

SUITE_REQUIRED_ARTIFACTS_BY_PATH = {
    "minimal": {"spec.md", "plan.md"},
    "full": {"suite-index.md", "spec.md", "plan.md"},
    "not_applicable": set(),
    "unknown": set(),
}

SUITE_CONDITIONAL_ARTIFACTS_BY_PATH = {
    "minimal": set(),
    "full": {"research.md", "contracts.md", "readiness-checklist.md"},
    "not_applicable": set(),
    "unknown": set(),
}

SUITE_SCAFFOLD_CONTRACT_LOCATORS = (
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/templates/spec-suite.md",
)

SUITE_VALIDATE_CONTRACT_LOCATORS = (
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/templates/spec-suite.md",
)

SUITE_EVIDENCE_CONTRACT_LOCATORS = (
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/templates/evidence-map.md",
)

SUITE_CARRIER_CONTRACT_LOCATORS = (
    "docs/methodology/harness/task-carrier-contract.md",
    "docs/methodology/templates/execution-breakdown.md",
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
)

SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR = "docs/methodology/templates/scaffold/evidence-map.md"
SUITE_EVIDENCE_SCAFFOLD_TEMPLATE = REPO_ROOT / SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR

SUITE_VALIDATE_ADVISORY_ARTIFACTS = {
    "full": (
        "evidence-map.md",
        "consistency-analysis.md",
        "execution-breakdown.md",
        "task-carrier",
    ),
    "minimal": (),
    "not_applicable": (),
}

SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS = {
    "suite-index.md",
    "research.md",
    "contracts.md",
    "readiness-checklist.md",
}

SUITE_NOT_APPLICABLE_ALIASES = {
    "full-suite-artifacts": SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS,
    "full-path-artifacts": SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS,
    "suite-level": {"suite"},
    "whole-suite": {"suite"},
    "formal-suite": {"suite"},
}

SUITE_NOT_APPLICABLE_REQUIRED_FIELDS = {
    "rationale": ("rationale", "reason"),
    "consumer_boundary": ("consumer boundary", "consumer_boundary", "consumer"),
    "recheck_condition": ("recheck condition", "recheck_condition", "recheck"),
}

SUITE_MAPPING_STRATEGY_MARKERS = (
    "automated",
    "manual",
    "structural",
    "not_applicable",
    "not applicable",
    "test evidence",
    "behavior evidence",
    "validation evidence",
    "structural check",
    "manual evidence",
)

SUITE_SCENARIO_ID_PATTERN = re.compile(r"(?i)(?:^|\b)scenario\s+([A-Z][A-Z0-9_-]*\d[A-Z0-9_-]*)\b")
SUITE_ACCEPTANCE_ID_PATTERN = re.compile(r"(?i)(?:^|\b)(?:acceptance|criterion)\s+([A-Z][A-Z0-9_-]*\d[A-Z0-9_-]*)\b|\b(A\d+|AC[-_]?\d+)\s*:")

SUITE_VALIDATE_FAILURE_TAXONOMY: dict[str, dict[str, str]] = {
    "invalid_suite_item": {
        "default_result": "block",
        "failed_layer": "suite-input",
        "fallback_to": "loom suite inspect --target <repo> --item <item> --json",
    },
    "missing_suite_path_decision": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite inspect --target <repo> --item <item> --json",
    },
    "missing_required_artifact": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite scaffold --target <repo> --item <item> --json",
    },
    "invalid_not_applicable_rationale": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "deferred_as_completed": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "missing_spec_plan_mapping": {
        "default_result": "block",
        "failed_layer": "spec/plan",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "missing_optional_suite_artifact": {
        "default_result": "advisory",
        "failed_layer": "suite",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "missing_evidence_map": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence scaffold --target <repo> --item <item> --json",
    },
    "stale_evidence": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "missing_fresh_verification_evidence": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "head_or_pr_drift": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "missing_source_locator": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "missing_task_carrier_locator": {
        "default_result": "block",
        "failed_layer": "task_carrier",
        "fallback_to": "loom suite carrier validate --target <repo> --item <item> --json",
    },
    "carrier_truth_conflict": {
        "default_result": "block",
        "failed_layer": "task_carrier",
        "fallback_to": "loom suite carrier inspect --target <repo> --item <item> --json",
    },
}

SUITE_EVIDENCE_REQUIRED_TYPES = ("behavior_evidence", "test_evidence", "fresh_verification_input")
SUITE_EVIDENCE_FRESHNESS_VALUES = {"present", "stale", "missing", "conflict", "not_applicable"}
SUITE_EVIDENCE_EMPTY_MARKERS = {
    "",
    "-",
    "tbd",
    "todo",
    "unknown",
    "n/a",
    "na",
    "not set",
    "not_set",
    "not-set",
}
SUITE_CARRIER_TYPES = {
    "github_issue",
    "github_project_item",
    "checklist_item",
    "repo_tasks_md",
    "external_tracker",
    "not_applicable",
}
SUITE_CARRIER_STATUS_VALUES = {
    "pending",
    "in_progress",
    "done",
    "blocked",
    "deferred",
    "not_applicable",
}
SUITE_CARRIER_RELATIONSHIPS = {"primary", "mirror", "evidence_locator", "not_applicable"}
SUITE_CARRIER_TRUTH_SIGNALS = {
    "carrier_done",
    "project_done",
    "project_in_progress",
    "checklist_checked",
    "evidence_missing",
    "issue_open",
    "issue_closed",
    "pr_open",
    "pr_merged",
    "work_item_open",
    "work_item_terminal",
}
SUITE_CARRIER_TERMINAL_CHECKPOINTS = {"closed", "merged", "retired", "complete", "completed"}


def suite_relevant_text_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip():
            current.append(line.strip())
            continue
        if current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return blocks


def suite_record_artifacts(block: str) -> set[str]:
    normalized = block.lower().replace("_", "-")
    artifacts = {
        artifact
        for artifact in SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS
        if artifact.lower() in normalized
    }
    for alias, alias_artifacts in SUITE_NOT_APPLICABLE_ALIASES.items():
        if alias in normalized or alias.replace("-", " ") in normalized:
            artifacts.update(alias_artifacts)
    return artifacts


def suite_record_required_fields(block: str) -> dict[str, bool]:
    lowered = block.lower().replace("_", " ")
    return {
        field: any(marker in lowered for marker in markers)
        for field, markers in SUITE_NOT_APPLICABLE_REQUIRED_FIELDS.items()
    }


def suite_applicability_records(paths: dict[str, list[Path]], target: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    not_applicable_records: list[dict[str, Any]] = []
    deferred_items: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for candidates in paths.values():
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            if not path.exists() or path.is_symlink() or not path.is_file():
                continue
            try:
                blocks = suite_relevant_text_blocks(path.read_text(encoding="utf-8"))
            except OSError:
                continue
            locator = repo_locator(path, target)
            for index, block in enumerate(blocks, start=1):
                lowered = block.lower()
                if "suite path:" in lowered and not any(marker in lowered for marker in ("rationale", "consumer", "recheck", "deferred")):
                    continue
                has_not_applicable = "not_applicable" in lowered or "not applicable" in lowered
                has_deferred = "deferred" in lowered
                artifacts = sorted(suite_record_artifacts(block))
                if has_not_applicable:
                    fields = suite_record_required_fields(block)
                    missing_fields = sorted(field for field, present in fields.items() if not present)
                    not_applicable_records.append(
                        {
                            "locator": locator,
                            "block": index,
                            "artifacts": artifacts,
                            "status": "valid" if artifacts and not missing_fields else "invalid",
                            "missing_fields": missing_fields,
                        }
                    )
                elif has_deferred:
                    deferred_items.append(
                        {
                            "locator": locator,
                            "block": index,
                            "artifacts": artifacts,
                            "status": "deferred",
                        }
                    )
    return not_applicable_records, deferred_items


def suite_covered_artifacts(records: list[dict[str, Any]]) -> set[str]:
    covered: set[str] = set()
    for record in records:
        if record.get("status") != "valid":
            continue
        artifacts = record.get("artifacts")
        if isinstance(artifacts, list):
            covered.update(str(artifact) for artifact in artifacts)
    return covered


def suite_unique_ids(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = value.strip().rstrip(":").upper()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def suite_spec_plan_ids(spec_text: str) -> tuple[list[str], list[str]]:
    scenario_ids: list[str] = []
    acceptance_ids: list[str] = []
    for line in spec_text.splitlines():
        stripped = line.strip()
        scenario_match = SUITE_SCENARIO_ID_PATTERN.search(stripped)
        if scenario_match:
            scenario_ids.append(scenario_match.group(1))
        acceptance_match = SUITE_ACCEPTANCE_ID_PATTERN.search(stripped)
        if acceptance_match:
            acceptance_ids.append(next(group for group in acceptance_match.groups() if group))
    return suite_unique_ids(scenario_ids), suite_unique_ids(acceptance_ids)


def suite_plan_mapping_lines(plan_text: str, identifier: str) -> list[str]:
    token = re.escape(identifier)
    id_pattern = re.compile(rf"(?i)(?:^|[^A-Z0-9_-]){token}(?:[^A-Z0-9_-]|$)")
    lines: list[str] = []
    for line in plan_text.splitlines():
        lowered = line.lower()
        if not id_pattern.search(line):
            continue
        if "->" not in line and "mapping" not in lowered and "strategy" not in lowered:
            continue
        if not any(marker in lowered for marker in SUITE_MAPPING_STRATEGY_MARKERS):
            continue
        lines.append(line.strip())
    return lines


def suite_spec_plan_mapping(paths: dict[str, list[Path]], target: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spec_locator = first_existing_locator(paths.get("spec.md", []), target)
    plan_locator = first_existing_locator(paths.get("plan.md", []), target)
    mapping = {
        "spec_locator": spec_locator,
        "plan_locator": plan_locator,
        "required_scenarios": [],
        "required_acceptance": [],
        "mapped_scenarios": [],
        "mapped_acceptance": [],
        "missing_scenarios": [],
        "missing_acceptance": [],
    }
    if spec_locator is None or plan_locator is None:
        return mapping, []

    spec_path = next((path for path in paths.get("spec.md", []) if path.exists() and path.is_file() and not path.is_symlink()), None)
    plan_path = next((path for path in paths.get("plan.md", []) if path.exists() and path.is_file() and not path.is_symlink()), None)
    if spec_path is None or plan_path is None:
        return mapping, []

    try:
        spec_text = spec_path.read_text(encoding="utf-8")
        plan_text = plan_path.read_text(encoding="utf-8")
    except OSError:
        return mapping, []

    scenario_ids, acceptance_ids = suite_spec_plan_ids(spec_text)
    mapped_scenarios: list[dict[str, Any]] = []
    missing_scenarios: list[str] = []
    for scenario_id in scenario_ids:
        lines = suite_plan_mapping_lines(plan_text, scenario_id)
        if lines:
            mapped_scenarios.append({"id": scenario_id, "plan_locator": plan_locator, "mapping": lines[0]})
        else:
            missing_scenarios.append(scenario_id)

    mapped_acceptance: list[dict[str, Any]] = []
    missing_acceptance: list[str] = []
    for acceptance_id in acceptance_ids:
        lines = suite_plan_mapping_lines(plan_text, acceptance_id)
        if lines:
            mapped_acceptance.append({"id": acceptance_id, "plan_locator": plan_locator, "mapping": lines[0]})
        else:
            missing_acceptance.append(acceptance_id)

    mapping.update(
        {
            "required_scenarios": scenario_ids,
            "required_acceptance": acceptance_ids,
            "mapped_scenarios": mapped_scenarios,
            "mapped_acceptance": mapped_acceptance,
            "missing_scenarios": missing_scenarios,
            "missing_acceptance": missing_acceptance,
        }
    )
    blocking_gaps: list[dict[str, Any]] = []
    for scenario_id in missing_scenarios:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-missing-scenario-mapping-{scenario_id.lower().replace('_', '-')}",
                classification="missing",
                failure_kind="missing_spec_plan_mapping",
                source_locator=spec_locator,
                consumer_impact=f"spec review cannot verify that scenario {scenario_id} maps to a plan validation strategy",
                remediation_direction=f"Map scenario {scenario_id} in plan.md to automated, manual, structural, or not_applicable validation.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
                surface="spec/plan",
                binding="suite-validate-spec-plan-mapping",
            )
        )
    for acceptance_id in missing_acceptance:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-missing-acceptance-mapping-{acceptance_id.lower().replace('_', '-')}",
                classification="missing",
                failure_kind="missing_spec_plan_mapping",
                source_locator=spec_locator,
                consumer_impact=f"spec review cannot verify that acceptance {acceptance_id} maps to a plan test strategy",
                remediation_direction=f"Map acceptance {acceptance_id} in plan.md to test evidence, structural check, manual evidence, or not_applicable.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
                surface="spec/plan",
                binding="suite-validate-spec-plan-mapping",
            )
        )
    return mapping, blocking_gaps


def suite_scaffold_payload(target: Path, item: str, suite_path: str, *, apply: bool) -> tuple[str, dict[str, Any], str | None]:
    item_error = suite_item_segment_error(item)
    if item_error:
        payload = {
            "suite_path": suite_path,
            "artifact_root": None,
            "suite_locator": None,
            "planned_writes": [],
            "source_templates": [],
            "consumed_locators": list(SUITE_SCAFFOLD_CONTRACT_LOCATORS),
            "overwrite_policy": {
                "mode": "preserve_existing",
                "allows_overwrite": False,
                "existing_files": [],
                "ambiguous_overwrite": "fail_closed",
            },
            "apply_required": not apply,
            "apply": apply,
            "rollback_note": "No files were created because the suite item did not resolve to a single repo-local path segment.",
            "created_locators": [],
            "missing_inputs": [item_error],
            "advisory_gaps": [],
        }
        return "Suite scaffold failed closed before resolving artifact paths.", payload, "invalid_suite_item"

    suite_root = target / ".loom" / "specs" / item
    artifacts = SUITE_SCAFFOLD_ARTIFACTS[suite_path]
    required_artifacts = SUITE_SCAFFOLD_REQUIRED_ARTIFACTS[suite_path]
    conditional_artifacts = SUITE_SCAFFOLD_CONDITIONAL_ARTIFACTS[suite_path]
    planned_writes: list[dict[str, Any]] = []
    source_templates: list[dict[str, str]] = []
    existing_files: list[str] = []
    created_locators: list[str] = []
    missing_inputs: list[str] = []
    consumed_locators = list(SUITE_SCAFFOLD_CONTRACT_LOCATORS)

    for artifact in artifacts:
        template = SUITE_SCAFFOLD_TEMPLATES[artifact]
        if not template.exists() or not template.is_file():
            missing_inputs.append(f"missing scaffold template: {template.relative_to(REPO_ROOT).as_posix()}")
        destination = suite_root / artifact
        for component in (target / ".loom", target / ".loom" / "specs", suite_root, destination):
            if component.is_symlink():
                missing_inputs.append(f"scaffold path must not traverse symlink: {repo_locator(component, target)}")
        if not destination.exists() and destination.parent.exists() and not destination.parent.is_dir():
            missing_inputs.append(f"scaffold parent is not a directory: {repo_locator(destination.parent, target)}")
        if destination.exists() and not destination.is_file():
            missing_inputs.append(f"scaffold artifact is not a regular file: {repo_locator(destination, target)}")

    for artifact in artifacts:
        destination = suite_root / artifact
        destination_locator = repo_locator(destination, target)
        template = SUITE_SCAFFOLD_TEMPLATES[artifact]
        template_locator = SUITE_SCAFFOLD_TEMPLATE_LOCATORS[artifact]
        exists = destination.exists()
        if exists:
            existing_files.append(destination_locator)
        if apply and not exists and not missing_inputs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            created_locators.append(destination_locator)
        planned_writes.append(
            {
                "artifact": artifact,
                "locator": destination_locator,
                "source_template": template_locator,
                "status": "exists" if exists else ("created" if apply and not missing_inputs else "would_create"),
                "planned_action": "preserve_existing" if exists else "create",
                "would_write": not exists,
                "wrote": apply and not exists and not missing_inputs,
                "overwrite_policy": "preserve_existing",
                "requirement": "required" if artifact in required_artifacts else "conditional",
            }
        )
        source_templates.append(
            {
                "artifact": artifact,
                "locator": template_locator,
            }
        )

    overwrite_policy = {
        "mode": "preserve_existing",
        "allows_overwrite": False,
        "existing_files": existing_files,
        "ambiguous_overwrite": "fail_closed",
    }
    payload = {
        "suite_path": suite_path,
        "artifact_root": repo_locator(suite_root, target),
        "suite_locator": repo_locator(suite_root, target),
        "planned_writes": planned_writes,
        "source_templates": source_templates,
        "required_artifacts": list(required_artifacts),
        "conditional_artifacts": list(conditional_artifacts),
        "consumed_locators": consumed_locators,
        "overwrite_policy": overwrite_policy,
        "apply_required": not apply,
        "apply": apply,
        "rollback_note": (
            "Dry-run only; no files were created. If applied later, rollback is deleting the created repo-relative locators before they are consumed as authored truth."
            if not apply
            else "Rollback is deleting the created repo-relative locators before they are consumed as authored truth; preserved existing files were not modified."
        ),
        "created_locators": created_locators,
        "missing_inputs": missing_inputs,
        "advisory_gaps": [],
    }
    if missing_inputs:
        summary = "Suite scaffold apply failed closed before writing artifacts." if apply else "Suite scaffold dry-run found unavailable scaffold inputs."
        return summary, payload, "missing_scaffold_inputs"
    if apply:
        summary = f"Suite scaffold applied {suite_path} suite artifacts with preserve-existing overwrite policy."
    else:
        summary = f"Suite scaffold dry-run planned {suite_path} suite artifacts without mutating the repository."
    return summary, payload, None


def suite_scaffold_dry_run_payload(target: Path, item: str, suite_path: str) -> tuple[str, dict[str, Any]]:
    summary, payload, _ = suite_scaffold_payload(target, item, suite_path, apply=False)
    return summary, payload


def suite_evidence_scaffold_content(target: Path, item: str, inspect_payload: dict[str, Any]) -> str:
    suite_path = str(inspect_payload.get("suite_path") or "unknown")
    suite_locator = str(inspect_payload.get("suite_locator") or f".loom/specs/{item}")
    spec_locator = str(inspect_payload.get("spec_locator") or f".loom/specs/{item}/spec.md")
    plan_locator = str(inspect_payload.get("plan_locator") or f".loom/specs/{item}/plan.md")
    path_decision_locator = str(inspect_payload.get("path_decision_locator") or "not_authored")
    task_carriers = inspect_payload.get("task_carrier_locators")
    task_carrier_locator = ", ".join(str(locator) for locator in task_carriers) if isinstance(task_carriers, list) and task_carriers else "not_applicable rationale required"
    template_text = SUITE_EVIDENCE_SCAFFOLD_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "- Work Item locator:": f"- Work Item locator: .loom/work-items/{item}.md",
        "- FR / parent locator:": "- FR / parent locator:",
        "- Scope:": "- Scope: current Work Item scope; replace with authored scope before review consumption.",
        "- Suite path:": f"- Suite path: {suite_path}",
        "- Current `HEAD`:": "- Current `HEAD`: fill with current head before merge-ready consumption.",
        "- PR locator, or `not_applicable` rationale:": "- PR locator, or `not_applicable` rationale: fill when PR exists; otherwise author not_applicable rationale.",
        "- Host state locator, or `not_applicable` rationale:": "- Host state locator, or `not_applicable` rationale: fill when host state exists; otherwise author not_applicable rationale.",
        "| `spec.md` |  | required |  |  |": f"| `spec.md` | {spec_locator} | required | suite inspect | Bind to current Work Item, scope, and head before consumption. |",
        "| `plan.md` |  | required |  |  |": f"| `plan.md` | {plan_locator} | required | suite inspect | Bind to current validation strategy and head before consumption. |",
        "| suite path decision |  | candidate / optional / not_applicable |  |  |": f"| suite path decision | {path_decision_locator} | candidate / optional / not_applicable | suite inspect | Recheck when suite path changes. |",
        "| execution breakdown / task carrier |  | candidate / optional / deferred / not_applicable |  |  |": f"| execution breakdown / task carrier | {task_carrier_locator} | candidate / optional / deferred / not_applicable | suite inspect | Recheck when task carrier contract is consumed. |",
        "| review record |  | optional / required / not_applicable |  |  |": "| review record |  | optional / required / not_applicable | authored review truth | Required only after review consumption. |",
        "| merge-ready basis |  | optional / required / not_applicable |  |  |": "| merge-ready basis |  | optional / required / not_applicable | merge-ready truth | Required only for merge-ready or closeout consumption. |",
        "| host state |  | required / not_applicable |  |  |": "| host state |  | required / not_applicable | host mirror | Required when PR / issue / Project exists. |",
        "| EV-001 | behavior_evidence |  | spec scenario / acceptance locator | Work Item / scope / head / PR | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status |  |": f"| EV-001 | behavior_evidence |  | {spec_locator} scenario / acceptance locator | {item} / scope / head / PR | missing | review / merge-ready / closeout / status | Add behavior evidence source locator and binding before validation. |",
        "| EV-002 | test_evidence |  | plan validation / test strategy locator | Work Item / scope / head / PR | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status |  |": f"| EV-002 | test_evidence |  | {plan_locator} validation / test strategy locator | {item} / scope / head / PR | missing | review / merge-ready / closeout / status | Add test evidence source locator and rerun validation before consumption. |",
        "| EV-003 | fresh_verification_input |  | evidence row ids | head / reviewed head / PR head / validation summary | present / stale / missing / conflict / not_applicable | merge-ready / closeout / status |  |": "| EV-003 | fresh_verification_input |  | EV-001 EV-002 | head / reviewed head / PR head / validation summary | missing | merge-ready / closeout / status | Mark present only after behavior and test evidence are present for the current object. |",
    }
    for old, new in replacements.items():
        template_text = template_text.replace(old, new)
    return template_text.rstrip() + "\n"


def suite_evidence_scaffold_payload(target: Path, item: str, *, apply: bool) -> tuple[str, dict[str, Any], str | None]:
    item_error = suite_item_segment_error(item)
    if item_error:
        payload = {
            "artifact_root": None,
            "suite_locator": None,
            "evidence_map_locator": None,
            "planned_writes": [],
            "source_templates": [],
            "consumed_locators": [*SUITE_EVIDENCE_CONTRACT_LOCATORS, SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR],
            "consumed_suite_locators": {},
            "overwrite_policy": {
                "mode": "preserve_existing",
                "allows_overwrite": False,
                "existing_files": [],
                "ambiguous_overwrite": "fail_closed",
            },
            "apply_required": not apply,
            "apply": apply,
            "rollback_note": "No files were created because the suite item did not resolve to a single repo-local path segment.",
            "created_locators": [],
            "missing_inputs": [item_error],
            "advisory_gaps": [],
            "seed_rows": [],
            "initial_freshness_policy": "scaffold never marks evidence present",
        }
        return "Suite evidence scaffold failed closed before resolving artifact paths.", payload, "invalid_suite_item"

    inspect_summary, inspect_payload = suite_inspect_payload(target, item)
    suite_root = target / ".loom" / "specs" / item
    destination = suite_root / "evidence-map.md"
    destination_locator = repo_locator(destination, target)
    missing_inputs: list[str] = []

    if not SUITE_EVIDENCE_SCAFFOLD_TEMPLATE.exists() or not SUITE_EVIDENCE_SCAFFOLD_TEMPLATE.is_file():
        missing_inputs.append(f"missing scaffold template: {SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR}")
    for component in (target / ".loom", target / ".loom" / "specs", suite_root, destination):
        if component.is_symlink():
            missing_inputs.append(f"scaffold path must not traverse symlink: {repo_locator(component, target)}")
    if not destination.exists() and destination.parent.exists() and not destination.parent.is_dir():
        missing_inputs.append(f"scaffold parent is not a directory: {repo_locator(destination.parent, target)}")
    if destination.exists() and not destination.is_file():
        missing_inputs.append(f"scaffold artifact is not a regular file: {destination_locator}")

    exists = destination.exists()
    created_locators: list[str] = []
    if apply and not exists and not missing_inputs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(suite_evidence_scaffold_content(target, item, inspect_payload), encoding="utf-8")
        created_locators.append(destination_locator)

    existing_files = [destination_locator] if exists else []
    consumed_suite_locators = {
        "suite_path": inspect_payload.get("suite_path"),
        "suite_locator": inspect_payload.get("suite_locator"),
        "path_decision_locator": inspect_payload.get("path_decision_locator"),
        "spec_locator": inspect_payload.get("spec_locator") or f".loom/specs/{item}/spec.md",
        "plan_locator": inspect_payload.get("plan_locator") or f".loom/specs/{item}/plan.md",
        "task_carrier_locators": inspect_payload.get("task_carrier_locators", []),
    }
    payload = {
        "suite_path": inspect_payload.get("suite_path"),
        "artifact_root": repo_locator(suite_root, target),
        "suite_locator": inspect_payload.get("suite_locator") or repo_locator(suite_root, target),
        "evidence_map_locator": destination_locator,
        "planned_writes": [
            {
                "artifact": "evidence-map.md",
                "locator": destination_locator,
                "source_template": SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR,
                "status": "exists" if exists else ("created" if apply and not missing_inputs else "would_create"),
                "planned_action": "preserve_existing" if exists else "create",
                "would_write": not exists,
                "wrote": apply and not exists and not missing_inputs,
                "overwrite_policy": "preserve_existing",
                "requirement": "evidence_map",
                "initial_freshness": "missing",
            }
        ],
        "source_templates": [{"artifact": "evidence-map.md", "locator": SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR}],
        "consumed_locators": [*SUITE_EVIDENCE_CONTRACT_LOCATORS, SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR],
        "consumed_suite_locators": consumed_suite_locators,
        "overwrite_policy": {
            "mode": "preserve_existing",
            "allows_overwrite": False,
            "existing_files": existing_files,
            "ambiguous_overwrite": "fail_closed",
        },
        "apply_required": not apply,
        "apply": apply,
        "rollback_note": (
            "Dry-run only; no files were created. If applied later, rollback is deleting the created repo-relative evidence-map locator before it is consumed as authored truth."
            if not apply
            else "Rollback is deleting the created repo-relative evidence-map locator before it is consumed as authored truth; preserved existing files were not modified."
        ),
        "created_locators": created_locators,
        "missing_inputs": missing_inputs,
        "advisory_gaps": [],
        "seed_rows": [
            {"evidence_id": "EV-001", "evidence_type": "behavior_evidence", "freshness": "missing"},
            {"evidence_id": "EV-002", "evidence_type": "test_evidence", "freshness": "missing"},
            {"evidence_id": "EV-003", "evidence_type": "fresh_verification_input", "freshness": "missing"},
        ],
        "initial_freshness_policy": "scaffold never marks evidence present",
        "inspect_summary": inspect_summary,
    }
    if missing_inputs:
        summary = "Suite evidence scaffold apply failed closed before writing artifacts." if apply else "Suite evidence scaffold dry-run found unavailable scaffold inputs."
        return summary, payload, "missing_scaffold_inputs"
    if apply:
        summary = "Suite evidence scaffold applied evidence-map artifact with preserve-existing overwrite policy."
    else:
        summary = "Suite evidence scaffold dry-run planned evidence-map artifact without mutating the repository."
    return summary, payload, None


def suite_inspect_payload(target: Path, item: str | None) -> tuple[str, dict[str, Any]]:
    paths = suite_artifact_paths(target, item)
    suite_index = paths.get("suite-index.md", [None])[0]
    spec = paths.get("spec.md", [None])[0]
    plan = paths.get("plan.md", [None])[0]

    path_decision_locator: str | None = None
    suite_path = "unknown"
    path_decisions: list[dict[str, Any]] = []
    decision_values: list[str] = []
    invalid_decision_locators: list[str] = []
    for path in (suite_index, spec, plan):
        if path is None:
            continue
        if path.exists() and (path.is_symlink() or not path.is_file()):
            if path == suite_index:
                locator = repo_locator(path, target)
                invalid_decision_locators.append(locator)
                path_decisions.append(
                    {
                        "locator": locator,
                        "value": None,
                        "status": "invalid",
                        "reason": "path decision candidate is not a regular file",
                    }
                )
            continue
        values, invalid_values = read_suite_path_marker_values(path)
        if not values and not invalid_values:
            continue
        locator = repo_locator(path, target)
        for value in values:
            path_decisions.append({"locator": locator, "value": value, "status": "present"})
            decision_values.append(value)
        for value in invalid_values:
            invalid_decision_locators.append(locator)
            path_decisions.append({"locator": locator, "value": value, "status": "invalid"})

    unique_decision_values = sorted(set(decision_values))
    if len(unique_decision_values) == 1 and not invalid_decision_locators:
        suite_path = unique_decision_values[0]
        path_decision_locator = next(
            (entry["locator"] for entry in path_decisions if entry.get("value") == suite_path),
            None,
        )

    required = SUITE_REQUIRED_ARTIFACTS_BY_PATH.get(suite_path, set())
    conditional = SUITE_CONDITIONAL_ARTIFACTS_BY_PATH.get(suite_path, set())
    advisory = set(SUITE_VALIDATE_ADVISORY_ARTIFACTS.get(suite_path, ()))

    artifact_inventory: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    locators: dict[str, Any] = {}
    if invalid_decision_locators or len(unique_decision_values) > 1:
        missing_inputs.append("suite_path_decision")
        for locator in sorted(set(invalid_decision_locators)):
            missing_inputs.append(f"invalid_suite_path_decision:{locator}")
        if len(unique_decision_values) > 1:
            for entry in path_decisions:
                if entry.get("status") == "present":
                    missing_inputs.append(f"conflicting_suite_path_decision:{entry['locator']}")
    for artifact, candidates in paths.items():
        locator, invalid_locator = first_artifact_locator_or_invalid(candidates, target)
        is_required = artifact in required
        is_conditional = artifact in conditional
        is_advisory = artifact in advisory
        requirement = (
            "required"
            if is_required
            else ("conditional" if is_conditional else ("extension" if is_advisory else "optional"))
        )
        if locator is not None:
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": locator,
                    "status": "present",
                    "required": is_required,
                    "requirement": requirement,
                }
            )
        elif invalid_locator is not None:
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": invalid_locator,
                    "status": "invalid",
                    "required": is_required,
                    "requirement": requirement,
                }
            )
            if is_required:
                missing_inputs.append(f"required_artifact:{invalid_locator}")
        elif is_required:
            expected = repo_locator(candidates[0], target)
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": expected,
                    "status": "missing",
                    "required": True,
                    "requirement": requirement,
                }
            )
            missing_inputs.append(f"required_artifact:{expected}")
        elif is_conditional or is_advisory:
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": repo_locator(candidates[0], target),
                    "status": "absent",
                    "required": False,
                    "requirement": requirement,
                }
            )

        key = artifact.replace("-", "_").removesuffix(".md") + "_locator"
        if artifact == "task-carrier":
            locators["task_carrier_locators"] = [locator] if locator is not None else []
        else:
            locators[key] = locator

    if suite_path == "unknown" and "suite_path_decision" not in missing_inputs:
        missing_inputs.insert(0, "suite_path_decision")

    advisory_gaps = []
    if suite_path == "unknown":
        advisory_gaps.append(
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
        )
    for missing in missing_inputs:
        if not missing.startswith("required_artifact:"):
            continue
        locator = missing.split(":", 1)[1]
        advisory_gaps.append(
            {
                "id": f"suite-inspect-missing-{Path(locator).name}",
                "classification": "missing",
                "failure_kind": "missing_required_artifact",
                "surface": "suite",
                "source_locator": locator,
                "consumer_impact": "inspect-only",
                "remediation_direction": "Run suite scaffold dry-run or author the missing repo-relative artifact before readiness validation.",
                "fallback_to": "loom suite scaffold --target <repo> --item <item> --json",
            }
        )

    summary_by_path = {
        "full": "Suite inspect found a full suite path decision.",
        "minimal": "Suite inspect found a minimal suite path decision.",
        "not_applicable": "Suite inspect found a not_applicable suite path decision.",
        "unknown": "Suite state is unknown; no suite path decision was derived.",
    }
    summary = summary_by_path.get(suite_path, summary_by_path["unknown"])
    if any(entry["status"] == "missing" for entry in artifact_inventory):
        summary = f"{summary} Missing expected artifact locators are reported for later validation."

    payload = {
        "suite_path": suite_path,
        "suite_locator": locators.get("suite_index_locator"),
        "path_decision_locator": path_decision_locator,
        "path_decisions": path_decisions,
        "artifact_inventory": artifact_inventory,
        "not_applicable_rationale": [],
        "deferred_items": [],
        "missing_inputs": missing_inputs,
        "advisory_gaps": advisory_gaps,
        **locators,
    }
    return summary, payload


def suite_validate_finding(
    *,
    gap_id: str,
    classification: str,
    failure_kind: str,
    source_locator: str | None,
    consumer_impact: str,
    remediation_direction: str,
    fallback_to: str,
    surface: str = "suite",
    binding: str = "suite-validate-core",
) -> dict[str, Any]:
    taxonomy = SUITE_VALIDATE_FAILURE_TAXONOMY.get(failure_kind, {})
    default_result = taxonomy.get("default_result", "block" if classification != "advisory" else "advisory")
    failed_layer = taxonomy.get("failed_layer", surface)
    return {
        "id": gap_id,
        "classification": classification,
        "failure_kind": failure_kind,
        "default_result": default_result,
        "failed_layer": failed_layer,
        "surface": surface,
        "source_locator": source_locator,
        "conflicting_locator": None,
        "freshness": "missing" if classification == "missing" else None,
        "binding": binding,
        "consumer_impact": consumer_impact,
        "remediation_direction": remediation_direction,
        "fallback_to": fallback_to,
    }


def suite_failure_taxonomy_for_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    taxonomy_entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for finding in findings:
        failure_kind = str(finding.get("failure_kind") or "")
        if not failure_kind or failure_kind in seen:
            continue
        seen.add(failure_kind)
        taxonomy = SUITE_VALIDATE_FAILURE_TAXONOMY.get(failure_kind, {})
        taxonomy_entries.append(
            {
                "failure_kind": failure_kind,
                "classification": finding.get("classification"),
                "default_result": finding.get("default_result") or taxonomy.get("default_result"),
                "failed_layer": finding.get("failed_layer") or taxonomy.get("failed_layer"),
                "source_locator": finding.get("source_locator"),
                "consumer_impact": finding.get("consumer_impact"),
                "remediation_direction": finding.get("remediation_direction"),
                "fallback_to": finding.get("fallback_to") or taxonomy.get("fallback_to"),
                "binding": finding.get("binding"),
            }
        )
    return taxonomy_entries


def suite_evidence_path(target: Path, item: str | None) -> Path | None:
    return suite_artifact_paths(target, item).get("evidence-map.md", [None])[0]


def normalized_table_cell(value: str) -> str:
    return re.sub(r"<br\s*/?>", " ", value.strip(), flags=re.IGNORECASE).replace("`", "").strip()


def normalize_table_header(value: str) -> str:
    normalized = normalized_table_cell(value).lower().replace("-", "_").replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "", normalized)


def is_empty_evidence_value(value: Any) -> bool:
    return str(value or "").strip().lower() in SUITE_EVIDENCE_EMPTY_MARKERS


def git_head_sha_for_target(target: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    head = completed.stdout.strip()
    return head if re.fullmatch(r"[0-9a-f]{40}", head) else None


def latest_validation_summary_for_item(target: Path, item: str) -> str | None:
    progress_path = target / ".loom" / "progress" / f"{item}.md"
    try:
        text = progress_path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        if line.startswith("- Latest Validation Summary:"):
            return line.split(":", 1)[1].strip()
    return None


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def evidence_binding_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field) or "")
        for field in (
            "binding",
            "freshness_rule",
            "provenance",
            "consumer_boundary",
        )
    )


def binding_sha_matches(observed: str, expected: str) -> bool:
    return expected.startswith(observed.lower()) if len(observed) < len(expected) else observed.lower() == expected


def extract_binding_shas(text: str, names: tuple[str, ...]) -> list[str]:
    name_pattern = "|".join(re.escape(name) for name in names)
    return [
        match.group(2).lower()
        for match in re.finditer(
            rf"\b({name_pattern})\b\s*[:=]\s*([0-9a-f]{{7,64}})",
            text,
            flags=re.IGNORECASE,
        )
    ]


def is_repo_local_source_locator(source_locator: str, source_kind: str) -> bool:
    if source_kind == "repo_file":
        return True
    if not source_locator or re.match(r"^[a-z][a-z0-9+.-]*:", source_locator, re.IGNORECASE):
        return False
    if source_locator.startswith((".", "/")):
        return True
    return " " not in source_locator and "/" in source_locator


def split_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [normalized_table_cell(cell) for cell in stripped.strip("|").split("|")]


def is_markdown_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_evidence_map_rows(path: Path, target: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        header_cells = split_markdown_table_row(lines[index])
        if not header_cells:
            index += 1
            continue
        if index + 1 >= len(lines):
            break
        separator_cells = split_markdown_table_row(lines[index + 1])
        if not is_markdown_separator_row(separator_cells):
            index += 1
            continue

        headers = [normalize_table_header(cell) for cell in header_cells]
        if "evidence_id" not in headers and "evidenceid" not in headers and "type" not in headers:
            index += 2
            continue

        index += 2
        while index < len(lines):
            cells = split_markdown_table_row(lines[index])
            if not cells or is_markdown_separator_row(cells):
                break
            mapped = {headers[cell_index]: cells[cell_index] for cell_index in range(min(len(headers), len(cells)))}
            evidence_id = mapped.get("evidence_id") or mapped.get("evidenceid") or mapped.get("id") or ""
            evidence_type = mapped.get("type") or mapped.get("evidence_type") or ""
            source_locator = mapped.get("source_locator") or mapped.get("source") or ""
            freshness = (mapped.get("freshness") or "").strip().lower().replace(" ", "_")
            row_locator = f"{repo_locator(path, target)}:{index + 1}"
            source_exists = None
            source_kind = mapped.get("source_kind") or mapped.get("sourcekind") or None
            if source_locator and not re.match(r"^[a-z][a-z0-9+.-]*:", source_locator, re.IGNORECASE):
                source_path = (target / source_locator).resolve()
                try:
                    source_exists = source_path.is_relative_to(target.resolve()) and source_path.exists()
                except OSError:
                    source_exists = False
            rows.append(
                {
                    "evidence_id": evidence_id,
                    "evidence_type": evidence_type.strip().lower(),
                    "source_locator": source_locator,
                    "source_kind": source_kind,
                    "consumes": mapped.get("consumes") or "",
                    "binding": mapped.get("binding") or "",
                    "freshness": freshness,
                    "freshness_rule": mapped.get("freshness_rule") or mapped.get("freshnessrule") or "",
                    "provenance": mapped.get("provenance") or "",
                    "consumer_boundary": mapped.get("consumer_boundary") or mapped.get("consumerboundary") or "",
                    "remediation_direction": mapped.get("remediation_direction") or mapped.get("remediationdirection") or "",
                    "locator": row_locator,
                    "source_exists": source_exists,
                }
            )
            index += 1
        continue
    return rows


def suite_evidence_inspect_payload(target: Path, item: str) -> tuple[str, dict[str, Any]]:
    evidence_path = suite_evidence_path(target, item)
    evidence_locator = repo_locator(evidence_path, target) if evidence_path else None
    status = "missing"
    rows: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    advisory_gaps: list[dict[str, Any]] = []

    if evidence_path is None:
        evidence_locator = f".loom/specs/{item}/evidence-map.md"
        missing_inputs.append("evidence_map_locator")
    elif evidence_path.exists() and (evidence_path.is_symlink() or not evidence_path.is_file()):
        status = "invalid"
        missing_inputs.append(f"invalid_evidence_map:{evidence_locator}")
    elif evidence_path.exists():
        status = "present"
        rows = parse_evidence_map_rows(evidence_path, target)
        if not rows:
            missing_inputs.append(f"evidence_rows:{evidence_locator}")
    else:
        missing_inputs.append("evidence_map_locator")

    if missing_inputs:
        advisory_gaps.append(
            suite_validate_finding(
                gap_id="suite-evidence-inspect-missing-evidence-map",
                classification="missing",
                failure_kind="missing_evidence_map",
                source_locator=evidence_locator,
                consumer_impact="inspect-only",
                remediation_direction="Author or scaffold evidence-map rows before evidence readiness validation.",
                fallback_to="loom suite evidence scaffold --target <repo> --item <item> --json",
                surface="evidence_map",
                binding="suite-evidence-inspect",
            )
        )

    payload = {
        "evidence_map": {
            "locator": evidence_locator,
            "status": status,
            "row_count": len(rows),
        },
        "evidence_map_locator": evidence_locator if status == "present" else None,
        "rows": rows,
        "required_evidence_types": list(SUITE_EVIDENCE_REQUIRED_TYPES),
        "freshness_values": sorted(SUITE_EVIDENCE_FRESHNESS_VALUES),
        "consumed_contracts": list(SUITE_EVIDENCE_CONTRACT_LOCATORS),
        "missing_inputs": missing_inputs,
        "advisory_gaps": advisory_gaps,
    }
    summary = "Suite evidence inspect found an evidence-map." if status == "present" else "Suite evidence inspect did not find a usable evidence-map."
    return summary, payload


def suite_evidence_validate_payload(target: Path, item: str) -> tuple[str, str, dict[str, Any], str | None, str | None, list[str]]:
    item_error = suite_item_segment_error(item)
    if item_error:
        blocking_gaps = [
            suite_validate_finding(
                gap_id="suite-evidence-validate-invalid-item",
                classification="blocking",
                failure_kind="invalid_suite_item",
                source_locator=None,
                consumer_impact="evidence validation cannot bind an unsafe item segment",
                remediation_direction="Use a single repo-local Work Item id as the suite item.",
                fallback_to="loom suite evidence inspect --target <repo> --item <item> --json",
                surface="evidence_map",
                binding="suite-evidence-validate",
            )
        ]
        payload = {
            "evidence_map": {"locator": None, "status": "invalid", "row_count": 0},
            "rows": [],
            "consumed_contracts": list(SUITE_EVIDENCE_CONTRACT_LOCATORS),
            "missing_inputs": [item_error],
            "blocking_gaps": blocking_gaps,
            "advisory_gaps": [],
            "findings": blocking_gaps,
            "failure_taxonomy": suite_failure_taxonomy_for_findings(blocking_gaps),
            "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
            "remediation_directions": [blocking_gaps[0]["remediation_direction"]],
        }
        return (
            "Suite evidence validate failed closed before resolving evidence-map.",
            "block",
            payload,
            "evidence_map",
            "invalid_suite_item",
            ["loom suite evidence inspect --target <repo> --item <item> --json"],
        )

    inspect_summary, inspect_payload = suite_evidence_inspect_payload(target, item)
    rows = inspect_payload.get("rows", [])
    missing_inputs = list(inspect_payload.get("missing_inputs", []))
    evidence_locator = inspect_payload.get("evidence_map", {}).get("locator")
    current_head = git_head_sha_for_target(target)
    validation_summary = latest_validation_summary_for_item(target, item)
    validation_summary_sha256 = sha256_text(validation_summary) if validation_summary else None
    blocking_gaps: list[dict[str, Any]] = []
    advisory_gaps: list[dict[str, Any]] = []

    def add_gap(
        *,
        gap_id: str,
        classification: str,
        failure_kind: str,
        source_locator: str | None,
        impact: str,
        remediation: str,
        fallback: str = "loom suite evidence validate --target <repo> --item <item> --json",
    ) -> None:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=gap_id,
                classification=classification,
                failure_kind=failure_kind,
                source_locator=source_locator,
                consumer_impact=impact,
                remediation_direction=remediation,
                fallback_to=fallback,
                surface="evidence_map",
                binding="suite-evidence-validate",
            )
        )

    if missing_inputs:
        add_gap(
            gap_id="suite-evidence-validate-missing-evidence-map",
            classification="missing",
            failure_kind="missing_evidence_map",
            source_locator=evidence_locator,
            impact="merge-ready evidence validation cannot consume missing or unreadable evidence-map rows",
            remediation="Author or scaffold evidence-map rows before evidence readiness validation.",
            fallback="loom suite evidence scaffold --target <repo> --item <item> --json",
        )

    required_row_fields = (
        "evidence_id",
        "evidence_type",
        "source_locator",
        "consumes",
        "binding",
        "freshness",
        "consumer_boundary",
        "remediation_direction",
    )
    present_by_type: dict[str, list[dict[str, Any]]] = {evidence_type: [] for evidence_type in SUITE_EVIDENCE_REQUIRED_TYPES}
    present_ids_by_type: dict[str, set[str]] = {evidence_type: set() for evidence_type in SUITE_EVIDENCE_REQUIRED_TYPES}

    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_locator = str(row.get("locator") or evidence_locator or "")
            evidence_type = str(row.get("evidence_type") or "").strip().lower()
            freshness = str(row.get("freshness") or "").strip().lower()
            missing_fields = [field for field in required_row_fields if is_empty_evidence_value(row.get(field))]
            if missing_fields:
                add_gap(
                    gap_id=f"suite-evidence-validate-missing-fields-{row.get('evidence_id') or Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_evidence_map",
                    source_locator=row_locator,
                    impact="merge-ready cannot consume evidence rows with incomplete binding, freshness, or consumer boundary fields",
                    remediation=f"Fill evidence-map fields before validation; missing: {', '.join(missing_fields)}.",
                    fallback="loom suite evidence scaffold --target <repo> --item <item> --json",
                )
                continue
            if freshness not in SUITE_EVIDENCE_FRESHNESS_VALUES:
                add_gap(
                    gap_id=f"suite-evidence-validate-invalid-freshness-{row.get('evidence_id')}",
                    classification="missing",
                    failure_kind="missing_evidence_map",
                    source_locator=row_locator,
                    impact="merge-ready cannot classify evidence freshness from an unknown value",
                    remediation="Use one of present, stale, missing, conflict, or not_applicable for evidence freshness.",
                    fallback="loom suite evidence validate --target <repo> --item <item> --json",
                )
                continue
            binding_drift = False
            if freshness == "present":
                source_locator = str(row.get("source_locator") or "")
                source_kind = str(row.get("source_kind") or "").strip().lower()
                if row.get("source_exists") is False and is_repo_local_source_locator(source_locator, source_kind):
                    binding_drift = True
                    add_gap(
                        gap_id=f"suite-evidence-validate-missing-source-{row.get('evidence_id')}",
                        classification="missing",
                        failure_kind="missing_source_locator",
                        source_locator=row_locator,
                        impact="merge-ready cannot consume present evidence whose repo-local source locator is missing",
                        remediation="Restore the cited source locator or update evidence-map to a current readable locator.",
                    )

                binding_text = evidence_binding_text(row)
                binding_text_lower = binding_text.lower()
                explicit_stale_markers = (
                    "previous head",
                    "old head",
                    "stale head",
                    "previous pr head",
                    "old pr head",
                    "stale pr head",
                    "old validation summary",
                    "stale validation summary",
                )
                if any(marker in binding_text_lower for marker in explicit_stale_markers):
                    binding_drift = True
                    add_gap(
                        gap_id=f"suite-evidence-validate-stale-binding-{row.get('evidence_id')}",
                        classification="stale",
                        failure_kind="stale_evidence",
                        source_locator=row_locator,
                        impact="merge-ready cannot consume evidence with an explicitly stale HEAD, PR head, or validation summary binding",
                        remediation="Refresh the evidence binding to the current HEAD, PR head, reviewed head, and validation summary.",
                    )

                head_checks = (
                    ("head", extract_binding_shas(binding_text, ("head_sha", "current_head", "head"))),
                    ("pr_head", extract_binding_shas(binding_text, ("pr_head_sha", "pr_head"))),
                    ("reviewed_head", extract_binding_shas(binding_text, ("reviewed_head_sha", "reviewed_head"))),
                )
                for binding_name, observed_shas in head_checks:
                    if not observed_shas:
                        continue
                    if current_head is None or not any(binding_sha_matches(observed, current_head) for observed in observed_shas):
                        binding_drift = True
                        add_gap(
                            gap_id=f"suite-evidence-validate-{binding_name.replace('_', '-')}-drift-{row.get('evidence_id')}",
                            classification="stale",
                            failure_kind="head_or_pr_drift",
                            source_locator=row_locator,
                            impact=f"merge-ready cannot consume present evidence whose {binding_name} binding does not match the current execution head",
                            remediation="Rerun or re-author the evidence against the current HEAD / PR head before merge-ready.",
                        )

                validation_digests = extract_binding_shas(
                    binding_text,
                    ("validation_summary_sha256", "validation_summary_digest", "validation_summary"),
                )
                if validation_digests and (
                    validation_summary_sha256 is None
                    or not any(binding_sha_matches(observed, validation_summary_sha256) for observed in validation_digests)
                ):
                    binding_drift = True
                    add_gap(
                        gap_id=f"suite-evidence-validate-validation-summary-drift-{row.get('evidence_id')}",
                        classification="stale",
                        failure_kind="stale_evidence",
                        source_locator=row_locator,
                        impact="merge-ready cannot consume present evidence whose validation summary binding is stale",
                        remediation="Refresh validation evidence and bind it to the current Latest Validation Summary digest.",
                    )

            if binding_drift:
                continue
            if freshness in {"stale", "conflict"}:
                add_gap(
                    gap_id=f"suite-evidence-validate-stale-{row.get('evidence_id')}",
                    classification="stale",
                    failure_kind="stale_evidence",
                    source_locator=row_locator,
                    impact="merge-ready cannot consume stale or conflicting evidence against the current execution object",
                    remediation="Refresh the cited evidence or bind it to the current HEAD, PR, review, and validation object before merge-ready.",
                )
            elif freshness == "missing":
                add_gap(
                    gap_id=f"suite-evidence-validate-missing-{row.get('evidence_id')}",
                    classification="missing",
                    failure_kind=(
                        "missing_fresh_verification_evidence"
                        if evidence_type == "fresh_verification_input"
                        else "missing_evidence_map"
                    ),
                    source_locator=row_locator,
                    impact="merge-ready cannot consume evidence rows marked missing",
                    remediation="Author the missing evidence source and update evidence-map freshness before validation.",
                    fallback=(
                        "loom suite evidence validate --target <repo> --item <item> --json"
                        if evidence_type == "fresh_verification_input"
                        else "loom suite evidence scaffold --target <repo> --item <item> --json"
                    ),
                )
            elif freshness == "present" and evidence_type in present_by_type:
                present_by_type[evidence_type].append(row)
                present_ids_by_type[evidence_type].add(str(row.get("evidence_id")))

    for evidence_type in ("behavior_evidence", "test_evidence"):
        if present_by_type[evidence_type]:
            continue
        add_gap(
            gap_id=f"suite-evidence-validate-missing-{evidence_type.replace('_', '-')}",
            classification="missing",
            failure_kind="missing_evidence_map",
            source_locator=evidence_locator,
            impact=f"merge-ready evidence validation requires a present {evidence_type} row",
            remediation=f"Author a present {evidence_type} row with source locator, binding, freshness, consumer boundary, and remediation direction.",
            fallback="loom suite evidence scaffold --target <repo> --item <item> --json",
        )

    fresh_rows = present_by_type["fresh_verification_input"]
    behavior_ids = present_ids_by_type["behavior_evidence"]
    test_ids = present_ids_by_type["test_evidence"]
    fresh_consumes_required = False
    for row in fresh_rows:
        consumes = str(row.get("consumes") or "")
        if any(evidence_id and evidence_id in consumes for evidence_id in behavior_ids) and any(
            evidence_id and evidence_id in consumes for evidence_id in test_ids
        ):
            fresh_consumes_required = True
            break
    if not fresh_rows or not fresh_consumes_required:
        add_gap(
            gap_id="suite-evidence-validate-missing-fresh-verification",
            classification="missing",
            failure_kind="missing_fresh_verification_evidence",
            source_locator=evidence_locator,
            impact="merge-ready cannot prove behavior and test evidence combine into a fresh verification input",
            remediation="Author a present fresh_verification_input row that consumes present behavior and test evidence ids for the current object.",
        )

    findings = [*blocking_gaps, *advisory_gaps]
    result = "block" if blocking_gaps else "pass"
    failed_layer = str(blocking_gaps[0].get("failed_layer") or "evidence_map") if blocking_gaps else None
    fail_closed_reason = str(blocking_gaps[0].get("failure_kind")) if blocking_gaps else None
    fallback_to = [str(blocking_gaps[0].get("fallback_to"))] if blocking_gaps else ["loom suite evidence inspect --target <repo> --item <item> --json"]
    summary = "Suite evidence validate found blocking evidence-map gaps." if blocking_gaps else "Suite evidence validate found present behavior, test, and fresh verification evidence."

    payload = {
        **inspect_payload,
        "required_evidence_types": list(SUITE_EVIDENCE_REQUIRED_TYPES),
        "consumed_contracts": list(SUITE_EVIDENCE_CONTRACT_LOCATORS),
        "missing_inputs": missing_inputs,
        "blocking_gaps": blocking_gaps,
        "advisory_gaps": advisory_gaps,
        "findings": findings,
        "failure_taxonomy": suite_failure_taxonomy_for_findings(findings),
        "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
        "freshness_context": {
            "head_sha": current_head,
            "validation_summary_sha256": validation_summary_sha256,
            "validation_summary_status": "present" if validation_summary else "missing",
        },
        "remediation_directions": [entry["remediation_direction"] for entry in findings],
    }
    return summary, result, payload, failed_layer, fail_closed_reason, fallback_to


def suite_carrier_path(target: Path, item: str | None) -> Path | None:
    return suite_artifact_paths(target, item).get("task-carrier", [None])[0]


def normalize_carrier_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9_]+", "", str(value or "").strip().lower().replace("-", "_").replace(" ", "_"))


def parse_task_carrier_rows(path: Path, target: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        header_cells = split_markdown_table_row(lines[index])
        if not header_cells or index + 1 >= len(lines):
            index += 1
            continue
        separator_cells = split_markdown_table_row(lines[index + 1])
        if not is_markdown_separator_row(separator_cells):
            index += 1
            continue

        headers = [normalize_table_header(cell) for cell in header_cells]
        if not ({"carrier_type", "carriertype"} & set(headers) or {"carrier_locator", "carrierlocator"} & set(headers)):
            index += 2
            continue

        index += 2
        while index < len(lines):
            cells = split_markdown_table_row(lines[index])
            if not cells or is_markdown_separator_row(cells):
                break
            mapped = {headers[cell_index]: cells[cell_index] for cell_index in range(min(len(headers), len(cells)))}
            carrier_locator = mapped.get("carrier_locator") or mapped.get("carrierlocator") or mapped.get("locator") or ""
            carrier_type = normalize_carrier_token(mapped.get("carrier_type") or mapped.get("carriertype") or mapped.get("type"))
            normalized_status = normalize_carrier_token(
                mapped.get("normalized_status") or mapped.get("normalizedstatus") or mapped.get("status")
            )
            relationship = normalize_carrier_token(mapped.get("relationship") or mapped.get("relation"))
            locator_exists = None
            if carrier_locator and is_repo_local_source_locator(carrier_locator, ""):
                carrier_path = (target / carrier_locator).resolve()
                try:
                    locator_exists = carrier_path.is_relative_to(target.resolve()) and carrier_path.exists()
                except OSError:
                    locator_exists = False
            rows.append(
                {
                    "carrier_type": carrier_type,
                    "carrier_locator": carrier_locator,
                    "source_value": mapped.get("source_value") or mapped.get("sourcevalue") or "",
                    "normalized_status": normalized_status,
                    "relationship": relationship,
                    "work_item_locator": mapped.get("work_item_locator") or mapped.get("workitemlocator") or "",
                    "breakdown_unit_locator": mapped.get("breakdown_unit_locator") or mapped.get("breakdownunitlocator") or "",
                    "spec_scenario_locator": mapped.get("spec_scenario_locator") or mapped.get("specscenariolocator") or "",
                    "plan_phase_locator": mapped.get("plan_phase_locator") or mapped.get("planphaselocator") or "",
                    "validation_strategy_locator": mapped.get("validation_strategy_locator") or mapped.get("validationstrategylocator") or "",
                    "provenance": mapped.get("provenance") or "",
                    "freshness_rule": mapped.get("freshness_rule") or mapped.get("freshnessrule") or "",
                    "locator": f"{repo_locator(path, target)}:{index + 1}",
                    "carrier_locator_exists": locator_exists,
                }
            )
            index += 1
        continue
    return rows


def suite_carrier_inspect_payload(target: Path, item: str) -> tuple[str, dict[str, Any]]:
    carrier_path = suite_carrier_path(target, item)
    carrier_locator = repo_locator(carrier_path, target) if carrier_path else f".loom/specs/{item}/task-carrier.md"
    status = "missing"
    rows: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    advisory_gaps: list[dict[str, Any]] = []

    if carrier_path is None:
        missing_inputs.append("task_carrier_locator")
    elif carrier_path.exists() and (carrier_path.is_symlink() or not carrier_path.is_file()):
        status = "invalid"
        missing_inputs.append(f"invalid_task_carrier:{carrier_locator}")
    elif carrier_path.exists():
        status = "present"
        rows = parse_task_carrier_rows(carrier_path, target)
        if not rows:
            missing_inputs.append(f"task_carrier_rows:{carrier_locator}")
    else:
        missing_inputs.append("task_carrier_locator")

    if missing_inputs:
        advisory_gaps.append(
            suite_validate_finding(
                gap_id="suite-carrier-inspect-missing-task-carrier",
                classification="missing",
                failure_kind="missing_task_carrier_locator",
                source_locator=carrier_locator,
                consumer_impact="inspect-only",
                remediation_direction="Author task-carrier rows before carrier readiness validation.",
                fallback_to="loom suite carrier validate --target <repo> --item <item> --json",
                surface="task_carrier",
                binding="suite-carrier-inspect",
            )
        )

    payload = {
        "task_carrier": {
            "locator": carrier_locator,
            "status": status,
            "row_count": len(rows),
        },
        "task_carrier_locator": carrier_locator if status == "present" else None,
        "rows": rows,
        "recognized_carrier_types": sorted(SUITE_CARRIER_TYPES),
        "normalized_status_values": sorted(SUITE_CARRIER_STATUS_VALUES),
        "relationship_values": sorted(SUITE_CARRIER_RELATIONSHIPS),
        "recognized_truth_signals": sorted(SUITE_CARRIER_TRUTH_SIGNALS),
        "consumed_contracts": list(SUITE_CARRIER_CONTRACT_LOCATORS),
        "truth_boundary": {
            "carrier_done_satisfies_work_item_done": False,
            "project_done_satisfies_work_item_done": False,
            "checklist_done_satisfies_evidence_or_gate": False,
        },
        "work_item_truth": {
            "work_item_locator": f".loom/work-items/{item}.md",
            "work_item_present": (target / ".loom" / "work-items" / f"{item}.md").is_file(),
            "recovery_locator": f".loom/progress/{item}.md",
            "recovery_present": (target / ".loom" / "progress" / f"{item}.md").is_file(),
        },
        "missing_inputs": missing_inputs,
        "advisory_gaps": advisory_gaps,
    }
    summary = "Suite carrier inspect found task-carrier rows." if status == "present" else "Suite carrier inspect did not find usable task-carrier rows."
    return summary, payload


def suite_carrier_truth_claim_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field) or "")
        for field in (
            "carrier_locator",
            "source_value",
            "normalized_status",
            "provenance",
            "freshness_rule",
            "relationship",
        )
    ).lower()


def read_markdown_bullet_field(path: Path, field: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    prefix = f"- {field}:"
    for line in lines:
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return ""


def suite_carrier_work_item_truth(target: Path, item: str) -> dict[str, Any]:
    recovery_path = target / ".loom" / "progress" / f"{item}.md"
    checkpoint = normalize_carrier_token(read_markdown_bullet_field(recovery_path, "Current Checkpoint"))
    return {
        "work_item_locator": f".loom/work-items/{item}.md",
        "work_item_present": (target / ".loom" / "work-items" / f"{item}.md").is_file(),
        "recovery_locator": f".loom/progress/{item}.md",
        "recovery_present": recovery_path.is_file(),
        "recovery_checkpoint": checkpoint or None,
        "recovery_terminal": checkpoint in SUITE_CARRIER_TERMINAL_CHECKPOINTS,
    }


def suite_carrier_signal_set(row: dict[str, Any]) -> set[str]:
    text = suite_carrier_truth_claim_text(row)
    carrier_type = str(row.get("carrier_type") or "")
    status = str(row.get("normalized_status") or "")
    signals: set[str] = set()
    if status == "done":
        signals.add("carrier_done")
    if carrier_type == "github_project_item" and (status == "done" or re.search(r"\b(project\s+)?done\b", text)):
        signals.add("project_done")
    if carrier_type == "github_project_item" and re.search(r"\b(project\s+)?in[_ -]?progress\b", text):
        signals.add("project_in_progress")
    if carrier_type == "checklist_item" and re.search(r"\b(checked|checklist\s+checked)\b", text):
        signals.add("checklist_checked")
    if re.search(r"\bevidence\s+(missing|absent|not[_ -]?present)\b", text):
        signals.add("evidence_missing")
    if re.search(r"\b(issue\s+)?open\b", text):
        signals.add("issue_open")
    if re.search(r"\b(issue\s+)?closed\b", text):
        signals.add("issue_closed")
    if re.search(r"\b(pr|pull request)\s+open\b", text):
        signals.add("pr_open")
    if re.search(r"\b(pr|pull request)\s+merged\b", text):
        signals.add("pr_merged")
    if re.search(r"\bwork[_ -]?item\s+(open|in[_ -]?progress)\b", text):
        signals.add("work_item_open")
    if re.search(r"\bwork[_ -]?item\s+(done|closed|complete|completed)\b", text):
        signals.add("work_item_terminal")
    return signals


def suite_carrier_truth_signal_classifications(row: dict[str, Any], truth: dict[str, Any]) -> list[dict[str, Any]]:
    signals = suite_carrier_signal_set(row)
    row_locator = str(row.get("locator") or "")
    classifications: list[dict[str, Any]] = []

    def add_conflict(conflict_id: str, observed: list[str], impact: str, remediation: str) -> None:
        classifications.append(
            {
                "id": conflict_id,
                "classification": "conflict",
                "failure_kind": "carrier_truth_conflict",
                "source_locator": row_locator,
                "carrier_type": row.get("carrier_type"),
                "carrier_locator": row.get("carrier_locator"),
                "observed_signals": observed,
                "truth_owner": "work_item+recovery",
                "work_item_truth": truth,
                "consumer_impact": impact,
                "remediation_direction": remediation,
                "blocking": True,
            }
        )

    if "project_done" in signals and "issue_open" in signals:
        add_conflict(
            "project-done-issue-open",
            ["project_done", "issue_open"],
            "merge-ready cannot consume a carrier row whose Project mirror says Done while the issue mirror says open",
            "Reconcile the host mirrors or mark one signal stale before consuming the carrier row.",
        )
    if "pr_merged" in signals and "issue_open" in signals:
        add_conflict(
            "pr-merged-issue-open",
            ["pr_merged", "issue_open"],
            "merge-ready cannot consume PR merged as Work Item completion while the issue mirror remains open",
            "Use PR merged only as merge locator evidence and close the Work Item through closeout.",
        )
    if "issue_closed" in signals and "project_in_progress" in signals:
        add_conflict(
            "issue-closed-project-in-progress",
            ["issue_closed", "project_in_progress"],
            "merge-ready cannot consume an issue-closed carrier when the Project mirror remains in progress",
            "Reconcile Project status or treat the Project value as stale mirror evidence.",
        )
    if "checklist_checked" in signals and "evidence_missing" in signals:
        add_conflict(
            "checklist-checked-evidence-missing",
            ["checklist_checked", "evidence_missing"],
            "checklist checked cannot satisfy missing evidence or gate truth",
            "Keep checklist state as tracking-only and restore evidence-map / verification evidence.",
        )
    if (
        ("project_done" in signals or "issue_closed" in signals or "pr_merged" in signals or "work_item_terminal" in signals)
        and truth.get("recovery_present")
        and not truth.get("recovery_terminal")
        and ("work_item_terminal" in signals or "work_item_open" in signals)
    ):
        add_conflict(
            "host-terminal-recovery-active",
            sorted(signals & {"project_done", "issue_closed", "pr_merged", "work_item_open", "work_item_terminal"}),
            "host terminal signals conflict with active recovery truth",
            "Return completion truth to Work Item/recovery/closeout and keep host carrier state as a mirror.",
        )

    if not classifications:
        classifications.append(
            {
                "id": "no-blocking-host-carrier-conflict",
                "classification": "not_applicable",
                "failure_kind": None,
                "source_locator": row_locator,
                "carrier_type": row.get("carrier_type"),
                "carrier_locator": row.get("carrier_locator"),
                "observed_signals": sorted(signals),
                "truth_owner": "work_item+recovery",
                "work_item_truth": truth,
                "consumer_impact": "host carrier signals remain tracking-only",
                "remediation_direction": None,
                "blocking": False,
            }
        )
    return classifications


def suite_carrier_validate_payload(target: Path, item: str) -> tuple[str, str, dict[str, Any], str | None, str | None, list[str]]:
    item_error = suite_item_segment_error(item)
    if item_error:
        blocking_gaps = [
            suite_validate_finding(
                gap_id="suite-carrier-validate-invalid-item",
                classification="blocking",
                failure_kind="invalid_suite_item",
                source_locator=None,
                consumer_impact="carrier validation cannot bind an unsafe item segment",
                remediation_direction="Use a single repo-local Work Item id as the suite item.",
                fallback_to="loom suite carrier inspect --target <repo> --item <item> --json",
                surface="task_carrier",
                binding="suite-carrier-validate",
            )
        ]
        payload = {
            "task_carrier": {"locator": None, "status": "invalid", "row_count": 0},
            "rows": [],
            "consumed_contracts": list(SUITE_CARRIER_CONTRACT_LOCATORS),
            "missing_inputs": [item_error],
            "blocking_gaps": blocking_gaps,
            "advisory_gaps": [],
            "findings": blocking_gaps,
            "failure_taxonomy": suite_failure_taxonomy_for_findings(blocking_gaps),
            "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
            "remediation_directions": [blocking_gaps[0]["remediation_direction"]],
        }
        return (
            "Suite carrier validate failed closed before resolving task-carrier rows.",
            "block",
            payload,
            "task_carrier",
            "invalid_suite_item",
            ["loom suite carrier inspect --target <repo> --item <item> --json"],
        )

    inspect_summary, inspect_payload = suite_carrier_inspect_payload(target, item)
    rows = inspect_payload.get("rows", [])
    carrier_locator = inspect_payload.get("task_carrier", {}).get("locator")
    missing_inputs = list(inspect_payload.get("missing_inputs", []))
    blocking_gaps: list[dict[str, Any]] = []
    advisory_gaps: list[dict[str, Any]] = []
    work_item_truth = suite_carrier_work_item_truth(target, item)
    truth_signal_classifications: list[dict[str, Any]] = []

    def add_gap(
        *,
        gap_id: str,
        classification: str,
        failure_kind: str,
        source_locator: str | None,
        impact: str,
        remediation: str,
        fallback: str = "loom suite carrier validate --target <repo> --item <item> --json",
    ) -> None:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=gap_id,
                classification=classification,
                failure_kind=failure_kind,
                source_locator=source_locator,
                consumer_impact=impact,
                remediation_direction=remediation,
                fallback_to=fallback,
                surface="task_carrier",
                binding="suite-carrier-validate",
            )
        )

    if missing_inputs:
        add_gap(
            gap_id="suite-carrier-validate-missing-task-carrier",
            classification="missing",
            failure_kind="missing_task_carrier_locator",
            source_locator=carrier_locator,
            impact="merge-ready carrier validation cannot consume missing or unreadable task-carrier rows",
            remediation="Author task-carrier rows with locator, status, relationship, Work Item backlink, provenance, and freshness rule.",
        )

    required_fields = (
        "carrier_type",
        "carrier_locator",
        "source_value",
        "normalized_status",
        "relationship",
        "work_item_locator",
        "breakdown_unit_locator",
        "spec_scenario_locator",
        "plan_phase_locator",
        "validation_strategy_locator",
        "provenance",
        "freshness_rule",
    )
    primary_by_unit: dict[str, list[dict[str, Any]]] = {}
    item_number = item.split("-", 1)[1] if item.startswith("WI-") and "-" in item else item
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_locator = str(row.get("locator") or carrier_locator or "")
            missing_fields = [field for field in required_fields if is_empty_evidence_value(row.get(field))]
            if missing_fields:
                add_gap(
                    gap_id=f"suite-carrier-validate-missing-fields-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="merge-ready cannot consume carrier rows with incomplete locator, backlink, provenance, or freshness fields",
                    remediation=f"Fill task-carrier fields before validation; missing: {', '.join(missing_fields)}.",
                )
                continue

            if str(row.get("carrier_type")) not in SUITE_CARRIER_TYPES:
                add_gap(
                    gap_id=f"suite-carrier-validate-invalid-type-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot normalize an unknown carrier type",
                    remediation="Use github_issue, github_project_item, checklist_item, repo_tasks_md, external_tracker, or not_applicable.",
                )
            if str(row.get("normalized_status")) not in SUITE_CARRIER_STATUS_VALUES:
                add_gap(
                    gap_id=f"suite-carrier-validate-invalid-status-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot consume an unknown normalized status",
                    remediation="Use pending, in_progress, done, blocked, deferred, or not_applicable.",
                )
            if str(row.get("relationship")) not in SUITE_CARRIER_RELATIONSHIPS:
                add_gap(
                    gap_id=f"suite-carrier-validate-invalid-relationship-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot consume an unknown carrier relationship",
                    remediation="Use primary, mirror, evidence_locator, or not_applicable.",
                )

            work_item_locator = str(row.get("work_item_locator") or "")
            if item not in work_item_locator and item_number not in work_item_locator:
                add_gap(
                    gap_id=f"suite-carrier-validate-work-item-backlink-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier rows must backlink the owning Work Item before they can be consumed",
                    remediation=f"Bind the carrier row to {item} or its issue locator.",
                )

            if row.get("carrier_locator_exists") is False:
                add_gap(
                    gap_id=f"suite-carrier-validate-missing-locator-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot consume a repo-local carrier locator that is missing",
                    remediation="Restore the repo-local carrier locator or update the carrier row to a readable locator.",
                )

            if row.get("relationship") == "primary":
                primary_by_unit.setdefault(str(row.get("breakdown_unit_locator") or ""), []).append(row)

            truth_claim_text = suite_carrier_truth_claim_text(row)
            truth_replacement_markers = (
                "work_item_completed",
                "work item completed",
                "work item done",
                "closeout complete",
                "closeout completed",
                "merge-ready pass",
                "merge_ready_pass",
                "review pass",
                "review approved",
                "evidence present",
                "gate pass",
                "project done means completed",
                "checklist checked means evidence",
            )
            if any(marker in truth_claim_text for marker in truth_replacement_markers):
                add_gap(
                    gap_id=f"suite-carrier-validate-truth-conflict-{Path(row_locator).name}",
                    classification="conflict",
                    failure_kind="carrier_truth_conflict",
                    source_locator=row_locator,
                    impact="carrier status cannot replace Work Item, evidence, review, merge-ready, or closeout truth",
                    remediation="Demote carrier status to tracking-only language and return completion truth to Work Item/review/merge-ready/closeout carriers.",
                    fallback="loom suite carrier inspect --target <repo> --item <item> --json",
                )

            if row.get("normalized_status") == "deferred" and re.search(r"\b(done|completed|closed)\b", truth_claim_text):
                add_gap(
                    gap_id=f"suite-carrier-validate-deferred-completed-{Path(row_locator).name}",
                    classification="conflict",
                    failure_kind="deferred_as_completed",
                    source_locator=row_locator,
                    impact="deferred carrier status cannot satisfy completed truth",
                    remediation="Record an activation condition for the deferred carrier or move completion truth to the owning Work Item closeout.",
                    fallback="loom suite carrier inspect --target <repo> --item <item> --json",
                )

            row_classifications = suite_carrier_truth_signal_classifications(row, work_item_truth)
            truth_signal_classifications.extend(row_classifications)
            for classification in row_classifications:
                if not classification.get("blocking"):
                    continue
                add_gap(
                    gap_id=f"suite-carrier-validate-host-conflict-{classification['id']}-{Path(row_locator).name}",
                    classification="conflict",
                    failure_kind="carrier_truth_conflict",
                    source_locator=row_locator,
                    impact=str(classification.get("consumer_impact") or "host carrier signal conflict blocks merge-ready consumption"),
                    remediation=str(classification.get("remediation_direction") or "Reconcile host carrier mirrors before merge-ready."),
                    fallback="loom suite carrier inspect --target <repo> --item <item> --json",
                )

    for unit_locator, primary_rows in primary_by_unit.items():
        if unit_locator and len(primary_rows) > 1:
            add_gap(
                gap_id=f"suite-carrier-validate-primary-conflict-{Path(unit_locator).name}",
                classification="conflict",
                failure_kind="carrier_truth_conflict",
                source_locator=unit_locator,
                impact="a breakdown unit cannot have multiple primary carriers",
                remediation="Keep one primary carrier for the breakdown unit and mark the rest mirror or evidence_locator.",
                fallback="loom suite carrier inspect --target <repo> --item <item> --json",
            )

    findings = [*blocking_gaps, *advisory_gaps]
    result = "block" if blocking_gaps else "pass"
    failed_layer = str(blocking_gaps[0].get("failed_layer") or "task_carrier") if blocking_gaps else None
    fail_closed_reason = str(blocking_gaps[0].get("failure_kind")) if blocking_gaps else None
    fallback_to = [str(blocking_gaps[0].get("fallback_to"))] if blocking_gaps else ["loom suite carrier inspect --target <repo> --item <item> --json"]
    summary = "Suite carrier validate found blocking task-carrier gaps." if blocking_gaps else "Suite carrier validate found carrier locators, normalized status, relationships, and Work Item backlinks."

    payload = {
        **inspect_payload,
        "required_fields": list(required_fields),
        "consumed_contracts": list(SUITE_CARRIER_CONTRACT_LOCATORS),
        "recognized_truth_signals": sorted(SUITE_CARRIER_TRUTH_SIGNALS),
        "truth_signal_classifications": truth_signal_classifications,
        "host_signal_conflicts": [entry for entry in truth_signal_classifications if entry.get("blocking")],
        "work_item_truth": {**inspect_payload.get("work_item_truth", {}), **work_item_truth},
        "missing_inputs": missing_inputs,
        "blocking_gaps": blocking_gaps,
        "advisory_gaps": advisory_gaps,
        "findings": findings,
        "failure_taxonomy": suite_failure_taxonomy_for_findings(findings),
        "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
        "remediation_directions": [entry["remediation_direction"] for entry in findings],
    }
    return summary, result, payload, failed_layer, fail_closed_reason, fallback_to


def suite_validate_payload(target: Path, item: str) -> tuple[str, str, dict[str, Any], str | None, str | None, list[str]]:
    item_error = suite_item_segment_error(item)
    if item_error:
        blocking_gaps = [
            suite_validate_finding(
                gap_id="suite-validate-invalid-item",
                classification="blocking",
                failure_kind="invalid_suite_item",
                source_locator=None,
                consumer_impact="suite validation cannot bind an unsafe item segment",
                remediation_direction="Use a single repo-local Work Item id as the suite item.",
                fallback_to="loom suite inspect --target <repo> --item <item> --json",
            )
        ]
        payload = {
            "suite_path": "unknown",
            "suite_locator": None,
            "path_decision_locator": None,
            "artifact_inventory": [],
            "consumed_contracts": list(SUITE_VALIDATE_CONTRACT_LOCATORS),
            "missing_inputs": [item_error],
            "blocking_gaps": blocking_gaps,
            "advisory_gaps": [],
            "findings": blocking_gaps,
            "failure_taxonomy": suite_failure_taxonomy_for_findings(blocking_gaps),
            "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
            "remediation_directions": [blocking_gaps[0]["remediation_direction"]],
        }
        return (
            "Suite validate failed closed before resolving artifact paths.",
            "block",
            payload,
            "suite-input",
            "invalid_suite_item",
            ["loom suite inspect --target <repo> --item <item> --json"],
        )

    inspect_summary, inspect_payload = suite_inspect_payload(target, item)
    paths = suite_artifact_paths(target, item)
    suite_path = inspect_payload.get("suite_path", "unknown")
    missing_inputs = list(inspect_payload.get("missing_inputs", []))
    blocking_gaps: list[dict[str, Any]] = []
    advisory_gaps: list[dict[str, Any]] = []
    not_applicable_records, deferred_items = suite_applicability_records(paths, target)

    def add_missing_input(value: str) -> None:
        if value not in missing_inputs:
            missing_inputs.append(value)

    for missing in missing_inputs:
        if missing == "suite_path_decision":
            blocking_gaps.append(
                suite_validate_finding(
                    gap_id="suite-validate-missing-suite-path-decision",
                    classification="missing",
                    failure_kind="missing_suite_path_decision",
                    source_locator=None,
                    consumer_impact="spec review cannot determine whether the suite is full, minimal, or not_applicable",
                    remediation_direction="Author a suite path decision before validating readiness.",
                    fallback_to="loom suite inspect --target <repo> --item <item> --json",
                )
            )
        elif missing.startswith("invalid_suite_path_decision:") or missing.startswith("conflicting_suite_path_decision:"):
            locator = missing.split(":", 1)[1]
            blocking_gaps.append(
                suite_validate_finding(
                    gap_id=f"suite-validate-invalid-path-decision-{Path(locator).name}",
                    classification="blocking",
                    failure_kind="missing_suite_path_decision",
                    source_locator=locator,
                    consumer_impact="spec review cannot consume an invalid or conflicting suite path decision",
                    remediation_direction="Keep exactly one legal suite path decision: full, minimal, or not_applicable.",
                    fallback_to="loom suite inspect --target <repo> --item <item> --json",
                )
            )
        elif missing.startswith("required_artifact:"):
            locator = missing.split(":", 1)[1]
            blocking_gaps.append(
                suite_validate_finding(
                    gap_id=f"suite-validate-missing-{Path(locator).name}",
                    classification="missing",
                    failure_kind="missing_required_artifact",
                    source_locator=locator,
                    consumer_impact="spec review readiness cannot pass while a required suite artifact is absent",
                    remediation_direction="Run suite scaffold dry-run or author the missing repo-relative artifact.",
                    fallback_to="loom suite scaffold --target <repo> --item <item> --json",
                )
            )

    for record in not_applicable_records:
        if record.get("status") == "valid":
            continue
        locator = str(record.get("locator") or "")
        missing_fields = ", ".join(str(field) for field in record.get("missing_fields", [])) or "artifact binding"
        for field in record.get("missing_fields", []) or ["artifact_binding"]:
            add_missing_input(f"not_applicable_rationale:{locator}:block-{record.get('block')}:{field}")
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-invalid-not-applicable-{Path(locator).name or 'record'}-{record.get('block')}",
                classification="blocking",
                failure_kind="invalid_not_applicable_rationale",
                source_locator=locator or None,
                consumer_impact="spec review cannot treat not_applicable as ready without rationale, consumer boundary, and recheck condition",
                remediation_direction=(
                    "Author not_applicable with explicit artifact binding, rationale, consumer boundary, "
                    f"and recheck condition; missing: {missing_fields}."
                ),
                fallback_to="loom suite validate --target <repo> --item <item> --json",
            )
        )

    covered_not_applicable = suite_covered_artifacts(not_applicable_records)
    deferred_coverage = suite_covered_artifacts(
        [{**record, "status": "valid"} for record in deferred_items]
    )
    if suite_path == "minimal":
        missing_not_applicable = sorted(SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS - covered_not_applicable)
        for artifact in missing_not_applicable:
            if artifact in deferred_coverage:
                matching = next(
                    (
                        record
                        for record in deferred_items
                        if artifact in [str(entry) for entry in record.get("artifacts", [])]
                    ),
                    None,
                )
                blocking_gaps.append(
                    suite_validate_finding(
                        gap_id=f"suite-validate-deferred-as-not-applicable-{artifact.replace('.', '-')}",
                        classification="blocking",
                        failure_kind="deferred_as_completed",
                        source_locator=str(matching.get("locator")) if matching else None,
                        consumer_impact="minimal suite readiness cannot consume deferred full-path artifacts as completed not_applicable rationale",
                        remediation_direction="Record not_applicable rationale, consumer boundary, and recheck condition, or keep the suite out of ready state.",
                        fallback_to="loom suite validate --target <repo> --item <item> --json",
                    )
                )
            else:
                add_missing_input(f"not_applicable_rationale:{artifact}")
                blocking_gaps.append(
                    suite_validate_finding(
                        gap_id=f"suite-validate-missing-not-applicable-{artifact.replace('.', '-')}",
                        classification="missing",
                        failure_kind="invalid_not_applicable_rationale",
                        source_locator=inspect_payload.get("path_decision_locator"),
                        consumer_impact="minimal suite readiness cannot skip full-path artifacts without authored not_applicable rationale",
                        remediation_direction=(
                            f"Author not_applicable for {artifact} with rationale, consumer boundary, "
                            "and recheck condition."
                        ),
                        fallback_to="loom suite validate --target <repo> --item <item> --json",
                    )
                )
    elif suite_path == "not_applicable" and "suite" not in covered_not_applicable:
        add_missing_input("not_applicable_rationale:suite")
        blocking_gaps.append(
            suite_validate_finding(
                gap_id="suite-validate-missing-suite-not-applicable-rationale",
                classification="missing",
                failure_kind="invalid_not_applicable_rationale",
                source_locator=inspect_payload.get("path_decision_locator"),
                consumer_impact="spec review cannot consume a not_applicable suite path without authored rationale",
                remediation_direction="Author suite-level not_applicable with rationale, consumer boundary, and recheck condition.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
            )
        )

    spec_plan_mapping = {
        "spec_locator": inspect_payload.get("spec_locator"),
        "plan_locator": inspect_payload.get("plan_locator"),
        "required_scenarios": [],
        "required_acceptance": [],
        "mapped_scenarios": [],
        "mapped_acceptance": [],
        "missing_scenarios": [],
        "missing_acceptance": [],
    }
    if suite_path in {"full", "minimal"}:
        spec_plan_mapping, mapping_gaps = suite_spec_plan_mapping(paths, target)
        blocking_gaps.extend(mapping_gaps)

    artifact_inventory = {
        entry.get("artifact"): entry
        for entry in inspect_payload.get("artifact_inventory", [])
        if isinstance(entry, dict)
    }
    for artifact in SUITE_VALIDATE_ADVISORY_ARTIFACTS.get(str(suite_path), ()):
        if artifact_inventory.get(artifact, {}).get("status") == "present":
            continue
        locator_field = "task_carrier_locators" if artifact == "task-carrier" else artifact.replace("-", "_").removesuffix(".md") + "_locator"
        locator_value = inspect_payload.get(locator_field)
        if locator_value:
            continue
        expected_locator = f".loom/specs/{item}/{artifact if artifact != 'task-carrier' else 'task-carrier.md'}"
        advisory_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-advisory-missing-{artifact.replace('.', '-').replace('_', '-')}",
                classification="advisory",
                failure_kind="missing_optional_suite_artifact",
                source_locator=expected_locator,
                consumer_impact="core suite validation can continue, but later evidence/carrier checks may require this artifact",
                remediation_direction="Leave for the owning evidence, consistency, or carrier validation Work Item unless the current consumer requires it.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
            )
        )

    findings = [*blocking_gaps, *advisory_gaps]
    result = "pass"
    failed_layer: str | None = None
    fail_closed_reason: str | None = None
    fallback_to = ["loom suite inspect --target <repo> --item <item> --json"]
    if blocking_gaps:
        result = "block"
        failed_layer = str(blocking_gaps[0].get("surface") or "suite")
        fail_closed_reason = blocking_gaps[0]["failure_kind"]
        fallback_to = [blocking_gaps[0]["fallback_to"]]
        summary = "Suite validate found blocking readiness gaps."
    elif suite_path == "not_applicable":
        result = "not_applicable"
        summary = "Suite validate found a not_applicable suite path decision."
    elif advisory_gaps:
        result = "advisory"
        summary = "Suite validate found no core blocking gaps, but later suite checks still have advisory gaps."
    else:
        summary = {
            "full": "Suite validate found a full suite path with core required artifacts present.",
            "minimal": "Suite validate found a minimal suite path with core required artifacts present.",
        }.get(str(suite_path), inspect_summary)

    payload = {
        **inspect_payload,
        "not_applicable_rationale": not_applicable_records,
        "deferred_items": deferred_items,
        "spec_plan_mapping": spec_plan_mapping,
        "consumed_contracts": list(SUITE_VALIDATE_CONTRACT_LOCATORS),
        "missing_inputs": missing_inputs,
        "blocking_gaps": blocking_gaps,
        "advisory_gaps": advisory_gaps,
        "findings": findings,
        "failure_taxonomy": suite_failure_taxonomy_for_findings(findings),
        "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
        "remediation_directions": [entry["remediation_direction"] for entry in findings],
    }
    return summary, result, payload, failed_layer, fail_closed_reason, fallback_to


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
    if action not in {"inspect", "scaffold", "validate", "evidence", "carrier"}:
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

    if action == "carrier":
        if len(argv) < 2:
            return emit(
                output(
                    "suite carrier",
                    "block",
                    summary="Suite carrier command requires inspect or validate.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing suite carrier action",
                    fallback_to=["loom suite carrier inspect --target <repo> --item <item> --json"],
                )
            )
        carrier_action = argv[1]
        if carrier_action not in {"inspect", "validate"}:
            return emit(
                output(
                    f"suite carrier {carrier_action}",
                    "block",
                    summary="Unsupported suite carrier action.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason=f"unsupported suite carrier action: {carrier_action}",
                    fallback_to=["loom suite carrier inspect --target <repo> --item <item> --json"],
                )
            )
        parser = argparse.ArgumentParser(prog=f"loom suite carrier {carrier_action}")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[2:])
        command_name = f"suite carrier {carrier_action}"
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target(command_name, target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    command_name,
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary=f"Suite carrier {carrier_action} requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    missing_inputs=["missing_work_item"],
                    blocking_gaps=[],
                    advisory_gaps=[],
                    fallback_to=[f"loom {command_name} --target <repo> --item <item> --json"],
                )
            )
        if carrier_action == "inspect":
            summary, carrier_payload = suite_carrier_inspect_payload(target, args.item)
            return emit(
                output(
                    command_name,
                    "pass",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=False,
                    missing_inputs=carrier_payload.get("missing_inputs", []),
                    advisory_gaps=carrier_payload.get("advisory_gaps", []),
                    payload=carrier_payload,
                )
            )

        summary, result, carrier_payload, failed_layer, fail_closed_reason, fallback_to = suite_carrier_validate_payload(target, args.item)
        return emit(
            output(
                command_name,
                result,
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=False,
                failed_layer=failed_layer,
                fail_closed_reason=fail_closed_reason,
                missing_inputs=carrier_payload.get("missing_inputs", []),
                blocking_gaps=carrier_payload.get("blocking_gaps", []),
                advisory_gaps=carrier_payload.get("advisory_gaps", []),
                fallback_to=fallback_to,
                payload=carrier_payload,
            )
        )

    if action == "evidence":
        if len(argv) < 2:
            return emit(
                output(
                    "suite evidence",
                    "block",
                    summary="Suite evidence command requires inspect, scaffold, or validate.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing suite evidence action",
                    fallback_to=["loom suite evidence inspect --target <repo> --item <item> --json"],
                )
            )
        evidence_action = argv[1]
        if evidence_action not in {"inspect", "scaffold", "validate"}:
            return emit(
                output(
                    f"suite evidence {evidence_action}",
                    "block",
                    summary="Unsupported suite evidence action.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason=f"unsupported suite evidence action: {evidence_action}",
                    fallback_to=["loom suite evidence inspect --target <repo> --item <item> --json"],
                )
            )
        parser = argparse.ArgumentParser(prog=f"loom suite evidence {evidence_action}")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        if evidence_action == "scaffold":
            parser.add_argument("--apply", action="store_true")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[2:])
        command_name = f"suite evidence {evidence_action}"
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target(command_name, target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    command_name,
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary=f"Suite evidence {evidence_action} requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    missing_inputs=["missing_work_item"],
                    blocking_gaps=[],
                    advisory_gaps=[],
                    fallback_to=[f"loom {command_name} --target <repo> --item <item> --json"],
                )
            )
        if evidence_action == "scaffold":
            summary, scaffold_payload, fail_closed_reason = suite_evidence_scaffold_payload(target, args.item, apply=args.apply)
            if fail_closed_reason:
                return emit(
                    output(
                        command_name,
                        "block",
                        target=str(target),
                        item_id=args.item,
                        summary=summary,
                        mutates=False,
                        failed_layer="suite-input",
                        fail_closed_reason=fail_closed_reason,
                        missing_inputs=scaffold_payload.get("missing_inputs", []),
                        advisory_gaps=scaffold_payload.get("advisory_gaps", []),
                        fallback_to=["loom suite evidence scaffold --target <repo> --item <item> --json"],
                        payload=scaffold_payload,
                    )
                )
            return emit(
                output(
                    command_name,
                    "pass",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=bool(scaffold_payload.get("created_locators")),
                    payload=scaffold_payload,
                )
            )
        if evidence_action == "inspect":
            summary, evidence_payload = suite_evidence_inspect_payload(target, args.item)
            return emit(
                output(
                    command_name,
                    "pass",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=False,
                    missing_inputs=evidence_payload.get("missing_inputs", []),
                    advisory_gaps=evidence_payload.get("advisory_gaps", []),
                    payload=evidence_payload,
                )
            )

        summary, result, evidence_payload, failed_layer, fail_closed_reason, fallback_to = suite_evidence_validate_payload(target, args.item)
        return emit(
            output(
                command_name,
                result,
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=False,
                failed_layer=failed_layer,
                fail_closed_reason=fail_closed_reason,
                missing_inputs=evidence_payload.get("missing_inputs", []),
                blocking_gaps=evidence_payload.get("blocking_gaps", []),
                advisory_gaps=evidence_payload.get("advisory_gaps", []),
                fallback_to=fallback_to,
                payload=evidence_payload,
            )
        )

    if action == "validate":
        parser = argparse.ArgumentParser(prog="loom suite validate")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[1:])
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target("suite validate", target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    "suite validate",
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary="Suite validate requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    missing_inputs=["missing_work_item"],
                    blocking_gaps=[],
                    advisory_gaps=[],
                    fallback_to=["loom suite validate --target <repo> --item <item> --json"],
                )
            )
        summary, result, validate_payload, failed_layer, fail_closed_reason, fallback_to = suite_validate_payload(target, args.item)
        return emit(
            output(
                "suite validate",
                result,
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=False,
                failed_layer=failed_layer,
                fail_closed_reason=fail_closed_reason,
                missing_inputs=validate_payload.get("missing_inputs", []),
                blocking_gaps=validate_payload.get("blocking_gaps", []),
                advisory_gaps=validate_payload.get("advisory_gaps", []),
                fallback_to=fallback_to,
                payload=validate_payload,
            )
        )

    if action == "scaffold":
        parser = argparse.ArgumentParser(prog="loom suite scaffold")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        parser.add_argument("--suite", choices=("minimal", "full"), default="minimal")
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[1:])
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target("suite scaffold", target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    "suite scaffold",
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary="Suite scaffold requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    fallback_to=["loom suite scaffold --target <repo> --item <item> --json"],
                )
            )
        summary, scaffold_payload, fail_closed_reason = suite_scaffold_payload(target, args.item, args.suite, apply=args.apply)
        if fail_closed_reason:
            return emit(
                output(
                    "suite scaffold",
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason=fail_closed_reason,
                    fallback_to=["loom suite scaffold --target <repo> --item <item> --json"],
                    payload=scaffold_payload,
                )
            )
        return emit(
            output(
                "suite scaffold",
                "pass",
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=bool(scaffold_payload.get("created_locators")),
                payload=scaffold_payload,
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

    summary, suite_payload = suite_inspect_payload(target, args.item)
    payload = output(
        "suite inspect",
        "pass",
        target=str(target),
        item_id=args.item,
        summary=summary,
        mutates=False,
        payload=suite_payload,
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
    if command == "carrier" or command.startswith("carrier "):
        carrier_args = command.split()[1:] + forwarded if command.startswith("carrier ") else forwarded
        return handle_carrier(carrier_args)
    if command == "host" or command.startswith("host "):
        host_args = command.split()[1:] + forwarded if command.startswith("host ") else forwarded
        return handle_host(host_args)
    if command == "skills" or command.startswith("skills "):
        skills_args = command.split()[1:] + forwarded if command.startswith("skills ") else forwarded
        return handle_skills(skills_args)
    if command == "suite" or command.startswith("suite "):
        suite_args = command.split()[1:] + forwarded if command.startswith("suite ") else forwarded
        return handle_suite(suite_args)
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
    if command == "closeout queue status":
        return handle_closeout_queue_status(forwarded)
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
