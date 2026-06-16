# Readiness Checklist

## Contract

- Schema marker: loom-full-suite-readiness/v1
- Consumes:
  - Suite index locator: .loom/specs/WI-1235/suite-index.md
  - Spec locator: .loom/specs/WI-1235/spec.md
  - Plan locator: .loom/specs/WI-1235/plan.md
  - Research locator, or `not required` rationale: .loom/specs/WI-1235/research.md
  - Contracts locator, or `not required` rationale: .loom/specs/WI-1235/contracts.md
- Produces:
  - Readiness verdict: ready-for-review
  - Blocking gaps: PR/review/merge-ready/merge/issue closeout still pending.
  - Evidence locators: .loom/specs/WI-1235/evidence-map.md
- Locator:
  - Readiness checklist locator: .loom/specs/WI-1235/readiness-checklist.md
- Provenance:
  - Source suite artifact locators: WI-1235 suite files.
  - Freshness rule: Refresh after any PR head, validation, review, or gate input change.

## Readiness Verdict

- Verdict: ready
- Blocking gaps: none for local implementation readiness; host PR/review/merge-ready/merge/closeout remain pending downstream gates.
- Evidence locator: .loom/specs/WI-1235/evidence-map.md
- Freshness rule: rerun suite/fact-chain/PR checks after carrier or code changes.

## Checklist

- [x] Suite index is current.
- [x] `spec.md` scenario ids / locators are present.
- [x] `spec.md` acceptance ids / locators are present.
- [x] `plan.md` maps every required scenario to automated, manual, structural, or `not required` validation.
- [x] `plan.md` maps every required acceptance item to test evidence, structural check, manual evidence, or `not required`.
- [x] Research decisions are resolved, deferred, or explicitly `not required`.
- [x] Contract deltas are declared, or explicitly `not required`.
- [x] Generated / skills integration needs are recorded for #1020 when relevant.
- [x] This checklist does not author `next_step`, `blockers`, or `latest_validation_summary`.

