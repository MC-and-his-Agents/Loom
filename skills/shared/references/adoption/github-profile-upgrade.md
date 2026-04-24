# GitHub Profile Upgrade

本文件定义 GitHub host 下 `light -> standard -> strong` 的升级路径。

## 1. 目标

升级不是“多加几份文档”，而是把 GitHub profile 从可接入推进到可持续消费 strong governance。

## 2. 升级主线

默认升级顺序固定为：

1. `light`
2. `standard`
3. `strong`

不支持跳过 `standard` 直接宣称 `strong`。

## 3. `light -> standard`

### 3.1 应新增的能力

- `FR` 与 `Work Item` 分层
- formal spec / `spec review`
- 基本 host binding
- 统一 `status control plane`
- closeout / reconciliation 的最小读面

### 3.2 完成判断

至少同时满足：

- `Work Item` 仍是唯一执行入口
- formal spec 路径已不再绕过 `spec review`
- review 与 `merge-ready` 已能消费 `spec_review`
- `status control plane` 已能暴露 item / checkpoint / review / merge-ready

## 4. `standard -> strong`

### 4.1 应新增的能力

- `Work Item` enforcement
- `FR -> Work Item -> PR -> merge commit` 绑定链
- `status control plane v2`
- `stale` / `drift` / `gate_failure` taxonomy
- 强前置 `gate chain`
- `GitHub controlled merge`
- closeout / reconciliation 一体化
- parity validation

### 4.2 完成判断

至少同时满足：

- 非 `Work Item` 入口会 fail-closed
- 所有正式 gate 都能回溯到稳定 `Work Item`
- merge 后可以稳定回链整条交付链
- `status control plane` 可直接暴露 closeout drift
- 已有版本控制内 parity validation 记录

## 5. residue 判断

以下情况表示仍存在 residue，不能宣称 strong governance 完成：

- 仍需口头说明才能定位当前 gate
- merge / closeout 仍依赖临时脚本猜绑定关系
- stale / drift 仍由不同入口各自解释
- GitHub profile 升级结果无法被后续 gate 稳定消费

## 6. Syvert parity 目标

GitHub strong governance 的目标不是复制 Syvert 的文件名，而是达到与 Syvert 同等级的治理能力：

- 唯一执行入口
- formal spec 前置 gate
- 强绑定链
- 统一 `status control plane`
- `GitHub controlled merge`
- closeout / reconciliation 收口

## 7. 非目标

- 不把 Syvert 的 repo-local 命名直接抄成 Loom 默认规则
- 不要求所有 adopted repo 一次性切到 `strong`
- 不把 validation-only parity 直接升级成 blocking host policy
