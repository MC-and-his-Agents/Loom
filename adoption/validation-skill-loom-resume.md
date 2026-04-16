# Skill Validation: `loom-resume`

## 1. 样本标识

- 场景 skill：`loom-resume`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#80`
- 子 issue：`#81`、`#82`、`#83`

## 2. 验证样本

- Demo 仓库：`examples/new-project`
- 可运行样本：`/Users/mc/dev/hotcp`

## 3. 显式触发验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --skill loom-resume`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-resume`
- 不被误路由到 `loom-pre-review`、`loom-handoff` 或其他场景

## 4. 隐式路由验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --task "请接手当前事项并恢复上下文后继续推进"`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-resume`
- `matched_signals` 能解释命中恢复场景

## 5. 下游消费验证

执行：

- `python3 tools/loom_flow.py flow resume --target examples/new-project --item INIT-0001`
- `python3 tools/loom_check.py`

结论：

- `flow resume` 固定按 `fact-chain -> state-check -> workspace-locate` 顺序编排
- 输出会稳定带出当前事项、现场入口、恢复入口、checkpoint、下一步、阻断项与最近验证摘要
- 该 flow 不回写任何载体，也不创建新的状态源

## 6. 关闭依据

- `loom-resume` 已从 skeleton 提升为正式场景入口
- 显式触发、隐式路由与 `flow resume` 下游消费均已有验证记录
- gate 已把 `flow resume` 的最小 JSON 语义纳入机械校验
