# WI-792 Spec

## Goal

Close GitHub issue #792 by making the retained GitHub issue, Project, PR, and native dependency host control plane behavior verifiable through PR #991 and the #812 closeout basis.

## Acceptance

- `github-intake issue` reads GitHub issue/Project/PR binding, goal semantics, native dependency summary, drift, route, missing inputs, and provenance as stable JSON without mutating GitHub state.
- Native dependency handling treats GitHub dependencies as a host mirror, classifies GraphQL capability, blocks on open blockers or stale mirror findings, and emits dry-run safe-sync actions only with proof locators.
- `loom_check --profile source` remains the full source self-check while named source surfaces support focused contract, bootstrap, fixture, and distribution regression validation with progress diagnostics and structured setup failures.
- #812 closeout evidence records completed FRs, fixtures, validation commands, manual GitHub verification, rollback basis, and non-blocking risks.
- PR #991, current branch, active Loom carrier, review evidence, installer version metadata, and host closeout state are aligned before #792 closeout.

## Out Of Scope

- Writing native GitHub dependency edges.
- Moving #872/#953 out of #792 scope.
- Closing #812/#792 before PR #991 is merged into `main`.
