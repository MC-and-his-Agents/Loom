# Loom Harness Design

## 1. 文档定位

本文档定义 Loom 的完整 harness 方案。

它只负责三类内容：

- 定义 harness 需要覆盖的完整能力面
- 定义稳定组件如何组合成执行支撑系统
- 定义尚未下沉到稳定组件的初始化与强度模型

`harness/*.md` 是稳定组件文档，负责承接最小可执行规则。
当某项能力已经有稳定组件时，本文档只说明它在完整方案中的职责与边界，不重复字段级规则、阶段顺序或放行输入细节。

本文档不负责事项分类、规格准入和成熟度定义；这些属于 `governance-design.md`。

## 2. 方案与组件边界

| 主题 | 稳定落点 | 本文档职责 |
| --- | --- | --- |
| 初始化与装配 | `harness-design.md` | 定义初始化场景、初始化产物强度与初始 clean state |
| work item / `exec-plan` | `harness/work-item-contract.md` | 定义正式执行单元；本文只定义它在完整方案中的装配位置 |
| 执行上下文 | `harness/execution-context.md` | 定义上下文合同；本文只要求每轮正式执行必须绑定 |
| 最小执行链路 | `harness/execution-chain.md` | 定义阶段顺序、主入口与回退去向；本文只说明它如何与初始化和强度模型组合 |
| 工作现场 | `harness/workspace-model.md` | 定义隔离现场与恢复定位；本文只定义它与纯度和恢复的组合关系 |
| 纯度预检 | `harness/workspace-and-purity.md` | 定义纯度规则；本文只定义它在正式执行前的作用 |
| 恢复模型 | `harness/recovery-model.md` | 定义 `checkpoint`、`resume`、`handoff` 与回写事实；本文不重复恢复字段 |
| 状态面与运行证据 | `harness/status-surface.md` | 定义状态读取字段、运行时证据入口与 `not_applicable` |
| 自动化前置 | `harness/automation-frontload.md` | 定义检查矩阵与覆盖边界 |
| merge checkpoint | `harness/merge-checkpoint.md` | 定义执行侧放行输入、结果语义与回退承接 |

## 3. Harness 目标

Loom 的 harness 方案要同时满足六个目标：

1. 让执行上下文不依赖会话记忆
2. 让每个正式事项有清晰工作现场
3. 让多轮事项可以暂停、恢复和交接
4. 让状态可被快速读取，而不制造第二真相源
5. 让适合自动化的判断尽量前置
6. 让 merge checkpoint 只承担执行放行，而不是承担全部治理

## 4. 初始化与装配

Harness 的第一步不是运行，而是初始化。

初始化机制负责回答：

- 当前仓库是哪种接入场景
- 应启用哪些 harness 组件
- 应生成哪些初始工件
- 后续执行从哪里进入

Loom 默认支持三种初始化场景：

- 新项目初始化
- 小型既有仓库接入
- 复杂既有仓库接入

初始化的目标不是一次性装齐全部能力，而是用合适强度建立执行基础。

初始化至少应产出以下结果：

- 初始化脚本或等价入口
- 初始能力清单
- 首批事项清单
- 初始 `checkpoint` / `progress` 载体
- 初始 clean state

初始化完成后，目标仓库应处于清晰起点，而不是半装配、半手动的模糊状态。

## 5. 组件装配原则

完整 harness 依赖稳定组件形成闭环，但装配关系遵守以下原则：

- 进入正式执行前，必须先有 work item、恢复入口、验证入口和工作现场入口
- 每轮执行的阶段顺序与回退去向，以 [harness/execution-chain.md](./harness/execution-chain.md) 为准
- 状态读取、运行证据、自动化前置和 merge checkpoint 都应消费同一组执行真相，不制造并行真相源
- merge checkpoint 的执行语义以 [harness/merge-checkpoint.md](./harness/merge-checkpoint.md) 为准；本文不再重复定义输入集和结果枚举

## 6. Harness 强度模型

Loom 不把 harness 做成单一重型系统，而是做成可升级结构。

强度变化通过启用不同组件组合与更强约束完成，而不是通过重复定义另一套规则完成。

### 6.1 轻量形态

适用于：

- 小型仓库
- 低复杂度事项
- 恢复痛点还不明显的仓库

默认启用：

- 执行上下文最小集
- 单现场单事项
- `checkpoint-lite`
- 基础自动化前置

### 6.2 标准形态

适用于：

- 事项经常跨多轮推进
- 已经出现恢复成本
- 已经需要明确 `handoff`

默认启用：

- 标准恢复入口
- 明确 `checkpoint` / `resume` / `handoff`
- 更强状态读取与验证汇总
- 可稳定消费的 merge checkpoint 输入

### 6.3 强化形态

适用于：

- 复杂仓库
- 多 agent 并行
- 高恢复成本
- 高治理成本

默认启用：

- 更严格的现场规则
- 更强运行时证据入口
- 更强纯度检查
- 更强自动化前置
- 更严格的放行回退承接

## 7. Harness 方案的一句话总结

Loom 的 harness 方案不是为了制造更多执行仪式，而是为了让初始化、执行、恢复、可见性和放行形成一条可升级、可组合、可验证的执行支撑系统。
