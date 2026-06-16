# Gate Freeze Snapshot

This file freezes the `loom-gate-freeze/v1` contract. It defines the gate
input snapshot that later CLI and hosted admission work can consume before
starting expensive gate checks.

It is a contract only. This file does not implement `loom gate freeze`, does not
change hosted workflows, and does not make the snapshot a substitute for review,
PR gate, controlled merge, hosted checks, release judgment, or closeout.

## 1. Goal

The snapshot answers one question:

- Are the inputs needed by hosted gate admission stable, current, and
  machine-readable for the intended PR head?

The snapshot must bind the same Work Item, branch, PR, head, PR body, metadata
carrier, Loom carriers, review record, shadow evidence, suite validation, and
release judgment boundary. If any binding is missing, stale, or contradictory,
the snapshot returns `block` with a typed next action.

## 2. Position In The Gate Chain

`gate freeze` sits before hosted gate admission and before expensive semantic or
hosted checks. It consumes existing read surfaces:

- `loom pr metadata-preflight`
- `loom suite validate`
- `loom suite evidence validate`
- `loom suite carrier validate`
- fact-chain / status-surface readback
- review/head binding
- shadow freshness or shadow parity readback when declared applicable
- release / no-release requiredness
- CLI command matrix availability

The snapshot is retained evidence about input stability. It is not authored
approval truth and must not satisfy:

- implementation review
- `loom-pr-merge-gate`
- controlled merge
- required hosted checks
- release evidence
- closeout / reconciliation

## 3. Required Envelope

Every snapshot uses the standard Loom CLI envelope and embeds a
`loom-gate-freeze/v1` payload:

```json
{
  "schema_version": "loom-cli-output/v1",
  "command": "gate freeze check",
  "result": "pass|block|fallback",
  "generated_at": "2026-06-16T17:46:34Z",
  "target": ".",
  "item_id": "WI-1507",
  "summary": "Gate inputs are stable for hosted admission.",
  "mutates": false,
  "failed_layer": null,
  "fail_closed_reason": null,
  "fallback_to": null,
  "payload": {
    "schema_version": "loom-gate-freeze/v1",
    "snapshot_id": "sha256:<digest>",
    "snapshot_subject": {},
    "input_bindings": {},
    "readiness": {},
    "failure_classifier": {},
    "next_action": {}
  }
}
```

`check` is read-only. A future `write` operation may retain the snapshot, but it
must still require explicit write semantics and must never mutate GitHub,
Project, PR, issue, branch protection, release, or closeout state.

## 4. Snapshot Subject

`snapshot_subject` binds the object being admitted:

| Field | Required | Meaning |
| --- | --- | --- |
| `work_item` | yes | Current Loom Work Item id. |
| `fr` | when present | Parent FR or governing issue locator. |
| `branch` | yes | PR head branch or formal execution branch. |
| `workspace` | yes | Formal worktree / workspace locator. |
| `pr` | when PR-bound | PR number and URL. |
| `base_branch` | when PR-bound | Target branch, normally `main`. |
| `head_sha` | yes | Current admitted head SHA. |
| `base_sha` | when PR-bound | Current base branch SHA used for admission. |
| `generated_at` | yes | Snapshot creation time. |
| `source_commands` | yes | Exact commands used to derive the snapshot. |

The snapshot must fail closed when CLI argument, PR body, Work Item, branch, or
fact-chain disagree on these fields.

## 5. Input Bindings

The `input_bindings` object contains one entry per consumed input surface.

Each entry uses this shape:

```json
{
  "result": "pass|block|fallback|advisory|not_applicable",
  "source_locator": "repo-relative path, command, or host URL",
  "source_hash": "sha256:<digest>",
  "bound_to": {
    "work_item": "WI-1507",
    "branch": "work/1507-gate-freeze-contract",
    "pr": null,
    "head_sha": "d634be43af641940a9734c1d50ebcdf2214f7b34"
  },
  "findings": [],
  "next_action": null
}
```

