# Current Status

## Derived Fact Chain View

- Item ID: WI-1270
- Goal: Split suite inspect/scaffold/validate checks into a named CLI contract surface.
- Scope: Add a stable `suite-contract` named surface in `tools/check_cli_contract.py` for suite inspect/scaffold/validate contract checks while preserving aggregate `check-cli-contract` coverage. Excludes suite evidence, suite carrier, governance closeout, adoption/host metadata, hosted workflow, release, metadata schema, and runtime suite semantic changes.
- Execution Path: issue #1270 -> branch work/1270-check-cli-suite-contract-surface -> PR #1360 -> local surface/aggregate validation -> PR metadata/head binding -> hosted checks -> scheduler-owned review/controlled merge/closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1270.md
- Review Entry: .loom/reviews/WI-1270.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface suite-contract; python3 tools/check_cli_contract.py; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR #1360 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1270 is closed, and post-merge closeout sync consumes PR, issue, branch, head, target main, review, and validation evidence.
- Current Checkpoint: merge
- Current Stop: PR #1360 is open at head 5eca51a3074edeafbb869aab4480d856f8bb5587 with final-head local validation, PR metadata/head binding, fact-chain, suite not_applicable validation, shadow parity, and scheduler-owned current-head semantic review passed. Review record `.loom/reviews/WI-1270.json` is authored against head 5eca51a3074edeafbb869aab4480d856f8bb5587 with no findings.
- Next Step: Update PR #1360 to the scheduler review carrier head, rerun PR gate/hosted checks, then perform controlled merge and post-merge closeout sync if gates pass.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-08 final-head validation on branch `work/1270-check-cli-suite-contract-surface` head `5eca51a3074edeafbb869aab4480d856f8bb5587`: `python3 tools/check_cli_contract.py --list-surfaces` passed and listed `suite-contract	suite-contract` plus `aggregate	check-cli-contract`; `python3 tools/check_cli_contract.py --surface suite-contract` passed; `python3 tools/check_cli_contract.py` passed with suite-contract and aggregate surfaces in 207.13s; `python3 tools/loom.py fact-chain --target . --json` passed with WI-1270 entry points; `python3 tools/loom.py suite validate --target . --item WI-1270 --json` returned expected `not_applicable` with no blocking gaps; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed before scheduler review carrier sync; `git diff --check` passed. PR #1360 metadata readback matched rendered machine carrier for WI-1270, branch, head SHA, workspace, suite not_applicable rationale, no_release judgment, and `Surface: suite-contract`. Hosted release-judgment passed. Scheduler-owned review record `.loom/reviews/WI-1270.json` was authored with decision allow, kind code_review, reviewed head 5eca51a3074edeafbb869aab4480d856f8bb5587, and no findings.
- Recovery Boundary: Only #1270 suite-contract surface split and minimal WI-1270 PR-readiness carriers are in scope. Do not handle #1271, #1272, #1273, #1274, #1257 closeout, runtime suite semantics, hosted workflows, release surfaces, metadata schema, or external-visible actions.
- Current Lane: check-cli-suite-contract-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: hosted merge gate initially blocked on stale WI-1324 fact-chain and missing scheduler-owned semantic review; carrier sync updated fact-chain to WI-1270, suite not_applicable, shadow parity, and final-head PR metadata. Scheduler-owned semantic review is now authored in `.loom/reviews/WI-1270.json`.
- Verification Entry: local validation, PR metadata/readback, and hosted check readback for PR #1360
- Lane Entry: check-cli-suite-contract-surface

## Sources

- Static Truth: .loom/work-items/WI-1270.md
- Dynamic Truth: .loom/progress/WI-1270.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
