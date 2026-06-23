# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1732 is a bounded removal/tombstone change for an already-deprecated package, with issue-level acceptance and focused tombstone tests. consumer boundary: suite validate, build, review, PR gate, hosted checks, and closeout may consume this minimal suite. recheck condition: require full suite if scope expands into root `loom` release, npm deprecate execution, host plugin freshness, or new installer behavior.
- Consumes:
  - Work Item / FR locator: GitHub issue #1732
  - Story Readiness: not required; #1732 has fixed product direction and acceptance criteria.
  - Story Business Confirmation: not required; decision is captured in #1732.
- Produces:
  - Scenario ids / locators: S1-S3 in this spec.
  - Acceptance ids / locators: A1-A5 in this spec.
  - Behavior evidence expectation: tombstone CLI blocks every legacy invocation and points to root `loom` plus `loom host ...`.
- Locator:
  - Spec locator: `.loom/specs/WI-1732/spec.md`
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1732
  - Freshness rule: recheck after package CLI, package README, CI, release-surface guard, or npm deprecate policy changes.

## Goal

Retire `@mc-and-his-agents/loom-installer` as an active installer. The package remains only as a fail-closed tombstone with migration text.

## Scope

- In scope:
  - Tombstone CLI result and tests.
  - Package README / metadata.
  - Node installer PR/release workflows.
  - Installer sunset release-surface guard.
  - WI-1732 Loom carriers.
- Out of scope:
  - `npm deprecate` execution.
  - Root Loom v0.19.0 release.
  - Host plugin freshness reporting.
  - Any single-skill or legacy plugin install restoration.

## Key Scenarios

### Scenario S1

Given a user invokes `loom-installer add plugin`, `add skill`, `upgrade-plan`, or `verify-upgrade`

When the tombstone CLI runs

Then it exits non-zero with a blocked result and migration commands for `@mc-and-his-agents/loom` and `loom host ...`.

### Scenario S2

Given CI sees `packages/loom-installer` changes

When the node-installer PR/release gates run

Then they run tombstone checks, not active installer behavior tests or version bump enforcement.

### Scenario S3

Given release closeout evaluates installer state

When it reaches npm deprecation

Then `npm deprecate` remains a separately confirmed external-visible action.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `packages/loom-installer/test/installer.test.ts`
  - S2 -> `.github/workflows/node-installer-pr.yml`, `.github/workflows/node-installer-release.yml`, `tools/check_release_surface.py`
  - S3 -> `packages/loom-installer/README.md`, `packages/loom-installer/README.zh-CN.md`, issue #1732
- Expected evidence locator: `.loom/specs/WI-1732/evidence-map.md`
- Freshness rule: rerun targeted checks after tombstone package, workflow, or release-surface guard changes.
- Execution ledger acceptance locator: `.loom/progress/WI-1732.md`

## Exceptions And Boundaries

- Failure modes: all legacy installer invocations fail closed; no target repository or host plugin state is mutated.
- Operational boundaries: no live npm deprecation, publish, tag, or GitHub Release in this implementation PR.
- Rollback expectation: revert the tombstone package / CI / guard changes and remove WI-1732 carriers before merge.

## Acceptance Criteria

- [x] A1: Legacy installer CLI fails closed for active install-like invocations.
- [x] A2: CLI output points to `@mc-and-his-agents/loom` and `loom host ...`.
- [x] A3: CI no longer enforces active installer behavior tests or installer behavior version bump.
- [x] A4: Package README says the package is retired and `npm deprecate` is separate closeout.
- [x] A5: Release-surface guard consumes tombstone semantics.
