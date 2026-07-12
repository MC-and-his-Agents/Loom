#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "src/skills/shared/scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

spec = importlib.util.spec_from_file_location("loom_flow", SHARED_SCRIPTS / "loom_flow.py")
assert spec is not None
loom_flow = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(loom_flow)


def write_idle_status(root: Path, *, init_result: str) -> None:
    (root / ".loom/status").mkdir(parents=True, exist_ok=True)
    labels = {
        "item_id": "Item ID",
        "goal": "Goal",
        "scope": "Scope",
        "execution_path": "Execution Path",
        "workspace_entry": "Workspace Entry",
        "recovery_entry": "Recovery Entry",
        "review_entry": "Review Entry",
        "validation_entry": "Validation Entry",
        "closing_condition": "Closing Condition",
        "current_checkpoint": "Current Checkpoint",
        "current_stop": "Current Stop",
        "next_step": "Next Step",
        "blockers": "Blockers",
        "latest_validation_summary": "Latest Validation Summary",
        "recovery_boundary": "Recovery Boundary",
        "current_lane": "Current Lane",
    }
    lines = ["# Status", "", "## Derived Fact Chain View", ""]
    for key, label in labels.items():
        value = "no_active_item" if key == "item_id" else "not_applicable"
        lines.append(f"- {label}: {value}")
    lines.extend(
        [
            "",
            "## Runtime Evidence",
            "",
            "- Run Entry: not_applicable",
            "- Logs Entry: not_applicable",
            "- Diagnostics Entry: not_applicable",
            "- Verification Entry: not_applicable",
            "- Lane Entry: not_applicable",
            "",
            "## Sources",
            "",
            "- Static Truth: not_applicable",
            "- Dynamic Truth: not_applicable",
            f"- Locator Truth: {init_result}",
            "- Fact Chain CLI: loom fact-chain --target . --json",
            "",
        ]
    )
    (root / ".loom/status/current.md").write_text("\n".join(lines), encoding="utf-8")


def write_idle_companion_init_result(root: Path) -> None:
    relative = ".loom/companion/init-result.json"
    (root / ".loom/companion").mkdir(parents=True, exist_ok=True)
    write_idle_status(root, init_result=relative)
    (root / relative).write_text(
        json.dumps(
            {
                "fact_chain": {
                    "mode": "idle",
                    "read_entry": "loom fact-chain --target . --json",
                    "entry_points": {
                        "current_item_id": "no_active_item",
                        "work_item": "not_applicable",
                        "recovery_entry": "not_applicable",
                        "status_surface": ".loom/status/current.md",
                    },
                }
            }
        ),
        encoding="utf-8",
    )


