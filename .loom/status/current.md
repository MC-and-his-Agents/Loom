# Current Status

## Derived Fact Chain View

- Item ID: WI-852
- Goal: 在 status surface 与 merge-ready 消费 Governance Lint evidence，提前暴露 blocking/advisory lint 风险且不制造第二 authored truth。
- Scope: 更新 status/merge-ready Governance Lint evidence 消费、deterministic loom_check 断言、输出合同与 generated skills surface；不改写 review approval、PR gate、controlled merge 或 repo-specific 私有规则。
- Execution Path: harness/governance-lint/status-merge-ready-consumption
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-852.md
- Review Entry: .loom/reviews/WI-852.json
- Validation Entry: py_compile_clean; skills_surface check; targeted daily execution and governance lint fixture checks; tools/loom_flow.py flow merge-ready; tools/loom_status.py; tools/loom_check.py
- Closing Condition: PR merge 后 closeout 消费 #852 issue、PR、merge commit、Project #4 状态，并解除 #844 的剩余 Governance Lint blocker。
- Current Checkpoint: merge checkpoint
- Current Stop: Implementation and portable workspace carrier evidence are aligned through reviewed head 2ccc73b5e98b2013dd724288e2ec2347337c71a6; later changes are review/status carrier-only.
- Next Step: Verify PR head/readiness metadata, consume merge-ready evidence, then controlled-merge and closeout if host checks pass.
- Blockers: None recorded.
- Latest Validation Summary: py_compile_clean passed for source/generated loom_flow.py, loom_status.py, and loom_check.py; tools/skills_surface.py check passed; git diff --check passed; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main passed; state-check WI-852 passed; flow merge-ready WI-852 passed with governance_lint(surface=merge_ready) result=pass before portable workspace refresh; loom_status WI-852 passed with governance_lint(surface=status) result=pass; shadow-parity passed; adopt verify passed; pr-gate local check passed; full python3 tools/loom_check.py . passed with 39 surfaces.
- Recovery Boundary: Only #852 status/merge-ready Governance Lint consumption, deterministic loom_check coverage, output contracts, generated skills surface, installer version metadata, portable workspace carrier metadata, shadow hash refreshes, and WI-852 carriers are in scope.
- Current Lane: branch work/852-governance-lint-status-merge-ready in formal worktree /Users/mc/dev/Loom-work-852-governance-lint-status-merge-ready, bound to issue #852 and parent #844

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-852.md
- Dynamic Truth: .loom/progress/WI-852.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
