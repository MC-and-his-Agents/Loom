# Validation: v0.10 Live Validation-Only Guardrail

This validation records the v0.10.0 `#609` line for the default validation-only boundary after live smoke foundation, host adapter live drift, and dynamic tool live availability were merged.

It verifies:

- validation-only live mismatch does not block ordinary orchestration-core consumption
- explicit blocking opt-in remains evidence, not an automatic upgrade judgment
- missing blocking prerequisites stay as configuration or contract gaps rather than silently upgrading a live result into final authority
- a single adopted repo live smoke run is not sufficient shadow parity blocking upgrade evidence

## Commands

```bash
python3 tools/loom_flow.py live-smoke run --target /tmp/loom-missing-live-target --item INIT-0001
python3 tools/loom_flow.py live-smoke run --target examples/new-project --dry-run --include-blocking-shadow
python3 tools/loom_flow.py shadow-parity --target <fixture>
python3 tools/loom_flow.py shadow-parity --target <fixture> --blocking
python3 tools/loom_check.py
```

## Expected Results

- missing adopted-repo target returns explicit unavailable evidence and top-level `warn`
- validation-only shadow parity mismatch returns `warn`
- blocking shadow parity returns `block` only when blocking mode is explicitly requested
- `--include-blocking-shadow` only records explicit blocking opt-in command presence; it does not by itself establish owner, fallback, override path, authority-of-truth, or sufficient live evidence for a blocking upgrade
- `interop.json` and `repo-interface.json` remain read surfaces and do not become the place where blocking ownership or final winner semantics are declared

## Notes

- this batch does not add a new checker entrypoint; it relies on the existing `shadow-parity`, `live-smoke`, release-readiness, and `loom_check` surfaces
- the guardrail is complete only when both advisory/default behavior and explicit blocking behavior are covered by regression evidence
