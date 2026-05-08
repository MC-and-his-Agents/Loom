# WI-566 Spec

## Goal

Standardize dynamic tool handshake semantics so Loom can report tool availability and failure evidence without executing tools or creating parallel truth.

## Acceptance Criteria

- `dynamic_tool_locators` remains declaration-time and locator-only in the repo companion contract.
- The stable handshake vocabulary is `advertised`, `unavailable`, `unsupported`, and `failed`.
- `tool_availability` appears in status/governance output and includes declared tools plus failure summary.
- `flow review` and `flow merge-ready` expose applicable tool availability under repo-specific requirements.
- Required tool failure blocks the owning execution surface and uses `fallback_to`.
- Optional or advisory tool failure remains advisory and does not block core status.
- Fixtures cover unsupported, unavailable, and failed tools.
- `make check` passes with no tracked verification drift.

## Non-Goals

- Do not execute dynamic tools.
- Do not move retained host action results from interop into repo companion.
- Do not add approval/sandbox policy semantics; that belongs to #571.
