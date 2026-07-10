# WI-1800 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1800 is a release convergence PR for an already-authored GitHub issue tree. The behavior contracts are the existing Loom CLI/gate surfaces and the #1793-#1799/#1801/#1803/#1804 issue bodies; the PR implements and validates those surfaces without introducing a new product scenario language that would benefit from a full suite.
- Consumer Boundary: review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, #1802 release tracker, and #1800 parent closeout.
- Recheck Condition: Require a full suite if the scope expands beyond the named issue tree, changes external permissions, introduces a new host adapter, changes release authority, or adds new user-facing product workflow semantics not already represented by the issue tree.
- Scope Proof: PR #1816 remains limited to target/context resolution, global-cli metadata-only bootstrap and CI verification, active-ruleset strong detector, adversarial adoption evidence, audited repair-pr evidence, runtime parity, release readiness for v0.21.2, merge wrapper target/readback behavior, opaque Work Item ID compatibility, generated/runtime parity, demo fixture sync, and WI-1800 carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: the controlling product and governance decomposition lives in the GitHub issue tree and this PR's release evidence, not in a new formal story/spec package. consumer boundary: suite validate, review, PR gate, hosted CI, release judgment, controlled merge, publish, and closeout may consume this minimal suite while still requiring fact-chain, current-head review, PR metadata, release judgment, hosted checks, and post-release readback. recheck condition: require full suite artifacts if the issue tree or PR scope expands into new host permissions, external writes, a new release authority model, or new user-facing workflow semantics.

## Scenarios

- S1: Global CLI metadata-only bootstrap and verify paths do not depend on repo-local `.loom/bin` or Codex Desktop runtime cache.
- S2: Target and workspace resolution stays anchored to invocation cwd across root CLI, shared runtime scripts, retained idle fallback, purity checks, and merge wrapper entrypoints.
- S3: Strong governance detector consumes active ruleset required checks, fails closed on ruleset read failure, and consumes fresh adversarial adoption evidence.
- S4: Repair PR mode records auditable evidence without mutating GitHub rulesets or bypassing gates.
- S5: Runtime parity and packaging surfaces agree for source, generated skills, plugin payload, `.loom/bin`, npm package, and v0.21.2 release metadata.
- S6: Metadata-only PR/merge surfaces accept non-empty path-safe opaque Work Item IDs without requiring a `WI-`, `INIT-`, issue, or `GH-` prefix.

## Acceptance

- [x] A1: Focused target/context, checkpoint alias, retained idle, and package-wrapper tests pass.
- [x] A2: Adoption-host metadata, merge-wrapper, controlled-merge, release-readback, gate-repair-pr, pr-gate-target-readback, governance-closeout, and runtime-copy-parity contracts pass.
- [x] A3: Release surface, npm package, package smoke, skills release-check, root verify, runtime parity, adversarial adoption record, and source `loom_check` pass locally.
- [x] A4: Demo bootstrap fixture drift is refreshed after runtime changes.
- [ ] A5: PR #1816 hosted checks, PR gate, current-head review consumption, controlled merge, `v0.21.2` release workflow, release readback, #1802 closeout, and #1800 parent closeout pass.

- Failure modes:
- Operational boundaries:
- Rollback or fallback expectations:

## Acceptance Criteria

- [ ] A1: Target outcome is observable
- [ ] A2: Key scenarios are covered
- [ ] A3: Important boundary behavior is defined
- [ ] A4: Validation evidence is identified
- [ ] A5: Behavior evidence can be consumed by review, merge-ready, and closeout
