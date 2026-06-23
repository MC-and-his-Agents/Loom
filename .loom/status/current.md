# Current Status

## Derived Fact Chain View

- Item ID: WI-1785
- Goal: 修复 closeout PR hosted gate surface 推断。
- Scope: Issue #1785: make the hosted `loom-pr-merge-gate` consume PR metadata surface `closeout` when the PR body machine carrier declares it, while keeping ordinary PRs on `merge_ready`. Ownership is limited to `.github/workflows/pr-merge-gate.yml`, WI-1785 carriers, `.loom/specs/WI-1785`, and `.loom/reviews/WI-1785*.json`.
- Execution Path: issue #1785 -> branch work/1785-closeout-gate-surface -> PR pending -> controlled merge -> closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1785.md
- Review Entry: .loom/reviews/WI-1785.json
- Validation Entry: `git diff --check`; workflow syntax/readback smoke; `loom pr gate --surface closeout` regression against #1784 body; suite/fact-chain/shadow checks.
- Closing Condition: PR merged and issue #1785 closed, then #1784 hosted merge gate rerun passes with closeout metadata.
- Current Checkpoint: closed_out
- Current Stop: WI-1785 closed out after PR #1786 merged at 24c1eb6a2a1889bf771d5da92a571c4c4b54b40e and issue #1785 closed at 2026-06-23T17:44:52Z.
- Next Step: Return to #1776 closeout PR #1784, update it onto main so hosted closeout gate consumes the workflow surface fix, then continue #1778 release closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 WI-1785 closeout readback: PR #1786 merged at 2026-06-23T17:42:20Z with merge commit 24c1eb6a2a1889bf771d5da92a571c4c4b54b40e; issue #1785 closed at 2026-06-23T17:44:52Z; PR metadata readback surface closeout passed; closeout status passed; carrier closeout-sync wrote closed_out metadata. Hosted #1786 checks passed before merge: loom-pr-merge-gate, loom-check, node-installer-pr, py-compile, demo-bootstrap, repo-local-cli, root-self-governance.
- Recovery Boundary: WI-1785 terminal closeout only consumes PR #1786 and issue #1785 facts. It does not change release readback verdicts, #1776 implementation facts, #1784 carrier content beyond later consumption, or #1778 release behavior.
- Current Lane: closeout-gate-surface

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1785 implementation started in repo-relative workspace `.` on branch `work/1785-closeout-gate-surface`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1785.md`.
- Diagnostics Entry: #1784 local `loom pr gate --surface closeout` passes, while hosted gate without surface blocks terminal closeout PRs.
- Verification Entry: diff check, py compile, local workflow surface inference smoke, suite/fact-chain/shadow checks.
- Lane Entry: closeout-gate-surface

## Sources

- Static Truth: .loom/work-items/WI-1785.md
- Dynamic Truth: .loom/progress/WI-1785.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
