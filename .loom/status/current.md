# Current Status

## Derived Fact Chain View

- Item ID: WI-1555
- Goal: Productize a one-shot post-merge closeout run that turns the current manual reconciliation, terminal carrier sync, recovery status, shadow refresh, and final closeout check sequence into a single dry-run/apply CLI entry.
- Scope: Issue #1555 only: add `loom closeout run` as a CLI facade over existing reconciliation, closeout check, carrier closeout-sync, recovery writeback, and carrier refresh runtime steps; add wrapper contract fixtures for dry-run, apply, and stop-before-mutation behavior. Do not implement #1532 closeout freeze admission, #1533 closeout-specific gate policy, #1534 docs/skills convergence, #1515 release/no-release closeout, or batch/mixed-risk closeout.
- Execution Path: issue #1555 -> branch work/1555-one-shot-closeout-run -> tools/loom.py closeout run facade -> tools/check_cli_contract.py closeout-wrapper fixture -> PR #1585
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1555.md
- Review Entry: .loom/reviews/WI-1555.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper; python3 tools/loom.py closeout run --target . --item WI-1582 --issue 1582 --pr 1583 --branch work/1582-closeout-hosted-admission --json; python3 tools/loom.py pr metadata-render/readback/preflight for PR #1585
- Closing Condition: PR #1585 is reviewed, checks pass or are classified, merged or explicitly superseded, issue #1555 is closed/reconciled, and WI-1555 repo carrier is terminalized without changing release/no-release policy.
- Current Checkpoint: merge
- Current Stop: WI-1555 code and carrier are bound at local head b3504780b40cc7edbbf601b973c75b56553bf431; fact-chain, build checkpoint, suite not_applicable validation, closeout-wrapper contract, clean py compile, and merge checkpoint have passed. Prior closed-item dry-run evidence is superseded by the active WI-1555 carrier; direct WI-1582 dry-run now blocks on expected carrier mismatch.
- Next Step: Push, update PR #1585 metadata head SHA, and wait for hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-18T17:28Z WI-1555 local validation at head b3504780b40cc7edbbf601b973c75b56553bf431 in /Users/mc/dev/Loom-1555-one-shot-closeout-run: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py passed; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper passed and covers closeout run dry-run/apply success plus blocked apply stop-before-carrier behavior; python3 tools/loom.py fact-chain --target . --json passed for WI-1555; python3 tools/loom.py checkpoint build --target . --item WI-1555 --json passed; python3 tools/loom.py suite validate --target . --item WI-1555 --json returned not_applicable with no missing inputs; python3 tools/loom.py checkpoint merge --target . --item WI-1555 --json passed; python3 tools/loom.py closeout run --target . --item WI-1582 --issue 1582 --pr 1583 --branch work/1582-closeout-hosted-admission --json returned structured block with failure_classifier missing_or_stale_closeout_input after active carrier switched to WI-1555, which is expected current-carrier mismatch rather than a #1555 code failure. Aggregate CLI contract was stopped after entering unrelated pre-review WI-924 live path.
- Recovery Boundary: WI-1555 owns only the one-shot closeout run facade, closeout-wrapper fixture surface, and its own carrier/review metadata. It does not own #1532/#1533 gate semantics, #1534 docs/skills convergence, #1515 release/no-release closeout, or post-merge batch processing.
- Current Lane: milestone-12-one-shot-closeout-run

## Runtime Evidence

- Run Entry: 2026-06-18 WI-1555 one-shot closeout run implementation
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: WI-1582/#1583/#1584 closeout showed that manual post-merge closeout still required repeated PR readback, issue reconciliation, carrier terminalization, status/shadow refresh, and final closeout check.
- Verification Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper; closeout run dry-run against WI-1582/#1583; PR #1585 metadata render/readback/preflight.
- Lane Entry: milestone-12-one-shot-closeout-run

## Sources

- Static Truth: .loom/work-items/WI-1555.md
- Dynamic Truth: .loom/progress/WI-1555.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
