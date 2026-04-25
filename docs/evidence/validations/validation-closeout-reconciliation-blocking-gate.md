# Validation: Closeout / Reconciliation Blocking Gate

## 1. 样本标识

- 验证目标：`#319`
- 验证日期：`2026-04-25`
- 验证范围：Loom core closeout / reconciliation gate

## 2. 验证目标

本记录证明 `closeout` 不再只读取零散 host 状态，而是必须消费同范围 `reconciliation audit` 结果，并按统一 taxonomy fail-closed。

## 3. 稳定 finding taxonomy

`reconciliation.findings[*]` 固定包含：

- `category`
- `kind`
- `severity`
- `fallback_to`
- `subject`
- `evidence`
- `recommended_action`

当前冻结的 `kind`：

- `merged_but_open`
- `absorbed_but_open`
- `parent_drift`
- `project_drift`
- `host_signal_drift`

## 4. Runtime Contract

`closeout check|sync` 必须遵守：

- `reconciliation.result = pass`
  - 允许继续 closeout 判断
- `reconciliation.result = warn`
  - 显式挂到 closeout 输出，但不默认阻断
- `reconciliation.result = fix-needed`
  - `closeout.result = block`
  - `closeout.fallback_to = reconciliation-sync`
- `reconciliation.result = block`
  - `closeout.result = block`
  - `closeout.fallback_to = manual-reconciliation`

## 5. 本轮验证

本轮把以下正向/负向样本写入 `loom_check` synthetic contract：

- `merged_but_open`
- `absorbed_but_open`
- `parent_drift`
- `host_signal_drift`
- `warn` 不默认阻断
- `fix-needed` 不允许 fail-open
- `block` 不允许回退到普通 `merge`

## 6. Release Judgment

`#319` 完成后，Loom core closeout/reconciliation 已具备稳定 blocking gate 语义。GitHub profile 后续仍可增强对象自动编排，但不得绕过这里冻结的 fail-closed 纪律。
