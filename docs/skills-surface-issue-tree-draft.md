# SKILLS Surface Issue Tree Draft

本文把 [skills-surface-delivery-judgment.md](/Users/mc/dev/Loom/docs/skills-surface-delivery-judgment.md) 直接翻成一版可提交的 GitHub issue tree 草案。

目标不是继续分析，而是提供：

- 1 个 parent issue 草案
- 5 个 child issue 草案
- 4 个 PR slice 对应关系

本稿默认用于 Loom 下一轮 `SKILLS` 产品面收敛工作。

## 1. Parent Issue Draft

### 标题

`SKILLS surface convergence: from protocol-exposed entry layer to user-facing bundle`

### 类型

`spec / planning issue`

### 建议正文

```md
## Goal

收敛 Loom 当前 `SKILLS` 层的产品面，使其从“协议暴露型入口说明”推进到“用户主路径清晰、宿主边界清楚、但 machine contract 暂不重写的 `SKILLS` bundle”。

## Why

当前 `skills/` 的主要问题不是能力缺失，而是三层混在了一起：

- 用户产品面
- 宿主合同面
- 内部 runtime 认知面

结果是：

- 用户先看到安装协议，而不是使用主路径
- `skills/README.md` 更像协议总览，而不是入口层产品说明
- `loom-init` 首屏合同密度高于可用性
- `repo-local-demo` / `installed-runtime` / `upgrade-rehearsal` 等词汇泄漏到首层心智

## Scope

本树只收以下目标：

1. 顶层 README 的用户主路径收敛
2. `skills/README.md` 的入口层产品面收敛
3. `skills/loom-init/SKILL.md` 首屏收敛
4. `skills` 用户公开面与宿主公开面的边界重述
5. release goal、版本判断与 closeout basis 收口

## Non-goals

以下内容不进入本树：

- 重写 `skills/registry.json`
- 重写 `skills/install-layout.json`
- 重写 `skills/upgrade-contract.json`
- 修改 root entry 身份、隐式路由优先级或场景 skill 角色合同
- 重写 runtime detection 代码语义
- 重新定义 installed runtime 的 machine evidence

这些工作若进入本树，版本语义将直接升级到 `major`，应另起后续树处理。

## Child Issues

1. `skills-benchmark-and-target-freeze`
2. `top-level-install-and-readme-surface`
3. `skills-readme-and-root-entry-surface`
4. `public-vs-host-surface-boundary`
5. `skills-surface-validation-release-closeout`

## Default PR Slices

1. `benchmark + delivery judgment`
2. `top-level user surface`
3. `skills surface`
4. `boundary + release + closeout`

## Release Goal

让 Loom 的 `SKILLS` 层从协议暴露型入口说明，收敛为用户主路径清晰、宿主边界清楚、但 machine contract 暂不重写的产品面。

默认版本判断：`minor`

若出现以下任一变化，必须升级为 `major`：

- `bootstrap/root contract` 最小职责变化
- 隐式路由优先级变化
- 场景 skill 角色合同变化
- `registry/install-layout/upgrade-contract` 的 machine 语义变化
- installed/runtime evidence 变化

## Done When

只有当以下条件同时满足时，本 issue 才可 closeout：

1. benchmark 与交付判断已进入版本控制
2. 根 README 已完成用户主路径收敛
3. `skills/README.md` 已完成入口层产品面收敛
4. `loom-init` 首屏已完成收敛，深知识已退回 references
5. `distribution-and-adapter-contract.md`、`upstream-delivery-surface.md`、`versioning-and-upgrades.md` 已对齐新的边界表述
6. release goal、默认版本判断和 closeout basis 已进入版本控制
7. parent issue 不再依赖会话解释“为什么这轮不改 machine contract”

## Closeout Basis

parent closeout 时只消费子 issue 已成立真相，不替代子 issue 的独立完成判断。

closeout comment 至少应写清：

1. 这轮明确收了什么
2. 哪些 machine contract 问题被有意延期
3. 为什么当前版本判断仍是 `minor`
4. 下一棵树应从哪里接续
```

## 2. Child Issue Drafts

### 2.1 `skills-benchmark-and-target-freeze`

#### 标题

`Benchmark and freeze the target boundary for SKILLS surface convergence`

#### 类型

`spec / planning issue`

#### 建议正文

```md
## Goal

把外部 benchmark 与 Loom 当前 `SKILLS` 问题收成版本控制中的冻结判断，作为后续 README、root entry、boundary 和 release 工作的统一输入。

## Scope

- 固定 benchmark 样本与调研边界
- 固定本轮收什么、不收什么
- 固定默认版本判断
- 固定 issue tree 与 PR slices

## Inputs

- `adoption/skills-repo-design-checklist.md`
- `docs/skills-surface-delivery-judgment.md`

## Deliverables

- benchmark 文档
- delivery judgment 文档
- 必要的索引补链

## Done When

1. benchmark 文档已明确：
   - 样本
   - 方法
   - 结论
   - Loom gap analysis
2. delivery judgment 已明确：
   - scope
   - non-goals
   - issue tree
   - PR slices
   - release goal
   - version judgment
3. 后续执行 issue 不再需要重新讨论“本轮为什么不改 machine contract”
```

### 2.2 `top-level-install-and-readme-surface`

#### 标题

`Converge top-level install story and user-facing README surface`

#### 类型

`active execution issue`

#### 建议正文

