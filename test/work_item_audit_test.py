#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "skills/shared/scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

spec = importlib.util.spec_from_file_location("loom_flow", SHARED_SCRIPTS / "loom_flow.py")
assert spec is not None
loom_flow = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(loom_flow)


class WorkItemAuditTest(unittest.TestCase):
    def test_carrier_refresh_apply_recomputes_remaining_after_readback(self) -> None:
        original_runtime_state = loom_flow.runtime_state_payload
        original_load_context = loom_flow.load_context
        original_runtime_updates = loom_flow.runtime_artifact_updates
        original_apply_runtime_updates = loom_flow.apply_runtime_artifact_updates
        original_shadow = loom_flow.refresh_shadow_evidence_actions
        original_apply_shadow = loom_flow.apply_shadow_evidence_actions
        try:
            loom_flow.runtime_state_payload = lambda _target: {
                "result": "pass",
                "summary": "runtime ok",
                "missing_inputs": [],
                "fallback_to": None,
            }
            loom_flow.load_context = lambda _target, _output, _item: (None, [loom_flow.IDLE_FACT_CHAIN_ERROR])
            phase = {"refreshed": False}

            def fake_runtime_artifact_updates(
                _target: Path,
                payload: dict[str, object],
                *,
                source: str,
            ) -> list[dict[str, object]]:
                path = ".loom/bootstrap/manifest.json" if source == "manifest" else ".loom/bootstrap/init-result.json"
                status = "current" if phase["refreshed"] else "refresh-needed"
                return [
                    {
                        "path": path,
                        "source": source,
                        "status": status,
                    }
                ]

            def fake_apply_runtime_artifact_updates(
                payload: dict[str, object],
                actions: list[dict[str, object]],
                *,
                source: str,
            ) -> None:
                if any(action.get("source") == source and action.get("status") == "refresh-needed" for action in actions):
                    phase["refreshed"] = True

            loom_flow.runtime_artifact_updates = fake_runtime_artifact_updates
            loom_flow.apply_runtime_artifact_updates = fake_apply_runtime_artifact_updates
            loom_flow.refresh_shadow_evidence_actions = lambda _target: []
            loom_flow.apply_shadow_evidence_actions = lambda _target, _actions: None

            with tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                bootstrap = root / ".loom" / "bootstrap"
                bootstrap.mkdir(parents=True, exist_ok=True)
                (bootstrap / "manifest.json").write_text("{}\n", encoding="utf-8")
                (bootstrap / "init-result.json").write_text("{}\n", encoding="utf-8")

                dry_run = loom_flow.carrier_refresh_payload(
                    root,
                    ".loom/bootstrap/init-result.json",
                    None,
                    dry_run=True,
                )
                applied = loom_flow.carrier_refresh_payload(
                    root,
                    ".loom/bootstrap/init-result.json",
                    None,
                    dry_run=False,
                )

            self.assertEqual(dry_run["result"], "pass")
            self.assertEqual(len(dry_run["refresh_needed"]), 2)
            self.assertFalse(applied["dry_run"])
            self.assertEqual(applied["result"], "pass")
            self.assertEqual(applied["refresh_needed"], [])
            self.assertEqual(len(applied["fixed"]), 2)
            self.assertEqual(applied["remaining_refresh"], [])
            self.assertEqual(
                applied["summary"],
                "carrier refresh completed and readback found no remaining updates.",
            )
        finally:
            loom_flow.runtime_state_payload = original_runtime_state
            loom_flow.load_context = original_load_context
            loom_flow.runtime_artifact_updates = original_runtime_updates
            loom_flow.apply_runtime_artifact_updates = original_apply_runtime_updates
            loom_flow.refresh_shadow_evidence_actions = original_shadow
            loom_flow.apply_shadow_evidence_actions = original_apply_shadow

    def test_host_complete_diagnostic_blocks_startup(self) -> None:
        finding = loom_flow.work_item_audit_finding_from_diagnostic(
            {
                "item_id": "WI-1494",
                "classification": "carrier_closeout_required",
                "freshness": "host_complete_carrier_active",
                "work_item_locator": ".loom/work-items/WI-1494.md",
                "binding_locator": ".loom/progress/WI-1494.md",
                "checkpoint": "merged",
                "blocking": False,
                "next_command": "python3 tools/loom_flow.py carrier closeout-sync --target . --item WI-1494 --apply",
            }
        )

        self.assertTrue(finding["blocking"])
        self.assertFalse(finding["purity_blocking"])
        self.assertEqual(finding["kind"], "host_complete_carrier_not_terminalized")
        self.assertEqual(finding["classifier"], "carrier_refresh_needed")
        self.assertIn("closeout-sync", finding["next_command"])

    def test_terminal_stale_diagnostic_is_nonblocking(self) -> None:
        finding = loom_flow.work_item_audit_finding_from_diagnostic(
            {
                "item_id": "WI-1541",
                "classification": "stale_carrier",
                "freshness": "terminal",
                "work_item_locator": ".loom/work-items/WI-1541.md",
                "binding_locator": ".loom/progress/WI-1541.md",
                "checkpoint": "closed_out",
                "blocking": False,
            }
        )

        self.assertFalse(finding["blocking"])
        self.assertEqual(finding["kind"], "unrelated_terminal_stale_carrier")
        self.assertEqual(finding["classifier"], "stale_carrier")

    def test_payload_compacts_nonblocking_findings_and_reports_shadow_drift(self) -> None:
        original_runtime_state = loom_flow.runtime_state_payload
        original_load_context = loom_flow.load_context
        original_purity = loom_flow.purity_report_from_context
        original_shadow = loom_flow.refresh_shadow_evidence_actions
        try:
            loom_flow.runtime_state_payload = lambda _target: {"result": "pass", "summary": "runtime ok", "missing_inputs": [], "fallback_to": None}
            loom_flow.load_context = lambda _target, _output, _item: (
                {
                    "target_root": Path("/fixture"),
                    "workspace_path": Path("/fixture"),
                    "workspace_entry": ".",
                    "item_id": "WI-1542",
                    "current_checkpoint": "build",
                },
                [],
            )
            loom_flow.purity_report_from_context = lambda _context: {
                "state": "clean",
                "hard_failures": [],
                "report_only": [],
                "active_workspace_diagnostics": [
                    {
                        "item_id": "WI-1494",
                        "classification": "carrier_closeout_required",
                        "freshness": "host_complete_carrier_active",
                        "work_item_locator": ".loom/work-items/WI-1494.md",
                        "binding_locator": ".loom/progress/WI-1494.md",
                        "checkpoint": "merged",
                        "blocking": False,
                    },
                    {
                        "item_id": "WI-1541",
                        "classification": "stale_carrier",
                        "freshness": "terminal",
                        "work_item_locator": ".loom/work-items/WI-1541.md",
                        "binding_locator": ".loom/progress/WI-1541.md",
                        "checkpoint": "closed_out",
                        "blocking": False,
                    },
                ],
            }
            loom_flow.refresh_shadow_evidence_actions = lambda _target: [
                {
                    "path": ".loom/shadow/merge-ready-loom.json",
                    "kind": "shadow-evidence",
                    "status": "refresh-needed",
                    "current_source_sha256": {"source": "old"},
                    "expected_source_sha256": {"source": "new"},
                }
            ]

            with tempfile.TemporaryDirectory() as tempdir:
                payload = loom_flow.work_item_audit_payload(Path(tempdir), ".loom/bootstrap/init-result.json", "WI-1542")

            self.assertEqual(payload["schema_version"], "loom-active-carrier-audit/v1")
            self.assertEqual(payload["result"], "block")
            self.assertEqual(payload["diagnostic_summary"]["by_classification"]["carrier_closeout_required"], 1)
            self.assertEqual(payload["diagnostic_summary"]["by_classification"]["stale_carrier"], 1)
            self.assertEqual(len(payload["findings"]), 2)
            self.assertEqual(len(payload["nonblocking_samples"]), 1)
            self.assertEqual(payload["findings"][1]["classifier"], "shadow_stale")
            self.assertNotIn("purity", payload)
        finally:
            loom_flow.runtime_state_payload = original_runtime_state
            loom_flow.load_context = original_load_context
            loom_flow.purity_report_from_context = original_purity
            loom_flow.refresh_shadow_evidence_actions = original_shadow


if __name__ == "__main__":
    unittest.main()
