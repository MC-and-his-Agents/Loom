# WI-1510 Plan

## Implementation Steps

1. Add a gate freeze carrier refresh binding that consumes `carrier_refresh_payload(..., dry_run=True)` and reports stale carrier refresh as `carrier_refresh_stale`.
2. Add a shadow freshness binding that reads declared shadow evidence source hashes, reports per-shadow freshness records, and distinguishes refreshable `shadow_source_hash_drift` from unreadable/conflicting shadow inputs.
3. Include the new bindings under `input_bindings.carrier_refresh` and `input_bindings.shadow_freshness` in `gate_freeze_payload`.
4. Generate refresh suggestions from refreshable bindings only, avoiding unsupported command names.
5. Extend focused CLI contract coverage and sync generated/runtime copies.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --json`
- `git diff --check`

## Dependencies

- Consumes #1507 and #1508 as the gate freeze contract and command entrypoint.
- Provides stable `carrier_refresh` and `shadow_freshness` fields for #1512.
- Does not block #1513/#1541/#1554 implementation lanes, but #1514/#1534/#1515 must consume the final merged #1510 field shape.

## Scope Guard

- Do not edit PR body, issue body, or host state from subagents.
- Do not change #1531-#1534 closeout profile semantics.
- Do not add a new `loom shadow-parity` wrapper surface in this PR.
