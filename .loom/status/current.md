# Current Status

## Derived Fact Chain View

- Item ID: WI-1289-1291
- Goal: Implement merge check/run consumption of PR gate and post-merge review bypass diagnostics for issues #1289 and #1291.
- Scope: CLI/runtime changes for loom pr gate, controlled merge, post-merge diagnostics, repair plan output, generated runtime parity, docs contract, and CLI contract fixtures.
- Execution Path: issues #1289/#1291 -> branch work/1289-1291-merge-check-run-pr-gate -> PR #1336 -> hosted checks -> controlled merge -> post-merge closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1289-1291.md
- Review Entry: .loom/reviews/WI-1289-1291.json
- Validation Entry: python3 tools/check_cli_contract.py; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py
- Closing Condition: PR #1336 merges through the controlled merge path and closeout consumes merged PR, target branch, issue states, review, gate, and release-impact evidence for #1289/#1291.
- Current Checkpoint: merge-ready
- Current Stop: Implementation PR #1336 is locally repaired through validated purity repair head f7779994803659743f96ad8c4bc8936a8e5ad054; carrier-only review/status/shadow refresh is pending commit before push.
- Next Step: Commit carrier refresh, update PR #1336 body to the pushed PR head, wait for hosted checks, consume controlled merge, then complete post-merge closeout for #1289/#1291.
- Blockers: None
- Latest Validation Summary: Local validation passed on 2026-06-06 for purity repair head f7779994803659743f96ad8c4bc8936a8e5ad054: git diff --check OK; py_compile_clean OK; tools/check_cli_contract.py passed; runtime-parity validate OK; check_demo_bootstrap_fixture OK; tools/skills_surface.py check OK; check_release_surface.py OK; check_npm_package.py passed; purity-check passed with hard_failures=[] and blocking_diag=0.
- Recovery Boundary: Scope remains WI-1289/WI-1291 implementation, generated runtime parity, PR metadata, review/merge gate evidence, controlled merge, and closeout carriers only.
- Current Lane: R2-T2 merge-check-run-pr-gate

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: post-merge PR/issue/main readback; controlled-merge merge; closeout check; retained targeted global-cli smoke; git diff --check; py_compile; skills check; hosted checks; release-judgment
- Lane Entry: R2-T2 merge-check-run-pr-gate

## Sources

- Static Truth: .loom/work-items/WI-1289-1291.md
- Dynamic Truth: .loom/progress/WI-1289-1291.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
