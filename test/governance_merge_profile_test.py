#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "skills/shared/scripts"
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


if __name__ == "__main__":
    unittest.main()
