# WI-1601 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1601.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1594`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1601`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1606`
- Scope: release readback, release resume classification, fixtures, and release surface docs.
- Suite path: minimal
- Current `HEAD`: refreshed by validation summary before merge-ready.
- Host state locator: PR #1606 readback and hosted Actions runs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1601/spec.md` | required | authored suite | Recheck when release readback/resume behavior changes. |
| `plan.md` | `.loom/specs/WI-1601/plan.md` | required | authored suite | Recheck when validation strategy changes. |
| suite path decision | `.loom/specs/WI-1601/spec.md#suite-path` | required | authored suite | Recheck if scope expands beyond the minimal release readback/resume slice. |
| execution breakdown / task carrier | `.loom/specs/WI-1601/task-carrier.md` | required | authored task carrier | Recheck before merge-ready and milestone closeout. |
| review record | `.loom/reviews/WI-1601.json` | required | authored review truth | Required after implementation/carriers are stable. |
| merge-ready basis | PR #1606 metadata/readback/gate evidence | required | PR and gate truth | Required before merge-ready or merge. |
| host state | PR #1606 / Actions checks | required | GitHub readback | Recheck after each push or PR body update. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `docs/adoption/loom-cli-release-surface.md` | `.loom/specs/WI-1601/spec.md` A1 A2 A3 A4 | Work Item WI-1601, branch `work/1601-release-resume`, PR #1606 | present | review / merge-ready / #1598 convergence / #1596 release closeout | Re-run release readback checks after release state or resume behavior changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py --surface release-readback`; `tools/check_release_surface.py --surface release-doc-contract`; `docs/evidence/fixtures/release-readback-fixtures.json` | `.loom/specs/WI-1601/plan.md` validation and test strategy | Work Item WI-1601 validation summary and current PR head | present | local checks / hosted checks / milestone closeout | Re-run targeted checks after release fixtures, CLI output, or docs surface changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1601.md` | EV-001 EV-002 | head / reviewed head / PR head / PR #1606 metadata readback / validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR body update, or hosted check result changes. |
