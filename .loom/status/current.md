# Current Status

## Derived Fact Chain View

- Item ID: WI-1129
- Goal: Implement `loom suite evidence scaffold` dry-run and explicit apply for evidence-map scaffold generation.
- Scope: #1129 only: update `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/full-spec-suite-cli-surface.md`, `docs/methodology/harness/cli-command-matrix.md`, terminalize `.loom/progress/WI-1127.md`, refresh root shadow parity hashes for `.loom/status/current.md`, and WI-1129 Loom carriers so evidence-map scaffold plans and writes `.loom/specs/<item>/evidence-map.md` safely. Do not implement carrier validation, merge-ready integration, closeout reconciliation, host writes, `/speckit.*`, or `.specify/` surfaces.
- Execution Path: issue #1129 -> branch work/1129-suite-evidence-scaffold -> worktree /Users/mc/dev/Loom-worktrees/1129-suite-evidence-scaffold -> PR #1172
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1129.md
- Review Entry: .loom/reviews/WI-1129.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1129 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1129 is closed completed, and #1126 can consume the evidence.
- Current Checkpoint: build
- Current Stop: PR #1172 is open on branch `work/1129-suite-evidence-scaffold` at head `bd4aef9fa45b7c8777d8d57a69a1f4e286ba8e3f`.
- Next Step: Run PR gate, wait for required checks, merge, and close out #1129.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1129 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1129 --json; python3 tools/loom.py suite evidence scaffold --target . --item WI-1129 --json; git diff --check; focused rg for suite evidence scaffold, missing, /speckit, and .specify; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1129; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1129; PR #1172 opened at head bd4aef9fa45b7c8777d8d57a69a1f4e286ba8e3f.
- Recovery Boundary: #1129 owns evidence-map scaffold dry-run/apply only. It must not implement carrier validation, merge-ready integration, closeout reconciliation, host writes, `/speckit.*`, or `.specify` surfaces. Generated scaffold rows must start as `missing` and cannot satisfy evidence validation until authored evidence updates them.
- Current Lane: full-spec-suite-cli/evidence-map-scaffold

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1129 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1129 --json; python3 tools/loom.py suite evidence scaffold --target . --item WI-1129 --json; git diff --check; focused rg for suite evidence scaffold, missing, /speckit, and .specify; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1129; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1129; PR #1172 opened at head bd4aef9fa45b7c8777d8d57a69a1f4e286ba8e3f.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1129.md
- Dynamic Truth: .loom/progress/WI-1129.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
