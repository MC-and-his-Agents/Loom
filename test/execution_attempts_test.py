#!/usr/bin/env python3

from __future__ import annotations

import sys
import os
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src/skills/shared/scripts"))

import execution_attempts


class ExecutionAttemptsTest(unittest.TestCase):
    def test_rejects_authored_progress_fields_recursively(self) -> None:
        paths = execution_attempts.collect_forbidden_execution_attempt_paths(
            {"failure": {"next_step": "do not persist"}, "steps": [{"current_stop": "forbidden"}]}
        )

        self.assertEqual(paths, ["failure.next_step", "steps[0].current_stop"])

    def test_classifies_retry_exhaustion_from_blocked_payload(self) -> None:
        details = execution_attempts.execution_failure_details(
            {"result": "block", "missing_inputs": ["retries exhausted while waiting for host"]}
        )

        self.assertEqual(details["classification"], "retry_exhaustion")

    def test_persists_and_reads_back_current_attempt(self) -> None:
        previous_workstation = os.environ.get("LOOM_WORKSTATION_ROOT")
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir) / "project"
                root.mkdir()
                os.environ["LOOM_WORKSTATION_ROOT"] = str(Path(tempdir) / "workstation")
                context = {
                    "target_root": root,
                    "item_id": "WI-1",
                    "workspace_entry": ".",
                    "workspace_path": root,
                }

                saved = execution_attempts.persist_execution_attempt(
                    context,
                    command="flow",
                    operation="build",
                    payload={"result": "pass", "missing_inputs": []},
                )
                latest = execution_attempts.latest_execution_attempt_payload(root, "WI-1")

                self.assertEqual(saved["result"], "pass")
                self.assertEqual(latest["status"], "present")
                self.assertEqual(latest["attempt"]["operation"], "build")
        finally:
            if previous_workstation is None:
                os.environ.pop("LOOM_WORKSTATION_ROOT", None)
            else:
                os.environ["LOOM_WORKSTATION_ROOT"] = previous_workstation


if __name__ == "__main__":
    unittest.main()
