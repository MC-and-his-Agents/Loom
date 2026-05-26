# Delivery Planning

本文件定义 Loom 的 delivery planning 合同。

Delivery planning 是 `story / roadmap / product context / governance goal` 与正式执行之间的规划层。它回答一个目标应该拆成几个 `Phase`、几个 `FR`、几个 `Work Item`，以及后续是否需要 `PR plan`、issue tree、task carrier 或 host mapping。

它不替代 `Work Item`、`spec.md`、`plan.md`、recovery、review、merge-ready 或 closeout。

## 1. 适用场景

当输入目标存在以下任一信号时，应先进入 delivery planning：

- 目标跨多个 `Work Item` 或多个 PR。
- 目标需要拆成 `Phase / FR / Work Item` issue tree。
- 目标来自 roadmap、product discussion、story intake 或治理方向，但尚未确定执行边界。
- 目标需要判断哪些事项进入 full spec suite，哪些可以走 minimal path。
- 目标需要决定 GitHub issue、sub-issue、Project item、checklist、`tasks.md` 或外部 tracker 如何承接拆解结果。

不需要 delivery planning 的情况：

- 已有单一明确 `Work Item`，且 scope、branch、validation 与 closeout 条件都清楚。
- 纯机械小修，已有 owner、locator、验证命令和回滚边界。
- 只是在执行、review、merge-ready 或 closeout 当前 Work Item。

## 2. 输入

Delivery planning 可以消费以下输入，但不得把它们复制成第二事实源：

- Roadmap、Phase 或 release goal。
- User Story、Story Readiness 与 Story Business Confirmation locator。
- Product context、业务约束、治理目标或风险说明。
- 既有 `FR`、`Work Item`、PR、Project item 或外部 tracker。
- spec-kit / SDD 类外部方法论调研结果。
- 已存在的 Loom truth carriers，例如 `spec.md`、`plan.md`、recovery、review record、merge-ready record 或 closeout evidence。

每个输入必须记录 locator。若输入来自会话判断，应在输出中标为 `conversation locator` 或 `not_applicable rationale`，并在后续实现前落到正式 carrier。

## 3. 输出

Delivery planning 输出至少包含：

- `planning_goal`: 本次规划要收敛的目标。
- `input_locators`: 被消费的 story、roadmap、issue、PR、doc 或会话 locator。
- `phase_plan`: 是否需要新 Phase；若不需要，说明承接到哪个既有 Phase。
- `fr_plan`: 需要几个 FR，每个 FR 的职责边界、非目标和完成语义。
- `work_item_plan`: 每个 FR 下需要几个 Work Item，每个 Work Item 的执行边界、验证入口和 closeout 条件。
- `dependency_plan`: FR 间、Work Item 间、同 FR 内部子项之间的 `blocked-by/blocks` 关系。
- `pr_plan`: 哪些 Work Item 可进入同一 PR，哪些必须拆 PR，以及单 PR 多 Work Item 的证据要求。
- `host_mapping`: 哪些关系进入 GitHub native parent/sub-issue，哪些进入 blocked-by/blocks，哪些只进入 Project view、checklist、`tasks.md` 或外部 tracker。
- `path_selection`: full spec suite、minimal path、not_applicable 或 deferred 的选择理由。
- `provenance`: 谁/什么输入驱动了拆分判断，以及后续消费者应读取的权威 locator。
- `freshness_rule`: 什么时候规划结果会 stale，需要重新分析。

## 4. 权威边界

Delivery planning 是规划合同，不是执行状态。

允许它决定：

- 目标拆成哪些 `Phase / FR / Work Item`。
- 哪些依赖是阻塞关系，哪些只是顺序建议。
- 哪些 Work Item 可合并到同一 PR，哪些必须拆开。
- 哪些 host object 承接组织视图或 task carrier。

禁止它决定：

- 当前 Work Item 已完成。
- review、merge-ready 或 closeout 已通过。
- Project item `Done` 等于 Loom completed truth。
- PR merged 等于 closeout。
- checklist、`tasks.md` 或 Project Status 替代 Work Item。

## 5. 与正式工件的关系

Delivery planning 输出被后续工件消费：

- `issue-tree-plan` 消费 `phase_plan`、`fr_plan`、`work_item_plan` 与 `dependency_plan`。
- PR slicing 策略消费 `pr_plan`。
- GitHub profile 消费 `host_mapping`。
- `spec.md` 消费被选中的 FR / Work Item 边界，但不复制完整 planning 记录。
- `plan.md` 消费当前 Work Item 的执行计划，不重新拆 Phase / FR tree。
- Review、merge-ready 与 closeout 只把 planning 当作上游范围证据，不能把它当成通过结论。

## 6. 状态与 freshness

Delivery planning 结果在以下情况必须重新核对：

- 上游 story、roadmap、Phase 或 FR scope 改变。
- Work Item 被新增、删除、合并、拆分或 deferred。
- GitHub parent/sub-issue 或 blocked-by/blocks 关系与 planning 输出不一致。
- Project Status 与 issue / PR / Work Item / review / closeout evidence 冲突。
- 单 PR 多 Work Item 后新增了未覆盖的验证要求。

重新核对可以得出三类结论：

- `current`: 规划仍然可被消费。
- `stale`: 规划与当前事实不一致，必须更新。
- `superseded`: 规划已被后续正式 carrier 吸收，应回链新 locator。

## 7. 最小验证

完成 delivery planning 合同时，至少验证：

- 输出说明了输入、输出、适用场景和非目标。
- 输出明确不替代 `Work Item`、`spec.md`、`plan.md`、review、merge-ready 或 closeout。
- 输出能被 issue-tree plan、PR slicing 和 GitHub mapping 消费。
- 每个拆分判断都有 locator 或 provenance。
- 每个 host mapping 都说明 authority boundary 与 forbidden use。
