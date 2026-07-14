# Controlled Merge

本文件定义 Loom strong governance 下的受控合并合同。

## 1. 目标

`controlled merge` 负责把 `merge-ready` 之后的宿主控制面读取、merge 方法约束、merge 后回链与 closeout 衔接收成一条正式链路。

它回答四件事：

- 当前 PR 是否满足宿主 merge 控制面
- 允许使用哪种 merge 方法
- merge 后如何回链 `Work Item -> PR -> merge commit -> main`
- merge 后如何把结果交给 `closeout` 与 `reconciliation`

## 2. 必需输入

进入 `controlled merge` 前，至少应能读取：

- PR-specific `pr merge gate` 已通过，见 [pr-merge-gate.md](./pr-merge-gate.md)
- `merge-ready` 已通过
- 可选 retained `pr-gate` result locator
- 可选 retained `merge-gate` / `merge-ready` result locator
- 当前 `Work Item` 与 PR 绑定
- 当前 PR 的 `head_sha`
- required checks / branch protection or active ruleset / triggered check rollup / mergeability
- 允许的 merge method
- 目标基线分支

其中 `loom-pr-merge-gate` 的宿主强制面可以来自两类权威读面之一：

- branch protection 的 required status checks
- active ruleset 暴露的 required status checks context

## 3. GitHub strong governance 默认值

GitHub profile 的 strong governance 默认要求：

- 禁止直推主干
- 必须通过 PR 合入
- PR 必须绑定单一当前 `Work Item`
- required checks 必须全部通过
- merge 前不得处于 draft
- 默认 merge method 为 `squash`
- merge 后必须能读取 merge commit

若仓库采用非默认 merge method，必须在 profile 中显式声明，不能靠口头默认值。

## 4. 绑定链

`controlled merge` 必须能稳定证明：

- `Work Item -> branch`
- `Work Item -> PR`
- `PR -> reviewed head`
- `PR -> merge commit`
- `merge commit -> target branch`

若其中任一关系缺失或冲突，必须返回 `binding_failure` 或 `host_signal_drift`。

## 5. merge 前阻断

以下情况至少要直接阻断：

- `pr merge gate` 未通过，或无法证明当前 PR head 已有 fresh authored review approval
- `merge-ready` 未通过
- implementation review 或 `spec_review` 已 stale
- PR `head_sha` 与受审 `head_sha` 不一致
- required checks 未全绿
- 当前 PR head 上已触发的非 required check 出现 failed、pending、unknown 或 unreadable 状态
- merge method 与当前 profile 不一致
- branch protection 或 active ruleset 仍禁止当前 merge 行为
- branch protection 与 active ruleset 读面都不可用，无法证明 `pr merge gate` 是宿主强制 check
- host mergeability 为 `DIRTY` 或 `DRAFT`

只要 branch protection 或 active ruleset 其中之一仍能证明 `loom-pr-merge-gate` 是当前 PR 的 required context，`controlled merge` 就必须把它消费为有效 host enforcement；不得额外要求另一侧读面也同时声明该 context。

GitHub `mergeStateStatus == BLOCKED` 是粗粒度宿主策略信号，不自动等价于 Loom semantic readiness 失败。若 fresh authored review approval、`loom-pr-merge-gate` required 且成功、required checks 全绿、PR head 无 drift、branch protection / ruleset readback 可解释，`controlled merge` 可以把 `BLOCKED` 作为 drift-only readback evidence 继续进入 host merge delegation；最终是否能合入仍由 `gh pr merge` 的宿主返回承接并记录。`BLOCKED` 不能替代 authored review approval，也不能让 raw guardian、GitHub review comment 或 CI 成为 approval truth。

## 6. retained gate result 消费

`controlled merge` 可以消费 retained `pr-gate` / `merge-gate` result locator，但只能把它们当作前序 gate 的 retained result，不得把它们提升为新的 approval truth。

公共默认路径的 retained `pr-gate` result 必须由以下命令产生完整 JSON，并写入 repo-relative、ignored 的 workstation file：

```bash
loom pr gate <pr> \
  --work-item <owner/repo/work_item/id> \
  --attestation-artifact-input <attestation-artifact.json> \
  --full-output --json
```

该 result 必须满足：

