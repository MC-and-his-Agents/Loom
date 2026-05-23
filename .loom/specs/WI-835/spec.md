# WI-835 Spec

## Goal

Close FR #835 by making complex-existing repository governance authority migration executable in Loom.

## Acceptance

- The adoption playbook covers Phase 1, Phase 1.1, and Phase 2 through Phase 7.
- Each phase declares authority before, authority after, rollback, validation, and no-dual-authority invariant.
- Review, spec-review, merge-ready, retained host signal, and controlled merge contracts expose stable machine-readable schemas.
- `loom_flow.py` emits the migration records needed by review, merge-ready, and controlled merge consumers.
- `loom_check.py` validates synthetic fixtures for app proof, fallback, stale/head mismatch, schema drift, dual authority, retained signal drift, and tracked file mutation.
- Generated skill surfaces and the demo bootstrap fixture are synchronized.

## Non-Goals

- Do not make host guardian, proof store, or repo-native gates a second Loom verdict authority.
- Do not close parent #835 until child issues #836 through #842 and the PR merge are reconciled.
