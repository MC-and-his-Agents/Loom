# WI-1541 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | `.loom/specs/WI-1541/spec.md` S1 S2 S3 | PR metadata render/readback/update wrapper surface | present | CLI operators, PR body preparation, review, merge-ready, closeout PRs | Re-run wrapper and pr-metadata contract checks after PR command surface changes. |
| EV-002 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1541/spec.md` S1 S2 S3 S4 | Runtime render/readback/update payloads and closeout surface reuse | present | repo-local wrapper, installed runtime, generated skills runtime copies | Re-sync generated runtime copies and rerun generated-tree-drift after runtime changes. |
| EV-003 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1541/spec.md` A1 A2 A3 A4 A5 | focused `pr-metadata` CLI contract surface | present | local and CI CLI contract checks | Extend focused checks when metadata fields or host update flow changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1541.md` | EV-001; EV-002; EV-003 | #1541 branch validation and generated runtime parity | present | review, merge-ready, PR gate, hosted checks, and milestone closeout | Re-run targeted validation after code, runtime copy, PR metadata, review, or carrier input changes. |
| EV-005 | build_evidence | `.loom/progress/WI-1541-build-evidence.json` | EV-001; EV-002; EV-003; EV-004 | integrated worker implementation, main-thread validation, and ownership evidence | present | build, review, merge-ready | Refresh when implementation, validation, review findings, or ownership changes. |
