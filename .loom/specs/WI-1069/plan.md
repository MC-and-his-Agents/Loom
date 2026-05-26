# WI-1069 Plan

1. Extend `.github/workflows/loom-cli-release.yml` with Node setup, npm package checks, npm registry state resolution, and publish steps guarded by release judgment.
2. Update release-surface documentation to define npm publish decisions, fail-closed auth behavior, and tag/release/npm consistency.
3. Strengthen `tools/check_release_surface.py` so PR/main checks verify the workflow retains npm publish preconditions.
4. Run focused checks and full repository validation.
5. Bind review evidence, open PR, run PR checks, merge, and hand off to #1070 for first actual npm release closeout.
