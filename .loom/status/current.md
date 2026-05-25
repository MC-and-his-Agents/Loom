# Current Status

## Derived Fact Chain View

- Item ID: WI-897
- Goal: Close #897 legacy repo migration validation and release judgment for #885 CLI-first phase
- Scope: #897 only: WebEnvoy/Syvert/HotCP legacy validation, migration playbook, three-repo validation evidence, and release judgment handoff to #996
- Execution Path: issue #897 -> branch work/897-legacy-validation -> formal worktree /Users/mc/dev/Loom-897-legacy-validation -> PR TBD
- Workspace Entry: /Users/mc/dev/Loom-897-legacy-validation
- Recovery Entry: .loom/progress/WI-897.md
- Review Entry: .loom/reviews/WI-897.json
- Validation Entry: python3 tools/check_cli_contract.py; python3 tools/version_surface_check.py; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-897; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py pr-gate check --target . --pr <PR> --head-sha <HEAD> --item WI-897; make check
- Closing Condition: #948-#952 evidence is versioned, #897 PR is merge-ready or merged, release judgment is recorded for #996 consumption, and fact chain/PR/head_sha are consistent
- Current Checkpoint: admission checkpoint
- Current Stop: Legacy migration fixture, playbook, validation evidence, and local validation suite are complete; PR creation and PR gate remain.
- Next Step: Commit implementation, push branch, create PR, then run PR gate and consume GitHub checks.
- Blockers: None recorded.
- Latest Validation Summary: Passed: `python3 tools/check_cli_contract.py`; `python3 tools/version_surface_check.py`; `npm --prefix packages/loom-installer run check:versions`; `npm --prefix packages/loom-installer run check:payload`; `npm --prefix packages/loom-installer run check:distribution`; `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-897`; `python3 .loom/bin/loom_flow.py shadow-parity --target .`; `python3 .loom/bin/loom_flow.py fact-chain --target .`; `make check`.
- Recovery Boundary: Continue from `/Users/mc/dev/Loom-897-legacy-validation` on branch `work/897-legacy-validation`.
- Current Lane: legacy migration validation

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check-runtime-regression; make py-compile; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main; make loom-check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-897.md
- Dynamic Truth: .loom/progress/WI-897.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
