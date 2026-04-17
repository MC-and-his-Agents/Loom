# Closeout Gate

本文件定义 Loom 当前最小 closeout 执行链路。

## 1. 能力定位

closeout gate 用来回答两件事：

- 当前事项是否已经达到“进入主干并收口”的最小条件
- GitHub issue / PR / project / main 是否与仓内结果态一致

## 2. 稳定入口

- `python3 tools/loom_flow.py closeout check --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 tools/loom_flow.py closeout sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`

## 3. `check` 最小检查面

`closeout check` 至少读取：

- 本地 gate 结果
- issue 状态
- PR 是否已 merged
- merged PR 是否已进入 `origin/main`
- project 中对应 issue 的状态

若这些事实不一致，结果必须返回 `block`。

## 4. `sync` 最小动作

`closeout sync` 只做控制面对齐动作：

- 在条件满足时关闭 issue
- 在 project 中把对应 item 状态设为 `Done`

它不替代：

- PR merge 动作
- review 执行层
- recovery writeback

## 5. 非目标

- 不在 Loom 内核里固化 GitHub UI、按钮或 ruleset 细节
- 不把 project 中不存在的 PR item 强行当作阻断
- 不让 closeout sync 绕过 gate 或 merge 事实
