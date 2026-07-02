# WI-1895 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1895 is a bounded CLI implementation over the schema frozen by WI-1894 and does not implement batch upgrade orchestration, destructive repo migration, or live registry drift validation; consumer boundary: suite validate, review, PR gate, merge-ready, FR #1893, and #1896 implementation; recheck condition: require full suite artifacts if this expands into multi-repository apply, destructive repair, or global cache relocation.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1895
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1893
  - Parent Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1888
  - Upstream schema locator: https://github.com/MC-and-his-Agents/Loom/issues/1894 and `docs/adoption/workstation-registry-contract.md`
  - Story Readiness consumed state: not required for this bounded CLI slice; rationale: #1888/#1893/#1894/#1895 define the accepted command scope; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if user-facing upgrade apply policy changes.
  - Story Business Confirmation consumed state: not required for this bounded CLI slice; rationale: the accepted business semantic is workstation discovery acceleration without replacing repo truth; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if registry entries become mutation authority.
- Produces:
  - Scenario ids / locators: S1 register, S2 list, S3 unregister, S4 target repo write boundary.
  - Acceptance ids / locators: A1-A6 below.
  - Behavior evidence expectation: CLI command outputs, isolated HOME contract test, command matrix/help coverage, and registry contract docs.
- Locator:
  - Spec locator: `.loom/specs/WI-1895/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1888, #1893, #1894, #1895, milestone #25 planning discussion.
  - Freshness rule: rerun validation after any workstation registry CLI, fixture, contract, checker, PR metadata, review, hosted-check, or closeout change.

## Goal

Implement the minimum `loom workstation register/list/unregister --json` surface
so a workstation can remember Loom-enabled repositories in
`~/.loom/repositories.json` without writing runtime, plugin, skills, or
adoption payload into those target repositories.

## Scope

In scope:

- Add `workstation register`, `workstation list`, and `workstation unregister` to the CLI command matrix and router.
- Write `~/.loom/repositories.json` using schema `loom-workstation-repositories/v1`.
- Register a target path, canonical `remote.origin.url` hash, adoption snapshot, opt-in state, and timestamps.
- List entries and stored-entry diagnostics.
- Remove entries or mark them list-only with `--keep-entry`.
- Extend `tools/check_cli_contract.py --surface workstation-registry` with isolated HOME CLI coverage.

Out of scope:

- `loom workstation upgrade --plan`.
- Live path existence, remote hash drift, and duplicate id fail-closed validation beyond stored-entry diagnostics.
- Runtime/tmp/global cache relocation.
- Codex marketplace/plugin refresh.
- Any target repository payload write.

## Scenarios

### S1: Register Repository

Given a target repository exists and may have `.loom/installed-state.json`
When `loom workstation register --target <repo> --json` runs
Then the command writes one entry to `~/.loom/repositories.json` with path, id, remote hash, adoption snapshot, opt-in state, and last-seen timestamp.

### S2: List Registry

Given a workstation registry exists or is absent
When `loom workstation list --json` runs
Then the command returns registry entries without mutating the filesystem and reports eligible opted-in entries.

### S3: Unregister Repository

Given a target path or repo id is present in the registry
When `loom workstation unregister` runs
Then the entry is removed, or with `--keep-entry` it remains visible with `opt_in.enabled = false`.

### S4: Target Repository Write Boundary

Given register/unregister update workstation truth
When the command runs
Then only `~/.loom/repositories.json` is written and the target repository receives no runtime, plugin, skills, adoption, issue, PR, review, or closeout payload.

## Acceptance

- [ ] A1: `loom help --json` and command matrix include `workstation register`, `workstation list`, and `workstation unregister`.
- [ ] A2: `register` writes `~/.loom/repositories.json` with schema `loom-workstation-repositories/v1` and a stable entry containing path, id, remote hash, adoption snapshot, opt-in state, and timestamps.
- [ ] A3: `list` is read-only for a fresh HOME and for a populated registry.
- [ ] A4: `unregister` can remove by id or target path, and `--keep-entry` marks the entry opted out/list-only.
- [ ] A5: Isolated HOME contract coverage proves the command sequence without writing unsupported payload into the target repository.
- [ ] A6: Live fail-closed validation for missing path, remote drift, and duplicate id remains deferred to #1896.

## Behavior Evidence

- Story scenario mapping: no separate story artifact; #1895 is an issue-defined CLI Work Item under FR #1893.
- Story readiness locator or rationale: no separate story artifact exists; #1888/#1893/#1894/#1895 provide accepted scope; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if upgrade apply policy changes.
- Story business confirmation locator or rationale: business semantics are limited to workstation discovery acceleration without repo truth authority; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if registry entries become mutation authority.
- Scenario coverage:
  - S1 -> `tools/loom.py` register implementation and isolated HOME contract test.
  - S2 -> `tools/loom.py` list implementation and isolated HOME contract test.
  - S3 -> `tools/loom.py` unregister implementation and isolated HOME contract test.
  - S4 -> isolated HOME target write boundary assertions and registry contract docs.
- Expected evidence locator: `.loom/specs/WI-1895/evidence-map.md`
- Freshness rule: refresh validation after any CLI, checker, contract, PR metadata, review, hosted-check, or closeout change.
- Execution ledger acceptance locator: `.loom/progress/WI-1895.md`

## Exceptions And Boundaries

- Failure modes: unreadable or unsupported global registry blocks the command with `failed_layer=workstation-registry`.
- Operational boundaries: command writes global workstation registry only; target repository mutation is out of scope.
- Rollback or fallback expectations: revert `tools/loom.py`, `tools/check_cli_contract.py`, contract doc updates, and WI carriers; downstream #1896 remains blocked until #1895 is reimplemented.
