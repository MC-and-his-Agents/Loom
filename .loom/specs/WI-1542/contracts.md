# Contracts

- `loom workspace audit` is a read-only wrapper entry for the repo-local startup audit.
- The wrapper delegates to runtime `work-item-audit` without mutating repo carriers, PR bodies, or host state.
- The runtime payload schema is `loom-active-carrier-audit/v1`.
- `carrier_closeout_required` diagnostics map to the stable classifier `carrier_refresh_needed` and remain startup-blocking.
- `stale_carrier` diagnostics are retained as compact nonblocking samples unless they describe the current active Work Item.
- Shadow source hash drift maps to the stable classifier `shadow_stale` and blocks until carrier/shadow evidence is refreshed.
- Generated skills runtime copies and demo bootstrap runtime fixtures must match `src/skills/shared/scripts/loom_flow.py`.
