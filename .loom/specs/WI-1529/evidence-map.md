# WI-1529 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | implementation_evidence | `tools/skills_surface.py` | `.loom/specs/WI-1529/spec.md` S1 S2 S3 S4 | WI-1529 / reference-integrity surface | present | skills surface, release/no-release closeout | Re-run `python3 tools/skills_surface.py check --surface reference-integrity` after changes to skill package layout or runtime copies. |
| EV-002 | fixture_evidence | `test/skills_surface_reference_integrity_test.py` | `.loom/specs/WI-1529/spec.md` S1 S2 S3 | WI-1529 / reference scanner and parity fixtures | present | local unit validation | Re-run `python3 test/skills_surface_reference_integrity_test.py` after scanner changes. |
| EV-003 | full_surface_evidence | `python3 tools/skills_surface.py check` | `.loom/specs/WI-1529/spec.md` S4 | WI-1529 / release surface consumption | present | pre-review, PR gate evidence, #1515 closeout readback | Re-run before review, after rebases, and before merge-ready. |
| EV-004 | fact_chain_evidence | `.loom/work-items/WI-1529.md`; `.loom/progress/WI-1529.md`; `.loom/status/current.md`; `.loom/reviews/WI-1529.json` | `.loom/specs/WI-1529/spec.md` S4 | WI-1529 / active carrier chain | pending | review / merge-ready | Refresh after final validation, review, PR creation/update, hosted checks, merge, or closeout sync. |
