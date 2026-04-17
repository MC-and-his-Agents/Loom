# Harness

`harness/` 承接 Loom 的稳定执行合同与宿主编排语义。

这里的文件不记录实时进度，也不把初始化场景或强度模型重复写成多份说明。
这里承接的是已经冻结的执行链路、宿主控制面边界与可持续复用的编排职责；完整阶段目标由 `docs/roadmap.md` 承接，初始化场景和强度模型讨论由 `harness-design.md` 承接。

## 组件边界

- [work-item-contract.md](./work-item-contract.md)
  - 定义进入正式执行前必须存在的事项与初始化产物合同
- [fact-chain-contract.md](./fact-chain-contract.md)
  - 定义静态真相、动态真相与派生读面的唯一归属关系
- [execution-context.md](./execution-context.md)
  - 定义每轮正式执行必须绑定和读取的最小上下文语义
- [execution-chain.md](./execution-chain.md)
  - 定义从初始化产物到 merge checkpoint 放行的最小执行链路
- `daily-entry-matrix.md`
  - 定义 `skills` / CLI / gate 在日常高频动作上的入口矩阵与职责边界
- `checkpoint-model.md`
  - 定义 `admission` / `build` checkpoint 的输入、输出、失败语义与回退去向
- [workspace-model.md](./workspace-model.md)
  - 定义执行现场的隔离、定位与 clean state 要求
- `workspace-lifecycle.md`
  - 定义 `create`、`locate`、`cleanup`、`retire` 与 `purity-check` 的生命周期合同
- [host-action-contract.md](./host-action-contract.md)
  - 定义现有 host-facing actions 的统一结果、`fallback_to` 与 ownership 合同
- [host-lifecycle-boundary.md](./host-lifecycle-boundary.md)
  - 定义 Loom 与宿主 branch / PR / git worktree 生命周期的边界
- [host-issue-binding.md](./host-issue-binding.md)
  - 定义 Loom 消费 `active issue` 与 branch / git worktree / PR / merge commit 的绑定合同
- [reconciliation-audit.md](./reconciliation-audit.md)
  - 定义 Loom 发现 absorbed-but-open / parent drift / project drift 的审计合同
- [recovery-model.md](./recovery-model.md)
  - 定义唯一恢复主入口、`checkpoint`、`resume`、`handoff` 与每轮回写合同
- [review-execution.md](./review-execution.md)
  - 定义正式 review 执行层、review record 与 merge checkpoint 的对接边界
- [status-surface.md](./status-surface.md)
  - 定义状态读取字段、运行时证据入口与 `not_applicable` 语义
- [automation-frontload.md](./automation-frontload.md)
  - 定义适合机械化前置的检查矩阵与覆盖边界
- [merge-checkpoint.md](./merge-checkpoint.md)
  - 定义执行侧放行输入、结果语义与回退承接
- [closeout-gate.md](./closeout-gate.md)
  - 定义 closeout check / sync 与 GitHub 控制面对齐的最小执行链路
- [workspace-and-purity.md](./workspace-and-purity.md)
  - 定义现场职责纯度、分支纯度与范围控制边界

这些文件共同表达的不是零散脚本集合，而是从 work item / fact-chain 到 review / merge / closeout 的统一编排链路。
当 Loom 需要调用 GitHub、CI、review engine、`git worktree` 或其他宿主能力时，也应先通过 [host-action-contract.md](./host-action-contract.md) 收口结果与去向，再由各专题文件承接细节，而不是在外部再复制一套真相。

## 目录约束

- 本目录优先表达可执行规则与编排责任，不在多个文件并行复述同一条执行链路
- 同一条 harness 规则应有唯一主落点；允许围绕同一编排链路按不同宿主表面拆分文件，但不得复制第二套真相
- 若某能力仍依赖初始化场景、装配关系、强度模型或阶段性取舍讨论，应留在 `harness-design.md` 或 `docs/roadmap.md`
