# Current Status

## Derived Fact Chain View

- Item ID: WI-1255
- Goal: Freeze regression inventories and boundary confirmation for #1248/#1268/#1275/#1281 without changing runner behavior.
- Scope: Add inventory-only evidence for daily-execution-cli, check_cli_contract.py, non-daily source-self fixtures, and repo-local-cli CI command boundaries under #1255. Do not change regression runner behavior, split actual suites, adjust CI semantics, or mark unknowns as confirmed.
- Execution Path: issues #1255/#1248/#1268/#1275/#1281 -> branch work/1255-regression-inventory -> PR #1326 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1255.md
- Review Entry: .loom/reviews/WI-1255.json
- Validation Entry: git diff --check; issue/body readback; regression surface locator readback; PR metadata preflight; hosted CI.
- Closing Condition: PR #1326 is merge-ready and merged to main with inventory evidence, no-release judgment, and follow-up PR-L/M/N boundaries preserved.
- Current Checkpoint: build
- Current Stop: Inventory evidence and WI-1255 carriers are committed and pushed for PR #1326 at head 76f21f7fa4afb3748d92470059da22dcfdaecbbf; workspace entry has been corrected to repo-relative '.' for CI fact-chain consumption.
- Next Step: Commit and push repo-relative workspace carrier fix, record current-head review evidence, then rerun PR gate and hosted check readback.
- Blockers: Hosted loom-pr-merge-gate and root-self-governance blocked because WI-1255 Workspace Entry used a local absolute path that escaped the CI target root; fixing to repo-relative '.'. PR is still draft until review/gates pass.
- Latest Validation Summary: Passed: git diff --check at head 76f21f7fa4afb3748d92470059da22dcfdaecbbf before workspace-entry fix; python3 .loom/bin/loom_init.py fact-chain --target . readback reports WI-1255 and recovery_readiness pass locally; PR #1326 REST readback reports head work/1255-regression-inventory at 76f21f7fa4afb3748d92470059da22dcfdaecbbf and exact Loom Work Item: WI-1255 body binding; python3 tools/loom_flow.py pr-metadata preflight --target . --surface merge_ready --owner MC-and-his-Agents --repo Loom --pr 1326 --head-sha 76f21f7fa4afb3748d92470059da22dcfdaecbbf --branch work/1255-regression-inventory returned pass; hosted py-compile, demo-bootstrap, and repo-local-cli passed; hosted root-self-governance and loom-pr-merge-gate blocked on absolute Workspace Entry and draft PR before this carrier fix.
- Recovery Boundary: Inventory-only PR. Do not implement #1269/#1276/#1282, change regression runner behavior, split suites, adjust CI semantics, or mark unknowns as confirmed.
- Current Lane: inventory-review

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
