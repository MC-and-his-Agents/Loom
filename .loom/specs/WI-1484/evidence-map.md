# WI-1484 Evidence Map

## Context

- Item: WI-1484
- PR: pending
- Current `HEAD`: current PR head at review time
- Suite Path: minimal

## Evidence Rows

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `test/output_envelope_test.py` | S1-S3 and A1-A4 in `.loom/specs/WI-1484/spec.md` | work_item=WI-1484; scope=cli-agent-safe-output; head_sha=current PR head at review time | present | review; merge-ready; #1478; #1484; #1485 | Recheck after output wrapper, command router, help matrix, or full-output parsing changes. |
| EV-002 | test_evidence | `python3 test/output_envelope_test.py`; `python3 -m py_compile tools/loom.py test/output_envelope_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata --surface controlled-merge --surface closeout-wrapper`; `git diff --check` | validation strategy in `.loom/specs/WI-1484/plan.md` | work_item=WI-1484; scope=cli-agent-safe-output; head_sha=current PR head at review time | present | review; merge-ready; #1489 | Rerun after code, tests, carrier, review, or metadata changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1484.md` | EV-001 EV-002 current validation summary and PR head binding | work_item=WI-1484; reviewed_head=current PR head at review time | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head, scope, or validation summary changes. |
