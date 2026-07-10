#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

spec = importlib.util.spec_from_file_location("skills_surface", TOOLS_ROOT / "skills_surface.py")
assert spec is not None
skills_surface = importlib.util.module_from_spec(spec)
sys.modules["skills_surface"] = skills_surface
assert spec.loader is not None
spec.loader.exec_module(skills_surface)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class SkillReferenceIntegrityTest(unittest.TestCase):
    def test_reference_scanner_detects_base_and_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            package_root = Path(tempdir) / "loom-story"
            runtime_root = package_root / ".loom-runtime"

            write_text(
                package_root / "notes" / "SKILL.md",
                "# Story\n"
                "- Valid runtime reference: [runtime route-matrix](../.loom-runtime/route-matrix.md)\n",
            )
            write_text(
                package_root / "contract.json",
                '{"upstream":"../outside.json"}',
            )
            write_text(
                package_root / "notes" / "config.json",
                '{"runtime":"../.loom-runtime/missing-runtime-copy.json"}',
            )
            write_text(runtime_root / "route-matrix.md", "# runtime route matrix")
            errors = skills_surface.assert_no_package_external_links(package_root, runtime_root)
            self.assertTrue(any("outside" in error for error in errors), f"expected outside reference error: {errors}")
            self.assertTrue(any("missing" in error for error in errors), f"expected missing target error: {errors}")

    def test_reference_scanner_treats_runtime_base_links_as_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            package_root = Path(tempdir) / "loom-story"
            runtime_root = package_root / ".loom-runtime"
            write_text(
                package_root / "notes" / "SKILL.md",
                "# Story\nSee [route-matrix](../.loom-runtime/route-matrix.md)\n",
            )
            write_text(runtime_root / "route-matrix.md", "# route matrix")
            errors = skills_surface.assert_no_package_external_links(package_root, runtime_root)
            self.assertEqual(errors, [])

    def test_reference_scanner_checks_root_runtime_rewrites(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            package_root = Path(tempdir) / "loom-review"
            runtime_root = package_root / ".loom-runtime"
            write_text(
                package_root / "SKILL.md",
                "# Review\n"
                "- [route matrix](.loom-runtime/route-matrix.md)\n"
                "- [missing runtime](.loom-runtime/missing-runtime-copy.md)\n",
            )
            write_text(
                package_root / "contract.json",
                '{"routing":{"reference":".loom-runtime/route-matrix.md"},'
                '"installation":{"registry":".loom-runtime/missing-registry.json"},'
                '"role":"scenario/review"}',
            )
            write_text(runtime_root / "route-matrix.md", "# route matrix")
            errors = skills_surface.assert_no_package_external_links(package_root, runtime_root)
            self.assertTrue(any("missing-runtime-copy.md" in error for error in errors), errors)
            self.assertTrue(any("missing-registry.json" in error for error in errors), errors)
            self.assertFalse(any("scenario/review" in error for error in errors), errors)

    def test_reference_copy_parity_matches_source_install_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            source_root = Path(tempdir) / "src_skills"
            package_root = Path(tempdir) / "install_skills"
            runtime_root = package_root / "loom-story" / ".loom-runtime"
            for name in skills_surface.RUNTIME_COPY_PARITY_FILES:
                write_text(source_root / name, f"source:{name}")
                write_text(package_root / name, f"source:{name}")
                write_text(runtime_root / name, f"source:{name}")

            install_errors = skills_surface.compare_source_install_runtime_parity(source_root, package_root)
            self.assertEqual(install_errors, [])
            runtime_errors = skills_surface.validate_reference_copy_parity(
                source_root,
                package_root / "loom-story",
                runtime_root,
            )
            self.assertEqual(runtime_errors, [])

            write_text(runtime_root / "route-matrix.md", "drift")
            runtime_errors = skills_surface.validate_reference_copy_parity(
                source_root,
                package_root / "loom-story",
                runtime_root,
            )
            self.assertTrue(
                any("runtime parity drift for route-matrix.md" in error for error in runtime_errors),
                runtime_errors,
            )


if __name__ == "__main__":
    unittest.main()
