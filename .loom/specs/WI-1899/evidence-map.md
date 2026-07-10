# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1899.md
- FR / parent locator: #1897 / #1888
- Scope: runtime/tmp output path resolver implementation and focused consumer fixtures.
- Suite path: minimal
- Current `HEAD`: 287b9c6f87ae32259fee1e9c115a1ed5681d17d9
- PR locator: pending
- Host state locator: issue #1899 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1899/spec.md | required | authored suite | Recheck when resolver scope changes. |
| `plan.md` | .loom/specs/WI-1899/plan.md | required | authored suite | Recheck when validation strategy changes. |
| `implementation-contract.md` | .loom/specs/WI-1899/implementation-contract.md | required | authored suite | Recheck when changed surfaces or invariants change. |
| `task-carrier.md` | .loom/specs/WI-1899/task-carrier.md | present | authored suite | Recheck before review, merge-ready, and closeout. |
| review record | .loom/reviews/WI-1899.json | pending | authored review truth | Required after implementation commit. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1899 | required | host mirror | Recheck before PR and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-000 | behavior_evidence | skills/shared/scripts/runtime_paths.py; skills/shared/scripts/loom_flow.py; tools/loom.py | S1 S2 S3 S4 / A1 A2 A3 A4 A5 | WI-1899 / runtime path behavior | present | review / merge-ready / closeout | Recheck after resolver, runtime artifact, or CLI output writer changes. |
| EV-001 | test_evidence | `python3 tools/check_cli_contract.py --surface runtime-paths` | S1 S2 S3 / A1 A2 A3 | WI-1899 / resolver helpers | present | review / merge-ready / closeout | Rerun after `runtime_paths.py` or resolver helpers change. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface pr-metadata` | S1 S3 / A4 | WI-1899 / PR metadata and PR intent artifacts | present | review / merge-ready / closeout | Rerun after PR metadata or PR intent artifact routing changes. |
| EV-003 | test_evidence | `python3 tools/check_cli_contract.py --surface runtime-upgrade` | S1 / A4 A6 | WI-1899 / runtime-upgrade PR body artifact | present | review / merge-ready / closeout | Rerun after runtime-upgrade wrapper changes. |
| EV-004 | test_evidence | `python3 tools/check_cli_contract.py --surface pr-gate-target-readback` | S1 / A5 | WI-1899 / gate PR body readback | present | review / merge-ready / closeout | Rerun after PR gate artifact binding changes. |
| EV-005 | test_evidence | `python3 tools/check_cli_contract.py --surface governance-closeout` | S2 S4 / A5 | WI-1899 / closeout, execution attempts, agent-safe artifacts | present | review / merge-ready / closeout | Rerun after closeout/gate-freeze/agent-safe output changes. |
| EV-006 | static_evidence | `python3 -m py_compile ...`; `git diff --check` | A6 | WI-1899 / touched runtime copies | present | review / merge-ready / closeout | Rerun after touched Python files change. |
| EV-007 | fresh_verification_input | .loom/progress/WI-1899.md | EV-000 EV-001 EV-002 EV-003 EV-004 EV-005 EV-006 | WI-1899 / current branch validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR metadata, hosted checks, merge, or closeout evidence changes. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| repo carrier slimdown | deferred | WI-1899 only moves runtime/tmp output paths. | review / merge-ready / closeout | Recheck when #1900 starts. | #1900 |
| full gate independence validation | deferred | WI-1899 covers focused consumers only. | review / merge-ready / closeout | Recheck when #1901 starts. | #1901 |
| legacy cache migration apply | deferred | WI-1899 provides read fallback; migration commands are separate. | review / merge-ready / closeout | Recheck when #1908/#1910 starts. | #1908 / #1910 |
