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
- `blocking_issues`
- `follow_ups`

允许结果：

- `allow`
- `block`
- `fallback`

约束：

- `fallback_to` 只在 `decision: fallback` 时使用
- `reviewed_head` 与 `reviewed_validation_summary` 必须对应本次审查基线
- review record 是 merge checkpoint 的正式输入之一，不得只留在会话或 PR 评论里
