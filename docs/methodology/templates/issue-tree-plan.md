# Issue Tree Plan

本文件定义 Loom 的 issue-tree-plan 模板合同。

Issue-tree plan 是 delivery planning 的下游规划工件。它把一个已确认需要拆解的目标表达为 `Phase / FR / Work Item` 树、依赖关系、deferred / not_applicable 判断和 host carrier mapping。

它不承载执行进度、review 结论、merge-ready 结论或 closeout truth。

## 1. 适用场景

当 delivery planning 输出需要创建或核对 issue tree 时，应使用 issue-tree plan。

适用信号：

- 目标需要一个新的 Phase，或需要挂到既有 Phase。
- 一个目标需要拆成多个 FR 或多个 Work Item。
- Work Item 之间存在 `blocked-by/blocks` 关系。
- 部分事项需要标记为 `deferred` 或 `not_applicable`。
- GitHub issue、Project item、checklist、`tasks.md` 或外部 tracker 需要承接同一拆解结果。

不适用信号：

- 当前目标已经是单一明确 Work Item。
- 只是在执行、review、merge-ready 或 closeout 当前 Work Item。
- 只需要 PR slicing 判断；该策略由 PR slicing 合同消费 issue-tree plan 后决定。

## 2. 输入

Issue-tree plan 必须消费 delivery planning 输出，至少记录：

- `planning_goal` locator。
- 上游 story、roadmap、product context、Phase、FR 或 governance goal locator。
- 被消费的 delivery planning contract 或 planning record locator。
- 既有 GitHub parent/sub-issue、blocked-by/blocks、Project item 或 tracker locator。
- 当前 reuse / create / defer / not_applicable 判断的依据。

若输入来自会话判断，必须记录 `conversation locator`，并在执行前落到正式 issue、PR、doc 或 repo-local carrier。

## 3. 输出字段

Issue-tree plan 至少包含以下字段：

- `schema_marker`: `loom-issue-tree-plan/v1`。
- `planning_goal`: 本次 issue tree 要表达的目标。
- `input_locators`: 被消费的上游 locator。
- `phase_boundary`: 新建 Phase、复用既有 Phase 或不需要 Phase 的判断。
- `fr_list`: 每个 FR 的标题、职责边界、非目标、完成语义和 parent locator。
- `work_item_list`: 每个 Work Item 的执行边界、所属 FR、验证入口、closeout 条件和 owner expectation。
- `dependency_plan`: FR 间、Work Item 间、同 FR 内部子项之间的 `blocked-by/blocks` 规划关系。
- `deferred_items`: 被 deferred 的事项、原因、激活条件和不得当作 completed 的声明。
- `not_applicable_items`: 不适用事项、理由和后续重新判断条件。
- `host_carrier_mapping`: 哪些关系进入 GitHub native parent/sub-issue、哪些进入 blocked-by/blocks、哪些只进入 Project view、checklist、`tasks.md` 或外部 tracker。
- `pr_slicing_placeholder`: 哪些 Work Item 可能同 PR、哪些看起来需要拆 PR；最终规则由 PR slicing 合同决定。
- `freshness_rule`: 何时必须重新核对 issue tree。
- `consumer_contract`: 后续 spec、plan、PR slicing、GitHub mapping、review、merge-ready 和 closeout 如何消费本工件。

## 4. 权威边界

Issue-tree plan 允许表达：

- 目标应拆成哪些 `Phase / FR / Work Item`。
- 层级关系应如何进入 parent/sub-issue。
- 阻塞关系应如何进入 `blocked-by/blocks`。
- 哪些事项 deferred、not_applicable 或只进入 host carrier。
- 哪些 Work Item 是 PR slicing 的输入候选。

Issue-tree plan 禁止表达：

- 某个 Work Item 已完成。
- review、merge-ready 或 closeout 已通过。
- Project Status `Done` 等于 Loom completed truth。
- checklist、`tasks.md` 或 Project item 替代 Work Item。
- PR slicing 的最终合并规则；它只能提供 placeholder。

## 5. Deferred 与 Not Applicable

`deferred` 与 `not_applicable` 必须分开。

`deferred` 表示该事项仍可能属于目标，但当前不进入执行。必须记录：

- deferred item 标题或 locator。
- deferred 原因。
- 激活条件。
- 当前不阻塞哪些 Phase、FR 或 Work Item。
- 明确声明：closed deferred item 是 deferred，不是 completed。

`not_applicable` 表示该事项不属于当前目标。必须记录：

- not applicable item 标题或 locator。
- 不适用理由。
- 重新判断条件。
- 哪些后续消费者不得再要求它。

## 6. Host Carrier Mapping

Host carrier mapping 只描述承接方式，不改变 Loom truth。

默认映射规则：

- `Phase -> FR -> Work Item` 层级优先进入 GitHub native parent/sub-issue。
- 阻塞执行顺序进入 GitHub native `blocked-by/blocks`。
- Project Status 只表达视图状态，例如 Todo / In Progress / Done。
- checklist、`tasks.md` 或外部 tracker 只能作为 task carrier 或组织视图。
- 任何 host carrier 都不能替代 Work Item、recovery、review、merge-ready 或 closeout。

Issue-tree plan 只规划哪些 host object 承接拆解结果。进入 `plan.md` 执行后，具体 execution breakdown unit 的 task carrier 类型、状态、locator、provenance 与 `tasks.md` 替代关系由 [../harness/task-carrier-contract.md](../harness/task-carrier-contract.md) 约束。

## 7. Freshness

出现以下情况时，issue-tree plan 变为 stale，必须重新核对：

- delivery planning 目标改变。
- Phase、FR 或 Work Item 被新增、删除、合并、拆分或 deferred。
- parent/sub-issue 或 blocked-by/blocks 与 plan 不一致。
- Project Status 与 issue / PR / Work Item / review / closeout evidence 冲突。
- PR slicing 合同改变了 Work Item 与 PR 的承接方式。

## 8. 消费关系

- `spec.md` 只消费当前 Work Item 或 FR 边界，不复制完整 issue-tree plan。
- `plan.md` 只消费当前 Work Item 的执行计划，不重新拆树。
- execution breakdown 消费 `plan.md` 的 phase / validation strategy，并把执行单元映射到 task carrier；它不反向重定义 issue-tree plan。
- PR slicing 合同消费 `work_item_list` 与 `pr_slicing_placeholder`。
- GitHub mapping 合同消费 `host_carrier_mapping`。
- Review、merge-ready 和 closeout 只把 issue-tree plan 当作上游范围证据，不能把它当作通过结论。

## 9. 最小验证

完成 issue-tree-plan 模板时，至少验证：

- 模板包含 phase boundary、FR list、Work Item list、dependencies、deferred/not_applicable 和 host carrier mapping。
- 模板能表达 blocked-by / blocks 的规划关系。
- 模板明确不承载执行进度、review 结论、merge-ready 或 closeout。
- 模板能被 PR slicing 和 GitHub mapping 消费。
- 模板没有硬编码当前仓库的具体 issue 编号作为 Loom 默认。
