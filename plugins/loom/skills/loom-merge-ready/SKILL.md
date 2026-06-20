---
name: loom-merge-ready
description: 负责 merge 前统一放行。Use when Codex needs to confirm whether the current item is ready for merge without replacing the host platform merge action.
---

# Loom Merge Ready

这个 skill 承接 merge-ready 场景，也就是 gate chain 里的 `merge gate` 汇总层。

优先入口：

- `python3 scripts/loom-merge-ready.py flow merge-ready --target <repo> [--item <id>]`

执行要求：

- 固定按 `runtime-state -> fact-chain -> state-check -> runtime-evidence -> checkpoint build -> checkpoint merge` 编排
- 只输出进入 `GitHub controlled merge` 前的统一放行摘要，不替代宿主平台 merge 动作
- PR 合并前的宿主硬门禁由 `pr-gate check` 和 `controlled-merge check|merge` 承接；它们只能消费 authored Loom review record，不能把 raw review/shadow evidence 当作 approval
- 不新建 authored 真相源，也不直接执行平台合并
- 消费 repo-local `loom suite evidence validate --json` 与
  `loom suite carrier validate --json` 输出中的 full/minimal suite path、
  evidence-map freshness、consistency-analysis classification 与 gate-chain 当前状态，
  但不重新定义这些合同；缺少可读 CLI JSON 时 fail closed
- full path 下，review record 必须证明已消费 suite locators、evidence-map、
  consistency-analysis、PR head / reviewed head / validation freshness；缺失、stale 或
  conflict 必须 fail-closed
- minimal path 下，只有带 rationale、consumer boundary 和 recheck condition 的
  `not_applicable` 可以跳过 full path 附加工件；missing、deferred 或 source/generated
  sync 待办不能被当作 merge-ready
- 有 PR 绑定时，merge-ready 应消费已冻结且已 readback 的 PR metadata、current
  head、carrier refresh、shadow freshness、review record 与 release-boundary 输入；
  这些输入由 `loom gate freeze check|write` 提供统一快照与 classifier。merge-ready
  不手工重拼一条旁路检查链；若 freeze 返回 `pr_metadata_drift`、`shadow_stale`、
  `review_stale`、`hosted_snapshot_mismatch` 或 `unsupported_command_surface`，
  必须先回到 freeze repair path。
- 当 PR 是 closeout-only carrier PR 时，merge-ready 只能消费
  `loom-closeout-specific-gate/v1` 的 verdict 作为 closeout admission 信号：
  `closeout_pr_allowed=true` 允许继续 closeout PR 路径，但不等于实现审查通过；
  `full_review_required=true` 或 `escalation_required=true` 必须回到 full review /
  guardian 或 blocker repair。Queue/status 的 `light_carrier_sync`、
  `batched_closeout`、`full_closeout` 只是运行时分类，必须映射回
  closeout-gate 的 `light`、`batched`、`full` canonical modes 后再判断。

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)

Merge-ready 消费的共享合同见：

- [spec-suite.md](../shared/references/templates/spec-suite.md)
- [evidence-map.md](../shared/references/templates/evidence-map.md)
- [consistency-analysis.md](../shared/references/templates/consistency-analysis.md)
- [gate-chain.md](../shared/references/harness/gate-chain.md)
- [lane-orchestration.md](../shared/references/harness/lane-orchestration.md)
- [../shared/references/harness/pr-merge-gate.md](../shared/references/harness/pr-merge-gate.md)
