# Spec Suite

本文件定义 Loom 当前最小正式规约套件。

本文件当前承接：

- `EXT-0015`
- `EXT-0016`
- `EXT-0017`
- `#649`

## 1. 正式规约套件的最小边界

Loom 当前把正式规约套件的最小内核定义为：

- `spec.md`
- `plan.md`

这两个工件分别承担不同职责，不得混写。

Formal spec path 有两条合法 suite path：

- `minimal suite`
  - 必含 `spec.md` 与 `plan.md`
  - 适用于低风险、局部、纯治理或文档类事项
  - 可用 `not_applicable` rationale 合法跳过 full path 附加工件
- `full suite`
  - 在 minimal suite 之上消费 suite-index、条件附加工件、evidence-map、
    consistency-analysis 与 gate-chain consumption
  - 适用于 formal spec、高风险、跨模块、强 review 或需要完整证据链的事项

路径选择必须有 locator 与 provenance。若从 full path 降到 minimal path，必须说明
附加工件为什么 `not_applicable`；若从 minimal path 升到 full path，必须说明触发信号
和需要补齐的工件。

## 2. `spec.md` 最小要求

`spec.md` 至少应表达：

- 目标
- 范围
- 关键场景，优先使用 `GWT`
- 异常与边界
- 验收标准

`spec.md` 承接 BDD 外环。它描述可观察行为，不描述内部实现步骤：

- `Given` 固定当前用户、系统或治理对象的起点
- `When` 固定触发动作或宿主事件
- `Then` 固定可验证结果、状态变化或 gate 消费结果
- 每个关键场景都应能映射到后续行为证据；若纯文档事项不适用，应显式说明 `not_applicable`
- 若存在 User Story，`spec.md` 只消费 story scenario id / locator 与业务可读 GWT，不复制 story 为第二事实源
- 若 User Story 涉及业务语义，`spec.md` 必须记录 `Story Business Confirmation` locator 或 `not_applicable` rationale；`pending` 或 `revision-requested` 不得进入 formal spec shaping

## 3. `plan.md` 最小要求

`plan.md` 至少应表达：

- 实施目标
- 阶段拆分
- 约束
- 验证方式
- `TDD` 或测试策略
- 依赖关系
- 进入实现前条件

`plan.md` 承接 TDD 内环。它把 `spec.md` 的行为场景转成实现推进与测试证据计划：

- 每个关键行为场景应声明将由哪些测试、检查、人工验证或运行证据覆盖
- 若场景来自 User Story，`plan.md` 应保留 story scenario id 到验证策略的映射
- 若场景来自 User Story，`plan.md` 只能基于已确认或明确 `not_applicable` 的 story 语义规划验证，不要求用户判断实现方案或测试策略
- 能自动化的行为先写或先调整失败用例，再实现，再以通过结果作为 test evidence
- 不能自动化的行为必须声明人工验证路径、证据 locator 与 fresh 条件
- 纯文档或治理规则变更可以不强制 TDD，但必须说明行为证据如何由结构检查、审查记录或示例消费

映射状态必须可被后续 gate 消费：

- `scenario_id` / scenario locator 映射到 automated、manual、structural 或
  `not_applicable` validation strategy
- `acceptance_id` / acceptance locator 映射到 test evidence、structural check、
  manual evidence 或 `not_applicable`
- full path 下，缺少 scenario -> validation 或 acceptance -> test mapping 默认阻断
  build / review
- minimal path 下，缺映射必须以 `not_applicable` rationale、替代验证入口和
  recheck condition 解释

## 4. 套件边界规则

Loom 必须区分：

- 正式契约工件
- 执行或进度工件

默认要求：

- `spec.md` 与 `plan.md` 属于正式最小套件
- 进度跟踪类工件是否存在，可以按项目需要扩展

Loom 当前不固化：

- 所有项目都必须有同一组附加工件
- `TODO.md` 或同类文件是永恒必选项

Full path 缺少必需工件、locator、provenance 或 gate 所需 evidence 时必须
fail-closed。Minimal path 缺少 full path 附加工件时，只有同时具备 rationale、
consumer boundary 与 recheck condition 的 `not_applicable` 才能消解；无理由缺口
仍是 `missing`。`deferred` 不等于 `not_applicable`，不得作为 completed truth 消费。

## 5. 行为证据与测试证据

正式规约套件必须让后续 gate 能区分两类证据：

- `behavior evidence`
  - 证明 `spec.md` 中可观察场景已经成立
- `test evidence`
  - 证明 `plan.md` 中约定的自动化、回归或人工验证路径已经执行

两类证据可以来自同一运行记录，但消费语义不同：

- review 消费它们来判断实现是否覆盖行为契约
- merge-ready 消费它们来判断当前 `HEAD` 是否仍有 fresh verification evidence
- closeout 消费它们来判断进入主干后的结果是否足以支持 `absorbed` / `closed_out`

## 6. 与 Execution Ledger 的映射

正式规约套件只提供 locator / evidence 输入，不维护恢复状态。

默认映射如下：

| 模板输出 | ledger 字段 | 归属边界 |
| --- | --- | --- |
| `spec.md` 的验收标准与行为证据 | `acceptance_locator` | 只说明验收和行为证据入口 |
| `plan.md` 的阶段、验证方式与测试策略 | `plan_locator` | 只说明执行计划入口 |
| checkpoint / review / gate 输出 | `validation_evidence_locator` | 只说明验证证据入口 |
| `handoff` 输出或交接说明 | `handoff_notes_locator` | 只说明交接入口 |

若存在 story intake，User Story locator 与 Story Business Confirmation locator 只能作为 `spec.md` / `plan.md` 的上游来源记录，不能进入 execution ledger 替代 `acceptance_locator`、`plan_locator` 或恢复状态。

纯文档事项可在对应字段声明 `not_applicable`，但必须与 spec / plan / recovery 中的事实不冲突。

模板不得 authored `next_step`、`blockers`、`latest_validation_summary`。这些字段只能由 recovery 主入口维护，再由 fact-chain、resume、handoff 与 merge-ready 消费。
