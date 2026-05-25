# WI-1009 Implementation Contract

## Inputs

- Issue #1009 depends on #1008.
- #1008 merged at f145673a3e535b345c47997a33bcf5385d7b879f and enabled main-push CLI publishing.
- Current root `VERSION` is `v0.12.0`, which is already published.
- Latest legacy installer baseline is `@mc-and-his-agents/loom-installer` `0.1.119` and GitHub release `loom-installer-v0.1.119`.

## Commit Contract

- The implementation PR may update root `VERSION`, generated version metadata, release readiness evidence, and Loom governance carriers.
- The PR must not change `packages/loom-installer/package.json` version or restore installer publish capabilities.
- The PR must not create tag/release evidence manually; publishing must be produced by the main-push workflow after merge.

## Verification Contract

- Local validation must include release-surface, version-surface, CLI contract, installer docs/version/payload/distribution checks, Loom fact-chain/shadow/adoption gates, and `make check`.
- PR validation must include local `pr-gate`, required PR checks, and `loom-cli-release/release-judgment`.
- Post-merge validation must prove the new `v0.13.0` tag and GitHub Release point at the merge commit and that installer release/npm state did not advance.
