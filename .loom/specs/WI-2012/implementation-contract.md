# Implementation Contract

- Owner: WI-2012 / GitHub #2012.
- Writable source: `src/skills/shared/scripts/loom_flow.py`, `src/skills/shared/scripts/loom_check.py`, `tools/check_cli_contract.py`, generated `skills/**` copies, and WI-2012 carriers.
- Preserve: repo-local manifest fail-closed behavior, current-head review binding, path-boundary validation, and shadow source hash validation.
- Forbidden: WebEnvoy repository changes, fake manifests, required-check bypass, and unrelated Loom refactors.
