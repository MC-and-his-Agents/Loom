# WI-898 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `Makefile`
- `docs/methodology/harness/cli-first-control-plane.md`
- `docs/methodology/harness/cli-command-matrix.md`
- `docs/methodology/harness/README.md`
- `docs/adoption/loom-installed-state-v2.md`
- `docs/adoption/README.md`
- `.loom/work-items/WI-898.md`
- `.loom/progress/WI-898.md`
- `.loom/reviews/WI-898.json`
- `.loom/reviews/WI-898.spec.json`
- `.loom/specs/WI-898/spec.md`
- `.loom/specs/WI-898/plan.md`
- `.loom/specs/WI-898/implementation-contract.md`

## Non-Goals

- Do not implement #888+ detect/doctor/repair.
- Do not migrate installer internals into CLI in this Work Item.
- Do not replace all scenario skills with CLI-backed execution.
- Do not change GitHub, CI, review engine, or worktree host implementations.

## Required Evidence

- CLI JSON examples for version and installed-state fail-closed behavior.
- Contract check coverage for positive and negative installed-state fixtures.
- Full `make check` pass.
- PR gate consuming `WI-898` authored review and spec review carriers.
