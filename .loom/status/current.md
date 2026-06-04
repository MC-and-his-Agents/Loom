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
- Current Checkpoint: pre-review
- Current Stop: PR #1298 has the idle fact-chain/status contract documentation implemented; this carrier-only update binds the branch fact-chain to WI-1229 after WI-1294 terminal closeout landed on main.
- Next Step: Resolve the real pre-review/merge gate policy for docs-only contract freezes: either perform a true current-head review with a supported suite path decision, or mark the formal suite not_applicable through a gate-supported contract. Do not add fake minimal suite artifacts only to satisfy the gate.
- Blockers: The WI mismatch should be resolved by this carrier binding; PR gate still needs a real authored review/suite policy decision for this docs-only contract PR.
- Latest Validation Summary: Carrier-only expected evidence: fact-chain should read WI-1229 instead of terminal WI-1294; git diff --check should pass. The PR gate is expected to continue blocking until real review/suite policy is resolved.
- Recovery Boundary: Carrier refresh only. Do not change idle contract prose, terminal closeout implementation, sync/repair behavior, release evidence, or unrelated root Loom state.
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
