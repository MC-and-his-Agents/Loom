# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1452.md
- FR / parent locator: GitHub issue #1452; parent #1285
- Scope: controlled-merge triggered-check rollup runtime/docs/fixture behavior only
- Suite path: minimal
- Current `HEAD`: 07bb4651cc662c008e2855f877fa6ee7844cc931 plus carrier-only sync
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1614
- Host state locator: GitHub issue #1452 and PR #1614

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1452/spec.md | required | authored minimal suite | Recheck when #1452 behavior scope changes. |
| `plan.md` | .loom/specs/WI-1452/plan.md | required | authored minimal suite | Recheck when validation strategy changes. |
| suite path decision | .loom/specs/WI-1452/spec.md | minimal | suite inspect | Recheck when suite path changes. |
| execution breakdown / task carrier | .loom/specs/WI-1452/task-carrier.md | required | authored task carrier | Recheck before merge-ready or closeout. |
| review record | .loom/reviews/WI-1452.json | required | authored review truth | Required before merge-ready. |
| merge-ready basis | PR #1614 hosted checks and controlled merge check | required | GitHub + Loom controlled merge | Required before merge. |
| host state | GitHub issue #1452; PR #1614 | required | GitHub readback | Recheck issue/PR/head before closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge` | .loom/specs/WI-1452/spec.md S1/S2/S3 and A1-A5 | WI-1452 / PR #1614 / head 07bb4651cc662c008e2855f877fa6ee7844cc931 | present | review / merge-ready / closeout / status | Rerun targeted surfaces if controlled-merge check semantics change. |
| EV-002 | test_evidence | `python3 -m py_compile src/skills/shared/scripts/loom_flow.py tools/check_cli_contract.py examples/new-project/.loom/bin/loom_flow.py`; `python3 tools/skills_surface.py check --surface generated-tree-drift`; `make loom-demo-new-project-check`; `git diff --check` | .loom/specs/WI-1452/plan.md validation / test strategy locator | WI-1452 / PR #1614 / head 07bb4651cc662c008e2855f877fa6ee7844cc931 | present | review / merge-ready / closeout / status | Rerun before merge if code or generated/demo surfaces change. |
| EV-003 | fresh_verification_input | PR #1614 metadata-update/readback for WI-1452 at head 07bb4651cc662c008e2855f877fa6ee7844cc931 | EV-001 EV-002 | head / reviewed head / PR head / validation summary | present | merge-ready / closeout / status | Re-read PR body and hosted checks after each push. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Cross-repo review-gate fixture closeout | deferred | Consumed by #1292 after #1452 lands. | #1452 review and merge-ready do not require #1292 completion. | Start #1292 after #1452 closeout. | GitHub issue #1292 |
| Release convergence | deferred | Consumed by #1293 after #1452 and #1292 land. | #1452 review and merge-ready do not require release publication. | Start #1293 after #1292 closeout. | GitHub issue #1293 |

## Follow-up Requirements

- #1292 consumes triggered-check behavior in HotCP/WebEnvoy/Syvert fixtures.
- #1293 consumes release/no-release evidence and publishes v0.16.0 after milestone scope closes.
