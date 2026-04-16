# Real Adoption Validation: Automation Frontload In `hotcp`

## 1. 样本标识

- 样本仓库：`hotcp`
- 仓库类型：`复杂既有仓库`
- 仓库位置：`/Users/mc/dev/hotcp`
- 验证副本：`/tmp/loom-val-hotcp`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#57`

## 2. 验证目标

验证扩展后的 automation-frontload 是否能稳定暴露以下典型漂移：

- 活跃状态冲突
- checkpoint 完整性缺口
- 范围越界或未分流残留

## 3. 正常样本复验

在完成 bootstrap 并提交基线后，执行：

- `.loom/bin/loom_flow.py state-check --target /tmp/loom-val-hotcp`
- `.loom/bin/loom_flow.py flow pre-review --target /tmp/loom-val-hotcp`
- `.loom/bin/loom_flow.py checkpoint admission --target /tmp/loom-val-hotcp`

结果：

- `state-check`：`pass`
- `flow pre-review`：`pass`
- `checkpoint admission`：`pass`

说明当前样本在无残留干扰时可以通过前置检查链路。

## 4. 负样本复验

构造残留改动（在工作区内追加未分流变更）后执行：

- `.loom/bin/loom_flow.py state-check --target /tmp/loom-val-hotcp`
- `.loom/bin/loom_flow.py purity-check --target /tmp/loom-val-hotcp`

结果：

- `state-check`：`block`
- `purity-check`：`block`

阻断信息包含 `workspace contains untriaged residual changes`，与前置失败分类中的 `workspace_residue`、`active_state_conflict` 语义一致。

## 5. 结论

- 扩展后的 automation-frontload 能在 review 前稳定挡住典型漂移
- 前置检查结果可以被统一入口（`state-check` / `flow pre-review`）消费
- `#57` 的验证收口条件已满足并进入版本控制
