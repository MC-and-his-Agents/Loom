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
- Current Stop: Terminal closeout PR gate repair plus fixture/shadow parity refresh is validated at head addea74dd6c19561f5f3719867d1a6aa01aa50dc; current-head review/status carrier refresh is being committed for PR #1343.
- Next Step: Commit carrier refresh, push PR #1343, wait for hosted checks, merge it through controlled merge, then rerun closeout-only PR #1342.
- Blockers: None
- Latest Validation Summary: Local validation passed on 2026-06-06 for terminal closeout gate repair head addea74dd6c19561f5f3719867d1a6aa01aa50dc: git diff --check OK; tools/check_demo_bootstrap_fixture.py OK; tools/skills_surface.py check OK; runtime-parity validate OK; shadow-parity --surface all --blocking OK; tools/check_cli_contract.py passed in 177.71s.
- Recovery Boundary: Scope remains WI-1289/WI-1291 implementation, generated runtime parity, PR metadata, review/merge gate evidence, controlled merge, and closeout carriers only.
- Current Lane: terminal-closeout-gate-repair

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; py_compile; tools/check_cli_contract.py; runtime-parity validate; tools/skills_surface.py check; check_release_surface.py; check_npm_package.py
- Lane Entry: terminal-closeout-gate-repair

## Sources

- Static Truth: .loom/work-items/WI-1289-1291.md
- Dynamic Truth: .loom/progress/WI-1289-1291.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
