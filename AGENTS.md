# Loom 仓库宪法

## 项目使命

Loom 是一个面向智能体优先项目的上游底座。

它要复用的不是业务代码，而是项目如何被组织、如何进入执行、如何跨多轮持续推进、如何审查，以及如何收口的能力。

Loom 当前聚焦三层能力：

- `governance`
- `harness`
- `SKILLS`

## 宪法规则

1. Loom 是上游运行模型仓库，不是业务模板仓库。
2. Loom 只沉淀多仓实证下成立的结构、机制、模板和教训，不复制单一仓库的历史形态。
3. `Syvert` 与 `WebEnvoy` 都是正反并存的实践来源；任何单仓经验都不得直接被当作 Loom 默认内核。
4. `governance`、`harness`、`templates`、`adoption`、`skills` 必须边界清晰，不得混成单一说明文档。
5. `keep` 条目进入 Loom 当前核心落点；`adapt` 条目进入候选落点；`needs_validation` 条目进入待验证区。
6. 先收敛最小规范，再讨论 profile；先有能力内核，再做装配入口。
7. Loom 的 `SKILLS` 是入口层，不是事实真相源。
8. Loom 的文档必须优先表达可执行结构，而不是只做理念陈述。
9. 重要判断必须进入版本控制，不得只留在会话里。
10. 禁止把某个下游仓库当前的目录名、命名习惯或门禁细节，未经抽象直接提升为 Loom 默认规则。

## 权威来源

文档冲突时按以下顺序处理：

1. [AGENTS.md](./AGENTS.md)
2. [VISION.md](./VISION.md)
3. [README.md](./README.md)
4. [docs/roadmap.md](./docs/roadmap.md)
5. [adoption/extraction-ledger.md](./adoption/extraction-ledger.md)
6. [adoption/landing-map.md](./adoption/landing-map.md)
7. 各区域 `README.md`
8. 各区域具体规则与说明文件

## 读取顺序

讨论 Loom 定位与边界时：

1. [AGENTS.md](./AGENTS.md)
2. [VISION.md](./VISION.md)
3. [README.md](./README.md)

讨论 Loom 当前有哪些能力、从哪里提取而来时：

1. [AGENTS.md](./AGENTS.md)
2. [adoption/extraction-ledger.md](./adoption/extraction-ledger.md)
3. [adoption/landing-map.md](./adoption/landing-map.md)

讨论 Loom 仓库结构与当前落点时：

1. [AGENTS.md](./AGENTS.md)
2. [adoption/landing-map.md](./adoption/landing-map.md)
3. 各区域 `README.md`
4. 各区域具体文件

讨论 Loom 当前阶段、阶段目标与阶段顺序时：

1. [AGENTS.md](./AGENTS.md)
2. [docs/roadmap.md](./docs/roadmap.md)
3. 对应 GitHub issues

## 目录职责

- `governance/`
  - 治理原则、审查模型、成熟度与关闭语义
- `harness/`
  - 执行上下文、工作现场、恢复模型、自动化前置与纯度控制
- `templates/`
  - 正式规约模板、PR 模板和其他结构化工件
- `adoption/`
  - 提取台账、落点映射、采用动机、事项分流与候选模式
- `skills/`
  - 初始化、执行、审查、收口等入口层职责定义

## 工作纪律

1. Loom 中的“说明文件”不应长期停留在纯解释状态；一旦对应条目已稳定，应继续推进到最小规范。
2. 同一条 Loom 规则不得在多个区域重复完整表述；其他文档应链接或引用唯一落点。
3. 若新增内容无法映射到 `governance`、`harness`、`templates`、`adoption`、`skills` 之一，应先停止并重新判断边界。
4. 若某结论只来自单一仓库且缺少第二来源支撑，默认进入 `adapt` 或 `needs_validation`，不得直接进入 `core`。
5. 若某项能力只是当前仓库的组织便利，而非上游运行模型能力，不应进入 Loom。
6. Loom 的模板与规则应优先追求最小可用，不追求首轮完备。
7. 在 Loom 中推进结构时，优先修正“边界不清”“落点缺失”“规则重复”，而不是先堆更多候选想法。

## 非目标

Loom 当前不是：

- 通用代码生成器
- 某个业务领域的脚手架
- 对 GitHub、CI 或 code review 的替代品
- 只靠 prompt 运转的文档仓库
- 已经定型的 profile 系统
