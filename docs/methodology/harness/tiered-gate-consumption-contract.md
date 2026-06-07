# Tiered Gate Consumption Contract

本文件定义 Loom gate 如何消费治理强度字段。

它承接 [loom-governance-intensity-mapping.md](../governance/loom-governance-intensity-mapping.md)
的 Loom 映射，并保护 [gate-chain.md](./gate-chain.md) 中的 fail-closed 顺序。

本文件只冻结合同，不实现 parser、CLI、fixture、runtime 或 `.loom/bin` 行为。

## 1. 消费目标

Gate 消费治理强度时必须回答：

- 当前变更声明的治理强度是什么
- formal suite 是 required、minimal 还是 `not_applicable`
- `not_applicable` 跳过了什么，为什么可以跳过，谁可以消费，何时失效
- review、fact-chain、CI/checks、PR gate、release / no-release 和 closeout 是否仍然必需
- 是否出现必须升级治理强度的信号

任何字段缺失、枚举未知、PR body machine carrier 解析失败、head SHA 不一致或
carrier 冲突，都必须 fail closed。

## 2. 最小字段

治理强度 machine carrier 至少需要以下字段。字段名是合同语义；具体载体由 #1321
实现，不在本文件落地 parser。

| 字段 | 允许值 | 必填条件 | 消费语义 |
| --- | --- | --- | --- |
| `loom_work_item` | 当前 Work Item id | 所有 Loom-governed PR | 绑定 PR metadata carrier 与 Work Item / issue 事实链 |
| `branch` | 当前 PR head branch | 所有 Loom-governed PR | 绑定 PR metadata carrier 与正式执行分支 / worktree |
| `head_sha` | 当前 PR head SHA | 所有 Loom-governed PR | 绑定 PR metadata carrier、review artifact 与 PR head |
| `governance_intensity` | `light` / `standard` / `reinforced` | 所有 Loom-governed PR | 决定最低证据、升级触发和 gate profile 期望 |
| `change_class` | `docs_only` / `docs_governance` / `contract` / `runtime` / `fixture` / `release` / `external_action` / `mixed` | 所有 Loom-governed PR | 解释为什么当前强度成立；高风险 class 不得降级 |
| `suite_path` | `full` / `minimal` / `not_applicable` | 所有 Work Item | 决定 full suite artifacts 是否必须可读 |
| `suite_not_applicable` | structured rationale object | `suite_path == not_applicable` | 证明 formal suite artifacts 仅对当前 scope 不适用 |
| `review_requirement` | `current_head_review_required` / `specialized_review_required` | 所有 Work Item | 保护 review 不被轻量路径跳过 |
| `fact_chain_required` | `true` | 所有 Work Item | 保护 Work Item、recovery、status、review locator 可读 |
| `pr_gate_required` | `true` | 所有 PR | 保护 PR head / Work Item / review / validation 绑定 |
| `release_judgment` | `release_required` / `no_release` / `deferred_release_judgment_blocking` | 所有 PR | 保护 release / no-release 判断 |
| `closeout_required` | `true` | 所有 Work Item | 保护 post-merge carrier 和 host sync |
| `upgrade_triggers` | list of trigger ids | 所有 Work Item | 记录当前已检查或已触发的升档信号 |

字段缺失时，gate 不能用默认值猜测通过。

## 3. `suite_path: not_applicable`

`suite_path: not_applicable` 只表示 formal suite artifacts 对当前 scope 不适用。
它不得跳过 review、fact-chain、CI/checks、PR gate、release / no-release 或 closeout。

`suite_not_applicable` 必须包含：

- `rationale`
- `consumer_boundary`
- `recheck_condition`
- `scope_proof`
- `review_requirement`

允许条件：

- 变更是 docs-only、docs-governance 语义冻结或其他不需要 formal suite artifacts 的局部合同
- scope proof 能证明 diff 未触碰 runtime、tools、fixtures、generated payload、skills 分发面、release mechanics、AGENTS 根规则或外部可见动作
- review record 会在当前 head 上消费该 rationale
- PR body 与 Work Item / recovery entry 指向同一 Work Item、branch、workspace 和 head SHA

阻断条件：

- rationale 为空或只写“文档变更”
- consumer boundary 没有说明哪些 gate 可以消费该判断
- recheck condition 没有说明 scope、risk、host state 或 evidence 变化如何使判断失效
- scope proof 无法用当前 diff、branch、PR head 或 carrier 证明
- review requirement 缺失或暗示无需 review
- 任何后续 gate 需要 formal suite evidence，但该 evidence 被静默省略

## 4. 不得跳过的 gate

所有强度都不得跳过：

- Work Item admission
- fact-chain / status-surface 消费
- current-head review 或明确的 specialized review
- PR metadata/readback 与 head binding
- hosted required checks 中适用部分
- PR gate
- release / no-release 判断
- controlled merge wrapper
- post-merge closeout / reconciliation

Gate 可以因为 `light` 或 `not_applicable` 缩小 suite artifact 面，但不能把
`not_applicable` 当成 review、CI、PR gate 或 closeout 的 substitute evidence。

## 5. Fail-closed 分类

Gate 至少要区分以下阻断原因：

- `governance_intensity_missing`
- `governance_intensity_invalid`
- `change_class_intensity_conflict`
- `suite_path_missing`
- `suite_path_invalid`
- `suite_not_applicable_missing`
- `suite_not_applicable_invalid`
- `review_requirement_missing`
- `fact_chain_binding_missing`
- `pr_metadata_parse_failed`
- `work_item_binding_conflict`
- `head_sha_mismatch`
- `release_judgment_missing`
- `closeout_requirement_missing`
- `upgrade_trigger_unresolved`

这些分类可以由后续实现扩展，但不得合并成不会阻断的 warning。

## 6. 升级规则

Gate 发现以下信号时必须要求升级或返回前序修复：

- `change_class` 是 `runtime`、`fixture`、`release`、`external_action` 或 `mixed`，但强度声明为 `light`
- docs-only 声明与 diff scope 不符
- PR body machine carrier 与 Work Item / recovery / status / review locator 冲突
- 当前 PR head 与 reviewed head 不一致，且漂移不是 gate 明确允许的 carrier-only drift
- release 判断缺失或与 scope 冲突
- downstream issue 依赖当前未冻结合同
- required hosted check、PR gate、controlled merge 或 closeout evidence 不可读

升级后的 gate 只能消费新的强度声明和对应证据；不能继续沿旧轻量路径放行。

## 7. 与后续实现的关系

本合同是 #1317 的冻结面。后续事项负责实现或验证：

- #1321：治理强度元数据载体
- #1322：docs-governance 轻量 gate 行为
- #1323：升级与滥用防护 fixtures
- #1324：文档与 release / no-release evidence 收口

在这些事项完成前，gate 必须按现有规则 fail closed，不得因为本文档存在就假设机器消费已经实现。

## 8. 一句话结论

分级 gate 消费可以让 Loom 区分 full suite 与合法 `not_applicable`，但任何轻量路径都不能绕过 review、事实链、head 绑定、CI、release 判断或 closeout。
