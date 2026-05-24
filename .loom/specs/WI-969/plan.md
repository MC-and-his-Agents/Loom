# WI-969 Plan

1. Verify `codex exec -m gpt-5.5` is accepted by the current Codex CLI before changing defaults.
2. Upgrade built-in stable review engine profiles from `gpt-5.2` to `gpt-5.5` while preserving existing reasoning effort.
3. Add repo-owned review profile policy parsing and validation with fail-closed behavior.
4. Add explicit local Codex config opt-in and enforce source precedence, reason requirements, and CI/headless restrictions.
5. Extend Codex App authoritative adapter metadata so requested and actual engine proof are traceable.
6. Expand `loom_check` fixtures for built-in defaults, CLI overrides, repo policy validation, local config opt-in, Codex App proof modes, and fallback execution.
7. Update review execution docs and regenerate `skills/` runtime surfaces from `src/skills/`.
8. Bump installer package version metadata required by the Node installer PR gate and refresh Loom work item/review carriers for PR #985.
9. Validate locally, push PR #985, wait for required checks, merge, then run reconciliation and closeout for #970-#975 and #969.
