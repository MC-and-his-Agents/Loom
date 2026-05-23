# WI-968 Implementation Contract

## Write Scope

- `tools/check_loom_check_runtime_regressions.py`
- `Makefile`
- `docs/methodology/harness/loom-check-runtime-purity.md`
- `docs/evidence/validations/validation-loom-check-runtime-regression-coverage.md`
- `src/skills/shared/references/harness/loom-check-runtime-purity.md` and generated `skills/**` reference copies
- `packages/loom-installer/package.json`
- `packages/loom-installer/package-lock.json`
- WI-968 work item, progress, spec, review, status, and shadow carriers

## Guardrails

- Default regression must stay lightweight and deterministic.
- The same-worktree double-start proof must fail before starting a second full `loom_check`.
- Node installer lock regression must not run npm while the synthetic owner lock is held.
- Heavy full-check concurrency remains explicit opt-in evidence and must not become a required default CI path.
