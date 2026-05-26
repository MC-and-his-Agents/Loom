# Installing Loom for Codex

Use the root `loom` CLI as the only primary install entry. The CLI installs,
synchronizes, and verifies the generated SKILLS payload and Codex plugin payload
for the target repository.

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

3. Verify the installed payload:

   ```bash
   loom host verify --host codex --mode plugin --target . --json
   loom skills check --target . --json
   loom doctor --target . --json
   ```

Codex should start from `loom-init` after host discovery reloads. The plugin and
SKILLS directories are CLI-managed payloads, not separate user install surfaces.

This installs Loom's generated skill and plugin payloads for the target
repository. It does not define which `.loom` files an adopted target repository
should commit. Target repository `.loom` carrier visibility is defined in
[loom-surfaces-version-control.md](./loom-surfaces-version-control.md).

## Update

```bash
npm update -g @mc-and-his-agents/loom
loom host install --host codex --mode plugin --target . --apply --force --json
loom host verify --host codex --mode plugin --target . --json
```

## Compatibility

The npm installer is not the Codex default path. `@mc-and-his-agents/loom-installer`
is a deprecated historical artifact. It is not the Codex install path and must
not be used as evidence that the root `loom` CLI was installed or published.
