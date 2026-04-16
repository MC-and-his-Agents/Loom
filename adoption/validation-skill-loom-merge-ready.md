# Skill Validation: `loom-merge-ready`

## 1. 样本标识

- 场景 skill：`loom-merge-ready`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#96`
- 子 issue：`#97`、`#98`、`#99`

## 2. 验证样本

- Demo 仓库：`examples/new-project`
- 可运行样本：`/Users/mc/dev/hotcp`
- `not_applicable` 样本：`/Users/mc/dev/loom-adoption-new-project`

## 3. 显式触发验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --skill loom-merge-ready`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-merge-ready`
- 不被误路由到 `loom-pre-review` 或 `loom-resume`

## 4. 隐式路由验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --task "请在合并前检查当前事项是否可以合并"`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-merge-ready`
- `matched_signals` 能解释命中 merge-ready 场景

## 5. 下游消费验证

执行：

- `python3 tools/loom_flow.py flow merge-ready --target examples/new-project --item INIT-0001`
- `python3 tools/loom_check.py`

结论：

- `flow merge-ready` 固定按 `fact-chain -> state-check -> runtime-evidence -> checkpoint-build -> checkpoint-merge` 顺序编排
- 输出会稳定给出统一放行结论、5 项运行时证据、`build`/`merge` checkpoint 摘要、当前 checkpoint、当前 lane 与最近验证摘要
- 该 flow 只输出 merge 前统一放行摘要，不替代宿主平台 merge 动作

## 6. 关闭依据

- `loom-merge-ready` 已从 skeleton 提升为正式场景入口
- 显式触发、隐式路由与 `flow merge-ready` 下游消费均已有验证记录
- gate 已把 `flow merge-ready` 的最小 JSON 语义纳入机械校验
