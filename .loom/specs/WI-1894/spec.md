# WI-1894 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1894 freezes a bounded schema/fixture contract for workstation registry and does not implement command behavior, repository mutation, global cache relocation, or batch upgrade orchestration; consumer boundary: suite validate, review, PR gate, merge-ready, FR #1893 planning, and #1895/#1896 implementation; recheck condition: require full suite artifacts if this expands into actual `loom workstation` mutations or multi-repository upgrade orchestration.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1894
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1893
  - Parent Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1888
  - Story Readiness consumed state: not required for this schema freeze; rationale: #1888/#1893/#1894 define the accepted milestone scope and fields; consumer boundary: suite validate, review, PR gate, and closeout for #1894; recheck condition: require story readiness if the work changes user-facing upgrade behavior or repository mutation semantics.
  - Story Business Confirmation consumed state: not required for this schema freeze; rationale: the business semantic is the accepted boundary that workstation registry speeds discovery but does not replace repo truth; consumer boundary: suite validate, review, PR gate, and closeout for #1894; recheck condition: require business confirmation if workstation registry changes upgrade apply policy.
- Produces:
  - Scenario ids / locators: S1 registry authority boundary, S2 minimal schema shape, S3 fail-closed fixture classifications.
  - Acceptance ids / locators: A1-A6 below.
  - Behavior evidence expectation: workstation registry contract, fixture catalog, taxonomy/installation contract links, and contract-test validation.
- Locator:
  - Spec locator: `.loom/specs/WI-1894/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1888, #1893, #1894, milestone #25 planning discussion.
  - Freshness rule: rerun validation after any workstation registry contract, fixture, taxonomy, global CLI/user plugin contract, CLI contract test, PR metadata, review, hosted-check, or closeout change.

## Goal

Freeze the `~/.loom/repositories.json` workstation registry schema so later CLI
and upgrade orchestration work can register Loom-enabled repositories, skip
repeated discovery, and fail closed on stale or ambiguous entries without
promoting workstation cache into repository truth.

## Scope

In scope:

- Add `docs/adoption/workstation-registry-contract.md`.
- Add `docs/evidence/fixtures/workstation-registry-fixtures.json`.
- Link the registry boundary from adoption README, installation taxonomy, and the global CLI/user plugin contract.
- Add a focused `workstation-registry` contract test surface in `tools/check_cli_contract.py`.
- Record WI-1894 suite, carrier, progress, review, and closeout evidence.

Out of scope:

- Implementing `loom workstation register/list/unregister`.
- Writing a real `~/.loom/repositories.json`.
- Implementing workstation upgrade orchestration or multi-repository apply.
- Moving runtime/tmp/cache files out of repository `.loom/`.
- Changing repository adoption, installed-state, runtime, plugin, or marketplace payload behavior.

## Scenarios

### S1: Registry Authority Boundary

Given a repository has Loom installed-state and this machine has a workstation registry entry
When an upgrade planner reads `~/.loom/repositories.json`
Then the registry can accelerate discovery but cannot prove repository adoption, review, merge-ready, PR, issue, or closeout truth.

### S2: Minimal Schema Shape

Given a workstation registers a Loom-enabled repository
When the registry entry is written
Then it records repo path, stable workstation-local id, remote hash, adoption mode, last seen Loom version, opt-in state, and last seen timestamp.

### S3: Fail-Closed Registry Drift

Given a registry entry is missing its path, has a remote hash mismatch, reuses a repo id, or is opted out
When the registry is consumed for planning
Then missing path, remote hash drift, and repo id conflict block mutation planning, while opted-out entries remain list-only and excluded from apply planning.

## Acceptance

- [ ] A1: The registry contract defines `loom-workstation-repositories/v1` and `~/.loom/repositories.json`.
- [ ] A2: The contract states workstation registry is workstation truth only and cannot replace `.loom/installed-state.json` or closeout/review/PR truth.
- [ ] A3: The minimal schema includes repo path, repo id, remote hash, adoption mode, last seen version, and opt-in state.
- [ ] A4: Fixture coverage includes valid opted-in, missing path, remote hash drift, duplicate id, and opted-out list-only cases.
- [ ] A5: Contract tests validate fixture shape, forbidden repository-truth fields, and fail-closed classifications.
- [ ] A6: No CLI command behavior, runtime payload, plugin payload, marketplace payload, or real workstation registry state is changed.

## Behavior Evidence

- Story scenario mapping: no separate story artifact; #1894 is an issue-defined schema/fixture Work Item under FR #1893.
- Story readiness locator or rationale: no separate story artifact exists; #1888/#1893/#1894 provide the accepted scope; consumer boundary: suite validate, review, PR gate, and closeout for #1894; recheck condition: require story readiness if workstation upgrade behavior or repository mutation is implemented.
- Story business confirmation locator or rationale: business semantics are limited to keeping workstation acceleration separate from repository truth; consumer boundary: suite validate, review, PR gate, and closeout for #1894; recheck condition: require business confirmation if upgrade apply policy changes.
- Scenario coverage:
  - S1 -> workstation registry contract and taxonomy/global CLI contract links.
  - S2 -> fixture catalog and contract-test shape validation.
  - S3 -> fixture catalog and contract-test classification validation.
- Expected evidence locator: `.loom/specs/WI-1894/evidence-map.md`
- Freshness rule: refresh validation after any registry contract, fixture, taxonomy, global CLI/user plugin contract, checker, PR metadata, review, hosted-check, or closeout change.
- Execution ledger acceptance locator: `.loom/progress/WI-1894.md`

## Exceptions And Boundaries

- Failure modes: schema drift, path missing, remote hash drift, duplicate id, opted-out entry, or forbidden repository truth fields in the registry.
- Operational boundaries: no real `~/.loom/repositories.json` is written in this Work Item.
- Rollback or fallback expectations: revert the contract/fixture/checker files; downstream #1895/#1896 remain blocked until a schema is re-frozen.
