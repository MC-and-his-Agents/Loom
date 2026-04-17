# Loom Roadmap

## 1. 文档定位

本文件定义 Loom 从零到目标状态的完整建设路线。

它只回答：

- Loom 要经过哪些阶段
- 每个阶段要建立什么能力
- 每个阶段的完成判断是什么
- 阶段之间如何衔接

本文件不承接以下内容：

- 当前正在做哪一个 issue
- 当前阶段的实时状态
- 哪个任务已完成、进行中或阻塞
- GitHub Project、issue、PR 的执行细节

这些频繁变化的信息，应由 GitHub issues、Project 或其他执行载体承接。

## 2. 目标状态

Loom 的目标不是只拥有一组文档，而是形成一套以 `merge-ready` 为中心、完整、可复用、可升级的治理与执行编排系统。

本轮先冻结目标态与职责边界；具体实现拆分、脚本补齐、门禁接线与宿主集成由后续 issue / PR 承接。

目标状态至少包括：

- `Governance Truth`
  - 事项入口、事项分流、规格准入、状态机、checkpoint、审查模型、成熟度与关闭语义清晰稳定
  - issue / project / PR / 仓库工件各自承接什么真相有明确边界
- `Harness Orchestration`
  - 初始化、执行上下文、工作现场、恢复模型、状态面、运行时可见性、自动化前置清晰稳定
  - review、guardian、CI、merge gate、closeout 形成分层流程，不再把 final review 当作第一次系统性发现问题的地方
  - GitHub、`gh`、branch / PR / `git worktree`、review engine 与其他宿主能力可以被 Loom 统一编排和消费
  - 高频执行动作、checkpoint 承接、工作现场治理、truth sync 与 gate 入口有稳定脚本或等价自动化入口
- `Executable SKILLS`
  - `SKILLS` 不再只是选择和说明入口，而是场景化一等执行面
  - 人和 agent 可以显式或隐式进入 adopt、resume、pre-review、handoff、retire、merge-ready 等动作
- 结构化模板体系
  - 正式规约模板、PR 模板和条件化模板块清晰稳定
- 多仓验证闭环
  - 能力不是停留在理念层，而是经过真实仓库验证、修正和沉淀
- 可升级能力内核
  - Loom 能脱离单一业务仓库独立演进，并为下游仓库提供升级路径

## 3. 阶段总览

Loom 从零到目标状态，按以下阶段推进：

1. `Phase A`
   冻结目标态与职责边界
2. `Phase B`
   把目标态收敛为稳定能力组件与仓库结构
3. `Phase C`
   建立场景化可执行入口与接入能力
4. `Phase D`
   建立执行编排、宿主集成与 merge-ready 支撑
5. `Phase E`
   完成多场景验证、版本化演进与上游交付

这些阶段表达的是能力建设顺序，不表达实时执行状态。

## 4. Phase A：冻结目标态与职责边界

这一阶段的目标，是先把 Loom 要成为怎样的系统用语言和边界定义清楚。

核心产出：

- 三层目标态
  - `Governance Truth`
  - `Harness Orchestration`
  - `Executable SKILLS`
- 宿主边界
  - GitHub、CI、review engine、`gh`、branch / PR / `git worktree` 等对象哪些进入 Loom 编排、哪些保留为宿主底层能力
- merge-readiness-centered 路线
  - review、guardian、CI、merge gate、closeout 的层级关系清晰
- 文档边界
  - `VISION.md`、`system-design.md`、`AGENTS.md`、`roadmap.md` 各自职责清楚
- 上游来源映射
  - `Syvert`
  - `WebEnvoy`
  - OpenAI / Anthropic 文章中的有效实践，已映射为目标能力

完成判断：

- Loom 的三层目标态已经可以被完整描述
- 系统总图与详细设计的分工已经清楚
- 目标态冻结与后续实现拆分的边界已经清楚

## 5. Phase B：收敛为能力组件

这一阶段的目标，是把完整方案收成稳定组件，而不是继续停留在抽象描述层。

核心产出：

- `governance/`
  - 原则
  - 状态机
  - 审查模型
  - 成熟度与关闭语义
- `harness/`
  - 执行上下文
  - 工作现场
  - 恢复模型
  - 状态面
  - 宿主编排
  - 自动化前置
  - 纯度与范围控制
- `skills/`
  - root entry
  - 场景 `SKILLS`
  - 路由与升级合同
- `templates/`
  - 正式规约模板
  - PR 模板
- `adoption/`
  - 提取台账
  - 落点映射
  - 接入路径
  - 候选模式

完成判断：

- 主要能力不再只存在于总文档中
- 每类能力已有稳定落点和职责边界
- 提取证据、目标能力和仓库落点之间可以互相映射

## 6. Phase C：建立可执行入口与接入能力

