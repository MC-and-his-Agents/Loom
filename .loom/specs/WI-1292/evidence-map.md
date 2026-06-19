# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1292.md
- Parent locator: GitHub issue #1285
- Dependency locator: GitHub issue #1452; PR #1614; PR #1637
- Scope: HotCP/WebEnvoy/Syvert review gate fixture coverage
- Suite path: minimal
- PR locator: pending

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1292/spec.md | required | authored minimal suite | Recheck when #1292 scope changes. |
| `plan.md` | .loom/specs/WI-1292/plan.md | required | authored minimal suite | Recheck when validation strategy changes. |
| #1452 closeout | GitHub issue #1452; PR #1614; PR #1637 | required | GitHub and Loom carrier readback | Recheck before merge-ready. |
| fixture implementation | tools/check_cli_contract.py | required | branch diff | Recheck after every implementation change. |
| fixture inventory | docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json | required | branch diff | Recheck after every inventory change. |
| review record | .loom/reviews/WI-1292.json | required | authored review truth | Required before merge-ready. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge` | S1-S4 and A1-A5 | WI-1292 / branch work/1292-review-gate-fixtures | present | review / merge-ready / closeout / status | Rerun if pr-gate or controlled-merge fixture behavior changes. |
| EV-002 | test_evidence | `python3 -m py_compile tools/check_cli_contract.py`; `python3 -m json.tool docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json >/dev/null`; `git diff --check` | implementation and inventory safety | WI-1292 / tools/check_cli_contract.py / fixture inventory | present | review / merge-ready / closeout / status | Rerun before PR update and merge. |
| EV-003 | dependency_evidence | #1452 CLOSED; PR #1614 merged; PR #1637 merged | #1452 triggered-check consumption | WI-1292 / #1452 dependency | present | review / merge-ready / closeout / status | Re-read if #1452 is reopened or carrier sync drifts. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1292.md | EV-001 EV-002 EV-003 | WI-1292 / latest validation summary / branch work/1292-review-gate-fixtures | present | review / merge-ready / closeout / status | Refresh progress summary after validation, PR creation/update, hosted checks readback, merge, or closeout. |

## Follow-up Requirements

- #1293 consumes this completed fixture coverage before v0.16.0 release.
- #1285 parent closeout waits until #1293 release and issue closeout are complete.
