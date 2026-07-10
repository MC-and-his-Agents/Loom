# WI-1495 Evidence Map

## Context

- Item: WI-1495
- PR: #1663
- Current `HEAD`: current PR head at review time
- Suite Path: minimal

## Evidence Rows

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `test/retained_item_lookup_test.py`; `tools/check_cli_contract.py`; `docs/methodology/harness/closeout-gate.md`; `docs/methodology/harness/host-action-contract.md` | S1-S3 and A1-A4 in `.loom/specs/WI-1495/spec.md` | work_item=WI-1495; scope=retained-closeout-fixture-docs; head_sha=current PR head at review time; pr=1663 | present | review; merge-ready; closeout; #1496 | Recheck after retained-item lookup, closeout gate wording, host-action contract wording, or generated mirror changes. |
| EV-002 | test_evidence | `PYTHONDONTWRITEBYTECODE=1 python3 test/retained_item_lookup_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `git diff --check` | validation strategy in `.loom/specs/WI-1495/plan.md` | work_item=WI-1495; scope=retained-closeout-fixture-docs; head_sha=current PR head at review time | present | review; merge-ready; closeout | Rerun after fixture, contract docs, generated mirrors, carrier, review, or metadata changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1495.md` | EV-001 EV-002 current validation summary and PR head binding | work_item=WI-1495; reviewed_head=current PR head at review time; pr=1663 | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head, scope, or validation summary changes. |
