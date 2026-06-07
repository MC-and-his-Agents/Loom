# Current Status

## Derived Fact Chain View

- Item ID: WI-1271
- Goal: Split `tools/check_cli_contract.py` suite evidence and suite carrier checks into a named CLI contract surface.
- Scope: Add a stable `suite-evidence` named surface in `tools/check_cli_contract.py` for suite evidence inspect/scaffold/validate and suite carrier inspect/validate contract checks while preserving aggregate `check-cli-contract` behavior. Excludes #1272 suite-carrier follow-up scope, #1273 governance closeout, #1274 adoption/host metadata, #1257 parent closeout, hosted workflow changes, metadata schema changes, release work, and runtime suite semantic changes outside `tools/check_cli_contract.py`.
- Execution Path: issue #1271 -> branch `work/1271-check-cli-suite-evidence-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1271.md
- Review Entry: .loom/reviews/WI-1271.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface suite-evidence; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1271 --json; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1271 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1271 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, and validation evidence.
- Current Checkpoint: build
- Current Stop: Implementation local validation passed for the new `suite-evidence` named surface while aggregate `check-cli-contract` behavior remains intact; PR creation, metadata readback, hosted checks, scheduler-owned review, controlled merge, and closeout remain pending.
- Next Step: Commit and push the branch, create/update the PR for #1271, verify PR body machine carrier/head binding, then read back hosted checks before stopping at `waiting-scheduler-gate`.
- Blockers: None
- Latest Validation Summary: 2026-06-08 local validation on branch `work/1271-check-cli-suite-evidence-surface`: `python3 tools/check_cli_contract.py --list-surfaces` passed and listed `suite-contract`, `suite-evidence`, and `aggregate`; `python3 tools/check_cli_contract.py --surface suite-evidence` passed in 2.39s; `python3 tools/check_cli_contract.py` passed with `suite-contract`, `suite-evidence`, and aggregate `check-cli-contract` surfaces in 194.60s; `git diff --check` passed before carrier authoring.
- Recovery Boundary: Only #1271 suite-evidence surface split and minimal WI-1271 PR-readiness carriers are in scope. Do not implement #1272, #1273, #1274, #1257 parent closeout, Round 5+, release work, hosted workflow changes, metadata schema changes, runtime suite semantic changes outside `tools/check_cli_contract.py`, or unrelated cleanup.
- Current Lane: check-cli-suite-evidence-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: none
- Verification Entry: local validation, PR metadata/readback, and hosted check readback for the #1271 PR
- Lane Entry: check-cli-suite-evidence-surface

## Sources

- Static Truth: .loom/work-items/WI-1271.md
- Dynamic Truth: .loom/progress/WI-1271.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
