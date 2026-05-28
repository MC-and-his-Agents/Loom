# WI-1129 Plan

- Suite path: minimal

## Implementation

- Add `suite evidence scaffold` to the implemented command matrix and CLI usage.
- Add a dedicated evidence scaffold payload that reads suite inspect locators, uses `docs/methodology/templates/scaffold/evidence-map.md`, and plans `.loom/specs/<item>/evidence-map.md`.
- Keep dry-run as the default with `mutates: false`; require explicit `--apply` before writing.
- Preserve existing evidence-map files and fail closed on unsafe item segments, symlink traversal, non-directory parents, or non-file artifact targets.
- Generate seed rows as `missing` so scaffold output cannot pass evidence validation until authored evidence updates source locators, bindings, and freshness.
- Update CLI contract fixtures and docs to reflect #1129 implemented surface.

## Validation Mapping

- Scenario S1 -> structural validation evidence: `python3 tools/check_cli_contract.py` evidence scaffold dry-run fixture.
- Scenario S2 -> structural validation evidence: `python3 tools/check_cli_contract.py` evidence scaffold apply, repeat apply, and existing-file preservation fixtures.
- Scenario S3 -> structural validation evidence: `python3 tools/check_cli_contract.py` scaffold validate-blocking, symlink, and traversal fixtures.

## Test Strategy

- A1 -> test evidence: `python3 tools/check_cli_contract.py` help matrix assertion.
- A2 -> test evidence: `python3 tools/check_cli_contract.py` dry-run payload and no-mutation assertion.
- A3 -> test evidence: `python3 tools/check_cli_contract.py` apply payload and created locator assertion.
- A4 -> test evidence: `python3 tools/check_cli_contract.py` generated scaffold validate-blocking assertion.
- A5 -> test evidence: focused `rg` for `suite evidence scaffold`, `missing`, `/speckit`, and `.specify`; plus CLI contract unsafe path fixtures.
