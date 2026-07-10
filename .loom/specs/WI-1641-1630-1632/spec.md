# WI-1641-1630-1632 Spec

- Suite path: not_applicable
- Rationale: This PR is a tightly scoped implementation/package-surface convergence for milestone #14 PR2. It changes generated skills/package payload behavior and validates through targeted contract checks rather than a new product behavior suite.
- Consumer boundary: skills generation, plugin payload packaging, CLI skills package reporting, npm package payload, host adapter checks, and release/version surface checks.
- Recheck condition: Reopen formal suite if this PR starts implementing user-level plugin install/register, removing repo-local CLI commands, migration UX, legacy gate policy, or v0.17.0 release execution.
- Scope proof: Bound to issues #1641/#1630/#1632 and branch `work/1641-plugin-payload-only`.
- Review requirement: implementation review before merge-ready.

## Acceptance Criteria

- AC-1: `plugins/loom/skills/` is generated from `src/skills/` and is the only current skills publishing payload for Codex plugin distribution.
- AC-2: Generated root `skills/` remains a checked-in mirror for source review/tests, not a current install target or single-skill distribution package.
- AC-3: Generated surfaces no longer contain `loom-package.json` or package-internal `.loom-runtime/` directories.
- AC-4: `loom skills package --json` reports plugin payload metadata instead of per-skill package metadata.
- AC-5: package/version/host adapter checks consume plugin payload provider semantics and fail closed on reintroduced single-skill artifacts.
