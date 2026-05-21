# Current Status

## Derived Fact Chain View

- Item ID: WI-847
- Goal: 实现 Governance Lint authored review approval bypass 检查，确保 raw/shadow/runtime/PR/CI/GitHub review evidence 不能替代 work_item.review_entry 的 authored implementation approval。
- Scope: 更新 PR merge gate 与 merge checkpoint 的 approval boundary 消费、governance_lint 输出、installed runtime regression fixtures、pr-merge-gate 文档和 generated skills surface；不运行语义 review、不替代 pr merge gate、不改变 review record schema、不引入 repo-specific lint 规则。
- Execution Path: harness/governance-lint/approval-bypass
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-847.md
- Review Entry: .loom/reviews/WI-847.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py
- Closing Condition: PR merge 后 closeout 消费 #847 issue、PR、merge commit、Project #4 状态，并解除 #851 的 #847 blocker。
- Current Checkpoint: build
- Current Stop: WI-847 implementation completed locally: PR gate and merge checkpoint now reject spec_review/non-implementation review records as implementation approval, expose approval-boundary governance_lint, and fixture raw/spec-review bypass cases fail closed.
- Next Step: Write WI-847 spec/review carriers, run checkpoint merge, create PR, wait for checks, then controlled merge and closeout if branch protection allows.
- Blockers: None recorded.
- Latest Validation Summary: py_compile_clean passed for source/generated loom_flow.py and loom_check.py; skills_surface check passed; git diff --check passed; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py passed with checked 38 surfaces.
- Recovery Boundary: Only #847 approval bypass governance lint behavior, pr-gate approval boundary output, installed runtime regression fixtures, generated skills surface, WI-847 carriers, and pr-merge-gate documentation are in scope.
- Current Lane: branch work/847-review-approval-bypass-lint in formal worktree /Users/mc/dev/Loom-work-847-review-approval-bypass-lint, bound to issue #847 and parent #844; baseline origin/main@04e3e6b89cf162636d47a552c665d516c0da5d0d.

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-847.md
- Dynamic Truth: .loom/progress/WI-847.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
