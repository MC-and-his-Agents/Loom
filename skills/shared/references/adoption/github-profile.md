# GitHub Profile

本文件定义 Loom 当前默认 `GitHub governance profile`。

GitHub 是默认 host-backed 实现，不是 Loom 唯一可支持宿主。

## 1. 目标

让普通仓库即使没有现成的 `AGENTS.md`、`VISION`、`ROADMAP`、`WORKFLOW`，也能通过 Loom 的最小接入路径获得同等级别的治理能力。

## 2. 最小对象组

GitHub profile 至少应能表达：

- `Roadmap / 阶段目标`
- `Phase`
- `FR`
- `Work Item`
- `implementation PR`
- review / merge gate 信号
- `status control plane`

这些对象可以通过 issue、sub-issue、PR、branch protection、required checks 等宿主能力承接。

## 3. 默认映射

当前默认映射如下：

- `Roadmap / 阶段目标`
  - 版本目标、阶段树或等价治理目标面
- `Phase`
  - 阶段级 issue 或等价规划对象
- `FR`
  - formal spec / planning issue
- `Work Item`
  - 唯一默认执行入口 issue
- `implementation PR`
  - 与当前 `Work Item` 绑定的实现 PR
- `status control plane`
  - 汇总 `Work Item`、gate chain、`head_sha` 与 GitHub 控制面信号的统一读面

## 4. 最小前置关系

默认前置关系必须成立：

- `FR` 先于 `Work Item`
- 命中 formal spec 路径时，`spec review` 先于 `implementation PR`
- `spec gate` 先于 implementation review / merge gate
- `PR review` 与 `merge-ready` 必须消费 `head_sha`
- `merge-ready` 只做最终放行，不补做前序规格判断
- host merge 必须由 GitHub 控制面受控执行，而不是由 Loom 直接代行

## 5. 与 `loom-adopt` 的关系

`loom-adopt` 在 GitHub profile 下至少应能生成或收口以下语义槽位：

- `governance charter`
- `project intent`
- `phase plan`
- `execution contract`

这些槽位不要求必须采用 Syvert 的文件名，但必须让 Loom 能稳定读取与继续执行。

## 6. 三档接入

### Light

- 只生成最小治理骨架
- 只启用 `Work Item -> review -> merge-ready`

### Standard

- 启用 `FR`、formal spec、`spec review`
- 提供更完整的 `item context` 与状态读取

### Strong Governance

- 启用更强的 host 状态读取、受控合并与高级 gate
- 固定使用 `Work Item` 作为唯一执行入口
- 固定暴露 `spec gate -> build gate -> review gate -> merge gate`
- 固定暴露统一 `status control plane`
- 固定要求成熟度升级与 GitHub controlled merge 可被复核

## 7. 非 GitHub 宿主

非 GitHub 宿主只要能提供相同语义，也可以实现 Loom。

Loom 冻结的是：

- 对象语义
- 前置关系
- 状态读取
- gate chain
- maturity upgrade
- merge-ready 语义

不是 GitHub 的产品细节。
