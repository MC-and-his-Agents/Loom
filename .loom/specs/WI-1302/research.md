# Research

- Finding: `tools/loom.py suite validate` already emits a formal-suite NA result for a legal suite-level path decision.
- Finding: prior gate consumption treated only `pass` and `advisory` as suite-ready, so docs-only contract PRs were forced toward fake minimal suites.
- Finding: the safe boundary is to skip only formal spec-review applicability while keeping implementation review and all merge evidence required.
- Source: `tools/loom.py suite validate`, `skills/shared/scripts/loom_flow.py`, subagent read-only reviews of #1297, #1298, #1299, and #1300.
