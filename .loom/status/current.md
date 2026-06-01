# Current Status

## Derived Fact Chain View

- Item ID: WI-874
- Goal: Validate Loom-managed PR body render/edit metadata immediately after render and after `gh pr edit`.
- Scope: #874 only: add PR body artifact preflight, post-edit/readback machine block comparison, safe `gh pr edit --body-file` guidance, focused fixtures, generated skills surface sync, and consume #877 terminal carrier updates in `.loom/progress/WI-877.md` / `.loom/work-items/WI-877.md` so the active fact chain is single-owner. Do not implement #875 Markdown drift/legacy migration expansion, #957 readiness/cost guard, or #1107 full spec suite CLI tree.
- Execution Path: issue #874 -> branch work/874-pr-body-render-edit-preflight -> workspace `.` in the checked out issue-scoped worktree recorded on issue #874 -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-874.md
- Review Entry: .loom/reviews/WI-874.json
- Validation Entry: git diff --check; focused rg for body-file, compare-body-file, gh pr edit, metadata-preflight, raw_excerpt_sha256, source_range_or_hash; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_cli_contract.py
- Closing Condition: PR merged to main, issue #874 closed completed, Project Loom Done, and closeout evidence records PR, head SHA, merge commit, target branch, validation, and Project truth.
- Current Checkpoint: build
- Current Stop: Local PR body render/edit metadata preflight implementation and focused contract validation are complete; PR/review/merge/closeout remain pending.
- Next Step: Run final focused validation set, create the issue-scoped PR, then progress through PR gate, controlled merge, reconciliation, and closeout.
- Blockers: None recorded.
- Latest Validation Summary: Passing local evidence on 2026-06-01: `git diff --check`; focused `rg` for `body-file`, `compare-body-file`, `gh pr edit`, `body_artifact`, machine block drift, `source_range_or_hash`, `raw_excerpt_sha256`, and `metadata-preflight`; `python3 tools/skills_surface.py check`; direct `python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .github/PULL_REQUEST_TEMPLATE.md --json`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/check_cli_contract.py`; `python3 tools/check_release_surface.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/loom.py suite validate --target . --item WI-874 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-874 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-874 --json`.
- Recovery Boundary: #874 owns PR body render/edit preflight, safe update guidance, and #877 terminal carrier consumption only; #875 Markdown drift/legacy migration expansion, #957 readiness/cost guard, and #1107 full spec suite CLI tree remain out of scope.
- Current Lane: loom-hardening/pr-body-render-edit-preflight

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-874.md
- Dynamic Truth: .loom/progress/WI-874.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
