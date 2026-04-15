---
name: loom-init
description: 分析一个新项目或既有仓库的协作场景，选择适合的 Loom 治理、harness、templates 与 adoption 组合，并输出初始化步骤、首批工件与后续事项拆解。Use when Codex needs to start a repository on top of Loom, retrofit Loom into an existing repo, or decide which Loom capabilities should be adopted first.
---

# Loom Init

使用本 skill 为新项目或既有仓库装配 Loom 的第一批能力。

先判断当前项目真正需要哪些能力，再决定引入哪些 Loom 工件。不要先套完整分层，也不要把所有模板一次性压进仓库。

## 1. 读取顺序

按以下顺序读取材料：

- 目标仓库中的 `AGENTS.md`、`README`、流程文档、PR 模板、issue 模板
- Loom 根文档：
  - `AGENTS.md`
  - `README.md`
- Loom 核心规则：
  - `governance/principles.md`
  - `governance/review-model.md`
  - `governance/maturity-and-closing.md`
  - `adoption/rationale.md`
  - `adoption/routing-and-checkpoints.md`
- `harness/recovery-model.md`
- `harness/status-surface.md`
- `harness/work-item-contract.md`
- `harness/workspace-model.md`
- `harness/automation-frontload.md`
- `harness/workspace-and-purity.md`
  - `templates/spec-suite.md`
  - `templates/pull-request.md`

只有在事项带有明显不确定性、需要进一步分层时，才补读：

- `adoption/candidate-patterns.md`
- `harness/execution-context.md`

## 2. 建立初始化问诊

优先从仓库现状推断答案，只在关键信息缺失时再问用户。

使用 [references/intake-signals.md](./references/intake-signals.md) 组织问诊，至少判断：

- 当前是新项目还是既有仓库整治
- 是否存在治理与业务强耦合且难以独立升级的问题
- 当前事项是否经常跨多轮推进
- merge 前 review 是否承担了第一次高质量语义判断
- 项目中是否存在共享契约、高风险链路、核心抽象
- 当前是否已经有 GitHub / PR / CI / worktree 等基础设施
- 团队或智能体当前最痛的恢复点在哪里

## 3. 做出装配判断

不要输出抽象“建议采用 Loom”。必须把判断落成具体装配决策。

使用以下决策规则：

- 如果目标仓库已经有清晰的根级边界文档，优先采用“伴随文档接入”，不要先重写根规则
- 只在当前项目已经出现长任务中断成本时，装配恢复模型
- 只在当前项目存在共享边界或高风险实现承诺时，装配正式规约套件
- 只在当前项目出现 review 过载或 merge 前过晚暴露问题时，装配前移 checkpoint
- 只在当前项目存在现场混杂或 PR 范围失控时，装配现场隔离与纯度规则
- 对新项目，默认先装最小能力，不一次性引入全部候选模式
- 对既有仓库，优先补最痛的结构性缺口，不要求一次性重构全部流程

不要：

- 提前固化 profile 体系
- 复制某个下游仓库的完整目录形态
- 把所有治理规则一次性写进一个超重 `AGENTS.md`

## 4. 输出初始化结果

始终使用 [references/output-contract.md](./references/output-contract.md) 的结构输出结果。

输出中至少包含：

- 当前项目判断摘要
- 推荐装配的 Loom 能力
- 明确暂不引入的能力
- 需要创建或更新的工件
- 首批事项拆解
- checkpoint 策略
- 验证方式与收口条件

如果用户要求实际初始化仓库，按以下顺序执行：

1. 建立根级规则入口
2. 建立治理与 adoption 最小工件
3. 建立 harness 与模板最小工件
4. 建立首批 issue / checkpoint / 验证路径

## 5. 处理新项目与既有仓库的差异

对于新项目：

- 直接给出最小装配方案
- 优先保证后续能持续演进
- 避免把未来可能需要的能力提前全部引入

对于既有仓库：

- 先指出当前结构性问题
- 再给出渐进 adoption 顺序
- 明确哪些问题先通过规则解决，哪些问题后续再脚本化
- 如果仓库已有清晰工程边界和 CI 基线，默认先给出最小治理包：
  - `WORKFLOW`
  - `code_review`
  - `spec_review`
  - PR 模板
  - 条件化 `spec.md` / `plan.md`
- 不要把 recovery、work-item、status-surface 当成第一轮默认必装项

## 6. 验证标准

只有当以下条件同时满足时，才把初始化视为完成：

- 输出结果能解释为什么是这组能力，而不是另一组
- 输出结果能映射回 Loom 当前文档中的明确规则
- 首批工件和事项可以直接执行，而不是停留在理念层
- 明确保留了“现在不做什么”，避免一次性过度安装
