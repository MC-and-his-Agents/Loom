# WI-1890 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1890 is a narrow checker and adoption-contract clarification under FR #1889, not a new user workflow or multi-module runtime feature; consumer boundary: suite validate, review, PR gate, marketplace-catalog follow-up #1891, and closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this work expands into actual marketplace catalog publication, workstation plugin installation, or downstream repo migration behavior.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1890
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1889
  - Parent Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1888
  - Story Readiness consumed state: not required for this checker-contract WI; rationale: the GitHub issue tree and this milestone discussion define the scope; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require story readiness if user-facing installation behavior is added.
  - Story Business Confirmation consumed state: not required for this checker-contract WI; rationale: the accepted outcome is captured by #1889/#1890; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require business confirmation if adoption semantics change for downstream repositories.
- Produces:
  - Scenario ids / locators: S1 published catalog accepted, S2 repo-local installed state remains blocked, S3 generated surfaces stay consistent.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: checker fixture behavior plus adoption-contract documentation and generated payload parity.
- Locator:
  - Spec locator: `.loom/specs/WI-1890/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1888, #1889, #1890, milestone #25 planning discussion.
  - Freshness rule: rerun validation after checker logic, adoption-contract docs, generated skills surface, runtime copy, or plugin payload metadata changes.

## Goal

Make Loom's checker and adoption contracts distinguish a source-repository published Codex marketplace catalog from repo-local installed marketplace state.

The outcome must unblock #1891 from adding a deterministic Loom marketplace catalog while preserving the existing rule that downstream repositories must not use `.agents/plugins/marketplace.json` as installed-state truth.

## Scope

- In scope:
  - Update the source self-plugin checker to allow only the Loom source repository's deterministic published catalog shape.
  - Keep blocking repo-local installed-state/cache-like marketplace data.
  - Add checker fixture coverage for valid published catalog and invalid local/absolute installed-state-like catalog.
  - Update adoption/install-boundary docs to name the published catalog as distribution metadata, not installed state.
  - Regenerate skills/runtime/plugin payload metadata required by the checker change.
  - Add WI-1890 suite and recovery carriers.
- Out of scope:
  - Adding the actual `.agents/plugins/marketplace.json` catalog. That belongs to #1891.
  - Implementing workstation registry, global runtime cache, workstation upgrade orchestration, or legacy migration.
  - Changing Codex marketplace installation behavior.
  - Recording machine-local plugin installation state in the repository.

## Key Scenarios

### Scenario S1

Given the Loom source repository publishes a catalog at `.agents/plugins/marketplace.json`

When the catalog contains exactly the Loom plugin entry pointing to `./plugins/loom` as distribution metadata

Then the source checker accepts it as a published marketplace catalog rather than installed marketplace state.

### Scenario S2

Given a repository contains marketplace data that records installed/enabled/cache state or points outside the source repository

When the checker validates that marketplace data

Then the checker fails closed and preserves the boundary against repo-local installed state.

### Scenario S3

Given the checker source changes

When generated skills surfaces, runtime copy parity, and plugin payload metadata are validated

Then all shipped copies and payload metadata remain consistent for review and release consumers.

## Behavior Evidence

- Story scenario mapping: no separate story artifact; #1890 is a governance/checker contract Work Item.
- Story readiness locator or rationale: no separate story artifact exists; #1889/#1890 provide the accepted scope; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require story readiness if user-facing installation behavior is added.
- Story business confirmation locator or rationale: business semantics are limited to the accepted marketplace/install-boundary distinction in #1889/#1890; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require business confirmation if adoption semantics change for downstream repositories.
- Scenario coverage:
  - S1 -> checker fixture inside `src/skills/shared/scripts/loom_check.py`
  - S2 -> checker fixture inside `src/skills/shared/scripts/loom_check.py`
  - S3 -> skills surface, runtime copy parity, plugin payload hash, and source loom_check validation.
- Expected evidence locator: `.loom/specs/WI-1890/evidence-map.md`
- Freshness rule: refresh validation after any checker, docs, generated surface, runtime copy, payload metadata, PR body, review, or hosted-check change.
- Execution ledger acceptance locator: `.loom/progress/WI-1890.md`

## Exceptions And Boundaries

- Failure modes:
  - If a catalog has workstation installed-state or cache-like fields, fail closed.
  - If a catalog points outside `./plugins/loom` in the Loom source repository, fail closed.
  - If generated checker copies drift, treat validation as stale.
- Operational boundaries:
  - This WI defines allowance semantics only; #1891 owns creating the actual published catalog file.
  - Downstream target repositories still cannot use `.agents/plugins/marketplace.json` as plugin installation truth unless a future contract explicitly permits it.
- Rollback or fallback expectations:
  - Revert checker/docs/generated metadata changes before PR merge if the published catalog shape proves incompatible with Codex marketplace parsing.

## Acceptance Criteria

- [ ] A1: Source checker accepts the deterministic published Loom marketplace catalog shape.
- [ ] A2: Source checker rejects marketplace installed-state/cache-like fields and paths outside `./plugins/loom`.
- [ ] A3: Adoption docs distinguish published catalog distribution metadata from repo-local installed state.
- [ ] A4: Generated skills/runtime/plugin payload metadata remain in sync.
- [ ] A5: Validation evidence can be consumed by review, merge-ready, #1891, and closeout.
