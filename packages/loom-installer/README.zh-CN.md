# @mc-and-his-agents/loom-installer

语言：中文 | [English version](./README.md)

Deprecated Loom npm / npx adapter helper 和 verifier。

Loom 默认安装模型是根 `loom` CLI package：`@mc-and-his-agents/loom`。它负责安装、同步和验证宿主 plugin/SKILLS payload。这个 package 是 deprecated legacy artifact，只为历史兼容证据和 verification output 保留。不要把它当作当前 Loom CLI 或推荐安装路径。

## Deprecated Commands

这些命令只为既有 legacy consumer 和证据记录保留，不是当前安装路径：

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

历史固定 installer 用法：

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

Installer package 已 sunset。`main` validation 仍可检查 package 和 legacy registry state，但不得 publish npm、创建 `loom-installer-v*` tag 或创建 installer GitHub Release。

Release model：

- PR 会运行 gates，但不会发布 npm。
- `main` 是 deprecated installer artifact 的 validation truth source。
- Loom 仓库 release 与 installer npm package version 分开维护。
- `loom` CLI release 使用根 `VERSION` 加 GitHub `v*` tag 和 Release；installer `latest` 不是 CLI release evidence。
- 最后一个 active installer baseline 是 `@mc-and-his-agents/loom-installer` `0.1.119` / `loom-installer-v0.1.119`。
- 后续 npm deprecation action 可以只改变 registry metadata，不推进 package version。
