# GitHub Profile Drift Reconciliation Validation

本记录归档 `#323` 的验证结果。

## 1. 验证目标

证明 GitHub profile 的 reconciliation 不再只读取零散 issue / PR / project 状态，而是消费 `loom-github-binding/v1` 绑定链，并把 drift 收敛到 Loom core taxonomy。

## 2. Runtime Entry

```bash
python3 tools/loom_flow.py reconciliation audit \
  --target . \
  --owner MC-and-his-Agents \
  --repo Loom \
  --phase <phase-issue> \
  --fr <fr-issue> \
  --issue <work-item> \
  --pr <implementation-pr> \
  --branch <branch>
```

`closeout check` 与 `closeout sync` 使用同一 reconciliation payload，不允许绕过 binding / drift 结果。

## 3. Stable Findings

本轮新增或强化的 finding kind：

- `binding_failure`
  - `category: gate_failure`
  - 绑定链缺失、冲突或无法证明
- `merge_signal_drift`
  - `category: drift`
  - PR 已 merged，但 merge commit 或 main 回链不可证明
- `parent_drift`
  - 继续表达 parent / child closeout 状态分叉
- `project_drift`
  - 继续表达 ProjectV2 status 与 issue / PR 状态分叉

所有 blocking drift 均 `fallback_to: manual-reconciliation`，可机械同步的 closeout drift 仍使用 `reconciliation-sync`。

## 4. Boundary

本轮不改变 ProjectV2 与 native sub-issues 的 GraphQL-only 实现。预算保护由 `#324` 承接。
