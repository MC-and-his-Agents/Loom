# Status Surface

本文件定义 Loom `status control plane v2` 的字段语义与读取纪律。

统一对象组见 [status-surface-contract.md](./status-surface-contract.md)。
失败分类见 [governance-failure-taxonomy.md](./governance-failure-taxonomy.md)。

## 1. 能力定位

状态面用于在单一读面里暴露当前治理现场。

它至少应回答：

- 当前是谁在执行
- 当前走到哪一个 gate
- 前序 gate 是否可继续消费
- 当前有哪些 `stale` / `drift` / `gate_failure`
- merge 与 closeout 是否已有足够 basis
- 当前 behavior evidence / test evidence 是否覆盖当前范围
- 最近验证是否仍是 fresh verification evidence

状态面不是 runtime state，也不是 runtime evidence ledger。它只消费这些来源并给出当前可读的 derived control-plane 结论。

## 2. 字段派生原则

所有字段都必须从既有主真相或 host signals 派生：

- `item`
  - 从 `Work Item` 派生
- `checkpoint`、`recovery`
  - 从恢复主入口派生
- `gates.spec_review`、`gates.implementation_review`
  - 从 review records 派生
- `gates.merge_ready`
  - 从 merge checkpoint 派生
- `gates.controlled_merge`
  - 从受控合并输出与 host merge signals 派生
- `gates.closeout`
  - 从 closeout / reconciliation 结果派生
- `binding`
  - 从 host binding surface 派生
- `github`
  - 从 host / control-plane mirror 派生
- retained host / repo-native result
  - 作为 evidence provenance 或 gate 前置结果派生
- `taxonomy`
  - 从统一失败分类派生

禁止手工维护第二套 authored 状态摘要。

每个影响放行的派生值必须保留来源说明：

- 来源层级
  - authored truth、host/control-plane mirror、retained result 或 derived surface
- 来源 locator
- 与当前 `item_id`、`HEAD`、范围、reviewed head、PR 或 merge commit 的绑定
- fresh / stale / missing / unreadable / not_applicable 判断

缺少上述来源说明时，该字段不可消费。
混合来源的字段组必须能下钻到字段级 provenance，不能用组级 provenance 掩盖局部 stale / drift。

行为证据与测试证据也只能派生读取：

- `behavior_evidence`
  - 从 spec 场景、验证记录、review record 与运行证据 locator 派生
- `test_evidence`
  - 从 plan 测试策略、自动检查、人工验证记录与验证摘要派生
- `fresh_verification_evidence`
  - 从当前 `HEAD`、当前范围、当前恢复摘要与最近验证记录的绑定关系派生

状态面可以展示这些字段，但不得在状态面内 authored 第二份结论。

Dynamic tool availability 也只能派生读取：

- `tool_availability`
  - 从 repo companion 的 `dynamic_tool_locators` 与只读 handshake declaration 派生
  - 展示 `advertised | unavailable | unsupported | failed`
  - required 工具失败可阻断对应 execution surface；optional / advisory 工具失败只作为 advisory evidence
  - 不调用工具、不写 host result、不替代 `execution_attempt`

Approval / sandbox policy 也只能派生读取：

- `policy_readiness`
  - 从 repo companion 的 `policy_locators` 与只读 policy declaration 派生
  - 展示 approval policy、sandbox policy 与 risk summary
  - required policy 的 `missing` / `conflict` / `unsafe` 可阻断对应 execution surface；optional / advisory policy risk 只作为 review input
  - 不申请权限、不修改 sandbox、不替代宿主权限系统

## 3. 必备展示面

统一状态面至少要展示：

- 当前 `Work Item`
- 当前 gate 与下一 gate
- 当前恢复停点
- formal spec 路径是否需要 `spec_review`
- implementation review 是否 stale
- `merge-ready` 是否受前序 gate 阻断
- `controlled merge` 是否满足宿主条件
- `closeout` / `reconciliation` 是否存在 drift
- 当前活跃 failures 列表
- BDD 外环场景的证据覆盖状态
- TDD 内环测试或等价检查的证据覆盖状态
- fresh verification evidence 的 `head_sha` / 范围 / 摘要绑定
- execution_budget 报告（`status` 为 `not_applicable`/`unavailable` 时不阻断）
- 最近 execution failure 分类（只作风险输入）
- retry evidence 摘要
- dynamic tool availability 与 failure summary
- approval / sandbox policy 与 risk summary

