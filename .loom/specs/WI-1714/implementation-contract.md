# WI-1714 Implementation Contract

## Runtime Contract

- `python3 tools/check_npm_package.py --surface plugin-payload-hash` emits a `loom-npm-package-check/v1` payload with `plugin_payload_hash`, `plugin_payload_hash_algorithm`, `plugin_payload_file_count`, ignored path rules, and evidence locators.
- Aggregate package validation includes the same plugin payload hash and keeps `npm-package-manifest`, `npm-pack-payload`, and `plugin-payload-hash` as package evidence labels.
- The hash algorithm sorts all non-ignored `plugins/loom` file paths by payload-relative POSIX path and updates SHA-256 with `path + NUL + bytes + NUL`.

## Boundary Contract

- `.DS_Store`, any `__pycache__` path part, and `*.pyc` files are ignored.
- Missing payload root, missing plugin manifest, empty payload, or mismatched declared `x-loom.plugin_payload_hash` fail closed.
- Missing manifest metadata remains `missing_pending_metadata` in #1714 so #1713 can write release-bound metadata.

## Non-Goals

- #1714 does not write plugin release metadata.
- #1714 does not inspect Codex source/cache freshness.
- #1714 does not change `loom version`, `loom host`, legacy installer behavior, version numbers, npm publish, or release closeout.
