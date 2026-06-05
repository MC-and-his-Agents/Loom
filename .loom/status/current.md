# Current Status

## Derived Fact Chain View

- Item ID: WI-1255
- Goal: Freeze regression inventories and boundary confirmation for #1248/#1268/#1275/#1281 without changing runner behavior.
- Scope: Add inventory-only evidence for daily-execution-cli, check_cli_contract.py, non-daily source-self fixtures, and repo-local-cli CI command boundaries under #1255. Do not change regression runner behavior, split actual suites, adjust CI semantics, or mark unknowns as confirmed.
- Execution Path: issues #1255/#1248/#1268/#1275/#1281 -> branch work/1255-regression-inventory -> PR #1326 -> CI/review -> merge to main.
- Workspace Entry: /Users/mc/dev/Loom-1255-regression-inventory
- Recovery Entry: .loom/progress/WI-1255.md
- Review Entry: .loom/reviews/WI-1255.json
- Validation Entry: git diff --check; issue/body readback; regression surface locator readback; PR metadata preflight; hosted CI.
- Closing Condition: PR #1326 is merge-ready and merged to main with inventory evidence, no-release judgment, and follow-up PR-L/M/N boundaries preserved.
- Current Checkpoint: build
- Current Stop: Inventory evidence and WI-1255 carriers authored for PR #1326 at head c5e2df4245b803f88efc81aa687a27b8401e4037; awaiting carrier commit, hosted CI readback, and current-head review.
- Next Step: Commit and push WI-1255 carriers, update PR #1326 body with exact Loom Work Item binding, then record current-head review evidence.
- Blockers: Hosted loom-pr-merge-gate currently blocks because the previous PR body did not provide an exact Loom Work Item binding and no WI-1255 carrier was present; root-self-governance failed for the same carrier binding drift.
- Latest Validation Summary: Passed: git diff --check at head c5e2df4245b803f88efc81aa687a27b8401e4037; issue/body readback for #1255/#1248/#1268/#1275/#1281/#1264/#1265/#1266; regression surface locator readback for docs/methodology/harness/regression-surface-contract.md, skills/shared/scripts/loom_check.py, tools/check_cli_contract.py, and .github/workflows/loom-check.yml; live PR metadata preflight passed for PR #1326 head c5e2df4245b803f88efc81aa687a27b8401e4037; hosted py-compile, demo-bootstrap, and repo-local-cli passed; hosted root-self-governance and loom-pr-merge-gate blocked on missing current Work Item carrier before this carrier update.
- Recovery Boundary: Inventory-only PR. Do not implement #1269/#1276/#1282, change regression runner behavior, split suites, adjust CI semantics, or mark unknowns as confirmed.
- Current Lane: inventory-carrier-alignment

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1312 local pr-gate, hosted required checks, and merge commit eae9f9753745cf0c1ec1a7a623904c4decd5315b
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1255.md
- Dynamic Truth: .loom/progress/WI-1255.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
