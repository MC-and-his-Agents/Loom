# GitHub Profile GraphQL Budget Guard Validation

本记录归档 `#324` 的验证结果。

## 1. 验证目标

证明 GitHub profile 不再把 GraphQL-only host reads 隐藏成普通读取，也不会把高频 repo / issue / PR 读取退回 `gh repo view`、`gh issue view` 或 `gh pr view`。

## 2. GraphQL-only Boundaries

以下路径仍是 GraphQL-only for now：

- ProjectV2 item / status surface
- ProjectV2 issue item field lookup
- native parent / sub-issue tree

这些 payload 必须暴露：

- `graphql_only: true`
- `budget_scope`
- `fallback_to`
- `recommended_action`

## 3. REST Boundary

以下高频读取继续使用 REST helper：

- `GET /repos/{owner}/{repo}`
- `GET /repos/{owner}/{repo}/branches/{branch}`
- `GET /repos/{owner}/{repo}/issues/{number}`
- `GET /repos/{owner}/{repo}/pulls/{number}`

`loom_check` 增加静态回归，禁止在 `skills/shared/scripts` 与 `tools` 的高频实现路径中重新引入：

```bash
rg "gh repo view|gh issue view|gh pr view" skills/shared/scripts tools
```

## 4. Boundary

本轮不尝试把 ProjectV2 或 native sub-issues REST 化，也不改变 #323 已冻结的 reconciliation taxonomy。预算 guard 只负责显式暴露 GraphQL-only 范围与失败降级。
