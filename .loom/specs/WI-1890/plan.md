# WI-1890 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1890 is a narrow checker and adoption-contract clarification with bounded generated-surface fallout; consumer boundary: suite validate, review, PR gate, follow-up #1891, and closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if the work expands into actual catalog publication, workstation plugin installation, or downstream migration behavior.
- Consumes:
  - Spec locator: `.loom/specs/WI-1890/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required for this checker-contract WI; rationale: #1890 is an issue-defined governance/checker contract slice; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require story readiness if user-facing installation behavior is added.
  - Story Business Confirmation consumed state: not required for this checker-contract WI; rationale: #1889/#1890 define the accepted marketplace/install-boundary business scope; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require business confirmation if adoption semantics change for downstream repositories.
- Produces:
  - Validation strategy by scenario: checker fixture behavior, docs contract review, generated surface/package consistency checks.
  - Test strategy by acceptance: focused checker fixture plus existing source/package/surface validations.
  - Fresh verification evidence expectation: `.loom/progress/WI-1890.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1890/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1890/spec.md`, #1890.
  - Freshness rule: refresh after checker, docs, generated surface, runtime copy, plugin payload metadata, PR metadata, review, or hosted-check changes.

## Implementation Goal

Deliver the #1890 contract slice that lets Loom publish a Codex marketplace catalog from the source repository while continuing to reject repo-local installed marketplace state.

Explicitly postponed to later issues: creating the marketplace catalog itself (#1891), documenting the complete install boundary (#1892), and all workstation/global-cache/orchestrator/migration FRs.

## Deferred Items

### Marketplace Catalog File

- Locator: #1891.
- Reason: #1890 only freezes checker semantics and documentation boundary; adding the actual catalog is the next Work Item.
- Activation condition: #1890 PR is merged or otherwise accepted by #1891.
- Does not currently block: validating checker acceptance/rejection semantics.
- Statement: deferred is not completed.

### Broader Installation Documentation

- Locator: #1892.
- Reason: #1890 updates the minimum contract language needed by the checker; end-user installation guidance remains separate.
- Activation condition: #1891 catalog exists or #1892 starts.
- Does not currently block: checker implementation.
- Statement: deferred is not completed.

## Skipped Items

### User Story Artifacts

- Locator: story readiness and business confirmation artifacts.
- Rationale: #1890 is a governance/checker contract slice whose accepted scope is the GitHub issue tree and milestone discussion.
- Recheck condition: require story artifacts if this expands into user-facing install/update behavior.
- Consumers that should not require it: suite validate, review, PR gate, and closeout for #1890.

## Phases

### Phase 1

- Objective: update checker and contracts.
- Deliverable: checker allows only the published Loom catalog shape and docs name the distribution-vs-installed boundary.
- Exit condition: focused compile/surface checks pass.

### Phase 2

- Objective: refresh generated/shipped surfaces.
- Deliverable: generated skills copies, runtime checker copy, and plugin payload metadata are consistent.
- Exit condition: skills surface, runtime parity, and plugin payload hash checks pass.

### Phase 3

- Objective: prepare for review and merge.
- Deliverable: WI-1890 suite/carriers, validation evidence, commit, PR, review, merge-ready, and closeout.
- Exit condition: PR merges and #1890 carrier/issue closeout consumes the final head/merge commit.

## Constraints

- Do not add `.agents/plugins/marketplace.json` in this WI.
- Do not record workstation installed/enabled/cache state in the repository.
- Do not implement global registry/cache/orchestrator/migration behavior.
- Keep checker semantics deterministic and limited to the Loom source repository's own plugin path.
- Keep generated copies and payload metadata aligned with source.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py .loom/bin/loom_check.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/loom_check.py`
  - `python3 tools/skills_surface.py check`
  - `python3 tools/check_npm_package.py --surface runtime-copy-parity`
  - `python3 tools/check_npm_package.py --surface plugin-payload-hash`
  - `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
  - `python3 tools/loom.py suite validate --target . --item WI-1890 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1890 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1890 --json`
  - `python3 tools/loom.py fact-chain --target . --item WI-1890 --json`
  - `git diff --check`
- Manual checks:
  - Review adoption docs for the published-catalog versus installed-state distinction.
  - Confirm no actual marketplace catalog file is added by #1890.
- Runtime evidence: not required for this WI because #1890 adds no catalog file and executes no marketplace install/runtime path; consumer boundary: review, PR gate, merge-ready, and closeout for #1890 may rely on checker/package evidence instead; recheck condition: require runtime evidence if #1890 starts executing Codex marketplace install behavior.
- Behavior evidence:
  - Checker fixture behavior embedded in the source checker and consumed by source `loom_check`.
- Story scenario to evidence mapping: no separate story artifact; see spec for issue-defined scenario mapping.
- Story readiness consumed: not required for this checker-contract WI; rationale: #1890 is an issue-defined governance/checker contract slice; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require story readiness if user-facing installation behavior is added.
- Story business confirmation locator or rationale: not required for this checker-contract WI; rationale: #1889/#1890 define the accepted marketplace/install-boundary business scope; consumer boundary: suite validate, review, PR gate, and closeout for #1890; recheck condition: require business confirmation if adoption semantics change for downstream repositories.
- Scenario validation mapping:
  - S1 -> automated: source `loom_check` fixture accepts valid published catalog.
  - S2 -> automated: source `loom_check` fixture rejects invalid outside-path catalog and checker rejects installed/cache-like keys.
  - S3 -> automated: skills surface, runtime parity, payload hash, and compile checks.
- Fresh verification evidence:
  - `.loom/progress/WI-1890.md`
- Execution ledger plan locator:
  - `.loom/specs/WI-1890/plan.md`
- Execution ledger validation evidence locator:
  - `.loom/specs/WI-1890/evidence-map.md`

## Test Strategy

- TDD or test-first expectation: preserve existing source-checker regression style by adding direct fixture behavior inside the checker contract check.
- Regression coverage to add or preserve: valid published catalog accepted; invalid outside-path catalog rejected; installed/cache-like marketplace fields rejected; generated surface parity preserved.
- Cases that are intentionally not automated: actual Codex marketplace installation is deferred to #1891/#1892 because no catalog file is added in #1890.
- How failing tests or equivalent checks will be introduced before implementation: checker fixture first exercises both allowed and rejected catalog shapes.
- How passing tests or equivalent checks will be captured as test evidence: local validation summary and evidence map consume source `loom_check` plus surface/package checks.
- Acceptance test mapping:
  - A1 -> test evidence: source `loom_check` fixture.
  - A2 -> test evidence: source `loom_check` fixture and checker review.
  - A3 -> structural check: adoption docs diff review.
  - A4 -> test evidence: skills surface/runtime parity/payload hash checks.
  - A5 -> structural check: suite/evidence/carrier/fact-chain validation.
- How User Story acceptance scenarios map to tests, checks, or manual validation:
  - No separate story artifact exists; #1890 consumes the issue tree as the behavior contract.

## Subagent Output Integration

- Owned outputs: none.
- Integration owner: main agent.
- Required evidence from each subagent: no subagent output was produced for this narrow serial WI.
- Review or reconciliation needed before merge-ready: main agent reviews checker/docs/generated payload consistency.
- Handoff notes locator or rationale: not required because the main thread owns implementation, validation, PR, and closeout without a handoff boundary; consumer boundary: review, PR gate, and closeout for #1890; recheck condition: require handoff notes if the work is paused or delegated.

## Dependencies

- Blocking inputs:
  - #1890 issue exists under #1889 and milestone #25.
- Required coordination:
  - #1891 must consume #1890 before adding the actual catalog file.
- Rollback boundary:
  - Before merge, revert checker/docs/generated metadata and remove WI-1890 carriers.
  - After merge, follow-up changes must happen in #1891/#1892 or later FR issues.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or not-required evidence
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has not-required rationale and recheck condition
- [x] Risks and dependencies are explicit
