# Lightweight Retrofit Default

本文件定义 Loom 面向小型既有仓库的默认 retrofit 策略。

它来自 `mail-listener` 的第一轮真实 adoption 验证。

## 1. 适用场景

当目标仓库同时满足以下条件时，默认采用本策略：

- 已有清晰的工程边界文档，例如 `AGENTS.md`
- 已有 CI 与基础测试
- 当前缺的是治理入口、review 合同或条件化 spec 路径
- 当前还没有明显的长任务恢复痛点

## 2. 默认目标

第一轮 retrofit 的目标不是装完整 Loom，而是先建立最小治理闭环。

默认先解决：

- 改动如何进入实现
- reviewer 如何判断改动
- 哪些边界改动必须先说明再实现

## 3. 默认装配

本策略默认优先装配：

- `WORKFLOW`
- `code_review`
- `spec_review`
- 最小 PR 模板
- 条件化 `spec.md` / `plan.md`

## 4. 默认接入方式

如果目标仓库已经有稳定的根级边界文档，默认采用 `companion docs` 接入：

- 保留原有根规则文档
- 只追加治理伴随文档与职责映射
- 不在第一轮重写整个根级规则体系

## 5. 默认不装配

第一轮默认不装配：

- 完整 recovery 模型
- work item 合同
- 状态面
- profile 分层
- 重 harness

## 6. checkpoint-lite

如果事项会跨多轮推进，但还不值得引入独立恢复工件，允许先采用 `checkpoint-lite`：

- 在 issue 或 PR 描述中记录当前停点
- 在 issue 或 PR 描述中记录下一步
- 在 issue 或 PR 描述中记录阻断项

这是一种轻量过渡形态，不等于永久替代 recovery 模型。
