# WI-1483 Implementation Contract

## Scope

- Add agent-safe default output for global `loom fact-chain`, `loom status`, and `loom shadow-parity`.
- Preserve explicit full raw output for scripts and debugging.
- Update contract tests to request full output when they consume nested payloads.

## Contract

- Default stdout may be a summary envelope when the raw payload exceeds the configured agent-safe budget.
- The summary envelope must include command, result, summary, key gaps, full output locator, diagnostic counts, and key locators.
- Full output remains available through `--full-output` and through the artifact locator written by default summary mode.
- Machine consumers that need nested delegated payload fields must pass `--full-output`.
- `loom shadow-parity` is the supported global CLI entrypoint for shadow parity reads.

## Non-Goals

- Do not change delegated fact-chain, status, or shadow parity judgment logic.
- Do not implement #1484 flow gate command summary output.
- Do not change Codex plugin text or migration docs.
- Do not restore repo-local runtime/plugin/skills paths.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `git diff --check`
- Real stdout budget probes recorded in `.loom/specs/WI-1483/evidence-map.md`.
