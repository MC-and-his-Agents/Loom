# Repo Companion Migration Contract

本文定义从既有治理栈迁到 `Loom core + repo companion` 的稳定下游合同。

它不是一次性 release note，而是面向下游仓库的公开迁移顺序与最小工件合同。

## 1. 最小新增工件

一次有效的 `repo companion migration` 至少新增以下两个机读文件：

- `.loom/companion/manifest.json`
- `.loom/companion/repo-interface.json`

其中：

- `manifest.json` 只负责 locator，不承载 authored state
- `repo-interface.json` 负责 companion-owned requirements / typed gates，以及 `v2` 下的 metadata/context 机读声明

对应稳定 schema 见 [repo-companion-contract.md](/Users/mc/dev/Loom/adoption/repo-companion-contract.md)。

## 2. 迁移顺序

默认迁移顺序固定为：

1. 先补 `repo companion` 主合同
2. 再补 `repo_interface` 读面
3. 再接 `loom_flow` 对 `repo_specific_requirements` 的消费
4. 再补 reference companion spec
5. 最后做 validation / release / closeout

禁止反向顺序：

- 不先写 reference spec 再倒推接口
- 不先写 migration / release 文档再补主合同
- 不让 `loom_flow` 在 `governance_surface` 之外自造 companion 解析逻辑

## 3. `repo-interface.json` 最小合同

下游迁移当前允许两种 schema：

- `loom-repo-interface/v1`
- `loom-repo-interface/v2`

其中：

- `v1` 继续兼容读取
- `v2` 在 `v1` 基础上新增 typed `specialized_gates`、`metadata_contract`、`context_schema`

`v1` 顶层字段固定为：

- `schema_version`
- `companion_entry`
- `repo_specific_requirements`
- `specialized_gates`

`v2` 顶层字段固定为：

- `schema_version`
- `companion_entry`
- `repo_specific_requirements`
- `specialized_gates`
- `metadata_contract`
- `context_schema`

其中：

- `repo_specific_requirements` 必须同时声明 `review`、`merge_ready`、`closeout`
- requirement 固定字段为 `id | summary | locator | enforcement`
- `enforcement` 只允许 `blocking | advisory`
- `specialized_gates` 固定字段为 `id | summary | locator`，并允许可选 `gate_type`
- `gate_type` 只允许 `admission | pre_review | review | build | merge_ready | closeout`
- `metadata_contract.fields[*]` 固定字段为 `id | summary | applicability_locator | authority_locator | enforcement`
- `context_schema.fields[*]` 固定字段为 `id | summary | type | required | mapping_rule_locator`
- `context_schema.fields[*].type` 只允许 `string | integer | number | boolean`

本批仍不引入 `contract_version`、runtime status、review summary 或 retained host actions 的执行结果字段；这些边界继续由 companion 文档与既有 host-action 合同承接。

## 4. 迁移时的兼容结果

下游迁移完成前，`governance_surface.repo_interface` 只允许出现以下四类结果：

- `absent`
- `companion_docs_only`
- `incomplete`
- `present`

兼容纪律：

- `absent`
  - 允许继续兼容旧仓库
- `companion_docs_only`
  - 允许保留历史 companion docs，但不得伪装成稳定机读接口
- `incomplete`
  - 必须显式报缺口，不猜测 requirements
- `present`
  - 只表示接口可读，不表示 Loom core 已满足 repo-specific requirements

## 5. Validation / Release / Closeout

一次 companion migration 要被视为完成，至少需要：

- 一条 companion interface validation 记录
- release note 中补 companion interface 能力面与默认版本判断
- upgrade note 中写明下游最小新增工件
- closeout basis 中写明 parent 只消费子 issue 已成立真相

对应文档：

- [validation-repo-companion-interface.md](/Users/mc/dev/Loom/adoption/validation-repo-companion-interface.md)
- [versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md)
- [../docs/complete-kernel-release.md](/Users/mc/dev/Loom/docs/complete-kernel-release.md)

## 6. 默认版本判断

本批 `repo companion migration` 默认按 `minor` 管理。

只有破坏以下任一稳定合同，才升为 `major`：

- `governance_surface`
- root contract
- 必备工件
- 既有 CLI 结果语义
