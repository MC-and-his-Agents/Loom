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
- `taxonomy`
  - 从统一失败分类派生

禁止手工维护第二套 authored 状态摘要。

行为证据与测试证据也只能派生读取：

- `behavior_evidence`
  - 从 spec 场景、验证记录、review record 与运行证据 locator 派生
- `test_evidence`
  - 从 plan 测试策略、自动检查、人工验证记录与验证摘要派生
- `fresh_verification_evidence`
  - 从当前 `HEAD`、当前范围、当前恢复摘要与最近验证记录的绑定关系派生

状态面可以展示这些字段，但不得在状态面内 authored 第二份结论。

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

## 4.1 行为 / 测试证据展示

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

## 5. gate 可消费判定

状态面必须明确区分：

- `gate 已存在`
- `gate 已通过`
- `gate 结论 stale`
- `gate 因前序缺失不可消费`

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

## 8. 非目标

- 不把状态面写成新的长期进度账本
- 不用状态面覆盖 `Work Item` / review record / merge checkpoint / closeout basis 的原始权威位置
- 不允许调用方只读局部字段就跳过前序 gate
