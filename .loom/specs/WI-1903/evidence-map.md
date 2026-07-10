# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1903.md
- FR / parent locator: #1902 / #1888
- Scope: plan-only workstation upgrade CLI and focused validation drift repair.
- Suite path: minimal
- Current `HEAD`: 27041cc764b78c30d353e179eaedfa3c2c7f5ead after implementation baseline commit.
- PR locator: pending
- Host state locator: issue #1903 readback.

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `docs/adoption/workstation-registry-contract.md` | S1 S2 S3 S4 / A1 A2 A3 A4 | WI-1903 / workstation plan output | present | review / merge-ready / closeout / status | Recheck after workstation upgrade planning or registry classification changes. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface workstation-registry` | S1 S2 S3 S4 / A1 A2 A3 A4 | WI-1903 / focused CLI fixture | present | review / merge-ready / closeout / status | Rerun after `tools/loom.py` or workstation registry fixtures change. |
| EV-003 | test_evidence | `python3 tools/skills_surface.py check --surface generated-tree-drift` | A5 | WI-1903 / runtime copy parity | present | review / merge-ready / closeout / status | Rerun after shared runtime copies change. |
| EV-004 | test_evidence | `python3 tools/loom_check.py --profile source --source-surface contract-only .` | A5 | WI-1903 / source contract validation | present | review / merge-ready / closeout / status | Rerun after `loom_check.py` or bootstrap hash carriers change. |
| EV-005 | test_evidence | `python3 tools/loom_check.py --profile source --source-surface daily-execution-cli-fast .` | A5 | WI-1903 / daily CLI smoke | present | review / merge-ready / closeout / status | Rerun after runtime flow or demo runtime changes. |
| EV-006 | test_evidence | `python3 tools/py_compile_clean.py ...`; `git diff --check` | changed files / A1 A5 | branch worktree | present | review / merge-ready / closeout / status | Fix syntax or whitespace before review. |
| EV-007 | fresh_verification_input | .loom/progress/WI-1903.md | EV-001 EV-002 EV-003 EV-004 EV-005 EV-006 | WI-1903 / current branch validation summary | present | merge-ready / closeout / status | Refresh after final commit, PR metadata, hosted checks, merge, or closeout evidence changes. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| workstation upgrade machine refresh details | deferred | Belongs to WI-1904. | #1903 review / closeout | Activate when implementing detailed CLI/plugin refresh coverage. | #1904 |
| per-repo adoption mutation apply | deferred | Belongs to WI-1905 and WI-1906. | #1903 review / closeout | Activate when implementing repo mutation classification/application. | #1905 / #1906 |
| freshness cache | deferred | Belongs to WI-1907. | #1903 review / closeout | Activate when optimizing repeated host/plugin checks. | #1907 |
