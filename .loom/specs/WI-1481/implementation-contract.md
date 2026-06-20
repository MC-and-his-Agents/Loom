# WI-1481 Implementation Contract

## Contract

- Add reusable helper functions in `tools/loom.py` for output envelopes, artifact writing, and over-budget summary payloads.
- Preserve existing command result semantics; helpers are opt-in for later command-specific issues.
- Store full diagnostic payloads only in ignored output artifacts or explicit artifact directories, never as Loom truth carriers.

## Non-Goals

- Do not integrate every high-noise command in this Work Item.
- Do not add configurable budget policy here.
- Do not restore repo-local runtime, plugin, or skills installation paths.

## Verification

- `python3 test/output_envelope_test.py`
- `python3 -m unittest discover -s test -p 'output_envelope_test.py'`
- `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`
- `git diff --check`
