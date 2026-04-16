# Workspace Lifecycle

本文件定义 Loom 当前工作现场生命周期与 `purity-check` 的执行侧合同。

字段归属与读取顺序仍以 [fact-chain-contract.md](./fact-chain-contract.md) 为准。
工作现场最小模型与纯度目标分别见 [workspace-model.md](./workspace-model.md) 与 [workspace-and-purity.md](./workspace-and-purity.md)。

## 1. 能力定位

Loom 当前日常执行 CLI 至少提供以下入口：

- `workspace create`
- `workspace locate`
- `workspace cleanup`
- `workspace retire`
- `purity-check`

这些入口只消费：

- `init-result` 的 locator truth
- `work item` 的 `workspace_entry`
- `work item` 的 `recovery_entry`
- 恢复主入口中的动态执行事实
- 状态面中的派生汇总

它们不得新增第二套执行状态真相。

## 2. 统一输入与输出

### 2.1 输入

所有生命周期入口至少接受：

- `--target`
  - 目标仓库根目录
- `--item`
  - 可选；若提供，则必须与事实链中的当前事项一致

机械读取顺序固定为：

1. 读取 `init-result`
2. 读取 `work item`
3. 读取恢复主入口
4. 需要汇总时读取状态面

### 2.2 输出

所有生命周期入口都应返回 JSON，至少表达：

- 当前事项
- 工作现场入口与定位结果
- 恢复入口
- 当前 checkpoint
- 当前 purity 结论
- `result`
- `summary`
- `missing_inputs`
- `fallback_to`

## 3. Workspace Create

### 3.1 语义

`workspace create` 只负责建立或验证 `workspace_entry` 对应的现场语义。

它可以：

- 验证 `workspace_entry` 能稳定定位
- 在 `workspace_entry` 指向仓库内相对路径且目录缺失时创建该目录

它不得：

- 自动创建宿主平台特定 worktree
- 额外记账另一份现场绑定真相
- 绕过事实链直接写入“当前事项”

### 3.2 失败语义

以下情况至少应返回 `block`：

- `workspace_entry` 越出目标仓库边界
- 事实链断裂
- 当前现场存在无关改动或脏状态
- 当前工作现场已被多个活跃事项复用

## 4. Workspace Locate

### 4.1 语义

`workspace locate` 至少返回：

- 当前事项 `item`
- 当前工作现场 `workspace`
- 恢复入口 `recovery`
- 当前 checkpoint `checkpoint`
- 当前 purity `purity`

### 4.2 失败语义

以下情况至少应返回 `block`：

- `workspace_entry` 无法定位
- 当前事实链无法读通
- 现场语义虽能定位，但当前 purity 已不适合继续执行

## 5. Workspace Cleanup

### 5.1 语义

`workspace cleanup` 只允许清理 Loom 自己产生的临时残留。

第一版最小能力只覆盖 Loom-owned temporary paths，例如：

- `.loom/tmp`
- `.loom/.tmp`
- `.loom/runtime/tmp`
- `.loom/runtime/cache`
- `.loom/flow/tmp`

### 5.2 失败语义

以下情况至少应返回 `block`，且不得自动删除内容：

- 工作区存在无关改动
- 工作区存在用户未分流的正式变更
- 将要删除的路径含有已跟踪文件
- 事实链、现场绑定或事项边界已经失真

## 6. Workspace Retire

### 6.1 语义

`workspace retire` 的顺序固定为：

1. 先执行 cleanup 语义
2. 再将恢复主入口中的 `Current Checkpoint` 回写为 `retired`
3. 同步回写状态面中的派生 `Current Checkpoint`

它不默认删除现场目录。

### 6.2 成功语义

`retire` 成功后，至少应满足：

- 当前事项仍可被事实链读到
- 恢复主入口的 `Current Checkpoint` 为 `retired`
- 状态面与恢复主入口一致
- 后续 `locate` 不会再把该现场误判为活跃执行现场

## 7. Purity Check

### 7.1 最小硬失败项

`purity-check` 第一版至少对以下情况给出硬失败：

- 事实链断裂
- 当前现场与 `workspace_entry` 不匹配
- 工作区存在未分流残留
- 当前现场被多个活跃事项共享，明显不再是单一目标

### 7.2 报告但暂不硬失败的项

以下项第一版只做报告，不作为硬失败：

- branch purity
- PR purity

这些项可以作为后续宿主适配扩展接入，但当前不改变生命周期命令的硬失败口径。

