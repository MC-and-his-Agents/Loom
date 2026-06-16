# Consistency Analysis

## Analysis Context

- Schema version: `loom-consistency-analysis/v1`
- Work Item locator: .loom/work-items/WI-1235.md
- Scope: #1235 safe repair/sync flow only.
- Current `HEAD`: branch `work/1235-safe-repair-sync`; exact PR head pending until commit/push.
- PR locator, or `not required` rationale: PR creation pending; this file is pre-PR local consistency analysis.
- Suite path: full
- Evidence-map locator: .loom/specs/WI-1235/evidence-map.md
- Analysis time: 2026-06-16T06:16:00Z

## Input Snapshot

| Input | Locator | Status | Binding | Freshness |
| --- | --- | --- | --- | --- |
| Work Item / FR | .loom/work-items/WI-1235.md; GitHub issue #1235 | required | item / scope / branch | present |
| `spec.md` | .loom/specs/WI-1235/spec.md | required | scenario / acceptance ids | present |
| `plan.md` | .loom/specs/WI-1235/plan.md | required | validation / test strategy ids | present |
| suite path decision | .loom/specs/WI-1235/suite-index.md | required | full suite boundary | present |
| execution breakdown / task carrier | .loom/specs/WI-1235/execution-breakdown.md; .loom/specs/WI-1235/task-carrier.md | required | local unit and host tracker | present |
| evidence-map | .loom/specs/WI-1235/evidence-map.md | required | evidence rows | present |
| review record | .loom/reviews/WI-1235.json | required before merge-ready | reviewed head / validation summary | pending until commit head stabilizes |
| host state | GitHub issue #1235; PR pending | required before closeout | issue / PR / checks | pending PR creation |

## Summary

- Result: pass
- Blocking gap count: 0 for local implementation consistency.
- Advisory gap count: 0 for suite artifact completeness.
- Not required count: 0.
- Remediation summary: create PR, refresh exact-head review, run hosted checks/merge-ready, then perform post-merge issue/PR/carrier closeout readback.

## Findings

| Id | Classification | Gap kind | Surface | Source locator | Freshness | Consumer impact | Remediation direction | Fallback to |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CA-001 | advisory | host_pr_pending | host_state | GitHub issue #1235 | pending | merge-ready / closeout | Create PR and refresh evidence before merge-ready. | `gh pr create` |

## Blocking Consistency Gaps

| Gap kind | Present | Source locator | Blocking surface | Remediation direction |
| --- | --- | --- | --- | --- |
| missing_scenario_mapping | no | .loom/specs/WI-1235/spec.md; .loom/specs/WI-1235/plan.md | review / merge-ready | none |
| missing_acceptance_test_mapping | no | .loom/specs/WI-1235/plan.md | review / merge-ready | none |
| stale_evidence | no | .loom/specs/WI-1235/evidence-map.md | review / merge-ready / closeout | rerun checks after head changes |
| missing_fresh_verification_evidence | no | .loom/progress/WI-1235.md | merge-ready / closeout | rerun checks after head changes |
| head_or_pr_drift | no | branch `work/1235-safe-repair-sync` | merge-ready / closeout | read back PR head after push |
| host_state_conflict | no | GitHub issue #1235 | merge-ready / closeout | read back issue/PR before merge |
| deferred_as_completed | no | .loom/specs/WI-1235/evidence-map.md | review / merge-ready / closeout | keep #1236/#1237/#1296 deferred |
| missing_source_locator | no | .loom/specs/WI-1235/evidence-map.md | review / merge-ready / status | none |
| parallel_truth | no | .loom/status/current.md; .loom/bootstrap/init-result.json | review / merge-ready / closeout | run fact-chain after carrier changes |
| candidate_input_treated_as_required | no | .loom/specs/WI-1235/suite-index.md | review / merge-ready | none |

## Consumer Boundary

- Review: consume spec, plan, evidence-map, task-carrier, and review record for current head.
- Merge-ready: require exact PR head/body, hosted checks, review record, and current carrier/shadow hashes.
- Closeout: require PR merge commit, target branch readback, issue CLOSED/COMPLETED, and carrier terminal sync.
- Status surface: reflects current WI-1235 pre-merge state only.
- #1019 gate-chain follow-up: none in #1235.
- #1020 skills / generated surface follow-up: generated runtime copies are included in this PR.

