# Current Status

## Derived Fact Chain View

- Item ID: WI-1124
- Goal: Emit stable machine-readable suite validation failure taxonomy findings.
- Scope: #1124 only: add suite validate failure taxonomy metadata for emitted readiness findings, including failure kind, default result, failed layer, source locator, consumer impact, remediation direction, fallback, and binding; consume the prior active `.loom/progress/WI-1123.md` carrier by moving it from merge to terminal closed. Defer spec-review gate integration to #1125.
- Execution Path: issue #1124 -> branch work/1124-suite-failure-taxonomy -> worktree /Users/mc/dev/Loom-worktrees/1124-suite-failure-taxonomy -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1124.md
- Review Entry: .loom/reviews/WI-1124.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1124 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1124 is closed completed, and #1119 can consume the evidence.
- Current Checkpoint: build
- Current Stop: Local implementation, carriers, and focused validation are prepared for build checkpoint review; prior WI-1123 active carrier is consumed as terminal closed state.
- Next Step: Run full checkpoint validation, record reviews, open PR, pass PR gate, merge, and close out #1124.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for failure_taxonomy, supported_failure_kinds, default_result, failed_layer, /speckit, .specify, spec-review, and suite validate; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1124.
- Recovery Boundary: #1124 owns stable machine-readable failure taxonomy output for `loom suite validate` findings and the terminalization of `.loom/progress/WI-1123.md` only. It must not implement #1125 spec-review integration, host writes, review writes from the CLI command, merge-ready writes, closeout writes, /speckit.*, or .specify surfaces.
- Current Lane: full-spec-suite-cli/failure-taxonomy

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for failure_taxonomy, supported_failure_kinds, default_result, failed_layer, /speckit, and .specify; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1124.md
- Dynamic Truth: .loom/progress/WI-1124.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
