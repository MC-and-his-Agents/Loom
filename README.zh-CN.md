# Loom

<a href="https://zread.ai/MC-and-his-Agents/Loom"><img height="28" alt="Ask Zread" src="https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff"></a>
<a href="https://deepwiki.com/MC-and-his-Agents/Loom"><img height="28" alt="Ask DeepWiki" src="https://deepwiki.com/badge.svg"></a>

语言：中文 | [英文版本](./README.md)

Loom 帮助编码智能体把议题推进成可以合并的拉取请求。

编码智能体已经很会写代码。真正困难的是代码之外的执行状态：当前正在做哪项工作、
在哪里执行、由哪条分支和哪个拉取请求承载、验证过什么、审查如何裁决、持续集成
是否一致，以及这项工作是否真的可以合并。

Loom 采用命令行优先设计，是一个智能体优先的项目运营层，用来管理这些执行状态。
它把零散请求转化为可追踪的工作项，把工作绑定到分支和拉取请求，持续携带验证与
审查证据，并为智能体提供清晰的恢复、审查、合并就绪和收尾路径。

没有 Loom 时，智能体恢复工作常常依赖聊天历史，并猜测当前状态。

有了 Loom，智能体从仓库事实恢复：

- 这项工作是什么；
- 工作现场在哪里；
- 哪条分支和哪个拉取请求承载这项工作；
- 已经改了什么；
- 已经验证了什么；
- 审查如何裁决；
- 这项工作如何对齐主干事实；
- 还有什么阻塞合并就绪；
- 合并后还需要如何收尾。

## 什么时候使用 Loom

当智能体工作已经超过“一条提示词改完文件”的范围时，使用 Loom。

这些场景尤其适合：

- 一个议题可能跨越多轮会话；
- 多个智能体或人工会接触同一项工作；
- 拉取请求需要审查证据、持续集成证据和合并就绪检查；
- 智能体中断后需要恢复，而不是重新阅读整段聊天；
- 项目需要可靠记录合并前后发生了什么；
- 关闭拉取请求还不够，文档、状态或项目事实也必须一致。

## Loom 会给仓库增加什么

仓库采用 Loom 后，会获得一条可由智能体操作的执行路径：

- 工作项：每次实现都从一个明确的工作单元开始。
- 工作现场绑定：工作会绑定到分支、工作区和拉取请求。
- 恢复路径：新的智能体可以恢复当前状态，而不是猜测。
- 审查路径：审查裁决会成为工作记录的一部分。
- 验证证据：检查结果和证据会被持续携带，而不是散落在聊天里。
- 合并就绪：拉取请求会和工作项、分支、审查、证据一起校验。
- 收尾：合并后清理工作现场，避免留下过期状态。

## 一项 Loom 工作如何推进

一次典型的 Loom 工作是这样的：

1. 从议题或请求开始。
2. Loom 创建或恢复一个工作项。
3. 智能体在绑定的分支和工作区中执行。
4. 智能体记录改了什么、验证了什么。
5. 审查检查当前代码头，而不是检查过期的会话记忆。
6. `loom ship` 在合并前检查工作项、分支、拉取请求、审查和证据是否一致。
7. 合并后，同一次 ship 运行会读回宿主状态，并完成最短合法收尾路径。

在底层，工作会沿着固定门控链推进：规格门控、构建门控、审查门控和合并门控。

目标不是让智能体打字更快，而是让工作更不容易丢失、误读或过早合并。

## 日常交付路径

安装 Loom 且工作项已经有拉取请求后，默认交付命令是 `loom ship`。这是普通工作的
产品路径：检查拉取请求元数据，确认门控输入，在传入 `--apply` 时通过宿主控制面合并，
然后完成内联或仅宿主收尾，不再为普通事项额外创建第二个收尾拉取请求。

```bash
loom ship \
  --target . \
  --item WI-123 \
  --issue 123 \
  --pr 456 \
  --branch work/123-example \
  --head-sha "$(git rev-parse HEAD)" \
  --apply \
  --json
```

这个包装器的合同保持收敛且有固定顺序：

- dry-run 只读消费 `pr-metadata preflight -> pr gate -> controlled merge check
  -> closeout policy`，然后输出首个阻塞摘要、`missing_inputs` 与
  `next_action`，不修改宿主或仓库状态；
- `--apply` 最多只会在上述只读序列前增加一步确定性的安全 metadata repair，
  且前提是显式提供 `--issue`、`--branch` 与 `--head-sha`；
- 这一步自动修复不会替你发明或裁决冲突的 Work Item、branch、head SHA、
  release 或 closeout 事实；
- `--json` 只保留短诊断输出；若 stdout 超预算，详细步骤会折叠到 artifact
  locator 之后；`--full-output` 只用于显式调试、审计或阻塞分类；
- closeout policy 决定普通交付是继续走当前共享的 inline/host-only 宿主收尾
  路径，还是停下并切到显式 batched carrier / full closeout 路径。

轻量和标准强度变更通常应在这一条命令里完成。只有发布、父级或里程碑收尾、多个工作项
共用一次交付、宿主与仓库事实冲突、强化治理变更，或确实需要版本化终态证据时，Loom
才升级为批量载体拉取请求或显式完整收尾拉取请求。

当前 `loom ship` 只执行普通 inline/host-only 宿主收尾路径。批量载体写入与
显式完整收尾拉取请求执行仍由后续 issue 承接；此包装器会显式阻断，并把调用者导向
对应的显式路径，而不是自行猜测。

## 在仓库中试用

理解 Loom 最快的方式，是在一个真实仓库中启用它，然后让智能体从 `loom-init`
开始。

