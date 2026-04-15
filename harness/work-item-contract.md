# Work Item Contract

本文件定义 Loom 当前最小 work item / exec-plan 合同。

## 1. work item 是执行入口

进入正式执行的事项，必须有可追踪的 work item。

默认要求：

- 一个 work item 对应一个清晰目标
- work item 必须能映射到当前执行路径
- work item 必须能指向相关正式工件或简化设计说明

## 2. 最小 work item 结构

一个可执行的 work item 至少应表达：

- 事项标识
- 目标
- 范围
- 当前执行路径
- 当前 checkpoint 状态
- 关联工件
- 关闭条件

## 3. exec-plan 的职责

如果项目使用 `exec-plan`，其职责应限制为执行与恢复。

默认要求：

- 记录当前停点
- 记录下一步
- 记录已验证事实
- 记录阻断项
- 记录与正式工件的关联

禁止事项：

- 用 `exec-plan` 替代正式需求真相
- 用 `exec-plan` 替代长期状态真相

## 4. 与分流路径的关系

不同执行路径对应不同最小输入：

- 轻量事项
  - work item 可直接进入实现与 PR
- 中等事项
  - work item 应关联简化设计说明
- 正式规约事项
  - work item 应关联 `spec.md` 与 `plan.md`

## 5. Loom 当前约束

Loom 当前要求：

- work item 是执行入口
- `exec-plan` 是执行与恢复工件，不是规则真相源
- 不同路径有不同最小输入，但都必须能被 checkpoint 与恢复
