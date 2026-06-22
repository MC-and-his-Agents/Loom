#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "skills/shared/scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


loom_flow = load_module("loom_flow", SHARED_SCRIPTS / "loom_flow.py")
loom_init = load_module("loom_init", SHARED_SCRIPTS / "loom_init.py")


class CheckpointCanonicalizationTest(unittest.TestCase):
    def test_normalize_checkpoint_reads_legacy_aliases(self) -> None:
        self.assertEqual(loom_flow.normalize_checkpoint("admission checkpoint"), "admission")
        self.assertEqual(loom_flow.normalize_checkpoint("build checkpoint"), "build")
        self.assertEqual(loom_flow.normalize_checkpoint("merge checkpoint"), "merge")
        self.assertEqual(loom_flow.normalize_checkpoint("closed"), "closed_out")
        self.assertEqual(loom_flow.normalize_checkpoint("done"), "closed_out")

    def test_render_recovery_entry_writes_canonical_checkpoint(self) -> None:
        rendered = loom_flow.render_recovery_entry(
            "WI-1737",
            {
                "current_checkpoint": "build checkpoint",
                "current_stop": "stop",
                "next_step": "next",
                "blockers": "none",
                "latest_validation_summary": "ok",
                "recovery_boundary": "boundary",
                "current_lane": "lane",
            },
        )

        self.assertIn("- Current Checkpoint: build\n", rendered)
        self.assertNotIn("build checkpoint", rendered)

    def test_render_status_surface_writes_canonical_checkpoint(self) -> None:
        rendered = loom_flow.render_status_surface(
            {
                "fact_chain": {
                    "entry_points": {
                        "work_item": ".loom/work-items/WI-1737.md",
                        "recovery_entry": ".loom/progress/WI-1737.md",
                        "status_surface": ".loom/status/current.md",
                    },
                    "read_entry": "python3 .loom/bin/loom_init.py fact-chain --target .",
                },
                "facts": {
                    "item_id": {"value": "WI-1737"},
                    "goal": {"value": "goal"},
                    "scope": {"value": "scope"},
                    "execution_path": {"value": "path"},
                    "workspace_entry": {"value": "."},
                    "recovery_entry": {"value": ".loom/progress/WI-1737.md"},
                    "review_entry": {"value": ".loom/reviews/WI-1737.json"},
                    "validation_entry": {"value": "pytest"},
                    "closing_condition": {"value": "done"},
                    "current_checkpoint": {"value": "merge checkpoint"},
                    "current_stop": {"value": "stop"},
                    "next_step": {"value": "next"},
                    "blockers": {"value": "none"},
                    "latest_validation_summary": {"value": "ok"},
                    "recovery_boundary": {"value": "boundary"},
                    "current_lane": {"value": "lane"},
                },
            },
            {
                "run_entry": {"value": "run"},
                "logs_entry": {"value": "logs"},
                "diagnostics_entry": {"value": "diag"},
                "verification_entry": {"value": "verify"},
                "lane_entry": {"value": "lane"},
            },
        )

        self.assertIn("- Current Checkpoint: merge\n", rendered)
        self.assertNotIn("merge checkpoint", rendered)

    def test_bootstrap_progress_and_status_use_canonical_checkpoint(self) -> None:
        base_result = {
            "run": {"scenario_key": "small-existing"},
            "initial_work_items": [
                {
                    "id": "INIT-0001",
                    "goal": "goal",
                    "scope": "scope",
                    "execution_path": "path",
                    "workspace_entry": ".",
                    "recovery_entry": ".loom/progress/INIT-0001.md",
                    "review_entry": ".loom/reviews/INIT-0001.json",
                    "validation_entry": "python3 .loom/bin/loom_init.py verify --target .",
                    "closing_condition": "done",
                }
            ],
            "fact_chain": {
                "read_entry": "python3 .loom/bin/loom_init.py fact-chain --target .",
                "entry_points": {
                    "work_item": ".loom/work-items/INIT-0001.md",
                    "recovery_entry": ".loom/progress/INIT-0001.md",
                }
            },
        }

        progress = loom_init.render_progress(base_result)
        status = loom_init.render_status(base_result)

        self.assertIn("- Current Checkpoint: admission\n", progress)
        self.assertIn("- Current Checkpoint: admission\n", status)
        self.assertNotIn("admission checkpoint", progress)
        self.assertNotIn("admission checkpoint", status)


if __name__ == "__main__":
    unittest.main()
