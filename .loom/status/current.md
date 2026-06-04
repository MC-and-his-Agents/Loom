# Current Status

## Derived Fact Chain View

- Item ID: WI-1264
- Goal: Freeze the regression surface core contract batch for #1264, #1265, and #1266.
- Scope: Define the regression bucket and named surface taxonomy, the minimum surface evidence schema, and the fast/full validation policy for the #1255 regression split tree. Ownership is limited to contract documentation and minimal cross-links in harness documentation for PR #1297. Implementation splits, inventories, release work, and runtime behavior changes remain out of scope.
- Execution Path: issues #1264/#1265/#1266 -> branch work/1264-regression-surface-contract -> PR #1297 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1264.md
- Review Entry: .loom/reviews/WI-1264.json
- Validation Entry: git diff --check; manual contract readback for taxonomy, evidence schema, and fast/full policy; PR CI.
- Closing Condition: PR #1297 is merged to main, #1264/#1265/#1266 are closed with contract evidence, and follow-up inventory/implementation issues remain explicitly out of scope.
- Current Checkpoint: pre-review
- Current Stop: PR #1297 has the regression surface core contract documentation implemented; this carrier-only update binds the branch fact-chain to WI-1264 after WI-1294 terminal closeout landed on main.
- Next Step: Resolve the real pre-review/merge gate policy for docs-only contract freezes: either perform a true current-head review with a supported suite path decision, or mark the formal suite not_applicable through a gate-supported contract. Do not add fake minimal suite artifacts only to satisfy the gate.
- Blockers: The WI mismatch is resolved locally; PR gate still needs a real authored review/suite policy decision for this docs-only contract PR.
- Latest Validation Summary: Carrier-only local evidence: `python3 tools/loom.py fact-chain --target . --json` reads WI-1264 instead of terminal WI-1294. `git diff --check` passes. The PR gate is expected to continue blocking until real review/suite policy is resolved.
- Recovery Boundary: Carrier refresh only. Do not change regression contract prose, inventories, implementation split behavior, release evidence, or unrelated root Loom state.
- Current Lane: pre-review/regression-surface-contract

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1297 validation section and hosted CI
- Lane Entry: pre-review/regression-surface-contract

## Sources

- Static Truth: .loom/work-items/WI-1264.md
- Dynamic Truth: .loom/progress/WI-1264.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
