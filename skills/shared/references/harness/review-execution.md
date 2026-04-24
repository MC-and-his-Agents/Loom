# Review Execution

本文件定义 Loom 当前最小正式 review 执行层。

## 1. 能力定位

Loom 把 review 分成四层：

- `spec gate`
  - formal spec 路径的通过 / 阻断结果
- `pre-review`
  - 机械预检，判断是否具备进入正式审查的最低条件
- `review gate`
  - 正式语义审查，输出 reviewer 结论
- `merge gate`
  - merge 前统一放行聚合

`review gate` 不替代前后两层，也不把语义判断硬编码成脚本。
默认开箱即用路径固定为：

1. `flow review`
   - 只读基线；确认是否具备进入 formal review 的条件
2. `review run`
   - 调用默认 Codex-backed reviewer，产出结构化 review evidence 与 Loom-normalized findings
3. `review record`
   - 把 formal review 结论写入单一 authored review record

## 2. 唯一 review 载体

正式 review 结论必须落在唯一 `review_entry` 指向的 review record。

默认入口：

- `python3 skills/loom-review/scripts/loom-review.py flow review --target <repo> [--item <id>]`
- `python3 skills/shared/scripts/loom_flow.py review run --target <repo> [--item <id>]`
- `python3 skills/shared/scripts/loom_flow.py review record --target <repo> [--item <id>] --decision <allow|block|fallback> --kind <general_review|code_review|spec_review> --summary <text> --reviewer <id>`

其中：

- `flow review` 固定保持只读，不触发 engine，也不产生副作用
- `review run` 只负责运行默认 reviewer、落盘 evidence、生成 normalized findings，并显式 fail-closed
- `review record` 仍只写入单一 `review_entry` 指向的 JSON
- 结构化审查结论可通过 `--findings-file <path>` 写入同一 review record
- `--blocking-issue` / `--follow-up` 只保留兼容 authored 入口，不得与 `--findings-file` 混用

默认 engine 当前固定为 Codex。
若 engine 不可用、schema 漂移、runtime 冲突或运行后改动了 tracked repo 内容，`review run` 必须返回 `block`，并指向 manual review 继续写回同一 `review record`；不得把这类失败伪装成 gate fallback。

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
- 每条 finding 至少应包含 `id`、`summary`、`severity`、`rebuttal`、`disposition`
- `severity` 当前稳定值为 `warn`、`block`
- `rebuttal` 当前稳定值为 `null` 或非空字符串
- `disposition` 当前稳定值为 `null` 或对象；对象内的 `status` 只允许 `accepted`、`rejected`、`deferred`
- `blocking_issues` / `follow_ups` 只是从 `findings` 投影出的兼容字段，不构成第二真相源
- `consumed_inputs.engine_adapter`、`consumed_inputs.engine_evidence`、`consumed_inputs.normalized_findings`
  - 只记录 evidence 来源，不构成第二 authored truth

## 4. 与 gate chain 的边界

`review gate` 固定只做机械消费：

- 读取 `work item.review_entry`
- 校验 `item_id` 是否匹配当前事项
- 校验 `reviewed_head` 是否仍匹配当前 `HEAD`
  - 若 `HEAD` 在 review 之后只新增了 Loom 自身的 review / recovery / status carriers 提交，允许继续消费
  - 一旦 `HEAD` 还包含其他路径漂移，仍按 review stale 处理
- 校验 `reviewed_validation_summary` 是否仍匹配当前 recovery 的 `latest_validation_summary`
- `decision: allow` 才算 review gate 已通过
- `decision: block` 返回 `block`
- `decision: fallback` 按 `fallback_to` 返回 `fallback`
- 如需读取阻断或后续事项，只能优先消费同一 review record 内的 `findings`

它不得直接消费 engine raw output、prompt、日志或其他 evidence 文件。

`merge gate` 进一步只消费通过后的 review record 与宿主控制面，不再重做实现审查。

## 5. 非目标

- 不把 review 结论写回 recovery entry 或 `status control plane`
- 不让 PR 模板充当正式 review 真相
- 不让 `merge gate` 替代正式 review
- 不为 rebuttal / disposition 再创建第二份 review artifact 或新状态机
- 不把 Loom 扩写成 multi-engine marketplace
