# WI-1127 Plan

- Suite path: minimal

## Implementation

- Add implemented command matrix entries for `suite evidence inspect` and `suite evidence validate`.
- Extend `handle_suite` with nested `evidence inspect|validate` parsing while keeping `suite evidence scaffold` unimplemented for the owning Work Item.
- Parse evidence-map Markdown rows into normalized evidence records.
- Validate required evidence row fields, allowed freshness values, stale/conflict states, required behavior/test evidence rows, and fresh verification consumption.
- Reuse the existing suite readiness envelope and failure taxonomy shape for missing evidence-map, stale evidence, and missing fresh verification evidence.
- Update CLI contract fixtures and docs to reflect #1127 implemented surface.

## Validation Mapping

- Scenario S1 -> structural validation evidence: `python3 tools/check_cli_contract.py` evidence inspect fixture.
- Scenario S2 -> structural validation evidence: `python3 tools/check_cli_contract.py` evidence happy validate fixture.
- Scenario S3 -> structural validation evidence: `python3 tools/check_cli_contract.py` missing and stale evidence validate fixtures.

## Test Strategy

- A1 -> test evidence: `python3 tools/check_cli_contract.py` help matrix assertions.
- A2 -> test evidence: `python3 tools/check_cli_contract.py` evidence inspect payload assertion.
- A3 -> test evidence: `python3 tools/check_cli_contract.py` evidence validate pass fixture.
- A4 -> test evidence: `python3 tools/check_cli_contract.py` missing and stale evidence blocking fixtures.
- A5 -> test evidence: focused `rg` for suite evidence command names and failure kinds.
