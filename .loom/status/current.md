# Current Status

## Derived Fact Chain View

- Item ID: WI-1110
- Goal: Expose suite path and artifact inventory locators in loom suite inspect.
- Scope: #1110 only: extend read-only suite inspect to derive explicit suite path decisions and repo-relative artifact inventory locators; update focused CLI contract fixtures; no readiness decision, scaffold writes, host mutation, review truth mutation, merge-ready truth, closeout truth, or spec-kit names/layout.
- Execution Path: issue #1110 -> branch work/1110-suite-inspect-locators -> worktree /Users/mc/dev/Loom-worktrees/1110-suite-inspect-locators -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1110.md
- Review Entry: .loom/reviews/WI-1110.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py suite inspect --target . --item WI-1110 --json; python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py
- Closing Condition: #1110 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1110 is closed completed, and #1108 can consume the evidence.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-1110 PR #1157 is open at head faf24ee9626845fe4e0901f6e11a1b505f0ea53f; local validation, spec review, implementation review, and host readback are complete.
- Next Step: Run PR gate and GitHub required checks for PR #1157, then perform controlled merge, closeout sync, Project Done update, and parent #1108 evidence consumption.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py suite inspect --target . --item WI-1110 --json; python3 tools/check_cli_contract.py; git diff --check; focused rg for suite inspect locator anchors; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1110; PR #1157 host readback head faf24ee9626845fe4e0901f6e11a1b505f0ea53f.
- Recovery Boundary: #1110 owns read-only suite inspect path decision and repo-relative artifact locator reporting plus focused CLI fixtures. It must not implement readiness validation, scaffold writes, evidence freshness, host mutation, review truth mutation by suite commands, merge-ready truth, closeout truth, spec-kit names, or .specify layout.
- Current Lane: full-spec-suite-cli/suite-inspect-locators

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg checks for full suite, task carrier, evidence-map, consistency-analysis, source/generated, generated skills, and drift boundaries; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/host_adapter_check.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1110.md
- Dynamic Truth: .loom/progress/WI-1110.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
