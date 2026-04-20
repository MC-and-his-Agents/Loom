# Loom

Loom 是一个面向 agent-first 项目的治理、执行与收口系统。

它解决的不是“怎么生成代码”，而是“项目怎么稳定推进”：

- agent 进入仓库后先从哪里开始
- 老任务如何恢复，而不是靠翻聊天记录
- review 如何前移，而不是把问题全压到最后
- 什么状态下才算真的可以合并
- 合并之后怎么把这一轮工作真正收口

[快速开始](#安装与快速开始) · [Agent Skills](#agent-skills) · [Harness](#harness) · [Workflow](#workflow) · [CLI](#cli-次级入口)

## 为什么用 Loom

Loom 不是业务模板，也不是一组散落的规则文档。
它的价值是把项目运行过程本身变成一套可执行系统。

- 为 agent 原生设计
  - 默认入口是 `SKILLS`，不是让 agent 先记一堆命令
- 让长任务可恢复
  - 当前工作、停点、下一步和阻断项不再只存在于聊天里
- 让 review 分层
  - pre-review、正式 review、merge-ready 各有职责，不把所有问题堆到最后
- 让“完成”变成闭环
  - 代码、PR、状态记录和收口动作一起对齐，而不是“进 main 就算完”

## Loom 会给项目带来什么变化

| 以前 | 使用 Loom 之后 |
| --- | --- |
| agent 进入仓库先猜该做什么 | agent 先进入 `loom-init`，再被路由到正确场景 |
| 老任务恢复靠聊天记录和记忆 | 当前工作状态可恢复、可接手 |
| final review 才第一次系统性发现问题 | pre-review、review、merge-ready 分层暴露问题 |
| 团队说不清“现在到底能不能 merge” | merge-ready 成为独立判断动作 |
| 代码进主干就算结束 | closeout 要求主干、PR、状态记录和控制面对齐 |

## 功能概览

| 能力面 | Loom 提供什么 |
| --- | --- |
| `SKILLS` 入口层 | `loom-init` + 7 个场景 skills，负责让 agent 进入正确动作 |
| `harness` 执行层 | 读取状态、恢复上下文、组织 review、merge-ready 和 closeout |
| `governance` 判断层 | 统一回答什么时候能继续、什么时候能 review、什么时候算完成 |
| `repo companion` 接入层 | 为既有仓库暴露 locator-only manifest、机读 repo requirements 和 specialized gates，而不把单仓规则抬升为 Loom core |
| Agent 平台接入 | 通过 `skills/registry.json`、`skills/install-layout.json`、`skills/upgrade-contract.json` 和 manifest/executable 进行发现、安装、运行态识别和升级 |
| 次级 CLI | 为自动化、脚本和调试保留等价入口 |

## 安装与快速开始

### 环境要求

- 一个支持安装和调用 `SKILLS` 的 Claude Code / Codex 等 Agent 平台
- 对 Loom 仓库的访问权限
- 如需本地验证或调试，需具备 `python3`

### AI Agent 版

最小安装动作是：

1. 获取这个仓库
2. 让 Claude Code / Codex 等 Agent 平台读取 [skills/registry.json](./skills/registry.json)
3. 让 Claude Code / Codex 等 Agent 平台同步 [skills/upgrade-contract.json](./skills/upgrade-contract.json)
4. 让 Claude Code / Codex 等 Agent 平台同步 [skills/install-layout.json](./skills/install-layout.json)
5. 安装或刷新 `loom-init` 与各场景 skill 的：
   - manifest
   - skill-local `scripts/`
   - `shared/scripts/`
   - `shared/assets/`
   - `shared/references/`
6. 确认 Claude Code / Codex 等 Agent 平台能把 `loom-init` 识别为默认入口
7. 用 `loom-init runtime-state` 或 `loom_flow runtime-state` 确认当前场景是 `installed-runtime`，而不是 `repo-local-demo`

不要把 repo-local `tools/` 可运行误当成安装成功。`tools/loom_init.py`、`tools/loom_flow.py`、`tools/loom_check.py` 只保留为仓库开发包装层；installed-skills 的正式执行面在 `skills/*/scripts/` 与 `skills/shared/*`。当前稳定 runtime scene 只允许 `repo-local-demo`、`installed-runtime`、`upgrade-rehearsal`；若缺 shared runtime/resources、layout/registry 漂移或 scene 与 carrier 冲突，Loom 必须 fail-closed 并返回原因。

当前稳定入口包括：

- 默认入口：`loom-init`
- 场景入口：
  - `loom-adopt`
  - `loom-resume`
  - `loom-pre-review`
  - `loom-review`
  - `loom-handoff`
  - `loom-retire`
  - `loom-merge-ready`

升级时，Claude Code / Codex 等 Agent 平台至少应刷新：

- `skills/registry.json`
- `skills/upgrade-contract.json`
- `skills/install-layout.json`
- 各 skill manifest
- skill-local `scripts/`
- `shared/scripts/`
- `shared/assets/`
- `shared/references/`

安装与升级的正式合同见 [skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)。

### 给正在开发项目的 Agent 的快速安装

如果你希望 AI Agent 直接把 Loom 装进它正在开发的项目流程里，可以把下面这段提示词直接发给它：

```text
帮我把 Loom 安装到当前项目使用的 Claude Code / Codex 等 Agent 平台中，并让它可以在这个项目里直接调用。

按 https://github.com/MC-and-his-Agents/Loom 操作：
1. 获取 Loom 仓库
2. 读取 skills/registry.json
3. 读取 skills/upgrade-contract.json
4. 读取 skills/install-layout.json
5. 安装或刷新 loom-init 和所有场景 skills 的 manifest、skill-local scripts、shared/scripts、shared/assets、shared/references
6. 确认 loom-init 被识别为默认入口
7. 安装完成后，不要直接开始改代码；先用 loom-init 判断当前项目属于哪个场景，并告诉我下一步应该进入哪个 skill

如果当前 Claude Code / Codex 等 Agent 平台使用的是本地 skills 目录、manifest 注册或等价机制，请按该平台的标准方式完成安装。
如果安装失败，请明确告诉我卡在哪一步。
```

这段提示词的目的不是让 agent 学会 Loom 的内部结构，而是让它先把 Loom 接进当前项目，再开始后续开发。

## Agent Skills

Loom 当前稳定提供 1 个默认入口和 7 个场景 skills。

| Skill | 什么时候用 | 它解决什么问题 |
| --- | --- | --- |
| `loom-init` | agent 第一次进入仓库时 | 我现在到底该从哪里开始？ |
| `loom-adopt` | 新项目或还没接入 Loom 的仓库 | 这个项目怎么装上 Loom 骨架？ |
| `loom-resume` | 接手做到一半的工作时 | 这件事怎么恢复并继续做？ |
| `loom-pre-review` | 正式 review 之前 | 能不能先把明显问题提前找出来？ |
| `loom-review` | 进入正式 review 时 | 怎么形成后续还能消费的审查结果？ |
| `loom-handoff` | 要换人继续时 | 怎么把当前状态讲清楚交给下一位执行者？ |
| `loom-retire` | 这轮执行不继续时 | 怎么做干净退出，不留悬空现场？ |
| `loom-merge-ready` | 判断是否可合并时 | 现在到底能不能 merge？ |

这些 skill 的作用不是解释原则，而是把 agent 带到正确场景。

## Harness

如果说 `SKILLS` 是前门，`harness` 就是后面的执行机械层。

它负责的不是“告诉 agent 应该想什么”，而是让下面这些事真的可执行：

| Harness 职责 | 对 agent 的意义 |
| --- | --- |
| 读取当前工作状态 | agent 不用从聊天和 PR 手工拼上下文 |
| 恢复上下文 | 老任务可以重新进入执行回合 |
| 维护执行现场 | 当前工作不会因为多轮推进而失控 |
| 组织 pre-review / review / merge-ready | 审查开始分层，而不是都堆到最后 |
| 执行 closeout 并对齐控制面 | “完成”不再只等于代码合并 |

没有 harness，skills 只是几个入口名。
有了 harness，skills 才会变成稳定 workflow。

## Workflow

Loom 的 workflow 不是一串命令顺序，而是一条 agent 在仓库里实际经历的执行回合。

典型主路径是：

`接入 -> 场景识别 -> 执行/恢复 -> pre-review -> review -> merge-ready -> closeout`

分支路径是：

- `handoff`
- `retire`

它们用于移交、暂停或退出，不是每一轮都必经的主终点。

### 1. 接入

agent 或 Claude Code / Codex 等 Agent 平台先把 Loom 接进项目。

你会得到什么：

- 项目第一次获得默认入口、验证入口和恢复入口
- agent 不再一进仓库就直接改代码

你需要接受什么变化：

- 项目要开始承认一套统一入口，而不是每次临场约定
- 后续执行会围绕 Loom 的入口链推进

适合什么项目：

- 想长期使用 agent 推进开发的项目
- 会持续新增事项、需要多轮推进的项目

不太适合什么项目：

- 一次性脚本仓库
- 没有持续执行需求、也不需要协作收口的小改动仓库

Loom 在这里做了什么：

- `loom-adopt` 负责接入场景
- harness 建立后续执行所需的最小支撑面
- 对既有仓库，优先通过 `repo companion` 暴露 repo-specific requirements / specialized gates，而不是重写根规则文档

### 2. 场景识别

agent 进入 `loom-init`。

你会得到什么：

- agent 不再先猜现在该 adopt、resume、review 还是收口
- 当前场景和当前工作开始明确

你需要接受什么变化：

- 进入工作前要先做一次场景判断
- 不是每次都从“直接开始改代码”起步

Loom 在这里做了什么：

- `loom-init` 负责路由
- harness 提供读取仓库状态所需的底层能力

### 3. 执行 / 恢复

agent 进入 `loom-adopt` 或 `loom-resume`。

你会得到什么：

- 当前工作、停点、下一步、阻断项开始进入可消费载体
- 长任务从“聊天记忆驱动”变成“可恢复的执行回合”

你需要接受什么变化：

- 当前工作不再只存在于会话里
- 任务推进需要持续回写停点、下一步和阻断项
- 执行现场开始变成需要被维护的对象，而不是随手开工的副产物

适合什么项目：

- 多 agent 接力的项目
- 一项工作会持续多天或多轮的项目
- 经常被 review、等待、切换优先级打断的项目

不太适合什么项目：

- 单人、一次性、几十分钟内能完成的小变更
- 几乎没有中断和接手成本的仓库

Loom 在这里做了什么：

- `loom-resume` 负责把 agent 带回正确执行点
- harness 负责当前工作状态、恢复、执行现场与状态读取

### 4. pre-review

agent 进入 `loom-pre-review`。

你会得到什么：

- 明显缺口先被提前暴露
- 正式 review 不再承担第一次系统性发现问题的职责

你需要接受什么变化：

- 不是写完就直接进正式 review
- 在 review 前要先过一层预检

适合什么项目：

- review 成本高的项目
- reviewer 容易过载、意见反复的项目

不太适合什么项目：

- 几乎没有正式审查动作的小型个人仓库

Loom 在这里做了什么：

- `loom-pre-review` 负责进入预检场景
- harness 负责 state-check、checkpoint、runtime evidence 等读面和门禁

### 5. review

agent 进入 `loom-review`。

你会得到什么：

- review 从“有人看过”变成“有正式审查结果”
- 审查结果开始成为后续放行判断的输入

你需要接受什么变化：

- review 不再只是 PR 评论或口头意见
- 审查结论要成为后续是否放行的正式输入

适合什么项目：

- 有正式 code review 需求的项目
- 共享模块、核心抽象、风险边界明显的项目

不太适合什么项目：

- 没有正式审查机制的极轻量个人实验仓库

Loom 在这里做了什么：

- `loom-review` 负责正式 review 入口
- harness 负责 review execution 与 review record

### 6. merge-ready

agent 进入 `loom-merge-ready`。

你会得到什么：

- “能不能 merge”从主观判断变成统一判断
- 项目从“接近完成”变成“明确可 merge / 不可 merge / 需回退”

你需要接受什么变化：

- merge 前要多一个明确判断动作
- 团队不能再只靠“看起来差不多”决定是否合并

适合什么项目：

- 有多人协作和持续合并节奏的项目
- 经常出现“CI 绿了但其实还没准备好”这类问题的项目

不太适合什么项目：

- 没有稳定 review / validation 流程的小型一次性仓库

Loom 在这里做了什么：

- `loom-merge-ready` 负责进入放行判断场景
- harness 负责 merge checkpoint、review 输入和状态聚合

### 7. closeout

主路径的最后一步是 closeout。

你会得到什么：

- “完成”不再只是代码进主干
- 主干、issue、PR、project 和状态记录开始一起对齐

你需要接受什么变化：

- 完成不再只看代码结果
- 还要把状态记录、交接痕迹和控制面对齐

适合什么项目：

- 对交付闭环、审计和后续维护要求高的项目
- 经常出现“代码合了但事情没真完”的项目

不太适合什么项目：

- 对关闭语义没有明确要求的临时仓库

Loom 在这里做了什么：

- skill 把执行者带到正确收口动作
- harness 负责 closeout check / sync 与控制面对齐

### 分支路径：handoff 和 retire

如果当前工作要换人继续，就进入 `loom-handoff`。
如果当前执行现场要干净退出，就进入 `loom-retire`。

它们解决的是：

- 暂停时不丢上下文
- 移交时不丢状态
- 退出时不留下悬空现场

这两条分支尤其适合：

- 多 agent 接力
- 工作经常被中断
- 需要明确“暂停”和“结束”差别的项目

## CLI 次级入口

Loom 的首选入口是 `SKILLS`。

CLI 主要给这些情况使用：

- 写脚本
- 做自动化
- 调试底层行为

最常见的底层命令包括：

- `python3 tools/loom_init.py route --target <repo> ...`
- `python3 tools/loom_flow.py flow resume|pre-review|review|handoff|merge-ready --target <repo>`
- `python3 tools/loom_flow.py closeout ...`
- `python3 skills/loom-init/scripts/loom-init.py route --target <repo> ...`
- `python3 skills/shared/scripts/loom_flow.py checkpoint|state-check|closeout ...`
- `make loom-check`

其中 `skills/*/scripts/` 与 `skills/shared/scripts/` 才是 installed-skills 的正式 CLI 面；repo-local `tools/` 只用于当前仓库开发和调试，不构成安装态证明。若 `runtime-state` 没有返回 `installed-runtime` 或显式的 `upgrade-rehearsal`，就不能把当前入口宣称为已安装 runtime 成功。

这条 fail-closed 纪律同样覆盖 `purity-check`、`workspace cleanup|retire`、`reconciliation audit|sync`、`closeout check|sync`；安装态 runtime/layout/resources 漂移时，这些入口必须先停下，而不是继续消费宿主控制面。

## 深入阅读

- [skills/README.md](./skills/README.md)
- [harness/README.md](./harness/README.md)
- [skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)
- [VISION.md](./VISION.md)
- [docs/complete-kernel-release.md](./docs/complete-kernel-release.md)
- [adoption/versioning-and-upgrades.md](./adoption/versioning-and-upgrades.md)