## 4. execution_budget

状态面在 `execution_budget` 字段组里展示 provider-neutral 预算快照：

- `schema_version`: `loom-execution-budget/v1`
- `status`: `present` / `not_applicable` / `unavailable`
- `enforcement`: `advisory`
- `summary`
- `dimensions`
  - 每项允许的 `id`：`turns`、`tokens`、`requests`、`retries`、`time_window`
  - 每项固定字段：`unit`、`used`、`limit`、`remaining`、`risk`、`source`
- `provenance`
- `adapter_evidence_locator`

`status` 为 `not_applicable` 或 `unavailable` 时仍为 advisory 证据，不得作为 merge-ready 的缺失输入 blocking 条件。

## 4.1 execution_failure

状态面可以从最近一次 `execution_attempt` 派生 `execution_failure`，用于暴露 `stall`、`timeout`、`retry_exhaustion` 等执行风险。该字段只读 runtime evidence，不创建 scheduler state，也不单独阻断 merge。

## 4.2 retry_evidence

状态面可以从 `.loom/runtime/attempts/<item-id>/` 的 attempt chain 派生 `retry_evidence`，用于暴露 attempt_count、retry_count、stale_attempt_count 与 exhausted 信号。该字段只读 runtime evidence，不声明 scheduler state。

## 4. `Runtime Evidence`

若事项涉及运行面，状态面必须继续提供固定区块 `Runtime Evidence`：

- `Run Entry`
- `Logs Entry`
- `Diagnostics Entry`
- `Verification Entry`
- `Lane Entry`

字段值只能是：

- locator
- `not_applicable`

字段缺失永远是错误，不等同于不适用。

## 4.1 `runtime_state` / `runtime_evidence` / status control plane

三者职责固定区分：

- `runtime_state`
  - 描述 Loom runtime / launcher / carrier 是否可运行、当前入口属于什么安装场景、缺少什么运行输入，以及 lane、run、logs、diagnostics 的 locator 或宿主运行对象状态
  - 可以阻断命令启动
  - 不承载事项进度、recovery state、validation verdict、review 结论、merge-ready 结论或 closeout 结论
- `runtime_evidence`
  - 描述已经被验证或审查消费的运行证据及其绑定，证明 run / logs / diagnostics / verification / lane 证据在哪里
  - 不承载下一步、当前停点、blocking owner 或最终 gate verdict
- status control plane
  - 汇总 authored truth、host mirror、retained result 与 runtime evidence，输出 `pass | block`、taxonomy 与 provenance
  - 不反向写入 runtime_state，也不把 runtime_state 当成事项状态面

若 runtime_state 与 runtime_evidence 的绑定不一致，状态面必须把相关 evidence 标记为 `stale` 或 `unreadable`。若调用方试图用 runtime_state 代替恢复主入口或 status control plane，必须视为 parallel truth 风险并阻断。
`runtime_evidence` 的 `present`、`not_applicable`、`stale`、`missing` 结论仍由状态面或 fact-chain 根据当前 `HEAD`、范围与恢复摘要派生；`Runtime Evidence` 区块本身只提供 locator 读面。

## 4.2 行为 / 测试证据展示

状态面展示行为证据与测试证据时，至少应区分：

- `present`
  - 当前证据存在，且绑定当前 `HEAD`、范围与恢复摘要
- `stale`
  - 证据存在，但不再覆盖当前受审对象
- `missing`
  - 当前 gate 必需的证据不存在
- `not_applicable`
  - 当前事项不涉及对应证据类型，且原因与 spec / plan / recovery 不冲突

