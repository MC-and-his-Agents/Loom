# WI-1486 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1486.md
- Issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1486
- Scope: Codex user-level plugin executable skill payload text.
- Suite path: minimal
- Host state locator: GitHub issue #1486 and implementation PR.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1486/spec.md` | required | issue #1486 | Recheck after skill output contract changes. |
| `plan.md` | `.loom/specs/WI-1486/plan.md` | required | issue #1486 | Recheck after validation strategy changes. |
| implementation contract | `.loom/specs/WI-1486/implementation-contract.md` | required | issue #1486 | Recheck after command example or output boundary changes. |
| task carrier | `.loom/specs/WI-1486/task-carrier.md` | required | GitHub issue #1486 | Recheck before closeout. |
| review record | `.loom/reviews/WI-1486.json` | required before merge | review gate | Recheck after head changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/**`; `skills/**`; `plugins/loom/skills/**` | S1-S3 and A1-A4 | work_item=WI-1486; scope=skill-payload | present | review; merge-ready; #1488; release; closeout | Regenerate mirrors and rerun skills surface checks after skill source edits. |
| EV-002 | test_evidence | focused validation commands in `.loom/specs/WI-1486/plan.md` | validation and test strategy | work_item=WI-1486; head_sha=current PR head at review time | present | review; merge-ready; closeout | Rerun listed checks after source, mirror, plugin payload, or carrier changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1486.md` | EV-001; EV-002; validation summary and PR head binding | work_item=WI-1486; reviewed_head=current PR head at review time | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head or validation summary changes. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| User documentation, help text, migration docs | deferred | #1486 only updates executable skill payload. | #1488 | Recheck after #1488 updates docs/help/migration. | https://github.com/MC-and-his-Agents/Loom/issues/1488 |
| Release evidence | deferred | Publication is owned by the release Work Item. | #1658 | Recheck after release PR/tag/release notes/package/plugin verification. | https://github.com/MC-and-his-Agents/Loom/issues/1658 |
