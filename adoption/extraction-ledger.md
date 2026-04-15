# Loom Extraction Ledger

## 目的

这份台账用于从 `Syvert`、`WebEnvoy` 以及后续更多真实仓库中，提取可上移到 Loom 的知识、资产、机制和经验教训。

它的目标不是复制文件，而是回答四个问题：

1. 哪些原则已经被真实项目验证过。
2. 哪些机制可以抽成可复用的 `harness` 能力。
3. 哪些工件应成为模板、采用输入或 `SKILLS` 入口的一部分。
4. 哪些摩擦、反模式和失败教训必须被 Loom 主动避免。

## 使用规则

- 一条记录只表达一个清晰结论，不混合多个判断。
- 优先记录“为什么成立”与“为什么不应直接上移”，而不是只记录结果。
- 没有证据的判断不直接进入 Loom 内核。
- 单一仓库观察到的经验，默认标记为 `needs_validation`，除非它明显属于局部资产整理而不是上游原则。
- 当同一结论被多个仓库支持时，优先提升为 Loom 候选内核。

## 字段定义

每条记录至少包含以下字段：

- `id`
  - 稳定标识，格式建议为 `EXT-0001`
- `source`
  - 原始来源，指向文件、脚本、PR、Issue、会话记录或人工归纳入口
- `evidence_source`
  - `syvert` / `webenvoy` / `both`
- `type`
  - `principle` / `mechanism` / `artifact` / `lesson` / `anti_pattern`
- `statement`
  - 被提取的核心结论，只写一条
- `evidence`
  - 支撑该结论的事实、现象、验证或反复出现的问题
- `reuse_level`
  - `general` / `configurable` / `repo_specific`
- `loom_target`
  - `governance` / `harness` / `skills` / `adoption` / `template`
- `status`
  - `keep` / `adapt` / `drop` / `needs_validation`
- `notes`
  - 额外说明，包括为什么暂不上移、需要什么第二证据、有哪些局限

## 判定规则

### `type`

- `principle`
  - 上位原则，例如真相源划分、事项入口规则、职责分层
- `mechanism`
  - 落地机制，例如 `exec-plan`、checkpoint / resume、merge gate
- `artifact`
  - 载体与模板，例如 `spec.md`、`plan.md`、handoff 模板
- `lesson`
  - 被真实推进过程验证过的经验
- `anti_pattern`
  - 反复出现、应被 Loom 主动避免的模式

### `reuse_level`

- `general`
  - 大概率可作为 Loom 默认能力
- `configurable`
  - 适合保留，但应参数化或按场景启用
- `repo_specific`
  - 明显依赖原仓库语义，不应直接上移

### `status`

- `keep`
  - 可以直接进入 Loom 候选内核
- `adapt`
  - 值得保留，但需要抽象、去项目化或降复杂度
- `drop`
  - 不建议进入 Loom
- `needs_validation`
  - 暂不固化，等待更多仓库或更多证据

## 输出目标

这份台账最终应支持三类稳定产物：

1. 知识账本
   - 多仓实践证明了什么
2. 资产清单
   - 哪些文档、模板、脚本、工件可上移
3. 教训与反模式清单
   - Loom 设计时必须主动避免什么

本文件只维护稳定提取结论。

动态执行信息，例如：

- 待补充来源
- 下一步采集动作
- 当前轮推进顺序

不在本文件中维护，应由 `docs/roadmap.md` 或对应 GitHub issues 承接。

补充约束：

- `WebEnvoy` 不是只提供反模式的样本仓库。
- 对 `WebEnvoy` 的提取必须同时记录：
  - 已验证的正向治理结构
  - 已观察到的摩擦、过载点与待优化机制
- Loom 的提取方法是“多仓正反并取”，不是把某个仓库单向当作教材。

## 当前首批候选条目

