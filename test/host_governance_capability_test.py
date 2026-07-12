#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "src/skills/shared/scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))


def load_governance_surface():
    spec = importlib.util.spec_from_file_location("governance_surface", SHARED_SCRIPTS / "governance_surface.py")
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


governance_surface = load_governance_surface()


class HostGovernanceCapabilityTest(unittest.TestCase):
    def test_classifies_github_capability_read_failures(self) -> None:
        cases = {
            "HTTP 403: forbidden": "permission_denied",
            "HTTP 403: Resource not accessible by integration for rulesets": "ruleset_permission_denied",
            "rulesets are unavailable on this plan": "plan_unavailable",
            "HTTP 404: private repository not found": "private_repository_unreadable",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(governance_surface.classify_github_control_plane_error(message), expected)

    def test_detects_host_enforced_required_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            with (
                patch.object(governance_surface, "detect_github_repo", return_value=("acme", "repo")),
                patch.object(
                    governance_surface,
                    "gh_rest_json",
                    return_value=({"full_name": "acme/repo", "default_branch": "main"}, []),
                ),
                patch.object(
                    governance_surface,
                    "gh_json",
                    side_effect=[
                        (
                            {
                                "protected": True,
                                "protection": {
                                    "required_status_checks": {
                                        "contexts": list(governance_surface.GITHUB_STABLE_CHECK_NAMES)
                                    },
                                    "required_pull_request_reviews": {},
                                },
                            },
                            [],
                        ),
                        ({"workflows": []}, []),
                        ({"check_runs": []}, []),
                    ],
                ),
                patch.object(governance_surface, "gh_json_list", return_value=([], [])),
            ):
                surface, missing = governance_surface.detect_github_control_plane(root)

        self.assertEqual(missing, [])
        self.assertEqual(surface["host_governance_capability"]["status"], "host_enforced")
        self.assertEqual(surface["host_governance_capability"]["signals"]["pr_reviews"], "required")

    def test_distinguishes_unreadable_rulesets_from_unconfigured(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            with (
                patch.object(governance_surface, "detect_github_repo", return_value=("acme", "private-repo")),
                patch.object(
                    governance_surface,
                    "gh_rest_json",
                    return_value=({"full_name": "acme/private-repo", "default_branch": "main"}, []),
                ),
                patch.object(
                    governance_surface,
                    "gh_json",
                    side_effect=[
                        ({"protected": False}, []),
                        ({"workflows": []}, []),
                        ({"check_runs": []}, []),
                    ],
                ),
                patch.object(
                    governance_surface,
                    "gh_json_list",
                    return_value=([], ["HTTP 403: Resource not accessible by integration for rulesets"]),
                ),
            ):
                surface, missing = governance_surface.detect_github_control_plane(root)

        self.assertEqual(missing, [])
        diagnosis = surface["host_governance_capability"]
        self.assertEqual(diagnosis["status"], "unreadable")
        self.assertEqual(diagnosis["reason"], "ruleset_permission_denied")
        self.assertIn("private repository governance settings", diagnosis["setup_guidance"])


if __name__ == "__main__":
    unittest.main()
