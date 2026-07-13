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
import execution_attempts
import execution_flow
import flow_runtime
import github_host
import host_profile
import live_smoke
import loom_flow
import review_flow


class LoomFlowModuleSplitTest(unittest.TestCase):
    DOMAIN_MODULES = {
        "closeout_flow",
        "delivery_control",
        "execution_flow",
        "host_profile",
        "live_smoke",
        "review_flow",
    }
    RUNTIME_MODULES = DOMAIN_MODULES | {"execution_attempts", "flow_runtime", "github_host"}
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

    def test_parser_and_dispatch_are_thin_and_have_declared_domain_owners(self) -> None:
        tree = ast.parse((RUNTIME / "loom_flow.py").read_text(encoding="utf-8"))
        allowed_imports = self.RUNTIME_MODULES | {"__future__", "argparse", "pathlib", "re", "sys", "tomllib", "typing"}
        imported_modules = {
            imported
            for node in ast.walk(tree)
            for imported in (
                [node.module] if isinstance(node, ast.ImportFrom) and node.module else
                [alias.name for alias in node.names] if isinstance(node, ast.Import) else
                []
            )
        }
        self.assertLessEqual(imported_modules, allowed_imports)
        expressions = [node for node in tree.body if isinstance(node, ast.Expr)]
        self.assertEqual(len(expressions), 1)
        self.assertIsInstance(expressions[0].value, ast.Constant)
        self.assertIsInstance(expressions[0].value.value, str)

        imported_handlers = {
            alias.asname or alias.name: node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        parser = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "parse_args")
        parser_variables = {
            target.id
            for node in ast.walk(parser)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "subparsers"
            and node.value.func.attr == "add_parser"
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        commands = {
            node.args[0].value
            for node in ast.walk(parser)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subparsers"
            and node.func.attr == "add_parser"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        }
        for call in (node for node in ast.walk(parser) if isinstance(node, ast.Call)):
            function = call.func
            if isinstance(function, ast.Name):
                self.assertIn(function.id, {"sorted", "tuple"})
                continue
            self.assertIsInstance(function, ast.Attribute)
            self.assertIsInstance(function.value, ast.Name)
            owner, operation = function.value.id, function.attr
            allowed = (
                (owner == "argparse" and operation == "ArgumentParser")
                or (owner == "parser" and operation in {"add_subparsers", "parse_args"})
                or (owner == "subparsers" and operation == "add_parser")
                or (owner in parser_variables and operation == "add_argument")
            )
            self.assertTrue(allowed, f"parse_args owns non-parser call: {owner}.{operation}")

        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        call_nodes = [node for node in ast.walk(main) if isinstance(node, ast.Call)]
        for call in call_nodes:
            self.assertIsInstance(call.func, ast.Name, "main may only call parse_args or a declared domain handler")
        main_calls = [node.func.id for node in call_nodes]
        self.assertEqual(main_calls.count("parse_args"), 1)
        handlers = [name for name in main_calls if name != "parse_args"]
        self.assertEqual(len(handlers), len(commands))
        self.assertEqual(len(handlers), len(set(handlers)))
        for handler in handlers:
            self.assertIn(imported_handlers.get(handler), self.DOMAIN_MODULES, handler)

        compat = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "__getattr__")
        compat_call_nodes = [node for node in ast.walk(compat) if isinstance(node, ast.Call)]
        for call in compat_call_nodes:
            self.assertIsInstance(call.func, ast.Name, "__getattr__ may only perform direct compatibility lookups")
        compat_calls = {node.func.id for node in compat_call_nodes}
        self.assertLessEqual(compat_calls, {"AttributeError", "getattr", "hasattr"})

    def test_domain_modules_do_not_import_dispatch_module(self) -> None:
        modules = (
            companion_contract,
            closeout_flow,
            delivery_control,
            execution_attempts,
            execution_flow,
            flow_runtime,
            github_host,
            host_profile,
            live_smoke,
            review_flow,
        )
        for module in modules:
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            imports = {
                imported
                for node in ast.walk(tree)
                for imported in (
                    [node.module] if isinstance(node, ast.ImportFrom) and node.module else
                    [alias.name for alias in node.names] if isinstance(node, ast.Import) else
                    []
                )
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
