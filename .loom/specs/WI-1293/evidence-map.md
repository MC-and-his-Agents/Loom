# WI-1293 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1293.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1285`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1293`
- Scope: v0.16.0 release/docs closeout for milestone 9.
- Suite path: minimal

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `README.md` | `.loom/specs/WI-1293/spec.md` A1 A2 | Work Item WI-1293, branch `work/1293-v0.16-release`; paired surfaces: `README.zh-CN.md`, `docs/adoption/github-profile.md`, `docs/methodology/harness/cli-command-matrix.md`, `tools/loom.py help --json` | present | review / merge-ready / release closeout | Refresh after documentation, CLI command matrix, or merge command behavior changes. |
| EV-002 | behavior_evidence | `docs/evidence/v0.16.0-release-readiness.md` | `.loom/specs/WI-1293/spec.md` A3 A4 A5 | Work Item WI-1293, branch `work/1293-v0.16-release`, target `v0.16.0` | present | review / merge-ready / release workflow / closeout | Refresh after version, release workflow, package payload, release artifact, or milestone issue truth changes. |
| EV-003 | test_evidence | `docs/evidence/v0.16.0-release-readiness.md` | `.loom/specs/WI-1293/spec.md` A1 A2 A3 A4 A5 | current release PR head validation summary | present | local checks / hosted checks / release workflow / closeout | Rerun after any version, package, generated skill metadata, workflow, documentation, CLI help, or carrier change. |
| EV-004 | predecessor_evidence | `.loom/progress/WI-1292.md` | `.loom/specs/WI-1293/spec.md` A4 | completed #1452 triggered-check behavior and #1292 cross-repo fixture closeout consumed by v0.16.0 release readiness | present | release docs / release evidence / parent closeout | Recheck if #1452 or #1292 closeout facts drift. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1293.md` | EV-001 EV-002 EV-003 EV-004 | current WI-1293 branch and validation inputs for release PR review | present | review / PR gate / merge-ready / closeout | Refresh after any PR body, carrier, version, package, release evidence, or hosted check drift. |
