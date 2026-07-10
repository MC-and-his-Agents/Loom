# WI-1892 Plan

## Objective

Clarify the install and upgrade boundary created by FR #1889: the Loom source repository can publish a Codex marketplace source for plugin discovery, but the global CLI remains npm-owned and repository adoption remains independently validated per target repository.

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1892 is a bounded documentation slice with no new runtime workflow, CLI behavior, plugin payload change, repository mutation, workstation registry, global cache, or upgrade orchestration; consumer boundary: suite validate, review, PR gate, merge-ready, FR #1889 closeout, and future FR #1902 planning may consume this minimal suite; recheck condition: require full suite artifacts if the work expands into automatic plugin installation, CLI upgrade automation, repository migration, or multi-repository upgrade orchestration.
- Consumes:
  - Spec locator: `.loom/specs/WI-1892/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required for this docs-only boundary WI; rationale: #1892 is defined by the issue tree and #1891's published marketplace catalog; consumer boundary: suite validate, review, PR gate, and closeout for #1892; recheck condition: require story readiness if user-facing install or upgrade behavior is added.
  - Story Business Confirmation consumed state: not required for this docs-only boundary WI; rationale: #1889/#1892 define the accepted documentation scope; consumer boundary: suite validate, review, PR gate, and closeout for #1892; recheck condition: require business confirmation if adoption or workstation upgrade behavior changes.
- Produces:
  - Validation strategy by scenario: targeted documentation search, diff review, suite validation, evidence validation, carrier validation, fact-chain validation, and diff hygiene.
  - Test strategy by acceptance: map each acceptance item to README, contract, host adapter matrix, or absence of runtime/plugin changes.
  - Implementation contract locator: `.loom/specs/WI-1892/implementation-contract.md`
  - Fresh verification evidence expectation: `.loom/progress/WI-1892.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1892/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1892/spec.md`, #1892.
  - Freshness rule: refresh after README, adoption contract, host adapter matrix, PR metadata, review, hosted-check, or closeout changes.

## Steps

1. Update README install and upgrade guidance with the marketplace/plugin, npm CLI, and per-repository adoption split.
2. Update the global CLI/user plugin contract so marketplace update is classified as workstation plugin truth only.
3. Update the Codex host adapter matrix row and surrounding notes with the same authority split.
4. Run targeted documentation validation plus suite, evidence, carrier, fact-chain, and diff hygiene checks.
5. Review, PR gate, merge-ready, and close out #1892 without expanding into FR #1902 workstation upgrade orchestration.

## Validation

- `rg -n "marketplace|host install|npm install -g|repo adoption|metadata-only" README.md docs/adoption/global-cli-user-plugin-contract.md docs/adoption/host-adapter-matrix.md`
- `python3 tools/loom.py suite validate --target . --item WI-1892 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1892 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1892 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1892 --json`
- `git diff --check`

## Test Strategy

- TDD or test-first expectation: not required; this Work Item changes documentation authority boundaries and validates them through targeted text checks plus Loom suite/fact-chain validation.
- Regression coverage to add or preserve: existing source marketplace catalog and plugin payload remain unchanged; docs now direct users to the correct authority for marketplace plugin, npm CLI, and per-repository adoption.
- Cases that are intentionally not automated: real Codex marketplace plugin installation, npm package upgrade, and multi-repository adoption migration are deferred to FR #1902/#1908.
- How failing tests or equivalent checks will be introduced before implementation: targeted `rg` would miss required boundary terms, and suite/fact-chain validation would fail if WI carriers are incomplete.
- How passing tests or equivalent checks will be captured as test evidence: local validation summary and evidence map consume targeted `rg`, suite validation, evidence validation, carrier validation, fact-chain validation, and diff hygiene.
- Acceptance test mapping:
  - A1 -> test evidence: README targeted text validation and diff review.
  - A2 -> test evidence: README upgrade text validation and diff review.
  - A3 -> test evidence: global CLI/user plugin contract targeted text validation.
  - A4 -> test evidence: host adapter matrix Codex row targeted text validation.
  - A5 -> structural check: `git diff --name-only` and diff review confirm no CLI/runtime/plugin payload files changed.
- How User Story acceptance scenarios map to tests, checks, or manual validation:
  - No separate story artifact exists; #1892 consumes the issue tree as the behavior contract.

## Subagent Output Integration

- Owned outputs: none.
- Integration owner: main agent.
- Required evidence from each subagent: no subagent output was produced for this narrow serial documentation WI.
- Review or reconciliation needed before merge-ready: main agent reviews README, adoption contract, host adapter matrix, validation evidence, PR metadata, and issue state.
- Handoff notes locator or rationale: not required because the main thread owns implementation, validation, PR, and closeout without a handoff boundary; consumer boundary: review, PR gate, and closeout for #1892; recheck condition: require handoff notes if the work is paused or delegated.

## Dependencies

- Hard dependency: #1891 closed, because #1891 publishes the marketplace catalog whose install boundary this Work Item documents.
- Convergence dependency: #1889 can close only after #1890, #1891, and #1892 are merged and closed.

## Non-Goals

- Do not mutate the user's real Codex marketplace configuration.
- Do not add CLI/plugin automatic upgrades, workstation registry, global runtime cache, repo adoption refresh, or legacy migration.
- Do not update package version, marketplace catalog, or plugin payload metadata.
