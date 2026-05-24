# WI-969 Spec

## Acceptance

- Stable review engine profiles `default`, `high-risk`, `spec-review`, and `repeated-blocker` must resolve to `gpt-5.5` by default.
- Reasoning effort remains `medium` for `default` and `high` for `high-risk`, `spec-review`, and `repeated-blocker`.
- Repo-owned `.loom/review-profiles.json` policy must use schema `loom-review-profiles/v1`, allow only stable profile ids, and fail closed on unknown schema, unknown profile ids, empty models, unknown reasoning effort, or missing selection reasons.
- Review engine profile source order must be explicit CLI override, repo-owned policy, explicit local Codex config opt-in, then Loom built-in stable profile.
- Local Codex config defaults must never be read by default; `--engine-use-local-codex-defaults` requires `--engine-override-reason`, and CI/headless/merge gate must reject it unless repo policy explicitly allows it.
- Codex App authoritative review evidence must record requested model/reasoning, actual model/reasoning proof when available, proof source, and enforcement mode in traceable review metadata.
- Unverified or mismatched engine proof must fail closed for `high-risk`, `spec-review`, and `repeated-blocker`; `default` may continue only with structured unverified evidence.
- Generated skills runtime, shared references, docs, fixtures, and installer package version metadata must stay synchronized with the source runtime behavior.

## Non-Goals

- Do not implement #836 adopted repo migration.
- Do not implement #957 expensive review readiness or cost guard changes.
- Do not remove `loom/default-codex-exec` fallback.
- Do not make raw Codex App output or local Codex config the authored review truth.
