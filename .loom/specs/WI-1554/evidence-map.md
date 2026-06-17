# WI-1554 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | `.loom/specs/WI-1554/spec.md` S1 S2 S3 | merge wrapper `pr-number` parsing and runtime delegation | present | CLI wrapper and controlled merge entrypoint | Re-run merge-wrapper contract and help/error checks after wrapper changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1554/spec.md` S1 S2 S3 | deterministic merge-wrapper regression surface | present | local and CI CLI contract checks | Extend the focused surface if merge wrapper arguments change. |
| EV-003 | fresh_verification_input | `2026-06-17T16:56Z validation summary in .loom/progress/WI-1554.md` | EV-001; EV-002 | branch work/1554-cli-wrapper-contract targeted validation | present | review, merge-ready, PR gate, hosted checks, and milestone closeout | Re-run targeted validation after code, fixture, PR metadata, review, or carrier input changes. |
