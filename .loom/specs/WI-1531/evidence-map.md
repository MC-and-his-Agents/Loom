# WI-1531 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | contract_evidence | `docs/methodology/harness/gate-freeze.md` | `.loom/specs/WI-1531/spec.md` S1 S2 S3 S4 | WI-1531 / closeout terminal profile contract | present | #1532/#1533/#1534 planning, review, PR gate | Re-read the terminal profile section after downstream field names stabilize. |
| EV-002 | closeout_boundary_evidence | `docs/methodology/harness/closeout-gate.md` | `.loom/specs/WI-1531/spec.md` S1 S3 | WI-1531 / closeout gate consumption boundary | present | closeout docs and future closeout profile gate | Re-check that closeout consumers still re-read host/git/carrier facts. |
| EV-003 | fixture_inventory_evidence | `docs/evidence/fixtures/closeout-freeze-terminal-profile-fixtures.json` | `.loom/specs/WI-1531/spec.md` S2 S3 S4 | WI-1531 / non-executable fixture inventory | present | #1534 executable fixture conversion | Re-run `python3 -m json.tool docs/evidence/fixtures/closeout-freeze-terminal-profile-fixtures.json`. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1531.md` | EV-001 EV-002 EV-003 | WI-1531 / latest validation summary / branch `work/1531-closeout-freeze-contract` | pending | review / merge-ready | Refresh after local validation, PR creation/update, hosted checks readback, review, or merge-ready. |
