# Current Status

## Derived Fact Chain View

- Item ID: WI-897
- Goal: Close #897 legacy repo migration validation and release judgment for #885 CLI-first phase
- Scope: #897 only: WebEnvoy/Syvert/HotCP legacy validation, migration playbook, three-repo validation evidence, and release judgment handoff to #996
- Execution Path: issue #897 -> branch work/897-legacy-validation -> formal worktree /Users/mc/dev/Loom-897-legacy-validation -> PR TBD
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-897.md
- Review Entry: .loom/reviews/WI-897.json
- Validation Entry: python3 tools/check_cli_contract.py; python3 tools/version_surface_check.py; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-897; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py pr-gate check --target . --pr <PR> --head-sha <HEAD> --item WI-897; make check
- Closing Condition: #948-#952 evidence is versioned, #897 PR is merge-ready or merged, release judgment is recorded for #996 consumption, and fact chain/PR/head_sha are consistent
- Current Checkpoint: merge
- Current Stop: PR #999 is open at head `7cedd042c43c40027a02893c94e94a0e269f0820`; local validation and review records are present, and PR gate is being reconciled.
- Next Step: Run PR gate against the current PR head and consume GitHub checks before merge.
- Blockers: None recorded.
- Latest Validation Summary: Reviewed head `e1351c425e5f5a89abf02418158eee71f19d4ae9` passed: `python3 tools/check_cli_contract.py`; `python3 tools/version_surface_check.py`; `npm --prefix packages/loom-installer run check:versions`; `npm --prefix packages/loom-installer run check:payload`; `npm --prefix packages/loom-installer run check:distribution`; `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-897`; `python3 .loom/bin/loom_flow.py shadow-parity --target .`; `python3 .loom/bin/loom_flow.py fact-chain --target .`; `make check`.
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
