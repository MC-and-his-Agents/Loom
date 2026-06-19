# WI-1600 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1600.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1594`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1600`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1604`
- Scope: dependency parser source semantics and provenance.
- Suite path: minimal
- Current `HEAD`: refreshed by validation summary before merge-ready.
- Host state locator: PR #1604 readback and hosted Actions runs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1600/spec.md` | required | authored suite | Recheck when dependency source semantics change. |
| `plan.md` | `.loom/specs/WI-1600/plan.md` | required | authored suite | Recheck when validation strategy changes. |
| suite path decision | `.loom/specs/WI-1600/spec.md#suite-path` | required | authored suite | Recheck if scope expands beyond the minimal dependency parser slice. |
| execution breakdown / task carrier | `.loom/specs/WI-1600/task-carrier.md` | required | authored task carrier | Recheck before merge-ready and milestone closeout. |
| review record | `.loom/reviews/WI-1600.json` | required | authored review truth | Required after implementation/carriers are stable. |
| merge-ready basis | PR #1604 metadata/readback/gate evidence | required | PR and gate truth | Required before merge-ready or merge. |
| host state | PR #1604 / Actions checks | required | GitHub readback | Recheck after each push or PR body update. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1600/spec.md` A1 A2 A3 A4 | Work Item WI-1600, branch `work/1600-native-dependency-only`, PR #1604 | present | review / merge-ready / #1598 convergence / #1596 release closeout | Re-run dependency parser fixtures after dependency source behavior changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py --surface governance-closeout`; `python3 tools/skills_surface.py check`; `make loom-demo-new-project-check` | `.loom/specs/WI-1600/plan.md` validation and test strategy | Work Item WI-1600 validation summary and current PR head | present | local checks / hosted checks / milestone closeout | Re-run targeted checks after parser, generated surface, docs, or fixture changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1600.md` | EV-001 EV-002 | head / reviewed head / PR head / PR #1604 metadata readback / validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR body update, or hosted check result changes. |
