# Routing And Checkpoints

本文件承接 Loom 的事项分流、入口判断与 checkpoint 策略。

## 当前核心落点

### `EXT-0007`

流程类型和例外分支过多会显著抬高判断成本。

Loom 需要提供：

- 决策图
- 引导式初始化入口
- 不依赖用户先理解完整分类学的采用路径

### `EXT-0024`

中等事项应允许通过“简化设计说明”进入实现，而不必一律升级为正式 FR。

Loom 需要保留三段式入口：

- 轻量事项
- 中等事项
- 正式规约事项

但不应在第一阶段把它做成僵硬 profile。

## 当前候选落点

### `EXT-0019`

事项分流思想值得保留，但分流规则必须更易判断。

当前作为 adoption 层候选能力保存，后续由初始化 `SKILL` 决定如何引导。

### `EXT-0022`

长任务生命周期至少需要：

- `admission checkpoint`
- `build checkpoint`
- `merge checkpoint`

其中：

- `admission checkpoint` 决定能否进入实现承诺
- `build checkpoint` 决定是否仍在正确轨道上
- `merge checkpoint` 决定当前 head 是否可进入主干

Loom 需要把这三类 checkpoint 从概念做成可执行结构。

## 与 `skills/` 的关系

本文件只定义采用层策略。

这些策略最终应由 `skills/` 中的初始化入口负责提问、判断和装配。
