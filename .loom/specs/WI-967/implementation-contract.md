# WI-967 Implementation Contract

## Write Scope

- `src/skills/shared/scripts/loom_check.py`
- Generated `skills/**/shared/scripts/loom_check.py` surfaces
- `examples/new-project/.loom/bin/loom_check.py` and bootstrap runtime hashes
- Installer package version metadata when distributed script drift requires it
- WI-967 Loom carriers and spec/review records

## Guardrails

- Default subprocess sanitization must not remove ordinary `PATH` or `HOME`.
- Explicit fixture `env=` values must win after sanitization.
- Missing-target samples must be absent on disk before invoking live-smoke commands.
- The implementation must not introduce a machine-global lock or fixed cross-repository path.
