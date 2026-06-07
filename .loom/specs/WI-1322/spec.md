# WI-1322 Spec

- Suite path: minimal

- Full-suite-artifacts not_applicable: rationale: WI-1322 is a narrow gate implementation slice with issue #1322, the frozen #1319 checklist, #1316/#1317 gate contract, #1320 inventory, and #1321 metadata carrier already defining the upstream product/contract context; full suite index, research, contracts, and readiness checklist would duplicate those sources for this implementation batch. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, controlled merge, and closeout consume the minimal suite plus targeted fixtures and carrier evidence; fact-chain, current-head review, PR metadata/readback, no-release judgment, controlled merge, and post-merge closeout remain required. recheck condition: require a full suite if scope expands into #1323 fixture matrix, #1324 parent closeout, release mechanics, external-visible behavior, runtime provider behavior, review engine behavior, broad merge strategy, or new downstream machine-consumed fields beyond the documented surface clarification. scope proof: `git diff origin/main...HEAD` must remain limited to docs-governance lite gate consumption, targeted fixtures/tests, contract clarification, runtime copy sync, and WI-1322 carriers. review requirement: `.loom/reviews/WI-1322.json` must approve the current PR head before merge-ready.

## Scenarios

### Scenario S1

Given PR metadata declares the docs-governance lite field set with complete formal-suite bypass rationale, `release_judgment=no_release`, and required non-suite gate fields
When the repo suite marker records the matching formal-suite bypass decision
Then suite validate can return the bypass result and pr-gate can pass only after fact-chain, current-head review, PR metadata binding, and merge checkpoint requirements pass.

### Scenario S2

Given a PR declares docs-governance lite metadata
When metadata conflicts with the repo suite marker, omits the not-applicable rationale, uses an old head review, mismatches PR head/body binding, declares unknown or high-risk governance values, or defers release judgment
Then the gate fails closed instead of treating the light path as advisory.

### Scenario S3

Given the PR metadata machine carrier is declared once for `surface: merge_ready`
When pre-review or review preflight is required before merge-ready
Then the gate consumes the same merge-ready carrier early without requiring a second review-surface machine block.

## Acceptance Criteria

- AC-1: A docs-governance lite formal-suite bypass positive fixture passes suite validate and pr-gate.
- AC-2: Runtime/code change, missing rationale, old head review, PR body/head mismatch, unknown governance intensity, high-risk change class, and deferred release judgment block through targeted fixtures or existing gate checks.
- AC-3: Current-head review, fact-chain, PR metadata/readback, no-release judgment, PR gate, controlled merge, and closeout remain required; docs-governance lite only narrows formal suite artifacts.
- AC-4: Review/pre-review metadata preflight can consume the single declared merge-ready governance carrier without inventing undocumented fields.
