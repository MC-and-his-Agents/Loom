# Current Status

## Derived Fact Chain View

- Item ID: WI-1229
- Goal: Freeze the idle/no-active-item fact-chain schema and status surface contract for parent #1228.
- Scope: Define canonical active, terminal, and idle repository execution state; specify how `.loom/bootstrap/init-result.json` and `.loom/status/current.md` represent idle without fake active locators; document provenance, backward compatibility, retained items, and governance status boundaries. Terminal metadata writing, command split implementation, carrier closeout sync, repair/apply flows, and later #1230-#1237/#1296 work remain out of scope.
- Execution Path: issue #1229 -> branch work/1229-idle-fact-chain-contract -> PR #1298 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1229.md
- Review Entry: .loom/reviews/WI-1229.json
- Validation Entry: git diff --check; tools/check_loom_check_runtime_regressions.py; PR CI.
- Closing Condition: PR #1298 is merged to main, #1229 is closed with contract evidence, and follow-up idle implementation issues remain explicitly out of scope.
- Current Checkpoint: merge
- Current Stop: Merge checkpoint inputs are assembled for the docs-only idle fact-chain/status contract batch: build checkpoint passes, fact-chain, suite not_applicable, shadow parity, runtime carrier refresh dry-run, targeted runtime regression check, and current-head review evidence are ready for PR #1298 hosted checks.
- Next Step: Push the refreshed WI-1229 head to PR #1298, rerun local/hosted pr-gate against the pushed head, and merge once hosted checks pass.
- Blockers: None
- Latest Validation Summary: `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1229; `python3 tools/loom.py suite validate --target . --item WI-1229 --json` returned `result=not_applicable` with no blocking gaps and valid suite-level rationale; `python3 tools/check_loom_check_runtime_regressions.py` passed; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed; `python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run` returned `result=pass` with empty `refresh_needed`.
- Recovery Boundary: Keep this PR limited to WI-1229 carriers, formal suite not_applicable locator, idle fact-chain/status contract documentation, taxonomy boundary documentation, and validation evidence. Do not change terminal metadata writing, command split behavior, carrier closeout sync behavior, repair/apply behavior, release behavior, or unrelated root Loom state.
- Current Lane: pre-review/idle-fact-chain-contract

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1298 validation section and hosted CI
- Lane Entry: pre-review/idle-fact-chain-contract

## Sources

- Static Truth: .loom/work-items/WI-1229.md
- Dynamic Truth: .loom/progress/WI-1229.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
