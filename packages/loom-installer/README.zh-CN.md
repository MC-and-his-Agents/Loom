# @mc-and-his-agents/loom-installer

语言：中文 | [English version](./README.md)

Loom 的 npm / npx adapter helper 和 verifier。

Loom 默认安装模型是完整仓库安装加宿主原生或宿主适配的 skill discovery。这个 package 保留给 adapter 托管的 plugin 安装、single-skill helper 和 verification output。

## Commands

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

单 skill 兼容路径：

```bash
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host codex
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host claude
```

只读升级演练与验证：

```bash
npx @mc-and-his-agents/loom-installer upgrade-plan plugin --host codex --json
npx @mc-and-his-agents/loom-installer verify-upgrade plugin --host codex --json
```

也可以先固定 installer 版本：

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin --host codex
```

Options：

- `--host codex|claude|auto`
- `--target <repo-root>`
- `--force`
- `--json`

## Requirements

- Node `>=20`
- Python `>=3.10`，推荐 `3.11+`

## Payload Model

发布包会包含生成出来的 payload。该 payload 会在 build、pack 和 publish 阶段，从 canonical `plugins/loom/.codex-plugin/` manifest 与已提交的生成 `skills/` install surface 动态生成。

生成出来的 payload 目录不会提交到 git。Build 步骤会以确定性方式重建它们，`check:payload` 会校验重建稳定性。根 `skills/` surface 本身会提交，并通过 `check:distribution` 校验。

Installer JSON output 会报告 `distribution_layer`、`version_context` 和 `failed_layer`，让调用方区分 host adapter plugin install 与 generated single-skill install。

Installer 管理的 layer 也会写入 `loom-installed-surface-status/v1` metadata。`upgrade-plan` 和 `verify-upgrade` 只读取该 metadata，并与 package payload 比对，报告 `upgrade_eligibility`、`changed_paths`、`drift`、`rollback_path` 和 fail-closed reason；它们不会修改目标仓库。状态合同见 `docs/adoption/installed-loom-status.md`。

## Release Notes

发布只会从 `main` 进行。

Release model：

- PR 会运行 gates，但不会发布 npm。
- `main` 是唯一 release truth source。
- Loom 仓库 release 与 installer npm package version 分开维护。
- 只有在 npm publish 成功后，才创建 `loom-installer-v<version>` git tag 和同名前缀的 GitHub Release。
