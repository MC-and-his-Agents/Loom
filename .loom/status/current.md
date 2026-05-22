# Current Status

## Derived Fact Chain View

- Item ID: WI-851
- Goal: 为 Governance Lint 增加 negative fixtures，覆盖 approval bypass、companion / interop 边界绕过、core hardcoding guard、高级 lint 声明缺口以及 stale evidence / head drift。
- Scope: 新增 `governance-lint-negative-fixtures.json`、扩展 `loom_check.py` repo-local fixture 消费、同步 generated skills surface 和 installer version；不新增独立 lint CLI、不复制下游 guardian 实现、不把 repo-specific 规则写入 Loom core。
- Execution Path: harness/governance-lint/negative-fixtures
- Workspace Entry: /Users/mc/dev/Loom-work-851-governance-lint-negative-fixtures
- Recovery Entry: .loom/progress/WI-851.md
- Review Entry: .loom/reviews/WI-851.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py
- Closing Condition: PR merge 后 closeout 消费 #851 issue、PR、merge commit、Project #4 状态，并解除 #852 的 negative-fixtures blocker。
- Current Checkpoint: merge-ready
- Current Stop: #851 implementation is committed at 7520d60a2cb8d34fac1c0ec791ea62f4b771f1c7; authored spec and implementation reviews are recorded against that implementation head. Full `tools/loom_check.py` passed naturally with 39 checked surfaces after the stale evidence lint gap was fixed.
- Next Step: Commit carrier-only review/status sync, rerun checkpoint merge, then push and open PR for #851.
- Blockers: None recorded.
- Latest Validation Summary: py_compile_clean passed for source/generated loom_flow.py and loom_check.py; skills_surface check passed; targeted check_governance_lint_negative_fixture_contract passed with 0 failures; git diff --check passed; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py passed naturally with checked 39 surfaces.
- Recovery Boundary: Only #851 Governance Lint negative fixture manifest, repo-local checker consumption, installed runtime negative PR-gate fixtures, generated skills surface, installer version bump, and WI-851 carriers are in scope.
- Current Lane: branch work/851-governance-lint-negative-fixtures in formal worktree /Users/mc/dev/Loom-work-851-governance-lint-negative-fixtures, bound to issue #851 and parent #844; baseline origin/main@6acefb2046c1e432e70e869cb01e2a267fd99cba.

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-851.md
- Dynamic Truth: .loom/progress/WI-851.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
