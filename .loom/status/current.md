# Current Status

## Derived Fact Chain View

- Item ID: WI-1028
- Goal: Update skills routing so Loom recognizes delivery planning and issue-tree planning scenes before build, review, merge-ready, or story-only shaping.
- Scope: #1028 skills routing boundary only; update route matrix, loom-init, loom-story, and synchronized generated skills surface. Consume #1024 delivery planning, #1025 issue-tree-plan, #1026 PR slicing, and #1027 GitHub mapping. Do not redefine those contracts, implement GitHub API automation, implement CLI commands, or change review/merge-ready truth.
- Execution Path: issue #1028 -> branch work/1028-planning-routing -> worktree /Users/mc/dev/Loom-1028-planning-routing.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1028.md
- Review Entry: .loom/reviews/WI-1028.json
- Validation Entry: git diff --check; rg -n "planning|issue-tree|route matrix|loom-init|loom-story|build|review" skills src docs .loom; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1028 --write; python3 tools/skills_surface.py check; python3 tools/check_npm_package.py; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1028 defines skills routing for delivery planning signals, clarifies when `loom-init` outputs issue-tree planning instead of routing to build/review/merge-ready/story-only shaping, synchronizes generated skills surface, and records closeout evidence back to #1028 and #1014.
- Current Checkpoint: implementation
- Current Stop: Skills routing planning boundary and generated surface sync are implemented locally and validated.
- Next Step: Record review, open PR, consume checks, merge, and close out #1028.
- Blockers: None recorded.
- Latest Validation Summary: Passed: `git diff --check`; focused `rg` checks for planning / issue-tree / route matrix / loom-init / loom-story / build / review routing; `python3 .loom/bin/loom_init.py verify --target .`; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1028 --write`; `python3 tools/skills_surface.py check`; `python3 tools/check_npm_package.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Recovery Boundary: #1028 owns skills routing for delivery planning signals only. Do not redefine #1024 delivery planning, #1025 issue-tree-plan, #1026 PR slicing, #1027 GitHub mapping, task carriers, gate-chain behavior, GitHub API automation, or CLI automation.
- Current Lane: planning-routing

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; rg -n "planning|issue-tree|route matrix|loom-init|loom-story|build|review" skills src docs .loom; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1028 --write; python3 tools/skills_surface.py check; python3 tools/check_npm_package.py; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1028.md
- Dynamic Truth: .loom/progress/WI-1028.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
