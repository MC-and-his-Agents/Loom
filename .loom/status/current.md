# Current Status

## Derived Fact Chain View

- Item ID: WI-1738
- Goal: 让 ship 自动推断 branch、head SHA 与 target branch
- Scope: Issue #1738: `loom ship` infers missing host bindings from explicit inputs, PR readback, and current checkout state, then passes the effective bindings to metadata preflight, PR gate, controlled merge, and host-only closeout.
- Execution Path: issue #1738 -> branch work/1738-ship-inference -> PR pending -> controlled merge -> closeout
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1738.md
- Review Entry: .loom/reviews/WI-1738.json
- Validation Entry: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper
- Closing Condition: PR merged and issue #1738 closed with ship binding inference evidence.
- Current Checkpoint: closeout
- Current Stop: WI-1738 implementation PR #1762 merged, issue #1738 closed, and terminal closeout metadata recorded.
- Next Step: Merge WI-1738 closeout carrier sync PR, then continue dependent issue #1739.
- Blockers: None recorded.
- Latest Validation Summary: Post-merge closeout evidence on 2026-06-23: PR #1762 merged at d10f421aaed781471b0f590e78163016b8be8e0f; issue #1738 closed at 2026-06-23T05:18:53Z; carrier closeout-sync recorded terminal metadata; implementation PR hosted checks passed for head 786c1d43f377ed54d880d7cff82e4982f1bf7142.
- Recovery Boundary: WI-1738 owns `loom ship` binding inference behavior, its CLI contract regression, and WI-1738 fact-chain/review/shadow evidence only.
- Current Lane: ship-inference

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1738 ship inference lane continued in issue-scoped worktree `work/1738-ship-inference`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1738.md`.
- Diagnostics Entry: Ship now records inferred branch/head/target bindings and passes effective bindings to delegated gates.
- Verification Entry: Targeted ship wrapper contract, suite validate, suite evidence validate, suite carrier validate, shadow parity, hosted checks, and controlled merge are consumed before merge.
- Lane Entry: ship-inference

## Sources

- Static Truth: .loom/work-items/WI-1738.md
- Dynamic Truth: .loom/progress/WI-1738.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
