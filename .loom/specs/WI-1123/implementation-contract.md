# WI-1123 Implementation Contract

## Owned Surface

- `tools/loom.py`
  - `loom suite validate`
  - `payload.spec_plan_mapping`
  - blocking gaps with `failure_kind = missing_spec_plan_mapping`
- `tools/check_cli_contract.py`
  - pass fixture for mapped full path
  - block fixture for missing scenario mapping
  - block fixture for missing acceptance mapping
- Source docs describing the #1123 slice of `suite validate`.

## Explicitly Not Owned

- #1124 final failure taxonomy expansion.
- #1125 `flow spec-review` / `gate spec-review` integration.
- Evidence-map freshness and task carrier validation.
- Generated skill/runtime synchronization.
- Host writes or authored review/merge-ready/closeout writes from CLI validation.

## Compatibility

Existing #1120-#1122 fixtures and read-only CLI envelope must remain stable.
