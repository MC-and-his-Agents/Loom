# Global CLI And User Plugin Install Contract

This document freezes the milestone #14 target install contract for #1621,
#1622, #1623, #1628, and #1638.

## Target Model

Loom has one supported downstream adoption model:

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom install --target . --apply --json
loom doctor --target . --json
```

The global `loom` CLI owns runtime execution. The Codex user-level Loom plugin
owns Loom skill discovery. The target repository owns only adoption metadata and
repo governance carriers.

## Repository Adoption Output

Metadata-only adoption writes repository truth only:

- `.loom/installed-state.json`
- root `AGENTS.md`, creating it first when it is missing
- Loom governance carriers that are explicitly part of repository truth

It must not write runtime, plugin, or skills payload into the target repository:

- no `.loom/bin` runtime layer
- no `plugins/loom/.codex-plugin/plugin.json`
- no `plugins/loom/skills/`
- no `.agents/skills`
- no Loom-owned root `skills/`

## Installed-State Semantics

An adopted repository declares:

```json
{
  "schema_version": "loom-installed-state/v2",
  "runtime_provider": "global-cli",
  "repo_payload": {
    "mode": "metadata-only",
    "intentional_absent_paths": [
      ".loom/bin",
      "plugins/loom/.codex-plugin/plugin.json",
      "plugins/loom/skills",
      ".agents/skills",
      "skills"
    ]
  },
  "skills_provider": {
    "provider": "codex-loom-plugin",
    "scope": "user",
    "required": true,
    "registration_authority": "workstation"
  },
  "provider_requirements": {
    "global_cli": {
      "required": true,
      "provider": "loom-cli",
      "authority": "workstation",
      "compatibility_mode_allowed": false
    }
  }
}
```

`installed-state validate` validates repository metadata. `doctor` may block on
missing global CLI or missing Codex user plugin, but those are provider gaps, not
repository payload drift.

## Codex User-Level Plugin Target

`loom host install --host codex --scope user --apply --json` installs the Codex
Loom plugin from the global Loom package into Codex user-level state. It must not
read from or write to `plugins/loom` in the target repository.

`loom host register --host codex --scope user --apply --json` registers/enables
that user-level plugin for Codex discovery.

Dry-run output must list only user-level planned writes, such as:

- Codex personal marketplace entry
- Codex user plugin cache payload
- Codex user config enablement

No dry-run or apply path may plan target repository writes for plugin install or
registration.

## Legacy Residue

The following paths are unsupported legacy residue in downstream repositories:

- `plugins/loom/`
- `.loom/bin`
- `.loom/bootstrap`
- `.agents/skills`
- Loom-owned root `skills/`
- `@mc-and-his-agents/loom-installer`

Detection and doctor output may classify them and explain the cleanup action.
They must not be treated as a current install, a fallback runtime, or a
compatible plugin payload.

## Host AGENTS.md Bootstrap Block

Metadata-only adoption must ensure the target repository root has `AGENTS.md`.
If it already exists, Loom inserts or updates this managed block. If it is
missing, Loom creates the file with this block:

```markdown
<!-- LOOM_BOOTSTRAP_START -->
## Loom Bootstrap

本仓库采用 Loom 来管理 agent 执行流程、工作事实载体、review、merge-ready 和 closeout；开始实现、review、merge-ready 或 closeout 前，先完成以下 bootstrap 检查。

1. 检查 `.loom/installed-state.json`。
2. 若本机没有 `loom`，执行：
   `npm install -g @mc-and-his-agents/loom`
3. 运行：
   `loom doctor --target . --json`
4. 若 Codex Loom plugin 缺失，执行：
   `loom host install --host codex --scope user --apply --json`
   `loom host register --host codex --scope user --apply --json`
5. 重新运行：
   `loom doctor --target . --json`

不要把 Loom runtime、plugin 或 skills payload 写入仓库；它们属于用户级全局安装。
<!-- LOOM_BOOTSTRAP_END -->
```

The block is root-only. Loom does not create subdirectory `AGENTS.md` files as
part of adoption.

## Consumer Boundary

This contract is a target-state contract. It does not implement command behavior.
Implementation work must consume it without reintroducing repo-local plugin
install, repo-local runtime install, or single-skill distribution semantics.
