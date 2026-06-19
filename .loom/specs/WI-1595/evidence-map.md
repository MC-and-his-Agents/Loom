# WI-1595 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1595.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1594`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1595`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1603`
- Scope: PR metadata dry-run default and actionable preflight diagnostics.
- Suite path: minimal
- Current `HEAD`: refreshed by validation summary before merge-ready.
- Host state locator: PR #1603 readback and hosted Actions runs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1595/spec.md` | required | authored suite | Recheck when PR metadata update/preflight behavior changes. |
| `plan.md` | `.loom/specs/WI-1595/plan.md` | required | authored suite | Recheck when validation strategy changes. |
| suite path decision | `.loom/specs/WI-1595/spec.md#suite-path` | required | authored suite | Recheck if scope expands beyond the minimal PR metadata slice. |
| execution breakdown / task carrier | `.loom/specs/WI-1595/task-carrier.md` | required | authored task carrier | Recheck before merge-ready and milestone closeout. |
| review record | `.loom/reviews/WI-1595.json` | required | authored review truth | Required after implementation/carriers are stable. |
| merge-ready basis | PR #1603 metadata/readback/gate evidence | required | PR and gate truth | Required before merge-ready or merge. |
| host state | PR #1603 / Actions checks | required | GitHub readback | Recheck after each push or PR body update. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1595/spec.md` A1 A2 A3 | Work Item WI-1595, branch `work/1595-pr-metadata-preflight`, PR #1603 | present | review / merge-ready / #1598 convergence | Re-run PR metadata contract and PR body readback after metadata behavior changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py --surface pr-metadata`; `make loom-demo-new-project-check`; `python3 tools/skills_surface.py check` | `.loom/specs/WI-1595/plan.md` validation and test strategy | Work Item WI-1595 validation summary and current PR head | present | local checks / hosted checks / milestone closeout | Re-run targeted checks after runtime, generated surface, or fixture changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1595.md` | EV-001 EV-002 | head / reviewed head / PR head / PR #1603 metadata readback / validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR body update, or hosted check result changes. |
