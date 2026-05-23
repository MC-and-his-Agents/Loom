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
- Current Stop: Implementation, fixture sync, and refreshed code review are committed locally for PR #982 after rebase onto origin/main.
- Next Step: Push rebased branch with force-with-lease, update PR #982 validation and binding evidence, confirm CI, then merge and close out #873.
- Blockers: None recorded.
- Latest Validation Summary: Post-rebase validation passed: python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-873; git diff --check; make check; python3 tools/loom_check.py .; direct pr-metadata preflight CLI fixtures for valid, malformed, and missing-field PR payloads. make test unavailable: no Makefile target.
- Recovery Boundary: WI-873 owns PR metadata machine carrier contract, parser/preflight runtime integration, diagnostics/migration behavior, loom_check fixtures, docs/reference sync, generated skills/runtime surfaces, and WI-873 carriers/review. Excludes adopting WebEnvoy-specific field taxonomy or unrelated governance gate redesign.
- Current Lane: merge-ready

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
