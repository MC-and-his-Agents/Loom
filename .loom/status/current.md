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
- Current Stop: Implementation is rebased onto origin/main at 5cdd8db8d80731a0bee036495506a6e67b22e5e6, local validation is complete, and PR #982 is ready for updated push/CI consumption.
- Next Step: Push rebased branch with force-with-lease, update PR #982 head/validation binding, confirm required checks, merge, then verify #873 closeout.
- Blockers: None recorded.
- Latest Validation Summary: Post-5cdd8db rebase validation passed: python3 tools/skills_surface.py generate; make loom-demo-new-project-sync; make check; git diff --check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main; direct pr-metadata preflight CLI fixtures for valid, malformed, and missing-field PR payloads. make test unavailable: no Makefile target.
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
