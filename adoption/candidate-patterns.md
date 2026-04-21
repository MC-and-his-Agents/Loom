# Candidate Patterns

本文件存放当前已观察到、但还不应直接固化为 Loom 默认内核的模式。

## `EXT-0020`

正式规约区分 `Spike / 标准 / 高风险` 三类深度，有明显价值。

当前结论：

- 这是强候选模式
- 但还没有足够多的仓库证据证明它应成为 Loom 默认结构
- 暂保留为 adoption 候选能力

## `EXT-0027`

Spike 事项应允许以“证据边界 + 准入条件 + handoff 输入”作为正式输出，而不必伪装成完整实施规格。

当前结论：

- 这是一条很强的方法论
- 但是否作为 Loom 的默认正式套件能力，仍需更多项目验证

## `EXT-0053`

`shadow parity` 的 mismatch 是否应自动升级为 blocking merge gate，当前还不应直接固化。

当前结论：

- `shadow parity` 作为 validation-only compare surface 已经成立
- 但“compare 结果自动决定 merge / closeout 放行”仍缺 live adopted repo 证据
- Loom 当前应继续保持：
  - compare 入口稳定
  - 结果固定为 `match | mismatch | unreadable`
  - 不声明哪一方自动获胜

## `parent-sub-issue relation`

跨多轮推进的事项，往往需要表达“总事项负责收敛目标与完成语义，子事项负责承接可独立推进的执行单元”这一关系。

这是一种平台无关的能力需求，不应被理解为某一托管平台专属的功能名词。

当前可验证实现之一，是 GitHub 的 parent issue / sub-issue 关系：它能帮助团队把较大的推进目标拆成可跟踪的子事项，并保留一定的汇总视角。

但 Loom 当前不应直接把 GitHub 的 parent/sub-issue 机制提升为内核规则，原因包括：

- Loom 需要保留“父事项 / 子事项关系”这一抽象能力，而不是绑定某个平台的对象模型
- 不同平台对层级关系、关闭联动、状态汇总和可见性边界的支持方式并不一致
- 即使在 GitHub 上，parent/sub-issue 也只能证明“这种关系可实现”，不能自动证明其字段、语义和收口规则就是 Loom 默认真相

当前结论：

- 这是一条值得继续验证的候选模式
- Loom 可以承认“父事项 / 子事项关系”是常见能力需求
- 但默认内核应先沉淀抽象语义与最小约束，而不是直接固化 GitHub 具体实现

当前最小抽象语义：

- 父事项负责阶段目标、收敛目标与关闭语义
- 子事项负责可独立推进的执行单元
- 状态汇总只是一种观察面，不自动成为语义真相源
- 宿主平台只负责承载层级关系，不定义 Loom 内核语义

截至当前 `Phase E` 的三类真实 adoption 验证：

- 新项目样本没有出现必须依赖父 / 子事项关系才能成立的证据
- `DevSkills` 样本的主要问题在验证入口与共享 contract 边界，不在父 / 子事项抽象
- `hotcp` 样本的主要问题在恢复、状态与纯度，不在父 / 子事项抽象

因此，`EXT-0043` 继续维持 `needs_validation`。
