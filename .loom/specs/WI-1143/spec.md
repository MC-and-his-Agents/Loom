# Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: #1143 is a narrow reconciliation consumer Work Item that maps existing suite gate failure taxonomy into reconciliation findings; consumer boundary: reconciliation, closeout, review, and merge-ready may consume this minimal suite evidence without treating skipped full path artifacts as completed; recheck condition: #1143 starts defining new CLI product scope, new consistency analyzer output, or new host mutation semantics.
- Consumes:
  - Work Item / FR locator: #1143 / #1136
  - Story Readiness source: GitHub Work Item body is the scoped carrier.
  - Story scenario source: scenarios are authored below.
  - Story Business Confirmation source: governance behavior only, with no business-semantics carrier.
- Produces:
  - Scenario ids / locators: S1-S4 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: reconciliation audit exposes suite drift findings for closeout consumers.
- Locator:
  - Spec locator: .loom/specs/WI-1143/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1143, #1136, docs/methodology/harness/full-spec-suite-cli-surface.md, docs/methodology/harness/gate-chain.md
  - Freshness rule: re-run reconciliation, closeout, and CLI contract checks after changing taxonomy mapping.

## Goal

- Make reconciliation audit classify suite-related closeout drift instead of only reporting generic host/control-plane drift.
- Preserve existing reconciliation findings for parent, project, merge, host, and dependency drift.

## Scope

- In scope: suite gate consumption inside reconciliation audit, suite drift finding mapping, missing suite gate fallback, CLI contract assertions, and generated skills runtime copies.
- Out of scope: new reconciliation host writes for suite drift, new consistency analyze implementation, changing existing parent/project/merge drift semantics, or adding source-specific command/layout surfaces.

## Key Scenarios

### Scenario S1

Given
- a closeout context has suite evidence validation blocking with stale evidence

When
- reconciliation audit consumes the suite gate

Then
- reconciliation emits a blocking `suite_stale_evidence` finding that preserves the original `stale_evidence` failure kind.

### Scenario S2

Given
- suite evidence is bound to an old current head, reviewed head, PR head, or merge basis

When
- reconciliation audit classifies the suite gate result

Then
- reconciliation emits a blocking `suite_head_or_pr_drift` finding.

### Scenario S3

Given
- a suite carrier has a host/project/checklist/PR truth conflict

When
- reconciliation audit classifies the suite carrier validation result

Then
- reconciliation emits a blocking `suite_host_state_conflict` finding without replacing existing host drift taxonomy.

### Scenario S4

Given
- suite gate evidence is required but unreadable or missing

When
- reconciliation audit runs before closeout

Then
- reconciliation emits a blocking `missing_suite_gate` finding and routes back to suite/fact-chain repair.

## Behavior Evidence

- Story scenario mapping: S1-S4 are issue-scoped and authored in this file.
- Story readiness locator: #1143 body is the readiness source.
- Story business confirmation locator: none required for this governance-only behavior.
- Scenario coverage:
  - S1 -> expected behavior evidence locator: `suite_gate_reconciliation_findings` stale evidence mapping.
  - S2 -> expected behavior evidence locator: `suite_gate_reconciliation_findings` head/PR drift mapping.
  - S3 -> expected behavior evidence locator: `suite_gate_reconciliation_findings` host carrier conflict mapping.
  - S4 -> expected behavior evidence locator: `suite_gate_reconciliation_findings` missing suite gate fallback.
- Expected evidence locator: .loom/specs/WI-1143/evidence-map.md
- Freshness rule: evidence is fresh only after local reconciliation/contract checks pass on the current head.
- Execution ledger acceptance locator: .loom/progress/WI-1143.md
- Behavior-bearing change rationale: reconciliation audit behavior changes and is covered by S1-S4.

## Exceptions And Boundaries

- Failure modes: stale evidence, head/PR drift, host carrier conflict, missing suite gate, unreadable host state, and existing project/parent/merge drift fail closed according to their existing owner.
- Operational boundaries: suite drift findings are audit evidence only; they do not create new `reconciliation sync` host actions.
- Rollback or fallback expectations: revert reconciliation suite mapping and rerun contract checks if audit blocks valid closeout contexts.

## Acceptance Criteria

- [ ] A1: Reconciliation audit can include `suite_gate_validation` when the audited issue has a retained Work Item suite.
- [ ] A2: Stale suite evidence maps to a blocking `suite_stale_evidence` finding with original `stale_evidence` evidence.
- [ ] A3: Head/PR drift maps to a blocking `suite_head_or_pr_drift` finding.
- [ ] A4: Host carrier/state conflict maps to a blocking `suite_host_state_conflict` finding while existing reconciliation taxonomy remains unchanged.
- [ ] A5: Missing or unreadable suite gate evidence maps to `missing_suite_gate` and does not create host writes.
