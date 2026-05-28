# Current Status

## Derived Fact Chain View

- Item ID: WI-1130
- Goal: Validate evidence freshness and HEAD / PR head binding for suite evidence-map consumption.
- Scope: #1130 only: update `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/full-spec-suite-cli-surface.md`, `docs/methodology/harness/cli-command-matrix.md`, terminalize `.loom/progress/WI-1129.md`, refresh root shadow parity hashes for `.loom/status/current.md`, and WI-1130 Loom carriers so `loom suite evidence validate` blocks stale evidence, missing present source locators, validation summary drift, and HEAD / PR head binding drift. Do not implement carrier validation, merge-ready integration, closeout reconciliation, host writes, `/speckit.*`, or `.specify` surfaces.
- Execution Path: issue #1130 -> branch work/1130-suite-evidence-freshness -> worktree /Users/mc/dev/Loom-worktrees/1130-suite-evidence-freshness -> PR #1173
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1130.md
- Review Entry: .loom/reviews/WI-1130.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1130 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1130 is closed completed, and #1126 can consume the evidence.
- Current Checkpoint: build
- Current Stop: PR #1173 is open from branch `work/1130-suite-evidence-freshness`; local review and validation evidence are recorded.
- Next Step: Run PR gate, merge, and close out #1130.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1130 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1130 --json; git diff --check; focused rg for head_or_pr_drift, missing_source_locator, validation_summary_sha256, /speckit, and .specify; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1130; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1130; PR #1173 opened at head 5ab2eebc1d58382616c4003a85439902742c911b.
- Recovery Boundary: #1130 owns evidence freshness and HEAD / PR head binding validation inside `loom suite evidence validate` only. It must not implement carrier validation, merge-ready integration, closeout reconciliation, host writes, `/speckit.*`, or `.specify` surfaces. CLI output remains validation evidence and does not replace Work Item, review, merge-ready, closeout, or docs/source truth.
- Current Lane: full-spec-suite-cli/evidence-freshness-head-binding

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1130 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1130 --json; git diff --check; focused rg for head_or_pr_drift, missing_source_locator, validation_summary_sha256, /speckit, and .specify; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1130; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1130; PR #1173 opened at head 5ab2eebc1d58382616c4003a85439902742c911b.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1130.md
- Dynamic Truth: .loom/progress/WI-1130.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
