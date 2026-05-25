# WI-1008 Spec

## Intent

Enable the single active `loom` CLI release workflow to publish automatically after eligible `main` merges without restoring any `loom-installer` publish path.

## Scope

- `.github/workflows/loom-cli-release.yml`
- `docs/adoption/loom-cli-release-surface.md`
- `tools/check_release_surface.py`
- Loom WI-1008 carriers and status surfaces

## Required Behavior

- Pull requests run release judgment but must not create tags or GitHub Releases.
- `push` events on `main` may create the GitHub `v*` tag and GitHub Release when CLI publish behavior changed and root `VERSION` names an unpublished candidate.
- `workflow_dispatch` with `publish=true` remains a repair path for missing tag/release evidence.
- Existing `v*` tags must never be overwritten. If CLI publish behavior changed and the current `VERSION` tag points at another commit, the workflow must fail closed with `version-already-published-on-different-commit`.
- Release-control-only changes, such as this workflow and release-surface documentation, must receive validation but must not auto-publish by themselves.
- Installer npm state, `loom-installer-v*` tags, and installer GitHub Releases must remain excluded from active `loom` CLI publish evidence.

## Non-Goals

- Do not perform the first `loom` CLI release in #1008.
- Do not bump root `VERSION` in #1008 unless a separate product decision requires it.
- Do not publish, deprecate, or advance `@mc-and-his-agents/loom-installer`.
- Do not add a new npm package, Homebrew formula, or standalone binary.
