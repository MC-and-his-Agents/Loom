# WI-969 Implementation Contract

## Write Scope

- `.loom/review-profiles.json`
- `.loom/work-items/WI-969.md`, `.loom/progress/WI-969.md`, `.loom/reviews/WI-969.json`, `.loom/reviews/WI-969.spec.json`, `.loom/specs/WI-969/*`, `.loom/status/current.md`, and terminal carrier cleanup needed for the active fact chain
- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/references/harness/review-execution.md`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_flow.py`, `skills/**/.loom-runtime/shared/scripts/loom_check.py`, and generated shared reference copies
- `skills/shared/scripts/loom_flow.py`, `skills/shared/scripts/loom_check.py`, and `skills/shared/references/harness/review-execution.md`
- `examples/new-project/.loom/bin/loom_flow.py`, `examples/new-project/.loom/bin/loom_check.py`, and matching bootstrap metadata
- `docs/methodology/harness/review-execution.md`
- `packages/loom-installer/package.json` and `packages/loom-installer/package-lock.json`

## Guardrails

- Fail closed on invalid review profile policy or unsafe engine proof for non-default profiles.
- Keep local Codex config opt-in explicit, reasoned, and lower precedence than repo policy.
- Preserve `loom/default-codex-exec` and continue passing `-m gpt-5.5` plus reasoning config through the fallback path.
- Keep authored review truth in the review record, with engine output retained only as evidence.
- Do not widen the PR into #836 or #957.
- Regenerate runtime surfaces from source rather than editing generated copies by hand.
