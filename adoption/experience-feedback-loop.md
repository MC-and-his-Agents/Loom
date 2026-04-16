# Experience Feedback Loop

本文定义 Loom 对下游实践的最小经验回流机制。

它回答的问题是：下游样本中的 adoption 结论，如何从一次验证稳定进入 `adoption/`、核心能力文档和 GitHub issue，而不是散落在会话里。

## 1. 回流目标

经验回流至少要完成四件事：

- 记录样本事实，而不是只记录印象
- 把事实提炼为可复用结论或负面结论
- 把结论映射到 Loom 的稳定落点或候选落点
- 让 issue 的关闭依据能直接追溯到版本化记录

## 2. 回流输入

每次回流都必须基于一份真实 adoption 验证记录，格式固定由 [validation-record-contract.md](./validation-record-contract.md) 约束。

最小输入字段包括：

- 样本标识与仓库类型
- `loom-init` 输入信号判断
- 选定装配路径
- 首批工件与恢复形态
- 主要摩擦、失效点与升级信号
- 新增或修正的 `EXT-*`
- `landing-map` 状态变化
- 对应 issue 的关闭依据

## 3. 回流流程

固定流程如下：

1. 先完成样本验证记录
2. 把稳定结论写入 `extraction-ledger.md`
3. 把落点与状态变化写入 `landing-map.md`
4. 更新被影响的核心文档或候选文档
5. 在对应 issue 中留下可追溯依据
6. 只有在文档真相与 issue 语义一致时才关闭 issue

任何一步缺失，都不应宣称经验已经回流完成。

## 4. 结论分流规则

### 4.1 进入 `keep`

必须同时满足：

- 至少有两个独立样本支持
- 结论不依赖单一宿主细节
- 已能映射到 Loom 的稳定能力边界

### 4.2 进入 `adapt`

满足以下任一条件时进入：

- 结论有价值，但仍需抽象或去项目化
- 结论当前仍混有宿主特定细节
- 结论需要更多样本确认边界，但已足够形成候选落点

### 4.3 进入 `needs_validation`

满足以下任一条件时进入：

- 目前只有单仓样本
- 结论只在 Loom 自举或单一平台上成立
- 仍无法确认它是否属于平台无关能力

### 4.4 进入 `drop`

满足以下任一条件时进入：

- 结论已被真实样本否定
- 结论明显属于局部组织便利，不适合作为 Loom 上游能力

## 5. 负面验证要求

负面验证同样必须回流。

如果某条候选能力在真实 adoption 中失败，至少要写清：

- 失败发生在哪类样本
- 失败是因为样本不匹配，还是因为 Loom 规则本身有问题
- 它应该降级为 `adapt`、维持 `needs_validation`，还是进入 `drop`

## 6. 与核心文档的映射

经验回流不应只更新 `adoption/`。

一旦结论已经改变 Loom 的默认判断，还必须同步更新：

- `skills/loom-init/**`
- `skills/distribution-and-adapter-contract.md`
- 相关 `governance/`、`harness/`、`templates/` 文档

## 7. 与 issue 关闭的关系

issue 的完成判断至少要求：

- 对应经验已经进入版本化文档
- `extraction-ledger.md` 与 `landing-map.md` 已同步
- 相关核心文档已更新
- issue 中的结论不再依赖会话上下文补齐

若结论最终仍停留在 `adapt` 或 `needs_validation`，只要理由、落点和关闭依据都已写清，issue 仍然可以关闭。
