# Versioning And Upgrade Path

本文定义 Loom 组件的版本对象、升级入口与公开升级合同。

它的目标是避免下游仓库只能依赖手工复制或临场比较来获取 Loom 更新。

当前正式产品版本：`v0.5.0`

当前发布判断：`minor`

## 1. 版本对象

Loom 的版本对象是“可被下游直接消费的能力面”，而不是单个文件。

当前产品版本的正式落点固定为：

- 仓库根目录的 [`VERSION`](../VERSION)
- 发布说明 [`../docs/complete-kernel-release.md`](../docs/complete-kernel-release.md)

当前稳定版本边界包括：

- `governance` 合同
- `harness` 合同
- `templates` 合同
- 四层 repo-local 交付面：
  - `repo-local plugin`
  - repo-local `loom CLI`
  - `scenario skills`
  - `single-skill standard-skill packages`
- `adoption` 中面向下游的稳定采用 / 升级规则
- `repo companion migration` 稳定下游合同（含 `repo-interface.json`）

候选文档、宿主特定实现和未升为 `keep` 的条目，不自动进入稳定版本边界。

以下内部版本对象不得与产品版本混淆：

- `skills/registry.json` 的 `registry_version`
- `skills/*/contract.json` 的 `contract_version`
- `skills/upgrade-contract.json` 的 `schema_version` / `registry_version` / `current_contract_version`
- `tools/loom_init.py` 的 `TOOL_VERSION` / `CONTRACT_VERSION`
- bootstrap 示例产物中的 `tool_version` / `contract_version` / `schema_version`

这些字段只表达技能、合同、工具或产物格式的内部演进，不等于 Loom 的正式产品版本号。

## 2. `major but still pre-1` 的含义

Loom 当前仍处于 `pre-1` 阶段，因此不会把每次重大收敛都伪装成 `v1.0.0`。

`major but still pre-1` 在 Loom 里的含义是：

- 这是一次足以改变下游安装面、调用面、交付面或升级判断的重大收敛
- 下游必须显式重读安装、升级与 release truth
- 但 Loom 仍未进入 `v1.x` 的长期稳定承诺阶段
- 因此重大版本在 pre-1 阶段仍写作 `v0.x.0`，而不是 `v1.0.0`

判断 `major` 看的不是数字写法，而是下游是否必须重新理解公开交付面。

## 3. 版本规则

Loom 继续使用 `major` / `minor` / `patch` 的发布判断，但在 `pre-1` 阶段保留 `v0.x.0` 的正式版本形态。

- `major`
  - 破坏现有下游采用合同、默认安装面、用户执行面、必备工件、checkpoint 语义、关闭语义或入口合同
  - 或显著重构 repo-local 交付形态，要求下游重读 install / release / upgrade truth
- `minor`
  - 新增可选能力、稳定新入口、扩展不破坏兼容的合同
  - 或在既有交付形态内扩展不破坏兼容的标准能力
- `patch`
  - 澄清、去歧义、非行为性修订与证据补强

## 4. 下游升级入口

下游仓库的升级入口至少应包含：

- 当前使用的 Loom 版本
- 本次可升级到的目标版本
- 受影响交付面
- 是否要求下游显式动作
- 升级步骤
- 不兼容点与回退建议

下游升级不要求统一分发协议，但必须是显式可识别动作，而不是静默漂移。

## 5. 升级说明最小格式

每次 Loom 升级至少应公开以下字段：

- 版本号
- 变更分类：`major` / `minor` / `patch`
- 当前是否仍处于 `pre-1`
- 受影响交付面
- 下游是否必须动作
- 升级步骤
- 不兼容点
- 回退建议

`v0.4.0` 之后，每次正式产品发布都应至少更新：

- [`VERSION`](../VERSION)
- [`../docs/complete-kernel-release.md`](../docs/complete-kernel-release.md)

必要时再同步更新 README、`skills/README.md`、上游交付面说明与执行入口兼容说明。

若发布包含 `repo companion migration` 合同变更，还应同步更新：

- [`repo-companion-migration.md`](./repo-companion-migration.md)
- [`reference-companion-spec-syvert.md`](./reference-companion-spec-syvert.md)
- [`reference-companion-spec-webenvoy.md`](./reference-companion-spec-webenvoy.md)
- [`validation-repo-companion-interface.md`](./validation-repo-companion-interface.md)

## 6. 交付面与升级动作的对应关系

### 6.1 `governance`

以下变化通常构成 `major`：

- 关闭语义变化
- 事项入口或真相源语义变化
- 审查职责分层变化

### 6.2 `harness`

