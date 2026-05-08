# Current Status

## Derived Fact Chain View

- Item ID: WI-689
- Goal: Deliver #689 installed Loom upgrade rehearsal and status for v0.8.0 / #531.
- Scope: Define installed Loom status, add installer upgrade-plan and verify-upgrade read surfaces, expose drift and rollback evidence, and cover rehearsal failure states with installer tests.
- Execution Path: phase/v0.8.0/fr/689
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-689.md
- Review Entry: .loom/reviews/WI-689.json
- Validation Entry: make check
- Closing Condition: Adoption docs define installed Loom surface status; installer emits read-only upgrade-plan and verify-upgrade evidence including changed paths, drift, rollback path, failed layer, and fail-closed reason; fixtures cover current, upgrade-available, drift, and incompatible metadata states; make check passes cleanly; and the #689 batch PR absorbs #690-#692.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-689 implementation, validation, spec review, and code review evidence are aligned on the batch branch.
- Next Step: Run merge-ready checks, open the #689 batch PR, merge to main, then close #690-#692.
- Blockers: None recorded.
- Latest Validation Summary: npm test passed for packages/loom-installer; npm run check:release passed for packages/loom-installer; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main passed; CLI smoke for upgrade-plan returned planned/current/mutates_target=false; make check passed with 27 surfaces and no tracked drift beyond this batch.
- Recovery Boundary: Branch work/689-installed-upgrade-rehearsal-status; active item WI-689; installed Loom status and upgrade rehearsal evidence are read surfaces only and must not replace repo companion, Work Item, review, merge-ready, closeout, issue, or PR truth.
- Current Lane: v0.8.0 / #531 / #689 installed Loom upgrade rehearsal and status

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-689.md
- Dynamic Truth: .loom/progress/WI-689.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
