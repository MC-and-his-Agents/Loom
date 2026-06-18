# WI-1533 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1533.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1505
- Issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1533
- Branch locator: work/1533-closeout-specific-gate
- Scope: closeout-specific gate verdict/escalation fields over existing closeout freeze and PR gate behavior.
- Suite path: minimal
- Base head: f964a3d15abe21bf04f36a1005f15f1948861068
- PR locator: pending
- Host state locator: GitHub issue #1533

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1533/spec.md | required | authored Work Item carrier | Recheck when closeout gate verdict fields or scope change. |
| `plan.md` | .loom/specs/WI-1533/plan.md | required | authored Work Item carrier | Recheck when validation strategy or generated runtime copy set changes. |
| `implementation-contract.md` | .loom/specs/WI-1533/implementation-contract.md | required | authored implementation contract | Recheck when closeout-specific gate fields, consumer boundary, or validation binding changes. |
| suite path decision | .loom/specs/WI-1533/spec.md | minimal | suite scaffold + authored rationale | Recheck if scope expands beyond bounded runtime/fixture contract. |
| task carrier | .loom/specs/WI-1533/task-carrier.md | required | authored task carrier | Recheck before review, PR gate, hosted checks, and closeout consumption. |
| spec review record | .loom/reviews/WI-1533.spec.json | present | authored spec review truth | Required before implementation review consumption. |
| review record | .loom/reviews/WI-1533.json | pending | authored review truth | Required after review consumption. |
| host state | issue #1533 / future PR | required | GitHub readback | Recheck after PR creation, PR body updates, pushes, or issue state changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | .loom/specs/WI-1533/spec.md S1 S2 S3 S4 | `loom-closeout-specific-gate/v1` verdict helper and closeout freeze / PR gate projection | present | review, PR gate, hosted checks, #1534 docs/skills, #1515 closeout | Re-run targeted closeout/pr-gate fixtures after runtime changes. |
| EV-002 | parity_evidence | `skills/shared/scripts/loom_flow.py` | EV-001 | source, shared, and generated runtime copy consistency validated by `tools/skills_surface.py check --surface generated-tree-drift` | present | installed/runtime and generated skills consumers | Re-run generated-tree drift and py_compile after source runtime changes. |
| EV-003 | test_evidence | `tools/check_cli_contract.py` | .loom/specs/WI-1533/spec.md S1 S2 S3 | contract fixtures assert pass verdict, release evidence escalation, and terminal closeout PR gate verdict | present | local targeted validation and hosted checks | Extend fixture if verdict schema, next action, or escalation fields change. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1533.md` | EV-001; EV-002; EV-003 | branch work/1533-closeout-specific-gate targeted validation at current PR head | present | review, merge-ready, PR gate, hosted checks, milestone closeout | Refresh after review, PR metadata readback, hosted checks, or further code changes. |

## Non-Goals / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Docs/skills convergence | deferred | #1534 owns prose, skills protocol, and aggregate fixture convergence after #1533 fields stabilize. | WI-1533 only exposes stable runtime fields. | Activate when #1533 is merged and #1534 starts. | #1534 |
| Release/no-release final closeout | deferred | #1515 owns final release/no-release judgment and milestone closeout readback. | WI-1533 leaves `release_no_release_final_closeout` pending. | Activate after #1534 and all M12 blockers close. | #1515 |
