# Current Status

## Derived Fact Chain View

- Item ID: WI-1240-1242
- Goal: Implement the first global-cli runtime provider executable support batch for issues #1240, #1241, and #1242.
- Scope: Model global-cli runtime provider in installed-state, make detect/doctor/verify accept no-.loom/bin repositories only when the provider contract is satisfied, classify stale .loom/bin as repairable residue, and report fact-chain/status/story-carrier current entrypoints through global loom commands while preserving repo-local wrapper compatibility. Ownership constraints are limited to #1240/#1241/#1242 implementation, generated runtime parity, demo fixture parity, and current WI/PR carriers. Excludes #1243/#1244 migration repair/fixtures and #1245/#1246 docs/release closeout.
- Execution Path: issues #1240/#1241/#1242 -> branch work/1240-1242-global-cli-runtime-provider -> PR #1327 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1240-1242.md
- Review Entry: .loom/reviews/WI-1240-1242.json
- Validation Entry: git diff --check; targeted global-cli smoke; py_compile; skills check; demo bootstrap check; PR gate; release judgment.
- Closing Condition: PR #1327 is merge-ready with global-cli provider behavior consistent across installed-state, doctor/verify, fact-chain/status/story-carrier entrypoints, repo-local wrapper compatibility preserved, and release impact recorded for downstream consumption.
- Current Checkpoint: closed
- Current Stop: PR #1327 was merged into main at 2842f86f460b528b95b1f539f0bf6ee83189cfd6 after controlled-merge consumed PR gate, branch protection, required checks, and host mergeability for head 00f17f6d54ad9e5e0cd5b668a516367bf9f396c7. Issues #1240, #1241, and #1242 are CLOSED/COMPLETED; closeout check consumed PR, issue, required-check, and target-main evidence.
- Next Step: Terminal; no WI-1240-1242 implementation or closeout-carrier work remains. Follow-up migration repair/fixtures stay with #1243/#1244, and docs/release closeout stays with #1245/#1246 or the parent release flow.
- Blockers: None
- Latest Validation Summary: Post-merge closeout evidence passed on 2026-06-05: PR #1327 readback state MERGED, merge commit 2842f86f460b528b95b1f539f0bf6ee83189cfd6, target main origin/main=2842f86f460b528b95b1f539f0bf6ee83189cfd6, issues #1240/#1241/#1242 CLOSED/COMPLETED; controlled-merge merge executed through Loom wrapper after required checks `demo-bootstrap`, `loom-check`, `loom-pr-merge-gate`, `py-compile`, and `repo-local-cli` passed; python3 .loom/bin/loom_flow.py closeout check --target . --pr 1327 --issue 1240 --branch work/1240-1242-global-cli-runtime-provider -> pass. Pre-merge retained validation remains: state-check pass, git diff --check pass, py_compile_clean OK, skills check pass, targeted global-cli smoke TARGETED_GLOBAL_CLI_CHECKS_PASS, fact-chain pass, flow build pass, adopt verify pass, shadow-parity pass, runtime-parity pass, runtime-evidence pass, local pr-gate pass, hosted checks pass, release-judgment pass. Full tools/check_cli_contract.py remains intentionally not rerun; prior full-contract failure remains classified as environment/carrier-state, not provider behavior.
- Recovery Boundary: Terminal closeout carrier sync only after PR #1327 merge. Do not change #1240/#1241/#1242 implementation behavior, #1243/#1244 migration repair/fixtures, #1245/#1246 docs/release closeout, or #1287/#1288 review-head/parser semantics.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: post-merge PR/issue/main readback; controlled-merge merge; closeout check; retained targeted global-cli smoke; git diff --check; py_compile; skills check; hosted checks; release-judgment
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1240-1242.md
- Dynamic Truth: .loom/progress/WI-1240-1242.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
