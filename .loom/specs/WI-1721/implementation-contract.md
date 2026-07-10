# Implementation Contract

## Contract

- `loom host doctor --host codex --scope user --json` exposes `plugin_payload_readback`.
- `plugin_payload_readback.layers` reports `source-payload`, `marketplace-source`, and `runtime-cache`.
- `source-payload` is read from the selected Loom package payload.
- `marketplace-source` is read from the Codex local user marketplace source managed by `loom host install`.
- `runtime-cache` is read from the Codex-owned loaded plugin cache and is never written by doctor.
- Metadata-missing states are distinct from stale hash/version states:
  - `source_metadata_missing`
  - `marketplace_source_metadata_missing`
  - `marketplace_source_stale`
  - `runtime_cache_metadata_missing`
  - `runtime_cache_stale`
- Malformed plugin manifests fail closed as structured readback output with a layer `error`, not as traceback.
- Runtime cache lookup prefers the cache directory matching the current `plugin_surface_version`.

## Non-Goals

- No Codex runtime cache writes.
- No single SKILL install surface.
- No aggregate `loom version` freshness UX.
- No v0.19.0 release behavior.

## Validation Binding

- `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py host doctor --host codex --scope user --json`
