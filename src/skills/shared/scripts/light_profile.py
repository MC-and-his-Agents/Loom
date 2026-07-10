#!/usr/bin/env python3
"""Read-only light-governance carrier invariant and migration plan."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


sys.dont_write_bytecode = True

SCHEMA = "loom-light-profile-migration-plan/v1"
INSTALLED_STATE_SCHEMA = "loom-installed-state/v2"
STATE_FILENAMES = (
    ".loom/installed-state.json",
    ".loom/installed-state.v2.json",
    ".loom/installed-state/installed-state.json",
)
LIGHT_PROFILES = frozenset(("light-governance", "attach-only"))
FORBIDDEN_CARRIERS = (
    (".loom/bootstrap/", "legacy_bootstrap"),
    (".loom/status/", "current_pointer"),
    (".loom/work-items/", "execution_carrier"),
    (".loom/progress/", "execution_carrier"),
    (".loom/specs/", "execution_carrier"),
    (".loom/stories/", "execution_carrier"),
    (".loom/reviews/", "execution_carrier"),
    (".loom/shadow/", "shadow_evidence"),
    (".loom/bin/", "runtime_payload"),
    (".loom/runtime/", "runtime_cache"),
    (".loom/tmp/", "runtime_cache"),
)
ALLOWED_BOOTSTRAP_LOCATORS = {".loom/bootstrap/init-result.json"}
DECLARATION_LOCATORS = (".loom/bootstrap/init-result.json", ".loom/bootstrap/manifest.json")


def resolve_target(raw_target: str) -> Path:
    target = Path(raw_target).expanduser()
    return target.resolve() if target.is_absolute() else (Path.cwd() / target).resolve()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def installed_state(target: Path) -> tuple[str, dict[str, Any] | None, str | None]:
    for locator in STATE_FILENAMES:
        path = target / locator
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            return locator, None, "installed-state must be a regular JSON file inside the target"
        payload = read_json(path)
        if payload is None or payload.get("schema_version") != INSTALLED_STATE_SCHEMA:
            return locator, None, "installed-state is unreadable or has an unsupported schema"
        return locator, payload, None
    return ".loom/installed-state.json", None, "installed-state is missing"


def observed_paths(target: Path) -> tuple[dict[str, str], str | None]:
    observed: dict[str, str] = {}
    for source, args in (
        ("tracked", ["git", "ls-files", "--cached", "-z"]),
        ("untracked", ["git", "ls-files", "--others", "--exclude-standard", "-z"]),
        ("ignored", ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"]),
    ):
        completed = subprocess.run(
            args,
            cwd=target,
            check=False,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if completed.returncode != 0:
            return {}, "target is not a readable Git working tree"
        for raw_path in completed.stdout.split(b"\0"):
            if raw_path:
                observed.setdefault(raw_path.decode("utf-8"), source)
    return dict(sorted(observed.items())), None


def forbidden_kind(path: str) -> str | None:
    if path in ALLOWED_BOOTSTRAP_LOCATORS:
        return None
    for prefix, kind in FORBIDDEN_CARRIERS:
        if path.startswith(prefix):
            return kind
    return None


def forbidden_violations(paths: dict[str, str]) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path, source in paths.items():
        kind = forbidden_kind(path)
        if kind is not None:
            violations.append(
                {
                    "locator": path,
                    "kind": kind,
                    "source": source,
                    "disposition": "remove_in_profile_migration_pr",
                }
            )
    return violations


def has_absolute_filesystem_path(value: object) -> bool:
    """Reject any portable-metadata value that is an absolute POSIX or Windows path."""

    if isinstance(value, str):
        return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()
    if isinstance(value, dict):
        return any(has_absolute_filesystem_path(entry) for entry in value.values())
    if isinstance(value, list):
        return any(has_absolute_filesystem_path(entry) for entry in value)
    return False


def metadata_violations(target: Path, paths: dict[str, str]) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in (*STATE_FILENAMES, *DECLARATION_LOCATORS):
        if path not in paths:
            continue
        source = paths[path]
        candidate = target / path
        if candidate.is_symlink() or not candidate.is_file():
            violations.append(
                {
                    "locator": path,
                    "kind": "unsafe_metadata_locator",
                    "source": source,
                    "disposition": "remove_in_profile_migration_pr",
                }
            )
            continue
        payload = read_json(candidate)
        if payload is None:
            if path in DECLARATION_LOCATORS:
                violations.append(
                    {
                        "locator": path,
                        "kind": "invalid_legacy_metadata",
                        "source": source,
                        "disposition": "remove_in_profile_migration_pr",
                    }
                )
            continue
        if has_absolute_filesystem_path(payload):
            violations.append(
                {
                    "locator": path,
                    "kind": "absolute_workstation_path",
                    "source": source,
                    "disposition": "remove_in_profile_migration_pr",
                }
            )
        if path not in DECLARATION_LOCATORS:
            continue
        for field in ("initial_artifacts", "planned_writes"):
            entries = payload.get(field)
            if not isinstance(entries, list):
                continue
            for entry in entries:
                declared = entry.get("path") if isinstance(entry, dict) else None
                if not isinstance(declared, str):
                    continue
                kind = forbidden_kind(declared)
                if kind is not None:
                    violations.append(
                        {
                            "locator": f"{path}:{field}:{declared}",
                            "kind": "forbidden_declaration",
                            "source": source,
                            "disposition": "remove_in_profile_migration_pr",
                        }
                    )
    return violations


def migration_actions(
    violations: list[dict[str, str]], state_error: str | None, profile: str | None
) -> list[dict[str, Any]]:
    if not violations and state_error is None:
        return []
    return [
        {
            "id": "gate_enabler_pr",
            "status": "required",
            "mutates": False,
            "scope": "repository-scoped advisory delivery-gate PR",
            "preserve": [".loom/installed-state.json", ".loom/companion/**", ".github/PULL_REQUEST_TEMPLATE.md", ".github/workflows/**"],
            "host_readback": {"authority": "GitHub check run", "expect": "new delivery gate passes before required-set replacement"},
        },
        {
            "id": "required_set_host_readback",
            "status": "pending_after_gate_enabler",
            "mutates": False,
            "host_mutation_authority": "repository administrator",
            "atomic": False,
            "readback": {
                "authority": "GitHub branch protection and rulesets",
                "expect": "new delivery-gate identity is required and legacy required checks are absent",
            },
        },
        {
            "id": "profile_migration_pr",
            "status": "pending_after_required_set_readback",
            "mutates": False,
            "scope": "one repository-scoped profile-migration PR",
            "remove": violations,
            "installed_state": (
                f"rewrite to metadata-only {profile}" if state_error else f"retain validated metadata-only {profile} state"
            ),
            "post_merge_readback": [
                {"authority": "GitHub main tree", "expect_absent": [prefix for prefix, _kind in FORBIDDEN_CARRIERS]},
                {"authority": "GitHub changed paths", "expect": "old branches cannot reintroduce forbidden light-profile locators"},
            ],
        },
    ]


def plan_payload(target: Path) -> dict[str, Any]:
    locator, state, state_error = installed_state(target)
    repo_payload = state.get("repo_payload") if isinstance(state, dict) else {}
    profile = repo_payload.get("adoption_mode") if isinstance(repo_payload, dict) else None
    if state_error is None and profile in LIGHT_PROFILES and repo_payload.get("mode") != "metadata-only":
        state_error = f"{profile} installed-state must use metadata-only repository payload"
    if state_error is None and profile not in LIGHT_PROFILES:
        return {
            "schema_version": SCHEMA,
            "command": "profile light-migration-plan",
            "operation": "plan",
            "result": "pass",
            "mutates": False,
            "host_mutations": False,
            "carrier_repair_actions": [],
            "applicable": False,
            "installed_state": {"locator": locator, "adoption_mode": profile},
            "primary_cause": {
                "id": "not_applicable",
                "domain": "light_profile",
                "summary": "target does not declare a light-profile adoption",
            },
            "migration": {"status": "not_applicable", "actions": []},
        }

    paths, git_error = observed_paths(target)
    if git_error:
        return {
            "schema_version": SCHEMA,
            "command": "profile light-migration-plan",
            "operation": "plan",
            "result": "block",
            "mutates": False,
            "host_mutations": False,
            "carrier_repair_actions": [],
            "applicable": True,
            "installed_state": {"locator": locator, "adoption_mode": profile},
            "legacy_gate_blocker": True,
            "violations": [],
            "migration": {"status": "blocked_tree_read", "reentrant": True, "actions": []},
            "primary_cause": {
                "id": "light_profile_tree_unreadable",
                "domain": "git_tree",
                "summary": git_error,
            },
            "failed_layer": "light-profile-tree",
            "fail_closed_reason": git_error,
        }

    violations = [*forbidden_violations(paths), *metadata_violations(target, paths)]
    violations.sort(key=lambda item: (item["locator"], item["kind"], item["source"]))
    migration = migration_actions(violations, state_error, profile)
    passed = not violations and state_error is None
    primary_id = "passed" if passed else "light_profile_forbidden_carrier" if violations else "light_profile_state_unreadable"
    return {
        "schema_version": SCHEMA,
        "command": "profile light-migration-plan",
        "operation": "plan",
        "result": "pass" if passed else "block",
        "mutates": False,
        "host_mutations": False,
        "carrier_repair_actions": [],
        "applicable": True,
        "installed_state": {"locator": locator, "status": "valid" if state_error is None else "invalid", "adoption_mode": profile},
        "observed_tree": {
            "sources": {source: sum(1 for value in paths.values() if value == source) for source in ("tracked", "untracked", "ignored")},
            "file_count": len(paths),
        },
        "primary_cause": {
            "id": primary_id,
            "domain": "light_profile" if primary_id != "light_profile_state_unreadable" else "installed_state",
            "summary": (
                "observed tree satisfies the light-profile carrier invariant"
                if passed
                else "observed Loom execution carriers conflict with light-profile adoption"
                if violations
                else str(state_error)
            ),
        },
        "legacy_gate_blocker": not passed,
        "violations": violations,
        "migration": {
            "status": "not_required" if passed else "profile_migration_required",
            "reentrant": True,
            "actions": migration,
        },
        "prohibited_actions": [
            "carrier repair",
            "carrier closeout-sync",
            "authored head repair",
            "closeout PR",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("plan",))
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = plan_payload(resolve_target(args.target))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
