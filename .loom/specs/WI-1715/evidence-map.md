# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1715.md
- FR / parent locator: issue #1711
- Scope: Report CLI and plugin payload freshness from existing CLI diagnostic surfaces.
- Suite path: minimal
- Current `HEAD`: b8e03633626955218d0fa97b5fe32b7edcac3b86 before WI-1715 commit
- PR locator: pending
- Host state locator: local Codex plugin readback through `loom version --json` and `loom host doctor --host codex --scope user --json`

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1715/spec.md | present | authored for issue #1715 | Recheck before PR metadata and merge-ready. |
| `plan.md` | .loom/specs/WI-1715/plan.md | present | authored for issue #1715 | Recheck after validation changes. |
| task carrier | .loom/specs/WI-1715/task-carrier.md | present | issue #1715 / branch work/1715-freshness-reporting | Recheck issue and PR state before closeout. |
| review record | .loom/reviews/WI-1715.json | pending | review truth | Required before merge-ready. |
| merge-ready basis | PR metadata / hosted checks | pending | merge-ready truth | Required before merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1 S2 S3 | WI-1715 / version_freshness | present | build / review / merge-ready / closeout | Re-run direct JSON checks after CLI output changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1 A2 A3 A4 A5 | WI-1715 / adoption-host-metadata surface | present | build / review / merge-ready | Re-run `python3 tools/check_cli_contract.py --surface adoption-host-metadata`. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1715.md` | EV-001 EV-002 | WI-1715 / latest validation summary | present | merge-ready / closeout / status | Refresh after final validation or head changes. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Release execution | deferred | WI-1715 is diagnostic reporting only. | #1718 release closeout | Version bump or release action enters scope. | #1718 |
| Plugin refresh apply UX | deferred | WI-1715 only reports actions. | #1716 stale refresh guidance | Refresh command behavior changes. | #1716 |
