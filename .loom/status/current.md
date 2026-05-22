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
- Current Stop: A renewed Codex App default-host review on 8c26fac proved host adapter discovery and binding, and confirmed the prior skills-surface validation drift no longer reproduces, but blocked because the prior authored review record had not yet been refreshed to 8c26fac. The review prompt now states that the current review run's normalized output is the candidate `review_record_input` and must not require `.loom/reviews/<item>.json` to be pre-refreshed before the run can allow.
- Next Step: Commit the prompt clarification and generated surfaces, rerun focused self-check with `tools/py_compile_clean.py`, then rerun Codex App default-host review and record only the normalized review_record_input if it allows.
- Blockers: None
- Latest Validation Summary: Focused self-check on clean 8c26fac passed before this prompt clarification: git diff --check, version surface check, py_compile coverage with cache cleanup, normal and contaminated-env skills_surface checks, fact-chain, and flow review. The renewed live Codex App review selected loom/codex-app-review from codex-app-host-default with stdio://, thread cwd bound to /Users/mc/dev/Loom-863-codex-app-review-host-proof, and reviewed_head 8c26fac. It returned block only because the prior authored review record was still stale before consuming the current run's normalized review_record_input; prompt guidance was updated in src and generated skills surfaces to make that replacement-evidence boundary explicit. The next self-check must use `tools/py_compile_clean.py` per the updated goal.
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
