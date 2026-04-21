# Skills

`skills/` 是 Loom 的场景封装层，也是 Loom 在完整安装形态下的用户执行面。

当 Loom 以 repo-local `loom` plugin 的方式被安装到 Codex、Claude Code 或其他 agent 平台后，用户真正会看到并调用的，就是这里的 scenario skills。

默认从 `loom-init` 开始。它是 Loom 唯一的 root entry，负责两件事：

- 初始化 Loom，或把 Loom retrofit 进既有仓库
- 在没有显式指定场景 skill 时，根据任务信号把执行者导向正确场景

不要把 `skills/` 当成新的事实真相源，也不要把裸 `skills/` 目录当成 Loom 的全部安装面。这里的职责是把 Loom 已有能力装配成稳定入口，并把用户带到正确场景。

## 执行面与正式交付物

Loom 在 `skills` 层固定承认两类对象：

- `scenario skills`
  - 用户执行面
  - 在完整 Loom 安装形态中，执行者看到并调用的是这组场景入口
- `single-skill standard-skill packages`
  - 单个标准 skill 的正式交付物
  - 每个 package 只承接一个标准 skill 的场景合同、最小 launcher / shim 与所需私有资源
  - 当前仓库中的生成产物位于 `packages/skills/<skill-id>/`

两者关系必须保持清晰：

- scenario skills 回答“用户现在该进入哪个动作”
- single-skill standard-skill package 回答“某个标准 skill 如何被单独正式交付”
- 单 skill package 不承诺整包 Loom 默认能力
- 单 skill package 不自动补齐 `loom-init`、其余 scenario skills 或完整 plugin 安装体验
- 单 skill package 可以复用同一 `loom` CLI 语义，但不会因此升级成整包 Loom 的替身

## 用户会看到哪些入口

Loom 当前稳定提供 1 个 root entry 和 7 个 scenario skills：

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
  - 用户已经知道当前是哪个场景，直接调用对应 scenario skill
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

## 单 skill package 的边界

如果你处理的是 `single-skill standard-skill package`，至少要保持以下判断：

- package 的稳定命名对象是单个标准 skill，而不是“缩小版整包 Loom”
- package 只能承诺该 skill 的输入、输出、引用关系与最小运行切片
- package 不应把其他 scenario skills 的可用性伪装成默认能力
- package 不应把 repo-local plugin 的安装成功伪装成单 skill 安装成功
- 若用户需要 `loom-init` 路由、完整 scenario skill 集合或整包 Loom 默认能力，应回到 repo-local `loom` plugin

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
