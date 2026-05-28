# WI-1130 Implementation Contract

## Consumed Contracts

- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- `docs/methodology/templates/evidence-map.md`
- `docs/methodology/templates/consistency-analysis.md`
- `docs/methodology/harness/task-carrier-contract.md`
- `docs/methodology/harness/gate-chain.md`
- `docs/adoption/github-profile.md`

## Boundaries

- The CLI may validate explicit evidence-map bindings; it must not create a parallel evidence truth source.
- Validation must fail closed for missing repo-local source locators, stale validation summary digest, and HEAD / PR head drift.
- Validation must remain read-only.
- No `/speckit.*` command names or `.specify/` layout may be added.
- No host action, review record write, merge-ready write, closeout write, or Project update may be performed by `suite evidence validate`.

## Output Contract

- Existing readiness fields remain stable.
- New freshness context is derived and diagnostic only.
- Blocking findings use existing taxonomy plus `head_or_pr_drift` and `missing_source_locator`.
