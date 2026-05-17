# WI-750 Implementation Contract

## Owned Paths

- `skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/loom_check.py`
- `docs/methodology/harness/review-execution.md`
- `skills/shared/references/harness/review-execution.md`
- `src/skills/shared/references/harness/review-execution.md`
- `skills/loom-review/SKILL.md`
- `src/skills/loom-review/SKILL.md`
- `skills/loom-spec-review/SKILL.md`
- `src/skills/loom-spec-review/SKILL.md`
- `skills/*/.loom-runtime/**`
- `examples/new-project/.loom/**`
- `examples/new-project/.github/PULL_REQUEST_TEMPLATE.md`
- `packages/loom-installer/package.json`
- `packages/loom-installer/package-lock.json`
- `.loom/work-items/WI-750.md`
- `.loom/progress/WI-750.md`
- `.loom/reviews/WI-750.json`
- `.loom/reviews/WI-750.spec.json`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/specs/WI-750/**`

## Invariants

- Do not remove Stage 1/2 shadow or opt-in compatibility interfaces.
- Do not let raw Codex App evidence become merge-ready approval truth.
- Do not change Loom review record consumption semantics outside the #750 adapter selection and metadata scope.
- Do not make Codex App default in CI, headless, missing proof, or unavailable app-server contexts.
- Fail closed on proof conflicts or target/head/schema binding failures.
