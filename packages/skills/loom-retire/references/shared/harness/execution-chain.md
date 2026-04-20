# Execution Chain

本文件定义 Loom 当前最小执行链路。

本文件当前承接：

- `EXT-0038` 的完整链路语义
- `#24` 的稳定落点

## 1. 能力定位

Loom 的 harness 不是若干孤立规则，而是一条从初始化产物到 `admission -> build -> merge` checkpoint 的最小执行链路。
字段归属与派生边界见 [fact-chain-contract.md](fact-chain-contract.md)。

本文件只定义链路本身：

- 每个阶段的必需输入
- 每个阶段的最小输出
- 唯一主入口
- 失败或不足时的回退去向

阶段内的字段级合同，仍以各稳定组件文档为准。

## 2. 最小执行链路

| 阶段 | 必需输入 | 最小输出 | 唯一主入口 | 不满足时的回退去向 |
| --- | --- | --- | --- | --- |
| 初始化产物就位 | 初始化场景、能力选择、首批事项 | 可进入执行的 work item、恢复入口、验证入口、工作现场入口 | [work-item-contract.md](work-item-contract.md) | 回到 `harness-design.md` 补初始化与装配 |
| 正式进入执行 | 当前事项、范围、执行路径、checkpoint 状态 | 单一正式执行单元被明确绑定 | [work-item-contract.md](work-item-contract.md) | 退回 work item 补范围、目标或关闭条件 |
| 每轮读取 | work item、恢复主入口、工作现场、最近验证摘要 | 本轮单一推进单元、当前上下文基线 | [execution-context.md](execution-context.md) | 退回恢复主入口或状态面补齐事实 |
| 隔离现场推进 | 上下文基线、工作现场、纯度约束 | 与当前事项一致的执行结果 | [workspace-model.md](workspace-model.md) | 退回现场治理，清理纯度或范围越界问题 |
| 每轮回写 | 本轮执行结果、验证记录、阻断项 | 最新停点、下一步、验证摘要、回退边界 | [recovery-model.md](recovery-model.md) | 回到恢复入口补齐回写，不得只停留在会话里 |
| 验证汇总 | 自动检查结果、人工验证、运行证据入口 | 最近验证摘要、未决阻断项、是否可进 checkpoint | [status-surface.md](status-surface.md) | 回到验证入口继续补验证或声明 `not_applicable` |
| admission checkpoint | 最新事实链、事项范围、入口完整性、关键阻断项 | `pass`、`block` 或 `fallback`（回退前序） | `checkpoint-model.md`（admission） | 回到 work item / recovery 回写补齐输入或收敛范围 |
| build checkpoint | admission 结果、构建/测试结论、运行时证据可读性 | `pass`、`block` 或 `fallback`（回退 admission） | `checkpoint-model.md`（build） | 回到 admission 或验证入口补齐缺失证据 |
| 正式 review | pre-review / review 基线、build 结果、review record | reviewer 结论可被 merge checkpoint 消费 | [review-execution.md](review-execution.md) | 回到 build / recovery 回写 / review record |
| merge checkpoint 放行 | build 结果、最新 head、验证摘要、风险与回滚、未决项 | `允许放行`、`阻断待补` 或 `退回前序 checkpoint` | [merge-checkpoint.md](merge-checkpoint.md) | 按结果回退到 build / admission / 验证阶段继续补材料 |
| closeout 收口 | main 已包含合并结果、issue / project / gate 状态 | issue / project / 主干状态一致 | [closeout-gate.md](closeout-gate.md) | 回到 merge / GitHub 状态同步 |

## 3. `checkpoint-lite` 升级条件在链路中的位置

`checkpoint-lite` 只适用于读取和回写成本都足够低的链路。

一旦出现以下任一信号，就应在“每轮回写”阶段升级为标准恢复形态，而不是继续拖到 checkpoint 阶段再补：

- 事项已连续跨多轮推进
- 新接手者无法仅靠现有入口恢复上下文
- 验证摘要、风险或回退边界已无法稳定寄存在 issue / PR 等载体
- admission / build / merge checkpoint 已需要稳定消费恢复事实

## 4. 链路约束

- 每轮执行只推进一个清晰单元，不在同一轮并行吞入多个无关目标
- 每个阶段都必须有唯一主入口；补充材料不得并行替代主入口
- merge checkpoint 只承接放行，不承担第一次高质量语义判断
- 本文件不替代各组件的字段级合同；字段级规则仍以被引用组件文档为准
