# Harness

`harness/` 承接 Loom 的稳定执行组件。

这里的文件只定义当前已经稳定的最小能力合同，不重复展开完整设计。
完整方案、初始化场景和强度模型由 `harness-design.md` 承接。

## 组件边界

- [work-item-contract.md](./work-item-contract.md)
  - 定义进入正式执行前必须存在的事项与初始化产物合同
- [fact-chain-contract.md](./fact-chain-contract.md)
  - 定义静态真相、动态真相与派生读面的唯一归属关系
- [execution-context.md](./execution-context.md)
  - 定义每轮正式执行必须绑定和读取的最小上下文语义
- [execution-chain.md](./execution-chain.md)
  - 定义从初始化产物到 merge checkpoint 放行的最小执行链路
- `checkpoint-model.md`
  - 定义 `admission` / `build` checkpoint 的输入、输出、失败语义与回退去向
- [workspace-model.md](./workspace-model.md)
  - 定义执行现场的隔离、定位与 clean state 要求
- `workspace-lifecycle.md`
  - 定义 `create`、`locate`、`cleanup`、`retire` 与 `purity-check` 的生命周期合同
- [recovery-model.md](./recovery-model.md)
  - 定义唯一恢复主入口、`checkpoint`、`resume`、`handoff` 与每轮回写合同
- [status-surface.md](./status-surface.md)
  - 定义状态读取字段、运行时证据入口与 `not_applicable` 语义
- [automation-frontload.md](./automation-frontload.md)
  - 定义适合机械化前置的检查矩阵与覆盖边界
- [merge-checkpoint.md](./merge-checkpoint.md)
  - 定义执行侧放行输入、结果语义与回退承接
- [workspace-and-purity.md](./workspace-and-purity.md)
  - 定义现场职责纯度、分支纯度与范围控制边界

## 目录约束

- 本目录优先表达可执行规则，不在多个文件并行复述同一条执行链路
- 同一条 harness 规则应有唯一主落点；其他文件只引用边界，不重复承接完整流程
- 若某能力仍依赖初始化场景、装配关系或强度模型讨论，应留在 `harness-design.md`
