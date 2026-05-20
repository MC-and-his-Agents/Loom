# WI-819 Implementation Contract

## Truth Sources

- `docs/methodology/templates/default-governance-scaffold-policy.md`
- `docs/methodology/governance/goal-schema.md`
- `docs/methodology/harness/governance-lint-taxonomy.md`
- `docs/methodology/harness/workspace-lifecycle.md`
- `docs/methodology/harness/workspace-and-purity.md`

## Runtime Surfaces

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/governance_surface.py`
- `src/skills/loom-retire/**`
- generated `skills/**/.loom-runtime/**`
- repo-local `.loom/bin/**` and `.loom/bootstrap/**` runtime hashes

## Boundaries

- `repo_specific` lint findings remain companion / profile evidence and are not core taxonomy rules.
- `workspace retire` reports local cleanup evidence and does not mutate versioned recovery or status carriers.
- malformed unrelated Work Item carriers are diagnostic report-only until they are proven to bind the current workspace; same-workspace unknown and active conflicts remain blocking.
