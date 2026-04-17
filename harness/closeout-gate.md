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
- 事项对应实现是否已达到 `absorbed`
- merged PR 是否已进入 `origin/main`
- project 中对应 issue 的状态

若这些事实不一致，结果必须返回 `block`。

这里的 `absorbed` 只表示 host merge 后可证明的实现吸收结论，不等于 `closed_out`。
因此，`closeout check` 至少要能区分：

- 该 issue 已由其对应实现进入 `closed_out`
- 该 issue 的实现已被其他 merged work `absorbed`，但控制面尚未完成 closeout sync
- 该 issue 仍保留独立剩余缺口，不能被视为 `absorbed`

## 4. `sync` 最小动作

`closeout sync` 只做控制面对齐动作：

- 在条件满足时关闭 issue
- 在 project 中把对应 item 状态设为 `Done`

若 parent issue 通过 child issue 的 `closed_out` / `absorbed` 结果完成自身 closeout 判断，`sync` 只负责把这一已成立结论写回控制面，不替代 parent 对剩余缺口的判断。

它不替代：

- PR merge 动作
- `absorbed` 证明本身
- review 执行层
- recovery writeback

## 5. 非目标

- 不在 Loom 内核里固化 GitHub UI、按钮或 ruleset 细节
- 不把 project 中不存在的 PR item 强行当作阻断
- 不让 closeout sync 绕过 gate 或 merge 事实
