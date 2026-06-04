# Current Status

## Derived Fact Chain View

- Item ID: WI-1286
- Goal: Freeze the review disposition and PR head binding contract for parent #1285.
- Scope: Define `semantic_review_disposition`, PR head binding, PR gate, merge check/run, closeout sync responsibility boundaries, allowed bypass types, and fail-closed conditions. Runtime implementation for #1287/#1288/#1289, downstream repository rule changes, and gate behavior changes remain out of scope.
- Execution Path: issue #1286 -> branch work/1286-review-head-binding-contract -> PR #1299 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1286.md
- Review Entry: .loom/reviews/WI-1286.json
- Validation Entry: git diff --check; focused rg for review disposition/head-binding contract terms; PR CI.
- Closing Condition: PR #1299 is merged to main, #1286 is closed with contract evidence, and follow-up gate/runtime implementation issues remain explicitly out of scope.
- Current Checkpoint: pre-review
- Current Stop: PR #1299 has the review disposition and PR head binding contract documentation implemented; this carrier-only update binds the branch fact-chain to WI-1286 after WI-1294 terminal closeout landed on main.
- Next Step: Resolve the real pre-review/merge gate policy for docs-only contract freezes: either perform a true current-head review with a supported suite path decision, or mark the formal suite not_applicable through a gate-supported contract. Do not add fake minimal suite artifacts only to satisfy the gate.
- Blockers: The WI mismatch should be resolved by this carrier binding; PR gate still needs a real authored review/suite policy decision for this docs-only contract PR.
- Latest Validation Summary: Carrier-only expected evidence: fact-chain should read WI-1286 instead of terminal WI-1294; git diff --check should pass. The PR gate is expected to continue blocking until real review/suite policy is resolved.
- Recovery Boundary: Carrier refresh only. Do not change review disposition contract prose, pr-gate/merge-gate runtime behavior, downstream repository rules, release evidence, or unrelated root Loom state.
- Current Lane: pre-review/review-head-binding-contract

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1299 validation section and hosted CI
- Lane Entry: pre-review/review-head-binding-contract

## Sources

- Static Truth: .loom/work-items/WI-1286.md
- Dynamic Truth: .loom/progress/WI-1286.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
