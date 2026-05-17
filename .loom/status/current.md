# Current Status

## Derived Fact Chain View

- Item ID: WI-750
- Goal: Switch Codex App host review runs to the Codex App review adapter by default when verified host proof is complete.
- Scope: Update review adapter selection, Codex App live runner behavior, review metadata, fallback/fail-closed semantics, generated skill surfaces, and review execution documentation for #750 phase 3.
- Execution Path: phase/codex-app-review-default/750
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-750.md
- Review Entry: .loom/reviews/WI-750.json
- Validation Entry: python3 -m py_compile tools/loom_flow.py tools/loom_check.py skills/shared/scripts/*.py src/skills/shared/scripts/*.py && python3 tools/loom_check.py && make check
- Closing Condition: PR #770 contains the #750 phase 3 implementation and docs; generated surfaces are synchronized; installer version behavior truth is bumped; py_compile, loom_check, make check, and PR gates pass; the branch is pushed with fresh authored spec and implementation review records.
- Current Checkpoint: merge checkpoint
- Current Stop: Implementation, documentation, generated surfaces, installer version bump, and local validation are complete on branch work/750-codex-app-default-review-adapter; fresh review records are being recorded for PR #770.
- Next Step: Commit the WI-750 fact chain, record spec and implementation review records against the reviewed heads, update PR #770 body with the Loom Work Item binding, push, and confirm PR gates.
- Blockers: None recorded.
- Latest Validation Summary: pending final validation refresh for WI-750 after fact-chain and installer version updates.
- Recovery Boundary: Branch work/750-codex-app-default-review-adapter; issue #750 phase 3; PR #770; raw Codex App review evidence remains runtime evidence only and never approval truth.
- Current Lane: #750 phase 3 / Codex App default review adapter

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-750.md
- Dynamic Truth: .loom/progress/WI-750.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
