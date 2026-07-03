# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1898.md
- FR / parent locator: #1897 / #1888
- Scope: repo/global artifact classification contract freeze only.
- Suite path: minimal
- Current `HEAD`: fill with current head before merge-ready consumption.
- PR locator, or not-required rationale: not required until PR exists; consumer boundary: review and pre-PR validation only; recheck condition: author PR locator before merge-ready.
- Host state locator, or not-required rationale: issue #1898 and later PR readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1898/spec.md | required | authored suite | Recheck when contract scope or scenarios change. |
| `plan.md` | .loom/specs/WI-1898/plan.md | required | authored suite | Recheck when validation strategy changes. |
| suite path decision | .loom/specs/WI-1898/spec.md#suite-contract | present | authored suite | Recheck when suite path changes. |
| execution breakdown / task carrier | .loom/specs/WI-1898/task-carrier.md | present | authored suite | Recheck before review, merge-ready, and closeout. |
| review record | .loom/reviews/WI-1898.json | required | authored review truth | Required after review consumption. |
| merge-ready basis | pending PR | not required before PR | merge-ready truth | Required only for merge-ready or closeout consumption. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1898 | required | host mirror | Recheck before PR and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/methodology/harness/repo-global-artifact-classification.md | S1 / A1 | WI-1898 / scope / head | present | review / merge-ready / closeout / status | Recheck after classification contract edits. |
| EV-002 | behavior_evidence | docs/adoption/installation-taxonomy.md | S1 S3 / A2 | WI-1898 / adoption taxonomy | present | review / merge-ready / closeout / status | Recheck after adoption taxonomy edits. |
| EV-003 | behavior_evidence | docs/adoption/global-cli-user-plugin-contract.md; docs/adoption/host-adapter-matrix.md | S2 S3 / A3 A4 | WI-1898 / provider and host adapter docs | present | review / merge-ready / closeout / status | Recheck after provider or host adapter contract edits. |
| EV-004 | test_evidence | python3 tools/loom.py suite validate --target . --item WI-1898 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1898 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1898 --json | A5 | WI-1898 suite artifacts | present | review / merge-ready / closeout / status | Rerun after suite or carrier edits. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1898.md | EV-001 EV-002 EV-003 EV-004 | head / reviewed head / PR head / validation summary | present | merge-ready / closeout / status | Refresh after validation, review, PR metadata, hosted checks, merge, or closeout evidence changes. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| runtime path resolver implementation | deferred | WI-1898 only freezes the contract. | review / merge-ready / closeout | Recheck when #1899 starts. | #1899 |
| repo carrier implementation | deferred | Carrier slimdown implementation is separate. | review / merge-ready / closeout | Recheck when #1900 starts. | #1900 |
| gate independence validation | deferred | Gate behavior validation is a later Work Item. | review / merge-ready / closeout | Recheck when #1901 starts. | #1901 |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: not required for this docs-only contract.
- Generated surface sync: not required for this docs-only contract.
- Drift check requirement: linked docs must keep a single authority boundary; no duplicated classification matrix outside the new contract.
