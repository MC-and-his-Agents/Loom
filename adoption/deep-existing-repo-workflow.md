# Deep Existing Repo Workflow

本文定义 Loom 面向成熟治理重仓接入树的 scoped workflow contract。

它只约束这类 `deep-existing-repo` / typed `repo companion` / `host adapter` / `shadow mode` 工作如何拆 issue、切 PR、做 release judgment 与 closeout 回写；它不是 Loom 全局 issue-model 规则，也不替代 [issue-model.md](/Users/mc/dev/Loom/governance/issue-model.md)、[versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md) 或 [closeout-gate.md](/Users/mc/dev/Loom/harness/closeout-gate.md)。

## 1. 使用边界

本文件仅适用于以下工作：

- 目标是让 Loom 稳定接入成熟既有治理重仓，而不是继续泛化 `complex-existing`
- 工作同时涉及 adoption path、`repo companion` 机读合同、retained host action 结果消费与 validation / closeout
- 需要提前固定拆分方式，避免边界冻结、脚本接线、schema 扩展、验证收口混成一条 PR

它不声明：

- Loom 全局 parent / child issue 默认真相
- Loom 要接管 branch / PR / worktree / merge / ruleset 的底层实现
- 任意 `complex-existing` 仓库都必须升级到 `deep-existing-repo`

## 2. 何时建立父/子 Issue

当成熟治理重仓接入同时涉及以下至少两个面向时，应建立父 issue：

- `deep-existing-repo` / `recognize-and-attach` adoption path
- typed `repo companion` machine contract
- retained host action / repo-native carrier / `shadow mode` 只读消费
- validation / release / parent closeout

在这类树中：

- parent issue
  - 负责总目标、默认 PR slices、版本判断口径与 closeout basis
- child issue
  - 负责单一执行面

这只是成熟治理重仓 adoption 的拆分建议，不改变 Loom 全局 issue-model 的抽象边界。

## 3. 默认 PR Slices

成熟治理重仓接入默认固定为以下 5 批，不混线：

1. `#243`
   - 冻结目标边界、默认 PR slices、版本判断口径与 closeout basis
2. `#244`
   - `deep-existing-repo` / `recognize-and-attach`
3. `#245`
   - typed `repo companion`：`repo-interface v2`
4. `#246`
   - `host adapter`、repo-native interop 与 `shadow mode`
5. `#247`
   - `Syvert` / `WebEnvoy` validation、release judgment 与 closeout

禁止混线：

- `#244` 不得提前引入 `repo-interface v2` 或 `interop.json`
- `#245` 不得接管 retained host actions 的底层实现
- `#246` 不得把 `shadow mode` 直接升级成新的 merge gate
- `#247` 不得抢前置 issue 的实现职责

## 4. 默认 Release Judgment

这类批次默认按 `minor` 规划。

仅当破坏以下任一稳定合同，才升为 `major`：

- `governance_surface.repository_mode`
- root contract
- 既有 CLI 顶层结果语义
- 必备工件

本树中的默认判断含义固定为：

- `deep-existing-repo`
  - 是 `complex-existing` 的 adoption path，不是新的 `repository_mode`
- typed `repo companion`
  - 通过 `repo-interface v2` 承接，并保持 `v1` 可读
- `shadow mode`
  - 当前只做 validation / parity，不直接成为 merge gate

release judgment 的正式版本语义仍以 [versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md) 为准；本文只固定成熟治理重仓接入树的默认判断。

## 5. 最小 Closeout 回写

这类 issue tree closeout 时，至少要对齐以下真相：

- `#243 -> #247` 已按固定顺序完成或明确吸收
- `deep-existing-repo`、typed `repo companion`、`host adapter`、repo-native interop 与 `shadow mode` 的边界已进入版本控制
- release note 已补默认版本判断与下游升级入口
- validation record 已覆盖 `Syvert` / `WebEnvoy` 样本，并明确 `keep`、`adapt`、`needs_validation`
- parent closeout basis 已说明：
  - 这轮新收了什么能力
  - 哪些边界继续保留在宿主层
  - 哪些候选项仍未进入 Loom core
  - 下一棵树从哪里继续

换句话说，这棵树的 closeout 不应再依赖会话反复解释“为什么 `deep-existing-repo` 不是第四个 scenario”“为什么 Loom 仍不接管宿主动作底层实现”。

## 6. `#242` Closeout Basis

`#242` 的正式 closeout basis 由 `#243 -> #247` 共同组成：

- `#243`
  - 冻结 `deep-existing-repo` 树的边界、PR slices、默认 release judgment 与 closeout 口径
- `#244`
  - 把 `deep-existing-repo` 固定为 `complex-existing` 下的 attach-only adoption path
- `#245`
  - 把 `repo-interface v2`、typed `specialized_gates`、`metadata_contract` 与 `context_schema` 收成正式 machine contract
- `#246`
  - 把 `interop.json`、retained host action result / repo-native carrier 的只读消费面，以及 validation-only `shadow parity` 收成正式合同
- `#247`
  - 用 `Syvert` / `WebEnvoy` 样本完成 validation、`v0.6.0 / minor` release judgment 与 parent closeout basis

本树完成后，继续保留在宿主层或候选区的内容包括：

- branch / PR / worktree / merge / ruleset 的底层宿主实现
- `metadata_contract` 的跨仓字段 taxonomy
- repo-native carrier / host adapter 的细字段和 payload 形状
- 把 parity mismatch 自动提升为 blocking merge gate

下一棵树若继续推进，应优先验证：

- live adopted repo 的 `interop.json` dogfood
- `metadata_contract` 是否出现第二个独立样本
- `shadow parity` 是否能安全进入更强的 closeout / merge 语义

## 7. 读取顺序

1. 目标仓库原有根级边界文档
2. [lightweight-retrofit-default.md](/Users/mc/dev/Loom/adoption/lightweight-retrofit-default.md)
3. [repo-companion-contract.md](/Users/mc/dev/Loom/adoption/repo-companion-contract.md)
4. [host-action-contract.md](/Users/mc/dev/Loom/harness/host-action-contract.md)
5. 本文件
6. 相关 reference / validation / release 文档
