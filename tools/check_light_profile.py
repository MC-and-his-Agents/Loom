#!/usr/bin/env python3
"""Targeted contract checks for the read-only light-profile migration plan."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "light_profile.py"
FIXTURES = ROOT / "tools" / "fixtures" / "light-profile" / "fixtures.json"
LOOM = ROOT / "tools" / "loom.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("light_profile", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("light-profile evaluator is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def commit_all(target: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def materialize_case(root: Path, fixture: dict[str, Any]) -> Path:
    target = root / str(fixture["id"])
    target.mkdir()
    subprocess.run(["git", "init"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=target, check=True)
    if not fixture.get("without_installed_state"):
        state = {
            "schema_version": "loom-installed-state/v2",
            "repo_payload": {
                "mode": "metadata-only",
                "adoption_mode": fixture["adoption_mode"],
            },
            "contract": {"minimum_loom_version": "v0.29.0"},
        }
        state["repo_payload"].update(fixture.get("repo_payload_extra", {}))
        state.update(fixture.get("installed_state_extra", {}))
        write_json(target / ".loom" / "installed-state.json", state)
    for relative, content in fixture.get("tracked_files", {}).items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if fixture.get("ignored_files"):
        (target / ".gitignore").write_text(".loom/tmp/\n", encoding="utf-8")
    commit_all(target)
    for collection_name in ("untracked_files", "ignored_files"):
        for relative, content in fixture.get(collection_name, {}).items():
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return target


def assert_case(evaluator: Any, root: Path, fixture: dict[str, Any]) -> None:
    target = materialize_case(root, fixture)
    status_before = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=target, check=True, text=True, stdout=subprocess.PIPE).stdout
    first = evaluator.plan_payload(target)
    second = evaluator.plan_payload(target)
    status_after = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=target, check=True, text=True, stdout=subprocess.PIPE).stdout
    if status_before != status_after:
        raise AssertionError(f"{fixture['id']} plan wrote to the target")
    if first != second:
        raise AssertionError(f"{fixture['id']} plan is not reentrant")
    expected = fixture["expected"]
    cause = first.get("primary_cause", {})
    if first.get("result") != expected["result"] or cause.get("id") != expected["primary_cause"]:
        raise AssertionError(f"{fixture['id']} result drifted: {first}")
    if bool(first.get("legacy_gate_blocker")) != expected["legacy_gate_blocker"]:
        raise AssertionError(f"{fixture['id']} legacy blocker drifted: {first}")
    if len(first.get("violations", [])) != expected["violation_count"]:
        raise AssertionError(f"{fixture['id']} violation count drifted: {first}")
    if first.get("mutates") is not False or first.get("host_mutations") is not False or first.get("carrier_repair_actions") != []:
        raise AssertionError(f"{fixture['id']} plan is not read-only: {first}")
    for action in first.get("migration", {}).get("actions", []):
        if action.get("mutates") is not False or "repair" in str(action.get("id", "")) or "closeout" in str(action.get("id", "")):
            raise AssertionError(f"{fixture['id']} proposed a forbidden remediation: {action}")

    if fixture["id"] == "heavy-tree":
        paths = {entry.get("locator") for entry in first.get("violations", [])}
        expected_files = {
            path
            for path in fixture["tracked_files"]
            if evaluator.forbidden_kind(path) is not None
        }
        if not expected_files.issubset(paths) or not any(":initial_artifacts:.loom/status/current.md" in str(path) for path in paths):
            raise AssertionError(f"heavy-tree fixture missed forbidden paths: {paths}")
        action_ids = [action.get("id") for action in first.get("migration", {}).get("actions", [])]
        if action_ids != ["gate_enabler_pr", "required_set_host_readback", "profile_migration_pr"]:
            raise AssertionError(f"heavy-tree migration order drifted: {action_ids}")
        actions = first["migration"]["actions"]
        if actions[1].get("atomic") is not False or actions[2].get("post_merge_readback", [])[0].get("authority") != "GitHub main tree":
            raise AssertionError(f"heavy-tree migration host-readback contract drifted: {actions}")
        completed = subprocess.run(
            [sys.executable, str(LOOM), "profile", "light-migration-plan", "--target", str(target), "--json", "--full-output"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout or completed.stderr)
        if completed.returncode == 0 or payload.get("command") != "profile light-migration-plan" or payload.get("primary_cause", {}).get("id") != "light_profile_forbidden_carrier":
            raise AssertionError(f"CLI route did not preserve light-profile failure semantics: {payload}")


def main() -> int:
    catalog = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != "loom-light-profile-fixtures/v1":
        raise AssertionError("light-profile fixture schema drifted")
    fixtures = catalog.get("cases")
    if not isinstance(fixtures, list) or {item.get("id") for item in fixtures if isinstance(item, dict)} != {
        "heavy-tree",
        "absolute-workspace-entry",
        "absolute-private-workspace-entry",
        "absolute-windows-workspace-entry",
        "clean-light",
        "attach-only-forbidden-carrier",
        "untracked-and-ignored",
        "legacy-missing-state",
        "light-nonmetadata-state",
        "non-light",
    }:
        raise AssertionError("light-profile fixture catalog is incomplete")
    evaluator = load_module()
    copies = [
        ROOT / "skills" / "shared" / "scripts" / "light_profile.py",
        ROOT / "plugins" / "loom" / "skills" / "shared" / "scripts" / "light_profile.py",
    ]
    if any(not path.is_file() or path.read_bytes() != SOURCE.read_bytes() for path in copies):
        raise AssertionError("light-profile evaluator distribution copies drifted")
    if (ROOT / ".loom" / "bin" / "light_profile.py").exists():
        raise AssertionError("light-profile evaluator must not become a repo-local runtime carrier")
    with tempfile.TemporaryDirectory(prefix="loom-light-profile-") as raw_tmp:
        for fixture in fixtures:
            assert_case(evaluator, Path(raw_tmp), fixture)
    print("light-profile migration contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
