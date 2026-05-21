# Current Status

## Derived Fact Chain View

- Item ID: WI-863
- Goal: Fix Codex App main-thread review host proof discovery and prove App review E2E for #863/#864.
- Scope: Codex App review host proof discovery, adapter selection, missing-proof diagnostics, focused fixtures, live review evidence, review record, and merge-ready/review gate consumption.
- Execution Path: issue-scoped branch work/863-codex-app-review-host-proof in independent worktree /Users/mc/dev/Loom-863-codex-app-review-host-proof
- Workspace Entry: /Users/mc/dev/Loom-863-codex-app-review-host-proof
- Recovery Entry: .loom/progress/WI-863.md
- Review Entry: .loom/reviews/WI-863.json
- Validation Entry: py_compile; skills_surface check; loom_check; live Codex App review run; review record; merge-ready/review gate
- Closing Condition: #863/#864 evidence accepted, PR gates pass, controlled merge completes, main syncs, and issue closeout records proof.
- Current Checkpoint: merge
- Current Stop: Codex App live review returned allow and the WI-863 review record is committed; merge-ready gate consumption is in progress.
- Next Step: Run merge-ready gate on a clean tree, then push/open PR for PR gate and controlled merge.
- Blockers: None
- Latest Validation Summary: py_compile passed for src/generated shared scripts; skills_surface check passed; embedded App JSON probe passed; root shadow-parity and adopt verify passed; version surface check passed; installer version bump check passed; tools/loom_check.py passed with 36 surfaces and loom-check-* temp dirs cleaned; live Codex App review run passed on head b42fd122 via thread 019e4af4-5eb2-7432-bd36-8d8facc33ab1 cwd /Users/mc/dev/Loom-863-codex-app-review-host-proof using App CLI 0.131.0-alpha.9; review record input decision=allow.
- Recovery Boundary: Scope remains #863/#864 review host proof discovery, adapter selection, diagnostic, fixture, live review evidence, review record, and merge-ready/review gate consumption.
- Current Lane: merge-ready-gate

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
