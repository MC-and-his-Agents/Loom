# Current Status

## Derived Fact Chain View

- Item ID: WI-1287
- Goal: Implement the `semantic_review_disposition` carrier and PR head binding enforcement for issues #1287 and #1288 under parent #1285.
- Scope: Add repo-local CLI/runtime validation for `semantic_review_disposition` statuses and required fields, require PR body machine carrier `Branch` and `Head SHA` consistency, bind authored implementation review artifacts to the current PR head, and add focused contract fixtures for missing, unknown, incomplete, stale, post-merge, and CI-only bypass cases. Do not implement #1289/#1291 merge check/run behavior and do not add companion or guardian adapter fixtures.
- Execution Path: issues #1287/#1288 -> branch work/1287-1288-review-head-binding -> official worktree /Users/mc/dev/Loom-1287-review-head-binding -> PR -> current-head review -> pr-gate/merge-ready.
- Workspace Entry: /Users/mc/dev/Loom-1287-review-head-binding
- Recovery Entry: .loom/progress/WI-1287.md
- Review Entry: .loom/reviews/WI-1287.json
- Validation Entry: git diff --check; targeted semantic review disposition fixture; py_compile_clean; skills surface/release checks; tools/check_cli_contract.py; fact-chain; suite validate; pr-gate dry check.
- Closing Condition: #1287 and #1288 have a PR whose body machine carrier matches the branch and head SHA, whose current-head implementation review record is consumed by pr-gate, and whose merge-ready evidence rejects stale review, unknown disposition, incomplete waive/not_applicable rationale, PR body/carrier mismatch, and CI-only bypass.
- Current Checkpoint: review
- Current Stop: Demo bootstrap fixture sync was required by hosted CI after the review carrier commit; current implementation inputs are being restabilized before re-review.
- Next Step: Commit demo bootstrap fixture sync and carrier scope update, rerun fact-chain/suite/pr-gate checks, then rewrite `.loom/reviews/WI-1287.json` against the new current head.
- Blockers: None
- Latest Validation Summary: Restabilization validation passed `make loom-demo-new-project-check`, `git diff --check`, `python3 tools/check_cli_contract.py`, `python3 tools/loom.py skills release-check --json`, and prior targeted review-record/semantic disposition fixtures; local aggregate `make loom-check` was terminated after a long hang in `tools/loom_check.py` and is not used as pass evidence.
- Recovery Boundary: Only #1287/#1288 review disposition carrier and PR head binding enforcement are in scope. Do not implement #1289/#1291 merge check/run behavior, do not add companion/guardian adapter fixtures, and do not treat CI/checks/guardian/companion evidence as a substitute for `semantic_review_disposition`.
- Current Lane: review-head-binding

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: targeted fixture and CLI contract outputs in this branch before review record
- Lane Entry: review-head-binding

## Sources

- Static Truth: .loom/work-items/WI-1287.md
- Dynamic Truth: .loom/progress/WI-1287.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
