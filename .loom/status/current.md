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
- Current Checkpoint: implementation_pr_ready
- Current Stop: PR #1360 is open at head 22f7c7973f27e2ef3e29be3aff1becf4954966b2 with local validation and PR metadata/head binding passed; hosted checks are being read back. Scheduler owns semantic review, controlled merge, and post-merge closeout.
- Next Step: Wait for scheduler-owned semantic review/high-cost gate decision, controlled merge, and closeout sync.
- Blockers: Scheduler-owned semantic review is not authored yet; hosted merge gate may remain blocked until the scheduler provides current-head review evidence.
- Latest Validation Summary: 2026-06-08 local validation on branch `work/1270-check-cli-suite-contract-surface` head `22f7c7973f27e2ef3e29be3aff1becf4954966b2`: `python3 tools/check_cli_contract.py --list-surfaces` passed and listed `suite-contract	suite-contract` plus `aggregate	check-cli-contract`; `python3 tools/check_cli_contract.py --surface suite-contract` passed; `python3 tools/check_cli_contract.py` passed with suite-contract and aggregate surfaces; `git diff --check` passed. PR #1360 metadata readback matched rendered machine carrier for WI-1270, branch, head SHA, workspace, and `Surface: suite-contract`.
- Recovery Boundary: Only #1270 suite-contract surface split and minimal WI-1270 PR-readiness carriers are in scope. Do not handle #1271, #1272, #1273, #1274, #1257 closeout, runtime suite semantics, hosted workflows, release surfaces, metadata schema, or external-visible actions.
- Current Lane: check-cli-suite-contract-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: hosted merge gate initially blocked on stale WI-1324 fact-chain and missing scheduler-owned semantic review; this carrier sync updates fact-chain to WI-1270 but does not author review evidence.
- Verification Entry: local validation, PR metadata/readback, and hosted check readback for PR #1360
- Lane Entry: check-cli-suite-contract-surface

## Sources

- Static Truth: .loom/work-items/WI-1270.md
- Dynamic Truth: .loom/progress/WI-1270.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
