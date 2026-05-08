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
- Current Checkpoint: build checkpoint
- Current Stop: Baseline repair has activated WI-561 and portable demo bootstrap is implemented.
- Next Step: Run full validation, record review evidence, and open the #531/#561 baseline PR.
- Blockers: Formal review and merge-ready are still pending for this baseline branch.
- Latest Validation Summary: Portable demo bootstrap mode has been implemented and WI-561 root self-governance carriers have been authored; full make check still pending.
- Recovery Boundary: Branch work/531-v080-baseline-repair; active item WI-561; retired bootstrap item INIT-0001.
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
