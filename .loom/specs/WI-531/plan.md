# WI-531 Plan

1. Verify all FR and child Work Item issues are closed.
2. Bump root repository release candidate `VERSION` to `v0.8.0`.
3. Regenerate checked-in skill package metadata so `repo_version` matches `VERSION`.
4. Refresh root self-governance carriers to WI-531 phase closeout.
5. Record spec and implementation review evidence.
6. Run merge-ready, adoption, shadow parity, and `make check` on the closeout branch.
7. Open and merge the final closeout PR.
8. Rerun `make check` on `main`, publish GitHub release/tag `v0.8.0`, sync #531, and close #531.
