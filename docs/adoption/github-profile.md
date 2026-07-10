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

### 按需 FR → Work Item admission

FR 在规划态可以没有 Work Item；只有它要进入 branch、build、PR、ship 或 completed/closeout 语义时，才必须先取得 `admitted` Work Item。

- `loom route --target <repo> --issue <fr> --task <scope> --json` 只读地给出最小 proposal；只有显式 `--apply` 才会创建或补齐原生 GitHub child 与声明的 `--blocked-by` 关系。
- apply 是可重入 reconciliation，不宣称 GitHub 多次 API 写入是原子事务。中途失败返回 `partial_apply`、已创建的 typed locator 与包含 `--work-item` 的恢复动作；恢复必须复用该 Work Item，不能按标题猜测或重复创建。
- admission 只消费 GitHub issue type、native parent/sub-issue、native dependency 与 host readback；不得写入 `.loom` current、progress、shadow、review ledger、手写 head 或 closeout carrier。
- 未拆分 FR 的执行意图返回 `needs_breakdown`；`duplicate`、`invalid`、`cancelled`、`superseded`、`deferred` 与 `not planned` 只能表示非完成例外，不能伪装为 completed。
- PR binding 与 FR/Phase close guard 是后续消费者：implementation PR 的 primary issue 必须是 `work_item`，而不是 FR 或 Phase。

GitHub task carrier 边界：

- GitHub issue / sub-issue 可以作为 execution breakdown unit 的 `github_issue` carrier，但只有被明确 author 为 `Work Item` 的 issue 才能进入正式执行。
- Project item 可以作为 `github_project_item` carrier，只提供视图、排序、筛选和 normalized status。
- Issue / PR / Markdown checklist 可以作为 `checklist_item` carrier，只表示局部步骤追踪。
- Repo-local `tasks.md` 可以作为 `repo_tasks_md` carrier，但不是 GitHub profile 或 Loom core 的必选工件。
- 外部 tracker 可以作为 `external_tracker` carrier；GitHub profile 只消费其 locator 和 provenance。
- Carrier state 必须映射到 `pending`、`in_progress`、`done`、`blocked`、`deferred` 或 `not_applicable`，并回链 `Work Item`、breakdown unit、spec scenario、plan phase 与 validation strategy。
- Carrier `done`、Project `Done`、checklist checked、issue closed 或 PR merged 都不等于 behavior evidence、test evidence、review pass、merge-ready pass 或 closeout。

GitHub task carrier profile：

| Host object | Carrier type | Allowed use | Required locator / provenance | Forbidden use |
| --- | --- | --- | --- | --- |
| Work Item issue | `github_issue` with `relationship: primary` only when the issue is authored as the Work Item | 承接当前 Work Item 的 scope、workspace entry、branch、PR、review、merge-ready、merge commit 和 closeout 回链 | issue number、parent FR、branch、正式 worktree、PR、head SHA、closeout comment、Project item if present | 不被 sub-issue、Project item、checklist、`tasks.md` 或 PR body Markdown 替代 |
| Sub-issue that is not the Work Item | `github_issue` with `relationship: primary` or `mirror` for a breakdown unit | 承接 execution breakdown unit 的讨论、局部阻断、局部状态和回链 | sub-issue number、parent issue、breakdown unit locator、source issue state、normalized status、creating or syncing comment | 不进入正式执行链；不替代 Work Item、recovery、review、merge-ready 或 closeout truth |
| Project item | `github_project_item` with `relationship: mirror` | 承接视图、排序、筛选、队列和 normalized status | Project number、item id、Status field source value、sync time 或 host event locator | 不替代 issue state、Work Item、review verdict、merge-ready result、closeout basis 或 evidence freshness |
| Issue / PR checklist item | `checklist_item` | 承接轻量步骤、人工确认 locator 或局部 ownership 标记 | containing issue / PR locator、checklist item text or anchor、checked state、sync comment if used as evidence locator | checked 不等于 behavior evidence、test evidence、review pass、merge-ready pass 或 closeout |
| Repo-local `tasks.md` | `repo_tasks_md` | 承接 repo-local task list、breakdown unit 到 carrier 的对照和 subagent ownership | repo-relative path、line or stable anchor、unit id、source commit or head SHA | 不是 GitHub profile 必选工件；不 authored recovery dynamic fields、gate state 或 closeout result |
| External tracker linked from GitHub | `external_tracker` | 承接 GitHub 外部组织系统中的 task locator 和 mirror status | external URL or id、linked issue / comment、source value、normalized status、freshness rule | GitHub profile 只消费 locator 与 provenance，不把外部状态提升为 Loom truth |
| No carrier needed | `not_applicable` | 当前 unit 不需要 GitHub carrier，或 minimal path 合法跳过 carrier | rationale、consumer boundary、recheck condition、owning Work Item locator | 不用静默缺失伪装成合法跳过 |

