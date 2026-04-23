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
  - 采用动机、事项分流、checkpoint 策略、默认 retrofit 路径、候选模式
- `skills/`
  - root entry、场景 skills、分发合同与场景路由入口职责

## Entry Contract Map

以下关系用于表达 adoption 结论如何被入口层直接消费：

- `repo companion` 主合同
  - 稳定落点：`adoption/repo-companion-contract.md`
  - 入口消费：`skills/loom-init/SKILL.md`
- `deep-existing-repo` 默认 attach 路径
  - 稳定落点：`adoption/deep-existing-repo-default.md`
  - 入口消费：`skills/loom-init/SKILL.md`; `skills/loom-init/references/intake-signals.md`
- 小型既有仓库默认 retrofit 策略
  - 稳定落点：`adoption/lightweight-retrofit-default.md`
  - 入口消费：`skills/loom-init/SKILL.md`
- `loom-init` 输入信号合同
  - 稳定落点：`skills/loom-init/references/intake-signals.md`
- root route matrix
  - 稳定落点：`skills/route-matrix.md`
  - 入口消费：`skills/loom-init/SKILL.md`
- `loom-init` 输出合同
  - 稳定落点：`skills/loom-init/references/output-contract.md`
- `repo interop` 主合同
  - 稳定落点：`adoption/repo-interop-contract.md`
- `skills` 分发与适配合同
  - 稳定落点：`skills/distribution-and-adapter-contract.md`
  - 入口消费：`skills/README.md`
补充约束：

