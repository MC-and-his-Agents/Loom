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
- Current Stop: Review prompt budget fix self-check passed: prompt now keeps full loom_check/make check/merge-ready/PR gate outside reviewer scope; generated skills surface is synchronized; shadow parity and adopt verify recovered after status hash refresh; full PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py . passed, checked 39 surfaces.
- Next Step: Commit and push prompt budget fix, rerun flow review on clean HEAD, then rerun explicit Codex App review and record only normalized review_record_input.
- Blockers: Pending commit/push and replacement Codex App review for current HEAD.
- Latest Validation Summary: Post-prompt-fix self-check passed: git diff --check, tools/py_compile_clean.py for shared loom_flow/loom_check scripts, PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check, python3 tools/version_surface_check.py, fact-chain, targeted shadow-parity/adopt verify, and full PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py . -> OK, checked 39 surfaces.
- Recovery Boundary: Current checkpoint is review record/head/validation reconciliation for PR #879. Keep scope limited to Codex App review host proof discovery, review run evidence, review record and gate consumption; do not expand #746 adapter migration, remove fallback, or promote raw App output to authored truth.
- Current Lane: review-record-reconciliation

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
