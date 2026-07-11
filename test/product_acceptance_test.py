#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/skills/shared/scripts"))

import product_acceptance


NOW = datetime(2026, 7, 11, tzinfo=timezone.utc)
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
            "run_id": "run-1",
            "artifact_refs": ["artifact:run-1"],
            "provider_profile": {"provider": "provider-x", "profile": "redacted-profile", "redacted": True},
            "component_versions": {"WebEnvoy/Core": "a" * 40},
            "operation_boundary": {"allowed_actions": ["launch", "read", "capture"], "prohibited_actions": PROHIBITED, "observed_actions": ["launch", "read", "capture"]},
        }],
    }


class ProductAcceptanceTest(unittest.TestCase):
    def test_live_readonly_passes_with_fresh_bound_evidence(self) -> None:
        result = product_acceptance.evaluate_acceptance(live_record(), now=NOW)
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["product_acceptance"]["verdict"], "passed")
        self.assertEqual(result["authority_verdict"]["verdict"]["delivery_state"], "not_evaluated")

    def test_fixture_cannot_satisfy_live_readonly(self) -> None:
        record = live_record()
        record["evidence"][0]["evidence_class"] = "fixture"
        result = product_acceptance.evaluate_acceptance(record, now=NOW)
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
            result = product_acceptance.evaluate_acceptance(record, now=NOW)
            self.assertEqual(result["result"], "block")
            self.assertEqual(result["failure_envelope"]["consequences"], [])

    def test_future_evidence_or_missing_write_boundary_is_blocked(self) -> None:
        future = live_record()
        future["evidence"][0]["observed_at"] = "2099-01-01T00:00:00Z"
        incomplete_boundary = live_record()
        incomplete_boundary["evidence"][0]["operation_boundary"]["prohibited_actions"] = []
        for record in (future, incomplete_boundary):
            self.assertEqual(product_acceptance.evaluate_acceptance(record, now=NOW)["result"], "block")

    def test_invalid_cli_clock_fails_closed(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            product_acceptance.main(["validate", "--input", "ignored.json", "--now", "not-a-time", "--json"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
