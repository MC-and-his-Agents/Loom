# WI-1510 Implementation Contract

- Suite path: minimal

## Contract Surface

- `gate_freeze_payload` includes `input_bindings.carrier_refresh`.
- `carrier_refresh` uses schema `loom-gate-freeze-carrier-refresh/v1`.
- `carrier_refresh` consumes dry-run carrier refresh output and reports pending refresh actions as `carrier_refresh_stale`.
- `gate_freeze_payload` includes `input_bindings.shadow_freshness`.
- `shadow_freshness` uses schema `loom-gate-freeze-shadow-freshness/v1`.
- `shadow_freshness.records[]` includes path, surface, side, freshness, drift kind, refreshable, next action, current source hashes, expected source hashes, and missing inputs.
- `readiness.refresh_suggestions` are derived from refreshable bindings and do not reference unsupported command names.

## Consumer Boundary

- #1512 may consume `carrier_refresh` and `shadow_freshness` as generic gate freeze input fields.
- #1532/#1533/#1534 may consume these field names later but must not treat this PR as implementing closeout terminal profile behavior.

## Non-Goals

- Do not implement hosted admission, closeout-specific gate, closeout terminal profile behavior, PR metadata rendering, closeout item binding, one-shot closeout run, or final release/no-release closeout.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `git diff --check`
