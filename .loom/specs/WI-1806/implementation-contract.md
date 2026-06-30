# WI-1806 Implementation Contract

## Ownership

- Owns `loom pr-intent prepare/check` shared profile routing, carrier generation, metadata validation, head binding, changed-path scope proof, and carrier-set consistency in `tools/loom.py`.
- Owns `loom docs-pr prepare/check` as the short path for the docs/governance-only profile.
- Owns focused contract fixtures in `tools/check_cli_contract.py` for profile happy paths, scope drift, stale head binding, and suite N/A exit semantics.
- Owns command matrix documentation for the new profile helpers and their non-bypass boundaries.
- Owns WI-1806 repo-local carriers needed for fact-chain and PR readiness.

## Boundaries

- Do not publish `v0.22.0`, update release evidence, or change package/plugin metadata until #1800 / `v0.21.2` completes or explicitly releases the publication line.
- Do not close or rewrite #1800/#1802 issue closeout or v0.21.2 release carriers.
- Do not make PR intent profiles bypass current-head review, PR gate, merge-ready, release/no-release readback, host reconciliation, or closeout evidence.
- Do not introduce a large DSL or a second metadata mechanism parallel to suite validation and PR metadata preflight.

## Release Metadata Rule

- #1815 release-only readiness may be prepared and checked on this branch.
- `v0.22.0` version, package metadata, plugin metadata/hash, release notes, publish, npm/package readback, and final release evidence must wait for #1800 / `v0.21.2`.
