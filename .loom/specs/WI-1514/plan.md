# WI-1514 Plan

- Suite path: not_applicable

## Implementation Steps

- Update `skills/loom-pre-review/SKILL.md` to call out gate freeze before formal review once a PR is bound.
- Update `skills/loom-review/SKILL.md` so review does not bypass freeze-side metadata/head/shadow/release-boundary blockers.
- Update `skills/loom-merge-ready/SKILL.md` so merge-ready consumes frozen and read-back PR inputs instead of reassembling a parallel check chain.
- Update `docs/methodology/harness/cli-command-matrix.md` with `unsupported_command_surface` troubleshooting guidance.
- Update `docs/evidence/regression-surface-inventory.md` with the current gate-freeze/hosted-admission coverage boundary.

## Validation

- `git diff --check`
- `rg` readback for `loom gate freeze check|write`, `pr_metadata_drift`, `shadow_stale`, `unsupported_command_surface`, and `hosted_snapshot_mismatch`
- PR metadata render/readback for PR #1574 and current head
