---
name: loom-retire
description: 负责清理并退休当前事项现场。Use when Codex needs to clean up Loom-owned residue and retire a workspace without discarding user changes.
---

# Loom Retire

这个 skill 承接 cleanup / retire 场景。
普通交付后的合并与收尾默认由 `loom ship` 完成；retire 只处理本地现场清理，
不负责选择收尾策略。

优先入口：

- `loom retire --target <repo> --item <id> --json`
- `loom workspace retire --target <repo> --item <id> --json`

执行要求：

- 默认先解释 retire 前置条件，再按 `purity-check -> workspace cleanup -> workspace retire` 顺序执行
- 默认输出只传递 agent-safe summary / artifact locator；完整诊断必须显式加 `--full-output`
- 若当前事项刚完成 host merge 后 closeout，先确认 `reconciliation audit|sync` 与 `closeout check|sync` 已消费完主干 / issue / PR / project 事实，再退休现场
- 若当前事项由 `loom ship` 完成且输出收尾通过或仅宿主收尾通过，可把该 ship
  证据当作 retire 前置读回；只有 ship 输出要求载体收尾、批量收尾或完整收尾时，
  才进入对应升级路径
- 不自动丢弃用户改动，不默认删除现场目录
- `workspace retire` 是 post-merge local cleanup / runtime evidence，不写 `.loom/progress/**` 或 `.loom/status/current.md` 这类版本化 carrier
- 版本化 closeout truth 必须在 merge 前由 closeout / reconciliation 路径形成，并在 merge 后由 closeout check / sync 消费；不能由本地 retire 追加生成
- retire 不选择 closeout mode。若 closeout queue/status 指向
  `auto_no_op`、`light_carrier_sync`、`batched_closeout`、`full_closeout` 或
  `blocked`，先按 closeout-gate 的 `auto_no_op`、`light`、`batched`、`full`
  mode 完成宿主 / 仓库载体收尾，或读取 `loom ship` 已完成的内联 / 仅宿主收尾证据，
  再执行本地 cleanup。`workspace retire`
  只能保留 local-only evidence，不能替代 `carrier closeout-sync --apply`、
  `reconciliation sync`、`closeout check` 或 closeout-only PR。

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
