# Host Lifecycle Boundary

本文件定义 Loom 与宿主平台在 `workspace`、branch、PR、git worktree 之间的生命周期边界。

## 1. 结论

- `workspace`
  - 进入 Loom 执行层
- branch
  - 保留给宿主平台
- PR
  - 保留给宿主平台
- git worktree
  - 保留给宿主平台

## 2. Loom 承接什么

Loom 固定承接：

- `workspace_entry` 对应的执行现场语义
- recovery 与 checkpoint 对执行现场的绑定
- branch / PR / worktree 是否已经影响执行正确性的边界检查结果
- merge 前对 host merge 的统一放行判断

## 3. Loom 不承接什么

Loom 当前不提供以下原生命令：

- branch create / rename / retire
- PR create / update / merge / close
- git worktree create / remove

这些动作继续留给 Git / GitHub 或其他宿主平台。

## 4. 稳定入口

- `python3 tools/loom_flow.py host-lifecycle --target <repo> [--item <id>]`
- `python3 tools/loom_flow.py workspace create|locate|cleanup|retire --target <repo> [--item <id>]`
- `python3 tools/loom_flow.py purity-check --target <repo> [--item <id>]`
- `python3 tools/loom_flow.py flow merge-ready --target <repo> [--item <id>]`

## 5. 边界约束

- branch / PR purity 可以被 Loom 报告和消费，但不意味着 Loom 接管其生命周期
- `workspace` 是执行现场抽象，不等于 git worktree
- 宿主对象的 UI、命名、按钮与策略不进入 Loom 默认内核
