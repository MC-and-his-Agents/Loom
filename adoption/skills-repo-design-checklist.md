# SKILLS Repo Benchmark And Loom Gap Analysis

本文把三个外部样本仓库作为 benchmark，完整评估“一个优秀 `SKILLS` 仓库”在产品面、分发面、shared 层、runtime、验证与升级面上应该长成什么样，并据此修正 Loom 的 gap analysis。

讨论范围刻意收窄为：

- 只评价“作为一个可分发和可消费的 `SKILLS` 仓库”是否优秀
- 不评价 Loom 的治理理念、checkpoint 设计或 harness 目标本身是否成立
- 不把单一仓库的局部实现直接提升为 Loom 默认规则

## 1. 调研方法

本次不再只看 `README` 和 `SKILL.md`，而是按以下六个面完整读取样本：

1. 产品面
   - 用户先看到什么
   - 技能是如何被命名和组织的
2. 安装 / 分发面
   - plugin / marketplace / npm / symlink / bootstrap / package / manifest
3. 技能单元与 shared 层
   - `SKILL.md`、references、scripts、assets、shared skill、meta-skill
4. runtime / tooling 面
   - skill 实际依附什么执行面
   - 真相源落在 skill、CLI、plugin 还是脚本层
5. 测试 / 验证面
   - 是否验证技能触发、显式调用、集成行为、安装后行为、回归
6. 版本 / 升级 / 兼容面
   - version truth、升级路径、兼容界面、同步面宽度

## 2. 样本与一手材料

### 2.1 `anthropics/skills`

