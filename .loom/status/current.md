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
- Current Stop: Live Codex App review on 1af91b6 passed with selected_adapter=loom/codex-app-review, selection_source=codex-app-host-default, thread_cwd_matches_target_root=true, fallback_reason=null, and authority_boundary=normalized review_record_input only. The formal review record was refreshed from normalized review_record_input; adopt verify and shadow-parity passed. A flow review rerun before commit fell back only on expected dirty review-record purity.
- Next Step: Commit review record and progress, then rerun clean flow review, loom_check, merge-ready, checkpoint merge, and PR gate consumption for PR #879.
- Blockers: None
- Latest Validation Summary: Self-check before live review passed: git diff --check, tools/py_compile_clean.py for shared loom_flow/loom_check scripts, skills_surface check, version_surface_check, .loom/bin/loom_init.py verify, fact-chain, flow review, and PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py . -> OK, checked 37 surfaces. Live Codex App review on 1af91b6 passed using stdio://, new-thread, formal worktree cwd, timeout_seconds=900, and normalized turn-start output; .loom/reviews/WI-863.json now consumes the App evidence locators and normalized findings.
- Recovery Boundary: Scope remains #863/#864 review host proof discovery, adapter selection, diagnostic, fixture, live review evidence, review record, and merge-ready/review gate consumption.
- Current Lane: record-gate-consumption

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
