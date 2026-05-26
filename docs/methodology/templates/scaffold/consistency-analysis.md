# Consistency Analysis

## Analysis Context

- Schema version: `loom-consistency-analysis/v1`
- Work Item locator:
- Scope:
- Current `HEAD`:
- PR locator, or `not_applicable` rationale:
- Suite path:
- Evidence-map locator:
- Analysis time:

## Input Snapshot

| Input | Locator | Status | Binding | Freshness |
| --- | --- | --- | --- | --- |
| Work Item / FR |  | required | item / scope / branch |  |
| `spec.md` |  | required | scenario / acceptance ids |  |
| `plan.md` |  | required | validation / test strategy ids |  |
| suite path decision |  | candidate / optional / not_applicable | #1016 boundary |  |
| execution breakdown / task carrier |  | candidate / optional / deferred / not_applicable | #1017 boundary |  |
| evidence-map |  | required | evidence rows |  |
| review record |  | optional / required / not_applicable | reviewed head / validation summary |  |
| host state |  | required / not_applicable | issue / PR / Project / checks |  |

## Summary

- Result: `pass` / `block` / `advisory` / `not_applicable`
- Blocking gap count:
- Advisory gap count:
- Not applicable count:
- Remediation summary:

## Findings

| Id | Classification | Gap kind | Surface | Source locator | Freshness | Consumer impact | Remediation direction | Fallback to |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CA-001 | blocking / advisory / stale / missing / conflict / not_applicable |  | spec / plan / evidence_map / review / merge_ready / closeout / host_state / status_surface |  | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status / #1019_gate_chain |  |  |

## Blocking Consistency Gaps

| Gap kind | Present | Source locator | Blocking surface | Remediation direction |
| --- | --- | --- | --- | --- |
| missing_scenario_mapping | yes / no / not_applicable |  | review / merge-ready |  |
| missing_acceptance_test_mapping | yes / no / not_applicable |  | review / merge-ready |  |
| stale_evidence | yes / no / not_applicable |  | review / merge-ready / closeout |  |
| missing_fresh_verification_evidence | yes / no / not_applicable |  | merge-ready / closeout |  |
| head_or_pr_drift | yes / no / not_applicable |  | merge-ready / closeout |  |
| host_state_conflict | yes / no / not_applicable |  | merge-ready / closeout |  |
| deferred_as_completed | yes / no / not_applicable |  | review / merge-ready / closeout |  |
| missing_source_locator | yes / no / not_applicable |  | review / merge-ready / status |  |
| parallel_truth | yes / no / not_applicable |  | review / merge-ready / closeout |  |
| candidate_input_treated_as_required | yes / no / not_applicable |  | review / merge-ready |  |

## Consumer Boundary

- Review:
- Merge-ready:
- Closeout:
- Status surface:
- #1019 gate-chain follow-up:
- #1020 skills / generated surface follow-up:

