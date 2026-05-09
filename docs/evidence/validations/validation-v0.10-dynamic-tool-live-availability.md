# Validation: v0.10 Dynamic Tool Live Availability

This validation records the v0.10.0 `#605` line for optional dynamic tool live/profile-local evidence.

It verifies:

- `python3 tools/loom_flow.py live-smoke dynamic-tool-availability --target <repo>` emits `loom-dynamic-tool-live-availability/v1`
- required dynamic tool failures can block the live profile without polluting `orchestration-core`
- optional/advisory failures remain profile-local `warn`
- the command does not execute tools or define a tool-specific protocol

## Commands

```bash
python3 tools/loom_flow.py live-smoke dynamic-tool-availability --target examples/new-project
python3 tools/loom_flow.py live-smoke dynamic-tool-availability --target /tmp/loom-missing-live-target
python3 tools/skills_surface.py check
python3 tools/loom_check.py
```

## Expected Results

- `examples/new-project` without a repo companion interface returns explicit unavailable evidence and `result: warn`
- a present repo companion interface with no declared dynamic tools returns `result: pass`
- required `unsupported`, `failed`, `unavailable`, or invalid handshake declarations can return `result: block`
- optional/advisory failures stay profile-local `warn`
- `tool_availability` keeps schema `loom-dynamic-tool-handshake/v1` inside the live wrapper

## Notes

- `fallback_to: live-smoke-retry-or-record-unavailable` remains the explicit unavailable path when the adopted-repo target or repo interface is absent
- `fallback_to: live-smoke-config-repair` remains the blocking repair path for invalid declarations or required failures
- This command reuses repo companion `dynamic_tool_locators` as declaration-time locator truth; it does not execute the tool or write host state
