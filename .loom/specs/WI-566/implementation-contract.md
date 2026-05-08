# WI-566 Implementation Contract

## Boundaries

- `repo-interface.json` owns dynamic tool declaration locators only.
- `interop.json` owns retained host action result locators.
- `execution_attempt` owns per-command attempt evidence.
- `tool_availability` is a derived runtime evidence read surface.

## Stable Fields

- `schema_version: loom-dynamic-tool-handshake/v1`
- `declared_tools[*].status: advertised | unavailable | unsupported | failed`
- `declared_tools[*].result: pass | block`
- `failure_summary.required_blocking`
- `failure_summary.optional_advisory`
- `failure_summary.by_status`

## Blocking Rules

- Required declaration locator missing, unsafe, unreadable, or failed blocks.
- Required tool `unavailable`, `unsupported`, or `failed` blocks the applicable execution surface.
- Optional/advisory tool failure is advisory evidence only.
- Top-level command results remain `pass | block | fallback`.
