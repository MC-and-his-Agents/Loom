#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class TargetResolutionTest(unittest.TestCase):
    def test_node_wrapper_resolves_relative_target_from_invocation_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir).resolve()
            result = subprocess.run(
                ["node", str(REPO_ROOT / "bin/loom.mjs"), "detect", "--target", ".", "--json"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["target"], str(root))

    def test_node_wrapper_build_failure_does_not_create_repo_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir).resolve()
            env = os.environ.copy()
            env["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "512"
            env.pop("LOOM_OUTPUT_ARTIFACT_DIR", None)
            result = subprocess.run(
                ["node", str(REPO_ROOT / "bin/loom.mjs"), "build", "--target", ".", "--item", "WI-test", "--json"],
                cwd=root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertTrue(result.stdout, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "block")
            self.assertFalse(payload["carrier_mutations"])
            self.assertFalse((root / ".loom").exists())

    def test_node_wrapper_removed_fact_chain_fails_before_target_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir).resolve()
            env = os.environ.copy()
            env["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "512"
            env.pop("LOOM_OUTPUT_ARTIFACT_DIR", None)
            result = subprocess.run(
                ["node", str(REPO_ROOT / "bin/loom.mjs"), "fact-chain", "--target", ".", "--json"],
                cwd=root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertTrue(result.stdout, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "block")
            self.assertEqual(payload["primary_error_code"], "unsupported_command_surface")
            self.assertFalse(payload["mutates"])
            self.assertFalse((root / ".loom").exists())


if __name__ == "__main__":
    unittest.main()
