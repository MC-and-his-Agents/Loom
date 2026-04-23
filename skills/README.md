# Skills

`skills/` is the canonical skills library for Loom.

When Loom is installed through Codex native skill discovery, a host plugin, or the npm installer, this directory is the user-facing execution surface. The methodology and architecture docs stay behind this layer; users should normally enter through skills, not through internal governance documents.

默认从 `loom-init` 开始。它是 Loom 唯一的 root entry，负责两件事：

- 初始化 Loom，或把 Loom retrofit 进既有仓库
- 在没有显式指定场景 skill 时，根据任务信号把执行者导向正确场景

## Skills Library

Loom exposes one root entry and seven scenario skills:

| Skill | Role |
| --- | --- |
| `loom-init` | Root entry; initializes and routes. |
| `loom-adopt` | Initializes a new repository or retrofits Loom into an existing one. |
| `loom-resume` | Restores context and continues execution. |
| `loom-pre-review` | Checks readiness before formal review. |
| `loom-review` | Runs formal review and records review output. |
| `loom-handoff` | Writes a handoff point and next-step state. |
| `loom-retire` | Cleans up or retires the current worksite. |
| `loom-merge-ready` | Performs the final pre-merge readiness check. |

## Entry Model

Loom supports two entry modes:

- Explicit entry: the user names a scenario skill directly.
- Routed entry: the user starts at `loom-init`, and `loom-init` selects the scenario from task signals.

If task signals are incomplete, ambiguous, or missing required execution inputs, route back to `loom-init` and ask for the smallest missing signal. Stable routing rules live in [route-matrix.md](./route-matrix.md).

## Install Model

The primary install model is the complete Loom skills library:

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
mkdir -p ~/.agents/skills
ln -s ~/.codex/loom/skills ~/.agents/skills/loom
```

The npm installer can also install the complete plugin surface:

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

## Advanced / Compatibility

Single-skill installation is supported for advanced compatibility, not as the default user journey:

```bash
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host codex
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host claude
```

A single installed skill only exposes that named skill to the host. It does not expose the full `loom-init` routing surface unless `loom-init` itself is installed, and it should not be presented as the complete Loom experience.

## Internal Contracts

These files are part of the runtime contract and should remain stable:

- [registry.json](./registry.json)
- [install-layout.json](./install-layout.json)
- [upgrade-contract.json](./upgrade-contract.json)
- [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)

Shared runtime scripts, assets, and references live under [shared/](./shared/). They are consumed by scenario skills and by release tooling when generating plugin or single-skill payloads.
