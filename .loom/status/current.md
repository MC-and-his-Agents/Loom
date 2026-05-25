# Current Status

## Derived Fact Chain View

- Item ID: WI-1010
- Goal: Execute `loom-installer` npm deprecation when authorized, or record npm permission-block evidence and owner action.
- Scope: #1010: npm deprecation status for `@mc-and-his-agents/loom-installer`, legacy baseline evidence, no installer publish, and closeout evidence for #1003.
- Execution Path: issue-scoped branch work/1010-installer-npm-deprecate in /Users/mc/dev/Loom-1010-installer-npm-deprecate
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1010.md
- Review Entry: .loom/reviews/WI-1010.json
- Validation Entry: npm view @mc-and-his-agents/loom-installer version deprecated --json
- Closing Condition: npm deprecation is applied, or npm permission failure is recorded with owner action while installer latest/tag/release remain at the legacy baseline.
- Current Checkpoint: validated
- Current Stop: npm deprecate permission-block evidence is committed at 86f77087ca8b3b5b2b31d8955502cc5898041184; installer latest remains 0.1.119.
- Next Step: Open PR, consume checks, then merge and close #1010 as permission-blocked with owner action.
- Blockers: npm registry write/deprecate permission is unavailable in this environment (`npm whoami` -> E401 Unauthorized).
- Latest Validation Summary: Passed: npm view @mc-and-his-agents/loom-installer version deprecated --json returned 0.1.119 with no deprecation metadata; npm whoami returned E401 Unauthorized; GitHub release list still shows latest installer release loom-installer-v0.1.119; max installer tag remains loom-installer-v0.1.119; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; npm --prefix packages/loom-installer run check:release; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1010; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1010; make check.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1010-installer-npm-deprecate on branch work/1010-installer-npm-deprecate; keep scope limited to npm deprecation/permission evidence and no-installer-publish closeout.
- Current Lane: installer-npm-deprecate

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: npm view @mc-and-his-agents/loom-installer version deprecated --json; npm whoami; python3 tools/check_release_surface.py
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1010.md
- Dynamic Truth: .loom/progress/WI-1010.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
