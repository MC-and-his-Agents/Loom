# WI-1739 Contracts

## Runtime Contract

- `loom ship --apply` may mutate safe metadata and versioned carriers before merge gates.
- `loom ship` without `--apply` remains read-only.
- Carrier refresh must run before PR metadata preflight in apply mode.
- Shadow parity must run after carrier refresh and before PR metadata preflight in apply mode.
- Any failed repair-chain step blocks before controlled merge.

## Output Contract

- Blocking repair-chain steps preserve `missing_inputs` in short diagnostics.
- `next_action` points to the single relevant repair/readback command.
- Full JSON remains available through `--json` or `--full-output`.