安装流程分三部分：

1. 安装全局 Loom 命令行工具。
2. 安装并注册 Codex 插件。
3. 用仅元数据的仓库采用模式让目标仓库采用 Loom。

把这段自包含提示词复制给编码智能体：

```text
请在当前目标仓库启用 Loom。不要假设这个仓库已经了解 Loom。

Loom 有三层：
1. Loom CLI：安装在本机的全局 `loom` 命令。
2. Codex 插件：由 CLI 安装的用户级 Codex 交互入口。
3. 仓库启用：向目标仓库写入元数据，让 Loom 可以管理工作项。

先安装 CLI：
node --version
npm --version
npm install -g @mc-and-his-agents/loom
loom version --json

然后安装并注册 Codex 插件：
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json

然后进入目标仓库根目录并启用 Loom：
cd /path/to/target-repository
loom install --target . --apply --json

最后验证：
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json

仓库启用必须使用仅元数据模式。不要把 Loom 仓库 clone 到目标项目里。
不要手动创建 `.loom/bin`、`.agents/skills` 或根 `skills`。如果任何命令失败，
立即停止，汇报失败命令，然后运行：
loom repair plan --target . --json
```

`loom install` 和 `loom upgrade` 只管理目标仓库的仅元数据启用状态。检查或刷新本机
Codex 插件入口时，使用 `loom host doctor|install|register --host codex --scope user`。

在新的 Codex 会话中从 `loom-init` 开始工作；如果 Codex Desktop 已经加载过
插件列表，重启 Codex Desktop。

日常开发中，当工作项已经有拉取请求后，让智能体使用 `loom ship` 交付，不要手工串联
合并就绪、宿主事实同步、载体收尾和收尾检查这些底层步骤。

在第二台开发机器上打开已采用 Loom 的仓库时，安装全局命令行工具、注册 Codex
用户级插件，然后验证仓库：

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

目标仓库的 upgrade 命令不会刷新 Codex 插件缓存。先运行
`loom host doctor --host codex --scope user --json`，需要修复或刷新本机插件入口时再运行
`loom host install --host codex --scope user --apply --json` 和
`loom host register --host codex --scope user --apply --json`。

## 为什么 Loom 能保持可靠

Loom 把智能体执行中最容易混在一起的部分拆开：治理规则、执行支撑、验证证据、
结构化工件和可执行技能。

这种拆分很重要，因为一个拉取请求看起来可能已经完成，但工作项、审查记录、验证证据
或收尾状态仍然可能是过期的。Loom 让这些通道保持独立，再通过命令行检查它们是否
一致。

在仓库边界，Loom 只保留元数据。全局 `loom` 命令负责安装 Codex 用户级插件、
记录仓库采用、读取事实链并执行验证。智能体从 `loom-init` 进入路由，再使用
`loom-adopt`、`loom-resume`、`loom-build` 和 `loom-review` 等场景技能推进工作。
当拉取请求准备交付时，`loom ship` 是合并与收尾的主要命令行路径。

在仓库实现层面，Loom 落为五个稳定部分：

- 治理定义规则、审查模型和收尾语义。
- 支撑提供执行支持、工作区隔离、恢复机制和运行时可见性。
- 模板承载结构化工件。
- 行为证据和测试证据让验证与声明保持分离。
- 技能将这些能力组装成可执行入口。
- 采纳记录能力的提取来源及当前落地位置。

依赖流严格单向：治理定义规则，模板承载结构，支撑在治理约束下运行，技能读取
所有内容并组装入口，采纳提供证据与演化。技能不能重新定义治理规则，模板不能
成为唯一事实来源，状态展示也不能成为第二个条目事实来源。

## Loom 不是什么

Loom 不决定构建什么产品、如何设计产品架构、如何对业务领域建模，也不要求所有
项目采用相同目录结构。它关注项目运营，而不是业务实质。

Loom 不是业务模板、代码生成器、仅限规格驱动开发的工具，也不是 GitHub、持续集成、
审查引擎或 `git worktree` 的替代品。它是项目运营层与可执行技能层，用来让智能体
以一致方式消费这些宿主能力。

## 维护者文档

- 愿景与边界：[VISION.md](./VISION.md)
- 仓库宪法：[AGENTS.md](./AGENTS.md)
- 变更治理强度：[docs/methodology/governance/change-governance-intensity.md](./docs/methodology/governance/change-governance-intensity.md)
- Loom 治理强度映射：[docs/methodology/governance/loom-governance-intensity-mapping.md](./docs/methodology/governance/loom-governance-intensity-mapping.md)
- 治理强度收尾证据：[docs/evidence/governance-intensity-final-closeout.md](./docs/evidence/governance-intensity-final-closeout.md)
- 技能入口：[skills/README.md](./skills/README.md)
- 方法论文档：[docs/methodology/](./docs/methodology/)
- 架构说明：[docs/architecture/](./docs/architecture/)
- 接入合同：[docs/adoption/](./docs/adoption/)
- 统一安装体验：[docs/adoption/unified-install-experience.md](./docs/adoption/unified-install-experience.md)
- 宿主适配矩阵：`docs/adoption/host-adapter-matrix.md`
- 版本权威图：[docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md)
- 证据台账：[docs/evidence/](./docs/evidence/)
- 分发合同：[skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)

## 设计哲学

Loom 以合并就绪为中心，并采用行为优先的执行口径。审查、验证、宿主状态、行为证据、
测试证据和收尾是彼此独立但必须收敛一致的表面，任何一个面没有收口，都不应视为工作
完成。
