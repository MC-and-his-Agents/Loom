# WI-1495 Plan

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: The implementation is already scoped to fixture and documentation hardening; the minimal suite records review/gate evidence without adding a larger formal suite. consumer boundary: review, PR gate, closeout, and #1496 downstream adoption docs consume this plan. recheck condition: require full suite artifacts if scope expands into resolver semantics, migration behavior, release behavior, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1495 and https://github.com/MC-and-his-Agents/Loom/issues/1496
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue bodies and milestone/11 planning review.
  - Story scenario locator, or skip rationale: scenarios are mapped in the spec.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in `.loom/specs/WI-1495/spec.md`.
  - Acceptance ids / locators: A1-A4 in `.loom/specs/WI-1495/spec.md`.
  - Behavior evidence expectation: retained closeout resolver fixture plus metadata-only adoption guidance.
- Locator:
  - Plan locator: .loom/specs/WI-1495/plan.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issues #1495/#1496 and PR #1663.
  - Freshness rule: recheck after retained-item lookup, closeout gate wording, host action contract wording, generated mirrors, or PR metadata changes.

## Phases

- P1: Add canonical retained-item lookup fixture coverage for `WI-<issue>` identity binding.
- P2: Update governance closeout CLI contract fixtures to cover retained-item auto lookup.
- P3: Update closeout gate and host action contract guidance, then refresh generated/plugin mirrors.
- P4: Add Loom carriers, review artifacts, PR metadata, and local gate evidence for PR #1663.

## Scenario Validation Mapping

- S1 -> automated: `test/retained_item_lookup_test.py` validates canonical retained item identity binding.
- S2 -> automated: `tools/check_cli_contract.py --surface governance-closeout` validates closeout fixture auto lookup.
- S3 -> automated: `tools/skills_surface.py check --surface generated-tree-drift` validates generated/reference mirror synchronization.

## Acceptance Test Mapping

- A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/retained_item_lookup_test.py`.
- A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`.
- A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`.
- A4 -> test evidence: suite validate, suite evidence validate, suite carrier validate, fact-chain, shadow-parity, and PR gate.