以下变化通常构成 `major`：

- checkpoint 语义变化
- 恢复主入口的必备要求变化
- 状态读取或执行现场合同变化

### 6.3 `templates`

以下变化通常构成 `minor` 或 `major`：

- 新增条件块通常为 `minor`
- 删除必填最小事实或改变正式套件最小要求，通常为 `major`

### 6.4 `repo-local plugin`

以下变化通常构成 `major`：

- 默认安装对象变化
- plugin 暴露的完整 Loom 入口面变化
- plugin 安装成功与单 skill 安装成功的边界变化

### 6.5 repo-local `loom CLI`

以下变化通常构成 `major`：

- CLI 的公开命令面、次级入口角色或宿主编排语义变化
- CLI 被提升成用户第一入口或新的事实真相源

以下变化通常构成 `minor`：

- 在不改变首层角色的前提下扩展兼容子命令或聚合 flow

### 6.6 `scenario skills`

以下变化通常构成 `major`：

- `bootstrap/root contract` 的最小职责变化
- `loom-init` 的 root entry 身份变化
- 隐式路由优先级或场景 skill 角色合同变化
- 用户执行面从 scenario skills 改写成其他对象

以下变化通常构成 `minor`：

- 新增稳定 scenario skill
- 新增不破坏兼容的聚合 flow，并被场景 skill 正式消费
- 收敛根 `README.md`、`skills/README.md`、`loom-init/SKILL.md` 等用户首层产品面，只要不改变 machine contract、route priority、scene role contract 或 runtime evidence

### 6.7 `single-skill standard-skill packages`

以下变化通常构成 `major`：

- 单 skill package 的正式边界变化
- 单 skill package 开始或停止承诺完整 Loom 默认能力
- package 的最小 launcher / shim / 私有 runtime 义务变化

以下变化通常构成 `minor`：

- 新增稳定的单 skill package 交付对象
- 在不改变边界的前提下扩展某个 package 的兼容说明

### 6.8 `adoption`

以下变化通常构成 `minor` 或 `patch`：

- 新增稳定 adoption 路径通常为 `minor`
- 新增稳定 `repo companion migration` 合同、但不破坏既有入口语义，通常为 `minor`
- 对已有路径做澄清或补证据通常为 `patch`

## 7. `v0.5.0` 的发布判断

`v0.5.0` 本次按 `minor` 管理，原因是：

- 用户首层产品路径保持不变，仍然只看到 `loom-pre-review -> loom-review -> loom-merge-ready`
- 这次新增的是既有交付形态内的稳定能力扩展：
  - 正式 review 内部执行链固定为 `flow review -> review run -> review record`
  - 默认 Codex-backed review adapter 被 Loom 正式承接
  - `merge-ready` / `checkpoint merge` 继续只消费单一 authored `review record`
- 本次没有改写四层 repo-local 交付形态、root entry 身份、route priority、checkpoint 语义或关闭语义
- 本次没有要求下游重新理解 install surface、scenario skill 边界或单 skill package 边界

本次仍不进入 `v1.0.0` 的原因是：

- Loom 仍处于 pre-1 阶段
- multi-engine、全局发行渠道与更完整的宿主回归矩阵仍未进入稳定发布面
- 本次新增的是默认 review 主路径，而不是 `v1.x` 级别的长期稳定承诺重写

## 8. 与 `skills` 分发合同的关系

`skills` 的安装、发现、升级与 adapter 合同，由 [../skills/distribution-and-adapter-contract.md](../skills/distribution-and-adapter-contract.md) 承接。

当前仓库中：

- `skills/registry.json`
  - 承接 root entry、场景 entry、角色与合同版本的机读声明
- `skills/install-layout.json`
  - 承接 installed-skills 的最小 runtime / resources 布局，声明 skill-local `scripts/` 与 `shared/scripts/assets/references` 的必备面
- `skills/upgrade-contract.json`
  - 承接最小机读升级协议，声明宿主必须重新读取 `registry/manifest/executable/referenced_resources/layout_manifest`

它们不替代本文的版本对象定义，只负责把显式升级与版本可见性落成可读取工件。

同样需要保持的边界是：

- 用户首层说明可以收敛或重写
- 但只要 `registry/install-layout/upgrade-contract` 的 machine 语义不变，它们就仍然只是宿主 / adapter 公开面的版本承载物
- 单 skill package 的说明合同可以补齐，但不应把 machine semantics 变化和文案澄清混写

执行入口的兼容边界与操作流验证由 [execution-entry-compatibility.md](./execution-entry-compatibility.md) 承接。
