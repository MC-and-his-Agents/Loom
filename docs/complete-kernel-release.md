# Loom v0.4.0 Release

本文是 Loom `v0.4.0` 的正式发布与升级说明。

发布日期：`2026-04-20`

变更分类：`major but still pre-1`

受影响交付面：

- `repo-local plugin`
- repo-local `loom CLI`
- `scenario skills`
- `single-skill standard-skill packages`
- `governance`
- `harness`
- `templates`
- `adoption`

下游是否需要动作：是。
至少需要重新读取稳定安装面、升级说明与 release note，并按本文确认自己消费的是完整 Loom install surface 还是单个 standard-skill package。若采用 `repo companion migration`，仍需维护 `.loom/companion/manifest.json` 与 `.loom/companion/repo-interface.json`。

对应 Loom issue：`#232`、`#236`、`#237`

## 1. 本次发布收敛的稳定交付面

`v0.4.0` 把 Loom 的 repo-local 交付形态正式固定为四层：

### 1.1 `repo-local plugin`

- 作为默认安装对象被 Agent 平台发现和安装
- 承接完整 Loom 入口面
- 对用户继续暴露 `loom-init` 与其余 scenario skills

### 1.2 repo-local `loom CLI`

- 作为次级执行面，统一承接 `loom ...` 的自动化、验证、调试与宿主编排语义
- 继续服务于 plugin 安装物与单 skill package
- 不升格成用户第一入口

### 1.3 `scenario skills`

- 继续作为用户执行面
- root entry：`loom-init`
- scenario skills：`loom-adopt`、`loom-resume`、`loom-pre-review`、`loom-review`、`loom-handoff`、`loom-retire`、`loom-merge-ready`
- 路由与升级工件仍以 `skills/registry.json`、`skills/upgrade-contract.json`、`skills/route-matrix.md` 为准

### 1.4 `single-skill standard-skill packages`

- 正式定义为单个标准 skill 的交付物
- 每个 package 只承接该 skill 的场景合同、最小 launcher / shim 与所需私有资源
- 不再沿用“单个用户可见 skill 产品单元”的旧 framing
- 不承诺整包 Loom 默认能力

## 2. 为什么这是 `major but still pre-1`

本次按 `major` 管理，原因是：

- Loom 的默认安装对象、次级执行面、用户执行面与单 skill 正式交付物边界都被重新收清
- 下游必须重新理解 plugin / CLI / scenario skills / single-skill packages 四层公开面
- 单 skill 包不再允许被写成“缩小版整包 Loom”

本次仍是 `pre-1`，原因是：

- Loom 仍未进入 `v1.x` 的长期稳定承诺阶段
- 全局发行渠道、宿主完整回归矩阵与更多宿主实现仍不属于稳定交付面
- 本次没有重写 JSON runtime contracts、shared runtime 脚本或 route priority / root identity 的 machine semantics

## 3. 下游升级路径

### 3.1 完整 Loom 消费方

1. 重新读取根 `README.md`、`skills/README.md`、`skills/distribution-and-adapter-contract.md`、`adoption/versioning-and-upgrades.md`
2. 刷新 repo-local `loom` plugin 的安装物、skill manifests、引用资源与升级协议
3. 确认默认仍从 `loom-init` 进入，且 7 个 scenario skills 可发现
4. 把用户执行面继续固定在 scenario skills，把 repo-local `loom CLI` 保持为次级入口

### 3.2 repo-local `loom CLI` 消费方

1. 在自动化、验证、调试与宿主编排中统一使用 `loom ...` 语义
2. 不把 CLI 写成新的事实真相源
3. 不把 CLI 公开面误写成 plugin 安装主路径

### 3.3 单 skill package 消费方

1. 先确认自己消费的是哪个 `single-skill standard-skill package`
2. 只按该 skill 的场景合同、最小 launcher / shim 与所需私有资源理解安装物
3. 不假设其余 scenario skills、`loom-init` 路由或整包 Loom 默认能力已经同时可用
4. 若需要完整 Loom 入口面，回到 repo-local `loom` plugin

### 3.4 兼容原则

- 新增公开层次不替代既有 root / scene contract
- 单命令入口与聚合入口并存
- gate 与 verify 复用同一 CLI，不维护第二套检查命令
- 单 skill package 的正式化不改变 scenario skill 的角色合同

详见：[adoption/execution-entry-compatibility.md](../adoption/execution-entry-compatibility.md)

## 4. 版本化公开面的对齐结果

本次 release 已把以下文档统一到同一条仓库真相：

- 根 `README.md`
- `skills/README.md`
- `skills/distribution-and-adapter-contract.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`
- `adoption/execution-entry-compatibility.md`
- `VERSION`

这些文档共同回答：

- 四层 repo-local 交付面是什么
- 哪些对象属于完整 Loom install surface
- 哪些对象只是单 skill 正式交付物
- 为什么本轮是 `v0.4.0` 的 `major but still pre-1`

## 5. 延续有效的验证与收口依据

本次 release 继续消费既有验证记录与 adoption 复验，而不是重写 machine contracts：

- 6 个场景 skill 的显式触发、隐式路由与下游消费验证
- 新项目完整内核复验：`loom-adoption-new-project`
- 既有仓库完整内核复验：`mail-listener` + `hotcp`
- 第一批执行化补充验证：
  - `adoption/validation-main-path-new-project.md`
  - `adoption/validation-existing-repo-execution-sync.md`
  - `adoption/validation-retrofit-143-tree.md`
- `repo companion` 机读读面与 requirement 消费验证：
  - `adoption/validation-repo-companion-interface.md`

本批的新增收口重点是 boundary / versioning / release truth 对齐，而不是重做 runtime validation。

## 6. 本次不进入发布面的内容

以下内容本次明确不进入 `v0.4.0` 的稳定发布面：

- 全局发行 Loom CLI
- npm、pipx、Homebrew 等分发渠道
- 宿主特定 marketplace 流程、路径、按钮或权限细节
- 把单个 standard-skill package 宣称为“默认完整 Loom”
- JSON runtime contracts、shared runtime 脚本或 route priority 的重写
