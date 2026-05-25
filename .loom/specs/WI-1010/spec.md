# WI-1010 Spec

## Intent

Record the final npm registry state for deprecated `loom-installer` and attempt deprecation only when npm registry permissions are available.

## Scope

- npm state for `@mc-and-his-agents/loom-installer`
- owner action evidence when npm deprecate is not authorized
- legacy installer baseline evidence
- Loom WI-1010 carriers and status surfaces

## Required Behavior

- Verify current npm package version/deprecation metadata.
- Verify local npm registry identity before attempting any deprecation.
- If authorized, run `npm deprecate @mc-and-his-agents/loom-installer@"*" "Deprecated: use the Loom CLI GitHub release line instead."` or equivalent wording.
- If unauthorized, do not attempt a blind write; record the exact npm permission failure and the owner action required.
- Preserve installer sunset behavior: no npm publish, no version bump, no new `loom-installer-v*` tag, and no installer GitHub Release.

## Non-Goals

- Do not publish a new installer package version.
- Do not change the active `loom` CLI release line.
- Do not add npm/Homebrew/standalone binary distribution for `loom`.
