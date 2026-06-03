# Host Issue Binding

本文件冻结 Loom strong governance 默认消费的统一 host binding contract。

它解决的问题不是“某个脚本怎样猜当前 PR”，而是“所有 review / merge-ready / controlled merge / closeout 应该消费同一套绑定语义”。

## 1. 目标

Loom 必须能稳定回答：

- 当前执行锚点是谁
- 该事项绑定了哪些 host objects
- 这些绑定是否仍然指向同一条交付链
- merge 后能否从 `Work Item` 追溯到 PR、merge commit 与 closeout basis

## 2. 统一绑定锚点

统一锚点固定为当前 `Work Item`。

在 formal planning 层：

- `FR`
  - 负责 requirement / formal spec 容器
- `Work Item`
  - 负责执行、review、merge 与 closeout

因此：

- `FR` 可以为 `Work Item` 提供上位边界
- `FR` 不能直接替代当前执行锚点
- PR、branch、`head_sha`、merge commit 都必须最终回链到当前 `Work Item`

## 3. 最小绑定对象组

当事项进入正式执行链后，Loom 至少要能读取以下绑定：

- `Work Item -> FR`（若存在 formal spec 路径）
- `Work Item -> host branch`
- `Work Item -> git worktree`
- `Work Item -> host PR`
- `Work Item -> current head_sha`
- `Work Item -> review authority boundary`
- `PR -> reviewed head_sha`
- `PR -> semantic review disposition`
- `PR -> merge commit`
- `merge commit -> target branch`

GitHub profile 下，这些对象通常由 issue、sub-issue、PR、branch 与 merge commit 承接；Loom 冻结的是关系语义，不是 GitHub 私有字段名。

## 4. 统一读取规则

所有正式 gate 只允许消费同一 binding surface：

- implementation review
  - 消费 `Work Item`、当前 `head_sha`、关联 PR、review authority boundary
- `merge-ready`
  - 消费 `Work Item -> PR -> reviewed head_sha -> semantic review disposition`
- `controlled merge`
  - 消费 `Work Item -> PR -> reviewed head_sha -> semantic review disposition -> merge commit`
- `closeout`
  - 消费 `Work Item -> PR -> merge commit -> target branch`

任何入口都不得再用局部约定重建第二套绑定规则。

## 5. GitHub strong governance 默认绑定链

GitHub host 下默认要求至少能证明：

- `FR -> Work Item`
- `Work Item -> implementation PR`
- `implementation PR -> merge commit`
- `merge commit -> default branch`

若当前事项是 docs-only closeout、formal spec closeout 或 parent closeout，仍然必须绑定当前 `Work Item`，不得回退到 `FR` 直接承接 PR。

## 6. 单 PR 吸收多事项

单个 PR 可以吸收多个 `Work Item`，但必须显式可证明。

最小要求：

- 当前 PR 关联的 `Work Item` 列表可稳定读取
- 每个 `Work Item` 都能分别判断是否已被该 merge commit 覆盖
- parent / child 不能因共享同一 PR 就自动一起 `closed_out`

默认结论：

- `absorbed`
  - 可以按事项分别成立
- `closed_out`
  - 必须按事项分别判断

## 7. 绑定失败分类

以下情况必须进入统一 taxonomy，而不是留给调用方自由解释：

- `binding_failure`
  - 必需绑定缺失、冲突或无法证明
- `head_drift`
  - 当前受审 `head_sha` 与绑定链不一致
- `review_authority_drift`
  - 当前 PR head、reviewed head 与 authored semantic review disposition 无法证明属于同一条交付链
- `host_signal_drift`
  - PR、merge commit、主干或宿主状态互相冲突
- `merge_signal_drift`
  - merge 后回链不完整，无法进入 closeout

## 8. 边界约束

- 本文件不接管 host branch / PR / merge 的底层生命周期动作
- 本文件不把 GitHub 字段名提升为 Loom core 唯一术语
- 本文件不把 `absorbed` 直接等同于 `closed_out`
- 本文件不允许 `FR`、PR 或 merge commit 越权替代 `Work Item`
- repo companion、guardian、PR comment、CI check 或 host review comment 只能提供 mirror / evidence；
  它们不得替代 `Work Item -> PR -> reviewed head_sha -> semantic_review_disposition`
  这条通用绑定链
