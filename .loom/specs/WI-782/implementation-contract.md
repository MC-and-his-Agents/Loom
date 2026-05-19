# WI-782 Implementation Contract

- Keep scope inside adoption/bootstrap verify behavior.
- Do not promote repo-specific downstream rules into Loom core.
- Use Git plumbing/status checks instead of ad hoc `.gitignore` string guesses where possible.
- Treat runtime scratch/cache/tmp paths as ignored runtime residue, not stable carriers.
- Generated `skills/**` changes must come from `src/skills/**` via `tools/skills_surface.py generate`.
