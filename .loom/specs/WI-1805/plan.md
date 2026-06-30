# WI-1805 Plan

## Phases

- P1: Implement host governance capability diagnosis for GitHub control-plane surfaces and fixtures.
- P2: Define governance capability profile contracts, maturity mapping, advisory fallback labels, and high-risk boundaries.
- P3: Make merge check/run consume governance capability profiles with host-enforced default, explicit advisory opt-in, and fail-closed strong-claim behavior.
- P4: Add governance mode evidence to PR metadata, closeout/release/readback surfaces, docs, and fixtures.
- P5: Prepare v0.23.0 version/package/plugin metadata, payload hash, and release readiness evidence.
- P6: Create PR, bind review to current head, run PR gate/hosted checks, merge, publish/read back v0.23.0, and close #1805/#1826-#1830/milestone.

## Scenario Mapping

- S1 -> P1
- S2 -> P2
- S3 -> P3
- S4 -> P3, P4
- S5 -> P4, P5, P6

## Acceptance Mapping

- A1 -> `governance_surface.py` runtime copies and `test/host_governance_capability_test.py`.
- A2 -> `docs/adoption/github-profile.md`, `docs/methodology/governance/governance-maturity-model.md`, and `test/governance_capability_profiles_test.py`.
- A3 -> `loom_flow.py`, `tools/loom.py`, and `test/governance_merge_profile_test.py`.
- A4 -> `test/governance_merge_profile_test.py` advisory and fail-closed cases.
- A5 -> PR metadata renderer, closeout policy output, docs/evidence fixtures, and release readiness evidence.
- A6 -> PR #1831 readback, review record, PR gate/hosted checks, merge commit, GitHub Release/npm readback, and terminal closeout evidence.

## Validation

- `python3 -m unittest test.host_governance_capability_test test.governance_capability_profiles_test test.governance_merge_profile_test test.output_envelope_test test.plugin_payload_hash_test`
- `node --test test/npm-package-smoke.test.mjs`
- `python3 tools/check_npm_package.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/py_compile_clean.py skills/shared/scripts/governance_surface.py src/skills/shared/scripts/governance_surface.py plugins/loom/skills/shared/scripts/governance_surface.py .loom/bin/governance_surface.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/loom.py test/host_governance_capability_test.py test/governance_capability_profiles_test.py test/governance_merge_profile_test.py`
- `git diff --check origin/main...HEAD`
- PR metadata preflight/readback for PR #1831
- Current-head review, PR gate, hosted checks, merge-ready, release readback, and closeout after the PR head is stable
