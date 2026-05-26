# Merge Checkpoint

本文件定义 Loom strong governance 下 `merge-ready` 的执行侧合同。

前序消费链见 [gate-chain.md](./gate-chain.md)。
受控合并合同见 [controlled-merge.md](./controlled-merge.md)。
PR-specific host enforcement bridge 见 [pr-merge-gate.md](./pr-merge-gate.md)。
Governance lint taxonomy 见 [governance-lint-taxonomy.md](./governance-lint-taxonomy.md)。

## 1. 能力定位

`merge-ready` 是 `controlled merge` 之前的最终放行层。

它只回答三类问题：

- 当前前序 gate 是否已完整通过
- 当前 `head_sha` 是否仍在批准范围内
- 当前验证、review 与运行证据是否足以进入宿主 merge 控制面
- 当前 behavior evidence / test evidence 是否仍是 fresh verification evidence

它不承担第一次高质量语义判断，也不替代 `controlled merge` 的宿主校验。

## 2. 放行前必读输入

进入 `merge-ready` 前，至少应能读取：

- 当前 `Work Item`
- formal spec 路径上的 `spec_review`
- suite path decision
- full suite artifact locators，或 minimal path `not_applicable` rationale
- evidence-map locator、scope、freshness 与 `head_sha` 绑定
- consistency-analysis locator、classification 与 remediation direction
- implementation review record
- 当前 `head_sha`
- host binding 中的 branch / PR / reviewed head
- 最近验证摘要
- behavior evidence
- test evidence
- fresh verification evidence 的 `head_sha` / 范围 / 恢复摘要绑定
- 运行时证据或 `not_applicable`
- `budget_risk` 摘要
- governance lint result 摘要
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
- full path 必需 suite 工件缺失、不可读、stale，或 provenance 缺失
- minimal path 的 `not_applicable` rationale 缺失、不可读、与 spec / plan /
  recovery 冲突，或 recheck condition 已触发但未重新判断
- evidence-map 缺失、不可读，或未覆盖当前 `head_sha`、当前范围、当前恢复摘要
- consistency-analysis 缺失、不可读，或输出 blocking consistency gap
- implementation review 不存在
- implementation review 为 `review_stale`
- 当前 `head_sha` 与 review / PR 绑定不一致
- 当前验证摘要与 review record 不一致
- behavior evidence 或 test evidence 缺失且没有有效 `not_applicable`
- evidence 存在但不覆盖当前 `head_sha`、当前范围或当前恢复摘要
- review record 中存在未处理的 `block` finding、未闭合的 accepted disposition，或无后续承接的 deferred disposition
- review record 消费的 full suite、evidence-map 或 consistency-analysis backlink
  与当前 `head_sha` / scope / validation summary 不一致
- repeated blocker / root-cause escalation 尚未回到前序 gate 处理
  - 回到 review record / 前序 gate / ownership 分配修正点
- core governance lint 存在 blocking result，且映射到当前 `merge-ready` 必需前置
- repo-specific lint 在 repo companion 中声明为 `merge_ready` blocking，且 result 仍为 fresh blocking

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
- `consistency_gap`

不得输出私有名词，例如“基本可合”“小问题先过”。

`evidence_failure` 至少覆盖：

- 缺少 behavior evidence
- 缺少 test evidence
- 缺少 fresh verification evidence
- 证据只存在于未整合的 subagent 输出中
- review disposition 指向的补救、拒绝理由或延期事项缺少可消费证据

`consistency_gap` 至少覆盖：

- scenario / acceptance mapping 缺失且没有合法 `not_applicable`
- evidence-map 与 review record、validation summary、current `HEAD` 或 host PR
  binding 冲突
- consistency-analysis 标记 blocking gap
- stale evidence 被后序 CI success 或 host checks 误当成 fresh evidence
- host state conflict，例如 PR head、reviewed head、merge-ready head 或 branch
  binding 互相不一致
- deferred-as-completed，即 deferred work、accepted finding 或 unresolved carrier
  被当成当前 Work Item 已完成

`not_applicable` 只在同时具备 rationale、consumer boundary、recheck
condition、source locator，并且与 spec / plan / recovery 不冲突时可以被
merge-ready 消费。否则必须按 `missing_prerequisite_gate` 或
`evidence_failure` fail closed。

`budget_risk` 在 `merge-ready` 中只作为 advisory evidence：

- `high` 风险必须进入 merge-ready 输出摘要，提醒 reviewer / recovery / host merge 消费方
- 不得把 advisory budget 加入 `missing_inputs`
- 不得因为 budget-only 风险把 `result` 从 `pass` 改成 `block` 或 `fallback`

Governance lint 在 `merge-ready` 中的消费纪律：

- `approval_bypass`、`host_binding_drift`、`evidence_stale`、`fact_chain_broken` 可阻断 `merge-ready`
- `core_hardcoding_leak` 和 `companion_boundary_bypass` 若影响当前放行输入，也必须阻断并回到对应边界修复
- advisory lint result 必须进入摘要，但不得单独把结果改为 `block` 或 `fallback`
- repo-specific lint 只有在 repo companion 声明 `surface: merge_ready` 且 enforcement 为 `blocking` 或 requirement 为 `required` 时才能阻断
- lint result 缺少 provenance、`HEAD`、scope、reviewed head 或 evidence freshness 绑定时，不得被当作 fresh verification evidence

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
- 不把 raw review、shadow evidence、CI 成功或 PR body 摘要当成 semantic approval
- 不跳过 review record 直接读取 reviewer 会话结论
- 不把 `merge-ready` 写成宿主按钮说明
- 不让当前层绕过前序 gate 缺口
- 不把旧验证、未绑定当前 `HEAD` 的测试结果或未整合的 subagent 输出当作 fresh verification evidence
- 不把 full suite / evidence-map / consistency-analysis 的 blocking gap 当作
  advisory warning
- 不用 PR checks、required checks 或 CI success 覆盖 stale evidence、head drift
  或 missing predecessor gate
- 不把 repo-specific lint 规则、guardian 名称、CI job 名或仓库目录名硬编码成 Loom core merge-ready 条件
