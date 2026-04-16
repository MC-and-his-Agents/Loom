# Harness

`harness/` 承接 Loom 的稳定执行组件。

这里的文件只定义当前已经稳定的最小能力合同，不重复展开完整设计。
完整设计、强度模型和装配讨论仍由 `harness-design.md` 承接。

## 组件边界

- [execution-context.md](./execution-context.md)
  - 定义正式执行轮次必须绑定和读取的最小上下文语义
- [work-item-contract.md](./work-item-contract.md)
  - 定义进入执行前必须存在的事项与初始化产物合同
- [workspace-model.md](./workspace-model.md)
  - 定义执行现场的隔离、定位与 clean state 要求
- [recovery-model.md](./recovery-model.md)
  - 定义 checkpoint、resume、handoff 与每轮回写合同
- [status-surface.md](./status-surface.md)
  - 定义状态读取面与运行时可见性的最小输出
- [automation-frontload.md](./automation-frontload.md)
  - 定义适合机械化前置的检查范围
- [workspace-and-purity.md](./workspace-and-purity.md)
  - 定义现场职责纯度、分支纯度与范围控制边界

## 目录约束

- 本目录优先表达可执行规则，不重复叙述时序性执行信息
- 同一条 harness 规则应有唯一主落点；其他文件只引用边界，不并行复述
- 若某能力仍依赖场景强度、装配策略或完整流程讨论，应留在 `harness-design.md`
