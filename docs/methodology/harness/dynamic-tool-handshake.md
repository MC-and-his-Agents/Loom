# Dynamic Tool Handshake

This contract defines the stable read surface for dynamic tool availability during Loom execution.

Dynamic tool handshake evidence is runtime evidence. It is not authored progress, not a retained host action result, and not a second status truth.

## Boundary

`dynamic_tool_locators` in `.loom/companion/repo-interface.json` remains declaration-time only. It declares:

- `id`
- `summary`
- `locator`
- `owner`
- `requirement`
- `surface`
- `fallback_to`

The locator may point at a readable handshake declaration. Loom reads that declaration but does not call the tool, probe the host, or write host results.

`python3 tools/loom_flow.py live-smoke dynamic-tool-availability --target <repo> [--surface <surface>]` is the live/profile-local evidence wrapper for this contract. It reads the same declarations and emits release-confidence evidence without executing the tool protocol itself.

Retained host action results remain in `.loom/companion/interop.json`. Attempt summaries remain in `execution_attempt`.

## Vocabulary

`tool_availability.declared_tools[*].status` uses exactly:

- `advertised`: the tool declaration is readable and no failed handshake is reported.
- `unavailable`: the tool or availability declaration is missing for this runtime/profile.
- `unsupported`: the host adapter reports that the requested tool call is not supported.
- `failed`: the tool handshake ran or was declared and failed.

These values are never top-level command results. Top-level `result` remains `pass | warn | block`.

## Severity

- Required declaration locator missing, unreadable, or unsafe: block the declaration surface.
- Optional or advisory declaration locator missing: report advisory `unavailable`; do not block status.
- Required tool `unavailable`, `unsupported`, or `failed` on an execution surface: block that surface and use `fallback_to`.
- Optional or advisory tool `unavailable`, `unsupported`, or `failed`: expose failure evidence without blocking core status.
- `merge_ready` blocks only for required capability failure or an explicitly blocking profile.

## Output

`tool_availability` uses schema `loom-dynamic-tool-handshake/v1` and includes:

- `result`
- `summary`
- `declared_tools`
- `failure_summary.required_blocking`
- `failure_summary.optional_advisory`
- `failure_summary.by_status`
- `missing_inputs`
- `fallback_to`

`loom_status` exposes the latest derived `tool_availability` from `governance_surface.repo_interface`.
`flow review` and `flow merge-ready` expose the applicable tool availability under `repo_specific_requirements.tool_availability`.

`live-smoke dynamic-tool-availability` embeds that same `tool_availability` payload inside `loom-dynamic-tool-live-availability/v1`, keeps optional/advisory failures profile-local, and does not call the tool or define a tool-specific protocol.
