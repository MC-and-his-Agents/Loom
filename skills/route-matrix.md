# Skills Route Matrix

本文定义 `loom-init` 作为 root entry 时的显式 / 隐式路由矩阵。

## 1. 优先级

1. 显式 skill 名称调用优先
2. 若无显式 skill，则按任务信号做隐式路由
3. 若无法稳定判断，回退到 `loom-init`，输出最小补充信号

## 2. 场景矩阵

| 场景 | 任务信号 | 目标 skill | 依赖 CLI |
| --- | --- | --- | --- |
| 初始化 / retrofit | 初始化、新项目接入、既有仓库 retrofit、引入 Loom | `loom-adopt` | `python3 tools/loom_init.py bootstrap\|verify\|fact-chain` |
| 恢复执行 | 接手当前事项、恢复上下文、问下一步、继续推进 | `loom-resume` | `python3 tools/loom_flow.py flow resume` |
| review 前统一检查 | review 前检查、进入 review、确认是否可 review | `loom-pre-review` | `python3 tools/loom_flow.py flow pre-review` |
| 交接 | 交接、回写停点、移交当前事项 | `loom-handoff` | `python3 tools/loom_flow.py flow handoff` |
| 清理 / retire | 清理现场、退休现场、结束当前事项现场 | `loom-retire` | `python3 tools/loom_flow.py workspace cleanup\|retire` |
| merge 前放行 | merge-ready、最终放行前预检、确认是否可合并 | `loom-merge-ready` | `python3 tools/loom_flow.py flow merge-ready` |

## 3. fallback 语义

出现以下任一情况时，root skill 不做猜测，直接回退到 `loom-init`：

- 没有明确 skill 名称，也没有稳定任务信号
- 同时命中多个场景，且无法根据任务语义收敛为单一路由
- 目标仓库或事项标识缺失，无法稳定执行下游入口

回退输出必须至少包含：

- `selected_skill: "loom-init"`
- `result: "fallback"`
- `missing_inputs`
- `fallback_to: "loom-init"`