def write_work_item(
    root: Path,
    item_id: str,
    *,
    issue: int | None = None,
    artifacts: list[str] | None = None,
    metadata_issue: bool = True,
    recovery_issue: bool = True,
) -> None:
    (root / ".loom/work-items").mkdir(parents=True, exist_ok=True)
    (root / ".loom/progress").mkdir(parents=True, exist_ok=True)
    metadata_issue_text = (
        f"issue #{issue}" if issue is not None and metadata_issue else "standalone retained item"
    )
    recovery_issue_text = (
        f"issue #{issue}" if issue is not None and recovery_issue else "standalone retained item"
    )
    artifact_lines = artifacts or [f".loom/work-items/{item_id}.md", f".loom/progress/{item_id}.md"]
    (root / f".loom/work-items/{item_id}.md").write_text(
        "\n".join(
            [
                f"# {item_id}",
                "",
                "## Static Facts",
                "",
                f"- Item ID: {item_id}",
                f"- Goal: Retained carrier for {metadata_issue_text}.",
                f"- Scope: Prove retained lookup for {metadata_issue_text}.",
                f"- Execution Path: {metadata_issue_text} -> retained closeout.",
                "- Workspace Entry: .",
                f"- Recovery Entry: .loom/progress/{item_id}.md",
                f"- Review Entry: .loom/reviews/{item_id}.json",
                "- Validation Entry: focused retained lookup test",
                f"- Closing Condition: {metadata_issue_text} is closed.",
                "",
                "## Associated Artifacts",
                "",
                *[f"- {artifact}" for artifact in artifact_lines],
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / f".loom/progress/{item_id}.md").write_text(
        "\n".join(
            [
                f"# {item_id} Progress",
                "",
                "## Dynamic Facts",
                "",
                f"- Item ID: {item_id}",
                "- Current Checkpoint: closed",
                f"- Current Stop: Retained evidence for {recovery_issue_text}.",
                "- Next Step: None",
                "- Blockers: None",
                "- Latest Validation Summary: focused retained lookup test passed",
                "- Recovery Boundary: retained fixture only",
                "- Current Lane: terminal-closeout",
                "",
                "## Execution Ledger",
                "",
                "- Ledger Binding: recovery_entry",
                "- Plan Locator: not_applicable",
                f"- Acceptance Locator: #{issue}"
                if issue is not None and recovery_issue
                else "- Acceptance Locator: not_applicable",
                "- Validation Evidence Locator: focused retained lookup test",
                "- Handoff Notes Locator: not_applicable",
                "- Evidence Freshness: current",
                "",
            ]
        ),
        encoding="utf-8",
    )


class RetainedItemLookupTest(unittest.TestCase):
    def test_fact_chain_reads_companion_init_result_when_bootstrap_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_idle_companion_init_result(root)

            report, errors = loom_flow.load_fact_chain_report(root, ".loom/bootstrap/init-result.json")

            self.assertEqual(errors, [])
            self.assertEqual(report["fact_chain"]["mode"], "idle")
            self.assertEqual(
                report["derived_status_surface"]["sources"]["init_result"],
                ".loom/companion/init-result.json",
            )

    def test_idle_context_falls_back_to_retained_item_when_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_idle_companion_init_result(root)
            write_work_item(root, "GH-78-LOOM-0211-CLEANUP", issue=78)

            context, errors = loom_flow.load_context_with_retained_idle_fallback(
                root,
                ".loom/bootstrap/init-result.json",
                "GH-78-LOOM-0211-CLEANUP",
            )

            self.assertEqual(errors, [])
            self.assertEqual(context["item_id"], "GH-78-LOOM-0211-CLEANUP")
            self.assertTrue(context["retained_item_context"])

    def test_preserves_wi_issue_number_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "WI-1234")

            lookup = loom_flow.closeout_expected_item_lookup(root, 1234)

            self.assertEqual(lookup["item_id"], "WI-1234")
            self.assertEqual(lookup["work_item_relative"], ".loom/work-items/WI-1234.md")
            self.assertEqual(lookup["missing_inputs"], [])

    def test_discovers_historical_gh_issue_id(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            item_id = "GH-21-LOOM-UPGRADE-BASELINE"
            write_work_item(root, item_id, issue=21)

            lookup = loom_flow.closeout_expected_item_lookup(root, 21)
            context, errors = loom_flow.load_retained_item_context(
                root,
                ".loom/bootstrap/init-result.json",
                lookup["item_id"],
                lookup["work_item_relative"],
            )

            self.assertEqual(lookup["item_id"], item_id)
            self.assertEqual(lookup["missing_inputs"], [])
            self.assertEqual(errors, [])
            self.assertEqual(context["item_id"], item_id)

    def test_discovers_issue_from_associated_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(
                root,
                "CUSTOM-RETAINED-CARRIER",
                issue=55,
                artifacts=["github:issue/55", ".loom/progress/CUSTOM-RETAINED-CARRIER.md"],
                metadata_issue=False,
                recovery_issue=False,
            )

            lookup = loom_flow.closeout_expected_item_lookup(root, 55)

            self.assertEqual(lookup["item_id"], "CUSTOM-RETAINED-CARRIER")
            self.assertEqual(lookup["missing_inputs"], [])

    def test_discovers_issue_from_recovery_entry_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(
                root,
                "RECOVERY-EVIDENCE-CARRIER",
                issue=56,
                metadata_issue=False,
                recovery_issue=True,
            )

            lookup = loom_flow.closeout_expected_item_lookup(root, 56)

            self.assertEqual(lookup["item_id"], "RECOVERY-EVIDENCE-CARRIER")
            self.assertEqual(lookup["missing_inputs"], [])

    def test_prefers_canonical_wi_over_recovery_issue_mentions(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "WI-1544")
            write_work_item(
                root,
                "WI-1529",
                issue=1544,
                metadata_issue=False,
                recovery_issue=True,
            )
            write_work_item(
                root,
                "WI-1540",
                issue=1544,
                metadata_issue=False,
                recovery_issue=True,
            )

            lookup = loom_flow.closeout_expected_item_lookup(root, 1544)

            self.assertEqual(lookup["item_id"], "WI-1544")
            self.assertEqual(lookup["work_item_relative"], ".loom/work-items/WI-1544.md")
            self.assertEqual(lookup["missing_inputs"], [])

    def test_canonical_wi_keeps_weak_text_matches_as_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "WI-1495")
            write_work_item(root, "WI-1493", issue=1495)
            write_work_item(root, "WI-1496", issue=1495)

            lookup = loom_flow.closeout_expected_item_lookup(root, 1495)

            self.assertEqual(lookup["item_id"], "WI-1495")
            self.assertEqual(lookup["work_item_relative"], ".loom/work-items/WI-1495.md")
            self.assertEqual(lookup["missing_inputs"], [])
            diagnostics = {
                entry["item_id"]: entry
                for entry in lookup["diagnostics"]
                if isinstance(entry, dict) and "item_id" in entry
            }
            self.assertEqual(diagnostics["WI-1495"]["priority"], 1)
            self.assertIn("canonical WI issue-number carrier path", diagnostics["WI-1495"]["reasons"])
            self.assertEqual(diagnostics["WI-1493"]["priority"], 0)
            self.assertEqual(diagnostics["WI-1496"]["priority"], 0)
            self.assertIn("work item title/body metadata references issue", diagnostics["WI-1493"]["reasons"])
            self.assertIn("recovery entry evidence references issue", diagnostics["WI-1496"]["reasons"])

    def test_ambiguous_retained_issue_matches_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "GH-21-LOOM-UPGRADE-BASELINE", issue=21)
            write_work_item(root, "LEGACY-ISSUE-21", issue=21)

            lookup = loom_flow.closeout_expected_item_lookup(root, 21)

            self.assertIsNone(lookup["item_id"])
            self.assertEqual(lookup["work_item_relative"], None)
            self.assertEqual(len(lookup["missing_inputs"]), 1)
            self.assertIn("ambiguous", lookup["missing_inputs"][0])
            self.assertIn("GH-21-LOOM-UPGRADE-BASELINE", lookup["missing_inputs"][0])
            self.assertIn("LEGACY-ISSUE-21", lookup["missing_inputs"][0])

    def test_explicit_item_disambiguates_weak_issue_mentions(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "WI-1510", issue=1510)
            write_work_item(
                root,
                "WI-1509",
                issue=1510,
                metadata_issue=False,
                recovery_issue=True,
            )
            write_work_item(
                root,
                "WI-1511",
                issue=1510,
                metadata_issue=False,
                recovery_issue=True,
            )

            lookup = loom_flow.closeout_expected_item_lookup(root, 1510, "WI-1510")

            self.assertEqual(lookup["item_id"], "WI-1510")
            self.assertEqual(lookup["work_item_relative"], ".loom/work-items/WI-1510.md")
            self.assertEqual(lookup["missing_inputs"], [])

    def test_explicit_item_conflicting_issue_lookup_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "WI-22")
            write_work_item(root, "WI-OTHER", issue=22)

            lookup = loom_flow.closeout_expected_item_lookup(root, 22, "WI-OTHER")

            self.assertIsNone(lookup["item_id"])
            self.assertEqual(lookup["work_item_relative"], None)
            self.assertEqual(len(lookup["missing_inputs"]), 1)
            self.assertIn("does not match retained-item lookup for issue #22", lookup["missing_inputs"][0])

    def test_explicit_unrelated_item_does_not_bypass_ambiguous_issue_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_work_item(root, "WI-UNRELATED")
            write_work_item(root, "GH-23-ONE", issue=23)
            write_work_item(root, "GH-23-TWO", issue=23)

            lookup = loom_flow.closeout_expected_item_lookup(root, 23, "WI-UNRELATED")

            self.assertIsNone(lookup["item_id"])
            self.assertEqual(lookup["work_item_relative"], None)
            self.assertEqual(len(lookup["missing_inputs"]), 1)
            self.assertIn("could not be confirmed against issue #23", lookup["missing_inputs"][0])

    def test_closeout_and_reconciliation_parse_explicit_item(self) -> None:
        closeout_args = loom_flow.parse_args(
            [
                "closeout",
                "check",
                "--target",
                ".",
                "--item",
                "WI-1510",
                "--issue",
                "1510",
            ]
        )
        reconciliation_args = loom_flow.parse_args(
            [
                "reconciliation",
                "sync",
                "--target",
                ".",
                "--item",
                "WI-1510",
                "--issue",
                "1510",
                "--dry-run",
            ]
        )

        self.assertEqual(closeout_args.item, "WI-1510")
        self.assertEqual(reconciliation_args.item, "WI-1510")


if __name__ == "__main__":
    unittest.main()
