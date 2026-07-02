# WI-1892 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1892 is a bounded documentation Work Item under FR #1889 that clarifies the marketplace/plugin/CLI/repo adoption installation boundary and does not introduce new runtime behavior, CLI commands, plugin payload changes, repo mutation, workstation registry, global cache, or upgrade orchestration; consumer boundary: suite validate, review, PR gate, merge-ready, FR #1889 closeout, and future FR #1902 planning may consume this minimal suite; recheck condition: require full suite artifacts if this work expands into actual plugin installation, CLI upgrade automation, repository migration, or multi-repository upgrade orchestration.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1892
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1889
  - Parent Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1888
  - Story Readiness consumed state: not required for this docs-only boundary WI; rationale: #1889/#1892 define the accepted scope and #1891 published the marketplace catalog; consumer boundary: suite validate, review, PR gate, and closeout for #1892; recheck condition: require story readiness if the work adds user-facing install or upgrade behavior.
  - Story Business Confirmation consumed state: not required for this docs-only boundary WI; rationale: the business semantic is the accepted installation boundary between marketplace plugin distribution, npm CLI distribution, and per-repository adoption validation; consumer boundary: suite validate, review, PR gate, and closeout for #1892; recheck condition: require business confirmation if the boundary changes repository mutation, workstation upgrade automation, or release behavior.
- Produces:
  - Scenario ids / locators: S1 user installation guide boundary, S2 global CLI/user plugin contract boundary, S3 host adapter matrix boundary.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: README install/upgrade guidance, global CLI/user plugin contract, host adapter matrix, targeted text validation, and suite/fact-chain validation.
- Locator:
  - Spec locator: `.loom/specs/WI-1892/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1888, #1889, #1891, #1892, milestone #25 planning discussion.
  - Freshness rule: rerun validation after any README, adoption contract, host adapter matrix, PR metadata, review, hosted-check, or closeout change.

## Goal

Document the installation boundary that a Codex marketplace source installs or updates only the Loom Codex plugin surface, npm installs or upgrades the global `loom` CLI, and each adopted repository still requires its own Loom adoption or runtime-upgrade validation.

## Scope

In scope:

- Update README install and upgrade guidance.
- Update `docs/adoption/global-cli-user-plugin-contract.md`.
- Update `docs/adoption/host-adapter-matrix.md`.
- Record WI-1892 suite, carrier, progress, review, and closeout evidence.

Out of scope:

- Changing CLI behavior or package publication behavior.
- Changing the Loom plugin payload, marketplace catalog, skills, or runtime files.
- Implementing workstation registry, global runtime cache, workstation upgrade orchestration, or legacy migration behavior.
- Mutating a real user Codex marketplace profile.

## Scenarios

### S1: User Installation Guide Boundary

Given a user reads the README installation or upgrade guidance
When the Loom source repository is used as a Codex marketplace source
Then the README states that marketplace install/update covers only the Codex plugin surface, npm covers the global CLI, and repository adoption/runtime upgrade remains per repository.

### S2: Global CLI/User Plugin Contract Boundary

Given an implementer reads the global CLI/user plugin contract
When marketplace plugin update is considered
Then the contract classifies that update as workstation truth, not CLI package truth and not repository adoption truth.

### S3: Host Adapter Matrix Boundary

Given an implementer reads the Codex host adapter row
When choosing install, discovery, upgrade, and verification surfaces
Then the matrix separates npm CLI install, user-level plugin install/register or marketplace update, and per-repository installed-state validation.

## Acceptance

- [ ] A1: README states the three separate layers: Codex marketplace/plugin, npm CLI, and per-repository adoption/runtime validation.
- [ ] A2: README upgrade guidance says marketplace plugin update does not upgrade the global CLI or mutate repository adoption state.
- [ ] A3: `docs/adoption/global-cli-user-plugin-contract.md` states marketplace plugin update is workstation truth and cannot be reported as repository adoption success without repository-local validation and closeout evidence.
- [ ] A4: `docs/adoption/host-adapter-matrix.md` Codex row separates default install, discovery, upgrade, and verification surfaces for npm CLI, user-level plugin, and repo adoption.
- [ ] A5: No CLI/runtime/plugin payload behavior is changed.

## Behavior Evidence

- Story scenario mapping: no separate story artifact; #1892 is an issue-defined installation-boundary documentation Work Item.
- Story readiness locator or rationale: no separate story artifact exists; #1889/#1891/#1892 provide the accepted scope; consumer boundary: suite validate, review, PR gate, and closeout for #1892; recheck condition: require story readiness if install or upgrade behavior is implemented.
- Story business confirmation locator or rationale: business semantics are limited to documenting that marketplace, npm CLI, and per-repository adoption have separate authority; consumer boundary: suite validate, review, PR gate, and closeout for #1892; recheck condition: require business confirmation if adoption automation or workstation upgrade behavior changes.
- Scenario coverage:
  - S1 -> README install/upgrade documentation and targeted `rg`.
  - S2 -> global CLI/user plugin contract documentation and targeted `rg`.
  - S3 -> host adapter matrix Codex row documentation and targeted `rg`.
- Expected evidence locator: `.loom/specs/WI-1892/evidence-map.md`
- Freshness rule: refresh validation after any README, adoption contract, host adapter matrix, PR metadata, review, hosted-check, or closeout change.
- Execution ledger acceptance locator: `.loom/progress/WI-1892.md`
