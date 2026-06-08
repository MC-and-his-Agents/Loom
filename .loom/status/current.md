# Current Status

## Derived Fact Chain View

- Item ID: WI-1274
- Goal: Split `tools/check_cli_contract.py` adoption/host metadata checks into a named CLI contract surface.
- Scope: Add a stable `adoption-host-metadata` named surface in `tools/check_cli_contract.py` for metadata-only adoption and host metadata verification checks already covered by aggregate `check-cli-contract`. Preserve aggregate behavior except for adding the named surface to surface listing and execution registry. Excludes #1257 parent closeout, #1270-#1273 terminal carriers, Round 5+, Deferred roadmap, release work, hosted workflow changes, metadata schema changes, task-carrier runtime validation semantic changes, and unrelated cleanup.
- Execution Path: issue #1274 -> branch `work/1274-check-cli-adoption-host-metadata-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1274.md
- Review Entry: .loom/reviews/WI-1274.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1274 --json; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1274 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1274 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, no-release judgment, hosted checks, and validation evidence.
- Current Checkpoint: implementation_ready_for_pr
- Current Stop: WI-1274 implementation is in progress on branch `work/1274-check-cli-adoption-host-metadata-surface`; local surface and aggregate validation passed before PR creation, and scheduler-owned semantic review, controlled merge, and closeout remain pending.
- Next Step: Create or update the implementation PR, prove PR metadata/head binding and hosted checks on the current head, then stop at waiting-scheduler-gate.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-08T00:52:56Z worker validation: `python3 tools/check_cli_contract.py --list-surfaces` passed and listed `adoption-host-metadata` plus `aggregate`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata` passed in 0.74s; `python3 tools/check_cli_contract.py` passed all six surfaces in 217.36s including aggregate `check-cli-contract`; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1274; `python3 tools/loom.py suite validate --target . --item WI-1274 --json` returned expected `not_applicable` with no blocking gaps and exit status 1; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed; `git diff --check` passed. PR metadata/head binding and hosted checks remain pending.
- Recovery Boundary: Only #1274 adoption-host-metadata surface split and minimal WI-1274 PR-readiness carriers are in scope. Do not touch #1257 parent closeout, #1270-#1273 terminal carriers, Round 5+, Deferred roadmap, release work, hosted workflow changes, metadata schema changes, task-carrier runtime validation semantic changes, or unrelated cleanup.
- Current Lane: check-cli-adoption-host-metadata-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: no blocking diagnostics currently recorded during implementation.
- Verification Entry: local surface, aggregate, fact-chain, suite not_applicable, shadow parity, and diff check passed before PR creation; PR metadata/head binding and hosted checks remain pending
- Lane Entry: check-cli-adoption-host-metadata-surface

## Sources

- Static Truth: .loom/work-items/WI-1274.md
- Dynamic Truth: .loom/progress/WI-1274.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
