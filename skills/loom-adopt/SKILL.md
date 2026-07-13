---
name: loom-adopt
description: Adopt a repository through Loom metadata and verify the global runtime provider.
---

# Loom Adopt

Use for first adoption or a supported v0.30→v0.31 upgrade.

```bash
loom install --target <repo> --apply --json
loom installed-state validate --target <repo> --json
loom verify --target <repo> --json
loom doctor --target <repo> --json
```

For an existing v0.30 installation, inspect the read-only plan first:

```bash
loom upgrade --target <repo> --json
loom upgrade --target <repo> --apply --json
loom verify --target <repo> --json
```

Plugin installation belongs to the Codex marketplace/plugin host. Do not copy
runtime or skills payloads into the target repository. Adoption is complete
when installed-state, global CLI provider, and metadata-only boundary pass and
no unsupported legacy surface is recommended as remediation.
