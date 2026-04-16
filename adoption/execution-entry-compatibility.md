# Execution Entry Compatibility And Operation Flow

本文定义 Loom 日常执行入口的升级兼容边界，并给出可复验的操作流。

对应 Loom issue：`#60`

## 1. 兼容边界

当前稳定入口按以下分层兼容：

| 层级 | 稳定入口 | 兼容承诺 |
| --- | --- | --- |
| 初始化与基础验证 | `loom_init bootstrap/verify/fact-chain` | 继续保留，不被 `loom_flow` 替换 |
| 日常读取与检查 | `loom_flow fact-chain/runtime-evidence/state-check` | 输出保持 JSON 结果语义（`result/summary/missing_inputs/fallback_to`） |
| checkpoint 执行 | `loom_flow checkpoint admission/build/merge` | 三阶段语义与回退关系保持不变 |
| 现场与纯度治理 | `loom_flow workspace <create/locate/cleanup/retire>` + `purity-check` | 生命周期动作与失败语义保持不变 |
| 高频组合入口 | `loom_flow flow pre-review` | 第一版聚合入口，不破坏单命令入口 |

## 2. 升级策略

- 升级优先“加入口，不改旧入口语义”
- 新增聚合入口（如 `flow pre-review`）不替换单命令入口
- gate 与 verify 始终复用同一 CLI，不维护第二套检查命令

## 3. 可复验操作流

在样本副本中按以下顺序执行：

1. `loom_init verify`
2. `loom_flow fact-chain`
3. `loom_flow runtime-evidence`
4. `loom_flow state-check`
5. `loom_flow flow pre-review`
6. `loom_flow checkpoint admission/build/merge`
7. `loom_flow workspace locate`

预期：

- 前 1-5 步提供“可继续执行/需阻断”的统一前置判断
- merge 阶段可按状态返回 `fallback`，而不是伪装成通过
- 操作流既可拆分执行，也可通过聚合入口执行高频路径

## 4. 验证结论

基于 `mail-listener`、`hotcp`、`loom-adoption-new-project` 的临时副本复验：

- `verify`：均返回 `ok: true`
- `fact-chain/runtime-evidence/state-check`：均可读
- `flow pre-review`：均可返回稳定 JSON 结果
- `checkpoint merge` 在当前样本阶段按预期返回 `fallback`

因此，下游仓库可以按统一入口消费完整执行内核，不再依赖手工拼接散落流程说明。
