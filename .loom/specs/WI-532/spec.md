# WI-532 Spec

## Objective

Close v0.9.0 / #532 only after repository release truth, GitHub issue truth, main, review evidence, merge-ready evidence, and release publication agree.

## Acceptance

- All FR issues #581, #585, #589, #593, and #684 are closed after their child Work Items merged to main.
- All child Work Items #582-#596 and #685-#688 are closed.
- `VERSION` declares `v0.9.0`, and generated skill package metadata exposes the same repository release candidate.
- `make check` passes on a clean worktree before and after the closeout PR merges.
- `npm --prefix packages/loom-installer run check:release` passes after the closeout PR merges.
- GitHub release/tag `v0.9.0` is created only after the final closeout commit is on `main`.
- #532 is closed only after the tag/release and issue checklist match the merged state.

## Non-Goals

- Do not publish intermediate FR releases.
- Do not reopen completed FR scope while performing closeout.
- Do not recreate or reimplement the already completed #684 line.
