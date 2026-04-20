# Status Surface

本文件定义 Loom 当前最小状态面合同。

本文件当前承接：

- `EXT-0035`

## 1. 能力定位

状态面用于快速读取当前执行状态和运行事实。

它服务读取，不服务并行记账。
本文件把“状态读取字段”和“运行时证据入口”明确拆开定义。
字段归属与派生关系以 [fact-chain-contract.md](./fact-chain-contract.md) 为准。

## 2. 状态读取字段

Loom 当前至少要求状态面能展示：

- 当前事项
- 当前执行路径
- 当前 checkpoint 阶段
- 当前工作现场
- 当前恢复主入口
- 当前 review 入口
- 当前环境 lane
- 当前阻断项
- 下一步
- 最近验证摘要

这些字段必须从已有主真相派生，不允许手工维护第二套 authored 值：

- `当前事项`、`当前执行路径`
  - 从 `work item` 派生
- `当前 checkpoint 阶段`、`当前阻断项`、`下一步`、`最近验证摘要`、`当前环境 lane`
  - 从恢复主入口派生
- `当前工作现场`、`当前恢复主入口`、`当前 review 入口`、`验证入口`
  - 从 `work item` 与 `init-result` 的 carrier 定位派生

## 3. `Runtime Evidence` 固定区块

状态面若承接运行时证据，必须提供固定标题区块 `Runtime Evidence`。

该区块固定为以下 5 个字段，字段不得缺失：

- `Run Entry`
- `Logs Entry`
- `Diagnostics Entry`
- `Verification Entry`
- `Lane Entry`

每个字段的值只能是：

- locator 字符串
- `not_applicable`

## 3.1 字段合同矩阵

| 字段 | 最小语义 | 允许值 | `not_applicable` 允许条件 |
| --- | --- | --- | --- |
| `Run Entry` | 告诉执行者去哪启动当前事项运行面 | locator / `not_applicable` | 事项不涉及可运行系统 |
| `Logs Entry` | 告诉执行者去哪看运行输出或日志 | locator / `not_applicable` | 无运行进程或无日志载体 |
| `Diagnostics Entry` | 指向指标、trace 或等价诊断入口 | locator / `not_applicable` | 当前事项没有诊断面 |
| `Verification Entry` | 指向 UI/API/E2E 等可验证入口 | locator / `not_applicable` | 事项不涉及可验证运行结果 |
| `Lane Entry` | 指向当前 lane 的运行/诊断读取入口 | locator / `not_applicable` | 事项没有 lane 区分 |

判定规则：

- 字段缺失始终是错误，不等同于 `not_applicable`。
- `not_applicable` 必须按字段判断，不能整组一刀切。
- 若某字段标记 `not_applicable`，应与 `current_lane`、`execution_path`、`latest_validation_summary` 等事实不冲突。

## 4. 运行时证据入口语义

最小证据类别对应如下：

- `Run Entry`
  - 当前工作现场对应的运行入口
- `Logs Entry`
  - 日志或等价运行输出入口
- `Diagnostics Entry`
  - 指标、trace 或其他等价诊断入口至少一种
- `Verification Entry`
  - UI、接口或端到端结果中的至少一种 agent 可验证入口
- `Lane Entry`
  - 当前环境 lane 对应的诊断或读取入口

Loom 固化的是“可读取、可验证”的能力目标，不固化具体可观测工具栈。

## 5. `not_applicable` 语义

若事项不涉及可运行系统，状态面应明确标出运行时证据为 `not_applicable`，而不是伪造运行入口。

典型场景包括：

- 纯文档事项
- 纯治理规则调整
- 仅结构整理、尚无运行载体的事项

`not_applicable` 可以按字段逐项声明。

例如：

- `Verification Entry` 可读
- `Run Entry`、`Logs Entry`、`Diagnostics Entry`、`Lane Entry` 为 `not_applicable`

`not_applicable` 只说明该字段当前不适用，不说明验证已自动通过。

## 6. 边界约束

- 禁止手工维护第二套平行真相
- 状态面负责读取，不重复承接正式规则定义
- 状态面若展示的 `next_step`、`blockers`、`latest_validation_summary` 与恢复主入口不一致，应视为事实链断裂
- `Runtime Evidence` 的 5 个字段必须全部出现；不允许用“缺字段”表达不适用
- 运行时证据入口不等于完整 observability 平台设计；本文件只要求最小可读入口

当前仓库中的统一读取入口包括：

- `python3 loom-init/scripts/loom-init.py fact-chain --target <repo>`
- `python3 shared/scripts/loom_flow.py runtime-evidence --target <repo> [--item <id>]`
