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

The Loom source repository may publish a Codex marketplace catalog that points
to its packaged plugin payload at `./plugins/loom`. That catalog is distribution
metadata only. It does not mean the plugin is installed, enabled, cached, or
fresh on any user's workstation.

When a user installs Loom through a Codex marketplace source, that action owns
only the Codex user-level plugin surface. It may replace the
`loom host install|register --host codex --scope user` refresh path for that
workstation, depending on the host's marketplace behavior, but it does not
install the global `loom` CLI and it does not write repository adoption truth.
The CLI is still installed or upgraded through the npm package, and each target
repository still needs its own `loom install`, `loom upgrade`, or
`loom runtime-upgrade ...` flow with repository-local validation, review, PR,
and closeout evidence.

Dry-run output must list only user-level planned writes, such as:

- Codex personal marketplace entry
- Codex user plugin cache payload
- Codex user config enablement

No dry-run or apply path may plan target repository writes for plugin install or
registration.

## Plugin Payload Freshness

The Codex user-level plugin payload is fresh only when the source package,
registered plugin source, and host runtime cache agree on plugin payload release
metadata:

- `source_package`: `@mc-and-his-agents/loom`
- `source_package_version`: the root npm package version that produced the
  payload
- `source_git_sha`: the release commit that produced the payload
- `plugin_payload_version`: the same release line as the root Loom package, for
  example `0.19.0`
- `plugin_payload_hash`: the deterministic hash defined in
  [version-authority-map.md](./version-authority-map.md)

`plugin_surface_version` remains the Codex plugin interface compatibility line.
It may stay unchanged while `plugin_payload_version` and
`plugin_payload_hash` change across Loom releases.

`registry_version` and per-skill `contract_version` are still validated as
payload integrity and behavior-contract evidence, but they must not be used as
the freshness decision for the installed Codex plugin payload.

## Plugin Refresh Guidance

`loom version --json`, `loom doctor`, `loom host doctor --host codex --scope
user --json`, and `loom upgrade-plan --target <repo> --host codex --json` expose
the same plugin payload freshness decision.

When the registered Codex plugin source is missing, stale, or missing release
metadata, the executable refresh path is:

```bash
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom host doctor --host codex --scope user --json
```

When only the Codex-owned runtime cache is stale or missing metadata, Loom must
not write that cache directly. The guidance is to start a new Codex session, or
restart Codex Desktop if the plugin list was already loaded, then read back:

```bash
loom host doctor --host codex --scope user --json
```

`loom install` and `loom upgrade` continue to manage only the target
repository's metadata-only installed-state. They do not refresh the Codex
workstation plugin payload and must redirect that intent to `loom host ...`.
Codex marketplace plugin update is also workstation truth; it must not be
reported as repository adoption success unless the target repository's Loom
installed-state, host verify, skills check, doctor, and closeout evidence pass.

If a target repository contains `.agents/plugins/marketplace.json`, Loom must
classify it as repository-local marketplace state unless a source-repository
contract explicitly proves it is a deterministic published catalog pointing at
`./plugins/loom`.

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

## Host AGENTS.md Execution Block

Metadata-only adoption must ensure the target repository root has `AGENTS.md`.
If it already exists, Loom inserts or updates this managed block. If it is
missing, Loom creates the file with this block. The `LOOM_BOOTSTRAP_*` markers
are retained only as the stable managed-region delimiters:

```markdown
<!-- LOOM_BOOTSTRAP_START -->
## Loom Execution

本仓库使用 Loom 管理 Work Item、admission/spec、build、review、merge-ready 和 closeout。Loom 是执行控制面，不替代仓库自身业务事实源。

开始改文件前：

1. 先用 `loom route --target . --task "<request>" --json` 判断入口；接手已有事项时先用 `loom resume --target . --json`。
2. 一次只推进一个明确 Work Item；不要把无关修复、后续想法或新范围塞进同一 PR。
3. 命中 formal spec path 时，缺 `spec.md`、`plan.md` 或 `spec_review approved` 不得进入实现。
4. 按 Loom 返回的 `next_action` / `fallback_to` 执行；`block` 表示回退修前序事实，不表示绕过门禁。
5. 验证证据必须写清命令、结果、时间或 head sha；不要只把结论留在会话里。
6. 改了代码、PR body、review 输入或 carrier 后，重新确认 review/gate evidence 是否仍 fresh。
7. merge 后不等于完成；按 Loom closeout 同步 issue、PR、主干和事实载体状态。

环境或插件问题交给 `loom doctor --target . --json` 的输出处理。
<!-- LOOM_BOOTSTRAP_END -->
```

The block is root-only. Loom does not create subdirectory `AGENTS.md` files as
part of adoption.

## Consumer Boundary

This contract is a target-state contract. It does not implement command behavior.
Implementation work must consume it without reintroducing repo-local plugin
install, repo-local runtime install, or single-skill distribution semantics.
