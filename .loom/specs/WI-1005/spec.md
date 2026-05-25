# WI-1005 Spec

## Intent

Disable the active `loom-installer` release path so a normal `push: main` cannot publish npm, create a `loom-installer-v*` tag, or create an installer GitHub Release.

## Scope

- `.github/workflows/node-installer-release.yml`
- `tools/check_release_surface.py`

## Required Behavior

- The installer release workflow may still run validation checks and report a sunset judgment.
- The installer release workflow must not request npm publish credentials.
- The installer release workflow must not contain package publication, installer tag creation, or installer GitHub Release creation steps.
- The release surface checker must fail if active installer publish capability is reintroduced.

## Non-Goals

- Do not deprecate npm in this work item.
- Do not change `loom` CLI automatic release behavior in this work item.
- Do not migrate installation documentation in this work item.
