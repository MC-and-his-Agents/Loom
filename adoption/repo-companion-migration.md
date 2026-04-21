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

对于成熟治理重仓，若还要暴露 retained host action result、repo-native carriers 或 `shadow parity`，再额外新增：

- `.loom/companion/interop.json`

对应稳定 schema 见：

- [repo-companion-contract.md](/Users/mc/dev/Loom/adoption/repo-companion-contract.md)
- [repo-interop-contract.md](/Users/mc/dev/Loom/adoption/repo-interop-contract.md)

## 2. 迁移顺序

默认迁移顺序固定为：

1. 先补 `repo companion` 主合同
2. 再补 `repo-interface.json`
3. 若目标仓库需要 typed gates、metadata/context machine contract，则升级到 `repo-interface v2`
4. 若目标仓库需要 retained host action result、repo-native carrier 或 `shadow parity` 读面，再补 `interop.json`
5. 再接 `governance_surface` / `loom_flow` 的读取消费
6. 再补 reference companion / interop spec
7. 最后做 validation / release / closeout

禁止反向顺序：

- 不先写 reference spec 再倒推接口
- 不先写 migration / release 文档再补主合同
- 不让 `loom_flow` 在 `governance_surface` 之外自造 companion / interop 解析逻辑

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

本批仍不引入 `contract_version`、runtime status、review summary 或 retained host actions 的执行结果字段；这些边界继续由 companion 文档、`interop.json` 与既有 host-action 合同承接。

## 4. `v1 -> v2` 与 `interop` 的升级动作

对下游仓库而言，这轮 companion migration 的最小升级动作固定为：

1. 保留 `.loom/companion/manifest.json`
2. 若只需要 `review` / `merge_ready` / `closeout` requirements，可继续停在 `repo-interface v1`
3. 若需要 typed gates、repo-specific context fields 或 metadata declaration，则升级到 `repo-interface v2`
4. 若需要 Loom 读取 retained host action result、repo-native carriers 或 `shadow parity`，再新增 `interop.json`

兼容纪律：

- `v1` 仓库不必为了升级 Loom 版本被迫立刻写 `v2`
- `v2` 不会改写 `v1` 的读取结果语义
- `interop.json` 是 companion-owned 的独立只读入口，不回塞到 `repo-interface.json`
- `interop.json` 的存在，不等于 Loom 接管 branch / PR / worktree / merge 的执行实现

## 5. 迁移时的兼容结果

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

## 6. Validation / Release / Closeout

一次 companion migration 要被视为完成，至少需要：

- 一条 companion interface validation 记录
- 一条成熟治理重仓 validation 记录（若本次 migration 涉及 `deep-existing-repo` / `interop`）
- release note 中补 companion interface 能力面与默认版本判断
- upgrade note 中写明下游最小新增工件
- closeout basis 中写明 parent 只消费子 issue 已成立真相

对应文档：

- [validation-repo-companion-interface.md](/Users/mc/dev/Loom/adoption/validation-repo-companion-interface.md)
- [validation-deep-existing-repo-syvert-webenvoy.md](/Users/mc/dev/Loom/adoption/validation-deep-existing-repo-syvert-webenvoy.md)
- [versioning-and-upgrades.md](/Users/mc/dev/Loom/adoption/versioning-and-upgrades.md)
- [../docs/complete-kernel-release.md](/Users/mc/dev/Loom/docs/complete-kernel-release.md)

## 7. 默认版本判断

本批 `repo companion migration` 默认按 `minor` 管理。

只有破坏以下任一稳定合同，才升为 `major`：

- `governance_surface`
- root contract
- 必备工件
- 既有 CLI 结果语义
