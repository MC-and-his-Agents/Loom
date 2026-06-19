# Validation: AGENTS Classify Before Execute

## Goal

验证 `AGENTS.md` 已新增“先分类再执行”的短原则，并且该原则仍保持跨项目适用，不依赖 Loom 专属 gate、schema、事故编号或命令流水账。

## Scope

本记录只覆盖：

- 原则要求先判断范围、风险、外部可见性与验证确定性，再选择执行路径与验证梯度
- 文案不把“小改动”或“文档改动”等同于天然轻量路径
- 文案不弱化 review、事实链、release / no-release 或 closeout
- 详细档位、映射和 gate 语义继续留在治理方法论文档，而不是回塞进 AGENTS

## Review Note

自审结论：通过。新增原则保持短、稳定、可跨项目复用，只冻结“先分类再执行”的纪律，不新增流程、字段或实现承诺。
