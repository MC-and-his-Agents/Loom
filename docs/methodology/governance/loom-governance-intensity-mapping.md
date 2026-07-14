# Loom Governance Intensity Mapping

本文件定义 Loom 对通用变更治理强度模型的仓库内映射。

通用模型见 [change-governance-intensity.md](./change-governance-intensity.md)。
本文件只说明 Loom 如何把 `light`、`standard`、`reinforced`
映射到自身的 issue、branch / worktree、review、gate、checks、release /
no-release 与 closeout 消费路径。治理强度不得恢复已退役 repo carrier。

本映射不得反向改写通用模型的风险维度或强度档位。

## 1. 定位

Loom 是 agent-first project operating layer。它的治理强度映射服务于：

- 在执行前选择合适路径
- 让 docs-only 变更可以使用明确的轻量 formal-suite 决策
- 保留 current-head review、PR/head binding、CI、release / no-release 与 host-derived closeout
- 把未实现的自动消费面交给后续 Work Item，而不是在本文档中假装已实现

本文件不实现 CLI、gate parser、fixtures、runtime 行为、`.loom/bin` 分发面或
docs-governance checklist。

Gate 对本映射的字段消费合同见
[tiered-gate-consumption-contract.md](../harness/tiered-gate-consumption-contract.md)。

## 2. Loom 执行面矩阵

| 强度 | 典型 Loom 变更 | issue / branch / worktree | 默认事实源 | 规格 / 验证 | review | gate / checks | closeout |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `light` | 局部文档、链接、格式、低风险说明 | 可用单一 issue 或 Work Item；必须在非 `main` 的绑定分支 / worktree 执行 | GitHub Issue/PR + Git/worktree live facts | 允许最小 targeted checks；不适用项只在 PR policy 中声明理由 | 需要 current-head host attestation | `git diff --check`、targeted checks、PR gate 与适用 required checks | 从 GitHub merge、checks、issue 与 no-release 判断派生 |
| `standard` | 方法论合同、内部执行合同、跨文件治理边界 | 绑定明确 Work Item、branch、正式 worktree、PR 与 live head | GitHub Issue/PR + repo companion policy | 使用仓库原生验证矩阵，说明下游消费者和升级条件 | docs / implementation review 绑定 exact head | targeted checks、一次必要 aggregate、PR gate、hosted checks | host-derived closeout，并记录后续 issue |
| `reinforced` | 运行模型、gate、runtime、CLI、fixtures、发布、权限或外部可见动作 | 正式 Work Item、隔离 worktree、PR、live head、dependency readback | 标准事实源不变；只提高验证与审查强度 | 增加安全、runtime、fixture、release 或 live evidence | exact-head 专门 review / guardian | 分级验证、hosted negatives、controlled merge 与必要发布检查 | 消费 merge、main、issue/project、release 与可信 acceptance facts |

## 3. 最低证据

所有强度都必须保留以下证据：

- 目标与范围
- 强度判定依据
- 变更摘要
- 当前验证结论
- current-head review attestation
- typed Work Item、PR head / branch / formal worktree 绑定
- release / no-release 判断
- closeout basis

`light` 只允许降低验证与说明成本，不改变事实 owner，也不恢复 repo carrier。

`standard` 还必须保留：

- 受影响 Loom 执行面
- 下游消费者或依赖事项
- 验证矩阵
- 回退或重新检查条件

`reinforced` 还必须保留：

- 必要的正式规格、计划或等价合同
- 风险分解和升级依据
- 长链路、runtime、host、fixture、release 或外部可见证据中适用部分
- 下游消费条件和禁止动作

## 4. `docs-only` 与 `docs-governance`

Docs-only 变更可以使用轻量 formal-suite 决策，但只能在以下条件同时成立时消费：

- scope 只包含方法论文档、模板说明、landing link 或当前 Work Item carrier
- 不改变 runtime、CLI、gate parser、fixtures、generated skill、`.loom/bin`、发布行为或 AGENTS 根规则
- `Suite path: not_applicable` 有 rationale、consumer boundary、recheck condition、scope proof、review requirement
- PR body 记录 release / no-release 判断
- current-head review、fact-chain、CI / hosted checks、PR gate、controlled merge 和 closeout 仍按当前路径执行

Docs-governance 轻量路径的执行 checklist 见
[docs-governance-lite-checklist.md](./docs-governance-lite-checklist.md)。
Gate 行为仍由 #1322 实现；本文档只冻结它必须消费的边界。

## 5. 升级触发

执行中出现以下任一情况，当前路径必须升级或回到分流判断：

- docs-only diff 扩大到 runtime、tools、fixtures、generated payload、skills 分发面或 AGENTS 根规则
- 本次变更开始定义 machine carrier 字段，且后续 gate 会机械消费该字段
- PR body、Work Item、status、review、branch、head SHA 或 issue 绑定不一致
- review 后发生非 carrier-only 漂移
- suite `not_applicable` 缺少 rationale、consumer boundary、recheck condition、scope proof 或 review requirement
- release / no-release 影响无法证明
- 下游 issue 开始消费尚未冻结或未审查的语义
- hosted checks、PR gate、controlled merge 或 closeout 无法读到同一 fact-chain

升级不是失败。升级表示当前证据不足以支撑原强度。

## 6. 后续消费面

本映射冻结语义，不实现后续消费面：

- #1318 消费本映射，沉淀先分类再执行的 AGENTS 原则
- #1319 消费本映射，定义 docs-governance 轻量路径 checklist
- #1321 消费本映射和 gate 合同，实现治理强度元数据载体
- #1322 消费本映射和 gate 合同，实现 docs-governance 轻量 gate 行为
- #1323 消费本映射和 gate 合同，增加升级与滥用防护 fixtures
- #1324 消费本映射，收口文档与 release / no-release 证据

这些事项未完成前，本文档不得被解释为对应 CLI、gate parser 或 fixture 已经可用。

## 7. 一句话结论

Loom 的治理强度映射让轻量路径更短，但不让任何路径绕过 review、事实链、head 绑定、CI、release 判断或 closeout。
