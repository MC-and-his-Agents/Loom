#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("loom_cli", REPO_ROOT / "tools/loom.py")
assert spec is not None
loom_cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(loom_cli)


class OutputEnvelopeTest(unittest.TestCase):
    def test_output_envelope_contains_agent_safe_fields(self) -> None:
        envelope = loom_cli.output_envelope(
            "fact-chain",
            "block",
            summary="Two carriers disagree.",
            key_gaps=["review head is stale"],
            failed_layer="fact-chain",
            fail_closed_reason="stale review",
        )

        self.assertEqual(envelope["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
        self.assertEqual(envelope["summary"], "Two carriers disagree.")
        self.assertEqual(envelope["failure_classification"]["failed_layer"], "fact-chain")
        self.assertEqual(envelope["key_gaps"], ["review head is stale"])
        self.assertEqual(envelope["full_output"]["available"], False)
        self.assertEqual(envelope["full_output"]["truncated"], False)

    def test_write_output_artifact_persists_full_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = loom_cli.output("status", "pass", summary="ok")
            locator = loom_cli.write_output_artifact(payload, artifact_dir=Path(tempdir))

            artifact = json.loads(Path(locator).read_text(encoding="utf-8"))

            self.assertEqual(artifact["schema_version"], loom_cli.OUTPUT_ARTIFACT_SCHEMA)
            self.assertEqual(artifact["command"], "status")
            self.assertEqual(artifact["payload"], payload)

    def test_agent_safe_payload_writes_artifact_when_over_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = loom_cli.output(
                "state-check",
                "block",
                summary="Too much diagnostic output.",
                blocking_gaps=[f"gap-{index}" for index in range(20)],
                diagnostic="x" * 4096,
                failed_layer="state-check",
                fail_closed_reason="fixture over budget",
            )

            safe = loom_cli.agent_safe_payload(
                payload,
                stdout_budget_bytes=512,
                artifact_dir=Path(tempdir),
            )

            locator = Path(safe["full_output"]["artifact_locator"])
            self.assertEqual(safe["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
            self.assertEqual(safe["summary"], "Too much diagnostic output.")
            self.assertEqual(safe["key_gaps"], [f"gap-{index}" for index in range(10)])
            self.assertEqual(safe["full_output"]["available"], True)
            self.assertEqual(safe["full_output"]["truncated"], True)
            self.assertTrue(locator.exists())
            self.assertNotIn('"diagnostic":', json.dumps(safe))


if __name__ == "__main__":
    unittest.main()
