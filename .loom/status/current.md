# Current Status

## Derived Fact Chain View

- Item ID: WI-566
- Goal: Deliver #566 dynamic tool handshake semantics for v0.8.0 / #531.
- Scope: Define the dynamic tool handshake vocabulary, preserve the companion / interop declaration boundary, expose tool availability and failure summary in flow/status output, and validate unsupported, unavailable, and failed tool fixtures.
- Execution Path: phase/v0.8.0/fr/566
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-566.md
- Review Entry: .loom/reviews/WI-566.json
- Validation Entry: make check
- Closing Condition: `tool_availability` exposes `advertised | unavailable | unsupported | failed`, required tool failure blocks the owning execution surface, optional/advisory failures remain advisory, status reads the latest derived summary, fixtures cover unsupported/unavailable/failed tools, `make check` passes cleanly, and the #566 batch PR absorbs #567-#570.
- Current Checkpoint: review checkpoint
- Current Stop: WI-566 dynamic tool handshake docs, implementation, generated skill surfaces, and fixtures are implemented; implementation review is next.
- Next Step: Record implementation review, run full make check on a clean tree, then produce merge-ready and PR evidence for #566.
- Blockers: None recorded.
- Latest Validation Summary: py_compile passed for shared runtime scripts; skills_surface check passed; repo companion dynamic tool fixture check passed with unsupported/unavailable/failed coverage; loom_status exposes tool_availability for WI-566 and is only blocked by missing implementation review; flow merge-ready exposes repo_specific_requirements.tool_availability and is only blocked by missing implementation review.
- Recovery Boundary: Branch work/566-dynamic-tool-handshake-semantics; active item WI-566; dynamic tool handshake evidence is derived from companion locators and must not replace recovery truth, execution_attempt evidence, or retained host action results.
- Current Lane: v0.8.0 / #531 / #566 dynamic tool handshake semantics

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-566.md
- Dynamic Truth: .loom/progress/WI-566.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
