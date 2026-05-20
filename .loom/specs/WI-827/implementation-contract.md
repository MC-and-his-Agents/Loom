# WI-827 Implementation Contract

## Truth Sources

- `docs/methodology/harness/native-dependency-contract.md`
- `docs/methodology/harness/host-binding-inspector.md`
- `docs/methodology/harness/status-surface-contract.md`
- `docs/methodology/governance/goal-schema.md`
- `docs/methodology/harness/governance-lint-taxonomy.md`
- `docs/adoption/repo-companion-contract.md`
- `docs/adoption/repo-interop-contract.md`

## Runtime Surfaces

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_status.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/governance_surface.py`
- generated `skills/**/.loom-runtime/**`
- `skills/shared/**`
- repo-local wrappers under `tools/`

## Fixture And Validation Surfaces

- `docs/evidence/fixtures/*dependency*`
- `docs/evidence/fixtures/*drift*`
- `docs/evidence/fixtures/*goal*`
- `docs/evidence/fixtures/*governance-lint*`
- `docs/evidence/fixtures/*hardcoding*`
- `tools/skills_surface.py check`
- `tools/host_adapter_check.py`
- `tools/version_surface_check.py`
- `tools/loom_check.py`
- `tools/loom_flow.py pr-gate check`

## Boundaries

- Native host dependency state is consumed as host evidence; authored Loom truth remains versioned in Work Item, progress, review, merge-ready, and closeout carriers.
- `/goal completion` is closeout evidence, not completion truth by itself.
- Project drift may be advisory or blocking by profile, but merge-ready must make that enforcement explicit.
- Advanced lint rules may consume repo companion declarations, but Loom core must reject hardcoded repo-specific paths, guardian names, or rule identities as defaults.
