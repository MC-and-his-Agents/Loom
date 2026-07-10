# WI-1741 Contracts

## Ship Validation Profile Payload

- Schema marker: `loom-ship-validation-profile/v1`
- Required fields: `result`, `requested_profile`, `selected_profile`, `source_surface`, `changed_paths`, `selection_reasons`, `validation_commands`.
- Legal selected profiles: `light`, `standard`, `full`, `release`.
- Legal request profiles: `auto`, `light`, `standard`, `full`, `release`.
- Explicit request profiles override path inference.
- `auto` must default to `standard` when changed paths cannot be read safely.

## Source Surface Mapping

| Profile | Source surface | Boundary |
| --- | --- | --- |
| light | contract-only | docs/package tombstone scope |
| standard | source-self-fixture | mixed or unclassified scope |
| full | daily-execution-cli-full | runtime, harness, tools, workflow, test, plugin, generated fixture scope |
| release | distribution-regression | release/package/version surface |

## Consumer Boundary

Review and merge-ready may consume the payload as a validation recommendation. It is not proof that validation has run, and it does not replace review record, PR checks, or closeout evidence.

## Recheck Condition

Recheck if `loom_check.py` source surfaces change, release/package validation changes, or `loom ship` adds new default delivery steps.
