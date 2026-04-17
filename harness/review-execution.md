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
- `blocking_issues`
- `follow_ups`

模板见 [../templates/review-record.md](../templates/review-record.md)。

## 4. 与 merge checkpoint 的边界

`merge checkpoint` 固定只做机械消费：

- 读取 `work item.review_entry`
- 校验 `item_id` 是否匹配当前事项
- 校验 `reviewed_head` 是否仍匹配当前 `HEAD`
- 校验 `reviewed_validation_summary` 是否仍匹配当前 recovery 的 `latest_validation_summary`
- `decision: allow` 才算 review 已通过
- `decision: block` 返回 `block`
- `decision: fallback` 按 `fallback_to` 返回 `fallback`

## 5. 非目标

- 不把 review 结论写回 recovery entry 或 status surface
- 不让 PR 模板充当正式 review 真相
- 不让 merge-ready 替代正式 review
