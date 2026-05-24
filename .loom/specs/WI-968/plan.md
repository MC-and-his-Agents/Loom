# WI-968 Plan

1. Add a lightweight regression script under `tools/` for loom_check runtime purity and concurrency hardening.
2. Wire the script into `make loom-check` through a named `loom-check-runtime-regression` target.
3. Document the default lightweight entry and the heavy opt-in boundary.
4. Refresh generated skills references from `src/skills`.
5. Bump installer metadata for distributed reference payload drift.
6. Validate py-compile, skills surface, version surface, version bump, the new regression target, and full `make loom-check`.
