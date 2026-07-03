# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: issue #1901 / FR #1897 / Phase #1888
  - Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; #1901 is scoped by the GitHub Work Item and FR #1897 runtime-cache boundary.
  - Story scenario locator, or not-required rationale: not required; scenarios below are direct operating-layer contract scenarios.
  - Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; internal gate/cache behavior.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: focused CLI contract fixture proves target repo-local cache absence does not block gate/read surfaces.
- Locator:
  - Spec locator: .loom/specs/WI-1901/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1901; issue #1900; docs/methodology/harness/repo-global-artifact-classification.md
  - Freshness rule: Recheck when runtime path resolution, agent-safe artifact resolution, review read, PR gate, merge-ready, doctor, or resume behavior changes.

## Goal

After runtime artifacts move to the workstation-level global cache, stable Loom gates must not require a target repository to contain `.loom/runtime` or `.loom/tmp`. Repo truth remains in stable carriers, while diagnostics and long outputs may be written through global runtime locators.

## Scope

- Add a contract fixture that creates a valid metadata-only Loom target repo with stable Work Item, progress, status, review, spec, installed-state, and PR payload carriers.
- Delete target repo-local `.loom/runtime` and `.loom/tmp` before running the gate/read checks.
- Prove `doctor`, `resume`, `review read`, PR gate, and `merge-ready` pass without recreating repo-local runtime cache directories.
- Prove agent-safe diagnostics still resolve through the global runtime cache.
- Do not change user-facing command semantics.
- Do not expand into workstation registry, workstation upgrade orchestration, legacy migration apply, release behavior, or hosted service mutation.

## Key Scenarios

### Scenario S1

Given a metadata-only Loom target repository has stable truth carriers but no repo-local `.loom/runtime` or `.loom/tmp`

When `loom doctor` and `loom resume` run against the target

Then they do not require repo-local runtime cache directories, and any long diagnostics are read from the global runtime cache.

### Scenario S2

Given the same cache-absent target has an authored review record and PR payload fixture

When review read and PR gate run

Then they consume stable repo truth and pass without repo-local runtime cache artifacts.

### Scenario S3

Given PR gate inputs are fresh and the target repo-local runtime/tmp cache is absent

When merge-ready runs

Then merge-ready passes without recreating repo-local runtime cache directories.

## Acceptance Criteria

- [x] A1: The `runtime-paths` surface includes a cache-absent fixture for doctor, resume, review read, PR gate, and merge-ready.
- [x] A2: The fixture deletes `.loom/runtime` and `.loom/tmp` before running the checks.
- [x] A3: The fixture verifies resume artifact locators resolve through the global runtime cache and not repo-local `.loom/tmp`.
- [x] A4: The fixture fails if any checked surface recreates repo-local `.loom/runtime` or `.loom/tmp`.
- [x] A5: The focused contract remains under the existing runtime-paths surface and does not introduce a separate gate framework.
