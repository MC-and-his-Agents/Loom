# @mc-and-his-agents/loom-installer

Loom 的 npm / npx 安装入口。

它负责两件事：

- 把 Loom 作为完整 plugin 接到 Codex 或 Claude
- 把某个单独 Loom skill 接到对应宿主

它不替代 Loom 当前的 Python runtime；真正的执行面仍然是仓库里的 Python 脚本与已发布的 skill / plugin 产物。

## 命令面

```bash
npx @mc-and-his-agents/loom-installer add plugin
npx @mc-and-his-agents/loom-installer add skill loom-init
```

也可以先安装再执行：

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin
npx loom-installer add skill loom-init
```

可选参数：

- `--host codex|claude|auto`
- `--target <repo-root>`
- `--force`
- `--json`

## 运行时要求

- Node `>=20`
- Python `>=3.10`，推荐 `3.11+`

## 发布说明

本包支持 `npm publish`，但发布只在 `main` 上进行。

发布模型：

- PR 只做门禁，不直接发布 npm
- `main` 是唯一发布真相源
- publish 成功后再创建同版本 git tag
