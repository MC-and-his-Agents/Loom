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
- Current Stop: Fixed review prompt guidance so stale prior review records are treated as historical input during replacement review runs; local focused checks and full loom_check have passed.
- Next Step: Commit and push the prompt/fixture/doc repair, rerun final self-check on the committed head, then run a renewed Codex App host review with default app adapter proof and record/gate consumption.
- Blockers: None
- Latest Validation Summary: Prompt guidance now tells formal reviewers not to block solely on a stale prior review record while review run is generating replacement evidence. Verified with PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile for shared loom_flow/loom_check scripts, python3 tools/skills_surface.py check, git diff --check, and PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py -> OK, checked 36 surfaces. Post-commit focused self-check passed py_compile, skills_surface check after pycache cleanup, version surface check, and fact-chain; a post-commit full loom_check rerun was discarded because pre-existing concurrent loom_check processes polluted the run, then all loom-check-* temp dirs were cleaned.
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
