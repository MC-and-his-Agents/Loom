# Spec

## Goal

Host-enforce Loom's semantic review approval model before Loom PRs can merge.

The outcome is that a PR-specific gate can prove the current PR head has a fresh authored Loom review record with `decision == allow`, and that raw review evidence, shadow evidence, CI success, or PR text cannot satisfy semantic approval.

## Scope

- In scope:
  - Add a narrow `loom-pr-merge-gate` workflow and `pr-gate check` command.
  - Add a controlled merge check/merge command that consumes PR gate output, required-check readback, and status check rollup before delegating to `gh pr merge`.
  - Preserve `loom-check` as the broad repository regression check rather than redefining it as the PR-specific gate.
  - Record PR #762 as self-governance regression evidence.
  - Add generated skill surfaces and tests for pass, missing review, stale review, non-allow review, raw-evidence-only bypass, and missing host enforcement.
- Out of scope:
  - Replacing GitHub branch protection or rulesets.
  - Replacing semantic review engines.
  - Making raw Codex App review output an approval truth source.
  - Starting Codex App review Stage 3 default switching.

## Key Scenarios

### Scenario 1

Given
- a PR bound to one Loom Work Item
- an authored implementation review record at `review_entry`
- review `decision == allow`
- reviewed head and validation summary cover the current PR head

When
- `loom-pr-merge-gate` runs for the PR

Then
- the gate returns `pass`
- the output names the authored review record as the approval truth
- raw review and shadow evidence remain non-authoritative

### Scenario 2

Given
- raw review evidence exists
- the authored review record is missing, stale, or non-allow

When
- `loom-pr-merge-gate` runs for the PR

Then
- the gate returns `block`
- failure taxonomy identifies the review or raw-evidence bypass failure
- controlled merge cannot delegate to `gh pr merge`

### Scenario 3

Given
- the PR gate command and workflow exist
- branch protection or active rulesets do not require `loom-pr-merge-gate`

When
- `controlled-merge check` runs

Then
- the command returns `block`
- the output reports host enforcement as unverified
- bare `gh pr merge` remains documented as a bypass risk

## Behavior Evidence

- Story scenario mapping: #763 parent issue and #766-#768/#765/#764 work items.
- Scenario coverage: installed-runtime fixtures in `src/skills/shared/scripts/loom_check.py`.
- Expected evidence locator: `docs/evidence/validations/validation-pr-762-semantic-review-gate-gap.md`.
- Freshness rule: the authored review record must match current `latest_validation_summary` and the PR head, allowing only carrier-only post-review drift.
- Execution ledger acceptance locator: `.loom/progress/WI-763.md`.

## Exceptions And Boundaries

- Failure modes:
  - missing PR payload or head SHA blocks
  - missing Work Item binding blocks
  - missing, stale, fallback, or blocking review blocks
  - raw-evidence-only approval attempt blocks
  - missing host required-check enforcement blocks controlled merge
- Operational boundaries:
  - `pr-gate check` proves PR-local semantic approval.
  - `controlled-merge check|merge` verifies host enforcement and delegates only when explicitly executed.
  - host branch protection/ruleset remains the enforcement substrate.
- Rollback or fallback expectations:
  - remove the new required check from branch protection/rulesets before reverting the workflow or command.
  - keep broad `loom-check` required throughout rollback.

## Acceptance Criteria

- [x] Target outcome is observable
- [x] Key scenarios are covered
- [x] Important boundary behavior is defined
- [x] Validation evidence is identified
- [x] Behavior evidence can be consumed by review, merge-ready, and closeout
