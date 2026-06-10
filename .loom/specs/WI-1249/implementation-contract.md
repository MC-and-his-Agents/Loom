# WI-1249 Implementation Contract

## Contract

`daily-execution-cli` must expose stable progress and timing evidence while preserving existing command membership and required coverage. Observability is additive: it identifies what is running, how long it took, what result was produced, and where a failure occurred without changing the underlying validation semantics.

## Write Scope

- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_check.py`
- `skills/*/.loom-runtime/shared/scripts/loom_check.py`
- `examples/new-project/.loom/bin/loom_check.py`
- `examples/new-project/.loom/bootstrap/init-result.json`
- `examples/new-project/.loom/bootstrap/manifest.json`
- #1249 Loom carrier/readiness metadata required for PR #1409
- PR #1409 metadata/body

## Required Behavior

- Emit stable `daily-execution-cli` `event=start`, `event=progress`, and `event=end` lines for sub-scenarios.
- Include scenario label, command, elapsed timing, outcome/result, failure count, and metadata.
- Enrich failure records with scenario label, command, concise summary, and relevant metadata.
- Preserve the #1248 command inventory and required coverage.
- Keep shared/runtime/demo copies synchronized where repo tooling requires parity.

## Forbidden Behavior

- Do not remove or weaken command coverage.
- Do not convert required failures to advisory results.
- Do not change command group ownership for #1250.
- Do not implement #1252 snapshot/bootstrap reuse or cost optimization.
- Do not change #1251 fallback boundaries.
- Do not define #1253 fast/full validation semantics.
- Do not merge, close, run guardian/formal review/semantic review, or perform closeout from the worker thread.

## Validation Binding

- `git diff --check`
- Focused `py_compile_clean` for touched `loom_check.py` copies.
- `make skills-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface merge-gate .`
- Synthetic failure metadata harness.
- `make loom-demo-new-project-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1249`
- PR metadata preflight/readback compare
- Hosted checks for PR #1409 current head
