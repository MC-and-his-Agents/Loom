# Loom Installable SKILLS Issue Tree Draft

本文把 [skills-surface-delivery-judgment.md](/Users/mc/dev/Loom/docs/skills-surface-delivery-judgment.md) 直接翻成一版可提交的 GitHub issue tree 草案。

目标不是继续分析，而是提供：

- 1 个 parent issue 草案
- 5 个 child issue 草案
- 4 个 PR slice 对应关系

本稿默认用于 Loom 下一轮 `repo-local plugin + repo-local loom CLI + scenario skills + single-skill standard-skill packages` 工作。

## 1. Parent Issue Draft

### 标题

`冻结 Loom v0.4.0 的 repo-local 交付形态：plugin、loom CLI、scenario skills 与 single-skill standard-skill packages`

### 类型

`spec / planning issue`

### 建议正文

```md
## Type

`spec / planning issue`

## Goal

把 Loom 下一轮对外交付面冻结成一组 repo-local 的稳定形态，并把后续实现、验证、release judgment 与 closeout 所需的 GitHub truth 一次性写清。

本树只承接以下四层交付面：

1. `repo-local plugin`
2. `repo-local loom CLI`
3. `scenario skills`
4. `single-skill standard-skill packages`

本树的目标不是继续讨论“用户可见单元到底怎么命名”，而是把这四层各自承接什么公开面、彼此如何装配、以及下一轮为什么按 `v0.4.0` 的 `major but still pre-1` 管理，全部冻结为可直接消费的仓库真相。

## Why

`v0.3.0` 已经收清了 Loom 的基础能力面，包括：

- root + 场景入口
- review / guardian / merge gate / closeout 的分层治理
- closeout / reconciliation 的 fail-closed 顺序
- adoption / release / upgrade 的最小版本化公开面

但当前这棵树的 GitHub truth 仍停留在旧 framing：

- “安装整个 Loom”
- “单个用户可见 skill 产品单元”
- `invocation-independent`
- `shared runtime / shared user understanding`

这组说法已经不足以承接最新共识。

现在需要冻结的新判断是：

- Loom 的 repo-local 默认交付物首先是 `plugin`
- `loom CLI` 是 repo-local 次级入口，不是新的事实真相源
- 用户侧执行入口以 `scenario skills` 为准
- 单 skill 交付不再写成抽象“产品单元”，而是写成 `single-skill standard-skill package`
- 这一轮会明显改变下游如何安装、识别和理解 Loom，因此应按 `major` 管理
- 但 Loom 仍处于 pre-1 阶段，这次发布目标仍写作 `v0.4.0`，不伪装成 `v1.0.0`

## Scope

本树只收以下目标：

1. 冻结 `repo-local plugin` 的默认入口、首层说明与交付摘要
2. 冻结 `repo-local loom CLI` 的定位、入口边界与非主路径角色
3. 冻结 `scenario skills` 与 `single-skill standard-skill packages` 的边界、装配关系与说明合同
4. 冻结 `v0.4.0` 的 release goal、`major but still pre-1` 判断、major gate、guardian gate 与 closeout basis
5. 固定 parent / child issue 语义与 PR 顺序，避免后续 PR 再次临场发明边界

## Constraints

- 不把 `skills` 提升为新的治理真相源
- 不把 `repo-local plugin` 写成宿主平台特定实现说明
- 不把 `repo-local loom CLI` 写成用户第一入口
- 不把单个 `scenario skill` 的 package 误写成“自带整包 Loom 理解前提”
- 不把某个宿主的 marketplace、路径、按钮、hook 或权限细节直接提升为 Loom 默认规则
- 不在 child PR 里临场重写 parent 的 release judgment、major gate 或 closeout basis

## Child Issues

- `#233` 冻结 `v0.4.0` 的目标边界、版本判断与 major gate
- `#234` 收 `repo-local plugin` 的默认入口、交付摘要与用户主路径
- `#235` 收 `repo-local loom CLI` 的定位、入口边界与 repo-local 操作面
- `#236` 收 `scenario skills` 与 `single-skill standard-skill packages` 的边界、装配关系与说明合同
- `#237` 最后补 validation、release judgment 与 parent closeout basis

## Default PR Slices

1. `PR-1`：`#233`
2. `PR-2`：`#234`
3. `PR-3`：`#235`
4. `PR-4`：`#236 + #237`

## Release Goal

让 Loom 从 `v0.3.0` 的“稳定 root + scene entry / harness / closeout / release 面”，进入 `v0.4.0` 的 repo-local 交付形态：

- repo 内默认通过 `plugin` 暴露 Loom
- repo 内保留 `loom CLI` 作为次级执行与自动化入口
- 用户可执行面由 `scenario skills` 承接
- 单 skill 交付通过 `single-skill standard-skill packages` 表达，而不再依赖旧的“单个用户可见 skill 产品单元”表述

