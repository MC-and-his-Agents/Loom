# Harness

`harness/` 承接 Loom 的稳定执行合同与宿主编排语义。

这里的文件不记录实时进度，也不把初始化场景或强度模型重复写成多份说明。
这里承接的是已经冻结的执行链路、宿主控制面边界与可持续复用的编排职责；当前阶段目标由对应 GitHub issues 承接，初始化场景和强度模型讨论由 [harness-design.md](../../architecture/harness-design.md) 承接。

## 组件边界

- [work-item-contract.md](./work-item-contract.md)
  - 定义唯一默认执行入口与 enforcement 合同
- [cli-first-control-plane.md](./cli-first-control-plane.md)
  - 定义 `loom` CLI、SKILLS、plugins、installer shim 与 `.loom/` 的职责边界和 fail-closed 规则
- [cli-command-matrix.md](./cli-command-matrix.md)
  - 冻结 CLI-first phase 的命令命名、状态分类与机器可读矩阵入口
- [full-spec-suite-cli-surface.md](./full-spec-suite-cli-surface.md)
  - 保留已退役 full-spec suite CLI 计划的 locator；当前公共产品面不得推荐该旧控制面
  - 规划 full spec suite 相关 CLI 自动化入口、JSON 输出、failure taxonomy 与后续 implementation backlog；不实现命令
- [fact-chain-contract.md](./fact-chain-contract.md)
  - 定义静态真相、动态真相、host/control-plane mirror、retained result 与派生读面的读取优先级和 provenance 纪律
- [execution-context.md](./execution-context.md)
  - 定义每轮正式执行必须绑定和读取的最小上下文语义
- [execution-attempt.md](./execution-attempt.md)
  - 定义单次命令尝试的 runtime evidence envelope、freshness 与禁止承载 authored progress 的边界
- [dynamic-tool-handshake.md](./dynamic-tool-handshake.md)
  - 定义 dynamic tool availability 的 `advertised` / `unavailable` / `unsupported` / `failed` 词表、companion / interop 边界与状态展示规则
- [policy-read-surface.md](./policy-read-surface.md)
  - 定义 approval / sandbox policy 读面、missing / conflict / unsafe 词表、风险摘要与 host-adapter 边界
- [hook-locator-contract.md](./hook-locator-contract.md)
  - 定义 lifecycle hook locator、host-native adapter mapping、extension 结果词表与 runtime-evidence-only 边界
- [hook-envelope-contract.md](./hook-envelope-contract.md)
  - 定义 mapped hook envelope、context injection / blocking decision / runtime evidence 分类与 failure 语义
- [structured-event-evidence.md](./structured-event-evidence.md)
  - 定义 agent / tool / validation / failure / tracker event evidence 的字段、fake orchestration fixtures 与禁止承载 authored truth 的边界
- [subagent-driven-execution.md](./subagent-driven-execution.md)
  - 定义 subagent-driven build mode 的 ownership、integration、repeated blocker 与主执行者回写边界
- [lane-orchestration.md](./lane-orchestration.md)
  - 定义 high-throughput milestone / FR 推进中的 lane descriptor、shared carrier 串行写、stale result 与冲突处理合同
- [item-context-contract.md](./item-context-contract.md)
  - 定义当前活跃 `Work Item` 的最小 machine-readable 上下文字段与读取边界
- [status-surface-contract.md](./status-surface-contract.md)
  - 定义 `status control plane v2` 的对象、字段组、provenance 与消费边界
- [status-surface.md](./status-surface.md)
  - 定义统一状态控制面的字段语义、`runtime_state` / `runtime_evidence` 边界、运行时证据与 closeout 展示
- [governance-failure-taxonomy.md](./governance-failure-taxonomy.md)
  - 定义 `stale` / `drift` / `gate_failure` 的统一 taxonomy
- [governance-lint-taxonomy.md](./governance-lint-taxonomy.md)
  - 定义 Governance Lint / Operating Lint 的 result strength、core lint kind、repo-specific 边界与 derived-evidence 消费纪律
- [execution-chain.md](./execution-chain.md)
  - 定义从初始化产物到 merge checkpoint 放行的最小执行链路
- [task-carrier-contract.md](./task-carrier-contract.md)
  - 定义 execution breakdown unit 如何由 GitHub issue、Project item、checklist、`tasks.md`、external tracker 或 `not_applicable` 承接，并保护 `Work Item` truth
- [gate-chain.md](./gate-chain.md)
  - 定义 implementation review、`merge-ready`、`controlled merge`、`closeout` 的强前置消费链
- [gate-freeze.md](./gate-freeze.md)
  - 保留已退役 gate-freeze snapshot 的 locator，并指向 current-head host attestation 与 retained PR gate result 的当前交接路径
- [tiered-gate-consumption-contract.md](./tiered-gate-consumption-contract.md)
  - 定义治理强度字段、`suite_path: not_applicable` 与 fail-closed gate 消费合同
  - Final closeout and release/no-release convergence for #1314 is indexed at [../../evidence/governance-intensity-final-closeout.md](../../evidence/governance-intensity-final-closeout.md)
- `checkpoint-model.md`
  - 定义 `admission` / `build` checkpoint 的输入、输出、失败语义与回退去向
- [workspace-model.md](./workspace-model.md)
  - 定义执行现场的隔离、定位与 clean state 要求
- [workspace-profile.md](./workspace-profile.md)
  - 定义 `single-workspace`、`per-item-worktree`、`attach-existing` 三类默认现场装配 profile
