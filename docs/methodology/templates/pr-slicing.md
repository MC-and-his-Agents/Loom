# PR Slicing

本文件定义 Loom 的 PR slicing 合同。

PR slicing 是 delivery planning 和 issue-tree plan 之后的承接策略。它回答：哪些 `Work Item` 可以进入同一个 implementation PR，哪些必须拆成不同 PR，以及单 PR 承接多个 `Work Item` 时必须保留哪些证据。

它不替代 `Work Item`、recovery、review、merge-ready 或 closeout truth。PR 是 host control carrier，不是 Loom 的完成事实源。

## 1. 适用场景

当 issue-tree plan 或执行准备阶段出现以下任一信号时，应做 PR slicing 判断：

- 一个 FR 下有多个 `Work Item`，且看起来可能由同一个改动批次完成。
- 多个 `Work Item` 修改同一批文件、同一接口或同一验证面。
- 一个 `Work Item` 的输出必须先被另一个 `Work Item` 消费。
- 一个目标需要判断是单 PR 收敛，还是拆成多 PR 降低 review 风险。
- PR body、review evidence、merge-ready evidence 或 closeout comment 需要回链多个 issue。

不需要 PR slicing 的情况：

- 当前目标已经是单一明确 `Work Item`，且 PR 只服务该 Work Item。
- 只是在 review、merge-ready、controlled merge 或 closeout 当前 PR。
- 只是在规划 Phase / FR / Work Item tree；该职责属于 delivery planning 和 issue-tree plan。

## 2. 输入

PR slicing 必须消费以下输入，并记录 locator：

- delivery planning 的 `pr_plan`。
- issue-tree plan 的 `work_item_list`、`dependency_plan` 和 `pr_slicing_placeholder`。
- 相关 `Work Item` 的 scope、non-goals、validation entry 和 closeout condition。
- GitHub parent/sub-issue、blocked-by/blocks 与 Project Status。
- PR template、PR body metadata 要求、review gate、merge-ready gate 和 closeout 规则。
- 既有多 Work Item 同 PR 的历史证据；历史只能作为参考，不能成为默认规则。

## 3. 输出字段

PR slicing 输出至少包含以下字段：

- `schema_marker`: `loom-pr-slicing/v1`。
- `slicing_goal`: 本次要判断的 PR 承接范围。
- `input_locators`: 被消费的 planning、issue、PR、doc 或 conversation locator。
- `candidate_work_items`: 候选 `Work Item` 列表、parent FR、scope 和验证入口。
- `dependency_read`: 候选项之间是 blocking dependency、sequencing only，还是 independent。
- `same_pr_decision`: `single_pr | split_pr | defer_decision | not_applicable`。
- `same_pr_conditions`: 若允许同 PR，必须满足的边界和证据条件。
- `split_pr_conditions`: 必须拆 PR 的触发条件。
- `primary_work_item`: 当前 PR gate 需要一个主 `Work Item` 时的绑定项。
- `additional_work_item_links`: 同 PR 承接的其他 `Work Item` 及其 closeout 处理方式。
- `pr_body_contract`: PR body 如何回链 issue、spec/plan、validation 和 follow-up。
- `review_risk`: review 风险判断、所需 reviewer 视角和风险降级方式。
- `validation_matrix`: 每个 `Work Item` 对应的验证证据。
- `merge_ready_consumption`: merge-ready 如何确认 PR head、review record、validation summary 和 issue 回链一致。
- `closeout_consumption`: closeout 如何逐个消费 PR、merge commit、Project Status 和 issue comment。
- `freshness_rule`: 什么时候 PR slicing 结果 stale。

## 4. Same PR 条件

多个 `Work Item` 可以进入同一 PR，必须同时满足：

- 它们服务同一个 parent FR，或 issue-tree plan 明确记录了跨 FR 同 PR 的理由。
- scope 可以被一个清晰 PR summary 说明，不需要把多个不相关目标塞进同一 review。
- 依赖关系不会制造不可审查的顺序风险；如果 A blocks B，同 PR 必须说明 B 只消费 A 在同一 diff 中已经稳定的合同。
- 每个 `Work Item` 的 validation entry 都能在同一 PR head 上被覆盖。
- PR body 明确列出 primary `Work Item` 和 additional `Work Item`，不能只写一个 issue。
- review record 明确消费所有被同 PR 承接的 `Work Item` scope，不允许只 review 主 issue。
- merge-ready evidence 能证明当前 PR head、review record、validation summary 和 issue 回链一致。
- closeout 必须逐个 `Work Item` 写明 PR、head SHA、merge commit、Project Status 和剩余 downstream。

