# WI-1001 Spec

## Intent

Define the post-#885 release split so future `loom` CLI behavior is released through the root Loom CLI line, while `loom-installer` remains a compatibility and legacy maintenance line.

## Required Behavior

- The primary `loom` CLI release authority is root `VERSION` plus GitHub `v*` tag and GitHub Release state.
- `@mc-and-his-agents/loom-installer` and `loom-installer-v*` tags are not evidence that the `loom` CLI was published.
- Normal PRs and `main` pushes record a `loom` CLI release judgment without publishing.
- Publishing a `loom` CLI release requires explicit `workflow_dispatch` intent.
- Installer release judgment advances only for installer shim/package behavior, not for generated skills, plugin discovery, or CLI runtime behavior alone.
- Documentation and checks must make the two release lines independently auditable.

## Non-Goals

- Do not add a new npm package, Homebrew formula, or standalone binary in this item.
- Do not synchronize root `VERSION`, installer package version, plugin version, skill/runtime versions, or schema versions.
- Do not reopen #885 or change unrelated governance/profile behavior.
