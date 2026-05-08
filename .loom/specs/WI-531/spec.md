# WI-531 Spec

## Objective

Close v0.8.0 / #531 only after repository release truth, GitHub issue truth, main, review evidence, merge-ready evidence, and release publication agree.

## Acceptance

- All FR issues #561, #566, #571, #576, #675, #679, #689, and #706 are closed after their child Work Items merged to main.
- All child Work Items #562-#565, #567-#570, #572-#575, #577-#580, #676-#678, #680-#683, #690-#692, and #707-#710 are closed.
- `VERSION` declares `v0.8.0`, and generated skill package metadata exposes the same repository release candidate.
- `make check` passes on a clean worktree before and after the closeout PR merges.
- GitHub release/tag `v0.8.0` is created only after the final closeout commit is on `main`.
- #531 is closed only after the tag/release and issue checklist match the merged state.

## Non-Goals

- Do not publish intermediate FR releases.
- Do not change installer, plugin, contract, schema, or skill package version lines merely to match `VERSION`.
- Do not reopen completed FR scope while performing closeout.