- `repo companion` contract 的唯一主落点固定为 `adoption/repo-companion-contract.md`
- 历史材料中的 `companion docs` 仅作为迁移表述保留，不再作为新的正式落点名

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
| EXT-0020 | `needs_validation` | `archive-only` | `parking` | Spike / 标准 / 高风险分层 |
| EXT-0021 | `keep` | `adoption/rationale.md` | `core` | 实现前 checkpoint 需工程化 |
| EXT-0022 | `keep` | `adoption/routing-and-checkpoints.md`; `harness/checkpoint-model.md`; `harness/execution-chain.md`; `harness/merge-checkpoint.md` | `core` | 三类 checkpoint 的治理语义与执行侧承接已收成稳定合同 |
| EXT-0023 | `keep` | `governance/principles.md` | `core` | 载体职责分离 |
| EXT-0024 | `keep` | `adoption/routing-and-checkpoints.md` | `core` | 中等事项设计说明通道 |
| EXT-0025 | `keep` | `harness/workspace-model.md`; `harness/workspace-lifecycle.md` | `core` | 单现场单事项与可定位生命周期入口 |
| EXT-0026 | `keep` | `governance/maturity-and-closing.md` | `core` | 关闭语义与成熟度绑定 |
| EXT-0027 | `adapt` | `archive-only` | `candidate` | Spike 证据分层方法论 |
| EXT-0028 | `adapt` | `templates/pull-request.md` | `candidate` | 结构化 PR 模板按条件展开 |
| EXT-0029 | `keep` | `harness/workspace-and-purity.md`; `harness/workspace-lifecycle.md` | `core` | 纯度预检、cleanup/retire 与范围前置 |
| EXT-0030 | `keep` | `adoption/rationale.md` | `core` | merge 前 review 过载的结构性根因 |
| EXT-0031 | `keep` | `adoption/lightweight-retrofit-default.md`; `skills/loom-init/references/intake-signals.md` | `core` | 小型真实仓库先补最小治理入口，但必须具备仓库级验证入口 |
| EXT-0032 | `keep` | `adoption/repo-companion-contract.md` | `core` | 既有根规则仓库优先以 `repo companion` 接入；历史 `companion docs` 仅保留作迁移表述，并由 `loom-init` 消费该主合同 |
| EXT-0033 | `keep` | `harness/recovery-model.md`; `skills/loom-init/SKILL.md`; `skills/loom-init/references/output-contract.md` | `core` | 低复杂度仓库允许 checkpoint-lite，并由入口层明确承接方式 |
| EXT-0034 | `keep` | `governance-design.md` | `core` | 短入口文档、深知识库与可机械校验的知识结构 |
| EXT-0035 | `keep` | `harness/status-surface.md`; `skills/loom-init/references/output-contract.md` | `core` | 运行时可见性、日志指标 trace 与 agent 可验证性 |
| EXT-0036 | `keep` | `harness/automation-frontload.md`; `tools/loom_check.py` | `core` | 知识库、模板与执行支撑的机械化校验能力 |
| EXT-0037 | `keep` | `harness/work-item-contract.md`; `harness/workspace-model.md`; `harness/execution-chain.md`; `harness-design.md`; `skills/loom-init/references/output-contract.md` | `core` | initializer 产物、初始 progress 与 clean state |
| EXT-0038 | `keep` | `harness/fact-chain-contract.md`; `harness/execution-context.md`; `harness/work-item-contract.md`; `harness/recovery-model.md`; `harness/execution-chain.md`; `skills/loom-init/references/output-contract.md` | `core` | 每轮读取与回写、单单元增量推进 |
| EXT-0039 | `keep` | `skills/distribution-and-adapter-contract.md` | `core` | `#273` 已把安装、发现、升级合同写成正式入口合同并接入 installer gate |
| EXT-0040 | `keep` | `skills/distribution-and-adapter-contract.md` | `core` | `#273` 已把薄 root contract 与深知识引用关系收成稳定入口边界，而不是候选约定 |
| EXT-0041 | `keep` | `harness/automation-frontload.md`; `skills/distribution-and-adapter-contract.md` | `core` | `#273` 已把 root route、fallback、runtime/install drift 与安装边界回归纳入现有门禁 |
| EXT-0042 | `keep` | `skills/distribution-and-adapter-contract.md` | `core` | 宿主特定细节收敛在 adapter 层 |
| EXT-0043 | `needs_validation` | `archive-only` | `parking` | `#180` 已补 Loom 自身 retrofit 证据，但父事项 / 子事项关系仍缺第二宿主或第二仓库样本，继续停在待验证区 |
| EXT-0044 | `keep` | `skills/loom-init/SKILL.md`; `skills/loom-init/references/intake-signals.md`; `skills/loom-init/references/output-contract.md` | `core` | `#168` 与 `#275` 现在已提供两个独立空仓新项目样本，稳定复验同一条 root route、`minimal-bootstrap` 输出形状、验证入口与 fail-closed merge/closeout 边界 |
| EXT-0045 | `keep` | `adoption/lightweight-retrofit-default.md`; `skills/loom-init/references/intake-signals.md`; `skills/loom-init/SKILL.md` | `core` | `#170` 已补既有仓库执行 / 回写 / sync repo companion 验证，继续支撑“轻量 retrofit 需要仓库级验证入口”的稳定边界 |
| EXT-0046 | `adapt` | `skills/loom-init/references/intake-signals.md`; `harness/recovery-model.md`; `harness/status-surface.md` | `candidate` | `hotcp` 继续证明某类复杂既有仓库需要更完整装配，但 `#275` 的 `Syvert` / `WebEnvoy` 第二样本反证说明不能把 `complex-existing` 一律升级成默认 `full-bootstrap` |
| EXT-0047 | `adapt` | `skills/loom-init/references/intake-signals.md`; `harness/recovery-model.md`; `harness/status-surface.md` | `candidate` | `hotcp` 继续证明现行入口与历史入口并存可能是恢复升级信号，但 `#275` 的 `Syvert` / `WebEnvoy` 第二样本说明仅凭该信号本身仍不足以要求 Loom-owned recovery/status carriers |
| EXT-0048 | `keep` | `adoption/deep-existing-repo-default.md`; `skills/loom-init/references/intake-signals.md`; `skills/loom-init/references/output-contract.md` | `core` | 成熟治理重仓在 `complex-existing` 下应优先走 attach-only 的 `deep-existing-repo`，而不是新增第四种 `repository_mode` |
| EXT-0049 | `keep` | `adoption/repo-companion-contract.md` | `core` | typed `specialized_gates` 与 locator-first `context_schema` 已成为稳定 companion 合同 |
| EXT-0050 | `adapt` | `adoption/repo-companion-contract.md` | `candidate` | `metadata_contract` 已进入 `repo-interface v2` 作为可选扩展，但字段 taxonomy 仍待第二个独立样本继续抽象 |
| EXT-0051 | `keep` | `adoption/repo-interop-contract.md`; `harness/host-action-contract.md` | `core` | retained host action result 与 repo-native carriers 需要通过独立 `interop.json` 被 Loom 只读消费，而不是回塞到 `repo-interface.json` 或接管宿主实现 |
| EXT-0052 | `keep` | `adoption/repo-interop-contract.md` | `core` | `shadow parity` 作为 `admission/review/merge_ready/closeout` 的 validation-only compare surface 已进入稳定合同 |
| EXT-0053 | `needs_validation` | `archive-only` | `parking` | parity mismatch 是否应自动升级为 blocking merge gate 仍缺 live adopted repo 证据，继续停在待验证区 |
