# Fact Chain Contract

本文件定义 Loom 当前完整执行内核的单一事实链合同。

本文件当前承接：

- `#35` 的稳定主落点

执行链路顺序见 [execution-chain.md](execution-chain.md)。

## 1. 能力定位

Loom 的执行真相只允许沿一条事实链流动：

- `work item`
  - 承接静态执行真相
- 恢复主入口
  - 承接动态执行真相
- 状态面
  - 只负责派生读取
- merge checkpoint
  - 只消费上述真相，不补读第二套状态来源

本文件只定义 repo execution truth 内部的字段归属、派生关系与禁止事项。
字段的最低表达要求，仍以各组件文档为准。

跨 repo 与 GitHub 控制面的真相分层，见 [../governance/truth-and-sync-boundary.md](../governance/truth-and-sync-boundary.md)。

## 2. 主真相载体

### 2.1 `work item`

`work item` 是静态执行真相的唯一主入口，至少承接：

- `item_id`
- `goal`
- `scope`
- `execution_path`
- `associated_artifacts`
- `workspace_entry`
- `recovery_entry`
- `review_entry`
- `validation_entry`
- `closing_condition`

这些字段服务执行入口与范围识别，不随单轮推进频繁回写。

### 2.2 恢复主入口

恢复主入口是动态执行真相的唯一主入口，至少承接：

- `item_id`
- `current_checkpoint`
- `current_stop`
- `next_step`
- `blockers`
- `latest_validation_summary`
- `recovery_boundary`
- `current_lane`

这些字段服务 `checkpoint`、`resume`、`handoff` 与 merge checkpoint 放行前的状态读取。

### 2.3 `init-result`

`init-result` 不是实时执行状态真相。

它只允许承接：

- 初始化路径
- 装配强度
- 恢复模式
- carrier 定位信息
- 统一读取入口

它不得并行复制当前停点、下一步、阻断项、最近验证摘要或当前 checkpoint。

## 2.4 标准事实模型与字段来源矩阵

以下矩阵是 Loom 完整执行内核当前稳定的最小事实模型。

| 字段 | 主来源 | 类型 | 允许消费方 |
| --- | --- | --- | --- |
| `item_id` | `work item` | authored | execution-context、status-surface、checkpoint、merge-checkpoint |
| `goal` | `work item` | authored | execution-context、checkpoint、merge-checkpoint |
| `scope` | `work item` | authored | execution-context、checkpoint、purity-check |
| `execution_path` | `work item` | authored | execution-context、checkpoint |
| `workspace_entry` | `work item` | authored | workspace-lifecycle、purity-check、status-surface |
| `recovery_entry` | `work item` | authored | execution-context、workspace-lifecycle、checkpoint |
| `review_entry` | `work item` | authored | review-execution、merge-checkpoint |
| `validation_entry` | `work item` | authored | checkpoint、merge-checkpoint、verify |
| `closing_condition` | `work item` | authored | checkpoint、merge-checkpoint |
| `current_checkpoint` | recovery 主入口 | authored | status-surface、checkpoint、workspace-lifecycle |
| `current_stop` | recovery 主入口 | authored | execution-context、checkpoint |
| `next_step` | recovery 主入口 | authored | execution-context、status-surface、checkpoint |
| `blockers` | recovery 主入口 | authored | execution-context、status-surface、checkpoint |
| `latest_validation_summary` | recovery 主入口 | authored | status-surface、checkpoint、merge-checkpoint |
| `recovery_boundary` | recovery 主入口 | authored | checkpoint、merge-checkpoint |
| `current_lane` | recovery 主入口 | authored | status-surface、checkpoint、runtime-evidence |
| `read_entry` | `init-result` | locator | verify、fact-chain、daily CLI |
| `status_surface` locator | `init-result` + `work item` 派生 | derived | fact-chain、verify、checkpoint、workspace-lifecycle |
| `runtime_evidence.*` | status-surface `Runtime Evidence` | derived | fact-chain、verify、merge-checkpoint、loom-check |

约束：

- `authored` 字段只能在主来源中维护。
- `derived` 字段只能由读取脚本从主来源计算或映射，不得手工改写为第二真相。
- `--activate` 只能显式切换当前 locator，不得通过 `resume`、`handoff` 或其他只读 flow 隐式改写活跃事项。

## 3. 派生读面

以下载体只允许派生读取，不允许独立 authored 字段覆盖主真相：

- [execution-context.md](execution-context.md)
- [status-surface.md](status-surface.md)
- [merge-checkpoint.md](merge-checkpoint.md)

派生规则固定如下：

- 静态执行事实
  - 从 `work item` 派生
- 动态执行事实
  - 从恢复主入口派生
- carrier 定位与读取入口
  - 从 `init-result` 派生

若派生读面展示的值与主真相不一致，应视为事实链断裂。

## 4. 不允许的并行记账

以下情况都属于并行真相，必须报错或阻断：

- 在 `work item` 之外 authored 第二份 `goal`、`scope`、`execution_path`
- 在恢复主入口之外 authored 第二份 `current_checkpoint`、`current_stop`、`next_step`、`blockers`
- 让状态面手工维护与恢复主入口不同的 `next_step` 或验证摘要
- 让 merge checkpoint 依赖另一份未声明主入口的状态摘要
- 让 `init-result` 承载实时执行状态

## 5. 最小消费规则

任何机械入口在读取执行状态时，至少要遵守以下顺序：

1. 先读 `init-result` 中的 carrier 定位
2. 再读 `work item`
3. 再读恢复主入口
4. 需要状态汇总时，再读派生状态面

不允许跳过主真相，直接把状态面或 merge checkpoint 输入当成 authored 真相。

当前仓库中的统一读取入口包括：

- `python3 loom-init/scripts/loom-init.py fact-chain --target <repo>`
- `python3 shared/scripts/loom_flow.py fact-chain --target <repo> [--item <id>]`

## 6. 边界约束

- Loom 固化的是字段归属与派生关系，不固化具体文件名或宿主平台字段名
- 若某仓库还停留在 `checkpoint-lite`，也必须明确唯一动态事实承载面
- 本文件不重复定义字段如何呈现在 Markdown、JSON 或其他载体；只定义谁拥有 authored 权限
- issue / project / PR / checks 等 host control truth 不在本文件内定义 authored 归属
- `active issue` 与 branch / `git worktree` / PR / merge commit 的绑定关系只可被本事实链消费，不进入仓内 authored 真相；其最小绑定合同见 [host-issue-binding.md](host-issue-binding.md)
