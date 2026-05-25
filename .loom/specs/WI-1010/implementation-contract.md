# WI-1010 Implementation Contract

## Inputs

- Issue #1010 depends on #1005 and #1006.
- #1005 disabled installer publishing.
- #1006 and #1007 moved active release evidence to the `loom` CLI line.
- Current npm package state reads `@mc-and-his-agents/loom-installer` latest `0.1.119`.

## Write Contract

- The PR may add evidence and Loom carriers.
- The PR must not change `packages/loom-installer/package.json` version.
- The PR must not restore `node-installer-release` publish capability.
- The PR must not create npm, GitHub tag, or GitHub Release side effects.

## Owner Action If Blocked

An npm owner with publish/deprecate permission must run:

```sh
npm deprecate @mc-and-his-agents/loom-installer@"*" "Deprecated: use the Loom CLI GitHub release line instead."
```

Then the owner must re-read:

```sh
npm view @mc-and-his-agents/loom-installer version deprecated --json
```
