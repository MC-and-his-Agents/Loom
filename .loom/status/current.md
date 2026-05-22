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
- Current Stop: A renewed Codex App default-host review on ea7b219 proved host adapter discovery and binding but blocked on validation drift: the reviewer inherited repo-local Loom runtime environment while running `tools/skills_surface.py check`, causing installed launcher smoke to see `LOOM_RUNTIME_SCENE=repo-local-demo` and fail the `installed-runtime` contract. `tools/skills_surface.py` now isolates launcher-smoke environment so installed package validation cannot inherit repo-local runtime markers.
- Next Step: Rerun focused self-check on the new head, then rerun Codex App default-host review and record only the normalized review_record_input if it allows.
- Blockers: None
- Latest Validation Summary: Focused self-check before renewed review passed on ea7b219: git diff --check, version surface check, PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile for shared loom_flow/loom_check scripts, PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check after pycache cleanup, fact-chain for WI-863, and flow review. The renewed live Codex App review selected loom/codex-app-review from codex-app-host-default with stdio://, thread cwd bound to /Users/mc/dev/Loom-863-codex-app-review-host-proof, and reviewed_head ea7b219, but returned block because reviewer validation inherited repo-local runtime environment and made installed launcher smoke fail. Root cause was reproduced with LOOM_RUNTIME_SCENE/LOOM_SOURCE_REPO_ROOT/LOOM_INSTALLED_SKILLS_ROOT in the outer environment, then fixed by isolating launcher-smoke environment in tools/skills_surface.py; the contaminated-env reproduction now passes, and py_compile cache was cleaned.
- Recovery Boundary: Scope remains #863/#864 review host proof discovery, adapter selection, diagnostic, fixture, live review evidence, review record, and merge-ready/review gate consumption.
- Current Lane: live-E2E-proof

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
