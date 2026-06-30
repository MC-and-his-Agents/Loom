# WI-1822 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1822 is a narrow released CLI bugfix for one checkpoint alias in an already-frozen resume/state-check normalization path.
- Consumer Boundary: review, PR metadata, hosted checks, PR gate, controlled merge, v0.22.1 release workflow, release readback, and issue closeout may consume this minimal suite while still requiring fact-chain, current-head review, PR metadata, hosted checks, and post-release readback.
- Recheck Condition: Require a full suite if scope expands beyond `normalize_checkpoint()` alias handling, changes terminal checkpoint semantics, changes review/merge-ready/release authority, or touches unrelated resume state behavior.
- Scope Proof: PR scope remains limited to normalizing `closeout` to `closed_out`, focused contract coverage, runtime-copy sync, WI-1822 carriers, and v0.22.1 patch release evidence.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: #1822 has a single behavior contract and no separate research, multi-contract design, readiness matrix, consistency analysis, or execution breakdown beyond the Work Item and task carrier. consumer boundary: suite validate, review, PR gate, hosted CI, release judgment, controlled merge, publish, and closeout may consume this minimal suite while still requiring fact-chain, current-head review, PR metadata, release judgment, hosted checks, and post-release readback. recheck condition: require full suite artifacts if the scope expands beyond checkpoint alias normalization or changes terminal checkpoint semantics.

## Scenarios

### S1 Closeout checkpoint alias is accepted

Given a Loom carrier or resume path contains `Current Checkpoint: closeout`
When Loom normalizes the checkpoint before state-check or resume consumption
Then the checkpoint is treated as terminal `closed_out`

## Acceptance

- A1: `normalize_checkpoint("closeout")` returns `closed_out`.
- A2: Existing `closed_out` terminal checkpoint behavior remains unchanged.
- A3: All runtime copies stay in sync after the source change.
- A4: The fix is released as a patch version because the bug exists in the published CLI path.

## Non-Goals

- Do not change checkpoint lifecycle semantics beyond the `closeout` alias.
- Do not alter #1800, #1802, v0.21.2, or #1806 closeout truth.
- Do not use this patch to bypass review, merge-ready, release readback, or closeout evidence.
