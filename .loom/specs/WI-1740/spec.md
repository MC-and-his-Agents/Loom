# WI-1740 Spec

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: WI-1740 is a bounded review freshness classifier update with focused PR gate fixture coverage. consumer boundary: suite validate, suite evidence validate, suite carrier validate, current-head review, PR metadata readback, hosted checks, controlled merge, and closeout may consume this minimal suite plus WI-1740 fact-chain. recheck condition: require a full suite if scope expands into release publishing, validation profile selection, ship repair-chain mutation, new external host writes, or broad review engine policy. scope proof: changed source paths stay limited to review head binding runtime copies, focused CLI contract tests, and WI-1740 carriers. review requirement: current-head review required before merge-ready consumption.

## Intent

Review freshness should explain what changed after review. Generated output drift should get a focused validation action instead of the same full review friction as source or behavior drift.

## Scenarios

| scenario_id | behavior | acceptance |
| --- | --- | --- |
| S1 | Only Loom carrier/review/status/shadow paths changed after review. | Binding remains `carrier-only`, stale is false, and gate consumers pass. |
| S2 | Only known generated surfaces changed after review. | Binding reports `generated-only`, stale is false, includes generated validation actions, and PR gate consumers pass. |
| S3 | Source, behavior, test, workflow, or mixed semantic paths changed after review. | Binding reports `implementation-drift-only` or `stale`, stale is true, and consumers require renewed authored review. |

## Out Of Scope

- Running generated repair automatically inside `loom ship` (#1739).
- Selecting changed-path validation profiles (#1741).
- Release closeout behavior.
