# Global CLI and Codex User Plugin Contract

The supported default product surface is the 30-command public CLI plus the
Codex marketplace plugin. The CLI owns runtime execution; Codex owns plugin
installation, cache refresh, enablement, and task reload.

## Authorities

| Fact | Authority |
| --- | --- |
| CLI package/version | npm package, root `VERSION`, release tag |
| Plugin source/version/hash | Loom release payload and marketplace catalog |
| Installed plugin/cache | Codex workstation state |
| Repository adoption | `.loom/installed-state.json` and companion metadata |
| Branch, PR, head, checks, merge | GitHub live readback |
| Current task/worktree | explicit CLI input and host/worktree readback |

Workstation state is not written into Git. Repository adoption must not create
`.loom/bin`, current/status/progress/review/shadow carriers, or a closeout PR.

## Default flow

```bash
npm install -g @mc-and-his-agents/loom@latest
loom install --target . --apply --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

Codex plugin installation/update is performed by Codex's marketplace/plugin
host. After an update, open a new task to load the refreshed plugin.

Lifecycle commands consume explicit typed Work Item, branch, worktree, PR, and
host facts. They do not fall back to a committed current pointer or repository
execution carriers. A removed command fails closed with one
`unsupported_command_surface` cause and routes to `loom help --json`.

## Compatibility

Legacy repo-local runtime and plugin payloads are diagnostics-only. They may be
read to produce a safe migration plan but are never a fallback runtime. The
current public surface and protocol ownership are defined by `loom help --json`.
