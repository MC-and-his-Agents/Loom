# WI-533 Spec

## Objective

Close `v0.10.0` / `#533` only after repository release truth, merged main scope, review evidence, closeout validation, and GitHub release publication agree.

## Acceptance

- `main` contains the merged candidate scope for `#728` through `#733`.
- Phase issues `#533`, `#649`, and `#693` remain closed as completed after the release is published.
- `VERSION` declares `v0.10.0`, and generated skill package metadata exposes the same repository release candidate.
- `make check` passes on a clean worktree before and after the closeout PR merges.
- `npm --prefix packages/loom-installer run check:release` passes after the closeout PR merges.
- GitHub release/tag `v0.10.0` is created only after the final closeout commit is on `main`.
- The final release body names the merged v0.10.0 scope and preserves the live/profile-local confidence boundary from `docs/evidence/v0.10.0-release-readiness.md`.

## Non-Goals

- Do not reopen already completed v0.10.0 or v0.10.x phase scope while performing release closeout.
- Do not promote adopted-repo live smoke into a core blocking gate.
- Do not publish an intermediate `v0.10.x` tag before `v0.10.0` release truth is aligned.
