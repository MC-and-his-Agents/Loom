# WI-963 Spec

## Behavior Contract

`loom_check` must have a single documented runtime-purity contract that downstream P0-A work can cite before changing locks, temporary paths, fixture generation, host environment handling, or Node installer regression behavior.

## Required Scenarios

1. A maintainer can find the `loom_check` runtime-purity authority under `docs/methodology/harness/`.
2. A skill consumer can read the same contract from shared harness references.
3. Source self-check fails if the contract or shared reference loses required anchors for profile boundary, run id, single-flight, fixed `/tmp`, host environment purity, stable fixture purity, or Node installer write isolation.
4. The contract explicitly excludes #866 closeout gate, #873 PR metadata, #969 review profile, #953 source self-check layering, and CLI-first mainline work.

## Acceptance

- `docs/methodology/harness/README.md` links the contract.
- `skills/shared/references/harness/loom-check-runtime-purity.md` is generated from `src/skills`.
- `loom_check` source profile can consume the contract as a checked source surface.
