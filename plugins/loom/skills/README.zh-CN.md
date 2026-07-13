# Loom Skills

Loom skills 是建立在 30 个公共 CLI 命令上的可执行 Agent 场景。它们编排宿主能力，
不拥有治理真相，也不会扩展 CLI 表面。

## 开始使用

以 `loom-init` 作为交互根入口。仓库采用只写 metadata：

```bash
loom install --target . --apply --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

Codex 插件通过 Codex marketplace 或 plugin host 安装、更新；该 workstation 动作与
仓库采用相互独立。

## 场景集合

- `loom-init`：检测、诊断与路由。
- `loom-adopt`：metadata-only 安装与验证。
- `loom-resume`：从显式 Work Item、branch、worktree、PR 和 GitHub readback 派生上下文。
- `loom-story`：在执行前整理 story readiness。
- `loom-build`：PR 创建前准入 typed Work Item 与 branch。
- `loom-pre-review`：审查前绑定真实 PR/current head。
- `loom-spec-review`、`loom-review`：执行语义审查并消费 host attestation。
- `loom-merge-ready`：消费 current-head attestation、hosted gate、checks 与 mergeability。
- `loom-handoff`：生成不修改仓库的会话摘要。
- `loom-retire`：退休本地 issue-scoped worktree。

精确公共命令见 [route-matrix.md](./route-matrix.md)。

## 产品边界

普通执行对 repo current、status、progress、review、shadow、closeout carrier 的修改数为
零。退役命令不能由 profile 恢复。review 与 closeout truth 来自宿主 attestation；产品
验收由产品 owner 持有，Loom 只消费经过认证的 locator。

`src/skills/` 是唯一 canonical source；构建过程生成并校验 `skills/`、plugin、example
与 package 分发面。
