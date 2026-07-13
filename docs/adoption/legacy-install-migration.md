# Legacy Install Migration

## Target state

- global `@mc-and-his-agents/loom@latest` CLI;
- Codex marketplace-managed Loom plugin;
- metadata-only repository adoption;
- no repo-local runtime, plugin payload, generated skills, or execution carriers.

## Migration

```bash
npm install -g @mc-and-his-agents/loom@latest
loom upgrade --target . --json
loom repair plan --target . --json
loom install --target . --apply --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

Refresh the Loom plugin through Codex's marketplace/plugin host and start a new
task. Do not call removed `loom host`, `loom skills`, or repo-local Python
entrypoints.

Legacy `.loom/bin`, `.loom/bootstrap`, `plugins/loom`, `.agents/skills`, and
Loom-generated repository `skills/` are removed only after ownership readback.
Target-owned files fail closed to manual review. Migration never restores
current/status/progress/review/shadow or closeout carriers.
