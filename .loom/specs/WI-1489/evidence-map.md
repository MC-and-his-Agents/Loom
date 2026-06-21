# WI-1489 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1489.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1480
- Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1476
- Scope: final regression and closeout verification for milestone/11.
- Suite path: minimal
- Current `HEAD`: pending PR head readback.
- PR locator: pending.
- Host state locator: issue #1489.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1489/spec.md | required | authored WI-1489 suite | Recheck when #1489 scope or parent closeout changes. |
| `plan.md` | .loom/specs/WI-1489/plan.md | required | authored WI-1489 suite | Recheck when validation strategy changes. |
| task carrier | .loom/specs/WI-1489/task-carrier.md | required | authored WI-1489 suite | Recheck issue, PR, and parent/phase state before closeout. |
| final closeout evidence | docs/evidence/milestone-11-final-closeout.md | required | regression evidence | Recheck after any regression command, release readback, dependency edge, or issue state changes. |
| WI-1658 release evidence | docs/evidence/v0.17.1-release-readiness.md; .loom/progress/WI-1658-goal-completion.json | required | release evidence | Recheck before closing #1489. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/milestone-11-final-closeout.md | S1-S4 and A1-A6 final closeout expectations | WI-1489 / milestone-11 / final-regression | present | review / PR gate / #1489 / #1480 / #1476 | Reinspect after any milestone issue state, release evidence, or regression command changes. |
| EV-002 | test_evidence | .loom/progress/WI-1489.md | final regression command summary | WI-1489 / current branch validation summary | present | review / PR gate / closeout | Rerun after any closeout evidence, CLI contract, suite, or carrier changes. |
| EV-003 | release_evidence | docs/evidence/v0.17.1-release-readiness.md | #1658 published release and carrier closeout; supporting goal evidence at .loom/progress/WI-1658-goal-completion.json | release=v0.17.1; PR #1671; carrier sync #1672 | present | #1489 / #1480 / #1476 | Recheck release readback before issue closeout. |
| EV-004 | fresh_verification_input | docs/evidence/milestone-11-final-closeout.md | EV-001 behavior evidence plus EV-002 test evidence and EV-003 release evidence | WI-1489 / current branch verification set | present | review / PR gate / #1489 closeout | Rerun local regression and release readback after any evidence, suite, PR metadata, or issue-state change. |