`fresh verification evidence` 只能由 `present` 且绑定当前对象的 behavior evidence / test evidence 组合派生。
若验证结果来自较早 `HEAD`、较早范围、过时恢复摘要，或来自未整合的 subagent 输出，状态面必须显示为 `stale` 或 `missing`，不得显示为 fresh。

## 5. Execution Ledger 派生展示

状态面可以展示 execution ledger 的派生结论，但不得 authored ledger 字段。

可展示字段限于：

- `ledger_locator`
- `ledger_completeness`
- `ledger_freshness`
- `ledger_conflict`

这些结论必须来自 fact-chain 对 recovery 主入口的解析。若 ledger 缺失、stale、绑定到第二 locator，或 authored recovery forbidden fields，状态面和 `loom_status` 都必须输出 blocking / stale 结论，而不是用状态面内容覆盖 recovery。

## 6. Latest Execution Attempt

状态面可以展示最近一次 `execution_attempt`，但只能作为 runtime evidence 读取。

- fresh attempt 必须满足 [execution-attempt.md](./execution-attempt.md) 的 envelope 合同、绑定当前 `item_id` 与当前 `HEAD`，且不包含 authored progress 字段
- stale attempt 可以展示 `attempt_id`、`result` 与 locator，但必须标为 `freshness: stale`
- missing 或 unreadable attempt evidence 必须标为 `missing` 或 `invalid`，不得用 flow 输出里的摘要补写第二真相
- attempt 的 `result` 不等于当前 gate 通过；gate 仍消费 Work Item、recovery、review、merge-ready 与 closeout 主载体

## 7. gate 可消费判定

状态面必须明确区分：

- `gate 已存在`
- `gate 已通过`
- `gate 结论 stale`
- `gate 因前序缺失不可消费`
- `gate 结论缺少 provenance`
- `gate 结论来自过期 retained result`

例如：

- formal spec 路径存在，但 `spec_review` 未批准
  - `gates.spec_review.status = block`
  - `taxonomy.active_failures` 必须含 `missing_prerequisite_gate`
- implementation review 已存在，但 `reviewed_head` 过时
  - `gates.implementation_review.status = block`
  - `taxonomy.active_failures` 必须含 `review_stale`
- behavior evidence / test evidence 缺失或 stale
  - 对应消费 gate 必须 `block`
  - `taxonomy.active_failures` 必须含 `evidence_failure`
- host mirror 与 authored truth 不一致
  - 对应消费 gate 必须 `block`
  - `taxonomy.active_failures` 必须含 `drift`
- retained result 绑定过期、来源不可读或缺少 producing command / action、target gate / surface、subject locator 等关键 provenance
  - 对应消费 gate 必须 `block`
  - `taxonomy.active_failures` 必须含 `stale` 或 `gate_failure`

## 6. closeout / reconciliation 展示

状态面必须把以下结论直接暴露出来，而不是要求调用方另查：

- 当前事项是否 `absorbed`
- 当前事项是否已经 `closed_out`
- 是否存在 `absorbed_but_open`
- 是否存在 `parent_drift`
- 是否存在 `project_drift`
- 是否存在 `merge_signal_drift`

## 7. 当前统一入口

当前仓库中的统一读取入口包括：

- `python3 tools/loom_status.py --target <repo> [--item <id>]`
- `python3 tools/loom_flow.py reconciliation audit --target <repo> ...`
- `python3 tools/loom_flow.py closeout check --target <repo> ...`

这些入口应输出同一控制面语义，而不是平行结果模型。

输出纪律：

- repo-local 与 host-backed 输出字段组保持一致
- host-backed 额外值必须标记为 host/control-plane mirror
- retained result 必须标记原始 result envelope 或等价 locator
- derived summary 不得遮蔽 authored truth 与 mirror 的冲突
- 任一关键来源不可读、过期或冲突时输出 `block`

## 8. 非目标

- 不把状态面写成新的长期进度账本
- 不用状态面覆盖 `Work Item` / review record / merge checkpoint / closeout basis 的原始权威位置
- 不允许调用方只读局部字段就跳过前序 gate
- 不把 runtime_state、runtime_evidence 或 host mirror 改造成事项 authored truth
