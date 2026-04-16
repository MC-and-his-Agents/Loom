# Loom System Design

## 1. 文档定位

本文档是 Loom 的系统总图。

它只回答四件事：

- Loom 由哪些系统部分组成
- 每个部分负责什么
- 它们之间如何依赖和协同
- 详细定义分别落在哪些文档

本文档不承接以下内容：

- 愿景与价值判断
  - 见 [VISION.md](./VISION.md)
- 当前阶段、推进顺序、进度状态
  - 见 [docs/roadmap.md](./docs/roadmap.md)
- 多仓提取证据与落点台账
  - 见 [adoption/extraction-ledger.md](./adoption/extraction-ledger.md)
  - 见 [adoption/landing-map.md](./adoption/landing-map.md)

## 2. 系统总图

从愿景层看，Loom 是三层系统：

- `governance`
- `harness`
- `skills`

从仓库实现层看，Loom 由五个稳定部分协同组成：

- `governance`
  - 制度与判断规则
- `harness`
  - 执行支撑与运行可见性
- `templates`
  - 结构化工件与条件化模板
- `skills`
  - 装配入口与执行入口
- `adoption`
  - 多仓提取证据、落点映射与接入方法

其中：

- `governance` 和 `harness` 是系统内核
- `templates` 是结构承载层
- `skills` 是入口层
- `adoption` 是证据与演化层

`skills` 不拥有规则真相，也不拥有执行真相。
`adoption` 不直接替代运行规则，它负责证明能力从哪里来、为什么成立、当前落在哪里。

## 3. Governance 子系统

治理方案的完整定义，见 [governance-design.md](./governance-design.md)。

更细的稳定规则，见：

- [governance/principles.md](./governance/principles.md)
- [governance/review-model.md](./governance/review-model.md)
- [governance/maturity-and-closing.md](./governance/maturity-and-closing.md)

`governance` 负责定义：

- 一件事如何进入执行
- 哪些事项可以直接实现
- 哪些事项必须先说明再实现
- 正式审查在什么时点发生
- 事项如何进入下一阶段
- 什么状态才算真正完成

Loom 将以下能力视为治理内核：

- 真相源分层
  - 调度真相与仓库语义真相分开
- 载体职责分离
  - Issue、Project、PR、规则文档、规格文档、执行工件各自承担单一职责
- 受控入口与事项分流
  - 轻量事项、中等事项、边界事项走不同路径
- 规格准入
  - 高影响改动先收口再实现
- 三个正式 checkpoint
  - `commit checkpoint`
  - `build checkpoint`
  - `merge checkpoint`
- 审查职责分层
  - 作者、reviewer、自动检查、merge gate 各负其责
- 成熟度与关闭语义
  - 说明完成、实现进行中、合并就绪、进入主干并收口必须区分
- 仓库知识库模型
  - 短入口文档加深知识文档，而不是超大单文件
- 机械化治理能力
  - 规则落点、知识结构、核心引用关系应逐步可检查

总图中特别强调的能力包括：

- 短 `AGENTS.md` 加深知识库结构
- 规则与知识结构的机械化校验

这两项能力在提取台账中对应：

- `EXT-0034`

## 4. Harness 子系统

执行方案的完整定义，见 [harness-design.md](./harness-design.md)。

该文档负责定义：

- 初始化与装配
- 稳定组件之间如何组成执行支撑系统
- harness 强度模型

更细的稳定组件合同，见：

- [harness/work-item-contract.md](./harness/work-item-contract.md)
- [harness/execution-context.md](./harness/execution-context.md)
- [harness/execution-chain.md](./harness/execution-chain.md)
- [harness/workspace-model.md](./harness/workspace-model.md)
- [harness/recovery-model.md](./harness/recovery-model.md)
- [harness/status-surface.md](./harness/status-surface.md)
- [harness/automation-frontload.md](./harness/automation-frontload.md)
- [harness/merge-checkpoint.md](./harness/merge-checkpoint.md)
- [harness/workspace-and-purity.md](./harness/workspace-and-purity.md)

当某项能力已经下沉到稳定组件时，以对应组件文档为准；`harness-design.md` 不重复字段级规则、执行阶段顺序或放行输入细节。

`harness` 负责定义：

- 仓库如何初始化到可执行 clean state
- 正式事项如何以 work item 进入执行
- 每轮读取、隔离现场推进、回写、验证汇总与 merge checkpoint 如何形成闭环
- 当前状态和运行事实如何被读取
- 哪些检查应前置到脚本或 CI
- merge checkpoint 在执行侧如何承接放行与回退

Loom 将以下能力视为 harness 内核：

- 方案级能力
  - 初始化场景、初始化产物和初始 clean state
  - 稳定组件的装配关系与强度模型