- schema 为 `loom-delivery-gate-readback/v1`；raw `loom-delivery-gate/v1` workflow evaluator JSON 必须拒绝
- `result == pass`
- PR number、Work Item、PR head SHA 与当前 PR 读面一致
- hosted check 名称为 `loom-delivery-gate` 且 completed/success
- host review attestation 的 Work Item、PR number 与 head SHA 仍绑定当前 PR

retained `merge-gate` result 必须满足：

- 来源为 `flow merge-ready` 或 `checkpoint merge`
- `result == pass`
- Work Item 与 retained `pr-gate` 一致
- merge checkpoint 为 pass
- 若暴露 validation summary，必须与 retained `pr-gate.review_approval.reviewed_validation_summary` 一致

消费 retained result 后，`controlled merge` 只补做 drift-only readback：

- current PR head
- required checks status
- triggered checks status
- branch protection / active ruleset 是否要求 `loom-pr-merge-gate`
- host mergeability
- merge method

任一 identity、head、validation、required check、triggered check、branch protection / ruleset、hard-block mergeability 或 merge method drift 都必须 `block`，或回到 `pr-gate` / `merge-ready` / `review`。hard-block mergeability 只包括 `DIRTY` 与 `DRAFT`；`BLOCKED` 必须解释为 host policy signal，只有在 Loom gate 与 host readback 其余条件均已通过时才可继续进入受控宿主委托。retained result 不能替代 host enforcement readback，也不能让 raw review / shadow evidence 成为 approval truth。

最小回归 fixture 固定在 `python3 tools/check_cli_contract.py --surface controlled-merge`：它验证 branch protection 未要求 `loom-pr-merge-gate` 时，只要 active ruleset 仍把该 context 标成 required，`controlled-merge check` 也必须继续通过。

## 7. triggered checks 读面

required checks 是宿主 branch protection / ruleset 声明的硬门禁读面；triggered checks 是当前 PR head 上已经运行或排队的 check rollup 读面。`controlled merge` 必须同时消费两者。

当 required checks 全绿但 triggered check rollup 中存在 failed、cancelled、timed out、action required、startup failure、pending、queued、in progress、unknown 或 unreadable 状态时，`controlled merge` 必须 fail closed。`SUCCESS` 可以放行；`SKIPPED` 和 `NEUTRAL` 可以放行，但必须在 JSON snapshot 中明确分类，不能静默当作 success。

## 8. merge 后交接

merge 成功后，`controlled merge` 必须输出最小交接 basis 给 `closeout`：

- 当前 `Work Item`
- PR 编号与 URL
- merged `head_sha`
- merge commit SHA
- 目标主干分支
- merge 时间

`closeout` 与 `reconciliation` 只消费这组 basis，不重新发明另一套 merge 证明方式。

## 9. merge signal drift

若 merge 后出现以下冲突，应归类为 `merge_signal_drift`：

- PR 已 merged，但 merge commit 无法定位
- merge commit 已进入主干，但 issue / project 仍显示未吸收
- merge method 与 profile 声明不一致
- 宿主返回的 mergeability、checks、branch protection 或 ruleset 结论互相冲突

## 10. 非目标

- 不在 Loom 文档内冻结 GitHub UI 操作步骤
- 不接管宿主 branch protection 或 ruleset 的底层实现
- 不把 `controlled merge` 简化成“PR 绿了就能合”
- 不把裸 `gh pr merge` 当成 Loom-governed PR 的日常合并入口；它会绕过本地受控合并检查，除非宿主 required check 已经强制 `pr merge gate`

## 11. Complex-existing wrapper consumption

成熟既有仓库可以保留 repo-owned merge wrapper，但 wrapper 必须降级为 host-action adapter。

稳定输出为 `loom-controlled-merge-consumption/v1`：

- `source_authority` 固定指向 Loom merge-ready result
- `wrapper_role` 固定为 `host_action_adapter`
- 必须校验 PR/head/base 未漂移
- 必须保留 required checks snapshot、triggered checks snapshot、review/spec record locators、retained host signal snapshot、merge commit 与 closeout basis

wrapper 不得继续自行聚合最终 merge readiness。Loom merge-ready allow result 缺失、stale、malformed，或 required / triggered checks readback 漂移时必须 fail closed。
