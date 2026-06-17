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

## 10. Closeout Terminal Profile

`loom-closeout-freeze/v1` is the terminal closeout profile of
`loom-gate-freeze/v1`. It freezes already-produced completion facts so a
closeout-only PR can transport terminal carrier sync without becoming the place
where host/head/body/carrier/shadow/review drift is first discovered.

This profile is a contract only. It does not implement `loom gate freeze
--profile closeout`, does not change hosted gate behavior, does not create a
new truth source, and does not weaken review, PR gate, controlled merge,
release/no-release, closeout, or reconciliation. Host, git, and repo carrier
truth must still be read back or recomputed by every consumer.

### 10.1 Dependency Lane

| Work item | Role | Minimum mergeable slice | Waits for |
| --- | --- | --- | --- |
| `#1531` | Define `loom-closeout-freeze/v1` | Schema, authority boundary, field sources, staleness rules, closeout modes, two-phase consumer contract, pending field list, and fixture inventory | `#1507`, `#1508`; consumes `#1509`, `#1511`; final shadow field names pending `#1510` |
| `#1532` | Local closeout freeze admission | Read-only CLI design for `check/write --profile closeout`, admission inputs, snapshot/hash output, and next-action shape | `#1531`; `#1510` consumable carrier/shadow surface |
| `#1533` | Closeout-specific hosted/repo-local gate | Snapshot/hash consumption, allowed paths, retained review, escalation verdict, and closeout-only gate output | `#1532`; `#1512` hosted admission surface |
| `#1534` | Docs, skills, fixtures convergence | Closeout mode user docs, skills protocol, executable fixtures, and reference integrity | `#1533`; `#1513` final classifier mapping |

`#1532` and `#1533` must not advance beyond design or fixture inventory until
their `#1510` / `#1512` consumer surfaces are stable. `#1534` must wait for
`#1533` and `#1513` before closing docs, skills, and executable fixtures.

### 10.2 Envelope

The profile is embedded under the standard gate freeze envelope:

```json
{
  "schema_version": "loom-cli-output/v1",
  "command": "gate freeze check",
  "result": "pass|block",
  "mutates": false,
  "payload": {
    "schema_version": "loom-closeout-freeze/v1",
    "profile": "closeout",
    "mode": "inline|auto_no_op|light|batched|full",
    "snapshot_id": "sha256:<digest>",
    "terminal_subject": {},
    "terminal_facts": {},
    "carrier_bindings": {},
    "retained_review": {},
    "release_boundary": {},
    "allowed_paths": {},
    "readiness": {},
    "pending_contract_fields": []
  }
}
```

`check` is read-only. A future write surface may retain a runtime snapshot or a
PR-body consumable hash, but it must not mutate GitHub, Project, PR, issue,
release, branch, or versioned closeout carriers.

### 10.3 Terminal Subject

`terminal_subject` binds the terminal consumer:

| Field | Required | Source |
| --- | --- | --- |
| `work_item` | yes | Fact-chain / progress carrier for the completed item. |
| `parent_fr` | when present | Work Item or GitHub issue relation. |
| `closeout_issue` | yes | GitHub issue readback, not PR body text alone. |
| `implementation_pr` | yes | Merged implementation PR readback. |
| `closeout_pr` | when PR-bound | Closeout-only PR number, branch, base, head SHA, and body readback. |
| `merge_commit` | yes | Controlled merge basis or host PR readback. |
| `target_branch` | yes | Target branch name plus readback SHA containing `merge_commit`. |
| `workspace` | yes | Formal worktree locator used to produce the snapshot. |
| `generated_at` | yes | Snapshot generation time. |
| `source_commands` | yes | Exact local and host readback commands used. |

Any disagreement between GitHub readback, git readback, fact-chain, PR body, or
carrier fields is `closeout_terminal_subject_drift` and blocks closeout profile
admission.

### 10.4 Terminal Facts

`terminal_facts` records the facts a closeout-only PR is allowed to carry:

| Field | Required | Source and staleness rule |
| --- | --- | --- |
| `issue_state` | yes | GitHub issue readback. Must be `closed` only when closeout basis proves the same Work Item; otherwise block. |
| `pr_merged` | yes | Implementation PR readback. Must include `mergedAt`, `headRefOid`, and merge commit. |
| `target_contains_merge_commit` | yes | Git readback from target branch. Must be recomputed, not copied from prior output. |
| `closed_at` | when issue closed | GitHub issue readback timestamp. |
| `project_status` | when project-bound | Project readback. `Done` is advisory until closeout basis passes. |
| `dependency_graph` | yes | Host binding inspector / native dependency readback. Open blockers or unreadable edges block. |
| `fact_chain_idle` | after carrier sync | Fact-chain readback showing `idle` / `no_active_item`, when the mode claims terminal carrier sync is complete. |

Closeout freeze must recompute host/git facts at admission time. It may retain
hashes and locators, but it must not treat stale runtime artifacts as terminal
truth.

### 10.5 Carrier Bindings

`carrier_bindings` must bind the same terminal facts across repo carriers:

- `.loom/progress/<item>.md` terminal closeout metadata
- `.loom/status/current.md` only as readback, never as a `#1531` write target
- review record locator and retained decision
- shadow freshness/parity, when declared by the profile
- closeout evidence locator
- release/no-release evidence locator

The current contract leaves these fields pending until upstream surfaces settle:

