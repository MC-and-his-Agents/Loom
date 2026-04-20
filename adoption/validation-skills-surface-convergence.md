# Validation: SKILLS Surface Convergence Tree

## 1. 样本标识

- 验证对象：Loom 仓库当前 `SKILLS surface convergence` 树
- 目标仓库：`/Users/mc/dev/Loom`
- parent issue：`#222`
- child issues：
  - `#223`
  - `#224`
  - `#225`
  - `#226`
  - `#227`
- 对应 PR slices：
  - `#223` -> benchmark + delivery judgment
  - `#224` -> top-level user surface
  - `#225` -> skills surface
  - `#226/#227` -> boundary + release + closeout
- 验证日期：`2026-04-20`

## 2. 本轮固定边界

本轮只验证 `SKILLS` 产品面收敛是否成立，不验证以下后续树内容：

- 不重写 `skills/registry.json`
- 不重写 `skills/install-layout.json`
- 不重写 `skills/upgrade-contract.json`
- 不修改 `loom-init` 的 root entry 身份
- 不修改隐式路由优先级
- 不修改场景 skill 角色合同
- 不重写 runtime detection 代码语义
- 不重新定义 installed/runtime evidence

因此，本记录只承接四件事：

1. 用户首层产品面是否已收清
2. `skills` 用户公开面与宿主公开面是否已分层
3. 默认版本判断是否仍然是 `minor`
4. parent closeout 应消费哪些已成立真相

## 3. 用户首层产品面验证

### 3.1 根 README

当前根 `README.md` 已先回答：

- 如何把 Loom skills 安装进 Agent 平台
- `loom-init` 是默认入口
- 安装完成后应先由 `loom-init` 判断当前场景，再继续执行

当前首屏已不再把以下内容当作安装主路径：

- `skills/registry.json`
- `skills/install-layout.json`
- `skills/upgrade-contract.json`
- `repo-local-demo` / `installed-runtime` / `upgrade-rehearsal`

这些内容已经退回到 [../skills/distribution-and-adapter-contract.md](../skills/distribution-and-adapter-contract.md) 等深层文档。

### 3.2 `skills/README.md`

当前 `skills/README.md` 已先回答：

- `skills/` 是 Loom 的入口层
- 默认从 `loom-init` 进入
- 7 个场景 skills 各自何时使用
- 显式进入与 `loom-init` 路由进入的关系

机读分发工件与 shared runtime/resources 已退到宿主 / adapter 说明，不再占据首屏。

### 3.3 `skills/loom-init/SKILL.md`

当前 `loom-init` 首屏已先回答：

- 什么时候先进入 `loom-init`
- 它先判断什么
- 显式 skill 优先
- 未显式指定时按任务信号路由
- 信号不足时停在 root entry，而不是猜测

读取顺序、问诊、装配判断与输出细则仍保留，但已退到首屏之后。

## 4. 边界与版本判断验证

### 4.1 用户公开面 vs 宿主公开面

当前仓库已明确分层：

- 用户首层公开面
  - 根 `README.md`
  - `skills/README.md`
  - `skills/loom-init/SKILL.md`
- 宿主 / adapter 公开面
  - `skills/distribution-and-adapter-contract.md`
  - `skills/registry.json`
  - `skills/install-layout.json`
  - `skills/upgrade-contract.json`
  - `skills/shared/scripts/assets/references`

这意味着：

- 用户先消费“怎么开始用 Loom skills”
- 宿主再消费“怎么发现、安装、升级、识别运行态并暴露失败”

### 4.2 `#226/#227` 的默认版本判断仍为 `minor`

本轮默认版本判断仍是 `minor`，原因是：

- 改动集中在用户可见的产品面、边界表述、验证记录与 closeout 说明
- `bootstrap/root contract` 最小职责未变
- 隐式路由优先级未变
- 场景 skill 角色合同未变
- `registry/install-layout/upgrade-contract` 的 machine 语义未变
- installed/runtime evidence 未变

若未来改动进入上述任一机器语义面，应升级为新的 `major` 树，而不是继续挤进本轮。

## 5. 最小门禁与验证结果

本轮执行 PR 在本地都按同一条门禁验证：

- `make loom-check`

其中，`#225/#226/#227` 的本地 `loom-check` 在历史 closeout 样本上出现过环境性波动：

- `#225`
  - 历史 closeout 样本的 `installed closeout sync` 曾短暂失败
  - 同一条 `closeout sync` 命令随后独立复验为 `pass`
  - 完整 `make loom-check` 重跑恢复为 `pass`
- `#226/#227`
  - 历史 closeout 样本的 `installed closeout check/sync` 失败原因被明确定位为 GitHub GraphQL API rate limit
  - 失败信息为：
    - `API rate limit already exceeded for user ID 9820018`
    - `project: unknown owner type`

因此，本记录将这组失败归类为宿主控制面 / GitHub API 环境限制，而不是 `SKILLS` 文档回归。本轮正式门禁仍以 PR CI 为准。

## 6. Parent Closeout Basis

`#222` closeout 时，至少应消费以下已成立真相：

- `#223`
  - benchmark 文档已进入版本控制
  - 交付判断、非目标、PR slices、release goal 与默认版本判断已冻结
- `#224`
  - 根 README 已完成用户主路径收敛
- `#225`
  - `skills/README.md` 与 `loom-init` 首屏已完成入口层产品面收敛
- `#226/#227`
  - 用户公开面 / 宿主公开面边界已重述
  - 默认版本判断仍为 `minor`
  - 本验证记录已进入版本控制

parent closeout comment 至少要写清：

1. 本轮明确收了什么
2. 哪些 machine contract 问题被有意延期
3. 为什么当前版本判断仍是 `minor`
4. 下一棵树应从哪里接续

对 `#226` 而言，closeout 依据是边界文档已把用户公开面与宿主公开面分层，并保留既有 machine semantics。

对 `#227` 而言，closeout 依据是本记录已经把验证结果、`minor` 判断依据、延期项与 parent closeout basis 收成版本控制真相。

## 7. 结论

`#222` 这棵树当前已经把 Loom `SKILLS` 层从“协议暴露型入口说明”推进到“用户主路径清晰、宿主边界清楚、但 machine contract 暂不重写”的状态。

因此，本记录确认：

- `#223/#224/#225/#226/#227` 的目标拆分是有效的
- 本轮不需要再靠会话解释“为什么这轮不改 machine contract”
- 下一棵树应改收 machine contract narrowing、runtime evidence hardening 或 entry behavior regression 是否进入默认 core
