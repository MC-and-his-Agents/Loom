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
- Current Stop: Terminal closeout PR gate repair is validated at head e65b5ec44bb6bfdf1fe89d801aa7c740aed6ee34; current-head review/status carrier refresh is pending commit before opening the repair PR.
- Next Step: Commit carrier refresh, open the gate repair PR, wait for hosted checks, merge it through controlled merge, then rerun closeout-only PR #1342.
- Blockers: None
- Latest Validation Summary: Local validation passed on 2026-06-06 for terminal closeout gate repair head e65b5ec44bb6bfdf1fe89d801aa7c740aed6ee34: git diff --check OK; py_compile OK; tools/check_cli_contract.py passed; runtime-parity validate OK; tools/skills_surface.py check OK; check_release_surface.py OK; check_npm_package.py passed.
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
