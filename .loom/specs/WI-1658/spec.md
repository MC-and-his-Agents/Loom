# WI-1658 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1658 is a bounded release-preparation and release-closeout item that consumes already-merged runtime, CLI, docs, and plugin payload changes. consumer boundary: release PR review, PR gate, merge-ready, release workflow readback, #1658 closeout, #1489 final closeout, and parent milestone closeout may consume this minimal suite plus release/package validation evidence. recheck condition: require full suite artifacts if scope expands into new runtime implementation, release workflow semantics, package payload layout, external installer behavior, or downstream repository migration.
- Consumes:
  - Work Item locator: https://github.com/MC-and-his-Agents/Loom/issues/1658
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1480
  - Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1476
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue #1658 body and closed predecessor issues in milestone/11.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: not_applicable; this item is release execution for already accepted product scope.
- Produces:
  - Scenario ids / locators: S1-S4 in this file.
  - Acceptance ids / locators: A1-A6 in this file.
  - Behavior evidence expectation: release validation proves context-safe output surfaces, global CLI package payload, Codex user-level plugin payload, and support-boundary release notes are ready before publish and readable after publish.
- Locator:
  - Spec locator: .loom/specs/WI-1658/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1658; v0.17.0 baseline; issue #1488 closeout.
  - Freshness rule: recheck after changes to `VERSION`, `package.json`, release workflow, package payload, plugin payload, output-envelope code/tests, or release notes.

## Goal

Publish `v0.17.1` as the first post-v0.17.0 release that includes the completed context-safe runtime adoption line after #1488 documentation closeout.

## Scope

- In scope: bump root Loom CLI release version to `v0.17.1`, record release readiness evidence, validate output budgets/artifacts/full-output behavior, validate package and Codex user-level plugin payload, and close #1658 only after real release readback exists.
- Out of scope: implementing new output behavior, changing release workflow semantics, restoring repo-local runtime/plugin/skills installs, single-skill package distribution, old installer compatibility paths, and downstream repository migration.

## Key Scenarios

### Scenario S1

Given a release operator prepares #1658
When they read the release branch
Then `VERSION` and root `package.json` declare the unpublished `v0.17.1` release candidate.

### Scenario S2

Given the release PR is reviewed before merge
When validation runs
Then stdout budget defaults, configurable budget overrides, artifact locator behavior, and explicit `--full-output` behavior are covered by automated tests or CLI help readback.

### Scenario S3

Given the release package is validated
When package checks run
Then the root package contains the global `loom` CLI and Codex user-level plugin payload, and it does not treat repo-local runtime/plugin/skills or old installer paths as current publish surfaces.

### Scenario S4

Given the release PR is merged to `main`
When `loom-cli-release` completes
Then release closeout records the actual main merge commit, `v0.17.1` tag, GitHub Release, npm package readback, workflow run, and installed/global CLI smoke evidence.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `VERSION`, `package.json`, and release readback classification.
  - S2 -> `test/output_envelope_test.py` and `loom help --json` output policy.
  - S3 -> `tools/check_npm_package.py`, npm pack dry-run, plugin payload locators under `plugins/loom`, and forbidden release surface checks.
  - S4 -> post-merge `loom release readback`, GitHub/NPM readbacks, and release workflow run.
- Expected evidence locator: .loom/specs/WI-1658/evidence-map.md
- Freshness rule: evidence must be rerun after any release candidate, package payload, output-envelope, or release-note change.

## Exceptions And Boundaries

- Pre-merge `release readback` must classify `v0.17.1` as unpublished; it is not final release evidence.
- Final release evidence can only be collected after controlled merge to `main` and the `loom-cli-release` push workflow.
- The Codex user-level plugin payload is shipped inside the root package; #1658 verifies the payload and support boundary, it does not vendor runtime into target repositories.
- Single-person development does not require another GitHub reviewer. The required approval truth is a current-head Loom review record consumed by PR gate; author/agent oral judgment is not sufficient.

## Acceptance Criteria

- [ ] A1: `VERSION` is `v0.17.1` and `package.json` is `0.17.1`.
- [ ] A2: Pre-merge release readback classifies `v0.17.1` as unpublished with no existing tag, GitHub Release, or npm version.
- [ ] A3: Pre-merge validation covers default stdout budget, configurable budget override, artifact locator, and explicit `--full-output` behavior.
- [ ] A4: Package validation proves the root package ships the global `loom` CLI and Codex user-level plugin payload without reviving repo-local install surfaces.
- [ ] A5: Release notes/support-boundary evidence says post-v0.17.0 support is metadata-only host repositories plus global CLI plus Codex user-level plugin.
- [ ] A6: Post-merge closeout evidence points to the actual `v0.17.1` tag, head/merge commit, GitHub Release, npm package, workflow run, installed/global CLI smoke, and #1658 closeout.
