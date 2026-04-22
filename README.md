# Loom

Loom 是一个面向 Agent Coding 场景的治理、执行与收口仓库。

它解决的不是“怎么生成业务代码”，而是“项目如何被稳定接入、持续推进、进入 review、判断是否可合并，并在合并后完成收口”。

## 适用场景

如果你正在用 Agent 持续参与项目开发，而不是一次性生成代码，Loom 适合这类场景：

- agent 进入仓库后，不知道应该先接入、继续做、还是进入 review
- 做到一半的任务需要恢复，但现场信息散落在聊天记录、PR 和临时说明里
- 问题经常在最后 review 才第一次系统性暴露
- 团队缺少统一的 merge-ready 判断
- 代码进主干后，这一轮工作仍然没有真正收口

更适合的仓库类型：

- 会持续多轮推进、需要恢复现场的开发仓库
- 有 review、合并和收口要求的多人协作仓库
- 希望让 Agent 在仓库内按稳定流程推进工作的项目

不太适合的仓库类型：

- 一次性脚本、临时实验或几十分钟内即可完成的小改动仓库
- 没有持续执行需求，也没有明确 review 或 closeout 语义的轻量仓库

Loom 面向的是 Agent 执行路径，不要求人类用户手工编排每一步功能入口。
接入完成后，Agent 会根据当前项目状态和已发现的 SKILLS 理解后续可执行路径。

## 快速接入

当接入流程在目标仓库写入 `.loom/` 产物时，会默认把 `.loom/` 追加到 `.gitignore`。

Loom 当前有两条明确的接入路径：

- 通过 npm 安装
  - 面向“我要在别的项目里使用 Loom”
  - 使用已发布的 `@mc-and-his-agents/loom-installer`
  - 这是默认推荐路径
- 通过 Loom 仓库接入
  - 面向“我要让 Agent 直接基于这个 Loom 仓库完成接入”
  - 适合还没准备 npm 安装面、或希望 Agent 按仓库 truth 直接接入的场景
  - 这不是另一种 npm 命令，而是让 Agent 以仓库地址作为接入来源

如果你只是想把 Loom 接到自己的项目里，优先用 npm 路径。
如果你正在调试、验证、演示，或希望 Agent 直接以 Loom 仓库为来源完成接入，再使用仓库路径。

### 用 `npx` 直接接入

如果当前 Agent 环境允许直接执行本地安装命令，可以直接使用 Loom 的 Node installer：

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
npx @mc-and-his-agents/loom-installer add skill loom-init --host codex
npx @mc-and-his-agents/loom-installer add skill loom-init --host claude
```

运行前提：

- Node `>=20`
- Python `>=3.10`，推荐 `3.11+`

这条 `npx` 入口只负责安装、发现和验证。
Loom 当前真实执行面仍然是仓库里的 Python runtime。

### 用 `npm` 安装后再接入

如果你希望先把 installer 固定到当前项目，也可以先安装再执行：

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin --host codex
npx loom-installer add plugin --host claude
npx loom-installer add skill loom-init --host codex
npx loom-installer add skill loom-init --host claude
```

以上两种都属于“通过 npm 安装”。

### 通过 Loom 仓库接入

如果你不打算先走已发布 npm 包，而是希望 Agent 直接以 Loom 仓库作为接入来源，可以把 Loom 仓库地址直接交给 Agent：

- Loom 仓库：`https://github.com/MC-and-his-Agents/Loom`

这种方式适合：

- 你要按仓库当前 truth 直接接入，而不是依赖已发布版本
- 你在验证、调试或演示 Loom
- 你希望 Agent 自己判断当前环境更适合 plugin 还是 single-skill 接入

这种方式不等于已经通过 npm 安装 `@mc-and-his-agents/loom-installer`。
它表达的是“把 Loom 仓库作为接入来源”，而不是“从 npm 获取 Loom 安装器”。

### 完整接入 Loom Plugin

适合场景：

- 你要把 Loom 作为当前项目的默认 Agent Coding 入口
- 你希望 Agent 在项目中自动发现并使用 Loom 提供的整套能力
- 你不想手工拼装接入、恢复、审查和收口环节

可以把下面这段提示词直接发给你的 Agent：

```text
帮我把这个仓库里的 Loom 以 plugin 方式接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的本地 plugin 方式完成接入，让 Loom 在当前项目中可被发现并正常使用。
不要直接开始改业务代码。
```

## 单独接入某个 Skill

如果你不需要整套 Loom，而是只想为当前项目补一个明确的场景入口，可以直接接入对应 skill。
下面每个场景都附了一段可直接复制的 prompt。

### `loom-init`

适合场景：

- 你希望 Agent 进入项目后先判断当前应该从哪个场景开始
- 你不想让 Agent 一进仓库就直接改代码

```text
帮我把这个仓库里的 `loom-init` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-init`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-adopt`

适合场景：

- 当前项目还没有 Loom，需要先完成接入骨架
- 你想让 Agent 帮你把项目纳入 Loom 工作流

```text
帮我把这个仓库里的 `loom-adopt` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-adopt`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-resume`

适合场景：

- 当前任务做到一半，需要恢复执行
- 你希望 Agent 先恢复现场，而不是靠聊天记录重新理解上下文

```text
帮我把这个仓库里的 `loom-resume` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-resume`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-pre-review`

适合场景：

- 你希望在正式 review 前先暴露明显问题
- 你不想把第一次系统性检查留到最后

```text
帮我把这个仓库里的 `loom-pre-review` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-pre-review`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-review`

适合场景：

- 你要把审查结果沉淀成正式输入，而不只是 PR 上的零散评论
- 你需要一个明确的 review 场景入口

```text
帮我把这个仓库里的 `loom-review` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-review`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-handoff`

适合场景：

- 当前工作要换一个 Agent 或换一个执行者继续
- 你希望交接时把状态说清楚，而不是只留聊天记录

```text
帮我把这个仓库里的 `loom-handoff` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-handoff`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-merge-ready`

适合场景：

- 你需要一个明确的入口来判断当前是否可以合并
- 你不想只靠主观感觉决定是否 merge

```text
帮我把这个仓库里的 `loom-merge-ready` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-merge-ready`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

### `loom-retire`

适合场景：

- 当前执行现场需要干净退出
- 你希望结束这一轮工作时不要留下悬空状态

```text
帮我把这个仓库里的 `loom-retire` skill 接入当前项目：
https://github.com/MC-and-his-Agents/Loom

请按当前 Agent 环境支持的方式，只接入 `loom-retire`，让它在当前项目中可被发现并正常使用。
不要安装整套 Loom，也不要直接开始改业务代码。
```

## 文档入口

如果你想继续看具体内容，从这里进入：

- 愿景与边界：[VISION.md](./VISION.md)
- Skills 与分发形态：[skills/README.md](./skills/README.md)
- Harness 执行层：[harness/README.md](./harness/README.md)
- Adoption 落点与接入材料：[adoption/README.md](./adoption/README.md)
- 安装、分发与适配合同：[skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)
