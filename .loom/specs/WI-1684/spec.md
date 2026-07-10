# WI-1684 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1684 is a bounded runtime vocabulary and fixture hardening change rather than a new workflow, release, or host-write design. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, evidence map, task carrier, and focused validation output. recheck condition: require full suite artifacts if scope expands into `loom ship`, host mutation behavior, release packaging, or public CLI command design.
- Work Item / FR locator: issue #1684 under FR #1681.
- Scenario locators: S1, S2.
- Acceptance locators: A1, A2, A3.
- Spec locator: .loom/specs/WI-1684/spec.md
- Provenance: GitHub issue #1684.
- Freshness rule: Recheck if change classes, PR metadata fields, or gate behavior change.

## Goal

Prevent high-risk change classes from passing as `light` governance while preserving the low-risk `docs_only`, `docs_governance`, and bounded `fixture` paths.

## Scope

- In scope: governance intensity change-class vocabulary, high-risk classification, focused metadata and PR gate fixtures, generated skills/plugin mirrors, and the tiered gate contract.
- Out of scope: `loom ship`, PR backlink repair, closeout policy, release packaging, and new host writes.

## Scenarios

### S1: High-Risk Classes Cannot Use Light

Given PR metadata declares `governance_intensity: light`
When `change_class` is `workflow`, `metadata_schema`, `host_write`, or `permissions`
Then metadata preflight and PR gate block the carrier instead of treating it as a low-risk path.

### S2: Existing Light Paths Still Work

Given PR metadata declares a valid low-risk light class
When the suite path and required review/release fields match the class
Then the existing positive fixtures continue to pass.

## Acceptance Criteria

- [ ] A1: `workflow`, `metadata_schema`, `host_write`, and `permissions` are legal change classes.
- [ ] A2: those classes are high-risk for attempted `light` governance.
- [ ] A3: targeted and aggregate CLI contract checks pass.
