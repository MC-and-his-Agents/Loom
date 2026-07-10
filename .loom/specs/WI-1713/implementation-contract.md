# WI-1713 Implementation Contract

## Ownership

- Owns `plugins/loom/.codex-plugin/plugin.json` release metadata fields.
- Owns `tools/check_npm_package.py` plugin payload hash and metadata validation behavior.
- Owns `tools/version_surface_check.py` release metadata required-field checks.
- Owns `tools/loom.py` version context payload metadata readback.
- Owns `test/plugin_payload_hash_test.py` payload hash regression coverage.
- Owns only WI-1713 Loom carriers.

## Boundaries

- Do not implement Codex source/cache/runtime cache freshness comparison; that belongs to #1721.
- Do not implement stale plugin action guidance; that belongs to #1716.
- Do not retire legacy single-skill installer behavior; that belongs to #1722.
- Do not bump `VERSION` or `package.json`, publish npm, create tags, or create GitHub Releases; that belongs to #1718.
- Do not use `skills/registry.json` `registry_version` as plugin payload freshness authority.

## Release Metadata Rule

- `plugin_surface_version` remains the Codex plugin interface compatibility line.
- `source_package` must be `@mc-and-his-agents/loom`.
- `source_package_version` and `plugin_payload_version` must match root `package.json` version.
- `plugin_payload_hash` must match the deterministic payload digest.
- `source_git_sha` is a non-empty release binding field; exact published release commit readback is finalized by release closeout.

## Hash Rule

- Walk `plugins/loom` files in POSIX relative path order.
- Ignore `.DS_Store`, `__pycache__`, and `*.pyc`.
- For `.codex-plugin/plugin.json`, normalize only the `plugin_payload_hash` value before hashing.
- Hash input for every file remains `relative_path + NUL + bytes + NUL`.
