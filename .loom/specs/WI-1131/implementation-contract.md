# WI-1131 Implementation Contract

## Consumed Contracts

- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- `docs/methodology/harness/task-carrier-contract.md`
- `docs/methodology/templates/execution-breakdown.md`
- `docs/methodology/templates/evidence-map.md`
- `docs/methodology/templates/consistency-analysis.md`
- `docs/methodology/harness/gate-chain.md`
- `docs/adoption/github-profile.md`

## Boundaries

- The CLI may inspect and validate task-carrier rows; it must not create a parallel Work Item, evidence, review, merge-ready, or closeout truth source.
- Validation must fail closed for missing carrier locators, invalid normalized status or relationship values, missing Work Item backlinks, primary carrier conflicts, deferred-as-completed, and truth replacement claims.
- Validation must remain read-only.
- No `/speckit.*` command names or `.specify/` layout may be added.
- No host action, review record write, merge-ready write, closeout write, Project update, or issue update may be performed by `suite carrier inspect` / `suite carrier validate`.

## Output Contract

- Existing readiness fields remain stable.
- Carrier rows are diagnostic and validation evidence only.
- Blocking findings use `missing_task_carrier_locator`, `carrier_truth_conflict`, `deferred_as_completed`, and existing suite taxonomy fields.
