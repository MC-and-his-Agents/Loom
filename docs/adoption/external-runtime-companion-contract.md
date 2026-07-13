# External Runtime Companion Contract

The transition described by earlier versions is complete: `global-cli` is the
only supported runtime provider for adopted repositories. A vendored
`.loom/bin` runtime is removed-state residue, not a fallback.

## Current boundary

- Repository companion files may declare repo-specific read-only integration
  locators.
- `external_result_sources` may read and validate external results; they do not
  execute host actions or own product truth.
- Runtime execution comes from the installed public `loom` CLI.
- Current/status/progress/review/shadow and ordinary closeout carriers are not
  preserved during migration.
- Missing CLI/provider state blocks with a precise remediation; it does not
  trigger rebootstrap or restore a repo-local runtime.

Use:

```bash
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
loom upgrade --target . --json
loom repair plan --target . --json
```

Removal is explicit and ownership-aware. Loom must not delete target-owned
content, and compatibility input must never re-enter the default execution path.