| id | source | evidence_source | type | statement | evidence | reuse_level | loom_target | status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EXT-0001 | `Syvert/AGENTS.md`, `Syvert/WORKFLOW.md` | `syvert` | `principle` | 调度真相与语义真相应分层存放，而不是混在一个地方。 | `Syvert` 明确将 GitHub 作为调度层、仓库作为语义层，形成较清晰的事项与文档边界。 | `general` | `governance` | `keep` | Loom 应保留这类原则，但不必强绑定某一具体工具名。 |
| EXT-0002 | `Syvert/AGENTS.md`, `docs/process/delivery-funnel.md` | `syvert` | `principle` | 重要工作不应直接从意图进入代码，应通过受控事项进入执行。 | `Syvert` 将 `Work Item` 定义为唯一执行入口，降低了事项边界漂移。 | `general` | `governance` | `keep` | Loom 需保留“受控执行入口”原则，但名称可更通用。 |
| EXT-0003 | `Syvert/docs/exec-plans/**`, `WORKFLOW.md` | `syvert` | `mechanism` | 长任务需要持久工件支持 checkpoint、resume 和 handoff。 | `exec-plan` 在 `Syvert` 中承担了恢复入口、停点记录和风险同步作用。 | `general` | `harness` | `keep` | 这是 Loom 最值得上移的核心 harness 能力之一。 |
| EXT-0004 | `Syvert/spec_review.md`, `code_review.md` | `syvert` | `principle` | 语义审查、自动检查与合并前门禁应职责分层。 | `Syvert` 将 reviewer、CI、guardian 分离，降低了单点混责。 | `general` | `governance` | `keep` | Loom 应继承此原则，但实现强度应可配置。 |
| EXT-0005 | `Syvert` 实践总结 | `syvert` | `lesson` | 治理与业务同仓有高上下文优势，但会削弱治理栈独立演进能力。 | `Syvert` 同时承担业务推进与治理试验场角色，后期出现上游抽离需求。 | `general` | `adoption` | `keep` | 这是 Loom 存在的重要前提，应写入 adoption 理由。 |
| EXT-0006 | `WebEnvoy` 治理优化分析会话 | `webenvoy` | `anti_pattern` | 同一规则散落在多个文档和模板中，会显著抬高维护成本并制造漂移。 | `WebEnvoy` 中规则同时出现在 `AGENTS`、review rubric、PR 模板等多个位置，被识别为明显优化点。 | `general` | `governance` | `keep` | Loom 应尽量建立单一真相源，其他载体只做摘要和引用。 |
| EXT-0007 | `WebEnvoy` 治理优化分析会话 | `webenvoy` | `anti_pattern` | 例外分支和流程类型过多，会显著抬高执行者判断成本。 | `WebEnvoy` 出现普通 PR、formal spec review PR、治理维护 PR 等多类流程，理解成本偏高。 | `general` | `adoption` | `keep` | Loom 需要决策图或引导式入口，而不是让用户先学分类学。 |
| EXT-0008 | `WebEnvoy` 治理优化分析会话 | `webenvoy` | `anti_pattern` | 模板过重会让作者机械填表，降低真实信息密度。 | `WebEnvoy` 的 PR 模板被识别为字段过多，容易出现形式完整、事实稀薄。 | `general` | `template` | `keep` | Loom 模板应从最小事实集出发，再按条件补充。 |
| EXT-0009 | `WebEnvoy` 治理优化分析会话 | `webenvoy` | `lesson` | 能自动判断的规则应尽量前置到脚本或 CI，而不是长期依赖人工审查。 | `WebEnvoy` 的多项阻断条件仍依赖 reviewer 或 guardian 手工判断，被识别为摩擦来源。 | `general` | `harness` | `keep` | Loom 的自动化设计应优先覆盖重复性高、口径稳定的判断。 |
| EXT-0010 | `Syvert` + `WebEnvoy` 综合判断 | `both` | `lesson` | Loom 的目标不应是复制某个仓库，而应提炼多仓实证下成立的运行模型。 | `Syvert` 提供主骨架，`WebEnvoy` 提供精简、去重、降摩擦约束，两者互补。 | `general` | `adoption` | `keep` | 这条应成为 Loom 提取策略的总原则。 |
| EXT-0011 | `Syvert/WORKFLOW.md` | `syvert` | `mechanism` | 进入执行的事项应绑定一组稳定的上下文字段，而不是只靠 Issue 编号。 | `Syvert` 在执行回合中显式绑定 `Issue`、`item_key`、`item_type`、`release`、`sprint`，用于执行、恢复和收口映射。 | `configurable` | `harness` | `adapt` | Loom 应保留“事项上下文绑定”机制，但字段集合和命名不应直接照搬。 |
| EXT-0012 | `Syvert/docs/process/worktree-lifecycle.md` | `syvert` | `mechanism` | 工作现场命名与复用应确定性生成，避免同一事项出现多个隐性现场。 | `Syvert` 通过 `issue-<number>-<slug>` 形式稳定映射 worktree 与分支，降低恢复与清理成本。 | `configurable` | `harness` | `adapt` | Loom 应保留确定性现场机制，但不应强绑定 `issue-` 前缀或 GitHub 命名。 |
| EXT-0013 | `Syvert/docs/process/agent-loop.md`, `Syvert/WORKFLOW.md` | `syvert` | `mechanism` | 每个长任务应有唯一恢复主入口，而不是多个并行恢复点。 | `Syvert` 将 active `exec-plan` 定义为默认且唯一的恢复主入口，减少多工件竞争。 | `general` | `harness` | `keep` | Loom 的最小 harness 应保留“唯一恢复主入口”这一约束。 |
| EXT-0014 | `Syvert/WORKFLOW.md` | `syvert` | `principle` | 审查输入应默认采用最小必要上下文，而不是把整仓材料一并塞给 reviewer。 | `Syvert` 明确规定 review 与 guardian 只消费与当前事项、当前 head、当前风险直接相关的最小上下文。 | `general` | `governance` | `keep` | 这条与 WebEnvoy 的重基线问题形成互补，应作为 Loom 的默认审查原则。 |
| EXT-0015 | `Syvert/docs/specs/_template/spec.md` | `syvert` | `artifact` | 正式需求模板应强制表达目标、范围、GWT 场景、异常边界与验收标准。 | `Syvert` 的 `spec.md` 模板虽然精简，但已经固定了背景、目标、范围、GWT、异常与边界、验收标准等核心区块。 | `general` | `template` | `keep` | Loom 可直接吸收这一结构，但应去除项目特定字段命名。 |
| EXT-0016 | `Syvert/docs/specs/_template/plan.md` | `syvert` | `artifact` | 实施计划模板应至少明确目标、阶段拆分、约束、验证、TDD、依赖关系和进入实现前条件。 | `Syvert` 的 `plan.md` 模板把实施判断显式压成固定结构，降低 reviewer 依赖口头补充。 | `general` | `template` | `keep` | 这是 Loom 最适合上移的模板资产之一。 |
| EXT-0017 | `Syvert/spec_review.md`, `WebEnvoy/spec_review.md` | `both` | `lesson` | 正式规约需要最小套件，但“最小套件包含哪些文件”不应被过早固化成永恒规则。 | `WebEnvoy` 仍将 `TODO.md` 视为最小正式套件的一部分；`Syvert` 已把 `TODO.md` 退出 formal spec live 最小套件，显示这类约束会随治理成熟度变化。 | `configurable` | `template` | `adapt` | Loom 应区分“正式契约工件”和“执行/进度工件”，避免把 `TODO.md` 固化为所有项目的正式最低要求。 |
| EXT-0018 | `WebEnvoy/code_review.md`, `Syvert/WORKFLOW.md` | `both` | `lesson` | 审查必须有基线，但默认基线不应长到让 reviewer 先做二次侦察。 | `WebEnvoy` 的代码审查基线覆盖范围很大；`Syvert` 明确引入最小必要上下文原则，说明 Loom 需要在“有基线”和“低负担”之间做平衡。 | `general` | `governance` | `keep` | Loom 的 review 设计应提供最小基线和条件补充，而不是一份永远拉满的阅读清单。 |
| EXT-0019 | `WebEnvoy/AGENTS.md` | `webenvoy` | `principle` | 事项应允许按轻量、中等、核心分流，但分流规则必须让执行者容易判断。 | `WebEnvoy` 明确区分轻量事项、中等事项、核心/高风险事项，但同时暴露出流程分类复杂、例外较多的问题。 | `configurable` | `adoption` | `adapt` | Loom 可以保留分流思想，但不应先做复杂分层体系，应由初始化 `SKILL` 引导选择。 |
| EXT-0020 | `WebEnvoy/spec_review.md` | `webenvoy` | `artifact` | 正式规约需要区分 Spike、标准、高风险三类深度，而不是所有事项都套同一规格。 | `WebEnvoy` 在 spec review 中显式区分 Spike FR、标准 FR、高风险 FR，并给出不同文档深度要求。 | `configurable` | `adoption` | `needs_validation` | 这个分层思路有价值，但 Loom 现阶段不应先固化为 profile，需要更多项目验证。 |
| EXT-0021 | `Syvert/spec_review.md`, `Syvert/delivery-funnel.md`, `WebEnvoy/AGENTS.md`, `WebEnvoy/spec_review.md` | `both` | `lesson` | 两个仓库都已经设计了实现前审查里程碑，但它还没有在所有执行路径中稳定工程化为硬状态。 | `Syvert` 明确存在 `spec-ready -> implementation-ready` 审查与漏斗；`WebEnvoy` 也明确规定 spec review 通过后才能纳入 Sprint 实施承诺。但实践反馈显示 merge 前 review 仍常承担第一次系统性高质量判断。 | `general` | `adoption` | `keep` | Loom 应明确区分“制度上存在”与“执行上稳定生效”，并把实现前 checkpoint 工程化。 |
| EXT-0022 | `Syvert/agent-loop.md`, `Syvert/code_review.md`, `WebEnvoy/AGENTS.md`, `WebEnvoy/code_review.md` | `both` | `lesson` | 长任务生命周期至少需要 `admission checkpoint`、`build checkpoint`、`merge checkpoint` 三类正式判断点。 | 两仓都已有 admission/spec review 与 merge gate，但中途 build 纠偏点偏弱，导致 merge 前 checkpoint 容易过载。 | `general` | `harness` | `adapt` | Loom 不应只定义 spec review 和 merge gate，还应显式设计 build 级 checkpoint。 |
| EXT-0023 | `WebEnvoy/docs/dev/AGENTS.md` | `webenvoy` | `principle` | 研发载体职责应明确分离：Issue、Project、PR、`TODO.md`、handoff 各自只承担一种语义。 | `WebEnvoy` 对开发区载体职责表达非常清楚，尤其强调 `TODO.md` / handoff 不承担项目真相源职责。 | `general` | `governance` | `keep` | 这是 Loom 可以直接吸收的正向结构，不应只从 Syvert 提取。 |
| EXT-0024 | `WebEnvoy/docs/dev/AGENTS.md` | `webenvoy` | `mechanism` | 轻量事项与中等事项可以通过“简化设计说明”进入实现，而不必一律升级为正式 FR。 | `WebEnvoy` 明确给中等事项提供 `Issue + 简化设计说明 + PR` 的通道，并允许 design note 落在 PR 描述或独立模板中。 | `configurable` | `adoption` | `keep` | 这为 Loom 初始化 `SKILL` 提供了很有价值的中间通道，不应只剩轻量/正式 FR 两极。 |
| EXT-0025 | `WebEnvoy/docs/dev/AGENTS.md` | `webenvoy` | `mechanism` | 正式链路默认使用独立 worktree 或隔离 clone，并要求单现场单事项，有助于降低分支污染。 | `WebEnvoy` 明确规定正式链路使用独立执行现场，并强调单 worktree 单 issue/PR、PR 创建后禁止扩 scope。 | `general` | `harness` | `keep` | 这与 Syvert 的确定性现场思想互补，说明 Loom 应保留执行现场隔离能力。 |
| EXT-0026 | `WebEnvoy/docs/dev/AGENTS.md` | `webenvoy` | `principle` | 关闭语义应与事项成熟度绑定，避免在 `spike` 或 `spec-ready` 阶段过早制造“已完成”假象。 | `WebEnvoy` 明确规定 `spike` / `spec-ready` 默认使用 `Refs #...`，只有实现闭环并达到 `merge-ready` 才使用 `Fixes #...`。 | `general` | `governance` | `keep` | 这是 Loom 可以吸收的强约束，能减少状态真相和成熟度错位。 |
| EXT-0027 | `WebEnvoy/spec_review.md` | `webenvoy` | `principle` | Spike 事项应允许以“证据边界 + 准入条件 + handoff 输入”作为正式输出，而不必伪装成完整实施规格。 | `WebEnvoy` 对 Spike FR 的定义较完整，并明确要求区分 `primary`、`candidate`、`fallback`、`admission_ready` 等证据层。 | `configurable` | `adoption` | `adapt` | 这不是反模式，而是正向方法论；但是否作为 Loom 默认能力仍需更多项目验证。 |
| EXT-0028 | `WebEnvoy/.github/PULL_REQUEST_TEMPLATE.md` | `webenvoy` | `artifact` | PR 模板可以作为结构化事实承载体，前提是区分“必填最小事实”和“条件触发块”。 | `WebEnvoy` 的 PR 模板把 integration、gate applicability、live evidence、回滚和执行现场都结构化了，说明模板可以承载高质量事实；问题在于当前默认负担过重。 | `general` | `template` | `adapt` | Loom 不应否定结构化 PR 模板本身，而应把它拆成基础块加条件块。 |
| EXT-0029 | `WebEnvoy/scripts/check-pr-purity.sh`, `docs/dev/AGENTS.md` | `webenvoy` | `mechanism` | 分支职责纯度和 PR 范围纯度适合前置到脚本，而不是只在 review 时发现。 | `WebEnvoy` 明确提出纯度预检门禁，并提供对应脚本入口，说明“职责漂移”可以部分自动化前移。 | `general` | `harness` | `keep` | 这是 Loom 值得吸收的正向机制，和“自动化前置”结论一致。 |
| EXT-0030 | `Syvert/spec_review.md`, `WebEnvoy/spec_review.md`, `WebEnvoy/code_review.md` | `both` | `lesson` | merge 前 review 过载的根因不是“有 guardian”，而是 admission/build checkpoint 没有同样稳定地承担高质量语义判断。 | 两仓都存在较强的 merge 前审查；但当前移 checkpoint 未稳定生效时，merge review 会被迫兼任阶段审查与终审。 | `general` | `adoption` | `keep` | 这是 Loom 设计 checkpoint 体系时应明确写入的结构性教训。 |
| EXT-0031 | `mail-listener/AGENTS.md`, `mail-listener/WORKFLOW.md`, `mail-listener/code_review.md`, `mail-listener/spec_review.md` | `mail-listener` | `lesson` | 对已有工程基线但缺完整治理闭环的小型真实仓库，Loom 的首轮 adoption 应优先补最小治理入口，而不是一次性装完整 harness。 | `mail-listener` 已有清晰边界、CI、测试与 agent 规则，但通过最小 adoption 只补 `WORKFLOW`、review 合同、条件化 spec 路径和 PR 模板，即可形成可执行闭环。 | `general` | `adoption` | `keep` | 这说明 Loom 对小型真实仓库的默认入口应更轻，先验证不过装，再决定是否追加 recovery/work-item/status-surface。 |
| EXT-0032 | `mail-listener/AGENTS.md`, `mail-listener/WORKFLOW.md` | `mail-listener` | `lesson` | 当下游仓库已经有稳定的项目边界文档时，Loom adoption 应采用“伴随文档接入”而不是重写根规则文档。 | `mail-listener` 保留原有 `AGENTS.md` 的项目边界与工程规则，只追加治理伴随文档的读取顺序与职责映射，即完成接入。 | `general` | `skills` | `keep` | `loom-init` 应先判断仓库是否已有清晰根规则；若已有，优先补 companion docs，而不是重写根级规则。 |
| EXT-0033 | `mail-listener/WORKFLOW.md`, `mail-listener/.github/PULL_REQUEST_TEMPLATE.md` | `mail-listener` | `lesson` | 对低复杂度仓库，`build checkpoint` 可以先寄存在 issue 或 PR 描述中，不必第一轮就引入独立 `exec-plan`。 | `mail-listener` 的第一轮 adoption 在不引入 `exec-plan` 的前提下，仍为跨多轮事项定义了停点、下一步和阻断项的最小记录方式。 | `configurable` | `harness` | `keep` | Loom 的轻量 adoption 路径应允许 `checkpoint-lite`，把恢复事实先寄存在现有载体中。 |
| EXT-0034 | `OpenAI harness engineering` | `article` | `principle` | 面向 agent 的知识不应塞进一个超大 `AGENTS.md`，而应进入可持续维护、可被机械检查的仓库知识结构。 | OpenAI 明确建议把短 `AGENTS.md` 当成目录，将知识沉淀到仓库文档中，并配合 linters、CI jobs、文档清理 agent 保持知识库可用。 | `general` | `governance` | `keep` | Loom 应把“短入口 + 深知识库 + 可机械校验”定义为目标能力，而不是只停留在文档分层口号。 |
| EXT-0035 | `OpenAI harness engineering` | `article` | `mechanism` | Harness 应提供对 agent 友好的运行时可见性和可验证性，包括按工作现场启动应用、直接读取日志/指标/trace、以及用浏览器自动化验证 UI。 | OpenAI 文中强调 per-worktree app、Chrome DevTools、可观察性栈和 agent legibility，说明运行时可见性本身是 harness 能力。 | `general` | `harness` | `keep` | Loom 需要把“运行时可见性”明确成能力目标，而不是只讨论 checkpoint 和规则。 |
| EXT-0036 | `OpenAI harness engineering` | `article` | `mechanism` | 仓库知识结构、规则模板和执行支撑应具备机械化校验能力，而不是只靠人工记得去维护。 | OpenAI 文中明确提到 linters、CI jobs、文档清理 agent，说明知识库新鲜度、交叉链接和结构完整性应能被自动化检查。 | `general` | `harness` | `keep` | Loom 的自动化前置应扩展到知识库与模板层，而不只检查代码或 PR 纯度。 |
| EXT-0037 | `Anthropic effective harnesses for long-running agents` | `article` | `mechanism` | 长时运行 harness 的核心不是更多说明，而是 initializer 先产出结构化执行环境：特性清单、初始化脚本、进度文件和初始 clean state。 | Anthropic 文中把 initializer 作为首轮 agent，先写 `feature list`、`init.sh`、`progress file`，并建立初始 git 提交，为后续多轮 agent 执行提供稳定起点。 | `general` | `harness` | `keep` | Loom 的初始化能力应把这些产物定义成目标能力，而不是只停留在“判断装什么”。 |
| EXT-0038 | `Anthropic effective harnesses for long-running agents` | `article` | `mechanism` | 长时运行 agent 应以单特性增量推进，每轮先读 progress 与 git 历史，再只推进一个清晰单元，并在结束时回写进度。 | Anthropic 文中强调 one feature at a time、每轮开始读 `progress file` 和 `git log`，结束时更新进度并提交代码，以避免上下文漂移。 | `general` | `harness` | `keep` | Loom 的 checkpoint / resume 机制应把“每轮读取与每轮回写”定义为正式能力，而不只描述静态结构。 |
