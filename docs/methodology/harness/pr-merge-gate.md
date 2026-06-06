# PR Merge Gate

This file defines the narrow PR-specific gate that connects Loom semantic review truth to host-enforced merge controls.

It is not a replacement for [merge-checkpoint.md](./merge-checkpoint.md) or [controlled-merge.md](./controlled-merge.md). It is the bridge that lets a host required check prove the current PR head has a fresh authored Loom review approval before merge.

## 1. Position

`pr merge gate` runs after formal review material exists and before `controlled merge` delegates to the host merge action.

It answers one question:

- Does the current PR head have a fresh authored Loom review approval that `merge-ready` can consume?

The binding subject is always the current PR head, not local checkout `HEAD` as an indirect substitute.

It does not run semantic review, does not inspect raw reviewer transcripts, and does not infer approval from CI or GitHub check success.

## 2. Required Inputs

The gate must be able to read:

- PR number or a unique PR inferred from PR head SHA
- PR head SHA
- PR body or host payload that binds the PR to a Loom Work Item
- repo-specific PR metadata preflight when declared by `metadata_contract.fields[*].machine_carrier`; the same parser preflight is consumed at `pre-review`, `review`, and `merge-ready` when the repo companion marks those surfaces in `preflight.required_before`
- current Loom fact chain for that Work Item
- `work_item.review_entry`
- authored review record at `review_entry`
- authored `semantic_review_disposition` derived from that same review record
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

The gate must treat `semantic_review_disposition` as the stable approval boundary for the current PR head:

- `required`
  - approval is still missing; gate must block
- `passed`
  - approval may satisfy the gate if every other freshness and binding condition passes
- `not_applicable`
  - only consumable when the same authored review record carries machine-readable
    `reason`、`change_class`、`substitute_validation`、`authority`
- `waived`
  - only consumable when the same authored review record carries machine-readable
    `reason`、`change_class`、`substitute_validation`、`authority`

`not_applicable` and `waived` are bypass-with-proof states, not silent skips.

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
- `semantic_review_disposition == passed`, or the same authored review record proves
  `not_applicable` / `waived` with valid reason, change class, substitute validation, and authority
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
- `pr_metadata_preflight`
- `post_merge_review_diagnostic`
- `governance_lint`
- `host_enforcement`
- `approval_boundary`
- `failure_taxonomy`

The same payload is the retained `pr-gate` result envelope. A downstream consumer may read it from a repo-relative retained result locator only when the envelope remains bound to:

- the same Work Item and `review_entry`
- the same review record locator, `decision`, `kind`, `reviewed_head`, and reviewed validation summary
- the same PR number, PR head SHA, base branch, and branch name
- a passing merge checkpoint result for the same gate chain

The retained envelope is fresh only when the current PR readback still reports the same head SHA and Work Item binding. Missing, unreadable, non-`pass`, wrong-schema, wrong-PR, wrong-Work-Item, stale-head, stale-validation, or non-implementation-review envelopes must `block` or fall back to `pr-gate` / `review`; they must not be treated as approval truth.

`governance_lint` exposes the approval-boundary lint result as derived evidence. It must not author a review verdict or replace `work_item.review_entry`; it only explains why raw review output, shadow evidence, PR body text, CI success, or GitHub review comments did not satisfy semantic approval.

`approval_boundary` must explicitly keep every non-authored evidence source false for approval truth:

- `raw_review_evidence_satisfies_approval`
- `shadow_evidence_satisfies_approval`
- `runtime_review_evidence_satisfies_approval`
- `pr_body_summary_satisfies_approval`
- `ci_success_satisfies_approval`
- `github_review_comments_satisfy_approval`
- `repo_companion_satisfies_approval`
- `guardian_satisfies_approval`

## 5. Failure Taxonomy

The gate must fail closed for:

- `pr_unreadable`
- `work_item_binding_missing`
- `work_item_binding_conflict`
- `fact_chain_unreadable`
- `review_missing`
- `review_schema_invalid`
- `review_not_approved`
- `semantic_review_disposition_missing`
- `semantic_review_disposition_invalid`
- `review_stale`
- `validation_summary_drift`
- `head_binding_drift`
- `checkout_head_drift`
- `raw_evidence_bypass`
- `post_merge_review_bypass`
- `ci_only_merge_bypass`
- `pr_metadata_preflight_failed`
- `host_enforcement_unverified`
- `retained_result_missing`
- `retained_result_unreadable`
- `retained_result_stale`

`raw_evidence_bypass` means raw or shadow evidence is present without an authored `review_entry` approval. This is always a block, never a pass.

`post_merge_review_bypass` means the review record or disposition was authored only after the merge-relevant PR head had already advanced or merged. `ci_only_merge_bypass` means CI / required checks passed without a consumable authored semantic review disposition for the same PR head.

When the PR is already merged, `post_merge_review_diagnostic` compares PR `mergedAt` with review record `authored_at` / `created_at` / `recorded_at` / submitted timestamp fields. If the review timestamp is later than `mergedAt`, the diagnostic must block and emit a repair plan that records the evidence as post-merge closeout evidence, preserves future protection through the controlled merge path, and forbids backdating or promoting historical bypass evidence into merge-before-review compliance.

`pr_metadata_preflight_failed` means a repo companion declared a blocking PR metadata machine carrier and the PR body machine block is malformed, missing required fields, or required but absent. The gate must report parser diagnostics instead of collapsing the failure into generic missing metadata fields.

Parser diagnostics must keep the machine-carrier boundary explicit: block locator, line/range, raw excerpt hash, declared source locator or source hash, expected schema/parser version, missing fields, parse error, repair hint, and fallback target. Those diagnostics prove the carrier is readable; they do not replace Work Item, review, merge-ready, closeout, or docs/source truth.

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

The default GitHub workflow runs on `pull_request` and checks out the PR head SHA that it verifies. That keeps the head-binding contract explicit, but it also means the check executes repository code from the PR head. Repositories that accept untrusted external contributions should treat this as a host-trust decision and either restrict who can run the required check or replace the workflow body with pinned tooling / API-fetched artifacts before enabling it as a required check.

## 7. Controlled Merge Boundary

`controlled merge` must run or consume this PR gate before delegating to `gh pr merge`.

When it consumes a retained `pr-gate` result, it must still perform drift-only readback for the current PR head, required checks, branch protection or active ruleset, mergeability, and merge method. The retained result only avoids re-reading the full semantic review and merge-ready decision.

The controlled merge wrapper must consume its own `controlled_merge_consumption` result before host delegation. Missing fresh PR gate evidence, retained PR gate drift, required-check drift, target mismatch, or stale head binding must block `loom merge run --apply`; those conditions may not be reported as advisory-only diagnostics.

In that drift-only readback, GitHub `BLOCKED` mergeability is not semantic approval truth and is not by itself a Loom readiness failure. It can be carried as a host policy signal only after the authored review record, `loom-pr-merge-gate`, required checks, PR head binding, and host enforcement readback have passed. GitHub review comments, including an author `COMMENTED` state, remain evidence-only and must not satisfy approval.

Bare `gh pr merge` bypasses Loom's semantic review approval bridge unless the host required check is already enforced. It should be treated as a bypass risk for Loom-governed PRs.

## 8. Non-goals

- Do not make `loom-check` the PR-specific gate.
- Do not copy a downstream repository's guardian implementation into Loom core.
- Do not require GitHub human review approval as a substitute for Loom `review_entry`.
- Do not let raw review evidence or CI success author semantic approval.
- Do not let repo companion, guardian, or any repo-owned wrapper replace Loom's generic `semantic_review_disposition` boundary.
