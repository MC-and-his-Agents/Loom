# Loom

Loom 是一个面向智能体优先项目的上游治理真相、harness 编排与可执行 `SKILLS` 仓库。

它不是业务模板，也不是单纯的文档集合。  
它解决的是另一类问题：为什么很多项目代码可以持续产出，但 issue / project / PR / review / CI / merge / closeout 这些执行对象仍然缺少统一控制面，导致执行秩序、审查质量、长任务连续性和交付收口反复失控。

## Loom 试图解决什么问题

很多团队在新项目启动时，真正缺的不是代码脚手架，而是下面这些基础能力：

### 1. 工作入口不清楚

一个想法、一个需求、一次修复、一次治理调整，常常都能直接变成代码改动。  
结果是：

- 很多改动说不清自己服务哪个目标
- 事项边界不断膨胀
- 审查时只能看 diff，缺少上位语义

### 2. 状态真相分散

项目状态通常同时散落在：

- GitHub Issue / Project
- PR 描述
- 仓库文档
- 聊天记录
- 个人记忆

结果是：

- 没人能快速判断哪一份才是当前真相
- 接手者需要重新拼装上下文
- 长任务一旦中断，就很难低成本恢复

### 3. 长任务无法稳定恢复

当事项需要多轮推进时，团队经常只能依赖：

- “继续上次那个分支”
- “翻一下聊天记录”
- “看起来这里应该改到一半了”

结果是：

- 停点不清楚
- 下一步不清楚
- 已验证内容和未决风险混在一起
- 人和智能体都容易重复劳动或误判当前状态

### 4. 审查职责混在一起

很多项目没有明确区分：

- 谁负责判断语义正确性
- 谁负责跑自动化检查
- 谁负责在合并前做最终门禁

结果是：

- 有时 CI 通过就被当作“可以合并”
- 有时 reviewer 需要自己补做流程校验
- 有时合并前并不知道当前 head 是否仍然安全

### 5. “完成”没有统一定义

很多事项在“代码写完”时就被视为结束，但这通常不够。  
真正容易遗漏的是：

- 对应事项状态没有同步
- 风险和验证证据没有沉淀
- 长任务工件没有收口
- 文档、审查、主干结果不一致

结果是：

- 事情看似完成，实际难以复验
- 后续维护者很难判断当时的设计和验证依据

## Loom 的答案

Loom 不试图替项目做业务决策。  
Loom 试图把治理真相、宿主编排和场景化执行入口收敛成同一套上游能力，让团队和智能体从一开始就有稳定的工作方式。

Loom 当前冻结的三层目标态是：

- `governance truth`
  - 定义事项如何分层、真相源在哪里、状态机如何推进、checkpoint / review / closeout 的职责如何划分
- `harness orchestration`
  - 提供 repo-local 执行语义与宿主能力编排，把工作现场、恢复、review、merge-ready、merge、closeout，以及 GitHub / CI / `git worktree` / `gh` 等宿主表面纳入统一控制面
- `executable SKILLS`
  - 提供人和智能体的场景化可执行入口，让 adopt、resume、pre-review、handoff、retire、merge-ready 等动作可以直接启动，而不是临场拼装流程

## Loom 提供的价值

采用 Loom 后，一个项目应能更早获得这些能力：

- 受控的执行入口，而不是随意开工
- 清晰的状态分层，而不是多处并行记账
- 对长任务友好的恢复机制，而不是依赖聊天上下文
- 以 `merge-ready` 为中心的分层审查与门禁，而不是把所有把关动作混在一起
- 对 GitHub / PR / review / CI / merge / closeout 的统一编排，而不是每轮都重新约定宿主动作
- 更可复验的收口，而不是“代码合了就算完”
- 可版本化升级的治理、harness 与 `SKILLS`，而不是每个项目各改各的

## Loom 不是什么

Loom 不是：

- 业务代码模板
- 通用代码生成器
- 只输出 Markdown 的文档仓库
- 从零重写 GitHub、CI、代码审查引擎、`git worktree` 或 `gh` 的底层产品
- 把所有项目强行约束成同一目录结构的僵硬框架

