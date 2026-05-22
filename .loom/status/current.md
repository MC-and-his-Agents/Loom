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
- Current Stop: Codex App live review timeout and process-group cleanup are committed. Focused self-check after that code change passed, including `tools/py_compile_clean.py`, skills surface, version surface, bootstrap verify, fact-chain, and flow review.
- Next Step: Rerun Codex App default-host review on the current head and record only the normalized review_record_input if it allows.
- Blockers: None
- Latest Validation Summary: Post-timeout-fix self-check passed with git diff --check, tools/py_compile_clean.py, skills_surface check, version surface check, `.loom/bin/loom_init.py verify --target .`, fact-chain, and flow review. The prior live Codex App review on 823b34d selected loom/codex-app-review from codex-app-host-default with stdio://, thread cwd bound to /Users/mc/dev/Loom-863-codex-app-review-host-proof, and reviewed_head 823b34d. It returned block only after proving the App path and identifying the missing live deadline/process cleanup boundary; that boundary is now fixed in src and generated skills surfaces.
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
