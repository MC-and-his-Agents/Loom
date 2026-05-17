# WI-750 Plan

1. Read #750 phase 3 scope, review execution docs, adapter selection code, and daily execution fixtures.
2. Implement the default adapter selector in `loom_flow.py`, preserving explicit adapter behavior and CI/headless fallback.
3. Extend Codex App authoritative review handling with live app-server proof, binding checks, output normalization, and fail-closed behavior.
4. Update `loom_check.py` fixtures for App default selection, CI fallback, unavailable endpoint fallback, proof conflicts, invalid schema, missing reviewed head, and raw-evidence merge-ready blocking.
5. Synchronize `skills/` and `src/skills/` mirrors plus generated `.loom-runtime` and demo bootstrap surfaces.
6. Update review execution and review skill documentation to describe the new default and fallback semantics.
7. Bump the installer package version because distributed skill behavior changed.
8. Run py_compile, `tools/loom_check.py`, installer version checks, version surface checks, and `make check`.
9. Record fresh spec and implementation review records, push PR #770, and confirm PR gates.
