# WI-1064 Spec

## Acceptance Criteria

- A version-controlled adoption contract freezes the only primary install surface as the root `loom` CLI.
- The contract names `@mc-and-his-agents/loom` as the target npm package and `loom` as the user-facing bin.
- The contract states that `plugins/` and `skills/` are CLI-managed payloads, not standalone user install entries.
- The contract states that `@mc-and-his-agents/loom-installer` is deprecated historical/compatibility evidence only and must not appear as a primary install path in follow-on work.
- The contract records runtime, npm token, version authority, release evidence, and permission-block handling boundaries for #1065-#1070.
- Existing release/version/CLI checks continue to pass.

## Non-goals

- Do not implement the root npm package.
- Do not add npm publish automation.
- Do not publish npm, create tags, or create GitHub Releases.
- Do not hard-cut README or primary install docs in this batch.
- Do not restore or advance `loom-installer`.
