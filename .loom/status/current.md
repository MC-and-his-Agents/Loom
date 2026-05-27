# Current Status

## Derived Fact Chain View

- Item ID: WI-1050
- Goal: Update scenario skills so `loom-story`, `loom-spec-review`, `loom-build`, `loom-pre-review`, and `loom-merge-ready` consume full/minimal suite path boundaries.
- Scope: #1050 scenario skills full/minimal path consumption only. Do not redefine #1014-#1019 core contracts, do not implement CLI command surface (#1052), and do not perform #1051 drift-check ownership beyond regenerating `skills/` from `src/skills` to keep the checked-in skill surface consistent.
- Execution Path: issue #1050 -> branch work/1050-scenario-skills-full-minimal -> worktree /Users/mc/dev/Loom-worktrees/1050-scenario-skills-full-minimal
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1050.md
- Review Entry: .loom/reviews/WI-1050.json
- Validation Entry: git diff --check; focused rg checks for full/minimal suite path, scenario/acceptance mapping, not_applicable rationale, consumer boundary, recheck condition, and fail-closed boundaries; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/host_adapter_check.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py.
- Closing Condition: #1050 scenario skills consume full/minimal suite path boundaries, PR is merged, closeout evidence comment is written, issue is closed, and Project status is reconciled.
- Current Checkpoint: merge-ready
- Current Stop: Scenario skills and generated skill surface updated locally; review records are bound to the implementation baseline commit.
- Next Step: Run checkpoint merge and PR gate, open PR, wait for checks, merge, then close #1050.
- Blockers: None recorded.
- Latest Validation Summary: Passed locally on branch `work/1050-scenario-skills-full-minimal`: `git diff --check`; focused `rg` checks for full/minimal suite path, scenario/acceptance mapping, `not_applicable` rationale, consumer boundary, recheck condition, and fail-closed boundaries; `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/check_release_surface.py`; `python3 tools/host_adapter_check.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`.
- Recovery Boundary: #1050 owns scenario skills full/minimal path consumption boundaries. Do not redefine #1014-#1019 core contracts, do not implement CLI command surface, and leave #1051 responsible for broader source/generated drift-check ownership and #1036 consumption.
- Current Lane: scenario-skills-full-minimal

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg checks for full/minimal suite path, scenario/acceptance mapping, not_applicable rationale, consumer boundary, recheck condition, and fail-closed boundaries; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_release_surface.py; python3 tools/host_adapter_check.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1050.md
- Dynamic Truth: .loom/progress/WI-1050.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
