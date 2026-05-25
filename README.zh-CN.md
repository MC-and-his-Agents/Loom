# Loom

语言：中文 | [English version](./README.md)

Loom 是一个 agent-first project operating layer。

它给编码智能体提供一条 behavior-first 的执行路径：从 adopt、resume、spec、plan、build checkpoint、review、merge-ready，到 handoff 和 closeout。它的目标不是更快地产生业务代码，而是避免智能体工作停在“代码已经改了”，并把目标、行为证据、测试证据、review 状态、主干真相和宿主控制面收敛一致。

## 工作方式

Loom 现在采用 CLI-first。`loom` 命令是执行控制面：它诊断 installed state、读取 fact chain、执行验证、输出 upgrade / repair plan，并用结构化 fail-closed 输出包装场景执行。

`SKILLS` 仍然是 agent-facing 入口。它们帮助智能体发现正确场景，并消费 CLI/runtime 输出。Plugins 和宿主 adapter 负责原生发现与 wiring。`.loom/` 继续作为仓库执行事实表面。npm `loom-installer` 是 compatibility shim，用于 adapter 托管安装、single-skill helper 和 legacy bridge；它不是主体执行层。

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

### Codex 原生 Skills 发现

可以直接这样告诉 Codex：

```text
Fetch and follow instructions from https://raw.githubusercontent.com/MC-and-his-Agents/Loom/refs/heads/main/docs/adoption/codex-install.md
```

也可以手动安装：

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
mkdir -p ~/.agents/skills
for skill in ~/.codex/loom/skills/loom-*; do
  ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
done
```

安装后请重启 Codex，让原生 skills discovery 重新加载 Loom skills。

### Adapter Installer

npm installer 不是 Codex 默认路径。它是 compatibility shim，不是默认控制面。需要 adapter 托管的 plugin 安装、single-skill helper、legacy bridge 或 installer verification output 时再使用：

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

也可以先固定 installer 版本：

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin --host codex
npx loom-installer add plugin --host claude
```

要求：

- Node `>=20`
- Python `>=3.10`，推荐 `3.11+`

Installer 会报告它触达的 distribution layer 和 version context；Loom 的执行语义仍属于 `loom` CLI，以及生成 skills surface 随附的 Python runtime。

## 发布面

Loom CLI 发布面是执行行为的主发布线。它的权威来源是根 `VERSION` 加 GitHub `v*` tag 和 Release 状态。`loom-installer 兼容线` 保持独立，只用于 adapter 托管安装、legacy bridge、verification、安全或 bootstrap 修复。

不要用 npm `@mc-and-his-agents/loom-installer` `latest` 或 `loom-installer-v*` tag 作为 `loom` CLI 已发布的证据。参见 [docs/adoption/loom-cli-release-surface.md](./docs/adoption/loom-cli-release-surface.md) 和 [docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md)。

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

可编辑 skills 源码真相位于 `src/skills/`。生成且提交的安装表面位于 [skills/](./skills/)。每个 `skills/<skill-id>` 都是带 `loom-package.json` 和 `.loom-runtime/` 的自包含 single-skill package。Canonical Codex plugin manifest 位于 [plugins/loom/.codex-plugin/](./plugins/loom/.codex-plugin/)。

## 高级 / 兼容

单 skill 安装仍然保留，作为兼容和高级路径，但它不再是 Loom 的主路径：

```bash
npx @mc-and-his-agents/loom-installer add skill loom-retire --host codex
npx @mc-and-his-agents/loom-installer add skill loom-retire --host claude
```

单独安装的 skill 只会向宿主暴露该 skill 本身。如果你需要 `loom-init` 路由能力和完整 scenario surface，请安装完整仓库和完整生成 skills surface。

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
