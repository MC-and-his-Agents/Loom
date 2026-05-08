# Current Status

## Derived Fact Chain View

- Item ID: WI-561
- Goal: Deliver #561 execution attempt envelope as the first v0.8.0 / #531 batch
- Scope: Repair Loom self-governance baseline for #531, bind the first active batch to #561, and remove demo bootstrap path/branch drift before FR review or merge-ready.
- Execution Path: phase/v0.8.0/fr/561
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-561.md
- Review Entry: .loom/reviews/WI-561.json
- Validation Entry: make check
- Closing Condition: Root self-status reads WI-561, demo bootstrap is portable and idempotent, and #531/#561 branch/PR truth can be established without INIT-0001 as the active item.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-561 baseline repair is locally merge-ready after full verification and installer gate repair.
- Next Step: Push the updated branch, wait for host checks, then merge the #531/#561 baseline PR when green.
- Blockers: None recorded.
- Latest Validation Summary: make check passed on work/531-v080-baseline-repair; WI-561 status, merge-ready, and adopt verify passed; demo bootstrap rerun wrote no tracked changes; installer version bump check and npm test passed for 0.1.72.
- Recovery Boundary: Branch work/531-v080-baseline-repair at commit 129edaa; active item WI-561; retired bootstrap item INIT-0001.
- Current Lane: v0.8.0 / #531 baseline repair

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-561.md
- Dynamic Truth: .loom/progress/WI-561.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
