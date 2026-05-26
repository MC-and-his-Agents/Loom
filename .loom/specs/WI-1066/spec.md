# WI-1066 Spec

## Acceptance Criteria

- `loom host install --host codex --mode plugin --target <repo> --apply --json` installs the Codex plugin payload, synchronized SKILLS payload, and `loom-installed-state/v2` metadata without invoking `packages/loom-installer`.
- `loom host verify --host codex --mode plugin --target <repo> --json` verifies the CLI-managed plugin manifest, plugin-local SKILLS payload, repository SKILLS payload, and installed-state metadata without mutating files.
- `loom skills sync --target <repo> --apply --json` synchronizes SKILLS payload through the root `loom` CLI, and `loom skills check --target <repo> --json` verifies installed payloads.
- `loom detect --target <repo> --json` classifies CLI-managed plugin/SKILLS payloads with valid installed-state metadata as `current`, not legacy or mixed legacy.
- CLI contract tests cover the install, verify, skills check, and detect current classification smoke path.
- Existing package/release/version checks continue to pass, and `loom-installer` is not used as a user-visible or runtime install dependency.

## Non-goals

- Do not publish the npm package.
- Do not add npm publish workflow or release tags.
- Do not hard-cut README or primary install docs in this batch; #1067 owns that.
- Do not implement host-specific marketplace packaging beyond the Codex plugin smoke path.
- Do not restore or advance `loom-installer`.
