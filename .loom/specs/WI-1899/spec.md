# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: issue #1899 / FR #1897 / Phase #1888
  - Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; #1899 is scoped by the GitHub Work Item and WI-1898 repo/global artifact contract.
  - Story scenario locator, or not-required rationale: not required; scenarios below are direct runtime-cache behavior scenarios.
  - Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; internal operating-layer behavior.
- Produces:
  - Scenario ids / locators: S1-S4 in this file.
  - Acceptance ids / locators: A1-A6 in this file.
  - Behavior evidence expectation: resolver and consumer fixtures prove runtime/tmp writes do not create repo-local cache artifacts while repo truth carriers remain repo-local.
- Locator:
  - Spec locator: .loom/specs/WI-1899/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1899; issue #1898; docs/methodology/harness/repo-global-artifact-classification.md
  - Freshness rule: Recheck when runtime path helper, PR metadata artifacts, gate-freeze artifacts, execution attempt evidence, or agent-safe output artifacts change.

## Goal

Move workstation-only Loom runtime and tmp outputs out of adopted repositories by default, without changing the logical locators consumed by existing commands and carriers.

## Scope

- Add global workstation cache helpers under `runtime_paths.py`.
- Map `.loom/runtime/**` to `~/.loom/repos/<repo-id>/runtime/**`.
- Map `.loom/tmp/**` to `~/.loom/repos/<repo-id>/tmp/**`.
- Keep repo truth carriers such as `.loom/status/current.md`, work items, progress, reviews, specs, installed-state, companion files, and shadow carriers repo-local.
- Preserve `.loom/runtime/**` and `.loom/tmp/**` as logical CLI locators in payloads, PR metadata, gate freeze snapshots, execution attempts, and agent-safe envelopes.
- Provide repo-local read fallback for legacy runtime evidence until WI-1908 migration removes old residue.

## Key Scenarios

### Scenario S1

Given a command writes a runtime artifact under `.loom/runtime/**`

When the target repository is processed by the resolver

Then the physical file is written under `~/.loom/repos/<repo-id>/runtime/**` and the emitted locator remains `.loom/runtime/**`.

### Scenario S2

Given a command writes a tmp or long-output artifact under `.loom/tmp/**`

When the target repository is processed by the resolver

Then the physical file is written under `~/.loom/repos/<repo-id>/tmp/**` and the emitted locator remains `.loom/tmp/**`.

### Scenario S3

Given a repo truth carrier such as `.loom/status/current.md`

When the same artifact resolver is asked to resolve that path

Then the file remains repo-local and is not treated as workstation cache.

### Scenario S4

Given an older repository still has repo-local `.loom/runtime/**` evidence

When read-only gate or closeout consumers need that evidence

Then the resolver reads global cache first and falls back to repo-local legacy runtime evidence until migration removes it.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `runtime-paths`, `pr-metadata`, `governance-closeout` surfaces.
  - S2 -> `runtime-paths`, `governance-closeout` agent-safe artifact path.
  - S3 -> `runtime-paths` surface and suite carrier validation.
  - S4 -> `governance-closeout` fixture using retained repo-local execution attempts.
- Expected evidence locator: .loom/specs/WI-1899/evidence-map.md
- Freshness rule: Recheck before review, merge-ready, and closeout; stale when runtime locator mapping or focused fixtures change.
- Execution ledger acceptance locator: .loom/specs/WI-1899/spec.md#acceptance-criteria

## Exceptions And Boundaries

- Global cache is not adoption truth, review truth, merge-ready truth, closeout truth, or release truth.
- Workstation registry repair, repo carrier slimdown, migration apply, and multi-repo upgrade orchestration are out of scope.
- Repo-local read fallback is compatibility only; new writes must not create repo-local `.loom/runtime/**` or `.loom/tmp/**` cache artifacts.

## Acceptance Criteria

- [x] A1: `.loom/runtime/**` write paths resolve to `~/.loom/repos/<repo-id>/runtime/**`.
- [x] A2: `.loom/tmp/**` write paths resolve to `~/.loom/repos/<repo-id>/tmp/**`.
- [x] A3: Repo truth carriers remain repo-local.
- [x] A4: PR metadata and PR intent bodies use logical runtime locators while physically writing to global cache.
- [x] A5: Gate freeze, closeout, execution attempt, and agent-safe output consumers can read global runtime artifacts and legacy repo-local fallback evidence.
- [x] A6: Source, plugin payload, repo-local runtime, and example runtime copies stay synchronized.
