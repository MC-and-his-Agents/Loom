# Reconciliation Audit

本文件定义 Loom strong governance 下 `reconciliation audit` 的统一状态面合同。

## 1. 能力定位

`reconciliation audit` 不再只是 closeout 旁边的独立审计动作。
它是统一状态控制面的 closeout / reconciliation 子面，负责暴露 merge 后控制面对齐结论。

## 2. 稳定入口

- `python3 tools/loom_flow.py reconciliation audit --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`

## 3. 固定 findings

当前冻结五类 finding：

- `merged_but_open`
  - 当前 issue 对应的实现 PR 已 merged 且 merge commit 已进入主干，但 issue 仍 open
- `absorbed_but_open`
  - 当前事项已被其他 merged work 证明吸收，但控制面仍 open
- `parent_drift`
  - parent 与 child 的收口结论不一致
- `project_drift`
  - issue / PR / project 状态未对齐
- `host_signal_drift`
  - GitHub issue、PR、project、branch 或 repository 信号不可读或互相冲突

每条 finding 至少表达：

- `category = drift`
- `kind`
- `severity`
- `subject`
- `evidence`
- `recommended_action`
- `fallback_to`

## 4. 结果语义

`reconciliation audit` 只允许：

- `pass`
- `warn`
- `fix-needed`
- `block`

解释固定如下：

- `pass`
  - 没有活跃 drift
- `warn`
  - 有观察项，但不阻断当前 closeout 判断
- `fix-needed`
  - 存在可机械同步的 drift，必须先走 `reconciliation sync`
- `block`
  - 存在硬冲突、关键输入缺失或无法继续视为 closeout-ready 的 drift

## 5. 与状态控制面的关系

统一状态控制面至少要能直接消费并展示：

- `reconciliation` 当前结果
- 活跃 drift 列表
- 当前事项是否 `absorbed`
- 当前事项是否具备 `closed_out` basis

调用方不得要求操作者再去另一份口头说明里解释这些 finding。

## 6. 边界约束

- 本入口只读控制面并输出审计结论
- 修复 drift 的正式写路径仍由 `reconciliation sync` 承接
- `reconciliation sync` 必须先消费同范围 audit，再输出 `loom-safe-sync-plan/v1`
- safe sync plan 只解释可机械证明的写入、跳过项与手动项，不替代 audit 本身
- 计划中的每个写入动作必须包含 `source_finding`、`proof_locator`、`write_target` 与 `rollback_note`
- 缺 proof、缺 GitHub object id、缺 Project status field 或存在 `block` finding 时不得生成可执行写入动作
- `absorbed` 的 merge 证明继续由 [host-issue-binding.md](./host-issue-binding.md) 承接
- taxonomy 必须服从 [governance-failure-taxonomy.md](./governance-failure-taxonomy.md)
