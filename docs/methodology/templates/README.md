# Templates

`templates/` 负责 Loom 的模板层。

它回答：

- 正式规约模板至少应长什么样
- PR 模板哪些信息应最小必填
- 哪些模板块应按条件触发

当前承接的条目：

- [spec-suite.md](./spec-suite.md)
  - `EXT-0015` `EXT-0016` `EXT-0017`
- [delivery-planning.md](./delivery-planning.md)
  - `#1014` `#1024`
- [issue-tree-plan.md](./issue-tree-plan.md)
  - `#1014` `#1025`
- [execution-breakdown.md](./execution-breakdown.md)
  - `#1017` `#1037`
- [pr-slicing.md](./pr-slicing.md)
  - `#1014` `#1026`
- [spec-template.md](./spec-template.md)
  - `#290`
- [implementation-contract-template.md](./implementation-contract-template.md)
  - `#290`
- [pull-request.md](./pull-request.md)
  - `EXT-0008` `EXT-0028`
- [release-closeout-template.md](./release-closeout-template.md)
  - `#693`
- [default-governance-scaffold-policy.md](./default-governance-scaffold-policy.md)
  - `#819`

当前目录中的核心文件，应优先表达最小模板约束，而不是只描述候选想法。

默认治理 scaffold 的主落点是 [default-governance-scaffold-policy.md](./default-governance-scaffold-policy.md)。其他 adoption / companion 文档只能引用它定义的 action 与 locator 边界，不得各自复制一套默认模板 truth。

除规则文件外，当前还提供可直接投放的最小实体模板：

- [scaffold/spec.md](./scaffold/spec.md)
  - 对应 `spec-suite.md` 中定义的 `spec.md` 最小骨架
- [scaffold/plan.md](./scaffold/plan.md)
  - 对应 `spec-suite.md` 中定义的 `plan.md` 最小骨架
- [scaffold/full-suite-index.md](./scaffold/full-suite-index.md)
  - 对应 `spec-suite.md` 中定义的 full suite index、path decision、artifact inventory 与 #1020 接入需求记录
- [scaffold/research.md](./scaffold/research.md)
  - 对应 `spec-suite.md` 中定义的 full suite 条件 research 工件
- [scaffold/contracts.md](./scaffold/contracts.md)
  - 对应 `spec-suite.md` 中定义的 full suite 条件 contracts 工件
- [scaffold/readiness-checklist.md](./scaffold/readiness-checklist.md)
  - 对应 `spec-suite.md` 中定义的 full suite 条件 readiness checklist 工件
- [scaffold/user-story.md](./scaffold/user-story.md)
  - 对应 `story-intake.md` 中定义的 story intake 最小骨架；其中 User Story、Story Readiness、Story Business Confirmation 与 Delivery Consumption Boundary 是分离产物
- [scaffold/issue-tree-plan.md](./scaffold/issue-tree-plan.md)
  - 对应 `issue-tree-plan.md` 中定义的 issue tree planning 最小骨架
- [scaffold/pr-slicing.md](./scaffold/pr-slicing.md)
  - 对应 `pr-slicing.md` 中定义的 PR slicing 最小骨架
- [scaffold/release-closeout.md](./scaffold/release-closeout.md)
  - 对应 `release-closeout-template.md` 中定义的 target release closeout 最小骨架

GitHub PR 的最小实体模板位于仓库根级：

- [../.github/PULL_REQUEST_TEMPLATE.md](../../../.github/PULL_REQUEST_TEMPLATE.md)
  - 对应 `pull-request.md` 中定义的基础必填块
