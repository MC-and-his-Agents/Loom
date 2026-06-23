# WI-1738 Spec

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: WI-1738 is a bounded ship wrapper inference change with focused CLI contract regression coverage. consumer boundary: suite validate, suite evidence validate, suite carrier validate, current-head review, PR metadata readback, hosted checks, controlled merge, and closeout may consume this minimal suite plus WI-1738 fact-chain. recheck condition: require a full suite if scope expands into release publishing, validation profile selection, review stale classification, shadow parity repair, or new closeout policy semantics. scope proof: changed source paths stay limited to `tools/loom.py`, focused CLI contract tests, and WI-1738 carriers. review requirement: current-head review required before merge-ready consumption.

## Intent

`loom ship` should infer branch, head SHA, and target branch from the current host context so normal issue-scoped ship paths do not require operators to remember repeated metadata flags.

## Scenarios

| scenario_id | behavior | acceptance |
| --- | --- | --- |
| S1 | `loom ship --item <id> --pr <n>` runs on an issue-scoped branch without explicit binding flags. | Ship reads the PR and checkout context, records inferred branch/head/target bindings, and passes effective branch/head values to metadata preflight, PR gate, and controlled merge checks. |
| S2 | `loom ship --apply --issue <n> --pr <n>` needs safe metadata repair and host-only closeout branch selection. | Safe metadata repair receives the inferred branch/head, and closeout target branch uses PR base readback when no explicit target branch is supplied. |
| S3 | Explicit binding flags conflict with PR readback. | Ship fails closed before mutating gates and emits a short next action asking for explicit corrected bindings. |

## Out Of Scope

- Implementing the #1739 pre-ship repair chain.
- Implementing #1740 review stale classification.
- Implementing #1741 changed-path validation profiles.
- Publishing or changing release behavior.
