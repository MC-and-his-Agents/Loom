# WI-876 Implementation Contract

## Write Scope

- `.loom/work-items/WI-876.md`
- `.loom/progress/WI-876.md`
- `.loom/reviews/WI-876.json`
- `.loom/specs/WI-876/*`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `docs/adoption/repo-companion-contract.md`
- `docs/methodology/templates/pull-request.md`
- `src/skills/shared/references/adoption/repo-companion-contract.md`
- `src/skills/shared/references/templates/pull-request.md`
- generated `skills/**` reference copies

## Guardrails

- Keep #876 contract-only.
- Do not change parser behavior, CLI command output, PR gate semantics, closeout semantics, or runtime contracts.
- Do not let parser/preflight/render output replace Work Item, review, merge-ready, closeout, or docs/source truth.
- Regenerate generated skills references from source rather than editing only generated copies.
