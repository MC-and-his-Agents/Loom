# SKILLS Surface Delivery Judgment

本文基于 [adoption/skills-repo-design-checklist.md](/Users/mc/dev/Loom/adoption/skills-repo-design-checklist.md) 的 benchmark 调研，冻结 Loom 下一轮 `SKILLS` 产品面收敛工作的交付判断。

它回答五件事：

1. 这轮工作的交付目标是什么
2. 这轮工作的 issue tree 应如何拆
3. PR 应如何分批，哪些不得混线
4. release goal 与默认版本判断是什么
5. 什么条件满足后，这轮工作才算 closeout

它不回答：

- Loom 全局长期路线
- `skills` 机读合同是否最终要重写成另一套结构
- 宿主 adapter 的具体实现细节

长期阶段路线仍以 [roadmap.md](/Users/mc/dev/Loom/docs/roadmap.md) 为准。
版本语义仍以 [adoption/versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md) 为准。
issue 类型与 parent / child closeout 语义仍以 [governance/issue-model.md](/Users/mc/dev/Loom/governance/issue-model.md) 为准。
可直接提交的 issue tree 草案见 [skills-surface-issue-tree-draft.md](/Users/mc/dev/Loom/docs/skills-surface-issue-tree-draft.md)。

## 1. 一句话判断

Loom 当前 `SKILLS` 层的主要问题不是能力缺失，而是产品面、宿主合同面和内部 runtime 认知面混层。

因此下一轮工作的正确目标不是：

- 重写整个 `skills` runtime
- 立刻推翻 `registry/install-layout/upgrade-contract`

而是：

- 先把 Loom 从“协议暴露型 `skills` 仓库”收敛到“用户主路径清晰的 `SKILLS` bundle”
- 同时显式冻结哪些 machine contract 仍保留、但不再占据第一层产品面

## 2. 本轮交付目标

本轮工作只收以下目标：

1. 用户主路径收敛
   - 顶层 README 不再以 adapter/operator 视角作为第一叙事
   - 用户可以先理解“怎么安装、怎么开始用 Loom skills”
2. `skills` 产品面收敛
   - `skills/README.md` 重新成为入口层产品说明，而不是协议总览
3. root skill 首屏收敛
   - `loom-init` 首屏只承担触发、判断和导向摘要
   - 深知识继续下沉到 references
4. runtime vocabulary 降层
   - `repo-local-demo`、`installed-runtime`、`upgrade-rehearsal` 退出首层用户心智
   - 保留在调试、宿主适配或深层文档中
5. 公开面边界重述
   - 明确区分“用户公开面”和“宿主公开面”
   - 但本轮不强行重写 machine contract 本身

## 3. 本轮非目标

以下内容明确不进入本轮：

1. 重写 `skills/registry.json`
2. 重写 `skills/install-layout.json`
3. 重写 `skills/upgrade-contract.json`
4. 修改隐式路由优先级、root entry 身份或场景 skill 角色合同
5. 重写 runtime detection 代码语义
6. 重新定义 installed runtime 的 machine evidence

原因很简单：

- 一旦本轮同时碰这些内容，版本语义会迅速抬升到 `major`
- benchmark 已经证明 Loom 当前最紧迫的问题在产品面暴露，而不是 machine contract 先天不存在

换句话说：

- 本轮先收“用户看见什么”
- 下一轮再决定“机器如何读这些合同”

## 4. issue tree 判断

这轮工作应建立父 issue。

原因：

- 它同时涉及 `README` / `skills` / `root skill` / adoption / release / closeout
- 若不提前固定拆分方式，很容易把文档收敛、入口行为、公开面边界和 release 判断混成一条 PR

### 4.1 Parent issue 语义

parent issue 负责：

- 总目标
  - Loom `SKILLS` 产品面收敛
- 默认 PR slices
- release goal
- closeout basis

parent issue 不直接承担实现主体。

### 4.2 Child issue 默认拆分

默认拆为 5 个 child issue，不混线：

1. `skills-benchmark-and-target-freeze`
   - 类型：`spec / planning issue`
   - 负责 benchmark、目标边界、非目标和默认版本判断
   - 可直接消费当前 [adoption/skills-repo-design-checklist.md](/Users/mc/dev/Loom/adoption/skills-repo-design-checklist.md) 与本文

2. `top-level-install-and-readme-surface`
   - 类型：`active execution issue`
   - 负责顶层 README 的安装叙事、快速开始和用户主路径收敛

3. `skills-readme-and-root-entry-surface`
   - 类型：`active execution issue`
   - 负责 `skills/README.md` 与 `skills/loom-init/SKILL.md` 首屏收敛

4. `public-vs-host-surface-boundary`
   - 类型：`active execution issue`
   - 负责 `skills/distribution-and-adapter-contract.md`、`adoption/upstream-delivery-surface.md`、`adoption/versioning-and-upgrades.md` 等边界重述
   - 目标是收紧公开面叙事，而不是修改 machine contract

5. `skills-surface-validation-release-closeout`
   - 类型：`validation / closeout issue`
   - 负责验证记录、release judgment、closeout basis 和对外收口说明

### 4.3 明确延期的后续树

以下内容应明确延期到下一棵树，不混入本轮 parent：

1. `machine-contract-narrowing`
   - 若要改 `registry/install-layout/upgrade-contract` 的公开职责
