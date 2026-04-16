# Loom Harness Design

## 1. 文档定位

本文档定义 Loom 的完整 harness 方案。

它只负责三类内容：

- 定义 harness 需要覆盖的完整能力面
- 定义稳定组件如何组合成执行支撑系统
- 定义尚未下沉到稳定组件的初始化与强度模型

`harness/*.md` 是稳定组件文档，负责承接稳定组件合同。
当某项能力已经有稳定组件时，本文档只说明它在完整方案中的职责与边界，不重复字段级规则、阶段顺序或放行输入细节。

本文档不负责事项分类、规格准入和成熟度定义；这些属于 `governance-design.md`。

## 2. 方案与组件边界

| 主题 | 稳定落点 | 本文档职责 |
| --- | --- | --- |
| 初始化与装配 | `harness-design.md` | 定义初始化场景、初始化产物强度与初始 clean state |
| work item / `exec-plan` | `harness/work-item-contract.md` | 定义正式执行单元；本文只定义它在完整方案中的装配位置 |
| 单一事实链 | `harness/fact-chain-contract.md` | 定义静态真相、动态真相与派生读面的归属关系 |
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

## 4. 完整执行内核目标态

Loom 不以“最小可执行规则”作为 harness 的完成线。

最小规则只用于定义稳定组件边界；完整执行内核的目标态，是让下游仓库在不依赖会话补脑的前提下，能够仅凭仓库内入口、脚本、状态载体和自动化门禁稳定推进正式事项。

完整执行内核至少应同时具备以下能力面：

- 完整事实链
  - 初始化入口、work item、执行上下文、恢复主入口、状态面与 merge checkpoint 形成单一可读取事实链
- checkpoint 工程化
  - `admission checkpoint`、`build checkpoint`、`merge checkpoint` 都有明确承接工件、输入、输出、回退去向与自动化入口
- 工作现场生命周期
  - 正式事项的创建、定位、恢复、清理与 retire 动作可以重复执行，并与单现场单事项、范围纯度约束绑定
- 运行时可见性与验证
  - lane、运行入口、日志、指标、trace、UI 或接口验证入口可以被读取；`not_applicable` 语义清楚
- 自动化门禁
  - 结构完整性、规则落点、模板存在性、活跃状态一致性、范围纯度、checkpoint 完整性与关键验证入口可以由脚本或 CI 暴露
- 日常执行入口
  - `bootstrap`、`verify`、`checkpoint`、`resume`、`handoff`、`review`、`merge`、`retire` 等高频动作有稳定入口，而不是要求执行者临场拼装

宿主特定实现不直接进入 Loom 内核；但宿主无关的执行脚本族、验证入口与 gate 入口，应成为完整执行内核的一部分。

## 5. 初始化与装配

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
它只负责把仓库带到可继续收敛完整执行内核的起点，不应被误当作 harness 的最终完成状态。

初始化至少应产出以下结果：

- 初始化脚本或等价入口
- 初始能力清单
- 首批事项清单
- 初始 `checkpoint` / `progress` 载体
- 初始 clean state

初始化完成后，目标仓库应处于清晰起点，而不是半装配、半手动的模糊状态。

## 6. 组件装配原则

完整 harness 依赖稳定组件形成闭环，但装配关系遵守以下原则：

- 进入正式执行前，必须先有 work item、恢复入口、验证入口和工作现场入口
- 每轮执行的阶段顺序与回退去向，以 [harness/execution-chain.md](./harness/execution-chain.md) 为准
- 状态读取、运行证据、自动化前置和 merge checkpoint 都应消费同一组执行真相，不制造并行真相源
- 字段 authored 权限与派生边界，以 [harness/fact-chain-contract.md](./harness/fact-chain-contract.md) 为准
- merge checkpoint 的执行语义以 [harness/merge-checkpoint.md](./harness/merge-checkpoint.md) 为准；本文不再重复定义输入集和结果枚举

## 7. Harness 强度模型

Loom 不把 harness 做成单一重型系统，而是做成可升级结构。

强度变化通过启用不同组件组合与更强约束完成，而不是通过重复定义另一套规则完成。
强度模型的意义，是让仓库从轻量起点持续收敛到完整执行内核，而不是长期停留在轻量形态。

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

## 8. Harness 方案的一句话总结

Loom 的 harness 方案不是为了制造更多执行仪式，而是为了让初始化、执行、恢复、可见性和放行形成一条可升级、可组合、可验证的执行支撑系统。
