# WI-906 Plan

1. Move `detect`, `doctor`, `repair plan`, and `repair apply` from reserved names to implemented CLI commands.
2. Reuse installed-state v2 validation as the authority boundary.
3. Add detection for legacy runtime, repo-local skills, full-repo skills, plugin, installer, single-skill, and symlink surfaces.
4. Make doctor fail closed on missing/invalid installed-state or blocking legacy surfaces.
5. Make repair plan non-mutating and repair apply fail closed.
6. Extend CLI contract checks with #906-#909 fixtures.
7. Update CLI and installed-state docs.
8. Run focused checks, full `make check`, PR gate, and CI before merge.
