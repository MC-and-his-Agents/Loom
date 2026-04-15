# Recovery Model

本文件承接 Loom 当前最核心的长任务恢复能力。

## 当前核心落点

### `EXT-0003`

长任务需要持久工件支持 checkpoint、resume 和 handoff。

### `EXT-0013`

每个长任务应有唯一恢复主入口，而不是多个并行恢复点。

## 当前结论

Loom 的最小 harness 至少应包含：

- checkpoint
- resume
- handoff
- 唯一恢复主入口
