# GitHub Profile

本文件定义 Loom strong governance 默认 `GitHub governance profile`。

GitHub 是默认 host-backed 实现，不是 Loom 唯一可支持宿主。

## 1. 目标

让普通仓库不仅能接入 Loom，还能沿同一条升级路径逐步达到 strong governance。

## 2. 最小对象组

GitHub profile 至少应能表达：

- `Roadmap / 阶段目标`
- 目标仓库 `release / version` 目标面
- `Phase`
- `FR`
- `Work Item`
- `implementation PR`
- implementation review / `merge-ready`
- `controlled merge`
- `closeout / reconciliation` 信号

这些对象可以通过 issue、sub-issue、PR、branch protection、required checks、merge commit、Project 等宿主能力承接。

## 3. 默认映射

当前默认映射如下：

- `Roadmap / 阶段目标`
  - 版本目标、阶段树或等价治理目标面
- 目标仓库 `release / version` 目标面
  - repo-owned 或 host-owned release target object
  - 用于声明当前目标版本、目标分支、release goal、纳入范围与 closeout evidence locator
  - 只作为规划与收口容器，不替代 `Work Item`
- `Phase`
  - 阶段级 issue 或等价规划对象
  - deferred Phase container 必须声明 `Activation Policy` 与 `Roadmap Inventory`
  - `Roadmap Inventory` 必须列出 canonical FR children 与 canonical Work Item children
  - closed deferred children are deferred, not completed
  - duplicate/retry artifacts 必须单独标明，并排除出 canonical inventory
- `FR`
  - formal spec / planning issue
- `Work Item`
  - 唯一默认执行入口 issue
- `implementation PR`
  - 与当前 `Work Item` 绑定的实现 PR
- `controlled merge`
  - branch protection、required checks、merge method、merge commit 的统一消费面
- `closeout / reconciliation`
  - 可继续消费目标仓库 release/version 目标面的 closeout evidence 与 release status gap

## 4. Delivery Planning Host Mapping

当 delivery planning 输出 `Phase / FR / Work Item / PR` 规划时，GitHub profile 必须把宿主对象当作 carrier，而不是 Loom truth。

默认承接规则：

- `Phase`
  - Host object: GitHub issue。
  - Authority boundary: 表达阶段目标、范围、非目标、FR 子项、完成语义和 closeout evidence locator。
  - Locator / provenance: issue number、Project item、parent/sub-issue links、closeout comment。
  - Forbidden use: 不直接承接 implementation PR，不替代 child FR / Work Item 的完成事实。
- `FR`
  - Host object: GitHub issue，优先作为 Phase 的 native sub-issue。
  - Authority boundary: 表达功能/治理能力边界、消费输入、输出合同、非目标、验收标准和 child Work Item。
  - Locator / provenance: issue number、parent Phase、sub-issue list、blocked-by/blocks links、progress comments。
  - Forbidden use: 不直接作为默认 implementation PR 绑定对象；实现必须落到 Work Item。
- `Work Item`
  - Host object: GitHub issue，优先作为 FR 的 native sub-issue。
  - Authority boundary: 唯一默认执行入口；绑定 branch、正式 worktree、PR、review、merge-ready、merge commit 和 closeout。
  - Locator / provenance: issue number、branch、workspace entry、PR、head SHA、merge commit、Project item、Loom recovery/review carriers。
  - Forbidden use: 不被 checklist item、Project item、`tasks.md` 条目或 PR body Markdown 替代。
- `Project item`
  - Host object: GitHub Project item。
  - Authority boundary: 视图、筛选、排序和执行看板。
  - Locator / provenance: Project number、item id、Status field。
  - Forbidden use: 不替代 issue state、Work Item、review、merge-ready、closeout 或 Loom recovery truth。
- `implementation PR`
  - Host object: GitHub pull request。
  - Authority boundary: 承接一个 primary Work Item 的实现 diff；多 Work Item 同 PR 时必须显式列出 additional Work Item links。
  - Locator / provenance: PR number、head branch、head SHA、required checks、review record、merge commit、linked issues。
  - Forbidden use: 不让 PR body、auto-close keyword 或 merged state 单独证明 Work Item completed。

层级与依赖规则：

- `Phase -> FR -> Work Item` 层级优先同步为 GitHub native parent/sub-issue。
- FR 间、Work Item 间、同 FR 内部子项之间的执行依赖优先同步为 GitHub native `blocked-by/blocks`。
- Project view、checklist、`tasks.md` 或外部 tracker 只能补充组织视图或 task carrier，不能替代 parent/sub-issue 与 `blocked-by/blocks`。
- 若 GitHub 原生关系暂时无法表达，issue comment 必须记录缺口、等价 locator 和重新同步条件。

