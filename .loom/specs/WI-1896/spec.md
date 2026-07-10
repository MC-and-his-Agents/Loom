# WI-1896 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md; rationale: WI-1896 is a focused workstation registry fail-closed hardening over an already-scoped CLI command surface; consumer boundary: suite validate, review, PR gate, merge-ready, and closeout for WI-1896; recheck condition: require full suite artifacts if the work expands into workstation upgrade orchestration, global runtime cache migration, target repository mutation, or release behavior.
- Consumes:
  - Work Item locator: https://github.com/MC-and-his-Agents/Loom/issues/1896
  - FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1893
  - Story Readiness consumed state: not required; rationale: #1896 is a bounded implementation Work Item with concrete negative registry fixtures; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if the scope changes to user-facing upgrade workflow design.
  - Story Business Confirmation consumed state: not required; rationale: this changes internal CLI safety behavior and does not alter business semantics; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if repository mutation policy or upgrade UX semantics change.
- Produces:
  - Scenario ids / locators: S1 missing path, S2 remote hash drift, S3 duplicate id.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: workstation registry CLI implementation and focused contract fixture.
- Locator:
  - Spec locator: `.loom/specs/WI-1896/spec.md`
- Provenance:
  - Source issue / PR / doc locator: #1896, #1893, docs/adoption/workstation-registry-contract.md, docs/evidence/fixtures/workstation-registry-fixtures.json.
  - Freshness rule: rerun validation after workstation registry code, docs, fixtures, PR metadata, review, hosted-check, or closeout evidence changes.

## Scenarios

### S1: Missing path fails closed

Given the workstation registry contains an opted-in repository entry whose stored path is gone,
When the operator runs `loom workstation list --json`,
Then the command returns `block`, classifies `path_missing`, excludes the entry from planning, and reports repair guidance.

### S2: Remote hash drift fails closed

Given the workstation registry contains an opted-in repository entry whose current `remote.origin.url` hash differs from the stored hash,
When the operator runs `loom workstation list --json` or tries to register another repository,
Then the command fails closed with `remote_hash_drift`, excludes the entry from planning, and refuses further register writes until repair.

### S3: Duplicate id fails closed

Given the workstation registry contains the same repo id for two different path/remote identities,
When the operator runs `loom workstation list --json`,
Then the command returns `block`, classifies `repo_id_conflict`, excludes the id from planning, and reports manual repair guidance.

## Acceptance

- [x] A1: Missing path entries fail closed with repair guidance and no planning eligibility.
- [x] A2: Remote hash drift fails closed with repair guidance and register refusal while drift is present.
- [x] A3: Duplicate repo ids fail closed with manual repair guidance and no planning eligibility.
- [x] A4: Opted-out entries remain non-blocking list-only diagnostics.
- [x] A5: Behavior evidence can be consumed by review, merge-ready, and closeout.
