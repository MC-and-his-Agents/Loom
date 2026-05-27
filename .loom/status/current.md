# Current Status

## Derived Fact Chain View

- Item ID: WI-1117
- Goal: Define and verify scaffold overwrite, rollback, and created locator JSON audit fields.
- Scope: #1117 only: harden `loom suite scaffold` JSON contract coverage for `planned_writes`, `source_templates`, `overwrite_policy`, `apply_required`, `rollback_note`, and `created_locators`, including ambiguous overwrite fail-closed evidence. Do not add rollback execution, new scaffold artifacts, host writes, review writes, merge-ready writes, closeout writes, generated skills, spec-kit command names, or `.specify/` layout.
- Execution Path: issue #1117 -> branch work/1117-scaffold-json -> worktree /Users/mc/dev/Loom-worktrees/1117-scaffold-json -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1117.md
- Review Entry: .loom/reviews/WI-1117.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py
- Closing Condition: #1117 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1117 is closed completed, and #1113 can consume the evidence.
- Current Checkpoint: PR checkpoint
- Current Stop: Branch work/1117-scaffold-json has validated scaffold JSON audit contract coverage and formal reviews recorded; PR creation is next.
- Next Step: Push branch, open PR for #1117, run PR gate and GitHub checks, then merge and close out #1117.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_cli_contract.py; git diff --check; focused rg for rollback_note, ambiguous_overwrite, created_locators, planned_writes, source_templates, apply_required, /speckit, and .specify; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1117; formal spec and general reviews recorded.
- Recovery Boundary: #1117 owns scaffold JSON contract coverage for overwrite, rollback, planned write, source template, apply-required, and created locator fields only. It must not add rollback execution, new scaffold artifacts, host writes, review writes, merge-ready writes, closeout writes, generated skills, /speckit.*, or .specify surfaces.
- Current Lane: full-spec-suite-cli/scaffold-json-audit

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg checks for suite scaffold anchors; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1117.md
- Dynamic Truth: .loom/progress/WI-1117.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
