# WI-871 Plan

## Steps

1. Extend `controlled-merge` CLI with explicit retained result locator inputs.
2. Validate retained `pr-gate` freshness against current PR readback.
3. Validate retained `merge-gate` freshness against retained `pr-gate` review / validation bindings.
4. Emit `retained_results` and drift-only readback without weakening host enforcement readback.
5. Add source self-check coverage for fresh retained pass and stale retained head block.
6. Update canonical harness / interop contracts, source skill references, generated skills surface, and installer version metadata.

## Validation

- `make py-compile`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
