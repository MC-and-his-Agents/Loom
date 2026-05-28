# Current Status

## Derived Fact Chain View

- Item ID: WI-1127
- Goal: Implement `loom suite evidence inspect` and `loom suite evidence validate` for evidence-map row inventory and freshness validation.
- Scope: #1127 only: update `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/full-spec-suite-cli-surface.md`, `docs/methodology/harness/cli-command-matrix.md`, terminalize `.loom/progress/WI-1125.md`, refresh root shadow parity hashes for `.loom/status/current.md`, and WI-1127 Loom carriers so evidence-map inspect/validate can report missing, stale, and missing fresh verification findings. Do not implement `suite evidence scaffold`, carrier validation, merge-ready integration, closeout reconciliation, host writes, `/speckit.*`, or `.specify/` surfaces.
- Execution Path: issue #1127 -> branch work/1127-suite-evidence-validate -> worktree /Users/mc/dev/Loom-worktrees/1127-suite-evidence-validate -> PR #1171
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1127.md
- Review Entry: .loom/reviews/WI-1127.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1127 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1127 is closed completed, and #1126 can consume the evidence.
- Current Checkpoint: merge
- Current Stop: PR #1171 is open for WI-1127 on branch `work/1127-suite-evidence-validate` with local checkpoint validation recorded.
- Next Step: Refresh review evidence for PR #1171, pass PR gate, merge, and close out #1127.
- Blockers: None
- Latest Validation Summary: Passed: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite evidence command names, failure kinds, `/speckit`, and `.specify`; python3 tools/loom.py suite validate --target . --item WI-1127 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1127 --json; python3 tools/check_cli_contract.py; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1127.
- Recovery Boundary: #1127 owns evidence-map inspect/validate row inventory and freshness validation only, plus terminalizing the already-merged WI-1125 recovery carrier and refreshing root shadow parity hashes for `.loom/status/current.md` drift introduced by this Work Item. It must not implement evidence scaffold writes, carrier validation, merge-ready integration, closeout reconciliation, host writes, `/speckit.*`, or `.specify` surfaces.
- Current Lane: full-spec-suite-cli/evidence-map-validation

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: Passed: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; git diff --check; focused rg for suite evidence command names, failure kinds, `/speckit`, and `.specify`; python3 tools/loom.py suite validate --target . --item WI-1127 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1127 --json; python3 tools/check_cli_contract.py; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1127.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1127.md
- Dynamic Truth: .loom/progress/WI-1127.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
