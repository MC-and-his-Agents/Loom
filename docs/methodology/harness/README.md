# Harness

`harness/` 承接 Loom 的稳定执行合同与宿主编排语义。

这里的文件不记录实时进度，也不把初始化场景或强度模型重复写成多份说明。
这里承接的是已经冻结的执行链路、宿主控制面边界与可持续复用的编排职责；当前阶段目标由对应 GitHub issues 承接，初始化场景和强度模型讨论由 [harness-design.md](../../architecture/harness-design.md) 承接。

## 组件边界

- [work-item-contract.md](./work-item-contract.md)
  - 定义唯一默认执行入口与 enforcement 合同
- [fact-chain-contract.md](./fact-chain-contract.md)
  - 定义静态真相、动态真相与派生读面的唯一归属关系
- [execution-context.md](./execution-context.md)
  - 定义每轮正式执行必须绑定和读取的最小上下文语义
- [item-context-contract.md](./item-context-contract.md)
  - 定义当前活跃 `Work Item` 的最小 machine-readable 上下文字段与读取边界
- [status-surface-contract.md](./status-surface-contract.md)
  - 定义 `status control plane v2` 的对象、字段组与消费边界
- [status-surface.md](./status-surface.md)
  - 定义统一状态控制面的字段语义、运行时证据与 closeout 展示
- [governance-failure-taxonomy.md](./governance-failure-taxonomy.md)
  - 定义 `stale` / `drift` / `gate_failure` 的统一 taxonomy
- [execution-chain.md](./execution-chain.md)
  - 定义从初始化产物到 merge checkpoint 放行的最小执行链路
- [gate-chain.md](./gate-chain.md)
  - 定义 implementation review、`merge-ready`、`controlled merge`、`closeout` 的强前置消费链
- `checkpoint-model.md`
  - 定义 `admission` / `build` checkpoint 的输入、输出、失败语义与回退去向
- [workspace-model.md](./workspace-model.md)
  - 定义执行现场的隔离、定位与 clean state 要求
- [workspace-profile.md](./workspace-profile.md)
  - 定义 `single-workspace`、`per-item-worktree`、`attach-existing` 三类默认现场装配 profile
- `workspace-lifecycle.md`
  - 定义 `create`、`locate`、`cleanup`、`retire` 与 `purity-check` 的生命周期合同
- [host-action-contract.md](./host-action-contract.md)
  - 定义现有 host-facing actions 的统一结果、`fallback_to` 与 ownership 合同
- [host-lifecycle-boundary.md](./host-lifecycle-boundary.md)
  - 定义 Loom 与宿主 branch / PR / git worktree 生命周期的边界
- [host-issue-binding.md](./host-issue-binding.md)
  - 定义 `Work Item` 与 branch / PR / head / merge commit 的绑定链
- [controlled-merge.md](./controlled-merge.md)
  - 定义 GitHub merge control plane 的默认消费与 merge 后交接
- [reconciliation-audit.md](./reconciliation-audit.md)
  - 定义 closeout / reconciliation 统一状态面的 drift 审计合同
- [recovery-model.md](./recovery-model.md)
  - 定义唯一恢复主入口、`checkpoint`、`resume`、`handoff` 与每轮回写合同
- [review-execution.md](./review-execution.md)
  - 定义正式 review 执行层、review record 与 merge checkpoint 的对接边界
- [automation-frontload.md](./automation-frontload.md)
  - 定义适合机械化前置的检查矩阵与覆盖边界
- [merge-checkpoint.md](./merge-checkpoint.md)
  - 定义 `merge-ready` 的执行侧放行输入、结果语义与回退承接
- [closeout-gate.md](./closeout-gate.md)
  - 定义 `closeout` 与 `reconciliation` 的最终收口链路
- [workspace-and-purity.md](./workspace-and-purity.md)
  - 定义现场职责纯度、分支纯度与范围控制边界

这些文件共同表达的不是零散脚本集合，而是从 `Work Item` / fact-chain 到 review / merge / closeout 的统一编排链路。
当 Loom 需要调用 GitHub、CI、review engine、`git worktree` 或其他宿主能力时，也应先通过 [host-action-contract.md](./host-action-contract.md) 收口结果与去向，再由各专题文件承接细节，而不是在外部再复制一套真相。

## 行为优先执行层

Loom 的默认执行层以 BDD 外环和 TDD 内环组合运行：

- BDD 外环来自正式 spec 的可观察场景，回答“什么行为必须成立”
- TDD 内环来自 plan / implementation 的测试策略，回答“实现如何以测试或等价检查证明推进”
- `behavior evidence` 证明场景成立；`test evidence` 证明测试、检查或人工验证已经执行
- `fresh verification evidence` 表示证据覆盖当前 `HEAD`、当前范围与当前恢复摘要，不得复用 stale 结果放行

这些语义不要求纯文档事项强制写测试，但要求每个 gate 能读到行为证据、测试证据或明确的 `not_applicable`。
当 execution 由多个 subagent 分工推进时，主执行者必须把各 subagent 的 owned output、验证结果、阻断项和偏离范围情况整合回单一恢复入口、review record 或对应 gate 输入；subagent 输出本身不构成第二真相源。

## 目录约束

- 本目录优先表达可执行规则与编排责任，不在多个文件并行复述同一条执行链路
- 同一条 harness 规则应有唯一主落点；允许围绕同一编排链路按不同宿主表面拆分文件，但不得复制第二套真相
- 若某能力仍依赖初始化场景、装配关系、强度模型或阶段性取舍讨论，应留在 [harness-design.md](../../architecture/harness-design.md) 或对应 GitHub issues
