# Current Status

## Derived Fact Chain View

- Item ID: WI-863
- Goal: Fix Codex App main-thread review host proof discovery and prove App review E2E for #863/#864.
- Scope: Codex App review host proof discovery, adapter selection, missing-proof diagnostics, focused fixtures, live review evidence, review record, and merge-ready/review gate consumption.
- Execution Path: issue-scoped branch work/863-codex-app-review-host-proof in independent worktree /Users/mc/dev/Loom-863-codex-app-review-host-proof
- Workspace Entry: ./
- Recovery Entry: .loom/progress/WI-863.md
- Review Entry: .loom/reviews/WI-863.json
- Validation Entry: py_compile; skills_surface check; loom_check; live Codex App review run; review record; merge-ready/review gate
- Closing Condition: #863/#864 evidence accepted, PR gates pass, controlled merge completes, main syncs, and issue closeout records proof.
- Current Checkpoint: merge
- Current Stop: Live Codex App review refreshed for current HEAD 5f9b27c: explicit App review used stdio://, new-thread, formal worktree cwd, selected loom/codex-app-review with no fallback, thread cwd matched target root, and .loom/reviews/WI-863.json consumes only normalized review_record_input.
- Next Step: Run carrier refresh, adopt verify, shadow parity, full loom_check, then merge-ready/checkpoint merge/PR gate for PR #879 and GitHub checks.
- Blockers: None
- Latest Validation Summary: Current HEAD 5f9b27c self-check and live review passed: git diff --check, tools/py_compile_clean.py for shared loom_flow/loom_check scripts, PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check, python3 tools/version_surface_check.py, node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main, fact-chain, flow review, full PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py . -> OK checked 39 surfaces, and explicit Codex App review produced normalized allow review_record_input.
- Recovery Boundary: Current checkpoint is merge-ready/review gate consumption for PR #879. Keep scope limited to Codex App review host proof discovery, review run evidence, review record and gate consumption; do not expand #746 adapter migration, remove fallback, or promote raw App output to authored truth.
- Current Lane: merge-ready-gate-consumption

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-863.md
- Dynamic Truth: .loom/progress/WI-863.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
