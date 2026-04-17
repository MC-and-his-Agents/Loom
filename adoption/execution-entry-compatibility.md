# Execution Entry Compatibility And Operation Flow

本文定义 Loom 日常执行入口的升级兼容边界，并给出可复验的操作流。

对应 Loom issue：`#60`

## 1. 兼容边界

当前稳定入口按以下分层兼容：

| 层级 | 稳定入口 | 兼容承诺 |
| --- | --- | --- |
| root 入口与基础验证 | `loom_init bootstrap/verify/fact-chain/route` | `loom-init` 继续作为唯一 root entry，路由能力不替代底层 CLI |
| 日常读取与检查 | `loom_flow fact-chain/runtime-evidence/state-check` | 输出保持 JSON 结果语义（`result/summary/missing_inputs/fallback_to`） |
| checkpoint 执行 | `loom_flow checkpoint admission/build/merge` | 三阶段语义与回退关系保持不变 |
| 现场与纯度治理 | `loom_flow workspace <create/locate/cleanup/retire>` + `purity-check` | 生命周期动作与失败语义保持不变 |
| 高频组合入口 | `loom_flow flow pre-review/review/resume/handoff/merge-ready` | 聚合入口扩张不破坏单命令入口，统一保持 JSON 结果语义 |
| 场景 skills | `loom-adopt/resume/pre-review/review/handoff/retire/merge-ready` | 场景 skill 只做入口编排，不新增第二套事实真相源 |

## 2. 升级策略

- 升级优先“加入口，不改旧入口语义”
- 新增聚合入口（如 `flow pre-review`、`flow merge-ready`）不替换单命令入口
- 新增 authored 入口（如 `review record`、`recovery writeback`、`work-item create|update`）不把只读 flow 变成隐式写入
- 新增场景 skill 入口不替代 `loom-init` 的 root 身份，只补显式入口与隐式路由
- gate 与 verify 始终复用同一 CLI，不维护第二套检查命令

## 3. 可复验操作流

在样本副本中按以下顺序执行：

1. `loom_init route`
2. `loom_init verify`
3. `loom_flow fact-chain`
4. `loom_flow runtime-evidence`
5. `loom_flow state-check`
6. `loom_flow flow resume`
7. `loom_flow flow pre-review`
8. `loom_flow flow review`
9. `loom_flow review read|record`
10. `loom_flow recovery writeback`
11. `loom_flow work-item create|update`
12. `loom_flow flow handoff`
13. `loom_flow flow merge-ready`
14. `loom_flow checkpoint admission/build/merge`
15. `loom_flow workspace locate/cleanup/retire`

预期：

- 前 1-9 步提供“该进入哪个入口/可继续执行/需阻断/是否应回退”的统一判断
- merge 阶段可按状态返回 `fallback`，而不是伪装成通过
- 操作流既可拆分执行，也可通过聚合入口执行高频路径

## 4. 验证结论

基于 `mail-listener`、`hotcp`、`loom-adoption-new-project` 的临时副本复验：

- `route`：显式 skill 命中与隐式信号命中均可复验
- `verify`：均返回 `ok: true`
- `fact-chain/runtime-evidence/state-check`：均可读
- `flow resume/pre-review/review/handoff/merge-ready`：均可返回稳定 JSON 结果
- `review record`、`recovery writeback`、`work-item create|update`：可显式回写 authored 结果而不引入第二真相
- `checkpoint merge` 在当前样本阶段按预期返回 `fallback`

因此，下游仓库可以按 root skill 或显式场景 skill 消费完整执行内核，不再依赖手工拼接散落流程说明。
