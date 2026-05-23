# WI-966 Implementation Contract

## Write Scope

- `packages/loom-installer/scripts/run-regression.mjs`
- `packages/loom-installer/.gitignore`
- `.github/workflows/node-installer-pr.yml`
- `.github/workflows/node-installer-release.yml`
- `src/skills/shared/scripts/loom_check.py` and generated `skills/**/.loom-runtime/shared/scripts/loom_check.py` copies
- `docs/methodology/harness/loom-check-runtime-purity.md` and generated skill runtime reference copies
- WI-966 Loom work item, progress, spec, review, and status carriers

## Guardrails

- The installer regression lock must be worktree/package-root local, not machine-global or repository-global across worktrees.
- Lock timeout diagnostics must identify the current owner and recovery path.
- npm cache must be unique per regression run.
- `payload` drift checks remain enabled and deterministic.
- Generated `skills/` surfaces must be refreshed only from `src/skills/`.
