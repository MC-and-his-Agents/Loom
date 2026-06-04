# Current Status

## Derived Fact Chain View

- Item ID: WI-1264
- Goal: Freeze the regression surface core contract batch for #1264, #1265, and #1266.
- Scope: Define the regression bucket and named surface taxonomy, the minimum surface evidence schema, and the fast/full validation policy for the #1255 regression split tree. Ownership is limited to contract documentation, the formal suite `not_applicable` locator, and minimal cross-links in harness documentation for PR #1297. Implementation splits, inventories, release work, and runtime behavior changes remain out of scope.
- Execution Path: issues #1264/#1265/#1266 -> branch work/1264-regression-surface-contract -> PR #1297 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1264.md
- Review Entry: .loom/reviews/WI-1264.json
- Validation Entry: git diff --check; manual contract readback for taxonomy, evidence schema, and fast/full policy; PR CI.
- Closing Condition: PR #1297 is merged to main, #1264/#1265/#1266 are closed with contract evidence, and follow-up inventory/implementation issues remain explicitly out of scope.
- Current Checkpoint: closed
- Current Stop: PR #1297 merged to main at 2026-06-04T17:29:52Z with merge commit b3d23c40bef7b8f29e5319447ae93ba05ad01472; issues #1264, #1265, and #1266 closed at 2026-06-04T17:29:53Z/17:29:54Z/17:29:54Z; controlled merge and hosted checks passed before closeout sync.
- Next Step: None; WI-1264 is terminal and retained only as regression surface contract evidence for the #1255 implementation sequence.
- Blockers: None
- Latest Validation Summary: PR #1297 at head 9671a09ef07d0e05c78dc4cdd3b0523454aa1b92 passed local pr-gate, controlled-merge check, hosted py-compile, demo-bootstrap, repo-local-cli, root-self-governance, loom-pr-merge-gate, and two loom-check jobs before squash merge.
- Recovery Boundary: Terminal closeout carrier only. Do not resume WI-1264 implementation here; inventory and implementation work continue through separate #1255 follow-up issues.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1297 local pr-gate, controlled merge check, hosted required checks, and merge commit b3d23c40bef7b8f29e5319447ae93ba05ad01472
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1264.md
- Dynamic Truth: .loom/progress/WI-1264.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
