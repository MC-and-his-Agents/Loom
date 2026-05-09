# WI-532 Plan

1. Refresh root self-governance carriers to WI-532 phase closeout.
2. Bump root repository release candidate `VERSION` to `v0.9.0`.
3. Regenerate checked-in skill package metadata so `repo_version` matches `VERSION`.
4. Bump the installer package version for the changed generated payload.
5. Record spec and implementation review evidence for the closeout branch.
6. Run `make check` on the closeout branch.
7. Open and merge the final closeout PR.
8. Rerun `make check` and `npm --prefix packages/loom-installer run check:release` on `main`, publish GitHub release/tag `v0.9.0`, sync #532, and close #532.
