# Current Status

## Derived Fact Chain View

- Item ID: WI-1806
- Goal: Provide shared PR intent profiles and easier governance carrier commands for docs/governance-only, closeout-only, release-only, carrier-sync-only, and fixture-only PRs.
- Scope: #1806 parent plus #1807-#1814 implementation and verification. Owned files are limited to `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/cli-command-matrix.md`, `.loom/reviews/WI-1806.spec.json`, `.loom/reviews/WI-1806.json`, `.loom/shadow/merge-ready-loom.json`, `.loom/shadow/closeout-loom.json`, and WI-1806 Loom carriers. #1815 release readiness is tracked; `v0.22.0` publishing is now sequenced after PR #1817 merge and release readback because `v0.21.2` is present on `main`.
- Execution Path: issue tree #1806 -> branch `work/1806-pr-intent-carrier-ergonomics` -> shared `pr-intent prepare/check` implementation -> focused CLI contract fixtures -> PR readiness -> merge -> #1815 `v0.22.0` release readiness.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1806.md
- Review Entry: .loom/reviews/WI-1806.json
- Validation Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface pr-metadata`; `python3 tools/check_cli_contract.py --surface suite-contract`; `python3 tools/check_cli_contract.py --surface aggregate`; `git diff --check`.
- Closing Condition: PR #1817 for #1806 merges with current-head review and gate evidence, then #1815 completes `v0.22.0` release notes, version/package/plugin metadata and hash checks, pre-release checks, npm/package readback, release evidence, and #1806 closeout.
- Current Checkpoint: merge
- Current Stop: Implementation and focused local validation for #1807-#1814 are complete on branch `work/1806-pr-intent-carrier-ergonomics`; PR #1817 has been rebased by merge onto `v0.21.2` main. #1815 release is no longer blocked by #1800, but waits for PR #1817 merge and release readback.
- Next Step: Rebind implementation review to the `v0.21.2` merge baseline, refresh PR #1817 metadata/readback for the new head, push, wait hosted checks, merge PR #1817, then run #1815 `v0.22.0` release and closeout on `main`.
- Blockers: None
- Latest Validation Summary: 2026-06-30 local validation passed for WI-1806 after merging `origin/main` at `f0594b3f` (`v0.21.2`) into head `33c7adfe`: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/skills_surface.py`; `python3 tools/check_cli_contract.py --surface pr-metadata` passed in 38.02s; `python3 tools/check_cli_contract.py --surface suite-contract` passed in 14.49s; `python3 tools/check_npm_package.py --surface runtime-copy-parity`; `python3 tools/loom.py fact-chain --target . --item WI-1806 --json`; `python3 tools/loom.py shadow-parity --target . --surface all --blocking --json`; `git diff --check`. PR #1817 metadata readback/preflight and PR gate must be rerun after the next head-changing review/status commit.
- Recovery Boundary: WI-1806 owns PR intent carrier ergonomics and #1815 `v0.22.0` release convergence only. It does not close #1800/#1802, does not rewrite `v0.21.2` release evidence, and does not make PR intent profiles bypass review, PR gate, merge-ready, release readback, host reconciliation, or closeout evidence.
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
