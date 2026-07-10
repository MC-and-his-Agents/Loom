# WI-1293 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1293 is a bounded release closeout and version advancement lane for milestone 9. It consumes already merged #1452 controlled-merge triggered-check behavior and #1292 cross-repo fixture coverage, updates documentation/help surfaces, and publishes the existing Loom CLI/package surface as v0.16.0. Separate research, readiness checklist, and broad contracts would duplicate existing release-surface contracts. consumer boundary: suite validate, spec review, implementation review, merge-ready, hosted CI, release workflow, target branch validation, #1293 closeout, and #1285 parent closeout. recheck condition: require full suite if scope expands into release workflow semantics, npm package payload semantics, #1452 runtime behavior, #1292 fixture logic, live branch protection/ruleset mutation, external repository changes, or unrelated runtime features.

## Acceptance Scenarios

- A1: README and adoption docs describe the standard Loom controlled merge chain and state that CI/checks cannot replace authored semantic review.
- A2: CLI help / command matrix exposes `pr gate`, `merge check`, and `merge run` as the standard merge path.
- A3: Version authority surfaces advance consistently from v0.15.0 to v0.16.0.
- A4: Release readiness evidence records candidate occupancy, validation commands, completed #1452/#1292 consumption, expected publish path, and explicit authorization boundary.
- A5: Post-merge release evidence binds the `loom-cli-release` main-push run, v0.16.0 tag, GitHub Release, npm package, target branch, installed/global CLI smoke, and installer non-advancement before terminal closeout.

## Non Goals

- Do not alter `loom-cli-release` publishing semantics.
- Do not alter npm package payload inclusion/exclusion semantics outside version metadata.
- Do not change #1452 controlled-merge runtime logic or #1292 regression fixture behavior.
- Do not mutate live branch protection/rulesets or external HotCP/WebEnvoy/Syvert repositories.
- Do not close parent #1285 before #1293 release evidence is terminal.
