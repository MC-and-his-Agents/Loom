# WI-1067 Spec

## Acceptance Criteria

- README and README.zh-CN present `npm install -g @mc-and-his-agents/loom` and root `loom` CLI commands as the primary install path.
- Codex install documentation uses the root `loom` CLI to install, synchronize, and verify Codex plugin/SKILLS payloads.
- Primary adoption and release-surface docs identify `@mc-and-his-agents/loom` as the user-facing CLI install channel and do not describe plugin, SKILLS, or installer commands as independent primary install surfaces.
- `loom-installer` remains visible only as deprecated historical/evidence or compatibility text, without recommended command blocks in primary README/Codex install paths.
- The documentation change does not add npm publish automation, new checker enforcement, release tags, or installer release behavior.
- Existing static doc-sync checks may be aligned with the new CLI-only wording so validation no longer requires obsolete clone/symlink/installer primary-path text.

## Non-goals

- Do not harden checkers; #1068 owns enforcement. Limit any checker edits to stale static wording required by #1067 docs.
- Do not add npm publish workflow or release tags; #1069 owns automation.
- Do not perform the first npm publish; #1070 owns release execution.
- Do not restore, republish, or recommend `loom-installer`.
- Do not rewrite host adapter internals or generated skills payloads.