Required input keys:

| Key | Required condition | Consumption |
| --- | --- | --- |
| `pr_body_readback` | PR-bound work | PR body file/readback hash and host body hash match the current PR body. |
| `metadata_block` | repo companion declares PR metadata | Machine block marker, parser version, source range/hash, required fields, and fingerprint. |
| `work_item_carrier` | always | `.loom/work-items/<item>.md` binds goal, scope, branch, recovery, review, validation, and closeout condition. |
| `progress_carrier` | always | `.loom/progress/<item>.md` binds checkpoint, next step, validation summary, and recovery boundary. |
| `status_surface` | always | `.loom/status/current.md` derives from the same fact-chain entry points. |
| `review_binding` | after review exists | Review record locator, decision, kind, reviewed head, validation summary, and allowed carrier-only drift classification. |
| `shadow_freshness` | when shadow surfaces exist or profile requires them | Shadow source hashes and parity state for declared shadow surfaces. |
| `suite_validation` | always | `loom suite validate` result and suite path decision. |
| `suite_evidence_validation` | always | `loom suite evidence validate` result, row-level gaps, source locators, failure kinds, consumer impact, and next action. |
| `suite_carrier_validation` | always | `loom suite carrier validate` result, carrier rows, host signal conflicts, failure kinds, consumer impact, and next action. |
| `release_requiredness` | always | `release_required`, `no_release`, or `deferred_release_judgment_blocking`, with pre/post merge boundary. |
| `command_surface` | always | Availability of every command referenced by `next_action` or `refresh_suggestions`. |

## 6. Vocabulary Versions

The snapshot must record the vocabulary it consumed:

```json
{
  "vocabulary_versions": {
    "evidence_map": {
      "freshness": ["present", "stale", "missing", "conflict", "not_applicable"],
      "evidence_type": ["behavior_evidence", "test_evidence", "fresh_verification_input"]
    },
    "task_carrier": {
      "carrier_type": ["github_issue", "github_project_item", "checklist_item", "repo_tasks_md", "external_tracker", "not_applicable"],
      "normalized_status": ["pending", "in_progress", "done", "blocked", "deferred", "not_applicable"],
      "relationship": ["primary", "mirror", "evidence_locator", "not_applicable"]
    },
    "release_requiredness": ["release_required", "no_release", "deferred_release_judgment_blocking"]
  }
}
```

Unknown values are `contract_vocabulary_drift`. They must not be collapsed into
manual investigation or advisory-only output when the owning gate needs the
surface.

## 7. Readiness Fields

`readiness` summarizes the input surfaces:

```json
{
  "result": "pass|block|fallback",
  "blocking_inputs": [],
  "advisory_inputs": [],
  "refresh_suggestions": [],
  "semantic_rerun_required": false,
  "hosted_admission_allowed": true
}
```

`blocking_inputs` must include the input key, failure kind, source locator,
consumer impact, and next action. `advisory_inputs` may be present only when the
consumer boundary does not require the input for hosted admission.

`refresh_suggestions` are allowed only for refreshable drift. The suggested
command must exist in the current command matrix. If no supported command
exists, emit `unsupported_command_surface` and provide a manual or existing
alternative path.

## 8. Failure Classifier

Each finding maps into the existing top-level taxonomy:

