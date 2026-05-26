# WI-1065 Spec

## Acceptance Criteria

- The repository root defines npm package `@mc-and-his-agents/loom` with version derived from root `VERSION` without the `v` prefix.
- The package exposes a `loom` bin that executes the committed `tools/loom.py` CLI from the packaged payload.
- The package payload is explicit and includes the CLI/runtime, skills registry, plugin manifest, and contract docs required for `loom --help` and `loom version` smoke commands.
- The package payload excludes repository-internal governance state, GitHub workflow state, examples, and `packages/loom-installer`.
- `npm pack --dry-run` and a local npm install smoke prove that the package can be installed and run without depending on `@mc-and-his-agents/loom-installer`.
- Existing release/version/CLI checks continue to pass.

## Non-goals

- Do not publish the npm package.
- Do not add npm publish automation or tokens.
- Do not hard-cut README or primary install docs in this batch.
- Do not implement CLI-managed plugin/SKILLS mutation beyond the existing CLI smoke surface.
- Do not restore or advance `loom-installer`.