默认版本判断：`major`

版本号目标：`v0.4.0`

这里的 `major` 表示：
- 安装面、调用面、交付面和升级判断都发生了显著变化
- 下游必须显式重读 release / upgrade / install truth

这里的 `still pre-1` 表示：
- Loom 仍未进入 `v1.x` 的稳定承诺阶段
- 本轮不是伪装成“已经定型”的终局版本，而是 pre-1 阶段的一次重大收敛

## Done When

只有当以下条件同时满足时，本 issue 才可 closeout：

1. 四层 repo-local 交付面已被写成稳定 GitHub truth：
   - `repo-local plugin`
   - `repo-local loom CLI`
   - `scenario skills`
   - `single-skill standard-skill packages`
2. `v0.4.0`、`major but still pre-1`、major gate、guardian gate 已被固定，不再依赖会话解释
3. 后续 PR 不再需要重新争论“这一轮到底在交付什么”
4. 旧 framing 已退出 parent / child issue 的第一层叙事
5. parent closeout comment 可以直接说明：
   - 本轮收了什么
   - 哪些对象进入 `v0.4.0`
   - 哪些事项被明确延期
   - 下一棵树从哪里接续

## Closeout Basis

parent closeout 只消费 child issue 已成立的真相，不替代 child 的独立完成判断。

parent closeout comment 至少要写清：

1. `repo-local plugin` 收了什么
2. `repo-local loom CLI` 收了什么
3. `scenario skills` 与 `single-skill standard-skill packages` 的边界如何成立
4. 为什么本轮是 `v0.4.0` 的 `major but still pre-1`
5. 哪些事项被延期到下一棵树
```

## 2. Child Issue Drafts

### 2.1 `freeze-installable-skills-major-tree`

#### 标题

`冻结 v0.4.0 的目标边界：repo-local delivery shape、major but still pre-1 与 major gate`

#### 类型

`spec / planning issue`

#### 建议正文

```md
Parent issue: #232

## Type

`spec / planning issue`

## Goal

把 `v0.4.0` 这一轮到底收什么、不收什么、为什么按 `major but still pre-1` 管理、以及后续 PR 必须遵守哪些 major gate，全部冻结成 GitHub truth。

## Responsibilities

- 冻结 `repo-local plugin + repo-local loom CLI + scenario skills + single-skill standard-skill packages` 这组目标形态
- 冻结 `v0.4.0` 是下一正式产品版本
- 冻结这一轮按 `major` 管理，但 Loom 仍处于 pre-1 阶段
- 冻结默认 PR 顺序、major gate、guardian gate 与 parent closeout basis
- 明确淘汰旧的“双安装形态 / 单个用户可见 skill 产品单元” framing
- 明确 child PR 不得临场降写为 `minor` 或 `patch`

## Done When

1. 已明确 `v0.4.0` 的 repo-local delivery shape 只承接四层交付面
2. 已明确本轮默认版本判断是 `major`，但仍是 `pre-1`
3. 已明确 major gate：
   - 不得越过 `#233` 重新定义产品形态
   - 不得把 host-specific 细节伪装成 Loom 默认规则
   - 不得让 `loom CLI` 变成新的真相源
4. 已明确 guardian gate 与 closeout basis
5. 后续执行 issue 不再需要重复解释“为什么旧 framing 已失效、为什么这一轮按 `v0.4.0` 的 `major but still pre-1` 管理”
```

### 2.2 `loom-plugin-install-surface`

#### 标题

`收敛 repo-local plugin 的默认入口、交付摘要与用户主路径`

#### 类型

`active execution issue`

#### 建议正文

```md
Parent issue: #232

## Type

`active execution issue`

## Goal

把 Loom 在 repo 内的默认交付形态写成 `repo-local plugin`，回答安装后用户得到什么、默认从哪里开始、以及 plugin 首层应该承接哪些说明。

## Responsibilities

- 明确 `repo-local plugin` 是 repo 内默认交付入口
- 明确 plugin 首层默认暴露什么：
  - Loom 的默认进入方式
  - repo-local 的安装 / 接入摘要
  - `scenario skills` 的可见入口关系
- 明确 plugin 不替代 Loom 的治理真相与 harness 真相
- 保留深层合同与宿主适配说明，但退居第二层
- 对齐根 README、skills 首层说明与 plugin 叙事

## Done When

1. 用户只看首层说明，就能理解 repo 内默认获得的是 Loom 的 `repo-local plugin`
2. plugin 首层能回答：
   - 安装后得到什么
   - 默认从哪里开始
   - 与 `scenario skills` 的关系是什么
3. plugin 不再被写成“宿主细节总览”或“协议文件目录”
4. 深层宿主 / adapter / contract 文档仍可达，但已退居第二层
5. `loom-init` 或等价默认进入方式在 plugin 叙事中保持清晰，不再混入旧 framing
```

### 2.3 `loom-cli-and-pilot-skill-wrappers`

#### 标题

`收敛 repo-local loom CLI 的定位、入口边界与 repo-local 操作面`

#### 类型

`active execution issue`

#### 建议正文

```md
Parent issue: #232

