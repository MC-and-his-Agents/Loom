# WI-877 Implementation Contract

## Write Scope

- `.loom/work-items/WI-877.md`
- `.loom/progress/WI-877.md`
- `.loom/reviews/WI-877.json`
- `.loom/reviews/WI-877.spec.json`
- `.loom/specs/WI-877/*`
- `.loom/progress/WI-876.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `docs/methodology/harness/pr-merge-gate.md`
- `src/skills/shared/scripts`
- `skills`

## Guardrails

- Keep #877 limited to parser preflight and diagnostics.
- Do not implement #874 render/edit validation, #875 fixture migration expansion, #957 readiness/cost guard, or #1107 full spec suite CLI tree.
- Do not rewrite frozen core contracts.
- Do not let parser or CLI output replace Work Item, review, merge-ready, closeout, or docs/source truth.
