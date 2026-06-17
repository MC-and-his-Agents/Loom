# WI-1511 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1511 is a bounded CLI/runtime hardening of the existing `loom-gate-freeze/v1`, review record, and PR gate binding surfaces. It changes how existing local carriers are classified and reported; it does not change GitHub host settings, release mechanics, external data, secrets, persistence, or ordinary authored review authority. consumer boundary: CLI contract checks, generated runtime drift checks, suite validate, review, PR gate, merge-ready, closeout, and #1512 hosted admission planning may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence. recheck condition: require a full suite if #1511 expands into hosted workflow changes, new host writes, security/privacy behavior, migration behavior, release mechanics, or external visible actions.

## Objective

Make gate freeze record and classify review/head binding before hosted gate admission, so operators can see whether the authored review still binds to the current PR head, whether drift is allowed carrier-only drift, or whether semantic drift requires rerunning review.

## Scope

In scope:

- Extend `loom-gate-freeze/v1` review binding evidence with review path, decision, kind, reviewed head, current/pr head, changed paths, disallowed paths, binding status, semantic review disposition status, result, and next action.
- Treat `fresh` and allowed `carrier-only` review bindings as consumable evidence while still writing the binding details into the snapshot.
- Treat missing review, invalid decision/kind, stale binding, implementation drift, invalid `semantic_review_disposition`, or validation-summary mismatch as fail-closed freeze inputs.
- Preserve the distinction between ordinary implementation PR review binding and terminal closeout retained-review handling.
- Add focused CLI contract coverage for fresh, carrier-only, and stale/semantic drift cases.

Out of scope:

- No weakening of #1285 semantic review/head binding.
- No promotion of raw review evidence, shadow evidence, CI, GitHub review state, or PR body prose into authored Loom review approval.
- No implementation of #1510 carrier/shadow freshness, #1512 hosted admission consumption, #1513 classifier expansion, #1514 docs/skills milestone sweep, or #1515 release/no-release closeout.
- No ordinary implementation PR bypass for terminal closeout retained-review rules.

## Acceptance Scenarios

### S1: Fresh review binding is recorded

Given a valid authored review record is bound to the current PR head
When `loom gate freeze check` runs for the Work Item
Then the freeze snapshot records review path, decision, kind, reviewed head, current/pr head, binding status `fresh`, and result `pass`.

### S2: Allowed carrier-only drift is recorded and consumable

Given a valid authored review record is behind the current PR head only by allowed carrier paths
When `loom gate freeze check` runs for the Work Item
Then the freeze snapshot records changed paths, disallowed paths, binding status `carrier-only`, and result `pass` without treating the carrier drift as semantic implementation drift.

### S3: Semantic or stale drift blocks freeze

Given a valid authored review record is behind the current PR head by implementation files or other disallowed paths
When `loom gate freeze check` runs for the Work Item
Then the freeze snapshot blocks, reports binding status `stale` or `implementation-drift-only`, includes disallowed paths, and gives a next action to rerun review for the current head.

### S4: Invalid semantic review disposition blocks freeze

Given the review record is missing, not `allow`, has a non-implementation kind, has invalid `semantic_review_disposition`, or reviewed validation summary does not match the retained validation summary
When `loom gate freeze check` runs for the Work Item
Then freeze blocks and reports that authored review approval is not consumable.

### S5: Closeout retained-review boundary stays explicit

Given a terminal closeout carrier PR needs retained review handling
When review/head binding is classified
Then ordinary implementation PR review binding remains strict, and any retained-review allowance is reported as closeout-specific evidence rather than as current-head implementation approval.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `tools/check_cli_contract.py` fresh review binding fixture.
  - S2 -> `tools/check_cli_contract.py` carrier-only drift fixture.
  - S3 -> `tools/check_cli_contract.py` stale/semantic drift fixture.
  - S4 -> `tools/check_cli_contract.py` invalid review/disposition fixture.
  - S5 -> local `pr-gate` / freeze evidence over closeout-specific retained review boundary, or structural coverage when hosted admission remains out of scope.
- Expected evidence locator: `.loom/specs/WI-1511/evidence-map.md`.
- Freshness rule: refresh after runtime edits, review record updates, PR body/head changes, generated runtime sync, or PR gate changes.
- Execution ledger acceptance locator: `.loom/progress/WI-1511.md`.

## Exceptions And Boundaries

- `carrier-only` means only locally allowed Loom carrier paths changed after review; implementation source, workflow, test, docs contract, or host metadata drift must not be silently accepted.
- `semantic_review_disposition` is evidence about authored review consumption, not a replacement for the review record itself.
- Raw runtime evidence, shadow evidence, CI success, GitHub review state, and PR prose remain non-authoritative for review approval.

## Acceptance Criteria

- [ ] A1: Gate freeze emits machine-readable review/head binding evidence.
- [ ] A2: Fresh and allowed carrier-only bindings pass with full binding details.
- [ ] A3: Stale semantic drift and invalid review/disposition inputs block with disallowed paths and next action.
- [ ] A4: CLI contract tests cover pass and fail-closed review/head binding cases.
- [ ] A5: Generated runtime copies and Loom carriers remain synchronized.