- 仓库入口
  - [README](https://raw.githubusercontent.com/anthropics/skills/main/README.md)
- 分发与分组
  - [.claude-plugin/marketplace.json](https://raw.githubusercontent.com/anthropics/skills/main/.claude-plugin/marketplace.json)
- 模板与规范
  - [template/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/template/SKILL.md)
  - [spec/agent-skills-spec.md](https://raw.githubusercontent.com/anthropics/skills/main/spec/agent-skills-spec.md)
- 复杂 skill 样本
  - [skills/pptx/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/SKILL.md)
  - [skills/pptx/editing.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/editing.md)
  - [skills/pptx/pptxgenjs.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/pptxgenjs.md)
- authoring / packaging / eval
  - [skills/skill-creator/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md)
  - [skills/skill-creator/scripts/quick_validate.py](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/scripts/quick_validate.py)
  - [skills/skill-creator/scripts/package_skill.py](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/scripts/package_skill.py)

### 2.2 `obra/superpowers`

- 仓库入口
  - [README](https://raw.githubusercontent.com/obra/superpowers/main/README.md)
- 宿主安装与分发
  - [docs/README.codex.md](https://raw.githubusercontent.com/obra/superpowers/main/docs/README.codex.md)
  - [.codex/INSTALL.md](https://raw.githubusercontent.com/obra/superpowers/main/.codex/INSTALL.md)
  - [.opencode/INSTALL.md](https://raw.githubusercontent.com/obra/superpowers/main/.opencode/INSTALL.md)
  - [.claude-plugin/plugin.json](https://raw.githubusercontent.com/obra/superpowers/main/.claude-plugin/plugin.json)
  - [.claude-plugin/marketplace.json](https://raw.githubusercontent.com/obra/superpowers/main/.claude-plugin/marketplace.json)
  - [.cursor-plugin/plugin.json](https://raw.githubusercontent.com/obra/superpowers/main/.cursor-plugin/plugin.json)
  - [package.json](https://raw.githubusercontent.com/obra/superpowers/main/package.json)
- bootstrap / root behavior
  - [hooks/session-start](https://raw.githubusercontent.com/obra/superpowers/main/hooks/session-start)
  - [hooks/hooks.json](https://raw.githubusercontent.com/obra/superpowers/main/hooks/hooks.json)
  - [hooks/hooks-cursor.json](https://raw.githubusercontent.com/obra/superpowers/main/hooks/hooks-cursor.json)
  - [skills/using-superpowers/SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md)
- workflow / meta skills
  - [skills/brainstorming/SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/brainstorming/SKILL.md)
  - [skills/writing-skills/SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-skills/SKILL.md)
- 测试
  - [tests/claude-code/README.md](https://raw.githubusercontent.com/obra/superpowers/main/tests/claude-code/README.md)
  - [tests/skill-triggering/run-all.sh](https://raw.githubusercontent.com/obra/superpowers/main/tests/skill-triggering/run-all.sh)
  - [tests/explicit-skill-requests/run-all.sh](https://raw.githubusercontent.com/obra/superpowers/main/tests/explicit-skill-requests/run-all.sh)

### 2.3 `larksuite/cli`

- 仓库入口
  - [README](https://raw.githubusercontent.com/larksuite/cli/main/README.md)
- shared / domain skills
  - [skills/lark-shared/SKILL.md](https://raw.githubusercontent.com/larksuite/cli/main/skills/lark-shared/SKILL.md)
  - [skills/lark-doc/SKILL.md](https://raw.githubusercontent.com/larksuite/cli/main/skills/lark-doc/SKILL.md)
- CLI 真相层
  - [cmd/root.go](https://raw.githubusercontent.com/larksuite/cli/main/cmd/root.go)
  - [cmd/update/update.go](https://raw.githubusercontent.com/larksuite/cli/main/cmd/update/update.go)
  - [internal/registry/loader.go](https://raw.githubusercontent.com/larksuite/cli/main/internal/registry/loader.go)
  - [internal/registry/loader_embedded.go](https://raw.githubusercontent.com/larksuite/cli/main/internal/registry/loader_embedded.go)
- 版本与升级
  - [CHANGELOG.md](https://raw.githubusercontent.com/larksuite/cli/main/CHANGELOG.md)
- E2E 测试
  - [tests/cli_e2e/README.md](https://raw.githubusercontent.com/larksuite/cli/main/tests/cli_e2e/README.md)

## 3. 样本画像

### 3.1 `anthropics/skills`: 标准 skill 仓库样板

#### 产品面

这是三者里最接近“标准 `SKILLS` 仓库”的一个。仓库 README 把 skill 定义为“folders of instructions, scripts, and resources”，并强调每个 skill 都是 self-contained folder，核心单位就是 `SKILL.md` 加少量 bundled resources。[README](https://raw.githubusercontent.com/anthropics/skills/main/README.md)

它的首层产品心智非常窄：

- skill 是一个目录
- 目录里必须有 `SKILL.md`
- 其他内容只是可选的 scripts / references / assets

这套定义在模板和 `skill-creator` 中是自洽的。[template/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/template/SKILL.md) [skills/skill-creator/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md)

#### 安装 / 分发面

仓库确实有分发层，但它非常薄：

- Claude Code 用 `.claude-plugin/marketplace.json` 把 skills 分组为 `document-skills`、`example-skills`、`claude-api`
- 用户入口仍然是 `/plugin marketplace add` 和 `/plugin install`
- 分发分组存在，但不会反向变成每个 skill 的第一层用户心智

Anthropic 还提供 `.skill` 打包脚本，但它被放在 `skill-creator` 内部，作为 authoring / distribution tooling，不是整个仓库的对外主叙事。[.claude-plugin/marketplace.json](https://raw.githubusercontent.com/anthropics/skills/main/.claude-plugin/marketplace.json) [skills/skill-creator/scripts/package_skill.py](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/scripts/package_skill.py)

#### 技能单元与 shared 层

Anthropic 没有做一个巨大 shared runtime；而是把 skill 尽可能保持为自包含单元：

- `SKILL.md`
- 按需 `scripts/`
- 按需 `references/`
- 按需 `assets/`

`skill-creator` 甚至把这种模式明写成“three-level loading system”：

1. metadata
2. `SKILL.md` body
3. bundled resources

这意味着深知识是被允许的，但必须通过 progressive disclosure 下沉，而不是默认挤进首屏。[skills/skill-creator/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md)

#### runtime / tooling 面

Anthropic 的 runtime 逻辑基本是 skill-local 的：

- `pptx` 依赖 skill 自带脚本和本地工具链
- `docx` / `xlsx` / `pdf` 同样如此
- 没有一个对所有 skill 都强制暴露的 runtime-state vocabulary

也就是说，它允许复杂 runtime 存在，但把复杂性压在具体 skill 的内部执行面，而不是仓库级公开合同面。[skills/pptx/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/SKILL.md)

#### 测试 / 验证面

Anthropic 的强项不是仓库级 trigger regression，而是 authoring / eval 工具链：

- frontmatter 和结构的轻量验证
- packaging 校验
- eval / benchmark / blind comparison / description optimization

这说明它很重视“skill 质量”，但验证层主要服务 skill 作者，而不是形成一个强协议型的安装 / runtime 合同。[skills/skill-creator/scripts/quick_validate.py](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/scripts/quick_validate.py) [skills/skill-creator/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md)

#### 版本 / 升级 / 兼容面

Anthropic 几乎没有把 install / update / runtime compatibility 扩成一个公开同步面。它的同步面非常窄：

- marketplace grouping
- template
- frontmatter contract
- package skill tooling

这和 Loom 当前把 `registry/install-layout/upgrade-contract/runtime_state` 都抬到入口层形成鲜明对照。

#### 对 Loom 的直接启发

- 强启发
  - user-facing 单元必须尽量自包含
  - 深知识应下沉到 references / scripts / assets
  - skill 首屏只承担触发和 quick reference，不承担总协议说明
- 不能直接照搬
  - Anthropic 没有 Loom 这种 root routing / multi-scene workflow 问题
  - 它的“无 shared runtime 中心”不能被机械上移为 Loom 默认实现

### 3.2 `superpowers`: 技能驱动的方法论产品

#### 产品面

`superpowers` 不是单纯的 skill 示例仓库，而是一个方法论产品。用户先消费的是 workflow：

- brainstorming
- using-git-worktrees
- writing-plans
- subagent-driven-development
- test-driven-development
- requesting-code-review

也就是说，用户先感知“我将怎样工作”，而不是“skills 仓库内部怎样装配”。[README](https://raw.githubusercontent.com/obra/superpowers/main/README.md)

#### 安装 / 分发面

`superpowers` 的分发层非常重，但被很好地隔离在宿主文档和 plugin manifest 中：

- Claude Code marketplace
- Superpowers marketplace
- Codex CLI / App
- Cursor
- OpenCode
- Copilot CLI
- Gemini CLI

每个平台都有自己的安装入口、manifest 或 hook：

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.cursor-plugin/plugin.json`
- `.codex/INSTALL.md`
- `.opencode/INSTALL.md`
- `.opencode/plugins/superpowers.js`
- `hooks/*.json`

关键点不在于“它没有 adapter”，恰恰相反，它 adapter 很多；但这些 adapter 细节被系统性地留在宿主层，而不是写进 skill 首屏。[docs/README.codex.md](https://raw.githubusercontent.com/obra/superpowers/main/docs/README.codex.md) [.codex/INSTALL.md](https://raw.githubusercontent.com/obra/superpowers/main/.codex/INSTALL.md) [.claude-plugin/plugin.json](https://raw.githubusercontent.com/obra/superpowers/main/.claude-plugin/plugin.json)

#### 技能单元与 shared 层

`superpowers` 的 shared 层不是一个 runtime library，而是一个“方法论 bootstrap”：

- `using-superpowers` 是根技能
- `writing-skills` 是 meta-skill
- 各类 workflow skills 表达流程纪律

这意味着它的共享层更偏行为约束和流程编排，而不是 shared scripts contract。[skills/using-superpowers/SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md) [skills/writing-skills/SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-skills/SKILL.md)

#### runtime / adapter 面

`superpowers` 的 root/bootstrapping 非常典型：

- Claude / Cursor 通过 `SessionStart` hook 注入 `using-superpowers`
- OpenCode 通过 plugin 代码改写 config，并把 bootstrap 塞进第一条用户消息
- Codex 通过 symlink / native discovery 暴露 skills

这里最值得注意的不是“用了 hook”，而是：

- root bootstrap 很薄，只负责强制你先进入 skills 纪律
- 平台差异通过 hook / plugin output format / tool mapping 单独适配
- 平台适配细节没有污染到每个 skill 的正文

[hooks/session-start](https://raw.githubusercontent.com/obra/superpowers/main/hooks/session-start) [.opencode/plugins/superpowers.js](https://raw.githubusercontent.com/obra/superpowers/main/.opencode/plugins/superpowers.js)

#### 测试 / 验证面

`superpowers` 是三个样本里最重视 skill behavior regression 的一个。它明确测试：

- 隐式 skill triggering
- 显式 skill requests
- Claude Code 集成行为
- subagent-driven-development 端到端行为
- OpenCode 插件加载和 tools 兼容

也就是说，它验证的是“agent 会不会真的按 skill 行事”，而不只是文档存在与否。[tests/skill-triggering/run-all.sh](https://raw.githubusercontent.com/obra/superpowers/main/tests/skill-triggering/run-all.sh) [tests/explicit-skill-requests/run-all.sh](https://raw.githubusercontent.com/obra/superpowers/main/tests/explicit-skill-requests/run-all.sh) [tests/claude-code/README.md](https://raw.githubusercontent.com/obra/superpowers/main/tests/claude-code/README.md)

#### 版本 / 升级 / 兼容面

`superpowers` 有 version truth，但它不是一个单独的 skills protocol contract，而是宿主工件共同持有：

- `package.json` version
- plugin manifests version
- `RELEASE-NOTES.md`
- 各平台自己的 update story

这说明 multi-host 分发可以 versioned，但不必以仓库级 `registry + install-layout + upgrade-contract` 三件套出现。

#### 对 Loom 的直接启发

- 强启发
  - 宿主适配可以很多，但必须隔离在宿主层
  - root bootstrap 应薄，只做纪律注入和导向
  - skill behavior regression 值得单独测试
- 不能直接照搬
  - `using-superpowers` 的强方法论 bootstrap 不一定适合作为 Loom 的默认用户体验
  - 它更像 process operating system，不是单纯 bundle

### 3.3 `larksuite/cli`: 稳定工具层 + skills 编排层

#### 产品面

`lark-cli` 最关键的结构不是 skills，而是 CLI first。它把产品心智明确分为：

- Human Quick Start
- AI Agent Quick Start
- Agent Skills
- Three-Layer Command System

也就是说，skills 不是孤立产品，而是稳定 CLI 真相层上的 agent-facing 编排面。[README](https://raw.githubusercontent.com/larksuite/cli/main/README.md)

#### 安装 / 分发面

`lark-cli` 的安装故事非常短：

```bash
npm install -g @larksuite/cli
npx skills add larksuite/cli -y -g
```

它的 skill 安装和 CLI 安装是两步，但都是用户可理解的标准动作，不要求用户先理解任何内部 registry / layout / runtime taxonomy。[README](https://raw.githubusercontent.com/larksuite/cli/main/README.md)

#### 技能单元与 shared 层

`lark-cli` 的 shared 层非常清楚：

- `lark-shared` 承担 auth、scope、identity、安全、更新提示
- domain skills 只讲各自业务域
- domain skills 用 references 承接长指南

这是一种很干净的 shared pattern：

- shared skill 负责横切问题
- domain skill 负责业务操作
- 底层 CLI 才是真相源

[skills/lark-shared/SKILL.md](https://raw.githubusercontent.com/larksuite/cli/main/skills/lark-shared/SKILL.md) [skills/lark-doc/SKILL.md](https://raw.githubusercontent.com/larksuite/cli/main/skills/lark-doc/SKILL.md)

#### runtime / tooling 面

`lark-cli` 把真相源明确放在 CLI：

- shortcuts
- API commands
- raw API
- schema
- embedded registry metadata
- async update notice

skills 主要做三件事：

- 告诉 agent 什么时候用哪个 domain skill
- 教 agent 如何调用 `lark-cli`
- 把公共认证和安全规则下沉到 `lark-shared`

这种分层的价值非常高：skill 不需要自己再发明一套 install/runtime truth surface，因为 CLI 已经承担了这层。[cmd/root.go](https://raw.githubusercontent.com/larksuite/cli/main/cmd/root.go) [internal/registry/loader.go](https://raw.githubusercontent.com/larksuite/cli/main/internal/registry/loader.go) [internal/registry/loader_embedded.go](https://raw.githubusercontent.com/larksuite/cli/main/internal/registry/loader_embedded.go)

#### 测试 / 验证面

`lark-cli` 的验证重点不在 automatic skill triggering，而在真实命令工作流：

- 大量 unit tests
- `tests/cli_e2e` 直接跑真实 CLI workflows
- 甚至自带一个本地 skill 来帮助新增 E2E testcase

这说明它把“skill 是否有用”的基础，放在“底层命令系统是否稳定”上，而不是放在一套独立 runtime-state 合同上。[tests/cli_e2e/README.md](https://raw.githubusercontent.com/larksuite/cli/main/tests/cli_e2e/README.md)

#### 版本 / 升级 / 兼容面

`lark-cli` 的升级面也落在 CLI 真相层：

- `cmd/update/update.go` 提供 update command
- JSON 输出中注入 `_notice.update`
- `CHANGELOG.md` 明确持续记录 skills、shortcuts、auth、docs 的变更
- `lark-shared` 甚至要求 agent 在看到 `_notice.update` 后主动提示用户升级 CLI 和 skills

这是一种非常强的分层信号：upgrade semantics 不在 skills repo contract，而在 CLI product contract。[cmd/update/update.go](https://raw.githubusercontent.com/larksuite/cli/main/cmd/update/update.go) [skills/lark-shared/SKILL.md](https://raw.githubusercontent.com/larksuite/cli/main/skills/lark-shared/SKILL.md) [CHANGELOG.md](https://raw.githubusercontent.com/larksuite/cli/main/CHANGELOG.md)

#### 对 Loom 的直接启发

- 强启发
  - 如果存在更底层的稳定工具面，skill 应依附它，而不是复制一套 runtime truth
  - shared skill 是承接横切心智的好模式
  - update / version / compatibility 最好落在更底层产品面
- 不能直接照搬
  - Loom 不是一个域命令行工具
  - `CLI first` 不能被简单翻译为 `scripts first`

## 4. 横向 benchmark

| 维度 | `anthropics/skills` | `superpowers` | `lark-cli` |
| --- | --- | --- | --- |
| 用户主叙事 | 技能目录 + marketplace | workflow product + platform installs | CLI product + agent skills |
| 对外技能单元 | self-contained folder | workflow skill + bootstrap | domain skill + shared skill |
| shared 层 | 少，偏 skill-local resources | 行为约束 / bootstrap / meta-skill | `lark-shared` 横切能力 |
| runtime 真相源 | skill-local scripts/resources | host hooks/plugins + skill discipline | CLI / registry / shortcuts / schema |
| 分发形态 | Claude plugin marketplace + `.skill` 打包 | 多宿主 manifests / hooks / install docs | npm + `npx skills add` |
| 版本面 | 很薄，主要 manifest/template/tooling | package + plugin manifests + release notes | CLI update command + changelog + JSON notice |
| 技能行为回归 | authoring/eval tooling 为主 | 最强，显式测 triggering / integration | 主要测 CLI workflows |
| 用户是否需要理解 runtime taxonomy | 基本不需要 | 基本不需要 | 基本不需要 |

### 4.1 共同成立的结论

三个样本都支持以下结论：

1. 用户主路径必须短
2. 首屏先讲什么时候用、怎么开始
3. 深知识必须下沉
4. 宿主适配可以复杂，但不应占据技能首屏
5. skills 的对外同步面应尽量窄

### 4.2 只在部分样本成立的结论

这些结论不能被过早上移为 Loom 默认内核：

1. root bootstrap 应该很薄
   - 主要由 `superpowers` 强支持
   - `anthropics/skills` 没有同类 root
   - `lark-cli` 也不是 root skill 模式
2. 入口层行为需要专门 trigger regression
   - `superpowers` 强支持
   - `anthropics/skills` 更偏 authoring eval
   - `lark-cli` 更偏 CLI E2E
3. skills 仓库应持有正式安装 / 发现 / 升级 machine contract
   - 三个样本都不强支持 Loom 当前这条做法
   - 它们都证明“需要安装与升级故事”
   - 但都没有证明“必须以仓库级 `registry + install-layout + upgrade-contract` 形式暴露给用户”

## 5. 修正后的设计清单

和上一版相比，这一版把“用户层 checklist”和“结构层 checklist”拆开。

### 5.1 用户层 checklist

| 编号 | 设计项 | benchmark 结论 |
| --- | --- | --- |
| U1 | 用户先看到单一路径 | 必须成立 |
| U2 | `SKILL.md` 首屏先讲触发条件和 quick path | 必须成立 |
| U3 | 用户不需要理解 runtime taxonomy | 必须成立 |
| U4 | 宿主适配细节不占据第一层心智 | 必须成立 |
| U5 | 技能命名与分组贴近用户任务 | 应成立 |

### 5.2 结构层 checklist

| 编号 | 设计项 | benchmark 结论 |
| --- | --- | --- |
| S1 | 深知识下沉到 references / scripts / assets | 必须成立 |
| S2 | 横切能力集中承接 | 应成立 |
| S3 | 若存在更底层工具真相源，skills 依附它 | 强建议 |
| S4 | 宿主安装 / 分发 / hook / manifest 与 skill 正文分层 | 必须成立 |
| S5 | 版本 / 升级面应尽量收敛，不制造多处真相 | 必须成立 |
| S6 | 入口层行为回归值得单独测试 | 候选增强能力 |
| S7 | root bootstrap 应尽量轻薄 | 候选增强能力 |

## 6. Loom 修正版 Gap Analysis

### 6.1 用户层

#### U1. 用户先看到单一路径

Loom 当前状态：

- 弱
- 顶层安装叙事要求宿主读取 `skills/registry.json`、同步 `upgrade-contract.json`、同步 `install-layout.json`、安装 `shared/scripts/assets/references`、再校验 runtime scene，[README.md](/Users/mc/dev/Loom/README.md)

基准对照：

- 三个 benchmark 都把安装故事收成用户可以直接执行的路径
- 没有一个把“技能仓库的内部合同文件”当成用户主叙事

结论：

- 这是 Loom 当前最大的产品面偏差之一

#### U2. `SKILL.md` 首屏先讲触发条件和 quick path

Loom 当前状态：

- 部分成立
- `loom-init` 虽然先讲初始化/路由，但很快进入 CLI、读取顺序、问诊和装配细则，[skills/loom-init/SKILL.md](/Users/mc/dev/Loom/skills/loom-init/SKILL.md)

基准对照：

- `pptx`、`brainstorming`、`lark-doc` 都更克制

结论：

- Loom 的 root skill 首屏仍然太像作者合同，不够像用户入口

#### U3. 用户不需要理解 runtime taxonomy

Loom 当前状态：

- 弱
- `repo-local-demo`、`installed-runtime`、`upgrade-rehearsal` 已经进入 README、`skills/README.md` 和 runtime 脚本词汇，[README.md](/Users/mc/dev/Loom/README.md) [skills/README.md](/Users/mc/dev/Loom/skills/README.md)

基准对照：

- 三个 benchmark 都不会要求用户先形成这一层心智

结论：

- Loom 当前把作者/调试层 vocabulary 泄漏到了用户层

#### U4. 宿主适配细节不占据第一层心智

Loom 当前状态：

- 原则上成立，产品面上未兑现
- `skills/distribution-and-adapter-contract.md` 已经正确表达了 adapter 边界
- 但首屏文档仍然从 adapter/operator 视角写作

基准对照：

- `superpowers` 是最强反例：adapter 很复杂，但写法上被彻底留在宿主层

结论：

- Loom 的问题不是“有 adapter contract”，而是“adapter contract 太靠前”

### 6.2 结构层

#### S1. 深知识下沉

Loom 当前状态：

- 基础设施已具备
- `shared/references/`、`shared/scripts/` 已经在做这件事

问题：

- 首屏没有真正克制，仍重复解释大量 runtime / install / drift 概念

结论：

- Loom 不是不会下沉，而是没有完成用户层与深层的真正切分

#### S2. 横切能力集中承接

Loom 当前状态：

- 部分成立
- 有 `shared/scripts` 与 `shared/references`

基准对照：

- `lark-shared` 给了更好的对照：shared 层应优先承接共享用户心智，而不是只承接共享 runtime 合同

结论：

- Loom 的 shared 层过度偏向内部执行合同中心

#### S3. 若存在更底层工具真相源，skills 依附它

Loom 当前状态：

- 这里最不稳定
- Loom 有 `skills/*/scripts` 与 `shared/scripts`
- 但当前又把脚本树和安装布局一起提升成公开同步面

基准对照：

- `lark-cli` 显示最健康的方式是“skill 依附更底层产品真相”
- Loom 还没有明确它的更底层真相究竟是 CLI、runtime 包、还是 root skill 合同

结论：

- Loom 需要先明确技能层之下的真相边界，再决定哪些工件要公开、哪些只供宿主消费

#### S4. 宿主安装 / 分发 / hook / manifest 与 skill 正文分层

Loom 当前状态：

- 弱

基准对照：

- `superpowers` 证明可以有很多 manifest / hook / install docs，但不让它们变成 skill 首屏内容
- `anthropics/skills` 证明 plugin marketplace grouping 可以存在，同时 skill 仍然保持自包含

结论：

- Loom 当前混层最明显的地方就在这里

#### S5. 版本 / 升级面收敛

Loom 当前状态：

- 弱
- 入口、版本、安装、升级、运行态识别、shared runtime 检查分散在 `registry.json`、`upgrade-contract.json`、`install-layout.json`、各 skill `contract.json`、`runtime_state.py` 和 README 中

基准对照：

- 没有 benchmark 样本支持 Loom 当前这种宽公开面的做法
- 它们支持“需要 upgrade story”
- 但不支持“需要把升级和安装布局同时暴露为用户公开技能合同”

结论：

- Loom 当前的多工件校验是有价值的，但其公开层级明显过高

#### S6. 入口层行为回归

Loom 当前状态：

- 候选增强能力

基准对照：

- `superpowers` 强支持
- `anthropics/skills` 和 `lark-cli` 提供的是侧面支持，不足以上移为默认 core

结论：

- Loom 可以继续保留为 `adapt`
- 但不应把这条当作已经被多个独立样本强验证的稳定边界

#### S7. root bootstrap 应尽量轻薄

Loom 当前状态：

- 弱

基准对照：

- 这条目前主要由 `superpowers` 强支持
- `anthropics/skills` 与 `lark-cli` 不能直接充当第二、第三个 root bootstrap 样本

结论：

- 这条仍适合保留为候选增强能力
- 但在产品直觉上，Loom 仍应朝这个方向收敛

## 7. 对 Loom 的最终判断

如果只从“优秀 `SKILLS` 仓库”来评价，Loom 当前的核心问题不是能力不足，而是分层暴露失衡。

更具体地说：

- Loom 已经具备不错的场景 skill 切分
- Loom 也已经具备 shared references / shared scripts 这种深知识承载能力
- Loom 的主要短板在于：
  - 用户主路径不够短
  - root skill 首屏不够轻
  - 安装态 / 源码态 / rehearsal 态词汇泄漏到首层心智
  - 安装 / 升级 / 运行态合同的公开面过宽
  - `skills/` 同时承担用户产品面、宿主合同面、内部 runtime 认知面

所以更准确的结论不是：

- Loom 不应该有 adapter/runtime/install contract

而是：

- Loom 不应该把这些层直接暴露成 `SKILLS` 仓库的第一层产品面

## 8. 优先修正顺序

若只针对 `SKILLS` 仓库产品面收敛，建议顺序如下：

1. 重写顶层安装叙事
   - 拆开“用户如何安装使用”和“宿主如何适配 Loom”
2. 收缩 `skills/README.md`
   - 让它重新成为入口层产品说明，而不是入口层协议总览
3. 收缩 `loom-init` 首屏
   - 先只保留触发条件、判断入口、场景路由摘要
4. 把 runtime scene / carrier 退到调试和宿主层
   - 不再让 `repo-local-demo` / `installed-runtime` / `upgrade-rehearsal` 占据首层心智
5. 重新划分公开同步面
   - 明确哪些只给宿主消费，哪些才是用户公开面

## 9. 本轮调研的边界

本轮结论已经比“只看 `README` 和 `SKILL.md`”扎实得多，但仍有边界：

- 它是仓库结构研究，不是 live install usability study
- 它没有在每个平台真实执行全部安装流程
- 它没有把所有 skill 都逐个消费一遍

因此它适合用于：

- 修正 Loom 的 `SKILLS` 产品面
- 收窄 Loom 的公开合同面
- 校正哪些结论可以上移，哪些仍应停在候选层

但不适合直接声称：

- 某个 benchmark 仓库的所有细节都能直接成为 Loom 默认规则
