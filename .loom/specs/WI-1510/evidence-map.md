# WI-1510 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1510/spec.md` S1 S2 S3 | gate freeze carrier refresh and shadow freshness bindings | present | gate freeze snapshot, hosted admission #1512, merge-ready, milestone closeout | Re-run gate freeze, carrier refresh dry-run, and shadow parity after runtime or carrier changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1510/spec.md` S1 S2 S3 | deterministic source-hash drift and refresh suggestion regression coverage | present | local and CI CLI contract checks | Extend the focused contract if freeze binding fields or classifier names change. |
| EV-003 | fresh_verification_input | `Pending final validation summary in .loom/progress/WI-1510.md` | EV-001; EV-002 | branch work/1510-carrier-shadow-freeze targeted validation | present | review, merge-ready, PR gate, hosted checks, and milestone closeout | Re-run targeted validation after code, fixture, carrier, review, PR metadata, or shadow input changes. |
