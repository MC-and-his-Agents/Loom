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
- `EXT-0036` 的治理侧部分

## 4. Harness 子系统

执行方案的完整定义，见 [harness-design.md](./harness-design.md)。

更细的稳定规则，见：

- [harness/execution-context.md](./harness/execution-context.md)
- [harness/workspace-model.md](./harness/workspace-model.md)
- [harness/recovery-model.md](./harness/recovery-model.md)
- [harness/status-surface.md](./harness/status-surface.md)
- [harness/automation-frontload.md](./harness/automation-frontload.md)
- [harness/workspace-and-purity.md](./harness/workspace-and-purity.md)
- [harness/work-item-contract.md](./harness/work-item-contract.md)

`harness` 负责定义：

- 仓库如何初始化到可执行状态
- 执行上下文如何绑定
- 工作现场如何建立和隔离
- 多轮事项如何 checkpoint、resume、handoff
- 每轮执行前后应读取和回写什么
- 当前状态和运行事实如何被读取
- 哪些检查应前置到脚本或 CI
- merge gate 在执行侧如何放行

Loom 将以下能力视为 harness 内核：

- 初始化机制
  - 初始化入口、初始化步骤、初始工件和初始 clean state
- 初始化产物
  - 首批能力清单
  - 首批事项清单
  - 初始化脚本或等价入口
  - 初始 checkpoint / progress 载体
- 执行上下文
  - 当前事项、路径、目标、工作现场、恢复入口、当前 checkpoint
- 工作现场机制
  - 单现场单事项
  - 现场可恢复定位
- 恢复机制
  - `checkpoint`
  - `resume`
  - `handoff`
  - 唯一恢复主入口
- 每轮读取与每轮回写
  - 先读 progress / checkpoint
  - 先读最近 git 历史
  - 单轮只推进一个清晰单元
  - 结束时回写进度、验证和下一步
- 状态与运行时可见性
  - 当前事项、停点、下一步、阻断项
  - 日志、指标、trace 或等价诊断信息
  - UI 或端到端结果可被 agent 直接验证
- 自动化前置
  - 结构完整性
  - 文档和模板存在性
  - 交叉链接与知识结构检查
  - 纯度与明显越界信号
- merge gate
  - 只承担执行放行，不承担第一次高质量语义判断

总图中特别强调的能力包括：

- 运行时可见性与 agent 可验证性
- 仓库知识结构、模板和执行支撑的机械化校验
- initializer 的结构化输出
- 单单元增量推进
- 每轮读取 progress 与 git 历史、每轮回写进度与验证

这几项能力在提取台账中对应：

- `EXT-0035`
- `EXT-0036`
- `EXT-0037`
- `EXT-0038`

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
