# WI-1488 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1488.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1480
- Scope: documentation/help/migration guidance for context-safe output and metadata-only global CLI/plugin adoption.
- Suite path: minimal
- Current `HEAD`: pending PR head readback before merge-ready consumption.
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1669.
- Host state locator: issue #1488.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1488/spec.md | required | authored WI-1488 suite | Recheck when #1488 scope or acceptance changes. |
| `plan.md` | .loom/specs/WI-1488/plan.md | required | authored WI-1488 suite | Recheck when validation strategy changes. |
| suite path decision | .loom/specs/WI-1488/spec.md#suite-contract | minimal | authored WI-1488 suite | Recheck if docs-only scope expands. |
| implementation contract | .loom/specs/WI-1488/implementation-contract.md | required | PR gate / review readiness input | Recheck after docs/help/runtime boundary changes. |
| execution breakdown / task carrier | .loom/specs/WI-1488/task-carrier.md | required | authored WI-1488 suite | Recheck issue state and branch/PR binding before review. |
| review record | .loom/reviews/WI-1488.json | required after review | authored review truth | Required before merge-ready. |
| merge-ready basis | pending PR gate | required after PR | merge-ready truth | Required before merge. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1488 | required | GitHub issue | Recheck before closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | README.md; docs/adoption/legacy-install-migration.md; docs/adoption/codex-install.md; docs/methodology/harness/cli-command-matrix.md | S1-S3 and A1-A4 | WI-1488 / docs scope / current PR head | present | review / merge-ready / #1658 / #1489 / closeout | Reinspect docs after any docs/help text change. |
| EV-002 | test_evidence | validation commands in .loom/specs/WI-1488/plan.md | validation and test strategy | WI-1488 / current PR head | present | review / merge-ready / closeout | Rerun focused checks after docs or carrier changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1488.md | EV-001 EV-002 validation summary and branch working tree binding | work_item=WI-1488; branch=work/1488-docs-migration; head=pending PR head readback; base_head=88362a3dc634d388aba42554db37b9f9a1432ea1; validation_summary=2026-06-21 docs/help/migration validation passed | present | merge-ready / closeout / status | Rerun focused checks and update this row after PR head changes. |

## Deferred Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Release execution | deferred | #1488 only prepares docs/help/migration wording; release publication belongs to #1658. | #1658 | Activate when #1488 merges and release branch starts. | https://github.com/MC-and-his-Agents/Loom/issues/1658 |
| Final regression closeout | deferred | #1489 owns final milestone regression matrix and parent closeout. | #1489 | Activate after #1658 release evidence exists. | https://github.com/MC-and-his-Agents/Loom/issues/1489 |
