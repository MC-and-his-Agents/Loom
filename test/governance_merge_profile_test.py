#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "src/skills/shared/scripts"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(SHARED_SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


loom_flow = load_module("loom_flow_for_governance_merge_profile_test", SHARED_SCRIPTS / "loom_flow.py")
loom_cli = load_module("loom_cli_for_governance_merge_profile_test", TOOLS_ROOT / "loom.py")


class GovernanceMergeProfileTest(unittest.TestCase):
    def test_host_enforced_blocks_when_host_required_check_is_unproven(self) -> None:
        payload = loom_flow.governance_capability_profile_payload(
            mode="host-enforced",
            host_enforcement={
                "required": False,
                "branch_protection_readable": True,
                "ruleset_readable": True,
            },
            allow_advisory=False,
            allow_high_risk_advisory=False,
            change_class=None,
        )

        self.assertEqual(payload["result"], "block")
        self.assertIn("loom-pr-merge-gate", payload["missing_inputs"][0])

    def test_host_enforced_defaults_to_limited_without_distinct_identity_readback(self) -> None:
        limited = loom_flow.governance_capability_profile_payload(
            mode="host-enforced",
            host_enforcement={
                "required": True,
                "branch_protection_readable": True,
                "ruleset_readable": True,
            },
            allow_advisory=False,
            allow_high_risk_advisory=False,
            change_class=None,
        )
        strong = loom_flow.governance_capability_profile_payload(
            mode="host-enforced",
            host_enforcement={
                "required": True,
                "branch_protection_readable": True,
                "trust_verdict": "strong",
            },
            allow_advisory=False,
            allow_high_risk_advisory=False,
            change_class=None,
        )

        self.assertEqual(limited["result"], "pass")
        self.assertEqual(limited["assurance"], "limited")
        self.assertEqual(strong["assurance"], "strong")

    def test_advisory_requires_explicit_opt_in_and_remains_low_assurance(self) -> None:
        blocked = loom_flow.governance_capability_profile_payload(
            mode="advisory/local-enforced",
            host_enforcement={"required": False},
            allow_advisory=False,
            allow_high_risk_advisory=False,
            change_class=None,
        )
        allowed = loom_flow.governance_capability_profile_payload(
            mode="advisory/local-enforced",
            host_enforcement={"required": False},
            allow_advisory=True,
            allow_high_risk_advisory=False,
            change_class=None,
        )

        self.assertEqual(blocked["result"], "block")
        self.assertEqual(allowed["result"], "pass")
        self.assertEqual(allowed["risk_label"], "low_assurance")
        self.assertEqual(allowed["host_enforcement_status"], "not_host_enforced")

    def test_high_risk_advisory_requires_separate_approval(self) -> None:
        blocked = loom_flow.governance_capability_profile_payload(
            mode="advisory/local-enforced",
            host_enforcement={"required": False},
            allow_advisory=True,
            allow_high_risk_advisory=False,
            change_class="release",
        )
        allowed = loom_flow.governance_capability_profile_payload(
            mode="advisory/local-enforced",
            host_enforcement={"required": False},
            allow_advisory=True,
            allow_high_risk_advisory=True,
            change_class="release",
        )

        self.assertEqual(blocked["result"], "block")
        self.assertEqual(allowed["result"], "pass")
        self.assertTrue(allowed["high_risk_approval"])

    def test_top_level_governance_profile_wrapper_delegates_to_flow(self) -> None:
        captured: dict[str, object] = {}

        def fake_emit_flow(command: str, flow_args: list[str], fallback_to: list[str]):
            captured["command"] = command
            captured["flow_args"] = flow_args
            captured["fallback_to"] = fallback_to
            return 0

        with patch.object(loom_cli, "emit_flow", side_effect=fake_emit_flow):
            status = loom_cli.handle_governance_profile(["status", "--target", "."])

        self.assertEqual(status, 0)
        self.assertEqual(captured["command"], "governance-profile status")
        self.assertEqual(captured["flow_args"], ["governance-profile", "status", "--target", "."])

    def test_pr_metadata_records_host_governance_mode(self) -> None:
        body, envelope, missing = loom_flow.render_governance_intensity_metadata_body(
            base_body="## Summary\n\nTest PR\n",
            field={"id": "loom-governance-intensity", "machine_carrier": {"surface": "merge_ready"}},
            requested_surface="merge_ready",
            item_id="MC-and-his-Agents/Loom/work_item/1805",
            branch_name="work/1805-host-governance-capability",
            head_sha="a" * 40,
            governance_intensity="standard",
            change_class="metadata_schema",
            suite_path="minimal",
            review_requirement="current_head_review_required",
            release_judgment="no_release",
            fact_chain_required=True,
            upgrade_triggers=[],
            suite_not_applicable=None,
            issue_number=1805,
            covered_issues=[],
            excluded_scope=[],
        )

        self.assertEqual(missing, [])
        fields = envelope["fields"]
        self.assertEqual(fields["governance_mode"], "host-enforced")
        self.assertEqual(fields["governance_assurance"], "limited")
        self.assertTrue(fields["host_enforcement_required"])
        self.assertIn("governance_mode", body)

    def test_closeout_policy_preserves_advisory_low_assurance_evidence(self) -> None:
        policy = loom_cli.ship_closeout_policy(
            {
                "governance_intensity": "standard",
                "governance_mode": "advisory/local-enforced",
                "governance_assurance": "low",
                "advisory_risk_label": "low_assurance",
                "change_class": "metadata_schema",
                "release_judgment": "no_release",
                "upgrade_triggers": [],
            }
        )

        self.assertEqual(policy["governance_mode"], "advisory/local-enforced")
        self.assertEqual(policy["advisory_risk_label"], "low_assurance")
        self.assertFalse(policy["host_enforced"])

    def test_closeout_policy_does_not_trust_authored_strong_assurance(self) -> None:
        policy = loom_cli.ship_closeout_policy(
            {
                "governance_intensity": "standard",
                "governance_mode": "host-enforced",
                "governance_assurance": "strong",
                "change_class": "metadata_schema",
                "release_judgment": "no_release",
                "upgrade_triggers": [],
            }
        )

        self.assertEqual(policy["governance_assurance"], "limited")
        self.assertTrue(policy["host_enforced"])


if __name__ == "__main__":
    unittest.main()
