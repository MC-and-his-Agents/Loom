# WI-1895 Plan

## Objective

Implement the bounded workstation registry CLI slice for FR #1893:
`loom workstation register/list/unregister --json`.

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1895 is a focused CLI and contract-test slice over a frozen schema; consumer boundary: suite validate, review, PR gate, merge-ready, FR #1893, and #1896; recheck condition: require full suite artifacts if the work expands into multi-repository apply, destructive migration, or global cache relocation.
- Consumes:
  - Spec locator: `.loom/specs/WI-1895/spec.md`
  - Scenario ids / locators: S1, S2, S3, S4
  - Acceptance ids / locators: A1-A6
  - Story Readiness consumed state: not required; rationale: #1895 has an explicit issue scope and upstream schema; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if upgrade apply behavior changes.
  - Story Business Confirmation consumed state: not required; rationale: #1893/#1895 freeze the authority boundary; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if registry entries become mutation authority.
- Produces:
  - Validation strategy by scenario: py compile, focused workstation-registry contract surface, adjacent adoption-host metadata surface, suite/evidence/carrier validation, fact-chain validation, help/command matrix readback, and diff hygiene.
  - Test strategy by acceptance: isolated HOME e2e in `tools/check_cli_contract.py` plus targeted CLI/manual readback.
  - Implementation contract locator: `.loom/specs/WI-1895/implementation-contract.md`
  - Fresh verification evidence expectation: `.loom/progress/WI-1895.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1895/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1895/spec.md`, #1895.
  - Freshness rule: refresh after CLI implementation, checker, registry contract, PR metadata, review, hosted-check, or closeout changes.

## Steps

1. Add workstation command entries and dispatch for `register`, `list`, and `unregister`.
2. Add registry read/write helpers for `~/.loom/repositories.json`.
3. Implement register path/remote/adoption snapshot and opt-in entry writes.
4. Implement list readback and stored-entry diagnostics.
5. Implement unregister remove and `--keep-entry` opt-out behavior.
6. Extend `workstation-registry` contract surface with isolated HOME CLI coverage.
7. Update the registry contract docs and WI carriers.
8. Run validation, review, PR gate, merge-ready, and closeout.

## Validation

- `python3 tools/check_cli_contract.py --surface workstation-registry`
- `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py suite validate --target . --item WI-1895 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1895 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1895 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1895 --json`
- `git diff --check`

## Test Strategy

- TDD or test-first expectation: the focused contract surface runs the new CLI sequence in an isolated HOME and asserts target repository write boundaries.
- Regression coverage to add or preserve: empty list, register, populated list, `--keep-entry` opt-out, unregister by id, registry schema, remote hash, adoption snapshot, and forbidden target payload writes.
- Cases intentionally not automated in this WI: live remote hash drift, missing registered path validation, duplicate id repair, and `workstation upgrade --plan`; these are owned by #1896/#1902.
- How failing tests or equivalent checks will be introduced before implementation: `workstation-registry` surface would fail if commands are absent, registry shape drifts, or target payload is written.
- How passing tests or equivalent checks will be captured as test evidence: local validation summary and evidence map consume the focused checker, adjacent checker, py compile, suite validation, fact-chain, and diff hygiene.
- Acceptance test mapping:
  - A1 -> structural check: command matrix/help readback and `REQUIRED_COMMANDS`.
  - A2 -> test evidence: isolated HOME register assertions.
  - A3 -> test evidence: isolated HOME empty and populated list assertions.
  - A4 -> test evidence: isolated HOME unregister assertions.
  - A5 -> test evidence: forbidden target write assertions.
  - A6 -> manual evidence: live fail-closed validation remains deferred to #1896 and is mapped through the deferred evidence table plus #1896 task carrier relationship.

## Subagent Output Integration

- Owned outputs: none.
- Integration owner: main agent.
- Required evidence from each subagent: no subagent output was produced for this bounded CLI slice.
- Review or reconciliation needed before merge-ready: main agent reviews CLI boundary, target write boundary, checker evidence, PR metadata, and issue state.
- Handoff notes locator or rationale: not required because the main thread owns implementation, validation, PR, and closeout; consumer boundary: review, PR gate, and closeout for #1895; recheck condition: require handoff notes if paused or delegated.

## Dependencies

- Hard dependency: #1894 schema contract merged and closed.
- Downstream dependency: #1896 consumes this CLI surface to add live fail-closed validation.
- Convergence dependency: #1893 can close only after #1894, #1895, and #1896 are merged and closed.

## Non-Goals

- Do not implement `loom workstation upgrade --plan`.
- Do not implement live path missing / remote hash drift / duplicate id validation.
- Do not mutate target repositories.
- Do not refresh Codex plugin marketplace/cache.
- Do not move runtime/tmp/check artifacts to global storage.
