# Merge Checkpoint

本文件定义 Loom strong governance 下 `merge-ready` 的执行侧合同。

前序消费链见 [gate-chain.md](./gate-chain.md)。
受控合并合同见 [controlled-merge.md](./controlled-merge.md)。

## 1. 能力定位

`merge-ready` 是 `controlled merge` 之前的最终放行层。

它只回答三类问题：

- 当前前序 gate 是否已完整通过
- 当前 `head_sha` 是否仍在批准范围内
- 当前验证、review 与运行证据是否足以进入宿主 merge 控制面

它不承担第一次高质量语义判断，也不替代 `controlled merge` 的宿主校验。

## 2. 放行前必读输入

进入 `merge-ready` 前，至少应能读取：

- 当前 `Work Item`
- formal spec 路径上的 `spec_review`
- implementation review record
- 当前 `head_sha`
- host binding 中的 branch / PR / reviewed head
- 最近验证摘要
- 运行时证据或 `not_applicable`
- 风险与回滚边界
- 未决阻断项

## 3. 强前置消费纪律

`merge-ready` 必须强制消费：

- `Work Item admission`
- formal spec 路径上的 `spec gate`
- implementation review
- 当前 host binding

以下任一情况都必须 fail-closed：

- 缺 formal `spec_review`
- `spec_review` 未批准
- implementation review 不存在
- implementation review 为 `review_stale`
- 当前 `head_sha` 与 review / PR 绑定不一致
- 当前验证摘要与 review record 不一致

## 4. 唯一允许结果

`merge-ready` 只允许输出：

- `allow`
  - 可以进入 `controlled merge`
- `block`
  - 仍缺当前层必需输入
- `fallback`
  - 必须退回前序 gate 重做

其中：

- 前序 gate 缺失或 stale
  - 一律 `fallback`
- 当前层材料缺失但不必回退前序方向判断
  - `block`

## 5. 统一失败分类

`merge-ready` 只允许使用统一 taxonomy：

- `spec_stale`
- `review_stale`
- `head_drift`
- `binding_failure`
- `missing_prerequisite_gate`
- `evidence_failure`

不得输出私有名词，例如“基本可合”“小问题先过”。

## 6. 与 `controlled merge` 的边界

`merge-ready` 负责确认 Loom 自身前序链是否完整。
`controlled merge` 负责继续消费宿主 merge 控制面。

因此：

- required checks 是否全绿
  - 可在 `merge-ready` 预读，但正式阻断归 `controlled merge`
- merge method 是否符合当前 profile
  - 归 `controlled merge`
- merge 后的回链与 closeout
  - 归 `controlled merge` 与 `closeout`

## 7. 边界约束

- 不直接消费 engine raw output、prompt、日志或其他 evidence 文件
- 不跳过 review record 直接读取 reviewer 会话结论
- 不把 `merge-ready` 写成宿主按钮说明
- 不让当前层绕过前序 gate 缺口