| Failure kind | Category | Default result | Typical next action |
| --- | --- | --- | --- |
| `pr_body_readback_mismatch` | `drift` | block | Re-read PR body, update body if needed, rerun metadata preflight. |
| `metadata_block_fingerprint_mismatch` | `drift` | block | Re-render PR body and rerun `loom pr metadata-preflight`. |
| `carrier_refresh_stale` | `stale` | block | Refresh the owning carrier through an existing supported carrier path. |
| `shadow_source_hash_drift` | `drift` | block | Refresh declared shadow source or rerun shadow parity if supported. |
| `review_head_binding_drift` | `stale` | block | Rerun implementation review unless drift is allowed carrier-only drift. |
| `suite_validation_failed` | `gate_failure` | block | Rerun or repair `loom suite validate`. |
| `suite_evidence_failed` | `gate_failure` | block | Repair evidence-map source locator/freshness and rerun validation. |
| `suite_carrier_failed` | `gate_failure` | block | Repair task carrier locator/status/conflict and rerun validation. |
| `release_requiredness_missing` | `gate_failure` | block | Author release/no-release judgment before admission. |
| `pre_post_merge_release_boundary_conflict` | `gate_failure` | block | Move post-merge evidence out of pre-merge readiness. |
| `unsupported_command_surface` | `gate_failure` | block | Use an existing command or implement the surface in a later Work Item. |
| `contract_vocabulary_drift` | `gate_failure` | block | Update the contract or producer vocabulary before consuming the snapshot. |

The classifier must also include:

- `category`
- `kind`
- `severity`
- `subject`
- `why_blocking`
- `fallback_to`
- `evidence`
- `consumer_impact`

## 9. Release Evidence Boundary

The snapshot must distinguish:

- `pre_merge_release_prep_evidence`
  - release/no-release judgment, package/version diff proof, release workflow
    applicability, local release-surface checks, and explicit non-release
    rationale.
- `post_merge_release_evidence`
  - tag, GitHub Release, npm publish, global CLI smoke, merge commit on target
    branch, and post-merge closeout readback.

Pre-merge gate freeze must not mark future tag, GitHub Release, npm registry, or
global CLI smoke as present. If the change requires an actual release, the
snapshot may only say release evidence is pending until the authorized post-merge
release step completes.

## 10. Positive Example

```json
{
  "schema_version": "loom-gate-freeze/v1",
  "snapshot_subject": {
    "work_item": "WI-1507",
    "branch": "work/1507-gate-freeze-contract",
    "workspace": "/Users/mc/dev/Loom-1507-gate-freeze-contract",
    "pr": null,
    "head_sha": "d634be43af641940a9734c1d50ebcdf2214f7b34",
    "base_sha": "d634be43af641940a9734c1d50ebcdf2214f7b34"
  },
  "readiness": {
    "result": "pass",
    "blocking_inputs": [],
    "advisory_inputs": [],
    "refresh_suggestions": [],
    "hosted_admission_allowed": true
  },
  "input_bindings": {
    "suite_evidence_validation": {
      "result": "pass",
      "source_locator": "loom suite evidence validate --target . --item WI-1507 --json",
      "findings": []
    },
    "release_requiredness": {
      "result": "pass",
      "source_locator": ".loom/progress/WI-1507.md#latest-validation-summary",
      "value": "no_release"
    }
  }
}
```

## 11. Negative Example

```json
{
  "schema_version": "loom-gate-freeze/v1",
  "readiness": {
    "result": "block",
    "blocking_inputs": [
      {
        "input": "suite_evidence_validation",
        "failure_kind": "contract_vocabulary_drift",
        "source_locator": ".loom/specs/WI-1507/evidence-map.md#row-ev-999",
        "consumer_impact": "hosted admission cannot classify evidence freshness",
        "next_action": "update producer vocabulary or contract before hosted gate"
      },
      {
        "input": "command_surface",
        "failure_kind": "unsupported_command_surface",
        "source_locator": "loom help --json",
        "consumer_impact": "freeze suggested a command that does not exist",
        "next_action": "use an existing supported command or implement the command in a later Work Item"
      }
    ],
    "hosted_admission_allowed": false
  }
}
```

## 12. Non-goals

- Do not implement the CLI in this contract Work Item.
- Do not alter hosted workflow admission in this contract Work Item.
- Do not update PR template behavior in this contract Work Item.
- Do not weaken review, PR gate, controlled merge, release/no-release, or
  closeout semantics.
- Do not promote raw review output, shadow evidence, CI, GitHub review comments,
  or PR body summaries to authored Loom review approval.
