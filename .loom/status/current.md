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
- Current Stop: CI portability repair is being committed and pushed so PR #879 can rerun root governance and loom_check on a checkout-local workspace entry.
- Next Step: Push the portable workspace binding repair, wait for PR #879 CI, then run renewed self-check and Codex App review/PR gate sequence if the head changes require it.
- Blockers: None
- Latest Validation Summary: Rebound WI-863 workspace entry from the local absolute worktree path to portable `./`, preserving host worktree proof through the execution path and host binding diagnostics while allowing CI checkout-root consumption. Focused checks passed: fact-chain, shadow-parity, adopt verify, py_compile, skills_surface check, version surface check, and full `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py` with 36 surfaces. `loom-check-*` temp dirs and pycache residue were cleaned after the run. No renewed Codex App review was started this round.
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
