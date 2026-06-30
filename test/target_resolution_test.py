#!/usr/bin/env python3

from __future__ import annotations

import json
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


if __name__ == "__main__":
    unittest.main()
