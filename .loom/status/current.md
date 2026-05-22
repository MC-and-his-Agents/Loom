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
- Current Stop: Post-merge loom_check stability checkpoint passed: shadow-parity now has an explicit 120s loom_check command budget across source, shared runtime, and generated skill runtime copies; generated skills surface is synchronized; full PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py . passed, checked 39 surfaces. Temporary loom-check/loom-pycompile/cache directories from this round were cleaned.
- Next Step: Commit the post-merge loom_check stability fix, then resume PR #879 merge/closeout mainline.
- Blockers: None
- Latest Validation Summary: Post-merge stability self-check passed: tools/py_compile_clean.py for shared loom_flow/loom_check scripts, PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check, python3 tools/version_surface_check.py, git diff --check, root .loom/bin shadow-parity, root .loom/bin adopt verify, and full PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py . -> OK, checked 39 surfaces.
- Recovery Boundary: Current checkpoint is post-merge loom_check and generated skills surface stability only. Existing Codex App host proof and review record remain authoritative; do not expand #746 adapter migration, remove fallback, or promote raw App output to authored truth.
- Current Lane: post-merge-loom-check-stability

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
