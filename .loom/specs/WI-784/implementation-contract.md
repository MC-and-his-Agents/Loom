# WI-784 Implementation Contract

## Writable Scope

- `src/skills/shared/scripts/loom_init.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/governance_surface.py`
- `src/skills/loom-init/**`
- `src/skills/loom-adopt/**`
- `docs/adoption/zero-friction-adoption-contract.md`
- `docs/adoption/deep-existing-repo-default.md`
- `docs/adoption/repo-companion-contract.md`
- Generated `skills/**` surfaces
- Refreshed example bootstrap outputs
- `.loom/**/WI-784*` carriers

## Boundaries

- Keep WebEnvoy read-only.
- Do not make `repo-interface.json` carry progress, review verdict, current stop, validation summary, closeout result, or host action result.
- Do not solve release placeholder removal, gitignore repair, Git visibility, pre-execution classification, or decision prompts in this checkpoint.
- Do not skip generated skills surface regeneration after changing `src/skills/**`.
