# Current Status

## Derived Fact Chain View

- Item ID: WI-873
- Goal: 收敛 PR metadata machine carrier contract 与 parser preflight，使 repo-specific PR metadata 不再依赖自由 Markdown。
- Scope: 扩展 repo companion metadata_contract machine_carrier 合同；实现 pr-metadata preflight CLI；接入 pr-gate check 与 flow merge-ready；补充 loom_check fixtures；同步 adoption/harness 文档、shared references、skills 安装面与 demo runtime。
- Execution Path: harness/pr-metadata-machine-preflight
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-873.md
- Review Entry: .loom/reviews/WI-873.json
- Validation Entry: python3 tools/skills_surface.py generate; make check; python3 tools/loom_check.py .; git diff --check; direct pr-metadata preflight fixture CLI checks
- Closing Condition: PR for #873 is merge-ready or merged with PR metadata machine contract, parser preflight, diagnostics, migration behavior, and fixture coverage validated.
- Current Checkpoint: merge checkpoint
- Current Stop: Implementation is committed and PR #982 is bound to #873; active fact chain now points at WI-873, and predecessor WI-965 is terminal after PR #979 merge/issue #965 closeout readback.
- Next Step: Record fresh formal review for WI-873, rerun local gates, push PR #982, confirm CI and merge readiness, then merge or record any remaining blocker.
- Blockers: None recorded.
- Latest Validation Summary: After carrier recovery: fact-chain pass; #979/#965 GitHub readback confirmed WI-965 is terminal; git diff --check passed. Earlier implementation validation passed: py_compile for governance_surface/loom_flow/loom_check; python3 tools/skills_surface.py generate; make check; python3 tools/loom_check.py .; direct pr-metadata preflight fixtures. make test unavailable because this repository has no test target.
- Recovery Boundary: WI-873 owns PR metadata machine carrier contract, parser/preflight runtime integration, diagnostics/migration behavior, loom_check fixtures, docs/reference sync, generated skills/runtime surfaces, and WI-873 carriers/review. Excludes adopting WebEnvoy-specific field taxonomy or unrelated governance gate redesign.
- Current Lane: pr-review

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-873.md
- Dynamic Truth: .loom/progress/WI-873.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
