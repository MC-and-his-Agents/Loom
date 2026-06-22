# Implementation Contract

## Contract

- `loom version --json` exposes `version_freshness`.
- Default `loom version` prints a short `action` line and optional `next` command.
- `version_freshness.cli` reports installed root CLI version, npm latest read status, latest version when readable, and CLI freshness.
- `version_freshness.plugin_payload` reuses the existing Codex plugin payload readback from source, marketplace source, and runtime cache.
- `version_freshness.surface_compatibility` reports whether installed plugin payload layers match the source plugin surface version.
- `loom doctor`, `loom host doctor`, and `loom upgrade-plan` expose the same freshness contract.
- `loom upgrade-plan` includes a `cli-plugin-freshness` action with one of `upgrade_cli`, `refresh_plugin`, `check_cli_latest`, or `already_current`.
- Diagnostic commands do not mutate target repositories or Codex host state.

## Non-Goals

- No plugin refresh apply behavior.
- No release or version bump.
- No single SKILL install behavior.
- No legacy installer behavior change.

## Validation Binding

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `git diff --check`
- `python3 tools/loom.py suite validate --target . --item WI-1715 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1715 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1715 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1715 --json`