Project `Status` 是宿主视图字段：

- `Todo`: 已规划或已加入 Project，但尚未进入正式执行现场。
- `In Progress`: 已有 active Work Item / owner / branch / worktree / PR，或明确处于执行中。
- `Done`: 只能作为 closeout 完成后的宿主视图状态；不能仅因 PR merged、issue closed、task checked 或 Project workflow 自动移动而视为 completed truth。

若 GitHub workflow 自动修改 Project `Status`，agent 必须重新核对 issue、PR、Work Item、recovery、review、merge-ready 和 closeout 证据。若 Project `Status` 与这些证据冲突，Loom truth carriers 与 closeout evidence 优先，Project item 需要回写或标记 drift。

## 5. strong governance 默认要求

GitHub host 下的 strong governance 默认要求：

- `Work Item` 是唯一默认执行入口
- 目标仓库 `release / version` 目标面只能映射 delivery chain，不得直接进入 execution
- `Phase -> FR -> Work Item -> PR -> merge commit` 绑定链可稳定读取
- formal spec 路径必须先过 `spec review`
- implementation review、`merge-ready`、`controlled merge`、`closeout` 强制消费前序 gate
- 统一状态面能直接暴露 stale / drift / gate failure
- closeout 必须消费 `reconciliation audit`
- 若仓库声明了目标 `release / version`，closeout 必须能区分 `merged but unreleased`、`released but unreconciled` 与 release evidence gap
- merge 默认走受控 PR 合入，默认方法为 `squash`

## 6. 三档 profile

### Light

- 只要求 `Work Item -> review -> merge-ready`
- 允许缺 formal spec 路径与强 closeout control plane

Light profile 从旧控制面迁移时使用两段式入口：

```bash
loom profile light-migration-plan --target . --json
loom profile light-migration-reconcile \
  --target . --repository OWNER/REPO --branch main --work-item ISSUE \
  --gate-pr PR --migration-pr PR --context CHECK --app-id APP_ID \
  --legacy-context OLD_CHECK --json
```

第二条命令默认只做 host readback 与计划；显式 `--apply` 才会先把新 delivery gate
加入 branch protection、readback 其 check/app identity，再移除声明的 legacy checks。
每次 GitHub API 写入尝试后都重新读取宿主状态，包括 transport timeout 或错误；
结果按 `applied / unchanged / indeterminate` 分类。多次写入不宣称原子，
`indeterminate` 或部分成功固定返回 `partial_apply`、不可为空的 mutation evidence
和包含同一 `--work-item` 的唯一恢复命令。相同 check context 必须只绑定预期
GitHub App；同 context 的冲突 app identity 在任何写入前阻断。
若 legacy check 由 ruleset 拥有，命令会在任何写入前阻断并要求先更新该 ruleset，
不会用 branch-only 变更伪造收敛。

迁移 PR 合并后，reconciliation 从 GitHub main tree 读取并验证 metadata-only
installed-state、`loom-repo-interface/v2` companion 内容、delivery workflow
执行合同，以及 workflow blob 与已验证 gate-enabler merge commit 的绑定；只存在
路径、空 companion 或 no-op workflow 都不能证明完成。gate-enabler check-runs
必须完整分页读取，不能以首页缺少目标 check 判断失败。
同一 required delivery gate 继续检查每个候选 tree，因此旧分支重新引入
`.loom/status/**` 等 carrier 时仍会被拒绝；这不依赖下游仓库迁移作为 Loom 完成条件。

### Standard

- 引入 `FR`、formal spec、`spec review`
- 引入统一状态读取面与基本 host binding

### Strong Governance

- 强制 `Work Item` enforcement
- 强制 host binding、gate chain、`controlled merge`
- 强制 closeout / reconciliation 一体化状态面
- 要求有 parity validation 证据

## 7. 与 adoption 的关系

- 默认升级顺序见 [github-profile-upgrade.md](./github-profile-upgrade.md)
- 成熟治理重仓的 attach-only 路径见 [deep-existing-repo-default.md](./deep-existing-repo-default.md)
- agent-assisted 低摩擦接入闭环见 [zero-friction-adoption-contract.md](./zero-friction-adoption-contract.md)

zero-friction adoption 可以帮助仓库进入 light 或 attach-only 起点，但不能跳过 `standard` 直接宣称 `strong`，也不能把 validation-only parity 自动升级为 blocking gate。

## 8. 非 GitHub 宿主

非 GitHub 宿主只要能提供相同语义，也可以实现 Loom。

Loom 冻结的是：

- 对象语义
- 绑定链
- gate chain
- 状态控制面
- closeout 语义

不是 GitHub 的产品细节。