这一阶段的目标，是让 Loom 不只是“被阅读”，而是“能被场景化调用并接入”。

核心产出：

- root skill
  - 能识别新项目、小型既有仓库、复杂既有仓库，并把执行者路由到正确场景
- 场景 `SKILLS`
  - adopt
  - resume
  - pre-review
  - handoff
  - retire
  - merge-ready
- 初始化输出合同
  - 首批工件
  - 首批事项
  - checkpoint 策略
  - 验证入口
- companion docs 接入路径
  - 对已有根规则文档的仓库，优先伴随接入而不是重写根规则

完成判断：

- Loom 已经具备明确的初始化与场景执行入口
- 不同仓库场景下的默认接入方式已经能被稳定表达并路由
- 下游仓库可以基于 Loom 开始第一轮接入，而不是只能人工理解整套文档

## 7. Phase D：建立执行编排、宿主集成与 merge-ready 支撑

这一阶段的目标，是把 Loom 的 harness 从“设计上成立”推进到“形成完整执行编排内核”。

核心产出：

- 初始化产物模型
  - 能定义首批能力清单、首批事项、初始 progress 和 clean state
- 每轮执行模型
  - 先读 progress / checkpoint
  - 先读最近 git 历史
  - 单轮推进单一清晰单元
  - 结束时回写进度与验证
- review 分层模型
  - pre-review
  - 正式 review / guardian
  - merge-ready
  - merge gate
- checkpoint 工程化
  - `admission checkpoint`、`build checkpoint`、`merge checkpoint` 都有明确承接工件、输入输出和回退去向
- 工作现场生命周期
  - 创建、定位、恢复、清理与 retire 有稳定入口
- 宿主对象编排
  - issue / project / PR / branch / `git worktree` / CI / review engine / closeout 的入口、结果语义与回退边界清晰
- 自动化前置能力
  - 结构完整性检查
  - 规则落点检查
  - 模板存在性检查
  - 交叉引用检查
  - 纯度与明显越界信号检查
  - 活跃状态一致性与 checkpoint 完整性检查
- 运行时可见性能力
  - 日志、指标、trace 或等价诊断信息可读取
  - UI 或端到端结果可验证
- 日常执行入口
  - `bootstrap`、`verify`、`checkpoint`、`resume`、`handoff`、`review`、`merge`、`retire` 等高频动作有稳定入口

完成判断：

- Loom 已不再停留在最小机械能力，而是形成可重复使用的完整执行编排内核
- 自动化前置不只检查代码，还覆盖知识结构和执行支撑
- `admission checkpoint`、`build checkpoint`、`merge checkpoint` 都有稳定承接，不再主要依赖临场解释
- harness 已覆盖“初始化、执行、恢复、review、merge-ready、放行、closeout、现场治理”这一完整链路

## 8. Phase E：完成验证、升级与上游交付

这一阶段的目标，是让 Loom 从“内部设计”变成“可持续复用的上游能力”。

核心产出：

- 多仓验证
  - 新项目验证
  - 小型既有仓库验证
  - 复杂既有仓库验证
- 经验回流机制
  - 下游实践能稳定回流到 `adoption/` 和能力组件
- 版本化与升级路径
  - Loom 组件可独立演进
  - 下游仓库可以按版本升级，而不是手工复制
- 上游交付形态
  - 文档、模板、入口、脚本、宿主编排边界和能力边界形成稳定发布面
  - 完整执行内核中的通用脚本与 gate 入口进入稳定交付面

完成判断：

- Loom 已不依赖单一试验仓库才能成立
- Loom 的能力可以被多个真实仓库重复使用
- Loom 已具备持续演进和对下游输出升级路径的能力

## 9. 阶段关系

这些阶段之间是递进关系：

- `Phase A`
  - 先冻结目标态与职责边界，避免后续能力建设失去目标
- `Phase B`
  - 再把目标态落成稳定组件，避免所有规则混在少数总文档里
- `Phase C`
  - 再建立可执行入口与接入能力，避免 Loom 只能被阅读，不能被调用
- `Phase D`
  - 再建立执行编排、宿主集成与 merge-ready 支撑，避免 harness 只停留在概念上
- `Phase E`
  - 最后通过多仓验证和版本化，把 Loom 变成真正的上游系统

## 10. 与执行层的关系

`roadmap.md` 只定义长期阶段路线。

执行层应另行承接：

- 当前阶段正在推进什么
- 当前阶段下有哪些 issue
- 哪些事项正在进行中
- 哪些事项被阻塞
- 哪些事项已经完成
- 哪些 GitHub / 宿主控制面动作已经生效

换句话说：

- `roadmap.md`
  - 回答“Loom 从零到目标状态要经过什么阶段”
- GitHub issues / Project
  - 回答“Loom 此刻正在做什么”
