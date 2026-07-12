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
- 若当前事项刚完成 host merge 后 closeout，先确认 host attestation/readback 与必要的 `reconciliation audit|sync` 已消费完主干 / issue / PR / project 事实，再退休现场
- 若当前事项由 `loom ship` 完成，可把同 head 的 host-only closeout attestation
  当作 retire 前置读回；不得再升级到 repo carrier 收尾
- 不自动丢弃用户改动，不默认删除现场目录
- `workspace retire` 是 post-merge local cleanup / runtime evidence，不写 `.loom/progress/**` 或 `.loom/status/current.md` 这类版本化 carrier
- closeout truth 由 GitHub review/PR/checks/merge/issue 与 host attestation 拥有；
  不能由本地 retire 追加生成
- retire 不选择 closeout mode，不调用 `carrier closeout-sync`，不创建 closeout-only
  或 current-retire PR。`workspace retire` 只能保留 local-only evidence。

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