## 5. 必须拆 PR 的条件

出现以下任一情况时，默认拆 PR：

- 候选项属于不同 FR，且没有明确的跨 FR 同 PR rationale。
- 一个 `Work Item` 的输出需要先独立 review、merge 或 closeout，另一个才能安全开始。
- 候选项触及不同风险域，例如行为变更、gate 逻辑、host adapter、release/publish、权限、数据或安全边界。
- 候选项需要不同 reviewer 视角，合在一起会降低 review 精度。
- 验证矩阵不能在同一 PR head 上清楚证明每个 `Work Item`。
- 任一候选项仍是 deferred、not_applicable 待确认，或 scope 不稳定。
- 合并后无法逐个 issue 做 closeout，或 Project Status 会和 Loom truth carriers 冲突。
- 单 PR 会迫使 PR gate、merge-ready 或 closeout 读取自由 Markdown 推断事实。

## 6. Primary Work Item 与 additional links

当宿主 PR gate 只能读取一个 `Loom Work Item` 字段时：

- `primary_work_item` 是 PR gate 的主绑定项。
- 其他同 PR 承接项必须进入 `additional_work_item_links`，并在 PR body、review record 和 closeout comment 中显式列出。
- additional item 不能只靠 GitHub auto-close 语义完成；closeout 必须逐项消费 merge commit 与 Project Status。
- 如果 gate、review 或 closeout 无法稳定消费 additional item，必须拆 PR。

## 7. 与 PR body 的关系

PR body 是 host 展示和绑定面。

必须包含：

- primary `Loom Work Item`。
- related issue / FR / Phase locator。
- spec / plan locator。
- validation summary。
- additional `Work Item` links，如果存在。
- risks and follow-ups。

不得包含：

- review verdict 作为 authority。
- merge-ready verdict 作为 authority。
- closeout result 作为 authority。
- 从自由 Markdown 推断出的 machine truth。

若 repo-specific metadata 需要被机器读取，必须使用 repo companion 合同中的 PR body HTML comment JSON machine carrier，而不是自由 Markdown。

## 8. Review 与 merge-ready 消费

Review 必须确认：

- PR scope 是否匹配 slicing decision。
- 每个被承接 `Work Item` 的 non-goals 没有被越界实现。
- validation matrix 是否覆盖所有被承接项。
- additional item 是否有独立 closeout 路径。

Merge-ready 必须确认：

- PR head SHA 与 review record 一致。
- validation summary 与 recovery/status 中的最新证据一致。
- PR body 的 primary/additional issue 回链完整。
- GitHub required checks 已通过。
- Project Status 不与 issue state、review、merge-ready 或 closeout truth 冲突。

## 9. Closeout 消费

单 PR 承接多个 `Work Item` 时，closeout 必须逐项记录：

- `Work Item` issue locator。
- PR locator。
- PR head SHA。
- merge commit。
- delivered artifact locator。
- validation evidence。
- Project Status。
- downstream 或 deferred/not_applicable 判断。

父 FR 只能在所有 required child `Work Item` 都 closed 或明确 deferred 且非阻塞时关闭。

## 10. Freshness

PR slicing 结果在以下情况 stale：

- issue-tree plan 的 Work Item list、dependency plan 或 PR slicing placeholder 改变。
- 任一候选 `Work Item` scope、validation entry 或 closeout condition 改变。
- blocked-by/blocks 关系改变。
- Project Status 与 issue / PR / review / closeout evidence 冲突。
- PR head 引入未被 slicing decision 覆盖的新 scope。
- gate chain 开始支持或停止支持多 Work Item machine binding。

## 11. 最小验证

完成 PR slicing 合同时，至少验证：

- 文档明确 same PR 条件和必须拆 PR 条件。
- 文档明确 primary `Work Item`、additional links、PR body、review evidence、merge-ready evidence 和 closeout 的关系。
- 文档明确 PR 是 host carrier，不替代 Loom truth。
- 文档说明单 PR 多 `Work Item` 必须有逐项证据回链。
- 文档没有实现 PR gate、merge-ready 或 GitHub mapping 逻辑。
