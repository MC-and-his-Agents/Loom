# Skill Validation: `loom-pre-review`

## 1. 样本标识

- 场景 skill：`loom-pre-review`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#84`
- 子 issue：`#85`、`#86`、`#87`

## 2. 验证样本

- Demo 仓库：`examples/new-project`
- 可运行样本：`/Users/mc/dev/hotcp`

## 3. 显式触发验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --skill loom-pre-review`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-pre-review`
- 不被误路由到 `loom-resume`、`loom-merge-ready` 或其他场景

## 4. 隐式路由验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --task "请在进入 review 前做统一检查"`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-pre-review`
- `matched_signals` 能解释命中 pre-review 场景

## 5. 下游消费验证

执行：

- `python3 tools/loom_flow.py flow pre-review --target examples/new-project --item INIT-0001`
- `python3 tools/loom_check.py`

结论：

- `flow pre-review` 固定按 `fact-chain -> state-check -> runtime-evidence -> checkpoint-admission -> workspace-locate` 顺序编排
- 输出会稳定给出统一通过/阻断/回退摘要
- skill 只负责进入 review 前的机械判断，不替代 reviewer 的语义审查

## 6. 关闭依据

- `loom-pre-review` 已从 skeleton 提升为正式场景入口
- 显式触发、隐式路由与下游消费均已有验证记录
- 该 skill 没有引入新的事实链载体或并行检查命令
