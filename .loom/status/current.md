# Current Status

## Derived Fact Chain View

- Item ID: WI-781
- Goal: Prevent adoption from silently hiding stable Loom carriers behind blanket `.loom` gitignore rules
- Scope: Detect blanket `.loom` ignore patterns, fail closed by default, support explicit repair to runtime-only ignores, document the version-control policy, refresh generated skills and examples, and validate stable carrier Git visibility
- Execution Path: adoption/bootstrap
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-781.md
- Review Entry: .loom/reviews/WI-781.json
- Validation Entry: python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py; targeted gitignore fixture; python3 tools/skills_surface.py check; python3 tools/loom_check.py .; make skills-check; make loom-check
- Closing Condition: #781 is implemented, validated, reviewed, merged, and issue state reflects the PR
- Current Checkpoint: merge
- Current Stop: #781 implementation, review records, targeted fixtures, generated surface refresh, carrier refresh, and full local validation are complete.
- Next Step: Commit, push, open PR, merge, and confirm issue #781 closes.
- Blockers: None recorded.
- Latest Validation Summary: py_compile -> OK; targeted `.loom/*` block, `/.loom/*` repair, stable Git-visible, runtime ignored, and verify drift fixture -> OK; python3 tools/skills_surface.py check -> OK; python3 tools/loom_check.py . -> OK (36 surfaces); make skills-check -> OK; make loom-check -> OK (36 surfaces); root shadow-parity -> pass; root adopt verify WI-781 -> pass; make check -> OK.
- Recovery Boundary: .loom/work-items/WI-781.md is the active static work item carrier.
- Current Lane: work/781-gitignore-loom-carrier-visibility

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-781.md
- Dynamic Truth: .loom/progress/WI-781.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
