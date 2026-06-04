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
- Current Stop: PR #1300 has the global CLI runtime provider contract documentation implemented; this carrier-only update binds the branch fact-chain to WI-1239 after WI-1294 terminal closeout landed on main.
- Next Step: Resolve the real pre-review/merge gate policy for docs-only contract freezes: either perform a true current-head review with a supported suite path decision, or mark the formal suite not_applicable through a gate-supported contract. Do not add fake minimal suite artifacts only to satisfy the gate.
- Blockers: The WI mismatch should be resolved by this carrier binding; PR gate still needs a real authored review/suite policy decision for this docs-only contract PR.
- Latest Validation Summary: Carrier-only expected evidence: fact-chain should read WI-1239 instead of terminal WI-1294; git diff --check should pass. The PR gate is expected to continue blocking until real review/suite policy is resolved.
- Recovery Boundary: Carrier refresh only. Do not change global-cli contract prose, installed-state/doctor/verify/repair behavior, migration behavior, release evidence, or unrelated root Loom state.
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
