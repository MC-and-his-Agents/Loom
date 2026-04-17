# Execution Entry Compatibility And Operation Flow

本文定义 Loom 日常执行入口的升级兼容边界，并给出可复验的操作流。

对应 Loom issue：`#60`

## 1. 兼容边界

当前稳定入口按以下分层兼容：

| 层级 | 稳定入口 | 兼容承诺 |
| --- | --- | --- |
| root 入口与基础验证 | `loom_init bootstrap/verify/fact-chain/route` | `loom-init` 继续作为唯一 root entry，路由能力不替代底层 CLI |
| 初始化与恢复公共治理读面 | `loom-init` 输出合同 + `loom-adopt` / `loom-resume` 场景合同 | `governance_surface` 作为稳定公共字段存在，场景 skill 只能复用或摘要，不新增第二套治理真相 |
| 日常读取与检查 | `loom_flow fact-chain/runtime-evidence/state-check` | 输出保持 JSON 结果语义（`result/summary/missing_inputs/fallback_to`） |
| checkpoint 执行 | `loom_flow checkpoint admission/build/merge` | 三阶段语义与回退关系保持不变 |
| 现场与纯度治理 | `loom_flow workspace <create/locate/cleanup/retire>` + `purity-check` | 生命周期动作与失败语义保持不变 |
| 宿主边界与 closeout | `loom_flow host-lifecycle` + `closeout check|sync` | Loom 明确边界与控制面对齐，但不接管宿主 branch/PR/worktree 生命周期 |
| drift 审计 | `loom_flow reconciliation audit` | 只生成 absorbed-but-open / parent drift / project drift 审计结论，不直接修改 GitHub 控制面 |
| 高频组合入口 | `loom_flow flow pre-review/review/resume/handoff/merge-ready` | 聚合入口扩张不破坏单命令入口，统一保持 JSON 结果语义 |
| 场景 skills | `loom-adopt/resume/pre-review/review/handoff/retire/merge-ready` | 场景 skill 只做入口编排，不新增第二套事实真相源 |

## 2. 升级策略

- 升级优先“加入口，不改旧入口语义”
- 新增聚合入口（如 `flow pre-review`、`flow merge-ready`）不替换单命令入口
- 新增 authored 入口（如 `review record`、`recovery writeback`、`work-item create|update`）不把只读 flow 变成隐式写入
- 新增场景 skill 入口不替代 `loom-init` 的 root 身份，只补显式入口与隐式路由
- `governance_surface` 只允许扩充 locator 或职责说明，不允许更名、拆成并行字段或复制实时 authored 状态
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
16. `loom_flow host-lifecycle`
17. `loom_flow reconciliation audit`
18. `loom_flow closeout check`

预期：

- 前 1-9 步提供“该进入哪个入口/可继续执行/需阻断/是否应回退”的统一判断
- `loom-init`、`loom-adopt`、`loom-resume` 对外公开的治理读面保持同一字段名 `governance_surface`
- merge 阶段可按状态返回 `fallback`，而不是伪装成通过
- 操作流既可拆分执行，也可通过聚合入口执行高频路径

## 4. 验证结论

基于 `mail-listener`、`hotcp`、`loom-adoption-new-project` 的临时副本复验：

- `route`：显式 skill 命中与隐式信号命中均可复验
- `governance_surface`：初始化与恢复场景均通过稳定公共字段暴露治理承接面，不额外发明并行状态源
- `verify`：均返回 `ok: true`
- `fact-chain/runtime-evidence/state-check`：均可读
- `flow resume/pre-review/review/handoff/merge-ready`：均可返回稳定 JSON 结果
- `review record`、`recovery writeback`、`work-item create|update`：可显式回写 authored 结果而不引入第二真相
- `checkpoint merge` 在当前样本阶段按预期返回 `fallback`
- `reconciliation audit` 会把 GitHub drift 显式化，但不提前执行 sync

因此，下游仓库可以按 root skill 或显式场景 skill 消费完整执行内核，不再依赖手工拼接散落流程说明。
