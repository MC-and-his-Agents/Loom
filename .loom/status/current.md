# Current Status

## Derived Fact Chain View

- Item ID: WI-1123
- Goal: Validate spec.md to plan.md scenario and acceptance mappings before review.
- Scope: #1123 only: require authored scenario ids and acceptance ids in spec.md to be mechanically consumed by plan.md validation and test strategy rows; block unexplained mapping gaps with `missing_spec_plan_mapping`. Defer final taxonomy expansion to #1124 and spec-review integration to #1125.
- Execution Path: issue #1123 -> branch work/1123-spec-plan-mapping -> worktree /Users/mc/dev/Loom-worktrees/1123-spec-plan-mapping -> PR #1168
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1123.md
- Review Entry: .loom/reviews/WI-1123.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1123 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1123 is closed completed, and #1119 can consume the evidence.
- Current Checkpoint: merge
- Current Stop: PR #1168 is open with WI-1123 implementation, validation, spec review, and implementation review carriers recorded.
- Next Step: Pass PR gate, merge PR #1168, and close out #1123.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for missing_spec_plan_mapping, spec_plan_mapping, suite_spec_plan, /speckit, and .specify surfaces; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1123.
- Recovery Boundary: #1123 owns spec.md to plan.md scenario and acceptance mapping validation in `loom suite validate` only. It must not implement #1124 final failure taxonomy expansion, #1125 spec-review integration, host writes, review writes from the CLI command, merge-ready writes, closeout writes, /speckit.*, or .specify surfaces.
- Current Lane: full-spec-suite-cli/spec-plan-mapping

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for missing_spec_plan_mapping, spec_plan_mapping, suite_spec_plan, /speckit, and .specify; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1123.md
- Dynamic Truth: .loom/progress/WI-1123.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