状态规范化规则：

- GitHub open issue 默认只能映射为 `pending` 或 `in_progress`，取决于是否已有 active Work Item / owner / branch / worktree / PR 或明确执行评论。
- GitHub closed issue 可以映射为 carrier `done`，但若该 issue 是 Work Item，仍必须有 closeout evidence 才能被 closeout 消费。
- GitHub blocked-by / blocking comment、label 或原生关系可以映射为 carrier `blocked`，但必须回链 blocker locator 或 recovery entry。
- `deferred` 必须有 follow-up locator、activation condition 和不得作为 completed 消费的声明。
- `not_applicable` 必须有 rationale、consumer boundary 和 recheck condition；没有这些字段的缺口是 `missing`。

Project `Status` 是宿主视图字段：

- `Todo`: 已规划或已加入 Project，但尚未进入正式执行现场。
- `In Progress`: 已有 active Work Item / owner / branch / worktree / PR，或明确处于执行中。
- `Done`: 只能作为 closeout 完成后的宿主视图状态；不能仅因 PR merged、issue closed、task checked 或 Project workflow 自动移动而视为 completed truth。

Host agent 读取或更新 Project `Status` 时必须先消费同一 Work Item 的 issue、PR、merge commit、recovery、review、merge-ready 和 closeout locators。若 GitHub workflow 自动修改 Project `Status`，agent 必须重新核对 issue、PR、Work Item、recovery、review、merge-ready、closeout 和 evidence-map freshness。若 Project `Status` 与这些证据冲突，Loom truth carriers 与 closeout evidence 优先，Project item 需要回写或标记 drift；冲突不得被下游 review、merge-ready 或 closeout 当作 advisory-only 状态展示。

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

### Capability enforcement

GitHub profile 中的 governance capability 只能用两种 enforcement profile 表达：

- `host-enforced`：GitHub branch protection、ruleset、required checks、PR merge policy 或等价宿主控制面已被 verified host read 证明正在强制执行。
- `advisory/local-enforced`：本地脚本、repo-local alias、非 required workflow、人工约定、shadow parity 或报告型检查。该 profile 必须带 `risk_label: low_assurance`，并声明 fallback / rollback；它不能计入 strong governance maturity。

`release`、`security`、`payment`、`data_migration` capability 默认必须保持 `host-enforced`。降级到 `advisory/local-enforced` 需要显式批准和版本控制内证据，并且只作为临时 rollout 状态，不作为 strong maturity 证据。

PR metadata、merge evidence、release evidence 与 closeout evidence 必须记录 governance mode。`advisory/local-enforced` 记录必须同时写出 `low_assurance` 风险标签和未宿主强制状态；readback/status 不得把该状态渲染成 `host-enforced` 或 strong governance。若 release / security / payment / data migration 事项缺少显式降级批准，gate 必须 fail closed。

### Semantic review 与 checks 边界

GitHub required checks、非 required triggered checks、guardian、integration、advisory verdict、GitHub review comment 和 CI-only signal 都不能替代 Loom semantic review。strong governance 的合并放行必须消费同一 PR head 上的 authored Loom review record、`pr gate`、`merge check` 和 host readback；checks 只能证明执行/宿主状态，不能自行成为 approval truth。

`SKIPPED` / `NEUTRAL` triggered checks 可以作为 allowed non-success readback 进入 controlled merge JSON；failed、cancelled、timed out、action required、startup failure、unknown、pending、queued、in progress 或 unreadable triggered checks 必须 fail closed。

## 6. 三档 profile

### Light

- 只要求 `Work Item -> review -> merge-ready`
- 允许缺 formal spec 路径与强 closeout control plane

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
