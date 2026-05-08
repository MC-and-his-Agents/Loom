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
- Current Checkpoint: merge checkpoint
- Current Stop: WI-566 dynamic tool handshake implementation, reviews, generated carriers, shadow evidence, and full verification are aligned on the batch branch.
- Next Step: Open the #566 batch PR, bind it to #567-#570, wait for host checks, merge to main, then run closeout for the child Work Items.
- Blockers: None recorded.
- Latest Validation Summary: make check passed on work/566-dynamic-tool-handshake-semantics with 26 loom_check surfaces; demo-bootstrap reported write.touched empty after generated runtime refresh; py_compile, skills_surface check, host_adapter_check, version_surface_check, repo companion dynamic tool fixtures, root adopt verify, and shadow parity all passed; flow merge-ready passed for WI-566 with tool_availability result pass.
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
