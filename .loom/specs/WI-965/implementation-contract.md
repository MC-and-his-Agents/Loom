# WI-965 Implementation Contract

## Write Scope

- `Makefile`
- `.github/workflows/loom-check.yml`
- `tools/check_demo_bootstrap_fixture.py`
- Harness automation frontload documentation and generated skill runtime reference copies
- WI-965 Loom carriers and review/spec records

## Guardrails

- The default check path must not call bootstrap against `examples/new-project` with `--write`.
- The isolated temporary target must be cleaned after the check.
- The explicit sync target may continue to write `examples/new-project` and run bootstrap verification.
- Temporary fixture generation must not depend on live GitHub or Codex App state.
