# Templates

`templates/` 负责 Loom 的模板层。

它回答：

- 正式规约模板至少应长什么样
- PR 模板哪些信息应最小必填
- 哪些模板块应按条件触发

当前承接的条目：

- [spec-suite.md](./spec-suite.md)
  - `EXT-0015` `EXT-0016` `EXT-0017`
- [pull-request.md](./pull-request.md)
  - `EXT-0008` `EXT-0028`

当前目录中的核心文件，应优先表达最小模板约束，而不是只描述候选想法。

除规则文件外，当前还提供可直接投放的最小实体模板：

- [scaffold/spec.md](./scaffold/spec.md)
  - 对应 `spec-suite.md` 中定义的 `spec.md` 最小骨架
- [scaffold/plan.md](./scaffold/plan.md)
  - 对应 `spec-suite.md` 中定义的 `plan.md` 最小骨架

GitHub PR 的最小实体模板位于仓库根级：

- [../.github/PULL_REQUEST_TEMPLATE.md](../../../.github/PULL_REQUEST_TEMPLATE.md)
  - 对应 `pull-request.md` 中定义的基础必填块
