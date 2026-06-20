# WI-1495 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1495/WI-1496 is a narrow resolver fixture and documentation hardening change for an already implemented closeout resolver path. consumer boundary: review, PR gate, closeout, and downstream adoption documentation checks consume this minimal suite plus evidence map. recheck condition: require full suite artifacts if scope expands into resolver semantics, migration behavior, release behavior, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1495 and https://github.com/MC-and-his-Agents/Loom/issues/1496
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue bodies and milestone/11 planning review are the source for this closeout hardening item.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: retained closeout resolver fixture plus metadata-only adoption guidance.
- Locator:
  - Spec locator: .loom/specs/WI-1495/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issues #1495/#1496 and PR #1663.
  - Freshness rule: recheck after retained-item lookup, closeout gate wording, host action contract wording, generated mirrors, or PR metadata changes.

## Key Scenarios

- S1: Closeout resolver lookup prefers canonical `WI-<issue>` retained Work Item identity when retained closeout metadata could otherwise be ambiguous.
- S2: Governance closeout contract fixtures exercise retained-item auto lookup without forcing callers to pass an explicit item id.
- S3: Downstream adoption documentation states metadata-only + global CLI/plugin migration and does not reintroduce repo-local runtime, plugin, skills, single-skill package, or legacy installer paths.

## Acceptance Criteria

- A1: `test/retained_item_lookup_test.py` includes a canonical `WI-<issue>` preferred fixture and passes.
- A2: `tools/check_cli_contract.py --surface governance-closeout` passes with the retained-item auto lookup fixture.
- A3: Generated skill/reference mirrors remain synchronized after closeout/host-action contract wording changes.
- A4: PR gate can consume WI-1495 minimal suite, evidence map, task carrier, and current-head review artifacts.
