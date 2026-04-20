# Versioning And Upgrade Path

本文定义 Loom 组件的版本对象、升级入口与公开升级合同。

它的目标是避免下游仓库只能依赖手工复制或临场比较来获取 Loom 更新。

当前正式产品版本：`v0.2.0`。

## 1. 版本对象

Loom 的版本对象是“可被下游直接消费的能力面”，而不是单个文件。

当前产品版本的正式落点固定为：

- 仓库根目录的 [`VERSION`](../VERSION)
- 发布说明 [`../docs/complete-kernel-release.md`](../docs/complete-kernel-release.md)

当前稳定版本边界包括：

- `governance` 合同
- `harness` 合同
- `templates` 合同
- `skills` 入口合同
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

## 2. 版本规则

Loom 采用语义版本：

- `major`
  - 破坏现有下游采用合同、必备工件、checkpoint 语义、关闭语义或入口合同
- `minor`
  - 新增可选能力、稳定新入口、扩展不破坏兼容的合同
- `patch`
  - 澄清、去歧义、非行为性修订与证据补强

## 3. 下游升级入口

下游仓库的升级入口至少应包含：

- 当前使用的 Loom 版本
- 本次可升级到的目标版本
- 受影响能力面
- 是否要求下游显式动作
- 升级步骤
- 不兼容点与回退建议

下游升级不要求统一分发协议，但必须是显式可识别动作，而不是静默漂移。

## 4. 升级说明最小格式

每次 Loom 升级至少应公开以下字段：

- 版本号
- 变更分类：`major` / `minor` / `patch`
- 受影响能力面
- 下游是否必须动作
- 升级步骤
- 不兼容点
- 回退建议

`v0.2.0` 之后，每次正式产品发布都应至少更新：

- [`VERSION`](../VERSION)
- [`../docs/complete-kernel-release.md`](../docs/complete-kernel-release.md)

必要时再同步更新 README、adoption 索引与上游交付面说明。

若发布包含 `repo companion migration` 合同变更，还应同步更新：

- [`repo-companion-migration.md`](./repo-companion-migration.md)
- [`reference-companion-spec-syvert.md`](./reference-companion-spec-syvert.md)
- [`reference-companion-spec-webenvoy.md`](./reference-companion-spec-webenvoy.md)
- [`validation-repo-companion-interface.md`](./validation-repo-companion-interface.md)

## 5. 能力面与升级动作的对应关系

### 5.1 `governance`

以下变化通常构成 `major`：

- 关闭语义变化
- 事项入口或真相源语义变化
- 审查职责分层变化

### 5.2 `harness`

以下变化通常构成 `major`：

- checkpoint 语义变化
- 恢复主入口的必备要求变化
- 状态读取或执行现场合同变化

### 5.3 `templates`

以下变化通常构成 `minor` 或 `major`：

- 新增条件块通常为 `minor`
- 删除必填最小事实或改变正式套件最小要求，通常为 `major`

### 5.4 `skills`

以下变化通常构成 `major`：

- `bootstrap/root contract` 的最小职责变化
- 安装、发现、升级、版本识别或 adapter 失败可见性合同变化
- `root_entry`、多 entry registry、隐式路由优先级或场景 skill 角色合同变化

以下变化通常构成 `minor`：

- 新增稳定场景 skill
- 新增不破坏兼容的聚合 flow，并被场景 skill 正式消费
- `skills/registry.json` 增加可发现 entry，但不改变既有 entry 的最小职责

### 5.5 `adoption`

以下变化通常构成 `minor` 或 `patch`：

- 新增稳定 adoption 路径通常为 `minor`
- 新增稳定 `repo companion migration` 合同、但不破坏既有入口语义，通常为 `minor`
- 对已有路径做澄清或补证据通常为 `patch`
- 像 `#169` 这样只补验证索引、交付面引用与 closeout 依据回写，而不改 adoption 合同语义，属于 `patch`
- 像 `#180` 这样只补 Loom 自身 retrofit 证据、但不改变关闭语义或默认 adoption 路径，也属于 `patch`

## 6. 示例

### `major` 示例

- 将 `checkpoint-lite` 从“允许的轻量过渡形态”改为“所有既有仓库都禁止使用”
- 这会改变下游恢复路径与首批工件要求，因此属于 `major`

### `minor` 示例

- 新增一个稳定的宿主无关入口合同说明，但不改变现有下游必须遵守的接口
- 这属于 `minor`

### `patch` 示例

- 把“小型既有仓库必须已有 CI / 基础测试”修正为“已有 CI / 基础测试，或等价质量基线”
- 这属于对既有规则的去歧义与证据补强，因此属于 `patch`
- 把 `#168/#170/#180` 的验证记录、发布面引用和父 issue 关闭依据统一回写到 adoption / release 文档
- 这属于验证索引与 closeout 证据补强，不构成新的能力面，因此属于 `patch`

## 7. 与 `skills` 分发合同的关系

`skills` 的安装、发现、升级与 adapter 合同，由 [../skills/distribution-and-adapter-contract.md](../skills/distribution-and-adapter-contract.md) 承接。

当前仓库中：

- `skills/registry.json`
  - 承接 root entry、场景 entry、角色与合同版本的机读声明
- `skills/install-layout.json`
  - 承接 installed-skills 的最小 runtime/resources 布局，声明 skill-local `scripts/` 与 `shared/scripts/assets/references` 的必备面
- `skills/upgrade-contract.json`
  - 承接最小机读升级协议，声明宿主必须重新读取 `registry/manifest/executable/referenced_resources/layout_manifest`

它们不替代本文的版本对象定义，只负责把显式升级与版本可见性落成可读取工件。

`#206` 当前引入的 installed-skills 布局重构，会改变 `skills` 的安装合同与 executable/resource 解析方式。下一次 Loom 正式产品发布若带上这组变更，应按 `major` 处理；在正式发版前，应继续以 issue / PR / install-layout 机读工件维持仓库真相一致。

## 8. 场景 SKILLS 第一波的升级语义

第一波稳定场景 skills 为：

- `loom-adopt`
- `loom-resume`
- `loom-pre-review`
- `loom-handoff`
- `loom-retire`
- `loom-merge-ready`

这一波属于 `minor` 升级，原因是：

- `loom-init` 仍保留唯一 root entry 身份
- 既有 `bootstrap/verify/fact-chain` 语义未被破坏
- 新增的是显式场景入口、root 隐式路由与聚合 flow，而不是替换旧入口

下游升级时至少应确认：

- 宿主能重新发现 7 个已注册 entries
- 宿主知道 `loom-init route` 与 6 个显式场景 skill 的入口关系
- 宿主刷新 `registry/manifest/executable/referenced_resources/layout_manifest`

本文只定义版本对象与升级说明格式，不重复宿主适配细节。

执行入口的兼容边界与操作流验证由 [execution-entry-compatibility.md](./execution-entry-compatibility.md) 承接。

## 9. Repo Companion Interface 批次（默认 `minor`）

本批 `repo companion` 文档化与合同化变更默认按 `minor` 管理，原因是：

- 新增了稳定下游合同面，但未破坏既有 Loom 入口语义
- 新增的是可选接入能力与机读声明，不是替换现有执行链路

下游新增接入时，最小新增工件为：

- `.loom/companion/manifest.json`
- `.loom/companion/repo-interface.json`

其中 `repo-interface.json` 当前最小稳定字段为：

- `schema_version`
- `companion_entry`
- `repo_specific_requirements`
- `specialized_gates`
