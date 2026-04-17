# Validation: Host Lifecycle Boundary And Closeout Gate

本文记录 `#133` / `#135` 的最小复验。

## 样本

- 仓内 demo：`examples/new-project`
- 仓内 GitHub 控制面样本：已合并的 `#138` / `#131`

## 复验命令

```bash
python3 tools/loom_flow.py host-lifecycle --target examples/new-project --item INIT-0001
python3 tools/loom_flow.py closeout check --target /Users/mc/dev/Loom-wt-129-batch3 --issue 131 --pr 138 --project 5
python3 tools/loom_flow.py closeout sync --target /Users/mc/dev/Loom-wt-129-batch3 --issue 131 --pr 138 --project 5
python3 tools/loom_check.py
```

## 结果

- `host-lifecycle`
  - 明确 `workspace` 由 Loom 执行层承接
  - 明确 branch / PR / git worktree 继续由宿主平台承接
  - 不再把 branch purity / PR purity 留成无去向的 report-only 结论
- `closeout check`
  - 能同时读取 gate、issue、PR、project、`origin/main`
  - 对 `#131` / `#138` 返回 `pass`
- `closeout sync`
  - 在状态已一致时保持幂等
  - 可作为 issue close 与 project `Done` 的显式控制面入口
- `loom_check`
  - 已纳入 `host-lifecycle` 的 CLI 契约验证

## 结论

Loom 现在已经把“执行现场抽象”和“宿主 Git/GitHub 对象生命周期”明确分层，同时把 post-merge 的 closeout 检查链路收敛成稳定命令，不再只靠规则文本和人工记忆。
