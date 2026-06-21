# WI-1658 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1658 publishes and verifies previously implemented context-safe runtime work rather than designing a new feature. consumer boundary: review, PR gate, merge-ready, release workflow readback, issue closeout, #1489, and milestone closeout may consume this minimal suite and release/package validation. recheck condition: require full suite artifacts if the branch starts changing runtime behavior, package layout semantics, release workflow semantics, or downstream migration behavior.
- Consumes:
  - Spec locator: .loom/specs/WI-1658/spec.md
  - Scenario ids / locators: S1-S4
  - Acceptance ids / locators: A1-A6
  - Story Readiness consumed state: issue #1658 body and predecessor closeout.
  - Story Business Confirmation consumed state: not_applicable.
- Produces:
  - Validation strategy by scenario: release readback, version/package checks, output-envelope tests, package checks, plugin payload inspection, hosted release workflow readback, and installed global CLI smoke.
  - Test strategy by acceptance: structural and automated release/package/runtime-output checks plus current-head review.
  - Fresh verification evidence expectation: rerun at current PR head before review and PR gate; rerun release readback after main-push publish.
- Locator:
  - Plan locator: .loom/specs/WI-1658/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1658/spec.md; issue #1658.
  - Freshness rule: recheck after version, package, output, plugin payload, or release evidence changes.

## Implementation Goal

Prepare and publish `v0.17.1` as the context-safe runtime release line after #1488, then close #1658 only after real release evidence is present.

## Phases

### Phase 1

- Objective: Prepare release branch.
- Deliverable: version bump, WI-1658 carriers, release-readiness evidence.
- Exit condition: local validation passes and v0.17.1 readback is unoccupied before PR.

### Phase 2

- Objective: Review and merge release PR.
- Deliverable: current-head Loom review record, PR metadata, PR gate, hosted checks, controlled merge.
- Exit condition: main receives the release commit and `loom-cli-release` push workflow starts or completes.

### Phase 3

- Objective: Consume post-merge release evidence.
- Deliverable: tag/GitHub Release/npm/workflow/installed global CLI readback, closeout carrier sync, #1658 closeout.
- Exit condition: #1658 is closed with repo and host evidence aligned.

## Constraints

- Do not restore repo-local plugin/runtime/skills install paths.
- Do not reintroduce single-skill package distribution or old installer compatibility as supported paths.
- Do not implement downstream repository migration.
- Do not treat pre-merge release readback as final release evidence.
- Do not require non-author GitHub reviewer approval; require authored Loom review truth bound to the current PR/head.

## Validation

- Automated checks:
  - `python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`
  - `python3 tools/version_surface_check.py`
  - `python3 tools/check_release_surface.py`
  - `python3 tools/check_npm_package.py`
  - `npm run test:package`
  - `npm pack --dry-run --json --ignore-scripts`
  - `python3 test/output_envelope_test.py`
  - `python3 tools/loom.py help --json`
  - `python3 tools/loom.py suite validate --target . --item WI-1658 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1658 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1658 --json`
  - `python3 tools/loom.py fact-chain --target . --json`
  - `git diff --check`
- Manual checks: inspect release notes/support-boundary wording and PR metadata readback.
- Runtime evidence: output-envelope tests, CLI help output policy, release readback, installed global CLI smoke after publish.
- Behavior evidence: .loom/specs/WI-1658/evidence-map.md
- Scenario validation mapping:
- S1 -> automated: version surface check and release readback confirm `VERSION`, `package.json`, and unoccupied `v0.17.1`.
- S2 -> automated: `test/output_envelope_test.py` plus `loom help --json` confirm default budget, environment overrides, artifact locator, and `--full-output`.
- S3 -> automated: package checks, npm pack dry-run, and release surface checks confirm global CLI package and Codex user-level plugin payload without repo-local install revival.
- S4 -> manual/post-merge automated: post-merge release readback, workflow run readback, tag, GitHub Release, npm, and installed/global CLI smoke evidence.

## Test Strategy

- TDD or test-first expectation: release item consumes existing output-envelope tests and release/package contracts; no new runtime behavior is added.
- Regression coverage to preserve: package payload, release workflow contract, release readback classifier, output budget/artifact/full-output tests, and plugin payload inclusion.
- Cases intentionally not automated before merge: actual tag/npm/GitHub Release creation; this is post-merge workflow evidence.
- Acceptance test mapping:
- A1 -> structural check: `VERSION`, `package.json`, and `python3 tools/version_surface_check.py`.
- A2 -> automated check: `python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`.
- A3 -> automated check: `python3 test/output_envelope_test.py` and `python3 tools/loom.py help --json`.
- A4 -> automated check: `python3 tools/check_npm_package.py`, `npm run test:package`, and `npm pack --dry-run --json --ignore-scripts`.
- A5 -> structural/manual check: docs/evidence/v0.17.1-release-readiness.md and release PR/release notes support-boundary wording.
- A6 -> post-merge automated check: release readback, workflow/tag/GitHub Release/npm readbacks, installed/global CLI smoke, and closeout check.

## Dependencies

- Blocking inputs: #1481, #1482, #1483, #1484, #1485, #1486, #1487, #1488, and #1493 are closed or consumed as release inputs.
- Required coordination: #1489 waits for #1658 release evidence before final milestone closeout.
- Rollback boundary: revert version bump and WI-1658 release carriers before merge; after publish, use a follow-up patch release rather than rewriting release artifacts.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by issue #1658
- [x] Story business semantics do not apply
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations are covered by existing release/package/output tests
- [x] Risks and dependencies are explicit
