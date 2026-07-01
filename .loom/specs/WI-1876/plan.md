# WI-1876 Plan

- Suite path decision consumed from `.loom/specs/WI-1876/spec.md`.

## Implementation Steps

1. Route target-aware agent-safe output through the resolved `--target` root when writing default relative full-output artifacts.
2. Preserve absolute `LOOM_OUTPUT_ARTIFACT_DIR` as an explicit override and document relative directory base behavior.
3. Cover `build` and `fact-chain` through focused Python tests and Node wrapper regression tests.
4. Update CLI contract readback helper so aggregate checks consume target-bound relative artifact locators with the same target base used by the command.
5. Complete PR #1878 review/gate, merge, v0.26.2 release readback, and terminal closeout.

## Ownership Constraints

- WI-1876 owns `tools/loom.py`, `tools/check_cli_contract.py`, `test/output_envelope_test.py`, `test/target_resolution_test.py`, `docs/methodology/harness/cli-command-matrix.md`, WI-1876 Loom carriers, and PR #1878 metadata.
- WI-1876 does not own downstream repository changes, authored truth carrier semantic changes, v0.26.1 closeout recovery, unrelated CLI behavior, or unrelated release surfaces.
- Release ownership is limited to v0.26.2 publication and closeout for this fix after PR #1878 merges.

## Validation

- `python3 -m unittest test.output_envelope_test test.target_resolution_test`
- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py test/target_resolution_test.py`
- Real Node wrapper probes for `build --target <tmp> --item WI-test --json` and `fact-chain --target <tmp> --json`
- `python3 tools/check_cli_contract.py --surface aggregate`
- PR metadata preflight/readback, PR gate, hosted checks, release readback, and terminal closeout before final issue closure
