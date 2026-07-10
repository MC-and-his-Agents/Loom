# WI-1713 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1713`
- Consumes:
  - Spec locator: `.loom/specs/WI-1713/spec.md`
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A4
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: plugin manifest inspection, hash tests, package/version checks, and version context readback.
  - Test strategy by acceptance: `test/plugin_payload_hash_test.py`, `tools/check_npm_package.py`, `tools/version_surface_check.py`, and `tools/loom.py version --json`.
  - Fresh verification evidence expectation: `.loom/progress/WI-1713.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1713/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1713 and `.loom/specs/WI-1713/spec.md`
  - Freshness rule: Re-run validation after plugin metadata, hash checker, version checker, version context, package manifest, or carrier changes.

## Implementation Goal

- Write plugin payload release metadata into the Codex plugin manifest.
- Normalize the self-referential `plugin_payload_hash` field while hashing the payload.
- Require the metadata in package/version checks and expose it through `loom` version context.

## Excluded Items

- Source/cache/runtime cache freshness comparison.
- Plugin refresh guidance or install/register mutations.
- Legacy single-skill installer retirement.
- Release version bump, tag, GitHub Release, npm publish, or generated release notes.

## Phases

### Phase 1

- Objective: Make plugin payload metadata readable.
- Deliverable: `plugins/loom/.codex-plugin/plugin.json` includes release metadata fields.
- Exit condition: version surface check can read the fields.

### Phase 2

- Objective: Make hash validation self-reference safe.
- Deliverable: `tools/check_npm_package.py` computes a deterministic digest that normalizes only `x-loom.plugin_payload_hash`.
- Exit condition: hash tests and package check pass.

### Phase 3

- Objective: Expose metadata to CLI and package gates.
- Deliverable: `tools/loom.py` version context reports plugin payload metadata; package/version gates require it.
- Exit condition: targeted validation, suite validation, build checkpoint, and review pass.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_npm_package.py tools/version_surface_check.py tools/loom.py`
  - `npm --prefix packages/loom-installer run check:versions`
  - `npm --prefix packages/loom-installer run check:distribution`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - `npm run test:package`
  - `git diff --check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1713 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1713 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1713 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1713 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1713 --build-evidence .loom/progress/WI-1713-build-evidence.json`
- Manual checks: inspect `git diff --stat` and confirm #1721/#1715/#1716/#1722 surfaces remain out of scope.
- Runtime evidence: `.loom/progress/WI-1713.md`
- Behavior evidence: plugin manifest, package checker, version checker, `loom` version context, and hash unit tests.
- Scenario validation mapping:
  - S1 -> automated evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py` and `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`.
  - S2 -> automated evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`.
  - S3 -> automated evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py version --json`.
- Fresh verification evidence: `.loom/progress/WI-1713.md`
- Execution ledger plan locator: `.loom/specs/WI-1713/plan.md`
- Execution ledger validation evidence locator: `.loom/progress/WI-1713.md`

## Test Strategy

- TDD or test-first expectation: preserve and extend the payload hash unit tests around the new self-reference rule.
- Regression coverage to add or preserve: package contract, version surface contract, release surface split, generated skills surface, and root npm package smoke.
- Cases intentionally not automated: exact release commit SHA materialization; final release readback is owned by #1718 because a committed file cannot contain the SHA of the same commit.
- Acceptance test mapping:
  - A1 -> test evidence: `tools/version_surface_check.py`
  - A2 -> test evidence: `test/plugin_payload_hash_test.py`
  - A3 -> test evidence: `tools/check_npm_package.py`
  - A4 -> test evidence: `tools/loom.py version --json`
