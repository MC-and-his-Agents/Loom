# Loom Review Input Signals

当任务满足以下任一信号时，进入 `loom-review`：

- 正式 review
- 语义审查
- 输出审查结论
- 输出 findings 和风险等级
- pre-review 通过后进入审查执行

最小输入：

- 目标仓库
- GitHub Work Item、PR 与 artifact locator
- review 意图与关注面（例如正确性、回归风险、合同一致性）
- review policy：`approved` 或明确允许的 `single_maintainer`
