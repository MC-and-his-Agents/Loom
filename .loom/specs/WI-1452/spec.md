# Spec

## Suite Contract

- Suite path: minimal
- Suite index locator: .loom/specs/WI-1452/spec.md
- Consumes:
  - Work Item / FR locator: GitHub issue #1452
  - Story Readiness: N/A
    - Locator: GitHub issue #1452
    - Rationale: #1452 is a runtime gate hardening issue with explicit acceptance criteria in the issue body.
    - Consumer boundary: spec review and implementation review may consume the issue body plus this minimal suite.
    - Recheck condition: reopen story shaping only if product behavior expands beyond controlled-merge triggered check consumption.
  - Story scenario: N/A
    - Locator: GitHub issue #1452
    - Rationale: scenarios are defined below from the issue acceptance criteria.
    - Consumer boundary: no separate story carrier is required for this issue.
    - Recheck condition: require a story carrier if #1292/#1293 scope is folded into this issue.
  - Story Business Confirmation: N/A
    - Locator: GitHub issue #1452
    - Rationale: this is internal merge safety behavior, not a new end-user business workflow.
    - Consumer boundary: review consumes technical acceptance criteria only.
    - Recheck condition: require business confirmation if external release UX or policy defaults change.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this spec
  - Acceptance ids / locators: A1-A5 in this spec
  - Behavior evidence expectation: targeted CLI contract fixtures and hosted PR gate readback
- Locator:
  - Spec locator: .loom/specs/WI-1452/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1452; PR #1614
  - Freshness rule: valid for PR #1614 head 07bb4651cc662c008e2855f877fa6ee7844cc931 and later carrier-only sync commits.

- Full suite artifacts not_applicable: rationale: WI-1452 uses the minimal suite because the issue body, spec, and plan already define the runtime gate behavior, scenarios, and validation evidence; consumer boundary: spec review, implementation review, merge-ready, and closeout consume the minimal suite plus PR #1614 evidence but do not require research, contracts, readiness-checklist, or suite-index artifacts; recheck condition: expand to full suite if #1452 scope adds new shared contracts, migration design, cross-repo fixture closeout, release publication, or live GitHub settings mutation.

## Goal

- Make `controlled-merge` fail closed when the current PR head has triggered checks that are failed, pending, queued, in progress, unreadable, or otherwise not explicitly allowed.
- Keep existing required-check semantics unchanged while adding a separate machine-readable triggered-check rollup.

## Scope

- In scope:
  - `controlled-merge` runtime check rollup consumption.
  - `triggered_check_rollup` and `triggered_checks` JSON output.
  - Targeted fixtures for allowed, failed, pending, and unreadable triggered checks.
  - Controlled-merge docs and generated/runtime/demo surface sync.
- Out of scope:
  - GitHub branch protection or ruleset live mutation.
  - #1292 cross-repo fixture closeout.
  - #1293 release convergence.
  - #1285 parent closeout.
  - VERSION, tag, GitHub Release, npm publish, or raw host merge behavior.

## Key Scenarios

### Scenario S1

Given required branch/ruleset checks are green

When a non-required triggered check on the same PR head failed, was cancelled, timed out, required action, or hit startup failure

Then `controlled-merge check` blocks and reports a triggered-check failure separately from required-check drift.

### Scenario S2

Given required branch/ruleset checks are green

When a triggered check is queued, pending, waiting, requested, or in progress

Then `controlled-merge check` blocks as pending and does not merge.

### Scenario S3

Given required branch/ruleset checks are green

When all triggered checks are `SUCCESS`, `SKIPPED`, or `NEUTRAL`

Then `controlled-merge check` may pass its triggered-check layer while preserving all existing required-check and retained-gate checks.

## Behavior Evidence

- Story scenario mapping: S1-S3 map directly to GitHub issue #1452 acceptance criteria.
- Story readiness: N/A
  - Locator: GitHub issue #1452
  - Rationale: issue body is the accepted behavior carrier.
  - Consumer boundary: review and merge-ready consume this spec plus issue #1452.
  - Recheck condition: require story readiness if UX/business semantics are added.
- Story business confirmation: N/A
  - Locator: GitHub issue #1452
  - Rationale: internal merge gate behavior has no external business copy or workflow.
  - Consumer boundary: release docs may summarize behavior but do not redefine it.
  - Recheck condition: require confirmation if product defaults or user-facing policy change.
- Scenario coverage:
  - S1 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
  - S2 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
  - S3 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`
- Expected evidence locator: `.loom/progress/WI-1452.md`; PR #1614 checks; review record `.loom/reviews/WI-1452.json`
- Freshness rule: evidence must reference PR #1614 current head or carrier-only drift accepted by merge gate.
- Execution ledger acceptance locator: `.loom/progress/WI-1452.md`

## Exceptions And Boundaries

- Failure modes: unreadable check rollup blocks; unknown triggered conclusion blocks; required-check missing/pending/failing remains unchanged.
- Operational boundaries: no live GitHub settings mutation; no release action in this issue.
- Rollback or fallback expectations: revert PR #1614 runtime/docs/fixture changes or disable consumption only through a follow-up Work Item.

## Acceptance Criteria

- [x] A1: Required checks remain unchanged.
- [x] A2: Failed non-required triggered checks block controlled merge.
- [x] A3: Pending triggered checks block controlled merge.
- [x] A4: `SUCCESS`, `SKIPPED`, and `NEUTRAL` are explicit allowed triggered states.
- [x] A5: JSON payload exposes `triggered_check_rollup` and enough classification detail for review, merge-ready, and closeout consumers.
