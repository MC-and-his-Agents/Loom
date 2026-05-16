# PR Merge Gate

This file defines the narrow PR-specific gate that connects Loom semantic review truth to host-enforced merge controls.

It is not a replacement for [merge-checkpoint.md](./merge-checkpoint.md) or [controlled-merge.md](./controlled-merge.md). It is the bridge that lets a host required check prove the current PR head has a fresh authored Loom review approval before merge.

## 1. Position

`pr merge gate` runs after formal review material exists and before `controlled merge` delegates to the host merge action.

It answers one question:

- Does the current PR head have a fresh authored Loom review approval that `merge-ready` can consume?

It does not run semantic review, does not inspect raw reviewer transcripts, and does not infer approval from CI or GitHub check success.

## 2. Required Inputs

The gate must be able to read:

- PR number or a unique PR inferred from PR head SHA
- PR head SHA
- PR body or host payload that binds the PR to a Loom Work Item
- current Loom fact chain for that Work Item
- `work_item.review_entry`
- authored review record at `review_entry`
- current `latest_validation_summary`
- local checkout `HEAD`
- host required-check and branch-protection readback when running in controlled merge mode

The PR body should expose the Work Item explicitly:

```text
Loom Work Item: WI-123
```

If the PR body and CLI argument disagree about the Work Item, the gate fails closed.

## 3. Approval Truth

Only the authored Loom review record referenced by `review_entry` can satisfy semantic approval.

The following can be retained as evidence but cannot satisfy approval:

- raw Codex App review output
- shadow review evidence
- runtime review evidence
- prompt or engine logs
- CI success
- GitHub review comments
- PR body summaries

The minimum pass condition is:

- `review_entry` exists and is readable
- review record schema is `loom-review/v1`
- `decision == allow`
- `reviewed_head` covers the current PR head
- `reviewed_validation_summary` equals current `latest_validation_summary`
- `kind` is `general_review` or `code_review`
- no implementation drift exists after review, except allowed Loom carrier-only drift already accepted by the review head-binding contract

## 4. Result Contract

Stable command:

```bash
python3 tools/loom_flow.py pr-gate check --target <repo> --pr <number>
```

The command returns the standard Loom result envelope:

- `pass`: current PR head is semantically approved and merge-ready material is fresh
- `block`: required PR, Work Item, review, validation, or head-binding input is missing or invalid
- `fallback`: a prior Loom gate must be repaired before PR merge readiness can be evaluated

Required payload fields:

- `schema_version: loom-pr-merge-gate/v1`
- `pr`
- `work_item`
- `review_approval`
- `merge_checkpoint`
- `host_enforcement`
- `approval_boundary`
- `failure_taxonomy`

## 5. Failure Taxonomy

The gate must fail closed for:

- `pr_unreadable`
- `work_item_binding_missing`
- `work_item_binding_conflict`
- `fact_chain_unreadable`
- `review_missing`
- `review_schema_invalid`
- `review_not_approved`
- `review_stale`
- `validation_summary_drift`
- `head_binding_drift`
- `checkout_head_drift`
- `raw_evidence_bypass`
- `host_enforcement_unverified`

`raw_evidence_bypass` means raw or shadow evidence is present without an authored `review_entry` approval. This is always a block, never a pass.

## 6. Host Enforcement

For Loom self-governance, the stable check name is:

```text
loom-pr-merge-gate
```

Host enforcement is proven only when all of these are true:

- workflow exists and runs on PRs
- check ran for the current PR head
- branch protection or an active ruleset requires the stable check name
- host readback is available and current

Local workflow files alone do not prove host enforcement.

## 7. Controlled Merge Boundary

`controlled merge` must run or consume this PR gate before delegating to `gh pr merge`.

Bare `gh pr merge` bypasses Loom's semantic review approval bridge unless the host required check is already enforced. It should be treated as a bypass risk for Loom-governed PRs.

## 8. Non-goals

- Do not make `loom-check` the PR-specific gate.
- Do not copy a downstream repository's guardian implementation into Loom core.
- Do not require GitHub human review approval as a substitute for Loom `review_entry`.
- Do not let raw review evidence or CI success author semantic approval.
