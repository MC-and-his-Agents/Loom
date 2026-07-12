#!/usr/bin/env python3
"""Focused contract checks for the v0.30 host-default lifecycle (#2042)."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("loom_cli", ROOT / "tools" / "loom.py")
loom = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(loom)


def compatibility(*, intensity: str | None, policy: str | None, expiry: str | None):
    return loom.legacy_carrier_compatibility(
        argparse.Namespace(
            governance_intensity=intensity,
            compatibility_policy=policy,
            compatibility_expires_at=expiry,
        )
    )


def main() -> int:
    for intensity in ("light", "standard", "reinforced"):
        decision = loom.ship_closeout_policy(
            {
                "governance_intensity": intensity,
                "change_class": "implementation",
                "release_judgment": "no_release",
                "governance_mode": "host-enforced",
            }
        )
        assert decision["policy"] == "host_only"
        assert decision["creates_closeout_pr_by_default"] is False

    release = loom.ship_closeout_policy(
        {
            "governance_intensity": "reinforced",
            "change_class": "release",
            "release_judgment": "release_required",
        }
    )
    assert release["policy"] == "release_manifest"
    assert release["creates_closeout_pr_by_default"] is False
    assert loom.ship_validation_profile_for_paths([], release)[0] == "release"

    now = datetime.now(timezone.utc)
    valid = compatibility(
        intensity="reinforced",
        policy=loom.LEGACY_CARRIER_COMPATIBILITY_POLICY,
        expiry=(now + timedelta(days=30)).isoformat(),
    )
    assert valid["result"] == "pass"
    invalid = (
        compatibility(intensity=None, policy=None, expiry=None),
        compatibility(intensity="standard", policy=loom.LEGACY_CARRIER_COMPATIBILITY_POLICY, expiry=(now + timedelta(days=30)).isoformat()),
        compatibility(intensity="reinforced", policy="wrong", expiry=(now + timedelta(days=30)).isoformat()),
        compatibility(intensity="reinforced", policy=loom.LEGACY_CARRIER_COMPATIBILITY_POLICY, expiry=(now - timedelta(seconds=1)).isoformat()),
        compatibility(intensity="reinforced", policy=loom.LEGACY_CARRIER_COMPATIBILITY_POLICY, expiry=(now + timedelta(days=91)).isoformat()),
        compatibility(intensity="reinforced", policy=loom.LEGACY_CARRIER_COMPATIBILITY_POLICY, expiry=(now + timedelta(days=1)).replace(tzinfo=None).isoformat()),
    )
    assert all(row["result"] == "block" for row in invalid)

    source = (ROOT / "tools" / "loom.py").read_text(encoding="utf-8")
    ship = source[source.index("def handle_ship("):source.index("def closeout_run_step(")]
    assert "carrier refresh" not in ship
    assert "shadow-parity" not in ship
    assert "host-review-attestation" in ship
    assert "host-closeout-attestation" in ship
    sync = source[source.index("def handle_closeout_sync("):source.index("def closeout_run_payload(")]
    assert "host-closeout-attestation" in sync
    assert "repo_mutations=False" in sync
    assert "creates_closeout_pr=False" in sync
    assert "carrier closeout-sync" not in sync

    tiers = loom.HELP_COMMAND_TIERS
    for command in ("attestation readback", "attestation closeout", "closeout"):
        assert command in tiers["common_path"]
    for command in ("carrier closeout-sync", "closeout run", "release closeout-sync"):
        assert all(command not in tier for tier in tiers.values())
        assert loom.COMMAND_INDEX[command]["status"] == "compatibility"

    skill_files = (
        ROOT / "src/skills/loom-review/SKILL.md",
        ROOT / "src/skills/loom-merge-ready/SKILL.md",
        ROOT / "src/skills/loom-retire/SKILL.md",
        ROOT / "src/skills/route-matrix.md",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in skill_files)
    for required in ("host attestation", "local-only", "不创建 closeout-only"):
        assert required in combined
    for forbidden in (
        "loom carrier closeout-sync --target",
        "loom release closeout-sync --target",
        "loom review record --target <repo> --item <id> --review-file .loom/reviews/<item>.json",
    ):
        assert forbidden not in combined

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "reinforced-carrier-compat/v1" in readme
    assert "Release readback is terminal for release aftercare" in readme
    assert "creates no closeout-only" in (ROOT / "docs/methodology/harness/cli-command-matrix.md").read_text(encoding="utf-8")
    check_executable_host_default_paths()
    print("host-default lifecycle checks passed")
    return 0


def check_executable_host_default_paths() -> None:
    help_result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "loom.py"), "ship", "--help"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert help_result.returncode == 0
    assert "--attestation-artifact-input" in help_result.stdout
    assert "--review-policy" in help_result.stdout

    originals = {
        "emit": loom.emit,
        "flow_payload": loom.flow_payload,
        "host_lifecycle_admission_payload": loom.host_lifecycle_admission_payload,
        "ship_binding_inference_payload": loom.ship_binding_inference_payload,
        "ship_changed_paths_payload": loom.ship_changed_paths_payload,
        "ship_validation_profile_payload": loom.ship_validation_profile_payload,
        "host_attestation_readback": loom.host_attestation_readback,
    }
    emitted: dict[str, object] = {}
    flow_calls: list[list[str]] = []
    attestation_calls: list[dict[str, object]] = []
    events: list[str] = []

    def fake_emit(payload, *, stream=None):
        emitted.clear()
        emitted.update(payload)
        return 0 if payload.get("result") == "pass" else 1

    def fake_flow(_command, args, *, fallback_to=None):
        flow_calls.append(list(args))
        events.append("flow:" + " ".join(args[:2]))
        if args[:2] == ["controlled-merge", "merge"]:
            return {"command": "controlled-merge", "result": "pass", "summary": "merged", "pr": {"number": 1, "baseRefName": "main"}}
        return {"command": " ".join(args[:2]), "result": "pass", "summary": "fixture pass"}

    def fake_attestation(_target, owner, repo, pr, work_item, artifact_id, *, closeout=False, review_policy="approved"):
        events.append("attestation:closeout" if closeout else "attestation:review")
        attestation_calls.append(
            {
                "owner": owner,
                "repo": repo,
                "pr": pr,
                "work_item": work_item,
                "artifact_id": artifact_id,
                "closeout": closeout,
                "review_policy": review_policy,
            }
        )
        return {"command": "attestation closeout" if closeout else "attestation readback", "result": "pass", "summary": "host attestation passed"}

    loom.emit = fake_emit
    loom.flow_payload = fake_flow
    loom.host_lifecycle_admission_payload = lambda **_kwargs: {"command": "lifecycle admission", "result": "pass", "summary": "admitted"}
    loom.ship_binding_inference_payload = lambda _args, _target: {
        "command": "ship binding inference",
        "result": "pass",
        "summary": "bound",
        "bindings": {"branch": "work/2042-host-default", "head_sha": "a" * 40, "target_branch": "main"},
    }
    loom.ship_changed_paths_payload = lambda *_args, **_kwargs: {"result": "pass", "paths": ["README.md"], "errors": []}
    loom.ship_validation_profile_payload = lambda *_args, **_kwargs: {"result": "pass", "selected_profile": "light"}
    loom.host_attestation_readback = fake_attestation
    try:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "artifact.json"
            artifact.write_text(json.dumps({"artifact_id": 7}), encoding="utf-8")

            status = loom.handle_ship(
                [
                    "--target", str(ROOT), "--item", "WI-2042", "--issue", "2042", "--pr", "1",
                    "--owner", "o", "--repo", "r", "--branch", "work/2042-host-default",
                    "--attestation-artifact-input", str(artifact), "--review-policy", "single_maintainer", "--json",
                ]
            )
            assert status == 0 and emitted.get("result") == "pass"
            assert any(call["closeout"] is False and call["artifact_id"] == 7 for call in attestation_calls)

            emitted.clear()
            attestation_calls.clear()
            flow_calls.clear()
            status = loom.handle_closeout_sync(
                "status",
                [
                    "--target", str(ROOT), "--item", "WI-2042", "--issue", "2042", "--pr", "1",
                    "--owner", "o", "--repo", "r", "--attestation-artifact-input", str(artifact),
                    "--review-policy", "single_maintainer", "--skip-cleanup", "--json",
                ],
            )
            assert status == 0 and emitted.get("repo_mutations") is False
            assert [step.get("name") for step in emitted.get("steps", [])] == ["host-closeout-attestation"]
            assert not flow_calls

            emitted.clear()
            attestation_calls.clear()
            flow_calls.clear()
            events.clear()
            status = loom.handle_merge(
                [
                    "run", "1", "--target", str(ROOT), "--work-item", "WI-2042", "--issue", "2042",
                    "--target-branch", "main", "--owner", "o", "--repo", "r", "--apply", "--closeout-run",
                    "--closeout-mode", "host_only", "--attestation-artifact-input", str(artifact),
                    "--review-policy", "single_maintainer", "--json",
                ]
            )
            assert status == 0 and emitted.get("result") == "pass"
            assert events.index("attestation:review") < events.index("flow:controlled-merge merge") < events.index("attestation:closeout")
            assert any(call["closeout"] is False and call["artifact_id"] == 7 for call in attestation_calls)
            assert any(call["closeout"] is True and call["artifact_id"] == 7 for call in attestation_calls)
            assert not any(call[:2] == ["closeout", "check"] or call[:2] == ["carrier", "closeout-sync"] for call in flow_calls)

            emitted.clear()
            attestation_calls.clear()
            flow_calls.clear()
            events.clear()
            status = loom.handle_merge(
                [
                    "run", "1", "--target", str(ROOT), "--work-item", "WI-2042", "--issue", "2042",
                    "--target-branch", "main", "--owner", "o", "--repo", "r", "--apply", "--closeout-run",
                    "--closeout-mode", "host_only", "--json",
                ]
            )
            assert status == 1 and emitted.get("result") == "block"
            assert not flow_calls and not attestation_calls
    finally:
        for name, value in originals.items():
            setattr(loom, name, value)


if __name__ == "__main__":
    raise SystemExit(main())