- 稳定组件
  - `work-item-contract`
    - 正式执行单元与 `exec-plan` 职责
  - `execution-context`
    - 当前事项、路径、目标、范围、工作现场、恢复入口、当前 checkpoint、验证入口
  - `execution-chain`
    - 从初始化产物到 merge checkpoint 放行的最小执行链路
  - `workspace-model` 与 `workspace-and-purity`
    - 隔离现场、单现场单事项与纯度预检
  - `recovery-model`
    - `checkpoint`、`resume`、`handoff` 与唯一恢复主入口
  - `status-surface`
    - 当前事项、停点、下一步、阻断项、最近验证摘要与运行时证据入口
  - `automation-frontload`
    - 结构、规则落点、模板、交叉引用、纯度信号与执行支撑入口的前置检查
  - `merge-checkpoint`
    - 放行输入、结果语义与回退承接

总图中特别强调的能力包括：

- `EXT-0035`
  - 由 [harness/status-surface.md](./harness/status-surface.md) 与 [skills/loom-init/references/output-contract.md](./skills/loom-init/references/output-contract.md) 共同承接状态读取与运行时可见性
- `EXT-0036`
  - 由 [harness/automation-frontload.md](./harness/automation-frontload.md) 承接 harness 侧机械化校验边界
- `EXT-0037`
  - 由 [harness/work-item-contract.md](./harness/work-item-contract.md)、[harness/workspace-model.md](./harness/workspace-model.md)、[harness/execution-chain.md](./harness/execution-chain.md)、[harness-design.md](./harness-design.md) 与 [skills/loom-init/references/output-contract.md](./skills/loom-init/references/output-contract.md) 共同承接 initializer 产物、初始 `progress` 与 clean state
- `EXT-0038`
  - 由 [harness/execution-chain.md](./harness/execution-chain.md)、[harness/execution-context.md](./harness/execution-context.md)、[harness/work-item-contract.md](./harness/work-item-contract.md)、[harness/recovery-model.md](./harness/recovery-model.md) 与 [skills/loom-init/references/output-contract.md](./skills/loom-init/references/output-contract.md) 共同承接每轮读取、回写和单单元推进

## 5. Templates 子系统

模板层的详细定义，见：

- [templates/spec-suite.md](./templates/spec-suite.md)
- [templates/pull-request.md](./templates/pull-request.md)

`templates` 不定义治理真相，它只把治理和 harness 的要求压成稳定结构。

模板层负责承接：

- 正式规格模板
  - `spec.md`
  - `plan.md`
- PR 模板
  - 最小事实集
  - 条件触发块
- 其他结构化执行工件
  - 只在对应场景下启用，不默认一刀切铺满

模板层的设计边界是：

- 承载结构
- 不垄断规则
- 不制造第二真相源

## 6. Skills 子系统

入口层的详细定义，见：

- [skills/README.md](./skills/README.md)
- [skills/loom-init/SKILL.md](./skills/loom-init/SKILL.md)

`skills` 负责把 Loom 的稳定能力装配成可直接执行的入口。

它至少承担四类职责：

- 场景识别
  - 判断是新项目、已有小仓库，还是复杂既有仓库
- 能力选择
  - 决定应启用哪些治理、harness 和模板组件
- 初始化输出
  - 产出首批工件、首批事项、checkpoint 策略和验证入口
- 日常入口
  - 逐步形成初始化、执行、审查、收口等统一入口

`skills` 的边界同样明确：

- 不反向定义治理规则
- 不替代恢复工件
- 不替代状态真相

## 7. Adoption 证据层

`adoption` 不是运行时内核，但它是 Loom 能否持续成立的证据层。

它负责三件事：

- 记录能力从哪些真实仓库和文章提取而来
- 记录每条能力当前落在哪个 Loom 文件中
- 记录不同仓库场景下的接入方法和候选模式

关键文档包括：

- [adoption/extraction-ledger.md](./adoption/extraction-ledger.md)
  - 稳定提取结论
- [adoption/landing-map.md](./adoption/landing-map.md)
  - 条目到仓库落点的映射
- [adoption/routing-and-checkpoints.md](./adoption/routing-and-checkpoints.md)
  - 事项路径与 checkpoint 方法
- [adoption/rationale.md](./adoption/rationale.md)
  - Loom 为什么存在

## 8. 依赖关系

Loom 的系统依赖应保持单向清晰：

1. `governance`
   定义规则、审查与关闭语义。
2. `templates`
   承接 `governance` 和 `harness` 需要的结构化工件。
3. `harness`
   在治理约束下，提供执行上下文、恢复、状态和自动化支撑。
4. `skills`
   读取 `governance`、`harness`、`templates`、`adoption`，把能力装配成入口。
5. `adoption`
   为上述能力提供提取证据、落点映射和后续演化依据。

不允许出现以下反向关系：

- `skills` 反向定义规则
- 模板层承担唯一治理真相
- 状态面成为第二套事项真相
- `system-design.md` 混入阶段进度和当前执行状态

## 9. 一句话总结

Loom 不是一组散落文档。

Loom 是一套把治理规则、执行支撑、结构化模板、入口装配和多仓证据连成闭环的项目运行系统。
