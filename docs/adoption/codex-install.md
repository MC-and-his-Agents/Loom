# Installing Loom for Codex

Use the root `loom` CLI as the only primary install entry. Codex adoption uses
metadata-only repository adoption plus a Codex user-level Loom plugin provider.
The milestone #14 target contract is
[global-cli-user-plugin-contract.md](./global-cli-user-plugin-contract.md), and
the authority terms are defined in
[installation-taxonomy.md](./installation-taxonomy.md).

## Prerequisites

- Node `>=20`
- Python `>=3.11`

## Installation

1. Install the root CLI:

   ```bash
   npm install -g @mc-and-his-agents/loom
   ```

2. Install and register the Codex user-level Loom plugin:

   ```bash
   loom host install --host codex --scope user --apply --json
   loom host register --host codex --scope user --apply --json
   ```

3. Adopt the target repository with metadata only.

Metadata-only adoption records repository adoption truth and relies on the
user-level Codex Loom plugin provider. It must not write `plugins/loom/skills/`,
`plugins/loom/.codex-plugin/plugin.json`, `.loom/bin`, `.agents/skills`, or root
`skills/`:

   ```bash
   loom install --target . --apply --json
   loom installed-state validate --target . --json
   loom host verify --host codex --target . --json
   loom skills check --target . --json
   loom doctor --target . --json
   ```

4. Verify the target repository mode:

   ```bash
   loom host verify --host codex --target . --json
   loom skills check --target . --json
   loom doctor --target . --json
   ```

`loom host verify --host codex` verifies repository
adoption metadata and reports the user-level provider requirement separately.
It does not require downstream top-level `skills/`, and it does not prove Codex
Desktop has registered, enabled, or loaded the plugin on the current
workstation.

If the repository still carries `.loom/bin`, `.loom/bootstrap`, `plugins/loom/`,
`.agents/skills`, or Loom-owned root `skills/`, treat those paths as unsupported
legacy residue until `doctor` classifies them.

<!-- legacy-installer-doc-sync-anchor: loom host install --host codex --scope user --apply --json -->
<!-- legacy-installer-doc-sync-anchor: loom host verify --host codex --target . --json -->
<!-- legacy-installer-doc-sync-anchor: CLI-managed payloads -->

The legacy installer doc-sync anchor above is retained only for checker
continuity. In the milestone #14 target it is historical vocabulary for
unsupported repo-local plugin payload residue, not a compatible current install
command.

Codex should start from `loom-init` after host discovery reloads. In
metadata-only adoption, the user-level Codex Loom plugin is the skills provider.
Downstream top-level `skills/` belongs to the target repository namespace unless
explicit Loom ownership is proven. Workstation registration is a user-level
Codex Desktop state: personal marketplace entry, user plugin cache payload, and
Codex config enablement. It is reported by `loom doctor` but is not written into
target repository truth.

Global CLI runtime availability is a separate provider dependency from Codex
Desktop registration. A repository may depend on both during migration or
compatibility mode, and Loom should report those gaps separately instead of
collapsing them into generic repository payload drift.

If Codex Desktop already loaded its plugin list, start a new Codex session or
restart Codex Desktop after registration. Loom reports this reload requirement;
it does not claim that the current session hot-loads newly registered plugins.

This installs the Codex user-level Loom plugin and records metadata-only
repository adoption. Target repository `.loom` carrier visibility is defined in
[loom-surfaces-version-control.md](./loom-surfaces-version-control.md).

## Update

```bash
npm update -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom host verify --host codex --target . --json
```

## Compatibility

The npm installer is not the Codex default path. `@mc-and-his-agents/loom-installer`
is a deprecated historical artifact. It is not the Codex install path and must
not be used as evidence that the root `loom` CLI was installed or published.

## Legacy Repository Payload

Repositories adopted under the older downstream plugin layout may still contain
`.loom/bin`, `.loom/bootstrap`, `plugins/loom/`, `.agents/skills`, or
Loom-generated top-level `skills/`. These paths are unsupported legacy residue,
not a required current layer. `loom doctor`, `loom repair plan`, and
`loom upgrade-plan` report them before any operator considers removal. Loom must
not delete or overwrite target-owned non-Loom skills automatically.
