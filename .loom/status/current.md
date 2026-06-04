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
- Current Checkpoint: review
- Current Stop: PR #1297 has consumed the merged docs-only suite `not_applicable` gate contract from #1302 and now carries a formal WI-1264 suite path decision instead of fake minimal suite artifacts.
- Next Step: Record a true current-head implementation review for PR #1297, run PR gate against the pushed head, and consume hosted checks.
- Blockers: None
- Latest Validation Summary: `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1264; `python3 tools/loom.py suite validate --target . --item WI-1264 --json` returned `result=not_applicable` with no blocking gaps and valid suite-level rationale.
- Recovery Boundary: Keep this PR limited to WI-1264 carriers, formal suite not_applicable locator, and regression contract docs. Do not add inventory, implementation splits, release work, runtime behavior changes, or fake minimal suite artifacts.
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
