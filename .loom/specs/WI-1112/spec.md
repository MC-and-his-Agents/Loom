# WI-1112 Spec

- Suite path: minimal
- Work Item: WI-1112

## Goal

Cover suite inspect unknown, minimal, full, and missing-path fixtures.

## Scope

- Keep the regression surface in `tools/check_cli_contract.py`, the existing CLI contract check.
- Assert that suite inspect does not mutate fixture directories across unknown, minimal, full, not_applicable, and missing required artifact states.
- Assert every fixture continues to use the shared `suite inspect` JSON envelope with `mutates: false`.
- Preserve stable repo-relative locators and missing-input reporting.

## Scenarios

### S1 Unknown State Is Read-Only

Given a target without a suite path decision,
When `loom suite inspect --json` runs,
Then it reports `suite_path: unknown`, includes `suite_path_decision` as a missing input, and leaves the target unchanged.

### S2 Minimal State Is Read-Only

Given a minimal suite with spec and plan artifacts,
When `loom suite inspect --json` runs,
Then it reports minimal locators, no missing inputs, and leaves the target unchanged.

### S3 Full State Is Read-Only

Given a full suite with required artifacts,
When `loom suite inspect --json` runs,
Then it reports full locators as repo-relative paths, no missing inputs, and leaves the target unchanged.

### S4 Missing Required Artifact Is Read-Only

Given a full suite path decision with a missing required artifact,
When `loom suite inspect --json` runs,
Then it reports the missing required artifact and leaves the target unchanged.

### S5 Not Applicable Branch Is Guarded

Given a not_applicable suite path decision,
When `loom suite inspect --json` runs,
Then it reports `suite_path: not_applicable`, no missing inputs, and leaves the target unchanged.

## Acceptance

- AC-1112-1: `tools/check_cli_contract.py` fails if any suite inspect fixture mutates the fixture target.
- AC-1112-2: `tools/check_cli_contract.py` fails if any suite inspect fixture stops emitting `mutates: false`.
- AC-1112-3: Unknown, minimal, full, not_applicable, and full-missing fixture payload assertions remain explicit.
- AC-1112-4: No new suite subcommands or readiness/scaffold semantics are introduced.
