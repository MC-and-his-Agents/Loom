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
- Current Checkpoint: closed_out
- Current Stop: Post-merge closeout is consumed in GitHub control-plane readback: PR #1336 merged through controlled merge at `d2c4749240eb7c68187f1f5552fdfa61f30a3d20`, issues #1289 and #1291 are CLOSED, and stale `blockedBy` edges to #1286/#1288/#1289 have been removed. Versioned terminal closeout metadata has been written on closeout branch `closeout/1289-1291-post-merge-consumed`.
- Next Step: Commit and merge this closeout-only carrier sync back to `main` so repo truth records the consumed closeout.
- Blockers: None
- Latest Validation Summary: Local validation passed on 2026-06-06 for purity repair head f7779994803659743f96ad8c4bc8936a8e5ad054: git diff --check OK; py_compile_clean OK; tools/check_cli_contract.py passed; runtime-parity validate OK; check_demo_bootstrap_fixture OK; tools/skills_surface.py check OK; check_release_surface.py OK; check_npm_package.py passed; purity-check passed with hard_failures=[] and blocking_diag=0.
- Recovery Boundary: Scope remains WI-1289/WI-1291 implementation, generated runtime parity, PR metadata, review/merge gate evidence, controlled merge, and closeout carriers only.
- Current Lane: post-merge-closeout-consumed

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1336 merged by controlled wrapper; hosted checks passed at head d8361c577305e9e6842d728ba716c3fa91fa2ca2; terminal carrier metadata written; #1289/#1291 CLOSED; stale blockedBy edges removed; pending closeout-only carrier PR merge to main.
- Lane Entry: post-merge-closeout-consumed

## Sources

- Static Truth: .loom/work-items/WI-1289-1291.md
- Dynamic Truth: .loom/progress/WI-1289-1291.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
