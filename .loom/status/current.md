# Current Status

## Derived Fact Chain View

- Item ID: WI-1806
- Goal: Provide shared PR intent profiles and easier governance carrier commands for docs/governance-only, closeout-only, release-only, carrier-sync-only, and fixture-only PRs.
- Scope: #1806 parent plus #1807-#1814 implementation and verification. Owned files are limited to `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/cli-command-matrix.md`, and WI-1806 Loom carriers. #1815 release readiness is tracked, but publishing `v0.22.0` is blocked until #1800 / `v0.21.2` releases or explicitly frees the release line.
- Execution Path: issue tree #1806 -> branch `work/1806-pr-intent-carrier-ergonomics` -> shared `pr-intent prepare/check` implementation -> focused CLI contract fixtures -> PR readiness -> release wait for #1800 / `v0.21.2`.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1806.md
- Review Entry: .loom/reviews/WI-1806.json
- Validation Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface pr-metadata`; `python3 tools/check_cli_contract.py --surface suite-contract`; `python3 tools/check_cli_contract.py --surface aggregate`; `git diff --check`.
- Closing Condition: PR for #1806 merges with current-head review and gate evidence. `v0.22.0` release closeout (#1815) remains blocked until #1800 / `v0.21.2` is complete or the release line is explicitly released.
- Current Checkpoint: merge
- Current Stop: Implementation and focused local validation for #1807-#1814 are complete on branch `work/1806-pr-intent-carrier-ergonomics`; PR/review/release closeout is pending. #1815 release is blocked by #1800 / `v0.21.2`.
- Next Step: Commit and push the #1806 branch, prepare PR metadata/readback, then run review/merge-ready only after PR metadata and head SHA are stable. Do not publish `v0.22.0` until #1800 / `v0.21.2` releases or explicitly releases the publication line.
- Blockers: None
- Latest Validation Summary: 2026-06-30 local validation passed for WI-1806: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface pr-metadata` passed in 30.61s after the `.loom/bootstrap/` carrier-sync fixture update; `python3 tools/loom.py fact-chain --target . --item WI-1806 --json`; PR #1817 metadata readback/preflight passed after body update and must be rerun after each head-changing carrier commit; `git diff --check`. Earlier same implementation batch passed `python3 tools/check_cli_contract.py --surface suite-contract` in 7.64s and `python3 tools/check_cli_contract.py --surface aggregate` in 426.70s before the final carrier path-only fixture tightening.
- Recovery Boundary: WI-1806 owns PR intent carrier ergonomics only. It does not close #1800/#1802, does not write v0.21.2 release evidence, does not publish `v0.22.0`, and does not make PR intent profiles bypass review, PR gate, merge-ready, release readback, host reconciliation, or closeout evidence.
- Current Lane: main-control-carrier-sync

## Runtime Evidence

- Run Entry: 2026-06-30 WI-1806 started in repo-relative workspace `.` on branch `work/1806-pr-intent-carrier-ergonomics`; local formal worktree locator is `/Users/mc/dev/Loom-1806-pr-intent-carrier-ergonomics`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1806.md`.
- Diagnostics Entry: #1806 has no existing branch/PR at start; GitHub issue native dependencies were empty; release boundary is external to #1806 and tied to #1800 / `v0.21.2`.
- Verification Entry: Focused local checks passed before PR metadata/readback; review, hosted checks, merge-ready, and release readback remain pending.
- Lane Entry: pr-intent-carrier-ergonomics

## Sources

- Static Truth: .loom/work-items/WI-1806.md
- Dynamic Truth: .loom/progress/WI-1806.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