2. `runtime-evidence-hardening`
   - 若要收紧 installed/runtime 识别条件
3. `entry-behavior-regression-suite`
   - 若要把 trigger / route regression 从候选提升为默认门禁

这些都可能牵动 `major` 级版本判断，不应和本轮产品面收敛混线。

## 5. 默认 PR Slices

本轮默认固定为 4 批 PR：

### PR-1 `benchmark + delivery judgment`

职责：

- benchmark 文档
- 本文
- 必要的 adoption / docs 索引

不得混入：

- README 重写
- `loom-init` 重写
- release note

### PR-2 `top-level user surface`

职责：

- 根 README 的安装、快速开始、用户主路径收敛

不得混入：

- `skills/README.md`
- `loom-init/SKILL.md`
- `distribution-and-adapter-contract.md`

### PR-3 `skills surface`

职责：

- `skills/README.md`
- `skills/loom-init/SKILL.md`
- 必要的 references 摘要调整

不得混入：

- machine contract JSON
- runtime detection 代码
- release note

### PR-4 `boundary + release + closeout`

职责：

- `skills/distribution-and-adapter-contract.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`
- release note / closeout 文档

不得混入：

- `registry/install-layout/upgrade-contract` 语义重写
- runtime script 行为变化

## 6. release goal 判断

### 6.1 本轮 release goal

本轮 release goal 应明确写成：

`让 Loom 的 SKILLS 层从协议暴露型入口说明，收敛为用户主路径清晰、宿主边界清楚、但 machine contract 暂不重写的产品面。`

这个目标的重点不是新增技能能力，而是：

- 修正用户如何理解 Loom skills
- 修正仓库如何对外描述 `skills`
- 修正哪些内容属于首层公开面

### 6.2 默认版本判断

本轮默认按 `minor` 规划。

理由：

- 会明显改变用户可见的 `skills` 产品叙事
- 会调整 root skill 与入口层说明的对外表达
- 但若严格遵守本文件边界，不会破坏既有 machine contract、route priority 或 executable semantics

### 6.3 何时升为 `major`

若本轮出现以下任一变化，版本判断必须升级为 `major`：

1. `bootstrap/root contract` 最小职责发生变化
2. 隐式路由优先级变化
3. 场景 skill 角色合同变化
4. `registry/install-layout/upgrade-contract` 的对外 machine 语义变化
5. installed/runtime/upgrade rehearsal 的 machine evidence 发生变化

这也是为什么这些内容被明确移出本轮。

### 6.4 何时可降为 `patch`

仅当本轮最终只剩：

- benchmark 文档
- delivery judgment 文档
- 非行为性说明补强

且没有实质改动 README / `skills/README` / `loom-init` 首屏时，才可降为 `patch`。

但按当前目标，本轮默认不按 `patch` 管理。

## 7. 最小验证面

本轮 closeout 前至少要验证：

1. 新用户只读根 README，就能理解：
   - 如何安装 / 接入 Loom skills
   - `loom-init` 是默认入口
   - 下一步如何开始
2. 只读 `skills/README.md`，不会再先进入 adapter/runtime 词汇
3. 只读 `loom-init/SKILL.md` 首屏，能先理解：
   - 什么时候触发
   - 先判断什么
   - 会被导向哪些场景
4. `distribution-and-adapter-contract.md` 仍保留宿主合同边界
   - 但不再被默认当成首屏用户说明
5. release / upgrade / delivery surface 文档对这轮变更的版本语义一致

这轮验证的重点不是“脚本能不能跑”，而是：

- 用户主路径是否收清
- 产品面和宿主面是否分层
- release judgment 是否与实际改动一致

## 8. Done When

只有当以下条件同时满足时，这棵树才算完成：

1. benchmark 与交付判断已进入版本控制
2. 顶层 README 已完成用户主路径收敛
3. `skills/README.md` 已完成入口层产品面收敛
4. `loom-init` 首屏已完成收敛，深知识已退回 references
5. `distribution-and-adapter-contract.md`、`upstream-delivery-surface.md`、`versioning-and-upgrades.md` 已对齐新的边界表述
6. release goal、默认版本判断和 closeout basis 已进入版本控制
7. parent issue 不再依赖会话解释“为什么这轮不改 machine contract”

如果只完成 benchmark 和交付判断，而未完成 README / root skill / boundary 收敛：

- parent issue 不能 closeout
- 只能停留在 planning freeze 已完成、execution 未完成

## 9. Closeout basis

本树 closeout 时，parent issue 至少要消费以下真相：

- benchmark 文档
- 本文
- 根 README 收敛 PR
- `skills/README.md` / `loom-init` 收敛 PR
- boundary / release / closeout PR

并且 parent closeout comment 至少要写清：

1. 这轮明确收的是什么
2. 哪些 machine contract 问题被有意延期
3. 为什么当前版本判断仍是 `minor`
4. 下一棵树应从哪里接续

## 10. 下一树的接续点

本轮完成后，下一棵树默认从这里继续：

1. 判断是否要正式收窄 `registry/install-layout/upgrade-contract` 的公开职责
2. 判断是否要把 runtime detection 从路径形状推断改为更强 evidence
3. 判断入口层行为回归测试是否进入默认 core

在这之前，不应让本轮树无限膨胀成 `skills` 全面重构树。
