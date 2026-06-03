# WI-1294 Implementation Contract

## Ownership

- Owns: `VERSION`, `package.json`, generated `skills/*/loom-package.json` `repo_version` values, WI-1294 Loom carriers, and terminal repair for `.loom/progress/WI-1217.md`.
- Does not own: metadata-only adoption behavior, release workflow logic, installer publishing, npm package name, or unrelated governance cleanup.

## Implementation Rules

- Root `VERSION` must be `v0.13.10`.
- Root `package.json` version must be `0.13.10`.
- Generated skill `repo_version` fields must match root `VERSION`.
- Existing `v0.13.9` tag, GitHub Release, and npm package must not be overwritten.
- Publishing must occur through `loom-cli-release` on `main`, not through local manual npm publish.

## Validation Contract

- Local checks: `tools/check_release_surface.py`, `tools/version_surface_check.py`, `tools/check_npm_package.py`, `tools/check_cli_contract.py`, `tools/skills_surface.py check`, `tools/loom.py skills check --target . --json`, `npm pack --dry-run --json --ignore-scripts`, and `git diff --check`.
- Host checks: PR CI, post-merge `loom-cli-release`, GitHub tag `v0.13.10`, GitHub Release `v0.13.10`, and npm `@mc-and-his-agents/loom@0.13.10`.
- Closeout: #1217 and #1294 must record final release evidence.
