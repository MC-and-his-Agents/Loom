# WI-1124 Spec

- Suite path: minimal

## Goal

`loom suite validate` emits stable machine-readable failure taxonomy findings for every readiness gap it reports.

## Acceptance Criteria

- [ ] A1: Each emitted finding carries failure kind, default result, failed layer, source locator, binding, consumer impact, remediation direction, and fallback.
- [ ] A2: The payload exposes a `failure_taxonomy` list derived from emitted findings.
- [ ] A3: Passing suites remain compatible with existing readiness outputs and do not gain blocking gaps.
