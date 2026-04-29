# Workspace Profile

本文件定义 Loom 新仓库与既有仓库默认可消费的 workspace profile。

它回答一件事：执行现场如何被装配、定位和校验，而不把 Git
`worktree` 的底层生命周期改写成 Loom-owned 能力。

## 1. 稳定 profiles

Loom 当前固定三种默认 profile：

- `single-workspace`
  - 使用仓库根目录作为执行现场。
  - 适合新仓库、单事项推进或尚未需要隔离 worktree 的轻量接入。
- `per-item-worktree`
  - 每个正式 `Work Item` 使用独立工作现场，通常可由宿主
    `git worktree` 承接。
  - 适合多事项并行、长任务恢复或需要强纯度隔离的仓库。
- `attach-existing`
  - 读取并校验既有仓库或 repo companion 声明的工作现场。
  - 适合成熟既有仓库的 recognize-and-attach 路径。

## 2. Profile 选择语义

profile 选择是派生读面，不是第二份 authored 真相。

最小默认推断：

- `workspace_entry` 为 `.` 时，选择 `single-workspace`
- `workspace_entry` 指向 `.worktrees/` 或包含当前 item id 时，选择
  `per-item-worktree`
- 其他可解析 repo-relative 现场默认视为 `attach-existing`

仓库后续可以在 profile 合同中显式声明更强策略；但显式声明也只能改变
Loom 如何校验现场，不改变 Git / GitHub / host adapter 的底层 ownership。

## 3. 每个 profile 必须暴露的事实

统一状态面至少应能读出：

- selected profile
- `workspace_entry`
- resolved workspace path
- workspace 是否存在
- purity check 结果
- host worktree binding 是否可观察
- 下一步修复建议

这些字段只能从 `Work Item`、fact-chain、workspace locate、purity check 与
host lifecycle 派生，不能反向覆盖 `Work Item` 或宿主对象。

## 4. 失败语义

- `missing_workspace_entry`
  - `Work Item` 缺少 workspace entry。
- `workspace_missing`
  - 声明的 workspace path 不存在。
- `workspace_escape`
  - 声明路径逃逸目标仓库。
- `workspace_dirty`
  - 当前现场存在未分流改动。
- `workspace_binding_drift`
  - workspace / branch / PR / host worktree 与当前事项绑定不一致。

以上失败可以阻断 resume、review 或 merge-ready；但不得被解释为 Git
worktree 生命周期命令失败。

## 5. Ownership 边界

Loom 拥有：

- workspace profile 语义
- workspace locate / purity / retire 的编排合同
- 当前事项与执行现场的绑定校验
- 派生状态面与修复建议

宿主平台仍拥有：

- `git worktree add/remove/list` 的底层实现
- branch create / rename / retire
- PR create / update / merge / close
- ruleset、required checks 与 merge policy 的强制执行

## 6. 非目标

- 不要求所有仓库都使用 Git worktree。
- 不把 `workspace` 命名成 `git worktree` 的别名。
- 不新增替代 Git 的 worktree manager。
- 不用 profile 状态反向覆盖 authored work item truth。
