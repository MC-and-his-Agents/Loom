# WI-533 Plan

1. Refresh root self-governance carriers to `WI-533` release closeout.
2. Bump root repository release candidate `VERSION` to `v0.10.0`.
3. Regenerate checked-in skill package metadata so `repo_version` matches `VERSION`.
4. Bump the installer package version for the changed generated payload and release truth.
5. Refresh v0.10.0 release readiness evidence so the candidate scope is recorded in version control.
6. Run `make check` on the closeout branch.
7. Open and merge the final closeout PR.
8. Rerun `make check` and `npm --prefix packages/loom-installer run check:release` on `main`, publish GitHub release/tag `v0.10.0`, and verify release truth matches the merged state.
