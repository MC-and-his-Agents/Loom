# Current Status

## Derived Fact Chain View

- Item ID: WI-1800
- Goal: Close the #1800 global CLI and strong governance hardening tree, ship v0.21.2, and leave #1802/#1800 for post-merge release closeout.
- Scope: #1800 PR scope: #1793-#1799, #1801, #1803, and #1804 fixes only. Includes target/context resolution, global-cli metadata-only bootstrap and CI verify, active-ruleset strong detector, adversarial adoption evidence, audited repair-pr evidence, runtime parity, release readiness for v0.21.2, merge wrapper target/readback behavior, and opaque path-safe Work Item ID compatibility. Excludes #1806 and #1807-#1810.
- Execution Path: Issue tree #1800 -> branch work/1800-global-cli-strong-governance-hardening -> PR #1816 -> release v0.21.2 -> #1802 release evidence -> #1800 parent closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1800.md
- Review Entry: .loom/reviews/WI-1800.json
- Validation Entry: Focused unit/contract/runtime parity/package/release checks plus tools/loom_check.py --profile source . on the final PR head.
- Closing Condition: PR #1816 merges to main; loom-cli-release publishes v0.21.2; release readback confirms tag, GitHub Release, npm package, workflow run, and installed/global CLI evidence; #1802 and #1800 closeout comments consume those facts.
- Current Checkpoint: merge
- Current Stop: Current-head spec and implementation reviews are recorded; WI-1800 is ready for PR metadata refresh, hosted check rerun, and merge-ready gate consumption.
- Next Step: Refresh merge-ready/closeout shadow evidence, update PR #1816 metadata to the final head, push, rerun hosted checks, then perform release and closeout after merge.
- Blockers: None
- Latest Validation Summary: 2026-06-30 local convergence after PR #1816 hosted failure classification: suite validate/evidence/carrier pass for WI-1800; demo bootstrap fixture drift check pass; root loom_init verify pass; fact-chain pass for WI-1800; runtime-parity validate pass; governance-profile status pass; carrier refresh dry-run reports only merge-ready/closeout shadow refresh needed after status update.
- Recovery Boundary: WI-1800 owns #1793-#1799, #1801, #1803, #1804, v0.21.2 release readiness, demo fixture sync caused by runtime changes, and current PR carriers. It excludes #1806 and #1807-#1810, and #1802/#1800 remain open until post-merge release evidence is consumed.
- Current Lane: controller convergence

## Runtime Evidence

- Run Entry: 2026-06-29 WI-1790 repair started in repo-relative workspace `.` on branch `work/fix-init-bootstrap-entrypoint`.
- Logs Entry: Local reproduction and validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1790.md`.
- Diagnostics Entry: Installed package bootstrap failed because wrappers searched for missing top-level `skills/shared/scripts/loom_init.py`; PR gate currently requires WI-1790 metadata and review refresh.
- Verification Entry: Local source/package checks passed before carrier refresh; hosted checks, release publish, plugin payload refresh, and installed CLI readback remain required.
- Lane Entry: init-bootstrap-installed-entrypoint-release

## Sources

- Static Truth: .loom/work-items/WI-1800.md
- Dynamic Truth: .loom/progress/WI-1800.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
