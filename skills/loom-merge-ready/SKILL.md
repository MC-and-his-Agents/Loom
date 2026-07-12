---
name: loom-merge-ready
description: 负责 merge 前统一放行。Use when Codex needs to confirm whether the current item is ready for merge without replacing the host platform merge action.
---

# Loom Merge Ready

`loom-merge-ready` 是显式合并前预检；普通交付主路径仍是 `loom ship`。

## 默认入口

1. `loom attestation readback --repo <owner/repo> --pr <n> --work-item <n>
   --artifact-input <file> [--review-policy approved|single_maintainer] --json`
2. `loom pr gate <pr> --work-item <n> --json`
3. `loom merge check <pr> --work-item <n> --json`

三个读面必须绑定同一 GitHub PR/current head。Attestation 必须认证 semantic tree、
review/verifier、trusted workflow run 与 artifact digest；PR gate / merge check 消费
GitHub metadata、required checks、base branch 与 mergeability。

## 约束

- 不读取或写入 repo review、current、status、progress 或 shadow carrier。
- 不执行 carrier refresh、freeze write、closeout-only PR 或 current-retire PR。
- PR head、checks、mergeability 均由 GitHub readback，不接收手写 head 作为 truth。
- full/minimal suite 仍消费全局 suite/evidence validator，但这些 locator 不是 review
  truth，也不得恢复 repo review record。
- 任一读面缺失或冲突时 fail closed，只返回一个 primary cause。
- reinforced 不隐式升级到 carrier path；历史 backend 只允许显式、90 天内到期的
  `reinforced-carrier-compat/v1`。

## 完成标准

- host attestation、PR gate 与 merge check 对同一 current head 全部通过；
- 普通 merge-ready 产生 0 个 repo mutation；
- 输出可供 GitHub controlled merge 消费，但不替代 merge 动作。

输入输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
