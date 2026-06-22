#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"

spec = importlib.util.spec_from_file_location("check_npm_package", TOOLS_ROOT / "check_npm_package.py")
assert spec is not None
check_npm_package = importlib.util.module_from_spec(spec)
sys.modules["check_npm_package"] = check_npm_package
assert spec.loader is not None
spec.loader.exec_module(check_npm_package)


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


class PluginPayloadHashTest(unittest.TestCase):
    def test_hash_changes_when_payload_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = Path(tempdir) / "plugins" / "loom"
            write_bytes(payload / ".codex-plugin" / "plugin.json", b'{"name":"loom"}\n')
            write_bytes(payload / "skills" / "loom-init" / "SKILL.md", b"initial\n")

            before = check_npm_package.compute_plugin_payload_hash(payload)["digest"]
            write_bytes(payload / "skills" / "loom-init" / "SKILL.md", b"changed\n")
            after = check_npm_package.compute_plugin_payload_hash(payload)["digest"]

            self.assertNotEqual(before, after)

    def test_hash_is_independent_of_filesystem_creation_order(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            first = Path(tempdir) / "first"
            second = Path(tempdir) / "second"

            write_bytes(first / "b.txt", b"b\n")
            write_bytes(first / "a.txt", b"a\n")
            write_bytes(second / "a.txt", b"a\n")
            write_bytes(second / "b.txt", b"b\n")

            first_hash = check_npm_package.compute_plugin_payload_hash(first)
            second_hash = check_npm_package.compute_plugin_payload_hash(second)

            self.assertEqual(first_hash["files"], ["a.txt", "b.txt"])
            self.assertEqual(second_hash["files"], ["a.txt", "b.txt"])
            self.assertEqual(first_hash["digest"], second_hash["digest"])

    def test_hash_ignores_os_and_python_cache_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = Path(tempdir) / "payload"
            write_bytes(payload / "skills" / "loom-init" / "SKILL.md", b"stable\n")

            before = check_npm_package.compute_plugin_payload_hash(payload)
            write_bytes(payload / ".DS_Store", b"finder\n")
            write_bytes(payload / "skills" / "__pycache__" / "cache.pyc", b"cache\n")
            write_bytes(payload / "skills" / "loom-init" / "runtime.pyc", b"cache\n")
            after = check_npm_package.compute_plugin_payload_hash(payload)

            self.assertEqual(before["files"], ["skills/loom-init/SKILL.md"])
            self.assertEqual(after["files"], ["skills/loom-init/SKILL.md"])
            self.assertEqual(before["digest"], after["digest"])

    def test_manifest_hash_field_is_self_reference_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = Path(tempdir) / "plugins" / "loom"
            manifest = payload / ".codex-plugin" / "plugin.json"
            write_bytes(
                manifest,
                b'{\n  "name": "loom",\n  "x-loom": {\n    "plugin_payload_hash": "first"\n  }\n}\n',
            )
            write_bytes(payload / "skills" / "loom-init" / "SKILL.md", b"stable\n")

            before = check_npm_package.compute_plugin_payload_hash(payload)
            write_bytes(
                manifest,
                b'{\n  "name": "loom",\n  "x-loom": {\n    "plugin_payload_hash": "second"\n  }\n}\n',
            )
            after = check_npm_package.compute_plugin_payload_hash(payload)

            self.assertEqual(before["digest"], after["digest"])
            self.assertEqual(before["normalized_self_references"], [".codex-plugin/plugin.json"])

    def test_manifest_other_metadata_changes_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            payload = Path(tempdir) / "plugins" / "loom"
            manifest = payload / ".codex-plugin" / "plugin.json"
            write_bytes(
                manifest,
                b'{\n  "name": "loom",\n  "x-loom": {\n    "plugin_payload_version": "0.18.0",\n    "plugin_payload_hash": "same"\n  }\n}\n',
            )

            before = check_npm_package.compute_plugin_payload_hash(payload)
            write_bytes(
                manifest,
                b'{\n  "name": "loom",\n  "x-loom": {\n    "plugin_payload_version": "0.19.0",\n    "plugin_payload_hash": "same"\n  }\n}\n',
            )
            after = check_npm_package.compute_plugin_payload_hash(payload)

            self.assertNotEqual(before["digest"], after["digest"])


if __name__ == "__main__":
    unittest.main()
