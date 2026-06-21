# WI-1691 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1691.md`
- FR / parent locator: issue #1689
- Scope: `loom ship --apply` orchestration with host-only closeout default; no default closeout PR.
- Suite path: minimal
- Current `HEAD`: update before merge-ready consumption.
- PR locator, or N/A rationale: fill when PR exists.
- Host state locator, or N/A rationale: issue #1691

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1691/spec.md` | required | authored for issue #1691 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1691/plan.md` | required | authored for issue #1691 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1691/spec.md` | minimal | authored suite contract | Recheck before merge-ready. |
| execution breakdown / task carrier | `.loom/specs/WI-1691/task-carrier.md` | required | authored task carrier | Recheck before review and closeout. |
| review record | `.loom/reviews/WI-1691.json` | required before merge-ready | authored review truth | Required after review consumption. |
| merge-ready basis | PR merge-ready attempt artifact | required before closeout | merge-ready truth | Required after PR exists. |
| host state | issue #1691 | required | host mirror | Recheck after PR creation and merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1-S4 ship apply behavior | WI-1691 / branch `work/1691-ship-apply` | present | review / merge-ready / closeout | Re-run ship-wrapper after `handle_ship` changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1-A5 wrapper contract | WI-1691 / root CLI wrapper | present | review / merge-ready / closeout | Re-run ship-wrapper and adjacent wrapper surfaces. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1691.md` | EV-001 EV-002 | current branch / current head before PR | present | merge-ready / closeout | Refresh after any implementation or contract-test changes. |
| EV-004 | build_evidence | `.loom/progress/WI-1691-build-evidence.json` | integrated implementation, subagent summary, ownership, and validation evidence | WI-1691 / build checkpoint | present | build / review / merge-ready | Regenerate through loom-build after implementation, validation, review findings, or ownership changes. |
| EV-005 | behavior_evidence | `.loom/specs/WI-1691/implementation-contract.md` | runtime, delegation, closeout policy, and boundary contracts | WI-1691 / implementation review | present | review / merge-ready | Refresh if apply behavior or closeout boundary changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| controlled-merge closeout-run | deferred | Explicit controlled-merge flag is separate from root ship apply. | planning only | Start #1692 after #1691 merges. | #1692 |
| README/skills convergence | deferred | User-facing documentation should consume the final ship path after apply behavior lands. | planning only | Start #1694 after #1691 merges. | #1694 |
| release publication | N/A | #1691 does not publish a release by itself. | closeout / release planning | Recheck if package or version metadata changes. | #1696 |
