# Current Status

## Derived Fact Chain View

- Item ID: WI-846
- Goal: 将 Governance Lint / Operating Lint 接入 loom check 与 flow pre-review 输出面，提前暴露 blocking/advisory lint evidence，降低无效 review。
- Scope: 更新 shared runtime pre-review governance_lint 输出、loom_check contract 与 negative fixture 验证、generated skills surface 和 #846 carriers；不新增独立 lint CLI、不接入高级 repo-specific lint、不改写 review 或 merge-ready 结论。
- Execution Path: harness/governance-lint/pre-review-consumption
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-846.md
- Review Entry: .loom/reviews/WI-846.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py
- Closing Condition: PR merge 后 closeout 消费 #846 issue、PR、merge commit、Project #4 状态，并解除 #852 的 loom check / pre-review blocker。
- Current Checkpoint: build
- Current Stop: #846 implementation, installer version bump, and formal review records are ready on branch work/846-governance-lint-check-pre-review at baseline origin/main@e9ce82e69b424169225044af74d38abf57339fb6; flow pre-review exposes Governance Lint as derived evidence, stale derived status blocks before semantic review, current Work Item declared artifacts are report-only, and undeclared same-directory artifacts still block state-check.
- Next Step: Refresh review records to the package-bump head, push PR #958, then rerun PR checks and merge-ready gate.
- Blockers: None recorded.
- Latest Validation Summary: git diff --check passed; py_compile_clean passed for source/generated loom_flow.py and loom_check.py; tools/skills_surface.py check passed; root state-check passed; root flow pre-review passed with governance_lint.result=pass; examples/new-project flow pre-review passed with governance_lint.result=pass; stale derived status pre-review negative smoke passed with governance_lint.result=block; undeclared same-directory artifact state-check smoke passed; root shadow-parity passed; root adopt verify WI-846 passed; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main passed for 0.1.131 -> 0.1.132; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py passed with checked 39 surfaces.
- Recovery Boundary: Only #846 pre-review Governance Lint consumption, `loom_check.py` contract/negative fixture validation, generated skills surface, and WI-846 carriers are in scope.
- Current Lane: branch `work/846-governance-lint-check-pre-review` in formal worktree `/Users/mc/dev/Loom-work-846-governance-lint-check-pre-review`, bound to issue #846 and parent #844.

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-846.md
- Dynamic Truth: .loom/progress/WI-846.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
