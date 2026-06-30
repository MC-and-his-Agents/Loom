# WI-1822 Plan

- Suite path consumed: minimal
- Story readiness consumed: issue #1822 bug report; no separate product story is required for this patch bugfix. Recheck if scope expands into a new user-facing checkpoint workflow.
- Story business confirmation consumed: issue #1822 bug report; no business semantic change is introduced by accepting the existing terminal checkpoint alias. Recheck if terminal checkpoint policy changes.

## Phases

1. Update the shared checkpoint normalization source and generated/runtime copies.
2. Add a focused CLI contract assertion for `closeout -> closed_out`.
3. Validate focused contract behavior, runtime copy parity, generated surface integrity, Python compile cleanliness, diff whitespace, and live resume/state-check repro.
4. Prepare PR, review, merge, and publish v0.22.1 patch release.

## Scenario Mapping

- S1 -> automated validation: `python3 tools/check_cli_contract.py --surface governance-closeout`.

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/check_cli_contract.py --surface governance-closeout`.
- A2 -> test evidence: `python3 tools/check_cli_contract.py --surface governance-closeout`.
- A3 -> test evidence: `python3 tools/check_npm_package.py --surface runtime-copy-parity` and `python3 tools/skills_surface.py check --surface generated-tree-drift --surface reference-integrity`.
- A4 -> manual evidence: v0.22.1 release readiness, package/plugin metadata checks, release workflow readback, npm/package readback, and issue closeout.

## Constraints

- Keep the implementation to the checkpoint alias and focused test.
- Do not modify #1800/#1802/v0.21.2 carriers or closeout.
- Do not claim merge-ready before PR metadata, review, head binding, hosted checks, and release/no-release evidence are stable.
