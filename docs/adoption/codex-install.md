# Installing Loom for Codex

Loom has two independent workstation dependencies:

- the public `loom` CLI, published as `@mc-and-his-agents/loom`;
- the Codex Loom plugin, installed and refreshed by Codex's marketplace/plugin host.

Neither dependency is repository truth. Adopted repositories keep metadata only
and do not vendor `.loom/bin`, plugin payloads, generated skills, current,
progress, review, shadow, or closeout carriers.

## Install or update

```bash
npm install -g @mc-and-his-agents/loom@latest
loom install --target . --apply --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

Install or update the `loom` plugin through the Codex marketplace/plugin host,
then start a new Codex task so the refreshed skills are loaded. Loom does not
write Codex private plugin state and does not claim that an existing task can
hot-load an updated plugin.

`loom verify` and `loom doctor` report the CLI, repository metadata, and visible
Codex provider boundary separately. A missing plugin is a Codex provider action,
not permission to restore a repository-local runtime.

## Legacy residue

`.loom/bin`, `.loom/bootstrap`, `plugins/loom`, `.agents/skills`, and
Loom-generated repository `skills/` are migration residue, not install proof.
Use `loom upgrade --target . --json` and `loom repair plan --target . --json` to
inspect ownership. Remove residue only when Loom ownership is proven; never
delete target-owned skills automatically.

See [legacy-install-migration.md](./legacy-install-migration.md) and
[installation-taxonomy.md](./installation-taxonomy.md).
