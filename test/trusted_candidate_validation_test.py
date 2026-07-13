#!/usr/bin/env python3
"""Security contracts for the base-owned candidate validation boundary."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_trusted_candidate_validation.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("trusted_candidate_validation", RUNNER)
    if spec is None or spec.loader is None:
        raise AssertionError("trusted candidate runner is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TrustedCandidateValidationTest(unittest.TestCase):
    def test_candidate_cannot_inject_python_startup_or_stdlib_modules(self) -> None:
        runner = load_runner()
        for relative, expected in (
            ("tools/sitecustomize.py", "tools/sitecustomize.py"),
            ("tools/usercustomize.py", "tools/usercustomize.py"),
            ("tools/json.py", "tools/json.py"),
            ("src/skills/shared/scripts/pathlib.py", "src/skills/shared/scripts/pathlib.py"),
            ("src/skills/shared/scripts/subprocess/__init__.py", "src/skills/shared/scripts/subprocess"),
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                trusted = root / "trusted"
                candidate = root / "candidate"
                path = candidate / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("raise SystemExit(0)\n", encoding="utf-8")
                self.assertEqual(runner.candidate_import_shadows(trusted, candidate), [expected])

    def test_candidate_mutation_of_base_owned_files_is_rejected(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trusted = root / "trusted"
            validation = root / "validation"
            for checkout in (trusted, validation):
                (checkout / "tools").mkdir(parents=True)
                (checkout / "Makefile").write_text("check:\n\t@true\n", encoding="utf-8")
            (validation / "Makefile").write_text("check:\n\t@false\n", encoding="utf-8")
            frozen = runner.freeze_base_owned_files(trusted)
            with self.assertRaisesRegex(ValueError, "modified base-owned validation files"):
                runner.verify_base_owned_files(frozen, validation)


if __name__ == "__main__":
    unittest.main()
