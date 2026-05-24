#!/usr/bin/env python3
"""CLI-first Loom control-plane entry.

The command surface is intentionally broader than the implementation surface.
Commands that are not implemented in this phase fail closed with a structured
JSON block instead of silently falling back to legacy wrappers.
"""

from __future__ import annotations

import argparse
import json
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
    {"command": "detect", "domain": "diagnostics", "status": "reserved", "json": True},
    {"command": "doctor", "domain": "diagnostics", "status": "reserved", "json": True},
    {"command": "repair plan", "domain": "repair", "status": "reserved", "json": True},
    {"command": "repair apply", "domain": "repair", "status": "reserved", "json": True},
    {"command": "install", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "upgrade-plan", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "upgrade", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "rollback", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "verify", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "init", "domain": "scenario", "status": "delegated", "json": "mixed"},
    {"command": "adopt", "domain": "scenario", "status": "delegated", "json": "mixed"},
    {"command": "route", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "status", "domain": "harness", "status": "delegated", "json": True},
    {"command": "fact-chain", "domain": "harness", "status": "delegated", "json": True},
    {"command": "profile status", "domain": "profile", "status": "reserved", "json": True},
    {"command": "profile upgrade-plan", "domain": "profile", "status": "reserved", "json": True},
    {"command": "profile upgrade", "domain": "profile", "status": "reserved", "json": True},
    {"command": "story", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "spec", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "plan", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "build", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "pre-review", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "spec-review", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "review", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "merge-ready", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "closeout", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "resume", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "handoff", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "retire", "domain": "scenario", "status": "reserved", "json": True},
    {"command": "checkpoint admission", "domain": "gate", "status": "reserved", "json": True},
    {"command": "checkpoint build", "domain": "gate", "status": "reserved", "json": True},
    {"command": "checkpoint merge", "domain": "gate", "status": "reserved", "json": True},
    {"command": "gate pre-review", "domain": "gate", "status": "reserved", "json": True},
    {"command": "gate spec-review", "domain": "gate", "status": "reserved", "json": True},
    {"command": "gate review", "domain": "gate", "status": "reserved", "json": True},
    {"command": "gate pr", "domain": "gate", "status": "reserved", "json": True},
    {"command": "gate merge", "domain": "gate", "status": "reserved", "json": True},
    {"command": "gate closeout", "domain": "gate", "status": "reserved", "json": True},
    {"command": "workspace create", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "workspace locate", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "workspace check", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "workspace retire", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "issue inspect", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "issue bind", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "issue reconcile", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "project status", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "project reconcile", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "pr inspect", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "pr metadata-preflight", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "pr gate", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "merge check", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "merge run", "domain": "delivery", "status": "reserved", "json": True},
    {"command": "reconcile", "domain": "host-control", "status": "reserved", "json": True},
    {"command": "host list", "domain": "host", "status": "reserved", "json": True},
    {"command": "host doctor", "domain": "host", "status": "reserved", "json": True},
    {"command": "host install", "domain": "host", "status": "reserved", "json": True},
    {"command": "host verify", "domain": "host", "status": "reserved", "json": True},
    {"command": "host upgrade", "domain": "host", "status": "reserved", "json": True},
    {"command": "host remove", "domain": "host", "status": "reserved", "json": True},
    {"command": "skills list", "domain": "skills", "status": "reserved", "json": True},
    {"command": "skills generate", "domain": "skills", "status": "reserved", "json": True},
    {"command": "skills sync", "domain": "skills", "status": "reserved", "json": True},
    {"command": "skills check", "domain": "skills", "status": "reserved", "json": True},
    {"command": "skills doctor", "domain": "skills", "status": "reserved", "json": True},
    {"command": "skills package", "domain": "skills", "status": "reserved", "json": True},
    {"command": "skills release-check", "domain": "skills", "status": "reserved", "json": True},
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
        "delegated compatibility commands:\n"
        "  init, adopt, route, status, fact-chain, resume, spec-review, review, merge-ready, check\n\n"
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
        if candidate in COMMAND_INDEX or candidate in COMMAND_ROUTES or candidate in {"flow", "check"}:
            return candidate, argv[length:]
    return argv[0], argv[1:]


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
    if command == "installed-state":
        return handle_installed_state(forwarded)
    if command.startswith("installed-state "):
        return handle_installed_state(command.split()[1:] + forwarded)
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
