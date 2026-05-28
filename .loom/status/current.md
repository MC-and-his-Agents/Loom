# Current Status

## Derived Fact Chain View

- Item ID: WI-1120
- Goal: Implement the core read-only `loom suite validate` command.
- Scope: #1120 only: add the command matrix entry, read-only validate envelope, core pass/block/advisory/not_applicable behavior, and CLI contract fixtures. Defer deeper path artifact validation, not_applicable rationale enforcement, spec/plan mapping, taxonomy expansion, and spec-review integration to #1121-#1125.
- Execution Path: issue #1120 -> branch work/1120-suite-validate-core -> worktree /Users/mc/dev/Loom-worktrees/1120-suite-validate-core -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1120.md
- Review Entry: .loom/reviews/WI-1120.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1120 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1120 is closed completed, and #1119 can consume the evidence.
- Current Checkpoint: build checkpoint
- Current Stop: Branch work/1120-suite-validate-core has passed local validation, shadow parity, and build checkpoint for #1120.
- Next Step: Push branch, open PR, run PR gate and GitHub checks, then merge and close out #1120.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite validate, suite validate constants, forbidden /speckit and .specify surfaces; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1120.
- Recovery Boundary: #1120 owns core `loom suite validate` command behavior only. It must not implement #1121 path-depth checks, #1122 not_applicable rationale enforcement, #1123 spec/plan mapping, #1124 final taxonomy expansion, #1125 spec-review integration, host writes, review writes, merge-ready writes, closeout writes, /speckit.*, or .specify surfaces.
- Current Lane: full-spec-suite-cli/validate-core

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite validate, suite validate constants, /speckit, and .specify; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1120.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1120.md
- Dynamic Truth: .loom/progress/WI-1120.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
