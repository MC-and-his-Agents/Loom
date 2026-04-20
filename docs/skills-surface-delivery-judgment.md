# Loom Installable SKILLS Delivery Judgment

本文冻结 Loom 下一轮 `SKILLS` 交付树的实施判断。

本轮不再沿用“`skills surface convergence`”那棵 `minor` 树，而是改为一棵新的 `major` 树，目标是把 Loom 收敛成一组 repo-local 的稳定交付形态：

- `repo-local plugin`
- `repo-local loom CLI`
- `scenario skills`
- `single-skill standard-skill packages`

本文回答五件事：

1. 本轮工作的交付目标是什么
2. 本轮工作的 issue tree 应如何拆
3. PR 应如何分批，哪些不得混线
4. release goal 与默认版本判断是什么
5. 什么条件满足后，这轮工作才算 closeout

它不回答：

- Loom 后续是否要做全局发行
- 是否要发 npm / pipx / Homebrew
- 未来是否要把单 skill 安装再升级成单独 plugin

长期阶段路线仍以 [roadmap.md](/Users/mc/dev/Loom/docs/roadmap.md) 为准。
版本语义仍以 [adoption/versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md) 为准。
可直接提交的 issue tree 草案见 [skills-surface-issue-tree-draft.md](/Users/mc/dev/Loom/docs/skills-surface-issue-tree-draft.md)。

## 1. 一句话判断

Loom 下一轮工作的正确目标，不是继续收 README 首屏，也不是把每个 skill 都提升成独立 plugin。

正确目标是：

- 用一个正式 plugin 解决安装面
- 用一个正式 CLI 解决执行内核
- 用一组标准 skills 解决场景封装
- 同时正式支持单 skill 安装，但单 skill 安装物不再承担完整 runtime

换句话说：

`plugin = 安装对象`

`CLI = 执行内核`

`skills = 场景封装`

## 2. 本轮交付目标

本轮只收以下目标：

1. 正式冻结新的四层产品结构
   - `repo-local plugin`
   - `repo-local loom CLI`
   - `scenario skills`
   - `single-skill standard-skill packages`
2. 正式冻结三条公开面
   - plugin 安装
   - CLI 直接调用
   - 单个标准 skill 安装
3. 把当前分散的 `loom_init.py` / `loom_flow.py` / `loom_check.py` 收敛成单一 `loom` 命令面
4. 把 public skills 收成 CLI 场景封装，而不是各自背完整 runtime
5. 完成 plugin packaging、single-skill packaging、versioning、validation 与 closeout

## 3. 本轮非目标

以下内容明确不进入本轮：

1. 全局发行 Loom CLI
2. 发布 npm 包
3. 把每个 public skill 都变成独立 plugin
4. 重写 `skills/registry.json`
5. 重写 `skills/install-layout.json`
6. 重写 `skills/upgrade-contract.json`
7. 修改隐式路由优先级、root entry 身份或 scene role contract
8. 重写 runtime evidence / fail-closed 语义

原因很简单：

- 本轮要先把安装面、执行面和场景封装层的产品结构做对
- 分发渠道和 machine semantics 的扩大，不应和这棵树混线

## 4. 产品结构判断

### 4.1 正式安装对象

本轮正式安装对象只有一个：

- `loom` repo-local plugin

它负责：

- 被 Codex 发现和安装
- 暴露 Loom 的 skills
- 私有携带 shared runtime / references / resources

### 4.2 正式 CLI

本轮正式执行内核固定为：

- repo-local `loom` CLI

它负责：

- 统一收敛 `init` / `route` / `flow` / `review` / `check`
- 统一编排 `gh`、`git`、`make` 等宿主工具
- 给 plugin 和单 skill 安装物提供共同执行面

### 4.3 正式 skills

本轮 public skills 的职责固定为：

- 解释什么时候进入该场景
- 解释最小输入和输出
- 调用统一 `loom` CLI

它们不再承担：

- 作为独立安装对象解释整套 Loom runtime
- 复制 Loom 内核真相
- 各自定义一套宿主工具编排语义

### 4.4 单 skill 安装形态

本轮仍正式支持单 skill 安装，但其正式形态固定为：

- 标准 skill 包
- 包内最小 `loom` shim / launcher
- 包内私有 CLI 资源

本轮不把单 skill 安装做成：

- 单独 plugin
- 依赖用户先安装完整 plugin 的半成品壳

