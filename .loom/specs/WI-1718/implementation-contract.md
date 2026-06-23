# WI-1718 Implementation Contract

## Ownership

- Owns root release authority: `VERSION` and root `package.json`.
- Owns v0.19.0 plugin payload release metadata in `plugins/loom/.codex-plugin/plugin.json`.
- Owns publish-time plugin metadata stamping in `tools/stamp_plugin_payload_metadata.py` and `.github/workflows/loom-cli-release.yml`.
- Owns release workflow contract guard updates in `tools/check_release_surface.py`.
- Owns v0.19.0 release readiness evidence and WI-1718 carriers.

## Boundaries

- Do not change plugin surface version `0.4.0` unless host-facing plugin interface changes.
- Do not change host adapter version, skills registry version, skill contract versions, or schema versions.
- Do not restore single-skill install or legacy plugin install behavior.
- Do not bump or publish `@mc-and-his-agents/loom-installer`.
- Do not execute `npm deprecate` without a separate explicit user confirmation.
- Do not close #1711 until #1718 release readback proves v0.19.0 publication and no stale child issue remains.

## Release Metadata Rule

- Candidate source manifest may use `source_git_sha=unreleased` and `source_git_sha_status=pending_release_commit` before merge.
- Publish workflow must stamp `source_git_sha=${{ github.sha }}` and set `source_git_sha_status=release_commit` before npm publish.
- Stamping must recompute `plugin_payload_hash` over the installable `plugins/loom` payload with only the self-referential hash field normalized.
- `source_package_version` and `plugin_payload_version` must match root `package.json` version.

## Rollback

- If v0.19.0 is not published, revert the release PR before merge or bump to a new unoccupied version before retrying.
- If release artifacts are partially published, do not overwrite tag/npm/release history; use release readback/resume to repair only missing evidence.
