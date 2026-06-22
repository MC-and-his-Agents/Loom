# WI-1696 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1696 is a release closeout Work Item with a narrow version-authority and evidence scope. It does not introduce new runtime behavior beyond publishing the already merged intensity-aware ship path.
- Consumer Boundary: review, PR gate, release judgment, controlled merge, release workflow, release readback, and phase closeout.
- Recheck Condition: Re-run release/package validation after any change to VERSION, package.json, release workflow, package payload, release evidence, or Work Item carriers.
- Scope Proof: Changes are limited to root CLI release authority, WI-1696 carriers, and release readiness evidence.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1696 is a bounded release closeout slice for an already implemented milestone and is fully reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, release readback, and package validation. consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, phase closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed. recheck condition: require full suite artifacts if this work expands into new product behavior, release workflow semantics, npm publish mechanics, host permissions, external credentials, or a multi-release migration.

## Scenarios

- S1: The release PR advances root Loom CLI authority from v0.17.1 to v0.18.0.
- S2: Release readiness evidence consumes all milestone #15 FR/Work Item outcomes and confirms v0.18.0 is unoccupied before merge.
- S3: After merge, the main-push release workflow publishes tag, GitHub Release, and npm package, then readback supports closing #1696 and #1680.

## Acceptance

- A1: `VERSION` is `v0.18.0` and `package.json` is `0.18.0`.
- A2: `docs/evidence/v0.18.0-release-readiness.md` records scope, consumed behavior, validation, publish boundary, and post-merge closeout contract.
- A3: Release/package validation passes at PR head.
- A4: Suite, fact-chain, state-check, review, PR metadata, hosted checks, and PR gate are consumable.
- A5: Post-merge release readback passes before #1696 and #1680 close.
