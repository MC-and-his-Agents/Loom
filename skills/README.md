# Skills

`skills/` 是 Loom 面向用户的入口层。

当 Loom 被安装到 Codex、Claude Code 或其他 agent 平台后，用户真正会看到并调用的，就是这里的 skill 名称。

默认从 `loom-init` 开始。它是 Loom 唯一的 root entry，负责两件事：

- 初始化 Loom，或把 Loom retrofit 进既有仓库
- 在没有显式指定场景 skill 时，根据任务信号把执行者导向正确场景

不要把 `skills/` 当成新的事实真相源。这里的职责是把 Loom 已有能力装配成稳定入口，并把用户带到正确场景。

## 用户会看到哪些入口

Loom 当前稳定提供 1 个 root entry 和 7 个场景 skills：

- `loom-init`
  - 默认入口；负责初始化与路由
- `loom-adopt`
  - 初始化新项目，或把 Loom 接入既有仓库
- `loom-resume`
  - 接手事项、恢复上下文、继续推进
- `loom-pre-review`
  - 正式 review 前的统一检查
- `loom-review`
  - 正式 review、语义审查、输出 review 结论
- `loom-handoff`
  - 交接当前事项，回写停点与下一步
- `loom-retire`
  - 清理或 retire 当前工作现场
- `loom-merge-ready`
  - merge 前最后一次放行检查

## 入口如何工作

Loom 的入口有两种进入方式：

- 显式进入
  - 用户已经知道当前是哪个场景，直接调用对应 skill
  - 显式 skill 优先，不再经过额外路由
- 路由进入
  - 用户没有显式指定场景时，先进入 `loom-init`
  - `loom-init` 根据任务信号，把执行者路由到正确场景 skill

若任务信号不足、同时命中多个场景，或缺少稳定执行所需的最小输入，不要猜测。回退到 `loom-init`，并要求最小补充信号。

稳定路由规则见 [route-matrix.md](./route-matrix.md)。

## 什么时候先用 `loom-init`

以下情况默认都先进入 `loom-init`：

- 第一次把 Loom 带进一个仓库
- 你只知道“现在要开始”，但还不知道该进入哪个场景
- 你需要 Loom 先判断这是初始化、恢复执行、review、交接还是 merge-ready
- 当前任务信号不完整，需要 root entry 先收清最小判断输入

如果你已经明确知道自己就是在做 review、handoff、retire 或 merge-ready，就直接进入对应场景 skill。

## 深入文档放在哪里

以下文档继续存在，但它们不再是用户理解 `skills/` 的第一屏：

- [loom-init/SKILL.md](./loom-init/SKILL.md)
  - root entry 的触发方式、快速判断与路由摘要
- [route-matrix.md](./route-matrix.md)
  - 显式进入 / 路由进入 / fallback 的稳定规则
- [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)
  - 宿主适配、安装、升级、分发与失败可见性边界
- [registry.json](./registry.json)
  - 机读入口注册表
- [upgrade-contract.json](./upgrade-contract.json)
  - 机读升级协议
- [install-layout.json](./install-layout.json)
  - 机读安装布局合同

只有在你处理分发、升级、宿主适配、机读合同或 runtime 诊断时，才需要优先进入这些深层材料。
