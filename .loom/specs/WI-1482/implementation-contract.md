# WI-1482 Implementation Contract

## Scope

- Implement configurable agent-safe stdout budget protection in `tools/loom.py`.
- Keep the change at the reusable helper layer; command-by-command integration remains in dependent issues.

## Contract

- Default agent-safe stdout budget is 16 KiB.
- Default summary target is 4 KiB.
- `LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES` and `LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES` may override defaults when set to positive integers.
- Invalid override values fall back to safe defaults.
- `full_output=True` is the explicit full output mode for debugging and returns the original payload.
- Over-budget default output writes the full payload to an artifact and returns a bounded envelope with locator metadata.

## Non-Goals

- Do not wire every high-noise command in this Work Item.
- Do not change pass/fail or gate semantics.
- Do not make artifact output a truth carrier.
- Do not restore repo-local runtime/plugin/skills installation paths.

## Validation

- `test_default_budget_keeps_large_payload_out_of_stdout`
- `test_budget_can_be_configured_with_env`
- `test_explicit_full_output_mode_returns_payload`
