# CLI-Only Install Contract

This document freezes the user-facing install contract for #1063 before package,
workflow, documentation, and checker implementation work begins.

## Decision

The only primary user-facing install surface for Loom is the root `loom` CLI.

The target install shape is:

```text
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply
loom host register --host codex --scope user --apply
loom install --target . --apply
loom doctor --target .
loom upgrade
```

Equivalent `npx @mc-and-his-agents/loom ...` usage may be supported by the root
package, but it is still the `loom` CLI surface.

## Package Contract

| Field | Frozen contract |
| --- | --- |
| npm package name | `@mc-and-his-agents/loom` |
| bin name | `loom` |
| primary install command | `npm install -g @mc-and-his-agents/loom` |
| ephemeral install command | `npx @mc-and-his-agents/loom ...` |
| version authority | root `VERSION`, converted from `vX.Y.Z` to npm `X.Y.Z` |
| published CLI evidence | npm package version plus GitHub `v*` tag and GitHub Release for the same release commit |
| publish secret | GitHub Actions repository secret `NPM_TOKEN` |

The root npm package must not reuse `packages/loom-installer/package.json`,
`@mc-and-his-agents/loom-installer`, or `loom-installer-v*` tags as its package,
version, or release authority.

## Runtime Boundary

The package may use a Node shim, Python source payload, or both. The runtime
decision belongs to #1065, but it must preserve these constraints:

- the user-facing executable is `loom`;
- the CLI reports fail-closed diagnostics when required local runtime support is
  missing;
- the package payload is explicit and checkable before publish;
- package contents are derived from committed root CLI/runtime/skills/plugins
  surfaces, not from the deprecated installer payload.

## Managed Payloads

`plugins/` and `skills/` remain versioned repository surfaces, but they are not
primary user install entries.

- Host plugins are host adapter payloads managed by the `loom` CLI.
- `SKILLS` are executable scenario payloads managed, synchronized, and verified
  by the `loom` CLI.
- Plugin surface version, host adapter version, skill package version, skill
  contract version, registry version, runtime core version, and schema version
  remain independent authority lines.
- Those independent versions must not drive root CLI publish decisions unless
  the root CLI release judgment explicitly includes them as CLI-managed payload
  changes.

## Deprecated Installer Boundary

`@mc-and-his-agents/loom-installer` is a deprecated historical and compatibility
artifact. It is not a primary install path, not a CLI package, and not release
evidence for the root `loom` CLI.

The hard-cut target for #1063 is:

- README, README.zh-CN, primary install/adoption docs, and new CLI help paths
  present only root `loom` CLI as the install entry.
- `loom-installer` references are allowed only for deprecated historical notes,
  evidence records, compatibility maintenance, or registry/tag non-advancement
  checks.
- `loom-installer` must not gain a new migration journey, active publish
  workflow, or recommended command path.

## Required Follow-on Work

#1064 freezes this contract. The remaining #1063 children consume it in order:

- #1065 creates the root npm package payload and `loom` bin entry.
- #1066 makes the CLI install, update, and verify plugins and SKILLS.
- #1067 hard-cuts README and primary install docs to CLI-only.
- #1068 enforces the contract with checkers.
- #1069 adds npm publish automation.
- #1070 performs the first npm CLI release and closes out the tree.

## Blocked or Missing Permissions

If npm package creation, npm publish, or CI release verification lacks permission,
the active Work Item must record:

- the attempted command or workflow run;
- whether `NPM_TOKEN` exists in GitHub Actions secrets;
- the npm registry response;
- the owner action required to unblock publish.

Permission gaps block publish execution, but they do not change this install
contract.
