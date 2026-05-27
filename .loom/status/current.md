# Current Status

## Derived Fact Chain View

- Item ID: WI-1111
- Goal: Expose `suite inspect` through Loom's declared CLI surface.
- Scope: #1111 only: add the already implemented read-only `loom suite inspect` command to help JSON, the human command matrix, and CLI contract checks; no new suite subcommands, no readiness decision, no scaffold writes, no host mutation, no review truth mutation, no merge-ready truth, no closeout truth, and no spec-kit names/layout.
- Execution Path: issue #1111 -> branch work/1111-suite-inspect-surface -> worktree /Users/mc/dev/Loom-worktrees/1111-suite-inspect-surface -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1111.md
- Review Entry: .loom/reviews/WI-1111.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py help --json; python3 tools/loom.py suite inspect --target . --item WI-1111 --json; python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py
- Closing Condition: #1111 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1111 is closed completed, and #1108 can consume the evidence.
- Current Checkpoint: build checkpoint
- Current Stop: Declared CLI surface edits, spec review, implementation review, shadow parity, adoption verify, runtime parity, and build checkpoint are complete.
- Next Step: Push branch, open PR, run PR metadata/pre-gate checks and host required checks, then controlled merge, closeout, and parent #1108 evidence consumption.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py help --json; python3 tools/loom.py suite inspect --target . --item WI-1111 --json; python3 tools/check_cli_contract.py; git diff --check; focused rg for suite inspect declaration anchors; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py governance-profile status --target .; python3 .loom/bin/loom_flow.py runtime-parity validate --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1111; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1111 --write; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1111.
- Recovery Boundary: #1111 owns declaring the existing read-only `loom suite inspect` surface in help JSON, command matrix docs, and CLI contract checks. It must not implement scaffold, validate, analyze, evidence, consistency, or carrier suite subcommands; must not decide readiness; must not write suite artifacts; must not mutate host state; and must not replace Work Item, review, merge-ready, closeout, or docs/source truth.
- Current Lane: full-spec-suite-cli/suite-inspect-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg checks for full suite, task carrier, evidence-map, consistency-analysis, source/generated, generated skills, and drift boundaries; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/host_adapter_check.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1111.md
- Dynamic Truth: .loom/progress/WI-1111.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
