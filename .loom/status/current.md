# Current Status

## Derived Fact Chain View

- Item ID: WI-778
- Goal: Define scaffold profiles for adoption intents
- Scope: Add a stable profile mapping for adoption intents and make dry-run, write, verify, initial artifacts, deferred capabilities, and upgrade triggers consume the same profile boundary
- Execution Path: adoption/bootstrap
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-778.md
- Review Entry: .loom/reviews/WI-778.json
- Validation Entry: make skills-check; python3 tools/loom_check.py .
- Closing Condition: #778 is implemented, validated, reviewed, merged, and issue state reflects the PR
- Current Checkpoint: merge checkpoint
- Current Stop: #778 implementation, installer version bump, WI-775 terminal carrier repair, local validation, and refreshed implementation review are ready for PR gate consumption.
- Next Step: Push PR #787, wait for required checks, merge, close issue #778, then continue with #784.
- Blockers: None recorded.
- Latest Validation Summary: py_compile -> OK; skills surface check -> OK; make skills-check -> OK; adopt verify root -> OK; installer version bump check -> OK; host-binding validate main -> OK; make loom-check -> OK; carrier refresh root -> OK.
- Recovery Boundary: Work item scaffolded at `.loom/work-items/WI-778.md`.
- Current Lane: PR #787

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-778.md
- Dynamic Truth: .loom/progress/WI-778.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
