# WI-1806 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1 S2 S3 S4 S5 | WI-1806 / pr-intent profiles | present | review / PR metadata / merge-ready | Re-run py_compile_clean, pr-metadata, suite-contract, and aggregate CLI contract after CLI changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | S1 S2 S3 S4 | WI-1806 / profile fixtures | present | review / PR gate / closeout | Re-run `python3 tools/check_cli_contract.py --surface pr-metadata` and aggregate after fixture changes. |
| EV-003 | test_evidence | `tools/check_cli_contract.py` | S3 | WI-1806 / suite N/A exit semantics | present | review / merge-ready / closeout | Re-run after suite validate or emit result handling changes. |
| EV-004 | contract_evidence | `docs/methodology/harness/cli-command-matrix.md` | S1 S2 S5 | WI-1806 / command matrix | present | PR body / docs / closeout | Re-read and update docs if command names, profiles, or release boundaries change. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1806.md` | EV-001 EV-002 EV-003 EV-004 A5 A6 | WI-1806 / current validation summary | present | review / merge-ready / release readiness | Refresh after commit head, PR metadata, review, hosted checks, or release readback. |

## External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| `v0.22.0` release (#1815) | blocked | #1800 / `v0.21.2` owns the current release line. | release closeout only | Start release readback only after #1800 / `v0.21.2` completes or explicitly releases the publication line. | #1815 |
| Current-head review / merge-ready | pending | PR head and PR body must be stable first. | merge-ready | Run after commit, push, PR body readback, and metadata preflight. | PR for WI-1806 |
