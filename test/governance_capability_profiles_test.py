#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs/evidence/fixtures/github-profile-maturity-fixtures.json"
HIGH_RISK_CAPABILITIES = {"release", "security", "payment", "data_migration"}


class GovernanceCapabilityProfilesTest(unittest.TestCase):
    def test_advisory_profile_is_low_assurance_and_not_strong(self) -> None:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        fixture = next(item for item in payload["fixtures"] if item["name"] == "advisory_low_assurance")

        advisory = [
            row
            for row in fixture["inputs"]["capability_enforcement"]
            if row["enforcement_profile"] == "advisory/local-enforced"
        ]
        self.assertTrue(advisory)
        self.assertTrue(all(row["risk_label"] == "low_assurance" for row in advisory))
        self.assertTrue(all(row["counts_toward_strong_maturity"] is False for row in advisory))
        self.assertEqual(fixture["expected"]["current"], "standard")
        self.assertIn("host_enforced_control_plane", fixture["expected"]["missing_by_level"]["strong"])

    def test_high_risk_capability_downgrade_requires_approval_and_evidence(self) -> None:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        rows = [
            row
            for fixture in payload["fixtures"]
            for row in fixture["inputs"].get("capability_enforcement", [])
            if row["capability"] in HIGH_RISK_CAPABILITIES
            and row["enforcement_profile"] == "advisory/local-enforced"
        ]

        self.assertTrue(rows)
        for row in rows:
            approved = row.get("explicit_approval") is True and row.get("version_controlled_evidence") is True
            self.assertFalse(approved)
            self.assertFalse(row["counts_toward_strong_maturity"])


if __name__ == "__main__":
    unittest.main()
