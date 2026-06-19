# WI-1596 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1596.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1594`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1596`
- Scope: v0.15.0 release closeout and milestone #13 parent closeout.
- Suite path: minimal

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `docs/evidence/v0.15.0-release-readiness.md` | `.loom/specs/WI-1596/spec.md` A1 A2 A3 A4 A5 | Work Item WI-1596, branch `work/1596-release-closeout`, target `v0.15.0` | present | review / merge-ready / release closeout | Refresh after version, release workflow, package payload, or milestone issue truth changes. |
| EV-002 | test_evidence | validation commands in `docs/evidence/v0.15.0-release-readiness.md` | `.loom/specs/WI-1596/spec.md` A1 A2 A3 A5 | current release PR head validation summary | present | local checks / hosted checks / release workflow / closeout | Rerun after any version, package, generated skill metadata, workflow, or carrier change. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1596.md` | EV-001 EV-002 | head / reviewed head / PR head / validation summary | present | merge-ready / release closeout / parent closeout | Refresh after final validation, review, PR body update, hosted checks, release workflow, or post-merge readback. |
