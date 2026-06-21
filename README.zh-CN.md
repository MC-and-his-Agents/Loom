# Loom

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/MC-and-his-Agents/Loom) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/MC-and-his-Agents/Loom)

语言：中文 | [English version](./README.md)

Loom 是一个 agent-first project operating layer。

它给编码智能体提供一条 behavior-first 的执行路径：从 adopt、resume、spec、plan、build checkpoint、review、merge-ready，到 handoff 和 closeout。它的目标不是更快地产生业务代码，而是避免智能体工作停在“代码已经改了”，并把目标、行为证据、测试证据、review 状态、主干真相和宿主控制面收敛一致。

## 工作方式

Loom 现在采用 CLI-first。`loom` 命令是执行控制面：它诊断 installed state、读取 fact chain、执行验证、输出 upgrade / repair plan，并用结构化 fail-closed 输出包装场景执行。

`SKILLS` 仍然是 agent-facing 入口，但用户不再把它们作为独立安装面安装。根 `loom` CLI 负责验证 metadata-only 仓库采用，并从全局包安装/注册 Codex 用户级 Loom plugin。发布的 skills payload 在 Codex 用户级 plugin 中，不进入每个目标仓库。`.loom/` 继续作为仓库执行事实表面。npm `loom-installer` package 是 deprecated legacy artifact；它不是当前 CLI、发布线或推荐安装路径。

智能体仍可在需要路由帮助时从 `loom-init` 起步。进入执行后，CLI 是稳定的机器接口：

```bash
loom doctor --target . --json
loom upgrade-plan --target . --json
loom verify --target . --json
loom skills release-check --json
```

基础执行流如下：

1. `loom doctor` 和 `loom verify` 回答仓库当前是否正在消费有效 Loom 层。
2. `loom upgrade-plan` 和 `loom repair plan` 为 current、legacy 或 mixed install 输出下一步非变更动作。
3. Scenario skills 把人和智能体意图路由到 story、spec、build、review、merge-ready、closeout 等 CLI-backed flow。
4. Work Item、spec、plan、build checkpoint、review、merge-ready 和 closeout 共同消费双重证据循环：行为证据描述外部可观察契约，测试证据证明内部实现循环。
5. Runtime evidence、review record、merge checkpoint 和 closeout check 共同让仓库状态与宿主控制面对齐。

## 安装

要求：

- Node `>=20`
- Python `>=3.11`

当前 Loom 安装模型有三个分开的目标：

1. 工作站状态：全局 `loom` CLI。
2. Codex 用户状态：从全局包安装并注册的 Codex 用户级 Loom plugin。
3. 仓库状态：每个目标仓库只记录 metadata-only Loom adoption。

在新工作站和目标仓库上运行：

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom install --target . --apply --json
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

`loom host install` 和 `loom host register` 只写 Codex 用户级工作站状态。
`loom install` 只写仓库 adoption metadata 和 Loom bootstrap 指令；
`loom host verify` 同时验证 metadata-only 仓库边界和 Codex 用户级 plugin
provider 注册。

注册 plugin 后，启动新的 Codex session；如果 Codex Desktop 已经加载过
plugin 列表，则重启 Codex Desktop。Loom 不声称当前 session 会热加载新注册的
plugin。

如果仓库里还存在 `.loom/bin`、`.loom/bootstrap`、`plugins/loom`、
`.agents/skills` 或 Loom-owned 根 `skills`，当前验证会阻断，直到显式完成
迁移或删除。迁移路径见
[docs/adoption/legacy-install-migration.md](./docs/adoption/legacy-install-migration.md)。

在第二台开发机器上打开已采用 Loom 的仓库时，安装全局 CLI、注册 Codex 用户级
plugin，然后验证仓库：

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

详细接入合同与验证命令见
[docs/adoption/unified-install-experience.md](./docs/adoption/unified-install-experience.md)、
[docs/adoption/installation-taxonomy.md](./docs/adoption/installation-taxonomy.md)
和 [docs/adoption/loom-installed-state-v2.md](./docs/adoption/loom-installed-state-v2.md)。

`npx @mc-and-his-agents/loom ...` 只能作为临时运行同一个根 `loom` CLI 的方式。

`loom-installer` 不属于 primary install journey。它只作为 legacy consumer 的 deprecated historical evidence 保留。

### Advanced / Compatibility

