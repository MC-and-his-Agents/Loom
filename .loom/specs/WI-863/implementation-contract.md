# WI-863 Implementation Contract

## Allowed Change Surface

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/loom-review/SKILL.md`
- `src/skills/loom-spec-review/SKILL.md`
- Generated `skills/**` surfaces derived from `src/skills`
- `docs/methodology/harness/review-execution.md`
- Loom Work Item, progress, spec, review, status, and runtime evidence carriers for `WI-863`

## Required Properties

- Verified Codex App host proof must be evaluated before treating `CI` or `CODEX_CI` as headless fallback.
- Complete App proof must select `loom/codex-app-review` with `selection_source = codex-app-host-default`.
- Incomplete proof must preserve safe fallback and expose missing proof diagnostics.
- App proof discovery must remain bounded and must not repeatedly scan broad host state during fixtures.
- Authoritative App raw output must be stored only as runtime evidence.
- `review record` and merge-ready/review gate must consume normalized `review_record_input` and the single authored review record.

## Exit Criteria

- Local validation passes.
- Live Codex App review proof is recorded.
- PR gates pass.
- Controlled merge completes.
- `main` is synchronized.
- #863 and #864 are closed with evidence.
