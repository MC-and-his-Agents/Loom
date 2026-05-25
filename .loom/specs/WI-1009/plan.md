# WI-1009 Plan

1. Confirm current release state: `VERSION=v0.12.0`, GitHub tag/release `v0.12.0` exists, and legacy installer latest is `0.1.119`.
2. Update root `VERSION` to `v0.13.0` and regenerate version surfaces.
3. Add release readiness evidence describing the version choice and required post-merge checks.
4. Run local checks for release surface separation, version surfaces, CLI contract, installer non-publish checks, Loom fact-chain/shadow/adoption gates, and `make check`.
5. Open #1009 PR from `work/1009-first-cli-release`, consume local pr-gate and GitHub PR checks.
6. Merge with head matching and verify main-push `loom-cli-release` creates tag/release `v0.13.0`.
7. Record post-merge release, npm, tag, and issue state evidence before closing #1009.
