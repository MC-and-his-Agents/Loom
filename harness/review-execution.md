# Review Execution

本文件定义 Loom 当前最小正式 review 执行层。

## 1. 能力定位

Loom 把 review 分成三层：

- `pre-review`
  - 机械预检，判断是否具备进入正式审查的最低条件
- `review`
  - 正式语义审查，输出 reviewer 结论
- `merge-ready`
  - merge 前统一放行聚合

`review` 不替代前后两层，也不把语义判断硬编码成脚本。

## 2. 唯一 review 载体

正式 review 结论必须落在唯一 `review_entry` 指向的 review record。

默认入口：

- `python3 tools/loom_flow.py flow review --target <repo> [--item <id>]`
- `python3 tools/loom_flow.py review record --target <repo> [--item <id>] --decision <allow|block|fallback> --kind <general_review|code_review|spec_review> --summary <text> --reviewer <id>`

其中：

- `review record` 仍只写入单一 `review_entry` 指向的 JSON
- 结构化审查结论可通过 `--findings-file <path>` 写入同一 review record
- `--blocking-issue` / `--follow-up` 只保留兼容 authored 入口，不得与 `--findings-file` 混用

## 3. review record 最小字段

review record 至少应包含：

- `item_id`
- `kind`
- `reviewed_head`
- `reviewed_validation_summary`
- `decision`
- `summary`
- `reviewer`
- `fallback_to`
- `findings`
- `blocking_issues`
- `follow_ups`

模板见 [../templates/review-record.md](../templates/review-record.md)。

其中：

- `findings` 是正式审查结论的权威数组
- 每条 finding 至少应包含 `summary`、`severity`、`disposition`
- `severity` 当前稳定值为 `warn`、`fix-needed`、`block`
- `disposition` 当前稳定值为 `blocking_issue`、`follow_up`
- `blocking_issues` / `follow_ups` 只是从 `findings` 投影出的兼容字段，不构成第二真相源

## 4. 与 merge checkpoint 的边界

`merge checkpoint` 固定只做机械消费：

- 读取 `work item.review_entry`
- 校验 `item_id` 是否匹配当前事项
- 校验 `reviewed_head` 是否仍匹配当前 `HEAD`
- 校验 `reviewed_validation_summary` 是否仍匹配当前 recovery 的 `latest_validation_summary`
- `decision: allow` 才算 review 已通过
- `decision: block` 返回 `block`
- `decision: fallback` 按 `fallback_to` 返回 `fallback`
- 如需读取阻断或后续事项，只能优先消费同一 review record 内的 `findings`

## 5. 非目标

- 不把 review 结论写回 recovery entry 或 status surface
- 不让 PR 模板充当正式 review 真相
- 不让 merge-ready 替代正式 review
- 不为 rebuttal / disposition 再创建第二份 review artifact 或新状态机
