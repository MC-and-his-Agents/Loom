# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: GitHub issue #1714 under parent #1711.
  - Story Readiness: N/A; this is an internal release/package validation work item with acceptance encoded in issue #1714.
  - Story scenario locator: N/A; scenarios are defined below from issue acceptance.
  - Story Business Confirmation: N/A; no business-domain behavior change.
- Produces:
  - Scenario ids / locators: S1 deterministic payload hash; S2 ignore cache artifacts; S3 declared hash mismatch fail-closed.
  - Acceptance ids / locators: A1 hash changes on payload content change; A2 traversal order does not affect hash; A3 ignored files do not affect hash; A4 package validation exposes `plugin-payload-hash`.
  - Behavior evidence expectation: unit tests plus `tools/check_npm_package.py --surface plugin-payload-hash`.
- Locator:
  - Spec locator: `.loom/specs/WI-1714/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1714, parent #1711, and docs/adoption/version-authority-map.md.
  - Freshness rule: re-run after changes under `plugins/loom`, `tools/check_npm_package.py`, or release validation docs.

## Goal

- Implement deterministic plugin payload hash generation for the installable `plugins/loom` Codex plugin payload.
- Add package/release validation that exposes the hash and fails closed if future manifest metadata declares a mismatching `plugin_payload_hash`.

## Scope

- In scope: hash generation, package validation surface, release evidence label, and focused regression tests.
- Out of scope: writing release metadata into plugin manifests, source/cache readback, `loom version` freshness reporting, host plugin refresh commands, legacy single-skill installer retirement, and v0.19.0 publishing.

## Key Scenarios

### Scenario S1

Given an installable `plugins/loom` payload
When any non-ignored payload file content changes
Then the computed `plugin_payload_hash` changes.

### Scenario S2

Given the same payload files created or traversed in different filesystem order
When the hash is computed
Then the digest remains stable because inputs are sorted by POSIX relative path.

### Scenario S3

Given plugin metadata declares `x-loom.plugin_payload_hash`
When the declared value does not match the current payload
Then package validation fails closed before release.

## Behavior Evidence

- Story scenario mapping: N/A; scenarios S1-S3 are issue-derived.
- Story readiness locator: N/A; #1714 is an implementation work item from #1711.
- Story business confirmation locator: N/A; no business-domain behavior.
- Scenario coverage:
  - S1 -> `python3 test/plugin_payload_hash_test.py`
  - S2 -> `python3 test/plugin_payload_hash_test.py`
  - S3 -> `python3 tools/check_npm_package.py --surface plugin-payload-hash`
- Expected evidence locator: `.loom/specs/WI-1714/evidence-map.md`
- Freshness rule: evidence is fresh only for the current PR head.
- Execution ledger acceptance locator: `.loom/progress/WI-1714.md`

## Exceptions And Boundaries

- Failure modes: missing plugin payload root, missing plugin manifest, empty hash input set, or declared hash mismatch must block package validation.
- Operational boundaries: the hash algorithm ignores `.DS_Store`, `__pycache__`, and `*.pyc`; all other payload files under `plugins/loom` are inputs.
- Rollback or fallback expectations: revert the package checker and release evidence label if the surface causes release validation regressions.

## Formal Minimal-Suite Artifact Boundary

- Not_applicable artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md.
- Rationale: WI-1714 uses the minimal suite because the work changes one package validation surface plus its focused regression test and does not need full-suite research, contract matrix, readiness checklist, or suite index artifacts.
- Consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, and closeout may consume this as the minimal-suite full-path artifact boundary only; it does not skip fact-chain, tests, review, PR metadata, hosted checks, controlled merge, or closeout.
- Recheck condition: author full-suite artifacts if the scope expands into plugin metadata writeback, host source/cache readback, CLI freshness reporting, legacy installer migration behavior, release publishing, or cross-module command boundary changes.

## Acceptance Criteria

- [x] A1: Payload content changes produce a different digest.
- [x] A2: Filesystem creation/traversal order does not change the digest.
- [x] A3: `.DS_Store`, `__pycache__`, and `*.pyc` do not change the digest.
- [x] A4: `tools/check_npm_package.py --surface plugin-payload-hash` reports the digest and participates in aggregate package validation.
