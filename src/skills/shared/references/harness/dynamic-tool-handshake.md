# Dynamic Tool Handshake

Dynamic tool handshake evidence is runtime evidence. It is not authored progress, not a retained host action result, and not a second status truth.

`dynamic_tool_locators` in `.loom/companion/repo-interface.json` remains declaration-time only. Retained host action results stay in `.loom/companion/interop.json`; attempt summaries stay in `execution_attempt`.

Stable statuses:

- `advertised`
- `unavailable`
- `unsupported`
- `failed`

These values are nested under `tool_availability.declared_tools[*].status`; top-level command `result` remains `pass | block | fallback`.

Required tool failure blocks the owning execution surface and uses `fallback_to`. Optional or advisory failure is displayed as advisory evidence and does not block core status.

