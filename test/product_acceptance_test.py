#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/skills/shared/scripts"))

import product_acceptance


NOW = datetime(2026, 7, 11, 0, 30, tzinfo=timezone.utc)
PROHIBITED = ["login", "captcha_or_risk_bypass", "submit", "publish", "send", "external_visible_write"]


def live_record() -> dict:
    return {
        "schema_version": product_acceptance.SCHEMA,
        "story_locator": "MC-and-his-Agents/Loom/issue/225",
        "scenario_id": "READ-001",
        "verdict": "passed",
        "minimum_evidence_class": "live_readonly",
        "evidence": [{
            "evidence_class": "live_readonly",
            "observed_at": "2026-07-11T00:00:00Z",
            "freshness_window_seconds": 3600,
            "run_id": 9,
            "artifact_refs": ["MC-and-his-Agents/Loom/artifact/7"],
            "provider_profile": {"provider": "provider-x", "profile": "redacted-profile", "redacted": True},
            "component_versions": {"MC-and-his-Agents/Loom": "a" * 40},
            "operation_boundary": {"allowed_actions": ["launch", "read", "capture"], "prohibited_actions": PROHIBITED, "observed_actions": ["launch", "read", "capture"]},
        }],
        "verifier": {"login": "maintainer", "id": 42},
    }


def archive(record: dict) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as bundle:
        bundle.writestr("acceptance.json", json.dumps(record))
    return output.getvalue()


def host_reader(
    record: dict,
    *,
    permission: str = "write",
    run_head: str = "a" * 40,
    artifact_name: str = product_acceptance.ARTIFACT_NAME,
    workflow_path: str = product_acceptance.TRUSTED_WORKFLOW_PATH,
    event: str = "workflow_dispatch",
    head_branch: str = "main",
):
    payload = archive(record)
    mapping = {
        "repos/MC-and-his-Agents/Loom": {"default_branch": "main"},
        "repos/MC-and-his-Agents/Loom/issues/225": {"number": 225},
        "repos/MC-and-his-Agents/Loom/actions/artifacts/7": {
            "id": 7, "name": artifact_name, "expired": False, "size_in_bytes": len(payload),
            "digest": "sha256:" + __import__("hashlib").sha256(payload).hexdigest(), "workflow_run": {"id": 9},
            "created_at": "2026-07-11T00:01:00Z",
        },
        "repos/MC-and-his-Agents/Loom/actions/runs/9": {
            "id": 9, "status": "completed", "conclusion": "success", "head_sha": run_head,
            "workflow_id": 11, "path": workflow_path, "event": event, "head_branch": head_branch,
            "run_started_at": "2026-07-10T23:59:00Z", "updated_at": "2026-07-11T00:02:00Z",
            "repository": {"full_name": "MC-and-his-Agents/Loom"},
            "triggering_actor": {"login": "maintainer", "id": 42},
        },
        "repos/MC-and-his-Agents/Loom/actions/workflows/11": {
            "id": 11, "path": workflow_path, "state": "active",
        },
        "repos/MC-and-his-Agents/Loom/collaborators/maintainer/permission": {
            "permission": permission, "user": {"login": "maintainer", "id": 42},
        },
        "repos/MC-and-his-Agents/Loom/commits/" + "a" * 40: {"sha": "a" * 40},
    }

    def read_json(_root, path):
        return (mapping[path], []) if path in mapping else (None, [f"unexpected path: {path}"])

    def read_bytes(_root, path):
        return (payload, []) if path.endswith("/actions/artifacts/7/zip") else (None, [f"unexpected bytes path: {path}"])

    return read_json, read_bytes


