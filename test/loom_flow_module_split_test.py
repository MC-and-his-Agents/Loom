#!/usr/bin/env python3

from __future__ import annotations

import ast
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/skills/shared/scripts"
sys.path.insert(0, str(RUNTIME))

import companion_contract
import closeout_flow
import delivery_control
import execution_flow
import flow_runtime
import host_profile
import live_smoke
import loom_flow
import review_flow


class LoomFlowModuleSplitTest(unittest.TestCase):
    DISPATCH_ASSIGNMENTS = {
        "AUTHORITATIVE_REVIEW_ADAPTERS",
        "CLOSEOUT_GATE_PROFILES",
        "CLOSEOUT_PR_ROLES",
        "CODEX_APP_REVIEW_ADAPTER",
        "CODEX_APP_REVIEW_CWD_ENV",
        "CODEX_APP_REVIEW_ENDPOINT_ENV",
        "CODEX_APP_REVIEW_SHADOW_ADAPTER",
        "CODEX_APP_REVIEW_THREAD_ID_ENV",
        "CODEX_THREAD_ID_ENV",
        "DEFAULT_REVIEW_ADAPTER",
        "GOVERNANCE_CAPABILITY_MODES",
        "GOVERNANCE_CHANGE_CLASS_VALUES",
        "GOVERNANCE_HOST_READBACK_REVIEW_REQUIREMENT",
        "GOVERNANCE_INTENSITY_VALUES",
        "GOVERNANCE_RELEASE_JUDGMENT_VALUES",
        "GOVERNANCE_REVIEW_REQUIREMENT_VALUES",
        "GOVERNANCE_SUITE_PATH_VALUES",
        "REVIEW_DECISIONS",
        "REVIEW_ENGINE_PROFILE_IDS",
        "REVIEW_ENGINE_REASONING_EFFORTS",
        "REVIEW_KINDS",
        "SHADOW_PARITY_SURFACES",
        "SHADOW_REVIEW_ADAPTERS",
        "TERMINAL_CLOSEOUT_STATES",
        "_COMPAT_MODULES",
    }

    def test_live_smoke_implementation_is_outside_dispatch_module(self) -> None:
        tree = ast.parse((RUNTIME / "loom_flow.py").read_text(encoding="utf-8"))
        definitions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }

        self.assertEqual(definitions, {"__getattr__", "parse_args", "main"})
        self.assertTrue(callable(live_smoke.handle_live_smoke))
        self.assertTrue(callable(live_smoke.live_smoke_run_payload))

    def test_legacy_domain_symbols_remain_available_from_dispatch_module(self) -> None:
        live_smoke_symbols = {
            name
            for name, value in vars(live_smoke).items()
            if not name.startswith("_")
            and (name.isupper() or callable(value))
            and getattr(value, "__module__", live_smoke.__name__) == live_smoke.__name__
        }
        migrated_constants = {
            "ENGINE_FAILURE_REASONS",
            "HOST_API_TOKEN_BRIDGE_COMMAND",
            "HOST_API_TOKEN_BRIDGE_NEXT_ACTION",
            "PROJECT_DRIFT_KINDS",
            "WORK_ITEM_FIELD_LABELS",
        }

        self.assertIn("LIVE_SMOKE_SCHEMA", live_smoke_symbols)
        self.assertIn("live_smoke_run_payload", live_smoke_symbols)
        for name in live_smoke_symbols | migrated_constants:
            self.assertTrue(hasattr(loom_flow, name), name)

    def test_dispatch_module_has_no_domain_assignments(self) -> None:
        tree = ast.parse((RUNTIME / "loom_flow.py").read_text(encoding="utf-8"))
        assignments = set()
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                assignments.update(target.id for target in targets if isinstance(target, ast.Name))

        self.assertEqual(assignments, self.DISPATCH_ASSIGNMENTS)

    def test_domain_modules_do_not_import_dispatch_module(self) -> None:
        modules = (
            companion_contract,
            closeout_flow,
            delivery_control,
            execution_flow,
            flow_runtime,
            host_profile,
            live_smoke,
            review_flow,
        )
        for module in modules:
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            imports = {
                node.module
                for node in tree.body
                if isinstance(node, ast.ImportFrom)
            }
            self.assertNotIn("loom_flow", imports, module.__name__)

        self.assertTrue(callable(delivery_control.handle_pr_gate))
        self.assertTrue(callable(host_profile.handle_governance_profile))
        self.assertTrue(callable(review_flow.handle_review))
        self.assertTrue(callable(closeout_flow.handle_closeout))
        self.assertTrue(callable(execution_flow.handle_flow))

    def test_missing_target_keeps_public_schema_and_exit_code(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RUNTIME / "loom_flow.py"), "live-smoke", "run"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["schema_version"], live_smoke.LIVE_SMOKE_SCHEMA)
        self.assertEqual(payload["result"], "block")
        self.assertEqual(payload["fallback_to"], live_smoke.LIVE_SMOKE_CONFIG_FALLBACK)

    def test_shared_runtime_emit_and_target_resolution_keep_contract(self) -> None:
        previous = os.environ.get("LOOM_INVOCATION_CWD")
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                os.environ["LOOM_INVOCATION_CWD"] = tempdir
                self.assertEqual(flow_runtime.resolve_target_arg("repo"), Path(tempdir, "repo").resolve())
            output = io.StringIO()
            with redirect_stdout(output):
                code = flow_runtime.emit({"result": "pass", "value": 1})
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue()), {"result": "pass", "value": 1})
        finally:
            if previous is None:
                os.environ.pop("LOOM_INVOCATION_CWD", None)
            else:
                os.environ["LOOM_INVOCATION_CWD"] = previous

    def test_companion_tool_filter_preserves_blocking_semantics(self) -> None:
        payload = companion_contract.tool_availability_for_surface(
            {
                "tool_availability": {
                    "declared_tools": [
                        {"id": "required", "surface": "review", "status": "failed", "result": "block", "missing_inputs": ["token"], "fallback_to": "build"},
                        {"id": "other", "surface": "closeout", "status": "failed", "result": "block"},
                    ]
                }
            },
            surface="review",
        )

        self.assertEqual(payload["result"], "block")
        self.assertEqual([entry["id"] for entry in payload["blocking_tools"]], ["required"])
        self.assertEqual(payload["missing_inputs"], ["token"])
        self.assertEqual(payload["fallback_to"], "build")


if __name__ == "__main__":
    unittest.main()
