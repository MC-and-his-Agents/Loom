# WI-1737 Spec

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: WI-1737 is a bounded checkpoint canonicalization fix with focused behavior and fixture regression coverage. consumer boundary: suite validate, suite evidence validate, suite carrier validate, current-head review, PR metadata readback, hosted checks, controlled merge, and closeout may consume this minimal suite plus WI-1737 fact-chain. recheck condition: require a full suite if scope expands into checkpoint state-machine semantics, ship orchestration, closeout policy, release behavior, external host writes, or new governance checkpoint values. scope proof: changed source paths stay limited to checkpoint normalization/write behavior, synchronized generated runtime copies, fixture updates, tests, and WI-1737 carriers. review requirement: current-head review required before merge-ready consumption.

## Intent

Checkpoint persistence keeps reading legacy checkpoint spellings but writes only the canonical checkpoint enum values that Loom gates consume.

## Scenarios

| scenario_id | behavior | acceptance |
| --- | --- | --- |
| S1 | A checkpoint update receives a legacy or alias value. | The read path accepts the input and normalizes it to the matching canonical value. |
| S2 | A checkpoint update is written back to Loom recovery/status fixtures. | The persisted checkpoint value is one of the canonical enum values only. |
| S3 | Demo bootstrap fixtures are regenerated or validated. | The generated `.loom` fixture continues to use canonical checkpoint values. |

## Out Of Scope

- Changing the checkpoint state machine semantics.
- Introducing new checkpoint values.
- Changing ship or closeout policy.
