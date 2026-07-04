# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1954.md
- Phase / bug locators: #1954 / #1928 / #1930
- Scope: v0.27.1 host friction implementation batch for #1928 and #1930.
- Suite path: minimal
- Current `HEAD`: c230f5898a93a3b8ac3b10ee4af408089271c999
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1967
- Host state locator: issues #1954, #1928, #1930, and #1955.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1954/spec.md | required | authored suite | Recheck when #1928/#1930 acceptance changes. |
| `plan.md` | .loom/specs/WI-1954/plan.md | required | authored suite | Recheck when validation strategy changes. |
| `task-carrier.md` | .loom/specs/WI-1954/task-carrier.md | present | authored suite | Recheck before review, merge-ready, release, and closeout. |
| review record | .loom/reviews/WI-1954.json | pending | authored review truth | Required after implementation review. |
| host state | https://github.com/MC-and-his-Agents/Loom/pull/1967 | open | GitHub PR | Recheck before merge-ready and release handoff. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_flow.py; src/skills/shared/scripts/loom_flow.py; plugins/loom/skills/shared/scripts/loom_flow.py; .loom/bin/loom_flow.py | A1 A2 A3 | WI-1954 / runtime behavior | present | review / PR gate / merge-ready / release / closeout | Recheck after activation, suite validation, or runtime copy behavior changes. |
| EV-002 | test_evidence | targeted #1928/#1930 regression assertions in tools/check_cli_contract.py | A1 A2 A3 | WI-1954 / regression tests | present | review / PR gate / merge-ready / release / closeout | Rerun after `loom_flow.py` or `tools/check_cli_contract.py` changes. |
| EV-003 | test_evidence | `make loom-demo-new-project-check` | A4 | WI-1954 / demo bootstrap fixture | present | review / hosted checks / release / closeout | Rerun after generated runtime or demo fixture changes. |
| EV-004 | test_evidence | `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json` | A4 | WI-1954 / release payload readiness | present | review / release / closeout | Rerun after runtime copies, plugin payload metadata, package payload, or release carrier changes. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1954.md | EV-001 EV-002 EV-003 EV-004 | WI-1954 / current branch validation summary | present | PR gate / merge-ready / release / closeout | Refresh after final carrier commit, PR metadata update, hosted checks, merge, or release readback. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| #1933 temporary label hardcoding | excluded | Explicitly excluded from v0.27.1 host friction batch. | review / release / closeout | Recheck only if #1933 is explicitly pulled into a later batch. | #1933 |
| #1935 / v0.28.0 host adoption tax | excluded | Explicitly outside the v0.27.1 patch scope. | review / release / closeout | Recheck when v0.28.0 host adoption work starts. | #1935 |
| downstream repo-local `tools/loom.py` shim | excluded | #1930 removes this host requirement by consuming global `loom` CLI JSON. | review / release / closeout | Recheck if suite validation starts requiring host-local shims again. | #1930 |