## 5. issue tree 判断

这轮工作应建立 parent issue。

原因：

- 它同时涉及 GitHub truth、plugin packaging、CLI 入口、skills 封装、adoption、release 与 closeout
- 若不提前固定拆分方式，很容易把 CLI 收敛、plugin 实施、single-skill packaging 和 release judgment 混成一条 PR

### 5.1 Parent issue 语义

parent issue 负责：

- 总目标
  - `repo-local plugin + repo-local loom CLI + scenario skills`
- 默认 PR slices
- release goal
- closeout basis

parent issue 不直接承担实现主体。

### 5.2 Child issue 默认拆分

默认拆为 5 个 child issue，不混线：

1. `freeze-installable-skills-major-tree`
   - 类型：`spec / planning issue`
   - 负责冻结新的产品结构、三条公开面、默认版本判断和 stop conditions

2. `loom-plugin-install-surface`
   - 类型：`active execution issue`
   - 负责正式 `loom` plugin、marketplace 和 plugin 安装主路径

3. `loom-cli-and-pilot-skill-wrappers`
   - 类型：`active execution issue`
   - 负责统一 `loom` CLI，以及 `loom-init` / `loom-review` 两个试点封装

4. `remaining-scene-skills-and-boundary-docs`
   - 类型：`active execution issue`
   - 负责其余 scene skills、single-skill packaging 扩展、boundary / versioning 文档对齐

5. `installable-skills-validation-release-closeout`
   - 类型：`validation / closeout issue`
   - 负责验证记录、release judgment、closeout basis 和对外收口说明

## 6. 默认 PR Slices

本轮默认固定为 4 批 PR：

### PR-1 `freeze + issue tree rewrite`

职责：

- 重写 `#232-#237`
- 冻结新的产品结构、公开面和 `v0.4.0`
- 把 delivery judgment 与 issue tree 收成版本控制中的真相

不得混入：

- plugin 实际安装树
- CLI 聚合实现
- release note

### PR-2 `loom plugin install surface`

职责：

- `plugins/loom/`
- `.agents/plugins/marketplace.json`
- 根 README 的 plugin 安装主路径

不得混入：

- single-skill packaging
- CLI 聚合逻辑
- release note

### PR-3 `loom cli + pilot skills`

职责：

- 统一 `loom` CLI
- `loom-init`
- `loom-review`
- 单 skill 包的最小 shim / shadow runtime 模式

不得混入：

- 其余 scene skills 扩展
- release note

### PR-4 `remaining skills + boundary + release + closeout`

职责：

- 其余 scene skills
- single-skill packaging 扩展
- `skills/distribution-and-adapter-contract.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`
- validation / release / closeout

不得混入：

- 全局发行渠道
- npm / pipx / Homebrew

## 7. release goal 判断

### 7.1 本轮 release goal

本轮 release goal 应明确写成：

`让 Loom 成为一个 repo-local plugin + repo-local CLI + scenario skills 的可安装产品层，并正式支持 single-skill packaging，但暂不进入全局发行。`

### 7.2 默认版本判断

本轮默认按 `major but still pre-1` 规划。

目标版本：

- `v0.4.0`

理由：

- 会正式改变 Loom 的安装对象、CLI 公开面和 single-skill 安装形态
- 会把当前多脚本入口降为非正式公开面
- 会重写 `skills` 对外的交付方式

### 7.3 何时继续抬升范围

若本轮出现以下任一变化，应拆成后续树，不继续塞进 `v0.4.0`：

1. 全局 CLI 发行
2. npm / pipx / Homebrew 分发
3. 每个 public skill 独立 plugin 化
4. `registry/install-layout/upgrade-contract` 的 machine 语义变化
5. runtime evidence / fail-closed 语义变化

## 8. Done When

只有当以下条件同时满足时，本 issue 才可 closeout：

1. GitHub issue tree 已重写为新的 major 实施树
2. `loom` plugin 已可在 repo 内被发现和安装
3. `loom` CLI 已成为正式公开执行内核
4. `loom-init`、`loom-review` 与其余 scene skills 已成为 CLI 场景封装
5. 单 skill 安装已形成标准 skill 包 + 最小 CLI shim 的正式形态
6. 根 README、boundary 文档、versioning 文档、validation 文档与 release note 已对齐新的产品结构
7. parent issue 不再依赖会话解释“为什么这轮不发 npm、也不做每个 skill 一个 plugin”
