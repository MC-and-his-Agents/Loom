# WI-1800 Plan

## Phases

- P1: Fix target/context resolution and fallback behavior for package wrappers, retained idle state, checkpoint aliases, and shared runtime scripts.
- P2: Fix global-cli metadata-only bootstrap and CI doctor/verify behavior without relying on Codex Desktop runtime cache.
- P3: Harden strong governance detector and adversarial adoption evidence consumption.
- P4: Add audited repair-pr evidence recording/validation without ruleset mutation.
- P5: Add runtime parity guard, release readiness evidence, version/plugin payload metadata, and v0.21.2 package surface.
- P6: Add #1803/#1804 PR/merge target/readback coverage and opaque path-safe Work Item ID compatibility.
- P7: Refresh demo bootstrap fixture, WI-1800 carriers, PR metadata, current-head review, hosted checks, merge, release readback, and closeout.

## Scenario Mapping

- S1 -> P2, P5
- S2 -> P1, P6
- S3 -> P3
- S4 -> P4
- S5 -> P5, P7
- S6 -> P6

## Acceptance Mapping

- A1 -> test evidence: `test.target_resolution_test`, checkpoint canonicalization, retained lookup, and skills surface reference integrity.
- A2 -> test evidence: `tools/check_cli_contract.py` surfaces for adoption-host-metadata, merge-wrapper, controlled-merge, release-readback, gate-repair-pr, pr-gate-target-readback, and governance-closeout.
- A3 -> test evidence: runtime-copy-parity, release surface, npm package, package smoke, skills release-check, root verify, runtime parity, adversarial adoption record, and source `loom_check`.
- A4 -> test evidence: `make loom-demo-new-project-sync` followed by `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`.
- A5 -> manual evidence: PR #1816 checks, PR gate, review consumption, controlled merge, `loom-cli-release`, release readback for v0.21.2, #1802, and #1800 closeout.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test.checkpoint_canonicalization_test test.retained_item_lookup_test test.skills_surface_reference_integrity_test test.target_resolution_test`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface gate-repair-pr`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-gate-target-readback`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface runtime-copy-parity`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`
- `npm run test:package`
- `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`
- `git diff --check`
- `python3 .loom/bin/loom_init.py verify --target .`
- `python3 .loom/bin/loom_flow.py runtime-parity validate --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py adopt adversarial-test --target . --record --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source .`
- Execution ledger validation evidence locator: `.loom/progress/WI-1800.md`

## Coordination

- Main controller owns PR body, release evidence, `.loom/status/current.md`, review record, and issue closeout.
- Lane output has been integrated into this PR and is no longer a separate truth source.
- #1806 and #1807-#1810 stay outside this release and do not block WI-1800.

## Ready For Review

- [x] Spec is stable enough for the current release PR.
- [x] Scope and non-goals are clear.
- [x] Validation path is defined.
- [x] Scenarios map to evidence in `.loom/specs/WI-1800/evidence-map.md`.
