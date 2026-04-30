# Host API Budget

Canonical contract: `docs/methodology/harness/host-api-budget.md`.

Installed summary:

- Non-merge reads use `cached_non_merge`.
- Merge gate reads use `uncached_live_gate` and fail closed on missing live host facts.
- REST is preferred; GraphQL requires explicit scope, cost, and fallback.
- Search endpoint and polling are not hot-path mechanisms.
- Remote read failures must surface as `unverified`, `stale`, or `host_unavailable`.
