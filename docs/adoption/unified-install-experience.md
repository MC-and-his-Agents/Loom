# Unified Install Experience

Loom uses one public runtime and one host-owned plugin path:

1. Install or update the root CLI with
   `npm install -g @mc-and-his-agents/loom@latest`.
2. Install or update the Loom plugin through the Codex marketplace/plugin host.
3. Adopt a repository with `loom install --target . --apply --json`.
4. Read back with `loom installed-state validate`, `loom verify`, and
   `loom doctor`.
5. Start a new Codex task after plugin refresh.

Codex is the only `native/primary` agent harness. Other reliable CLI callers
are `CLI-compatible`; unverified hosts are `unsupported`. Agents enter through
`loom-init`. The source distribution may contain generated
`plugins/loom/skills` for packaging, but adopted repositories never receive it.

The repository receives metadata-only adoption. It does not receive `.loom/bin`,
plugin Python copies, generated skills, current/status/progress/review/shadow,
or closeout carriers.

## Runtime and source boundaries

- `global-cli` is the only supported repository runtime provider.
- `src/skills/` is canonical source; generated plugin/package mirrors are build
  outputs and must pass digest checks.
- Codex marketplace/cache state remains workstation-private.
- GitHub owns PR/head/check/merge facts.
- Loom derives lifecycle state from explicit typed locators and host/worktree
  readback.

Legacy repo-local payloads are reported by `loom detect`, `loom doctor`,
`loom upgrade`, and `loom repair plan`. They are not automatically restored or
deleted.

Normal agent use is `loom ... --json`. Each failure has one primary cause and
one public CLI remediation or a separately typed manual/provider action.
