# WI-1511 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1511/spec.md` S1 S2 S3 S4 S5 | WI-1511 / gate freeze review-head binding | present | CLI contract / review / merge-ready / #1512 planning | Re-run `python3 tools/loom.py gate freeze check --target . --item WI-1511 --json` after runtime or review binding changes. |
| EV-002 | generated_surface_evidence | `skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1511/spec.md` A5 | WI-1511 / generated runtime copies including `.loom/bin`, skill runtimes, and example project | present | generated-tree drift / distribution checks | Re-run `python3 tools/skills_surface.py check --surface generated-tree-drift` after shared runtime edits. |
| EV-003 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1511/spec.md` S1 S2 S3 S4 | WI-1511 / CLI contract coverage | present | local validation / hosted CI | Re-run `python3 tools/check_cli_contract.py` after payload shape or fixture changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1511.md` | EV-001 EV-002 EV-003 | WI-1511 / latest validation summary / branch `work/1511-review-head-freeze` | present | review / merge-ready | Refresh after validation, PR creation/update, hosted checks readback, review, or merge-ready. |
