# WI-1484 Implementation Contract

## Scope

- Wrap global `loom` flow, delegated, scenario, PR gate, merge, reconcile, carrier, and closeout queue command paths with agent-safe default stdout.
- Preserve explicit full JSON diagnostics through `--full-output`.
- Expose command-level output policy, budget configuration, and artifact configuration through `loom help --json`.
- Add focused output envelope regression coverage for default summary/artifact behavior and full-output escape hatches.

## Contract

- High-noise global CLI command families default to agent-safe stdout when their JSON payload exceeds the configured stdout budget.
- The default summary envelope must use `loom-agent-output-envelope/v1`, include the command result summary, missing inputs or fallback information when present, and include a full output artifact locator when the raw payload is over budget.
- Full diagnostics remain available only when callers explicitly request full output with `--full-output`; wrapped handlers must strip that flag before delegated runtime execution.
- The stdout budget, summary target, and artifact directory remain configurable through documented environment variables, with stable defaults exposed in help JSON.
- Low-noise command paths may remain direct JSON when they are not expected to exceed the agent-safe budget.

## Non-Goals

- Do not change the output envelope schema from #1477.
- Do not update Codex plugin skill text or executable skill protocol wording for #1486.
- Do not update migration/adoption documentation for #1488.
- Do not change release workflow, package metadata, or downstream repository adoption behavior.
- Do not restore repo-local plugin, runtime, skills, single-skill package, or legacy installer compatibility paths.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py test/output_envelope_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata --surface controlled-merge --surface closeout-wrapper`
- `LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES=1024 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py build --target . --item WI-1484 --json`
- `LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES=1024 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge-ready --target . --item WI-1484 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py build --target . --item WI-1484 --json --full-output`
- `git diff --check`
