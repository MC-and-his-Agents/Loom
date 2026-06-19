# WI-1318 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1318.md`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1318`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1602`
- Scope: docs-only AGENTS classify-before-execute governance principle.
- Suite decision: recorded in `.loom/specs/WI-1318/spec.md`.
- Host state locator: PR #1602 readback and hosted Actions runs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| suite path decision | `.loom/specs/WI-1318/spec.md#suite-path-decision` | required | authored suite decision | Recheck if scope expands beyond AGENTS/docs evidence/carriers. |
| docs validation evidence | `docs/evidence/validations/validation-agents-classify-before-execute.md` | required | authored docs review evidence | Recheck after AGENTS wording changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1318/task-carrier.md` | required | authored task carrier | Recheck before merge-ready and milestone closeout. |
| review record | `.loom/reviews/WI-1318.json` | required | authored review truth | Required after docs and carriers are stable. |
| merge-ready basis | PR #1602 metadata/readback/gate evidence | required | PR and gate truth | Required before merge-ready or merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `AGENTS.md` | `.loom/specs/WI-1318/spec.md` scope proof | Work Item WI-1318, branch `work/1318-agents-classify-first`, PR #1602 | present | review / merge-ready / milestone closeout | Re-read AGENTS rule if wording changes. |
| EV-002 | test_evidence | `docs/evidence/validations/validation-agents-classify-before-execute.md`; `git diff --check`; `python3 tools/loom.py workspace audit --target . --json` | docs validation and suite decision | Work Item WI-1318 validation summary and current PR head | present | local checks / hosted checks / milestone closeout | Re-run docs validation checks after AGENTS or carrier changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1318.md` | EV-001 EV-002 | head / reviewed head / PR head / PR #1602 metadata readback / validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR body update, or hosted check result changes. |