class ProductAcceptanceTest(unittest.TestCase):
    def test_local_record_cannot_self_assert_passed(self) -> None:
        result = product_acceptance.evaluate_acceptance(live_record(), now=NOW)
        self.assertEqual(result["result"], "block")
        self.assertFalse(result["product_acceptance"]["trusted"])
        self.assertEqual(result["authority_verdict"]["verdict"]["delivery_state"], "not_evaluated")

    def test_host_resolver_authenticates_locator_artifact_run_and_verifier(self) -> None:
        read_json, read_bytes = host_reader(live_record())
        result = product_acceptance.resolve_acceptance(
            ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
        )
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["product_acceptance"]["verdict"], "passed")
        self.assertTrue(result["product_acceptance"]["trusted"])
        self.assertFalse(result["product_acceptance"]["owns_lifecycle_closure"])

    def test_stronger_evidence_satisfies_lower_minimum(self) -> None:
        record = live_record()
        record["minimum_evidence_class"] = "process_runtime"
        read_json, read_bytes = host_reader(record)
        result = product_acceptance.resolve_acceptance(
            ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
        )
        self.assertEqual(result["result"], "pass")

    def test_auxiliary_weaker_evidence_does_not_block_a_qualifying_row(self) -> None:
        record = live_record()
        auxiliary = json.loads(json.dumps(record["evidence"][0]))
        auxiliary["evidence_class"] = "static"
        record["evidence"].append(auxiliary)
        read_json, read_bytes = host_reader(record)
        commit_reads = 0

        def counted_read_json(root, path):
            nonlocal commit_reads
            if "/commits/" in path:
                commit_reads += 1
            return read_json(root, path)

        self.assertEqual(product_acceptance.resolve_acceptance(
            ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=counted_read_json, read_bytes=read_bytes,
        )["result"], "pass")
        self.assertEqual(commit_reads, 1)

    def test_fixture_cannot_satisfy_live_readonly(self) -> None:
        record = live_record()
        record["evidence"][0]["evidence_class"] = "fixture"
        read_json, read_bytes = host_reader(record)
        result = product_acceptance.resolve_acceptance(
            ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
        )
        self.assertEqual(result["result"], "block")
        self.assertEqual(result["product_acceptance"]["verdict"], "blocked")
        self.assertEqual(result["failure_envelope"]["primary_cause"]["failure_domain"], "product_acceptance")

    def test_waiver_is_not_passed(self) -> None:
        record = live_record()
        record.update({"verdict": "waived", "rationale": "manual approval required", "evidence": []})
        result = product_acceptance.evaluate_acceptance(record, now=NOW)
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["product_acceptance"]["verdict"], "waived")

    def test_stale_or_unsafe_evidence_is_blocked(self) -> None:
        stale = live_record()
        stale["evidence"][0]["observed_at"] = "2026-07-10T00:00:00Z"
        unsafe = live_record()
        unsafe["evidence"][0]["operation_boundary"]["observed_actions"] = ["external_visible_write"]
        for record in (stale, unsafe):
            read_json, read_bytes = host_reader(record)
            result = product_acceptance.resolve_acceptance(
                ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
            )
            self.assertEqual(result["result"], "block")
            self.assertEqual(result["failure_envelope"]["consequences"], [])
            self.assertEqual(result["failure_envelope"]["secondary_causes"], [])

    def test_future_evidence_or_missing_write_boundary_is_blocked(self) -> None:
        future = live_record()
        future["evidence"][0]["observed_at"] = "2099-01-01T00:00:00Z"
        incomplete_boundary = live_record()
        incomplete_boundary["evidence"][0]["operation_boundary"]["prohibited_actions"] = []
        for record in (future, incomplete_boundary):
            read_json, read_bytes = host_reader(record)
            self.assertEqual(product_acceptance.resolve_acceptance(
                ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
            )["result"], "block")

    def test_untrusted_verifier_or_mismatched_run_fails_closed(self) -> None:
        for kwargs in (
            {"permission": "read"},
            {"run_head": "b" * 40},
            {"artifact_name": "forged"},
            {"workflow_path": ".github/workflows/arbitrary.yml"},
            {"event": "pull_request"},
            {"head_branch": "feature"},
        ):
            read_json, read_bytes = host_reader(live_record(), **kwargs)
            result = product_acceptance.resolve_acceptance(
                ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
            )
            self.assertEqual(result["result"], "block")
            self.assertFalse(result["product_acceptance"]["trusted"])

    def test_class_claim_time_window_and_fanout_limits_fail_closed(self) -> None:
        wrong_class = live_record()
        wrong_class["evidence"][0]["evidence_class"] = "external_visible_write"
        outside_window = live_record()
        outside_window["evidence"][0]["observed_at"] = "2026-07-11T00:01:30Z"
        too_many = live_record()
        too_many["evidence"] = [json.loads(json.dumps(too_many["evidence"][0])) for _ in range(product_acceptance.MAX_EVIDENCE_ROWS + 1)]
        for record in (wrong_class, outside_window, too_many):
            read_json, read_bytes = host_reader(record)
            self.assertEqual(product_acceptance.resolve_acceptance(
                ROOT, "MC-and-his-Agents/Loom/issue/225", 7, now=NOW, read_json=read_json, read_bytes=read_bytes,
            )["result"], "block")

    def test_invalid_cli_clock_fails_closed(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            product_acceptance.main(["validate", "--input", "ignored.json", "--now", "not-a-time", "--json"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
