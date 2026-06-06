# WI-1289-1291 Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1289/WI-1291 is a narrow runtime and gate repair slice with a bounded implementation plan, no external research track, and no new public contract beyond the PR gate/review record methodology updates already listed in scope; consumer boundary: suite validation, review, merge-ready, and closeout should consume `spec.md`, `plan.md`, `evidence-map.md`, `task-carrier.md`, the review artifact, PR gate evidence, and hosted checks instead of requiring full-suite artifacts; recheck condition: add full-suite artifacts if this work expands into a cross-module design migration, new host API contract, profile rollout, or multi-PR execution breakdown.
- Consumes:
  - Work Item locator: `.loom/work-items/WI-1289-1291.md`
  - Issue locators: GitHub issues #1289 and #1291
- Produces:
  - Scenario ids: S1, S2, S3
  - Acceptance ids: A1, A2, A3, A4, A5
  - Behavior evidence expectation: CLI contract fixtures and hosted PR gate readback
- Locator:
  - Spec locator: `.loom/specs/WI-1289-1291/spec.md`
- Provenance:
  - Source issues: #1289 and #1291
  - Freshness rule: recheck when `tools/loom.py`, `skills/shared/scripts/loom_flow.py`, generated runtime copies, PR gate semantics, or closeout diagnostics change

## Goal

Standardize Loom's controlled merge path so `loom merge check` and `loom merge run` consume PR gate evidence before host merge, and expose post-merge review bypass diagnostics with a repair plan.

## Scope

- In scope: merge wrapper arguments, controlled merge fail-closed consumption, PR gate diagnostics, closeout/reconciliation diagnostics, review timestamp carrier, generated runtime parity, documentation, and CLI contract fixtures.
- Out of scope: replacing GitHub merge APIs, weakening review/head binding, backdating review evidence, or completing unrelated Work Items.

## Scenarios

### S1: Controlled Merge Consumes PR Gate

Given a PR whose body, head SHA, Work Item, authored review record, semantic review disposition, and required checks are current

When `loom merge check` or the underlying controlled merge runtime evaluates the PR

Then the result includes a passing PR gate and passing `controlled_merge_consumption` before any host merge delegation.

### S2: Retained PR Gate Drift Blocks Merge

Given a retained PR gate result that was produced for an earlier PR head

When controlled merge re-reads the current PR head before host merge

Then controlled merge blocks and reports stale retained PR gate consumption rather than treating the retained result as advisory-only.

### S3: Post-Merge Review Bypass Is Diagnosed

Given a merged PR whose authored review timestamp is later than the PR `mergedAt` timestamp

When PR gate, closeout, or reconciliation inspects the evidence

Then Loom reports post-merge review bypass diagnostics and a repair plan that records the evidence as post-merge closeout evidence, not merge-before-review compliance.

## Acceptance Criteria

- [x] A1: `loom merge check/run` exposes fixture and retained-result inputs needed to consume PR gate evidence.
- [x] A2: controlled merge blocks before host delegation when retained PR gate consumption, required checks, target binding, or PR head freshness fails.
- [x] A3: review records written by Loom include an authored timestamp suitable for post-merge diagnostics.
- [x] A4: PR gate, closeout, and reconciliation expose post-merge review bypass diagnostics and repair guidance.
- [x] A5: generated runtime copies remain synchronized with the shared runtime implementation.
