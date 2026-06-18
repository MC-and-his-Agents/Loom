# WI-1512 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1512.md`
- Parent locator: `https://github.com/MC-and-his-Agents/Loom/issues/1505`
- Issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1512`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1572`
- Scope: hosted freeze admission for PR gate readback/snapshot inputs.
- Suite path: minimal
- Current `HEAD`: refreshed by validation summary before merge-ready.
- Host state locator: PR #1572 readback and hosted Actions runs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1512/spec.md` | required | authored suite | Recheck when hosted admission behavior changes. |
| `plan.md` | `.loom/specs/WI-1512/plan.md` | required | authored suite | Recheck when validation strategy changes. |
| suite path decision | `.loom/specs/WI-1512/spec.md#suite-contract` | required | authored suite | Recheck if scope expands beyond minimal runtime/fixture slice. |
| execution breakdown / task carrier | `.loom/specs/WI-1512/task-carrier.md` | required | authored task carrier | Recheck before merge-ready and milestone closeout. |
| review record | `.loom/reviews/WI-1512.json` | required | authored review truth | Required after implementation/carriers are stable. |
| merge-ready basis | PR #1572 metadata/readback/gate evidence | required | PR and gate truth | Required before merge-ready or merge. |
| host state | PR #1572 / Actions checks | required | GitHub readback | Recheck after each push or PR body update. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1512/spec.md` S1 S2 S3 | hosted admission recomputation, PR readback consumption, snapshot comparison | present | review / merge-ready / hosted gate / #1532/#1533 consumers | Re-run pr-metadata fixture and hosted PR gate after behavior changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1512/plan.md` validation strategy | pass/body-drift/snapshot-mismatch fixture coverage | present | local checks / CI release judgment / milestone closeout | Extend targeted fixture if hosted admission schema changes. |
| EV-003 | generated_runtime_evidence | `examples/new-project/.loom/bin/loom_flow.py` | EV-001 | source/install/runtime/demo copy consistency | present | generated-tree-drift / demo-bootstrap / node installer checks | Run `tools/skills_surface.py generate` and `make loom-demo-new-project-sync` after runtime changes. |
| EV-004 | pr_metadata_evidence | `.github/PULL_REQUEST_TEMPLATE.md` | PR #1572 machine carrier | repo PR metadata machine carrier contract; PR #1572 host readback supplies Work Item, branch, head SHA, release judgment, and surface binding | present | PR gate / merge-ready | Regenerate PR body and readback after each commit. |
| EV-005 | fact_chain_evidence | `.loom/work-items/WI-1512.md` | Work Item and recovery truth | current item `WI-1512` | present | PR gate / review / status | Keep shared carrier writes serialized in main thread. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1512.md` | EV-001 EV-002 EV-003 EV-004 EV-005 | head / reviewed head / PR head / validation summary | present | merge-ready / closeout / status | Refresh after final commit and review record. |

## Deferred Follow-Ups

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| closeout freeze profile | deferred | #1532 defines `loom-closeout-freeze/v1`; #1512 only handles hosted admission for existing gate freeze inputs. | #1532/#1533/#1534 | Start when #1512 is merged and consumable. | #1532 |
| closeout-specific gate | deferred | #1533 consumes closeout freeze profile after #1532. | #1533/#1534/#1515 | Start after #1532. | #1533 |
| one-shot post-merge closeout run | deferred | #1555 owns closeout run orchestration after #1494/#1543. | #1534/#1515 | Start when #1555 dependencies are stable. | #1555 |
