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
  - `adoption/lightweight-retrofit-default.md`
- `harness/recovery-model.md`
- `harness/status-surface.md`
- `harness/work-item-contract.md`
- `harness/workspace-model.md`
- `harness/automation-frontload.md`
- `harness/workspace-and-purity.md`
- `harness/execution-context.md`
- `templates/spec-suite.md`
- `templates/pull-request.md`
- `skills/loom-init/references/intake-signals.md`
- `skills/loom-init/references/output-contract.md`

只有在事项带有明显不确定性、需要进一步分层时，才补读：

- `adoption/candidate-patterns.md`

## 2. 建立初始化问诊

优先从仓库现状推断答案，只在关键信息缺失时再问用户。

使用 [references/intake-signals.md](./references/intake-signals.md) 组织问诊。必须先完成最小必判字段的收集，再做路径判断。

问诊结果必须收成以下结论，而不是停留在零散观察：

- 初始化场景
  - `新项目`
  - `小型既有仓库`
  - `复杂既有仓库`
- 装配强度
  - `轻量`
  - `标准`
  - `强化`
- 默认接入方式
  - 根级重写
  - `companion docs`
- 恢复形态
  - `checkpoint-lite`
  - 标准恢复形态
- 首批执行入口与验证入口
- 初始 clean state 目标

## 3. 做出装配判断

不要输出抽象“建议采用 Loom”。必须把判断落成“判定信号 -> 默认动作”的装配决策。

### 3.1 新项目

当仓库尚未形成稳定工程基线、目标是建立最小起步结构时，判为 `新项目`。

默认动作：

- 采用最小装配
- 不预装重 harness
- 只建立后续可升级入口
- 只引入当前能支撑持续演进的最小治理、模板与验证入口
- 恢复形态默认从轻量开始；若当前没有跨多轮承接需求，可以只声明升级条件，不提前铺满恢复工件

### 3.2 小型既有仓库

当仓库满足 [adoption/lightweight-retrofit-default.md](../../adoption/lightweight-retrofit-default.md) 的默认条件时，判为 `小型既有仓库`。

默认动作：

- 直接消费 `lightweight retrofit default`
- 默认采用 `companion docs` 接入
- 默认装配：
  - `WORKFLOW`
  - `code_review`
  - `spec_review`
  - 最小 PR 模板
  - 条件化 `spec.md` / `plan.md`
- 默认不装配：
  - 完整 recovery 模型
  - work item 合同
  - 状态面
  - profile 分层
  - 重 harness
- 若需要轻量跨轮承接，默认使用 `checkpoint-lite`
- 即使本轮不装配标准恢复或状态面，也必须写清：
  - issue / PR 中谁是恢复主入口
  - 哪个载体承接当前停点、下一步、阻断项与最近验证摘要

### 3.3 复杂既有仓库

既有仓库只要不满足轻量条件，或已经出现明显恢复痛点、共享边界风险、现场混杂、review 过载中的任一高强度信号，就判为 `复杂既有仓库`。

默认动作：

- 进入更完整装配
- 显式纳入：
  - 恢复主入口
  - 执行上下文
  - work item 或等价执行入口
  - 状态读取
  - 隔离现场与纯度规则
- 对涉及共享契约、运行模型、高风险核心抽象的事项，默认纳入正式规约套件与前移 checkpoint
- 对恢复成本明显升高的事项，默认从 `checkpoint-lite` 升级到标准恢复形态

## 4. 输出初始化结果

始终使用 [references/output-contract.md](./references/output-contract.md) 的结构输出结果。

输出中必须显式写出：

- 初始化场景
- 装配强度
- 恢复形态
- 首批执行入口
- 验证入口
- 初始 clean state
- 本轮暂不装配能力的承接方式

如果用户要求实际初始化仓库，按以下顺序执行：

1. 建立根级规则入口或 `companion docs` 入口
2. 建立治理与 adoption 最小工件
3. 建立 harness 与模板最小工件
4. 建立首批 issue / checkpoint / 验证路径
5. 核对输出是否已经形成可继续执行的初始化产物模型

## 5. 处理三类场景的差异

### 5.1 新项目

- 直接给出最小装配方案
- 优先保证后续能持续演进
- 避免把未来可能需要的能力提前全部引入
- 不默认铺满重 harness，只写清升级入口与触发条件

### 5.2 小型既有仓库

- 默认走 `lightweight retrofit default`
- 先指出当前结构性问题
- 再给出渐进 adoption 顺序
- 明确哪些问题先通过规则解决，哪些问题后续再脚本化
- 不要把 recovery、work-item、status-surface 当成第一轮默认必装项
- 若走 `checkpoint-lite`，必须写清 issue / PR 对停点、下一步、阻断项、验证摘要的承接方式

### 5.3 复杂既有仓库

- 先指出导致不能走轻量路径的升级信号
- 再给出更完整装配顺序
- 必须写清正式执行入口、恢复主入口、状态读取入口与现场绑定方式
- 若涉及共享边界或高风险实现承诺，必须写清正式规约工件与 checkpoint 承接关系

## 6. 验证标准

只有当以下条件同时满足时，才把初始化视为完成：

- 输出结果能解释为什么是这组能力，而不是另外两条路径
- 输出结果能映射回 Loom 当前文档中的明确规则
- 首批工件、首批事项、恢复形态、验证入口与初始 clean state 可以直接承接后续执行
- 明确保留了“现在不做什么”，且写清升级触发条件
- 对未装配能力给出了明确承接方式，而不是留给临场经验补齐
