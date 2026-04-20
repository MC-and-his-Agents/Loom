# Closeout Gate

本文件定义 Loom 当前最小 closeout 执行链路。

宿主动作统一结果词表与 `fallback_to` 纪律见 [host-action-contract.md](host-action-contract.md)。本文件只承接 closeout 专有的 fail-closed 顺序与同步边界。

## 1. 能力定位

closeout gate 用来回答两件事：

- 当前事项是否已经达到“进入主干并收口”的最小条件
- GitHub issue / PR / project / main 是否与仓内结果态一致

在 installed-skills 或 `.loom/bin` carrier 下，`reconciliation audit|sync` 与 `closeout check|sync` 必须先消费 `runtime-state`。
若 install layout、shared runtime、shared references 或 bootstrap manifest 漂移，入口必须直接 `block`。

## 2. 稳定入口

- `python3 skills/shared/scripts/loom_flow.py reconciliation audit --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 skills/shared/scripts/loom_flow.py closeout check --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 skills/shared/scripts/loom_flow.py closeout sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 skills/shared/scripts/loom_flow.py reconciliation sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>] [--comment-file <path>] [--dry-run]`

## 3. `check` 最小检查面

`closeout check` 至少读取：

- 本地 gate 结果
- 同范围 `reconciliation audit` 结果
- issue 状态
- PR 是否已 merged
- 事项对应实现是否已达到 `absorbed`
- merged PR 是否已进入 `origin/main`
- project 中对应 issue 的状态

若这些事实不一致，结果必须返回 `block`。

`closeout check` 只允许返回 `pass` 或 `block`：

- 普通 closeout 缺口
  - 返回 `block`，并把 `fallback_to` 指向 `merge`
- reconciliation 返回 `fix-needed`
  - 返回 `block`，并把 `fallback_to` 指向 `reconciliation-sync`
- reconciliation 返回 `block`
  - 返回 `block`，并把 `fallback_to` 指向 `manual-reconciliation`

`closeout` 不把 drift 或控制面缺口伪装成顶层 `fallback` 结果。

`closeout check` 内部消费 `reconciliation audit` 时，阻断纪律如下：

- `pass`：允许继续读取 merge / main / project 等 closeout 事实
- `warn`：必须显式挂到 closeout 输出，但不默认阻断
- `fix-needed`：必须返回 `block`；先经 `reconciliation sync` 完成机械对齐，再重新执行 closeout check
- `block`：必须返回 `block`；先消除硬冲突或缺失事实，且在 audit 重新达标前禁止任何 closeout sync 写入

这里的 `absorbed` 只表示 host merge 后可证明的实现吸收结论，不等于 `closed_out`。
因此，`closeout check` 至少要能区分：

- 该 issue 已由其对应实现进入 `closed_out`
- 该 issue 的实现已被其他 merged work `absorbed`，但控制面尚未完成 closeout sync
- 该 issue 仍保留独立剩余缺口，不能被视为 `absorbed`

## 4. `sync` 最小动作

本阶段的正式写路径是 `reconciliation sync`。`closeout sync` 不单独跳过这一步；它只在同范围 reconciliation 已达可同步条件后继续消费 closeout 结论。`reconciliation sync` 只做控制面对齐动作：

- 先消费同范围的 `reconciliation audit` 结果，再生成可执行 sync 计划
- 在条件满足时关闭 issue
- 在 project 中把对应 item 状态设为 `Done`

约束：

- 若 `reconciliation audit` 出现任一 `block` finding，`sync` 必须直接返回 `block`，且不做任何写入
- `sync` 只允许对 `fix-needed` finding 做机械修复；`warn` 仅保留提示，不触发写入
- `--dry-run` 只输出基于 audit 的计划，不修改 GitHub 控制面
- `--comment-file` 与 `--comment` 二选一，只为当前 issue closeout comment 提供正文来源

`closeout sync` 仍保持 closeout 控制面对齐入口，但不得绕过已显式暴露的 reconciliation 结果。

`closeout sync` 也只允许返回 `pass` 或 `block`。若同步前置不满足，或同步后仍无法把控制面对齐，必须继续显式指向 `reconciliation-sync`、`manual-reconciliation` 或 `merge`，而不是产出新的 host action 结果词表。

若 parent issue 通过 child issue 的 `closed_out` / `absorbed` 结果完成自身 closeout 判断，`sync` 只负责把这一已成立结论写回控制面，不替代 parent 对剩余缺口的判断。

它不替代：

- PR merge 动作
- `absorbed` 证明本身
- review 执行层
- recovery writeback
- workspace cleanup / retire

## 5. 非目标

- 不在 Loom 内核里固化 GitHub UI、按钮或 ruleset 细节
- 不把 project 中不存在的 PR item 强行当作阻断
- 不让 closeout sync 绕过 gate 或 merge 事实
- 不把 reconciliation sync 扩展成新的对象模型或自动化宿主产品
