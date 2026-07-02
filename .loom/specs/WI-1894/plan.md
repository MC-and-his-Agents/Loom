# WI-1894 Plan

## Objective

Freeze the workstation registry schema and fixture contract for FR #1893 without
implementing the CLI commands that will consume it.

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1894 is a bounded schema/fixture slice with no runtime workflow, CLI mutation behavior, plugin payload change, repository mutation, global cache relocation, or upgrade orchestration; consumer boundary: suite validate, review, PR gate, merge-ready, FR #1893 planning, and #1895/#1896 implementation; recheck condition: require full suite artifacts if this expands into real workstation registry mutation or batch upgrade apply behavior.
- Consumes:
  - Spec locator: `.loom/specs/WI-1894/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A6
  - Story Readiness consumed state: not required for this schema freeze; rationale: #1894 is defined by the issue tree and FR #1893; consumer boundary: suite validate, review, PR gate, and closeout for #1894; recheck condition: require story readiness if user-facing workstation commands are implemented.
  - Story Business Confirmation consumed state: not required for this schema freeze; rationale: #1888/#1893/#1894 define the accepted authority boundary; consumer boundary: suite validate, review, PR gate, and closeout for #1894; recheck condition: require business confirmation if upgrade apply or repository mutation behavior changes.
- Produces:
  - Validation strategy by scenario: targeted documentation search, JSON validity check, focused contract test, adjacent adoption-host metadata test, py compile, suite/evidence/carrier validation, fact-chain validation, and diff hygiene.
  - Test strategy by acceptance: map each acceptance item to the registry contract, fixture catalog, checker surface, or absence of CLI/runtime/plugin payload changes.
  - Implementation contract locator: `.loom/specs/WI-1894/implementation-contract.md`
  - Fresh verification evidence expectation: `.loom/progress/WI-1894.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1894/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1894/spec.md`, #1894.
  - Freshness rule: refresh after registry contract, fixture, taxonomy, global CLI/user plugin contract, checker, PR metadata, review, hosted-check, or closeout changes.

## Steps

1. Add the workstation registry contract with schema, authority boundary, field rules, and fail-closed classifications.
2. Add fixture coverage for valid opted-in, missing path, remote hash drift, duplicate id, and opted-out list-only registry states.
3. Link the new registry contract from adoption README, installation taxonomy, and global CLI/user plugin contract.
4. Add a focused CLI contract-test surface that validates the registry fixture catalog without requiring unimplemented CLI commands.
5. Run targeted validation, suite/evidence/carrier/fact-chain checks, review, PR gate, merge-ready, and close out #1894.

## Validation

- `python3 -m json.tool docs/evidence/fixtures/workstation-registry-fixtures.json >/dev/null`
- `python3 tools/check_cli_contract.py --surface workstation-registry`
- `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py`
- `rg -n "workstation registry|repositories.json|remote hash|repo_id_conflict|opted_out" docs/adoption docs/evidence/fixtures/workstation-registry-fixtures.json tools/check_cli_contract.py`
- `python3 tools/loom.py suite validate --target . --item WI-1894 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1894 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1894 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1894 --json`
- `git diff --check`

## Test Strategy

- TDD or test-first expectation: fixture catalog and checker surface are added with the contract so #1895/#1896 cannot implement a different schema without failing the focused surface.
- Regression coverage to add or preserve: `workstation-registry` surface validates schema version, authority, required fields, forbidden repo-truth fields, fixture ids, and fail-closed classifications.
- Cases that are intentionally not automated: real `~/.loom/repositories.json` writes, real repository path existence checks, and remote readback are deferred to #1895/#1896 implementation.
- How failing tests or equivalent checks will be introduced before implementation: the fixture catalog includes negative cases for missing path, remote hash drift, duplicate id, and opted-out list-only state.
- How passing tests or equivalent checks will be captured as test evidence: local validation summary and evidence map consume JSON validity, focused checker, adjacent checker, py compile, suite validation, evidence validation, carrier validation, fact-chain validation, and diff hygiene.
- Acceptance test mapping:
  - A1 -> behavior evidence: contract text and targeted `rg`.
  - A2 -> behavior evidence: contract text, taxonomy/global CLI contract links, and targeted `rg`.
  - A3 -> test evidence: fixture catalog and focused checker.
  - A4 -> test evidence: fixture catalog required fixture ids and focused checker.
  - A5 -> test evidence: focused checker surface.
  - A6 -> structural check: `git diff --name-only` / diff review confirms no CLI/runtime/plugin payload command behavior changes beyond the checker surface.

## Subagent Output Integration

- Owned outputs: none.
- Integration owner: main agent.
- Required evidence from each subagent: no subagent output was produced for this schema-freeze WI; #1895 implementation may split CLI implementation and fixture-validation lanes.
- Review or reconciliation needed before merge-ready: main agent reviews registry contract, fixture catalog, checker surface, validation evidence, PR metadata, and issue state.
- Handoff notes locator or rationale: not required because the main thread owns implementation, validation, PR, and closeout without a handoff boundary; consumer boundary: review, PR gate, and closeout for #1894; recheck condition: require handoff notes if the work is paused or delegated.

## Dependencies

- Hard dependency: none.
- Downstream dependency: #1895 must consume the frozen schema before implementing register/list/unregister.
- Convergence dependency: #1893 can close only after #1894, #1895, and #1896 are merged and closed.

## Non-Goals

- Do not implement `loom workstation` commands.
- Do not write the real global `~/.loom/repositories.json` on this machine.
- Do not move `.loom/runtime`, `.loom/tmp`, checks, artifacts, or long logs to global storage.
- Do not modify plugin payload, marketplace catalog, runtime payload, package version, or repository adoption command behavior.
