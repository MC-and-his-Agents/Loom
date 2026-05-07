# Status Surface Contract

本文件冻结 Loom `status control plane v2` 的统一读取合同。

它回答的不是“状态写在哪”，而是“resume / review / merge-ready / closeout 至少要从同一个控制面读出哪些治理现场”。

状态控制面是 derived surface。它必须展示 provenance 与阻断原因，但不得新增第二套 authored truth。

## 1. 目标

`status control plane v2` 至少要同时服务：

- `loom-resume`
- `loom-spec-review`
- `loom-review`
- `loom-merge-ready`
- `controlled merge`
- `closeout`
- repo-local `loom_status`
- host-backed GitHub 状态消费

它不新增 authored 真相，只统一读取已有真相与 host signals。

读取顺序固定为：

1. repo-authored truth
   - `Work Item`、恢复主入口、review record、merge / closeout basis
2. host / control-plane mirror
   - issue、project、PR、checks、ruleset、host binding
3. retained result
   - guardian、integration、repo-native verdict、host action result envelope
4. derived status surface
   - 汇总展示、taxonomy、最终 `pass | block`

状态面只能把第 2、3 层作为 mirror / evidence / locator provenance 消费，不能把它们提升为第 1 层。
第 4 层是本次状态面的输出 / 展示层，不是生成当前状态面时可反读的输入。旧状态面最多用于 stale-surface 检测，不能作为当前 `pass | block` 的来源。

## 2. 统一读取对象

统一状态面至少必须能读出：

- 当前 `Work Item`
- 当前 gate 链位置
- checkpoint / recovery 状态
- `spec_review`
- implementation review
- `merge-ready`
- `controlled_merge`
- `closeout`
- 活跃 failures taxonomy
- host binding
- GitHub control plane signals

## 3. 字段组 v2

### 3.1 `item`

至少包含：

- `id`
- `goal`
- `scope`
- `execution_path`
- `fr_ref`
- `workspace_entry`
- `recovery_entry`
- `review_entry`
- `validation_entry`

### 3.2 `checkpoint`

至少包含：

- `raw`
- `normalized`
- `current_gate`
- `next_gate`

### 3.3 `recovery`

至少包含：

- `current_stop`
- `next_step`
- `blockers`
- `latest_validation_summary`
- `recovery_boundary`
- `current_lane`

### 3.4 `execution_ledger`

至少包含：

- `authoritative_carrier`
- `authoritative_path`
- `completeness`
- `freshness`
- `fields`
  - `ledger_binding`
  - `plan_locator`
  - `acceptance_locator`
  - `validation_evidence_locator`
  - `handoff_notes_locator`
  - `evidence_freshness`
- `missing_fields`
- `forbidden_authored_fields`

该字段组只展示 recovery-bound ledger 的派生结论。它不得 authored `next_step`、`blockers` 或 `latest_validation_summary`。

### 3.5 `gates`

固定包含：

- `spec_review`
- `implementation_review`
- `merge_ready`
- `controlled_merge`
- `closeout`

每个 gate 至少表达：

- `status`
- `decision_ref`
- `reviewed_head` 或等价 head 绑定
- `consumed_prerequisites`
- `blocking_failures`

### 3.6 `binding`

至少包含：

- `work_item_ref`
- `fr_ref`
- `branch_ref`
- `pr_ref`
- `head_sha`
- `reviewed_head_sha`
- `merge_commit_sha`
- `target_branch`

### 3.7 `taxonomy`

至少包含：

- `active_failures`
- `stale`
- `drift`
- `gate_failures`

### 3.8 `github`

至少包含：

- `issue`
- `parent_issue`
- `sub_issues`
- `pr`
- `required_checks`
- `mergeability`
- `branch_protection`
- `project`

### 3.8 `provenance`

每个会影响 `pass | block` 的字段组至少要能暴露：

- `source_layer`
  - `authored_truth | host_control_mirror | retained_result | derived_surface`
- `source_locator`
- `source_binding`
- `freshness`
  - `fresh | stale | missing | unreadable | not_applicable`
- `conflict`
  - `none | drift | stale_surface | stale_retained_result | parallel_truth`

`provenance` 是读取说明，不是新的 authored 字段组。它可以在 JSON 输出中按字段内联，也可以作为并列索引输出，但必须能被机械入口追溯到具体字段。
若一个字段组混合消费多个来源，provenance 必须能下钻到字段级，不能用组级 provenance 掩盖局部 stale / drift。

## 4. 总结果语义

统一状态控制面本身只允许输出：

- `pass`
- `block`

判定原则：

- 只要存在活跃 `stale` / `drift` / `gate_failure`，结果就是 `block`
- 只要缺前序 gate 或绑定链不完整，结果就是 `block`
- 只要关键字段缺少 provenance、provenance 指向不可读来源，或同一事实出现 parallel truth，结果就是 `block`
- retained result 与 producing command / action、target gate / surface、subject locator、当前 `HEAD`、范围、恢复摘要或 gate 前置不匹配时，结果就是 `block`
- 只有关键读面全部可消费且前序链完整时，结果才是 `pass`

## 5. closeout / reconciliation 一体化要求

`closeout` 与 `reconciliation` 不得再是状态面外的口头补充。

v2 必须至少能稳定读出：

- `absorbed_but_open`
- `parent_drift`
- `project_drift`
- `merge_signal_drift`
- 当前事项是否已经 `absorbed`
- 当前事项是否已满足 `closed_out` basis

## 6. repo-local 与 host-backed 边界

- repo-local 路径可以只依赖 `.loom/` 与本地 git
- host-backed 路径可以额外消费 issue / PR / project / branch protection / required checks
- 两条路径必须输出同一套字段组与 taxonomy
- host-backed 路径输出的 GitHub 值是 host/control-plane mirror；repo-local 路径可以缓存其 locator 或 retained result，但不得把缓存值当成 authored truth

## 7. 非目标

- 不把状态面升级成第二套 authored 账本
- 不允许不同 skill 各自拼装私有状态结构
- 不把 GitHub 私有字段直接冻结为 Loom core 唯一命名
- 不用 `runtime_state` 代替 status control plane
