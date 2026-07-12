from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_distribution


class BuildDistributionSafetyTest(unittest.TestCase):
    def test_rejects_repository_source_and_unowned_outputs(self) -> None:
        for output in (ROOT, ROOT / "src", ROOT / "skills"):
            with self.subTest(output=output), self.assertRaises(RuntimeError):
                build_distribution.build(output)
        with self.assertRaises(RuntimeError):
            build_distribution.build(Path(tempfile.gettempdir()))
        with tempfile.TemporaryDirectory() as tmp:
            occupied = Path(tmp) / "occupied"
            occupied.mkdir()
            (occupied / "user.txt").write_text("keep\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                build_distribution.build(occupied)
            self.assertEqual((occupied / "user.txt").read_text(encoding="utf-8"), "keep\n")

    def test_rejects_symlink_escape_and_manifest_inventory_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / "outside"
            outside.mkdir()
            link = ROOT / "build" / "unsafe-distribution-link"
            link.parent.mkdir(exist_ok=True)
            try:
                link.symlink_to(outside, target_is_directory=True)
                with self.assertRaises(RuntimeError):
                    build_distribution.build(link)
            finally:
                link.unlink(missing_ok=True)

            output = base / "distribution"
            build_distribution.build(output)
            (output / "rogue.py").write_text("pass\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                build_distribution.materialize(output, "package")

    def test_clean_refuses_tampered_materialization(self) -> None:
        output = ROOT / "build" / "distribution-safety-test"
        build_distribution.build(output)
        build_distribution.materialize(output, "package")
        generated = ROOT / "skills" / "shared" / "scripts" / "loom_flow.py"
        original = generated.read_bytes()
        try:
            generated.write_bytes(original + b"\n# concurrent change\n")
            with self.assertRaises(RuntimeError):
                build_distribution.clean_materialized("package")
        finally:
            generated.write_bytes(original)
            build_distribution.clean_materialized("package")
            if output.exists():
                import shutil

                shutil.rmtree(output)

    def test_receipt_rejects_unknown_fields(self) -> None:
        output = ROOT / "build" / "distribution-receipt-test"
        build_distribution.build(output)
        build_distribution.materialize(output, "package")
        receipt_path = build_distribution.package_receipt_path(ROOT / "skills")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["unexpected"] = True
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        try:
            with self.assertRaises(RuntimeError):
                build_distribution.clean_materialized("package")
        finally:
            receipt.pop("unexpected")
            receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            build_distribution.clean_materialized("package")
            if output.exists():
                import shutil

                shutil.rmtree(output)

    def test_runtime_rematerialize_refuses_modified_or_unknown_files(self) -> None:
        output = ROOT / "build" / "distribution-runtime-safety-test"
        build_distribution.build(output)
        build_distribution.materialize(output, "repo-fixtures")
        runtime_root = ROOT / ".loom" / "bin"
        generated = runtime_root / "loom_flow.py"
        original = generated.read_bytes()
        try:
            generated.write_bytes(original + b"\n# concurrent change\n")
            with self.assertRaises(RuntimeError):
                build_distribution.materialize(output, "repo-fixtures")
            generated.write_bytes(original)
            rogue = runtime_root / "rogue.py"
            rogue.write_text("pass\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                build_distribution.materialize(output, "repo-fixtures")
            rogue.unlink()
        finally:
            generated.write_bytes(original)
            build_distribution.clean_materialized("repo-fixtures")
            if output.exists():
                import shutil

                shutil.rmtree(output)


if __name__ == "__main__":
    unittest.main()
