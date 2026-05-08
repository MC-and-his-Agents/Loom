# Current Status

## Derived Fact Chain View

- Item ID: WI-675
- Goal: Deliver #675 deterministic review engine execution for v0.8.0 / #531.
- Scope: Define the review engine profile contract, resolve explicit Codex model and reasoning profile in review run, and require auditable profile evidence in review fixtures.
- Execution Path: phase/v0.8.0/fr/675
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-675.md
- Review Entry: .loom/reviews/WI-675.json
- Validation Entry: make check
- Closing Condition: Review execution has a stable profile contract; review run passes explicit model and reasoning parameters instead of inheriting host defaults; engine metadata and review_record_input expose the resolved profile, selection reason, and override reason; override without reason fails closed; review fixtures require profile evidence; generated skill surfaces are synchronized; make check passes cleanly; and the #675 batch PR absorbs #676-#678.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-675 implementation, fixtures, generated surfaces, installer version, and review evidence are aligned on the batch branch.
- Next Step: Run installer/version checks, refresh review evidence, run merge-ready, open #675 batch PR, merge to main, then close #676-#678.
- Blockers: None recorded.
- Latest Validation Summary: python3 -m py_compile passed for changed loom_flow and loom_check scripts; python3 tools/skills_surface.py check passed; python3 tools/loom_check.py passed with 27 surfaces; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main passed; npm run check:payload --prefix packages/loom-installer passed.
- Recovery Boundary: Branch work/675-deterministic-review-engine-execution; active item WI-675; review engine profile evidence is execution evidence and must not replace authored review, Work Item, recovery, merge-ready, closeout, issue, or PR truth.
- Current Lane: v0.8.0 / #531 / #675 deterministic review engine execution

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-675.md
- Dynamic Truth: .loom/progress/WI-675.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
