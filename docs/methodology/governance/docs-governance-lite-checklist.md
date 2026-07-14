# Docs-Governance Lite Checklist

本文件定义低风险治理文档变更的轻量路径。它降低重复治理成本，但不跳过真实
scope、current-head review、required checks 或 host readback。

## 1. 适用条件

仅当以下条件全部成立时使用 light：

- diff 只修改 methodology、模板说明或 landing links；
- 不改变 runtime、CLI/parser、schema、fixture、workflow、权限、release 或外部
  可见行为；
- 变更局部、可逆，reviewer 可从当前 diff 与既有合同完成判断；
- 没有安全、隐私、数据、迁移、部署或外部账号风险。

任一条件不成立时升级为 standard 或 reinforced，不以“docs-only”绕过风险。

## 2. 最小证据

| Evidence | Requirement |
| --- | --- |
| Goal and scope | GitHub Issue / Work Item 明确目标、范围与禁止范围。 |
| Workspace | 显式 Work Item、issue-scoped branch 与正式 worktree 一致。 |
| PR binding | GitHub PR、branch 与 live head readback 一致；不手写 head truth。 |
| Review | current-head semantic review 由 GitHub host attestation 证明。 |
| Validation | `git diff --check`、相关 docs/static checks 与 required hosted checks 通过。 |
| Release judgment | 明确 `no_release`，或在确有产品表面变化时升级治理强度。 |
| Closeout | 合并后从 GitHub merge、checks、issue 与 host attestation 派生。 |

若 PR metadata 需要声明 formal-suite 不适用，理由、consumer boundary、recheck
condition、scope proof 与 review requirement 放在 PR 的 machine block；不得为此
创建 repo-local spec、progress、review、status 或 closeout carrier。

## 3. 升级条件

出现以下任一情况立即退出 light：

- diff 进入 `tools/`、runtime、generated payload、tests/fixtures 或 workflow；
- 新增或修改机器消费字段、枚举、parser、gate 或 failure semantics；
- PR scope、Work Item、branch、worktree 或 live head 不一致；
- 需要 release、权限变更、host write 或外部可见动作；
- current-head review 或 targeted checks 发现产品行为风险。

## 4. 禁止项

- 不提交 current/status/progress/review/shadow 或普通 closeout carrier；
- 不把 PR merged、CI green 或 delivery closeout 推导为产品验收 passed；
- 不为通过门禁创建空提交、空 PR 或重复 aggregate；
- 不让 light 隐式升级为旧 execution-control 路径。

gate 的 profile 消费语义见
[tiered-gate-consumption-contract.md](../harness/tiered-gate-consumption-contract.md)。
