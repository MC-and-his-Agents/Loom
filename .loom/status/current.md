# Current Status

## Derived Fact Chain View

- Item ID: WI-1869
- Goal: 收敛 v0.26.1 closeout 恢复路径与发布后读回打磨。
- Scope: implement #1870 stale native blocked-by removal apply, #1871 release readback closeout-head commit guidance, #1872 terminal closeout carrier-only review record consumption, and #1873 closeout common path docs/help/regression updates.
- Execution Path: issue #1869 -> branch work/1869-closeout-recovery-polish -> PR -> targeted contract checks -> merge -> #1870/#1871/#1872/#1873 closeout; #1874 handles the later v0.26.1 release.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1869.md
- Review Entry: .loom/reviews/WI-1869.json
- Validation Entry: CLI contract checks, release readback fixture, governance closeout fixture, skills release-check, and aggregate CLI contract.
- Closing Condition: #1870-#1873 implementation/docs/regression are merged, repo carriers and PR metadata bind to the merge head, and #1874 remains the release-only follow-up.
- Current Checkpoint: merge
- Current Stop: v0.26.1 closeout recovery implementation and local contract validation are ready for PR review.
- Next Step: Commit implementation, push branch, create/update PR metadata, run PR gate and hosted checks, then merge before #1874 release.
- Blockers: None recorded.
- Latest Validation Summary: local validation passed on 2026-07-01: `python3 tools/check_cli_contract.py --surface release-readback`; `python3 tools/check_cli_contract.py --surface governance-closeout`; `python3 tools/check_cli_contract.py --surface closeout-wrapper`; `python3 tools/check_cli_contract.py --surface pr-metadata`; `python3 tools/check_cli_contract.py --surface runtime-upgrade`; `python3 tools/loom.py skills release-check --json`; `python3 tools/check_cli_contract.py --surface aggregate`.
- Recovery Boundary: WI-1869 owns #1870-#1873 implementation/docs/regression and repo carrier refresh for changed runtime files. It does not bump v0.26.1, publish packages, close #1874, or alter unrelated milestones.
- Current Lane: implementation

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1869 implementation work is active in `/Users/mc/dev/Loom.worktrees/1869-closeout-recovery-polish` on branch `work/1869-closeout-recovery-polish`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1869.md`.
- Diagnostics Entry: Branch starts from main after v0.26.0 release closeout and targets #1869/#1870-#1873 implementation before #1874 release.
- Verification Entry: targeted and aggregate local CLI contracts passed before PR creation.
- Lane Entry: implementation

## Sources

- Static Truth: .loom/work-items/WI-1869.md
- Dynamic Truth: .loom/progress/WI-1869.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
