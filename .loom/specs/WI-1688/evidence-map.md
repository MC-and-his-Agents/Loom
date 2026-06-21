# WI-1688 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1688.md`
- FR / parent locator: issue #1685
- Scope: compact non-passing root CLI diagnostics without changing delegated gate semantics.
- Suite path: minimal
- Current `HEAD`: update before merge-ready consumption.
- PR locator, or N/A rationale: fill when PR exists.
- Host state locator, or N/A rationale: issue #1688

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1688/spec.md` | required | authored for issue #1688 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1688/plan.md` | required | authored for issue #1688 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1688/spec.md` | minimal | authored suite contract | Recheck before merge-ready. |
| execution breakdown / task carrier | `.loom/specs/WI-1688/task-carrier.md` | required | authored task carrier | Recheck before review and closeout. |
| review record | `.loom/reviews/WI-1688.json` | required before merge-ready | authored review truth | Required after review consumption. |
| merge-ready basis | PR merge-ready attempt artifact | required before closeout | merge-ready truth | Required after PR exists. |
| host state | issue #1688 | required | host mirror | Recheck after PR creation and merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1 actionable envelope behavior | WI-1688 / branch `work/1688-minimal-action-feedback` | present | review / merge-ready / closeout | Re-run output envelope tests after wrapper output changes. |
| EV-002 | test_evidence | `test/output_envelope_test.py` | A1-A4 compact output and `--full-output` behavior | WI-1688 / root CLI wrapper | present | review / merge-ready / closeout | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`. |
| EV-003 | test_evidence | `tools/check_cli_contract.py` | A5 contract consumers unwrap agent-safe artifacts | WI-1688 / closeout queue contract | present | review / merge-ready / closeout | Re-run governance-closeout contract surface. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1688.md` | EV-001 EV-002 EV-003 | current branch / current head before PR | present | merge-ready / closeout | Refresh after any implementation or contract-test changes. |
| EV-005 | build_evidence | `.loom/progress/WI-1688-build-evidence.json` | integrated implementation, test, contract consumer, ownership, and validation evidence | WI-1688 / build checkpoint | present | build / review / merge-ready | Refresh after implementation, validation, review findings, or ownership changes. |
| EV-006 | behavior_evidence | `.loom/specs/WI-1688/implementation-contract.md` | runtime, extraction, and boundary contracts | WI-1688 / implementation review | present | review / merge-ready | Refresh if wrapper output behavior or consumer boundary changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| release publication | N/A | #1688 does not publish a release by itself. | closeout / release planning | Recheck if packaging or version files change. | #1696 |
| `loom ship` implementation | deferred | Owned by #1690 and #1691. | planning only | Start #1690/#1691. | #1690, #1691 |
