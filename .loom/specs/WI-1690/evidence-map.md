# WI-1690 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1690.md`
- FR / parent locator: issue #1689
- Scope: `loom ship` dry-run orchestration only; no host or repo mutation.
- Suite path: minimal
- Current `HEAD`: update before merge-ready consumption.
- PR locator, or N/A rationale: fill when PR exists.
- Host state locator, or N/A rationale: issue #1690

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1690/spec.md` | required | authored for issue #1690 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1690/plan.md` | required | authored for issue #1690 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1690/spec.md` | minimal | authored suite contract | Recheck before merge-ready. |
| execution breakdown / task carrier | `.loom/specs/WI-1690/task-carrier.md` | required | authored task carrier | Recheck before review and closeout. |
| review record | `.loom/reviews/WI-1690.json` | required before merge-ready | authored review truth | Required after review consumption. |
| merge-ready basis | PR merge-ready attempt artifact | required before closeout | merge-ready truth | Required after PR exists. |
| host state | issue #1690 | required | host mirror | Recheck after PR creation and merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1-S3 ship dry-run behavior | WI-1690 / branch `work/1690-ship-dry-run` | present | review / merge-ready / closeout | Re-run ship-wrapper after `handle_ship` changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1-A5 wrapper contract | WI-1690 / root CLI wrapper | present | review / merge-ready / closeout | Re-run ship-wrapper and aggregate surfaces. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1690.md` | EV-001 EV-002 | current branch / current head before PR | present | merge-ready / closeout | Refresh after any implementation or contract-test changes. |
| EV-004 | build_evidence | `.loom/progress/WI-1690-build-evidence.json` | integrated implementation, subagent summary, ownership, and validation evidence | WI-1690 / build checkpoint | present | build / review / merge-ready | Regenerate through loom-build after implementation, validation, review findings, or ownership changes. |
| EV-005 | behavior_evidence | `.loom/specs/WI-1690/implementation-contract.md` | runtime, delegation, closeout policy, and boundary contracts | WI-1690 / implementation review | present | review / merge-ready | Refresh if dry-run behavior or apply boundary changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| `loom ship --apply` | deferred | #1690 is dry-run only and must not mutate host or repo state. | merge-ready / closeout | Start #1691 after dry-run surface merges. | #1691 |
| controlled merge closeout-run | deferred | Explicit closeout-run merge wrapper integration is separate. | planning only | Start #1692 after #1691 or shared closeout policy consumption is stable. | #1692 |
| release publication | N/A | #1690 does not publish a release by itself. | closeout / release planning | Recheck if package or version metadata changes. | #1696 |
