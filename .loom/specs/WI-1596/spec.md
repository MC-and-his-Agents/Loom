# WI-1596 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1596 is a bounded release closeout and version advancement lane for milestone #13. It consumes completed child issue/PR facts and publishes the existing Loom CLI/package surface as v0.15.0; separate research, readiness checklist, and broad contracts would duplicate existing release-surface contracts. consumer boundary: suite validate, spec review, implementation review, merge-ready, hosted CI, release workflow, target branch validation, #1596 closeout, #1598 closeout, and #1594 parent closeout. recheck condition: require full suite if scope expands into release workflow semantics, npm package payload semantics, host auth behavior, PR metadata semantics, dependency parser semantics, closeout role behavior, or unrelated runtime features.

## Acceptance Scenarios

- A1: Version authority surfaces advance consistently from v0.14.2 to v0.15.0.
- A2: Release readiness evidence records candidate occupancy, validation commands, expected publish path, and explicit authorization boundary.
- A3: Milestone #13 issues, PRs, merge commits, hosted checks, and target branch readback are consumable for release closeout.
- A4: WI-1598 terminal carrier metadata is present for downstream #1596/#1594 closeout.
- A5: Post-merge release evidence must bind the release workflow run, v0.15.0 tag, GitHub Release, npm package, target branch, and installer non-advancement before terminal closeout.

## Non Goals

- Do not change release workflow semantics, npm package payload semantics, host auth, PR metadata renderer semantics, dependency parser semantics, or closeout role behavior.
- Do not publish without explicit authorization.
