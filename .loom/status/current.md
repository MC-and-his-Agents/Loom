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
- Current Stop: Merged origin/main into the WI-863 branch, resolved active fact-chain carriers back to WI-863, and completed focused self-check before renewed review.
- Next Step: Run renewed Codex App default-host review on the post-main-merge head, record normalized review input, refresh carriers, then rerun PR gate and controlled merge.
- Blockers: None
- Latest Validation Summary: After merging origin/main, conflicts were resolved by preserving WI-863 as the active fact-chain/status carrier while retaining main's unrelated WI and skill updates. Focused self-check passed: git diff --check, PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile for shared loom_flow/loom_check scripts, python3 tools/skills_surface.py check, python3 tools/version_surface_check.py, and fact-chain for WI-863. A full post-merge loom_check attempt was discarded because pre-existing concurrent loom_check processes polluted the run; all loom-check-* temp dirs and Python cache artifacts were then cleaned.
- Recovery Boundary: Scope remains #863/#864 review host proof discovery, adapter selection, diagnostic, fixture, live review evidence, review record, and merge-ready/review gate consumption.
- Current Lane: review-run-evidence

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
