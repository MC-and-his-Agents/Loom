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
- Current Checkpoint: build checkpoint
- Current Stop: Batch #566 implementation is in progress on branch `work/566-dynamic-tool-handshake-semantics`.
- Next Step: Finish dynamic tool handshake docs, implementation, fixtures, generated skill surfaces, validation, formal review, PR, and closeout for #567-#570.
- Blockers: None recorded.
- Latest Validation Summary: Pending for WI-566.
- Recovery Boundary: Branch work/566-dynamic-tool-handshake-semantics; active item WI-566; dynamic tool handshake evidence is derived runtime evidence and must not replace recovery truth or retained host action truth.
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
