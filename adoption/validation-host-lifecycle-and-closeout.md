# Validation: Host Lifecycle Boundary And Closeout Gate

本文记录 `#133` / `#135` / `#162` 的最小复验。

## 样本

- 仓内 demo：`examples/new-project`
- 仓内 GitHub 控制面样本：已合并的 `#138` / `#131`
- 负样本：`loom_check` 内联合成的 closeout / reconciliation fail-closed 样本

## 复验命令

```bash
python3 tools/loom_flow.py host-lifecycle --target examples/new-project --item INIT-0001
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom-wt-162-negative-closeout-validation --issue 131 --pr 138 --project 5
python3 tools/loom_flow.py reconciliation sync --target /Users/mc/dev/Loom-wt-162-negative-closeout-validation --issue 131 --pr 138 --project 5 --dry-run
python3 tools/loom_flow.py closeout check --target /Users/mc/dev/Loom-wt-162-negative-closeout-validation --issue 131 --pr 138 --project 5 --skip-gate
python3 tools/loom_flow.py closeout sync --target /Users/mc/dev/Loom-wt-162-negative-closeout-validation --skip-gate
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
  - 在输出中挂回同范围 `reconciliation audit` payload
- `closeout sync`
  - 在状态已一致时保持幂等
  - 若 `reconciliation` 仍是 `fix-needed` / `block`，会拒绝继续 closeout 写入
- `reconciliation audit`
  - 对干净样本返回 `pass`
  - 负样本类型稳定收敛为 `absorbed_but_open`、`parent_drift`、`project_drift`
- `reconciliation sync --dry-run`
  - 只输出计划动作，不伪装成已经完成控制面对齐
- `loom_check`
  - 已纳入 `host-lifecycle`、`reconciliation audit`、`closeout` 消费边界的 CLI 契约验证
  - 用合成负样本固定验证以下 fail-closed 纪律：
    - `closeout-fix-needed-fail-open`
    - `closeout-block-fallback-drift`
    - `closeout-malformed-reconciliation`
    - `closeout-warn-does-not-block`

## 负样本结论

- `absorbed-but-open`
  - 若 closeout 消费到 `fix-needed` 的吸收漂移却仍返回 `pass`，`loom_check` 必须失败
- `parent drift`
  - 若 reconciliation 已 `block` 但 closeout 没有保持 `block` 或错误回退到 `merge`，`loom_check` 必须失败
- `project drift`
  - 若 project 控制面漂移被 closeout 静默吞掉，`loom_check` 必须失败
- `sync 后复验`
  - 干净样本通过 `reconciliation sync --dry-run` 后，`closeout check` 继续对 `#131/#138/project 5` 返回 `pass`

## 结论

Loom 现在已经把“执行现场抽象”和“宿主 Git/GitHub 对象生命周期”明确分层，同时把 post-merge 的 closeout 检查链路收敛成稳定命令。`#162` 进一步把负向 closeout 验证写入版本控制，证明 `fix-needed` / `block` drift 不会再被 fail-open 地放过，而 `warn` 仍保持显式展示但不默认阻断。
