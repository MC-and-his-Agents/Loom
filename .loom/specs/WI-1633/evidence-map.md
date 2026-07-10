# WI-1633 Evidence Map

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | `.loom/specs/WI-1633/spec.md` suite boundary and issues #1633/#1639 | Root `loom` no longer exposes repo-local host install modes, `--skill-id`, or `skills sync`; downstream skills generation is blocked. | present | PR4 host/skills CLI behavior only | Recheck if host parser, skills parser, metadata-only verification, or source plugin payload generation changes. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate` | EV-001 | CLI contract covers no repo-local writes, no old host args in help, no `skills sync`, downstream `skills generate` block, and aggregate command matrix parity. | present | PR4 review, PR gate, hosted checks | Rerun after `tools/loom.py`, `tools/check_cli_contract.py`, command matrix, or carrier changes. |
| EV-003 | test_evidence | `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `node packages/loom-installer/scripts/check-doc-sync.mjs`; `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `git diff --check` | EV-001 | Host/docs/package/release/static checks passed for PR4 head before PR metadata refresh. | present | package/release/doc guardrails for PR4 | Rerun after host adapter docs, package check docs, release surface, or static syntax changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1633.md` | EV-001; EV-002; EV-003 | Latest validation summary binds PR4 evidence to the current Work Item and future review record. | present | review, PR gate, hosted checks, closeout | Refresh progress, review, shadow, and PR metadata after head or validation evidence changes. |
