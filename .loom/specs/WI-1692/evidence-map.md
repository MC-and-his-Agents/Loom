# WI-1692 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1692.md`
- FR / parent locator: issue #1689
- Scope: explicit controlled-merge closeout-run transition with closeout policy gating.
- Suite path: minimal
- Current `HEAD`: `f60c6b9ae58c0290fb18c0c1f71f66aa7be5c618`
- PR locator, or N/A rationale: PR #1707
- Host state locator, or N/A rationale: issue #1692

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1692/spec.md` | required | authored for issue #1692 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1692/plan.md` | required | authored for issue #1692 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1692/spec.md` | minimal | authored suite contract | Recheck before merge-ready. |
| implementation contract | `.loom/specs/WI-1692/implementation-contract.md` | required | authored contract | Recheck when wrapper behavior changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1692/task-carrier.md` | required | authored task carrier | Recheck before review and closeout. |
| review record | `.loom/reviews/WI-1692.json` | required before merge-ready | authored review truth | Required after review consumption. |
| merge-ready basis | PR #1707 | required before closeout | PR metadata and hosted checks | Required after PR exists. |
| host state | issue #1692 | required | host mirror | Recheck after PR merge and issue closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1-S4 controlled merge closeout behavior | WI-1692 / branch `work/1692-controlled-merge-closeout-run` / head `f60c6b9ae58c0290fb18c0c1f71f66aa7be5c618` | present | review / merge-ready / closeout | Re-run merge-wrapper after `handle_merge` or closeout policy changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1-A5 wrapper contract | WI-1692 / root CLI wrapper / head `f60c6b9ae58c0290fb18c0c1f71f66aa7be5c618` | present | review / merge-ready / closeout | Re-run merge-wrapper and adjacent wrapper surfaces. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1692.md` | EV-001 EV-002 | current branch / current head / PR #1707 | present | merge-ready / closeout | Refresh after implementation, test, carrier, review, or PR metadata changes. |
| EV-004 | behavior_evidence | `.loom/specs/WI-1692/implementation-contract.md` | runtime, closeout policy, failure, and boundary contracts | WI-1692 / implementation review | present | review / merge-ready | Refresh if controlled merge or closeout boundary changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| README/skills convergence | deferred | User-facing documentation should consume the final ship path after this transition lands. | planning only | Start #1694 after #1692 merges. | #1694 |
| release publication | N/A | #1692 does not publish a release by itself. | closeout / release planning | Recheck if package or version metadata changes. | #1696 |
