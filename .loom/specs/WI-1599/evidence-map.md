# WI-1599 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1599.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1594`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1599`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1605`
- Scope: closeout PR role model, readback, and fixtures.
- Suite path: minimal
- Current `HEAD`: refreshed by validation summary before merge-ready.
- Host state locator: PR #1605 readback and hosted Actions runs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1599/spec.md` | required | authored suite | Recheck when closeout role model behavior changes. |
| `plan.md` | `.loom/specs/WI-1599/plan.md` | required | authored suite | Recheck when validation strategy changes. |
| suite path decision | `.loom/specs/WI-1599/spec.md#suite-path` | required | authored suite | Recheck if scope expands beyond the minimal closeout role slice. |
| execution breakdown / task carrier | `.loom/specs/WI-1599/task-carrier.md` | required | authored task carrier | Recheck before merge-ready and milestone closeout. |
| review record | `.loom/reviews/WI-1599.json` | required | authored review truth | Required after implementation/carriers are stable. |
| merge-ready basis | PR #1605 metadata/readback/gate evidence | required | PR and gate truth | Required before merge-ready or merge. |
| host state | PR #1605 / Actions checks | required | GitHub readback | Recheck after each push or PR body update. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1599/spec.md` A1 A2 A3 A4 | Work Item WI-1599, branch `work/1599-closeout-pr-roles`, PR #1605 | present | review / merge-ready / #1598 convergence / #1596 release closeout | Re-run closeout role contract checks after closeout role behavior changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py --surface governance-closeout`; `python3 tools/skills_surface.py check`; `make loom-demo-new-project-check` | `.loom/specs/WI-1599/plan.md` validation and test strategy | Work Item WI-1599 validation summary and current PR head | present | local checks / hosted checks / milestone closeout | Re-run targeted checks after runtime, generated surface, or fixture changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1599.md` | EV-001 EV-002 | head / reviewed head / PR head / PR #1605 metadata readback / validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR body update, or hosted check result changes. |
