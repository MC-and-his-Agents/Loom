# Loom Landing Map

本文件把当前 `extraction-ledger.md` 中所有可见条目映射到 Loom 仓库中的实际落点。

映射规则：

- `keep`
  - 当前进入 Loom 核心落点
- `adapt`
  - 当前进入 Loom 候选落点，待抽象与去项目化后再收敛
- `needs_validation`
  - 当前进入待验证区，不进入默认内核

## Area Map

- `governance/`
  - 原则、审查模型、成熟度与关闭语义
- `harness/`
  - work item、执行上下文、工作现场、恢复模型、状态面、纯度与自动化前置
- `templates/`
  - 正式规约模板、PR 模板
- `adoption/`
  - 采用动机、事项分流、checkpoint 策略、候选模式
- `skills/`
  - 初始化与采用装配入口职责

## Item Map

| id | status | landing_path | landing_mode | note |
| --- | --- | --- | --- | --- |
| EXT-0001 | `keep` | `governance/principles.md` | `core` | 真相源分层 |
| EXT-0002 | `keep` | `governance/principles.md` | `core` | 受控执行入口 |
| EXT-0003 | `keep` | `harness/recovery-model.md` | `core` | checkpoint / resume / handoff |
| EXT-0004 | `keep` | `governance/review-model.md` | `core` | reviewer / CI / guardian 分层 |
| EXT-0005 | `keep` | `adoption/rationale.md` | `core` | Loom 上游存在理由 |
| EXT-0006 | `keep` | `governance/principles.md` | `core` | 单一真相源，避免规则漂移 |
| EXT-0007 | `keep` | `adoption/routing-and-checkpoints.md` | `core` | 用入口替代复杂分类暴露 |
| EXT-0008 | `keep` | `templates/pull-request.md` | `core` | 模板从最小事实集出发 |
| EXT-0009 | `keep` | `harness/automation-frontload.md` | `core` | 自动判断尽量前置 |
| EXT-0010 | `keep` | `adoption/rationale.md` | `core` | 多仓提炼，不复制单仓 |
| EXT-0011 | `adapt` | `harness/execution-context.md` | `candidate` | 事项上下文字段需参数化 |
| EXT-0012 | `adapt` | `harness/workspace-model.md` | `candidate` | 现场命名需去 GitHub 化 |
| EXT-0013 | `keep` | `harness/recovery-model.md` | `core` | 唯一恢复主入口 |
| EXT-0014 | `keep` | `governance/review-model.md` | `core` | 最小必要上下文 |
| EXT-0015 | `keep` | `templates/spec-suite.md` | `core` | `spec.md` 基础结构 |
| EXT-0016 | `keep` | `templates/spec-suite.md` | `core` | `plan.md` 基础结构 |
| EXT-0017 | `adapt` | `templates/spec-suite.md` | `candidate` | 正式套件与进度工件分离 |
| EXT-0018 | `keep` | `governance/review-model.md` | `core` | 审查基线应最小化 |
| EXT-0019 | `adapt` | `adoption/routing-and-checkpoints.md` | `candidate` | 分流思想保留，但不先固化分层 |
| EXT-0020 | `needs_validation` | `adoption/candidate-patterns.md` | `parking` | Spike / 标准 / 高风险分层 |
| EXT-0021 | `keep` | `adoption/rationale.md` | `core` | 实现前 checkpoint 需工程化 |
| EXT-0022 | `adapt` | `adoption/routing-and-checkpoints.md` | `candidate` | 三类 checkpoint 模型 |
| EXT-0023 | `keep` | `governance/principles.md` | `core` | 载体职责分离 |
| EXT-0024 | `keep` | `adoption/routing-and-checkpoints.md` | `core` | 中等事项设计说明通道 |
| EXT-0025 | `keep` | `harness/workspace-model.md` | `core` | 单现场单事项 |
| EXT-0026 | `keep` | `governance/maturity-and-closing.md` | `core` | 关闭语义与成熟度绑定 |
| EXT-0027 | `adapt` | `adoption/candidate-patterns.md` | `candidate` | Spike 证据分层方法论 |
| EXT-0028 | `adapt` | `templates/pull-request.md` | `candidate` | 结构化 PR 模板按条件展开 |
| EXT-0029 | `keep` | `harness/workspace-and-purity.md` | `core` | 纯度预检与范围前置 |
| EXT-0030 | `keep` | `adoption/rationale.md` | `core` | merge 前 review 过载的结构性根因 |
| EXT-0031 | `keep` | `adoption/routing-and-checkpoints.md` | `core` | 小型真实仓库先补最小治理入口 |
| EXT-0032 | `keep` | `skills/loom-init/SKILL.md` | `core` | 既有根规则仓库优先 companion docs 接入 |
| EXT-0033 | `keep` | `harness/recovery-model.md` | `core` | 低复杂度仓库允许 checkpoint-lite |
| EXT-0034 | `keep` | `governance-design.md` | `core` | 短入口文档、深知识库与可机械校验的知识结构 |
| EXT-0035 | `keep` | `harness/status-surface.md`; `harness-design.md` | `core` | 运行时可见性、日志指标 trace 与 agent 可验证性 |
| EXT-0036 | `keep` | `harness/automation-frontload.md`; `harness-design.md` | `core` | 知识库、模板与执行支撑的机械化校验能力 |
| EXT-0037 | `keep` | `harness/work-item-contract.md`; `harness/workspace-model.md`; `harness-design.md` | `core` | initializer 产物、初始 progress 与 clean state |
| EXT-0038 | `keep` | `harness/execution-context.md`; `harness/work-item-contract.md`; `harness/recovery-model.md`; `harness-design.md` | `core` | 每轮读取与回写、单单元增量推进 |
