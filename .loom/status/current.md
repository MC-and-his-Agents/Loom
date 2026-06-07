# Current Status

## Derived Fact Chain View

- Item ID: WI-1271
- Goal: Split `tools/check_cli_contract.py` suite evidence checks into a named CLI contract surface.
- Scope: Add a stable `suite-evidence` named surface in `tools/check_cli_contract.py` for suite evidence inspect/scaffold/validate and evidence-map contract checks while preserving aggregate `check-cli-contract` behavior. Suite carrier inspect/validate assertions remain aggregate-only until #1272. Excludes #1272 suite-carrier follow-up scope, #1273 governance closeout, #1274 adoption/host metadata, #1257 parent closeout, hosted workflow changes, metadata schema changes, release work, and runtime suite semantic changes outside `tools/check_cli_contract.py`.
- Execution Path: issue #1271 -> branch `work/1271-check-cli-suite-evidence-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1271.md
- Review Entry: .loom/reviews/WI-1271.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface suite-evidence; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1271 --json; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1271 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1271 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, and validation evidence.
- Current Checkpoint: merge
- Current Stop: PR #1362 is open at head d8ee5c591e4ff025237d483b04a27eeabae9511f with corrected evidence-only implementation validation, PR metadata/head binding, hosted check readback, and scheduler-owned current-head semantic review passed. Review record `.loom/reviews/WI-1271.json` is authored against head d8ee5c591e4ff025237d483b04a27eeabae9511f with no findings.
- Next Step: Update PR #1362 to the scheduler review carrier head, rerun PR gate/hosted checks, then perform controlled merge and post-merge closeout sync if gates pass.
- Blockers: None
- Latest Validation Summary: 2026-06-08 correction validation on branch `work/1271-check-cli-suite-evidence-surface`: `python3 tools/check_cli_contract.py --list-surfaces` passed and listed `suite-contract`, `suite-evidence`, and `aggregate` only; `python3 tools/check_cli_contract.py --surface suite-evidence` passed in 1.66s with evidence-only checks; `python3 tools/check_cli_contract.py` passed in 181.38s and preserved carrier assertions through aggregate; `python3 tools/loom.py fact-chain --target . --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1271 --json` returned `not_applicable` with no blocking gaps under the existing exit-1 contract; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed after shadow refresh; `git diff --check` passed. Scheduler-owned review record `.loom/reviews/WI-1271.json` was authored with decision allow, kind code_review, reviewed head d8ee5c591e4ff025237d483b04a27eeabae9511f, and no findings.
- Recovery Boundary: Only #1271 suite-evidence surface split and minimal WI-1271 PR-readiness carriers are in scope. Do not implement #1272, #1273, #1274, #1257 parent closeout, Round 5+, release work, hosted workflow changes, metadata schema changes, runtime suite semantic changes outside `tools/check_cli_contract.py`, or unrelated cleanup.
- Current Lane: check-cli-suite-evidence-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: hosted merge gate and root-self-adoption initially blocked on missing scheduler-owned semantic review; scheduler-owned semantic review is now authored in `.loom/reviews/WI-1271.json`.
- Verification Entry: local validation, PR metadata/readback, and hosted check readback for the #1271 PR
- Lane Entry: check-cli-suite-evidence-surface

## Sources

- Static Truth: .loom/work-items/WI-1271.md
- Dynamic Truth: .loom/progress/WI-1271.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
