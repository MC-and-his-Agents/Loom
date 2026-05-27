# Current Status

## Derived Fact Chain View

- Item ID: WI-1115
- Goal: Implement explicit repo-local writes for `loom suite scaffold --apply`.
- Scope: #1115 only: allow `loom suite scaffold --apply` to create missing minimal `spec.md` and `plan.md` files under `.loom/specs/<item>/`, preserve existing files, report actual `created_locators`, and keep full suite generation, host writes, review writes, merge-ready writes, closeout writes, generated skills, spec-kit command names, and `.specify/` layout out of scope.
- Execution Path: issue #1115 -> branch work/1115-suite-scaffold-apply -> worktree /Users/mc/dev/Loom-worktrees/1115-suite-scaffold-apply -> PR #1161
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1115.md
- Review Entry: .loom/reviews/WI-1115.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py help --json; python3 tools/loom.py suite scaffold --target <tmp> --item WI-1115 --json --apply; python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py
- Closing Condition: #1115 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1115 is closed completed, and #1113 can consume the evidence.
- Current Checkpoint: merge checkpoint
- Current Stop: PR #1161 is open at head `f8aecbe2855f3596367b182229113bb572f31d2b`; local merge checkpoint and PR gate are next.
- Next Step: Run local merge checkpoint and PR gate for PR #1161, then wait for required GitHub checks before controlled merge.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py help --json; python3 tools/loom.py suite scaffold --target <tmp> --item WI-1115 --json --apply; targeted traversal item, absolute item, symlink artifact, and directory artifact fail-closed checks; python3 tools/check_cli_contract.py; git diff --check; focused rg for suite scaffold apply and fail-closed anchors; python3 tools/skills_surface.py check; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1115 --write; python3 .loom/bin/loom_flow.py governance-profile status --target .; python3 .loom/bin/loom_flow.py runtime-parity validate --target .; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1115; python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1115.
- Recovery Boundary: #1115 owns explicit repo-local `loom suite scaffold --apply` writes for missing minimal `.loom/specs/<item>/spec.md` and `plan.md` only. It preserves existing files, reports actual created locators, fails closed for traversal or absolute items, symlink paths, and non-file artifact placeholders, keeps dry-run read-only, keeps full suite generation reserved, and must not write host, review, merge-ready, closeout, generated skills, spec-kit command names, or `.specify/` surfaces.
- Current Lane: full-spec-suite-cli/suite-scaffold-apply

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg checks for suite scaffold anchors; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1115.md
- Dynamic Truth: .loom/progress/WI-1115.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
