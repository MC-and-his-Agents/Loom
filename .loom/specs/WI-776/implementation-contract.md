# WI-776 Implementation Contract

- Keep the change scoped to adoption intake/classification and its tests/docs.
- Do not create a new heavy scaffold profile for docs-first repositories.
- Do not promote downstream repo-specific policy, review, or release rules into Loom core.
- Distinguish domain/product fact-model docs from engineering shared contracts or runtime schemas.
- Generated `skills/**` changes must come from `src/skills/**` via `tools/skills_surface.py generate`.