| Pending field | Blocked by | Interim handling |
| --- | --- | --- |
| Final carrier refresh result field name | `#1510` | Record as `pending_contract_field: carrier_refresh_result`; consumers must not guess. |
| Final shadow source hash / parity field names | `#1510` | Record as `pending_contract_field: shadow_freshness`; consumers may only cite existing shadow locators. |
| Hosted snapshot readback binding | `#1512` | Record as `pending_contract_field: hosted_snapshot_binding`; local admission cannot claim hosted consumption. |
| Closeout-specific classifier names | `#1513` | Record compatible generic kinds and `pending_contract_field: failure_classifier_mapping`. |

### 10.6 Retained Review And Allowed Paths

`retained_review` may be consumed only when the implementation review was
authored before merge, has `decision == allow`, is an implementation review
kind, and remains bound to the merged PR head or to closeout-only carrier drift.

`allowed_paths` for closeout-only PRs are limited to terminal metadata,
carrier sync, shadow/hash refresh, readback evidence, no-release rationale, and
closeout comments or records that do not change implementation behavior. Any
change to implementation files, CLI behavior, skills behavior, templates,
contracts, gate rules, release judgment semantics, or unclassified batch scope
is `closeout_implementation_drift` and requires full review / guardian
escalation.

### 10.7 Two-Phase Consumption

Closeout freeze has two consumers:

1. Closeout PR admission before creating or updating a closeout-only PR.
   Admission proves terminal facts are stable enough to carry and returns a
   snapshot/hash that the PR body and later gate can read.
2. Closeout PR consume/check before merging a closeout-only PR. The consumer
   re-reads host/git/carrier facts, verifies the snapshot/hash still binds the
   current PR head and body, checks allowed paths, and either passes closeout
   profile or escalates to full review / guardian.

Both phases fail closed. The second phase must not trust the first phase without
readback.

### 10.8 Closeout Modes

| Mode | Meaning | Required consumer boundary |
| --- | --- | --- |
| `inline` | Terminal facts are consumed in the implementation PR flow; no separate closeout PR. | Must still retain merge, target branch, issue, release/no-release, and carrier evidence. |
| `auto_no_op` | Host and repo carriers already agree; no PR body or carrier diff is needed. | Must prove no versioned carrier change is required. |
| `light` | Single closeout-only PR carries terminal metadata or hash refresh. | Must pass allowed paths and retained review checks. |
| `batched` | One closeout PR carries multiple terminal-only items. | Must prove every item independently passes; mixed risk escalates full. |
| `full` | Closeout includes contract, behavior, implementation, release dispute, or classifier change. | Must run normal review / guardian and merge-ready gates. |

### 10.9 Closeout Failure Kinds

Until `#1513` freezes final classifier names, consumers must preserve these
generic closeout profile kinds without treating them as automatic exemptions:

| Failure kind | Default result | Next action |
| --- | --- | --- |
| `closeout_terminal_subject_drift` | block | Re-read issue, PR, merge commit, target branch, and carrier bindings. |
| `closeout_host_git_mismatch` | block | Repair host/git readback or return to controlled merge evidence. |
| `closeout_carrier_drift` | block | Run the supported carrier closeout sync path or repair the carrier. |
| `closeout_shadow_stale` | block | Wait for `#1510` field names, then refresh shadow/hash evidence through supported commands. |
| `closeout_release_evidence_gap` | block | Author release/no-release evidence with pre/post-merge boundary. |
| `closeout_retained_review_unconsumable` | block | Rerun review or escalate to full review / guardian. |
| `closeout_allowed_paths_violation` | block | Remove non-closeout changes or convert the PR to full review. |
| `closeout_batch_mixed_risk` | block | Split safe terminal items from risky items or use full mode. |

The initial fixture inventory for these modes and risks is
[closeout-freeze-terminal-profile-fixtures.json](../../evidence/fixtures/closeout-freeze-terminal-profile-fixtures.json).
That file is a contract fixture source for `#1531`; executable regression
coverage remains owned by `#1534`.

## 11. Positive Example

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

## 12. Closeout Profile Example

```json
{
  "schema_version": "loom-closeout-freeze/v1",
  "profile": "closeout",
  "mode": "light",
  "snapshot_id": "sha256:<digest>",
  "terminal_subject": {
    "work_item": "WI-1531",
    "parent_fr": "#1505",
    "implementation_pr": "<merged-implementation-pr>",
    "closeout_pr": null,
    "merge_commit": "0123456789abcdef0123456789abcdef01234567",
    "target_branch": "main",
    "workspace": "/Users/mc/dev/Loom-1531-closeout-freeze-contract"
  },
  "terminal_facts": {
    "issue_state": "closed",
    "pr_merged": true,
    "target_contains_merge_commit": true,
    "dependency_graph": "pass",
    "fact_chain_idle": "pending_until_carrier_sync"
  },
  "readiness": {
    "result": "pass",
    "closeout_pr_allowed": true,
    "full_review_required": false
  },
  "pending_contract_fields": [
    "carrier_refresh_result",
    "shadow_freshness",
    "hosted_snapshot_binding",
    "failure_classifier_mapping"
  ]
}
```

## 13. Negative Example

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

## 14. Non-goals

- Do not implement the CLI in this contract Work Item.
- Do not alter hosted workflow admission in this contract Work Item.
- Do not update PR template behavior in this contract Work Item.
- Do not weaken review, PR gate, controlled merge, release/no-release, or
  closeout semantics.
- Do not let closeout-only PRs carry implementation drift, new product facts,
  release judgment disputes, template or gate rule changes without full review.
- Do not promote raw review output, shadow evidence, CI, GitHub review comments,
  or PR body summaries to authored Loom review approval.
