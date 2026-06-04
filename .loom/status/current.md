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
- Current Stop: PR #1299 has the review disposition and PR head binding contract documentation implemented, is rebased on main after #1307, and carries a formal WI-1286 suite path decision instead of fake minimal suite artifacts.
- Next Step: Record a true current-head implementation review for PR #1299, refresh retained carriers, run PR gate against the pushed head, and consume hosted checks.
- Blockers: None
- Latest Validation Summary: `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1286; `python3 tools/loom.py suite validate --target . --item WI-1286 --json` returned `result=not_applicable` with no blocking gaps and valid suite-level rationale.
- Recovery Boundary: Keep this PR limited to WI-1286 carriers, formal suite not_applicable locator, review disposition/head-binding contract docs, repo companion boundary wording, and validation evidence. Do not implement #1287/#1288/#1289, change pr-gate/merge-gate runtime behavior, add downstream repository rules, or add fake minimal suite artifacts.
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
