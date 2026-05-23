# WI-967 Spec

## Acceptance

- Default `loom_check` subprocesses do not inherit host-only `CODEX_*`, `LOOM_CODEX_APP_REVIEW_*`, `CI`, `CODEX_CI`, `GH_TOKEN`, or `GITHUB_TOKEN` values.
- Fixtures can still pass those variables explicitly through the `env=` command boundary when a test intentionally needs them.
- Missing live-smoke target samples use a per-run unique absent path, not a fixed `/tmp/loom-missing-live-target` path.
- Existing explicit Codex App proof and live-smoke fixtures keep their semantics.
- Generated skills runtime and bootstrapped demo runtime stay in sync with the source script.

## Non-Goals

- Do not remove Codex App review adapter tests.
- Do not change explicit live smoke meaning.
- Do not implement #965 fixture write isolation, #966 installer write isolation, #968 regression matrix, #953 profile layering, or CLI-first mainline changes.
