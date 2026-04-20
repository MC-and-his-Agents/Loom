# Companion-Oriented Workflow

本文定义 `repo companion` 改造的 scoped workflow contract。

它只约束这类 companion-oriented 工作如何拆 issue、切 PR、做 release judgment 与 closeout 回写；它不是 Loom 全局 issue-model 规则，也不替代 [issue-model.md](/Users/mc/dev/Loom/governance/issue-model.md)、[versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md) 或 [closeout-gate.md](/Users/mc/dev/Loom/harness/closeout-gate.md)。

## 1. 使用边界

本文件仅适用于以下工作：

- 目标是新增或调整 `repo companion` 合同
- 工作同时涉及 companion 文档、机读接口、flow 消费、reference spec 或 migration closeout
- 需要提前固定拆分方式，避免合同、代码、reference spec、release/closeout 混成一条 PR

它不声明：

- Loom 全局 parent / child issue 默认真相
- 任意仓库都必须采用同一 issue tree
- 宿主平台的 parent/sub-issue 字段语义

## 2. 何时建立父/子 Issue

当 companion 改造同时涉及以下至少两个面向时，应建立父 issue：

- companion 主合同
- `governance_surface` / `loom-init` / `loom_flow` 接线
- reference companion spec
- migration / validation / release / closeout

在这类树中：

- parent issue
  - 负责总目标、默认 PR slices 与 closeout basis
- child issue
  - 负责单一执行面

这只是 companion-oriented adoption 的拆分建议，不改变 Loom 全局 issue-model 的抽象边界。

## 3. 默认 PR Slices

`repo companion` 改造默认固定为以下 6 批，不混线：

1. `#199`
   - companion 主合同与 manifest / repo-interface 最小边界
2. `#200`
   - `governance_surface` / `loom-init` 暴露 `repo_interface`
3. `#204`
   - scoped workflow 合同
4. `#201`
   - `loom_flow` 消费 `repo_specific_requirements`
5. `#202`
   - `Syvert` / `WebEnvoy` reference companion spec
6. `#203`
   - migration / validation / release / closeout 收口

禁止混线：

- companion 主合同不得与代码接线混在同一 PR
- workflow 合同不得与脚本接线混在同一 PR
- reference spec 不得抢在机读接口稳定前定稿
- migration / validation / release / closeout 不得抢前置 issue 的职责

## 4. 默认 Release Judgment

这类批次默认按 `minor` 规划。

仅当破坏以下任一稳定合同，才升为 `major`：

- `governance_surface`
- root contract
- 必备工件
- 既有 CLI 结果语义

release judgment 的正式版本语义仍以 [versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md) 为准；本文只固定 companion-oriented 改造的默认判断。

## 5. 最小 Closeout 回写

这类 issue tree closeout 时，至少要对齐以下真相：

- issue tree 已按 6 批完成或明确吸收
- release note 已补 companion interface 变更与默认版本判断
- upgrade note 已写下游最小新增工件
- validation record 已覆盖 absent / docs-only / incomplete / present 的机读状态
- closeout basis 已说明 parent 只消费子 issue 已成立真相

换句话说，`repo companion` 树的 closeout 不应再依赖会话反复解释“为什么要这么拆、为什么现在算完成”。

## 6. 读取顺序

1. 目标仓库原有根级边界文档
2. [repo-companion-contract.md](/Users/mc/dev/Loom/adoption/repo-companion-contract.md)
3. 本文件
4. 相关 reference / migration / release / validation 文档
