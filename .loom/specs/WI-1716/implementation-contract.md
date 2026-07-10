# Implementation Contract

- `version_freshness.plugin_payload.refresh_guidance` exposes schema `loom-plugin-payload-refresh-guidance/v1`.
- `refresh_guidance.apply_commands` lists only explicit user-level host commands that Loom can run with `--apply`.
- Stale or missing marketplace source guidance uses:
  - `loom host install --host codex --scope user --apply --json`
  - `loom host register --host codex --scope user --apply --json`
  - `loom host doctor --host codex --scope user --json`
- Stale or missing runtime cache guidance sets `reload_required=true`, leaves `apply_commands=[]`, and uses host doctor as the readback command.
- `version_freshness_action()` mirrors the refresh guidance into the `cli-plugin-freshness` upgrade-plan action.
- Target repository `loom install` and `loom upgrade` remain repository installed-state commands and do not refresh the Codex workstation plugin payload.
