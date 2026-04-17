# Review Record

正式 review record 至少应表达：

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

允许结果：

- `allow`
- `block`
- `fallback`

约束：

- `fallback_to` 只在 `decision: fallback` 时使用
- `reviewed_head` 与 `reviewed_validation_summary` 必须对应本次审查基线
- `findings` 是权威 findings / disposition 数组；每条至少包含 `summary`、`severity`、`disposition`
- `severity` 当前稳定值为 `warn`、`fix-needed`、`block`
- `disposition` 当前稳定值为 `blocking_issue`、`follow_up`
- `blocking_issues` / `follow_ups` 仅作为兼容字段保留，默认从 `findings` 投影，不应被当作独立 authored 真相
- review record 是 merge checkpoint 的正式输入之一，不得只留在会话或 PR 评论里
