# WI-1717 Implementation Contract

## Ownership

- Owns `tools/check_cli_contract.py` freshness regression assertions inside the existing `adoption-host-metadata` surface.
- Owns WI-1717 Loom carriers, including build evidence, suite evidence map, task carrier, review records, status, and bootstrap pointers.
- Reuses `test/plugin_payload_hash_test.py` as existing hash regression evidence without changing the hash implementation.

## Boundaries

- Do not change `tools/loom.py` freshness behavior in this Work Item.
- Do not change plugin payload hash algorithm semantics.
- Do not implement v0.19.0 release closeout, version bumps, npm publish, GitHub release, or tag creation.
- Do not change `packages/loom-installer` tombstone behavior or legacy installer semantics.
- Do not add a new broad fixture framework.

## Regression Contract

- `loom version --json` must report `surface_compatibility.status=compatible` for current CLI and plugin payload metadata.
- Short `loom version` output must include `action already_current` when CLI and plugin payload are current.
- Runtime cache plugin surface divergence must produce `surface_compatibility.status=incompatible` and include `runtime-cache` in `incompatible_layers`.
- Existing payload hash tests remain the authority for deterministic hash stability, file ordering, ignored files, and self-reference handling.
