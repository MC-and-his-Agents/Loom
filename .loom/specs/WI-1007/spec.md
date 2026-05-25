# WI-1007 Spec

## Intent

Make the release/version/CLI checks enforce that `loom` is the only active CLI release line and that `loom-installer` remains deprecated legacy evidence only.

## Scope

- `tools/check_release_surface.py`
- `tools/check_cli_contract.py`
- `tools/loom.py` release-check output and check chain
- `packages/loom-installer/package.json`
- `packages/loom-installer/scripts/check-doc-sync.mjs`
- Loom WI-1007 carriers and status surfaces

## Required Behavior

- Release surface checks reject active/recommended/current CLI, install, or release evidence statements for `@mc-and-his-agents/loom-installer`, `npx loom-installer`, or `loom-installer-v*` tags.
- `loom skills release-check --json` includes machine-readable release authority showing `loom` as the active CLI line, `VERSION` as candidate authority, GitHub `v*` tag plus GitHub Release as published evidence, and `loom-installer` as non-CLI legacy evidence.
- CLI contract validation asserts that `skills release-check` exposes the authority boundary and does not treat the installer baseline as CLI evidence.
- Installer package release checks run the release surface checker, so package-local prepublish/release validation cannot bypass the #1007 enforcement.
- Doc-sync keeps the Codex default path statement explicit: npm installer is not the Codex default path.

## Non-Goals

- Do not publish `loom` or `@mc-and-his-agents/loom-installer`.
- Do not enable automatic `loom` CLI publishing.
- Do not deprecate npm metadata.
- Do not add a new package, Homebrew formula, or standalone binary.
