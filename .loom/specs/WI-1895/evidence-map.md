# WI-1895 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
|---|---|---|---|---|---|---|---|
| EV-001 | behavior_evidence | `docs/adoption/workstation-registry-contract.md` | S1-S4 / A1-A6 | command surface and target-write boundary | present | review / PR gate / merge-ready / #1896 | Recheck after registry contract or CLI semantics change. |
| EV-002 | behavior_evidence | `tools/loom.py` | S1-S4 / A1-A4 | command entries, dispatch, registry helpers, register/list/unregister behavior | present | review / PR gate / hosted checks | Recheck after CLI edits. |
| EV-003 | test_evidence | `python3 tools/check_cli_contract.py --surface workstation-registry` | A1-A6 | isolated HOME CLI contract and target write boundary | present | review / PR gate / hosted checks | Rerun after CLI/checker/fixture edits. |
| EV-004 | test_evidence | `python3 tools/check_cli_contract.py --surface adoption-host-metadata` | S4 / A5 / A6 | adjacent adoption and host boundary unchanged | present | review / PR gate | Rerun after adoption/host-related edits. |
| EV-005 | test_evidence | `python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py` | A1-A5 | Python syntax/import safety | present | review / PR gate | Rerun after Python edits. |
| EV-006 | test_evidence | `python3 tools/loom.py help --json` | A1 | command matrix/help readback | present | review / PR gate | Rerun after command matrix edits. |
| EV-007 | test_evidence | `python3 tools/loom.py suite validate --target . --item WI-1895 --json` | A1-A6 | suite contract validation | present | review / merge-ready / closeout | Rerun after suite or carrier edits. |
| EV-008 | test_evidence | `python3 tools/loom.py suite evidence validate --target . --item WI-1895 --json` | A1-A6 | evidence map validation | present | review / merge-ready / closeout | Rerun after evidence map edits. |
| EV-009 | test_evidence | `python3 tools/loom.py suite carrier validate --target . --item WI-1895 --json` | A1-A6 | task carrier validation | present | review / merge-ready / closeout | Rerun after task carrier edits. |
| EV-010 | test_evidence | `python3 tools/loom.py fact-chain --target . --item WI-1895 --json` | A1-A6 | fact-chain validation | present | review / merge-ready / closeout | Rerun after docs, suite, carrier, progress, or review edits. |
| EV-011 | test_evidence | `git diff --check` | A1-A6 | diff hygiene | present | review / PR gate | Rerun after any file edit. |
| EV-012 | fresh_verification_input | `.loom/progress/WI-1895.md` | EV-001-EV-011 / A1-A6 | current branch / current head / WI-1895 | present | review / merge-ready / closeout | Refresh after final validation, PR metadata, review, hosted checks, and merge readback. |

## Deferred Evidence

| Evidence | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up |
|---|---|---|---|---|---|
| Live missing path validation | deferred | WI-1895 implements command read/write only; fail-closed validation is scoped to #1896. | #1896 implementation / FR #1893 closeout | Require when implementing registry validation. | #1896 |
| Live remote hash drift validation | deferred | WI-1895 stores the remote hash but does not compare it against future live reads. | #1896 implementation / FR #1893 closeout | Require when implementing registry validation. | #1896 |
| Duplicate id conflict repair | deferred | WI-1895 exposes stored-entry diagnostics only; conflict fail-closed handling is scoped to #1896. | #1896 implementation / FR #1893 closeout | Require when implementing registry validation. | #1896 |
| Workstation upgrade plan | deferred | Upgrade orchestration is owned by FR #1902. | FR #1902 | Require when implementing `loom workstation upgrade --plan`. | #1902 |