## Type

`active execution issue`

## Goal

把 `repo-local loom CLI` 的角色写清楚：它是 repo-local 的次级执行入口、自动化入口和调试入口，不是新的用户第一入口，也不是新的治理真相源。

## Responsibilities

- 明确 `repo-local loom CLI` 的定位：
  - repo-local automation
  - verify / debug / orchestration
  - 与 plugin / skills 等价但次级的执行面
- 明确 CLI 与 `repo-local plugin`、`scenario skills` 的边界
- 明确哪些动作优先通过 plugin / skills 理解，哪些动作保留在 CLI
- 对齐 README、skills、harness 与 release 叙事中的 CLI 角色

## Done When

1. `repo-local loom CLI` 的定位已明确为次级入口，而不是首层用户入口
2. 文档已明确 CLI 承接的主要场景：
   - automation
   - verification
   - debugging
   - host orchestration
3. 文档已明确 CLI 不替代：
   - governance truth
   - plugin 首层安装叙事
   - scenario skills 的用户执行入口
4. plugin / CLI / skills 三者关系已经稳定，不再互相越权
5. 下游读者不会再把 CLI 误解成“必须先学会的一套独立产品”
```

### 2.4 `remaining-scene-skills-and-boundary-docs`

#### 标题

`定义 scenario skills 与 single-skill standard-skill packages 的边界、装配关系与说明合同`

#### 类型

`active execution issue`

#### 建议正文

```md
Parent issue: #232

## Type

`active execution issue`

## Goal

把 Loom 的用户执行面稳定写成 `scenario skills`，并把单 skill 交付稳定写成 `single-skill standard-skill packages`，同时收清两者之间的边界、装配关系与最小说明合同。

## Responsibilities

- 明确 Loom 的用户执行入口集合以 `scenario skills` 为准
- 明确单 skill 交付的正式表述为 `single-skill standard-skill packages`
- 明确单 skill package 与 repo-local plugin 的关系
- 明确单 skill package 首层必须自解释什么：
  - 什么时候用
  - 解决什么问题
  - 与 Loom 其余入口是什么关系
- 明确单 skill package 不自动承诺整包 Loom 的默认能力
- 清理旧的“单个用户可见 skill 产品单元” framing

## Done When

1. `scenario skills` 已被稳定写成 Loom 的用户执行面
2. `single-skill standard-skill packages` 已成为单 skill 交付的正式表述
3. 单 skill package 的首层说明能独立回答：
   - 什么时候调用
   - 解决什么问题
   - 与 plugin / CLI / 其他 scenario skills 的关系
4. 文档已明确：
   - 单 skill package 不等于整包 Loom
   - 单 skill package 不自动承诺 root routing 或其他 repo-local 默认能力
5. 旧 framing 已退出首层叙事，不再出现“单个用户可见 skill 产品单元”这类表述
```

### 2.5 `installable-skills-validation-release-closeout`

#### 标题

`验证、release judgment 与 closeout：收口 v0.4.0 repo-local delivery tree`

#### 类型

`validation / closeout issue`

#### 建议正文

```md
Parent issue: #232

## Type

`validation / closeout issue`

## Goal

补齐 `v0.4.0` 这棵树的验证记录、release judgment、guardian 消费口径与 closeout basis，确保 parent closeout 可以直接消费，不再依赖会话补充。

## Responsibilities

- 验证四层交付面：
  - `repo-local plugin`
  - `repo-local loom CLI`
  - `scenario skills`
  - `single-skill standard-skill packages`
- 固化 `v0.4.0`、`major but still pre-1` 与 parent closeout basis
- 对齐 parent / child issue、PR 顺序、主干结果、guardian 门禁与 closeout comment
- 写清本轮收了什么、延期了什么、下一棵树从哪里接续

## Done When

1. 已有验证记录覆盖四层 repo-local 交付面
2. release goal 已进入版本控制，并明确对应 `v0.4.0`
3. 默认版本判断与实际改动一致，仍为 `major but still pre-1`
4. guardian 的消费口径与 parent closeout basis 已固定
5. parent closeout comment 已可直接说明：
   - 本轮交付对象
   - 延期对象
   - 下一树接续点
6. 不再需要靠会话解释为什么旧 framing 已被替换、为什么本轮是 `v0.4.0`
```

## 3. PR Slice 对应关系

- `PR-1: freeze + issue tree rewrite`
  - 对应：Parent issue + Child 1
- `PR-2: loom plugin install surface`
  - 对应：Child 2
- `PR-3: loom cli + pilot skills`
  - 对应：Child 3
- `PR-4: remaining skills + boundary + release + closeout`
  - 对应：Child 4 + Child 5
