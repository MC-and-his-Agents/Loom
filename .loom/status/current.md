# Current Status

## Derived Fact Chain View

- Item ID: WI-1239
- Goal: Freeze the global CLI runtime provider contract for downstream repositories under parent #1238.
- Scope: Define runtime provider taxonomy, provider authority boundaries, required `global-cli` command surface, metadata-only adoption relationship, compatibility mode, and migration boundary wording. Installed-state, doctor, verify, repair, migration, plugin registration, runtime execution behavior changes, and #1240-#1246 implementation work remain out of scope.
- Execution Path: issue #1239 -> branch work/1239-global-cli-provider-contract -> PR #1300 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1239.md
- Review Entry: .loom/reviews/WI-1239.json
- Validation Entry: git diff --check; tools/loom.py help --json; PR CI.
- Closing Condition: PR #1300 is merged to main, #1239 is closed with contract evidence, and follow-up global-cli provider implementation issues remain explicitly out of scope.
- Current Checkpoint: pre-review
- Current Stop: PR #1300 is rebased on main after WI-1286 closeout, scoped back to docs/carrier contract changes, and has a formal suite not_applicable locator for the global CLI provider contract batch.
- Next Step: Record current-head spec and implementation review artifacts, update PR #1300 head metadata, then rerun local pr-gate and hosted checks.
- Blockers: None locally after suite path validation; hosted PR checks and current-head review consumption still need to be refreshed.
- Latest Validation Summary: `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1239; `python3 tools/loom.py suite validate --target . --item WI-1239 --json` returned `result=not_applicable` with no blocking gaps and valid suite-level rationale; `python3 tools/loom.py help --json` returned a readable command surface; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed.
- Recovery Boundary: Keep this PR limited to WI-1239 carriers, formal suite not_applicable locator, global-cli provider contract documentation, adoption documentation, README contract pointers, and validation evidence. Do not change installed-state/doctor/verify/repair behavior, migration behavior, checker behavior, plugin registration behavior, runtime execution semantics, release evidence, or unrelated root Loom state.
- Current Lane: pre-review/global-cli-provider-contract

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1300 validation section and hosted CI
- Lane Entry: pre-review/global-cli-provider-contract

## Sources

- Static Truth: .loom/work-items/WI-1239.md
- Dynamic Truth: .loom/progress/WI-1239.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
