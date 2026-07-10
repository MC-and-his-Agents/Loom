# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1901.md
- FR / parent locator: #1897 / #1888
- Scope: gate/read surface independence from repo-local `.loom/runtime` and `.loom/tmp`.
- Suite path: minimal
- Current `HEAD`: pending final PR head after carrier commit.
- PR locator: pending
- Host state locator: issue #1901 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1901/spec.md | required | authored suite | Recheck when cache/gate behavior changes. |
| `plan.md` | .loom/specs/WI-1901/plan.md | required | authored suite | Recheck when validation strategy changes. |
| `implementation-contract.md` | .loom/specs/WI-1901/implementation-contract.md | required | authored suite | Recheck when fixture invariants change. |
| `task-carrier.md` | .loom/specs/WI-1901/task-carrier.md | present | authored suite | Recheck before review, merge-ready, and closeout. |
| review record | .loom/reviews/WI-1901.json | pending | authored review truth | Required after final validation. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1901 | required | host mirror | Recheck before PR and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-000 | behavior_evidence | tools/check_cli_contract.py | S1 S2 S3 / A1 A2 A3 A4 A5 | WI-1901 / cache-absent gate behavior | present | review / merge-ready / closeout / status | Recheck after runtime path resolver or gate/read surface changes. |
| EV-001 | test_evidence | `python3 tools/py_compile_clean.py tools/check_cli_contract.py` | changed Python / A5 | WI-1901 / contract syntax | present | review / merge-ready / closeout / status | Rerun after editing `tools/check_cli_contract.py`. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface runtime-paths` | S1 S2 S3 / A1 A2 A3 A4 A5 | WI-1901 / cache-absent fixture | present | review / merge-ready / closeout / status | Rerun after runtime-paths fixtures or checked command behavior changes. |
| EV-003 | test_evidence | `python3 tools/loom.py suite validate --target . --item WI-1901 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1901 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1901 --json` | A5 | WI-1901 / suite carrier consumption | present | review / merge-ready / closeout / status | Rerun after spec, plan, evidence map, or task carrier changes. |
| EV-004 | test_evidence | `git diff --check` | changed files / A4 | branch head | present | review / merge-ready / closeout / status | Fix whitespace before review. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1901.md | EV-000 EV-001 EV-002 EV-003 EV-004 | WI-1901 / current branch validation summary | present | merge-ready / closeout / status | Refresh after final commit, review record, PR metadata, hosted checks, merge, or closeout evidence changes. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| workstation upgrade orchestration | out_of_scope | Belongs to FR #1902. | #1901 review / closeout | Recheck if this fixture requires workstation registry or upgrade planning. | #1902 |
| legacy repo migration apply | out_of_scope | Belongs to FR #1908. | #1901 review / closeout | Recheck if cache-absent validation starts mutating legacy surfaces. | #1908 |
| hosted service mutation | not_required | Fixture runs locally with stable PR payload inputs. | review / merge-ready / closeout | Recheck if hosted gate policy or live branch protection changes. | none |