- [repo-local-gate-starter.md](./repo-local-gate-starter.md)
  - 定义新仓库可用的本地 gate starter aliases，并明确它们不是宿主强制门禁
- [regression-surface-contract.md](./regression-surface-contract.md)
  - 定义 regression bucket、named surface、最小 evidence schema，以及 fast/full validation 的共享合同
- `workspace-lifecycle.md`
- `worker-backend-contract.md`
  - 定义 `create`、`locate`、`cleanup`、`retire` 与 `purity-check` 的生命周期合同
- [host-action-contract.md](./host-action-contract.md)
  - 定义现有 host-facing actions 的统一结果、`fallback_to` 与 ownership 合同
- [host-api-budget.md](./host-api-budget.md)
  - 定义 GitHub REST / GraphQL 读取预算、快照、缓存与 fallback 语义
- [host-lifecycle-boundary.md](./host-lifecycle-boundary.md)
  - 定义 Loom 与宿主 branch / PR / git worktree 生命周期的边界
- [host-issue-binding.md](./host-issue-binding.md)
  - 定义 `Work Item` 与 branch / PR / head / merge commit 的绑定链
- [host-binding-inspector.md](./host-binding-inspector.md)
  - 定义 host binding inspector 的只读绑定链、Project item 与 dependency graph 输出合同
- [native-dependency-contract.md](./native-dependency-contract.md)
  - 定义 GitHub native issue dependency 作为 host mirror 的读取、drift 与 gate 消费边界
- [controlled-merge.md](./controlled-merge.md)
  - 定义 GitHub merge control plane 的默认消费与 merge 后交接
- [pr-merge-gate.md](./pr-merge-gate.md)
  - 定义 PR-specific semantic review approval 与宿主 required check 的桥接合同
- [reconciliation-audit.md](./reconciliation-audit.md)
  - 定义 closeout / reconciliation 统一状态面的 drift 审计合同
- [recovery-model.md](./recovery-model.md)
  - 定义唯一恢复主入口、`checkpoint`、`resume`、`handoff` 与每轮回写合同
- [repo-global-artifact-classification.md](./repo-global-artifact-classification.md)
  - 定义 repo truth、workstation registry、global runtime cache、diagnostic artifact 与 repo carrier 摘要/locator 的分类边界
- [review-execution.md](./review-execution.md)
  - 定义正式 review、current-head host attestation 与 merge-ready 的对接边界
- [automation-frontload.md](./automation-frontload.md)
  - 定义适合机械化前置的检查矩阵与覆盖边界
- [loom-check-runtime-purity.md](./loom-check-runtime-purity.md)
  - 定义 `loom_check` 并发隔离、运行现场纯度、临时目录 ownership 与宿主环境继承边界
- [merge-checkpoint.md](./merge-checkpoint.md)
  - 定义 `merge-ready` 的执行侧放行输入、结果语义与回退承接
- [closeout-gate.md](./closeout-gate.md)
  - 定义 `closeout` 与 `reconciliation` 的最终收口链路
- [workspace-and-purity.md](./workspace-and-purity.md)
  - 定义现场职责纯度、分支纯度与范围控制边界

这些文件共同表达的不是零散脚本集合，而是从 typed Work Item、正式 worktree、
GitHub PR/head 到 review、merge 与 host-derived closeout 的统一编排链路。
当 Loom 需要调用 GitHub、CI、review engine、`git worktree` 或其他宿主能力时，也应先通过 [host-action-contract.md](./host-action-contract.md) 收口结果与去向，再由各专题文件承接细节，而不是在外部再复制一套真相。

读取纪律：

- goal、scope 与 dependency 由 GitHub Issue / Work Item 拥有
- PR、branch、head、checks 与 merge facts 由 GitHub live readback 拥有
- semantic review 与 delivery closeout 由 current-head host attestation 拥有
- retained result 只能作为已发生宿主动作或 repo-native verdict 的证据 provenance，必须绑定当前消费对象
- repo companion 只声明 policy 与 interop locator，不承接 execution truth
- derived surface 只汇总、展示 taxonomy 与阻断原因；不得反向覆盖 authored truth
- provenance 缺失、绑定过期、parallel truth 或 stale derived surface 在放行路径上必须阻断

## 行为优先执行层

Loom 的默认执行层以 BDD 外环和 TDD 内环组合运行：

- BDD 外环来自正式 spec 的可观察场景，回答“什么行为必须成立”
- TDD 内环来自 plan / implementation 的测试策略，回答“实现如何以测试或等价检查证明推进”
- `behavior evidence` 证明场景成立；`test evidence` 证明测试、检查或人工验证已经执行
- `fresh verification evidence` 表示证据覆盖当前 `HEAD`、当前范围与当前恢复摘要，不得复用 stale 结果放行

这些语义不要求纯文档事项强制写测试，但要求每个 gate 能读到行为证据、测试证据或明确的 `not_applicable`。
当 execution 由多个 subagent 分工推进时，主执行者必须复核 owned output、验证
结果、阻断项与 scope，再由 reviewer 或 GitHub host facts 进入 gate；subagent 输出
本身不构成第二真相源。

## 目录约束

- 本目录优先表达可执行规则与编排责任，不在多个文件并行复述同一条执行链路
- 同一条 harness 规则应有唯一主落点；允许围绕同一编排链路按不同宿主表面拆分文件，但不得复制第二套真相
- 若某能力仍依赖初始化场景、装配关系、强度模型或阶段性取舍讨论，应留在 [harness-design.md](../../architecture/harness-design.md) 或对应 GitHub issues
