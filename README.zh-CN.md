# Loom

语言：中文 | [English version](./README.md)

Loom 是一个 agent-first project operating layer。

它给编码智能体提供一条 behavior-first 的执行路径：从 adopt、resume、spec、plan、build checkpoint、review、merge-ready，到 handoff 和 closeout。它的目标不是更快地产生业务代码，而是避免智能体工作停在“代码已经改了”，并把目标、行为证据、测试证据、review 状态、主干真相和宿主控制面收敛一致。

## 工作方式

Loom 现在采用 CLI-first。`loom` 命令是执行控制面：它诊断 installed state、读取 fact chain、执行验证、输出 upgrade / repair plan，并用结构化 fail-closed 输出包装场景执行。

`SKILLS` 仍然是 agent-facing 入口，但用户不再把它们作为独立安装面安装。根 `loom` CLI 负责安装、同步和验证生成 skills 与宿主 plugin payload。Plugins 和宿主 adapter 在 CLI 管理下负责原生发现与 wiring。`.loom/` 继续作为仓库执行事实表面。npm `loom-installer` package 是 deprecated legacy artifact；它不是当前 CLI、发布线或推荐安装路径。

智能体仍可在需要路由帮助时从 `loom-init` 起步。进入执行后，CLI 是稳定的机器接口：

```bash
python3 tools/loom.py doctor --target . --json
python3 tools/loom.py upgrade-plan --target . --json
python3 tools/loom.py verify --target . --json
python3 tools/loom.py skills release-check --json
```

基础执行流如下：

1. `loom doctor` 和 `loom verify` 回答仓库当前是否正在消费有效 Loom 层。
2. `loom upgrade-plan` 和 `loom repair plan` 为 current、legacy 或 mixed install 输出下一步非变更动作。
3. Scenario skills 把人和智能体意图路由到 story、spec、build、review、merge-ready、closeout 等 CLI-backed flow。
4. Work Item、spec、plan、build checkpoint、review、merge-ready 和 closeout 共同消费双重证据循环：行为证据描述外部可观察契约，测试证据证明内部实现循环。
5. Runtime evidence、review record、merge checkpoint 和 closeout check 共同让仓库状态与宿主控制面对齐。

## 安装

### Root CLI

安装根 Loom CLI：

```bash
npm install -g @mc-and-his-agents/loom
```

为目标仓库安装并验证 Codex 宿主 payload：

```bash
loom host install --host codex --mode plugin --target . --apply --json
loom host verify --host codex --mode plugin --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

`loom host install` 和 `loom host verify` 管理并验证目标仓库的 plugin
payload：`.loom/installed-state.json`、`plugins/loom/.codex-plugin/plugin.json`
以及内嵌的 `plugins/loom/skills/` skills payload。Codex plugin mode 不再默认写入
或要求下游仓库顶层 `skills/`；如果下游仓库存在顶层 `skills/`，它默认属于目标仓库命名空间，旧 Loom 生成残留只通过 repair / upgrade plan 给出安全迁移建议。

`npx @mc-and-his-agents/loom ...` 只能作为临时运行同一个根 `loom` CLI 的方式。

要求：

- Node `>=20`
- Python `>=3.11`

`loom-installer` 不属于 primary install journey。它只作为 legacy consumer 的 deprecated historical evidence 保留。

### Advanced / Compatibility

历史 native skills-library clone 路径不是新用户的 primary install path：

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
```

请改用根 `loom` CLI。已有 skills-library clone 只应视为 CLI 可以验证、修复或替换的 compatibility source；用户不应把 SKILLS 或 plugins 当作独立安装面安装。

## 发布面

Loom CLI 发布面是执行行为的唯一 active 发布线。它的权威来源是根 `VERSION` 加 GitHub `v*` tag 和 Release 状态。`loom-installer deprecated legacy line` 只作为历史 npm/tag 证据保留，不得作为常规发布路径继续前进。

不要用 npm `@mc-and-his-agents/loom-installer` `latest` 或 `loom-installer-v*` tag 作为 `loom` CLI 已发布的证据。最终 legacy baseline 是 `loom-installer-v0.1.119` / npm `0.1.119`，除非后续 deprecation action 只改变 npm metadata。参见 [docs/adoption/loom-cli-release-surface.md](./docs/adoption/loom-cli-release-surface.md) 和 [docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md)。

## 基本工作流

1. 先运行 `loom doctor --target . --json` 或 `loom verify --target . --json`，判断仓库当前 Loom 层。
2. 变更 installed runtime、skills、plugin 或 companion surface 前，先运行 `loom upgrade-plan --target . --json`。
3. 需要场景路由时，从 `loom-init` 开始，再使用 `loom-adopt`、`loom-resume`、`loom-build`、`loom-review`、`loom-merge-ready` 等 scenario skills。
4. 用 `loom checkpoint merge`、`loom gate pr`、`loom gate closeout` 等 CLI-backed gate 消费 readiness evidence。
5. 用 `loom-handoff` 或 `loom-retire` 把现场收成可恢复或已关闭状态。

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

可编辑 skills 源码真相位于 `src/skills/`。Loom 源仓库生成且提交的 payload 表面位于 [skills/](./skills/)。每个 `skills/<skill-id>` 都是带 `loom-package.json` 和 `.loom-runtime/` 的自包含 skill payload，由根 CLI 管理。下游 Codex plugin 安装把这份 payload 内嵌到 `plugins/loom/skills/`；下游顶层 `skills/` 不再是默认 Loom plugin 安装面。Canonical Codex plugin manifest 位于 [plugins/loom/.codex-plugin/](./plugins/loom/.codex-plugin/)，并通过 `loom host ...` 安装或验证。

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
