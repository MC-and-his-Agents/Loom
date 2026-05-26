# WI-1019 Plan

## Implementation Target

Update harness methodology contracts for gate-chain consumption only.

## Phases

1. Read #1012, #1016, #1017, #1018, #1020 and child Work Items #1045-#1048.
2. Update `gate-chain.md` for full suite gate inputs, pre-review, review, merge gate and closeout consumption.
3. Update `review-execution.md` for pre-review/review consumption and review record backlinks.
4. Update `merge-checkpoint.md` for blocking consistency gap, stale evidence, head drift and valid `not_applicable`.
5. Update `closeout-gate.md` for evidence-map / consistency-analysis / merged result reconciliation.
6. Record #1020 integration needs and validation evidence.

## Validation Strategy

| Scenario | Validation |
| --- | --- |
| S1 | Focused `rg` for pre-review, evidence-map, consistency-analysis and blocking gap terms. |
| S2 | Focused `rg` for review record and consumed input terms. |
| S3 | Focused `rg` for merge-ready, stale evidence, head drift, fail-closed and consistency gap terms. |
| S4 | Focused `rg` for closeout, merge commit, target branch, issue state and reconciliation audit terms. |
| S5 | Focused `rg` for `not_applicable`, missing, rationale and minimal path terms. |

## Test Strategy

- `git diff --check`
- Focused `rg` over `docs/methodology/harness` and `.loom/progress/WI-1019.md`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Fresh Evidence Expectation

Evidence is fresh when it is produced from branch `work/1019-gate-chain-consumption` at commit `e40f982d1bbd59a0168a935a3200dfd39dc4c764` or a later carrier-only commit for #1019 review / recovery / status evidence.

## Dependencies

- Consumes #1016, #1017 and #1018 contracts without redefining them.
- #1020 consumes this Work Item for skills/GitHub profile/generated-surface integration.
