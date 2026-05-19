# Current Status

## Derived Fact Chain View

- Item ID: WI-779
- Goal: Align lightweight-retrofit docs, dry-run output, write behavior, and verify logic
- Scope: Make small-existing light-governance avoid Loom-owned work item/progress/status/spec carriers while preserving execution-control full carriers in `src/skills/shared/scripts/loom_init.py`, `src/skills/shared/scripts/loom_check.py`, `src/skills/loom-init/`, `src/skills/shared/references/adoption/`, `docs/adoption/`, `skills/`, `examples/new-project/`, `.loom/work-items/WI-779.md`, `.loom/progress/WI-779.md`, `.loom/progress/WI-784.md`, `.loom/reviews/WI-779.json`, `.loom/reviews/WI-779.spec.json`, `.loom/specs/WI-779/`, `.loom/status/current.md`, and `.loom/bootstrap/init-result.json`.
- Execution Path: adoption/bootstrap
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-779.md
- Review Entry: .loom/reviews/WI-779.json
- Validation Entry: python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py; targeted #779 adoption fixture; python3 tools/skills_surface.py check; make skills-check; make loom-check
- Closing Condition: #779 is implemented, validated, reviewed, merged, and issue state reflects the PR
- Current Checkpoint: merge checkpoint
- Current Stop: #779 implementation, validation, spec review, and general review are recorded; preparing PR push and merge gate.
- Next Step: Push branch, create PR for #779, run PR gate, wait for required checks, merge, and close #779.
- Blockers: None recorded.
- Latest Validation Summary: py_compile -> OK; targeted #779 adoption fixture -> OK; python3 tools/skills_surface.py check -> OK; make skills-check -> OK; make loom-check -> OK; installer version bump check -> OK (no bump required); spec review -> allow; general review -> allow.
- Recovery Boundary: .loom/work-items/WI-779.md is the active static work item carrier.
- Current Lane: work/779-lightweight-retrofit-alignment

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-779.md
- Dynamic Truth: .loom/progress/WI-779.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
