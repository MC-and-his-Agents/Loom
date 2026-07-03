# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1900.md
- FR / parent locator: #1897 / #1888
- Scope: repo-facing carrier/output artifact metadata for long command diagnostics.
- Suite path: minimal
- Current `HEAD`: 2f0e983cd380620d9b27312870ad6f23e7bd1b4b before implementation commit; refresh after commit before review.
- PR locator: pending
- Host state locator: issue #1900 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1900/spec.md | required | authored suite | Recheck when output/carrier contract changes. |
| `plan.md` | .loom/specs/WI-1900/plan.md | required | authored suite | Recheck when validation strategy changes. |
| `implementation-contract.md` | .loom/specs/WI-1900/implementation-contract.md | required | authored suite | Recheck when changed metadata fields or validation invariants change. |
| `task-carrier.md` | .loom/specs/WI-1900/task-carrier.md | present | authored suite | Recheck before review, merge-ready, and closeout. |
| review record | .loom/reviews/WI-1900.json | pending | authored review truth | Required after implementation commit. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1900 | required | host mirror | Recheck before PR and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-000 | behavior_evidence | tools/loom.py; tools/check_cli_contract.py | S1 S2 S3 / A1 A2 A3 A4 A5 | WI-1900 / carrier-output behavior | present | review / merge-ready / closeout / status | Recheck after agent-safe output or artifact resolver contracts change. |
| EV-001 | test_evidence | `python3 tools/check_cli_contract.py --surface governance-closeout` | S1 S3 / A1 A3 A4 | WI-1900 / agent-safe output envelope | present | review / merge-ready / closeout / status | Rerun after `tools/loom.py` or governance closeout contract fixtures change. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface runtime-paths` | S2 / A2 | WI-1900 / global runtime locator resolver | present | review / merge-ready / closeout / status | Rerun after runtime path resolver or artifact locator resolution changes. |
| EV-003 | test_evidence | `python3 tools/loom.py suite validate --target . --item WI-1900 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1900 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1900 --json` | A5 | WI-1900 / suite carrier consumption | present | review / merge-ready / closeout / status | Rerun after spec, plan, evidence map, or task carrier changes. |
| EV-004 | test_evidence | `git diff --check` | changed files / A4 | branch head | present | review / merge-ready / closeout / status | Fix whitespace before review. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1900.md | EV-000 EV-001 EV-002 EV-003 EV-004 | WI-1900 / current branch validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR metadata, hosted checks, merge, or closeout evidence changes. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| separate User Story artifact | not_required | Internal runtime/carrier contract work from FR #1897. | review / merge-ready / closeout | Recheck if user-facing workflow behavior changes. | none |
| full gate independence proof | deferred | Requires WI-1900 contract, belongs to WI-1901. | #1900 review / closeout | Activate after #1900 merges. | #1901 |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: no plugin skill behavior change expected beyond output metadata consumption.
- Generated surface sync: sync copied runtime files only if copied runtime files change.
- Drift check requirement: run focused contracts and suite validators after implementation.
