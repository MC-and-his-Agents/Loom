# Skill Validation: `loom-retire`

## 1. 样本标识

- 场景 skill：`loom-retire`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#92`
- 子 issue：`#93`、`#94`、`#95`

## 2. 验证样本

- Demo 仓库：`examples/new-project`
- checkpoint-lite 样本：`/Users/mc/dev/mail-listener`
- 可运行样本：`/Users/mc/dev/hotcp`

## 3. 显式触发验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --skill loom-retire`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-retire`
- 不被误路由到 `loom-handoff` 或 `loom-merge-ready`

## 4. 隐式路由验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --task "请清理现场并 retire 当前事项"`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-retire`
- `matched_signals` 能解释命中 retire 场景

## 5. 下游消费验证

执行：

- `python3 tools/loom_flow.py purity-check --target examples/new-project --item INIT-0001`
- `python3 tools/loom_flow.py workspace cleanup --target examples/new-project --item INIT-0001`
- `python3 tools/loom_flow.py workspace retire --target examples/new-project --item INIT-0001`
- `python3 tools/loom_check.py`

结论：

- `loom-retire` 默认先解释前置条件，再按 `purity-check -> workspace cleanup -> workspace retire` 顺序执行
- `cleanup` 只清理 Loom 自己产生的残留，遇到无关脏改动不会自动丢弃用户变更
- `retire` 会把恢复主入口回写到终态 `current_checkpoint: retired`，但不默认删除现场目录

## 6. 关闭依据

- `loom-retire` 已从 skeleton 提升为正式场景入口
- 显式触发、隐式路由与 retire 链路消费均已有验证记录
- gate 已复用既有 `purity-check` / `workspace cleanup` / `workspace retire` 入口做机械校验
