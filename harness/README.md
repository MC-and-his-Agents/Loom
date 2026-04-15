# Harness

`harness/` 负责 Loom 的执行层。

它回答：

- 执行上下文如何绑定
- 工作现场如何创建和隔离
- 长任务如何恢复
- 哪些判断适合前置到脚本或状态面

当前承接的核心条目：

- [execution-context.md](./execution-context.md)
  - `EXT-0011`
- [workspace-model.md](./workspace-model.md)
  - `EXT-0012` `EXT-0025`
- [recovery-model.md](./recovery-model.md)
  - `EXT-0003` `EXT-0013`
- [automation-frontload.md](./automation-frontload.md)
  - `EXT-0009`
- [workspace-and-purity.md](./workspace-and-purity.md)
  - `EXT-0029`
