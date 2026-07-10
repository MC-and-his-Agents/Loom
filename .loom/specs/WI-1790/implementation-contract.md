# WI-1790 Implementation Contract

## Ownership

- Owns wrapper runtime resolution for `tools/loom_init.py`, `tools/loom_flow.py`, `tools/loom_check.py`, and `tools/loom_status.py`.
- Owns the minimal bootstrap success JSON shape needed for agent-safe CLI wrapping.
- Owns npm package payload checks and tarball smoke coverage for installed `loom init bootstrap`.
- Owns v0.21.1 root package metadata and Codex plugin payload metadata/hash for this patch release.
- Owns generated runtime parity and demo bootstrap fixture updates caused by this fix.

## Boundaries

- Do not rewrite the Loom initialization model.
- Do not add a new host adapter, plugin surface version, skill contract version, or legacy installer publish path.
- Do not treat v0.21.0 publication or WI-1778 closeout as evidence for this patch release.
- Do not mutate user repositories beyond the explicit bootstrap fixture used for smoke validation.

## Release Metadata Rule

- `VERSION` and root `package.json` must name an unpublished patch version before publish.
- `plugins/loom/.codex-plugin/plugin.json` package and payload metadata must match the root package version before packaging.
- After publish, Codex plugin payload refresh is required because the payload hash changed.
