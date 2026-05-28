# Current Status

## Derived Fact Chain View

- Item ID: WI-1122
- Goal: Validate authored not_applicable rationale for minimal and suite-level suite validation.
- Scope: #1122 only: require authored not_applicable records to include artifact binding, rationale, consumer boundary, and recheck condition; block deferred records when they are the only explanation for a not_applicable readiness gap. Defer spec/plan scenario mapping to #1123, final taxonomy expansion to #1124, and spec-review integration to #1125.
- Execution Path: issue #1122 -> branch work/1122-not-applicable-rationale -> worktree /Users/mc/dev/Loom-worktrees/1122-not-applicable-rationale -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1122.md
- Review Entry: .loom/reviews/WI-1122.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1122 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1122 is closed completed, and #1119 can consume the evidence.
- Current Checkpoint: build
- Current Stop: Local implementation, carriers, and focused validation are prepared for build checkpoint review.
- Next Step: Run build checkpoint, record reviews, open PR, pass PR gate, merge, and close out #1122.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for not_applicable, deferred_as_completed, invalid_not_applicable_rationale, forbidden /speckit and .specify surfaces; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1122.
- Recovery Boundary: #1122 owns not_applicable rationale and deferred distinction in `loom suite validate` only. It must not implement #1123 spec/plan mapping checks, #1124 final failure taxonomy expansion, #1125 spec-review integration, host writes, review writes from the CLI command, merge-ready writes, closeout writes, /speckit.*, or .specify surfaces.
- Current Lane: full-spec-suite-cli/not-applicable-rationale

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite_path, conditional artifacts, conflicting_suite_path_decision, invalid_suite_path_decision, /speckit, and .specify; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1122.md
- Dynamic Truth: .loom/progress/WI-1122.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
