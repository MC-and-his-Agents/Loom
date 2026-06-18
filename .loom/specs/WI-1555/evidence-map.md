# WI-1555 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1555.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1505
- Issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1555
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1585
- Scope: #1555 one-shot post-merge closeout run CLI/runtime orchestration only.
- Suite path: not_applicable for formal-suite artifacts.
- Rationale: WI-1555 wires existing reconciliation, closeout check, carrier closeout-sync, recovery writeback, and carrier refresh primitives behind one facade; it does not introduce new closeout risk policy, hosted gate semantics, release judgment, or batch behavior.
- Consumer boundary: This not_applicable decision applies only to the #1555 wrapper/runtime contract. Review, PR metadata, hosted checks, shadow freshness, and closeout evidence remain required.
- Recheck condition: Recheck if `closeout run` starts changing closeout risk policy, batch or mixed-risk behavior, release/no-release judgment, hosted gate semantics, or runtime primitive contracts beyond wrapper orchestration.
- Current head binding: PR #1585 machine carrier and .loom/progress/WI-1555.md record the consumed head.
- Host state locator: GitHub issue #1555 and PR #1585 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1555/spec.md | required | authored Work Item carrier | Recheck when closeout run command semantics or boundaries change. |
| `plan.md` | .loom/specs/WI-1555/plan.md | required | authored Work Item carrier | Recheck when validation strategy or consumed runtime primitives change. |
| suite path decision | .loom/specs/WI-1555/spec.md | not_applicable | suite inspect | Recheck if #1555 starts changing closeout policy, hosted gate semantics, release judgment, or batch behavior. |
| execution breakdown / task carrier | .loom/specs/WI-1555/task-carrier.md | required | authored task carrier | Recheck before review, merge-ready, hosted gate, and closeout consumption. |
| review record | .loom/reviews/WI-1555.json | required | authored review truth | Rebind when non-carrier implementation files change after review. |
| merge-ready basis | .loom/progress/WI-1555.md | required | merge checkpoint truth | Recheck after PR body, review, status, shadow, evidence map, task carrier, or head changes. |
| host state | PR #1585 / issue #1555 | required | GitHub readback | Recheck after PR body updates, pushes, merges, or issue state changes. |
| not_applicable suite-level artifacts | .loom/specs/WI-1555/spec.md | not_applicable | Rationale: narrow CLI/runtime orchestration only; Consumer boundary: no new closeout policy, hosted gate semantics, release judgment, or batch behavior; Recheck condition: require a full or minimal suite if those boundaries change. | Recheck before review, hosted gate, merge-ready, or closeout consumption. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | .loom/specs/WI-1555/spec.md acceptance | `closeout run` help surface, dry-run/apply dispatch, ordered step payload, terminal metadata, failure classifier, next action, and stop-before-later-mutation behavior | present | #1555 CLI facade only | Re-run py compile and closeout-wrapper contract checks after wrapper/runtime argument changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | .loom/specs/WI-1555/plan.md validation | Targeted `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper` fixture covers dry-run argument forwarding, apply success ordering, inferred terminal metadata, and blocked apply stop-before-carrier behavior | present | PR #1585 review, merge-ready, and hosted checks | Re-run after changes to `tools/loom.py`, closeout runtime arguments, terminal metadata fields, or failure classifiers. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1555.md | EV-001; EV-002 | Latest validation summary for PR #1585 and WI-1555 carriers | present | hosted gate, merge-ready, closeout | Refresh progress, review, shadow evidence, and PR metadata before hosted recheck when head changes. |
| EV-004 | carrier_evidence | .loom/reviews/WI-1555.json | EV-001; EV-002; EV-003 | Review record plus `.loom/shadow/closeout-loom.json` and `.loom/shadow/merge-ready-loom.json` carriers bind current WI-1555 merge-ready input | present | PR gate, hosted checks, and final #1555 closeout | Re-record review and refresh shadow after non-carrier implementation changes or merge-ready input drift. |

## Scope Exclusions / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Formal full suite | not_applicable | WI-1555 is a focused wrapper/runtime orchestration slice and does not define a new formal product behavior suite. | This skips formal suite artifacts only; it does not skip review, PR metadata, hosted checks, shadow freshness, or closeout evidence. | Recheck if #1555 starts changing closeout policy, hosted gate semantics, release judgment, batch behavior, or primitive contracts beyond orchestration. | .loom/specs/WI-1555/spec.md |
| Closeout freeze admission and gate policy | not_applicable | #1532 and #1533 own closeout freeze admission and closeout-specific gate semantics. | WI-1555 may call existing primitives but must not redefine their risk policy. | Recheck after #1532/#1533 if the facade must consume new stable fields. | #1532 / #1533 |
| Docs, skills, and release/no-release convergence | deferred | #1534 and #1515 own milestone/12 convergence and release/no-release closeout. | WI-1555 exposes a reusable entry for those consumers after merge. | Recheck when #1534/#1515 consume the new command. | #1534 / #1515 |
