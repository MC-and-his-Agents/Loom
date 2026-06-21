# WI-1658 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1658.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1480
- Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1476
- Scope: v0.17.1 release preparation, publish readback, and #1658 closeout for the context-safe runtime line.
- Suite path: minimal
- Current `HEAD`: release PR head `e09d502e5a9509c0e9de06f302a83dd9c362c871`; post-merge target commit `3e17dd73fb4ccb260ede68e5518b83aa904fb682`.
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1671.
- Host state locator: issue #1658.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1658/spec.md | required | authored WI-1658 suite | Recheck when #1658 scope or release acceptance changes. |
| `plan.md` | .loom/specs/WI-1658/plan.md | required | authored WI-1658 suite | Recheck when validation strategy changes. |
| suite path decision | .loom/specs/WI-1658/spec.md#suite-contract | minimal | authored WI-1658 suite | Recheck if release-prep scope expands. |
| implementation contract | .loom/specs/WI-1658/implementation-contract.md | required | PR gate / review readiness input | Recheck after version, package, plugin payload, output-envelope, or release-evidence changes. |
| execution breakdown / task carrier | .loom/specs/WI-1658/task-carrier.md | required | authored WI-1658 suite | Recheck issue state and branch/PR binding before review. |
| review record | .loom/reviews/WI-1658.json | required after review | authored review truth | Required before merge-ready; must bind the reviewed implementation head. |
| release readiness | docs/evidence/v0.17.1-release-readiness.md | required | release evidence | Recheck after validation, PR, merge, workflow, tag, GitHub Release, npm readback, or #1489 consumption changes. |
| goal completion evidence | .loom/progress/WI-1658-goal-completion.json | required | closeout evidence | Recheck after release readback, issue closeout, or terminal carrier sync changes. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1658 | required | GitHub issue | Recheck before #1489 consumes WI-1658 terminal evidence. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/v0.17.1-release-readiness.md | S1-S4 and A1-A6 release behavior expectations | WI-1658 / PR #1671 / merge commit 3e17dd73fb4ccb260ede68e5518b83aa904fb682 / v0.17.1 support boundary | present | review / PR gate / merge-ready / closeout / #1489 | Reinspect release readiness and support-boundary notes after version, package, plugin, output, PR, release evidence, or #1489 consumption changes. |
| EV-002 | test_evidence | .loom/progress/WI-1658.md | release readback, closeout run, carrier refresh, and final closeout check | WI-1658 / closed_out progress carrier / PR #1671 / issue #1658 closed | present | closeout / #1489 | Rerun closeout validation and update progress after any release evidence, carrier, or host closeout drift. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1658-goal-completion.json | EV-001 EV-002 terminal release and closeout binding | work_item=WI-1658; release=v0.17.1; merge_commit=3e17dd73fb4ccb260ede68e5518b83aa904fb682; issue=1658 closed | present | closeout / #1489 / status | Rebuild goal completion evidence after release readback, issue state, PR merge commit, or terminal carrier metadata changes. |
| EV-004 | release_candidate_evidence | VERSION | S1 / A1-A2 | WI-1658 / v0.17.1 release candidate | present | review / release workflow | If occupied or mismatched, bump to a new unpublished version before merge. |
| EV-005 | package_plugin_evidence | package.json | S3 / A4 | WI-1658 / @mc-and-his-agents/loom@0.17.1 / Codex user-level plugin payload | present | review / release workflow / post-release smoke | Fix manifest/files payload before merge if global CLI or plugin payload is missing. |

## Deferred Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Final milestone regression | deferred | #1658 publishes the release; #1489 owns final regression and milestone issue closeout. | #1489 | Activate after v0.17.1 release evidence exists and #1658 is closed. | https://github.com/MC-and-his-Agents/Loom/issues/1489 |
| Downstream migration | deferred | #1658 publishes support boundary only; downstream repositories are not completion criteria. | adoption consumers | Activate only under separate downstream Work Items. | https://github.com/MC-and-his-Agents/Loom/issues/1496 |
