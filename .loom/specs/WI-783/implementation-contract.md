# WI-783 Implementation Contract

## Write Scope

- `docs/adoption/**`
- `src/skills/**`
- generated `skills/**`
- `.loom/work-items/WI-783.md`
- `.loom/progress/WI-783.md`
- `.loom/reviews/WI-783*.json`
- `.loom/specs/WI-783/**`
- `packages/loom-installer/package*.json`

## Invariants

- `docs/adoption/loom-surfaces-version-control.md` is the authoritative policy.
- Installed skill references must not introduce independent rules that drift from the docs contract.
- Generated `skills/` content must come from `python3 tools/skills_surface.py generate`.
- Behavior enforcement remains deferred to later milestone issues.
