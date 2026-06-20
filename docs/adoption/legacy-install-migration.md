# Legacy Install Migration

This document defines the migration path from older repo-local Loom installs to
the pure global model.

## Target State

- The workstation installs the global CLI: `npm install -g @mc-and-his-agents/loom`.
- Codex uses a user-level Loom plugin installed and registered from that global
  package.
- The target repository keeps only metadata-only adoption truth, such as
  `.loom/installed-state.json` and the Loom bootstrap block in `AGENTS.md`.
- The target repository does not keep Loom-owned repo-local runtime, plugin, or
  generated skills payloads.

## Migration Commands

Run these commands from the target repository:

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom install --target . --apply --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

`loom host install` and `loom host register` write only user workstation state.
`loom install` writes repository adoption metadata and the Loom bootstrap block.
It does not write `plugins/loom`, `.agents/skills`, `.loom/bin`, `.loom/bootstrap`,
or root `skills`.

## Legacy Residue

Current verification fails closed when the target repository still contains any
of these older Loom-owned repo-local surfaces:

- `.loom/bin`
- `.loom/bootstrap`
- `plugins/loom`
- `.agents/skills`
- root `skills`

Do not treat these paths as current install proof. Remove or migrate them only
after confirming they are Loom-owned and not target-owned repository content.
Loom diagnostics report the residue; they do not automatically delete it.

## New Device Checkout

When a new workstation clones a repository that already adopted Loom, run:

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom host verify --host codex --target . --json
loom doctor --target . --json
```

If Codex already loaded its plugin list, start a new Codex session or restart
Codex Desktop after registration.
