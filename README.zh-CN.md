# Loom

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/MC-and-his-Agents/Loom) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/MC-and-his-Agents/Loom)

语言：中文 | [英文版本](./README.md)

Loom 是一个智能体优先的项目运营层：一个面向编码智能体的结构化执行框架。它提供
一条行为优先的路径，贯穿从仓库采纳、合并就绪到收尾的全过程。

Loom 不刻意追求代码生成速度本身。它确保工作最终收敛到更强的完成状态：目标、
文档、审查状态、验证证据、主干事实和宿主控制面保持一致。它采用命令行优先
设计，在仓库边界只保留元数据，并围绕五个协同平面构建：治理事实、支撑编排、
行为与测试证据、规范约束和可执行技能。

## Loom 解决的问题

当人和智能体都能快速生成代码时，真正的瓶颈会从代码生成转移到持续、有序的
执行。Loom 解决这个问题的方式不是复用业务代码，而是复用项目如何被组织、如何
进入执行、如何跨轮推进、如何达到合并就绪，以及如何收尾的运行结构。

新项目不再需要从“空仓库 + 临时约定 + 零散上下文”开始，而是可以从一套可持续、
可验证、可由智能体操作的运行时结构开始。

Loom 不决定构建什么产品、如何设计产品架构、如何对业务领域建模，也不要求所有
项目采用相同目录结构。它关注项目运营，而不是业务实质。

## 架构概览

从愿景视角看，Loom 是一个三层系统；在仓库实现层面，它落为五个稳定部分：

- 治理定义规则、审查模型和收尾语义。
- 支撑提供执行支持、工作区隔离、恢复机制和运行时可见性。
- 模板承载结构化工件。
- 技能将这些能力组装成可执行入口。
- 采纳记录能力的提取来源及当前落地位置。

依赖流严格单向：治理定义规则，模板承载结构，支撑在治理约束下运行，技能读取
所有内容并组装入口，采纳提供证据与演化。技能不能重新定义治理规则，模板不能
成为唯一事实来源，状态展示也不能成为第二个
条目事实来源。

## 工作理念

Loom 采用命令行优先设计。全局 `loom` 命令负责安装 Codex 用户级插件、记录
仅元数据的仓库采用、读取事实链并执行验证。智能体从 `loom-init`
进入路由，再使用 `loom-adopt`、`loom-resume`、`loom-build`、`loom-review` 和
`loom-merge-ready` 等场景技能推进工作。

Loom 围绕工作项组织执行；工作项是正式执行入口。工作会沿着固定门控链推进：
规格门控、构建门控、审查门控和合并门控。每个门控都消费证据，并产出通过、阻塞
或回退裁决。

Loom 还分离事实来源。治理规则、执行事实、审查记录和 GitHub 拉取请求、CI、
议题等宿主状态各自占据独立通道。命令行工具读取并汇总这些来源，但不创建第二份
事实副本。当某个门控通过时，相关层面已经围绕同一项工作完成校验。

## 快速开始

把这段提示词复制给编码智能体：

```text
请在当前仓库安装 Loom，使用当前全局命令行模型。采用仅元数据的仓库采用方式；
不要创建仓库内 Loom 运行时、插件内容、`.loom/bin`、`.agents/skills` 或
Loom 管理的根 `skills`。按下面步骤执行。
如果命令失败，停止并汇报失败命令以及 `loom repair plan --target . --json`。
```

前置要求：Node `>=20`，Python `>=3.11`。

1. 安装根命令行工具：

```bash
npm install -g @mc-and-his-agents/loom
```

2. 安装并注册 Codex 用户级插件：

```bash
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
```

3. 让当前仓库采用 Loom：

```bash
loom install --target . --apply --json
```

4. 验证安装：

```bash
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

5. 在新的 Codex 会话中从 `loom-init` 开始工作；如果 Codex Desktop 已经加载过
   插件列表，重启 Codex Desktop。

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
测试证据和收尾是彼此独立但必须收敛一致的表面，任何一个面没有收口，都不应视为工作完成。

Loom 不是业务模板、代码生成器、仅限规格驱动开发的工具，也不是 GitHub、CI、审查引擎或
`git worktree` 的替代品。它是项目运营层与可执行技能层，用来让智能体以一致方式消费这些宿主能力。
