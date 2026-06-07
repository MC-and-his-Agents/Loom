# WI-1323 Spec

- Suite path: minimal

- Full-suite-artifacts not_applicable: rationale: WI-1323 is a bounded regression-fixture Work Item whose upstream product and gate contracts are already frozen by #1316/#1317 and whose carrier/parser/gate behavior is already implemented and closed out by #1321/#1322; a full suite index, research, contracts, and readiness checklist would duplicate those sources for this fixture-only slice. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, controlled merge, and closeout consume this minimal suite with targeted fixture evidence; fact-chain, current-head review, PR metadata/readback, no-release judgment, PR gate, hosted checks, controlled merge, and post-merge closeout remain required. recheck condition: require a full suite if scope expands beyond targeted fixtures/test helpers and WI-1323 carriers into gate contract/schema redesign, runtime behavior, release mechanics, permissions, external-visible actions, or #1324 parent/final closeout. scope proof: `git diff origin/main...HEAD` must remain limited to `tools/check_cli_contract.py` targeted fixture/test-helper changes and WI-1323 carrier/review/status evidence. review requirement: `.loom/reviews/WI-1323.json` must approve the current PR head before merge-ready.

## Scenarios

### Scenario S1

Given PR metadata declares the legal docs-governance light field set with complete suite bypass rationale, `release_judgment=no_release`, and current-head review requirements
When the suite marker records the matching formal-suite bypass decision and the review/head/merge checkpoint are current
Then suite validate can return the bypass result and pr-gate can pass while preserving fact-chain, review, metadata/readback, PR gate, controlled merge, and closeout requirements.

### Scenario S2

Given a PR tries to use the light suite-bypass path for runtime/code, fixture, release-impacting docs, missing rationale, blocking release judgment, or suite/metadata mismatch
When the metadata preflight or pr-gate consumes the machine carrier
Then the result is `block` and the carrier is treated as invalid gate input, not advisory text.

### Scenario S3

Given PR body metadata, PR head, branch, carrier fields, and review head are expected to bind the same execution object
When readback drift, carrier/head mismatch, PR body branch mismatch, or stale review is present
Then the gate fails closed before controlled merge.

## Acceptance Criteria

- AC-1: docs-governance light suite-bypass positive fixture passes targeted suite/pr-gate behavior.
- AC-2: runtime/code high-risk light abuse, fixture high-risk light abuse, release-impacting docs light abuse, old head review, missing rationale, PR body/readback mismatch, carrier/head mismatch, and suite/metadata mismatch block through real gate commands.
- AC-3: Targeted fixture tests, suite validate, pr-gate dry checks, git diff --check, no-release evidence, current-head review, hosted checks, controlled merge, and post-merge closeout evidence are recorded.
- AC-4: The implementation does not lower gate strictness, redesign the metadata schema, fabricate formal suite artifacts, or advance #1324 parent/final closeout.
