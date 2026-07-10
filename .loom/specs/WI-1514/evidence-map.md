# WI-1514 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1514.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1505
- Scope: #1514 gate freeze docs, skills, and fixture inventory convergence only.
- Suite path: not_applicable for formal-suite artifacts.
- Rationale: WI-1514 is a docs/skills/evidence inventory convergence slice and does not change executable runtime behavior.
- Consumer boundary: This not_applicable decision applies only to formal suite artifacts; review, PR metadata, hosted checks, shadow freshness, and closeout evidence remain required.
- Recheck condition: Recheck if #1514 starts changing runtime behavior, gate semantics, classifier vocabulary, hosted admission inputs, or PR metadata contracts.
- Current head binding: PR #1574 machine carrier and .loom/progress/WI-1514.md record the consumed head.
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1574
- Host state locator: GitHub issue #1514 and PR #1574 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1514/spec.md | required | authored Work Item carrier | Recheck when gate freeze docs/skills scope changes. |
| `plan.md` | .loom/specs/WI-1514/plan.md | required | authored Work Item carrier | Recheck when validation strategy or consumed commands change. |
| suite path decision | .loom/specs/WI-1514/spec.md | not_applicable | suite inspect | Recheck if #1514 starts changing executable runtime behavior. |
| execution breakdown / task carrier | .loom/specs/WI-1514/task-carrier.md | required | authored task carrier | Recheck before review, merge-ready, hosted gate, and closeout consumption. |
| review record | .loom/reviews/WI-1514.json | required | authored review truth | Rebind only if non-carrier implementation files change after review. |
| merge-ready basis | .loom/progress/WI-1514.md | required | merge checkpoint truth | Recheck after PR body, review, status, shadow, or head changes. |
| host state | PR #1574 / issue #1514 | required | GitHub readback | Recheck after PR body updates, pushes, merges, or issue state changes. |
| not_applicable suite-level artifacts | .loom/specs/WI-1514/spec.md | not_applicable | Rationale: docs/skills/evidence inventory only; Consumer boundary: no runtime behavior, hosted gate semantics, or closeout terminal behavior; Recheck condition: recheck when those boundaries change. | Recheck before review, hosted gate, merge-ready, or closeout consumption. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `skills/loom-pre-review/SKILL.md`; `skills/loom-review/SKILL.md`; `skills/loom-merge-ready/SKILL.md` | .loom/specs/WI-1514/spec.md acceptance | Gate freeze repair and freeze input consumption guidance | present | pre-review, review, merge-ready skills | Re-run generated surface check and targeted text readback after skill wording changes. |
| EV-002 | behavior_evidence | `docs/methodology/harness/cli-command-matrix.md`; `docs/evidence/regression-surface-inventory.md` | .loom/specs/WI-1514/spec.md acceptance | CLI troubleshooting and regression inventory boundary | present | docs, skills, hosted gate consumers | Recheck if wrapper/runtime command surface, classifier vocabulary, or hosted admission inputs change. |
| EV-003 | test_evidence | `tools/skills_surface.py check --surface generated-tree-drift`; `git diff --check`; `python3 tools/loom.py pr metadata-readback ...`; `python3 tools/loom.py pr gate ...` | .loom/specs/WI-1514/plan.md validation | PR #1574 current head and WI-1514 carriers | present | review, merge-ready, hosted checks | Re-run after head, PR body, review, carrier, generated skill, or shadow input changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1514.md | EV-001; EV-002; EV-003 | Latest validation summary for PR #1574 | present | hosted gate, merge-ready, closeout | Refresh progress and PR metadata before hosted recheck. |

## Scope Exclusions / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Formal full suite | not_applicable | WI-1514 is docs/skills/evidence inventory convergence and does not change runtime behavior. | This skips formal suite artifacts only; it does not skip review, PR metadata, hosted checks, or closeout evidence. | Recheck if #1514 starts changing executable gate behavior. | .loom/specs/WI-1514/spec.md |
| Closeout terminal behavior | not_applicable | Closeout terminal profile and one-shot closeout run are owned by #1532/#1533/#1534/#1555. | WI-1514 may document gate freeze consumption only. | Recheck after #1533/#1555 if docs need convergence wording. | #1534 |