```md
## Goal

把根 README 从 adapter/operator-first 的安装叙事，收敛为用户可直接消费的 Loom skills 主路径说明。

## Scope

- 重写安装与快速开始主叙事
- 先讲如何接入和开始使用 Loom skills
- 保留深层文档入口，但不再让协议工件占据首屏

## Must Preserve

- 不改 machine contract
- 不改 root entry 身份
- 不改 executable semantics

## Out of Scope

- `skills/README.md`
- `skills/loom-init/SKILL.md`
- `skills/distribution-and-adapter-contract.md`

## Done When

1. 新用户只读根 README，就能理解：
   - 如何安装 / 接入 Loom skills
   - `loom-init` 是默认入口
   - 下一步如何开始
2. README 首屏不再要求用户先理解：
   - `registry.json`
   - `install-layout.json`
   - `upgrade-contract.json`
   - runtime scene vocabulary
3. 深层协议文档仍可从 README 进入，但已退居第二层
```

### 2.3 `skills-readme-and-root-entry-surface`

#### 标题

`Converge skills README and loom-init root entry surface`

#### 类型

`active execution issue`

#### 建议正文

```md
## Goal

把 `skills/README.md` 与 `skills/loom-init/SKILL.md` 收成真正的入口层产品说明，而不是协议总览或作者合同。

## Scope

- 重写 `skills/README.md`
- 收缩 `loom-init` 首屏
- 把深知识继续压回 references

## Must Preserve

- root entry 仍为 `loom-init`
- 场景 skill 切分不变
- route semantics 不变

## Out of Scope

- `registry/install-layout/upgrade-contract` JSON
- runtime detection 代码
- release note

## Done When

1. 只读 `skills/README.md`，不会再先进入 adapter/runtime 词汇
2. 只读 `loom-init/SKILL.md` 首屏，能先理解：
   - 什么时候触发
   - 先判断什么
   - 会被导向哪些场景
3. `repo-local-demo` / `installed-runtime` / `upgrade-rehearsal` 不再作为首屏主叙事
4. 深知识已有清晰 references 落点，不需要再挤回首屏
```

### 2.4 `public-vs-host-surface-boundary`

#### 标题

`Restate public-vs-host boundary for the skills surface`

#### 类型

`active execution issue`

#### 建议正文

```md
## Goal

重新表述 Loom `SKILLS` 的用户公开面与宿主公开面边界，明确哪些内容属于第一层产品面，哪些内容只给宿主/adapter 消费。

## Scope

- `skills/distribution-and-adapter-contract.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`

## Must Preserve

- adapter 边界原则仍成立
- machine contract 仍保留
- 不修改其实际 JSON 语义

## Out of Scope

- runtime script 代码
- registry/install-layout/upgrade-contract 文件内容
- 路由或 executable 语义

## Done When

1. 文档已经明确区分：
   - 用户公开面
   - 宿主公开面
2. `distribution-and-adapter-contract.md` 不再被默认当成首屏用户说明
3. `upstream-delivery-surface.md` 与 `versioning-and-upgrades.md` 已对齐本轮 `minor` 判断
4. 后续若要改 machine contract，对外已经有清晰的下一树入口
```

### 2.5 `skills-surface-validation-release-closeout`

#### 标题

`Validate, release-judge, and close out the skills surface convergence tree`

#### 类型

`validation / closeout issue`

#### 建议正文

```md
## Goal

为本轮 `SKILLS` 产品面收敛补齐验证记录、release judgment、closeout basis 与对外收口说明。

## Scope

- 验证记录
- release goal 对账
- 版本判断对账
- closeout basis

## Inputs

- parent issue
- README surface PR
- skills surface PR
- boundary PR

## Done When

1. 本轮最小验证面已对齐：
   - 根 README 用户主路径
   - `skills/README.md` 首屏
   - `loom-init` 首屏
   - boundary 文档
   - release/version 文档
2. release goal 已进入版本控制
3. 默认版本判断与实际改动一致
4. parent closeout comment 已明确：
   - 本轮收口对象
   - 延期对象
   - `minor` 判断依据
   - 下一树接续点
```

## 3. PR Slice Mapping

### PR-1 `benchmark + delivery judgment`

对应 issue：

- `skills-benchmark-and-target-freeze`

建议内容：

- benchmark 文档
- delivery judgment 文档
- adoption / docs / README 索引补链

### PR-2 `top-level user surface`

对应 issue：

- `top-level-install-and-readme-surface`

建议内容：

- 根 README 的安装与快速开始收敛

### PR-3 `skills surface`

对应 issue：

- `skills-readme-and-root-entry-surface`

建议内容：

- `skills/README.md`
- `skills/loom-init/SKILL.md`
- 必要的 references 摘要调整

### PR-4 `boundary + release + closeout`

对应 issue：

- `public-vs-host-surface-boundary`
- `skills-surface-validation-release-closeout`

建议内容：

- `skills/distribution-and-adapter-contract.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`
- release note / closeout 文档

## 4. 使用说明

推荐提交顺序：

1. 先开 parent issue
2. 再开 5 个 child issue
3. PR 严格按 4 批推进
4. parent closeout 只消费 child issue 已成立真相

推荐不要在 issue tree 里提前引入的条目：

- `machine-contract-narrowing`
- `runtime-evidence-hardening`
- `entry-behavior-regression-suite`

这些应保留为下一树，而不是在本轮执行期膨胀进来。
