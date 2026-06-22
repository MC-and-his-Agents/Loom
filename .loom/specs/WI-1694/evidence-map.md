# WI-1694 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1694.md`
- FR / parent locator: issue #1693
- Scope: README, skills, generated payload, and fixture convergence to `loom ship` as ordinary delivery path.
- Suite path: minimal
- Current `HEAD`: update before merge-ready consumption.
- PR locator, or N/A rationale: fill when PR exists.
- Host state locator, or N/A rationale: issue #1694

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1694/spec.md` | required | authored for issue #1694 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1694/plan.md` | required | authored for issue #1694 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1694/spec.md` | minimal | authored suite contract | Recheck before review and merge-ready. |
| execution breakdown / task carrier | `.loom/specs/WI-1694/task-carrier.md` | required | authored task carrier | Recheck before review and closeout. |
| review record | `.loom/reviews/WI-1694.json` | required before merge-ready | authored review truth | Required after review consumption. |
| merge-ready basis | PR merge-ready attempt artifact | required before closeout | merge-ready truth | Required after PR exists. |
| host state | issue #1694 | required | host mirror | Recheck after PR creation and merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `README.md`, `README.zh-CN.md` | S1 README ordinary delivery path | WI-1694 / branch `work/1694-ship-entry-convergence` | present | review / PR gate / merge-ready / closeout | Re-read README parity after delivery wording changes. |
| EV-002 | behavior_evidence | `src/skills/README.md`, `src/skills/README.zh-CN.md`, `src/skills/route-matrix.md`, `src/skills/loom-merge-ready/SKILL.md`, `src/skills/loom-retire/SKILL.md` | S2 skills route and cleanup boundary | WI-1694 / source skills | present | review / generated surface / release #1696 | Re-run skills generation and skills surface check after source skill changes. |
| EV-003 | behavior_evidence | `skills/`, `plugins/loom/skills/` | generated skills and plugin payload parity | WI-1694 / generated payload | present | review / release #1696 | Re-run `tools/skills_surface.py generate` and `tools/skills_surface.py check`. |
| EV-004 | test_evidence | `tools/check_cli_contract.py` | S3 ship docs entry drift guard; A1-A5 | WI-1694 / ship-wrapper fixture | present | review / PR gate / merge-ready | Re-run `tools/check_cli_contract.py --fixture-group ship-wrapper`. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1694.md` | EV-001 EV-004 | current branch / current head before PR | present | review / merge-ready / closeout | Refresh after any README, skills, fixture, or carrier change. |
| EV-006 | build_evidence | `.loom/progress/WI-1694-build-evidence.json` | integrated README, skills, fixture, subagent inventory, ownership, and validation evidence | WI-1694 / build checkpoint | present | build / review / merge-ready | Regenerate through loom-build after implementation, validation, review findings, or ownership changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| release publication | deferred | Release and milestone closeout are owned by #1696. | planning only | Start #1696 after #1694 merges. | #1696 |
| runtime `loom ship` behavior | N/A | Runtime behavior was implemented by #1690/#1691/#1692; WI-1694 only changes docs, skills, generated payload, and fixture drift guard. | review / PR gate | Recheck if ship-wrapper or merge-wrapper fails. | #1690, #1691, #1692 |
