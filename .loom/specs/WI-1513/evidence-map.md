# WI-1513 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1513/spec.md` S1 S2 | gate freeze failure classifier payload and classifier vocabulary mapping | present | gate freeze snapshot, hosted admission #1512, closeout gate #1533, docs/skills #1514/#1534, merge-ready, milestone closeout | Re-run gate freeze classifier checks after runtime or classifier vocabulary changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1513/spec.md` A1 A2 A3 A4 A5 | aggregate CLI contract coverage for supported classifiers, next actions, and PR metadata drift classification | present | local and CI CLI contract checks | Extend the focused contract if classifier names, next actions, or gate freeze payload shape change. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1513.md` | EV-001; EV-002 | branch work/1513-failure-classifier-v2 targeted validation and PR #1564 metadata readback | present | review, merge-ready, PR gate, hosted checks, and milestone closeout | Re-run targeted validation after code, generated runtime copies, carrier, review, or PR metadata changes. |
