# Workspace And Purity

本文件定义 Loom 当前的正式执行现场与范围纯度规则。

## 1. 权威绑定

正式执行现场必须能证明：

```text
GitHub Work Item -> issue-scoped branch -> formal worktree -> PR -> live head
```

绑定来自显式 typed locator、Git worktree 与 GitHub live readback。会话记忆、临时
目录、committed current pointer、status、progress、review 或 shadow 文件都不能
替代该绑定。

## 2. 最小纯度

- 一个正式 branch/worktree 服务一个主要 Work Item 或明确声明的同 FR batch；
- 一个 PR 只承载声明范围内的改动；
- 无关改动、临时产物与另一事项的现场不得混入；
- PR 建立后不扩大 scope，后续缺口回到 GitHub issue tree。

## 3. 公共入口

- `loom workspace create` 创建或绑定 issue-scoped 正式 worktree；
- `loom workspace check` 从 Git 与 GitHub facts 验证 item、branch、worktree、PR
  和 head；
- `loom build` 在真实 PR 之前也可通过显式 Work Item 与 branch admission；
- `loom workspace retire` 只清理本地已完成现场，不关闭 issue、不修改 PR，
  也不写 repo closeout carrier。

## 4. 失败语义

以下情况 fail closed，并只返回一个 primary cause：

- 正式 worktree 不存在或未绑定目标 branch；
- checkout branch 与显式 Work Item / PR head branch 不一致；
- PR head 与当前 checkout head 不一致；
- 工作区存在未分流的越界改动；
- GitHub、Git 或 worktree facts 不可读。

remediation 应直接指向 Git/worktree、GitHub host action 或上述公共命令。不得要求
恢复 stale current pointer、同步 versioned carrier、创建空提交或空 PR。

`active_workspace_diagnostics` 只能是上述 Git/worktree/host facts 的派生读面，
不得重新引入 repo current 或 recovery carrier。

## 5. Closeout 边界

普通 delivery closeout 由 GitHub merge、checks、issue 与 host attestation 派生。
本地 worktree retirement 是独立清理动作；它既不证明产品验收，也不产生第二个
closeout PR。

宿主生命周期边界见 [host-lifecycle-boundary.md](./host-lifecycle-boundary.md)。
