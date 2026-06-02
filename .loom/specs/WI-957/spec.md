# WI-957 Spec

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: #957 is a focused guard integration consuming already-implemented PR metadata, suite, review profile, and closeout preview surfaces; consumer boundary: it does not define the #1107 full spec suite CLI tree or rewrite frozen core contracts; recheck condition: switch to full suite if this Work Item starts changing core Work Item, review, merge-ready, closeout, or source-truth contracts.
- Consumes: issue #957, #876 machine carrier contract, #877 parser preflight, #874 PR body render/edit validation, #875 drift/legacy fixtures, and #969 review profile proof.
- Produces: pre-review readiness/cost guard evidence consumable before semantic review.

## Goal

Block expensive semantic review until the current PR/worktree/head and deterministic evidence are stable enough to review, while preserving Loom authored truth boundaries.

## Scope

- In scope:
  - Add `loom-pre-review-readiness-cost-guard/v1` output to existing `flow pre-review`.
  - Check PR head versus checkout head when a PR binding is supplied.
  - Diagnose dirty worktree state before review.
  - Consume `Latest Validation Summary` for deterministic checks, generated skills surface checks, and release/package checks when relevant.
  - Consume PR metadata preflight evidence from #876/#877/#874/#875.
  - Consume #969 review profile proof without owning model policy.
  - Expose closeout preview and post-review carrier-only policy as review-cost inputs.
- Out of scope:
  - #1107 full spec suite CLI tree.
  - Rewriting frozen Work Item, review, merge-ready, closeout, or docs/source truth contracts.
  - Letting parser, CLI, PR body, CI output, or runtime evidence replace authored truth.
  - Changing controlled merge, closeout, or model policy behavior.

## Scenarios

### S1: Stable PR Is Ready For Semantic Review

Given a clean worktree with checkout HEAD aligned to PR head
And deterministic checks are recorded in the current validation summary
And PR metadata preflight passes
When `flow pre-review` runs
Then readiness/cost guard passes and exposes consumed signals.

### S2: PR Head Drift Blocks Review Spend

Given PR head differs from local checkout HEAD
When `flow pre-review` runs with that PR binding
Then readiness/cost guard blocks with `checkout_head_drift` and fallback `push_or_refresh_pr_head`.

### S3: Missing Deterministic Evidence Blocks Review Spend

Given a build/review checkpoint or PR binding exists
When the validation summary lacks required deterministic check evidence
Then readiness/cost guard blocks with deterministic validation failure taxonomy.

### S4: Post-review Carrier-only Policy Is Explicit

Given review may later be retained after carrier-only evidence refresh
When readiness/cost guard runs
Then it exposes the carrier-only policy and states semantic path drift requires review.

## Acceptance

- A1: `flow pre-review` includes `pre-review-readiness-cost-guard` after PR metadata preflight.
- A2: Guard output includes `result`, `missing_inputs`, `failure_taxonomy`, `fallback_to`, and human summary.
- A3: PR head drift blocks with `checkout_head_drift` and `push_or_refresh_pr_head`.
- A4: Guard consumes PR metadata preflight, #969 profile proof, closeout preview, and post-review carrier-only policy.
- A5: Guard diagnoses generated skills surface and release/package check evidence from validation summary without replacing authored truth.
