# Current Status

## Derived Fact Chain View

- Item ID: WI-1121
- Goal: Validate suite path decisions and required/conditional suite artifacts.
- Scope: #1121 only: block missing, invalid, or conflicting suite path decisions; block missing or non-file required artifacts; inventory full path conditional artifacts without enforcing rationale. Defer not_applicable/deferred rationale to #1122, spec/plan mapping to #1123, taxonomy expansion to #1124, and spec-review integration to #1125.
- Execution Path: issue #1121 -> branch work/1121-suite-path-artifacts -> worktree /Users/mc/dev/Loom-worktrees/1121-suite-path-artifacts -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1121.md
- Review Entry: .loom/reviews/WI-1121.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1121 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1121 is closed completed, and #1119 can consume the evidence.
- Current Checkpoint: build
- Current Stop: Branch work/1121-suite-path-artifacts has implemented path decision and required/conditional artifact validation with focused local checks passing.
- Next Step: Record reviews, run build checkpoint, open PR, pass merge gate, merge, and close out #1121.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite_path, conditional artifacts, conflicting_suite_path_decision, invalid_suite_path_decision, forbidden /speckit and .specify surfaces; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Recovery Boundary: #1121 owns suite path decision legality, required artifact existence/regular-file validation, and conditional artifact inventory only. It must not implement #1122 not_applicable/deferred rationale enforcement, #1123 spec/plan mapping checks, #1124 final taxonomy expansion, #1125 spec-review integration, host writes, review writes from the CLI command, merge-ready writes, closeout writes, /speckit.*, or .specify surfaces.
- Current Lane: full-spec-suite-cli/validate-path-artifacts

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite_path, conditional artifacts, conflicting_suite_path_decision, invalid_suite_path_decision, /speckit, and .specify; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1121.md
- Dynamic Truth: .loom/progress/WI-1121.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
