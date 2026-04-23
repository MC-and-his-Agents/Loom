# Loom 仓库宪法

## 项目使命

Loom 是一个面向智能体优先项目的上游治理与执行编排仓库。

它要复用的不是业务代码，而是项目如何被组织、如何进入执行、如何跨多轮持续推进、如何进入 merge-ready、以及如何收口的能力。

Loom 当前冻结的三层目标态是：

- `governance truth`
- `harness orchestration`
- `executable SKILLS`

## 宪法规则

1. Loom 是上游治理与执行编排仓库，不是业务模板仓库。
2. Loom 只沉淀多仓实证下成立的结构、机制、模板和教训，不复制单一仓库的历史形态。
3. `Syvert` 与 `WebEnvoy` 都是正反并存的实践来源；任何单仓经验都不得直接被当作 Loom 默认内核。
4. `governance`、`harness`、`templates`、`adoption`、`skills` 必须边界清晰，不得混成单一说明文档。
5. `keep` 条目进入 Loom 当前核心落点；`adapt` 条目进入候选落点；`needs_validation` 条目进入待验证区。
6. 先冻结目标态与职责边界，再推进实现拆分、装配入口与 profile。
7. Loom 的 `SKILLS` 是可执行入口与编排层，不是事实真相源。
8. Loom 的文档必须优先表达可执行结构，而不是只做理念陈述。
9. 重要判断必须进入版本控制，不得只留在会话里。
10. 禁止把某个下游仓库当前的目录名、命名习惯或门禁细节，未经抽象直接提升为 Loom 默认规则。
11. Loom 默认追求 `merge-readiness-centered` 的治理流程，不把 final review 当作第一次系统性发现问题的场所。
12. Loom 不要求自研 GitHub、CI、review engine、`git worktree` 或 `gh` 的底层实现，但必须能统一编排和消费这些宿主能力。

## 权威来源

文档冲突时按以下顺序处理：

1. [AGENTS.md](./AGENTS.md)
2. [VISION.md](./VISION.md)
3. [README.md](./README.md)
4. [docs/evidence/extraction-ledger.md](./docs/evidence/extraction-ledger.md)
5. [docs/evidence/landing-map.md](./docs/evidence/landing-map.md)
6. `docs/` 与 `skills/` 下各区域 `README.md`
7. 各区域具体规则与说明文件

## 读取顺序

讨论 Loom 定位与边界时：

1. [AGENTS.md](./AGENTS.md)
2. [VISION.md](./VISION.md)
3. [README.md](./README.md)

讨论 Loom 当前有哪些能力、从哪里提取而来时：

1. [AGENTS.md](./AGENTS.md)
2. [docs/evidence/extraction-ledger.md](./docs/evidence/extraction-ledger.md)
3. [docs/evidence/landing-map.md](./docs/evidence/landing-map.md)

讨论 Loom 仓库结构与当前落点时：

1. [AGENTS.md](./AGENTS.md)
2. [docs/evidence/landing-map.md](./docs/evidence/landing-map.md)
3. `docs/` 与 `skills/` 下各区域 `README.md`
4. 各区域具体文件

讨论 Loom 当前阶段、阶段目标与阶段顺序时：

1. [AGENTS.md](./AGENTS.md)
2. 对应 GitHub issues

## 目录职责

- `docs/methodology/governance/`
  - 治理原则、状态机、审查模型、成熟度与关闭语义
- `docs/methodology/harness/`
  - 执行上下文、工作现场、恢复模型、宿主编排、自动化前置与纯度控制
- `docs/methodology/templates/`
  - 正式规约模板、PR 模板和其他结构化工件
- `skills/`
  - 初始化、接手、执行、审查、merge-ready、收口等一等可执行入口
- `docs/adoption/`
  - 采用动机、事项分流、repo companion 与 repo interop 合同
- `docs/evidence/`
  - 提取台账、落点映射与验证样本归档

## 工作纪律

1. Loom 中的“说明文件”不应长期停留在纯解释状态；一旦对应条目已稳定，应继续推进到最小规范。
2. 同一条 Loom 规则不得在多个区域重复完整表述；其他文档应链接或引用唯一落点。
3. 若新增内容无法映射到 `docs/methodology`、`docs/adoption`、`docs/evidence`、`skills` 之一，应先停止并重新判断边界。
4. 若某结论只来自单一仓库且缺少第二来源支撑，默认进入 `adapt` 或 `needs_validation`，不得直接进入 `core`。
5. 若某项能力只是当前仓库的组织便利，而非上游运行模型能力，不应进入 Loom。
6. Loom 的模板与规则应优先追求最小可用，不追求首轮完备。
7. 在 Loom 中推进结构时，优先修正“边界不清”“落点缺失”“规则重复”，而不是先堆更多候选想法。

## 非目标

Loom 当前不是：

- 通用代码生成器
- 某个业务领域的脚手架
- 从零重写 GitHub、CI、code review、`git worktree` 或 `gh` 的底层产品
- 只靠 prompt 运转的文档仓库
- 已经定型的 profile 系统
