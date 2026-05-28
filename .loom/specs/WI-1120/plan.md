# WI-1120 Plan

## Implementation Plan

1. Add `suite validate` to `tools/loom.py` command metadata and usage.
2. Implement a read-only validate helper that consumes `suite_inspect_payload`.
3. Map unknown suite paths and missing required artifacts to blocking gaps.
4. Preserve `not_applicable` and advisory result envelopes for the core command.
5. Add CLI contract fixtures for pass, block, advisory, and not_applicable.
6. Update CLI surface docs to mark #1120 as the implemented core validate slice.

## Validation Plan

- `python3 tools/check_cli_contract.py`
- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` for `suite validate`, validate constants, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1120`

## Out Of Scope

- No #1121 path-depth validation.
- No #1122 not_applicable rationale enforcement.
- No #1123 spec/plan mapping checks.
- No #1124 final failure taxonomy expansion.
- No #1125 `flow spec-review` integration.
