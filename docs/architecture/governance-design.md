# Loom Governance Design

## 1. 文档定位

本文档是 Loom 治理方案总览。

它负责：

- 定义完整治理方案的结构
- 说明治理组件如何协同
- 提供组件级真相源索引

它不承接组件级规则全文。

治理规则真相源在：

- [../methodology/governance/principles.md](../methodology/../methodology/governance/principles.md)
- [../methodology/governance/review-model.md](../methodology/../methodology/governance/review-model.md)
- [../methodology/governance/maturity-and-closing.md](../methodology/../methodology/governance/maturity-and-closing.md)

## 2. 治理目标

Loom 治理方案要同时满足五个目标：

1. 让事项进入执行前先被正确分类
2. 让高影响改动在实现前完成必要收口
3. 让中途偏航在 build 阶段被识别和纠偏
4. 让 merge checkpoint 专注放行，而不是第一次理解事项
5. 让事项状态、文档状态、审查状态和主干状态最终一致

## 3. 方案结构

Loom 治理内核由三个稳定组件构成：

- `principles`
  - 定义真相源分层、入口分流、规格准入、知识库模型与机械化治理边界
- `review-model`
  - 定义审查职责分层、三个 checkpoint 审查分工、最小必要上下文与回退规则
- `maturity-and-closing`
  - 定义事项成熟度阶段、关闭一致性条件与关闭反模式

## 4. 事项模型与入口

Loom 默认采用三类事项分流：

- 轻量事项
- 中等事项
- 边界事项

事项进入执行的默认顺序是“先分类、再判定准入、再进入实现”。

权威规则见 [../methodology/governance/principles.md](../methodology/../methodology/governance/principles.md)。

## 5. 规格准入

边界事项默认必须先说明再实现，最小工件为 `spec.md` 与 `plan.md`。

规格准入触发条件与准入问题定义见 [../methodology/governance/principles.md](../methodology/../methodology/governance/principles.md)。

## 6. 三个正式 checkpoint

治理层固定三个正式 checkpoint：

- `admission checkpoint`
- `build checkpoint`
- `merge checkpoint`

每个 checkpoint 的审查职责分工与回退规则见 [../methodology/governance/review-model.md](../methodology/../methodology/governance/review-model.md)。

## 7. 审查职责分层

Loom 审查模型固定四类角色：

- 作者
- reviewer
- 自动检查
- merge gate

角色边界、最小上下文与基线规则见 [../methodology/governance/review-model.md](../methodology/../methodology/governance/review-model.md)。

## 8. 成熟度与关闭语义

Loom 关闭语义与事项成熟度绑定。

说明完成、实现进行中、合并就绪、主干收口属于不同阶段；只有进入主干并收口才算事项完成。

权威规则见 [../methodology/governance/maturity-and-closing.md](../methodology/../methodology/governance/maturity-and-closing.md)。

## 9. 真相源与知识库模型

治理要求调度真相与仓库语义真相分层，并要求载体职责单一。

治理还要求短入口文档与深知识文档分层组织，避免规则散落和重复维护。

权威规则见 [../methodology/governance/principles.md](../methodology/../methodology/governance/principles.md)。

## 10. 机械化治理能力

治理内核不仅定义规则，也要求规则逐步可被机械检查，包括：

- 规则落点存在性
- 核心结构完整性
- 关键引用可达性
- 明显职责越界信号

权威规则见 [../methodology/governance/principles.md](../methodology/../methodology/governance/principles.md)。

## 11. 与 Harness 的边界

本文件不定义执行现场、恢复机制、状态桥接和脚本化前置能力；这些属于 `harness-design.md` 与 `harness/`。

治理负责“做什么判断、何时判断、由谁判断”，harness 负责“如何把这些判断变成可运行执行机制”。

## 12. 一句话总结

`governance-design.md` 负责完整方案结构，`governance/*.md` 负责稳定规则真相；两者协同但不重复维护全文。
