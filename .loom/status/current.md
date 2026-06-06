# Current Status

## Derived Fact Chain View

- Item ID: WI-1269
- Goal: Add the check_cli_contract.py named surface runner with filters, progress/timing, and failure grouping while preserving aggregate behavior.
- Scope: Implement the reusable named surface runner in `tools/check_cli_contract.py`, add optional `--surface` and `--fixture-group` filters plus `--list-surfaces`, report progress/timing, and group failures by surface and fixture group. Preserve full `python3 tools/check_cli_contract.py` aggregate behavior. Excludes #1270-#1274 and #1276-#1280 regression surface splits.
- Execution Path: issue #1269 -> branch work/1269-cli-contract-surface-runner -> PR #1334 -> hosted checks/review -> controlled merge -> post-merge closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1269.md
- Review Entry: .loom/reviews/WI-1269.json
- Validation Entry: python3 tools/py_compile_clean.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface missing; python3 tools/check_cli_contract.py --surface aggregate; PR metadata preflight; hosted checks; controlled merge gate.
- Closing Condition: PR #1334 is merged through controlled merge, issue #1269 is closed, and post-merge closeout consumes PR, issue, branch, head, target-main, review, and validation evidence.
- Current Checkpoint: closed_out
- Current Stop: Post-merge closeout consumed: PR #1334 is merged, issue #1269 is closed as completed, stale closed blocker edges from #1266 and #1268 were removed, and reconciliation audit now passes with no findings.
- Next Step: None; WI-1269 post-merge closeout is consumed. Follow-up split issues #1270-#1274 remain open and out of scope.
- Blockers: None
- Latest Validation Summary: Post-merge closeout evidence on 2026-06-06: PR #1334 state MERGED at 2026-06-06T09:19:42Z, head 29c4f6931c77d0393fd5b1d257938c3adf3ceb79, merge commit 8519ad6fb28b3fde44af765996b7e420ee39775c contained in origin/main; issue #1269 CLOSED at 2026-06-06T10:34:57Z with closeout comment https://github.com/MC-and-his-Agents/Loom/issues/1269#issuecomment-4638262459; GitHub native blockedBy edges to closed #1266/#1268 removed by removeBlockedBy GraphQL mutation; reconciliation audit passed with no findings; closeout check consumed retained review .loom/reviews/WI-1269.json, hosted required checks demo-bootstrap/loom-check/loom-pr-merge-gate/py-compile/repo-local-cli, suite not_applicable closeout gate, and PR merge backlink.
- Recovery Boundary: Closeout-only for #1269 / PR #1334. Do not handle #1270-#1274, #1276-#1280, or unrelated regression surface splits. Do not write /Users/mc/dev/Loom main.
- Current Lane: post-merge-closeout-consumed

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: local CLI contract validation; PR #1334 metadata preflight; authored review record; local PR gate pending rerun; hosted checks pending; controlled merge pending
- Lane Entry: implementation-merge-ready

## Sources

- Static Truth: .loom/work-items/WI-1269.md
- Dynamic Truth: .loom/progress/WI-1269.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
