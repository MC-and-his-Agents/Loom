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
- Current Checkpoint: merge
- Current Stop: WI-1785 implementation and review are locally complete; PR #1786 metadata is stable and the branch is awaiting hosted checks, controlled merge, and closeout.
- Next Step: Consume hosted checks for PR #1786, merge after gate pass, then update #1784 branch so its hosted closeout gate can consume the workflow fix.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local validation passed on branch `work/1785-closeout-gate-surface`: git diff --check; python3 tools/py_compile_clean.py tools/loom.py; local Python smoke verified closeout, merge_ready, malformed, and empty PR metadata surface inference. #1784 closeout-surface gate was separately proven in its closeout worktree before this fix; hosted #1784 rerun remains the post-merge consumer proof.
- Recovery Boundary: WI-1785 owns only hosted `loom-pr-merge-gate` surface inference for PR body machine metadata and its Loom carriers. It does not change release readback verdicts, terminal closeout carrier semantics, or cleanup automation.
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
