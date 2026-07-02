# WI-1891 Plan

## Objective

Add the source-repository Codex marketplace catalog that #1890 made legal, then verify the catalog is parseable and does not cross into installed-state truth.

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1891 is a bounded source-catalog publication slice with no new runtime workflow, CLI behavior, repo mutation, or install-boundary documentation; consumer boundary: suite validate, review, PR gate, merge-ready, #1892 follow-up planning, and closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if the work expands into workstation upgrade orchestration, automatic plugin installation, repo adoption mutation, broader install-boundary documentation, or legacy migration behavior.
- Consumes:
  - Spec locator: `.loom/specs/WI-1891/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required for this catalog-publication WI; rationale: #1891 is defined by the issue tree and #1890's checker contract; consumer boundary: suite validate, review, PR gate, and closeout for #1891; recheck condition: require story readiness if user-facing installation behavior is added.
  - Story Business Confirmation consumed state: not required for this catalog-publication WI; rationale: #1889/#1891 define the accepted marketplace-source scope; consumer boundary: suite validate, review, PR gate, and closeout for #1891; recheck condition: require business confirmation if adoption or workstation upgrade behavior changes.
- Produces:
  - Validation strategy by scenario: catalog structural checks, temporary-home Codex marketplace parse, and source checker validation.
  - Test strategy by acceptance: focused JSON parse, marketplace add parse, source loom_check, issue readback, and diff hygiene.
  - Fresh verification evidence expectation: `.loom/progress/WI-1891.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1891/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1891/spec.md`, #1891.
  - Freshness rule: refresh after catalog, plugin manifest, checker, PR metadata, review, hosted-check, or closeout changes.

## Steps

1. Add `.agents/plugins/marketplace.json` with a single `loom` plugin entry.
2. Validate JSON shape and Codex marketplace parsing in a temporary `HOME`.
3. Run source self-fixture `loom_check` to prove the catalog is accepted by Loom's source checker.
4. Review, PR gate, merge-ready, and close out #1891 without expanding into #1892 documentation or workstation upgrade behavior.

## Validation

- `python3 -m json.tool .agents/plugins/marketplace.json >/dev/null`
- `tmp_home=$(mktemp -d); HOME="$tmp_home" codex plugin marketplace add /Users/mc/dev/Loom; rc=$?; rm -rf "$tmp_home"; exit $rc`
- `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- `git diff --check`
- `python3 tools/loom.py suite validate --target . --item WI-1891 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1891 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1891 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1891 --json`

## Test Strategy

- TDD or test-first expectation: not required; this Work Item publishes a deterministic marketplace catalog and validates it through structural and CLI parser checks.
- Regression coverage to add or preserve: the source checker contract from #1890 continues to accept the published catalog and reject installed-state-like marketplace files.
- Cases that are intentionally not automated: real user Codex profile installation and automatic upgrade are deferred to #1892 / FR #1902.
- How failing tests or equivalent checks will be introduced before implementation: source checker failure would reject an invalid catalog, and the temporary-home Codex parser command would fail if Codex cannot read the repository marketplace.
- How passing tests or equivalent checks will be captured as test evidence: local validation summary and evidence map consume JSON validation, temporary-home Codex parse, source `loom_check`, suite validation, and fact-chain validation.
- Acceptance test mapping:
  - A1 -> test evidence: JSON validation and catalog diff review.
  - A2 -> structural check: catalog source path review and temporary-home Codex parse.
  - A3 -> test evidence: temporary-home `codex plugin marketplace add /Users/mc/dev/Loom`.
  - A4 -> test evidence: source `loom_check`.
  - A5 -> structural check: GitHub issue #1892 remains open before #1889 closeout.
- How User Story acceptance scenarios map to tests, checks, or manual validation:
  - No separate story artifact exists; #1891 consumes the issue tree as the behavior contract.

## Subagent Output Integration

- Owned outputs: none.
- Integration owner: main agent.
- Required evidence from each subagent: no subagent output was produced for this narrow serial WI.
- Review or reconciliation needed before merge-ready: main agent reviews catalog, plugin manifest target, validation evidence, PR metadata, and issue follow-up state.
- Handoff notes locator or rationale: not required because the main thread owns implementation, validation, PR, and closeout without a handoff boundary; consumer boundary: review, PR gate, and closeout for #1891; recheck condition: require handoff notes if the work is paused or delegated.

## Dependencies

- Hard dependency: #1890 closed, because #1890 defines the checker allowance for a published marketplace catalog.
- Soft dependency: #1892 remains open and will document install boundaries after this catalog exists.

## Non-Goals

- Do not mutate the user's real Codex marketplace configuration.
- Do not add plugin install, upgrade, registry, cache, or migration behavior.
- Do not update package version or plugin payload metadata.
