#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/skills/shared/scripts"
sys.path.insert(0, str(RUNTIME))

import loom_init
import loom_status


def string_values(value: object) -> list[str]:
    if isinstance(value, dict):
        return [text for child in value.values() for text in string_values(child)]
    if isinstance(value, list):
        return [text for child in value for text in string_values(child)]
    return [value] if isinstance(value, str) else []


class DerivedStateBootstrapTest(unittest.TestCase):
    def test_unrequested_full_bootstrap_uses_host_derived_light_profile(self) -> None:
        self.assertEqual(
            loom_init.scaffold_profile_key("full-bootstrap", {}),
            "light-governance",
        )
        self.assertEqual(
            loom_init.effective_adoption_intent("full-bootstrap", {}),
            "light-governance",
        )
        self.assertEqual(
            loom_init.scaffold_profile_key(
                "full-bootstrap", {"adoption_intent": "execution-control"}
            ),
            "execution-control",
        )

    def test_ordinary_profiles_do_not_declare_execution_state_carriers(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            for profile in ("light-governance", "attach-only"):
                artifacts = loom_init.initial_artifacts(
                    root,
                    False,
                    "full-bootstrap" if profile == "light-governance" else "deep-existing-repo",
                    profile,
                    True,
                )
                paths = {str(item["path"]) for item in artifacts}
                self.assertIn(".loom/bootstrap/manifest.json", paths)
                self.assertNotIn(".loom/bootstrap/init-result.json", paths)
                self.assertNotIn(".loom/status/current.md", paths)
                self.assertFalse(any(path.startswith(".loom/shadow/") for path in paths))

    def test_bootstrap_manifest_is_small_portable_locator_contract(self) -> None:
        payload = loom_init.manifest_payload(
            {
                "scaffold_profile": {"name": "light-governance"},
                "recommended_adoption": {
                    "capabilities": [{"name": "minimal-governance-entry"}]
                },
                "initial_artifacts": [
                    {"path": ".loom/bootstrap/manifest.json"},
                    {"path": ".loom/companion/repo-interface.json"},
                ],
            }
        )

        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "profile",
                "repository_locator",
                "companion_locator",
                "capabilities",
                "artifact_locators",
            },
        )
        self.assertEqual(payload["repository_locator"], ".")
        self.assertNotIn("runtime_state", payload)
        self.assertFalse(
            any(Path(value).is_absolute() for value in string_values(payload)),
            json.dumps(payload, ensure_ascii=False),
        )

    def test_manifest_validator_rejects_types_fake_root_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            parent = Path(tempdir)
            root = parent / "repo"
            outside = parent / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "interop.json").write_text("{}\n", encoding="utf-8")
            (root / "escape").symlink_to(outside, target_is_directory=True)
            payload = {
                "schema_version": "loom-bootstrap-manifest/v2",
                "profile": "light-governance",
                "repository_locator": "nested",
                "companion_locator": "escape/interop.json",
                "capabilities": "not-a-list",
                "artifact_locators": ["escape/interop.json"],
            }

            errors = loom_init.validate_host_derived_manifest(root, payload)

            self.assertTrue(any("repository_locator" in error for error in errors), errors)
            self.assertTrue(any("capabilities" in error for error in errors), errors)
            self.assertTrue(any("inside the target repository" in error for error in errors), errors)
            unknown = dict(payload)
            unknown["repository_locator"] = "."
            unknown["companion_locator"] = "."
            unknown["artifact_locators"] = []
            unknown["capabilities"] = ["unknown-capability"]
            self.assertTrue(
                any(
                    "unsupported capability" in error
                    for error in loom_init.validate_host_derived_manifest(root, unknown)
                )
            )
            unknown["unexpected"] = True
            self.assertTrue(
                any(
                    "keys must exactly match" in error
                    for error in loom_init.validate_host_derived_manifest(root, unknown)
                )
            )

    def test_corrupt_manifest_never_falls_back_to_stale_legacy_carriers(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / ".loom/bootstrap").mkdir(parents=True)
            (root / ".loom/bootstrap/init-result.json").write_text("{}\n", encoding="utf-8")
            (root / ".loom/status").mkdir(parents=True)
            (root / ".loom/status/current.md").write_text("stale\n", encoding="utf-8")

            cases = (("{broken\n", "invalid JSON"), ('{"schema_version":"unknown"}\n', "unsupported"))
            for content, expected in cases:
                with self.subTest(expected=expected):
                    (root / ".loom/bootstrap/manifest.json").write_text(content, encoding="utf-8")
                    completed = subprocess.run(
                        [sys.executable, str(RUNTIME / "loom_status.py"), "--target", str(root)],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    payload = json.loads(completed.stdout)

                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(payload["result"], "block")
                    self.assertIn(expected, " ".join(payload["missing_inputs"]))
                    self.assertNotIn("fact-chain", json.dumps(payload))

    def test_explicit_item_requires_matching_open_work_item_and_pr_binding(self) -> None:
        original = loom_status.github_status_payload
        root = ROOT
        base_args = {
            "item": "MC-and-his-Agents/Loom/work_item/2041",
            "issue": 2041,
            "pr": None,
            "owner": "MC-and-his-Agents",
            "repo_name": "Loom",
        }
        cases = [
            ({"issue": {"number": 2042, "state": "OPEN", "labels": ["work-item"]}, "pr": None}, "does not match", 2042),
            ({"issue": {"number": 2041, "state": "OPEN", "labels": ["fr"]}, "pr": None}, "not uniquely typed", 2041),
            ({"issue": {"number": 2041, "state": "CLOSED", "labels": ["work-item"]}, "pr": None}, "not open", 2041),
            (
                {
                    "issue": {"number": 2041, "state": "OPEN", "labels": ["work-item"]},
                    "pr": {"number": 99, "body": "Loom Work Item: MC-and-his-Agents/Loom/work_item/9999"},
                },
                "not bound",
                2041,
            ),
        ]
        try:
            for index, (github, expected, issue_number) in enumerate(cases):
                with self.subTest(case=index):
                    args = argparse.Namespace(**base_args)
                    args.issue = issue_number
                    if github.get("pr") is not None:
                        args.pr = 99
                    loom_status.github_status_payload = lambda *_args, _github=github, **_kwargs: (_github, [])
                    payload = loom_status.host_derived_status_payload(
                        root,
                        manifest={"profile": "light-governance"},
                        runtime_state={"result": "pass"},
                        args=args,
                    )
                    self.assertEqual(payload["result"], "block")
                    self.assertIn(expected, " ".join(payload["missing_inputs"]))
                    self.assertNotEqual(payload["item"]["source"], "github_host_readback")
        finally:
            loom_status.github_status_payload = original

    def test_pr_binding_accepts_standard_and_machine_metadata_and_rejects_conflict(self) -> None:
        original = loom_status.github_status_payload
        item = "MC-and-his-Agents/Loom/work_item/2041"
        args = argparse.Namespace(
            item=item,
            issue=2041,
            pr=99,
            owner="MC-and-his-Agents",
            repo_name="Loom",
        )
        machine = (
            "<!-- loom:repo-pr-metadata\n"
            '{"metadata_contract_id":"loom-governance-intensity","fields":'
            f'{{"work_item_locator":"{item}"}}}}\n'
            "-->"
        )
        bodies = (
            (f"## Related Work\n- Work Item: {item}\n", "pass"),
            (machine, "pass"),
            (f"- Work Item: {item}\n" + machine.replace(item, "MC-and-his-Agents/Loom/work_item/9999"), "block"),
            ("- Work Item: garbage\n" + machine, "block"),
            ("- Work Item: OTHER/Repo/work_item/9999\n" + machine, "block"),
            (f"- Work Item: {item}\n" + machine.replace(item, "garbage"), "block"),
            (f"- Work Item: {item}\n" + machine.replace(item, "OTHER/Repo/work_item/9999"), "block"),
        )
        try:
            for body, expected in bodies:
                with self.subTest(expected=expected, body=body[:30]):
                    github = {
                        "issue": {"number": 2041, "state": "OPEN", "labels": ["work-item"]},
                        "pr": {"number": 99, "body": body},
                    }
                    loom_status.github_status_payload = lambda *_args, _github=github, **_kwargs: (_github, [])
                    payload = loom_status.host_derived_status_payload(
                        ROOT,
                        manifest={"profile": "light-governance"},
                        runtime_state={"result": "pass"},
                        args=args,
                    )
                    self.assertEqual(payload["result"], expected, payload)
        finally:
            loom_status.github_status_payload = original

    def test_default_written_fixture_contains_no_runtime_snapshot_or_machine_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNTIME / "loom_init.py"),
                    "bootstrap",
                    "--target",
                    str(root),
                    "--scenario",
                    "new",
                    "--write",
                    "--force",
                    "--portable-output",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertFalse((root / ".loom/bootstrap/init-result.json").exists())
            self.assertFalse((root / ".loom/status/current.md").exists())
            self.assertFalse((root / ".loom/shadow").exists())
            self.assertEqual(
                loom_init.verify_target(root, root / ".loom/bootstrap/init-result.json"),
                [],
            )
            generated = "\n".join(
                path.read_text(encoding="utf-8")
                for path in root.rglob("*")
                if path.is_file() and ".git" not in path.parts
            )
            self.assertNotIn(str(root), generated)
            self.assertNotIn("/Users/", generated)
            self.assertNotIn("C:\\Users\\", generated)

            build = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/loom.py"),
                    "build",
                    "--target",
                    str(root),
                    "--item",
                    "WI-2041",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            build_payload = json.loads(build.stdout)
            diagnostics = json.dumps(build_payload, ensure_ascii=False)
            self.assertIn(build_payload["result"], {"pass", "block"})
            self.assertNotIn("status/current.md", diagnostics)
            self.assertNotIn("init-result.json", diagnostics)
            self.assertNotIn(".loom/shadow", diagnostics)

            fake_item = subprocess.run(
                [
                    sys.executable,
                    str(RUNTIME / "loom_status.py"),
                    "--target",
                    str(root),
                    "--item",
                    "DOES-NOT-EXIST",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            fake_payload = json.loads(fake_item.stdout)
            self.assertNotEqual(fake_item.returncode, 0)
            self.assertEqual(fake_payload["result"], "block")
            self.assertIn("canonical owner/repo/work_item/id", " ".join(fake_payload["missing_inputs"]))

            closeout = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/loom.py"),
                    "closeout",
                    "--target",
                    str(root),
                    "--item",
                    "WI-2041",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            closeout_payload = json.loads(closeout.stdout)
            closeout_diagnostics = json.dumps(closeout_payload, ensure_ascii=False)
            self.assertNotIn("status/current.md", closeout_diagnostics)
            self.assertNotIn("current-retire", closeout_diagnostics)

    def test_host_closeout_has_no_current_retire_surface(self) -> None:
        closeout_source = (RUNTIME / "closeout_flow.py").read_text(encoding="utf-8")
        host_source = (RUNTIME / "github_host.py").read_text(encoding="utf-8")
        self.assertNotIn(".loom/status/current.md", closeout_source)
        self.assertNotIn(".loom/status/current.md", host_source)
        self.assertNotIn("current-retire", closeout_source)

    def test_parallel_worktree_ignores_stale_committed_current(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir) / "repo"
            linked = Path(tempdir) / "linked"
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "loom@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Loom Fixture"], check=True)
            (root / "README.md").write_text("fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "worktree", "add", "-qb", "work/parallel", str(linked)],
                check=True,
            )
            bootstrap = linked / ".loom/bootstrap"
            bootstrap.mkdir(parents=True)
            companion = linked / ".loom/companion"
            companion.mkdir(parents=True)
            (companion / "repo-interface.json").write_text("{}\n", encoding="utf-8")
            (bootstrap / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "loom-bootstrap-manifest/v2",
                        "profile": "light-governance",
                        "repository_locator": ".",
                        "companion_locator": ".loom/companion/repo-interface.json",
                        "capabilities": [],
                        "artifact_locators": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            status = linked / ".loom/status"
            status.mkdir(parents=True)
            (status / "current.md").write_text("stale item from another worktree\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(RUNTIME / "loom_status.py"), "--target", str(linked)],
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(payload["result"], "pass")
            self.assertFalse(payload["committed_execution_state"]["current_status_consumed"])
            self.assertEqual(payload["worktree"]["source"], "git_worktree_readback")
            self.assertEqual(payload["worktree"]["branch"], "work/parallel")
            expected_head = subprocess.check_output(
                ["git", "-C", str(linked), "rev-parse", "HEAD"], text=True
            ).strip()
            self.assertEqual(payload["worktree"]["head_sha"], expected_head)
            self.assertEqual(payload["provenance"][0]["authority"], "git_worktree_readback")


if __name__ == "__main__":
    unittest.main()
