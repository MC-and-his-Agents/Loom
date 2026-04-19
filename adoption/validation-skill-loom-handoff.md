# Skill Validation: `loom-handoff`

## 1. 样本标识

- 场景 skill：`loom-handoff`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#88`
- 子 issue：`#89`、`#90`、`#91`

## 2. 验证样本

- Demo 仓库：`examples/new-project`
- 复杂既有仓库：`/Users/mc/dev/hotcp`

## 3. 显式触发验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --skill loom-handoff`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-handoff`
- 不被误路由到 `loom-resume`、`loom-retire` 或其他场景

## 4. 隐式路由验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --task "请准备交接当前事项并回写停点"`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-handoff`
- `matched_signals` 能解释命中 handoff 场景

## 5. 下游消费验证

执行：

- `python3 tools/loom_flow.py flow handoff --target examples/new-project --item INIT-0001`
- `python3 tools/loom_check.py`

结论：

- `flow handoff` 固定按 `runtime-state -> fact-chain -> state-check -> workspace-locate` 顺序编排
- 输出会稳定给出 `recovery_entry`、`status_surface`、`current_stop`、`next_step`、`blockers`、`latest_validation_summary`、`fallback_target`
- 输出顶层稳定携带 `runtime_state`，且一旦 `runtime_state.result=block` 就 fail-closed
- 该 flow 只生成最小回写清单与定位，不直接回写任何 authored 载体

## 6. 关闭依据

- `loom-handoff` 已从 skeleton 提升为正式场景入口
- 显式触发、隐式路由与 `flow handoff` 下游消费均已有验证记录
- gate 已把 `flow handoff` 的最小 JSON 语义纳入机械校验
