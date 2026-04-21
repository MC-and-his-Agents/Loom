# Repo Companion Contract

本文冻结 Loom 面向既有仓库的 `repo companion` 主合同。

术语约束：

- 正式术语统一使用 `repo companion`
- 历史材料中的 `companion docs` 只作为迁移/回溯表述保留，不再作为当前正式合同名

## 1. 目标与边界

`repo companion` 用于既有仓库的增量 adoption。

它只承接以下对象：

- repo-specific 规则入口
- repo-specific requirements 的机读声明
- specialized gates 的机读声明
- 仓库级 adoption / workflow 挂接入口

它不承接以下 authored truth：

- work item
- recovery 进度
- review 结论
- current stop / next step / blockers / validation summary
- closeout 已完成状态

这些 authored truth 继续由现有 `harness/`、`governance/`、review record、recovery carrier 与 closeout 合同承接。

## 2. Ownership Boundary

- Loom core
  - 持有通用 governance truth、checkpoint 语义、review layering、host-action 与 closeout 合同
- repo companion
  - 持有 repo-specific requirements、specialized gates、repo-level workflow 挂接与 locator
- host adapter / host platform
  - 持有 branch / PR / worktree / CI / ruleset / project 等 retained host actions 的底层实现

稳定约束：

- `repo companion` 不得把 repo-specific 规则伪装成 Loom core 默认规则
- `repo companion` 不得改写 retained host actions 的 ownership
- retained host actions 继续以 [host-action-contract.md](/Users/mc/dev/Loom/harness/host-action-contract.md) 与 [closeout-gate.md](/Users/mc/dev/Loom/harness/closeout-gate.md) 为唯一主落点

## 3. `.loom/companion/manifest.json`

`.loom/companion/manifest.json` 是 `repo companion` 的 locator-only manifest。

当前稳定 schema：

```json
{
  "schema_version": "loom-repo-companion-manifest/v1",
  "companion_entry": ".loom/companion/README.md",
  "repo_interface": ".loom/companion/repo-interface.json"
}
```

字段约束：

- `schema_version` 固定为 `loom-repo-companion-manifest/v1`
- `companion_entry` 必须指向可读的 `repo companion` 主文档
- `repo_interface` 必须指向可读的 `.loom/companion/repo-interface.json`

禁止事项：

- 增加实时 authored state
- 增加 review summary / current stop / blockers / validation summary
- 增加 closeout result 或任何“已经完成”的运行态声明
- 把 manifest 扩成第二套状态面

换句话说，manifest 只负责定位 companion 入口与机读接口，不负责承载运行态真相。

## 4. `.loom/companion/repo-interface.json`

`.loom/companion/repo-interface.json` 是 companion-owned 的最小机读合同，供 `governance_surface` 与 `loom_flow` 消费。

当前兼容读取两个 schema：

- `loom-repo-interface/v1`
- `loom-repo-interface/v2`

其中：

- `v1` 继续保持可读，作为下游兼容口径
- `v2` 是当前正式扩展口径，用于承接 typed `specialized_gates`、repo-specific metadata contract 与 context schema

### 4.1 `v1` 兼容合同

```json
{
  "schema_version": "loom-repo-interface/v1",
  "companion_entry": ".loom/companion/README.md",
  "repo_specific_requirements": {
    "review": [],
    "merge_ready": [],
    "closeout": []
  },
  "specialized_gates": []
}
```

`v1` 字段约束：

- `schema_version` 固定为 `loom-repo-interface/v1`
- `companion_entry` 必须指向可读的 companion 主文档
- `repo_specific_requirements` 必须同时声明 `review`、`merge_ready`、`closeout` 三个 surface
- `specialized_gates` 必须存在，可为空数组

### 4.2 `v2` 扩展合同

```json
{
  "schema_version": "loom-repo-interface/v2",
  "companion_entry": ".loom/companion/README.md",
  "repo_specific_requirements": {
    "review": [],
    "merge_ready": [],
    "closeout": []
  },
  "specialized_gates": [],
  "metadata_contract": {
    "fields": []
  },
  "context_schema": {
    "fields": []
  }
}
```

`v2` 在 `v1` 之上新增两个可选顶层 section：

- `metadata_contract`
- `context_schema`

稳定约束：

- `metadata_contract` 与 `context_schema` 只在 `v2` 合法
- `v2` 不改变 `repo_specific_requirements` 与 `specialized_gates` 的既有纪律
- `v2` 不把 repo runtime state、review summary、validation status 或 retained host action result 写入 `repo-interface.json`

### 4.3 通用字段纪律

`repo_specific_requirements` 的每条 requirement 固定字段：

- `id`
- `summary`
- `locator`
- `enforcement`

其中：

- `enforcement` 只允许 `blocking | advisory`
- `locator` 必须指向仓内可读路径

`specialized_gates` 的每条 gate 固定字段：

- `id`
- `summary`
- `locator`
- `gate_type` 可选

其中：

- `gate_type` 只允许 `admission | pre_review | review | build | merge_ready | closeout`
- `gate_type` 只用于说明 gate 所属 Loom surface，不承载 repo-specific 运行态细节

### 4.4 `metadata_contract`

`metadata_contract` 用于声明 repo-specific metadata fields，而不是把这些字段抬升为 Loom core 默认字段。

`metadata_contract.fields[*]` 固定字段：

- `id`
- `summary`
- `applicability_locator`
- `authority_locator`
- `enforcement`

其中：

- `applicability_locator` 指向“何时需要这组 metadata”的 companion 或 repo-local 权威说明
- `authority_locator` 指向 metadata 真正承载的 repo-native carrier、模板或权威入口
- `enforcement` 只允许 `blocking | advisory`

### 4.5 `context_schema`

`context_schema` 用于声明 repo-specific required context fields 与映射规则，不暗含单一 Loom 通用字段模型。

`context_schema.fields[*]` 固定字段：

- `id`
- `summary`
- `type`
- `required`
- `mapping_rule_locator`

其中：

- `type` 只允许基础类型：`string | integer | number | boolean`
- `required` 必须是布尔值
- `mapping_rule_locator` 指向仓库如何把宿主上下文映射到该字段的权威说明

### 4.6 纪律重申

无论 `v1` 或 `v2`，以下纪律保持不变：

- `manifest.json` 仍 locator-only
- `repo-interface.json` 仍不承载运行态、review summary、current stop、validation status 或 host action result
- repo-specific 规则仍通过 companion 合同挂接，不得伪装成 Loom core 默认规则

## 5. 读面语义

`governance_surface.repo_interface` 当前只允许暴露以下四类状态：

- `absent`
  - 仓库没有 `repo companion` manifest
- `companion_docs_only`
  - 仓库有旧式 companion docs，但没有稳定机读 manifest
- `incomplete`
  - manifest 或 repo-interface 存在，但 locator / schema / required surface 不完整
- `present`
  - manifest 与 repo-interface 都可读且满足最小合同

稳定约束：

- `companion_docs_only` 不得被伪装成稳定 repo interface
- `incomplete` 必须显式报缺口，不得猜测 requirements
- `present` 只表示接口可读，不表示 repo-specific requirements 已被 Loom core 满足

## 6. 与从属合同的关系

`repo companion` 是仓库级 adoption 主合同。

若后续需要 companion-oriented workflow 或 migration 文档：

- 只能作为从属合同
- 只能消费本文件已经冻结的边界
- 不得反向扩张为 Loom 全局 issue-model 或 parent/sub-issue 默认规则
