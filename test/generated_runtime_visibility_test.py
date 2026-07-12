#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/skills/shared/scripts"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(RUNTIME))

import build_distribution
import loom_init


class GeneratedRuntimeVisibilityTest(unittest.TestCase):
    def make_repo(self, parent: Path) -> tuple[Path, dict[str, object]]:
        output = parent / "distribution"
        build_distribution.build(output)
        repo = parent / "repo"
        runtime = repo / ".loom/bin"
        runtime.mkdir(parents=True)
        for name in build_distribution.RUNTIME_NAMES:
            shutil.copy2(output / "repo-runtime" / name, runtime / name)
        shutil.copy2(output / "manifest.json", runtime / build_distribution.RUNTIME_MANIFEST_NAME)
        bootstrap = repo / ".loom/bootstrap"
        bootstrap.mkdir(parents=True)
        (bootstrap / "init-result.json").write_text("{}\n", encoding="utf-8")
        (repo / ".gitignore").write_text(".loom/bin/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "-f", ".loom/bootstrap/init-result.json", ".gitignore"], check=True)
        result = {
            "scaffold_profile": {"name": "execution-control"},
            "required_carriers": [
                {"path": relative, "kind": "loom-tool", "owner": "loom-runtime"}
                for relative in loom_init.RUNTIME_ARTIFACT_SOURCES
            ],
        }
        return repo, result

    def test_ignored_generated_runtime_passes_with_canonical_manifest_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo, result = self.make_repo(Path(tempdir))

            report = loom_init.stable_carrier_git_visibility(repo, result)

            self.assertEqual(report["result"], "pass", report)
            runtime_rows = [row for row in report["checked"] if row["path"].startswith(".loom/bin/")]
            self.assertEqual(len(runtime_rows), len(build_distribution.RUNTIME_NAMES))
            self.assertTrue(all(row["status"] == "generated" for row in runtime_rows), runtime_rows)
            manifest = json.loads(
                (repo / ".loom/bin" / build_distribution.RUNTIME_MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["output_root"], ".")
            self.assertNotIn(str(Path(tempdir)), json.dumps(manifest))

    def test_generated_runtime_fails_closed_on_drift_missing_unknown_and_manifest_tamper(self) -> None:
        mutations = ("drift", "missing", "unknown", "manifest")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tempdir:
                repo, result = self.make_repo(Path(tempdir))
                runtime = repo / ".loom/bin"
                if mutation == "drift":
                    (runtime / "loom_status.py").write_text("drift\n", encoding="utf-8")
                elif mutation == "missing":
                    (runtime / "loom_status.py").unlink()
                elif mutation == "unknown":
                    (runtime / "unknown.py").write_text("unknown\n", encoding="utf-8")
                else:
                    manifest_path = runtime / build_distribution.RUNTIME_MANIFEST_NAME
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest["aggregate_sha256"] = "0" * 64
                    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

                report = loom_init.stable_carrier_git_visibility(repo, result)

                self.assertEqual(report["result"], "block", report)
                self.assertTrue(report["blocking_errors"], report)


if __name__ == "__main__":
    unittest.main()
