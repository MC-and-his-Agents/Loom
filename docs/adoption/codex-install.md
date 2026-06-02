# Installing Loom for Codex

Use the root `loom` CLI as the only primary install entry. For Codex plugin
mode, the CLI installs and verifies the target repository's repo-local Codex
plugin payload, including embedded Loom skills under `plugins/loom/skills/`.

## Prerequisites

- Node `>=20`
- Python `>=3.11`

## Installation

1. Install the root CLI:

   ```bash
   npm install -g @mc-and-his-agents/loom
   ```

2. Install the Codex host payload into the target repository:

   ```bash
   loom host install --host codex --mode plugin --target . --apply --json
   ```

3. Verify the target repository payload:

   ```bash
   loom host verify --host codex --mode plugin --target . --json
   loom skills check --target . --json
   loom doctor --target . --json
   ```

`loom host verify --host codex --mode plugin` verifies the target repository
plugin payload only. It checks `.loom/installed-state.json`,
`plugins/loom/.codex-plugin/plugin.json`, and the embedded
`plugins/loom/skills/` payload; it does not require downstream top-level
`skills/`, and it does not prove Codex Desktop has registered, enabled, or
loaded the plugin on the current workstation.

4. Register the repo-local Codex plugin payload with this workstation when the
   repository is used in Codex Desktop:

   ```bash
   loom host register --host codex --source ./plugins/loom --scope user --dry-run --json
   loom host register --host codex --source ./plugins/loom --scope user --apply --json
   ```

Codex should start from `loom-init` after host discovery reloads. The plugin
directory is the CLI-managed payload in the target repository; its embedded
`plugins/loom/skills/` directory is the Loom skills payload for plugin mode.
Downstream top-level `skills/` belongs to the target repository namespace unless
an explicit future profile owns it. Workstation registration is a user-level Codex Desktop state:
personal marketplace entry, user plugin cache payload, and Codex config
enablement. It is reported by `loom doctor` but is not written into target
repository truth.

If Codex Desktop already loaded its plugin list, start a new Codex session or
restart Codex Desktop after registration. Loom reports this reload requirement;
it does not claim that the current session hot-loads newly registered plugins.

This installs Loom's generated skill and plugin payloads for the target
repository. It does not define which `.loom` files an adopted target repository
should commit. Target repository `.loom` carrier visibility is defined in
[loom-surfaces-version-control.md](./loom-surfaces-version-control.md).

## Update

```bash
npm update -g @mc-and-his-agents/loom
loom host install --host codex --mode plugin --target . --apply --force --json
loom host verify --host codex --mode plugin --target . --json
loom host register --host codex --source ./plugins/loom --scope user --dry-run --json
loom host register --host codex --source ./plugins/loom --scope user --apply --json
```

## Compatibility

The npm installer is not the Codex default path. `@mc-and-his-agents/loom-installer`
is a deprecated historical artifact. It is not the Codex install path and must
not be used as evidence that the root `loom` CLI was installed or published.

## Legacy Top-Level Skills

Repositories adopted under the older downstream plugin layout may still contain
Loom-generated top-level `skills/` next to `plugins/loom/skills/`. In plugin
mode, that top-level directory is legacy residue, not a required current layer.
`loom doctor`, `loom repair plan`, and `loom upgrade-plan` report it before any
operator considers removal. Loom must not delete or overwrite target-owned
non-Loom skills automatically.
