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
- Current Stop: Implementation PR #1336 is locally repaired at implementation head 062bc8a2b83c460ff78a600097f987e845d1ef04 plus carrier-only review/status/progress refresh; hosted checks must be rerun after push/readback.
- Next Step: Push repair, rerun hosted checks, consume controlled merge, then complete post-merge closeout for #1289/#1291.
- Blockers: None
- Latest Validation Summary: Local validation passed on 2026-06-06 for implementation head 062bc8a2b83c460ff78a600097f987e845d1ef04 before carrier-only refresh: py_compile_clean OK; demo bootstrap fixture OK; root runtime-parity validate OK; adopt verify OK; carrier refresh --dry-run OK; suite validate/evidence/carrier validate OK; tools/check_cli_contract.py passed; skills_surface.py check OK; check_release_surface.py OK; check_npm_package.py OK; git diff --check OK.
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
