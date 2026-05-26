# WI-1068 Plan

1. Strengthen `tools/check_release_surface.py` with CLI-only active-doc coverage and negative fixtures for SKILLS/plugin/installer install surfaces.
2. Strengthen `tools/check_npm_package.py` so root package manifest and dry-run payload remain bound to root `loom` CLI plus CLI-managed payloads.
3. Run focused release/package/CLI checks, installer legacy checks, Loom fact-chain/shadow/adopt checks, and `make check`.
4. Bind review and PR evidence to the final head, then merge only after GitHub checks pass.
