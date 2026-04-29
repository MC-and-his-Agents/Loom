# @mc-and-his-agents/loom-installer

语言：中文 | [English version](./README.md)

Loom 的 npm / npx installer。

主安装模式是完整 Loom plugin surface。单 skill 安装仍然保留，用于兼容和高级场景。

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

发布包会包含生成出来的 payload。该 payload 会在 build、pack 和 publish 阶段，从 canonical `plugins/loom/.codex-plugin/` manifest 与 `skills/` 源动态生成。

生成出来的 payload 目录不会提交到 git。Build 步骤会以确定性方式重建它们，`check:payload` 会校验重建稳定性。

## Release Notes

发布只会从 `main` 进行。

Release model：

- PR 会运行 gates，但不会发布 npm。
- `main` 是唯一 release truth source。
- Loom 仓库 release 与 installer npm package version 分开维护。
- 只有在 npm publish 成功后，才创建 `loom-installer-v<version>` git tag 和同名前缀的 GitHub Release。
