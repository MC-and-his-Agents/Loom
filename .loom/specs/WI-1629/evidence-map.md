# WI-1629 Evidence Map

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | `.loom/specs/WI-1629/spec.md` suite boundary and issue #1629 | Codex user-level plugin install/register defaults to the global Loom package payload and does not write target repositories. | present | PR3 install/register behavior only | Recheck if host install/register source resolution, target writes, or Codex user-level registration changes. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; temporary HOME smoke tests | EV-001 | CLI contract and smoke evidence cover user-level install/register writes and no target repo writes. | present | PR3 review, PR gate, hosted checks | Rerun after `tools/loom.py`, `tools/check_cli_contract.py`, host install/register, or Codex plugin payload source changes. |
| EV-003 | test_evidence | `python3 tools/host_adapter_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/check_release_surface.py`; `node --test test/npm-package-smoke.test.mjs`; `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `git diff --check` | EV-001 | Host/package/release/static checks passed for PR3 head before gate metadata refresh. | present | package and release-surface guardrails for PR3 | Rerun after host adapter, package manifest, release surface, or static syntax changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1629.md` | EV-001; EV-002; EV-003 | Latest validation summary binds PR3 evidence to the current Work Item and review record. | present | review, PR gate, hosted checks, closeout | Refresh progress, review, shadow, and PR metadata after head or validation evidence changes. |
