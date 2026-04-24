# Work Item Contract

本文件定义 Loom 当前最小 work item / `exec-plan` 合同。

本文件当前承接：

- `EXT-0037` 的初始化产物模型

完整执行顺序见 [execution-chain.md](./execution-chain.md)。

## 1. 能力定位

`Work Item` 是进入正式执行的唯一入口。
若项目使用 `exec-plan` 或等价工件，它只承接执行与恢复。

本文件同时定义初始化后至少应落位哪些执行产物。
字段归属见 [fact-chain-contract.md](./fact-chain-contract.md)。

## 2. work item 最小合同

进入正式执行的事项，必须有可追踪的 `Work Item`，并至少表达：

- 事项标识
- 目标
- 范围
- 当前执行路径
- 关联工件
- 工作现场入口
- 恢复主入口路径
- review 结论入口
- 当前验证入口
- 关闭条件

一个 `Work Item` 对应一个清晰目标，不得承载多个无关正式事项。
任何 host issue、PR、plan、spec 都只能映射或引用它，不得越权替代它成为正式执行入口。

## 3. 初始化产物模型

当 Loom 初始化一个仓库或一条正式执行链路时，最小产物应包括：

- 可进入执行的首批 `Work Item` 或等价事项清单
- 至少一个 `progress` / `checkpoint` 载体
- 与事项关联的唯一恢复主入口约定
- 可定位的执行路径与工作现场入口
- 后续验证或执行支撑的入口约定
- 首个稳定提交或等价回退边界，用于界定初始化后的首轮 clean state

Loom 不固化这些产物的具体文件名，但要求它们在初始化完成后已可读取、可回写、可继续执行。

## 4. `exec-plan` 的职责边界

如果项目使用 `exec-plan`，其职责应限制为：

- 记录当前停点
- 记录下一步
- 记录已验证事实
- 记录阻断项
- 记录与正式工件的关联

禁止事项：

- 用 `exec-plan` 替代正式需求真相
- 用 `exec-plan` 替代长期状态真相
- 用 `exec-plan` 吞并多个无关事项

## 5. 与执行链路的关系

`Work Item` / `exec-plan` 至少要能被以下环节消费：

- 每轮读取
- 工作现场定位
- 每轮回写
- 验证汇总
- spec gate 命中判断
- gate chain 放行

不同执行路径可以有不同最小输入强度：

- 轻量事项
  - work item 可直接进入实现与 PR
- 中等事项
  - work item 应关联简化设计说明
- 正式规约事项
  - work item 应关联 `spec.md` 与 `plan.md`

无论路径轻重，都必须能被 [execution-context.md](./execution-context.md)、[recovery-model.md](./recovery-model.md) 与 [merge-checkpoint.md](./merge-checkpoint.md) 消费。

## 6. 事实链约束

- `Work Item` 只承接静态执行真相，不并行 authored 当前停点、下一步、阻断项或最近验证摘要
- `Work Item` 可以 authored `review_entry` 这类 locator，但不得 authored review 结论本身
- 当前 checkpoint 属于恢复主入口，而不是 `Work Item`
- `status control plane` 若展示 `goal`、`scope`、`execution_path` 等字段，必须从 `Work Item` 派生

## 7. 最小 author/update 入口

静态事项 authoring 由日常 CLI 显式承接：

- `python3 shared/scripts/loom_flow.py work-item create --target <repo> --item <id> ...`
- `python3 shared/scripts/loom_flow.py work-item update --target <repo> --item <id> ...`

边界固定如下：

- `create` / `update` 只写静态字段与关联工件
- 是否切换为当前活跃事项，必须显式使用 `--activate`
- `--activate` 只允许改 locator truth，不得顺手写 recovery 动态字段
