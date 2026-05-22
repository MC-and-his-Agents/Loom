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
- Current Stop: A renewed Codex App default-host review on ff1ddf6 proved host adapter discovery and binding but blocked on reviewer-induced Python cache artifacts during skills surface validation; the review prompt now instructs reviewers to run Python validation with bytecode disabled and clean validation side effects before judging surface purity.
- Next Step: Commit the prompt-side validation hygiene fix, rerun focused self-check on the new head, then rerun Codex App default-host review and record only the normalized review_record_input if it allows.
- Blockers: None
- Latest Validation Summary: Focused self-check before renewed review passed: git diff --check, PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile for shared loom_flow/loom_check scripts, PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check, python3 tools/version_surface_check.py, fact-chain for WI-863, and flow review on the clean ff1ddf6 worktree. The renewed live Codex App review selected loom/codex-app-review from codex-app-host-default with stdio://, thread cwd bound to /Users/mc/dev/Loom-863-codex-app-review-host-proof, and reviewed_head ff1ddf6, but returned block because reviewer validation generated __pycache__ artifacts before running skills_surface. Prompt guidance was updated in src and generated skills surfaces to require bytecode-disabled Python validation and cleanup of reviewer-created cache artifacts before treating skills surface purity as an implementation defect.
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