但 Loom 的目标职责，正是把这些宿主能力统一纳入一致的治理与执行编排，而不是把它们排除在体系外。

## 仓库将包含什么

Loom 当前按五个区域组织：

- `governance/`
  - 治理真相、事项模型、状态机、审查职责、成熟度与关闭语义
- `harness/`
  - repo-local 执行语义、工作现场、恢复模型、checkpoint、宿主编排、纯度与自动化前置
- `templates/`
  - 正式规约模板、PR 模板和其他结构化工件
- `adoption/`
  - 提取台账、落点映射、采用动机、事项分流与候选模式
- `skills/`
  - 初始化、接手、审查、交接、merge-ready、收口等场景化可执行入口

仓库内当前的主要交付物包括：

- 初始化 `SKILL` 第一版
- 第一轮模拟 adoption 验证
- 新项目、小型既有仓库、复杂既有仓库三类真实 adoption 验证记录
- 经验回流、版本化与上游交付面文档
- `loom-check` 仓库自检入口与 CI 工作流
- `loom-init` 最小可执行 bootstrap CLI
- 可直接投放的 `spec.md`、`plan.md` 与 PR 模板实体
- 新项目 bootstrap demo 复验链路
- 完整执行内核发布与升级说明（[docs/complete-kernel-release.md](./docs/complete-kernel-release.md)）

当前上游交付面已经明确包括：

- `governance`、`harness`、`templates` 的稳定核心合同
- `SKILLS` 的稳定可执行入口、路由与适配合同
- `adoption` 中的验证记录合同、经验回流、升级路径与上游交付面说明

## 适合谁

Loom 适合这些场景：

- 你想启动一个新项目，但不想再从零发明协作秩序
- 你希望人和智能体围绕同一套仓库工件工作
- 你需要长任务能 checkpoint、恢复和交接
- 你希望治理能力独立于单一业务仓库持续演进

## Loom 2.0 的执行目标

Loom 当前已经具备一批 repo-local CLI、gate 与 `SKILLS` 入口。  
在这个基础上，Loom 2.0 的目标不是停在“最小可执行”层面，而是形成一套以 `merge-ready` 为中心、可被下游直接消费的完整执行编排面。

当前已经稳定的 repo-local 入口包括：

- 仓库自检可通过 `make loom-check` 运行
- 初始化入口可通过 `python3 tools/loom_init.py bootstrap --target <repo>` 运行
- 事实链读取入口可通过 `python3 tools/loom_init.py fact-chain --target <repo>` 运行
- 日常事实读取入口可通过 `python3 tools/loom_flow.py fact-chain --target <repo>` 运行
- 运行时证据读取入口可通过 `python3 tools/loom_flow.py runtime-evidence --target <repo>` 运行
- 状态一致性检查入口可通过 `python3 tools/loom_flow.py state-check --target <repo>` 运行
- 高频预检统一入口可通过 `python3 tools/loom_flow.py flow pre-review --target <repo>` 运行
- 日常执行入口可通过 `python3 tools/loom_flow.py <...>` 运行
- 新项目 demo 可通过 `make loom-demo-new-project` 复验

继续收敛的目标还包括：

- 根 `SKILL` 与场景 `SKILLS` 形成稳定路由，让 agent 可以直接启动 adopt / resume / pre-review / handoff / retire / merge-ready
- review、guardian、CI、merge gate、closeout 在不同层级提前暴露问题，而不是把 final review 当作第一次系统性发现问题的地方
- `admission checkpoint`、`build checkpoint`、`merge checkpoint` 的工程化承接
- 工作现场生命周期与纯度治理的稳定入口
- 运行时可见性、验证入口与 gate 输入的稳定脚本面
- issue / project / PR / 状态面 / closeout 的真相同步与宿主控制面编排
- branch / PR / `git worktree` / CI / review engine 等宿主对象的边界与承接方式明确
- 日常执行动作的统一入口，而不是依赖会话解释补齐
- `SKILLS` / CLI / gate 的日常入口矩阵与职责边界

本仓当前先冻结这一目标态与职责边界；具体实现拆分、脚本补齐、门禁接线与验证回合由后续 issue / PR 承接。
