# Current Status

## Derived Fact Chain View

- Item ID: WI-1272
- Goal: Split `tools/check_cli_contract.py` suite carrier checks into a named CLI contract surface.
- Scope: Add a stable `suite-carrier` named surface in `tools/check_cli_contract.py` for suite carrier inspect/validate coverage, including carrier type recognition, normalized statuses, truth boundary, missing/invalid carrier negative fixtures, source locator checks, and existing suite carrier payload assertions. Preserve aggregate `check-cli-contract` behavior. Excludes task-carrier runtime validation semantic changes, suite contract/evidence surface changes except aggregate compatibility, #1273 governance closeout, #1274 adoption/host metadata, #1257 parent closeout, hosted workflow changes, metadata schema changes, release work, and unrelated cleanup.
- Execution Path: issue #1272 -> branch `work/1272-check-cli-suite-carrier-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1272.md
- Review Entry: .loom/reviews/WI-1272.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface suite-carrier; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1272 --json; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1272 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1272 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, no-release judgment, hosted checks, and validation evidence.
- Current Checkpoint: implementation
- Current Stop: Local implementation validation passed for the `suite-carrier` named check_cli_contract surface; PR creation/update and hosted check readback are next.
- Next Step: Create or update the PR, run PR metadata preflight/readback, read back hosted checks, then wait for scheduler-owned gate.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-07 local validation for WI-1272 passed: `python3 tools/check_cli_contract.py --list-surfaces` listed `suite-contract`, `suite-evidence`, `suite-carrier`, and `aggregate	check-cli-contract`; `python3 tools/check_cli_contract.py --surface suite-carrier` passed; `python3 tools/check_cli_contract.py` passed with `suite-contract`, `suite-evidence`, `suite-carrier`, and aggregate `check-cli-contract` coverage; `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1272 --json` returned expected `result: not_applicable` with valid rationale and no missing inputs or blocking gaps.
- Recovery Boundary: Only #1272 suite-carrier surface split and minimal WI-1272 PR-readiness carriers are in scope. Do not implement task-carrier runtime validation semantic changes, #1273, #1274, #1257, Round 5+, release work, hosted workflow changes, metadata schema changes, suite contract/evidence semantic changes, or unrelated cleanup.
- Current Lane: check-cli-suite-carrier-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: no blocking diagnostics currently recorded after local validation.
- Verification Entry: local validation passed; PR metadata/head binding and hosted checks pending
- Lane Entry: check-cli-suite-carrier-surface

## Sources

- Static Truth: .loom/work-items/WI-1272.md
- Dynamic Truth: .loom/progress/WI-1272.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
