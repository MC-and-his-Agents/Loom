#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
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
    def tearDown(self) -> None:
        os.environ.pop("LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES", None)
        os.environ.pop("LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES", None)
        os.environ.pop("LOOM_OUTPUT_ARTIFACT_DIR", None)

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
            self.assertEqual(safe["stdout_budget_bytes"], 512)
            self.assertTrue(locator.exists())
            self.assertNotIn('"diagnostic":', json.dumps(safe))

    def test_default_budget_keeps_large_payload_out_of_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = loom_cli.output(
                "fixture",
                "pass",
                summary="Large fixture output.",
                diagnostic="x" * (loom_cli.DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES * 2),
            )

            safe = loom_cli.agent_safe_payload(payload, artifact_dir=Path(tempdir))
            rendered = json.dumps(safe, indent=2, ensure_ascii=False)

            self.assertLessEqual(len(rendered.encode("utf-8")), loom_cli.DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES)
            self.assertEqual(safe["stdout_budget_bytes"], loom_cli.DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES)
            self.assertTrue(Path(safe["full_output"]["artifact_locator"]).exists())
            self.assertNotIn('"diagnostic":', rendered)

    def test_budget_can_be_configured_with_env(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            os.environ["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "768"
            os.environ["LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES"] = "32"
            payload = loom_cli.output(
                "fixture",
                "block",
                summary="s" * 128,
                blocking_gaps=[f"gap-{index}" for index in range(20)],
                diagnostic="x" * 4096,
            )

            safe = loom_cli.agent_safe_payload(payload, artifact_dir=Path(tempdir))

            self.assertEqual(safe["stdout_budget_bytes"], 768)
            self.assertEqual(safe["summary_target_bytes"], 32)
            self.assertLessEqual(len(safe["summary"].encode("utf-8")), 32)
            self.assertEqual(safe["key_gaps"], [f"gap-{index}" for index in range(10)])

    def test_explicit_full_output_mode_returns_payload(self) -> None:
        payload = loom_cli.output(
            "fixture",
            "pass",
            summary="debug",
            diagnostic="x" * (loom_cli.DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES * 2),
        )

        self.assertIs(loom_cli.agent_safe_payload(payload, full_output=True), payload)

    def test_actionable_block_payload_is_compacted_before_budget_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = loom_cli.output(
                "pr metadata-preflight",
                "block",
                summary="PR metadata preflight found repairable drift.",
                findings=[
                    {
                        "kind": "missing_human_backlink",
                        "severity": "fix-needed",
                        "subject": "Issue backlink",
                        "recommended_action": "Update the PR body Issue line.",
                        "next_command": "loom pr metadata-update 1703 --issue 1687 --apply --json",
                    }
                ],
                repair_plan={
                    "actions": [
                        {
                            "action": "update_pr_body_issue_backlink",
                            "description": "Insert `- Issue: #1687`.",
                            "next_command": "loom pr metadata-update 1703 --issue 1687 --apply --json",
                        }
                    ]
                },
            )

            safe = loom_cli.agent_safe_payload(payload, artifact_dir=Path(tempdir))

            self.assertEqual(safe["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
            self.assertEqual(safe["summary"], "PR metadata preflight found repairable drift.")
            self.assertEqual(safe["actionable_findings"][0]["kind"], "missing_human_backlink")
            self.assertIn("loom pr metadata-update", safe["actionable_findings"][0]["next_command"])
            self.assertTrue(Path(safe["full_output"]["artifact_locator"]).exists())
            self.assertNotIn("findings", safe)

    def test_actionable_findings_are_limited_to_five(self) -> None:
        payload = loom_cli.output(
            "closeout",
            "block",
            summary="Closeout has several blockers.",
            findings=[
                {"kind": f"finding-{index}", "recommended_action": f"fix-{index}"}
                for index in range(8)
            ],
        )

        safe = loom_cli.agent_safe_payload(payload)

        self.assertEqual(len(safe["actionable_findings"]), 5)
        self.assertEqual([entry["kind"] for entry in safe["actionable_findings"]], [f"finding-{index}" for index in range(5)])

    def test_pass_payload_under_budget_is_not_compacted(self) -> None:
        payload = loom_cli.output("fixture", "pass", summary="ok", findings=[{"kind": "advisory", "recommended_action": "none"}])

        self.assertIs(loom_cli.agent_safe_payload(payload), payload)

    def test_status_handler_defaults_to_agent_safe_stdout(self) -> None:
        original = loom_cli.delegated_payload
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_OUTPUT_ARTIFACT_DIR"] = tempdir
                os.environ["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "1024"

                def fake_payload(*_args, **_kwargs):
                    return loom_cli.output(
                        "status",
                        "pass",
                        summary="Status contains large diagnostics.",
                        missing_inputs=["carrier drift"],
                        target="/tmp/repo",
                        diagnostic="x" * 4096,
                    )

                loom_cli.delegated_payload = fake_payload
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = loom_cli.handle_status(["--target", ".", "--json"])

                rendered = stream.getvalue()
                payload = json.loads(rendered)
                self.assertEqual(code, 0)
                self.assertLessEqual(len(rendered.encode("utf-8")), 1024)
                self.assertEqual(payload["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
                self.assertEqual(payload["diagnostic_counts"]["missing_inputs"], 1)
                self.assertEqual(payload["key_gaps"], ["carrier drift"])
                self.assertTrue(Path(payload["full_output"]["artifact_locator"]).exists())
                self.assertNotIn('"diagnostic":', rendered)
        finally:
            loom_cli.delegated_payload = original

    def test_pr_gate_handler_defaults_to_actionable_stdout(self) -> None:
        original = loom_cli.flow_payload
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_OUTPUT_ARTIFACT_DIR"] = tempdir

                def fake_payload(*_args, **_kwargs):
                    return loom_cli.output(
                        "pr gate",
                        "block",
                        summary="PR gate found metadata drift.",
                        findings=[
                            {
                                "classifier": "pr_metadata_drift",
                                "next_action": "Regenerate or update the PR body machine carrier.",
                                "next_command": "loom pr metadata-update 1703 --apply --json",
                            }
                        ],
                    )

                loom_cli.flow_payload = fake_payload
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = loom_cli.handle_pr(["gate", "1703", "--json"])

                payload = json.loads(stream.getvalue())
                self.assertEqual(code, 1)
                self.assertEqual(payload["command"], "pr gate")
                self.assertEqual(payload["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
                self.assertEqual(payload["actionable_findings"][0]["classifier"], "pr_metadata_drift")
                self.assertIn("loom pr metadata-update", payload["actionable_findings"][0]["next_command"])
                self.assertTrue(Path(payload["full_output"]["artifact_locator"]).exists())
        finally:
            loom_cli.flow_payload = original

    def test_fact_chain_handler_supports_full_output_escape_hatch(self) -> None:
        original = loom_cli.flow_payload
        try:
            def fake_payload(*_args, **_kwargs):
                return loom_cli.output(
                    "fact-chain",
                    "pass",
                    summary="Fact chain full output.",
                    fact_chain={"read_entry": "loom fact-chain --target . --json"},
                    diagnostic="x" * 4096,
                )

            loom_cli.flow_payload = fake_payload
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = loom_cli.handle_fact_chain(["--target", ".", "--json", "--full-output"])

            payload = json.loads(stream.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(payload["command"], "fact-chain")
            self.assertIn("diagnostic", payload)
            self.assertNotIn("envelope_schema", payload)
        finally:
            loom_cli.flow_payload = original

    def test_shadow_parity_handler_defaults_to_agent_safe_stdout(self) -> None:
        original = loom_cli.flow_payload
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_OUTPUT_ARTIFACT_DIR"] = tempdir
                os.environ["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "1024"

                def fake_payload(*_args, **_kwargs):
                    return {
                        "command": "shadow-parity",
                        "result": "block",
                        "summary": "shadow parity blocking mode found mismatch or unreadable surfaces.",
                        "reports": [
                            {
                                "surface": "review",
                                "result": "mismatch",
                                "summary": "review surface drifted",
                                "loom_locator": ".loom/shadow/review.json",
                                "repo_locator": ".github/review.json",
                            }
                        ],
                        "blocking_failures": [{"kind": "parallel_truth_drift", "surface": "review"}],
                        "diagnostic": "x" * 4096,
                    }

                loom_cli.flow_payload = fake_payload
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = loom_cli.handle_shadow_parity(["--target", ".", "--surface", "all", "--blocking", "--json"])

                rendered = stream.getvalue()
                payload = json.loads(rendered)
                self.assertEqual(code, 1)
                self.assertLessEqual(len(rendered.encode("utf-8")), 1024)
                self.assertEqual(payload["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
                self.assertEqual(payload["diagnostic_counts"]["reports"], 1)
                self.assertEqual(payload["diagnostic_counts"]["non_passing_reports"], 1)
                self.assertIn(".loom/shadow/review.json", payload["key_locators"])
                self.assertTrue(Path(payload["full_output"]["artifact_locator"]).exists())
                self.assertNotIn('"diagnostic":', rendered)
        finally:
            loom_cli.flow_payload = original

    def test_flow_wrapper_defaults_to_agent_safe_stdout(self) -> None:
        original = loom_cli.flow_payload
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_OUTPUT_ARTIFACT_DIR"] = tempdir
                os.environ["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "1024"

                def fake_payload(*_args, **_kwargs):
                    return loom_cli.output(
                        "checkpoint build",
                        "block",
                        summary="Checkpoint emitted large diagnostics.",
                        missing_inputs=["review"],
                        diagnostic="x" * 4096,
                    )

                loom_cli.flow_payload = fake_payload
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = loom_cli.handle_checkpoint(["build", "--target", ".", "--json"])

                rendered = stream.getvalue()
                payload = json.loads(rendered)
                self.assertEqual(code, 1)
                self.assertLessEqual(len(rendered.encode("utf-8")), 1024)
                self.assertEqual(payload["command"], "checkpoint build")
                self.assertEqual(payload["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
                self.assertEqual(payload["key_gaps"], ["review"])
                self.assertTrue(Path(payload["full_output"]["artifact_locator"]).exists())
                self.assertNotIn('"diagnostic":', rendered)
        finally:
            loom_cli.flow_payload = original

    def test_flow_wrapper_supports_full_output_escape_hatch(self) -> None:
        original = loom_cli.flow_payload
        seen_args: list[str] = []
        try:
            def fake_payload(_command, flow_args, **_kwargs):
                seen_args.extend(flow_args)
                return loom_cli.output(
                    "checkpoint build",
                    "block",
                    summary="Checkpoint full output.",
                    diagnostic="x" * 4096,
                )

            loom_cli.flow_payload = fake_payload
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = loom_cli.handle_checkpoint(["build", "--target", ".", "--json", "--full-output"])

            payload = json.loads(stream.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(payload["command"], "checkpoint build")
            self.assertIn("diagnostic", payload)
            self.assertNotIn("envelope_schema", payload)
            self.assertNotIn("--full-output", seen_args)
        finally:
            loom_cli.flow_payload = original

    def test_scenario_build_defaults_to_agent_safe_stdout(self) -> None:
        original = loom_cli.flow_payload
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_OUTPUT_ARTIFACT_DIR"] = tempdir
                os.environ["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "1024"

                def fake_payload(*_args, **_kwargs):
                    return loom_cli.output(
                        "build",
                        "block",
                        summary="Build emitted large diagnostics.",
                        blocking_failures=["suite evidence missing"],
                        diagnostic="x" * 4096,
                    )

                loom_cli.flow_payload = fake_payload
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = loom_cli.handle_scenario("build", ["--target", ".", "--item", "WI-test", "--json"])

                rendered = stream.getvalue()
                payload = json.loads(rendered)
                self.assertEqual(code, 1)
                self.assertLessEqual(len(rendered.encode("utf-8")), 1024)
                self.assertEqual(payload["command"], "build")
                self.assertEqual(payload["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
                self.assertEqual(payload["key_gaps"], ["suite evidence missing"])
                self.assertTrue(Path(payload["full_output"]["artifact_locator"]).exists())
                self.assertNotIn('"diagnostic":', rendered)
        finally:
            loom_cli.flow_payload = original

    def test_scenario_build_supports_full_output_escape_hatch(self) -> None:
        original = loom_cli.flow_payload
        try:
            def fake_payload(*_args, **_kwargs):
                return loom_cli.output(
                    "build",
                    "block",
                    summary="Build full output.",
                    diagnostic="x" * 4096,
                )

            loom_cli.flow_payload = fake_payload
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = loom_cli.handle_scenario("build", ["--target", ".", "--item", "WI-test", "--json", "--full-output"])

            payload = json.loads(stream.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(payload["command"], "build")
            self.assertIn("diagnostic", payload)
            self.assertNotIn("envelope_schema", payload)
        finally:
            loom_cli.flow_payload = original

    def test_dispatch_defaults_to_agent_safe_stdout(self) -> None:
        original = loom_cli.delegated_payload
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_OUTPUT_ARTIFACT_DIR"] = tempdir
                os.environ["LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES"] = "1024"

                def fake_payload(*_args, **_kwargs):
                    return loom_cli.output(
                        "merge-ready",
                        "block",
                        summary="Merge-ready emitted large diagnostics.",
                        missing_inputs=["review approval"],
                        diagnostic="x" * 4096,
                    )

                loom_cli.delegated_payload = fake_payload
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = loom_cli.dispatch("merge-ready", ["--target", ".", "--json"])

                rendered = stream.getvalue()
                payload = json.loads(rendered)
                self.assertEqual(code, 1)
                self.assertLessEqual(len(rendered.encode("utf-8")), 1024)
                self.assertEqual(payload["command"], "merge-ready")
                self.assertEqual(payload["envelope_schema"], loom_cli.OUTPUT_ENVELOPE_SCHEMA)
                self.assertEqual(payload["key_gaps"], ["review approval"])
                self.assertTrue(Path(payload["full_output"]["artifact_locator"]).exists())
                self.assertNotIn('"diagnostic":', rendered)
        finally:
            loom_cli.delegated_payload = original

    def test_dispatch_supports_full_output_escape_hatch(self) -> None:
        original = loom_cli.delegated_payload
        seen_args: list[str] = []
        try:
            def fake_payload(_command, _tool_name, delegated_args, **_kwargs):
                seen_args.extend(delegated_args)
                return loom_cli.output(
                    "merge-ready",
                    "block",
                    summary="Merge-ready full output.",
                    diagnostic="x" * 4096,
                )

            loom_cli.delegated_payload = fake_payload
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = loom_cli.dispatch("merge-ready", ["--target", ".", "--json", "--full-output"])

            payload = json.loads(stream.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(payload["command"], "merge-ready")
            self.assertIn("diagnostic", payload)
            self.assertNotIn("envelope_schema", payload)
            self.assertNotIn("--full-output", seen_args)
        finally:
            loom_cli.delegated_payload = original

    def test_help_exposes_agent_safe_output_contract(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = loom_cli.handle_help(["--json"])

        payload = json.loads(stream.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["output_modes"]["stdout_budget_bytes_default"], loom_cli.DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES)
        self.assertEqual(payload["output_modes"]["summary_target_bytes_default"], loom_cli.DEFAULT_AGENT_SAFE_SUMMARY_TARGET_BYTES)
        by_command = {entry["command"]: entry for entry in payload["commands"]}
        self.assertEqual(by_command["build"]["output_policy"]["full_output_flag"], "--full-output")
        self.assertEqual(by_command["gate pr"]["output_policy"]["full_output_flag"], "--full-output")
        self.assertTrue(by_command["build"]["output_policy"]["artifact_on_over_budget"])


if __name__ == "__main__":
    unittest.main()