历史 native skills-library clone 路径不是新用户的 primary install path：

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
```

请改用根 `loom` CLI。已有 skills-library clone 只应视为 CLI 可以验证、修复或替换的 compatibility source；用户不应把 SKILLS 或 plugins 当作独立安装面安装。

## 输出模式

Loom 命令默认使用上下文安全输出。命令只有在 JSON 能放进有效 stdout
预算时才直接输出完整 JSON；更大的诊断会在 stdout 输出摘要和 artifact locator，
让智能体和 handoff 引用 locator，而不是粘贴完整报告或长日志。

三种输出模式的使用边界：

- 默认 `--json`：用于正常 agent 工作流、review、gate、handoff 和 closeout；
  只传播摘要和 artifact locator。
- Artifact locator：用于诊断超过预算，或其他线程需要读取完整本地证据时；
  artifact 是诊断文件，不是 authored truth carrier。
- 显式 `--full-output`：只在调试、审计或阻断分类需要完整 stdout JSON 时使用。

默认 stdout 硬上限是 16 KiB，summary 目标是 4 KiB。可通过
`LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES`、`LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES`
和 `LOOM_OUTPUT_ARTIFACT_DIR` 对单个进程调整。

## 发布面

Loom CLI 发布面是执行行为的唯一 active 发布线。它的权威来源是根 `VERSION` 加 GitHub `v*` tag 和 Release 状态。`loom-installer deprecated legacy line` 只作为历史 npm/tag 证据保留，不得作为常规发布路径继续前进。

不要用 npm `@mc-and-his-agents/loom-installer` `latest` 或 `loom-installer-v*` tag 作为 `loom` CLI 已发布的证据。最终 legacy baseline 是 `loom-installer-v0.1.119` / npm `0.1.119`，除非后续 deprecation action 只改变 npm metadata。参见 [docs/adoption/loom-cli-release-surface.md](./docs/adoption/loom-cli-release-surface.md) 和 [docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md)。

## 基本工作流

1. 先运行 `loom doctor --target . --json` 或 `loom verify --target . --json`，判断仓库当前 Loom 层。
2. 变更 metadata-only adoption、全局 CLI provider、Codex 用户级 plugin 注册或 legacy residue repair 前，先运行 `loom upgrade-plan --target . --json`。
3. 需要场景路由时，从 `loom-init` 开始，再使用 `loom-adopt`、`loom-resume`、`loom-build`、`loom-review`、`loom-merge-ready` 等 scenario skills。
4. 用 `loom pr gate`、`loom merge check`、`loom merge run`、`loom gate closeout` 等 CLI-backed gate 消费 readiness evidence。
5. 用 `loom-handoff` 或 `loom-retire` 把现场收成可恢复或已关闭状态。

标准受控合并链路是先运行 `loom pr gate <pr> --head-sha <sha> --work-item <WI> --json`，再运行 `loom merge check <pr> --head-sha <sha> --work-item <WI> --json`，最后运行 `loom merge run <pr> --head-sha <sha> --work-item <WI> --apply --json`。required CI、非 required triggered checks 与宿主 branch protection 都会被这条链路消费，但它们不能替代绑定同一 PR head 的 authored Loom semantic review record。

智能体不能把“已经有改动文件”当作完成。对 Loom 来说，只有目标、文档、review 状态、验证证据、主干真相和宿主控制面全部对齐，才算真正完成。

## Skills 库

Loom 当前暴露一个 root entry 和十个 scenario skills：

| Skill | 作用 |
| --- | --- |
| `loom-init` | Root entry；负责初始化或路由到正确场景。 |
| `loom-adopt` | 为仓库建立最小 Loom 接入面。 |
| `loom-resume` | 恢复上下文并继续当前 `Work Item`。 |
| `loom-build` | 在 review 前执行 bounded implementation/build 轮。 |
| `loom-story` | 将产品上下文收束为 User Story、Story Readiness 与业务语义确认点。 |
| `loom-pre-review` | 在正式 review 前检查 readiness。 |
| `loom-spec-review` | 审查 formal spec 路径并产出 `spec-approved` gate。 |
| `loom-review` | 执行正式 review 并记录结果。 |
| `loom-handoff` | 写出可恢复的交接点。 |
| `loom-merge-ready` | 验证 merge readiness。 |
| `loom-retire` | 在不丢弃用户改动的前提下清理并退场。 |

可编辑 skills 源码真相位于 `src/skills/`。Loom 源仓库生成且提交的 [skills/](./skills/) 是源码镜像。真正发布给 Codex 的 skills payload 位于 `plugins/loom/skills/`；`skills/<skill-id>` 不是自包含 single-skill package，也不再携带 `loom-package.json` 或 `.loom-runtime/` 作为分发产物。下游顶层 `skills/` 不再是默认 Loom plugin 安装面。Canonical Codex plugin manifest 位于 [plugins/loom/.codex-plugin/](./plugins/loom/.codex-plugin/)，并通过 `loom host install --host codex --scope user --apply` 安装到用户级 Codex plugin。

## 维护者文档

- 愿景与边界：[VISION.md](./VISION.md)
- 仓库宪法：[AGENTS.md](./AGENTS.md)
- Skills 面：[skills/README.md](./skills/README.md)
- 方法论文档：[docs/methodology/](./docs/methodology/)
- 架构说明：[docs/architecture/](./docs/architecture/)
- 接入合同：[docs/adoption/](./docs/adoption/)
- 统一安装体验：[docs/adoption/unified-install-experience.md](./docs/adoption/unified-install-experience.md)
- 宿主适配矩阵：`docs/adoption/host-adapter-matrix.md`
- 版本权威图：[docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md)
- 证据台账：[docs/evidence/](./docs/evidence/)
- 分发合同：[skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)

## 设计哲学

Loom 以 merge-readiness 为中心，并采用 behavior-first 的执行口径。Review、validation、host state、行为证据、测试证据和 closeout 是彼此独立但必须收敛一致的表面，任何一个面没有收口，都不应视为工作完成。

Loom 不是业务模板、代码生成器，也不是 GitHub、CI、review engine 或 `git worktree` 的替代品。它是 project operating layer 与可执行 skills 层，用来让智能体以一致方式消费这些宿主能力。
