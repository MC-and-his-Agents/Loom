# WI-1790 Plan

## Phases

- P1: Reproduce installed CLI bootstrap failure and identify wrapper/runtime path mismatch.
- P2: Add a shared wrapper resolver and route existing wrapper entrypoints through it.
- P3: Preserve repo-local runtime classification while allowing installed package runtime classification.
- P4: Add tarball bootstrap smoke and update package payload validation.
- P5: Refresh generated runtime copies, demo bootstrap fixtures, v0.21.1 release metadata, and Loom carriers.
- P6: Update PR metadata, record current-head review, pass hosted checks, merge, publish, refresh plugin payload, and run installed CLI smoke.

## Scenario Mapping

- S1 -> P1, P2, P4
- S2 -> P2, P3
- S3 -> P2, P5
- S4 -> P4
- S5 -> P5, P6

## Acceptance Mapping

- A1 -> test evidence: reproduction command `loom init bootstrap --target <fixture repo> --json`; source fix evidence in `tools/runtime_wrapper.py` and wrapper entrypoints.
- A2 -> structural evidence: generated runtime parity across `skills/shared/scripts/loom_init.py`, `src/skills/shared/scripts/loom_init.py`, and `plugins/loom/skills/shared/scripts/loom_init.py`.
- A3 -> test evidence: `npm run test:package`; packed tarball installed bootstrap smoke.
- A4 -> test evidence: `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/skills_surface.py check --surface plugin-payload-metadata`; `python3 tools/check_npm_package.py`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`; `git diff --check`.
- A5 -> manual evidence: hosted checks, PR gate, controlled merge, release workflow readback, npm installed CLI smoke, and Codex plugin payload refresh readback.

## Validation

- `loom version --json`
- `loom host doctor --host codex --scope user --json`
- `loom init bootstrap --target <fixture repo> --json`
- `python3 tools/py_compile_clean.py tools/loom.py tools/runtime_wrapper.py tools/loom_init.py tools/loom_flow.py tools/loom_check.py tools/loom_status.py tools/check_npm_package.py tools/check_release_surface.py tools/version_surface_check.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/skills_surface.py check --surface plugin-payload-metadata`
- `python3 tools/check_npm_package.py`
- `npm run test:package`
- `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`
- `git diff --check`
- Hosted PR checks and `loom-pr-merge-gate`
- Post-release `npm install -g @mc-and-his-agents/loom@0.21.1` plus installed `loom init bootstrap` and `loom init runtime-state` smoke
