# WI-1001 Implementation Contract

## Owned Paths

- `.github/workflows/loom-cli-release.yml`
- `.github/workflows/node-installer-release.yml`
- `.github/workflows/node-installer-pr.yml`
- `docs/adoption/loom-cli-release-surface.md`
- `docs/adoption/version-authority-map.md`
- `tools/check_release_surface.py`
- `tools/version_surface_check.py`
- `packages/loom-installer/scripts/check-version-bump.mjs`
- `packages/loom-installer/scripts/check-doc-sync.mjs`
- `README.md`
- `README.zh-CN.md`
- `packages/loom-installer/README.md`
- `packages/loom-installer/README.zh-CN.md`
- `.loom/work-items/WI-1001.md`
- `.loom/progress/WI-1001.md`
- `.loom/reviews/WI-1001.json`
- `.loom/reviews/WI-1001.spec.json`

## Invariants

- `loom` CLI release evidence comes from `VERSION`, GitHub `v*` tag, GitHub Release, and the `loom-cli-release` workflow.
- Installer release evidence comes from `packages/loom-installer/package.json`, npm publish state, `loom-installer-v*` tag, and `node-installer-release`.
- CLI/runtime changes must not be treated as installer publish evidence by themselves.
- Installer shim changes must still require the installer version bump path.
