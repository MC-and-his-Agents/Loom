# Checkpoint Model

本文件定义 Loom 当前 `admission checkpoint` 与 `build checkpoint` 的执行侧合同。

`merge checkpoint` 继续唯一落在 [merge-checkpoint.md](./merge-checkpoint.md)。
三类 checkpoint 的字段归属与读取顺序仍以 [fact-chain-contract.md](./fact-chain-contract.md) 为准。

## 1. 能力定位

Loom 当前的 checkpoint 顺序固定为：

- `admission checkpoint`
- `build checkpoint`
- `merge checkpoint`

其中：

- `admission checkpoint`
  - 承接正式进入执行前的范围、目标、事项绑定与恢复入口可读性判断
- `build checkpoint`
  - 承接执行中段的载体一致性、验证入口可消费性与状态链完整性判断
- `merge checkpoint`
  - 只承接最终放行，见 [merge-checkpoint.md](./merge-checkpoint.md)

## 2. 统一读取基线

任一 checkpoint 的机械读取都必须按以下顺序进行：

1. 从 `init-result` 读取 carrier locator
2. 读取 `work item`
3. 读取恢复主入口
4. 需要状态汇总时，再读取状态面

不允许跳过主真相，直接用状态面、PR 模板或其他派生材料替代事实链。

## 3. Admission Checkpoint

### 3.1 必读输入

`admission checkpoint` 至少读取以下输入：

- `work item` 中的目标、范围、执行路径
- `work item` 中的 `workspace_entry`
- `work item` 中的 `recovery_entry`
- `work item` 中的 `validation_entry`
- `work item` 中的 `closing_condition`
- 恢复主入口中的当前 checkpoint、当前停点、下一步、阻断项

### 3.2 唯一允许结果

`admission checkpoint` 只允许输出：

- `pass`
  - 当前事项可被事实链稳定读取，且工作现场语义已明确
- `block`
  - 事实链能读取，但当前事项材料仍需在 admission 层补齐
- `fallback`
  - 当前状态必须退回更早的 admission 收口，不应继续进入后续 checkpoint

### 3.3 失败语义与回退

以下情况至少应阻断或回退：

- `goal`、`scope`、`execution_path` 缺失
- `workspace_entry`、`recovery_entry`、`validation_entry` 不能定位
- 恢复主入口与 `work item` 的事项标识不一致
- 当前现场已明显混入别的活跃事项或无关残留

当结果为 `fallback` 时，回退方向固定为 `admission`。

## 4. Build Checkpoint

### 4.1 必读输入

`build checkpoint` 在 admission 输入之上，还至少读取：

- 恢复主入口中的最近验证摘要
- 恢复主入口中的当前 lane
- 恢复主入口中的恢复边界
- 状态面中的派生汇总
- 当前验证入口是否仍可消费

### 4.2 唯一允许结果

`build checkpoint` 只允许输出：

- `pass`
  - 执行载体、验证入口与状态链可被稳定消费
- `block`
  - 当前 build 材料不足，但不需要回退到更早 checkpoint 重做方向判断
- `fallback`
  - 当前状态无法继续 build，应退回前序 checkpoint 收口

### 4.3 失败语义与回退

以下情况至少应阻断或回退：

- 状态面与恢复主入口不一致
- 最近验证摘要、lane 或恢复边界缺失
- 当前验证入口无法定位
- admission 材料本身已失真

当结果为 `fallback` 时：

- admission 输入失真
  - 回退到 `admission`
- build 自身材料缺失但 admission 仍成立
  - 可返回 `block`，不强制回退

## 5. 与 Merge Checkpoint 的边界

- `admission checkpoint` 与 `build checkpoint` 不承担最终放行
- `merge checkpoint` 可以额外消费 PR 模板、reviewer 结论与运行证据，但这些都不是长期真相源
- PR 模板只能作为 merge 放行的补充输入，不得反向覆盖 `work item`、恢复主入口或状态面的 authored 事实

