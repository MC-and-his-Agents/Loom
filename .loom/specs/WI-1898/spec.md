# Spec

## Suite Contract

- Suite path: not_applicable
- Formal-suite not_applicable: rationale: WI-1898 is a docs-only contract freeze for repo/global artifact classification; it does not introduce runtime behavior, repository mutation, gate behavior, migration apply, release behavior, or host/plugin installation behavior. consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, merge-ready, issue closeout, and FR #1897 consumption may consume this locator only as the formal suite path decision; fact-chain, current-head review, PR metadata/head binding, local validation, hosted checks, no-release judgment, controlled merge, and closeout evidence remain required. recheck condition: require a minimal or full suite if this PR expands beyond docs contract wording, cross-links, and WI-1898 carriers, or starts implementing #1899, #1900, #1901, #1908, runtime path resolution, repository mutation, gate parser behavior, migration apply, release mechanics, permissions, or external-visible host actions. scope proof: `git diff origin/main...HEAD` must remain limited to WI-1898 carriers and repo/global artifact classification documentation. review requirement: current_head_review_required.
- Consumes:
  - Work Item / FR locator: issue #1898 / FR #1897 / Phase #1888
  - Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; issue #1898 is already scoped as a contract Work Item.
  - Story scenario locator, or not-required rationale: not required; scenarios below are contract-consumption scenarios.
  - Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; this is an internal operating-layer contract.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: docs contract and adoption cross-links are readable and non-conflicting; formal suite artifact discovery is explicitly skipped.
- Locator:
  - Spec locator: .loom/specs/WI-1898/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1898; docs/adoption/installation-taxonomy.md; docs/adoption/global-cli-user-plugin-contract.md; docs/adoption/host-adapter-matrix.md
  - Freshness rule: Recheck when repo/global artifact authority, runtime cache paths, or workstation registry semantics change.

## Goal

Freeze a single repo/global artifact classification contract that later Work Items can consume when moving workstation-only runtime, tmp, checks, and long diagnostic artifacts out of adopted repositories.

The required outcome is clear: repository truth remains versioned in the target repository, while global `~/.loom/repos/<repo-id>/` cache is only an accelerator for local recovery, diagnostics, and batch planning.

## Scope

- In scope:
  - Add the authoritative repo/global artifact classification contract under `docs/methodology/harness/`.
  - Define which artifact classes stay in repository truth and which may move to workstation global cache.
  - Define allowed repo carrier summaries and global artifact locators.
  - Link the contract from installation taxonomy, global CLI/user plugin contract, host adapter matrix, and harness README.
- Out of scope:
  - Runtime path resolver implementation.
  - Cache migration commands.
  - Gate implementation changes.
  - Legacy residue removal.
  - Workstation upgrade orchestrator behavior.

## Key Scenarios

### Scenario S1

Given an adopted repository contains Loom truth carriers

When a future migration classifies `.loom/` artifacts

Then Work Item, progress, status, review, spec suite, installed-state, companion, and closeout truth remain repository-owned and versioned.

### Scenario S2

Given an artifact only serves local recovery, diagnostics, long output retention, or batch planning

When a future implementation stores it under `~/.loom/repos/<repo-id>/`

Then the repository keeps at most a summary, command, head or merge binding, hash, global locator, and freshness rule.

### Scenario S3

Given a gate, doctor, resume, or upgrade planner can see global cache

When repository truth or host readback is missing, stale, or mismatched

Then the global cache does not satisfy adoption, review, merge-ready, closeout, or release truth and the consumer falls back to repository-local validation.

## Behavior Evidence

- Story scenario mapping: not required; S1-S3 are direct contract scenarios.
- Story readiness locator or not-required rationale: not required; scoped docs-only Work Item.
- Story business confirmation locator or not-required rationale: not required; internal operating-layer semantics.
- Scenario coverage:
  - S1 -> docs/methodology/harness/repo-global-artifact-classification.md#classification-matrix
  - S2 -> docs/methodology/harness/repo-global-artifact-classification.md#repo-carrier-shape-after-slimdown
  - S3 -> docs/methodology/harness/repo-global-artifact-classification.md#consumer-boundary
- Expected evidence locator: .loom/specs/WI-1898/evidence-map.md
- Freshness rule: Recheck before review, merge-ready, and closeout; stale if any linked adoption or host adapter contract changes this boundary.
- Execution ledger acceptance locator: .loom/specs/WI-1898/spec.md#acceptance-criteria
- Not-required rationale, if this is not a behavior-bearing change: not required; this is a behavior-bearing contract for future commands.

## Exceptions And Boundaries

- Failure modes:
  - Global cache is treated as repository truth.
  - Repo carriers retain long logs or raw runtime payloads.
  - Workstation registry entries are treated as adoption or closeout proof.
  - Linked adoption docs redefine the same boundary differently.
- Operational boundaries:
  - Global cache may be absent without making repository truth invalid.
  - Consumers must fail closed on hash, head, locator, or freshness mismatch.
- Rollback or fallback expectations:
  - Revert docs-only contract if it conflicts with implementation evidence before later Work Items consume it.

## Acceptance Criteria

- [x] A1: A single harness contract defines repo-owned truth versus global workstation cache artifacts.
- [x] A2: Installation taxonomy references the contract and keeps adoption truth separate from cache/provider state.
- [x] A3: Global CLI/user plugin contract references the cache boundary without making cache a plugin or adoption authority.
- [x] A4: Host adapter matrix states adapters may use global cache only as diagnostics/planning acceleration.
- [x] A5: Suite evidence and carrier validation can consume the contract without requiring implementation or release behavior.
