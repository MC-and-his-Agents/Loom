# WI-1894 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
|---|---|---|---|---|---|---|---|
| EV-001 | behavior_evidence | `docs/adoption/workstation-registry-contract.md` | S1 / S2 / S3 / A1-A4 | workstation registry authority, schema, and fail-closed classifications | present | review / PR gate / merge-ready / FR #1893 closeout / #1895 implementation | Recheck after any workstation registry schema or authority-boundary edit. |
| EV-002 | behavior_evidence | `docs/evidence/fixtures/workstation-registry-fixtures.json` | S2 / S3 / A3 / A4 | fixture coverage for valid, missing path, remote drift, duplicate id, and opted-out registry states | present | review / PR gate / #1895 / #1896 | Recheck after fixture edits or classifier name changes. |
| EV-003 | behavior_evidence | `docs/adoption/installation-taxonomy.md` and `docs/adoption/global-cli-user-plugin-contract.md` | S1 / A2 | workstation registry separated from repository adoption truth and provider/plugin truth | present | review / PR gate / adoption docs consumers | Recheck after adoption authority taxonomy changes. |
| EV-004 | test_evidence | `python3 -m json.tool docs/evidence/fixtures/workstation-registry-fixtures.json >/dev/null` | A3 / A4 | fixture JSON validity | present | review / PR gate | Rerun after fixture edits. |
| EV-005 | test_evidence | `python3 tools/check_cli_contract.py --surface workstation-registry` | A1-A5 | focused registry fixture and classifier contract | present | review / PR gate / hosted checks | Rerun after fixture or checker edits. |
| EV-006 | test_evidence | `python3 tools/check_cli_contract.py --surface adoption-host-metadata` | A2 / A6 | adjacent adoption authority boundary unchanged | present | review / PR gate | Rerun after adoption contract edits. |
| EV-007 | test_evidence | `python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py` | A5 / A6 | checker syntax and import safety | present | review / PR gate | Rerun after Python edits. |
| EV-008 | test_evidence | `python3 tools/loom.py suite validate --target . --item WI-1894 --json` | A1-A6 | suite contract validation | present | review / merge-ready / closeout | Rerun after suite or carrier edits. |
| EV-009 | test_evidence | `python3 tools/loom.py suite evidence validate --target . --item WI-1894 --json` | A1-A6 | evidence map validation | present | review / merge-ready / closeout | Rerun after evidence map edits. |
| EV-010 | test_evidence | `python3 tools/loom.py suite carrier validate --target . --item WI-1894 --json` | A1-A6 | task carrier validation | present | review / merge-ready / closeout | Rerun after task carrier edits. |
| EV-011 | test_evidence | `python3 tools/loom.py fact-chain --target . --item WI-1894 --json` | A1-A6 | fact-chain validation | present | review / merge-ready / closeout | Rerun after docs, suite, carrier, progress, or review edits. |
| EV-012 | test_evidence | `git diff --check` | A6 | diff hygiene | present | review / PR gate | Rerun after any file edit. |
| EV-013 | fresh_verification_input | `.loom/progress/WI-1894.md` | EV-001-EV-012 / A1-A6 | current branch / current head / WI-1894 | present | review / merge-ready / closeout | Refresh after final validation, PR metadata, review, hosted checks, and merge readback. |

## Deferred Evidence

| Evidence | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up |
|---|---|---|---|---|---|
| Real `~/.loom/repositories.json` write/readback | deferred | WI-1894 freezes schema and fixtures only; CLI mutation is owned by #1895. | #1895 implementation / FR #1893 closeout | Require when implementing register/list/unregister. | #1895 |
| Real missing path / remote hash readback | deferred | WI-1894 provides fixture classifications; live filesystem/git checks are owned by fail-closed validation. | #1896 implementation / FR #1893 closeout | Require when implementing registry validation. | #1896 |
| Multi-repository workstation upgrade plan | deferred | Workstation upgrade orchestration is owned by FR #1902. | FR #1902 | Require when implementing `loom workstation upgrade --plan`. | #1902 |
