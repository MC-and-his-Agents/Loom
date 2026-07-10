# WI-1806 Plan

## Phases

- P1: Add shared PR intent profile foundations for profile metadata, carrier generation, head binding, scope proof, and carrier-set consistency.
- P2: Implement docs/governance-only, closeout-only, release-only, carrier-sync-only, and fixture-only `prepare/check` paths.
- P3: Add `docs-pr prepare/check` as a short path for docs/governance-only.
- P4: Normalize suite N/A CLI exit semantics and update consuming fixtures.
- P5: Document the command matrix and add focused contract fixtures for positive and fail-closed behavior.
- P6: Prepare PR/review evidence for #1806 and hold #1815 release until #1800 / `v0.21.2` clears.

## Scenario Mapping

- S1 -> P1, P2, P5
- S2 -> P3, P5
- S3 -> P4, P5
- S4 -> P1, P2, P5
- S5 -> P2, P6

## Acceptance Mapping

- A1 -> behavior evidence in `tools/loom.py`; test evidence in `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py` and `python3 tools/check_cli_contract.py --surface pr-metadata`.
- A2 -> behavior evidence in `docs-pr` and `pr-intent` profile fixtures.
- A3 -> behavior evidence in `emit()` suite N/A handling and `python3 tools/check_cli_contract.py --surface suite-contract`.
- A4 -> behavior evidence in release-only, carrier-sync-only, and fixture-only fixture branches under `assert_pr_intent_profile_fixture`.
- A5 -> manual and gate evidence after PR metadata/readback and current-head review.
- A6 -> manual evidence: release readback after #1800 / `v0.21.2` completes or releases the publication line.

## Validation

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/check_cli_contract.py --surface suite-contract`
- `python3 tools/check_cli_contract.py --surface aggregate`
- `git diff --check`
- PR metadata preflight/readback after PR body is authored
- Review, PR gate, merge-ready, and release readback after the PR head is stable
