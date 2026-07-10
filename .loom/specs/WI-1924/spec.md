# WI-1924 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md; rationale: WI-1924 is a bounded closeout gate regression repair with an existing failing live closeout status and focused contract fixture; consumer boundary: suite validate, review, PR gate, merge-ready, closeout status for WI-1924, and WI-1895 carrier-sync closeout evidence; recheck condition: require full suite artifacts if the fix expands into new closeout workflow semantics, repository migration behavior, or release policy.
- Consumes:
  - Work Item locator: https://github.com/MC-and-his-Agents/Loom/issues/1924
  - Regression evidence locator: https://github.com/MC-and-his-Agents/Loom/issues/1895 and PR #1923 closeout status failure.
  - Story Readiness consumed state: not required for this bounded gate bug fix; rationale: the accepted behavior is defined by closeout role inputs and the real WI-1895 regression; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if user-facing workstation upgrade behavior changes.
  - Story Business Confirmation consumed state: not required; rationale: this changes only internal closeout gate evidence binding and does not alter product semantics; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if closeout policy or repository mutation semantics change.
- Produces:
  - Scenario ids / locators: S1 role-aware merge-ready binding, S2 current carrier/final host evidence binding, S3 legacy fallback.
  - Acceptance ids / locators: A1-A3 below.
  - Behavior evidence expectation: closeout gate code, focused governance-closeout fixture, wrapper surface, generated copy parity, and live WI-1895 carrier-sync closeout status.
- Locator:
  - Spec locator: `.loom/specs/WI-1924/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1924, #1895, #1923, milestone #25 execution discussion.
  - Freshness rule: rerun validation after any closeout gate, role argument, generated copy, PR metadata, review, hosted-check, or closeout evidence change.

## Scenarios

### S1: Role-aware merge-ready binding

Given closeout status is evaluating a `carrier_sync_pr` or `final_closeout_pr` and an `implementation_pr` role is provided,
When retained merge-ready execution evidence is checked,
Then it is compared to the implementation PR head, not the carrier/final PR head.

### S2: Current PR evidence remains current-bound

Given closeout status is evaluating that carrier/final PR,
When host checks and merge backlink evidence are checked,
Then they remain bound to the current carrier/final PR head.

### S3: Legacy fallback remains unchanged

Given no implementation PR role is provided,
When closeout status checks retained merge-ready evidence,
Then existing behavior remains unchanged and the evidence is compared to the current PR head.

## Acceptance

- [ ] A1: Carrier/final closeout PRs no longer fail solely because their head differs from the implementation PR merge-ready attempt head.
- [ ] A2: Implementation PR closeout behavior and legacy missing-attempt fallback remain unchanged.
- [ ] A3: Focused contract coverage proves the split binding.
