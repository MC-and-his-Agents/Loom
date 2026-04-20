# Loom Adopt Input Signals

当任务满足以下任一信号时，进入 `loom-adopt`：

- 明确要求初始化新项目
- 明确要求把既有仓库接入 Loom
- 明确要求 retrofit Loom 入口、首批工件或初始化事实链
- 明确要求判断某个仓库应该采用哪条 Loom 初始化路径

最小输入：

- 目标仓库
- 当前接入范围
- 是否需要实际落盘
- 当前任务是否仍属于初始化，而不是恢复/交接/review/merge-ready

若缺少最后一项，必须先回到 [../../route-matrix.md](../../route-matrix.md) 重新判断场景。
