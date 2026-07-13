# CLI-Only Install Contract

The only Loom runtime install is:

```bash
npm install -g @mc-and-his-agents/loom@latest
```

The package name is `@mc-and-his-agents/loom`, the executable is `loom`, and the
root `VERSION`, npm version, Git tag, GitHub Release, and release commit must
agree. `@mc-and-his-agents/loom-installer` is a retired historical artifact.

The Codex plugin is not installed by a Loom `host` command. Codex's own
marketplace/plugin host owns plugin install, update, enablement, cache, and task
reload. Repository adoption remains separate:

```bash
loom install --target . --apply --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

The package may contain generated distribution payloads, but downstream
repositories must not vendor them. Missing runtime/provider support fails
closed; it never authorizes restoration of a repo-local wrapper.
